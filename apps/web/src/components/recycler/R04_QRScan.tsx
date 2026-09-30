import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';

export default function R04_QRScan() {
  const navigate = useNavigate();
  const [manualRef, setManualRef] = useState('');
  const [cameraError, setCameraError] = useState(false);
  const [scannedRecord, setScannedRecord] = useState<{
    ref: string;
    material: string;
    weight: number;
    collector: string;
    status: string;
  } | null>({
    ref: 'ST-24A7',
    material: 'Insulated Copper Cable',
    weight: 84.8,
    collector: 'Ramesh Kumar (#409)',
    status: 'Proposal Synced — Pending Recycler Confirmation',
  });

  const handleLookup = () => {
    if (!manualRef.trim()) return;
    setScannedRecord({
      ref: manualRef.toUpperCase(),
      material: 'Copper Transformer Coils',
      weight: 120.5,
      collector: 'Verified Collector',
      status: 'Proposal Synced — Pending Recycler Confirmation',
    });
  };

  const handleSimulateScan = () => {
    setScannedRecord({
      ref: 'ST-24A7',
      material: 'Insulated Copper Cable',
      weight: 84.8,
      collector: 'Ramesh Kumar (#409)',
      status: 'Proposal Synced — Pending Recycler Confirmation',
    });
    setCameraError(false);
  };

  return (
    <div className="space-y-space-lg">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-space-md pb-space-sm border-b border-surface-container-high">
        <div>
          <h2 className="text-2xl lg:text-3xl font-headline font-bold text-on-surface">
            Second-Device QR Scanner & Handover Reception
          </h2>
          <p className="text-xs text-on-surface-variant max-w-2xl mt-0.5">
            Scan collector's offline QR code or enter handover reference to verify material and record physical custody transfer.
          </p>
        </div>

        <div className="bg-surface-container-high px-space-md py-1.5 rounded-lg flex items-center gap-2 text-xs font-semibold text-on-surface">
          <span className="w-2 h-2 rounded-full bg-emerald-600 animate-pulse" />
          Terminal Online (Sync OK)
        </div>
      </div>

      {/* Main Scanner Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-space-lg">
        {/* Left Column: Camera Viewfinder & Manual Input (7 cols) */}
        <div className="lg:col-span-7 flex flex-col gap-space-md">
          {/* Viewfinder Frame */}
          <div className="bg-surface-container-low rounded-xl p-space-lg relative overflow-hidden flex flex-col items-center justify-center min-h-[360px] shadow-sm border border-surface-container-high">
            {/* Viewfinder Scrim & Frame */}
            <div className="absolute inset-0 bg-neutral-900/90 z-0"></div>

            {cameraError ? (
              <div className="relative z-10 text-center p-6 space-y-3 max-w-sm">
                <span className="material-symbols-outlined text-amber-500 text-5xl">videocam_off</span>
                <h3 className="text-base font-headline font-bold text-white">Camera Access Required</h3>
                <p className="text-xs text-neutral-300">
                  Browser permissions are blocked or HTTPS camera feed is unavailable. Use manual reference entry below.
                </p>
                <button
                  onClick={() => setCameraError(false)}
                  className="px-space-lg py-2 bg-primary text-on-primary text-xs font-headline font-bold rounded-lg hover:bg-primary-container transition-colors shadow-sm"
                >
                  Retry Camera
                </button>
              </div>
            ) : (
              <>
                <div className="relative z-10 w-64 h-64 border-2 border-white/60 rounded-xl flex items-center justify-center">
                  <div className="absolute top-0 left-0 w-6 h-6 border-t-4 border-l-4 border-primary" />
                  <div className="absolute top-0 right-0 w-6 h-6 border-t-4 border-r-4 border-primary" />
                  <div className="absolute bottom-0 left-0 w-6 h-6 border-b-4 border-l-4 border-primary" />
                  <div className="absolute bottom-0 right-0 w-6 h-6 border-b-4 border-r-4 border-primary" />
                  <div className="w-3 h-3 bg-primary rounded-full animate-ping opacity-75" />
                  <span className="absolute -bottom-9 text-white font-headline text-xs bg-black/60 px-3 py-1 rounded-full">
                    Align Collector QR inside frame
                  </span>
                </div>

                {/* Viewfinder simulation buttons */}
                <div className="absolute bottom-3 z-10 flex items-center gap-2">
                  <button
                    onClick={handleSimulateScan}
                    className="px-3 py-1 bg-white/90 hover:bg-white text-neutral-900 text-xs font-semibold rounded shadow"
                  >
                    Simulate Successful Scan
                  </button>
                  <button
                    onClick={() => setCameraError(true)}
                    className="px-3 py-1 bg-neutral-800/90 hover:bg-neutral-800 text-neutral-200 text-xs font-semibold rounded shadow"
                  >
                    Simulate Camera Denied
                  </button>
                </div>
              </>
            )}
          </div>

          {/* Manual Fallback Reference Input */}
          <div className="bg-surface-container-low rounded-xl p-space-lg shadow-sm border border-surface-container-high space-y-space-sm">
            <label htmlFor="manual-ref-input" className="block text-sm font-headline font-bold text-on-surface">
              Manual Reference Lookup Fallback
            </label>
            <p className="text-xs text-on-surface-variant">
              Enter the 6-character reference printed on collector's phone or paper token.
            </p>
            <div className="flex gap-space-sm">
              <div className="relative flex-1">
                <span className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-outline font-bold">
                  #
                </span>
                <input
                  id="manual-ref-input"
                  type="text"
                  value={manualRef}
                  onChange={(e) => setManualRef(e.target.value)}
                  placeholder="e.g. ST-24A7"
                  className="w-full pl-8 pr-3 py-2 bg-surface-container-lowest border border-outline rounded-lg text-sm font-mono font-bold uppercase tracking-wider focus:outline-none focus:ring-2 focus:ring-primary"
                />
              </div>
              <button
                onClick={handleLookup}
                className="px-space-xl py-2 bg-primary text-on-primary font-headline font-bold text-xs rounded-lg hover:bg-primary-container transition-colors shadow-sm"
              >
                Lookup
              </button>
            </div>
          </div>
        </div>

        {/* Right Column: Scanned Record Preview & Next Step (5 cols) */}
        <div className="lg:col-span-5 flex flex-col gap-space-md">
          {scannedRecord ? (
            <div className="bg-surface-container-low rounded-xl p-space-lg shadow-sm border-2 border-primary/40 space-y-space-md relative overflow-hidden">
              <div className="flex items-center justify-between pb-space-xs border-b border-surface-container-high">
                <div className="flex items-center gap-2">
                  <span className="material-symbols-outlined text-primary text-[22px]">qr_code_scanner</span>
                  <span className="text-sm font-headline font-bold text-on-surface">Recognized Proposal</span>
                </div>
                <span className="px-2 py-0.5 bg-emerald-100 text-emerald-800 rounded text-[11px] font-bold">
                  Valid QR
                </span>
              </div>

              <div className="space-y-2">
                <div className="flex justify-between items-baseline">
                  <span className="text-xs text-on-surface-variant">Reference ID:</span>
                  <span className="font-mono font-bold text-primary text-base">{scannedRecord.ref}</span>
                </div>
                <div className="flex justify-between items-baseline">
                  <span className="text-xs text-on-surface-variant">Collector:</span>
                  <span className="text-xs font-semibold text-on-surface">{scannedRecord.collector}</span>
                </div>
                <div className="flex justify-between items-baseline">
                  <span className="text-xs text-on-surface-variant">Material Class:</span>
                  <span className="text-xs font-semibold text-on-surface">{scannedRecord.material}</span>
                </div>
                <div className="flex justify-between items-baseline">
                  <span className="text-xs text-on-surface-variant">Proposed Weight:</span>
                  <span className="font-mono font-bold text-on-surface text-sm">{scannedRecord.weight} kg</span>
                </div>
              </div>

              <div className="p-space-sm bg-surface-container rounded-lg text-[11px] text-on-surface-variant flex items-center gap-2">
                <span className="material-symbols-outlined text-[16px] text-emerald-700">verified</span>
                <span>SHA-256 hash fingerprint verified against immutable server proposal.</span>
              </div>

              <button
                onClick={() => navigate(`/recycler/receipt?ref=${scannedRecord.ref}&weight=${scannedRecord.weight}`)}
                className="w-full py-2.5 px-space-lg bg-primary hover:bg-primary-container text-on-primary font-headline font-bold text-xs rounded-xl shadow-md flex items-center justify-center gap-2 transition-all active:scale-[0.98]"
              >
                <span>Proceed to Receipt & Settlement Review</span>
                <span className="material-symbols-outlined text-[16px]">arrow_forward</span>
              </button>
            </div>
          ) : (
            <div className="bg-surface-container-low rounded-xl p-space-lg shadow-sm border border-surface-container-high text-center py-12 space-y-2">
              <span className="material-symbols-outlined text-outline text-4xl">qr_code_2</span>
              <h4 className="text-sm font-headline font-semibold text-on-surface">No QR Scanned Yet</h4>
              <p className="text-xs text-on-surface-variant max-w-xs mx-auto">
                Scan collector's device or use manual lookup to inspect handover details.
              </p>
            </div>
          )}

          {/* Statutory Integrity Card */}
          <div className="p-space-md bg-surface-container rounded-xl text-xs text-on-surface-variant space-y-1">
            <div className="font-headline font-bold text-on-surface flex items-center gap-1.5">
              <span className="material-symbols-outlined text-[16px] text-primary">gavel</span>
              Statutory Custody Notice
            </div>
            <p className="text-[11px]">
              Confirmation creates a Digital Handover Record of physical mass receipt. It does not certify EPR compliance or proof of recycling.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
