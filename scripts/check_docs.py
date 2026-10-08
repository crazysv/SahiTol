"""Validate documentation traceability, integrity and honest progress; stdlib only.

Does not execute application acceptance or prove semantic exhaustiveness.
Normal run writes docs/DOCUMENTATION_AUDIT.md; exits nonzero on errors.
"""
from pathlib import Path
from urllib.parse import unquote, urlsplit
import hashlib, json, re, subprocess, sys
from datetime import datetime, timezone

ROOT=Path(__file__).resolve().parents[1]

def check_catalog(c,s,root=ROOT):
    errors=[]
    def need(ok,msg):
        if not ok: errors.append(msg)
    def unique(rows,label):
        ids=[r['id'] for r in rows]
        need(len(ids)==len(set(ids)),f'Duplicate {label} IDs')
        return {r['id']:r for r in rows}
    ts=unique(c['tasks'],'task'); rs=unique(c['requirements'],'requirement'); ats=unique(c['tests'],'case')
    need(set(s['tasks'])==set(ts),'Task status set differs from catalog')
    need(set(s['tests'])==set(ats),'Case status set differs from catalog')
    used_tasks=set(); used_cases=set()
    for rid,r in rs.items():
        need(r['scope'] in {'RELEASE','FUTURE','EXTERNAL_GAP'},f'{rid}: invalid scope')
        need(bool(r['tasks']),f'{rid}: no implementation tasks')
        need(bool(r['source']) and bool(r['acceptance']),f'{rid}: missing source/acceptance')
        need((root/r['spec']).is_file(),f'{rid}: missing spec {r["spec"]}')
        for t in r['tasks']:
            used_tasks.add(t); need(t in ts,f'{rid}: missing task {t}')
            if t in ts and r['scope']=='RELEASE': need(ts[t]['scope']=='RELEASE',f'{rid}: release depends on future task {t}')
        a=r['test']; used_cases.add(a)
        need(a in ats and ats[a]['requirement']==rid,f'{rid}: missing/mismatched acceptance {a}')
        if a in ats: need(ats[a]['acceptance']==r['acceptance'],f'{rid}: acceptance text drift')
    need(used_tasks==set(ts),'Orphan or unknown tasks in requirement mapping')
    need(used_cases==set(ats),'Orphan or unknown acceptance cases')
    visiting=set(); visited=set()
    def visit(t):
        if t in visiting:
            errors.append(f'Dependency cycle involving {t}'); return
        if t in visited or t not in ts: return
        visiting.add(t)
        for d in ts[t]['dependencies']:
            need(d in ts,f'{t}: missing dependency {d}')
            if d in ts and ts[t]['scope']=='RELEASE': need(ts[d]['scope']=='RELEASE',f'{t}: future dependency in release')
            visit(d)
        visiting.remove(t); visited.add(t)
    for tid,t in ts.items():
        visit(tid)
        need(t['scope'] in {'RELEASE','FUTURE'},f'{tid}: invalid task scope')
        need(bool(t['output']) and bool(t['reading']),f'{tid}: missing output/reading')
        for p in t['reading']: need((root/p).is_file(),f'{tid}: missing reading {p}')
        if tid not in s['tasks']: continue
        st=s['tasks'][tid]
        need(st['status'] in {'TODO','IN_PROGRESS','WAITING_STITCH','WAITING_INPUT','BLOCKED','DONE','DEFERRED'},f'{tid}: invalid task state')
        if t['scope']=='RELEASE': need(st['status']!='DEFERRED',f'{tid}: mandatory task silently deferred')
        if t['scope']=='FUTURE': need(st['status']=='DEFERRED',f'{tid}: promote future scope before working it')
        if st['status']=='DONE':
            need(bool(st['evidence']),f'{tid}: DONE without evidence')
            for d in t['dependencies']: need(s['tasks'].get(d,{}).get('status')=='DONE',f'{tid}: DONE before dependency {d}')
    for aid,a in ats.items():
        need(a['requirement'] in rs,f'{aid}: missing requirement')
        if aid not in s['tests']: continue
        st=s['tests'][aid]; scope=rs.get(a['requirement'],{}).get('scope')
        need(st['status'] in {'NOT_RUN','PASS','FAIL','BLOCKED','UNMET','DEFERRED'},f'{aid}: invalid test state')
        if scope=='RELEASE': need(st['status'] not in {'UNMET','DEFERRED'},f'{aid}: required case hidden as deferred/unmet')
        if scope=='FUTURE': need(st['status']=='DEFERRED',f'{aid}: future case needs scope promotion')
        if st['status']=='PASS':
            need(bool(st['evidence']),f'{aid}: PASS without evidence')
            for t in rs.get(a['requirement'],{}).get('tasks',[]): need(s['tasks'].get(t,{}).get('status')=='DONE',f'{aid}: PASS before contributing task {t}')
    for kind in ('tasks','tests'):
        for key,st in s[kind].items():
            for path in st['evidence']:
                p=(root/path).resolve()
                need(p.is_relative_to(root.resolve()) and p.is_file(),f'{key}: missing/outside evidence {path}')
                need('templates' not in p.parts and p.name!='DOCUMENTATION_AUDIT.md',f'{key}: template/docs audit cannot prove application acceptance')
    # Protect the owner's explicit six must-haves from accidental demotion/removal.
    for rid in ['R-OFFER-01','R-ML-03','R-LANG-02','R-HAND-02','R-ADMIN-02','R-ECON-01','R-GOV-02','R-GOV-03','R-OPS-01']:
        need(rs.get(rid,{}).get('scope')=='RELEASE',f'Protected required feature missing/demoted: {rid}')
    need(rs.get('R-RES-02',{}).get('scope')=='EXTERNAL_GAP','Primary fieldwork obligation disappeared')
    return errors

def check_sources(c,root=ROOT):
    errors=[]; inventory=json.loads((root/'docs/planning/source_inventory.json').read_text(encoding='utf-8'))
    fixed={'E':'8255866f535798931a6e4c389abd74590c1907cd414e9a7e549216601ea65d28','P':'3d11ef10e6fb87bb6895fe516f5699c47fa5849146bf20edb86192912eb5298e'}
    ids={r['id'] for r in c['requirements']}; lengths={}; covered=set()
    for source in inventory:
        raw=(root/source['path']).read_bytes(); lines=raw.decode('utf-8-sig').splitlines(); digest=hashlib.sha256(raw).hexdigest()
        if digest!=source['sha256'] or digest!=fixed.get(source['alias']): errors.append(f'{source["alias"]}: source bytes/hash changed')
        if len(lines)!=source['lines']: errors.append(f'{source["alias"]}: source line count mismatch')
        lengths[source['alias']]=len(lines); cursor=1
        for section in source['sections']:
            if section['start']!=cursor or section['end']<section['start']: errors.append(f'{source["alias"]}: coverage gap/overlap at {cursor}')
            cursor=section['end']+1
            if not section['requirements'] or set(section['requirements'])-ids: errors.append(f'{source["alias"]}:{section["start"]}: invalid scope mapping')
            covered.update(section['requirements'])
            for h in section['headings']:
                if not(section['start']<=h['line']<=section['end']) or lines[h['line']-1].strip()!=h['text']: errors.append(f'{source["alias"]}: heading inventory drift')
        if cursor!=len(lines)+1: errors.append(f'{source["alias"]}: incomplete range coverage')
    for r in c['requirements']:
        for ref in r['source']:
            if ref=='CURRENT_REQUEST': continue
            match=re.fullmatch(r'([EP]):(\d+)-(\d+)',ref)
            if not match: errors.append(f'{r["id"]}: malformed source citation {ref}'); continue
            a,start,end=match.groups()
            if not 1<=int(start)<=int(end)<=lengths[a]: errors.append(f'{r["id"]}: source range outside file {ref}')
        if r['id'] not in covered and r['source']!=['CURRENT_REQUEST']: errors.append(f'{r["id"]}: absent from source reconciliation')
    return errors,inventory

def anchors(text):
    result=set(); counts={}
    for line in text.splitlines():
        m=re.match(r'^#{1,6}\s+(.+?)\s*#*$',line)
        if not m: continue
        slug=re.sub(r'[^\w\- ]','',m.group(1).lower()).replace(' ','-')
        n=counts.get(slug,0); counts[slug]=n+1
        result.add(slug+(f'-{n}' if n else ''))
    return result

def check_links(root=ROOT):
    errors=[]; count=0
    paths=[path for path in root.rglob('*.md') if not any(p in {'.git','node_modules','.venv','build','dist'} for p in path.parts)]
    for path in paths:
        text=path.read_text(encoding='utf-8')
        text=re.sub(r'```.*?```','',text,flags=re.S)
        for match in re.finditer(r'\[[^\]\n]*\]\(([^)\n]+)\)',text):
            target=match.group(1).strip().strip('<>')
            if urlsplit(target).scheme or target.startswith('//'): continue
            dest,_,frag=target.partition('#'); dest=unquote(dest)
            f=(path.parent/dest).resolve() if dest else path.resolve(); count+=1
            if not f.exists(): errors.append(f'{path.relative_to(root)}: broken link {target}'); continue
            if frag and f.suffix=='.md' and unquote(frag) not in anchors(f.read_text(encoding='utf-8')): errors.append(f'{path.relative_to(root)}: missing anchor {target}')
    return errors,count,len(paths)

def check_screen_map(c,s,root=ROOT):
    errors=[]; task_ids={t['id'] for t in c['tasks']}
    design=(root/'docs/05_DESIGN_STITCH.md').read_text(encoding='utf-8')
    screens={}
    for line in design.splitlines():
        if re.match(r'^\| (S00|C\d\d|R\d\d|A\d\d|V01|U01) \|',line):
            parts=[x.strip() for x in line.split('|')[1:-1]]
            screens[parts[0]]=parts[-1].split(',')
    expected={'S00','V01','U01'}|{f'C{i:02}' for i in range(1,18)}|{f'R{i:02}' for i in range(1,8)}|{f'A{i:02}' for i in range(1,8)}
    if set(screens)!=expected: errors.append('Screen inventory is missing/duplicating baseline IDs')
    registry=(root/'design/stitch/SCREEN_REGISTRY.md').read_text(encoding='utf-8')
    for screen,ts in screens.items():
        if set(ts)-task_ids: errors.append(f'{screen}: unknown implementation task')
        if any(s['tasks'].get(t,{}).get('status')=='DONE' for t in ts):
            rows=[l for l in registry.splitlines() if l.startswith(f'| {screen} |')]
            ready=[l for l in rows if 'REVIEWED_READY' in l or 'IMPLEMENTED_VERIFIED' in l]
            if not ready:
                errors.append(f'{screen}: completed UI task lacks individual approved Stitch registry row')
            else:
                fields=[x.strip() for x in ready[0].split('|')[1:-1]]
                if len(fields)<7 or any(x in {'','—','None','-'} for x in fields[2:6]): errors.append(f'{screen}: missing project/screen/notification/state evidence')
            if all(s['tasks'].get(t,{}).get('status')=='DONE' for t in ts) and not any('IMPLEMENTED_VERIFIED' in l for l in rows): errors.append(f'{screen}: all UI tasks DONE but screen not implementation-verified')
    return errors,len(screens)

def main():
    c=json.loads((ROOT/'docs/planning/catalog.json').read_text(encoding='utf-8'))
    s=json.loads((ROOT/'docs/planning/status.json').read_text(encoding='utf-8'))
    errors=check_catalog(c,s)
    se,inventory=check_sources(c); errors+=se
    le,links,mds=check_links(); errors+=le
    ue,screens=check_screen_map(c,s); errors+=ue
    fixture=json.loads((ROOT/'docs/planning/handover_fixture.json').read_text(encoding='utf-8'))
    canonical=json.dumps(fixture['proposal_payload'],ensure_ascii=False,sort_keys=True,separators=(',',':'))
    if canonical!=fixture['canonical_utf8'] or hashlib.sha256(canonical.encode()).hexdigest()!=fixture['proposal_hash']: errors.append('Handover canonical fixture mismatch')
    rendered=subprocess.run([sys.executable,str(ROOT/'scripts/render_docs.py'),'--check'],capture_output=True,text=True)
    if rendered.returncode: errors.append(rendered.stderr.strip() or rendered.stdout.strip())
    release=[r for r in c['requirements'] if r['scope']=='RELEASE']
    report=['# Documentation integrity audit','',f'Run: {datetime.now(timezone.utc).isoformat(timespec="seconds")}. Result: **'+('PASS' if not errors else 'FAIL')+'**.','',f'- {len(c["requirements"])} requirements: {len(release)} RELEASE, 1 EXTERNAL_GAP, 18 FUTURE.',f'- {len(c["tasks"])} tasks: 50 release and 18 future; {len(c["tests"])} acceptance specifications.',f'- {screens} screen IDs linked to implementation tasks.',f'- {mds} Markdown files; {links} local links/anchors checked.',f'- {sum(x["lines"] for x in inventory):,} archived source lines across {sum(len(x["sections"]) for x in inventory)} contiguous mapped sections; both original SHA-256 hashes verified.','- Unique IDs, requirement/task/case references, reading paths, dependency acyclicity, protected must-haves, evidence-path/state rules, generated-view freshness and canonical hash fixture checked.','', '## Interpretation and limits','', 'PASS means this documentation package passes structural checks. It does not prove every prose interpretation is perfect, source claims are true, or application features work. Source coverage records line ranges and reviewed topics; the semantic reconciliation and future dispositions remain reviewable in [source reconciliation](27_SOURCE_RECONCILIATION.md).','', f'Application release tasks DONE: {sum(x["status"]=="DONE" for k,x in s["tasks"].items() if k.startswith("T"))}/50. Release cases PASS: {sum(s["tests"][r["test"]]["status"]=="PASS" for r in release)}/{len(release)}. The primary fieldwork obligation is {s["tests"][next(r["test"] for r in c["requirements"] if r["id"]=="R-RES-02")]["status"]}.','', 'No software/device/ML/audio/deployment/submission result is inferred from this audit. External web URLs are citations, not continuously monitored availability checks. Evidence existence is checked mechanically; evidence substance still needs review.','', '## Errors','']
    report += [f'- {e}' for e in errors] if errors else ['None.']
    (ROOT/'docs/DOCUMENTATION_AUDIT.md').write_text('\n'.join(report)+'\n',encoding='utf-8')
    print(('PASS' if not errors else 'FAIL')+f': {len(errors)} errors; {links} local links; {screens} screens; {len(c["requirements"])} requirements.')
    for e in errors: print(e)
    return 1 if errors else 0

if __name__=='__main__': raise SystemExit(main())
