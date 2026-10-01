import React from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { HandoverDetail, lookupDemoHandover } from '../../lib/api';

function formatMoney(paise: number | undefined) {
  if (paise === undefined) return 'Not recorded';
  return `₹${(paise / 100).toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
}

function formatMass(grams: number | null | undefined) {
  if (grams === undefined || grams === null) return 'Not recorded';
  return `${(grams / 1000).toFixed(2)} kg`;
}

export default function R05_ReceiptReview() {
  const [searchParams] = useSearchParams();
  const handoverId = searchParams.get('handover_id');
  const [record, setRecord] = React.useState<HandoverDetail | null>(null);
  const [error, setError] = React.useState<string | null>(null);

  React.useEffect(() => {
    if (!handoverId) {
      setError('No verified handover ID was supplied. Return to the QR scanner and verify the proposal first.');
      return;
    }
    let cancelled = false;
    lookupDemoHandover(handoverId)
      .then((result) => { if (!cancelled) setRecord(result); })
      .catch((reason: unknown) => {
        if (!cancelled) setError(reason instanceof Error ? reason.message : 'Unable to load the verified receipt.');
      });
    return () => { cancelled = true; };
  }, [handoverId]);

  if (error) return (
    <div className="max-w-2xl mx-auto space-y-space-md">
      <h2 className="text-2xl font-headline font-bold text-on-surface">Receipt unavailable</h2>
      <p className="p-space-md rounded-xl bg-error-container text-on-error-container text-sm">{error}</p>
      <Link to="/recycler/scan" className="text-sm font-semibold text-primary hover:underline">Return to QR scanner</Link>
    </div>
  );
  if (!record) return <p className="text-sm text-on-surface-variant">Loading verified handover record…</p>;

  const payload = record.proposal_payload;
  const weights = payload.weight_snapshot;
  const values = payload.value_snapshot;
  const material = payload.material_snapshot;
  const isConfirmed = record.status === 'CONFIRMED';

  return (
    <div className="space-y-space-lg max-w-5xl mx-auto">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-space-md pb-space-sm border-b border-surface-container-high">
        <div>
          <div className="flex items-center gap-2 text-xs text-on-surface-variant mb-1">
            <Link to="/recycler" className="hover:underline flex items-center gap-1"><span className="material-symbols-outlined text-[16px]">arrow_back</span> Back to Inbox</Link>
            <span>/</span><span>Digital Handover Record</span>
          </div>
          <h2 className="text-2xl lg:text-3xl font-headline font-bold text-on-surface">Receipt: <span className="text-primary font-mono">{record.id}</span></h2>
          <p className="text-xs text-on-surface-variant mt-0.5">Server-backed physical receipt; it is not proof of recycling or an EPR certificate.</p>
        </div>
        <div className={`px-space-md py-1.5 rounded-xl border text-xs font-headline font-bold ${isConfirmed ? 'bg-emerald-50 border-emerald-300 text-emerald-900' : 'bg-amber-50 border-amber-300 text-amber-900'}`}>
          {isConfirmed ? 'Recycler confirmation recorded' : `Status: ${record.status}`}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-space-lg">
        <section className="bg-surface-container-low rounded-xl p-space-lg shadow-sm border border-surface-container-high space-y-space-md">
          <h3 className="text-base font-headline font-bold text-on-surface flex items-center gap-2"><span className="material-symbols-outlined text-primary">receipt_long</span> Confirmed proposal</h3>
          <dl className="grid grid-cols-2 gap-y-space-md text-sm">
            <dt className="text-on-surface-variant">Material code</dt><dd className="font-mono font-semibold text-right">{material?.material_id || 'Not recorded'}</dd>
            <dt className="text-on-surface-variant">Condition</dt><dd className="font-semibold text-right">{material?.condition || 'Not recorded'}</dd>
            <dt className="text-on-surface-variant">Proposed mass</dt><dd className="font-mono font-semibold text-right">{formatMass(weights?.estimated_weight_g)}</dd>
            <dt className="text-on-surface-variant">Received mass</dt><dd className="font-mono font-semibold text-right">{formatMass(weights?.measured_weight_g)}</dd>
            <dt className="text-on-surface-variant">Agreed value</dt><dd className="font-mono font-semibold text-right">{formatMoney(values?.agreed_total_paise)}</dd>
          </dl>
        </section>

        <section className="bg-surface-container-low rounded-xl p-space-lg shadow-sm border border-surface-container-high space-y-space-md">
          <h3 className="text-base font-headline font-bold text-on-surface flex items-center gap-2"><span className="material-symbols-outlined text-primary">verified</span> Integrity and custody</h3>
          <p className="text-xs text-on-surface-variant">The QR seal matches the server proposal. This screen is read-only because confirmation was performed on the preceding scanner screen.</p>
          <div className="p-space-sm bg-surface-container rounded-lg text-xs break-all font-mono text-on-surface-variant">SHA-256: {record.proposal_hash}</div>
          <p className="text-[11px] text-outline border-t border-surface-container pt-space-sm">Digital Handover Record certifies physical scrap receipt. Received mass does not prove recycling. Non-EPR instrument.</p>
        </section>
      </div>
    </div>
  );
}
