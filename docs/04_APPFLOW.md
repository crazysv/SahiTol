# Roles, journeys, and state transitions

Read with [schema](06_SCHEMA.md), [API](16_API_CONTRACT.md), [sync](17_OFFLINE_SYNC.md) and [Stitch screen inventory](05_DESIGN_STITCH.md). These transitions are authoritative; old mixed state machines in the archives are superseded.

## Permissions and roles

| Actor | May do | Must not do |
|---|---|---|
| Collector | Own profile/lots; choose/accept offers; propose handover; acknowledge changed terms/payment; see own history | Access only own/authorized records; never confirm as facility |
| Collector boundary | See eligible public facility data | Read other collectors' private records; confirm as recycler; approve registry status |
| Recycler facility user | View lots directed/listed to their facility; offer/reject; confirm measured receipt; record payment; export their transactions | Read arbitrary lots; approve own legal verification; change collector agreement silently |
| Admin | Curate sources/materials/safety; review facility evidence; inspect permitted quality/audit records | Fabricate party confirmation or retroactively rewrite signed-off facts |
| Public receipt viewer | Redacted reference/status/integrity verification | Confirm handover or access phones, exact GPS, private photos, money details |

Auth role is separate from facility kind (recycler/refurbisher/dismantler/aggregator/collection centre). Multi-collector delegated operation is future work. Public-directory presence is not enrollment: only seeded demo facilities have demo operators; never impersonate staff of a real company.

## Collector journey

1. C01 language, C02 activation/login or explicit demo mode; consent notices are short and local-language. Camera/location permissions are requested at use, not all at launch.
2. C03 home reads cached local summary: Sell Material, Prices, My Earnings, Safety, pending sync; My Lots/Recyclers/Profile provide supporting navigation as designed in Stitch.
3. C04 photo/import and category suggestion; choose/confirm manually including UNKNOWN. C05 weight/condition/optional description, collection time/location quality. Progressive screens keep primary fields ≤3 per step.
4. C06 dated board/trend/audio; C07 lot estimate, offer comparison and safety prompt; C08 candidate list/map and C09 facility evidence/quote details. Save works without price or a match.
5. Submit a listing or directed request when connected. Offline intent can queue. Recycler responds R02/R03. Collector acknowledges offer terms and expiry; only server-accepted agreement is binding in platform state.
6. C10 records physical handover proposal locally, C11 displays pending QR/PDF. Photos, estimated and measured weights (if known), location, time, terms and source snapshots are retained.
7. Connect, sync and review conflicts. R04 second-phone scan opens existing server proposal; R05 recycler records measured receipt. If changed terms need approval, collector explicitly agrees in C16 review; pending data is preserved.
8. C12/C13 ledger shows receipt and payment independently. Cash or optional UPI/other is recorded and acknowledged/disputed. C14 queue shows sync and required action. C17 safety works offline. V01 public verifier is redacted; U01 economics is illustrative.

## Separate state dimensions

### Lot lifecycle

| From | Command/event | To | Preconditions |
|---|---|---|---|
| none | create draft | DRAFT | Owner/device identity; stable UUID |
| DRAFT | finalize collection | COLLECTED | Confirmed manual category (UNKNOWN allowed for review), positive estimated weight; evidence gaps explicit |
| COLLECTED | list/request destination | LISTED | Server validates current fields; unknown route cannot enter eligible matching |
| LISTED | select eligible destination | MATCHED | Selected facility/route; offline selection is proposed, not server-authoritative |
| MATCHED | accept active offer | ACCEPTED | Collector acceptance, eligible facility, nonexpired terms; one active agreement |
| ACCEPTED | record physical handover | HANDED_OVER | Pending handover proposal; not yet recycler-confirmed |
| HANDED_OVER | complete mutual terms + recycler receipt confirmation | RECEIVED | Server commit; authorized party, evidence complete or explicit reviewed exception for location quality |
| RECEIVED | settle and close | CLOSED | Acknowledged paid total matches agreed final value, no open dispute |
| DRAFT/COLLECTED/LISTED/MATCHED/ACCEPTED | cancel with reason | CANCELLED | No confirmed physical receipt; acceptance cancellation visible to other party |
| MATCHED | offer rejected/expired or collector declines | LISTED | Preserve rejected/expired offer history; permit another match |

`CREATED` is an event name, not a second synonym for DRAFT. An individual request/offer can be `REJECTED` or `EXPIRED` without destroying the material lot. `DISPUTED`/`REVIEW_REQUIRED` are review dimensions, not replacements for all lifecycle information. No ordinary transition leaves CLOSED/CANCELLED; a correction/reopening is an explicit audited admin-reviewed workflow, never status PATCH.

Offline proposal before offer acceptance: permit saving evidence and a destination/quoted-terms intent. It remains locally pending and cannot advance server state past required agreement checks. On sync, a recycler can provide/confirm an offer; collector acknowledges it and the proposal is then applied. This supports recording a physical event without inventing online agreement. Record discrepancies rather than hiding the physical event if later eligibility fails.

### Offers

`DRAFT → OPEN → ACCEPTED | REJECTED | EXPIRED | WITHDRAWN`. An accepted offer is an immutable snapshot. Default expiry is supplied by the recycler or explicit demo fixture, never guessed from another rate. If the recycler changes quote/weight/grade, create a new proposed terms revision. Atomic unique constraint ensures at most one active accepted transaction per lot.

### Handovers

`PENDING_CONFIRMATION → PENDING_COLLECTOR_ACK → CONFIRMED`, or directly `PENDING_CONFIRMATION → CONFIRMED` when the collector has already acknowledged the identical terms and recycler confirms. `DISPUTED` is available from either pending stage or as a flag after confirmation, preserving historical confirmation. `VOIDED` is allowed only before confirmed receipt with reason; confirmed records get compensating corrections, not deletion.

Both sides must agree to the same terms hash. The recycler's actual measured weight is stored separately from collector estimate; it becomes agreed final weight only after collector acknowledgement. Same exact confirmation retry returns prior result; competing different confirmation returns conflict/review, never automatically replaces it. A phone scan is a navigation action, not a signature, identity check or payment.

### Payments

Amount assertions use `PROPOSED → ACKNOWLEDGED | DISPUTED | REVERSED`. Aggregate `payment_status` is `PENDING`, `PARTIAL`, `PAID` or `DISPUTED`, derived from acknowledged unreversed amounts and dispute state. Either party can record a claimed payment; the counterparty acknowledges receipt/payment. An offline record stays a pending assertion until synced and resolved. UPI reference is optional private metadata, not proof of bank settlement.

No acknowledged payment: pending dues equal agreed total. Partial payment: positive outstanding balance. Paid: zero balance. Overpayment: review, do not clamp it away. A zero-value/disposal agreement needs an explicit no-payment-required acknowledgement, not an accidental PAID default. Handovers can be received while unpaid; ledger never hides that debt.

### Synchronization

Outbox states: `QUEUED → SENDING → ACKNOWLEDGED`, with `RETRY_WAIT`, `AUTH_REQUIRED`, `NEEDS_REVIEW`, `NEEDS_REPAIR` and `DEPENDENCY_PENDING` alternatives. User-facing labels translate these to saved on phone, sending, synchronized, retry, login required, conflict or repair. Sync describes server acknowledgement, not handover/payment status. See [protocol](17_OFFLINE_SYNC.md).

## Exceptions that must have designed states

| Trigger | Visible outcome and recovery |
|---|---|
| No camera/photo | Permission rationale/import/manual draft; no fake photograph or false evidence-complete receipt |
| No GPS | Coarse/manual location with quality label; no silently fabricated point; matching may use region only |
| UNKNOWN or battery subtype uncertain | Manual review and safety card; no speculative authorized match |
| No price, stale price | No estimate/low confidence with timestamp; can still record lot |
| No match | Save, widen geography, request clarification; route unchanged |
| Offer expires while offline | Original retained, server rejects acceptance, ask for new terms |
| QR not on server | “Saved on collector device; waiting for sync”; manual reference/retry after upload |
| Hash mismatch | Show record does not match; no confirmation until resolved |
| Weight/grade/price changed | Review both values and acknowledge or dispute |
| Media upload fails | Structured record saved, missing evidence visible; retry file separately; confirmation gated |
| Free host cold start | Waiting/retry message; outbox intact; no user data loss |
| Session expires | Continue allowed local activity; reconnect login and resume |
| Non-payment | Received material plus outstanding balance; never mark complete |

## Dataset side effects

Create lot → material observation + collection event. Offer → quote observation (appropriately scoped and reviewed). Confirm receipt → transaction final terms + receipt event. Acknowledged eligible sale → one linked price observation; disputes/reversal update eligibility with lineage. Payment → assertion/ack event + derived ledger. Every mutation carries actor/time/source/demo context. Data effects occur in the same transaction or a durable retryable projection job, not a best-effort callback that can be lost.
