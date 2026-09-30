"""Materials taxonomy, language aliases, and contextual safety guides router."""
import re
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.db.session import get_db
from app.db.models.material import MaterialCategory, Material, MaterialAlias, SafetyGuide

router = APIRouter(prefix="/api/v1/materials", tags=["materials"])
safety_router = APIRouter(prefix="/api/v1/safety-guides", tags=["safety-guides"])


def normalize_term(term: str) -> str:
    """Normalize search term by stripping punctuation and collapsing whitespace."""
    term = term.strip().lower()
    # Replace punctuation / special characters with space
    term = re.sub(r"[^\w\s\u0900-\u097F]", " ", term)
    term = re.sub(r"\s+", " ", term).strip()
    return term


# Schemas
class CategoryResponse(BaseModel):
    id: str
    code: str
    label_key: str
    display_order: int
    active: bool


class AliasResponse(BaseModel):
    language: str
    local_term: str
    normalized_term: str


class SafetyGuideSummary(BaseModel):
    id: str
    route: str
    text_key: str
    icon_asset_ref: str
    image_asset_ref: Optional[str] = None
    audio_keys: Optional[Dict[str, str]] = None
    version: str


class MaterialSummary(BaseModel):
    id: str
    category_id: str
    subcategory_code: str
    description_key: str
    condition_options: List[str]
    allowed_units: str
    default_route: str
    route_requires_context: bool
    safety_guide_ids: List[str]
    active: bool
    aliases: List[AliasResponse] = []


class MaterialDetail(MaterialSummary):
    safety_guides: List[SafetyGuideSummary] = []


class SearchMatch(BaseModel):
    material: MaterialSummary
    matched_alias: AliasResponse
    exact_match: bool


# Endpoints
@router.get("/categories", response_model=List[CategoryResponse])
def list_categories(
    active_only: bool = True,
    db: Session = Depends(get_db)
):
    """List all material categories ordered by display_order."""
    query = select(MaterialCategory).order_by(MaterialCategory.display_order)
    if active_only:
        query = query.where(MaterialCategory.active == True)
    categories = db.execute(query).scalars().all()
    return [
        CategoryResponse(
            id=cat.id,
            code=cat.code,
            label_key=cat.label_key,
            display_order=cat.display_order,
            active=cat.active,
        )
        for cat in categories
    ]


@router.get("/search", response_model=List[SearchMatch])
def search_materials_by_alias(
    q: str = Query(..., min_length=1, description="Term to resolve (English, Hindi, or Marathi)"),
    language: Optional[str] = Query(None, description="Optional language filter (en, hi, mr)"),
    db: Session = Depends(get_db)
):
    """Resolve a colloquial or formal material name / alias to stable material IDs."""
    norm_query = normalize_term(q)
    if not norm_query:
        return []

    # Query matching aliases
    alias_stmt = select(MaterialAlias).join(Material, MaterialAlias.material_id == Material.id)
    if language:
        alias_stmt = alias_stmt.where(MaterialAlias.language == language)

    # First attempt exact normalized term match
    exact_stmt = alias_stmt.where(MaterialAlias.normalized_term == norm_query)
    exact_matches = db.execute(exact_stmt).scalars().all()

    results: List[SearchMatch] = []
    seen_materials = set()

    for alias in exact_matches:
        mat = alias.material
        if mat.id not in seen_materials:
            seen_materials.add(mat.id)
            mat_aliases = [
                AliasResponse(language=a.language, local_term=a.local_term, normalized_term=a.normalized_term)
                for a in mat.aliases
            ]
            results.append(SearchMatch(
                material=MaterialSummary(
                    id=mat.id,
                    category_id=mat.category_id,
                    subcategory_code=mat.subcategory_code,
                    description_key=mat.description_key,
                    condition_options=mat.condition_options or [],
                    allowed_units=mat.allowed_units,
                    default_route=mat.default_route,
                    route_requires_context=mat.route_requires_context,
                    safety_guide_ids=mat.safety_guide_ids or [],
                    active=mat.active,
                    aliases=mat_aliases,
                ),
                matched_alias=AliasResponse(
                    language=alias.language,
                    local_term=alias.local_term,
                    normalized_term=alias.normalized_term,
                ),
                exact_match=True
            ))

    # If no exact match or partial search, query contains
    if not results:
        partial_stmt = alias_stmt.where(MaterialAlias.normalized_term.contains(norm_query))
        partial_matches = db.execute(partial_stmt).scalars().all()
        for alias in partial_matches:
            mat = alias.material
            if mat.id not in seen_materials:
                seen_materials.add(mat.id)
                mat_aliases = [
                    AliasResponse(language=a.language, local_term=a.local_term, normalized_term=a.normalized_term)
                    for a in mat.aliases
                ]
                results.append(SearchMatch(
                    material=MaterialSummary(
                        id=mat.id,
                        category_id=mat.category_id,
                        subcategory_code=mat.subcategory_code,
                        description_key=mat.description_key,
                        condition_options=mat.condition_options or [],
                        allowed_units=mat.allowed_units,
                        default_route=mat.default_route,
                        route_requires_context=mat.route_requires_context,
                        safety_guide_ids=mat.safety_guide_ids or [],
                        active=mat.active,
                        aliases=mat_aliases,
                    ),
                    matched_alias=AliasResponse(
                        language=alias.language,
                        local_term=alias.local_term,
                        normalized_term=alias.normalized_term,
                    ),
                    exact_match=False
                ))

    return results


@router.get("", response_model=List[MaterialSummary])
def list_materials(
    category_id: Optional[str] = Query(None, description="Filter by category ID"),
    route: Optional[str] = Query(None, description="Filter by default regulatory route"),
    language: Optional[str] = Query(None, description="Filter aliases to specific language"),
    active_only: bool = True,
    db: Session = Depends(get_db)
):
    """List materials with optional filters, returning aliases and safety guides."""
    stmt = select(Material)
    if active_only:
        stmt = stmt.where(Material.active == True)
    if category_id:
        stmt = stmt.where(Material.category_id == category_id)
    if route:
        stmt = stmt.where(Material.default_route == route)

    materials = db.execute(stmt).scalars().all()
    results = []
    for mat in materials:
        aliases = [
            AliasResponse(language=a.language, local_term=a.local_term, normalized_term=a.normalized_term)
            for a in mat.aliases
            if not language or a.language == language
        ]
        results.append(MaterialSummary(
            id=mat.id,
            category_id=mat.category_id,
            subcategory_code=mat.subcategory_code,
            description_key=mat.description_key,
            condition_options=mat.condition_options or [],
            allowed_units=mat.allowed_units,
            default_route=mat.default_route,
            route_requires_context=mat.route_requires_context,
            safety_guide_ids=mat.safety_guide_ids or [],
            active=mat.active,
            aliases=aliases,
        ))
    return results


@router.get("/{material_id}", response_model=MaterialDetail)
def get_material(
    material_id: str,
    db: Session = Depends(get_db)
):
    """Retrieve full material details by ID, including embedded safety guides."""
    mat = db.execute(select(Material).where(Material.id == material_id)).scalar_one_or_none()
    if not mat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Material '{material_id}' not found"
        )

    aliases = [
        AliasResponse(language=a.language, local_term=a.local_term, normalized_term=a.normalized_term)
        for a in mat.aliases
    ]

    # Fetch safety guides
    safety_guides = []
    if mat.safety_guide_ids:
        guides = db.execute(
            select(SafetyGuide).where(SafetyGuide.id.in_(mat.safety_guide_ids))
        ).scalars().all()
        for g in guides:
            safety_guides.append(SafetyGuideSummary(
                id=g.id,
                route=g.route,
                text_key=g.text_key,
                icon_asset_ref=g.icon_asset_ref,
                image_asset_ref=g.image_asset_ref,
                audio_keys=g.audio_keys,
                version=g.version
            ))

    return MaterialDetail(
        id=mat.id,
        category_id=mat.category_id,
        subcategory_code=mat.subcategory_code,
        description_key=mat.description_key,
        condition_options=mat.condition_options or [],
        allowed_units=mat.allowed_units,
        default_route=mat.default_route,
        route_requires_context=mat.route_requires_context,
        safety_guide_ids=mat.safety_guide_ids or [],
        active=mat.active,
        aliases=aliases,
        safety_guides=safety_guides,
    )


# Safety Guides Endpoints
@safety_router.get("", response_model=List[SafetyGuideSummary])
def list_safety_guides(
    route: Optional[str] = Query(None, description="Filter by regulatory route"),
    material_id: Optional[str] = Query(None, description="Filter by associated material ID"),
    db: Session = Depends(get_db)
):
    """List approved safety guides with optional route or material filters."""
    stmt = select(SafetyGuide).where(SafetyGuide.review_status == "APPROVED")
    if route:
        stmt = stmt.where(SafetyGuide.route == route)
    guides = db.execute(stmt).scalars().all()

    if material_id:
        guides = [g for g in guides if material_id in (g.material_ids or [])]

    return [
        SafetyGuideSummary(
            id=g.id,
            route=g.route,
            text_key=g.text_key,
            icon_asset_ref=g.icon_asset_ref,
            image_asset_ref=g.image_asset_ref,
            audio_keys=g.audio_keys,
            version=g.version
        )
        for g in guides
    ]


@safety_router.get("/{guide_id}", response_model=SafetyGuideSummary)
def get_safety_guide(
    guide_id: str,
    db: Session = Depends(get_db)
):
    """Retrieve a single safety guide by ID."""
    guide = db.execute(select(SafetyGuide).where(SafetyGuide.id == guide_id)).scalar_one_or_none()
    if not guide:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Safety guide '{guide_id}' not found"
        )
    return SafetyGuideSummary(
        id=guide.id,
        route=guide.route,
        text_key=guide.text_key,
        icon_asset_ref=guide.icon_asset_ref,
        image_asset_ref=guide.image_asset_ref,
        audio_keys=guide.audio_keys,
        version=guide.version
    )
