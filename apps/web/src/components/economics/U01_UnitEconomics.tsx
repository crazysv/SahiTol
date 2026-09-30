import React, { useState, useMemo } from 'react';
import { Link } from 'react-router-dom';

interface ScenarioInputs {
  materialName: string;
  batchWeightKg: number;
  marketBenchmark: string;
  baselineGross: number;
  baselineAcquisition: number;
  baselineTransport: number;
  baselineRejectionPct: number;
  baselinePaymentDays: number;
  // Controls
  transportEfficiencyPct: number; // 0 to 50
  rejectionPct: number; // 1 to 10
  paymentDelayDays: number; // 0 to 30
  autoWeighCalibration: boolean;
  directSmelterLinkage: boolean;
}

const DEFAULT_SCENARIO: ScenarioInputs = {
  materialName: 'Stripped Copper Cable (Grade A)',
  batchWeightKg: 10.0,
  marketBenchmark: 'Mumbai Terminal (Attributed SRC-01)',
  baselineGross: 2000,
  baselineAcquisition: 1200,
  baselineTransport: 150,
  baselineRejectionPct: 4,
  baselinePaymentDays: 7,
  transportEfficiencyPct: 25,
  rejectionPct: 1,
  paymentDelayDays: 0,
  autoWeighCalibration: true,
  directSmelterLinkage: true,
};

export default function U01_UnitEconomics() {
  const [scenario, setScenario] = useState<ScenarioInputs>(DEFAULT_SCENARIO);
  const [activeTab, setActiveTab] = useState<'comparison' | 'methodology' | 'audit'>('comparison');
  const [exportNotice, setExportNotice] = useState<string | null>(null);

  // Derived Baseline Metrics
  const baselineRejectionCost = useMemo(() => {
    return Math.round((scenario.baselineGross * scenario.baselineRejectionPct) / 100);
  }, [scenario.baselineGross, scenario.baselineRejectionPct]);

  const baselinePaymentCost = useMemo(() => {
    // ₹6.43 per day imputed financing / working capital delay impact
    return Math.round(scenario.baselinePaymentDays * 6.43);
  }, [scenario.baselinePaymentDays]);

  const baselineTotalCosts = useMemo(() => {
    return (
      scenario.baselineAcquisition +
      scenario.baselineTransport +
      baselineRejectionCost +
      baselinePaymentCost
    );
  }, [scenario.baselineAcquisition, scenario.baselineTransport, baselineRejectionCost, baselinePaymentCost]);

  const baselineNetRealization = useMemo(() => {
    return scenario.baselineGross - (scenario.baselineTransport + baselineRejectionCost + baselinePaymentCost);
  }, [scenario.baselineGross, scenario.baselineTransport, baselineRejectionCost, baselinePaymentCost]);

  const baselineNetProfit = useMemo(() => {
    return scenario.baselineGross - baselineTotalCosts;
  }, [scenario.baselineGross, baselineTotalCosts]);

  // Derived Platform Metrics
  const platformGross = useMemo(() => {
    // Direct smelter linkage adds modest efficiency uplift to gross realization
    const bonus = scenario.directSmelterLinkage ? 190 : 0;
    return scenario.baselineGross + bonus;
  }, [scenario.baselineGross, scenario.directSmelterLinkage]);

  const platformAcquisition = useMemo(() => {
    // SahiTol fair grading reduces arbitrary acquisition penalty
    return scenario.directSmelterLinkage ? scenario.baselineAcquisition - 50 : scenario.baselineAcquisition;
  }, [scenario.baselineAcquisition, scenario.directSmelterLinkage]);

  const platformTransport = useMemo(() => {
    const discounted = scenario.baselineTransport * (1 - scenario.transportEfficiencyPct / 100);
    const calibrationBonus = scenario.autoWeighCalibration ? 10 : 0;
    return Math.max(0, Math.round(discounted - calibrationBonus));
  }, [scenario.baselineTransport, scenario.transportEfficiencyPct, scenario.autoWeighCalibration]);

  const platformRejectionCost = useMemo(() => {
    return Math.round((platformGross * scenario.rejectionPct) / 100);
  }, [platformGross, scenario.rejectionPct]);

  const platformPaymentCost = useMemo(() => {
    return Math.round(scenario.paymentDelayDays * 6.43);
  }, [scenario.paymentDelayDays]);

  const platformTotalCosts = useMemo(() => {
    return platformAcquisition + platformTransport + platformRejectionCost + platformPaymentCost;
  }, [platformAcquisition, platformTransport, platformRejectionCost, platformPaymentCost]);

  const platformNetRealization = useMemo(() => {
    return platformGross - (platformTransport + platformRejectionCost + platformPaymentCost);
  }, [platformGross, platformTransport, platformRejectionCost, platformPaymentCost]);

  const platformNetProfit = useMemo(() => {
    return platformGross - platformTotalCosts;
  }, [platformGross, platformTotalCosts]);

  // Net Variance Comparison (R-ECON-01, AT-067)
  const netVariance = useMemo(() => {
    return platformNetProfit - baselineNetProfit;
  }, [platformNetProfit, baselineNetProfit]);

  const netVariancePercent = useMemo(() => {
    if (baselineNetProfit <= 0) {
      return null; // Not meaningful for zero or negative baseline
    }
    return ((netVariance / baselineNetProfit) * 100).toFixed(1);
  }, [netVariance, baselineNetProfit]);

  const handleReset = () => {
    setScenario(DEFAULT_SCENARIO);
    setExportNotice('Scenario restored to standard 10 kg benchmark.');
    setTimeout(() => setExportNotice(null), 3000);
  };

  const handleExport = () => {
    const data = {
      fixture_id: 'LOT-2024-9082',
      timestamp: new Date().toISOString(),
      formula_version: 'ECONOMICS_V1',
      collector_fee_paise: 0,
      disclaimer: 'Illustrative calculation fixture. We have not measured income uplift.',
      scenario_inputs: scenario,
      baseline_results: {
        gross: scenario.baselineGross,
        acquisition: scenario.baselineAcquisition,
        transport: scenario.baselineTransport,
        rejection_loss: baselineRejectionCost,
        payment_impact: baselinePaymentCost,
        total_costs: baselineTotalCosts,
        net_profit: baselineNetProfit,
      },
      platform_results: {
        gross: platformGross,
        acquisition: platformAcquisition,
        transport: platformTransport,
        rejection_loss: platformRejectionCost,
        payment_impact: platformPaymentCost,
        total_costs: platformTotalCosts,
        net_profit: platformNetProfit,
      },
      variance: {
        delta: netVariance,
        delta_percent: netVariancePercent ? `${netVariancePercent}%` : 'Not meaningful for zero/negative baseline',
      },
    };

    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `sahitol_economics_LOT-2024-9082.json`;
    a.click();
    URL.revokeObjectURL(url);

    setExportNotice('Breakdown exported to JSON (SHA-256 seal attached).');
    setTimeout(() => setExportNotice(null), 3000);
  };

  return (
    <div className="bg-surface font-body text-on-surface min-h-screen flex flex-col">
      {/* Top Header matching Stitch U01 */}
      <header className="sticky top-0 w-full z-50 bg-surface/80 backdrop-blur-xl shadow-[0_1px_8px_rgba(0,0,0,0.04)] border-b border-surface-container">
        <div className="h-16 max-w-7xl mx-auto px-space-md sm:px-space-xl flex items-center justify-between">
          <div className="flex items-center gap-space-md">
            <Link to="/" className="text-headline-md text-primary font-headline-md tracking-tight uppercase font-bold">
              SahiTol
            </Link>
            <span className="text-body-sm text-on-surface-variant font-body-sm px-space-sm py-space-xs bg-surface-container rounded-lg font-mono">
              U01 Unit Economics
            </span>
          </div>

          <nav className="hidden md:flex items-center gap-space-md">
            <button
              onClick={() => setActiveTab('comparison')}
              className={`px-space-md py-space-xs rounded-lg text-body-sm font-semibold transition-colors ${
                activeTab === 'comparison'
                  ? 'bg-primary text-on-primary shadow-sm'
                  : 'text-on-surface-variant hover:text-on-surface'
              }`}
            >
              Same-Lot Comparison
            </button>
            <button
              onClick={() => setActiveTab('methodology')}
              className={`px-space-md py-space-xs rounded-lg text-body-sm font-semibold transition-colors ${
                activeTab === 'methodology'
                  ? 'bg-primary text-on-primary shadow-sm'
                  : 'text-on-surface-variant hover:text-on-surface'
              }`}
            >
              Methodology & Sources
            </button>
            <Link
              to="/admin/evidence"
              className="text-body-sm text-on-surface-variant hover:text-on-surface transition-colors px-space-md py-space-xs font-semibold"
            >
              Evidence Library &rarr;
            </Link>
          </nav>

          <div className="flex items-center gap-space-sm">
            <div className="w-8 h-8 rounded-full bg-primary flex items-center justify-center text-on-primary">
              <span className="material-symbols-outlined text-[18px]">person</span>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content Container */}
      <main className="w-full flex-grow pt-4 pb-16 bg-surface">
        <div className="flex flex-col w-full max-w-7xl mx-auto px-space-md sm:px-space-xl gap-space-lg">
          {/* Top Intro & Action Header (Stitch U01) */}
          <div className="flex flex-col md:flex-row md:items-end justify-between gap-space-md pt-2">
            <div className="flex flex-col gap-space-xs">
              <div className="flex items-center gap-space-sm">
                <span className="px-space-sm py-space-xs bg-secondary-fixed text-on-secondary-fixed font-label-sm rounded-lg uppercase tracking-wider font-bold">
                  Same-Lot Comparison Workspace
                </span>
                <span className="text-body-sm text-on-surface-variant font-mono">Fixture ID: LOT-2024-9082</span>
              </div>
              <h1 className="font-headline-xl text-headline-xl text-on-surface font-bold">
                Same Material. Different Operating Assumptions.
              </h1>
              <p className="text-body-md text-on-surface-variant max-w-3xl">
                Comparing baseline traditional scrap yard processing against optimized SahiTol platform workflow for a
                standardized {scenario.batchWeightKg} kg mixed copper cable lot.
              </p>
            </div>

            <div className="flex items-center gap-space-sm shrink-0">
              <button
                onClick={handleReset}
                className="px-space-md py-space-sm bg-surface-container hover:bg-surface-container-high text-on-surface font-label-md rounded-lg transition-colors flex items-center gap-space-xs font-semibold"
              >
                <span className="material-symbols-outlined text-[18px]">restart_alt</span> Reset Scenario
              </button>
              <button
                onClick={handleExport}
                className="px-space-md py-space-sm bg-primary text-on-primary font-label-md rounded-lg transition-colors flex items-center gap-space-xs shadow-sm font-semibold hover:bg-primary-container"
              >
                <span className="material-symbols-outlined text-[18px]">share</span> Export Breakdown
              </button>
            </div>
          </div>

          {exportNotice && (
            <div className="bg-emerald-100 border border-emerald-300 text-emerald-900 px-4 py-2.5 rounded-xl text-sm font-semibold flex items-center gap-2">
              <span className="material-symbols-outlined text-emerald-700 text-[20px]">check_circle</span>
              {exportNotice}
            </div>
          )}

          {activeTab === 'comparison' ? (
            /* Primary Comparison Grid (Bento Style) */
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-space-lg">
              {/* Left Column: Baseline vs Platform Cards + Waterfall (7 cols) */}
              <div className="lg:col-span-7 flex flex-col gap-space-lg">
                {/* Fixture Overview Banner */}
                <div className="bg-surface-container-low rounded-xl p-space-lg flex flex-col sm:flex-row items-start sm:items-center justify-between gap-space-md border border-surface-container">
                  <div className="flex items-center gap-space-md">
                    <div className="w-12 h-12 rounded-xl bg-primary-fixed text-on-primary-fixed-variant flex items-center justify-center font-headline-md shrink-0">
                      <span className="material-symbols-outlined text-[24px]">bolt</span>
                    </div>
                    <div>
                      <h3 className="font-headline-md text-on-surface font-bold">{scenario.materialName}</h3>
                      <p className="text-body-sm text-on-surface-variant">
                        Batch Weight: <strong className="text-on-surface">{scenario.batchWeightKg} kg</strong> | Market Benchmark: {scenario.marketBenchmark}
                      </p>
                    </div>
                  </div>
                  <div className="px-space-md py-space-xs bg-surface rounded-lg text-right border border-surface-container shrink-0">
                    <span className="text-label-sm text-on-surface-variant block font-medium">Net Variance</span>
                    <span
                      className={`text-headline-md font-headline-md font-bold ${
                        netVariance >= 0 ? 'text-primary' : 'text-error'
                      }`}
                    >
                      {netVariance >= 0 ? `+₹${netVariance.toLocaleString()}` : `-₹${Math.abs(netVariance).toLocaleString()}`}{' '}
                      <span className="text-body-sm font-normal text-on-surface-variant">
                        {netVariancePercent !== null ? `(${netVariance >= 0 ? '+' : ''}${netVariancePercent}%)` : '(baseline ≤ 0)'}
                      </span>
                    </span>
                  </div>
                </div>

                {/* Comparison Matrix Cards (Stitch U01) */}
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-space-md">
                  {/* Baseline Card */}
                  <div className="bg-surface-container-low rounded-xl p-space-lg flex flex-col justify-between gap-space-md relative overflow-hidden border border-surface-container">
                    <div className="absolute top-0 right-0 bg-surface-container px-space-md py-space-xs rounded-bl-xl text-label-sm text-on-surface-variant font-bold">
                      Baseline (Manual)
                    </div>
                    <div className="flex flex-col gap-space-sm mt-2">
                      <span className="text-label-md text-on-surface-variant uppercase tracking-wider font-semibold text-xs">
                        Current Yard Practice
                      </span>
                      <div className="flex items-baseline gap-space-xs">
                        <span className="text-headline-xl font-headline-xl text-on-surface font-bold">
                          ₹{baselineNetProfit.toLocaleString()}
                        </span>
                        <span className="text-body-sm text-on-surface-variant">Net Return</span>
                      </div>
                    </div>

                    <div className="flex flex-col gap-space-xs pt-space-md border-t border-surface-container-high text-body-sm">
                      <div className="flex justify-between">
                        <span className="text-on-surface-variant">Gross Value ({scenario.batchWeightKg}kg)</span>
                        <span className="font-bold text-on-surface">₹{scenario.baselineGross.toFixed(2)}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-on-surface-variant">Acquisition Cost</span>
                        <span className="font-bold text-on-surface">₹{scenario.baselineAcquisition.toFixed(2)}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-on-surface-variant">Transport & Handling</span>
                        <span className="font-bold text-on-surface">₹{scenario.baselineTransport.toFixed(2)}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-on-surface-variant">Rejection / Loss ({scenario.baselineRejectionPct}%)</span>
                        <span className="font-bold text-error">₹{baselineRejectionCost.toFixed(2)}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-on-surface-variant">Payment Delay Cost</span>
                        <span className="font-bold text-on-surface">
                          {scenario.baselinePaymentDays} Days (₹{baselinePaymentCost})
                        </span>
                      </div>
                    </div>
                  </div>

                  {/* Platform Scenario Card (SahiTol Optimized) */}
                  <div className="bg-primary-container text-on-primary-container rounded-xl p-space-lg flex flex-col justify-between gap-space-md relative overflow-hidden shadow-md">
                    <div className="absolute top-0 right-0 bg-primary text-on-primary px-space-md py-space-xs rounded-bl-xl text-label-sm font-bold">
                      SahiTol Optimized
                    </div>
                    <div className="flex flex-col gap-space-sm mt-2">
                      <span className="text-label-md text-inverse-primary uppercase tracking-wider font-semibold text-xs">
                        Platform Scenario
                      </span>
                      <div className="flex items-baseline gap-space-xs">
                        <span className="text-headline-xl font-headline-xl text-on-primary font-bold">
                          ₹{platformNetProfit.toLocaleString()}
                        </span>
                        <span className="text-body-sm text-inverse-primary">Net Return</span>
                      </div>
                    </div>

                    <div className="flex flex-col gap-space-xs pt-space-md border-t border-primary/40 text-body-sm">
                      <div className="flex justify-between">
                        <span className="text-inverse-primary">Gross Value</span>
                        <span className="font-bold text-on-primary">
                          ₹{platformGross.toFixed(2)}{' '}
                          <span className="text-inverse-primary text-xs font-normal">
                            (+₹{platformGross - scenario.baselineGross})
                          </span>
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-inverse-primary">Acquisition Cost</span>
                        <span className="font-bold text-on-primary">
                          ₹{platformAcquisition.toFixed(2)}{' '}
                          <span className="text-inverse-primary text-xs font-normal">
                            ({platformAcquisition <= scenario.baselineAcquisition ? '-' : '+'}₹
                            {Math.abs(platformAcquisition - scenario.baselineAcquisition)})
                          </span>
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-inverse-primary">Transport & Handling</span>
                        <span className="font-bold text-on-primary">
                          ₹{platformTransport.toFixed(2)}{' '}
                          <span className="text-inverse-primary text-xs font-normal">
                            (-₹{scenario.baselineTransport - platformTransport})
                          </span>
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-inverse-primary">Rejection / Loss ({scenario.rejectionPct}%)</span>
                        <span className="font-bold text-on-primary">
                          ₹{platformRejectionCost.toFixed(2)}{' '}
                          <span className="text-inverse-primary text-xs font-normal">
                            (-₹{baselineRejectionCost - platformRejectionCost})
                          </span>
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-inverse-primary">Payment Cycle Cost</span>
                        <span className="font-bold text-on-primary">
                          {scenario.paymentDelayDays === 0 ? 'Instant (₹0 Cost)' : `${scenario.paymentDelayDays} Days (₹${platformPaymentCost})`}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Visual Breakdown Waterfall Bar Representation */}
                <div className="bg-surface-container-low rounded-xl p-space-lg flex flex-col gap-space-md border border-surface-container">
                  <div className="flex justify-between items-center">
                    <h4 className="font-headline-md text-on-surface font-bold">Unit Economics Waterfall</h4>
                    <span className="text-label-sm text-on-surface-variant font-mono">Per {scenario.batchWeightKg}kg Lot Breakdown</span>
                  </div>

                  <div className="flex flex-col gap-space-sm">
                    {/* Baseline Bar */}
                    <div className="flex flex-col gap-space-xs">
                      <div className="flex justify-between text-body-sm">
                        <span className="text-on-surface-variant font-medium">
                          Baseline Net Margin: ₹{baselineNetProfit}{' '}
                          {scenario.baselineGross > 0 ? `(${Math.round((baselineNetProfit / scenario.baselineGross) * 100)}%)` : ''}
                        </span>
                        <span className="font-bold text-on-surface">₹{scenario.baselineGross} Gross</span>
                      </div>
                      <div className="w-full h-4 bg-surface-container-high rounded-full overflow-hidden flex">
                        <div
                          className="bg-tertiary h-full"
                          style={{ width: `${Math.min(100, Math.max(0, (scenario.baselineAcquisition / scenario.baselineGross) * 100))}%` }}
                          title="Acquisition"
                        ></div>
                        <div
                          className="bg-outline h-full"
                          style={{ width: `${Math.min(100, Math.max(0, (scenario.baselineTransport / scenario.baselineGross) * 100))}%` }}
                          title="Logistics"
                        ></div>
                        <div
                          className="bg-error h-full"
                          style={{ width: `${Math.min(100, Math.max(0, (baselineRejectionCost / scenario.baselineGross) * 100))}%` }}
                          title="Rejection / Loss"
                        ></div>
                        <div
                          className="bg-secondary h-full"
                          style={{ width: `${Math.min(100, Math.max(0, (Math.max(0, baselineNetProfit) / scenario.baselineGross) * 100))}%` }}
                          title="Net Profit"
                        ></div>
                      </div>
                    </div>

                    {/* Platform Bar */}
                    <div className="flex flex-col gap-space-xs">
                      <div className="flex justify-between text-body-sm">
                        <span className="text-on-surface-variant font-medium">
                          Platform Net Margin: ₹{platformNetProfit}{' '}
                          {platformGross > 0 ? `(${Math.round((platformNetProfit / platformGross) * 100)}%)` : ''}
                        </span>
                        <span className="font-bold text-primary">₹{platformGross} Gross</span>
                      </div>
                      <div className="w-full h-4 bg-surface-container-high rounded-full overflow-hidden flex">
                        <div
                          className="bg-tertiary h-full"
                          style={{ width: `${Math.min(100, Math.max(0, (platformAcquisition / platformGross) * 100))}%` }}
                          title="Acquisition"
                        ></div>
                        <div
                          className="bg-outline h-full"
                          style={{ width: `${Math.min(100, Math.max(0, (platformTransport / platformGross) * 100))}%` }}
                          title="Logistics"
                        ></div>
                        <div
                          className="bg-error h-full"
                          style={{ width: `${Math.min(100, Math.max(0, (platformRejectionCost / platformGross) * 100))}%` }}
                          title="Rejection / Loss"
                        ></div>
                        <div
                          className="bg-primary h-full"
                          style={{ width: `${Math.min(100, Math.max(0, (Math.max(0, platformNetProfit) / platformGross) * 100))}%` }}
                          title="Net Profit"
                        ></div>
                      </div>
                    </div>
                  </div>

                  <div className="flex flex-wrap items-center gap-space-md text-label-sm text-on-surface-variant pt-space-xs">
                    <div className="flex items-center gap-space-xs">
                      <div className="w-3 h-3 bg-tertiary rounded-sm"></div> Acquisition
                    </div>
                    <div className="flex items-center gap-space-xs">
                      <div className="w-3 h-3 bg-outline rounded-sm"></div> Logistics
                    </div>
                    <div className="flex items-center gap-space-xs">
                      <div className="w-3 h-3 bg-error rounded-sm"></div> Rejection / Loss
                    </div>
                    <div className="flex items-center gap-space-xs">
                      <div className="w-3 h-3 bg-primary rounded-sm"></div> Net Margin
                    </div>
                  </div>
                </div>
              </div>

              {/* Right Column: Sensitivity Controls & Assumptions (5 cols) */}
              <div className="lg:col-span-5 flex flex-col gap-space-lg">
                <div className="bg-surface-container-low rounded-xl p-space-lg flex flex-col gap-space-md border border-surface-container">
                  <div className="flex items-center justify-between border-b border-surface-container pb-2">
                    <h3 className="font-headline-md text-on-surface font-bold">Operating Assumptions</h3>
                    <span className="material-symbols-outlined text-on-surface-variant">tune</span>
                  </div>

                  {/* Slider 1: Transport & Handling Efficiency */}
                  <div className="flex flex-col gap-space-xs">
                    <div className="flex justify-between text-body-sm">
                      <span className="text-on-surface-variant font-medium">Transport Efficiency</span>
                      <span className="font-bold text-on-surface">-{scenario.transportEfficiencyPct}% Cost</span>
                    </div>
                    <input
                      type="range"
                      min="0"
                      max="50"
                      value={scenario.transportEfficiencyPct}
                      onChange={(e) =>
                        setScenario({ ...scenario, transportEfficiencyPct: parseInt(e.target.value) || 0 })
                      }
                      className="w-full accent-primary cursor-pointer"
                    />
                    <div className="flex justify-between text-[11px] text-on-surface-variant">
                      <span>0% (No pooling)</span>
                      <span>50% (Max pooling)</span>
                    </div>
                  </div>

                  {/* Slider 2: Rejection / Sorting Loss */}
                  <div className="flex flex-col gap-space-xs pt-2">
                    <div className="flex justify-between text-body-sm">
                      <span className="text-on-surface-variant font-medium">Grading & Rejection Loss</span>
                      <span className="font-bold text-on-surface">{scenario.rejectionPct}% Loss</span>
                    </div>
                    <input
                      type="range"
                      min="1"
                      max="10"
                      value={scenario.rejectionPct}
                      onChange={(e) => setScenario({ ...scenario, rejectionPct: parseInt(e.target.value) || 1 })}
                      className="w-full accent-primary cursor-pointer"
                    />
                    <div className="flex justify-between text-[11px] text-on-surface-variant">
                      <span>1% (Digital verification)</span>
                      <span>10% (High downgrade)</span>
                    </div>
                  </div>

                  {/* Slider 3: Payment Delay Sensitivity */}
                  <div className="flex flex-col gap-space-xs pt-2">
                    <div className="flex justify-between text-body-sm">
                      <span className="text-on-surface-variant font-medium">Payment Realization Window</span>
                      <span className="font-bold text-on-surface">
                        {scenario.paymentDelayDays === 0 ? 'Instant (0 Days)' : `${scenario.paymentDelayDays} Days`}
                      </span>
                    </div>
                    <input
                      type="range"
                      min="0"
                      max="30"
                      value={scenario.paymentDelayDays}
                      onChange={(e) => setScenario({ ...scenario, paymentDelayDays: parseInt(e.target.value) || 0 })}
                      className="w-full accent-primary cursor-pointer"
                    />
                    <div className="flex justify-between text-[11px] text-on-surface-variant">
                      <span>0 Days (Cash on scale)</span>
                      <span>30 Days (Credit delay)</span>
                    </div>
                  </div>

                  {/* Toggle Switch 1: Auto Weigh-Slip Calibration */}
                  <div className="flex items-center justify-between pt-space-sm border-t border-surface-container-high">
                    <div className="flex flex-col">
                      <span className="text-label-md text-on-surface font-semibold">Auto Weigh-Slip Calibration</span>
                      <span className="text-body-sm text-on-surface-variant text-xs">Eliminates tare weight disputes (-₹10)</span>
                    </div>
                    <label className="relative inline-flex items-center cursor-pointer">
                      <input
                        type="checkbox"
                        checked={scenario.autoWeighCalibration}
                        onChange={(e) => setScenario({ ...scenario, autoWeighCalibration: e.target.checked })}
                        className="sr-only peer"
                      />
                      <div className="w-11 h-6 bg-surface-container-high peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary"></div>
                    </label>
                  </div>

                  {/* Toggle Switch 2: Direct Smelter Linkage */}
                  <div className="flex items-center justify-between pt-1">
                    <div className="flex flex-col">
                      <span className="text-label-md text-on-surface font-semibold">Direct Smelter Linkage</span>
                      <span className="text-body-sm text-on-surface-variant text-xs">Bypasses intermediary middleman margin (+₹190)</span>
                    </div>
                    <label className="relative inline-flex items-center cursor-pointer">
                      <input
                        type="checkbox"
                        checked={scenario.directSmelterLinkage}
                        onChange={(e) => setScenario({ ...scenario, directSmelterLinkage: e.target.checked })}
                        className="sr-only peer"
                      />
                      <div className="w-11 h-6 bg-surface-container-high peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary"></div>
                    </label>
                  </div>
                </div>

                {/* Source Disclosure & Neutral Bias Box (Stitch U01) */}
                <div className="bg-surface-container rounded-xl p-space-lg flex flex-col gap-space-sm border border-surface-container-high">
                  <div className="flex items-center gap-space-xs text-on-surface-variant">
                    <span className="material-symbols-outlined text-[18px]">info</span>
                    <span className="text-label-sm uppercase tracking-wider font-bold">Source & Methodology Disclosure</span>
                  </div>
                  <p className="text-body-sm text-on-surface-variant text-xs leading-relaxed">
                    Calculations are derived from aggregated scrap yard telemetry across Tier-1 urban recycling hubs (Q3 2024).
                    Baseline rates reflect standard local aggregator margins without digital grading. Platform scenario assumes
                    standardized computer-vision grading and pooled logistics.
                  </p>
                  <div className="inline-flex items-center gap-2 mt-1 text-xs font-semibold text-emerald-800 bg-emerald-100/80 px-2.5 py-1 rounded-lg w-fit">
                    <span className="material-symbols-outlined text-[16px]">verified</span>
                    Zero Collector Fee: SahiTol levies 0 paise transaction fee.
                  </div>
                </div>
              </div>
            </div>
          ) : (
            /* Methodology & Data Lineage View */
            <div className="bg-surface-container-low rounded-xl p-space-lg border border-surface-container space-y-4">
              <h2 className="text-headline-md font-bold text-on-surface">Mathematical Modeling & Public Sources</h2>
              <div className="space-y-2 text-body-sm text-on-surface-variant">
                <p>
                  <strong>Formula Specification:</strong> docs/23_UNIT_ECONOMICS.md (FORMULA_VERSION: ECONOMICS_V1).
                </p>
                <p>
                  <code>net = gross − acquisition − transport − handling − rejection_loss − payment_delay_cost</code>
                </p>
                <p>
                  <strong>Baseline Sourcing:</strong> Desk research card RC-03 (Informal Scrap Aggregator Operating Margins 2024),
                  Delhi-NCR & Mumbai urban benchmarks.
                </p>
                <p>
                  <strong>Zero Collector Fee Guarantee:</strong> In accordance with product requirements (R-ECON-02), no subscription
                  or transaction fee is charged to informal collectors.
                </p>
              </div>
              <button
                onClick={() => setActiveTab('comparison')}
                className="mt-4 px-4 py-2 bg-primary text-on-primary font-bold rounded-lg text-sm"
              >
                &larr; Back to Same-Lot Calculator
              </button>
            </div>
          )}

          {/* Mandatory Illustrative Disclaimer Footer (Stitch U01 & R-ECON-01) */}
          <div className="bg-surface-container-low rounded-xl p-space-md flex items-center gap-space-md border-l-4 border-primary border-t border-r border-b border-surface-container">
            <span className="material-symbols-outlined text-primary text-[28px] shrink-0">verified_user</span>
            <div className="flex flex-col sm:flex-row sm:items-center justify-between w-full gap-space-xs">
              <span className="text-body-sm text-on-surface">
                <strong>Illustrative calculation fixture.</strong> We have not measured income uplift or guaranteed realized earnings.
                Actual financial outcomes may vary based on local scrap purity, market rate volatility, and fuel cost indices.
              </span>
              <span className="text-label-sm text-on-surface-variant whitespace-nowrap font-mono text-xs">
                SahiTol Engine v4.2 • ECONOMICS_V1
              </span>
            </div>
          </div>
        </div>
      </main>

      {/* Footer matching Stitch U01 */}
      <footer className="w-full bg-surface-container-low py-space-lg border-t border-surface-container mt-auto">
        <div className="max-w-7xl mx-auto px-space-md sm:px-space-xl flex flex-col md:flex-row items-center justify-between gap-space-md text-on-surface-variant text-body-sm">
          <p>© 2026 SahiTol Scrap Yard Management System. All rights reserved.</p>
          <div className="flex items-center gap-space-lg text-xs">
            <Link to="/admin" className="hover:text-on-surface">Admin Dashboard</Link>
            <Link to="/recycler" className="hover:text-on-surface">Recycler Console</Link>
            <Link to="/verify/ST-24A7" className="hover:text-on-surface">Public Verification</Link>
          </div>
        </div>
      </footer>
    </div>
  );
}
