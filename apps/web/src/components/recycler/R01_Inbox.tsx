import React, { useMemo, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { fetchRecyclerIncoming } from '../../lib/api';

interface IncomingLotItem {
  id: string;
  referenceId: string;
  time: string;
  collectorAlias: string;
  collectorTier: string;
  materialName: string;
  materialCategory: string;
  declaredWeightKg: number;
  verifiedWeightKg: number | null;
  status: 'WAITING_REVIEW' | 'OFFER_PENDING' | 'ACCEPTED' | 'REJECTED';
  impuritiesEst: string;
  hasPhoto: boolean;
}

export default function R01_Inbox() {
  const navigate = useNavigate();
  const [filter, setFilter] = useState<'ALL' | 'WAITING' | 'CABLES' | 'BOARDS'>('ALL');
  const { data: incoming, isLoading, error } = useQuery({
    queryKey: ['recycler-incoming'],
    queryFn: fetchRecyclerIncoming,
    refetchInterval: 10_000,
  });
  const lots = useMemo<IncomingLotItem[]>(() => {
    if (!incoming) return [];
    return incoming.map((request) => {
      const materialName = request.lot.material_name || request.lot.material_id || 'Unspecified material';
      const category = materialName.toUpperCase().includes('PCB') || materialName.toUpperCase().includes('CIRCUIT')
        ? 'CIRCUIT_BOARDS'
        : materialName.toUpperCase().includes('CABLE') ? 'CABLES_WIRES' : 'OTHER';
      const openOffer = request.offers.some((offer) => offer.status === 'OPEN');
      return {
        id: request.request_id,
        referenceId: request.lot_id,
        time: new Date(request.created_at).toLocaleString(),
        collectorAlias: request.lot.collector_alias || 'Collector',
        collectorTier: 'Live request',
        materialName,
        materialCategory: category,
        declaredWeightKg: (request.lot.estimated_weight_g || 0) / 1000,
        verifiedWeightKg: null,
        status: openOffer ? 'OFFER_PENDING' : request.state === 'PENDING' ? 'WAITING_REVIEW' : request.state === 'ACCEPTED' ? 'ACCEPTED' : 'REJECTED',
        impuritiesEst: 'Not assessed',
        hasPhoto: false,
      };
    });
  }, [incoming]);

  const filteredLots = lots.filter((lot) => {
    if (filter === 'WAITING') return lot.status === 'WAITING_REVIEW';
    if (filter === 'CABLES') return lot.materialCategory === 'CABLES_WIRES';
    if (filter === 'BOARDS') return lot.materialCategory === 'CIRCUIT_BOARDS';
    return true;
  });

  return (
    <div className="space-y-space-lg">
      {/* Top Operational Banner & Greeting */}
      <section className="grid grid-cols-1 lg:grid-cols-4 gap-space-md">
        <div className="lg:col-span-3 bg-surface-container-high rounded-xl p-space-lg flex flex-col justify-between relative overflow-hidden shadow-sm">
          <div className="absolute -right-12 -bottom-12 w-64 h-64 rounded-full bg-secondary-container/20 blur-3xl pointer-events-none" />
          <div>
            <div className="flex items-center gap-space-sm mb-space-xs">
              <span className="px-space-sm py-space-xs bg-primary text-on-primary text-xs rounded font-headline uppercase tracking-wider font-bold">
                Active Shift #402
              </span>
              <span className="text-sm text-on-surface-variant font-body">
                Verma Electricals • Delhi Central Hub (Okhla Zone 4)
              </span>
            </div>
            <h2 className="text-2xl lg:text-3xl font-headline font-bold text-on-surface mb-space-xs">
              Yard Dashboard & Material Inbox
            </h2>
            <p className="text-body-md text-on-surface-variant max-w-2xl">
              Review incoming lots, inspect weigh-slips submitted by collectors, and dispatch competitive quotes to close scrap acquisitions with transparent provenance.
            </p>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-3 gap-space-md mt-space-lg pt-space-md bg-surface-container-low rounded-lg p-space-md border border-surface-container-high">
            <div>
              <span className="text-xs text-on-surface-variant block">Weighbridge Status</span>
              <span className="text-sm font-headline font-bold text-on-surface flex items-center gap-space-xs mt-0.5">
                <span className="w-2.5 h-2.5 rounded-full bg-emerald-600 animate-pulse"></span> Online & Calibrated
              </span>
            </div>
            <div>
              <span className="text-xs text-on-surface-variant block">Active Sorters</span>
              <span className="text-sm font-headline font-bold text-on-surface mt-0.5 block">
                14 Personnel on Floor
              </span>
            </div>
            <div className="col-span-2 sm:col-span-1">
              <span className="text-xs text-on-surface-variant block">Today's Inflow</span>
              <span className="text-sm font-headline font-bold text-primary mt-0.5 block">
                4,820 kg Processed
              </span>
            </div>
          </div>
        </div>

        {/* Quick Stats Card */}
        <div className="bg-surface-container-low rounded-xl p-space-lg flex flex-col justify-between shadow-sm border border-surface-container-high">
          <div>
            <span className="text-xs text-on-surface-variant uppercase tracking-wider block mb-space-xs font-semibold">
              Terminal Turnaround
            </span>
            <div className="text-3xl font-headline font-bold text-on-surface mb-space-xs">
              98.4%
            </div>
            <p className="text-xs text-on-surface-variant">
              Average lot turnaround time: 14 minutes from drop to offer.
            </p>
          </div>
          <div className="mt-space-lg">
            <div className="w-full bg-surface-container-highest rounded-full h-2.5 overflow-hidden">
              <div className="bg-primary h-full rounded-full" style={{ width: '85%' }}></div>
            </div>
            <div className="flex justify-between text-xs text-on-surface-variant mt-1.5 font-medium">
              <span>Target: 15m</span>
              <span className="text-primary font-bold">Ahead of Schedule</span>
            </div>
          </div>
        </div>
      </section>

      {isLoading && <p className="text-sm text-on-surface-variant">Loading live incoming requests…</p>}
      {error && <p className="text-sm text-error" role="alert">{error instanceof Error ? error.message : 'Could not load live incoming requests.'}</p>}

      {/* Summary Metric Cards */}
      <section className="grid grid-cols-1 md:grid-cols-3 gap-space-md">
        <div
          onClick={() => setFilter('WAITING')}
          className="bg-surface-container rounded-xl p-space-lg shadow-sm border border-surface-container-high hover:border-primary transition-all cursor-pointer group"
        >
          <div className="flex items-center justify-between mb-space-md">
            <span className="p-space-sm rounded-lg bg-secondary-container text-on-secondary-container material-symbols-outlined text-[24px]">
              inbox
            </span>
            <span className="px-space-sm py-space-xs bg-primary-fixed text-on-primary-fixed text-xs rounded font-bold">
              Action Required
            </span>
          </div>
          <div className="text-3xl font-headline font-bold text-on-surface mb-1">
            {lots.filter((l) => l.status === 'WAITING_REVIEW').length} Lots
          </div>
          <div className="text-sm text-on-surface-variant">Waiting Review</div>
          <div className="mt-space-md pt-space-md border-t border-surface-variant flex items-center justify-between text-sm text-primary font-bold group-hover:translate-x-0.5 transition-transform">
            <span>Process Queue</span>
            <span className="material-symbols-outlined text-[18px]">arrow_forward</span>
          </div>
        </div>

        <div className="bg-surface-container rounded-xl p-space-lg shadow-sm border border-surface-container-high">
          <div className="flex items-center justify-between mb-space-md">
            <span className="p-space-sm rounded-lg bg-secondary-container text-on-secondary-container material-symbols-outlined text-[24px]">
              local_shipping
            </span>
            <span className="px-space-sm py-space-xs bg-secondary-fixed text-on-secondary-fixed text-xs rounded font-bold">
              Active Offers
            </span>
          </div>
          <div className="text-3xl font-headline font-bold text-on-surface mb-1">
            {lots.filter((l) => l.status === 'OFFER_PENDING').length} Lots
          </div>
          <div className="text-sm text-on-surface-variant">Offers Dispatched & Awaiting Response</div>
          <div className="mt-space-md pt-space-md border-t border-surface-variant flex items-center justify-between text-sm text-primary font-bold">
            <Link to="/recycler/history" className="flex items-center justify-between w-full hover:underline">
              <span>Track Dispatches</span>
              <span className="material-symbols-outlined text-[18px]">arrow_forward</span>
            </Link>
          </div>
        </div>

        <div className="bg-surface-container rounded-xl p-space-lg shadow-sm border border-surface-container-high">
          <div className="flex items-center justify-between mb-space-md">
            <span className="p-space-sm rounded-lg bg-secondary-container text-on-secondary-container material-symbols-outlined text-[24px]">
              verified
            </span>
            <span className="px-space-sm py-space-xs bg-surface-container-highest text-on-surface text-xs rounded font-bold">
              Settled
            </span>
          </div>
          <div className="text-3xl font-headline font-bold text-on-surface mb-1">
            28 Tons
          </div>
          <div className="text-sm text-on-surface-variant">Completed Handover Today</div>
          <div className="mt-space-md pt-space-md border-t border-surface-variant flex items-center justify-between text-sm text-primary font-bold">
            <Link to="/recycler/history" className="flex items-center justify-between w-full hover:underline">
              <span>View Full Ledger</span>
              <span className="material-symbols-outlined text-[18px]">arrow_forward</span>
            </Link>
          </div>
        </div>
      </section>

      {/* Incoming Material Inbox Table */}
      <section className="bg-surface-container-low rounded-xl p-space-lg shadow-sm border border-surface-container-high">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-space-md mb-space-md">
          <div>
            <h3 className="text-xl font-headline font-bold text-on-surface">Incoming Material Queue</h3>
            <p className="text-xs text-on-surface-variant mt-0.5">
              Live scale tickets and lots routed to Yard #402
            </p>
          </div>

          {/* Filter Pills */}
          <div className="flex flex-wrap items-center gap-space-xs">
            <button
              onClick={() => setFilter('ALL')}
              className={`px-space-md py-1.5 rounded-lg text-xs font-headline font-semibold transition-colors ${
                filter === 'ALL'
                  ? 'bg-primary text-on-primary'
                  : 'bg-surface-container-high text-on-surface-variant hover:text-on-surface'
              }`}
            >
              All ({lots.length})
            </button>
            <button
              onClick={() => setFilter('WAITING')}
              className={`px-space-md py-1.5 rounded-lg text-xs font-headline font-semibold transition-colors ${
                filter === 'WAITING'
                  ? 'bg-primary text-on-primary'
                  : 'bg-surface-container-high text-on-surface-variant hover:text-on-surface'
              }`}
            >
              Waiting Review ({lots.filter((l) => l.status === 'WAITING_REVIEW').length})
            </button>
            <button
              onClick={() => setFilter('CABLES')}
              className={`px-space-md py-1.5 rounded-lg text-xs font-headline font-semibold transition-colors ${
                filter === 'CABLES'
                  ? 'bg-primary text-on-primary'
                  : 'bg-surface-container-high text-on-surface-variant hover:text-on-surface'
              }`}
            >
              Cables
            </button>
            <button
              onClick={() => setFilter('BOARDS')}
              className={`px-space-md py-1.5 rounded-lg text-xs font-headline font-semibold transition-colors ${
                filter === 'BOARDS'
                  ? 'bg-primary text-on-primary'
                  : 'bg-surface-container-high text-on-surface-variant hover:text-on-surface'
              }`}
            >
              PCBs
            </button>
          </div>
        </div>

        {/* Responsive Table */}
        <div className="overflow-x-auto rounded-lg border border-surface-container-high">
          <table className="w-full text-left text-sm">
            <thead className="bg-surface-container-high text-xs text-on-surface-variant font-headline uppercase tracking-wider">
              <tr>
                <th className="p-space-md">Lot Reference</th>
                <th className="p-space-md">Time</th>
                <th className="p-space-md">Collector</th>
                <th className="p-space-md">Material</th>
                <th className="p-space-md">Weight (kg)</th>
                <th className="p-space-md">Status</th>
                <th className="p-space-md text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-surface-container-high bg-surface-container-lowest">
              {filteredLots.map((lot) => (
                <tr key={lot.id} className="hover:bg-surface-container-low transition-colors">
                  <td className="p-space-md font-mono font-bold text-on-surface">
                    <span className="flex items-center gap-1.5">
                      <span className="material-symbols-outlined text-[16px] text-primary">qr_code</span>
                      {lot.referenceId}
                    </span>
                  </td>
                  <td className="p-space-md text-xs text-on-surface-variant">{lot.time}</td>
                  <td className="p-space-md">
                    <div className="font-medium text-on-surface">{lot.collectorAlias}</div>
                    <span className="text-[11px] text-outline font-normal">{lot.collectorTier}</span>
                  </td>
                  <td className="p-space-md">
                    <div className="font-medium text-on-surface">{lot.materialName}</div>
                    <span className="text-[11px] text-on-surface-variant">Est. Impurities: {lot.impuritiesEst}</span>
                  </td>
                  <td className="p-space-md font-mono">
                    <div className="font-bold text-on-surface">{lot.verifiedWeightKg ?? lot.declaredWeightKg} kg</div>
                    {lot.verifiedWeightKg && lot.verifiedWeightKg !== lot.declaredWeightKg && (
                      <span className="text-[11px] text-amber-700">Dec: {lot.declaredWeightKg} kg</span>
                    )}
                  </td>
                  <td className="p-space-md">
                    {lot.status === 'WAITING_REVIEW' && (
                      <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-semibold bg-amber-100 text-amber-800">
                        Waiting Review
                      </span>
                    )}
                    {lot.status === 'OFFER_PENDING' && (
                      <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-semibold bg-blue-100 text-blue-800">
                        Offer Dispatched
                      </span>
                    )}
                    {lot.status === 'ACCEPTED' && (
                      <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-semibold bg-emerald-100 text-emerald-800">
                        Agreed
                      </span>
                    )}
                  </td>
                  <td className="p-space-md text-right">
                    <div className="flex items-center justify-end gap-2">
                      <button
                        onClick={() => navigate(`/recycler/incoming?ref=${lot.referenceId}&requestId=${lot.id}`)}
                        className="px-space-md py-1 text-xs font-semibold bg-surface-container-high hover:bg-surface-container-highest text-on-surface rounded transition-colors"
                      >
                        Inspect
                      </button>
                      <button
                        onClick={() => navigate(`/recycler/quote?ref=${lot.referenceId}&requestId=${lot.id}&weight=${lot.verifiedWeightKg ?? lot.declaredWeightKg}`)}
                        className="px-space-md py-1 text-xs font-semibold bg-primary hover:bg-primary-container text-on-primary rounded transition-colors shadow-sm"
                      >
                        Quote
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}
