import React, { useState } from 'react';
import { useNavigate, useSearchParams, Link } from 'react-router-dom';

export default function R02_IncomingLot() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const lotRef = searchParams.get('ref') || 'ST-24A7';

  const [verifiedWeight, setVerifiedWeight] = useState(84.8);
  const declaredWeight = 85.5;
  const varianceKg = (verifiedWeight - declaredWeight).toFixed(1);
  const variancePercent = (((verifiedWeight - declaredWeight) / declaredWeight) * 100).toFixed(2);

  return (
    <div className="space-y-space-lg">
      {/* Header breadcrumb & Actions */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-space-md pb-space-sm border-b border-surface-container-high">
        <div>
          <div className="flex items-center gap-2 text-xs text-on-surface-variant mb-1">
            <Link to="/recycler" className="hover:underline flex items-center gap-1">
              <span className="material-symbols-outlined text-[16px]">arrow_back</span> Back to Inbox
            </Link>
            <span>/</span>
            <span>Inspection</span>
          </div>
          <h2 className="text-2xl lg:text-3xl font-headline font-bold text-on-surface">
            Lot Inspection Workspace: <span className="text-primary font-mono">{lotRef}</span>
          </h2>
        </div>

        <div className="flex items-center gap-space-sm">
          <div className="px-space-md py-1.5 bg-secondary-container text-on-secondary-container rounded-lg text-xs font-headline font-bold flex items-center gap-1 shadow-sm">
            <span className="material-symbols-outlined text-[16px]">verified</span>
            Route Authorized
          </div>
          <div className="px-space-md py-1.5 bg-surface-container-high text-on-surface-variant rounded-lg text-xs font-headline">
            Yard #402 Okhla
          </div>
        </div>
      </div>

      {/* Main Asymmetric Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-space-lg">
        {/* Left Column: Photo & Provenance (7 cols) */}
        <div className="lg:col-span-7 flex flex-col gap-space-md">
          {/* Photo & Scale Capture Card */}
          <div className="bg-surface-container-low rounded-xl p-space-md shadow-sm border border-surface-container-high flex flex-col gap-space-md">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <span className="material-symbols-outlined text-primary text-[20px]">photo_camera</span>
                <span className="text-sm font-headline font-bold text-on-surface">Live Scale Capture</span>
              </div>
              <span className="px-2 py-0.5 bg-surface-container-highest text-on-surface-variant rounded text-xs">
                Timestamp: Today 14:02
              </span>
            </div>

            {/* Photo placeholder frame styled as inspection camera */}
            <div className="relative w-full h-72 sm:h-80 rounded-lg overflow-hidden bg-surface-container flex items-center justify-center border border-surface-container-high">
              <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-transparent to-transparent z-10"></div>
              {/* Graphic container simulating photo capture */}
              <div className="w-full h-full bg-cover bg-center flex items-center justify-center text-center p-6 bg-surface-container-high">
                <div className="space-y-2">
                  <span className="material-symbols-outlined text-primary text-5xl">inventory_2</span>
                  <div className="text-sm font-headline font-semibold text-on-surface">
                    Insulated Copper Wire (55% Recovery Standard)
                  </div>
                  <div className="text-xs text-on-surface-variant">
                    Image captured via SahiTol Android Collector app (SHA-256 verified)
                  </div>
                </div>
              </div>

              <div className="absolute bottom-3 left-3 z-20 px-3 py-1 bg-surface/90 backdrop-blur-md rounded-lg flex items-center gap-2 text-xs font-headline font-semibold text-on-surface">
                <span className="w-2 h-2 rounded-full bg-emerald-600 animate-pulse"></span>
                Digital Platform Scale #4 Connected
              </div>
            </div>

            {/* Metrics scan row */}
            <div className="grid grid-cols-3 gap-space-sm pt-space-xs text-center">
              <div className="bg-surface-container p-space-sm rounded-lg">
                <span className="text-xs text-on-surface-variant block">Condition Scan</span>
                <span className="text-sm font-headline font-bold text-on-surface">Good Grade A</span>
              </div>
              <div className="bg-surface-container p-space-sm rounded-lg">
                <span className="text-xs text-on-surface-variant block">Impurities</span>
                <span className="text-sm font-headline font-bold text-on-surface">&lt; 1.2% Est.</span>
              </div>
              <div className="bg-surface-container p-space-sm rounded-lg">
                <span className="text-xs text-on-surface-variant block">Moisture Index</span>
                <span className="text-sm font-headline font-bold text-on-surface">Dry / Optimal</span>
              </div>
            </div>
          </div>

          {/* Provenance Card */}
          <div className="bg-surface-container-low rounded-xl p-space-lg shadow-sm border border-surface-container-high">
            <div className="flex items-center justify-between mb-space-sm">
              <div className="flex items-center gap-2">
                <span className="material-symbols-outlined text-primary text-[20px]">badge</span>
                <h3 className="text-sm font-headline font-bold text-on-surface">Originating Collector Provenance</h3>
              </div>
              <span className="text-[11px] text-outline">Privacy Protected Link</span>
            </div>

            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-space-md bg-surface-container p-space-md rounded-lg">
              <div className="flex items-center gap-space-md">
                <div className="w-10 h-10 rounded-full bg-primary text-on-primary flex items-center justify-center font-headline font-bold text-sm">
                  RK
                </div>
                <div>
                  <div className="text-sm font-headline font-bold text-on-surface">Ramesh Kumar</div>
                  <div className="text-xs text-on-surface-variant">Collector ID #409 • Okhla Hub Zone</div>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <span className="px-2 py-1 bg-surface-container-high rounded text-xs text-on-surface font-semibold flex items-center gap-1">
                  <span className="material-symbols-outlined text-[14px]">verified_user</span>
                  Trusted Tier 2
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Right Column: Weight Comparison & Action Terminal (5 cols) */}
        <div className="lg:col-span-5 flex flex-col gap-space-md">
          {/* Weight Comparison Block */}
          <div className="bg-surface-container-low rounded-xl p-space-lg shadow-sm border border-surface-container-high space-y-space-md">
            <h3 className="text-base font-headline font-bold text-on-surface flex items-center gap-2">
              <span className="material-symbols-outlined text-primary text-[20px]">scale</span>
              Scale Certification & Weight
            </h3>

            <div className="bg-surface-container p-space-md rounded-lg space-y-2">
              <div className="flex justify-between items-center text-xs text-on-surface-variant">
                <span>Declared by Collector:</span>
                <span className="font-mono font-bold text-on-surface">{declaredWeight} kg</span>
              </div>
              <div className="flex justify-between items-center text-sm font-headline font-bold">
                <span className="text-on-surface">Yard Scale Verified:</span>
                <span className="font-mono text-primary text-lg">{verifiedWeight} kg</span>
              </div>
              <div className="pt-2 border-t border-surface-variant flex justify-between items-center text-xs">
                <span className="text-on-surface-variant">Tolerance Delta:</span>
                <span className={`font-mono font-bold ${Math.abs(Number(variancePercent)) <= 2 ? 'text-emerald-700' : 'text-amber-700'}`}>
                  {varianceKg} kg ({variancePercent}%)
                </span>
              </div>
            </div>

            {/* Editable verified scale adjustment */}
            <div className="space-y-1">
              <label className="text-xs font-semibold text-on-surface-variant block">
                Adjust Scale Certified Weight (kg):
              </label>
              <input
                type="number"
                step="0.1"
                value={verifiedWeight}
                onChange={(e) => setVerifiedWeight(parseFloat(e.target.value) || 0)}
                className="w-full bg-surface-container-lowest border border-outline-variant rounded-lg p-2 text-sm font-mono font-bold text-on-surface focus:outline-none focus:ring-2 focus:ring-primary"
              />
              <span className="text-[11px] text-outline block">
                Calibrated to ±0.05% under National Legal Metrology standards.
              </span>
            </div>
          </div>

          {/* Action Card */}
          <div className="bg-surface-container-low rounded-xl p-space-lg shadow-sm border border-surface-container-high space-y-space-md">
            <h3 className="text-base font-headline font-bold text-on-surface">Inspection Actions</h3>
            <p className="text-xs text-on-surface-variant">
              Confirm physical lot attributes to unlock formal quotation terminal.
            </p>

            <button
              onClick={() => navigate(`/recycler/quote?ref=${lotRef}&weight=${verifiedWeight}`)}
              className="w-full py-space-md px-space-lg bg-primary hover:bg-primary-container text-on-primary font-headline font-bold text-sm rounded-xl shadow-md flex items-center justify-center gap-2 transition-all active:scale-[0.98]"
            >
              <span className="material-symbols-outlined text-[18px]">payments</span>
              <span>Proceed to Quote Terminal</span>
            </button>

            <div className="grid grid-cols-2 gap-space-sm pt-space-xs">
              <button
                onClick={() => alert(`Flagged weight discrepancy of ${varianceKg}kg for audit.`)}
                className="py-2 px-space-sm bg-surface-container-high hover:bg-surface-container-highest text-on-surface rounded-lg text-xs font-semibold transition-colors"
              >
                Flag Discrepancy
              </button>
              <button
                onClick={() => alert('Scale tare recalibrated. Ready for re-weigh.')}
                className="py-2 px-space-sm bg-surface-container-high hover:bg-surface-container-highest text-on-surface rounded-lg text-xs font-semibold transition-colors"
              >
                Request Re-Weigh
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
