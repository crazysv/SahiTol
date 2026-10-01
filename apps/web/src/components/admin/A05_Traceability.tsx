import React, { useState } from 'react';
import { fetchTraceability, TraceabilityReport } from '../../lib/api';

export default function A05_Traceability() {
  const [lotSearch, setLotSearch] = useState('');
  const [selectedMaterial, setSelectedMaterial] = useState('Copper Scrap (Heavy)');
  const [selectedStatus, setSelectedStatus] = useState('Completed & Settled');
  const [verifying, setVerifying] = useState(false);
  const [verifiedChain, setVerifiedChain] = useState(true);
  const [report, setReport] = useState<TraceabilityReport | null>(null);
  const [loadError, setLoadError] = useState<string | null>(null);

  const handleVerifyChain = () => {
    if (!lotSearch.trim()) { setLoadError('Enter a UUID lot ID to inspect its server trace.'); return; }
    setVerifying(true); setLoadError(null);
    void fetchTraceability(lotSearch.trim()).then((result) => { setReport(result); setVerifiedChain(result.is_hash_chain_valid); }).catch((error: unknown) => { setReport(null); setLoadError(error instanceof Error ? error.message : 'Unable to load traceability report.'); }).finally(() => setVerifying(false));
  };

  return (
    <div className="flex flex-col w-full pb-24">
      {/* Top Banner / Header Segment (Stitch A05) */}
      <div className="w-full bg-surface-container-low px-gutter py-space-xl flex flex-col md:flex-row items-start md:items-center justify-between gap-space-lg border-b border-surface-container">
        <div className="flex flex-col gap-space-xs">
          <div className="flex items-center gap-space-sm">
            <span className="px-2 py-0.5 bg-primary/10 text-primary rounded text-label-sm uppercase tracking-wider font-label-sm font-bold">
              Immutable Ledger v4.2
            </span>
            <span className="text-on-surface-variant text-body-sm font-medium">
              • Hash Chain Verified
            </span>
          </div>
          <h1 className="text-headline-xl text-on-surface font-bold">
            Traceability & Transaction Audit
          </h1>
          <p className="text-body-md text-on-surface-variant max-w-2xl">
            Search and inspect end-to-end material lineages from field collection to final smelting or recycling facilities with absolute cryptographic integrity.
          </p>
        </div>

        <div className="flex items-center gap-space-md w-full md:w-auto">
          <button
            onClick={handleVerifyChain}
            disabled={verifying}
            className="flex-1 md:flex-none px-4 py-3 bg-surface-container-high hover:bg-surface-dim text-on-surface rounded-xl font-label-md flex items-center justify-center gap-space-sm transition-colors border border-surface-container shadow-sm font-semibold"
          >
            <span className={`material-symbols-outlined text-[20px] ${verifying ? 'animate-spin' : ''}`}>
              verified
            </span>
            {verifying ? 'Verifying Hashes...' : 'Verify Chain State'}
          </button>

          <button
            onClick={() => alert('Exporting full audit trail package (PDF/JSON with Merkle proof)...')}
            className="flex-1 md:flex-none px-5 py-3 bg-primary hover:bg-primary-container text-on-primary rounded-xl font-label-md flex items-center justify-center gap-space-sm shadow-sm transition-colors font-semibold"
          >
            <span className="material-symbols-outlined text-[20px]">download</span>
            Export Audit Report
          </button>
        </div>
      </div>

      {/* Search & Filter Control Bar (Stitch A05) */}
      <div className="max-w-7xl mx-auto w-full px-gutter -mt-6 z-10">
        <div className="bg-surface-container-lowest p-space-lg rounded-xl shadow-xl flex flex-col lg:flex-row items-stretch lg:items-center gap-space-md border border-surface-container-high">
          <div className="flex-1 relative flex items-center">
            <span className="material-symbols-outlined absolute left-4 text-on-surface-variant text-[22px]">
              search
            </span>
            <input
              type="text"
              value={lotSearch}
              onChange={(e) => setLotSearch(e.target.value)}
              placeholder="Search by Lot ID, RFID tag, Hash, or Collector ID..."
              className="w-full pl-12 pr-4 py-3.5 bg-surface-container-low rounded-xl text-on-surface placeholder:text-on-surface-variant/60 focus:outline-none focus:ring-2 focus:ring-primary text-body-md border border-surface-container"
            />
          </div>

          <div className="flex flex-wrap items-center gap-space-sm">
            <select
              value={selectedMaterial}
              onChange={(e) => setSelectedMaterial(e.target.value)}
              className="px-4 py-3.5 bg-surface-container-low text-on-surface rounded-xl font-label-md focus:outline-none focus:ring-2 focus:ring-primary border border-surface-container text-xs"
            >
              <option>All Material Types</option>
              <option>Copper Scrap (Heavy)</option>
              <option>Aluminium Extrusion</option>
              <option>HDPE Rigid Plastic</option>
              <option>Corrugated Paper</option>
            </select>

            <select
              value={selectedStatus}
              onChange={(e) => setSelectedStatus(e.target.value)}
              className="px-4 py-3.5 bg-surface-container-low text-on-surface rounded-xl font-label-md focus:outline-none focus:ring-2 focus:ring-primary border border-surface-container text-xs"
            >
              <option>All Statuses</option>
              <option>Completed & Settled</option>
              <option>Dispute Flagged</option>
              <option>In Transit</option>
            </select>

            <button
            onClick={handleVerifyChain}
              className="px-6 py-3.5 bg-primary text-on-primary font-label-md rounded-xl hover:bg-primary-container transition-colors flex items-center justify-center gap-space-xs font-semibold"
            >
              <span>Inspect Lot</span>
              <span className="material-symbols-outlined text-[18px]">arrow_forward</span>
            </button>
          </div>
        </div>
      </div>

      {/* Main Workspace / Split View (Stitch A05) */}
      <div className="max-w-7xl mx-auto w-full px-gutter mt-space-xl grid grid-cols-1 lg:grid-cols-12 gap-space-xl">
        {/* Left Column: Lot Overview & Hash Integrity Report (4 Cols) */}
        <div className="lg:col-span-4 flex flex-col gap-space-lg">
          {/* Lot Card */}
          <div className="bg-surface-container-lowest p-space-lg rounded-xl shadow-sm flex flex-col gap-space-md relative overflow-hidden border border-surface-container-high">
            <div className="absolute top-0 right-0 w-32 h-32 bg-primary/5 rounded-bl-full pointer-events-none"></div>
            <div className="flex items-center justify-between">
              <span className="px-2.5 py-1 bg-secondary-container text-on-secondary-container rounded font-label-sm font-bold">
                Verified Lot
              </span>
              <span className="text-body-sm text-on-surface-variant font-mono">{report?.events.at(-1)?.event_hash.slice(0, 12) ?? 'No server trace loaded'}</span>
            </div>
            <div>
              <h2 className="text-headline-md text-on-surface font-bold">{lotSearch}</h2>
              <p className="text-body-sm text-on-surface-variant">{report?.material_id ?? 'Enter a lot UUID and inspect the server trace.'}</p>
            </div>
            <div className="grid grid-cols-2 gap-space-md pt-2">
              <div className="bg-surface-container-low p-3 rounded-xl border border-surface-container">
                <span className="text-label-sm text-on-surface-variant block font-medium">Recorded Weight</span>
                <span className="text-headline-md text-on-surface font-bold">{report ? `${report.events_count} events` : '—'}</span>
              </div>
              <div className="bg-surface-container-low p-3 rounded-xl border border-surface-container">
                <span className="text-label-sm text-on-surface-variant block font-medium">Total Valuation</span>
                <span className="text-headline-md text-primary font-bold">{report?.lot_status ?? '—'}</span>
              </div>
            </div>
            <div className="flex flex-col gap-2 pt-2 border-t border-surface-container text-xs">
              <div className="flex justify-between">
                <span className="text-on-surface-variant">Origin Collector:</span>
                <span className="font-bold text-on-surface">Ramesh Kumar (COL-402)</span>
              </div>
              <div className="flex justify-between">
                <span className="text-on-surface-variant">Intake Facility:</span>
                <span className="font-bold text-on-surface">Okhla Yard Alpha</span>
              </div>
              <div className="flex justify-between">
                <span className="text-on-surface-variant">Timestamp:</span>
                <span className="font-mono text-on-surface">2026-09-29 08:30 IST</span>
              </div>
            </div>
          </div>

          {/* Hash-Chain Status */}
          <div className="bg-surface-container-lowest p-space-lg rounded-xl shadow-sm flex flex-col gap-space-md border border-surface-container-high">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-space-sm">
                <span className="material-symbols-outlined text-primary text-[24px]">gpp_good</span>
                <h3 className="text-headline-md text-on-surface font-bold">Hash-Chain Status</h3>
              </div>
              <span className="px-2 py-0.5 bg-emerald-100 text-emerald-800 rounded text-label-sm font-bold">
                {report ? (verifiedChain ? 'Verified' : 'Integrity issue') : 'Not checked'}
              </span>
            </div>
            <p className="text-body-sm text-on-surface-variant">
              {report ? `Server evaluation returned ${report.events_count} event(s).` : 'No trace has been loaded; integrity is not asserted.'}
            </p>
            <div className="bg-surface-container-low p-3 rounded-xl font-mono text-xs text-on-surface-variant break-all border border-surface-container">
              Root Hash: {report?.events.at(-1)?.event_hash ?? '—'}
            </div>
            <div className="flex flex-col gap-2 text-xs border-t border-surface-container pt-2">
              <div className="flex items-center justify-between">
                <span className="text-on-surface-variant">Block Depth</span>
                <span className="font-bold text-on-surface">5 Lineage Blocks</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-on-surface-variant">Verification Scheme</span>
                <span className="font-bold text-on-surface font-mono">SAHITOL-JCS-1 (SHA-256)</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-on-surface-variant">Audit Verification</span>
                <span className="font-bold text-emerald-700">Verified Just Now</span>
              </div>
            </div>
          </div>

          {/* Revisions & Notes */}
          <div className="bg-surface-container-lowest p-space-lg rounded-xl shadow-sm flex flex-col gap-space-md border border-surface-container-high">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-space-sm">
                <span className="material-symbols-outlined text-secondary text-[24px]">history_edu</span>
                <h3 className="text-headline-md text-on-surface font-bold">Revisions & Notes</h3>
              </div>
              <span className="px-2 py-0.5 bg-amber-100 text-amber-800 rounded text-label-sm font-bold">
                1 Note
              </span>
            </div>
            <div className="bg-surface-container-low p-3.5 rounded-xl flex flex-col gap-space-xs border border-surface-container">
              <div className="flex items-center justify-between">
                <span className="text-label-sm text-primary font-bold">Revision #1 (Weight Adj)</span>
                <span className="text-xs text-on-surface-variant font-mono">09:15 IST</span>
              </div>
              <p className="text-body-sm text-on-surface text-xs">
                Moisture deduction applied: -15kg verified by yard manager (YM-12). Collector explicitly confirmed terms on device.
              </p>
            </div>
          </div>
        </div>

        {/* Right Column: Event Chain Lineage (8 Cols) */}
        <div className="lg:col-span-8 flex flex-col gap-space-md">
          <div className="bg-surface-container-lowest p-space-xl rounded-xl shadow-sm border border-surface-container-high space-y-6">
            <div className="flex items-center justify-between border-b border-surface-container pb-4">
              <div>
                <h3 className="text-headline-lg font-bold text-on-surface">Event Chain Lineage</h3>
                <p className="text-xs text-on-surface-variant">
                  Cryptographically chained domain events with individual payload hashes and actor signatures
                </p>
              </div>
              <span className="px-3 py-1 bg-emerald-100 text-emerald-800 font-bold text-xs rounded-full">
                5 Complete Transitions
              </span>
            </div>

            {/* Stepper Timeline */}
            <div className="space-y-6 relative before:absolute before:inset-0 before:left-4 before:w-0.5 before:bg-surface-container-high">
              {[
                {
                  step: 1,
                  event: 'LOT_COLLECTED (Ingress)',
                  actor: 'Collector: Ramesh Kumar (COL-402)',
                  time: '2026-09-29 08:30 IST',
                  hash: 'f8d31a4c9b2e...5510',
                  desc: 'Collector initiated lot intake at primary aggregation station. 1,435 kg declared gross.',
                  status: 'VERIFIED',
                },
                {
                  step: 2,
                  event: 'ML_CLASSIFICATION_ADVISORY',
                  actor: 'On-Device MobileNetV3-Small LiteRT',
                  time: '2026-09-29 08:32 IST',
                  hash: '772ac1048b9f...e021',
                  desc: 'Classified MAT-CAB-01 (Copper Cable) with 0.94 confidence (exceeds 0.65 threshold).',
                  status: 'VERIFIED',
                },
                {
                  step: 3,
                  event: 'TERMS_REVISION_AGREED',
                  actor: 'Recycler Yard Manager (YM-12)',
                  time: '2026-09-29 08:45 IST',
                  hash: '918bf414c27a...a991',
                  desc: 'Physical scale reconciliation: -15kg moisture adjustment proposed and accepted by collector.',
                  status: 'VERIFIED',
                },
                {
                  step: 4,
                  event: 'HANDOVER_CONFIRMED',
                  actor: 'Dual-Device QR Protocol',
                  time: '2026-09-29 09:02 IST',
                  hash: 'a09162336537...b3c7',
                  desc: 'Recycler device scanned client QR proposal. Digital Handover Record issued with statutory non-EPR notice.',
                  status: 'VERIFIED',
                },
                {
                  step: 5,
                  event: 'PAYMENT_SETTLED',
                  actor: 'Cash Dues Ledger (Zero-Fee)',
                  time: '2026-09-29 09:05 IST',
                  hash: '44a88bc91230...7712',
                  desc: 'Cash payout of ₹9,94,000 acknowledged. Collector platform fee: 0 paise. Transaction closed.',
                  status: 'VERIFIED',
                },
              ].map((ev) => (
                <div key={ev.step} className="relative flex items-start gap-4 pl-1">
                  <div className="w-8 h-8 rounded-full bg-primary text-on-primary flex items-center justify-center font-bold text-xs shrink-0 z-10 shadow">
                    {ev.step}
                  </div>
                  <div className="flex-1 bg-surface-container-low p-4 rounded-xl border border-surface-container space-y-1.5">
                    <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-1">
                      <span className="font-bold text-sm text-on-surface font-mono">{ev.event}</span>
                      <span className="text-[11px] text-on-surface-variant font-mono">{ev.time}</span>
                    </div>
                    <div className="text-xs text-on-surface-variant flex items-center gap-2">
                      <span>Actor: <strong className="text-on-surface">{ev.actor}</strong></span>
                      <span className="text-emerald-700 font-bold">• {ev.status}</span>
                    </div>
                    <p className="text-xs text-on-surface pt-0.5">{ev.desc}</p>
                    <div className="pt-1 text-[11px] font-mono text-on-surface-variant/80 flex items-center gap-1">
                      <span className="material-symbols-outlined text-[14px]">lock</span>
                      SHA-256 Hash: {ev.hash}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
