"""Baseline documentation fixtures and empty CSV headers; no real records imported."""
from pathlib import Path
import json, hashlib, csv
root=Path(__file__).resolve().parents[1]
headers={
'material_catalog':['material_id','category_code','subcategory_code','label_en','label_hi','label_mr','default_route','route_requires_context','allowed_units','safety_guide_ids','source_id','origin_class','source_kind','is_demo','schema_version'],
'material_observations':['observation_id','lot_id','material_id','condition','weight_g','measurement_kind','image_id','region_id','occurred_at','source_id','origin_class','source_kind','is_demo','schema_version'],
'price_observations':['id','material_id','subcategory_id','condition','region_id','price_kind','rate_paise_per_unit','unit','currency','observed_at','facility_id','transaction_id','source_id','review_status','origin_class','source_kind','is_demo','schema_version'],
'recyclers':['facility_id','name','facility_type','region_id','public_address','latitude','longitude','location_quality','route','registration_reference','registration_status','valid_until','last_verified_at','verification_level','materials_accepted','pickup_available','service_area','source_id','origin_class','source_kind','is_demo','schema_version'],
'transactions':['transaction_id','lot_id','collector_pseudonym','facility_id','material_id','final_weight_g','agreed_total_paise','currency','lifecycle_status','handover_status','payment_status','acknowledged_paid_paise','outstanding_paise','occurred_at','source_id','origin_class','source_kind','is_demo','schema_version'],
'traceability':['event_id','aggregate_id','sequence','event_type','actor_pseudonym','device_occurred_at','received_at_server','payload_sha256','prev_hash','event_hash','media_checksums','status','source_id','origin_class','source_kind','is_demo','schema_version'],
'collectors':['collector_pseudonym','alias','preferred_language','general_region_id','created_at','active_lot_count','source_id','origin_class','source_kind','is_demo','schema_version'],
'ai_training':['image_id','asset_ref','sha256','material_label','object_group_id','source_group','split','source_id','license_ref','label_reviewer','label_confidence','condition','weight_g','region_id','transaction_id','origin_class','source_kind','is_demo','schema_version'],
'sources':['source_id','publisher','title','url','publication_date','retrieved_at','source_kind','license','license_url','sha256','local_snapshot','locator','review_status'],
'field_lineage':['entity_type','entity_id','field_name','assertion_value','source_id','locator','transformation_version','reviewer','asserted_at','validation_status']}
for name,cols in headers.items():
    path=root/'data/templates'/f'{name}.csv'
    if not path.exists():
        with path.open('w',newline='',encoding='utf-8') as f: csv.writer(f,lineterminator='\n').writerow(cols)
payload={
'schema_version':'SAHITOL-HANDOVER-1',
'handover_id':'10000000-0000-4000-8000-000000000001',
'transaction_id':'20000000-0000-4000-8000-000000000001',
'lot_id':'30000000-0000-4000-8000-000000000001',
'collector_id':'40000000-0000-4000-8000-000000000001',
'facility_id':'50000000-0000-4000-8000-000000000001',
'agreed_terms_hash':None,
'material_snapshot':{'material_id':'60000000-0000-4000-8000-000000000001','condition':'UNKNOWN','regulatory_route':'E_WASTE'},
'weight_snapshot':{'estimated_weight_g':8500,'measured_weight_g':None},
'value_snapshot':{'currency':'INR','estimated_low_paise':None,'estimated_high_paise':None,'agreed_total_paise':None},
'location_snapshot':{'location_id':None,'source':'MISSING','accuracy_m':None,'captured_at':None},
'occurred_at':'2026-09-28T08:30:00.000Z',
'media':[],
'is_demo':True}
canonical=json.dumps(payload,ensure_ascii=False,sort_keys=True,separators=(',',':'))
fixture={'purpose':'Serialization fixture for a pending proposal with missing agreement/evidence, not confirmation eligibility or real transaction data.','canonicalization':'SAHITOL-JCS-1','proposal_payload':payload,'canonical_utf8':canonical,'proposal_hash':hashlib.sha256(canonical.encode('utf-8')).hexdigest()}
(root/'docs/planning/handover_fixture.json').write_text(json.dumps(fixture,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('Created empty headers and computed canonicalization fixture:',fixture['proposal_hash'])
