import React, { useEffect, useState } from 'react';
import { useNavigate, useSearchParams, Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { fetchRecyclerIncoming } from '../../lib/api';

/** A server-backed inspection view; it must never substitute a decorative lot. */
export default function R02_IncomingLot() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const requestId = searchParams.get('requestId');
  const { data: incoming, isLoading, error } = useQuery({
    queryKey: ['recycler-incoming'], queryFn: fetchRecyclerIncoming,
  });
  const request = incoming?.find((item) => item.request_id === requestId);
  const declaredWeight = (request?.lot.estimated_weight_g || 0) / 1000;
  const [offerWeight, setOfferWeight] = useState<number | null>(null);

  useEffect(() => {
    if (request && offerWeight === null) setOfferWeight(declaredWeight);
  }, [request, declaredWeight, offerWeight]);

  if (isLoading) return <p className="text-sm text-on-surface-variant">Loading this live incoming lot…</p>;
  if (error || !request) return (
    <div className="space-y-space-md">
      <p className="text-sm text-error" role="alert">{error instanceof Error ? error.message : 'This incoming request is no longer available to this recycler account.'}</p>
      <Link to="/recycler" className="text-sm text-primary hover:underline">Return to Inbox</Link>
    </div>
  );

  const lotRef = request.lot_id;
  const materialName = request.lot.material_name || request.lot.material_id || 'Unspecified material';
  const currentWeight = offerWeight ?? declaredWeight;
  const varianceKg = (currentWeight - declaredWeight).toFixed(1);
  const variancePercent = declaredWeight > 0 ? (((currentWeight - declaredWeight) / declaredWeight) * 100).toFixed(2) : '0.00';
  const collectorAlias = request.lot.collector_alias || 'Collector identity not supplied';
  const initials = collectorAlias.split(/\s+/).filter(Boolean).map((word) => word[0]).join('').slice(0, 2).toUpperCase() || 'CO';

  return (
    <div className="space-y-space-lg">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-space-md pb-space-sm border-b border-surface-container-high">
        <div>
          <div className="flex items-center gap-2 text-xs text-on-surface-variant mb-1"><Link to="/recycler" className="hover:underline flex items-center gap-1"><span className="material-symbols-outlined text-[16px]">arrow_back</span> Back to Inbox</Link><span>/</span><span>Inspection</span></div>
          <h2 className="text-2xl lg:text-3xl font-headline font-bold text-on-surface">Lot Inspection Workspace: <span className="text-primary font-mono">{lotRef}</span></h2>
        </div>
        <div className="flex items-center gap-space-sm"><div className="px-space-md py-1.5 bg-secondary-container text-on-secondary-container rounded-lg text-xs font-headline font-bold flex items-center gap-1 shadow-sm"><span className="material-symbols-outlined text-[16px]">verified</span> Live request</div><div className="px-space-md py-1.5 bg-surface-container-high text-on-surface-variant rounded-lg text-xs font-headline">{request.state}</div></div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-space-lg">
        <div className="lg:col-span-7 flex flex-col gap-space-md">
          <div className="bg-surface-container-low rounded-xl p-space-md shadow-sm border border-surface-container-high flex flex-col gap-space-md">
            <div className="flex items-center justify-between"><div className="flex items-center gap-2"><span className="material-symbols-outlined text-primary text-[20px]">inventory_2</span><span className="text-sm font-headline font-bold text-on-surface">Collector lot payload</span></div><span className="px-2 py-0.5 bg-surface-container-highest text-on-surface-variant rounded text-xs">Live request</span></div>
            <div className="relative w-full h-72 sm:h-80 rounded-lg overflow-hidden bg-surface-container flex items-center justify-center border border-surface-container-high"><div className="w-full h-full flex items-center justify-center text-center p-6 bg-surface-container-high"><div className="space-y-2"><span className="material-symbols-outlined text-primary text-5xl">inventory_2</span><div className="text-sm font-headline font-semibold text-on-surface">{materialName}</div><div className="text-xs text-on-surface-variant">{request.lot.images.length > 0 ? `${request.lot.images.length} submitted image reference(s) recorded.` : 'No image was attached to this lot.'}</div></div></div></div>
            <div className="grid grid-cols-3 gap-space-sm pt-space-xs text-center">
              <div className="bg-surface-container p-space-sm rounded-lg"><span className="text-xs text-on-surface-variant block">Condition</span><span className="text-sm font-headline font-bold text-on-surface">{request.lot.condition || 'Not specified'}</span></div>
              <div className="bg-surface-container p-space-sm rounded-lg"><span className="text-xs text-on-surface-variant block">Material</span><span className="text-sm font-headline font-bold text-on-surface">{request.lot.material_id || 'Unspecified'}</span></div>
              <div className="bg-surface-container p-space-sm rounded-lg"><span className="text-xs text-on-surface-variant block">Area</span><span className="text-sm font-headline font-bold text-on-surface">{request.lot.coarse_area || 'Not supplied'}</span></div>
            </div>
          </div>

          <div className="bg-surface-container-low rounded-xl p-space-lg shadow-sm border border-surface-container-high"><div className="flex items-center justify-between mb-space-sm"><div className="flex items-center gap-2"><span className="material-symbols-outlined text-primary text-[20px]">badge</span><h3 className="text-sm font-headline font-bold text-on-surface">Originating Collector Provenance</h3></div><span className="text-[11px] text-outline">Privacy-protected live request</span></div><div className="flex flex-col sm:flex-row sm:items-center justify-between gap-space-md bg-surface-container p-space-md rounded-lg"><div className="flex items-center gap-space-md"><div className="w-10 h-10 rounded-full bg-primary text-on-primary flex items-center justify-center font-headline font-bold text-sm">{initials}</div><div><div className="text-sm font-headline font-bold text-on-surface">{collectorAlias}</div><div className="text-xs text-on-surface-variant">{request.lot.coarse_area || 'Area withheld or not supplied'}</div></div></div><span className="px-2 py-1 bg-surface-container-high rounded text-xs text-on-surface font-semibold">Request-linked record</span></div></div>
        </div>

        <div className="lg:col-span-5 flex flex-col gap-space-md">
          <div className="bg-surface-container-low rounded-xl p-space-lg shadow-sm border border-surface-container-high space-y-space-md"><h3 className="text-base font-headline font-bold text-on-surface flex items-center gap-2"><span className="material-symbols-outlined text-primary text-[20px]">scale</span>Declared and proposed weight</h3><div className="bg-surface-container p-space-md rounded-lg space-y-2"><div className="flex justify-between items-center text-xs text-on-surface-variant"><span>Declared by Collector:</span><span className="font-mono font-bold text-on-surface">{declaredWeight} kg</span></div><div className="flex justify-between items-center text-sm font-headline font-bold"><span className="text-on-surface">Offer weight basis:</span><span className="font-mono text-primary text-lg">{currentWeight} kg</span></div><div className="pt-2 border-t border-surface-variant flex justify-between items-center text-xs"><span className="text-on-surface-variant">Difference:</span><span className={`font-mono font-bold ${Math.abs(Number(variancePercent)) <= 2 ? 'text-emerald-700' : 'text-amber-700'}`}>{varianceKg} kg ({variancePercent}%)</span></div></div><div className="space-y-1"><label className="text-xs font-semibold text-on-surface-variant block">Set offer weight basis (kg):</label><input type="number" step="0.1" value={currentWeight} onChange={(event) => setOfferWeight(parseFloat(event.target.value) || 0)} className="w-full bg-surface-container-lowest border border-outline-variant rounded-lg p-2 text-sm font-mono font-bold text-on-surface focus:outline-none focus:ring-2 focus:ring-primary" /><span className="text-[11px] text-outline block">This is the commercial offer basis; it does not alter the collector's original declared weight.</span></div></div>
          <div className="bg-surface-container-low rounded-xl p-space-lg shadow-sm border border-surface-container-high space-y-space-md"><h3 className="text-base font-headline font-bold text-on-surface">Inspection Actions</h3><p className="text-xs text-on-surface-variant">Continue with this exact live request. The quote terminal will re-check it before sending terms.</p><button onClick={() => navigate(`/recycler/quote?ref=${encodeURIComponent(lotRef)}&requestId=${encodeURIComponent(request.request_id)}&weight=${currentWeight}`)} className="w-full py-space-md px-space-lg bg-primary hover:bg-primary-container text-on-primary font-headline font-bold text-sm rounded-xl shadow-md flex items-center justify-center gap-2 transition-all active:scale-[0.98]"><span className="material-symbols-outlined text-[18px]">payments</span><span>Proceed to Quote Terminal</span></button></div>
        </div>
      </div>
    </div>
  );
}
