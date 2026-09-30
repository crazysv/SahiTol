import React, { useState } from 'react';

interface CollectorRecord {
  id: string;
  alias: string;
  avatar: string;
  avatarBg: string;
  avatarColor: string;
  region: string;
  regionGroup: string;
  lots: number;
  recentActivity: string;
}

const mockCollectors: CollectorRecord[] = [
  {
    id: '#COL-8821',
    alias: 'IronFox_99',
    avatar: 'IF',
    avatarBg: 'bg-secondary-container',
    avatarColor: 'text-on-secondary-container',
    region: 'North Sector (Zone 4)',
    regionGroup: 'North Sector',
    lots: 142,
    recentActivity: '2 hours ago',
  },
  {
    id: '#COL-3049',
    alias: 'CopperDelta',
    avatar: 'CD',
    avatarBg: 'bg-primary-fixed-dim',
    avatarColor: 'text-on-primary-fixed',
    region: 'Eastern Hub (Zone 1)',
    regionGroup: 'Eastern Hub',
    lots: 98,
    recentActivity: '15 mins ago',
  },
  {
    id: '#COL-9112',
    alias: 'KabadPioneer',
    avatar: 'KP',
    avatarBg: 'bg-secondary-container',
    avatarColor: 'text-on-secondary-container',
    region: 'Western Corridor (Zone 7)',
    regionGroup: 'Western Corridor',
    lots: 310,
    recentActivity: '1 day ago',
  },
  {
    id: '#COL-5519',
    alias: 'EcoScrap_42',
    avatar: 'ES',
    avatarBg: 'bg-surface-container-high',
    avatarColor: 'text-on-surface',
    region: 'North Sector (Zone 2)',
    regionGroup: 'North Sector',
    lots: 64,
    recentActivity: '4 hours ago',
  },
  {
    id: '#COL-7740',
    alias: 'MetroKabadi',
    avatar: 'MK',
    avatarBg: 'bg-primary-fixed',
    avatarColor: 'text-on-primary-fixed-variant',
    region: 'Western Corridor (Zone 3)',
    regionGroup: 'Western Corridor',
    lots: 185,
    recentActivity: '6 hours ago',
  },
];

export default function A02_Collectors() {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedRegion, setSelectedRegion] = useState('All');
  const [activeModalRecord, setActiveModalRecord] = useState<CollectorRecord | null>(null);
  const [exportNotice, setExportNotice] = useState(false);

  const filteredCollectors = mockCollectors.filter((c) => {
    const matchesRegion = selectedRegion === 'All' || c.regionGroup === selectedRegion;
    const matchesSearch =
      c.alias.toLowerCase().includes(searchQuery.toLowerCase()) ||
      c.region.toLowerCase().includes(searchQuery.toLowerCase()) ||
      c.id.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesRegion && matchesSearch;
  });

  const handleExport = () => {
    setExportNotice(true);
    setTimeout(() => setExportNotice(false), 3000);
  };

  return (
    <div className="flex flex-col w-full">
      <div className="max-w-7xl mx-auto w-full px-gutter py-space-xl">
        {/* Top Security & Status Banner (Stitch A02) */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-space-md mb-space-xl p-space-lg bg-surface-container-low rounded-xl border border-surface-container">
          <div className="flex items-center gap-space-md">
            <div className="w-12 h-12 rounded-xl bg-primary flex items-center justify-center text-on-primary shadow-sm">
              <span className="material-symbols-outlined text-[24px]">verified_user</span>
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="text-label-sm uppercase tracking-wider text-primary font-bold">
                  Privacy Mask Active
                </span>
                <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-bold bg-secondary-container text-on-secondary-container">
                  Zero-PII Zone
                </span>
              </div>
              <h1 className="text-headline-lg font-headline-lg text-on-surface font-bold">
                Collector Minimal Records Directory
              </h1>
            </div>
          </div>
          <div className="flex items-center gap-space-sm">
            <div className="px-4 py-2 bg-surface-container rounded-xl text-body-sm text-on-surface-variant flex items-center gap-2 border border-surface-container-high">
              <span className="w-2.5 h-2.5 rounded-full bg-emerald-600 animate-pulse"></span>
              <span className="font-mono">Encrypted Gateway v4.2</span>
            </div>
          </div>
        </div>

        {/* Quick Stats & Filter Bar (Stitch A02) */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-space-md mb-space-xl">
          <div className="p-space-lg bg-surface-container-low rounded-xl border border-surface-container">
            <span className="text-label-sm text-on-surface-variant uppercase tracking-wider font-semibold">
              Active Aliases
            </span>
            <div className="text-headline-xl font-headline-xl text-on-surface mt-1 font-bold">1,420</div>
            <span className="text-body-sm text-on-surface-variant">Anonymized field units</span>
          </div>
          <div className="p-space-lg bg-surface-container-low rounded-xl border border-surface-container">
            <span className="text-label-sm text-on-surface-variant uppercase tracking-wider font-semibold">
              Total Lots Logged
            </span>
            <div className="text-headline-xl font-headline-xl text-primary mt-1 font-bold">38,912</div>
            <span className="text-body-sm text-on-surface-variant">Verified material batches</span>
          </div>
          <div className="p-space-lg bg-surface-container-low rounded-xl border border-surface-container">
            <span className="text-label-sm text-on-surface-variant uppercase tracking-wider font-semibold">
              Masked Regions
            </span>
            <div className="text-headline-xl font-headline-xl text-on-surface mt-1 font-bold">24 Zones</div>
            <span className="text-body-sm text-on-surface-variant">General area indexing only</span>
          </div>
          <div className="p-space-lg bg-surface-container-low rounded-xl flex flex-col justify-center border border-surface-container">
            <button
              onClick={handleExport}
              className="w-full h-12 bg-primary text-on-primary rounded-xl font-label-md flex items-center justify-center gap-2 hover:bg-primary-container transition-colors shadow-sm font-semibold"
            >
              <span className="material-symbols-outlined text-[18px]">download</span>
              Export Index Data
            </button>
            {exportNotice && (
              <span className="text-[11px] text-emerald-700 font-semibold text-center mt-1">
                Sanitized minimal index exported (CSV)
              </span>
            )}
          </div>
        </div>

        {/* Data Minimization Protocol Warning Card */}
        <div className="p-space-md bg-surface-container-lowest rounded-xl mb-space-lg border-l-4 border-primary shadow-sm flex items-start gap-3">
          <span className="material-symbols-outlined text-primary text-[20px] shrink-0 mt-0.5">lock</span>
          <div className="text-xs text-on-surface-variant space-y-0.5">
            <span className="font-bold text-on-surface">Strict Compliance & Data Minimization Protocol (R-ADMIN-01):</span>
            <p>
              In compliance with Digital Personal Data Protection principles, SahiTol administrators never store or display collector government IDs (Aadhaar/PAN), bank accounts, or fine GPS coordinates. Only pseudonymized aliases, coarse operating sectors, and tamper-evident lot counts are indexed.
            </p>
          </div>
        </div>

        {/* Search and Filters (Stitch A02) */}
        <div className="flex flex-col md:flex-row gap-space-md mb-space-lg items-center justify-between">
          <div className="w-full md:w-96 relative">
            <span className="material-symbols-outlined absolute left-3 top-3.5 text-on-surface-variant">search</span>
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Filter by alias or region..."
              className="w-full h-12 pl-10 pr-4 bg-surface-container-low text-on-surface rounded-xl outline-none focus:ring-2 focus:ring-primary text-body-md border border-surface-container"
            />
          </div>
          <div className="flex items-center gap-space-sm w-full md:w-auto overflow-x-auto">
            {['All', 'North Sector', 'Eastern Hub', 'Western Corridor'].map((region) => (
              <button
                key={region}
                onClick={() => setSelectedRegion(region)}
                className={`px-4 py-2.5 rounded-xl text-label-md transition-colors whitespace-nowrap font-medium ${
                  selectedRegion === region
                    ? 'bg-primary text-on-primary font-bold shadow-sm'
                    : 'bg-surface-container-low text-on-surface hover:bg-surface-container-high'
                }`}
              >
                {region === 'All' ? 'All Regions' : region}
              </button>
            ))}
          </div>
        </div>

        {/* Minimal Collector Table (Stitch A02) */}
        <div className="bg-surface-container-low rounded-xl overflow-hidden mb-space-xl border border-surface-container shadow-sm">
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="bg-surface-container-high text-on-surface-variant text-label-md border-b border-surface-container">
                  <th className="p-space-md font-label-lg">Collector Alias</th>
                  <th className="p-space-md font-label-lg">General Region</th>
                  <th className="p-space-md font-label-lg">Lots Recorded</th>
                  <th className="p-space-md font-label-lg">Recent Activity</th>
                  <th className="p-space-md font-label-lg">Privacy Status</th>
                  <th className="p-space-md font-label-lg text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-surface-container bg-surface-container-lowest">
                {filteredCollectors.map((c) => (
                  <tr key={c.id} className="hover:bg-surface-container transition-colors">
                    <td className="p-space-md">
                      <div className="flex items-center gap-3">
                        <div
                          className={`w-10 h-10 rounded-full ${c.avatarBg} ${c.avatarColor} flex items-center justify-center font-bold text-label-md font-headline`}
                        >
                          {c.avatar}
                        </div>
                        <div>
                          <div className="font-label-lg text-on-surface font-semibold">{c.alias}</div>
                          <div className="text-body-sm text-on-surface-variant font-mono text-xs">
                            ID: {c.id}
                          </div>
                        </div>
                      </div>
                    </td>
                    <td className="p-space-md text-body-md text-on-surface">{c.region}</td>
                    <td className="p-space-md font-bold text-on-surface">{c.lots} lots</td>
                    <td className="p-space-md text-body-sm text-on-surface-variant">{c.recentActivity}</td>
                    <td className="p-space-md">
                      <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold bg-emerald-100 text-emerald-800">
                        <span className="material-symbols-outlined text-[14px]">lock</span> PII Scrubbed
                      </span>
                    </td>
                    <td className="p-space-md text-right">
                      <button
                        onClick={() => setActiveModalRecord(c)}
                        className="px-3 py-1.5 bg-surface-container-high hover:bg-primary hover:text-on-primary text-label-sm text-on-surface rounded-lg transition-colors font-medium border border-surface-container"
                      >
                        View Log
                      </button>
                    </td>
                  </tr>
                ))}
                {filteredCollectors.length === 0 && (
                  <tr>
                    <td colSpan={6} className="p-8 text-center text-sm text-on-surface-variant">
                      No collector records found matching "{searchQuery}".
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>

      {/* Collector Details Modal (Stitch A02) */}
      {activeModalRecord && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm p-4">
          <div className="bg-surface-container-lowest max-w-lg w-full rounded-2xl p-6 shadow-2xl border border-surface-container-high space-y-4">
            <div className="flex items-center justify-between pb-3 border-b border-surface-container">
              <div className="flex items-center gap-3">
                <div
                  className={`w-10 h-10 rounded-full ${activeModalRecord.avatarBg} ${activeModalRecord.avatarColor} flex items-center justify-center font-bold font-headline`}
                >
                  {activeModalRecord.avatar}
                </div>
                <div>
                  <h3 className="text-lg font-headline font-bold text-on-surface">
                    {activeModalRecord.alias}
                  </h3>
                  <span className="text-xs font-mono text-on-surface-variant">{activeModalRecord.id}</span>
                </div>
              </div>
              <button
                onClick={() => setActiveModalRecord(null)}
                className="w-8 h-8 rounded-full hover:bg-surface-container flex items-center justify-center text-on-surface-variant"
              >
                <span className="material-symbols-outlined text-[20px]">close</span>
              </button>
            </div>

            <div className="space-y-3">
              <div className="p-3 bg-emerald-50 border border-emerald-200 rounded-xl space-y-1 text-xs text-emerald-900">
                <div className="flex items-center gap-1.5 font-bold text-emerald-800">
                  <span className="material-symbols-outlined text-[16px]">verified_user</span>
                  Verified Privacy Mask Guarantees
                </div>
                <ul className="list-disc pl-4 space-y-0.5 text-[11px] text-emerald-800">
                  <li>No national identity or biometric identifiers stored</li>
                  <li>No bank accounts or payment credentials visible to admin</li>
                  <li>Operating area is strictly blurred to regional zone ({activeModalRecord.region})</li>
                  <li>Authentication credentials stored via Argon2id PIN hashes only</li>
                </ul>
              </div>

              <div className="grid grid-cols-2 gap-2 text-xs">
                <div className="p-2.5 bg-surface-container-low rounded-xl">
                  <span className="text-on-surface-variant block">Cumulative Volume:</span>
                  <span className="font-bold text-on-surface text-sm">{activeModalRecord.lots} Lots Logged</span>
                </div>
                <div className="p-2.5 bg-surface-container-low rounded-xl">
                  <span className="text-on-surface-variant block">Last Seen:</span>
                  <span className="font-bold text-on-surface text-sm">{activeModalRecord.recentActivity}</span>
                </div>
              </div>
            </div>

            <div className="pt-2 flex justify-end">
              <button
                onClick={() => setActiveModalRecord(null)}
                className="px-4 py-2 bg-surface-container-high hover:bg-surface-dim text-on-surface font-label-md rounded-xl transition text-sm font-semibold"
              >
                Close Record
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
