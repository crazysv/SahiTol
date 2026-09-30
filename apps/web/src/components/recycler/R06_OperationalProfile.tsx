import React, { useState } from 'react';

interface MaterialRateItem {
  id: string;
  name: string;
  category: string;
  currentRate: number;
  marketTrend: 'UP' | 'DOWN' | 'STABLE';
  isAccepted: boolean;
}

const DEFAULT_RATES: MaterialRateItem[] = [
  { id: 'mat-001', name: 'Super Grade Copper Wire', category: 'CABLES_WIRES', currentRate: 650, marketTrend: 'UP', isAccepted: true },
  { id: 'mat-002', name: 'Insulated Copper Cable (Armoured)', category: 'CABLES_WIRES', currentRate: 180, marketTrend: 'STABLE', isAccepted: true },
  { id: 'mat-003', name: 'Brass Radiator Cuttings', category: 'NON_FERROUS_METALS', currentRate: 310, marketTrend: 'UP', isAccepted: true },
  { id: 'mat-004', name: 'Printed Circuit Boards (Grade A High Yield)', category: 'CIRCUIT_BOARDS', currentRate: 450, marketTrend: 'STABLE', isAccepted: true },
  { id: 'mat-005', name: 'Aluminium Extrusion Scrap', category: 'NON_FERROUS_METALS', currentRate: 145, marketTrend: 'DOWN', isAccepted: true },
  { id: 'mat-006', name: 'Mixed Electronics Shredding Grade', category: 'MIXED_ELECTRONICS', currentRate: 35, marketTrend: 'STABLE', isAccepted: false },
];

export default function R06_OperationalProfile() {
  const [rates, setRates] = useState<MaterialRateItem[]>(DEFAULT_RATES);
  const [pickupAvailable, setPickupAvailable] = useState(true);
  const [pickupRadiusKm, setPickupRadiusKm] = useState(25);
  const [gateDropOff, setGateDropOff] = useState(true);
  const [isSaved, setIsSaved] = useState(false);

  const handleRateChange = (id: string, newRate: number) => {
    setRates((prev) =>
      prev.map((r) => (r.id === id ? { ...r, currentRate: newRate } : r))
    );
  };

  const handleToggleAccept = (id: string) => {
    setRates((prev) =>
      prev.map((r) => (r.id === id ? { ...r, isAccepted: !r.isAccepted } : r))
    );
  };

  const handleSaveProfile = () => {
    setIsSaved(true);
    setTimeout(() => setIsSaved(false), 3000);
  };

  return (
    <div className="space-y-space-lg">
      {/* Profile Header Card */}
      <div className="bg-surface-container-low rounded-xl p-space-lg shadow-sm border border-surface-container-high flex flex-col md:flex-row md:items-center justify-between gap-space-md">
        <div>
          <div className="flex items-center gap-space-xs text-xs text-on-surface-variant font-mono mb-1">
            <span>FACILITY ID: VER-DEL-9042</span>
            <span>•</span>
            <span className="text-primary font-bold">L3 COMPLIANCE VERIFIED</span>
          </div>
          <h2 className="text-2xl lg:text-3xl font-headline font-bold text-on-surface">
            Verma Electricals & Metal Recycling
          </h2>
          <p className="text-sm text-on-surface-variant mt-0.5">
            Delhi Central Scrap Hub • Yard #402, Okhla Industrial Area Phase III
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-space-md bg-surface-container-high p-space-md rounded-xl">
          <div className="flex flex-col">
            <span className="text-xs text-on-surface-variant uppercase font-semibold">Consent Status</span>
            <span className="text-xs font-headline text-emerald-700 font-bold flex items-center gap-1 mt-0.5">
              <span className="material-symbols-outlined text-[16px]">verified</span> DPCC Valid thru 2028
            </span>
          </div>
          <div className="h-8 w-[1px] bg-surface-variant hidden md:block" />
          <button
            onClick={() => alert('Audit state refreshed from DPCC registry.')}
            className="px-space-md py-1.5 bg-primary text-on-primary text-xs font-headline font-bold rounded-lg shadow-sm hover:bg-primary-container transition-colors flex items-center gap-1"
          >
            <span className="material-symbols-outlined text-[16px]">sync</span> Refresh State
          </button>
        </div>
      </div>

      {isSaved && (
        <div className="p-3 bg-emerald-100 border border-emerald-300 text-emerald-800 rounded-lg text-xs font-semibold flex items-center gap-2">
          <span className="material-symbols-outlined text-[18px]">check_circle</span>
          Operational profile and price board updated successfully!
        </div>
      )}

      {/* Main Grid: Operating Scope & Material Pricing */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-space-lg">
        {/* Left Column: Scope & Logistics Config (1 col) */}
        <div className="space-y-space-md lg:col-span-1">
          {/* Operating Scope Card */}
          <div className="bg-surface-container-low rounded-xl p-space-lg shadow-sm border border-surface-container-high space-y-space-md">
            <h3 className="text-base font-headline font-bold text-on-surface flex items-center gap-2">
              <span className="material-symbols-outlined text-primary text-[20px]">hub</span>
              Operating Scope
            </h3>
            <p className="text-xs text-on-surface-variant">
              Active processing parameters registered under SahiTol Recycler Network.
            </p>

            <div className="space-y-2 text-xs divide-y divide-surface-container-high">
              <div className="flex justify-between items-center py-1.5">
                <span className="text-on-surface-variant">Primary Hub:</span>
                <span className="font-semibold text-on-surface">Delhi Central (Zone 4)</span>
              </div>
              <div className="flex justify-between items-center py-1.5">
                <span className="text-on-surface-variant">Daily Processing Capacity:</span>
                <span className="font-semibold text-on-surface">12.5 Metric Tons</span>
              </div>
              <div className="flex justify-between items-center py-1.5">
                <span className="text-on-surface-variant">Weighbridge Tolerance:</span>
                <span className="font-mono font-bold text-on-surface">± 0.05%</span>
              </div>
              <div className="flex justify-between items-center py-1.5">
                <span className="text-on-surface-variant">Pollution Cert:</span>
                <span className="font-mono font-bold text-primary">DPCC-OKH-8821</span>
              </div>
            </div>
          </div>

          {/* Logistics Configuration Card */}
          <div className="bg-surface-container-low rounded-xl p-space-lg shadow-sm border border-surface-container-high space-y-space-md">
            <h3 className="text-base font-headline font-bold text-on-surface flex items-center gap-2">
              <span className="material-symbols-outlined text-primary text-[20px]">local_shipping</span>
              Service Area Configuration
            </h3>

            <div className="space-y-space-md">
              <label className="flex items-center justify-between p-space-md bg-surface-container rounded-lg cursor-pointer hover:bg-surface-container-high transition-colors">
                <div className="flex items-center gap-space-md">
                  <span className="material-symbols-outlined text-primary text-[20px]">local_shipping</span>
                  <div>
                    <span className="text-xs font-headline font-bold text-on-surface block">
                      Pickup Available
                    </span>
                    <span className="text-[11px] text-on-surface-variant">
                      Radius: {pickupRadiusKm} km from Okhla
                    </span>
                  </div>
                </div>
                <input
                  type="checkbox"
                  checked={pickupAvailable}
                  onChange={(e) => setPickupAvailable(e.target.checked)}
                  className="w-4 h-4 accent-primary rounded cursor-pointer"
                />
              </label>

              {pickupAvailable && (
                <div className="space-y-1 px-1">
                  <div className="flex justify-between text-xs text-on-surface-variant">
                    <span>Operating Radius:</span>
                    <span className="font-bold text-on-surface">{pickupRadiusKm} km</span>
                  </div>
                  <input
                    type="range"
                    min="5"
                    max="60"
                    step="5"
                    value={pickupRadiusKm}
                    onChange={(e) => setPickupRadiusKm(parseInt(e.target.value))}
                    className="w-full accent-primary"
                  />
                </div>
              )}

              <label className="flex items-center justify-between p-space-md bg-surface-container rounded-lg cursor-pointer hover:bg-surface-container-high transition-colors">
                <div className="flex items-center gap-space-md">
                  <span className="material-symbols-outlined text-primary text-[20px]">domain</span>
                  <div>
                    <span className="text-xs font-headline font-bold text-on-surface block">
                      Drop-off Facility Gate
                    </span>
                    <span className="text-[11px] text-on-surface-variant">
                      Gate #2 (Commercial Vehicles)
                    </span>
                  </div>
                </div>
                <input
                  type="checkbox"
                  checked={gateDropOff}
                  onChange={(e) => setGateDropOff(e.target.checked)}
                  className="w-4 h-4 accent-primary rounded cursor-pointer"
                />
              </label>
            </div>
          </div>
        </div>

        {/* Right Column: Active Commercial Price Board (2 cols) */}
        <div className="lg:col-span-2 space-y-space-md">
          <div className="bg-surface-container-low rounded-xl p-space-lg shadow-sm border border-surface-container-high">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-space-sm mb-space-md">
              <div>
                <h3 className="text-lg font-headline font-bold text-on-surface flex items-center gap-2">
                  <span className="material-symbols-outlined text-primary text-[22px]">price_change</span>
                  Yard Commercial Price Board
                </h3>
                <p className="text-xs text-on-surface-variant mt-0.5">
                  Set baseline offering rates visible to matching collectors in your region.
                </p>
              </div>

              <button
                onClick={handleSaveProfile}
                className="px-space-lg py-2 bg-primary hover:bg-primary-container text-on-primary text-xs font-headline font-bold rounded-lg shadow-sm transition-colors"
              >
                Save Price Updates
              </button>
            </div>

            <div className="overflow-x-auto rounded-lg border border-surface-container-high">
              <table className="w-full text-left text-sm">
                <thead className="bg-surface-container-high text-xs text-on-surface-variant font-headline uppercase">
                  <tr>
                    <th className="p-space-md">Status</th>
                    <th className="p-space-md">Material Name</th>
                    <th className="p-space-md">Category</th>
                    <th className="p-space-md">Trend</th>
                    <th className="p-space-md text-right">Active Rate (₹/kg)</th>
                  </tr>
                </thead>
                <tbody className="bg-surface-container-lowest divide-y divide-surface-container-high">
                  {rates.map((item) => (
                    <tr key={item.id} className="hover:bg-surface-container-low transition-colors">
                      <td className="p-space-md">
                        <input
                          type="checkbox"
                          checked={item.isAccepted}
                          onChange={() => handleToggleAccept(item.id)}
                          className="w-4 h-4 accent-primary rounded cursor-pointer"
                          title="Toggle accepting this material"
                        />
                      </td>
                      <td className="p-space-md font-medium text-on-surface">
                        {item.name}
                      </td>
                      <td className="p-space-md text-xs text-on-surface-variant font-mono">
                        {item.category}
                      </td>
                      <td className="p-space-md">
                        {item.marketTrend === 'UP' && (
                          <span className="inline-flex items-center text-xs font-semibold text-emerald-700">
                            ↑ +₹15/kg
                          </span>
                        )}
                        {item.marketTrend === 'DOWN' && (
                          <span className="inline-flex items-center text-xs font-semibold text-amber-700">
                            ↓ -₹5/kg
                          </span>
                        )}
                        {item.marketTrend === 'STABLE' && (
                          <span className="inline-flex items-center text-xs text-on-surface-variant">
                            — Stable
                          </span>
                        )}
                      </td>
                      <td className="p-space-md text-right">
                        <div className="flex items-center justify-end gap-1">
                          <span className="text-xs text-on-surface-variant">₹</span>
                          <input
                            type="number"
                            value={item.currentRate}
                            disabled={!item.isAccepted}
                            onChange={(e) => handleRateChange(item.id, parseFloat(e.target.value) || 0)}
                            className="w-20 p-1.5 text-right font-mono font-bold text-sm bg-surface-container-lowest border border-outline-variant rounded disabled:opacity-40"
                          />
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            <div className="mt-space-md p-space-sm bg-surface-container-low rounded-lg text-xs text-on-surface-variant flex items-center gap-2">
              <span className="material-symbols-outlined text-[16px] text-primary">info</span>
              <span>
                Rates update atomically with timestamped audit entries. Collector offers remain frozen to quote time.
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
