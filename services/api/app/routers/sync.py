"""Durable Offline Synchronization Protocol Router.
Implements T014: push per-operation responses, dependency ordering, expected versions,
payload fingerprints (SAHITOL-JCS-1 SHA-256), atomic idempotency storage (sync_operations),
and cursor-based pull deltas with tombstones (sync_changes).
Specifications: docs/17_OFFLINE_SYNC.md, docs/16_API_CONTRACT.md.
Acceptance cases: AT-040, AT-041.
"""
import base64
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Set, Tuple

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field, model_validator
from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.db.models.audit import SyncChange, SyncOperation
from app.db.models.auth import User
from app.db.models.collector import Collector
from app.db.models.lot import Lot, LotImage, MediaObject
from app.db.models.material import Material
from app.db.models.price import PriceObservation
from app.domain.canonical import compute_canonical_hash
from app.security import get_current_user

router = APIRouter(prefix="/api/v1/sync", tags=["sync"])


# --- Cursor Encoding / Decoding ---

def encode_cursor(seq: int) -> str:
    """Encode monotonically increasing sequence to opaque base64 cursor token."""
    raw = f"sahitol_cur_v1:{seq}".encode("utf-8")
    return base64.urlsafe_b64encode(raw).decode("ascii")


def decode_cursor(cursor_str: str) -> int:
    """Decode opaque cursor to integer sequence, raising 410 CURSOR_EXPIRED on corruption."""
    if not cursor_str or cursor_str == "0":
        return 0
    try:
        raw = base64.urlsafe_b64decode(cursor_str.encode("ascii")).decode("utf-8")
        if not raw.startswith("sahitol_cur_v1:"):
            raise ValueError("Invalid cursor format")
        seq_part = raw.split(":", 1)[1]
        seq = int(seq_part)
        if seq < 0:
            raise ValueError("Negative cursor sequence")
        return seq
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail={
                "error": {
                    "code": "CURSOR_EXPIRED",
                    "message": "The sync cursor has expired or is invalid. Perform a full bootstrap.",
                    "details": str(e),
                    "retryable": False
                }
            }
        )


# --- Pydantic Schemas ---

class SyncOperationItem(BaseModel):
    operation_id: Optional[uuid.UUID] = None
    id: Optional[uuid.UUID] = None
    device_id: Optional[str] = None
    entity_type: str
    entity_id: uuid.UUID
    command: Optional[str] = None
    command_type: Optional[str] = None
    expected_version: Optional[int] = None
    base_server_version: Optional[int] = None
    payload: Optional[Dict[str, Any]] = None
    payload_json: Optional[Dict[str, Any]] = None
    payload_sha256: Optional[str] = None
    depends_on: Optional[List[uuid.UUID]] = Field(default_factory=list)
    dependency_operation_ids: Optional[List[uuid.UUID]] = None
    media_ids: Optional[List[uuid.UUID]] = Field(default_factory=list)
    created_at: Optional[datetime] = None

    @model_validator(mode="before")
    @classmethod
    def normalize_fields(cls, data: Any) -> Any:
        if isinstance(data, dict):
            # Normalize operation_id from id
            if "operation_id" not in data and "id" in data:
                data["operation_id"] = data["id"]
            elif "id" not in data and "operation_id" in data:
                data["id"] = data["operation_id"]
            # Normalize command from command_type
            if "command" not in data and "command_type" in data:
                data["command"] = data["command_type"]
            # Normalize expected_version from base_server_version
            if "expected_version" not in data and "base_server_version" in data:
                data["expected_version"] = data["base_server_version"]
            # Normalize payload from payload_json
            if "payload" not in data and "payload_json" in data:
                data["payload"] = data["payload_json"]
            elif "payload" not in data and "payload_json" not in data:
                data["payload"] = {}
            # Normalize depends_on from dependency_operation_ids
            if ("depends_on" not in data or data["depends_on"] is None) and "dependency_operation_ids" in data:
                data["depends_on"] = data["dependency_operation_ids"]
        return data


class SyncBatchRequest(BaseModel):
    device_id: Optional[str] = "collector-device"
    batch_id: Optional[str] = None
    operations: List[SyncOperationItem] = Field(default_factory=list)


class OperationResult(BaseModel):
    operation_id: uuid.UUID
    outcome: str  # APPLIED, ALREADY_APPLIED, RETRY, AUTH_REQUIRED, CONFLICT, REJECTED, DEPENDENCY_PENDING
    entity_id: Optional[uuid.UUID] = None
    server_version: Optional[int] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[Dict[str, Any]] = None
    retry_after_seconds: Optional[int] = None


class SyncMeta(BaseModel):
    request_id: str
    server_time: datetime
    schema_version: str = "v1.0"
    next_cursor: Optional[str] = None
    has_more: Optional[bool] = None


class SyncBatchResponseData(BaseModel):
    results: List[OperationResult]


class SyncBatchResponse(BaseModel):
    data: SyncBatchResponseData
    meta: SyncMeta


class SyncChangeItem(BaseModel):
    sequence: int
    entity_type: str
    entity_id: str
    entity_version: int
    operation: str  # UPSERT, DELETE
    data: Optional[Dict[str, Any]] = None
    created_at: datetime


class SyncChangesResponseData(BaseModel):
    changes: List[SyncChangeItem]


class SyncChangesResponse(BaseModel):
    data: SyncChangesResponseData
    meta: SyncMeta


# --- Domain Command Dispatcher ---

def execute_domain_operation(
    db: Session,
    current_user: User,
    entity_type: str,
    entity_id: uuid.UUID,
    command: str,
    expected_version: Optional[int],
    payload: Dict[str, Any],
    media_ids: Optional[List[uuid.UUID]],
    is_demo: bool,
) -> Tuple[str, Optional[int], Optional[Dict[str, Any]], Optional[Dict[str, Any]]]:
    """Execute domain command.

    Returns: (outcome, server_version, result_data, error_dict)
    """
    now = datetime.now(timezone.utc)

    # 1. LOT ENTITY OPERATIONS
    if entity_type == "LOT":
        if command in ("CREATE_DRAFT", "CREATE"):
            collector_profile = db.execute(
                select(Collector).where(Collector.user_id == current_user.id)
            ).scalar_one_or_none()
            if not collector_profile and current_user.role != "ADMIN":
                return "REJECTED", None, None, {
                    "code": "COLLECTOR_PROFILE_REQUIRED",
                    "message": "A collector profile is required before creating lots."
                }
            collector_id_raw = payload.get("collector_id")
            if collector_id_raw:
                try:
                    collector_uuid = uuid.UUID(str(collector_id_raw))
                except ValueError:
                    return "REJECTED", None, None, {"code": "INVALID_COLLECTOR_ID", "message": "Invalid collector UUID"}
                if current_user.role != "ADMIN" and collector_uuid != collector_profile.id:
                    return "REJECTED", None, None, {"code": "FORBIDDEN", "message": "Cannot create lot for another collector"}
            else:
                # `lots.collector_id` references the profile, while the access
                # token identifies the user.  These UUIDs are intentionally
                # distinct in production and must not be interchanged.
                collector_uuid = collector_profile.id if collector_profile else current_user.id

            est_weight = payload.get("estimated_weight_g")
            if est_weight is not None and est_weight <= 0:
                return "REJECTED", None, None, {"code": "INVALID_WEIGHT", "message": "Estimated weight must be positive integer grams"}

            mat_id = payload.get("material_id")
            mat_route = payload.get("regulatory_route")
            if mat_id:
                material = db.execute(select(Material).where(Material.id == mat_id)).scalar_one_or_none()
                if not material:
                    return "REJECTED", None, None, {"code": "INVALID_MATERIAL", "message": f"Material ID '{mat_id}' not found in curated catalog"}
                if not mat_route:
                    mat_route = material.default_route

            # Idempotent existing lot check
            existing_lot = db.execute(select(Lot).where(Lot.id == entity_id)).scalar_one_or_none()
            if existing_lot:
                return "APPLIED", existing_lot.version, {
                    "id": str(existing_lot.id),
                    "status": existing_lot.status,
                    "version": existing_lot.version
                }, None

            lot = Lot(
                id=entity_id,
                collector_id=collector_uuid,
                material_id=mat_id,
                material_context=payload.get("material_context"),
                regulatory_route=mat_route,
                estimated_weight_g=est_weight,
                condition=payload.get("condition"),
                description=payload.get("description"),
                status="DRAFT",
                version=1,
                origin_class="PLATFORM_GENERATED",
                source_kind="PLATFORM_OBSERVATION",
                is_demo=is_demo,
                created_at=now,
                updated_at=now,
            )
            db.add(lot)

            # Link any media objects
            effective_media = media_ids or payload.get("media_ids") or []
            for idx, mid in enumerate(effective_media):
                mid_uuid = mid if isinstance(mid, uuid.UUID) else uuid.UUID(str(mid))
                db.add(LotImage(
                    lot_id=lot.id,
                    media_id=mid_uuid,
                    order_index=idx,
                    purpose="PHOTO",
                    captured_at=now
                ))

            db.flush()
            return "APPLIED", 1, {
                "id": str(lot.id),
                "status": lot.status,
                "material_id": lot.material_id,
                "estimated_weight_g": lot.estimated_weight_g,
                "condition": lot.condition,
                "version": 1
            }, None

        elif command in ("UPDATE_DRAFT", "UPDATE"):
            lot = db.execute(select(Lot).where(Lot.id == entity_id)).scalar_one_or_none()
            if not lot:
                return "REJECTED", None, None, {"code": "NOT_FOUND", "message": f"Lot '{entity_id}' not found"}

            if lot.status != "DRAFT":
                return "CONFLICT", lot.version, None, {
                    "code": "IMMUTABLE_AGREEMENT",
                    "message": f"Cannot edit lot with status '{lot.status}'"
                }

            if expected_version is not None and lot.version != expected_version:
                return "CONFLICT", lot.version, None, {
                    "code": "VERSION_CONFLICT",
                    "message": f"Expected version {expected_version} does not match server version {lot.version}",
                    "details": {"current_version": lot.version, "expected_version": expected_version}
                }

            if "estimated_weight_g" in payload:
                w = payload["estimated_weight_g"]
                if w is not None and w <= 0:
                    return "REJECTED", None, None, {"code": "INVALID_WEIGHT", "message": "Estimated weight must be positive integer grams"}
                lot.estimated_weight_g = w

            if "condition" in payload:
                lot.condition = payload["condition"]
            if "description" in payload:
                lot.description = payload["description"]
            if "material_id" in payload and payload["material_id"]:
                mat = db.execute(select(Material).where(Material.id == payload["material_id"])).scalar_one_or_none()
                if not mat:
                    return "REJECTED", None, None, {"code": "INVALID_MATERIAL", "message": f"Material ID '{payload['material_id']}' not found in curated catalog"}
                lot.material_id = payload["material_id"]
                if "regulatory_route" in payload and payload["regulatory_route"]:
                    lot.regulatory_route = payload["regulatory_route"]
                else:
                    lot.regulatory_route = mat.default_route

            lot.version += 1
            lot.updated_at = now
            db.flush()
            return "APPLIED", lot.version, {
                "id": str(lot.id),
                "status": lot.status,
                "material_id": lot.material_id,
                "estimated_weight_g": lot.estimated_weight_g,
                "condition": lot.condition,
                "version": lot.version
            }, None

        elif command == "COLLECT_LOT":
            lot = db.execute(select(Lot).where(Lot.id == entity_id)).scalar_one_or_none()
            if not lot:
                return "REJECTED", None, None, {"code": "NOT_FOUND", "message": f"Lot '{entity_id}' not found"}

            if expected_version is not None and lot.version != expected_version:
                return "CONFLICT", lot.version, None, {
                    "code": "VERSION_CONFLICT",
                    "message": f"Expected version {expected_version} does not match server version {lot.version}",
                    "details": {"current_version": lot.version, "expected_version": expected_version}
                }

            lot.status = "COLLECTED"
            lot.version += 1
            lot.updated_at = now
            db.flush()
            return "APPLIED", lot.version, {"id": str(lot.id), "status": lot.status, "version": lot.version}, None

        elif command == "LIST_LOT":
            lot = db.execute(select(Lot).where(Lot.id == entity_id)).scalar_one_or_none()
            if not lot:
                return "REJECTED", None, None, {"code": "NOT_FOUND", "message": f"Lot '{entity_id}' not found"}

            if expected_version is not None and lot.version != expected_version:
                return "CONFLICT", lot.version, None, {
                    "code": "VERSION_CONFLICT",
                    "message": f"Expected version {expected_version} does not match server version {lot.version}",
                    "details": {"current_version": lot.version, "expected_version": expected_version}
                }

            lot.status = "LISTED"
            lot.version += 1
            lot.updated_at = now
            db.flush()
            return "APPLIED", lot.version, {"id": str(lot.id), "status": lot.status, "version": lot.version}, None

        elif command == "CANCEL_LOT":
            lot = db.execute(select(Lot).where(Lot.id == entity_id)).scalar_one_or_none()
            if not lot:
                return "REJECTED", None, None, {"code": "NOT_FOUND", "message": f"Lot '{entity_id}' not found"}

            if expected_version is not None and lot.version != expected_version:
                return "CONFLICT", lot.version, None, {
                    "code": "VERSION_CONFLICT",
                    "message": f"Expected version {expected_version} does not match server version {lot.version}",
                    "details": {"current_version": lot.version, "expected_version": expected_version}
                }

            lot.status = "CANCELLED"
            lot.version += 1
            lot.updated_at = now
            db.flush()
            return "APPLIED", lot.version, {"id": str(lot.id), "status": lot.status, "version": lot.version}, None

        elif command == "DELETE":
            lot = db.execute(select(Lot).where(Lot.id == entity_id)).scalar_one_or_none()
            if not lot:
                return "REJECTED", None, None, {"code": "NOT_FOUND", "message": f"Lot '{entity_id}' not found"}

            lot.status = "CANCELLED"
            lot.version += 1
            lot.updated_at = now
            db.flush()
            return "APPLIED", lot.version, {"id": str(lot.id), "status": "DELETED", "version": lot.version}, None

    # 2. PRICE_OBSERVATION ENTITY OPERATIONS
    elif entity_type == "PRICE_OBSERVATION":
        if command in ("CREATE_OBSERVATION", "CREATE"):
            mat_id = payload.get("material_id")
            rate = payload.get("rate_paise_per_unit")
            if not mat_id or not rate or rate <= 0:
                return "REJECTED", None, None, {
                    "code": "INVALID_PRICE_OBSERVATION",
                    "message": "material_id and positive rate_paise_per_unit are required"
                }

            mat = db.execute(select(Material).where(Material.id == mat_id)).scalar_one_or_none()
            if not mat:
                return "REJECTED", None, None, {"code": "INVALID_MATERIAL", "message": f"Material ID '{mat_id}' not found in catalog"}

            obs_raw = payload.get("observed_at")
            if obs_raw:
                if isinstance(obs_raw, str):
                    obs_dt = datetime.fromisoformat(obs_raw.replace("Z", "+00:00"))
                else:
                    obs_dt = obs_raw
            else:
                obs_dt = now

            obs = PriceObservation(
                id=entity_id,
                material_id=mat_id,
                subcategory_id=payload.get("subcategory_id"),
                region_id=payload.get("region_id", "DELHI_NCR"),
                condition=payload.get("condition"),
                rate_paise_per_unit=rate,
                unit=payload.get("unit", "kg"),
                price_kind=payload.get("price_kind", "BUY"),
                observed_at=obs_dt,
                source_id=payload.get("source_id", "SRC-03"),
                review_status="PENDING_REVIEW",
                origin_class="PLATFORM_OBSERVATION",
                source_kind="COLLECTOR_REPORT",
                is_demo=is_demo,
                created_at=now
            )
            db.add(obs)
            db.flush()
            return "APPLIED", 1, {
                "id": str(obs.id),
                "material_id": obs.material_id,
                "rate_paise_per_unit": obs.rate_paise_per_unit,
                "review_status": obs.review_status
            }, None

    # 3. MEDIA ENTITY OPERATIONS
    elif entity_type == "MEDIA":
        if command in ("ATTACH_MEDIA", "CREATE"):
            return "APPLIED", 1, {"id": str(entity_id), "status": "ATTACHED"}, None

    # Extensible generic fallback
    return "REJECTED", None, None, {
        "code": "UNSUPPORTED_COMMAND",
        "message": f"Command '{command}' for entity type '{entity_type}' is not supported"
    }


# --- Push Handlers: POST /api/v1/sync/batch and POST /api/v1/sync/push ---

@router.post("/batch", response_model=SyncBatchResponse)
@router.post("/push", response_model=SyncBatchResponse)
def sync_batch(
    req: SyncBatchRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Process batched outbox operations with topological ordering, expected versions,
    canonical payload fingerprinting, and atomic idempotency storage.
    """
    if len(req.operations) > 50:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "error": {
                    "code": "BATCH_SIZE_EXCEEDED",
                    "message": "Sync batch exceeds maximum limit of 50 operations.",
                    "details": {"max_limit": 50, "received_count": len(req.operations)},
                    "retryable": False
                }
            }
        )

    effective_device_id = req.device_id or "collector-device"
    results: List[OperationResult] = []
    applied_in_batch: Set[uuid.UUID] = set()
    failed_in_batch: Set[uuid.UUID] = set()

    for op in req.operations:
        op_id = op.operation_id or op.id
        if not op_id:
            results.append(OperationResult(
                operation_id=uuid.uuid4(),
                outcome="REJECTED",
                error={"code": "MISSING_OPERATION_ID", "message": "operation_id is required"}
            ))
            continue

        payload = op.payload or {}
        canonical_hash = compute_canonical_hash(payload)

        # 1. Payload Hash Verification (if client declared payload_sha256)
        if op.payload_sha256 and op.payload_sha256.lower() != canonical_hash.lower():
            failed_in_batch.add(op_id)
            results.append(OperationResult(
                operation_id=op_id,
                outcome="REJECTED",
                entity_id=op.entity_id,
                error={
                    "code": "PAYLOAD_HASH_MISMATCH",
                    "message": "Declared payload_sha256 does not match canonical payload hash",
                    "details": {"canonical_hash": canonical_hash, "received_hash": op.payload_sha256}
                }
            ))
            continue

        # 2. Check Idempotency & existing operation in DB
        existing_op = db.execute(
            select(SyncOperation).where(SyncOperation.operation_id == op_id)
        ).scalar_one_or_none()

        if existing_op:
            # Verify actor ownership
            if existing_op.actor_id != current_user.id and current_user.role != "ADMIN":
                failed_in_batch.add(op_id)
                results.append(OperationResult(
                    operation_id=op_id,
                    outcome="CONFLICT",
                    entity_id=op.entity_id,
                    error={
                        "code": "AUTH_FORBIDDEN",
                        "message": "Cannot replay operation submitted by another actor."
                    }
                ))
                continue

            # Verify identical payload fingerprint
            if existing_op.payload_hash.lower() != canonical_hash.lower():
                failed_in_batch.add(op_id)
                results.append(OperationResult(
                    operation_id=op_id,
                    outcome="CONFLICT",
                    entity_id=op.entity_id,
                    error={
                        "code": "IDEMPOTENCY_KEY_REUSED",
                        "message": "Operation ID reused with a different payload.",
                        "details": {"original_hash": existing_op.payload_hash, "current_hash": canonical_hash}
                    }
                ))
                continue

            # Idempotent replay: return cached durable outcome without producing a second domain effect
            applied_in_batch.add(op_id)
            cached_result = existing_op.response_json.get("result")
            cached_version = existing_op.response_json.get("server_version")
            results.append(OperationResult(
                operation_id=op_id,
                outcome="ALREADY_APPLIED",
                entity_id=existing_op.entity_id or op.entity_id,
                server_version=cached_version,
                result=cached_result
            ))
            continue

        # 3. Check Dependencies
        deps_unsatisfied = False
        dep_error = None
        for dep_id in (op.depends_on or []):
            if dep_id in applied_in_batch:
                continue
            if dep_id in failed_in_batch:
                deps_unsatisfied = True
                dep_error = {
                    "code": "DEPENDENCY_FAILED",
                    "message": f"Dependency operation {dep_id} failed in this batch."
                }
                break
            # Check DB for previously committed dependency
            db_dep = db.execute(
                select(SyncOperation).where(
                    SyncOperation.operation_id == dep_id,
                    SyncOperation.state == "COMMITTED"
                )
            ).scalar_one_or_none()
            if not db_dep:
                deps_unsatisfied = True
                dep_error = {
                    "code": "DEPENDENCY_NOT_SATISFIED",
                    "message": f"Required dependency operation {dep_id} has not been committed."
                }
                break

        if deps_unsatisfied:
            failed_in_batch.add(op_id)
            results.append(OperationResult(
                operation_id=op_id,
                outcome="DEPENDENCY_PENDING",
                entity_id=op.entity_id,
                error=dep_error
            ))
            continue

        # 4. Execute domain command within nested savepoint
        op_result: Optional[OperationResult] = None
        try:
            with db.begin_nested():
                cmd = (op.command or "CREATE").upper()
                ent_type = op.entity_type.upper()

                res_outcome, res_version, res_data, res_err = execute_domain_operation(
                    db=db,
                    current_user=current_user,
                    entity_type=ent_type,
                    entity_id=op.entity_id,
                    command=cmd,
                    expected_version=op.expected_version,
                    payload=payload,
                    media_ids=op.media_ids,
                    is_demo=current_user.is_demo
                )

                if res_outcome == "APPLIED":
                    # Record SyncOperation row
                    sync_op = SyncOperation(
                        actor_id=current_user.id,
                        device_id=op.device_id or effective_device_id,
                        operation_id=op_id,
                        payload_hash=canonical_hash,
                        state="COMMITTED",
                        response_json={"result": res_data, "server_version": res_version},
                        committed_at=datetime.now(timezone.utc),
                        entity_id=op.entity_id
                    )
                    db.add(sync_op)

                    # Record SyncChange row for pull deltas
                    visibility = f"collector:{current_user.id}" if ent_type == "LOT" else "PUBLIC"
                    sync_change = SyncChange(
                        entity_type=ent_type,
                        entity_id=op.entity_id,
                        entity_version=res_version or 1,
                        visibility_scope=visibility,
                        deleted_at=datetime.now(timezone.utc) if cmd == "DELETE" else None,
                        created_at=datetime.now(timezone.utc)
                    )
                    db.add(sync_change)
                    db.flush()

                    applied_in_batch.add(op_id)
                    op_result = OperationResult(
                        operation_id=op_id,
                        outcome="APPLIED",
                        entity_id=op.entity_id,
                        server_version=res_version,
                        result=res_data
                    )
                else:
                    failed_in_batch.add(op_id)
                    op_result = OperationResult(
                        operation_id=op_id,
                        outcome=res_outcome,
                        entity_id=op.entity_id,
                        server_version=res_version,
                        error=res_err
                    )

        except Exception as e:
            failed_in_batch.add(op_id)
            op_result = OperationResult(
                operation_id=op_id,
                outcome="REJECTED",
                entity_id=op.entity_id,
                error={"code": "EXECUTION_ERROR", "message": str(e)}
            )

        if op_result:
            results.append(op_result)

    db.commit()

    return SyncBatchResponse(
        data=SyncBatchResponseData(results=results),
        meta=SyncMeta(
            request_id=str(uuid.uuid4()),
            server_time=datetime.now(timezone.utc),
            schema_version="v1.0"
        )
    )


# --- Pull Handlers: GET /api/v1/sync/changes and GET /api/v1/sync/pull ---

@router.get("/changes", response_model=SyncChangesResponse)
@router.get("/pull", response_model=SyncChangesResponse)
def get_sync_changes(
    cursor: str = Query("0", description="Opaque monotonic cursor token from previous sync"),
    limit: int = Query(200, ge=1, le=200, description="Page limit (default/max 200)"),
    entity_type: Optional[str] = Query(None, description="Optional entity type filter"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve incremental deltas and tombstones since the provided cursor, scoped to authenticated user."""
    seq = decode_cursor(cursor)

    stmt = select(SyncChange).where(SyncChange.sequence > seq)

    # Scoping by user role & identity
    if current_user.role != "ADMIN":
        allowed_scopes = ["PUBLIC", "REFERENCE", f"user:{current_user.id}", f"collector:{current_user.id}"]
        stmt = stmt.where(SyncChange.visibility_scope.in_(allowed_scopes))

    if entity_type:
        stmt = stmt.where(SyncChange.entity_type == entity_type.upper())

    stmt = stmt.order_by(SyncChange.sequence.asc()).limit(limit + 1)
    changes = db.execute(stmt).scalars().all()

    has_more = len(changes) > limit
    returned_changes = changes[:limit]

    items: List[SyncChangeItem] = []
    for ch in returned_changes:
        if ch.deleted_at is not None:
            items.append(SyncChangeItem(
                sequence=ch.sequence,
                entity_type=ch.entity_type,
                entity_id=str(ch.entity_id),
                entity_version=ch.entity_version,
                operation="DELETE",
                data=None,  # Tombstone
                created_at=ch.created_at
            ))
        else:
            # Resolve entity projection
            entity_data: Dict[str, Any] = {"entity_id": str(ch.entity_id), "version": ch.entity_version}
            if ch.entity_type == "LOT":
                lot = db.execute(select(Lot).where(Lot.id == ch.entity_id)).scalar_one_or_none()
                if lot:
                    entity_data = {
                        "id": str(lot.id),
                        "collector_id": str(lot.collector_id),
                        "material_id": lot.material_id,
                        "regulatory_route": lot.regulatory_route,
                        "estimated_weight_g": lot.estimated_weight_g,
                        "condition": lot.condition,
                        "status": lot.status,
                        "version": lot.version,
                        "is_demo": lot.is_demo,
                        "created_at": lot.created_at.isoformat() if lot.created_at else None,
                        "updated_at": lot.updated_at.isoformat() if lot.updated_at else None,
                    }
            elif ch.entity_type == "PRICE_OBSERVATION":
                obs = db.execute(select(PriceObservation).where(PriceObservation.id == ch.entity_id)).scalar_one_or_none()
                if obs:
                    entity_data = {
                        "id": str(obs.id),
                        "material_id": obs.material_id,
                        "region_id": obs.region_id,
                        "rate_paise_per_unit": obs.rate_paise_per_unit,
                        "unit": obs.unit,
                        "price_kind": obs.price_kind,
                        "review_status": obs.review_status,
                        "observed_at": obs.observed_at.isoformat() if obs.observed_at else None,
                    }

            items.append(SyncChangeItem(
                sequence=ch.sequence,
                entity_type=ch.entity_type,
                entity_id=str(ch.entity_id),
                entity_version=ch.entity_version,
                operation="UPSERT",
                data=entity_data,
                created_at=ch.created_at
            ))

    next_seq = returned_changes[-1].sequence if returned_changes else seq
    next_cursor = encode_cursor(next_seq)

    return SyncChangesResponse(
        data=SyncChangesResponseData(changes=items),
        meta=SyncMeta(
            request_id=str(uuid.uuid4()),
            server_time=datetime.now(timezone.utc),
            schema_version="v1.0",
            next_cursor=next_cursor,
            has_more=has_more
        )
    )
