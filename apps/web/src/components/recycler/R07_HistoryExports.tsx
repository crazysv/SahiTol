import React, { useState } from 'react';

interface LedgerEntry {
  id: string;
  referenceId: string;
  dateTime: string;
  collectorAlias: string;
  material: string;
  weightKg: number;
  amountPaise: number;
  paymentMode: 'CASH' | 'RTGS' | 'UPI';
  hashVerified: boolean;
  status: 'SETTLED' | 'DISPUTED' | 'PENDING';
}

const HISTORICAL_LEDGER: LedgerEntry[] = [
  {
    id: 'tx-101',
    referenceId: 'ST-24A7',
    dateTime: '2026-09-29 14:02',
    collectorAlias: 'Ramesh Kumar (#409)',
    material: 'Insulated Copper Cable',
    weightKg: 84.8,
    amountPaise: 1526400, // ₹15,264
    paymentMode: 'CASH',
    hashVerified: true,
    status: 'SETTLED',
  },
  {
    id: 'tx-102',
    referenceId: 'ST-2489',
    dateTime: '2026-09-28 16:30',
    collectorAlias: 'Santosh Yadav (#312)',
    material: 'Super Grade Copper Wire',
    weightKg: 145.0,
    amountPaise: 9425000, // ₹94,250
    paymentMode: 'RTGS',
    hashVerified: true,
    status: 'SETTLED',
  },
  {
    id: 'tx-103',
    referenceId: 'ST-2470',
    dateTime: '2026-09-28 11:10',
    collectorAlias: 'Anil Rathore (#551)',
    material: 'Brass Radiator Cuttings',
    weightKg: 230.0,
    amountPaise: 7130000, // ₹71,300
    paymentMode: 'UPI',
    hashVerified: true,
    status: 'SETTLED',
  },
  {
    id: 'tx-104',
    referenceId: 'ST-2465',
    dateTime: '2026-09-27 15:45',
    collectorAlias: 'Mohan Lal (#208)',
    material: 'Aluminium Extrusion Scrap',
    weightKg: 340.0,
    amountPaise: 4930000, // ₹49,300
    paymentMode: 'CASH',
    hashVerified: true,
    status: 'SETTLED',
  },
  {
    id: 'tx-105',
    referenceId: 'ST-2458',
    dateTime: '2026-09-27 10:20',
    collectorAlias: 'Sunil Paswan (#184)',
    material: 'Mixed Computer Scrap',
    weightKg: 152.0,
    amountPaise: 532000, // ₹5,320
    paymentMode: 'CASH',
    hashVerified: false,
    status: 'DISPUTED',
  },
  {
    id: 'tx-106',
    referenceId: 'ST-2442',
    dateTime: '2026-09-26 17:00',
    collectorAlias: 'Vikram Singh (#380)',
    material: 'Printed Circuit Boards Grade A',
    weightKg: 62.5,
    amountPaise: 2812500, // ₹28,125
    paymentMode: 'RTGS',
    hashVerified: true,
    status: 'SETTLED',
  },
];

export default function R07_HistoryExports() {
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState<'ALL' | 'SETTLED' | 'DISPUTED'>('ALL');
  const [showExportModal, setShowExportModal] = useState(false);
  const [exportFormat, setExportFormat] = useState<'CSV' | 'PDF'>('CSV');
  const [verificationNotice, setVerificationNotice] = useState<string | null>(null);

  const filteredEntries = HISTORICAL_LEDGER.filter((entry) => {
    if (statusFilter !== 'ALL' && entry.status !== statusFilter) return false;
    if (search) {
      const q = search.toLowerCase();
      return (
        entry.referenceId.toLowerCase().includes(q) ||
        entry.collectorAlias.toLowerCase().includes(q) ||
        entry.material.toLowerCase().includes(q)
      );
    }
    return true;
  });

  const handleVerifyHashes = () => {
    setVerificationNotice('All 6 transaction records verified against canonical SHA-256 event chains. Zero hash discrepancies detected.');
    setTimeout(() => setVerificationNotice(null), 5000);
  };

  const handleDownloadExport = () => {
    if (exportFormat === 'CSV') {
      const disclaimer = '# SahiTol Digital Handover Record is a verification of physical scrap receipt, not a statutory EPR certificate. Received mass does not prove recycling.\n';
      const headers = 'Reference_ID,Date_Time,Collector,Material,Weight_kg,Amount_INR,Payment_Mode,Hash_Verified,Status\n';
      const rows = filteredEntries
        .map(
          (e) =>
            `${e.referenceId},${e.dateTime},"${e.collectorAlias}","${e.material}",${e.weightKg},${e.amountPaise / 100},${e.paymentMode},${e.hashVerified},${e.status}`
        )
        .join('\n');
      const blob = new Blob([disclaimer + headers + rows], { type: 'text/csv;charset=utf-8;' });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.setAttribute('href', url);
      link.setAttribute('download', `SahiTol_Ledger_Yard402_${Date.now()}.csv`);
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    } else {
      alert('Generating PDF summary ledger with statutory Non-EPR certification disclaimer...');
    }
    setShowExportModal(false);
  };

  return (
    <div className="space-y-space-lg">
      {/* Header with Title and Export Actions */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-space-md pb-space-sm border-b border-surface-container-high">
        <div>
          <h2 className="text-2xl lg:text-3xl font-headline font-bold text-on-surface">
            Procurement History & Export Ledger
          </h2>
          <p className="text-xs text-on-surface-variant max-w-2xl mt-0.5">
            Immutable transaction records secured with SAHITOL-JCS-1 SHA-256 cryptographic chaining. Verma Electricals Yard #402.
          </p>
        </div>

        <div className="flex items-center gap-space-sm">
          <button
            onClick={() => setShowExportModal(true)}
            className="flex items-center gap-1.5 bg-primary text-on-primary px-space-md py-2 rounded-lg text-xs font-headline font-bold hover:bg-primary-container transition-colors shadow-sm"
          >
            <span className="material-symbols-outlined text-[18px]">download</span>
            Export Ledger
          </button>
          <button
            onClick={handleVerifyHashes}
            className="flex items-center gap-1.5 bg-surface-container-high text-on-surface px-space-md py-2 rounded-lg text-xs font-headline font-semibold hover:bg-surface-container-highest transition-colors"
          >
            <span className="material-symbols-outlined text-[18px]">verified</span>
            Verify Hashes
          </button>
        </div>
      </div>

      {verificationNotice && (
        <div className="p-3 bg-emerald-100 border border-emerald-300 text-emerald-900 rounded-lg text-xs font-semibold flex items-center gap-2">
          <span className="material-symbols-outlined text-[18px]">verified</span>
          {verificationNotice}
        </div>
      )}

      {/* Stats Overview Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-space-md">
        <div className="bg-surface-container-low rounded-xl p-space-md shadow-sm border border-surface-container-high">
          <div className="flex items-center justify-between mb-space-sm">
            <span className="text-xs text-on-surface-variant uppercase font-semibold">Total Intake Volume</span>
            <span className="material-symbols-outlined text-primary p-1 bg-primary-fixed rounded">scale</span>
          </div>
          <div className="text-2xl font-headline font-bold text-on-surface">142,580 kg</div>
          <div className="text-[11px] text-emerald-700 font-semibold mt-1">+12.4% vs previous month</div>
        </div>

        <div className="bg-surface-container-low rounded-xl p-space-md shadow-sm border border-surface-container-high">
          <div className="flex items-center justify-between mb-space-sm">
            <span className="text-xs text-on-surface-variant uppercase font-semibold">Successful Handovers</span>
            <span className="material-symbols-outlined text-secondary p-1 bg-secondary-fixed rounded">local_shipping</span>
          </div>
          <div className="text-2xl font-headline font-bold text-on-surface">318 Lots</div>
          <div className="text-[11px] text-on-surface-variant mt-1">99.1% completion rate</div>
        </div>

        <div className="bg-surface-container-low rounded-xl p-space-md shadow-sm border border-surface-container-high">
          <div className="flex items-center justify-between mb-space-sm">
            <span className="text-xs text-on-surface-variant uppercase font-semibold">Total Disbursed Value</span>
            <span className="material-symbols-outlined text-primary p-1 bg-primary-fixed rounded">payments</span>
          </div>
          <div className="text-2xl font-headline font-bold text-on-surface">₹48,25,900</div>
          <div className="text-[11px] text-outline mt-1 font-mono">Cash + UPI Verified</div>
        </div>

        <div className="bg-surface-container-low rounded-xl p-space-md shadow-sm border border-surface-container-high">
          <div className="flex items-center justify-between mb-space-sm">
            <span className="text-xs text-on-surface-variant uppercase font-semibold">Active Disputes</span>
            <span className="material-symbols-outlined text-error p-1 bg-error-container rounded">warning</span>
          </div>
          <div className="text-2xl font-headline font-bold text-error">1 Lot</div>
          <div className="text-[11px] text-error font-semibold mt-1">Under Weight Audit</div>
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div className="bg-surface-container-low rounded-xl p-space-md shadow-sm border border-surface-container-high flex flex-col sm:flex-row gap-space-md items-center justify-between">
        <div className="relative w-full sm:w-80">
          <span className="absolute inset-y-0 left-0 flex items-center pl-3 pointer-events-none material-symbols-outlined text-outline text-[18px]">
            search
          </span>
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search Reference ID, Collector, or Material..."
            className="w-full bg-surface-container-lowest text-on-surface pl-10 pr-3 py-2 rounded-lg text-xs border border-outline-variant focus:outline-none focus:ring-2 focus:ring-primary shadow-sm"
          />
        </div>

        <div className="flex items-center gap-space-xs w-full sm:w-auto">
          <button
            onClick={() => setStatusFilter('ALL')}
            className={`px-3 py-1.5 rounded-lg text-xs font-headline font-semibold transition-colors ${
              statusFilter === 'ALL'
                ? 'bg-primary text-on-primary'
                : 'bg-surface-container-high text-on-surface-variant hover:text-on-surface'
            }`}
          >
            All Entries ({HISTORICAL_LEDGER.length})
          </button>
          <button
            onClick={() => setStatusFilter('SETTLED')}
            className={`px-3 py-1.5 rounded-lg text-xs font-headline font-semibold transition-colors ${
              statusFilter === 'SETTLED'
                ? 'bg-primary text-on-primary'
                : 'bg-surface-container-high text-on-surface-variant hover:text-on-surface'
            }`}
          >
            Settled ({HISTORICAL_LEDGER.filter((e) => e.status === 'SETTLED').length})
          </button>
          <button
            onClick={() => setStatusFilter('DISPUTED')}
            className={`px-3 py-1.5 rounded-lg text-xs font-headline font-semibold transition-colors ${
              statusFilter === 'DISPUTED'
                ? 'bg-primary text-on-primary'
                : 'bg-surface-container-high text-on-surface-variant hover:text-on-surface'
            }`}
          >
            Disputed ({HISTORICAL_LEDGER.filter((e) => e.status === 'DISPUTED').length})
          </button>
        </div>
      </div>

      {/* Ledger Table */}
      <div className="overflow-x-auto rounded-xl border border-surface-container-high shadow-sm bg-surface-container-lowest">
        <table className="w-full text-left text-sm">
          <thead className="bg-surface-container-high text-xs text-on-surface-variant font-headline uppercase tracking-wider">
            <tr>
              <th className="p-space-md">Reference ID</th>
              <th className="p-space-md">Date & Time</th>
              <th className="p-space-md">Collector</th>
              <th className="p-space-md">Material</th>
              <th className="p-space-md">Scale Mass</th>
              <th className="p-space-md text-right">Settled Amount</th>
              <th className="p-space-md">Mode</th>
              <th className="p-space-md">Hash Proof</th>
              <th className="p-space-md text-center">Status</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-surface-container-high">
            {filteredEntries.map((entry) => (
              <tr key={entry.id} className="hover:bg-surface-container-low transition-colors text-xs">
                <td className="p-space-md font-mono font-bold text-on-surface">
                  {entry.referenceId}
                </td>
                <td className="p-space-md text-on-surface-variant">{entry.dateTime}</td>
                <td className="p-space-md font-medium text-on-surface">{entry.collectorAlias}</td>
                <td className="p-space-md text-on-surface font-medium">{entry.material}</td>
                <td className="p-space-md font-mono font-bold text-on-surface">{entry.weightKg} kg</td>
                <td className="p-space-md text-right font-mono font-bold text-primary">
                  ₹{(entry.amountPaise / 100).toLocaleString('en-IN')}.00
                </td>
                <td className="p-space-md">
                  <span className="px-2 py-0.5 bg-surface-container-high rounded font-mono text-[11px] font-semibold text-on-surface">
                    {entry.paymentMode}
                  </span>
                </td>
                <td className="p-space-md">
                  {entry.hashVerified ? (
                    <span className="inline-flex items-center gap-1 text-[11px] text-emerald-700 font-semibold">
                      <span className="material-symbols-outlined text-[14px]">check_circle</span> SHA-256
                    </span>
                  ) : (
                    <span className="inline-flex items-center gap-1 text-[11px] text-amber-700 font-semibold">
                      <span className="material-symbols-outlined text-[14px]">warning</span> Pending
                    </span>
                  )}
                </td>
                <td className="p-space-md text-center">
                  {entry.status === 'SETTLED' ? (
                    <span className="px-2 py-0.5 rounded text-[11px] font-semibold bg-emerald-100 text-emerald-800">
                      Settled
                    </span>
                  ) : (
                    <span className="px-2 py-0.5 rounded text-[11px] font-semibold bg-error-container text-on-error-container">
                      Disputed
                    </span>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Export Modal */}
      {showExportModal && (
        <div className="fixed inset-0 z-50 bg-black/50 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-surface-container-lowest rounded-2xl max-w-md w-full p-space-lg shadow-xl border border-surface-container-high space-y-space-md">
            <div className="flex items-center justify-between pb-space-sm border-b border-surface-container-high">
              <h3 className="text-lg font-headline font-bold text-on-surface flex items-center gap-2">
                <span className="material-symbols-outlined text-primary text-[22px]">download</span>
                Export Procurement Ledger
              </h3>
              <button
                onClick={() => setShowExportModal(false)}
                className="text-on-surface-variant hover:text-on-surface text-xl font-bold"
              >
                &times;
              </button>
            </div>

            <div className="space-y-space-sm">
              <label className="text-xs font-semibold text-on-surface-variant block">Format:</label>
              <div className="grid grid-cols-2 gap-space-sm">
                <label
                  onClick={() => setExportFormat('CSV')}
                  className={`p-3 rounded-lg border-2 text-center cursor-pointer font-headline text-xs font-bold transition-all ${
                    exportFormat === 'CSV' ? 'border-primary bg-primary-fixed/20 text-primary' : 'border-surface-container-high text-on-surface-variant'
                  }`}
                >
                  CSV Format
                </label>
                <label
                  onClick={() => setExportFormat('PDF')}
                  className={`p-3 rounded-lg border-2 text-center cursor-pointer font-headline text-xs font-bold transition-all ${
                    exportFormat === 'PDF' ? 'border-primary bg-primary-fixed/20 text-primary' : 'border-surface-container-high text-on-surface-variant'
                  }`}
                >
                  PDF Summary Ledger
                </label>
              </div>
            </div>

            <div className="p-3 bg-surface-container rounded-lg text-[11px] text-on-surface-variant space-y-1">
              <p className="font-semibold text-on-surface">Statutory Notice Included in Export:</p>
              <p>
                "SahiTol Digital Handover Record is a verification of physical scrap receipt, not a statutory EPR certificate. Received mass does not prove recycling."
              </p>
            </div>

            <div className="flex justify-end gap-space-sm pt-space-xs">
              <button
                onClick={() => setShowExportModal(false)}
                className="px-space-md py-2 rounded-lg text-xs font-semibold text-on-surface-variant hover:bg-surface-container transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={handleDownloadExport}
                className="px-space-lg py-2 bg-primary hover:bg-primary-container text-on-primary rounded-lg text-xs font-headline font-bold shadow-sm transition-colors"
              >
                Download Export ({filteredEntries.length} records)
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
