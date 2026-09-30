import React from 'react';
import { BrowserRouter, Routes, Route, Link } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import RecyclerLayout from './components/recycler/RecyclerLayout';
import R01_Inbox from './components/recycler/R01_Inbox';
import R02_IncomingLot from './components/recycler/R02_IncomingLot';
import R03_QuoteTerminal from './components/recycler/R03_QuoteTerminal';
import R04_QRScan from './components/recycler/R04_QRScan';
import R05_ReceiptReview from './components/recycler/R05_ReceiptReview';
import R06_OperationalProfile from './components/recycler/R06_OperationalProfile';
import R07_HistoryExports from './components/recycler/R07_HistoryExports';
import V01_PublicVerification from './components/verification/V01_PublicVerification';
import AdminLayout from './components/admin/AdminLayout';
import A01_Overview from './components/admin/A01_Overview';
import A02_Collectors from './components/admin/A02_Collectors';
import A03_Facilities from './components/admin/A03_Facilities';
import A04_CatalogPrices from './components/admin/A04_CatalogPrices';
import A05_Traceability from './components/admin/A05_Traceability';
import A06_QualityReview from './components/admin/A06_QualityReview';
import A07_EvidenceLinks from './components/admin/A07_EvidenceLinks';
import U01_UnitEconomics from './components/economics/U01_UnitEconomics';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});

function HomeView() {
  return (
    <div className="max-w-4xl mx-auto p-6 space-y-6">
      <header className="border-b border-surface-container-high pb-4">
        <div className="flex items-center gap-3">
          <span className="material-symbols-outlined text-primary text-4xl" style={{ fontVariationSettings: "'FILL' 1" }}>
            scale
          </span>
          <div>
            <h1 className="text-3xl font-headline font-bold text-on-surface">SahiTol Console</h1>
            <p className="text-sm text-on-surface-variant mt-0.5">
              Recycler operations, administration, and public verification for formal scrap chains.
            </p>
          </div>
        </div>
        <div className="inline-flex items-center gap-1.5 mt-3 px-2.5 py-1 text-xs font-semibold bg-emerald-100 text-emerald-800 rounded-full">
          <span className="w-2 h-2 rounded-full bg-emerald-600"></span>
          Stitch Design System Active: Project 245073995801566548 (37 screens registered)
        </div>
      </header>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="p-5 border border-surface-container-high rounded-xl bg-surface-container-lowest shadow-sm hover:shadow transition">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-headline font-semibold text-on-surface">Recycler Console</h2>
            <span className="px-2 py-0.5 text-[11px] bg-primary-fixed text-on-primary-fixed rounded font-bold">R01–R07</span>
          </div>
          <p className="text-xs text-on-surface-variant mt-1.5">
            Incoming lot inspection, live scale capture, quotes (rate vs fixed), QR scan, receipt confirmation, and procurement ledger.
          </p>
          <div className="flex flex-wrap gap-2 mt-4">
            <Link
              to="/recycler"
              className="px-3 py-1.5 text-xs font-headline font-bold bg-primary text-on-primary rounded-lg hover:bg-primary-container transition-colors shadow-sm"
            >
              Open Console &rarr;
            </Link>
            <Link
              to="/recycler/scan"
              className="px-3 py-1.5 text-xs font-headline font-bold bg-secondary text-on-secondary rounded-lg hover:bg-secondary/90 transition-colors shadow-sm"
            >
              QR Scanner (R04)
            </Link>
          </div>
        </div>

        <div className="p-5 border border-surface-container-high rounded-xl bg-surface-container-lowest shadow-sm hover:shadow transition">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-headline font-semibold text-on-surface">Admin Quality Dashboard</h2>
            <span className="px-2 py-0.5 text-[11px] bg-surface-container-high text-on-surface-variant rounded font-bold">A01–A07</span>
          </div>
          <p className="text-xs text-on-surface-variant mt-1.5">
            Data quality review flags, facility directory validation, price moderation, and platform metrics.
          </p>
          <Link
            to="/admin"
            className="inline-block mt-4 px-3 py-1.5 text-xs font-headline font-bold bg-surface-container-high text-on-surface rounded-lg hover:bg-surface-container-highest transition-colors"
          >
            Open Admin Dashboard &rarr;
          </Link>
        </div>

        <div className="p-5 border border-surface-container-high rounded-xl bg-surface-container-lowest shadow-sm hover:shadow transition">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-headline font-semibold text-on-surface">Public Verification</h2>
            <span className="px-2 py-0.5 text-[11px] bg-secondary-container text-on-secondary-container rounded font-bold">V01</span>
          </div>
          <p className="text-xs text-on-surface-variant mt-1.5">
            Inspect digital handover proposal status and SHA-256 cryptographic hash integrity independently.
          </p>
          <Link
            to="/verify/ST-24A7"
            className="inline-block mt-4 px-3 py-1.5 text-xs font-headline font-bold bg-secondary-container text-on-secondary-container rounded-lg hover:opacity-90 transition-colors shadow-sm"
          >
            Verify Handover Record &rarr;
          </Link>
        </div>

        <div className="p-5 border border-surface-container-high rounded-xl bg-surface-container-lowest shadow-sm hover:shadow transition">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-headline font-semibold text-on-surface">Illustrative Economics</h2>
            <span className="px-2 py-0.5 text-[11px] bg-surface-container-high text-on-surface-variant rounded font-bold">U01</span>
          </div>
          <p className="text-xs text-on-surface-variant mt-1.5">
            Interactive lot-level comparison under transparent illustrative assumptions (0 paise collector fee).
          </p>
          <Link
            to="/economics"
            className="inline-block mt-4 px-3 py-1.5 text-xs font-headline font-bold bg-surface-container-high text-on-surface rounded-lg hover:bg-surface-container-highest transition-colors"
          >
            View Economics Model &rarr;
          </Link>
        </div>
      </div>
    </div>
  );
}

function PlaceholderScreen({ title, screenId }: { title: string; screenId: string }) {
  return (
    <div className="max-w-2xl mx-auto p-6 space-y-4">
      <Link to="/" className="text-sm text-primary hover:underline">&larr; Back to Home</Link>
      <h1 className="text-2xl font-headline font-bold text-on-surface">{title} ({screenId})</h1>
      <div className="p-4 bg-surface-container-low border border-surface-container-high rounded-xl text-sm text-on-surface-variant">
        <p className="font-semibold text-on-surface">Registered Stitch Design</p>
        <p className="mt-1">
          Screen {screenId} is registered in the Stitch design system. The underlying API endpoints
          are connected.
        </p>
      </div>
    </div>
  );
}

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<HomeView />} />
          
          {/* Recycler Console (T022 & T025 - R01 to R07) */}
          <Route path="/recycler" element={<RecyclerLayout />}>
            <Route index element={<R01_Inbox />} />
            <Route path="incoming" element={<R02_IncomingLot />} />
            <Route path="quote" element={<R03_QuoteTerminal />} />
            <Route path="scan" element={<R04_QRScan />} />
            <Route path="receipt" element={<R05_ReceiptReview />} />
            <Route path="profile" element={<R06_OperationalProfile />} />
            <Route path="history" element={<R07_HistoryExports />} />
          </Route>

          {/* Public Verification (T025 - V01) */}
          <Route path="/verify/:id?" element={<V01_PublicVerification />} />

          {/* Admin Quality Dashboard (T030 - A01 to A07) */}
          <Route path="/admin" element={<AdminLayout />}>
            <Route index element={<A01_Overview />} />
            <Route path="overview" element={<A01_Overview />} />
            <Route path="collectors" element={<A02_Collectors />} />
            <Route path="facilities" element={<A03_Facilities />} />
            <Route path="catalog" element={<A04_CatalogPrices />} />
            <Route path="traceability" element={<A05_Traceability />} />
            <Route path="quality" element={<A06_QualityReview />} />
            <Route path="evidence" element={<A07_EvidenceLinks />} />
          </Route>
          <Route path="/economics" element={<U01_UnitEconomics />} />
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  );
}
