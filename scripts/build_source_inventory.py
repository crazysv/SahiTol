"""Reproduce the documentation baseline source reconciliation index (not app data)."""
from pathlib import Path
import hashlib, json, re
root=Path(__file__).resolve().parents[1]
c=json.loads((root/'docs/planning/catalog.json').read_text(encoding='utf-8'))
E=[
(1,'Identity, audience, regulatory frame and full collector journey','R-GOV,R-REG,R-LOT,R-OFFER,R-HAND,R-PAY'),
(509,'Material taxonomy','R-LOT,R-DATA'),(568,'Prices and confidence','R-PRICE'),(732,'Recycler evidence and matching','R-REC'),
(877,'Competition and differentiation claims','R-RES,R-DOC'),(970,'Passport and handover','R-HAND'),(1039,'QR hashes and confirmation','R-HAND,R-OFF'),
(1113,'Ledger and payments','R-PAY'),(1171,'Safety','R-SAFE'),(1201,'Languages and audio','R-LANG'),(1257,'Assisted-agent idea','R-FUT-01'),
(1285,'Offline behavior','R-OFF'),(1350,'Old architecture alternatives; superseded by native choice','R-ARC,R-AUTH,R-OPS'),(1586,'Caches and sync','R-OFF'),
(1719,'Entities lifecycle datasets','R-DATA,R-LOT,R-OFFER,R-HAND,R-PAY'),(2012,'Targets and data flywheel','R-DATA,R-UX'),
(2080,'Field study proposals; secondary-only decision wins, obligation retained','R-RES'),(2219,'Synthetic data tooling','R-DATA'),
(2278,'Classification and evaluation','R-ML,R-FUT-04'),(2457,'Statistical valuation and future price ML','R-PRICE,R-FUT-03'),
(2518,'Matching and future learned ranking','R-REC,R-FUT-05'),(2564,'Anomaly rules','R-PRICE,R-ADMIN'),(2610,'Security privacy provenance','R-SEC,R-DATA'),
(2709,'Old stack/env/repo proposals; reconciled','R-ARC,R-OPS'),(2928,'Local material aliases','R-LOT,R-LANG'),(2963,'Optional voice input','R-FUT-06'),
(2991,'Screen inventory and usability/performance','R-UX,R-GOV-02'),(3139,'Economics and sustainability','R-ECON,R-FUT-16'),
(3260,'Product metrics','R-ADMIN,R-OPS-04'),(3346,'Future pilot plan','R-FUT-12'),(3398,'Demo script and data quality','R-QA,R-ADMIN,R-GOV-04'),
(3598,'Judge questions and claim boundaries','R-RES,R-REG,R-ML,R-PRICE'),(3876,'Advanced dispute review','R-HAND,R-FUT-15'),
(3901,'Honesty data cards and quality','R-DATA,R-RES,R-ADMIN'),(4072,'Alternative architecture; latest stack overrides','R-ARC,R-OPS'),
(4159,'Old schedule/team/tasks; one-builder deadline overrides','R-GOV,R-QA'),(4470,'Tests and definition of done','R-QA,R-GOV'),
(4569,'Differentiators and evidence','R-RES,R-DOC'),(4669,'Pilot expansion ML agents routes and compliance adapters','R-FUT'),
(4718,'Long-term data network government metrics scale','R-FUT-09,R-FUT-13,R-FUT-14'),(4792,'Technology/social value recaps','R-ARC,R-RES'),
(4917,'Do-not-build list and future services','R-FUT-16,R-FUT-18,R-SEC'),(4941,'Must-build synthesis','ALL'),
(4971,'Narrative principles and quality','R-GOV,R-RES,R-DOC'),(5120,'Completion/priorities; final choices override optional labels','ALL'),
(5285,'Historical citation list and separators','R-RES'),(5315,'Second analysis and corrections','R-RES,R-REG'),
(5336,'Supplied full problem statement including external fieldwork','ALL'),(5371,'Research statistics competition; unverified claims quarantined','R-RES,R-REG'),
(5447,'Architecture AI and optional recovery score','R-ARC,R-ML,R-FUT-11'),(5479,'Sync and seven datasets','R-OFF,R-DATA'),
(5500,'Old stack UX schema; latest native contracts override','R-ARC,R-UX,R-DATA'),(5555,'Fieldwork/economics proposals','R-RES,R-ECON'),
(5581,'Old roadmap demo FAQ tests and risks','R-GOV,R-QA,R-REG'),(5674,'Third consolidated analysis identity product','R-GOV,R-RES'),
(5786,'Regulation and roles','R-REG,R-REC'),(5898,'Users and core modules','R-AUTH,R-LOT,R-PRICE,R-REC,R-OFFER,R-HAND,R-PAY,R-SAFE,R-LANG,R-UX'),
(6349,'Alternative stack; native lock supersedes frontend/runtime variants','R-ARC,R-OPS'),(6527,'Datasets and AI','R-DATA,R-ML,R-FUT-06'),
(6714,'Schema API and security','R-DATA,R-OFF,R-SEC'),(6861,'Competition field proposals and economics','R-RES,R-ECON'),
(7035,'Scope roadmap demo and testing','R-GOV,R-QA,R-UX'),(7304,'Repo and truthful narrative','R-DOC,R-REG,R-RES'),
(7461,'Fourth repeated synthesis incl optional recovery score and stale free-tier claims','ALL'),
(7740,'Fifth repeated synthesis; alternate product names/auth/host choices superseded','ALL'),
(8092,'Sixth repeated synthesis; invented uplift/authority claims rejected','ALL'),
(8372,'Seventh detailed synthesis identity and brief','R-GOV,R-REG,R-RES'),(8525,'Stats regulation privacy and competition','R-RES,R-REG,R-SEC'),
(8727,'Modules and alternate architecture','R-LOT,R-PRICE,R-REC,R-HAND,R-PAY,R-ARC,R-LANG,R-SAFE'),
(9035,'Entities data lifecycle and AI including future recovery','R-DATA,R-ML,R-OFF,R-FUT-11'),
(9260,'Field economics pitch FAQ and execution','R-RES,R-ECON,R-QA,R-GOV'),
(9691,'Claim restrictions and historical references','R-RES,R-REG'),
(10265,'Historical follow-up questions and summary; latest answers in P override','R-GOV,R-RES,R-REG')]
P=[
(1,'Earlier architecture/schedule/fieldwork discussion; later choices override','ALL'),
(1043,'Owner rejects primary fieldwork, secondary-research strategy','R-RES'),
(1441,'Native Android and broad stack proposal','R-ARC,R-OFF,R-ML'),
(1764,'Free tools and remove Redis/MinIO complexity','R-OPS,R-ARC'),
(1942,'Corrected auth/native stack','R-ARC,R-AUTH'),
(1980,'Further native backend/web/infra stack detail','R-ARC,R-OFF,R-OPS,R-ML,R-LANG'),
(2293,'PostGIS/MapLibre/LiteRT/photo/data tooling tweaks','R-ARC,R-ML,R-REC,R-LOT,R-DATA'),
(2320,'Assistant reverted to PWA cleanup; superseded, retain compatible domain clarifications','ALL'),
(2468,'Conflict reconciliation','R-ARC,R-GOV,R-PRICE,R-OFF'),
(2507,'Explicit answers on name/data/field/regions','R-GOV,R-RES,R-DATA,R-REC'),
(2551,'Explicit conflict resolution and retained choices','R-GOV,R-ARC,R-RES'),
(2574,'Documentation intent and one-builder/presenter split','R-GOV,R-DOC'),
(2602,'Final native/deadline/hosted/all six must-have decisions','R-ARC,R-OPS,R-GOV,R-ML,R-ADMIN,R-LANG,R-HAND,R-ECON'),
(2614,'Economics/audio/device/data answers','R-ECON,R-LANG,R-HAND,R-ML'),
(2632,'Final locked summary; controls earlier alternatives','ALL')]
inventory=[]
for alias,name,starts in [('E','Entire_Content.txt',E),('P','previous_convo.txt',P)]:
    path=root/'docs/sources'/name; raw=path.read_bytes(); lines=raw.decode('utf-8-sig').splitlines()
    sections=[]
    for i,(start,title,prefixes) in enumerate(starts):
        end=starts[i+1][0]-1 if i+1<len(starts) else len(lines)
        ids=[r['id'] for r in c['requirements'] if prefixes=='ALL' or any(r['id'].startswith(prefix) for prefix in prefixes.split(','))]
        headings=[{'line':n,'text':line.strip()} for n,line in enumerate(lines[start-1:end],start) if re.match(r'^#{1,6}\s+\S',line.strip())]
        sections.append(dict(start=start,end=end,topic=title,requirements=ids,disposition='RECONCILED',headings=headings))
    inventory.append(dict(alias=alias,path=f'docs/sources/{name}',lines=len(lines),sha256=hashlib.sha256(raw).hexdigest(),sections=sections))
(root/'docs/planning/source_inventory.json').write_text(json.dumps(inventory,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
out=['# Source reconciliation and coverage','', 'Both supplied text files were read end to end before specification drafting. The unchanged copies and SHA-256 hashes below preserve provenance. E/P ranges are physical lines, including separators and repeated text. The current user request overrides embedded historical instructions.','', 'This is a section-level semantic reconciliation plus a mechanically checked line-range inventory. Every line belongs to a named range; that does **not** prove every natural-language idea was understood by a machine. Requirements and future acceptance mappings make the interpretation reviewable. Repeated consolidations intentionally map to many requirements because they repeat the whole product.','', '## Conflict dispositions','', '- Superseded: product-name variants, PWA/Dexie/Next.js/Capacitor, Supabase Auth, ONNX/TFJS, Redis/MinIO, local-only hosting, dropping PostGIS, multi-builder/three-week schedules, old optional status for selected six features. See [decisions](09_DECISIONS.md).','- Required: final native stack, hosted judge access, source-backed core journey, seven datasets, all six features, both languages, two devices, documentation linkage and owner-generated Stitch gate. See [requirements](15_REQUIREMENTS.md).','- Explicit external gap: primary fieldwork under desk-only owner decision. No fabricated research substitutes.','- Retained future: advanced voice/ML/routes/assisted agents/expansion/integrations/signatures/recovery/environmental metrics/pilot/partner services; [future backlog](26_FUTURE_BACKLOG.md).','- Rejected or unverified claims: nonexistent cited official valuation formula, guaranteed income/credit, exact recycler/submission/statistical counts without current primary evidence, official EPR receipt, competitor negative claims, permanent free quotas, automatic keepalive.','- Examples only: sample schema snippets, seed quantities, prediction 82%, 8.5kg, sample price/range/distance, target metrics, fabricated/demo personas. Translate behavior, never pretend those results are actual.','', 'The screenshots are document-organization references, not additional project scope. Their old file names do not require unrelated files; this package supplies project-specific equivalents and dedicated contracts.','']
for source in inventory:
    out += [f"## {source['alias']}: {Path(source['path']).name}",'',f"Lines: {source['lines']}; SHA-256: `{source['sha256']}`.",'', '| Lines | Source topic and interpretation | Requirement families |','|---|---|---|']
    for section in source['sections']:
        families=sorted(set('-'.join(r.split('-')[:2]) for r in section['requirements']))
        out.append(f"| {section['start']}–{section['end']} | {section['topic']} | {', '.join(families)} |")
    out.append('')
out += ['Full IDs and original heading/line inventory are in [source_inventory.json](planning/source_inventory.json). [Documentation audit](DOCUMENTATION_AUDIT.md) checks hashes, contiguous coverage and valid requirement links. New interpretations must update the catalog, decision, source inventory and derived planning views together.']
(root/'docs/27_SOURCE_RECONCILIATION.md').write_text('\n'.join(out)+'\n',encoding='utf-8')
print('Preserved sources mapped across',sum(len(x['sections']) for x in inventory),'contiguous sections.')
