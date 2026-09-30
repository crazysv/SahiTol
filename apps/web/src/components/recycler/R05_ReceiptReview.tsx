import React, { useState } from 'react';
import { useNavigate, useSearchParams, Link } from 'react-router-dom';

export default function R05_ReceiptReview() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const lotRef = searchParams.get('ref') || 'ST-24A7';
  const initialWeight = parseFloat(searchParams.get('weight') || '84.8');

  const [measuredWeight, setMeasuredWeight] = useState(initialWeight);
  const declaredWeight = 85.5;
  const ratePerKg = 180;
  const agreedTotal = Math.round(declaredWeight * ratePerKg);
  const finalTotal = Math.round(measuredWeight * ratePerKg);
  const varianceKg = (measuredWeight - declaredWeight).toFixed(1);
  const hasDiscrepancy = Math.abs(measuredWeight - declaredWeight) > 0.05;

  const [paymentMode, setPaymentMode] = useState<'CASH' | 'UPI' | 'RTGS'>('CASH');
  const [upiRef, setUpiRef] = useState('');
  const [collectorAcknowledged, setCollectorAcknowledged] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isConfirmed, setIsConfirmed] = useState(false);
  const timerRef = React.useRef<ReturnType<typeof setTimeout> | null>(null);

  React.useEffect(() => {
    return () => {
      if (timerRef.current) clearTimeout(timerRef.current);
    };
  }, []);

  const handleConfirmReceipt = () => {
    setIsSubmitting(true);
    timerRef.current = setTimeout(() => {
      setIsSubmitting(false);
      setIsConfirmed(true);
    }, 500);
  };

  const handleDispute = () => {
    if (confirm('Document weight dispute? Transaction will be marked DISPUTED without overwriting physical facts.')) {
      alert('Dispute recorded. Case opened for supervisor review.');
      navigate('/recycler/history');
    }
  };

  return (
    <div className="space-y-space-lg max-w-5xl mx-auto">
      {/* Header Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-space-md pb-space-sm border-b border-surface-container-high">
        <div>
          <div className="flex items-center gap-2 text-xs text-on-surface-variant mb-1">
            <Link to="/recycler" className="hover:underline flex items-center gap-1">
              <span className="material-symbols-outlined text-[16px]">arrow_back</span> Back to Inbox
            </Link>
            <span>/</span>
            <span>Receipt & Settlement</span>
          </div>
          <h2 className="text-2xl lg:text-3xl font-headline font-bold text-on-surface">
            Receipt & Settlement Review: <span className="text-primary font-mono">{lotRef}</span>
          </h2>
          <p className="text-xs text-on-surface-variant mt-0.5">
            Reconcile quotation against verified yard scale telemetry and authorize physical handover receipt.
          </p>
        </div>

        {/* Cryptographic Seal Verified Badge */}
        <div className="flex items-center gap-2 bg-surface-container-high px-space-md py-1.5 rounded-xl border border-surface-container">
          <span className="material-symbols-outlined text-primary text-[20px]" style={{ fontVariationSettings: "'FILL' 1" }}>
            verified
          </span>
          <div>
            <div className="flex items-center gap-1 text-xs font-headline font-bold text-on-surface">
              <span>Cryptographic Seal Verified</span>
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-600 animate-pulse" />
            </div>
            <p className="text-[10px] text-outline font-mono">SHA-256: a0916...3365</p>
          </div>
        </div>
      </div>

      {isConfirmed ? (
        <div className="bg-emerald-50 border border-emerald-300 rounded-2xl p-space-xl text-center space-y-space-md shadow-sm">
          <div className="w-16 h-16 bg-emerald-100 text-emerald-700 rounded-full flex items-center justify-center mx-auto">
            <span className="material-symbols-outlined text-4xl">receipt_long</span>
          </div>
          <h3 className="text-2xl font-headline font-bold text-emerald-950">
            Digital Handover Record Confirmed!
          </h3>
          <p className="text-sm text-emerald-900 max-w-lg mx-auto">
            Receipt issued for <span className="font-bold font-mono">{measuredWeight} kg</span> of Insulated Copper Wire. Total payout of <span className="font-bold font-mono">₹{finalTotal.toLocaleString('en-IN')}</span> recorded via {paymentMode}.
          </p>
          <div className="p-space-sm bg-emerald-100/60 rounded-lg text-xs text-emerald-900 font-mono max-w-md mx-auto">
            RECEIPT HASH: a09162336537df26e84bb57c...
          </div>
          <div className="pt-space-md flex justify-center gap-space-md">
            <Link
              to="/recycler"
              className="px-space-lg py-2.5 bg-primary text-on-primary font-headline font-bold text-xs rounded-xl hover:bg-primary-container transition-colors shadow-sm"
            >
              Return to Inbox
            </Link>
            <Link
              to="/recycler/history"
              className="px-space-lg py-2.5 bg-surface-container-high text-on-surface font-headline font-semibold text-xs rounded-xl hover:bg-surface-container-highest transition-colors"
            >
              View in Ledger
            </Link>
            <Link
              to={`/verify/${lotRef}`}
              className="px-space-lg py-2.5 border border-outline text-on-surface font-headline font-semibold text-xs rounded-xl hover:bg-surface-container transition-colors"
            >
              Public Verify Page
            </Link>
          </div>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-space-lg">
          {/* Left Column: Material Identity & Comparison (7 cols) */}
          <div className="lg:col-span-7 flex flex-col gap-space-md">
            {/* Material Identity Card */}
            <div className="bg-surface-container-low rounded-xl p-space-lg shadow-sm border border-surface-container-high space-y-space-md">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-space-md">
                  <div className="w-12 h-12 bg-primary text-on-primary rounded-xl flex items-center justify-center">
                    <span className="material-symbols-outlined text-[24px]">electric_bolt</span>
                  </div>
                  <div>
                    <span className="text-[11px] uppercase tracking-wider text-primary font-bold">
                      Class: Non-Ferrous Wire Scrap
                    </span>
                    <h3 className="text-lg font-headline font-bold text-on-surface">Insulated Copper Cable</h3>
                    <p className="text-xs text-on-surface-variant">Batch Ref: {lotRef} · Collector: Ramesh Kumar (#409)</p>
                  </div>
                </div>
                <span className="px-2.5 py-1 bg-secondary-container text-on-secondary-container text-xs font-bold rounded-full">
                  Active Scale Feed
                </span>
              </div>

              {/* Agreed vs Measured Table */}
              <div className="grid grid-cols-2 gap-space-md p-space-md bg-surface-container-high rounded-xl">
                <div className="border-r border-surface-variant pr-space-md">
                  <span className="text-xs uppercase text-outline font-semibold block mb-1">Agreed Quotation</span>
                  <div className="text-xl font-headline font-bold text-on-surface">{declaredWeight} kg</div>
                  <div className="text-xs text-on-surface-variant mt-0.5">Rate: ₹{ratePerKg} / kg</div>
                  <div className="text-base font-headline font-bold text-on-surface-variant mt-2 font-mono">
                    ₹{agreedTotal.toLocaleString('en-IN')}.00
                  </div>
                </div>

                <div className="pl-space-xs">
                  <span className="text-xs uppercase text-primary font-bold block mb-1">Scale Measured</span>
                  <div className="flex items-baseline gap-2">
                    <span className="text-xl font-headline font-bold text-primary font-mono">{measuredWeight} kg</span>
                    {hasDiscrepancy && (
                      <span className="text-xs font-bold text-amber-700 font-mono">
                        {varianceKg} kg var
                      </span>
                    )}
                  </div>
                  <div className="text-xs text-on-surface-variant mt-0.5">Rate: ₹{ratePerKg} / kg</div>
                  <div className="text-base font-headline font-bold text-primary mt-2 font-mono">
                    ₹{finalTotal.toLocaleString('en-IN')}.00
                  </div>
                </div>
              </div>

              {/* Discrepancy & TermsRevision Banner */}
              {hasDiscrepancy && (
                <div className="p-space-md bg-amber-50 border border-amber-200 rounded-xl flex items-start gap-space-md">
                  <span className="material-symbols-outlined text-amber-700 text-[22px] mt-0.5">warning</span>
                  <div className="flex-1 text-xs text-amber-900 space-y-1">
                    <h4 className="font-headline font-bold">Terms Revision — Weight Variance Detected</h4>
                    <p>
                      Measured weight variance of {varianceKg} kg detected against initial proposal. Payout automatically updated from ₹{agreedTotal} to ₹{finalTotal}.
                    </p>
                    <label className="flex items-center gap-2 pt-1 cursor-pointer">
                      <input
                        type="checkbox"
                        checked={collectorAcknowledged}
                        onChange={(e) => setCollectorAcknowledged(e.target.checked)}
                        className="w-4 h-4 accent-primary rounded"
                      />
                      <span className="font-semibold text-amber-950">
                        Collector Ramesh Kumar physically inspected scale and acknowledged variance
                      </span>
                    </label>
                  </div>
                </div>
              )}
            </div>

            {/* Scale Telemetry Override */}
            <div className="bg-surface-container-low rounded-xl p-space-lg shadow-sm border border-surface-container-high space-y-2">
              <h4 className="text-sm font-headline font-bold text-on-surface">Scale Mass Telemetry Override</h4>
              <p className="text-xs text-on-surface-variant">
                Manually adjust if hopper tare calibration difference is observed during unload.
              </p>
              <div className="flex gap-space-sm items-center">
                <input
                  type="number"
                  step="0.1"
                  value={measuredWeight}
                  onChange={(e) => setMeasuredWeight(parseFloat(e.target.value) || 0)}
                  className="w-36 bg-surface-container-lowest border border-outline rounded-lg p-2 font-mono font-bold text-sm text-on-surface"
                />
                <span className="text-xs font-mono font-bold text-on-surface">KG</span>
              </div>
            </div>
          </div>

          {/* Right Column: Financial Settlement (5 cols) */}
          <div className="lg:col-span-5 flex flex-col gap-space-md">
            <div className="bg-surface-container-low rounded-xl p-space-lg shadow-sm border border-surface-container-high space-y-space-md">
              <h3 className="text-base font-headline font-bold text-on-surface flex items-center gap-2">
                <span className="material-symbols-outlined text-primary text-[20px]">payments</span>
                Financial Settlement Authorization
              </h3>

              <div className="p-space-md bg-surface-container rounded-xl space-y-1">
                <span className="text-xs text-on-surface-variant block">Total Net Settlement Amount:</span>
                <div className="text-3xl font-headline font-bold text-primary font-mono">
                  ₹{finalTotal.toLocaleString('en-IN')}.00
                </div>
                <span className="text-[11px] text-outline block">
                  Zero collector fee deductions applied. Collector receives 100% of payout.
                </span>
              </div>

              {/* Payment Mode Selector */}
              <div className="space-y-2">
                <label className="text-xs font-semibold text-on-surface-variant block">Settlement Payment Mode:</label>
                <div className="grid grid-cols-3 gap-space-xs">
                  <button
                    type="button"
                    onClick={() => setPaymentMode('CASH')}
                    className={`py-2 text-xs font-headline font-bold rounded-lg border transition-all ${
                      paymentMode === 'CASH'
                        ? 'bg-primary text-on-primary border-primary shadow-sm'
                        : 'bg-surface-container-high text-on-surface border-transparent hover:bg-surface-container-highest'
                    }`}
                  >
                    Cash First
                  </button>
                  <button
                    type="button"
                    onClick={() => setPaymentMode('UPI')}
                    className={`py-2 text-xs font-headline font-bold rounded-lg border transition-all ${
                      paymentMode === 'UPI'
                        ? 'bg-primary text-on-primary border-primary shadow-sm'
                        : 'bg-surface-container-high text-on-surface border-transparent hover:bg-surface-container-highest'
                    }`}
                  >
                    UPI Reference
                  </button>
                  <button
                    type="button"
                    onClick={() => setPaymentMode('RTGS')}
                    className={`py-2 text-xs font-headline font-bold rounded-lg border transition-all ${
                      paymentMode === 'RTGS'
                        ? 'bg-primary text-on-primary border-primary shadow-sm'
                        : 'bg-surface-container-high text-on-surface border-transparent hover:bg-surface-container-highest'
                    }`}
                  >
                    Bank / RTGS
                  </button>
                </div>
              </div>

              {paymentMode === 'UPI' && (
                <div className="space-y-1">
                  <label className="text-xs font-semibold text-on-surface-variant block">UPI Reference / UTR Number:</label>
                  <input
                    type="text"
                    value={upiRef}
                    onChange={(e) => setUpiRef(e.target.value)}
                    placeholder="e.g. 423984102941"
                    className="w-full bg-surface-container-lowest border border-outline rounded-lg p-2 font-mono text-xs text-on-surface"
                  />
                </div>
              )}

              {/* Action Buttons */}
              <div className="space-y-space-sm pt-space-xs">
                <button
                  type="button"
                  disabled={isSubmitting || (hasDiscrepancy && !collectorAcknowledged)}
                  onClick={handleConfirmReceipt}
                  className="w-full py-3 bg-primary hover:bg-primary-container text-on-primary font-headline font-bold text-xs rounded-xl shadow-md flex items-center justify-center gap-2 transition-all active:scale-[0.98] disabled:opacity-50"
                >
                  <span className="material-symbols-outlined text-[18px]">verified</span>
                  <span>{isSubmitting ? 'Confirming...' : 'Confirm Handover & Issue Digital Receipt'}</span>
                </button>

                <button
                  type="button"
                  onClick={handleDispute}
                  className="w-full py-2 bg-error-container text-on-error-container hover:opacity-90 font-headline font-semibold text-xs rounded-xl transition-colors"
                >
                  Document Physical Lot Dispute
                </button>
              </div>

              {/* Statutory Disclaimer */}
              <div className="text-[11px] text-outline border-t border-surface-container pt-space-sm">
                Digital Handover Record certifies physical scrap receipt. Received mass does not prove recycling. Non-EPR instrument.
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
