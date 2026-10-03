/**
 * SahiTol Web API Client
 * Configured to communicate with FastAPI backend services.
 */

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export interface HealthResponse {
  status: string;
  app: string;
  version: string;
  environment: string;
  demo_mode: boolean;
  timestamp: string;
}

export async function fetchHealth(): Promise<HealthResponse> {
  const res = await fetch(`${API_BASE_URL}/health`);
  if (!res.ok) {
    throw new Error(`Health check failed with status: ${res.status}`);
  }
  return res.json();
}

export async function demoLogin(role: 'RECYCLER' | 'ADMIN' | 'COLLECTOR') {
  const res = await fetch(`${API_BASE_URL}/api/v1/auth/demo`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ role, persona_id: role === 'RECYCLER' ? 'yard_operator' : 'default', device_id: 'web-recycler-console' }),
  });
  if (!res.ok) {
    throw new Error(`Demo login failed: ${res.statusText}`);
  }
  return res.json();
}

export type HandoverDetail = {
  id: string;
  status: string;
  proposal_hash: string;
  version: number;
  proposal_payload: {
    material_snapshot?: { material_id?: string; condition?: string };
    weight_snapshot?: { estimated_weight_g?: number; measured_weight_g?: number | null };
    value_snapshot?: { agreed_total_paise?: number; currency?: string };
  };
};

async function recyclerHeaders(): Promise<HeadersInit> {
  const session = await demoLogin('RECYCLER');
  return { Authorization: `Bearer ${session.access_token}`, 'Content-Type': 'application/json' };
}

export type AdminOverview = {
  as_of: string;
  last_refresh: string;
  collectors: { total_registered: number; active_in_window: number; demo_collectors: number };
  facilities: { total_facilities: number; verified_facilities: number; by_kind: Record<string, number> };
  lots: { total_lots: number; by_status: Record<string, number>; demo_lots_count: number };
  handovers: { confirmed_count: number; disputed_count: number; formal_received_mass_g: number; demo_mass_g: number; mass_label: string };
  financials: { gross_agreed_paise: number; acknowledged_paid_paise: number; outstanding_dues_paise: number; disputed_paise: number };
  quality: { total_flags: number; open_flags: number; resolved_flags: number };
  unmet_fieldwork_obligation: string;
};

export type QualityFlag = {
  id: string; entity_type: string; entity_id: string; rule_id: string; severity: string;
  evidence_json: Record<string, unknown>; status: string; reason: string | null; created_at: string;
};

export type AdminCollector = { id: string; display_alias: string; preferred_language: string; general_area: string | null; region_id: string | null; created_at: string; lot_count: number; active_lot_count: number };
export type PriceReviewItem = { id: string; material_id: string; region_id: string; rate_paise_per_unit: number; unit: string; price_kind: string; observed_at: string; source_id: string; review_status: string; is_demo: boolean };
export type TraceabilityReport = { lot_id: string; lot_status: string; material_id: string | null; events_count: number; is_hash_chain_valid: boolean; events: Array<{ id: string; event_type: string; actor_id: string; role: string; occurred_at: string; payload_json: Record<string, unknown>; event_hash: string }> };
export type DatasetDirectory = { fieldwork_status: string; datasets: Array<{ family: string; label: string; row_count: number; export_url: string; data_card_url: string }> };
export type AdminFacility = { id: string; name: string; kind: string; region_id: string; active: boolean; authorizations: Array<{ route: string; authority: string; reference: string; status: string; verification_level: string; valid_until: string | null }> };
export type AdminMaterial = { id: string; category_id: string; description_key: string; active: boolean; alias_count: number };

async function adminHeaders(): Promise<HeadersInit> {
  const session = await demoLogin('ADMIN');
  return { Authorization: `Bearer ${session.access_token}`, 'Content-Type': 'application/json' };
}

async function adminRequest<T>(path: string, init: RequestInit = {}): Promise<T> {
  const res = await fetch(`${API_BASE_URL}/api/v1/admin${path}`, {
    ...init,
    headers: { ...(await adminHeaders()), ...(init.headers || {}) },
  });
  if (!res.ok) throw new Error(`Admin request failed (${res.status})`);
  return res.json() as Promise<T>;
}

export function fetchAdminOverview(): Promise<AdminOverview> {
  return adminRequest<AdminOverview>('/overview');
}

export function fetchQualityFlags(): Promise<QualityFlag[]> {
  return adminRequest<QualityFlag[]>('/quality-flags?status=OPEN');
}

export function fetchAdminCollectors(): Promise<AdminCollector[]> { return adminRequest<AdminCollector[]>('/collectors'); }
export function fetchPriceReviews(): Promise<PriceReviewItem[]> { return adminRequest<PriceReviewItem[]>('/price-review'); }
export function decidePriceReview(id: string, decision: 'APPROVE' | 'REJECT', reason: string): Promise<{ review_status: string }> {
  return adminRequest<{ review_status: string }>(`/price-review/${encodeURIComponent(id)}/decision`, { method: 'POST', body: JSON.stringify({ decision, reason }) });
}
export function fetchTraceability(lotId: string): Promise<TraceabilityReport> { return adminRequest<TraceabilityReport>(`/traceability/${encodeURIComponent(lotId)}`); }
export function fetchDatasetDirectory(): Promise<DatasetDirectory> { return adminRequest<DatasetDirectory>('/datasets'); }
export function fetchAdminFacilities(): Promise<AdminFacility[]> { return adminRequest<AdminFacility[]>('/facilities'); }
export function fetchAdminMaterials(): Promise<AdminMaterial[]> { return adminRequest<AdminMaterial[]>('/materials'); }

export function resolveQualityFlag(id: string, decision: 'RESOLVE' | 'DISMISS' | 'ACKNOWLEDGE', reason: string): Promise<QualityFlag> {
  return adminRequest<QualityFlag>(`/quality-flags/${encodeURIComponent(id)}/resolve`, {
    method: 'POST', body: JSON.stringify({ decision, reason }),
  });
}

export async function lookupDemoHandover(handoverId: string): Promise<HandoverDetail> {
  const res = await fetch(`${API_BASE_URL}/api/v1/handovers/${encodeURIComponent(handoverId)}`, {
    headers: await recyclerHeaders(),
  });
  if (!res.ok) throw new Error(`Server lookup failed (${res.status})`);
  return res.json();
}

export async function confirmDemoHandover(record: HandoverDetail): Promise<void> {
  const res = await fetch(`${API_BASE_URL}/api/v1/handovers/${encodeURIComponent(record.id)}/confirm`, {
    method: 'POST',
    headers: await recyclerHeaders(),
    body: JSON.stringify({ expected_version: record.version, proposal_hash: record.proposal_hash }),
  });
  if (!res.ok) throw new Error(`Server confirmation failed (${res.status})`);
}

export type RecyclerIncomingRequest = {
  request_id: string;
  lot_id: string;
  facility_id: string;
  state: string;
  reason: string | null;
  created_at: string;
  lot: {
    material_id: string | null;
    material_name: string | null;
    material_context: string | null;
    estimated_weight_g: number | null;
    condition: string | null;
    coarse_area: string | null;
    collector_alias: string | null;
    images: Array<{ media_id: string; storage_key: string; mime_type: string; byte_size: number; sha256: string; purpose: string }>;
  };
  offers: Array<{ id: string; status: string }>;
};

export async function fetchRecyclerIncoming(): Promise<RecyclerIncomingRequest[]> {
  const res = await fetch(`${API_BASE_URL}/api/v1/recycler/incoming?request_state=ALL`, {
    headers: await recyclerHeaders(),
  });
  if (!res.ok) throw new Error(`Incoming requests failed (${res.status})`);
  return res.json() as Promise<RecyclerIncomingRequest[]>;
}

export async function createRecyclerOffer(
  requestId: string,
  payload: {
    price_basis: 'RATE_PER_KG' | 'FIXED_TOTAL';
    rate_paise_per_kg?: number;
    fixed_total_paise?: number;
    condition: string;
    weight_basis_g: number;
  },
): Promise<{ id: string }> {
  const res = await fetch(`${API_BASE_URL}/api/v1/requests/${encodeURIComponent(requestId)}/offers`, {
    method: 'POST',
    headers: await recyclerHeaders(),
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    let detail = `Offer creation failed (${res.status})`;
    try { detail = (await res.json()).detail || detail; } catch { /* retain status */ }
    throw new Error(detail);
  }
  return res.json() as Promise<{ id: string }>;
}
