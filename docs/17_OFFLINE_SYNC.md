# Offline persistence and synchronization

Contract for T013–T015/T023–T027. Read with [schema](06_SCHEMA.md), [API](16_API_CONTRACT.md) and [state transitions](04_APPFLOW.md). Android's Room database is the UI's data source. Connectivity, server acceptance and physical receipt are different facts.

## Local commit and identity

Generate UUIDs on the device for each entity, event and operation. Capture `device_occurred_at`, timezone offset and server `received_at` separately; a wrong device clock must not reorder accepted payments or resolve conflicts. Do not create identity from timestamps. Partition every local table/file/cache by account and environment; demo and live identities never share queues.

Photo capture writes an app-private temporary file, validates/compresses/removes EXIF, then atomically renames it. One Room transaction writes the business object, local event and outbox row referencing that durable file. Show “Saved on this phone” only after commit. On restart reconcile staged orphans without deleting referenced unsynced files. The UI always reads the committed projection, including pending badges.

Outbox operation fields: `operation_id`, `account_id`, `device_id`, `entity_type`, `entity_id`, `command`, `expected_version`, `payload`, `payload_sha256`, `depends_on[]`, `media_ids[]`, `created_at`, `attempt_count`, `next_attempt_at`, `state`, `last_error_code`. Payloads become immutable once attempted. A user repair creates a superseding operation linked to the failed one; it never reuses a key with a different payload.

States: `QUEUED → SENDING → ACKNOWLEDGED`; transient error → `RETRY_WAIT`; 401 → `AUTH_REQUIRED`; version/domain conflict → `NEEDS_REVIEW`; invalid input → `NEEDS_REPAIR`. Process death in SENDING restores retry with the same operation ID. Business status must not be inferred from these states.

## Push contract

`POST /api/v1/sync/batch` accepts at most 50 operations per batch (engineering default, configurable). Envelope: `{device_id, operations:[...]}`. Each operation carries the fields above except local retry metadata; server derives account from authentication. Room field mapping is explicit: `owner_user_id→account_id`, `command_type→command`, `base_server_version→expected_version`, `payload_json→payload`, `dependency_operation_ids→depends_on`, `status→state`. Media bytes are uploaded separately; commands refer to validated media IDs. Dependencies must exist and be acknowledged, or precede the command in a topologically sorted batch. Different independent entities can succeed despite another operation failing; waiting ones remain `DEPENDENCY_PENDING` until eligible.

Each response result contains `operation_id`, `outcome` (`APPLIED`, `ALREADY_APPLIED`, `RETRY`, `AUTH_REQUIRED`, `CONFLICT`, `REJECTED`, `DEPENDENCY_PENDING`), `entity_id`, `server_version` when known, `result` or `error`, and `retry_after_seconds` when relevant. Return per-operation outcomes under HTTP 200 for a valid authenticated batch; reject malformed envelopes/auth at request level. A transport failure or missing result is unknown outcome, never success.

Server transaction per operation:

1. Authenticate; verify actor/role/entity ownership and environment. Revalidate the current route, agreement and domain transition.
2. Atomically claim unique `(actor_id, operation_id)` in `sync_operations`, locking/constraining concurrent duplicates. Bind canonical payload fingerprint and command. Same key with different fingerprint returns 409 `IDEMPOTENCY_KEY_REUSED`.
3. Check dependencies and expected aggregate version. Apply business writes, immutable events, change-log entries and stored response in one database transaction. Do not commit “in progress” forever outside the transaction.
4. Return the durable response. A crash after commit but before ACK must replay that response without a second receipt/payment/price observation. An unauthorized caller cannot replay another actor's stored result.

Retain financial/handover operation IDs with the corresponding audit history; do not expire deduplication after an arbitrary short retry TTL. Archiving must preserve a unique tombstone/result reference. Nonfinancial cleanup requires a documented bounded offline lifetime and explicit rebootstrap behavior first.

Uploads use stable media IDs and SHA-256 checksums. Server validates declared and actual MIME, decoded size and ownership, reserves/finalizes metadata idempotently, and returns an existing result for identical retries. Storage failure must not acknowledge a complete evidence attachment. A pending proposal may show missing media explicitly, but confirmation requiring evidence waits until attachment validation. Garbage collection cannot remove unacknowledged device evidence.

## Pull contract

`GET /api/v1/sync/changes?cursor=<opaque>&limit=200` returns `data.changes` and `meta` containing `next_cursor`, `has_more`, `server_time`, request ID and snapshot/schema versions, using the API envelope. Push results similarly live in `data.results`. Changes have entity type/id/version, operation `UPSERT|DELETE`, redacted role-scoped data and monotonically ordered server sequence. Cursors are bound to account/role/environment/filter and represent a consistent high-water snapshot. Never derive them from device wall time or unscoped integer IDs.

Apply each page and its cursor in one Room transaction. Replaying a page is harmless; only newer versions replace confirmed projections. Preserve local pending edits separately and surface conflict instead of overwriting them. Tombstones remove visibility and update caches, while pending dependencies and necessary audit references stay recoverable. Authorization revocation removes formerly visible projections/files after preserving permitted unsent personal work through a safe recovery path.

Expired/invalid cursor returns `410 CURSOR_EXPIRED`: obtain full reference/user snapshot in a staging transaction, reconcile pending operations, then replace confirmed projections and commit the new cursor. Never delete the outbox to “fix sync.” Version changes requiring an app upgrade pause unsupported commands with a clear state.

## Worker and authentication behavior

Use one unique WorkManager chain per account/environment with connected-network constraints and exponential backoff plus jitter. Manual sync enqueues/drains the same worker, preventing duplicate workers. Process one aggregate's dependent operations in order. Metered uploads and foreground progress must be visible; network availability does not imply API reachability. Retry 408/429/5xx and network timeouts; respect Retry-After. Do not retry 422 indefinitely. A 409 needs current state and a user-safe resolution. Refresh credentials once through a serialized refresh flow, then pause for reauthentication if still unauthorized.

Initial real account activation/bootstrap requires network. An already activated profile may keep capturing drafts offline; an expired JWT is never considered server authorization. Keep refresh credentials in Android Keystore-backed storage, not ordinary Room or logs. An offline local lock may restrict device access, but cannot mint server tokens. Demo first launch uses clearly labelled bundled demo identities/data only. Logout checks pending items, preserves encrypted/account-scoped recoverable data, and requires explicit disposition before destructive clearing. Switching users cannot reveal another account's drafts.

## Conflict policy

| Data | Resolution |
|---|---|
| Unsubmitted local draft | Explicit field merge allowed after showing both versions; retain original event |
| Reference material/price/facility cache | Server version wins for future decisions; retain snapshots used in old transactions |
| Offered/accepted terms | Optimistic aggregate version; explicit requote and acknowledgement, never last-write-wins |
| Handover proposal | Immutable client proposal and hash; append confirmation/change/dispute events |
| Final weight/price differs | Recycler records measured revision; collector must acknowledge before confirmed settlement |
| Payment | Append assertion/acknowledgement/reversal; deduplicate operation and preserve disputes |
| Expired/revoked destination | Revalidate; block new acceptance/confirmation with reason, retain historical receipt |

Offline selection and QR do not manufacture an accepted quote. A proposal created before live agreement can be retained, but it is not server-confirmable until its prerequisites are satisfied with matching terms. If completing agreement/evidence changes frozen payload fields, create a linked superseding proposal/hash/QR and keep the original as pending/superseded history. The second phone must see “not synchronized / cannot verify yet” for an unknown reference. Reconnect the collector, synchronize, then scan the current proposal. Browser confirmation is an online baseline; do not pretend the recycler web app has durable offline confirmation.

## QR and integrity

QR encodes a configured HTTPS verification origin, random handover reference/UUID and payload hash/version, never a name/phone/GPS/PIN/token/photo URL. The backend maps the reference to a minimal public status; detailed evidence requires authorized login. A custom origin or external URL scanned by the web console is rejected rather than fetched. Manual reference input is equivalent and rate-limited.

Canonical fields and event hashes follow [SAHITOL-JCS-1](06_SCHEMA.md). T023 must create a golden payload and expected byte sequence/digest used by Python, Kotlin and browser tests. PDF uses exactly the stored proposal/confirmed snapshot, with status, source, time, weight, terms and hash. Pending PDF remains pending forever as an artifact; a later confirmed PDF is a new linked version. A matching SHA-256 confirms byte equality with a trusted record, not identity, material composition or physical recycling. Server signatures remain in [future scope](26_FUTURE_BACKLOG.md).

## Required fault evidence

Cover airplane mode, reboot after local save, process kill during file write/DB commit/upload/ACK, duplicate concurrent push, response loss after server commit, one rejected operation in a batch, dependency out of order, changed-payload key reuse, cursor replay/expiry, concurrent devices, token expiry, wrong clock, stale facility, edited terms, storage failure and account switching. For each show initial state, induced fault, durable rows/outbox, recovery and final counts. See [acceptance register](20_TEST_ACCEPTANCE.md); a green worker log alone is insufficient.
