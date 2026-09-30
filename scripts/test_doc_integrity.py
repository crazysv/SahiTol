"""Negative controls for omission/progress protections; does not test the app."""
from copy import deepcopy
from pathlib import Path
import json, tempfile
from check_docs import ROOT, check_catalog, check_links, check_screen_map

c=json.loads((ROOT/'docs/planning/catalog.json').read_text(encoding='utf-8'))
s=json.loads((ROOT/'docs/planning/status.json').read_text(encoding='utf-8'))
checks=[]

def run(label,change,expected):
    cc,ss=deepcopy(c),deepcopy(s)
    change(cc,ss)
    errors=check_catalog(cc,ss)
    assert any(expected in e for e in errors),(label,errors)
    checks.append(label)

run('Missing task mapping rejected',lambda c,s:c['requirements'][0].update(tasks=[]),'no implementation tasks')
run('Dependency cycle rejected',lambda c,s:c['tasks'][0]['dependencies'].append('T050'),'Dependency cycle')
run('False DONE without evidence rejected',lambda c,s:s['tasks']['T001'].update(status='DONE',evidence=[]),'DONE without evidence')
run('False PASS without evidence rejected',lambda c,s:s['tests']['AT-001'].update(status='PASS',evidence=[]),'PASS without evidence')
run('Required feature demotion rejected',lambda c,s:next(r for r in c['requirements'] if r['id']=='R-ML-03').update(scope='FUTURE'),'Protected required feature')
run('Deferred mandatory work rejected',lambda c,s:s['tasks']['T001'].update(status='DEFERRED'),'silently deferred')
run('Missing external obligation rejected',lambda c,s:next(r for r in c['requirements'] if r['id']=='R-RES-02').update(scope='RELEASE'),'Primary fieldwork obligation disappeared')
ss=deepcopy(s); ss['tasks']['T003']['status']='DONE'
with tempfile.TemporaryDirectory(prefix='sahitol-screen-check-') as temporary:
    p=Path(temporary); (p/'docs').mkdir(); (p/'design/stitch').mkdir(parents=True)
    (p/'docs/05_DESIGN_STITCH.md').write_text((ROOT/'docs/05_DESIGN_STITCH.md').read_text(encoding='utf-8'),encoding='utf-8')
    (p/'design/stitch/SCREEN_REGISTRY.md').write_text('| S00 | NOT_REQUESTED | — | — | — | None | None |\n',encoding='utf-8')
    assert any('S00' in e for e in check_screen_map(c,ss,p)[0])
checks.append('Unapproved frontend completion rejected')
with tempfile.TemporaryDirectory(prefix='sahitol-doc-check-') as temporary:
    p=Path(temporary)
    (p/'README.md').write_text('[missing](absent.md)\n[anchor](target.md#absent)\n',encoding='utf-8')
    (p/'target.md').write_text('# Present\n',encoding='utf-8')
    errors,_,_=check_links(p)
    assert any('broken link' in e for e in errors) and any('missing anchor' in e for e in errors)
    checks.append('Broken file and anchor links rejected')
assert not check_catalog(c,s),'Baseline unexpectedly fails catalog validation'
print(f'PASS: {len(checks)} negative controls; baseline valid. No application tests executed.')
for item in checks: print('- '+item)
