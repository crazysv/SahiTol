import React, { useCallback, useEffect, useRef, useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';

type BarcodeDetectorInstance = {
  detect: (source: ImageBitmapSource) => Promise<Array<{ rawValue: string }>>;
};

type BarcodeDetectorConstructor = new (options?: { formats?: string[] }) => BarcodeDetectorInstance;

declare global {
  interface Window {
    BarcodeDetector?: BarcodeDetectorConstructor;
  }
}

export default function R04_QRScan() {
  const navigate = useNavigate();
  const [manualRef, setManualRef] = useState('');
  const [cameraError, setCameraError] = useState(false);
  const [cameraActive, setCameraActive] = useState(false);
  const [scannedRecord, setScannedRecord] = useState<{
    ref: string;
    material?: string;
    weight?: number;
    status: string;
    hash?: string;
  } | null>(null);
  const videoRef = useRef<HTMLVideoElement>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const scanFrameRef = useRef<number | null>(null);

  const stopCamera = useCallback(() => {
    if (scanFrameRef.current !== null) {
      cancelAnimationFrame(scanFrameRef.current);
      scanFrameRef.current = null;
    }
    streamRef.current?.getTracks().forEach((track) => track.stop());
    streamRef.current = null;
    setCameraActive(false);
  }, []);

  const recordFromQr = useCallback((rawValue: string) => {
    // The offline QR carries only a reference, material, measured mass and canonical
    // hash. It never transports PII, GPS, images, or payment details.
    let ref = rawValue.split('/').filter(Boolean).at(-1)?.toUpperCase() || 'UNKNOWN';
    let material: string | undefined;
    let weight: number | undefined;
    let hash: string | undefined;
    try {
      const parsed = new URL(rawValue);
      ref = parsed.searchParams.get('ref')?.toUpperCase() || ref;
      material = parsed.searchParams.get('material') || undefined;
      const parsedWeight = Number(parsed.searchParams.get('weight'));
      weight = Number.isFinite(parsedWeight) ? parsedWeight : undefined;
      hash = parsed.searchParams.get('hash') || undefined;
    } catch {
      // Legacy QR records contain only an opaque reference and must not acquire
      // fabricated sample terms.
    }
    setScannedRecord({
      ref,
      material,
      weight,
      hash,
      status: material && weight !== undefined
        ? 'Offline record decoded — server confirmation pending'
        : 'Reference scanned — server lookup required',
    });
    stopCamera();
  }, [stopCamera]);

  const startCamera = useCallback(async () => {
    setCameraError(false);
    if (!navigator.mediaDevices?.getUserMedia || !window.BarcodeDetector) {
      setCameraError(true);
      return;
    }

    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: { ideal: 'environment' } },
        audio: false,
      });
      streamRef.current = stream;
      const video = videoRef.current;
      if (!video) {
        stopCamera();
        return;
      }
      video.srcObject = stream;
      await video.play();
      setCameraActive(true);
      const detector = new window.BarcodeDetector({ formats: ['qr_code'] });
      const scan = async () => {
        if (!videoRef.current || videoRef.current.readyState < HTMLMediaElement.HAVE_CURRENT_DATA) {
          scanFrameRef.current = requestAnimationFrame(scan);
          return;
        }
        try {
          const codes = await detector.detect(videoRef.current);
          if (codes[0]?.rawValue) {
            recordFromQr(codes[0].rawValue);
            return;
          }
        } catch {
          // Keep the camera usable: an unreadable frame is not a permission failure.
        }
        scanFrameRef.current = requestAnimationFrame(scan);
      };
      scanFrameRef.current = requestAnimationFrame(scan);
    } catch {
      stopCamera();
      setCameraError(true);
    }
  }, [recordFromQr, stopCamera]);

  useEffect(() => stopCamera, [stopCamera]);

  const handleLookup = () => {
    if (!manualRef.trim()) return;
    setScannedRecord({
      ref: manualRef.toUpperCase(),
      status: 'Reference entered — server lookup required',
    });
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
                  onClick={startCamera}
                  className="px-space-lg py-2 bg-primary text-on-primary text-xs font-headline font-bold rounded-lg hover:bg-primary-container transition-colors shadow-sm"
                >
                  Retry Camera
                </button>
              </div>
            ) : (
              <>
                <video
                  ref={videoRef}
                  className={`absolute inset-0 h-full w-full object-cover ${cameraActive ? 'block' : 'hidden'}`}
                  muted
                  playsInline
                  aria-label="Live rear-camera QR scanner"
                />
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

                {/* Camera control intentionally requires an explicit user gesture. */}
                <div className="absolute bottom-3 z-10 flex items-center gap-2">
                  <button
                    onClick={cameraActive ? stopCamera : startCamera}
                    className="px-3 py-1 bg-white/90 hover:bg-white text-neutral-900 text-xs font-semibold rounded shadow"
                  >
                    {cameraActive ? 'Stop Camera' : 'Start Camera'}
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
                <span className="px-2 py-0.5 bg-amber-100 text-amber-800 rounded text-[11px] font-bold">
                  Pending Server Check
                </span>
              </div>

              <div className="space-y-2">
                <div className="flex justify-between items-baseline">
                  <span className="text-xs text-on-surface-variant">Reference ID:</span>
                  <span className="font-mono font-bold text-primary text-base">{scannedRecord.ref}</span>
                </div>
              <p className="text-[11px] text-on-surface-variant">{scannedRecord.status}</p>
                <div className="flex justify-between items-baseline">
                  <span className="text-xs text-on-surface-variant">Material Class:</span>
                  <span className="text-xs font-semibold text-on-surface">{scannedRecord.material || 'Awaiting server lookup'}</span>
                </div>
                <div className="flex justify-between items-baseline">
                  <span className="text-xs text-on-surface-variant">Proposed Weight:</span>
                  <span className="font-mono font-bold text-on-surface text-sm">{scannedRecord.weight === undefined ? 'Awaiting server lookup' : `${scannedRecord.weight} kg`}</span>
                </div>
              </div>

              <div className="p-space-sm bg-surface-container rounded-lg text-[11px] text-on-surface-variant flex items-center gap-2">
                <span className="material-symbols-outlined text-[16px] text-amber-700">pending</span>
                <span>{scannedRecord.hash ? `SHA-256 seal received: ${scannedRecord.hash.slice(0, 12)}… Server verification is still required.` : 'No verified terms are available until server lookup succeeds.'}</span>
              </div>

              <button
                disabled={!scannedRecord.material || scannedRecord.weight === undefined}
                onClick={() => navigate(`/recycler/receipt?ref=${scannedRecord.ref}&weight=${scannedRecord.weight}`)}
                className="w-full py-2.5 px-space-lg bg-primary hover:bg-primary-container disabled:bg-outline disabled:cursor-not-allowed text-on-primary font-headline font-bold text-xs rounded-xl shadow-md flex items-center justify-center gap-2 transition-all active:scale-[0.98]"
              >
                <span>{scannedRecord.material && scannedRecord.weight !== undefined ? 'Proceed to Receipt & Settlement Review' : 'Awaiting Server Lookup'}</span>
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
