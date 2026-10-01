import React, { useEffect, useState } from 'react';
import { decidePriceReview, fetchAdminMaterials, fetchPriceReviews } from '../../lib/api';

export default function A04_CatalogPrices() {
  const [activeTab, setActiveTab] = useState<'catalog' | 'aliases' | 'prices' | 'safety'>('catalog');
  const [searchQuery, setSearchQuery] = useState('');
  const [patchDeployed, setPatchDeployed] = useState(false);

  // Price observation moderation items
  const [observations, setObservations] = useState([
    {
      id: 'OBS-4401',
      material: 'Printed Circuit Boards (Grade High)',
      code: 'MAT-PCB-01',
      yard: 'Mayapuri Aggregator #2',
      grossRate: '₹750.00 / kg',
      referenceRate: '₹550.00 – ₹620.00 / kg',
      deviation: '+25.0% (High Outlier)',
      status: 'PENDING_REVIEW',
      reviewReason: 'Price exceeds 1.5x IQR upper threshold for Delhi-NCR region',
    },
    {
      id: 'OBS-4402',
      material: 'Heavy Melting Scrap (HMS 1&2)',
      code: 'MAT-MET-01',
      yard: 'Okhla Yard Alpha',
      grossRate: '₹34.50 / kg',
      referenceRate: '₹33.00 – ₹36.00 / kg',
      deviation: '+1.5% (Nominal)',
      status: 'APPROVED',
      reviewReason: 'Within normal regional price band',
    },
    {
      id: 'OBS-4403',
      material: 'Lead-Acid Battery (Sealed Inverter)',
      code: 'MAT-BAT-01',
      yard: 'Dharavi Battery Depot',
      grossRate: '₹72.00 / kg',
      referenceRate: '₹88.00 – ₹95.00 / kg',
      deviation: '-18.2% (Low Outlier)',
      status: 'PENDING_REVIEW',
      reviewReason: 'Rate below 1.5x IQR lower threshold; potential battery condition discount',
    },
  ]);

  const [loadError, setLoadError] = useState<string | null>(null);
  const [materialsCount, setMaterialsCount] = useState<number | null>(null);
  useEffect(() => {
    void fetchPriceReviews().then((rows) => setObservations(rows.map((row) => ({
      id: row.id, material: row.material_id, code: row.material_id, yard: row.region_id,
      grossRate: `₹${(row.rate_paise_per_unit / 100).toFixed(2)} / ${row.unit.toLowerCase()}`,
      referenceRate: 'Review required against eligible cohort', deviation: 'Review pending', status: row.review_status,
      reviewReason: `Source ${row.source_id}; observed ${new Date(row.observed_at).toLocaleDateString('en-GB')}`,
    })))).catch((error: unknown) => setLoadError(error instanceof Error ? error.message : 'Unable to load price reviews.'));
  }, []);
  useEffect(() => { void fetchAdminMaterials().then((materials) => setMaterialsCount(materials.length)).catch((error: unknown) => setLoadError(error instanceof Error ? error.message : 'Unable to load catalog.')); }, []);

  const handleModerate = (id: string, newStatus: 'APPROVED' | 'REJECTED') => {
    const decision = newStatus === 'APPROVED' ? 'APPROVE' : 'REJECT';
    void decidePriceReview(id, decision, 'Reviewed by administrator through the approved moderation workflow.').then((result) => {
      setObservations((prev) => prev.map((observation) => observation.id === id ? { ...observation, status: result.review_status } : observation));
    }).catch((error: unknown) => setLoadError(error instanceof Error ? error.message : 'Unable to submit moderation decision.'));
  };

  const handleDeployPatch = () => {
    setPatchDeployed(true);
    setTimeout(() => setPatchDeployed(false), 4000);
  };

  return (
    <div className="flex flex-col w-full">
      {/* Top Bar / Subheader Navigation for Workshop (Stitch A04) */}
      <div className="w-full bg-surface-container-low py-space-md border-b border-surface-container">
        <div className="max-w-7xl mx-auto px-gutter flex flex-col md:flex-row items-start md:items-center justify-between gap-space-md">
          <div>
            <span className="text-label-sm uppercase tracking-wider text-primary font-bold">
              Reference-Data Workshop
            </span>
            <h1 className="text-headline-lg font-headline-lg text-on-surface font-bold">
              Material Catalog & Safety Governance
            </h1>
          </div>
          <div className="flex items-center gap-space-sm overflow-x-auto w-full md:w-auto">
            {[
              { id: 'catalog', label: 'Catalog Revisions' },
              { id: 'aliases', label: 'Alias Resolution' },
              { id: 'prices', label: 'Price Moderation' },
              { id: 'safety', label: 'Safety & Lang' },
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as any)}
                className={`px-4 py-2 rounded-xl text-label-md font-bold transition-all whitespace-nowrap ${
                  activeTab === tab.id
                    ? 'bg-primary text-on-primary shadow-sm'
                    : 'bg-surface-container-high text-on-surface hover:bg-surface-dim'
                }`}
              >
                {tab.label}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Main Content Area */}
      <div className="max-w-7xl mx-auto px-gutter py-space-xl w-full">
        {/* TAB 1: CATALOG REVISIONS */}
        {activeTab === 'catalog' && (
          <div className="space-y-space-xl">
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-space-lg">
              {/* Left Column: Catalog Stats & Visualizer */}
              <div className="lg:col-span-1 space-y-space-lg">
                <div className="bg-surface-container p-space-lg rounded-xl shadow-sm space-y-space-md border border-surface-container-high">
                  <div className="flex items-center justify-between">
                    <span className="text-label-md text-on-surface-variant font-medium">Active Revision</span>
                    <span className="px-2.5 py-1 bg-primary text-on-primary text-label-sm rounded-full font-bold">
                      v4.8.2-IND
                    </span>
                  </div>
                  <div className="flex items-baseline gap-space-sm">
                    <span className="text-headline-xl text-on-surface font-bold">{materialsCount ?? '—'}</span>
                    <span className="text-body-sm text-on-surface-variant">Standardized Items</span>
                  </div>
                  {/* Mini Breakdown */}
                  <div className="space-y-space-xs pt-space-sm">
                    <div className="flex justify-between text-label-sm text-on-surface-variant">
                      <span>Ferrous Metals (38%)</span>
                      <span>542 items</span>
                    </div>
                    <div className="w-full h-3 bg-surface-container-high rounded-full overflow-hidden flex">
                      <div className="bg-primary h-full" style={{ width: '38%' }}></div>
                      <div className="bg-secondary h-full" style={{ width: '25%' }}></div>
                      <div className="bg-tertiary h-full" style={{ width: '37%' }}></div>
                    </div>
                    <div className="flex justify-between text-label-sm text-on-surface-variant pt-1">
                      <span>Plastics & Polymers (25%)</span>
                      <span>357 items</span>
                    </div>
                  </div>
                </div>

                {/* Quick Action Card */}
                <div className="bg-primary-fixed p-space-lg rounded-xl shadow-sm space-y-space-md text-on-primary-fixed">
                  <div className="flex items-center gap-space-sm">
                    <span className="material-symbols-outlined text-[24px]">verified</span>
                    <h3 className="text-headline-md font-headline-md font-bold">Publish Patch</h3>
                  </div>
                  <p className="text-body-sm">
                    Push localized price grade changes and synonym mappings to 42 active collection yards instantly.
                  </p>
                  <button
                    onClick={handleDeployPatch}
                    className="w-full py-3 bg-primary text-on-primary font-bold rounded-xl text-label-md shadow-sm hover:opacity-95 transition-opacity"
                  >
                    Deploy Revision v4.8.3
                  </button>
                  {patchDeployed && (
                    <div className="p-2 bg-emerald-100 text-emerald-800 rounded-lg text-xs font-bold text-center">
                      Revision v4.8.3 deployed to sync cache
                    </div>
                  )}
                </div>
              </div>

              {/* Right Column: Revisions & Material Ledger Table */}
              <div className="lg:col-span-2 space-y-space-lg">
                <div className="bg-surface-container p-space-lg rounded-xl shadow-sm space-y-space-lg border border-surface-container-high">
                  <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-space-md">
                    <h2 className="text-headline-md text-on-surface font-bold">
                      Recent Material Sub-Categories
                    </h2>
                    <div className="flex items-center gap-space-sm w-full sm:w-auto">
                      <input
                        type="text"
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                        placeholder="Search material ID or name..."
                        className="bg-surface px-3 py-2 rounded-xl text-body-sm text-on-surface outline-none focus:ring-2 focus:ring-primary w-full sm:w-64 border border-surface-container-high"
                      />
                    </div>
                  </div>

                  {/* Ledger Table */}
                  <div className="overflow-x-auto">
                    <table className="w-full text-left border-collapse">
                      <thead>
                        <tr className="border-b border-surface-container-high text-label-sm text-on-surface-variant uppercase tracking-wider">
                          <th className="py-3 px-3">Code / ID</th>
                          <th className="py-3 px-3">Material Description</th>
                          <th className="py-3 px-3">Base Grade</th>
                          <th className="py-3 px-3">Benchmark</th>
                          <th className="py-3 px-3 text-right">Action</th>
                        </tr>
                      </thead>
                      <tbody className="text-body-sm text-on-surface divide-y divide-surface-container-high">
                        {[
                          { code: 'MAT-MET-01', desc: 'Heavy Melting Scrap (HMS 1&2)', grade: 'Grade A', rate: '₹34.50 / kg' },
                          { code: 'MAT-PLA-01', desc: 'HDPE Blow Molding Regrind (Blue)', grade: 'Grade B+', rate: '₹52.00 / kg' },
                          { code: 'MAT-MET-02', desc: 'Aluminium Extrusion Scrap (6063)', grade: 'Grade A', rate: '₹185.00 / kg' },
                          { code: 'MAT-PAP-01', desc: 'Corrugated Cardboard (OCC 95/5)', grade: 'Standard', rate: '₹14.20 / kg' },
                          { code: 'MAT-PCB-01', desc: 'Printed Circuit Boards (High Grade)', grade: 'Grade A', rate: '₹620.00 / kg' },
                          { code: 'MAT-BAT-01', desc: 'Lead-Acid Batteries (Isolated Route)', grade: 'Hazardous', rate: '₹92.00 / kg' },
                        ].map((m) => (
                          <tr key={m.code} className="hover:bg-surface-container-high transition-colors">
                            <td className="py-3 px-3 font-mono text-primary font-bold">{m.code}</td>
                            <td className="py-3 px-3 font-medium">{m.desc}</td>
                            <td className="py-3 px-3">
                              <span className="px-2 py-0.5 bg-secondary-fixed text-on-secondary-fixed-variant rounded text-label-sm font-semibold">
                                {m.grade}
                              </span>
                            </td>
                            <td className="py-3 px-3 font-semibold">{m.rate}</td>
                            <td className="py-3 px-3 text-right">
                              <button
                                onClick={() => alert(`Edit material ${m.code}`)}
                                className="px-3 py-1 bg-surface text-on-surface hover:bg-surface-container-highest rounded-lg text-label-sm font-bold border border-surface-container-high"
                              >
                                Edit
                              </button>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* TAB 2: ALIAS MANAGEMENT */}
        {activeTab === 'aliases' && (
          <div className="space-y-space-xl">
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-space-lg">
              {/* Alert Box for Ambiguities */}
              <div className="bg-error-container text-on-error-container p-space-lg rounded-xl shadow-sm space-y-space-md border border-error-container">
                <div className="flex items-center gap-space-sm">
                  <span className="material-symbols-outlined text-[24px]">warning</span>
                  <h3 className="text-headline-md font-headline-md font-bold">Ambiguity Queue (14)</h3>
                </div>
                <p className="text-body-sm">
                  Unmatched local slang or overlapping colloquial names reported by field collectors require canonical mapping.
                </p>
                <div className="p-3 bg-surface text-on-surface rounded-xl space-y-2 border border-surface-container">
                  <div className="flex justify-between items-center text-xs">
                    <span className="font-bold">"Kala Batri" (Hindi/Marathi)</span>
                    <span className="text-error font-mono">Unmapped</span>
                  </div>
                  <p className="text-[11px] text-on-surface-variant">Reported by 12 collectors in Delhi and Pune.</p>
                  <div className="flex gap-2 pt-1">
                    <button
                      onClick={() => alert('Mapped "Kala Batri" to MAT-BAT-01')}
                      className="px-2.5 py-1 bg-primary text-on-primary rounded text-xs font-bold"
                    >
                      Map to Lead-Acid
                    </button>
                  </div>
                </div>
              </div>

              {/* Canonical Mappings Directory */}
              <div className="lg:col-span-2 bg-surface-container p-space-lg rounded-xl shadow-sm border border-surface-container-high space-y-4">
                <h3 className="text-headline-md font-bold text-on-surface">Active Multilingual Alias Mappings</h3>
                <p className="text-xs text-on-surface-variant">
                  Standardized colloquial terms across Hindi, Marathi, and English referenced in voice assistance and offline matching.
                </p>

                <div className="space-y-2">
                  {[
                    { term: 'ताम्बे का तार / Tamba', lang: 'Hindi', canonical: 'MAT-CAB-01 (Copper Cable)' },
                    { term: 'लोहा भंगार / Loha', lang: 'Marathi/Hindi', canonical: 'MAT-MET-01 (HMS Scrap)' },
                    { term: 'गट्ठा / Gatta Cardboard', lang: 'Hindi', canonical: 'MAT-PAP-01 (OCC Cardboard)' },
                    { term: 'कम्प्यूटर बोर्ड / Motherboard', lang: 'Hindi', canonical: 'MAT-PCB-01 (High Grade PCB)' },
                  ].map((a, i) => (
                    <div key={i} className="p-3 bg-surface-container-lowest rounded-xl flex items-center justify-between border border-surface-container">
                      <div>
                        <div className="font-bold text-on-surface text-sm">{a.term}</div>
                        <span className="text-xs text-primary font-mono">{a.canonical}</span>
                      </div>
                      <span className="px-2 py-0.5 bg-surface-container-high text-xs rounded text-on-surface-variant font-medium">
                        {a.lang}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* TAB 3: PRICE MODERATION (R-PRICE-05 / AT-020) */}
        {activeTab === 'prices' && (
          <div className="space-y-space-lg">
            {/* Policy & Guardrail Notice (R-PRICE-05 / AT-020) */}
            <div className="p-4 bg-amber-50 border border-amber-200 rounded-xl flex items-start gap-3">
              <span className="material-symbols-outlined text-amber-700 text-xl shrink-0 mt-0.5">policy</span>
              <div className="text-xs text-amber-900 space-y-1">
                <span className="font-bold text-sm block">Quote Anomaly Review Policy (R-PRICE-05 / AT-020):</span>
                <p>
                  High or low quote deviations trigger administrative review <strong>only when statistically significant comparable trade data exists</strong> (calculated via 1.5x IQR against regional medians).
                </p>
                <p className="font-semibold text-amber-800">
                  CRITICAL GUARDRAIL: Anomaly alerts strictly state "Review Required". They never accuse the collector or recycler of fraud, and never unilaterally block counterparty trade choice without an explicit statutory/safety eligibility violation.
                </p>
              </div>
            </div>

            {/* Moderation Queue Table */}
            <div className="bg-surface-container p-space-lg rounded-xl shadow-sm border border-surface-container-high space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="text-headline-md font-bold text-on-surface">Price Observations Moderation Queue</h3>
                <span className="text-xs text-on-surface-variant font-mono">
                  {observations.filter((o) => o.status === 'PENDING_REVIEW').length} Pending Review
                </span>
              </div>

              <div className="space-y-3">
                {observations.map((obs) => (
                  <div
                    key={obs.id}
                    className="p-4 bg-surface-container-lowest rounded-xl border border-surface-container flex flex-col md:flex-row md:items-center justify-between gap-4"
                  >
                    <div className="space-y-1">
                      <div className="flex items-center gap-2">
                        <span className="font-mono text-xs text-primary font-bold">{obs.id}</span>
                        <span className="text-xs text-on-surface-variant">• {obs.yard}</span>
                        <span
                          className={`px-2 py-0.5 text-xs font-bold rounded ${
                            obs.status === 'APPROVED'
                              ? 'bg-emerald-100 text-emerald-800'
                              : obs.status === 'REJECTED'
                              ? 'bg-rose-100 text-rose-800'
                              : 'bg-amber-100 text-amber-800'
                          }`}
                        >
                          {obs.status}
                        </span>
                      </div>
                      <h4 className="font-bold text-on-surface text-sm">{obs.material}</h4>
                      <p className="text-xs text-on-surface-variant">{obs.reviewReason}</p>
                      <div className="text-xs flex gap-4 pt-1 font-mono">
                        <span>Reported: <strong className="text-primary">{obs.grossRate}</strong></span>
                        <span>Band: <strong>{obs.referenceRate}</strong></span>
                        <span className="text-amber-800 font-bold">{obs.deviation}</span>
                      </div>
                    </div>

                    <div className="flex items-center gap-2 shrink-0">
                      {obs.status === 'PENDING_REVIEW' ? (
                        <>
                          <button
                            onClick={() => handleModerate(obs.id, 'APPROVED')}
                            className="px-3 py-1.5 bg-emerald-700 hover:bg-emerald-800 text-white rounded-lg text-xs font-bold transition"
                          >
                            Approve Rate
                          </button>
                          <button
                            onClick={() => handleModerate(obs.id, 'REJECTED')}
                            className="px-3 py-1.5 bg-surface-container-high hover:bg-surface-dim text-on-surface rounded-lg text-xs font-bold transition border border-surface-container"
                          >
                            Quarantine
                          </button>
                        </>
                      ) : (
                        <span className="text-xs text-on-surface-variant font-mono">
                          Review Complete
                        </span>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* TAB 4: SAFETY & LANG */}
        {activeTab === 'safety' && (
          <div className="space-y-space-lg">
            <div className="bg-surface-container p-space-lg rounded-xl shadow-sm border border-surface-container-high space-y-4">
              <h3 className="text-headline-md font-bold text-on-surface">Contextual Safety Handling Guidelines</h3>
              <p className="text-xs text-on-surface-variant">
                Standard safety advisory cards displayed during collection inspection with pre-recorded audio keys.
              </p>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {[
                  {
                    title: 'Sealed Lead-Acid & Li-Ion Batteries',
                    hazard: 'Explosion & Toxic Acid Leakage',
                    audioKey: 'AUDIO_BATTERY_SAFETY_HI',
                    rule: 'Strictly isolate from bulk scrap. Never puncture, disassemble, or store near heat sources.',
                  },
                  {
                    title: 'Cathode Ray Tubes (CRT Monitors)',
                    hazard: 'Implosion & Toxic Lead Dust',
                    audioKey: 'AUDIO_CRT_SAFETY_HI',
                    rule: 'Do not crush glass funnel. Handle with gloves and protective face shield.',
                  },
                  {
                    title: 'Capacitors & Transformer Oils',
                    hazard: 'Polychlorinated Biphenyls (PCBs)',
                    audioKey: 'AUDIO_TRANSFORMER_SAFETY_MR',
                    rule: 'Inspect for chemical oil leaks. Route exclusively to authorized hazardous waste facility.',
                  },
                  {
                    title: 'Refrigerant Compressors',
                    hazard: 'Pressurized Gas & Ozone Depletion',
                    audioKey: 'AUDIO_COMPRESSOR_SAFETY_HI',
                    rule: 'Do not shear copper pipe until refrigerant gas has been recovered in certified recovery unit.',
                  },
                ].map((s, i) => (
                  <div key={i} className="p-4 bg-surface-container-lowest rounded-xl border border-surface-container space-y-2">
                    <div className="flex justify-between items-start">
                      <h4 className="font-bold text-on-surface text-sm">{s.title}</h4>
                      <span className="px-2 py-0.5 bg-rose-100 text-rose-800 text-[10px] font-bold rounded">
                        {s.hazard}
                      </span>
                    </div>
                    <p className="text-xs text-on-surface-variant">{s.rule}</p>
                    <div className="flex items-center gap-2 pt-1">
                      <span className="material-symbols-outlined text-primary text-[16px]">volume_up</span>
                      <span className="text-[11px] font-mono text-primary font-semibold">{s.audioKey}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
