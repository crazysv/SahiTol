"""Illustrative Economics & Platform Sustainability Router (T038).
Implements transparent same-lot comparison, sensitivity analysis, stored scenarios,
and hypothetical platform sustainability models.
Technical specification: docs/23_UNIT_ECONOMICS.md, docs/16_API_CONTRACT.md lines 94-95.
Requirements: R-ECON-01, R-ECON-02.
Acceptance cases: AT-067, AT-068.
"""
from datetime import datetime, timezone
import uuid
from typing import List, Dict, Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field, ConfigDict
from sqlalchemy.orm import Session
from sqlalchemy import select, or_

from app.db.session import get_db
from app.db.models.audit import EconomicsScenario
from app.db.models.auth import User
from app.security import get_current_user, UserRole
from app.domain.economics import (
    FORMULA_VERSION,
    CAVEAT_ILLUSTRATIVE,
    CAVEAT_LEDGER_SEPARATION,
    CAVEAT_SUSTAINABILITY,
    SameLotInputs,
    SameLotComparisonResult,
    SustainabilityInputs,
    SustainabilityResult,
    calculate_same_lot_comparison,
    calculate_platform_sustainability,
)

router = APIRouter(tags=["economics"])


# =============================================================================
# Request / Response Schemas
# =============================================================================

class CreateScenarioRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=100, description="Descriptive scenario name")
    inputs: SameLotInputs
    source_ids: List[str] = Field(default_factory=list, description="Associated source citations")


class EconomicsScenarioResponse(BaseModel):
    id: uuid.UUID
    name: str
    inputs: Dict[str, Any]
    calculation: SameLotComparisonResult
    source_ids: List[str]
    formula_version: str
    is_illustrative: bool
    created_by: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Default Seed Scenarios for immediate client illustration
DEFAULT_SEED_SCENARIOS = [
    {
        "id": "e0000000-0000-0000-0000-000000000001",
        "name": "TechSpec Baseline: Printed Circuit Boards (10kg)",
        "inputs": SameLotInputs(
            material_id="MAT-PCB-01",
            weight_g=10000,
            acquisition_cost_paise=100000,
            current_rate_paise_per_kg=15000,
            current_transport_paise=10000,
            current_handling_paise=5000,
            current_rejection_loss_paise=0,
            current_other_cost_paise=0,
            current_time_hours=3.0,
            current_time_value_paise_per_hour=0,
            platform_rate_paise_per_kg=16000,
            platform_transport_paise=8000,
            platform_handling_paise=5000,
            platform_rejection_loss_paise=0,
            platform_other_cost_paise=0,
            platform_time_hours=1.5,
            platform_time_value_paise_per_hour=0,
            source_reference="docs/23_UNIT_ECONOMICS.md line 15",
            assumptions_note="Illustrative baseline comparison for Delhi-NCR scrap electronics"
        ),
        "source_ids": ["SRC-01"]
    },
    {
        "id": "e0000000-0000-0000-0000-000000000002",
        "name": "Copper Cables: Mechanical Stripping vs Informal Sale (7.35kg)",
        "inputs": SameLotInputs(
            material_id="MAT-CAB-01",
            weight_g=7350,
            acquisition_cost_paise=70000,
            current_rate_paise_per_kg=14250,
            current_transport_paise=5000,
            current_handling_paise=2500,
            current_rejection_loss_paise=0,
            current_other_cost_paise=0,
            current_time_hours=2.0,
            current_time_value_paise_per_hour=0,
            platform_rate_paise_per_kg=15750,
            platform_transport_paise=4000,
            platform_handling_paise=2500,
            platform_rejection_loss_paise=0,
            platform_other_cost_paise=0,
            platform_time_hours=1.0,
            platform_time_value_paise_per_hour=0,
            source_reference="SRC-01 CPCB Market Price Surveys",
            assumptions_note="Intact cable transport to formal dismantler avoiding illegal burning"
        ),
        "source_ids": ["SRC-01"]
    },
    {
        "id": "e0000000-0000-0000-0000-000000000003",
        "name": "High Transport Remote Collector (Negative Platform Benefit)",
        "inputs": SameLotInputs(
            material_id="MAT-PLA-01",
            weight_g=50000,
            acquisition_cost_paise=100000,
            current_rate_paise_per_kg=2500,
            current_transport_paise=3000,
            current_handling_paise=2000,
            current_rejection_loss_paise=0,
            current_other_cost_paise=0,
            current_time_hours=1.0,
            current_time_value_paise_per_hour=0,
            platform_rate_paise_per_kg=2700,
            platform_transport_paise=25000,
            platform_handling_paise=2000,
            platform_rejection_loss_paise=0,
            platform_other_cost_paise=0,
            platform_time_hours=3.0,
            platform_time_value_paise_per_hour=0,
            source_reference="docs/23_UNIT_ECONOMICS.md line 15",
            assumptions_note="Illustrates scenario where high long-distance transport makes formal destination unfavorable"
        ),
        "source_ids": ["SRC-01"]
    }
]


# =============================================================================
# 1. Stateless Same-Lot Calculation Endpoint (R-ECON-01, AT-067)
# =============================================================================

@router.post("/api/v1/economics/calculate", response_model=SameLotComparisonResult)
@router.post("/economics/calculate", response_model=SameLotComparisonResult)
def calculate_economics(inputs: SameLotInputs) -> SameLotComparisonResult:
    """
    Stateless transparent calculation of same-lot current vs. platform scenario.
    Zero side-effects on ledger. Includes sensitivity analysis and explicit caveats.
    """
    return calculate_same_lot_comparison(inputs)


# =============================================================================
# 2. Saved Scenarios Management (R-ECON-01, AT-067)
# =============================================================================

@router.get("/api/v1/economics/scenarios")
@router.get("/economics/scenarios")
def list_scenarios(
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
) -> List[Dict[str, Any]]:
    """
    Retrieve available illustrative scenarios.
    Returns built-in defaults plus user's privately saved scenarios.
    """
    results: List[Dict[str, Any]] = []

    # 1. Add built-in reference scenarios
    for seed in DEFAULT_SEED_SCENARIOS:
        calc = calculate_same_lot_comparison(seed["inputs"])
        results.append({
            "id": seed["id"],
            "name": seed["name"],
            "inputs": seed["inputs"].model_dump(),
            "calculation": calc.model_dump(),
            "source_ids": seed["source_ids"],
            "formula_version": FORMULA_VERSION,
            "is_illustrative": True,
            "is_default": True,
            "created_by": None
        })

    # 2. Add persisted scenarios for current user
    if current_user:
        stmt = select(EconomicsScenario).where(
            or_(
                EconomicsScenario.created_by == current_user.id,
                current_user.role == UserRole.ADMIN.value
            )
        ).order_by(EconomicsScenario.created_at.desc())
        db_scenarios = db.execute(stmt).scalars().all()

        for s in db_scenarios:
            try:
                inputs_obj = SameLotInputs(**s.assumptions_json)
                calc = calculate_same_lot_comparison(inputs_obj)
            except Exception:
                continue

            results.append({
                "id": str(s.id),
                "name": s.name,
                "inputs": s.assumptions_json,
                "calculation": calc.model_dump(),
                "source_ids": s.source_ids,
                "formula_version": s.formula_version,
                "is_illustrative": s.is_illustrative,
                "is_default": False,
                "created_by": str(s.created_by),
                "created_at": s.created_at.isoformat(),
                "updated_at": s.updated_at.isoformat()
            })

    return results


@router.post("/api/v1/economics/scenarios", status_code=status.HTTP_201_CREATED)
@router.post("/economics/scenarios", status_code=status.HTTP_201_CREATED)
def create_scenario(
    payload: CreateScenarioRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Save an illustrative same-lot scenario to the database for administrative review or personal reuse.
    Enforces user ownership and validates scenario calculation.
    """
    calc = calculate_same_lot_comparison(payload.inputs)
    now = datetime.now(timezone.utc)

    scenario = EconomicsScenario(
        id=uuid.uuid4(),
        name=payload.name,
        assumptions_json=payload.inputs.model_dump(),
        source_ids=payload.source_ids,
        formula_version=FORMULA_VERSION,
        is_illustrative=True,
        created_by=current_user.id,
        version=1,
        created_at=now,
        updated_at=now
    )
    db.add(scenario)
    db.commit()
    db.refresh(scenario)

    return {
        "id": str(scenario.id),
        "name": scenario.name,
        "inputs": scenario.assumptions_json,
        "calculation": calc.model_dump(),
        "source_ids": scenario.source_ids,
        "formula_version": scenario.formula_version,
        "is_illustrative": scenario.is_illustrative,
        "created_by": str(scenario.created_by),
        "created_at": scenario.created_at.isoformat(),
        "updated_at": scenario.updated_at.isoformat()
    }


@router.get("/api/v1/economics/scenarios/{id}")
@router.get("/economics/scenarios/{id}")
def get_scenario(
    id: str,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
) -> Dict[str, Any]:
    """Retrieve specific saved or default illustrative scenario."""
    # Check default seed scenarios first
    for seed in DEFAULT_SEED_SCENARIOS:
        if seed["id"] == id:
            calc = calculate_same_lot_comparison(seed["inputs"])
            return {
                "id": seed["id"],
                "name": seed["name"],
                "inputs": seed["inputs"].model_dump(),
                "calculation": calc.model_dump(),
                "source_ids": seed["source_ids"],
                "formula_version": FORMULA_VERSION,
                "is_illustrative": True,
                "is_default": True
            }

    try:
        scenario_uuid = uuid.UUID(id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Scenario not found")

    scenario = db.execute(
        select(EconomicsScenario).where(EconomicsScenario.id == scenario_uuid)
    ).scalar_one_or_none()

    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")

    # Access scoping: only creator or admin can view custom scenario
    if current_user and (scenario.created_by != current_user.id and current_user.role != UserRole.ADMIN.value):
        raise HTTPException(status_code=403, detail="Not authorized to access this scenario")

    inputs_obj = SameLotInputs(**scenario.assumptions_json)
    calc = calculate_same_lot_comparison(inputs_obj)

    return {
        "id": str(scenario.id),
        "name": scenario.name,
        "inputs": scenario.assumptions_json,
        "calculation": calc.model_dump(),
        "source_ids": scenario.source_ids,
        "formula_version": scenario.formula_version,
        "is_illustrative": scenario.is_illustrative,
        "is_default": False,
        "created_by": str(scenario.created_by),
        "created_at": scenario.created_at.isoformat(),
        "updated_at": scenario.updated_at.isoformat()
    }


@router.delete("/api/v1/economics/scenarios/{id}")
@router.delete("/economics/scenarios/{id}")
def delete_scenario(
    id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Delete a user-saved scenario."""
    try:
        scenario_uuid = uuid.UUID(id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Scenario not found")

    scenario = db.execute(
        select(EconomicsScenario).where(EconomicsScenario.id == scenario_uuid)
    ).scalar_one_or_none()

    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")

    if scenario.created_by != current_user.id and current_user.role != UserRole.ADMIN.value:
        raise HTTPException(status_code=403, detail="Not authorized to delete this scenario")

    db.delete(scenario)
    db.commit()

    return {"deleted": True, "id": id}


# =============================================================================
# 3. Platform Sustainability Calculator Endpoint (R-ECON-02, AT-068)
# =============================================================================

@router.post("/api/v1/economics/sustainability", response_model=SustainabilityResult)
@router.post("/economics/sustainability", response_model=SustainabilityResult)
def calculate_sustainability(inputs: SustainabilityInputs) -> SustainabilityResult:
    """
    Stateless calculation of hypothetical downstream platform sustainability.
    Evaluates break-even transaction count without imposing any collector fees.
    """
    return calculate_platform_sustainability(inputs)
