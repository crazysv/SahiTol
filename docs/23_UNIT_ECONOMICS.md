# Illustrative collector and platform economics

Required editable U01 screen, T038/T039 and deck narrative. Owner chose an **illustrative calculation based on stated public-source assumptions**, not primary income measurement. Sources inform context/ranges; every concrete default needs a source or an explicit “chosen scenario assumption.” Actual ledger records never get mixed into the model silently. Read [evidence rules](21_RESEARCH_EVIDENCE.md).

## Same-lot comparison

Use the same material, quantity, condition and period for current and platform scenarios. Inputs (integer paise/grams where monetary/physical): quantity, buying/acquisition cost, selling rate or fixed gross, transport/pickup, handling/sorting, rejection/loss cost, other costs, time hours and optional time-value cost. Quantity losses cannot be double-counted both by lowering sold weight and subtracting their full sale value. Price cohorts/units must be comparable.

`gross = round_half_up(sold_weight_g × rate_paise_per_kg / 1000)` or explicit fixed gross.

`net = gross − acquisition − transport − handling − rejection_loss_cost − other_cost − optional_time_cost`.

`delta = platform_net − current_net`; `delta_percent = 100 × delta / current_net` only for **positive** current net; otherwise show “not meaningful for zero/negative baseline.” Net is a scenario return after listed costs, not verified wage or household income. Cashflow views distinguish receivable from acknowledged paid; optional payment-delay sensitivity uses labelled assumptions, never bank lending promises.

Purely illustrative test fixture, **not sourced market prices**: 10kg, acquisition ₹1,000; current rate ₹150/kg, transport ₹100, handling ₹50 → current net ₹350. Platform assumed rate ₹160/kg, transport ₹80, handling ₹50 → net ₹470, delta ₹120, 34.29%. Keep this fixture in demo/tests only. UI should permit lower platform rate/higher transport so negative benefit appears; no default animation implying the platform always wins. A production-facing default must visibly carry “illustrative” and link its input sources/assumptions.

For each input retain value/unit/source URL or assumption rationale, observation date/region/material, author/version and confidence. Public quote does not establish realized collector price or monthly income. Do not multiply one lot into a monthly outcome without displaying lots/day, working days, capacity, costs and uncertainty as editable assumptions.

## Platform sustainability

No collector subscription or transaction fee in prototype. A hypothetical downstream service fee can be modelled separately: `revenue = eligible_completed_transactions × assumed_fee` (or declared percent of relevant value, never both inadvertently). `contribution = revenue − per_transaction_variable_costs`; `operating_result = contribution − fixed_period_costs`. Include hosting/storage, support/onboarding/verification and administration assumptions; free-tier prototype bills are not long-term zero costs.

For positive per-transaction contribution, break-even count is ceiling(fixed_cost / contribution_per_transaction); otherwise show no finite break-even under these inputs. Do not claim recyclers agreed to pay. No payment collection, monetization SDK, subsidy, CSR contract or credit referral is implemented merely because economics discusses it.

## Acceptance

Tests cover exact fixture arithmetic, non-integer kg, paise rounding, same unit basis, zero/negative baseline, negative platform benefit, zero contribution, invalid/overflow inputs and source/assumption display. U01 updates all results from inputs, has hi/mr labels and accessible numbers, links actual ledger separately, and uses owner-generated Stitch screens. Presenters state: “This is an editable illustration; we have not measured income uplift.”
