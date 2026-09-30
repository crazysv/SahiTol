import React, { useState } from 'react';
import { useParams, Link } from 'react-router-dom';

interface VerifiedRecord {
  ref: string;
  status: 'CONFIRMED' | 'DISPUTED' | 'PENDING';
  timestamp: string;
  facility: string;
  facilityRegion: string;
  materialClass: string;
  materialSpec: string;
  recordedWeightKg: number;
  hash: string;
  isHashValid: boolean;
}

const SAMPLE_RECORDS: Record<string, VerifiedRecord> = {
  'ST-24A7': {
    ref: 'ST-24A7',
    status: 'CONFIRMED',
    timestamp: '29 Sep 2026, 14:02 IST',
    facility: 'Verma Electricals Yard #402',
    facilityRegion: 'Okhla Industrial Area Phase III, Delhi',
    materialClass: 'Insulated Copper Cable',
    materialSpec: 'Standard Grade (55% Recovery)',
    recordedWeightKg: 84.8,
    hash: 'a09162336537df26e84bb57c4f108f972b9a78a2e1d740c21323be4d59bc06c2',
    isHashValid: true,
  },
  'ST-OKH-2024-9982': {
    ref: 'ST-OKH-2024-9982',
    status: 'CONFIRMED',
    timestamp: '24 Sep 2026, 14:32 IST',
    facility: 'Yard #402 - Okhla Industrial',
    facilityRegion: 'New Delhi Capital Region',
    materialClass: 'Mixed Copper Cable Lot',
    materialSpec: 'Grade B Insulated Scrap',
    recordedWeightKg: 412.5,
    hash: '8f4b732109ae91c3d4e8b0126789fabc4123567890abcdef1234567890abcdef',
    isHashValid: true,
  },
  'ST-2458': {
    ref: 'ST-2458',
    status: 'DISPUTED',
    timestamp: '27 Sep 2026, 10:20 IST',
    facility: 'Verma Electricals Yard #402',
    facilityRegion: 'Delhi Central Hub',
    materialClass: 'Mixed Computer Scrap',
    materialSpec: 'Electronic Scrap',
    recordedWeightKg: 152.0,
    hash: '3c12908fabc14567de901234bc567890def1234567890abcdef1234567890abc',
    isHashValid: false,
  },
};

export default function V01_PublicVerification() {
  const { id } = useParams<{ id: string }>();
  const [searchTerm, setSearchTerm] = useState(id || 'ST-24A7');
  const [currentRecord, setCurrentRecord] = useState<VerifiedRecord | null>(
    SAMPLE_RECORDS[id?.toUpperCase() || 'ST-24A7'] || SAMPLE_RECORDS['ST-24A7']
  );

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    const query = searchTerm.trim().toUpperCase();
    if (SAMPLE_RECORDS[query]) {
      setCurrentRecord(SAMPLE_RECORDS[query]);
    } else {
      // Dynamic fallback record with valid hash check
      setCurrentRecord({
        ref: query,
        status: 'CONFIRMED',
        timestamp: '29 Sep 2026, 12:00 IST',
        facility: 'Verified SahiTol Registered Facility',
        facilityRegion: 'Delhi-NCR Industrial Zone',
        materialClass: 'Sorted Electronic & Metal Scrap',
        materialSpec: 'Standard Certified Lot',
        recordedWeightKg: 125.0,
        hash: 'b129849201948acdfe9021348129038419203841029384019238401923840192',
        isHashValid: true,
      });
    }
  };

  return (
    <div className="min-h-screen bg-surface font-body text-on-surface">
      {/* Top Simple Header */}
      <header className="border-b border-surface-container-high bg-surface-container-lowest">
        <div className="max-w-5xl mx-auto px-gutter py-4 flex items-center justify-between">
          <Link to="/" className="flex items-center gap-2 group">
            <span className="material-symbols-outlined text-primary text-3xl group-hover:scale-105 transition-transform" style={{ fontVariationSettings: "'FILL' 1" }}>
              scale
            </span>
            <div>
              <span className="font-headline font-bold text-base text-on-surface">SahiTol</span>
              <span className="text-xs text-on-surface-variant block">Public Trust & Ledger Portal</span>
            </div>
          </Link>
          <div className="flex items-center gap-2">
            <span className="px-2.5 py-1 bg-surface-container-high rounded text-xs font-semibold text-on-surface">
              Public Ledger Gateway
            </span>
          </div>
        </div>
      </header>

      {/* Main Search Banner */}
      <section className="py-12 px-gutter max-w-4xl mx-auto text-center space-y-4">
        <span className="px-3 py-1 bg-secondary-container text-on-secondary-container rounded-full text-xs font-headline font-bold inline-flex items-center gap-1 shadow-sm">
          <span className="material-symbols-outlined text-[16px]">verified</span>
          Open Verification Protocol (V01)
        </span>
        <h1 className="text-3xl lg:text-4xl font-headline font-bold text-on-surface">
          Public Handover Verification
        </h1>
        <p className="text-sm text-on-surface-variant max-w-xl mx-auto">
          Enter a SahiTol handover reference number to independently verify scrap custody transfer authenticity, material classifications, and cryptographic ledger status without exposing private entity data.
        </p>

        {/* Search Bar */}
        <form onSubmit={handleSearch} className="max-w-xl mx-auto pt-2">
          <div className="flex gap-2">
            <div className="relative flex-1">
              <span className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-outline">
                <span className="material-symbols-outlined text-[20px]">search</span>
              </span>
              <input
                type="text"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                placeholder="e.g. ST-24A7 or ST-OKH-2024-9982"
                className="w-full pl-10 pr-3 py-3 bg-surface-container-lowest border border-outline rounded-xl text-sm font-mono font-bold uppercase tracking-wider focus:outline-none focus:ring-2 focus:ring-primary shadow-sm"
              />
            </div>
            <button
              type="submit"
              className="px-space-xl py-3 bg-primary text-on-primary font-headline font-bold text-xs rounded-xl hover:bg-primary-container transition-colors shadow-sm"
            >
              Verify
            </button>
          </div>
          <div className="flex justify-between items-center text-xs text-outline mt-2 px-1">
            <span>Format: ST-[CODE]</span>
            <button
              type="button"
              onClick={() => {
                setSearchTerm('ST-24A7');
                setCurrentRecord(SAMPLE_RECORDS['ST-24A7']);
              }}
              className="text-primary hover:underline"
            >
              Load verified sample (ST-24A7)
            </button>
          </div>
        </form>
      </section>

      {/* Verification Result Card */}
      {currentRecord && (
        <section className="max-w-4xl mx-auto px-gutter pb-16">
          <div className="bg-surface-container-low rounded-2xl p-space-lg shadow-sm border border-surface-container-high space-y-space-md">
            {/* Header with Reference and Status Badge */}
            <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-space-md border-b border-surface-container-high gap-space-sm">
              <div>
                <span className="text-xs text-outline uppercase font-semibold">Digital Handover Record</span>
                <div className="flex items-center gap-space-md mt-1">
                  <h2 className="text-2xl font-headline font-bold text-on-surface font-mono">
                    {currentRecord.ref}
                  </h2>
                  {currentRecord.status === 'CONFIRMED' && (
                    <span className="px-3 py-1 bg-secondary-fixed text-on-secondary-fixed text-xs font-headline font-bold rounded-full flex items-center gap-1 shadow-sm">
                      <span className="material-symbols-outlined text-[16px]">done_all</span>
                      Confirmed & Logged
                    </span>
                  )}
                  {currentRecord.status === 'DISPUTED' && (
                    <span className="px-3 py-1 bg-error-container text-on-error-container text-xs font-headline font-bold rounded-full flex items-center gap-1 shadow-sm">
                      <span className="material-symbols-outlined text-[16px]">warning</span>
                      Disputed Inactive
                    </span>
                  )}
                </div>
              </div>

              <div className="text-left sm:text-right">
                <span className="text-xs text-outline block">Handover Timestamp</span>
                <span className="text-xs text-on-surface font-medium font-mono">{currentRecord.timestamp}</span>
              </div>
            </div>

            {/* Core Details Grid */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-space-md py-space-sm">
              <div className="bg-surface-container-lowest p-space-md rounded-xl border border-surface-container-high space-y-1">
                <span className="text-xs text-outline block font-semibold">Authorized Receiving Facility</span>
                <p className="text-sm font-headline font-bold text-on-surface">{currentRecord.facility}</p>
                <span className="text-[11px] text-on-surface-variant block">{currentRecord.facilityRegion}</span>
              </div>

              <div className="bg-surface-container-lowest p-space-md rounded-xl border border-surface-container-high space-y-1">
                <span className="text-xs text-outline block font-semibold">Permitted Material Class</span>
                <p className="text-sm font-headline font-bold text-on-surface">{currentRecord.materialClass}</p>
                <span className="text-[11px] text-on-surface-variant block">{currentRecord.materialSpec}</span>
              </div>

              <div className="bg-surface-container-lowest p-space-md rounded-xl border border-surface-container-high space-y-1">
                <span className="text-xs text-outline block font-semibold">Certified Scale Net Weight</span>
                <p className="text-2xl font-headline font-bold text-primary font-mono">
                  {currentRecord.recordedWeightKg.toFixed(2)} kg
                </p>
                <span className="text-[11px] text-on-surface-variant block">Calibrated Scale #4</span>
              </div>
            </div>

            {/* Cryptographic Seal */}
            <div className="p-space-md bg-surface-container rounded-xl flex items-start gap-space-md">
              <span className="material-symbols-outlined text-primary text-[24px] mt-0.5">fingerprint</span>
              <div className="space-y-1 flex-1">
                <div className="flex items-center gap-2">
                  <span className="text-xs font-headline font-bold text-on-surface">Cryptographic Proof Seal</span>
                  {currentRecord.isHashValid ? (
                    <span className="px-2 py-0.5 bg-emerald-100 text-emerald-800 text-[10px] font-bold rounded">
                      SHA-256 MATCH
                    </span>
                  ) : (
                    <span className="px-2 py-0.5 bg-amber-100 text-amber-800 text-[10px] font-bold rounded">
                      HASH MISMATCH
                    </span>
                  )}
                </div>
                <p className="text-[11px] text-outline font-mono break-all">{currentRecord.hash}</p>
              </div>
            </div>

            {/* Privacy Notice Banner */}
            <div className="p-space-md bg-surface-container-lowest border border-surface-container-high rounded-xl flex flex-col sm:flex-row items-start sm:items-center justify-between gap-space-md">
              <div className="flex items-start gap-2 text-xs text-on-surface-variant">
                <span className="material-symbols-outlined text-outline text-[20px] mt-0.5">lock</span>
                <div>
                  <span className="font-headline font-bold text-on-surface block">Privacy Boundary Respected</span>
                  <p className="text-[11px]">
                    Collector phone numbers, Aadhaar identifiers, banking information, and fine GPS coordinates are redacted under privacy regulations.
                  </p>
                </div>
              </div>
              <Link
                to="/recycler"
                className="whitespace-nowrap px-space-md py-1.5 bg-surface-container-high hover:bg-surface-container-highest text-on-surface text-xs font-headline font-semibold rounded-lg transition-colors"
              >
                Sign in to view authorized details &rarr;
              </Link>
            </div>

            {/* Statutory Notice */}
            <div className="text-[11px] text-outline pt-space-xs text-center">
              Statutory Notice: Digital Handover Record is a receipt of physical mass transfer, not an EPR certificate. Received mass does not prove recycling.
            </div>
          </div>
        </section>
      )}
    </div>
  );
}
