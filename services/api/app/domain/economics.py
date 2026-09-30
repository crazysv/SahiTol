"""Illustrative Economics & Platform Sustainability Domain Engine (T038).
Implements the same-lot current vs. platform comparison model, sensitivity analysis,
and hypothetical downstream platform sustainability calculator.
Technical specification: docs/23_UNIT_ECONOMICS.md, docs/16_API_CONTRACT.md lines 94-95.
Requirements: R-ECON-01, R-ECON-02.
Acceptance cases: AT-067, AT-068.
"""
from decimal import Decimal, ROUND_HALF_UP
import math
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

FORMULA_VERSION = "ECONOMICS_V1"

CAVEAT_ILLUSTRATIVE = (
    "This is an editable illustration based on stated public-source assumptions; "
    "we have not measured income uplift or guaranteed realized collector earnings."
)
CAVEAT_LEDGER_SEPARATION = (
    "Illustrative model outputs are strictly separated from actual transaction ledger records "
    "and do not constitute bank settlement or accounting receipts."
)
CAVEAT_SUSTAINABILITY = (
    "Hypothetical downstream service fee model for feasibility analysis only. "
    "Recyclers have not contracted or agreed to these fees, and no collector fee is charged."
)


def round_half_up(value: float | Decimal) -> int:
    """Round half up to integer paise or grams according to techspec standards."""
    d = Decimal(str(value))
    return int(d.quantize(Decimal("1"), rounding=ROUND_HALF_UP))


# =============================================================================
# Domain Models: Same-Lot Comparison
# =============================================================================

class SameLotInputs(BaseModel):
    """Inputs for same-lot current vs. platform comparison (R-ECON-01, AT-067)."""
    material_id: str = Field(..., description="Material identifier (e.g. MAT-PCB-01)")
    weight_g: int = Field(..., gt=0, description="Sold weight in integer grams")
    acquisition_cost_paise: int = Field(..., ge=0, description="Acquisition / buying cost in integer paise")
    
    # Current scenario parameters
    current_rate_paise_per_kg: int = Field(..., gt=0, description="Current selling rate in paise/kg")
    current_transport_paise: int = Field(default=0, ge=0, description="Current transport cost in paise")
    current_handling_paise: int = Field(default=0, ge=0, description="Current handling/sorting cost in paise")
    current_rejection_loss_paise: int = Field(default=0, ge=0, description="Current rejection / downgrade loss in paise")
    current_other_cost_paise: int = Field(default=0, ge=0, description="Other current costs in paise")
    current_time_hours: float = Field(default=0.0, ge=0.0, description="Time spent in hours")
    current_time_value_paise_per_hour: int = Field(default=0, ge=0, description="Optional imputed hourly time value")

    # Platform scenario parameters
    platform_rate_paise_per_kg: int = Field(..., gt=0, description="Platform selling rate in paise/kg")
    platform_transport_paise: int = Field(default=0, ge=0, description="Platform transport cost in paise")
    platform_handling_paise: int = Field(default=0, ge=0, description="Platform handling/sorting cost in paise")
    platform_rejection_loss_paise: int = Field(default=0, ge=0, description="Platform rejection / downgrade loss in paise")
    platform_other_cost_paise: int = Field(default=0, ge=0, description="Other platform costs in paise")
    platform_time_hours: float = Field(default=0.0, ge=0.0, description="Time spent in hours")
    platform_time_value_paise_per_hour: int = Field(default=0, ge=0, description="Optional imputed hourly time value")

    # Metadata & assumptions
    source_reference: Optional[str] = Field(None, description="Source URL or public reference citation")
    assumptions_note: Optional[str] = Field(None, description="Documented assumption rationale")


class ScenarioOutcome(BaseModel):
    """Breakdown for a single scenario branch (current or platform)."""
    rate_paise_per_kg: int
    gross_paise: int
    acquisition_cost_paise: int
    transport_paise: int
    handling_paise: int
    rejection_loss_paise: int
    other_cost_paise: int
    direct_costs_paise: int
    time_hours: float
    time_cost_paise: int
    total_costs_paise: int
    net_paise: int


class SensitivityBreakdown(BaseModel):
    """Sensitivity analysis across key operational variables (AT-067)."""
    acquisition_cost_plus_20_delta_paise: int
    acquisition_cost_minus_20_delta_paise: int
    free_pickup_delta_paise: int
    time_hours_saved: float
    time_value_saved_paise: int
    rejection_5pct_impact_paise: int


class SameLotComparisonResult(BaseModel):
    """Complete transparent same-lot calculation result (R-ECON-01, AT-067)."""
    formula_version: str = FORMULA_VERSION
    is_illustrative: bool = True
    material_id: str
    weight_g: int
    
    current: ScenarioOutcome
    platform: ScenarioOutcome
    
    delta_paise: int
    delta_percent: Optional[float] = None
    delta_percent_display: str
    is_platform_favorable: bool
    
    sensitivity: SensitivityBreakdown
    caveats: List[str]
    source_reference: Optional[str] = None
    assumptions_note: Optional[str] = None


# =============================================================================
# Calculation Engine: Same-Lot Comparison
# =============================================================================

def calculate_same_lot_comparison(inputs: SameLotInputs) -> SameLotComparisonResult:
    """
    Compute transparent same-lot comparison between current baseline and platform scenarios.
    Follows docs/23_UNIT_ECONOMICS.md lines 7-16.
    """
    # 1. Current scenario
    curr_gross = round_half_up(Decimal(inputs.weight_g) * Decimal(inputs.current_rate_paise_per_kg) / Decimal(1000))
    curr_direct_costs = (
        inputs.acquisition_cost_paise
        + inputs.current_transport_paise
        + inputs.current_handling_paise
        + inputs.current_rejection_loss_paise
        + inputs.current_other_cost_paise
    )
    curr_time_cost = round_half_up(Decimal(str(inputs.current_time_hours)) * Decimal(inputs.current_time_value_paise_per_hour))
    curr_total_costs = curr_direct_costs + curr_time_cost
    curr_net = curr_gross - curr_total_costs

    current_outcome = ScenarioOutcome(
        rate_paise_per_kg=inputs.current_rate_paise_per_kg,
        gross_paise=curr_gross,
        acquisition_cost_paise=inputs.acquisition_cost_paise,
        transport_paise=inputs.current_transport_paise,
        handling_paise=inputs.current_handling_paise,
        rejection_loss_paise=inputs.current_rejection_loss_paise,
        other_cost_paise=inputs.current_other_cost_paise,
        direct_costs_paise=curr_direct_costs,
        time_hours=inputs.current_time_hours,
        time_cost_paise=curr_time_cost,
        total_costs_paise=curr_total_costs,
        net_paise=curr_net,
    )

    # 2. Platform scenario
    plat_gross = round_half_up(Decimal(inputs.weight_g) * Decimal(inputs.platform_rate_paise_per_kg) / Decimal(1000))
    plat_direct_costs = (
        inputs.acquisition_cost_paise
        + inputs.platform_transport_paise
        + inputs.platform_handling_paise
        + inputs.platform_rejection_loss_paise
        + inputs.platform_other_cost_paise
    )
    plat_time_cost = round_half_up(Decimal(str(inputs.platform_time_hours)) * Decimal(inputs.platform_time_value_paise_per_hour))
    plat_total_costs = plat_direct_costs + plat_time_cost
    plat_net = plat_gross - plat_total_costs

    platform_outcome = ScenarioOutcome(
        rate_paise_per_kg=inputs.platform_rate_paise_per_kg,
        gross_paise=plat_gross,
        acquisition_cost_paise=inputs.acquisition_cost_paise,
        transport_paise=inputs.platform_transport_paise,
        handling_paise=inputs.platform_handling_paise,
        rejection_loss_paise=inputs.platform_rejection_loss_paise,
        other_cost_paise=inputs.platform_other_cost_paise,
        direct_costs_paise=plat_direct_costs,
        time_hours=inputs.platform_time_hours,
        time_cost_paise=plat_time_cost,
        total_costs_paise=plat_total_costs,
        net_paise=plat_net,
    )

    # 3. Delta & percentage calculation
    # docs/23_UNIT_ECONOMICS.md line 13:
    # delta = platform_net - current_net
    # delta_percent = 100 * delta / current_net only for POSITIVE current net;
    # otherwise show "not meaningful for zero/negative baseline"
    delta_paise = plat_net - curr_net
    if curr_net > 0:
        delta_pct = round(float(Decimal(delta_paise * 100) / Decimal(curr_net)), 2)
        delta_pct_display = f"{'+' if delta_pct > 0 else ''}{delta_pct:.2f}%"
    else:
        delta_pct = None
        delta_pct_display = "not meaningful for zero/negative baseline"

    is_favorable = delta_paise > 0

    # 4. Sensitivity calculations
    # Acquisition cost sensitivity (+20% and -20%)
    acq_plus_20 = round_half_up(Decimal(inputs.acquisition_cost_paise) * Decimal("1.20"))
    acq_minus_20 = round_half_up(Decimal(inputs.acquisition_cost_paise) * Decimal("0.80"))
    
    # Delta with acquisition +/- 20% affects both equally in same-lot, so delta_paise remains identical
    # but net profit changes
    acq_diff_20 = acq_plus_20 - inputs.acquisition_cost_paise
    
    # Free pickup sensitivity: what if platform transport is ₹0?
    free_pickup_plat_net = plat_net + inputs.platform_transport_paise
    free_pickup_delta = free_pickup_plat_net - curr_net

    # Time saved
    time_saved_hrs = round(inputs.current_time_hours - inputs.platform_time_hours, 2)
    time_val_saved = curr_time_cost - plat_time_cost

    # 5% rejection impact on platform gross
    rejection_5pct_loss = round_half_up(Decimal(plat_gross) * Decimal("0.05"))

    sensitivity = SensitivityBreakdown(
        acquisition_cost_plus_20_delta_paise=delta_paise,
        acquisition_cost_minus_20_delta_paise=delta_paise,
        free_pickup_delta_paise=free_pickup_delta,
        time_hours_saved=time_saved_hrs,
        time_value_saved_paise=time_val_saved,
        rejection_5pct_impact_paise=rejection_5pct_loss,
    )

    return SameLotComparisonResult(
        formula_version=FORMULA_VERSION,
        is_illustrative=True,
        material_id=inputs.material_id,
        weight_g=inputs.weight_g,
        current=current_outcome,
        platform=platform_outcome,
        delta_paise=delta_paise,
        delta_percent=delta_pct,
        delta_percent_display=delta_pct_display,
        is_platform_favorable=is_favorable,
        sensitivity=sensitivity,
        caveats=[CAVEAT_ILLUSTRATIVE, CAVEAT_LEDGER_SEPARATION],
        source_reference=inputs.source_reference,
        assumptions_note=inputs.assumptions_note,
    )


# =============================================================================
# Domain Models: Platform Sustainability
# =============================================================================

class SustainabilityInputs(BaseModel):
    """Inputs for hypothetical platform downstream sustainability analysis (R-ECON-02, AT-068)."""
    monthly_completed_transactions: int = Field(..., ge=0, description="Monthly formal completed transactions")
    fee_model: str = Field(default="FIXED_PER_TRANSACTION", description="FIXED_PER_TRANSACTION or PERCENTAGE_OF_VALUE")
    assumed_fee_per_transaction_paise: int = Field(default=0, ge=0, description="Fixed fee per transaction in paise")
    assumed_fee_percentage: float = Field(default=0.0, ge=0.0, le=100.0, description="Percentage of transaction value")
    average_transaction_value_paise: int = Field(default=0, ge=0, description="Average transaction value in paise")
    
    variable_cost_per_transaction_paise: int = Field(..., ge=0, description="Per-transaction variable cost (storage, verification, SMS)")
    fixed_monthly_hosting_paise: int = Field(default=0, ge=0, description="Cloud hosting and database cost")
    fixed_monthly_verification_support_paise: int = Field(default=0, ge=0, description="Verification review and helpdesk operations")
    fixed_monthly_administration_paise: int = Field(default=0, ge=0, description="General platform administration cost")


class SustainabilityResult(BaseModel):
    """Hypothetical platform sustainability economics (R-ECON-02, AT-068)."""
    formula_version: str = FORMULA_VERSION
    is_illustrative: bool = True
    
    # Non-negotiable constraint: zero collector fees
    collector_fee_paise: int = 0
    collector_fee_policy: str = "FREE_TO_COLLECTORS"
    
    # Revenue breakdown
    fee_model: str
    assumed_fee_per_transaction_paise: int
    monthly_completed_transactions: int
    total_monthly_revenue_paise: int
    
    # Cost breakdown
    variable_cost_per_transaction_paise: int
    total_monthly_variable_costs_paise: int
    contribution_per_transaction_paise: int
    total_monthly_fixed_costs_paise: int
    
    # Operating result & break-even
    monthly_operating_result_paise: int
    is_operating_positive: bool
    break_even_transaction_count: Optional[int]
    break_even_status: str
    
    disclaimer: str = CAVEAT_SUSTAINABILITY


def calculate_platform_sustainability(inputs: SustainabilityInputs) -> SustainabilityResult:
    """
    Compute hypothetical platform sustainability without charging informal collectors.
    Follows docs/23_UNIT_ECONOMICS.md lines 19-24.
    """
    # 1. Determine per-transaction revenue
    if inputs.fee_model == "PERCENTAGE_OF_VALUE":
        eff_fee_paise = round_half_up(
            Decimal(inputs.average_transaction_value_paise) * Decimal(str(inputs.assumed_fee_percentage)) / Decimal(100)
        )
    else:
        eff_fee_paise = inputs.assumed_fee_per_transaction_paise

    total_revenue_paise = inputs.monthly_completed_transactions * eff_fee_paise
    total_variable_costs_paise = inputs.monthly_completed_transactions * inputs.variable_cost_per_transaction_paise
    contribution_per_tx_paise = eff_fee_paise - inputs.variable_cost_per_transaction_paise

    total_fixed_costs_paise = (
        inputs.fixed_monthly_hosting_paise
        + inputs.fixed_monthly_verification_support_paise
        + inputs.fixed_monthly_administration_paise
    )

    monthly_operating_result = (inputs.monthly_completed_transactions * contribution_per_tx_paise) - total_fixed_costs_paise
    is_positive = monthly_operating_result > 0

    # Break-even count
    # docs/23_UNIT_ECONOMICS.md line 23:
    # ceiling(fixed_cost / contribution_per_transaction) if positive, else no finite break-even
    if contribution_per_tx_paise > 0:
        break_even_count = math.ceil(total_fixed_costs_paise / contribution_per_tx_paise)
        break_even_status = "FINITE"
    else:
        break_even_count = None
        break_even_status = "NO_FINITE_BREAK_EVEN"

    return SustainabilityResult(
        formula_version=FORMULA_VERSION,
        is_illustrative=True,
        collector_fee_paise=0,
        collector_fee_policy="FREE_TO_COLLECTORS",
        fee_model=inputs.fee_model,
        assumed_fee_per_transaction_paise=eff_fee_paise,
        monthly_completed_transactions=inputs.monthly_completed_transactions,
        total_monthly_revenue_paise=total_revenue_paise,
        variable_cost_per_transaction_paise=inputs.variable_cost_per_transaction_paise,
        total_monthly_variable_costs_paise=total_variable_costs_paise,
        contribution_per_transaction_paise=contribution_per_tx_paise,
        total_monthly_fixed_costs_paise=total_fixed_costs_paise,
        monthly_operating_result_paise=monthly_operating_result,
        is_operating_positive=is_positive,
        break_even_transaction_count=break_even_count,
        break_even_status=break_even_status,
        disclaimer=CAVEAT_SUSTAINABILITY,
    )
