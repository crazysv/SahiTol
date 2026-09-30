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
  const res = await fetch(`${API_BASE_URL}/api/v1/auth/demo-login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ role, persona_id: 'default' }),
  });
  if (!res.ok) {
    throw new Error(`Demo login failed: ${res.statusText}`);
  }
  return res.json();
}
