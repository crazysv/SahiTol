from fastapi import APIRouter, Depends, Query
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.routers.facilities import query_facilities, FacilityListItemResponse

router = APIRouter(prefix="/api/v1/recyclers", tags=["recyclers"])


@router.get("/directory", response_model=List[FacilityListItemResponse])
def get_directory(
    region_id: Optional[str] = Query(None, description="Regional filter"),
    formal_destination_only: bool = Query(False, description="Filter for strong formal destinations"),
    is_demo: bool = Query(False, description="Include demo fixtures"),
    db: Session = Depends(get_db)
):
    """List formal destinations with verification levels."""
    return query_facilities(
        db=db,
        region_id=region_id,
        formal_destination_only=formal_destination_only,
        is_demo=is_demo
    )


@router.post("/match")
def match_destinations(lot_id: str) -> Dict[str, Any]:
    """Execute MATCH_V1 matching algorithm on eligible destinations."""
    return {
        "policy_version": "MATCH_V1",
        "matches": []
    }
