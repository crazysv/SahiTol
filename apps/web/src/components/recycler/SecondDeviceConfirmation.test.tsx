import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { MemoryRouter, Routes, Route } from 'react-router-dom';
import R04_QRScan from './R04_QRScan';
import R05_ReceiptReview from './R05_ReceiptReview';
import V01_PublicVerification from '../verification/V01_PublicVerification';

vi.mock('../../lib/api', async () => {
  const actual = await vi.importActual<typeof import('../../lib/api')>('../../lib/api');
  return {
    ...actual,
    lookupDemoHandover: vi.fn().mockResolvedValue({
      id: 'handover-live-1', status: 'CONFIRMED', proposal_hash: 'a'.repeat(64), version: 2,
      proposal_payload: {
        material_snapshot: { material_id: 'MAT-CAB-01', condition: 'GOOD' },
        weight_snapshot: { estimated_weight_g: 2500, measured_weight_g: 2300 },
        value_snapshot: { agreed_total_paise: 41400, currency: 'INR' },
      },
    }),
  };
});

describe('Second-Device QR Confirmation & Public Verification Views (T025)', () => {
  it('renders R04_QRScan with viewfinder, manual fallback, and recognized proposal', () => {
    render(
      <MemoryRouter>
        <R04_QRScan />
      </MemoryRouter>
    );

    expect(screen.getByText(/Second-Device QR Scanner/i)).toBeDefined();
    expect(screen.getByText(/Terminal Online/i)).toBeDefined();
    expect(screen.getByText(/Align Collector QR inside frame/i)).toBeDefined();

    // The view starts without a fabricated recognition; an actual scan or lookup
    // must supply the record. JSDOM has no camera API, so Start Camera gives the
    // honest recovery state.
    expect(screen.getByText('No QR Scanned Yet')).toBeDefined();
    fireEvent.click(screen.getByRole('button', { name: /Start Camera/i }));
    expect(screen.getByText('Camera Access Required')).toBeDefined();

    // Manual lookup fallback
    const manualInput = screen.getByPlaceholderText(/e.g. ST-24A7/i);
    fireEvent.change(manualInput, { target: { value: 'ST-9999' } });
    const lookupBtn = screen.getByRole('button', { name: /Lookup/i });
    fireEvent.click(lookupBtn);
    expect(screen.getByText('ST-9999')).toBeDefined();
    expect(screen.getByText(/server lookup required/i)).toBeDefined();
    expect((screen.getByRole('button', { name: /Verifying with Server/i }) as HTMLButtonElement).disabled).toBe(true);
  });

  it('renders R05_ReceiptReview only from the confirmed server handover, without a second confirmation action', async () => {
    render(
      <MemoryRouter initialEntries={['/recycler/receipt?handover_id=handover-live-1']}>
        <R05_ReceiptReview />
      </MemoryRouter>
    );

    await waitFor(() => expect(screen.getByText(/Recycler confirmation recorded/i)).toBeDefined());
    expect(screen.getByText('MAT-CAB-01')).toBeDefined();
    expect(screen.getByText('2.30 kg')).toBeDefined();
    expect(screen.getByText('₹414.00')).toBeDefined();
    expect(screen.queryByRole('button', { name: /Confirm Handover/i })).toBeNull();
  });

  it('renders V01_PublicVerification with independent ledger search, cryptographic proof, and privacy boundary', () => {
    render(
      <MemoryRouter initialEntries={['/verify/ST-24A7']}>
        <Routes>
          <Route path="/verify/:id?" element={<V01_PublicVerification />} />
        </Routes>
      </MemoryRouter>
    );

    expect(screen.getByText('Public Handover Verification')).toBeDefined();
    expect(screen.getByText(/Open Verification Protocol \(V01\)/i)).toBeDefined();

    // Result card details
    expect(screen.getByText('Confirmed & Logged')).toBeDefined();
    expect(screen.getByText('Verma Electricals Yard #402')).toBeDefined();
    expect(screen.getByText('84.80 kg')).toBeDefined();
    expect(screen.getByText('SHA-256 MATCH')).toBeDefined();
    expect(screen.getByText('Privacy Boundary Respected')).toBeDefined();
    expect(screen.getByText(/Statutory Notice: Digital Handover Record is a receipt of physical mass transfer/i)).toBeDefined();

    // Search for disputed sample
    const searchInput = screen.getByPlaceholderText(/e.g. ST-24A7 or ST-OKH-2024-9982/i);
    fireEvent.change(searchInput, { target: { value: 'ST-2458' } });
    const verifyBtn = screen.getByRole('button', { name: /^Verify$/i });
    fireEvent.click(verifyBtn);

    expect(screen.getByText('Disputed Inactive')).toBeDefined();
    expect(screen.getByText('HASH MISMATCH')).toBeDefined();
  });
});
