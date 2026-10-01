import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { MemoryRouter, Routes, Route } from 'react-router-dom';
import R04_QRScan from './R04_QRScan';
import R05_ReceiptReview from './R05_ReceiptReview';
import V01_PublicVerification from '../verification/V01_PublicVerification';

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
  });

  it('renders R05_ReceiptReview with discrepancy calculation, payment mode, and receipt issue', () => {
    render(
      <MemoryRouter initialEntries={['/recycler/receipt?ref=ST-24A7&weight=84.8']}>
        <R05_ReceiptReview />
      </MemoryRouter>
    );

    expect(screen.getByText(/Receipt & Settlement Review:/i)).toBeDefined();
    expect(screen.getByText(/Cryptographic Seal Verified/i)).toBeDefined();
    expect(screen.getByText(/Insulated Copper Cable/i)).toBeDefined();

    // Agreed vs Measured comparison
    expect(screen.getByText('85.5 kg')).toBeDefined();
    expect(screen.getByText('84.8 kg')).toBeDefined();
    expect(screen.getByText(/Terms Revision — Weight Variance Detected/i)).toBeDefined();

    // Payment mode selection
    const upiBtn = screen.getByRole('button', { name: /UPI Reference/i });
    fireEvent.click(upiBtn);
    expect(screen.getByPlaceholderText(/e.g. 423984102941/i)).toBeDefined();

    // Confirm receipt
    const confirmBtn = screen.getByRole('button', { name: /Confirm Handover & Issue Digital Receipt/i });
    fireEvent.click(confirmBtn);
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
