import React from 'react';
import { describe, it, expect } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { MemoryRouter, Routes, Route } from 'react-router-dom';
import AdminLayout from './AdminLayout';
import A01_Overview from './A01_Overview';
import A02_Collectors from './A02_Collectors';
import A03_Facilities from './A03_Facilities';
import A04_CatalogPrices from './A04_CatalogPrices';
import A05_Traceability from './A05_Traceability';
import A06_QualityReview from './A06_QualityReview';
import A07_EvidenceLinks from './A07_EvidenceLinks';

describe('Admin Quality Dashboard (T030 - Screens A01 to A07)', () => {
  it('renders AdminLayout with all 7 Stitch navigation links and screen badges', () => {
    render(
      <MemoryRouter initialEntries={['/admin/overview']}>
        <Routes>
          <Route path="/admin" element={<AdminLayout />}>
            <Route path="overview" element={<A01_Overview />} />
          </Route>
        </Routes>
      </MemoryRouter>
    );

    expect(screen.getByText('SahiTol')).toBeDefined();
    expect(screen.getByText('Admin')).toBeDefined();
    expect(screen.getByText('A01')).toBeDefined();
    expect(screen.getByText('A02')).toBeDefined();
    expect(screen.getByText('A03')).toBeDefined();
    expect(screen.getByText('A04')).toBeDefined();
    expect(screen.getByText('A05')).toBeDefined();
    expect(screen.getByText('A06')).toBeDefined();
    expect(screen.getByText('A07')).toBeDefined();
  });

  it('renders A01_Overview with honest mass labels, hero metrics, and sync action', () => {
    render(
      <MemoryRouter>
        <A01_Overview />
      </MemoryRouter>
    );

    expect(screen.getByText('System Pulse Overview')).toBeDefined();
    expect(screen.getByText('Sync Ledger')).toBeDefined();
    expect(screen.getByText('Material Recorded')).toBeDefined();
    expect(screen.getByText('Received YTD')).toBeDefined();
    expect(screen.getByText('Pending Review')).toBeDefined();
    expect(screen.getByText('Open Disputes')).toBeDefined();
    expect(screen.getByText(/received mass does not equal recycled mass/i)).toBeDefined();

    const syncBtn = screen.getByRole('button', { name: /sync ledger/i });
    fireEvent.click(syncBtn);
    expect(screen.getByText(/syncing/i)).toBeDefined();
  });

  it('renders A02_Collectors with strict privacy mask, search filter, and scrubbed log modal', () => {
    render(
      <MemoryRouter>
        <A02_Collectors />
      </MemoryRouter>
    );

    expect(screen.getByText('Collector Minimal Records Directory')).toBeDefined();
    expect(screen.getByText('Zero-PII Zone')).toBeDefined();
    expect(screen.getByText(/Strict Compliance & Data Minimization Protocol/i)).toBeDefined();
    expect(screen.getByText('IronFox_99')).toBeDefined();

    // Filter by search
    const searchInput = screen.getByPlaceholderText(/filter by alias or region/i);
    fireEvent.change(searchInput, { target: { value: 'CopperDelta' } });
    expect(screen.getByText('CopperDelta')).toBeDefined();
    expect(screen.queryByText('IronFox_99')).toBeNull();

    // View log modal
    const viewLogBtns = screen.getAllByRole('button', { name: /view log/i });
    fireEvent.click(viewLogBtns[0]);
    expect(screen.getByText(/verified privacy mask guarantees/i)).toBeDefined();
    expect(screen.getByText(/no national identity or biometric identifiers stored/i)).toBeDefined();
  });

  it('renders A03_Facilities with L0-L4 ladder, active L3 tier, and quarantine toggle (AT-064)', () => {
    render(
      <MemoryRouter>
        <A03_Facilities />
      </MemoryRouter>
    );

    expect(screen.getByText('Source & Facility Authorization')).toBeDefined();
    expect(screen.getByText('Current Tier: L3 Verified')).toBeDefined();
    expect(screen.getByText('Third-Party Lab & Physical Audit')).toBeDefined();
    expect(screen.getByText(/cannot self-approve their own verification tiers/i)).toBeDefined();

    // Quarantine toggle
    const quarantineBtn = screen.getByRole('button', { name: /quarantine facility/i });
    fireEvent.click(quarantineBtn);
    expect(screen.getByText(/lift quarantine/i)).toBeDefined();
    expect(screen.getByText(/quarantined/i)).toBeDefined();
  });

  it('renders A04_CatalogPrices with catalog tabs, ambiguity queue, and quote anomaly review (AT-020)', () => {
    render(
      <MemoryRouter>
        <A04_CatalogPrices />
      </MemoryRouter>
    );

    expect(screen.getByText('Material Catalog & Safety Governance')).toBeDefined();
    expect(screen.getByText('Heavy Melting Scrap (HMS 1&2)')).toBeDefined();

    // Switch to Price Moderation tab
    const pricesTab = screen.getByRole('button', { name: /price moderation/i });
    fireEvent.click(pricesTab);
    expect(screen.getByText(/Quote Anomaly Review Policy/i)).toBeDefined();
    expect(screen.getByText(/never accuse the collector or recycler of fraud/i)).toBeDefined();

    // Moderate a pending rate
    const approveBtn = screen.getAllByRole('button', { name: /approve rate/i })[0];
    fireEvent.click(approveBtn);
    expect(screen.getAllByText('APPROVED').length).toBeGreaterThan(0);
  });

  it('renders A05_Traceability with lot card, intact hash-chain, and 5-step lineage', () => {
    render(
      <MemoryRouter>
        <A05_Traceability />
      </MemoryRouter>
    );

    expect(screen.getByText('Traceability & Transaction Audit')).toBeDefined();
    expect(screen.getByText('LOT-8942-IN')).toBeDefined();
    expect(screen.getByText('100% Intact')).toBeDefined();
    expect(screen.getByText(/a09162336537b01b/i)).toBeDefined();
    expect(screen.getByText('Event Chain Lineage')).toBeDefined();
    expect(screen.getByText(/LOT_COLLECTED/i)).toBeDefined();
    expect(screen.getByText(/ML_CLASSIFICATION_ADVISORY/i)).toBeDefined();
    expect(screen.getByText(/TERMS_REVISION_AGREED/i)).toBeDefined();
    expect(screen.getByText(/HANDOVER_CONFIRMED/i)).toBeDefined();
    expect(screen.getByText(/PAYMENT_SETTLED/i)).toBeDefined();
  });

  it('renders A06_QualityReview with triage categories, denominators, and resolution reason modal (AT-065)', () => {
    render(
      <MemoryRouter>
        <A06_QualityReview />
      </MemoryRouter>
    );

    expect(screen.getByText('Data Quality Workbench')).toBeDefined();
    expect(screen.getByText('All Issues (1,428)')).toBeDefined();
    expect(screen.getByText('Null Moisture Content Parameter')).toBeDefined();
    expect(screen.getByText(/all triage resolutions require logging an authenticated actor ID and justification reason/i)).toBeDefined();

    // Open resolution modal
    const applyFixBtns = screen.getAllByRole('button', { name: /apply fix/i });
    fireEvent.click(applyFixBtns[0]);
    expect(screen.getByText('Resolve Quality Anomaly')).toBeDefined();

    // Confirm resolution
    const confirmBtn = screen.getByRole('button', { name: /confirm resolution/i });
    fireEvent.click(confirmBtn);
    expect(screen.getAllByText(/RESOLVED/i).length).toBeGreaterThan(0);
  });

  it('renders A07_EvidenceLinks with 7 dataset families, desk research, and UNMET fieldwork disclosure (AT-066)', () => {
    render(
      <MemoryRouter>
        <A07_EvidenceLinks />
      </MemoryRouter>
    );

    expect(screen.getByText('Dataset & Model Evidence Library')).toBeDefined();
    expect(screen.getByText('The Seven Core Dataset Families')).toBeDefined();
    expect(screen.getByText('Ferrous & Heavy Iron Scrap')).toBeDefined();
    expect(screen.getByText('Battery Chemistries & Hazardous Units')).toBeDefined();
    expect(screen.getByText('UNMET')).toBeDefined();

    // Switch to Desk Research tab
    const researchTab = screen.getByRole('button', { name: /desk research/i });
    fireEvent.click(researchTab);
    expect(screen.getByText('RC-01')).toBeDefined();
    expect(screen.getByText(/primary field research with informal waste collectors remains UNMET/i)).toBeDefined();

    // Switch to Model Versioning & Metrics tab
    const modelTab = screen.getByRole('button', { name: /model versioning/i });
    fireEvent.click(modelTab);
    expect(screen.getByText(/MobileNetV3-Small LiteRT Classifier/i)).toBeDefined();
    expect(screen.getAllByText(/1.18 MB/i).length).toBeGreaterThan(0);
    expect(screen.getByText(/0.65 \(Fallback to Manual\)/i)).toBeDefined();
  });
});
