# Session continuity and failure recovery

Entry points: [session-start](../commands/session-start.md), [session-continue](../commands/session-continue.md). They are reusable command bodies ready to register in the chosen IDE; this package does not claim they are installed as native slash commands. Use identical content/links when adapting to the IDE's supported custom-command mechanism. A plain pasted command body also works.

## Reconstruct before acting

Read root [AGENTS](../AGENTS.md), [master](../MASTER_CONTENT.md), [index](00_README.md), [session state](SESSION_STATE.md), [tracker](08_TRACKER.md), [decisions](09_DECISIONS.md), [questions](10_OPEN_QUESTIONS.md), [guardrails](12_GUARDRAILS.md). Inspect current files/Git changes and task evidence. Run `python scripts/check_docs.py`; fix planning inconsistency before claiming completion. Do not run the baseline catalog builder during normal implementation.

Catalog is scope/task/case truth; status JSON is progress truth. Generated tracker/roadmap/plan/register are views, not independently edited sources. If tracker disagrees with code/evidence, reopen the task or restore lost evidence after verification; never trust an old assistant's “done” sentence. Read the selected task's linked specifications, requirements, acceptance case and dependencies in full. Do not load only the roadmap then implement from memory.

## Next-task rule

Finish/repair an active task when safe, else choose the earliest RELEASE task whose dependencies are DONE and whose required inputs are available. Phase/order guide selection, not permission to ignore dependencies. T002 may register S00 first, but each later UI task still needs its own screen gate. A task can make partial backend progress while waiting on its UI; status stays incomplete with a precise note. Never select FUTURE work to avoid a blocked required task when independent release work remains.

Advance continuously through authorized tasks after verification, updating state at each meaningful boundary. Do not ask “continue?” or “next task?” Keep user informed of findings/risks. Stop dependent work only for missing required input, genuine authorization boundary or blocking defect; request the specific missing item and progress unrelated eligible work. Deadline pressure does not resolve a missing Stitch approval or permit scope cuts.

## Progress transaction

For each task: set IN_PROGRESS; implement; run relevant checks; capture paths/results/version/device/environment; update mapped case statuses only when their **whole** acceptance is verified; mark task DONE only after its concrete output/dependencies and relevant task-level evidence exist. A cross-task case may remain NOT_RUN until later tasks even when one contributor task is done—do not create a circular requirement to pass end-to-end cases before dependencies can complete.

Edit [status.json](planning/status.json), run `python scripts/render_docs.py`, run validator, update SESSION_STATE and CHANGELOG with current task, next candidate, blockers, precise resume instructions and test results. Task evidence is not a substitute for final acceptance; overall release requires both all tasks and all RELEASE cases. Keep evidence in repository paths with no secrets; screenshots/logs alone need an explanatory evidence record.

## Practical failures

| Failure | Recovery |
|---|---|
| Context lost/new agent | Follow read order above, inspect latest evidence and dirty changes, resume exact incomplete task |
| Contradictory docs | Apply decision precedence, compare preserved source lines; update all affected docs/mappings, never silently choose an old stack |
| Missing Stitch screen/MCP access | WAITING_STITCH with screen IDs/error; ask owner to generate/connect; continue independent tasks |
| Android dependency/device issue | Minimal reproduce on approved S00, pin compatible versions, document attempts; no automatic PWA rewrite |
| Outbox appears stuck | Inspect auth/network/retry/dependency/media/version states; retain rows/files and same idempotency keys |
| Duplicate/mismatched financial state | Halt affected confirmation, inspect immutable event/operation response, reconcile via explicit revision/acknowledgement, not raw DB overwrite |
| Migration/deploy fails | Capture error, preserve data, use rehearsed version-aware rollback/restore; don't reset live DB |
| Demo network fails | State pending honestly, show local fallback or labelled recording; do not claim server confirmation |
| Near deadline with required work missing | Report missing T-/R-/AT- IDs and workable options; only owner can change scope |

Never delete user work, clear pending queues, overwrite source archives, fabricate test results or move mandatory work to future to make a session look complete.
