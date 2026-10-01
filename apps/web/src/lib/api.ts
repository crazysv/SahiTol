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
  };
};

async function recyclerHeaders(): Promise<HeadersInit> {
  const session = await demoLogin('RECYCLER');
  return { Authorization: `Bearer ${session.access_token}`, 'Content-Type': 'application/json' };
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
