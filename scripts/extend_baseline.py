"""One-time future-scope enrichment; never resets existing task/test progress."""
from pathlib import Path
import json
root = Path(__file__).resolve().parents[1]
p = root / 'docs/planning'
c = json.loads((p/'catalog.json').read_text(encoding='utf-8'))
s = json.loads((p/'status.json').read_text(encoding='utf-8'))
items = [
('Assisted collector and aggregator accounts','E:1257-1284','Explicit delegation/consent, actor versus beneficial owner, safe phone-less onboarding, separate permissions and offline ownership tests; no admin impersonation shortcut.'),
('Multi-collector batching and pickup operations','E:5920-5934','Batch membership/weights/provenance and collector-level proceeds reconcile; operational capacity and actual pickup success recorded; no double counting.'),
('Predictive prices and automated public feeds','E:2490-2516;E:4669-4701','Licensed sustained comparable observations, temporal holdout against statistical baseline, uncertainty/drift monitoring and a permitted refresh pipeline; keep indicative labels.'),
('Consented active learning and broader classifier','E:2278-2455;E:7154-7162','New consent/rights policy, reviewed correction labels, expanded relevant classes, leakage-safe evaluation and version rollback; current release remains public-images-only.'),
('Learned recycler ranking and advanced risk detection','E:2544-2608','Enough quality outcome labels, temporal evaluation/fairness/reason codes, human review and safety hard filters; do not learn to override route eligibility or accuse fraud.'),
('Voice input and multilingual assistant','E:2963-2989;E:6631-6637','Free/licensed offline ASR where viable, hi/mr noisy-environment tests, explicit confirmation of money/material values and manual fallback; no arbitrary autonomous transaction agent.'),
('Pickup route optimization','E:4692-4701;E:4931-4934','Consented operational locations, realistic vehicle/capacity/time windows, permitted map data and measured routing baseline; no continuous collector tracking by default.'),
('ERP GST PRO brand and CPCB adapters','E:4703-4716;E:7709-7711','Documented official/partner API contracts, credentials and legal role, validated field mapping/sandbox evidence, access/audit controls; no claim of integration or certificate issuance before verification.'),
('Downstream processing and material mass balance','E:4753-4774;E:530-536','Recycler processing evidence, batch splits/merges/yield reconciliation and independently supported downstream outcomes before calling received mass recycled.'),
('Ed25519 server-signed records','E:6196-6196;E:8551-8553','Canonical payload parity, secure signing keys/rotation/revocation/trusted public-key distribution and verification fixtures; signature still does not prove physical facts.'),
('Recovery indicator and environmental estimates','E:5474-5474;E:7632-7632;E:9246-9246','Exact peer-reviewed composition/LCA sources, material/device-specific uncertainty and defensible model validation; no invented official formula, exact metal yield or unsupported CO2 savings. Owner must explicitly promote this optional idea.'),
('Supervised real-world pilot and partnerships','E:3346-3396;E:4669-4691','Consented real collectors/facilities, review safety/privacy/retention/support, actual partnership evidence and measured feedback; historical 5–10/20–30 counts are planning suggestions.'),
('More regions languages and material routes','E:4683-4691;E:4776-4790','Region/language source and review coverage, safe route-specific authorization and model/material validation; preserve e-waste focus until explicit expansion.'),
('Aggregated sector and government insights','E:4718-4774','Adequate representative data, aggregation/privacy controls and sample/denominator limitations for supply/capacity gaps, volatility/material flows/safety; no prototype national statistics.'),
('Advanced dispute review and support workflow','E:3876-3898','Evidence submission/reviewer permissions/appeal/resolution timeline, immutable original quote/final terms and policy; basic pending/disputed states already required in release.'),
('Optional payments messaging and monetization','E:3222-3257;E:4917-4939;E:7017-7027','Separate owner approval, lawful provider terms, fee transparency, webhook idempotency and reconciled settlement; SMS/WhatsApp/email/real UPI/paid SaaS not release dependencies.'),
('Collector identity sharing and partner services','E:7866-7866;E:5576-5576;E:9462-9462','Minimal revocable identity QR/consent-scoped history sharing; verified partner eligibility rules before any credit/welfare claim; never public financial profiles or guaranteed access.'),
('Production operations and scale','E:4917-4939;E:7607-7609','Measured bottleneck/load and security requirements justify queues/caching/infra, incident support and disaster recovery; no speculative Kubernetes/microservices or blockchain requirement.'),
]
existing = {t['id'] for t in c['tasks']}
for i,(title,source,acceptance) in enumerate(items,1):
    tid, rid, case = f'F{i:03}', f'R-FUT-{i:02}', f'FT-{i:03}'
    if tid in existing:
        continue
    c['tasks'].append(dict(id=tid,phase=8,title=title,dependencies=['T050'],reading=['docs/26_FUTURE_BACKLOG.md'],output=acceptance,scope='FUTURE'))
    c['requirements'].append(dict(id=rid,scope='FUTURE',title=title,tasks=[tid],spec='docs/26_FUTURE_BACKLOG.md',source=source.split(';'),test=case,acceptance=acceptance))
    c['tests'].append(dict(id=case,requirement=rid,acceptance=acceptance,kind='future acceptance'))
    s['tasks'][tid]=dict(status='DEFERRED',evidence=[],note='Explicit future scope; requires owner promotion and expanded plan.',owner='Unassigned future owner')
    s['tests'][case]=dict(status='DEFERRED',evidence=[],note='Outside current release, retained for completeness.')
for t in c['tasks']:
    t.setdefault('scope','RELEASE')
    if t['id']=='T037':
        t['dependencies']=[d for d in t['dependencies'] if d!='T032']
        if 'T005' not in t['dependencies']: t['dependencies'].append('T005')
        t['output']=t['output'].replace('T032 supplies licence-review tooling, not image dependencies for audio content.','T005 supplies shared licence/source-review tooling; image-dataset work is not an audio dependency.')
    if t['id']=='T020' and 'T021' not in t['dependencies']:
        t['dependencies'].append('T021')
    if t['id']=='T022':
        t['output']=t['output'].replace('incoming/lot evidence/offer/profile/history/export interactions','incoming/lot evidence/offer/profile/history interactions; R07 export wiring is completed in T031')
    if t['id']=='T031':
        for d in ['T002','T022','T030']:
            if d not in t['dependencies']: t['dependencies'].append(d)
        if 'R07/A07' not in t['output']:
            t['output']+=' Wire approved R07/A07 export downloads and manifest/data-card views end to end; verify actual files and permissions.'
c['version']=2
for name,data in [('catalog.json',c),('status.json',s)]:
    (p/name).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('Catalog includes explicit future scope without resetting progress.')
