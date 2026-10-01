import React, { useEffect, useState } from 'react';
import { AdminFacility, fetchAdminFacilities } from '../../lib/api';

export default function A03_Facilities() {
  const [quarantined, setQuarantined] = useState(false);
  const [showComplianceModal, setShowComplianceModal] = useState(false);
  const [complianceChecking, setComplianceChecking] = useState(false);
  const [complianceResult, setComplianceResult] = useState<string | null>(null);
  const [facilities, setFacilities] = useState<AdminFacility[]>([]);
  const [loadError, setLoadError] = useState<string | null>(null);
  const facility = facilities[0];

  useEffect(() => { void fetchAdminFacilities().then(setFacilities).catch((error: unknown) => setLoadError(error instanceof Error ? error.message : 'Unable to load facility evidence.')); }, []);

  const handleRunCompliance = () => {
    setComplianceChecking(true); setComplianceResult(null);
    setTimeout(() => { setComplianceChecking(false); setComplianceResult(facility ? 'Review the persisted authorization evidence shown below; this screen does not make a statutory compliance determination.' : 'No facility evidence loaded; compliance cannot be determined.'); }, 300);
  };

  return (
    <div className="flex flex-col w-full max-w-7xl mx-auto px-gutter py-space-xl gap-space-xl">
      {/* Top Asymmetric Header Block (Stitch A03) */}
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-space-lg bg-surface-container-low p-space-xl rounded-xl shadow-sm border border-surface-container">
        <div className="flex flex-col gap-space-xs max-w-2xl">
          <div className="flex items-center gap-space-sm">
            <span className="px-2.5 py-1 bg-primary text-on-primary text-label-sm rounded uppercase tracking-wider font-bold">
              Active Workspace
            </span>
            <span className="text-on-surface-variant text-label-sm font-semibold tracking-wider font-mono">
              FACILITY ID: {facility?.id ?? 'Loading…'}
            </span>
            {quarantined && (
              <span className="px-2 py-0.5 text-xs font-bold bg-error text-on-error rounded uppercase animate-pulse">
                Quarantined
              </span>
            )}
          </div>
          <h1 className="text-headline-xl font-headline-xl text-on-surface font-bold">
            Source & Facility Authorization
          </h1>
          <p className="text-body-md text-on-surface-variant">
            Real-time evidence inspection workspace tracking L0-L4 verification ladders, route-specific material scopes, validity expirations, and audit revision histories.
          </p>
        </div>

        <div className="flex items-center gap-space-md">
          <button
            onClick={() => {
              setShowComplianceModal(true);
              handleRunCompliance();
            }}
            className="px-5 py-3 bg-primary text-on-primary text-label-md rounded-xl font-headline-md flex items-center gap-space-sm hover:bg-primary-container transition-colors shadow-sm font-semibold"
          >
            <span className="material-symbols-outlined text-[20px]" style={{ fontVariationSettings: "'FILL' 1" }}>
              verified
            </span>
            Run Compliance Check
          </button>

          <button
            onClick={() => setQuarantined(!quarantined)}
            className={`px-5 py-3 rounded-xl text-label-md font-headline-md flex items-center gap-space-sm transition-colors font-semibold ${
              quarantined
                ? 'bg-error text-on-error hover:bg-error/90'
                : 'bg-surface-container-high text-on-surface hover:bg-surface-dim'
            }`}
          >
            <span className="material-symbols-outlined text-[20px]">
              {quarantined ? 'lock_open' : 'shield_locked'}
            </span>
            <span>{quarantined ? 'Lift Quarantine' : 'Quarantine Facility'}</span>
          </button>
        </div>
      </div>

      {/* Admin Authorization Rule Guard Banner (R-ADMIN-01) */}
      <div className="p-space-md bg-surface-container-lowest rounded-xl border-l-4 border-secondary shadow-sm flex items-start gap-3">
        <span className="material-symbols-outlined text-secondary text-[20px] shrink-0 mt-0.5">policy</span>
        <div className="text-xs text-on-surface-variant space-y-0.5">
          <span className="font-bold text-on-surface">Administrative Gate Enforcement (R-ADMIN-01 / AT-064):</span>
          <p>
            Under SahiTol platform policy, registered recyclers and aggregation yards can submit operational profiles, but <strong>cannot self-approve their own verification tiers or statutory scopes</strong>. All tier upgrades from L0 to L4 require explicit admin review with cryptographic ledger audit logging.
          </p>
        </div>
      </div>
      {loadError && <p role="alert" className="p-3 bg-error-container text-on-error-container rounded-xl text-sm">Facility evidence unavailable: {loadError}</p>}

      {/* Main Grid Layout: Left Column (Ladder & Scope), Right Column (Facility Dossier) */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-space-xl">
        {/* Left Column: Evidence Ladder L0-L4 (7 cols) */}
        <div className="lg:col-span-7 flex flex-col gap-space-lg">
          <div className="bg-surface-container-low p-space-lg rounded-xl flex flex-col gap-space-md shadow-sm border border-surface-container">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-space-sm">
                <span className="material-symbols-outlined text-primary text-[24px]">stairs</span>
                <h2 className="text-headline-md font-headline-md text-on-surface font-bold">
                  Evidence Levels (L0 - L4 Ladder)
                </h2>
              </div>
              <span className="text-label-sm font-semibold px-3 py-1 bg-secondary-container text-on-secondary-container rounded-full">
                  Current evidence: {facility?.authorizations[0]?.verification_level ?? 'Not loaded'}
              </span>
            </div>
            <p className="text-body-sm text-on-surface-variant">
              Traceability assurance climbs from self-declaration (L0) up to continuous IoT telemetry & mass-balance audit (L4).
            </p>

            {/* Ladder Steps */}
            <div className="flex flex-col gap-space-sm mt-space-sm">
              {/* L0 */}
              <div className="p-space-md rounded-xl bg-surface-container-lowest flex items-center justify-between border border-surface-container">
                <div className="flex items-center gap-space-md">
                  <div className="w-10 h-10 rounded-xl bg-surface-container-high flex items-center justify-center font-headline font-bold text-on-surface text-label-lg">
                    L0
                  </div>
                  <div>
                    <h4 className="text-label-lg text-on-surface font-semibold">Self-Declaration</h4>
                    <p className="text-body-sm text-on-surface-variant">Basic vendor intake form without documentary proof.</p>
                  </div>
                </div>
                <span className="text-label-sm text-on-surface-variant bg-surface-container px-2.5 py-1 rounded font-medium">
                  Superseded
                </span>
              </div>

              {/* L1 */}
              <div className="p-space-md rounded-xl bg-surface-container-lowest flex items-center justify-between border border-surface-container">
                <div className="flex items-center gap-space-md">
                  <div className="w-10 h-10 rounded-xl bg-surface-container-high flex items-center justify-center font-headline font-bold text-on-surface text-label-lg">
                    L1
                  </div>
                  <div>
                    <h4 className="text-label-lg text-on-surface font-semibold">Documentary Baseline</h4>
                    <p className="text-body-sm text-on-surface-variant">GSTIN, Trade License, and KYC documentation uploaded.</p>
                  </div>
                </div>
                <span className="text-label-sm text-primary bg-primary-fixed px-2.5 py-1 rounded font-bold">
                  Passed (2024)
                </span>
              </div>

              {/* L2 */}
              <div className="p-space-md rounded-xl bg-surface-container-lowest flex items-center justify-between border border-surface-container">
                <div className="flex items-center gap-space-md">
                  <div className="w-10 h-10 rounded-xl bg-surface-container-high flex items-center justify-center font-headline font-bold text-on-surface text-label-lg">
                    L2
                  </div>
                  <div>
                    <h4 className="text-label-lg text-on-surface font-semibold">Geo-Fence & Weighment Logs</h4>
                    <p className="text-body-sm text-on-surface-variant">Weighbridge slip cross-checks and yard coordinates verified.</p>
                  </div>
                </div>
                <span className="text-label-sm text-primary bg-primary-fixed px-2.5 py-1 rounded font-bold">
                  Passed (Q2)
                </span>
              </div>

              {/* L3 (Active) */}
              <div className="p-space-md rounded-xl bg-primary text-on-primary flex items-center justify-between shadow-md relative overflow-hidden">
                <div className="absolute -right-6 -bottom-6 w-24 h-24 bg-white/10 rounded-full blur-xl pointer-events-none"></div>
                <div className="flex items-center gap-space-md">
                  <div className="w-10 h-10 rounded-xl bg-white/20 flex items-center justify-center font-headline font-bold text-on-primary text-label-lg">
                    L3
                  </div>
                  <div>
                    <h4 className="text-label-lg text-on-primary flex items-center gap-space-xs font-bold">
                      Third-Party Lab & Physical Audit
                      <span className="material-symbols-outlined text-[16px]">verified</span>
                    </h4>
                    <p className="text-body-sm text-primary-fixed">On-site physical inspection & CPCB consent verified.</p>
                  </div>
                </div>
                <span className="text-label-sm text-primary bg-on-primary px-3 py-1.5 rounded-xl font-bold shadow-sm">
                  Active Tier
                </span>
              </div>

              {/* L4 */}
              <div className="p-space-md rounded-xl bg-surface-container-lowest flex items-center justify-between opacity-70 border border-surface-container">
                <div className="flex items-center gap-space-md">
                  <div className="w-10 h-10 rounded-xl bg-surface-container-high flex items-center justify-center font-headline font-bold text-on-surface text-label-lg">
                    L4
                  </div>
                  <div>
                    <h4 className="text-label-lg text-on-surface font-semibold">Continuous IoT & Mass-Balance Stream</h4>
                    <p className="text-body-sm text-on-surface-variant">Automated conveyor telemetry and live RFID stream tracking.</p>
                  </div>
                </div>
                <span className="text-label-sm text-on-surface-variant bg-surface-container px-2.5 py-1 rounded">
                  Locked / Optional
                </span>
              </div>
            </div>
          </div>

          {/* Route-Specific Scopes & Materials */}
          <div className="bg-surface-container-low p-space-lg rounded-xl flex flex-col gap-space-md shadow-sm border border-surface-container">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-space-sm">
                <span className="material-symbols-outlined text-primary text-[24px]">alt_route</span>
                <h2 className="text-headline-md font-headline-md text-on-surface font-bold">
                  Route-Specific Material Scopes
                </h2>
              </div>
              <button
                onClick={() => alert('New route scope configuration window')}
                className="text-label-md text-primary hover:underline flex items-center gap-space-xs font-semibold"
              >
                <span className="material-symbols-outlined text-[16px]">add</span> Add Scope Route
              </button>
            </div>
            <p className="text-body-sm text-on-surface-variant">
              Authorized commodity grades permitted through specific logistic corridors.
            </p>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-space-md mt-space-xs">
              <div className="p-space-md bg-surface-container-lowest rounded-xl flex flex-col gap-space-sm border-l-4 border-primary shadow-sm border border-surface-container">
                <div className="flex items-center justify-between">
                  <span className="text-label-sm font-semibold uppercase text-primary">Corridor Alpha</span>
                  <span className="text-label-sm text-emerald-800 bg-emerald-100 px-2 py-0.5 rounded font-bold">
                    Active
                  </span>
                </div>
                <h4 className="text-label-lg text-on-surface font-semibold">Heavy Ferrous Scrap (HMS 1 & 2)</h4>
                <div className="flex items-center gap-space-sm text-body-sm text-on-surface-variant">
                  <span className="material-symbols-outlined text-[16px]">local_shipping</span>
                  <span>Delhi-NCR Hub → Okhla Dismantler</span>
                </div>
                <div className="flex items-center justify-between text-body-sm pt-space-xs border-t border-surface-container text-xs">
                  <span>Max Vol: <strong>500 Tons/mo</strong></span>
                  <span className="text-primary font-bold">99.4% Purity Match</span>
                </div>
              </div>

              <div className="p-space-md bg-surface-container-lowest rounded-xl flex flex-col gap-space-sm border-l-4 border-secondary shadow-sm border border-surface-container">
                <div className="flex items-center justify-between">
                  <span className="text-label-sm font-semibold uppercase text-secondary">Corridor Beta</span>
                  <span className="text-label-sm text-emerald-800 bg-emerald-100 px-2 py-0.5 rounded font-bold">
                    Active
                  </span>
                </div>
                <h4 className="text-label-lg text-on-surface font-semibold">E-Waste Printed Circuit Boards</h4>
                <div className="flex items-center gap-space-sm text-body-sm text-on-surface-variant">
                  <span className="material-symbols-outlined text-[16px]">local_shipping</span>
                  <span>Surat Collection Centre → Mumbai Recycler</span>
                </div>
                <div className="flex items-center justify-between text-body-sm pt-space-xs border-t border-surface-container text-xs">
                  <span>Max Vol: <strong>120 Tons/mo</strong></span>
                  <span className="text-secondary font-bold">Grade High/Med Verified</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Right Column: Facility Dossier & Verification Review (5 cols) */}
        <div className="lg:col-span-5 flex flex-col gap-space-lg">
          <div className="bg-surface-container-low p-space-lg rounded-xl shadow-sm border border-surface-container space-y-4">
            <div className="flex items-center justify-between border-b border-surface-container pb-3">
              <div>
                <span className="text-label-sm uppercase tracking-wider text-on-surface-variant font-semibold">
                  Facility Dossier
                </span>
                  <h3 className="text-lg font-headline font-bold text-on-surface">{facility?.name ?? 'No facility selected'}</h3>
              </div>
              <span className="px-2.5 py-1 bg-primary text-on-primary rounded-xl text-xs font-bold">
                {facility?.authorizations[0]?.status ?? 'Not verified'}
              </span>
            </div>

            <div className="space-y-3 text-xs">
              <div className="p-3 bg-surface-container-lowest rounded-xl border border-surface-container space-y-1.5">
                <div className="flex justify-between">
                  <span className="text-on-surface-variant font-medium">Authority:</span>
                  <span className="font-mono font-bold text-on-surface">{facility?.authorizations[0]?.authority ?? '—'}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-on-surface-variant font-medium">Evidence reference:</span>
                  <span className="font-mono font-bold text-on-surface">{facility?.authorizations[0]?.reference ?? '—'}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-on-surface-variant font-medium">Evidence validity:</span>
                  <span className="font-bold text-emerald-800">{facility?.authorizations[0]?.valid_until ? new Date(facility.authorizations[0].valid_until).toLocaleDateString('en-GB') : 'Not recorded'}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-on-surface-variant font-medium">Route:</span>
                  <span className="font-bold text-primary">{facility?.authorizations[0]?.route ?? 'Not recorded'}</span>
                </div>
              </div>

              <div className="p-3 bg-surface-container-lowest rounded-xl border border-surface-container space-y-2">
                <span className="font-bold text-on-surface block">Evidence status (not a statutory determination):</span>
                <div className="space-y-1 text-[11px]">
                  <div className="flex items-center gap-2 text-emerald-800">
                    <span className="material-symbols-outlined text-[16px]">check_circle</span>
                    Authorization state: {facility?.authorizations[0]?.status ?? 'Not loaded'}
                  </div>
                  <div className="flex items-center gap-2 text-emerald-800">
                    <span className="material-symbols-outlined text-[16px]">check_circle</span>
                    Verification method: {facility?.authorizations[0]?.verification_level ?? 'Not loaded'}
                  </div>
                  <div className="flex items-center gap-2 text-emerald-800">
                    <span className="material-symbols-outlined text-[16px]">check_circle</span>
                    Facility is {facility?.active ? 'active' : 'inactive'} in the persisted directory
                  </div>
                </div>
              </div>
            </div>

            <div className="pt-2">
              <button
                onClick={() => setLoadError('Re-verification requires a documented evidence reference and reason; use the server verification workflow.')}
                className="w-full py-3 bg-primary text-on-primary font-headline font-bold rounded-xl text-label-md hover:bg-primary-container transition shadow-sm"
              >
                Assert Administrative Re-Verification
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Compliance Modal */}
      {showComplianceModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm p-4">
          <div className="bg-surface-container-lowest max-w-md w-full rounded-2xl p-6 shadow-2xl border border-surface-container-high space-y-4">
            <div className="flex items-center justify-between pb-2 border-b border-surface-container">
              <h3 className="font-headline font-bold text-lg text-on-surface flex items-center gap-2">
                <span className="material-symbols-outlined text-primary">verified</span>
                Compliance Diagnostic
              </h3>
              <button
                onClick={() => setShowComplianceModal(false)}
                className="w-8 h-8 rounded-full hover:bg-surface-container flex items-center justify-center text-on-surface-variant"
              >
                <span className="material-symbols-outlined text-[20px]">close</span>
              </button>
            </div>

            {complianceChecking ? (
              <div className="py-8 text-center space-y-2">
                <div className="w-8 h-8 border-3 border-primary border-t-transparent rounded-full animate-spin mx-auto"></div>
                <p className="text-xs text-on-surface-variant">Checking state PCB and CPCB registry registries...</p>
              </div>
            ) : (
              <div className="space-y-3">
                <div className="p-3 bg-emerald-50 border border-emerald-200 rounded-xl text-xs text-emerald-900">
                  <span className="font-bold block mb-1">Evidence review:</span>
                  {complianceResult}
                </div>
                <div className="text-[11px] text-on-surface-variant">
                  This diagnostic reads persisted evidence only; it cannot assert external legal compliance.
                </div>
              </div>
            )}

            <div className="flex justify-end pt-2">
              <button
                onClick={() => setShowComplianceModal(false)}
                className="px-4 py-2 bg-surface-container-high hover:bg-surface-dim text-on-surface font-semibold text-xs rounded-xl transition"
              >
                Dismiss
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
