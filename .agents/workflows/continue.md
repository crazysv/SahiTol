---
description: session continue prompt
---

Continue SahiTol from the last verified state and advance through eligible tasks. Do not wait for me to manually say “next task” after every small step.

1. Re-read [AGENTS](../../AGENTS.md), [SESSION_STATE](../../docs/SESSION_STATE.md), [tracker](../../docs/08_TRACKER.md), [decisions](../../docs/09_DECISIONS.md), [open inputs](../../docs/10_OPEN_QUESTIONS.md) and [recovery](../../docs/13_RECOVERY.md). If context is incomplete, perform the complete [session-start](start.md) read sequence first, including MASTER_CONTENT. Inspect existing changes and evidence.
2. Reconcile the current task against canonical catalog/status and actual outputs. Complete/fix it; do not mark DONE from a previous message. Read all specs and R-/AT- mappings for the next eligible task before acting. No requirement can remain only in a side document outside the execution graph.
3. Apply the [Stitch gate](../../docs/05_DESIGN_STITCH.md) to every frontend screen/state: owner generates, owner notifies, agent retrieves designated screens via MCP, registers revisions, then implements. Missing design means WAITING_STITCH for dependent work; continue eligible nonvisual work. Do not generate UI yourself, even via a frontend skill.
4. Implement, run appropriate checks, fix failures, store actual evidence, update [status JSON](../../docs/planning/status.json), run `python scripts/render_docs.py` then `python scripts/check_docs.py`, and update session/changelog. Keep acceptance NOT_RUN/FAIL until actually verified. Preserve the still-unmet fieldwork obligation and future backlog.
5. Proceed automatically to the next eligible required task with brief meaningful progress updates. Stop dependent work only for a concrete missing input/authorization/blocker, and identify exact task/screen/requirement IDs. Do not replace mandatory features, lower acceptance criteria or start unrelated future work because the deadline is close.

At session end report what is verified, what remains, blockers and next action; do not claim app/release/submission completion unless the [release checklist](../../docs/25_RELEASE_CHECKLIST.md) is actually satisfied.