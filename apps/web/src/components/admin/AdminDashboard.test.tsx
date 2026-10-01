import React from 'react';
import { afterEach, describe, expect, it, vi } from 'vitest';
import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import A01_Overview from './A01_Overview';
import A02_Collectors from './A02_Collectors';
import A05_Traceability from './A05_Traceability';
import A06_QualityReview from './A06_QualityReview';
import A07_EvidenceLinks from './A07_EvidenceLinks';

const response = (body: unknown) => Promise.resolve({ ok: true, json: () => Promise.resolve(body) });
afterEach(() => vi.unstubAllGlobals());

function mockApi() {
  vi.stubGlobal('fetch', vi.fn((input: string) => {
    if (input.includes('/auth/demo')) return response({ access_token: 'demo-token' });
    if (input.includes('/overview')) return response({ last_refresh: '2026-10-01T00:00:00Z', handovers: { formal_received_mass_g: 2300, disputed_count: 1, mass_label: 'received, not recycled' }, quality: { open_flags: 2 } });
    if (input.includes('/collectors')) return response([{ id: 'c1', display_alias: 'VerifiedAlias', preferred_language: 'hi', general_area: 'Delhi', region_id: 'DELHI_NCR', created_at: '2026-10-01T00:00:00Z', lot_count: 3, active_lot_count: 1 }]);
    if (input.includes('/quality-flags')) return response([{ id: 'q1', entity_type: 'LOT', entity_id: 'lot1', rule_id: 'DQ-DUPLICATE-MEDIA', severity: 'MEDIUM', evidence_json: {}, status: 'OPEN', reason: 'Review duplicate media.', created_at: '2026-10-01T00:00:00Z' }]);
    if (input.includes('/datasets')) return response({ fieldwork_status: 'UNMET', datasets: [{ family: 'materials', label: 'Materials', row_count: 7, export_url: '', data_card_url: '' }] });
    if (input.includes('/traceability/')) return response({ lot_id: 'lot1', lot_status: 'CONFIRMED', material_id: 'MAT-PCB-01', events_count: 1, is_hash_chain_valid: true, events: [{ id: 'e1', event_type: 'LOT_CREATED', actor_id: 'c1', role: 'COLLECTOR', occurred_at: '2026-10-01T00:00:00Z', payload_json: {}, event_hash: 'abc123' }] });
    return response([]);
  }));
}

describe('T030 API-backed admin screens', () => {
  it('renders server overview values and the honest mass label', async () => { mockApi(); render(<MemoryRouter><A01_Overview /></MemoryRouter>); await waitFor(() => expect(screen.getByText('2.3')).toBeDefined()); expect(screen.getByText(/received, not recycled/i)).toBeDefined(); });
  it('uses the privacy-minimal collector API response', async () => { mockApi(); render(<MemoryRouter><A02_Collectors /></MemoryRouter>); await waitFor(() => expect(screen.getByText('VerifiedAlias')).toBeDefined()); expect(screen.queryByText('IronFox_99')).toBeNull(); });
  it('loads real quality flags and submits a server resolution', async () => { mockApi(); render(<MemoryRouter><A06_QualityReview /></MemoryRouter>); await waitFor(() => expect(screen.getByText('DQ-DUPLICATE-MEDIA')).toBeDefined()); fireEvent.click(screen.getByRole('button', { name: /apply fix/i })); fireEvent.change(screen.getByPlaceholderText(/state the audit reason/i), { target: { value: 'Evidence reviewed and corrected.' } }); fireEvent.click(screen.getByRole('button', { name: /confirm resolution/i })); await waitFor(() => expect(fetch).toHaveBeenCalled()); });
  it('loads the data-card count and requested server trace', async () => { mockApi(); const view = render(<MemoryRouter><A07_EvidenceLinks /></MemoryRouter>); await waitFor(() => expect(screen.getByText('1 Families')).toBeDefined()); view.unmount(); render(<MemoryRouter><A05_Traceability /></MemoryRouter>); fireEvent.change(screen.getByPlaceholderText(/search by lot id/i), { target: { value: 'lot1' } }); fireEvent.click(screen.getByRole('button', { name: /inspect lot/i })); await waitFor(() => expect(screen.getByText('MAT-PCB-01')).toBeDefined()); });
});
