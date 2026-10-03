import React, { useEffect, useState } from 'react';
import { useNavigate, useSearchParams, Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { createRecyclerOffer, fetchRecyclerIncoming } from '../../lib/api';

export default function R03_QuoteTerminal() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const requestId = searchParams.get('requestId');
  const { data: incoming, isLoading, error } = useQuery({
    queryKey: ['recycler-incoming'], queryFn: fetchRecyclerIncoming,
  });
  const request = incoming?.find((item) => item.request_id === requestId);
  const lotRef = request?.lot_id || searchParams.get('ref') || 'Unknown lot';
  const weight = request ? (request.lot.estimated_weight_g || 0) / 1000 : 0;
  const materialName = request?.lot.material_name || request?.lot.material_id || 'Unspecified material';
  const hasOpenOffer = request?.offers.some((offer) => offer.status === 'OPEN') ?? false;
  const dispatchBlocked = request ? request.state !== 'PENDING' || hasOpenOffer : true;

  const [pricingModel, setPricingModel] = useState<'RATE_PER_KG' | 'FIXED_TOTAL'>('RATE_PER_KG');
  const [ratePerKg, setRatePerKg] = useState(180);
  const [fixedTotal, setFixedTotal] = useState(0);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [quoteDispatched, setQuoteDispatched] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);

  useEffect(() => {
    if (request && fixedTotal === 0) setFixedTotal(Math.round(weight * ratePerKg));
  }, [request, weight, ratePerKg, fixedTotal]);

  const calculatedTotal = pricingModel === 'RATE_PER_KG' ? Math.round(weight * ratePerKg) : fixedTotal;

  const handleDispatchQuote = async () => {
    if (!requestId || !request || dispatchBlocked || weight <= 0) {
      setSubmitError('This quote must be opened from one pending live incoming request with a positive declared weight.');
      return;
    }
    setIsSubmitting(true);
    setSubmitError(null);
    try {
      await createRecyclerOffer(requestId, {
        price_basis: pricingModel,
        rate_paise_per_kg: pricingModel === 'RATE_PER_KG' ? Math.round(ratePerKg * 100) : undefined,
        fixed_total_paise: pricingModel === 'FIXED_TOTAL' ? Math.round(fixedTotal * 100) : undefined,
        condition: request.lot.condition || 'UNSPECIFIED',
        weight_basis_g: Math.round(weight * 1000),
      });
      setIsSubmitting(false);
      setQuoteDispatched(true);
    } catch (error) {
      setIsSubmitting(false);
      setSubmitError(error instanceof Error ? error.message : 'Could not create the offer.');
    }
  };

  if (isLoading) return <p className="text-sm text-on-surface-variant">Loading the live request before preparing an offer…</p>;
  if (error || !request) return (
    <div className="space-y-space-md">
      <p className="text-sm text-error" role="alert">{error instanceof Error ? error.message : 'This incoming request is no longer available to this recycler account.'}</p>
      <Link to="/recycler" className="text-sm text-primary hover:underline">Return to Inbox</Link>
    </div>
  );

  return (
    <div className="space-y-space-lg max-w-4xl mx-auto">
      {/* Header bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-space-md pb-space-sm border-b border-surface-container-high">
        <div>
          <div className="flex items-center gap-2 text-xs text-on-surface-variant mb-1">
            <Link to="/recycler" className="hover:underline flex items-center gap-1">
              <span className="material-symbols-outlined text-[16px]">arrow_back</span> Back to Inbox
            </Link>
            <span>/</span>
            <span>Commercial Quote</span>
          </div>
          <h2 className="text-2xl lg:text-3xl font-headline font-bold text-on-surface">
            Commercial Offer Terminal: <span className="text-primary font-mono">{lotRef}</span>
          </h2>
          <p className="text-xs text-on-surface-variant mt-0.5">
            Live request • Declared weight: <span className="font-bold text-on-surface font-mono">{weight} kg</span>
          </p>
        </div>

        <div className="bg-surface-container-high p-space-md rounded-lg text-right">
          <span className="text-xs text-on-surface-variant block font-medium">Offer Validity Window</span>
          <span className="text-sm font-headline font-bold text-primary flex items-center gap-1 mt-0.5 justify-end">
            <span className="material-symbols-outlined text-[18px]">schedule</span>
            4 Hours from Dispatch
          </span>
        </div>
      </div>

      {quoteDispatched ? (
        <div className="bg-emerald-50 border border-emerald-300 rounded-xl p-space-xl text-center space-y-space-md">
          <div className="w-16 h-16 bg-emerald-100 text-emerald-700 rounded-full flex items-center justify-center mx-auto">
            <span className="material-symbols-outlined text-4xl">check_circle</span>
          </div>
          <h3 className="text-2xl font-headline font-bold text-emerald-900">
            Quote Successfully Dispatched!
          </h3>
          <p className="text-sm text-emerald-800 max-w-md mx-auto">
            Commercial offer of <span className="font-bold font-mono">₹{calculatedTotal.toLocaleString('en-IN')}</span> has been transmitted for lot <span className="font-bold font-mono">{lotRef}</span>. Terms are locked to the server-issued request.
          </p>
          <div className="pt-space-md flex justify-center gap-space-md">
            <Link
              to="/recycler"
              className="px-space-lg py-2.5 bg-primary text-on-primary font-headline font-bold text-sm rounded-lg hover:bg-primary-container transition-colors shadow-sm"
            >
              Return to Inbox
            </Link>
            <Link
              to="/recycler/history"
              className="px-space-lg py-2.5 bg-surface-container-high text-on-surface font-headline font-semibold text-sm rounded-lg hover:bg-surface-container-highest transition-colors"
            >
              View Active Bids
            </Link>
          </div>
        </div>
      ) : dispatchBlocked ? (
        <div className="bg-surface-container-low rounded-xl p-space-xl shadow-sm border border-surface-container-high text-center space-y-space-md">
          <div className="w-16 h-16 bg-surface-container-high text-on-surface-variant rounded-full flex items-center justify-center mx-auto">
            <span className="material-symbols-outlined text-4xl">task_alt</span>
          </div>
          <h3 className="text-2xl font-headline font-bold text-on-surface">
            {request.state === 'ACCEPTED' ? 'This offer has already been accepted' : hasOpenOffer ? 'This request already has an active offer' : `This request is ${request.state.toLowerCase()}`}
          </h3>
          <p className="text-sm text-on-surface-variant max-w-lg mx-auto">
            {request.state === 'ACCEPTED'
              ? `Lot ${lotRef} is already under agreed terms. A second quote cannot be dispatched.`
              : hasOpenOffer
                ? `The collector already has a live offer for lot ${lotRef}. Return to the inbox instead of sending a duplicate.`
                : `Lot ${lotRef} is no longer available for a new quote.`}
          </p>
          <div className="pt-space-md flex justify-center gap-space-md">
            <Link
              to="/recycler"
              className="px-space-lg py-2.5 bg-primary text-on-primary font-headline font-bold text-sm rounded-lg hover:bg-primary-container transition-colors shadow-sm"
            >
              Return to Inbox
            </Link>
            <Link
              to="/recycler/history"
              className="px-space-lg py-2.5 bg-surface-container-high text-on-surface font-headline font-semibold text-sm rounded-lg hover:bg-surface-container-highest transition-colors"
            >
              View History
            </Link>
          </div>
        </div>
      ) : (
        <>
          {/* Material & Lot Summary Card */}
          <div className="bg-surface-container-low rounded-xl p-space-lg shadow-sm border border-surface-container-high">
            <div className="flex items-center justify-between mb-space-md">
              <h3 className="text-base font-headline font-bold text-on-surface flex items-center gap-2">
                <span className="material-symbols-outlined text-primary text-[20px]">inventory_2</span>
                Material Lot Payload
              </h3>
              <span className="text-xs font-mono text-on-surface-variant">LOT-{lotRef}</span>
            </div>

            <div className="overflow-x-auto rounded-lg border border-surface-container-high">
              <table className="w-full text-left text-sm">
                <thead className="bg-surface-container-high text-xs text-on-surface-variant font-headline uppercase">
                  <tr>
                    <th className="p-space-md">Material Grade</th>
                    <th className="p-space-md">Purity Spec</th>
                    <th className="p-space-md">Scale Certified Weight</th>
                    <th className="p-space-md text-right">Computed Baseline</th>
                  </tr>
                </thead>
                <tbody className="bg-surface-container-lowest divide-y divide-surface-container-high">
                  <tr>
                    <td className="p-space-md font-headline font-bold text-on-surface">
                      {materialName}
                    </td>
                    <td className="p-space-md text-on-surface-variant text-xs">
                      {request.lot.condition || 'Condition not specified'}
                    </td>
                    <td className="p-space-md font-mono text-on-surface font-bold">
                      {weight.toFixed(2)} kg
                    </td>
                    <td className="p-space-md text-right font-mono font-bold text-primary">
                      ₹{calculatedTotal.toLocaleString('en-IN')}.00
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          {/* Pricing Model Selector */}
          <div className="bg-surface-container-low rounded-xl p-space-lg shadow-sm border border-surface-container-high space-y-space-md">
            <h3 className="text-base font-headline font-bold text-on-surface flex items-center gap-2">
              <span className="material-symbols-outlined text-primary text-[20px]">payments</span>
              Select Commercial Pricing Model
            </h3>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-space-md">
              {/* Option 1: Variable Rate Model */}
              <label
                onClick={() => setPricingModel('RATE_PER_KG')}
                className={`relative flex flex-col p-space-lg rounded-xl border-2 cursor-pointer transition-all ${
                  pricingModel === 'RATE_PER_KG'
                    ? 'bg-surface-container-lowest border-primary shadow-md'
                    : 'bg-surface-container-high/40 border-surface-container-high hover:border-outline'
                }`}
              >
                <div className="flex items-center justify-between mb-space-sm">
                  <span className="text-sm font-headline font-bold text-on-surface">
                    Rate per Kilogram (RATE_PER_KG)
                  </span>
                  <input
                    type="radio"
                    name="pricing_model"
                    checked={pricingModel === 'RATE_PER_KG'}
                    onChange={() => setPricingModel('RATE_PER_KG')}
                    className="w-4 h-4 accent-primary"
                  />
                </div>
                <p className="text-xs text-on-surface-variant mb-space-md">
                  Calculated dynamically from verified scale mass multiplied by your agreed unit rate.
                </p>

                <div className="mt-auto space-y-2 pt-space-xs border-t border-surface-variant">
                  <div className="flex items-center justify-between gap-2">
                    <span className="text-xs font-semibold text-on-surface-variant">Offer Rate (₹/kg):</span>
                    <input
                      type="number"
                      value={ratePerKg}
                      onChange={(e) => setRatePerKg(parseFloat(e.target.value) || 0)}
                      className="w-24 p-1.5 text-right font-mono font-bold text-sm bg-surface-container-lowest border border-outline-variant rounded"
                    />
                  </div>
                  <div className="flex justify-between items-baseline text-xs">
                    <span className="text-on-surface-variant">Total Quote:</span>
                    <span className="text-base font-mono font-bold text-primary">
                      ₹{Math.round(weight * ratePerKg).toLocaleString('en-IN')}
                    </span>
                  </div>
                </div>
              </label>

              {/* Option 2: Fixed Total Lot Model */}
              <label
                onClick={() => setPricingModel('FIXED_TOTAL')}
                className={`relative flex flex-col p-space-lg rounded-xl border-2 cursor-pointer transition-all ${
                  pricingModel === 'FIXED_TOTAL'
                    ? 'bg-surface-container-lowest border-primary shadow-md'
                    : 'bg-surface-container-high/40 border-surface-container-high hover:border-outline'
                }`}
              >
                <div className="flex items-center justify-between mb-space-sm">
                  <span className="text-sm font-headline font-bold text-on-surface">
                    Fixed Total Sum (FIXED_TOTAL)
                  </span>
                  <input
                    type="radio"
                    name="pricing_model"
                    checked={pricingModel === 'FIXED_TOTAL'}
                    onChange={() => setPricingModel('FIXED_TOTAL')}
                    className="w-4 h-4 accent-primary"
                  />
                </div>
                <p className="text-xs text-on-surface-variant mb-space-md">
                  Lump-sum commercial commitment locked for the entire verified lot payload regardless of tare variations.
                </p>

                <div className="mt-auto space-y-2 pt-space-xs border-t border-surface-variant">
                  <div className="flex items-center justify-between gap-2">
                    <span className="text-xs font-semibold text-on-surface-variant">Lump Sum (₹):</span>
                    <input
                      type="number"
                      value={fixedTotal}
                      onChange={(e) => setFixedTotal(parseFloat(e.target.value) || 0)}
                      className="w-32 p-1.5 text-right font-mono font-bold text-sm bg-surface-container-lowest border border-outline-variant rounded"
                    />
                  </div>
                  <div className="flex justify-between items-baseline text-xs">
                    <span className="text-on-surface-variant">Fixed Quote:</span>
                    <span className="text-base font-mono font-bold text-on-surface">
                      ₹{fixedTotal.toLocaleString('en-IN')}
                    </span>
                  </div>
                </div>
              </label>
            </div>
          </div>

          {/* Statutory Integrity Note */}
          <div className="p-space-md bg-surface-container rounded-lg border border-surface-container-high text-xs text-on-surface-variant space-y-1">
            <div className="flex items-center gap-1.5 font-headline font-bold text-on-surface">
              <span className="material-symbols-outlined text-[16px] text-primary">security</span>
              SahiTol Platform Integrity & Statutory Notice
            </div>
            <p>
              Digital Handover Record is an audit log of physical scrap custody, not a statutory EPR certificate. 
              Zero deductions apply to the collector (Collector Platform Fee = 0 paise).
            </p>
          </div>

          {/* Action Terminal Buttons */}
          {submitError && (
            <p className="text-sm text-error" role="alert">{submitError}</p>
          )}
          <div className="flex flex-col sm:flex-row items-center justify-between gap-space-md pt-space-sm">
            <button
              onClick={() => navigate('/recycler')}
              className="w-full sm:w-auto px-space-lg py-2.5 bg-surface-container-high hover:bg-surface-container-highest text-on-surface font-semibold text-sm rounded-xl transition-colors"
            >
              Cancel & Return
            </button>

            <div className="flex items-center gap-space-sm w-full sm:w-auto">
              <button
                onClick={() => {
                  if (confirm('Are you sure you want to reject this lot? It will be rematched back to LISTED status.')) {
                    navigate('/recycler');
                  }
                }}
                className="w-full sm:w-auto px-space-md py-2.5 border border-error text-error hover:bg-error/10 font-semibold text-sm rounded-xl transition-colors"
              >
                Reject Lot
              </button>

              <button
                onClick={handleDispatchQuote}
                disabled={isSubmitting}
                className="w-full sm:w-auto px-space-xl py-2.5 bg-primary hover:bg-primary-container text-on-primary font-headline font-bold text-sm rounded-xl shadow-md flex items-center justify-center gap-2 transition-all active:scale-[0.98]"
              >
                <span className="material-symbols-outlined text-[18px]">send</span>
                <span>{isSubmitting ? 'Transmitting...' : `Dispatch Quote (₹${calculatedTotal.toLocaleString('en-IN')})`}</span>
              </button>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
