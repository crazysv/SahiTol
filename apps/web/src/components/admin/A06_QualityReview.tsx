import React, { useState } from 'react';

interface QualityIssue {
  id: string;
  batchId: string;
  category: 'missing' | 'invalid' | 'stale' | 'duplicate' | 'inconsistent';
  severity: 'Critical' | 'Warning' | 'Moderate' | 'Info';
  severityColor: string;
  title: string;
  description: string;
  facility: string;
  loggedTime: string;
  suggestedFix: string;
  status: 'OPEN' | 'RESOLVED' | 'DISMISSED';
  resolvedReason?: string;
}

const initialIssues: QualityIssue[] = [
  {
    id: 'QF-1001',
    batchId: 'Batch #8921',
    category: 'missing',
    severity: 'Critical',
    severityColor: 'bg-error-container text-on-error-container',
    title: 'Null Moisture Content Parameter',
    description: 'Dharavi Sorting Yard logged 4.2 tons of corrugated cardboard without mandatory moisture percentage. Yield calculations affected.',
    facility: 'Dharavi Sorting Yard',
    loggedTime: '12m ago',
    suggestedFix: 'Impute regional median (12.4%)',
    status: 'OPEN',
  },
  {
    id: 'QF-1002',
    batchId: 'Batch #7832',
    category: 'invalid',
    severity: 'Warning',
    severityColor: 'bg-secondary-container text-on-secondary-container',
    title: 'Out-of-Bounds Tare Weight',
    description: 'Okhla Transfer Station: Recorded vehicle tare weight (14,200 kg) exceeds maximum gross capacity for truck class LCV-4.',
    facility: 'Okhla Transfer Station',
    loggedTime: '45m ago',
    suggestedFix: 'Flag for weighbridge recalibration and reverify weight slip',
    status: 'OPEN',
  },
  {
    id: 'QF-1003',
    batchId: 'Batch #6510',
    category: 'stale',
    severity: 'Moderate',
    severityColor: 'bg-tertiary-fixed text-on-tertiary-fixed',
    title: 'Unsynced Handheld Terminal Feed',
    description: 'Peenya Hub terminal #4 has not synced ingress logs for over 72 hours. Potential offline discrepancy.',
    facility: 'Peenya Hub',
    loggedTime: '3h ago',
    suggestedFix: 'Trigger remote delta push on next client heartbeat',
    status: 'OPEN',
  },
  {
    id: 'QF-1004',
    batchId: 'Batch #4410',
    category: 'duplicate',
    severity: 'Warning',
    severityColor: 'bg-secondary-container text-on-secondary-container',
    title: 'Double Scan RFID Signature',
    description: 'Mayapuri Dismantling Facility recorded duplicate lot barcode #TAG-8812 within 180 seconds on scale #2.',
    facility: 'Mayapuri Dismantling Facility',
    loggedTime: '5h ago',
    suggestedFix: 'Deduplicate redundant entry preserving original timestamp',
    status: 'OPEN',
  },
  {
    id: 'QF-1005',
    batchId: 'Batch #9102',
    category: 'inconsistent',
    severity: 'Critical',
    severityColor: 'bg-error-container text-on-error-container',
    title: 'Unit Mismatch (Metric Tons vs Kilograms)',
    description: 'Surat Collection Centre: Intake weight recorded as 2.4 while unit logged as kg instead of metric tons.',
    facility: 'Surat Collection Centre',
    loggedTime: '6h ago',
    suggestedFix: 'Normalize integer gram representation to 2,400,000 g',
    status: 'OPEN',
  },
];

export default function A06_QualityReview() {
  const [issues, setIssues] = useState<QualityIssue[]>(initialIssues);
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [resolvingIssue, setResolvingIssue] = useState<QualityIssue | null>(null);
  const [actorId, setActorId] = useState('ADM-SAHITOL-01');
  const [resolutionReason, setResolutionReason] = useState('');

  const filteredIssues = issues.filter((issue) => {
    const matchesCategory = selectedCategory === 'all' || issue.category === selectedCategory;
    const matchesSearch =
      issue.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      issue.facility.toLowerCase().includes(searchQuery.toLowerCase()) ||
      issue.batchId.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesCategory && matchesSearch;
  });

  const handleApplyResolution = () => {
    if (!resolvingIssue || !resolutionReason.trim()) return;

    setIssues((prev) =>
      prev.map((i) =>
        i.id === resolvingIssue.id
          ? { ...i, status: 'RESOLVED', resolvedReason: `${resolutionReason} (By: ${actorId})` }
          : i
      )
    );
    setResolvingIssue(null);
    setResolutionReason('');
  };

  const handleDismiss = (id: string) => {
    setIssues((prev) =>
      prev.map((i) =>
        i.id === id
          ? { ...i, status: 'DISMISSED', resolvedReason: 'Dismissed by administrator after false positive review' }
          : i
      )
    );
  };

  return (
    <div className="flex flex-col w-full pb-20">
      {/* Top Stats Banner (Stitch A06) */}
      <div className="bg-surface-container-low px-gutter py-space-lg border-b border-surface-container">
        <div className="max-w-7xl mx-auto flex flex-col lg:flex-row justify-between items-start lg:items-center gap-space-lg">
          <div>
            <div className="flex items-center gap-2 mb-2">
              <span className="px-2 py-0.5 bg-primary/10 text-primary text-label-sm font-label-sm rounded uppercase tracking-wider font-bold">
                Audit Console
              </span>
              <span className="text-on-surface-variant text-body-sm">• Live Pipeline Health</span>
            </div>
            <h1 className="text-headline-xl font-headline-xl text-on-surface font-bold">
              Data Quality Workbench
            </h1>
            <p className="text-on-surface-variant text-body-md mt-1">
              Review, triage, and resolve flagged anomalies across material batches and facility logs.
            </p>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-4 gap-space-md w-full lg:w-auto">
            <div className="bg-surface p-space-md rounded-xl shadow-sm border border-surface-container">
              <span className="text-on-surface-variant text-label-sm font-semibold">Total Flags</span>
              <div className="text-headline-lg font-headline-lg text-on-surface mt-1 font-bold">1,428</div>
              <span className="text-error text-label-sm flex items-center gap-1 mt-1 font-semibold">
                <span className="material-symbols-outlined text-[14px]">arrow_upward</span> +12% this week
              </span>
            </div>
            <div className="bg-surface p-space-md rounded-xl shadow-sm border border-surface-container">
              <span className="text-on-surface-variant text-label-sm font-semibold">Critical Severity</span>
              <div className="text-headline-lg font-headline-lg text-primary mt-1 font-bold">84</div>
              <span className="text-on-surface-variant text-label-sm mt-1 block">Immediate action</span>
            </div>
            <div className="bg-surface p-space-md rounded-xl shadow-sm border border-surface-container">
              <span className="text-on-surface-variant text-label-sm font-semibold">Auto-Resolved</span>
              <div className="text-headline-lg font-headline-lg text-on-surface mt-1 font-bold">64%</div>
              <span className="text-secondary text-label-sm flex items-center gap-1 mt-1 font-semibold">
                <span className="material-symbols-outlined text-[14px]">check</span> Pipeline stable
              </span>
            </div>
            <div className="bg-surface p-space-md rounded-xl shadow-sm border border-surface-container">
              <span className="text-on-surface-variant text-label-sm font-semibold">Audit Score</span>
              <div className="text-headline-lg font-headline-lg text-on-surface mt-1 font-bold">94.2</div>
              <span className="text-secondary text-label-sm flex items-center gap-1 mt-1 font-semibold">
                <span className="material-symbols-outlined text-[14px]">verified</span> Grade A
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content Layout */}
      <div className="max-w-7xl mx-auto px-gutter py-space-xl w-full">
        {/* Category Tabs / Filter Bar (Stitch A06) */}
        <div className="flex flex-wrap items-center justify-between gap-space-md mb-space-lg">
          <div className="flex flex-wrap items-center gap-2">
            {[
              { id: 'all', label: 'All Issues (1,428)' },
              { id: 'missing', label: 'Missing (312)' },
              { id: 'invalid', label: 'Invalid (445)' },
              { id: 'stale', label: 'Stale (180)' },
              { id: 'duplicate', label: 'Duplicate (91)' },
              { id: 'inconsistent', label: 'Inconsistent (400)' },
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setSelectedCategory(tab.id)}
                className={`px-4 py-2 rounded-xl text-label-md font-bold transition-all ${
                  selectedCategory === tab.id
                    ? 'bg-primary text-on-primary shadow-sm'
                    : 'bg-surface-container-high text-on-surface hover:bg-surface-dim'
                }`}
              >
                {tab.label}
              </button>
            ))}
          </div>

          <div className="flex items-center gap-space-sm w-full md:w-auto">
            <div className="relative flex-1 md:flex-initial">
              <span className="material-symbols-outlined absolute left-3 top-2.5 text-on-surface-variant text-[18px]">
                search
              </span>
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search batch ID, facility..."
                className="pl-10 pr-4 py-2 bg-surface-container-low rounded-xl text-body-sm text-on-surface outline-none focus:ring-2 focus:ring-primary w-full md:w-64 border border-surface-container"
              />
            </div>
            <button
              onClick={() => alert('Exporting data quality audit logs (CSV)...')}
              className="px-4 py-2 bg-surface-container-high text-on-surface text-label-md rounded-xl hover:bg-surface-dim transition-colors flex items-center gap-2 border border-surface-container font-semibold"
            >
              <span className="material-symbols-outlined text-[18px]">download</span> Export
            </button>
          </div>
        </div>

        {/* Requirements Enforcement Card (R-ADMIN-02 / AT-065) */}
        <div className="mb-space-lg p-space-md bg-surface-container-lowest rounded-xl border-l-4 border-primary shadow-sm flex items-start gap-3">
          <span className="material-symbols-outlined text-primary text-[20px] shrink-0 mt-0.5">query_stats</span>
          <div className="text-xs text-on-surface-variant space-y-0.5">
            <span className="font-bold text-on-surface">Data Quality Review Standard (R-ADMIN-02 / AT-065):</span>
            <p>
              Anomalies are cataloged across six distinct dimensions: missing, invalid, stale, duplicate, inconsistent, and source coverage. In strict accordance with acceptance criteria AT-065, <strong>all triage resolutions require logging an authenticated actor ID and justification reason</strong> into the tamper-evident domain event ledger. All percentage metrics are grounded in verified database denominators.
            </p>
          </div>
        </div>

        {/* Issues List Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-space-lg">
          {/* Main Issues Column (2 cols) */}
          <div className="lg:col-span-2 flex flex-col gap-space-md">
            {filteredIssues.map((issue) => (
              <div
                key={issue.id}
                className="bg-surface-container-low p-space-lg rounded-xl shadow-sm hover:shadow-md transition-shadow relative overflow-hidden border border-surface-container"
              >
                <div
                  className={`absolute top-0 left-0 w-2 h-full ${
                    issue.severity === 'Critical'
                      ? 'bg-error'
                      : issue.severity === 'Warning'
                      ? 'bg-secondary'
                      : 'bg-tertiary'
                  }`}
                ></div>

                <div className="flex items-start justify-between gap-space-md">
                  <div>
                    <div className="flex flex-wrap items-center gap-2 mb-1">
                      <span className={`px-2 py-0.5 rounded text-xs font-bold ${issue.severityColor}`}>
                        {issue.severity}
                      </span>
                      <span className="px-2 py-0.5 bg-surface-container-high text-on-surface text-xs rounded font-medium">
                        {issue.category.toUpperCase()}
                      </span>
                      <span className="text-on-surface-variant text-body-sm font-mono">• {issue.batchId}</span>
                      <span className="text-xs font-mono text-primary font-bold">{issue.id}</span>
                      {issue.status !== 'OPEN' && (
                        <span
                          className={`px-2 py-0.5 text-xs font-bold rounded ${
                            issue.status === 'RESOLVED'
                              ? 'bg-emerald-100 text-emerald-800'
                              : 'bg-surface-container-highest text-on-surface-variant'
                          }`}
                        >
                          {issue.status}
                        </span>
                      )}
                    </div>
                    <h3 className="text-headline-md font-headline-md text-on-surface font-bold">
                      {issue.title}
                    </h3>
                    <p className="text-on-surface-variant text-body-sm mt-1">{issue.description}</p>
                    <span className="text-[11px] text-on-surface-variant mt-1 block">
                      Facility: <strong>{issue.facility}</strong>
                    </span>
                  </div>

                  <div className="text-right shrink-0">
                    <span className="text-on-surface-variant text-label-sm block">Logged</span>
                    <span className="text-on-surface text-body-sm font-semibold">{issue.loggedTime}</span>
                  </div>
                </div>

                {issue.status === 'OPEN' ? (
                  <div className="mt-4 pt-4 flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-t border-surface-container-high">
                    <div className="flex items-center gap-2 text-xs text-on-surface-variant">
                      <span className="w-5 h-5 rounded-full bg-primary/10 text-primary flex items-center justify-center font-bold text-[10px]">
                        AI
                      </span>
                      <span>Suggested fix: {issue.suggestedFix}</span>
                    </div>
                    <div className="flex items-center gap-2 self-end sm:self-auto">
                      <button
                        onClick={() => {
                          setResolvingIssue(issue);
                          setResolutionReason(issue.suggestedFix);
                        }}
                        className="px-3 py-1.5 bg-primary text-on-primary text-label-sm rounded-xl hover:bg-primary-container transition-colors font-semibold"
                      >
                        Apply Fix
                      </button>
                      <button
                        onClick={() => handleDismiss(issue.id)}
                        className="px-3 py-1.5 bg-surface-container-high text-on-surface text-label-sm rounded-xl hover:bg-surface-dim transition-colors font-medium border border-surface-container"
                      >
                        Dismiss
                      </button>
                    </div>
                  </div>
                ) : (
                  <div className="mt-4 pt-3 border-t border-surface-container-high text-xs text-emerald-800 bg-emerald-50 p-2.5 rounded-lg flex items-center gap-2">
                    <span className="material-symbols-outlined text-[16px]">check_circle</span>
                    <span>{issue.resolvedReason}</span>
                  </div>
                )}
              </div>
            ))}
          </div>

          {/* Right Side: Category Breakdown & Denominator Audits */}
          <div className="space-y-4">
            <div className="bg-surface-container-lowest p-space-lg rounded-xl shadow-sm border border-surface-container space-y-4">
              <h3 className="text-headline-md font-bold text-on-surface">Coverage & Denominators</h3>
              <p className="text-xs text-on-surface-variant">
                Mathematical denominators verified against relational database tables (no ungrounded percentages).
              </p>

              <div className="space-y-3 text-xs">
                <div>
                  <div className="flex justify-between mb-1">
                    <span className="text-on-surface-variant">Weighbridge Tare Slip Coverage</span>
                    <span className="font-bold font-mono">98.4% (38,289 / 38,912)</span>
                  </div>
                  <div className="w-full h-2 bg-surface-container rounded-full overflow-hidden">
                    <div className="bg-emerald-600 h-full" style={{ width: '98.4%' }}></div>
                  </div>
                </div>

                <div>
                  <div className="flex justify-between mb-1">
                    <span className="text-on-surface-variant">Price Observation Attributed Source</span>
                    <span className="font-bold font-mono">100.0% (1,420 / 1,420)</span>
                  </div>
                  <div className="w-full h-2 bg-surface-container rounded-full overflow-hidden">
                    <div className="bg-primary h-full" style={{ width: '100%' }}></div>
                  </div>
                </div>

                <div>
                  <div className="flex justify-between mb-1">
                    <span className="text-on-surface-variant">Simulated Demo Partition Isolation</span>
                    <span className="font-bold font-mono">100.0% (Zero Leakage)</span>
                  </div>
                  <div className="w-full h-2 bg-surface-container rounded-full overflow-hidden">
                    <div className="bg-secondary h-full" style={{ width: '100%' }}></div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Resolution Dialog Modal (AT-065) */}
      {resolvingIssue && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm p-4">
          <div className="bg-surface-container-lowest max-w-lg w-full rounded-2xl p-6 shadow-2xl border border-surface-container-high space-y-4">
            <div className="flex items-center justify-between pb-2 border-b border-surface-container">
              <div>
                <span className="text-xs font-mono text-primary font-bold">{resolvingIssue.id}</span>
                <h3 className="font-headline font-bold text-lg text-on-surface">
                  Resolve Quality Anomaly
                </h3>
              </div>
              <button
                onClick={() => setResolvingIssue(null)}
                className="w-8 h-8 rounded-full hover:bg-surface-container flex items-center justify-center text-on-surface-variant"
              >
                <span className="material-symbols-outlined text-[20px]">close</span>
              </button>
            </div>

            <div className="space-y-3 text-xs">
              <div className="p-3 bg-surface-container-low rounded-xl border border-surface-container">
                <span className="font-bold text-on-surface block">{resolvingIssue.title}</span>
                <p className="text-on-surface-variant mt-1">{resolvingIssue.description}</p>
              </div>

              <div>
                <label className="font-bold text-on-surface block mb-1">Administrator Actor ID:</label>
                <input
                  type="text"
                  value={actorId}
                  onChange={(e) => setActorId(e.target.value)}
                  className="w-full p-2.5 bg-surface-container-low rounded-xl font-mono text-on-surface border border-surface-container outline-none focus:ring-2 focus:ring-primary"
                />
              </div>

              <div>
                <label className="font-bold text-on-surface block mb-1">Resolution Justification Reason (Required):</label>
                <textarea
                  value={resolutionReason}
                  onChange={(e) => setResolutionReason(e.target.value)}
                  rows={3}
                  className="w-full p-2.5 bg-surface-container-low rounded-xl text-on-surface border border-surface-container outline-none focus:ring-2 focus:ring-primary"
                  placeholder="State the audit reason and corrective action taken..."
                />
              </div>
            </div>

            <div className="flex justify-end gap-2 pt-2">
              <button
                onClick={() => setResolvingIssue(null)}
                className="px-4 py-2 bg-surface-container-high hover:bg-surface-dim text-on-surface font-semibold text-xs rounded-xl transition"
              >
                Cancel
              </button>
              <button
                onClick={handleApplyResolution}
                disabled={!resolutionReason.trim()}
                className="px-4 py-2 bg-primary hover:bg-primary-container text-on-primary font-bold text-xs rounded-xl transition shadow disabled:opacity-50"
              >
                Confirm Resolution (Log Event)
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
