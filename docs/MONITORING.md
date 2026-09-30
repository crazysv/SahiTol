# Product metrics, diagnostics and data quality

T028/T029/T030/T042 own this work. No external monitoring account, scheduled automation or alert channel is configured by these docs. Logs and dashboard queries must derive from persisted events with time window, region, origin/demo filters and last-refresh time. Query failure is not a zero result.

| Metric | Definition / denominator |
|---|---|
| Active collectors | Distinct authorized collector IDs with qualifying lot/transaction activity in displayed window; separate demo |
| Lots created / submitted / completed | Distinct lot IDs by actual transition time; don't sum retries/events as new lots |
| Match coverage | Submitted route-eligible lots with ≥1 eligible candidate / submitted lots evaluated; also report ineligible/missing-data counts |
| Offer acceptance | Accepted offers / offers delivered in defined cohort; explain expiry/window effects |
| Formal received mass | Sum final acknowledged grams for confirmed eligible-destination receipts, excluding demo/cancelled/disputed or superseded records; received, not recycled |
| Gross / paid / dues | Agreed final value, acknowledged non-reversed payment, outstanding nonnegative balance; disputed portions separate |
| Receipt completeness | Confirmed records with required evidence fields / confirmed records; disclose field rules |
| Sync success | Unique operations acknowledged / unique attempted operations; retries measured separately |
| Sync latency / queue age | Server ACK minus first attempt and oldest local queued age separately; device clock caveat |
| Quality completeness | Present valid required fields / applicable required fields, per dataset; null legitimate optional fields excluded |
| Stale / duplicate / invalid | Flagged active rows / inspected applicable rows; include review and resolved counts |
| Provenance coverage | Accepted rows with required source assertions / accepted rows; report counts by origin/demo |
| Classifier correction | User-changed confirmed predictions / predictions actually reviewed; never all images or field accuracy |
| Model metrics | Imported signed-off evaluation artifacts with split counts; not recomputed decorative dashboard numbers |

Quality review stores rule/version, entity/source IDs, severity, reason, detected time, status OPEN/ACKNOWLEDGED/RESOLVED/DISMISSED, actor/resolution/time. Dismissal needs a reason. Underlying evidence corrections create revisions and recompute flags; do not hide them by deleting a source. Rules and numeric defaults are in [techspec](03_TECHSPEC.md).

Redacted structured logs: request/correlation ID, operation ID, role (no PIN/token/phone), endpoint/result/latency, error code, retry count and dependency IDs as appropriate. Metrics include API health, DB connection, storage upload failures, 401/409/429/5xx, queue age, conflicts, cursor resets and missing media. Optional lightweight error reporting is future unless chosen without new paid dependency.

Proposed initial operator triggers: readiness failure across two manual checks; any private-data exposure; upload failures for >5 minutes of active demo; outbox not progressing after reconnect/manual sync; repeated conflict for one aggregate; authorization evidence expires; unexpectedly empty datasets. These are operational defaults, not configured automated alerts. Record expected free-host cold starts separately. Recovery: confirm environment/connectivity/auth, use correlation ID, inspect durable operation/result, retry same key or repair conflict, verify final counts; follow [recovery](13_RECOVERY.md). Never reset all data to make a dashboard green.
