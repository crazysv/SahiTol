import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { BrowserRouter, MemoryRouter, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import RecyclerLayout from './RecyclerLayout';
import R01_Inbox from './R01_Inbox';
import R02_IncomingLot from './R02_IncomingLot';
import R03_QuoteTerminal from './R03_QuoteTerminal';
import R06_OperationalProfile from './R06_OperationalProfile';
import R07_HistoryExports from './R07_HistoryExports';
import { fetchRecyclerIncoming } from '../../lib/api';

vi.mock('../../lib/api', () => ({
  fetchRecyclerIncoming: vi.fn().mockResolvedValue([
    {
      request_id: 'request-1', lot_id: 'ST-24A7', facility_id: 'facility-1', state: 'PENDING', reason: null,
      created_at: '2026-10-04T00:00:00Z', offers: [],
      lot: { material_id: 'CABLE', material_name: 'Insulated Copper Cable', material_context: null, estimated_weight_g: 85500, condition: 'SCRAP', coarse_area: null, collector_alias: 'Ramesh Kumar', images: [] },
    },
  ]),
  createRecyclerOffer: vi.fn(),
}));

describe('Recycler Console Views (T022)', () => {
  it('renders RecyclerLayout with logo, yard subtitle, and all navigation links', () => {
    render(
      <MemoryRouter initialEntries={['/recycler']}>
        <Routes>
          <Route path="/recycler" element={<RecyclerLayout />}>
            <Route index element={<div>Inbox Content</div>} />
          </Route>
        </Routes>
      </MemoryRouter>
    );

    expect(screen.getByText('SahiTol Recycler')).toBeDefined();
    expect(screen.getByText('Yard #402 - Okhla Industrial')).toBeDefined();
    expect(screen.getAllByText('Inbox').length).toBeGreaterThan(0);
    expect(screen.getAllByText('Incoming Lot').length).toBeGreaterThan(0);
    expect(screen.getAllByText('Quote Terminal').length).toBeGreaterThan(0);
    expect(screen.getAllByText('Operational Profile').length).toBeGreaterThan(0);
    expect(screen.getAllByText('History & Exports').length).toBeGreaterThan(0);
    expect(screen.getByText('Inbox Content')).toBeDefined();
  });

  it('renders R01_Inbox with live operational metrics and lot queue filtering', async () => {
    const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } });
    render(
      <QueryClientProvider client={queryClient}>
        <MemoryRouter>
          <R01_Inbox />
        </MemoryRouter>
      </QueryClientProvider>
    );

    expect(screen.getByText('Yard Dashboard & Material Inbox')).toBeDefined();
    expect(screen.getByText(/Active Shift #402/i)).toBeDefined();
    expect(screen.getByText(/Weighbridge Status/i)).toBeDefined();
    expect(await screen.findByText('ST-24A7')).toBeDefined();

    // Filter to Cables
    const cablesBtn = screen.getByRole('button', { name: /Cables/i });
    fireEvent.click(cablesBtn);
    expect(screen.getByText('Insulated Copper Cable')).toBeDefined();
  });

  it('renders R02_IncomingLot from the live request without substituting a static lot', async () => {
    const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } });
    render(
      <QueryClientProvider client={queryClient}>
        <MemoryRouter initialEntries={['/recycler/incoming?ref=ST-24A7&requestId=request-1']}>
          <R02_IncomingLot />
        </MemoryRouter>
      </QueryClientProvider>
    );

    expect(await screen.findByText(/Lot Inspection Workspace:/i)).toBeDefined();
    expect(screen.getByText('ST-24A7')).toBeDefined();
    expect(screen.getByText('Insulated Copper Cable')).toBeDefined();
    expect(screen.getByText(/Ramesh Kumar/i)).toBeDefined();
    expect(screen.getByText(/Proceed to Quote Terminal/i)).toBeDefined();

    expect(screen.getByText('85.5 kg')).toBeDefined();
  });

  it('renders R03_QuoteTerminal with the matching live request and pricing models', async () => {
    const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } });
    render(
      <QueryClientProvider client={queryClient}>
        <MemoryRouter initialEntries={['/recycler/quote?ref=ST-24A7&requestId=request-1']}>
          <R03_QuoteTerminal />
        </MemoryRouter>
      </QueryClientProvider>
    );

    expect(await screen.findByText(/Commercial Offer Terminal:/i)).toBeDefined();
    expect(screen.getByText(/Rate per Kilogram \(RATE_PER_KG\)/i)).toBeDefined();
    expect(screen.getByText(/Fixed Total Sum \(FIXED_TOTAL\)/i)).toBeDefined();

    // Toggle to Fixed Total model
    const fixedTotalOption = screen.getByText(/Fixed Total Sum \(FIXED_TOTAL\)/i);
    fireEvent.click(fixedTotalOption);

    // Statutory notice present
    expect(screen.getByText(/SahiTol Platform Integrity & Statutory Notice/i)).toBeDefined();
    expect(screen.getByText(/Collector Platform Fee = 0 paise/i)).toBeDefined();
  });

  it('explains why an accepted request cannot dispatch a duplicate quote', async () => {
    vi.mocked(fetchRecyclerIncoming).mockResolvedValueOnce([
      {
        request_id: 'accepted-request', lot_id: 'ST-ACCEPTED', facility_id: 'facility-1', state: 'ACCEPTED', reason: null,
        created_at: '2026-10-04T00:00:00Z', offers: [{ id: 'offer-1', status: 'ACCEPTED' }],
        lot: { material_id: 'MAT-PCB-01', material_name: 'Printed circuit boards', material_context: null, estimated_weight_g: 13000, condition: 'CLEAN', coarse_area: null, collector_alias: 'Demo Santosh', images: [] },
      },
    ]);
    const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } });
    render(
      <QueryClientProvider client={queryClient}>
        <MemoryRouter initialEntries={['/recycler/quote?ref=ST-ACCEPTED&requestId=accepted-request']}>
          <R03_QuoteTerminal />
        </MemoryRouter>
      </QueryClientProvider>
    );

    expect(await screen.findByText(/This offer has already been accepted/i)).toBeDefined();
    expect(screen.queryByRole('button', { name: /Dispatch Quote/i })).toBeNull();
    expect(screen.getByRole('link', { name: /Return to Inbox/i })).toBeDefined();
  });

  it('renders R06_OperationalProfile with scope, service area, and rate updates', () => {
    render(
      <MemoryRouter>
        <R06_OperationalProfile />
      </MemoryRouter>
    );

    expect(screen.getByText('Verma Electricals & Metal Recycling')).toBeDefined();
    expect(screen.getByText('DPCC Valid thru 2028')).toBeDefined();
    expect(screen.getByText(/Service Area Configuration/i)).toBeDefined();
    expect(screen.getByText('Super Grade Copper Wire')).toBeDefined();

    // Save rates
    const saveBtn = screen.getByRole('button', { name: /Save Price Updates/i });
    fireEvent.click(saveBtn);
    expect(screen.getByText(/profile and price board updated successfully/i)).toBeDefined();
  });

  it('renders R07_HistoryExports with ledger table, hash verification, and CSV export', () => {
    render(
      <MemoryRouter>
        <R07_HistoryExports />
      </MemoryRouter>
    );

    expect(screen.getByText('Procurement History & Export Ledger')).toBeDefined();
    expect(screen.getByText('ST-24A7')).toBeDefined();
    expect(screen.getByText('142,580 kg')).toBeDefined();

    // Verify Hashes
    const verifyBtn = screen.getByRole('button', { name: /Verify Hashes/i });
    fireEvent.click(verifyBtn);
    expect(screen.getByText(/Zero hash discrepancies detected/i)).toBeDefined();

    // Export Ledger modal
    const exportBtn = screen.getByRole('button', { name: /Export Ledger/i });
    fireEvent.click(exportBtn);
    expect(screen.getByText(/Statutory Notice Included in Export/i)).toBeDefined();
  });
});
