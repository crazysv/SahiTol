"""Render linked planning views from catalog.json + status.json. Python 3.10+."""
from pathlib import Path
import json, sys

ROOT = Path(__file__).resolve().parents[1]
P = ROOT/'docs/planning'
c = json.loads((P/'catalog.json').read_text(encoding='utf-8'))
s = json.loads((P/'status.json').read_text(encoding='utf-8'))
tasks, reqs, tests = c['tasks'], c['requirements'], c['tests']
tm = {x['id']:x for x in tasks}
rm = {x['id']:x for x in reqs}
def write(name, lines):
    path=ROOT/'docs'/name
    content='\n'.join(lines)+'\n'
    if '--check' in sys.argv:
        if not path.exists() or path.read_text(encoding='utf-8') != content:
            raise SystemExit(f'Stale generated view: {path.name}; run render_docs.py')
    else:
        path.write_text(content,encoding='utf-8')
def esc(x): return str(x).replace('|','\\|').replace('\n',' ')
def link(path): return f'[{Path(path).stem}]({path.removeprefix("docs/")})'
def tlink(t): return f'[{t}](07_IMPLEMENTATION_PLAN.md#{t.lower()})'
def rlink(r): return f'[{r}](15_REQUIREMENTS.md#{r.lower()})'
def alink(a): return f'[{a}](20_TEST_ACCEPTANCE.md#{a.lower()})'
def mapped(t): return [r for r in reqs if t in r['tasks']]
def evidence(items): return ', '.join(f'[{Path(p).name}](../{p})' for p in items) or 'None'
note='Generated from [catalog](planning/catalog.json) and [status](planning/status.json). Edit those files, then run `python scripts/render_docs.py` and `python scripts/check_docs.py`. Do not edit this view independently.'
phases={0:'Feasibility, sources and owner screen handoff',1:'Backend foundation and reviewed reference data',2:'Durable native collector core and sync',3:'Prices, matching and recycler offers',4:'Handover, confirmation and payment evidence',5:'AI, languages, datasets, admin and economics',6:'Hosted/local operations and full verification',7:'Evidence, presentation and submission artifacts',8:'Explicit future scope'}
gates={0:'S00 supplied; real Android spike and source decisions recorded. No automatic fallback.',1:'Migrations/auth/private storage and curated source datasets verified; missing facts remain explicit.',2:'Local restart and retry-safe sync work; C01–C05/C14/C15 supplied and implemented.',3:'Dated indicative prices and hard route filters tested; actual offers/acceptance and approved consoles.',4:'Two phones confirm one synced proposal; revisions, payment acknowledgements, PDF and ledger agree.',5:'All six selected must-haves, seven dataset lifecycles, model/audio rights and real outputs present.',6:'Fault/security/device/language/performance tests, cellular-hosted journey and restore evidence.',7:'All required task/case evidence plus four accessible artifacts; fieldwork limitation disclosed.',8:'Owner promotion and expanded plan required; excluded from current-release percentage.'}
lines=['# Roadmap','',note,'','Owner deadline: **2026-09-30** for all four artifacts; exact official cutoff unverified. These are dependency stages, not a claim the remaining work fits the available time. One builder executes; five teammates present. Do not cut required work silently.','', 'Critical chains: T001→T003→T013→T015→collector; T006→T021→T023→T025→T026; T032→T033→T034; T036→T037→T046; all converge at T043–T050. T002 gates each UI batch; T004/T005 enable data work independently.','']
for phase,title in phases.items():
    lines += [f'## Stage {phase}: {title}','',gates[phase],'','| Task | Work | Status | Dependencies |','|---|---|---|---|']
    for t in tasks:
        if t['phase']==phase: lines.append(f"| {tlink(t['id'])} | {esc(t['title'])} | {s['tasks'][t['id']]['status']} | {', '.join(tlink(d) for d in t['dependencies']) or 'None'} |")
    lines.append('')
lines += ['Parallelizable work means independent work by the same builder or explicitly authorized collaborators; it does not change the one-builder assumption. If the deadline becomes infeasible, report exact required gaps and request an owner scope decision while continuing useful authorized work.','', 'Completion rules: [release checklist](25_RELEASE_CHECKLIST.md). Every task below is also linked to requirements and checks; no feature is complete from roadmap status alone.']
write('02_ROADMAP.md',lines)
lines=['# Implementation plan','',note,'','All tasks start unimplemented. A task DONE needs its concrete output and task-level evidence; multi-task acceptance may remain pending until integration. Final release requires every RELEASE case PASS. T002 never bypasses per-screen Stitch gates.','']
for t in tasks:
    rs=mapped(t['id'])
    lines += [f"## {t['id']}",'',f"**{t['title']}** — stage {t['phase']}; scope {t['scope']}; status **{s['tasks'][t['id']]['status']}**.",'',f"Dependencies: {', '.join(tlink(d) for d in t['dependencies']) or 'None'}.",'',f"Read before coding: {', '.join(link(p) for p in t['reading'])}.",'',f"Concrete output: {t['output']}",'',f"Requirements: {', '.join(rlink(r['id']) for r in rs)}.",'',f"Acceptance: {', '.join(alink(r['test']) for r in rs)}.",'', 'Task closure: implement the output, test relevant paths/failure cases, save reproducible evidence, update status and affected acceptance, regenerate/validate docs and update session state. Future tasks remain deferred until explicitly promoted.','']
write('07_IMPLEMENTATION_PLAN.md',lines)
release_tasks=[t for t in tasks if t['scope']=='RELEASE']
release_reqs=[r for r in reqs if r['scope']=='RELEASE']
done=sum(s['tasks'][t['id']]['status']=='DONE' for t in release_tasks)
passed=sum(s['tests'][r['test']]['status']=='PASS' for r in release_reqs)
lines=['# Execution tracker','',note,'',f"**Release tasks: {done}/{len(release_tasks)} DONE. Release acceptance: {passed}/{len(release_reqs)} PASS.** Future scope and external gaps are not counted as completed release work.",'','Allowed task states: TODO, IN_PROGRESS, WAITING_STITCH, WAITING_INPUT, BLOCKED, DONE; FUTURE starts DEFERRED. Allowed test states: NOT_RUN, PASS, FAIL, BLOCKED; external gap starts UNMET; future starts DEFERRED. Notes explain blockers and next action. Evidence paths are repository-relative, no secret-bearing files.','', '| Task | Work | Scope | Status | Evidence | Note |','|---|---|---|---|---|---|']
for t in tasks:
    st=s['tasks'][t['id']]
    lines.append(f"| {tlink(t['id'])} | {esc(t['title'])} | {t['scope']} | {st['status']} | {evidence(st['evidence'])} | {esc(st['note'])} |")
lines += ['','## External obligation','']
for r in reqs:
    if r['scope']=='EXTERNAL_GAP': lines += [f"- {rlink(r['id'])}: **{s['tests'][r['test']]['status']}** — {esc(s['tests'][r['test']]['note'])}"]
lines += ['','## Requirement completion','', '| Requirement | Scope | Task completion | Acceptance |','|---|---|---|---|']
for r in reqs:
    count=sum(s['tasks'][t]['status']=='DONE' for t in r['tasks'])
    lines.append(f"| {rlink(r['id'])} | {r['scope']} | {count}/{len(r['tasks'])} | {alink(r['test'])}: {s['tests'][r['test']]['status']} |")
write('08_TRACKER.md',lines)
lines=['# Complete requirement register','',note,'','Each row below has scope, source, detailed specification, implementation tasks and observable acceptance. E/P citations reference physical lines in preserved [Entire_Content](sources/Entire_Content.txt) / [previous_convo](sources/previous_convo.txt). CURRENT_REQUEST means the owner’s present instructions. Historical passages are interpreted through [decisions](09_DECISIONS.md), not executed literally.','']
for r in reqs:
    lines += [f"## {r['id']}",'',f"**{r['title']}** — {r['scope']}.",'',f"Source: {'; '.join(r['source'])}. Specification: {link(r['spec'])}.",'',f"Implementation: {', '.join(tlink(t) for t in r['tasks'])}. Acceptance: {alink(r['test'])}.",'',r['acceptance'],'']
write('15_REQUIREMENTS.md',lines)
lines=['# Acceptance and verification register','',note,'','These are test specifications, not executed tests. Capture actual environment/build/device/dataset, setup, action, expected versus observed result, logs/screenshots/DB counts and tester/time in the [evidence template](templates/TEST_EVIDENCE.md). Cases can require multiple fixtures. A prose claim or unchecked screenshot alone is not PASS.','', '## Verification layers','', 'Use domain unit fixtures for weighted quantiles/rounding/matching/canonical hashes/state transitions; PostgreSQL integration for migrations, authorization and concurrent idempotency; Android Room/worker/instrumentation for durable offline behavior; web/API integration for recycler/admin; real devices for camera/QR/audio/performance. Choose concrete commands during T001 and save outputs per task.','', 'Mandatory scenarios: complete online journey; activated airplane-mode photo→model→price/cache→pending QR→restart→reconnect→sync→second-phone confirmation→payment→ledger/admin; denied camera/GPS; no price/no match; expired facility/offer; differing measured weight; duplicate concurrent requests; crash after server commit; partial media/batch failure; token expiry/account switch; changed-payload retry; cursor expiry; disputed/reversed partial payment; missing/corrupt model/audio; Hindi/Marathi numeric boundaries; hosted cold start/redeploy persistence; backup/restore.','', 'Use safe isolated demo data. Model accuracy/performance and language review are measured and recorded, never inferred from a successful build. Acceptance cases spanning multiple tasks close at integration, avoiding dependency deadlocks.','']
for a in tests:
    r=rm[a['requirement']]; st=s['tests'][a['id']]
    lines += [f"## {a['id']}",'',f"**{r['title']}** — {r['scope']}; status **{st['status']}**.",'',f"Requirement: {rlink(r['id'])}. Tasks: {', '.join(tlink(t) for t in r['tasks'])}. Spec: {link(r['spec'])}.",'','Check: '+a['acceptance'],'',f"Evidence: {evidence(st['evidence'])}."+(f" Note: {esc(st['note'])}" if st['note'] else ''),'']
write('20_TEST_ACCEPTANCE.md',lines)
print(f'Rendered 5 linked views: {len(tasks)} tasks, {len(reqs)} requirements, {len(tests)} cases.')
