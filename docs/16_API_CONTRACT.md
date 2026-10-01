# FastAPI contract

Base `/api/v1` for business endpoints; `/health/live` and `/health/ready` are unprefixed host-level probes. Related: [schema](06_SCHEMA.md), [flow](04_APPFLOW.md), [sync](17_OFFLINE_SYNC.md), [security](12_GUARDRAILS.md). T001/T006/T014 generate the corresponding OpenAPI specification and typed clients; this file is the baseline, not a running API.

## General rules

- HTTPS for hosted/release. JWT bearer access token; authenticated user/role/ownership come from server context, never client actor fields. Web refresh may use HttpOnly secure cookie with explicit CSRF/origin protection; Android refresh uses secure storage. Do not mix with Supabase Auth.
- UUID IDs; integer paise/grams, `INR`; UTC millisecond timestamps. Ordinary paginated lists use opaque cursor/limit, default 25/max 100; sync changes use default/max 200. Stable sorting and ownership filters apply before pagination.
- Responses: `{data: ..., meta: {request_id, server_time, schema_version}}`. List meta adds `next_cursor`. Domain records include provenance, freshness/demo and versions. No blanket `verified=true` for a whole response with mixed claims.
- Errors: `{error:{code,message_key,details,retryable},meta:{request_id,server_time}}`. `details` contains field errors/current_version or suggested recovery; never secrets/private foreign records. Localized clients translate `message_key`.
- Mutations use a stable `Idempotency-Key` UUID and `If-Match`/`expected_version` for edits. Operation payload fingerprint is checked. A retry reuses key/body; changed intent uses a new key. Domain commands do not expose generic unrestricted `status` PATCH.
- Dates/source/phone/schema limits validated server-side. Binary photos upload separately; JSON cannot contain unbounded base64. Unknown fields in financial/security commands rejected.
- Every accepted mutation emits authorized deltas, domain/audit events as appropriate, and carries demo context. No server mutation endpoint may bypass the same domain service used by `/sync/batch`.

## Endpoint inventory

| Method and path | Actor / purpose | Key input → output / safeguards |
|---|---|---|
| GET /health/live | Public process liveness | Minimal alive; no DB credentials/config |
| GET /health/ready | Limited public readiness | Database/storage readiness summary and non-sensitive `storage_probe` diagnostic (only `adapter_readiness` after a real adapter check); detailed checks admin-only and no endpoint/credential disclosure |
| POST /auth/register | Collector online activation | phone,PIN,alias?,language,region,consent → profile/session; no arbitrary role |
| POST /auth/login | Any provisioned role | phone,PIN,device_id → access/session; throttled, generic failure |
| POST /auth/demo | Isolated demo only | demo profile code → restricted demo account; never production bypass |
| POST /auth/refresh | Session owner | rotating refresh token/cookie → short-lived access; replay detection |
| POST /auth/logout | Session owner | revoke refresh/session; client pending-record decision separate |
| GET /auth/me | Authenticated | role,profile,facility memberships,demo/environment |
| GET/PATCH /collectors/me | Collector | alias,language,region/general area only; expected_version |
| GET /collectors/me/earnings | Collector | period/from/to → gross,acknowledged_paid,asserted_pending,outstanding,count,weight,as_of |
| GET /collectors/me/transactions | Collector | cursor,date/status filters → own transaction summaries |
| GET /reference/bootstrap | Authenticated/demo | region,language,known versions → versioned material/price/facility/safety/policy bundle |
| GET /reference/changes | Authenticated/demo | opaque cursor → authorized changes and tombstones |
| GET /materials | Authenticated/demo | language,version → catalog,aliases,route context,safety references |
| GET /safety-guides | Authenticated/demo | material/route/language → versioned approved text/audio metadata |
| POST /media/uploads | Owner of parent/draft | media_id,parent_id,mime,size,sha256 → upload instructions; limits/ownership enforced |
| PUT /media/{id}/content | Owner / signed upload route | bounded image stream; validate checksum/decode/type, quarantine until validated |
| POST /media/{id}/complete | Owner | verify persisted object matches metadata → validated media reference |
| GET /media/{id}/access | Authorized owner/facility participant | short-lived read URL; private by default |
| POST /lots | Collector | client UUID,material?,weight?,condition?,collection metadata,media IDs → DRAFT/version |
| GET /lots | Collector/facility/admin | own or authorized incoming scope; filters/cursor |
| GET /lots/{id} | Authorized participant | projection,events,proposals,evidence metadata |
| PATCH /lots/{id} | Owner before immutable agreement | allowed draft fields + expected_version; never overwrite accepted terms |
| POST /lots/{id}/collect | Owner | validated collection fields → COLLECTED |
| POST /lots/{id}/list | Owner | listing/directed facility request → LISTED; revalidate route |
| POST /lots/{id}/cancel | Owner / permitted counterparty workflow | reason + version → CANCELLED only if permitted |
| POST /prices/observations | Collector/recycler/admin | material,condition,region,observed_at,unit,kind,rate,source → pending review observation |
| GET /prices/observations | Authorized scoped reader/admin | own/public approved history; no private identity leakage |
| GET /prices/summary | Authenticated/demo | cohort filters → quantiles,count,sources,confidence,reason,policy,as_of |
| GET /prices/trends | Authenticated/demo | comparable cohort/date bucket → daily observations/median/gaps |
| POST /lots/{id}/estimate | Owner | snapshot ID or comparable cohort → immutable valuation snapshot; null if insufficient |
| GET /facilities | Authenticated/demo | region,material,route → source-backed directory, role and eligibility reasons |
| GET /facilities/{id} | Authenticated/demo | public business profile/source claims; restricted internal notes |
| POST /lots/{id}/matches | Owner | location/ref,search radius,policy version → eligible ranked explanations + exclusion counts |
| POST /lots/{id}/requests | Owner | chosen facility → directed request; offline intent revalidated |
| GET /recycler/incoming | Facility member | facility_id + filter/cursor → permitted requests/lots |
| GET /recycler/transactions | Facility member | facility/date/status/cursor → own receipt/payment/history projections |
| GET/PATCH /recycler/profile | Facility member | accepted operational fields; authorization not editable by facility |
| POST /requests/{id}/offers | Target facility member | rate/fixed basis,condition,expiry,terms → OPEN offer |
| POST /requests/{id}/reject | Target facility member | reason → rejected request; collector can rematch |
| POST /offers/{id}/accept | Collector lot owner | terms_hash,expected_version → accepted offer + transaction atomically |
| POST /offers/{id}/withdraw | Owning facility member | reason + version → WITHDRAWN if not accepted |
| GET /transactions/{id} | Participant/admin | quoted/final terms,receipt/payment/review states and versions |
| POST /handovers | Collector participant | immutable client proposal + hash → PENDING_CONFIRMATION; dependency checks |
| POST /demo/handovers/import | Authenticated demo collector only | provisions missing labelled demo prerequisites, then invokes normal immutable handover creation; never confirms a receipt |
| GET /handovers/{id} | Participant/admin | proposal + revisions + event verification context |
| POST /handovers/{id}/confirm | Linked facility member | expected_version,proposal_hash,terms revision,measured material/weight/value → CONFIRMED or PENDING_COLLECTOR_ACK |
| POST /handovers/{id}/acknowledge-terms | Collector owner | exact terms_hash/version → mutually accepted terms; confirm if recycler already acknowledged |
| POST /handovers/{id}/dispute | Participant | reason,proposed correction,evidence refs → review/dispute without rewriting facts |
| POST /handovers/{id}/void | Participant under rules | reason,version → void pending record only |
| GET /handovers/{id}/receipt | Participant | format PDF/JSON → versioned platform record with current state and original hash |
| GET /verify/{public_token} | Public redacted capability | reference,current state,material summary,hash/version,non-EPR notice only; no confirmation mutation |
| POST /transactions/{id}/payments | Participant | entry UUID,amount,method,private_reference?,occurred_at → asserted payment; actor identity and demo provenance are server-derived |
| POST /payments/{id}/acknowledge | Counterparty | exact amount/version → acknowledged or dispute required; asserting user cannot self-acknowledge |
| POST /payments/{id}/dispute | Counterparty | reason → DISPUTED |
| POST /payments/{id}/reverse | Authorized reviewed correction | original ID,reason,counterparty workflow → append reversal; no deletion |
| POST /transactions/{id}/close | Participant/service | only mutually confirmed received+settled+undisputed → CLOSED |
| POST /sync/batch | Authenticated device | operation envelopes → independent ordered results; see protocol |
| GET /sync/changes | Authenticated scope | opaque cursor/limit → entity versions/tombstones + next_cursor/has_more |
| GET /admin/overview | Admin | selected filters → calculated counts,denominators,as_of |
| GET /admin/collectors | Admin | minimal profiles/activity; sensitive access audited |
| GET /admin/facilities | Admin | persisted facility directory with route/evidence assertions; does not certify external compliance |
| GET/POST /admin/materials | Admin | versioned catalog CRUD through explicit validation |
| PATCH /admin/materials/{id} | Admin | revision/deactivate; retain historical lot references |
| POST /admin/material-aliases | Admin | normalized alias/language/material, ambiguity validation |
| GET/POST/PATCH /admin/safety-guides[/{id}] | Admin | sourced content versions; only approved versions ship to clients |
| POST /admin/facilities/{id}/verification | Admin reviewer | source/ref/scope/validity/status/reason → new evidence assertion, not arbitrary badge |
| GET /admin/price-review | Admin | pending/quarantined observations + reasons |
| POST /admin/price-review/{id}/decision | Admin | approve/reject/revise with reason; recompute affected summaries |
| GET /admin/quality-flags | Admin | severity/rule/source/region filters → flags with entity drill-down |
| POST /admin/quality-flags/{id}/resolve | Admin | reason,evidence → resolution; cannot fabricate consent/receipt |
| GET /admin/traceability | Admin | reference/lot/event → audited timeline and integrity report |
| GET/POST /admin/research-insights | Admin | secondary sources/insights/requirement links; no fabricated primary research |
| GET /admin/datasets | Admin | seven family manifests/cards, counts, validation/source versions and export availability; missing artifact explicitly pending |
| GET /admin/models | Admin | model/version/licence/card and measured evaluation artifacts; no invented metrics before training |
| GET/POST/PATCH /admin/sources[/{id}] | Admin | source metadata/field assertions/review revisions; retain original snapshots |
| GET /analytics/{dashboard,price-trends,material-flow} | Scoped admin/facility as defined | aggregates exclude private/different-facility data; demo filter explicit |
| POST /economics/calculate | Authenticated/demo | versioned illustrative inputs → transparent outputs, source IDs and caveats; no ledger side effect |
| GET/POST /economics/scenarios | Authenticated scoped user | stored illustrative scenarios; owner's access enforced |
| GET /exports/{dataset} | Scoped user/admin | family,filters,CSV/JSON → safe export + manifest; seven families supported |
| GET /recycler/procurement-log | Facility member | own confirmed/pending records + filter → CSV/PDF platform procurement log, not EPR certification |

Square-bracket paths in the admin table are descriptive shorthand; OpenAPI must define each concrete path and method individually. Recycler facility registration is seeded/provisioned or submitted for admin review; no self-signup can self-assign verified status. If adding an onboarding request endpoint during implementation, add its requirement mapping, permissions and tests before use.

## Pending handover payload and fixture

The [computed fixture](planning/handover_fixture.json) contains a complete pending-proposal payload, exact canonical UTF-8 representation and SHA-256 `a091623365372138e72b1d767cca58ac80c59667b59b86f511ebf11b64eb783f`. It is synthetic documentation input, not an actual transaction or confirmation-eligible record. Its missing agreement/media/location are explicit; T023 must add fully evidenced confirmation and changed-terms/event-chain fixtures.

Frozen required top-level keys: `schema_version`, `handover_id`, `transaction_id`, `lot_id`, `collector_id`, `facility_id`, `agreed_terms_hash` (nullable pending), `material_snapshot`, `weight_snapshot`, `value_snapshot`, `location_snapshot`, `occurred_at`, `media`, `is_demo`. Snapshot keys and null handling are demonstrated in the fixture. Media entries contain `media_id` and `sha256`, sorted by media ID. Location coordinates, when present in the referenced evidence record, use fixed integer microdegrees; accuracy uses integer metres to avoid floating-point hash drift. Source/current-record provenance remains linked through immutable snapshots and IDs.

Wire create request is `{id, proposal_payload, proposal_hash, expected_version}`; `id` must equal `proposal_payload.handover_id`, with expected_version null for creation. Actor identities and linked IDs must be validated against authenticated ownership, not trusted because present in a hashed payload. A missing-terms proposal later completed creates a new linked revision/hash; never insert terms into the old frozen payload and call the old hash valid.

## HTTP and domain result mapping

| Result | Response and client action |
|---|---|
| Created | 201 + ID/version; local update after durable ACK |
| Idempotent replay | 200 + stored original result + replay marker; no new event/payment |
| 401 | Pause sync, retain work, reauthenticate |
| 403 | Do not retry blindly; role/object scope error; no foreign data disclosed |
| 404 | Missing/unauthorized indistinguishable as appropriate; unsynced QR uses explicit minimal not-yet-found view |
| 409 | Version/idempotency/terms conflict with safe current version; preserve both proposals |
| 422 | Validation error with field/reason; user repair, new operation ID for changed intent |
| 429 | Respect Retry-After/backoff |
| 5xx / timeout | Retry same operation with backoff; server may already have committed |

Browser camera requires a secure context; use hosted HTTPS in the two-phone demo. Local LAN HTTP camera access may fail; use reference entry or a deliberate trusted HTTPS development setup instead of falsely treating it as a native scanner bug. Public verification is read-only, rate-limited and reveals minimal information. See [deployment](DEPLOYMENT.md).

The QR handover UUID is an opaque lookup handle, not a bearer credential. R04
signs in as the isolated demo recycler before reading a detailed proposal,
compares the QR hash with the server proposal, and only then enables
facility-authorized confirmation. The demo import endpoint is restricted to
`is_demo` collectors and uses the same handover creation service after creating
only labelled demo prerequisites.
