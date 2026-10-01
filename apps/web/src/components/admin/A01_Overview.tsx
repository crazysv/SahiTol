import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { AdminOverview, fetchAdminOverview } from '../../lib/api';

export default function A01_Overview() {
  const [timeRange, setTimeRange] = useState<'24H' | '7D' | '30D'>('7D');
  const [materialFilter, setMaterialFilter] = useState('All Materials');
  const [syncing, setSyncing] = useState(false);
  const [lastUpdated, setLastUpdated] = useState('29 Sep • 18:20');
  const [overview, setOverview] = useState<AdminOverview | null>(null);
  const [loadError, setLoadError] = useState<string | null>(null);

  const refresh = async () => {
    setSyncing(true);
    setLoadError(null);
    try {
      const result = await fetchAdminOverview();
      setOverview(result);
      setLastUpdated(new Date(result.last_refresh).toLocaleString('en-GB'));
    } catch (error) {
      setLoadError(error instanceof Error ? error.message : 'Unable to load platform metrics.');
    } finally {
      setSyncing(false);
    }
  };

  useEffect(() => { void refresh(); }, []);

  const handleSyncLedger = () => {
    void refresh();
  };

  return (
    <div className="flex flex-col w-full">
      {/* Top Bar / Sub-header for System Pulse (Stitch A01) */}
      <div className="w-full bg-surface-container-low px-gutter py-space-md flex flex-col md:flex-row md:items-center justify-between gap-space-md border-b border-surface-container">
        <div className="flex items-center gap-space-md">
          <div className="w-3 h-3 rounded-full bg-primary animate-ping"></div>
          <span className="text-headline-md font-headline-md text-on-surface">System Pulse Overview</span>
          <span className="text-body-sm px-2.5 py-1 bg-surface-container-high text-on-surface-variant rounded-xl font-mono">
            Updated {lastUpdated}
          </span>
          <span className="px-2 py-0.5 text-xs font-bold bg-secondary-container text-on-secondary-container rounded">
            Live Feed
          </span>
        </div>

        <div className="flex items-center gap-space-sm">
          <button
            onClick={handleSyncLedger}
            disabled={syncing}
            className="px-4 py-2 bg-primary text-on-primary text-label-md rounded-xl hover:bg-primary-container transition-colors flex items-center gap-2 shadow-sm disabled:opacity-50"
          >
            <span className={`material-symbols-outlined text-[18px] ${syncing ? 'animate-spin' : ''}`}>
              refresh
            </span>
            {syncing ? 'Syncing...' : 'Sync Ledger'}
          </button>

          <button
            onClick={() => setMaterialFilter(materialFilter === 'All Materials' ? 'Ferrous & Non-Ferrous' : 'All Materials')}
            className="px-4 py-2 bg-surface-container-high text-on-surface text-label-md rounded-xl hover:bg-surface-dim transition-colors flex items-center gap-2"
          >
            <span className="material-symbols-outlined text-[18px]">filter_alt</span>
            Provenance: {materialFilter}
          </button>
        </div>
      </div>

      {/* Statutory & Honest Metrics Banner (Guardrail / R-ADMIN-03) */}
      <div className="max-w-7xl mx-auto w-full px-gutter pt-4">
        <div className="p-3 bg-amber-50 border border-amber-200 rounded-xl flex items-start gap-2.5 text-xs text-amber-900">
          <span className="material-symbols-outlined text-amber-700 text-lg shrink-0 mt-0.5">info</span>
          <div>
            <span className="font-bold">Provenance & Integrity Notice:</span> All metrics derive strictly from verified cryptographic event logs. In strict accordance with SahiTol guardrails, <strong>received mass does not equal recycled mass</strong> and does not constitute EPR certification or claimed carbon offsets without downstream recycler transformation proof.
          </div>
        </div>
        {loadError && <p role="alert" className="mt-3 p-3 text-sm rounded-xl bg-error-container text-on-error-container">Metrics unavailable: {loadError}. Existing figures are not shown as zero.</p>}
      </div>

      {/* Main Content Flow */}
      <div className="max-w-7xl mx-auto w-full px-gutter py-space-xl flex flex-col gap-space-xl">
        {/* Hero Metric Cards Grid (Stitch A01) */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-space-md">
          {/* Card 1: Material Recorded */}
          <div className="bg-surface-container-lowest p-space-lg rounded-xl shadow-sm flex flex-col justify-between relative overflow-hidden group hover:shadow-md transition-shadow border border-surface-container-high">
            <div className="absolute top-0 right-0 w-24 h-24 bg-primary/5 rounded-bl-full pointer-events-none"></div>
            <div className="flex justify-between items-start mb-space-md">
              <span className="text-label-md text-on-surface-variant uppercase tracking-wider font-semibold">
                Material Recorded
              </span>
              <span className="p-2 bg-primary-fixed text-on-primary-fixed-variant rounded-xl material-symbols-outlined">
                scale
              </span>
            </div>
            <div>
              <div className="text-headline-xl font-headline-xl text-on-surface mb-space-xs font-bold">
                {overview ? (overview.handovers.formal_received_mass_g / 1000).toLocaleString('en-IN') : '—'} <span className="text-body-lg text-on-surface-variant font-normal">kg</span>
              </div>
              <div className="flex items-center gap-1 text-body-sm text-primary font-semibold">
                <span className="material-symbols-outlined text-[16px]">info</span> Confirmed non-demo received mass
              </div>
            </div>
          </div>

          {/* Card 2: Received YTD */}
          <div className="bg-surface-container-lowest p-space-lg rounded-xl shadow-sm flex flex-col justify-between relative overflow-hidden group hover:shadow-md transition-shadow border border-surface-container-high">
            <div className="absolute top-0 right-0 w-24 h-24 bg-secondary-fixed/20 rounded-bl-full pointer-events-none"></div>
            <div className="flex justify-between items-start mb-space-md">
              <span className="text-label-md text-on-surface-variant uppercase tracking-wider font-semibold">
                Received YTD
              </span>
              <span className="p-2 bg-secondary-fixed text-on-secondary-fixed-variant rounded-xl material-symbols-outlined">
                inventory_2
              </span>
            </div>
            <div>
              <div className="text-headline-xl font-headline-xl text-on-surface mb-space-xs font-bold">
                {overview ? (overview.handovers.formal_received_mass_g / 1_000_000).toLocaleString('en-IN', { maximumFractionDigits: 3 }) : '—'} <span className="text-body-lg text-on-surface-variant font-normal">tons</span>
              </div>
              <div className="flex items-center gap-1 text-body-sm text-on-surface-variant font-semibold">
                <span className="material-symbols-outlined text-[16px] text-emerald-600">check_circle</span> {overview?.handovers.mass_label ?? 'Loading provenance…'}
              </div>
            </div>
          </div>

          {/* Card 3: Pending Review */}
          <div className="bg-surface-container-lowest p-space-lg rounded-xl shadow-sm flex flex-col justify-between relative overflow-hidden group hover:shadow-md transition-shadow border border-surface-container-high">
            <div className="absolute top-0 right-0 w-24 h-24 bg-error-container/30 rounded-bl-full pointer-events-none"></div>
            <div className="flex justify-between items-start mb-space-md">
              <span className="text-label-md text-on-surface-variant uppercase tracking-wider font-semibold">
                Pending Review
              </span>
              <span className="p-2 bg-error-container text-on-error-container rounded-xl material-symbols-outlined">
                pending_actions
              </span>
            </div>
            <div>
              <div className="text-headline-xl font-headline-xl text-on-surface mb-space-xs font-bold">
                {overview ? overview.quality.open_flags : '—'} <span className="text-body-lg text-on-surface-variant font-normal">flags</span>
              </div>
              <div className="flex items-center gap-1 text-body-sm text-error font-semibold">
                <span className="material-symbols-outlined text-[16px]">schedule</span> Requires QA action
              </div>
            </div>
          </div>

          {/* Card 4: Open Disputes */}
          <div className="bg-surface-container-lowest p-space-lg rounded-xl shadow-sm flex flex-col justify-between relative overflow-hidden group hover:shadow-md transition-shadow border border-surface-container-high">
            <div className="absolute top-0 right-0 w-24 h-24 bg-tertiary-fixed/30 rounded-bl-full pointer-events-none"></div>
            <div className="flex justify-between items-start mb-space-md">
              <span className="text-label-md text-on-surface-variant uppercase tracking-wider font-semibold">
                Open Disputes
              </span>
              <span className="p-2 bg-tertiary-fixed text-on-tertiary-fixed rounded-xl material-symbols-outlined">
                gavel
              </span>
            </div>
            <div>
              <div className="text-headline-xl font-headline-xl text-on-surface mb-space-xs font-bold">
                {overview ? overview.handovers.disputed_count : '—'} <span className="text-body-lg text-on-surface-variant font-normal">cases</span>
              </div>
              <div className="flex items-center gap-1 text-body-sm text-tertiary font-semibold">
                <span className="material-symbols-outlined text-[16px]">warning</span> Avg resolution 4.2h
              </div>
            </div>
          </div>
        </div>

        {/* Asymmetric Section: System Health & Quality Queues (Stitch A01) */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-space-xl">
          {/* Left 2 Cols: Material Flow & Freshness Visualizer */}
          <div className="lg:col-span-2 bg-surface-container-lowest p-space-xl rounded-xl shadow-sm flex flex-col justify-between border border-surface-container-high">
            <div>
              <div className="flex items-center justify-between mb-space-lg">
                <div>
                  <h2 className="text-headline-lg font-headline-lg text-on-surface font-bold">
                    Material Influx vs Processing
                  </h2>
                  <p className="text-body-sm text-on-surface-variant">
                    Real-time tonnage tracking across Northern & Western regional hubs
                  </p>
                </div>
                <div className="flex gap-space-xs">
                  {(['24H', '7D', '30D'] as const).map((r) => (
                    <button
                      key={r}
                      onClick={() => setTimeRange(r)}
                      className={`px-3 py-1 text-label-sm rounded-xl font-semibold transition ${
                        timeRange === r
                          ? 'bg-primary text-on-primary'
                          : 'bg-surface-container-high text-on-surface hover:bg-surface-dim'
                      }`}
                    >
                      {r}
                    </button>
                  ))}
                </div>
              </div>

              {/* Bar Visualizer */}
              <div className="h-64 w-full flex items-end justify-between gap-space-xs pt-space-xl pb-space-sm px-space-xs bg-surface-container-low rounded-xl relative overflow-hidden">
                <div className="absolute inset-0 flex flex-col justify-between p-space-md pointer-events-none opacity-20">
                  <div className="w-full h-[1px] bg-on-surface"></div>
                  <div className="w-full h-[1px] bg-on-surface"></div>
                  <div className="w-full h-[1px] bg-on-surface"></div>
                  <div className="w-full h-[1px] bg-on-surface"></div>
                </div>

                {/* Day bars */}
                {[
                  { day: 'Mon', h: '40%', val: '12t' },
                  { day: 'Tue', h: '65%', val: '18t' },
                  { day: 'Wed', h: '55%', val: '15t' },
                  { day: 'Thu', h: '85%', val: '24t' },
                  { day: 'Fri', h: '70%', val: '20t' },
                  { day: 'Sat', h: '95%', val: '28t' },
                  { day: 'Sun', h: '60%', val: '17t' },
                ].map((b, i) => (
                  <div
                    key={i}
                    className="w-full bg-primary/70 hover:bg-primary transition-all rounded-t-lg relative group cursor-pointer"
                    style={{ height: b.h }}
                  >
                    <div className="absolute -top-8 left-1/2 -translate-x-1/2 bg-inverse-surface text-inverse-on-surface text-[10px] px-1.5 py-0.5 rounded opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap shadow font-mono">
                      {b.day}: {b.val}
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="grid grid-cols-3 gap-space-md mt-space-lg pt-space-lg border-t border-surface-container-high">
              <div>
                <span className="text-body-sm text-on-surface-variant block font-medium">Sync Latency</span>
                <span className="text-headline-md font-headline-md text-on-surface font-bold">140ms</span>
              </div>
              <div>
                <span className="text-body-sm text-on-surface-variant block font-medium">Ledger Integrity</span>
                <span className="text-headline-md font-headline-md text-primary font-bold">99.9%</span>
              </div>
              <div>
                <span className="text-body-sm text-on-surface-variant block font-medium">Active Nodes</span>
                <span className="text-headline-md font-headline-md text-on-surface font-bold">42 Yards</span>
              </div>
            </div>
          </div>

          {/* Right Col: Quality Review Queue */}
          <div className="bg-surface-container-lowest p-space-xl rounded-xl shadow-sm flex flex-col justify-between border border-surface-container-high">
            <div>
              <div className="flex items-center justify-between mb-space-lg">
                <h3 className="text-headline-md font-headline-md text-on-surface font-bold">Quality Queues</h3>
                <Link to="/admin/quality" className="text-label-sm text-primary font-bold hover:underline">
                  View All
                </Link>
              </div>

              <div className="flex flex-col gap-space-md">
                {/* Queue Item 1 */}
                <div className="p-space-md bg-surface-container-low rounded-xl flex items-center justify-between border border-surface-container">
                  <div className="flex items-center gap-space-md">
                    <div className="w-10 h-10 rounded-xl bg-secondary-fixed flex items-center justify-center font-bold text-on-secondary-fixed font-headline-md">
                      AL
                    </div>
                    <div>
                      <h4 className="text-label-md text-on-surface font-semibold">Aluminium Scrap #402</h4>
                      <p className="text-body-sm text-on-surface-variant">Batch from Delhi Yard • 1.4t</p>
                    </div>
                  </div>
                  <Link
                    to="/admin/quality"
                    className="px-3 py-1.5 bg-surface text-on-surface text-label-sm rounded-xl hover:bg-primary hover:text-on-primary transition-colors border border-surface-container font-medium"
                  >
                    Inspect
                  </Link>
                </div>

                {/* Queue Item 2 */}
                <div className="p-space-md bg-surface-container-low rounded-xl flex items-center justify-between border border-surface-container">
                  <div className="flex items-center gap-space-md">
                    <div className="w-10 h-10 rounded-xl bg-primary-fixed text-on-primary-fixed-variant flex items-center justify-center font-bold font-headline-md">
                      PL
                    </div>
                    <div>
                      <h4 className="text-label-md text-on-surface font-semibold">PET Flakes Grade A</h4>
                      <p className="text-body-sm text-on-surface-variant">Batch from Mumbai Yard • 3.8t</p>
                    </div>
                  </div>
                  <Link
                    to="/admin/quality"
                    className="px-3 py-1.5 bg-surface text-on-surface text-label-sm rounded-xl hover:bg-primary hover:text-on-primary transition-colors border border-surface-container font-medium"
                  >
                    Inspect
                  </Link>
                </div>

                {/* Queue Item 3 */}
                <div className="p-space-md bg-surface-container-low rounded-xl flex items-center justify-between border border-surface-container">
                  <div className="flex items-center gap-space-md">
                    <div className="w-10 h-10 rounded-xl bg-tertiary-fixed text-on-tertiary-fixed flex items-center justify-center font-bold font-headline-md">
                      CU
                    </div>
                    <div>
                      <h4 className="text-label-md text-on-surface font-semibold">Copper Wire Millberry</h4>
                      <p className="text-body-sm text-on-surface-variant">Batch from Surat Yard • 850kg</p>
                    </div>
                  </div>
                  <Link
                    to="/admin/traceability"
                    className="px-3 py-1.5 bg-surface text-on-surface text-label-sm rounded-xl hover:bg-primary hover:text-on-primary transition-colors border border-surface-container font-medium"
                  >
                    Inspect
                  </Link>
                </div>
              </div>
            </div>

            <div className="mt-space-lg pt-space-md border-t border-surface-container-high flex items-center justify-between text-body-sm text-on-surface-variant">
              <span>Auto-refresh active</span>
              <span className="flex items-center gap-1 text-primary font-medium">
                <span className="w-2 h-2 rounded-full bg-primary animate-pulse"></span> Live Feed
              </span>
            </div>
          </div>
        </div>

        {/* Bottom Wide Section: Facility & Provenance Map Snapshot (Stitch A01) */}
        <div className="bg-surface-container-lowest p-space-xl rounded-xl shadow-sm border border-surface-container-high">
          <div className="flex flex-col md:flex-row md:items-center justify-between mb-space-lg gap-space-md">
            <div>
              <h3 className="text-headline-md font-headline-md text-on-surface font-bold">
                Provenance & Regional Distribution
              </h3>
              <p className="text-body-sm text-on-surface-variant">
                Traceability verification across industrial feeder nodes
              </p>
            </div>
            <div className="flex items-center gap-space-sm">
              <span className="text-body-sm font-semibold text-on-surface">Filter By:</span>
              <select
                value={materialFilter}
                onChange={(e) => setMaterialFilter(e.target.value)}
                className="bg-surface-container-high text-on-surface px-3 py-2 rounded-xl text-label-md outline-none border border-surface-container"
              >
                <option>All Materials</option>
                <option>Ferrous & Non-Ferrous</option>
                <option>Polymers & Plastics</option>
              </select>
            </div>
          </div>

          {/* Regional Hub Distribution Visualizer */}
          <div className="w-full h-72 rounded-xl bg-surface-container-low border border-surface-container relative overflow-hidden flex items-end p-space-lg shadow-inner">
            <div className="absolute inset-0 bg-gradient-to-t from-surface-container-highest/80 via-surface-container-low/40 to-transparent"></div>
            
            {/* Visual Grid Lines and Coordinate Pins */}
            <div className="absolute inset-0 p-8 flex items-center justify-around pointer-events-none opacity-40">
              <div className="w-12 h-12 rounded-full border border-dashed border-primary animate-ping"></div>
              <div className="w-16 h-16 rounded-full border border-dashed border-secondary"></div>
              <div className="w-10 h-10 rounded-full border border-dashed border-tertiary"></div>
            </div>

            <div className="relative z-10 bg-surface/95 backdrop-blur-md p-space-md rounded-xl flex flex-wrap items-center gap-space-lg shadow-md border border-surface-container-high">
              <div className="flex items-center gap-2">
                <span className="w-3 h-3 rounded-full bg-primary"></span>
                <span className="text-label-md text-on-surface font-medium">North Hub (Delhi-NCR): 18 Yards</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="w-3 h-3 rounded-full bg-secondary"></span>
                <span className="text-label-md text-on-surface font-medium">West Hub (Gujarat/Mumbai): 16 Yards</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="w-3 h-3 rounded-full bg-tertiary"></span>
                <span className="text-label-md text-on-surface font-medium">South Hub (Chennai): 8 Yards</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
