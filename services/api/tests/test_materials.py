"""Tests for material taxonomy, multilingual language aliases, safety guides, and lot draft linkage."""
import pytest
import uuid
from fastapi.testclient import TestClient

from app.main import app
from app.db.session import get_db
from app.db.models.collector import Collector
from app.db.models.auth import User
from app.db.models.material import Material, MaterialCategory, MaterialAlias, SafetyGuide
from app.db.seeds.materials import seed_materials
from app.security import create_access_token
from tests.test_db import TestingSessionLocal, override_get_db


@pytest.fixture(scope="module", autouse=True)
def setup_materials_database():
    """Seed test database with materials, categories, safety guides, and aliases."""
    app.dependency_overrides[get_db] = override_get_db
    with TestingSessionLocal() as session:
        seed_materials(session)
    yield


@pytest.fixture
def client():
    return TestClient(app)


def test_categories_listing(client):
    """Test listing of all 11 material categories in display order."""
    response = client.get("/api/v1/materials/categories")
    assert response.status_code == 200
    categories = response.json()
    assert len(categories) == 11
    cat_ids = [c["id"] for c in categories]
    expected_categories = [
        "PCB", "BATTERY", "CRT", "LCD", "CABLES",
        "MOTORS", "PLASTICS", "METALS", "MIXED_ELECTRONICS",
        "OTHER", "UNKNOWN"
    ]
    for exp in expected_categories:
        assert exp in cat_ids

    # Verify display order
    orders = [c["display_order"] for c in categories]
    assert orders == sorted(orders)


def test_complete_material_coverage(client):
    """Verify every required material is present in the curated catalog."""
    response = client.get("/api/v1/materials")
    assert response.status_code == 200
    materials = response.json()
    mat_ids = {m["id"]: m for m in materials}

    # CRT, LCD, PCB, cable, battery, motor/magnet, mixed plastics, mixed electronics, metals, OTHER, UNKNOWN
    required_ids = [
        "MAT-PCB-01",  # High-grade motherboard / server PCB
        "MAT-PCB-02",  # Low-grade appliance board
        "MAT-BAT-01",  # Lead-acid battery
        "MAT-BAT-02",  # Lithium-ion battery
        "MAT-BAT-03",  # Other battery chemistries
        "MAT-BAT-04",  # Unknown chemistry battery
        "MAT-CRT-01",  # CRT monitor glass tube
        "MAT-LCD-01",  # LCD / LED flat panel
        "MAT-CAB-01",  # Copper cable
        "MAT-CAB-02",  # Aluminum cable
        "MAT-MOT-01",  # Electric motor
        "MAT-MOT-02",  # Compressor & magnets
        "MAT-PLA-01",  # Rigid e-waste plastics (ABS/HIPS)
        "MAT-PLA-02",  # General mixed plastics
        "MAT-MET-01",  # Scrap copper
        "MAT-MET-02",  # Scrap aluminum
        "MAT-MET-03",  # Iron & steel scrap
        "MAT-MIX-01",  # Mixed IT equipment
        "MAT-MIX-02",  # Small household appliances
        "MAT-OTH-01",  # Other recyclables
        "MAT-UNK-01",  # Unidentified scrap
    ]
    for req_id in required_ids:
        assert req_id in mat_ids, f"Required material {req_id} missing from catalog"
        mat = mat_ids[req_id]
        assert len(mat["condition_options"]) > 0
        assert mat["allowed_units"]
        assert len(mat["aliases"]) > 0


def test_provenance_dependent_routing(client):
    """Test provenance-dependent regulatory routes for plastics, batteries, and hazardous waste."""
    # 1. Rigid E-Waste Plastics (contains brominated flame retardants) -> AUTHORIZED_EWASTE
    resp_pla1 = client.get("/api/v1/materials/MAT-PLA-01")
    assert resp_pla1.status_code == 200
    pla1 = resp_pla1.json()
    assert pla1["default_route"] == "AUTHORIZED_EWASTE"
    assert pla1["route_requires_context"] is True

    # 2. General Mixed Plastics -> GENERAL_RECYCLING with context required
    resp_pla2 = client.get("/api/v1/materials/MAT-PLA-02")
    assert resp_pla2.status_code == 200
    pla2 = resp_pla2.json()
    assert pla2["default_route"] == "GENERAL_RECYCLING"
    assert pla2["route_requires_context"] is True

    # 3. Batteries -> BATTERY_ISOLATION under separate battery portal rules
    for bat_id in ["MAT-BAT-01", "MAT-BAT-02", "MAT-BAT-03", "MAT-BAT-04"]:
        resp_bat = client.get(f"/api/v1/materials/{bat_id}")
        assert resp_bat.status_code == 200
        bat = resp_bat.json()
        assert bat["default_route"] == "BATTERY_ISOLATION"
        assert bat["route_requires_context"] is True

    # 4. CRT -> HAZARDOUS_DISPOSAL
    resp_crt = client.get("/api/v1/materials/MAT-CRT-01")
    assert resp_crt.status_code == 200
    crt = resp_crt.json()
    assert crt["default_route"] == "HAZARDOUS_DISPOSAL"
    assert crt["route_requires_context"] is True

    # 5. UNKNOWN -> REVIEW_REQUIRED
    resp_unk = client.get("/api/v1/materials/MAT-UNK-01")
    assert resp_unk.status_code == 200
    unk = resp_unk.json()
    assert unk["default_route"] == "REVIEW_REQUIRED"
    assert unk["route_requires_context"] is True


def test_language_alias_resolution_hindi(client):
    """Test alias search resolving Hindi colloquial terms to stable material IDs."""
    test_cases = [
        ("मदरबोर्ड", "MAT-PCB-01"),
        ("हरा पत्ता", "MAT-PCB-01"),
        ("सीआरटी मॉनिटर", "MAT-CRT-01"),
        ("कांच वाला टीवी", "MAT-CRT-01"),
        ("इन्वर्टर बैटरी", "MAT-BAT-01"),
        ("गाड़ी की बैटरी", "MAT-BAT-01"),
        ("मोबाइल की बैटरी", "MAT-BAT-02"),
        ("तांबे का तार", "MAT-CAB-01"),
        ("बिजली की मोटर", "MAT-MOT-01"),
        ("ई-वेस्ट प्लास्टिक", "MAT-PLA-01"),
        ("अज्ञात सामान", "MAT-UNK-01"),
    ]
    for query, expected_mat_id in test_cases:
        res = client.get(f"/api/v1/materials/search?q={query}&language=hi")
        assert res.status_code == 200
        data = res.json()
        assert len(data) > 0, f"Query '{query}' returned no matches"
        assert data[0]["material"]["id"] == expected_mat_id, f"Query '{query}' resolved to {data[0]['material']['id']}, expected {expected_mat_id}"


def test_language_alias_resolution_marathi(client):
    """Test alias search resolving Marathi colloquial terms to stable material IDs."""
    test_cases = [
        ("मदरबोर्ड", "MAT-PCB-01"),
        ("हिरवा बोर्ड", "MAT-PCB-01"),
        ("सीआरटी मॉनिटर", "MAT-CRT-01"),
        ("काचेची ट्यूब", "MAT-CRT-01"),
        ("इन्व्हर्टर बॅटरी", "MAT-BAT-01"),
        ("गाडीची बॅटरी", "MAT-BAT-01"),
        ("मोबाईल बॅटरी", "MAT-BAT-02"),
        ("तांब्याची वायर", "MAT-CAB-01"),
        ("विजेची मोटर", "MAT-MOT-01"),
        ("ई-कचरा प्लास्टिक", "MAT-PLA-01"),
        ("अज्ञात वस्तू", "MAT-UNK-01"),
    ]
    for query, expected_mat_id in test_cases:
        res = client.get(f"/api/v1/materials/search?q={query}&language=mr")
        assert res.status_code == 200
        data = res.json()
        assert len(data) > 0, f"Query '{query}' returned no matches"
        assert data[0]["material"]["id"] == expected_mat_id, f"Query '{query}' resolved to {data[0]['material']['id']}, expected {expected_mat_id}"


def test_language_alias_resolution_english(client):
    """Test alias search resolving English terms to stable material IDs."""
    test_cases = [
        ("motherboard", "MAT-PCB-01"),
        ("green board", "MAT-PCB-01"),
        ("brown board", "MAT-PCB-02"),
        ("lead acid battery", "MAT-BAT-01"),
        ("inverter battery", "MAT-BAT-01"),
        ("lithium ion battery", "MAT-BAT-02"),
        ("mobile battery", "MAT-BAT-02"),
        ("crt monitor", "MAT-CRT-01"),
        ("picture tube", "MAT-CRT-01"),
        ("copper wire", "MAT-CAB-01"),
        ("electric motor", "MAT-MOT-01"),
        ("unknown item", "MAT-UNK-01"),
    ]
    for query, expected_mat_id in test_cases:
        res = client.get(f"/api/v1/materials/search?q={query}&language=en")
        assert res.status_code == 200
        data = res.json()
        assert len(data) > 0, f"Query '{query}' returned no matches"
        assert data[0]["material"]["id"] == expected_mat_id, f"Query '{query}' resolved to {data[0]['material']['id']}, expected {expected_mat_id}"


def test_contextual_safety_guides(client):
    """Test safety guides have multilingual audio keys and link properly to materials."""
    response = client.get("/api/v1/safety-guides")
    assert response.status_code == 200
    guides = response.json()
    assert len(guides) >= 9

    guide_ids = {g["id"]: g for g in guides}
    expected_guides = [
        "SG-CABLE-01",    # No burning cables
        "SG-PCB-01",      # No acid leaching or heating
        "SG-CRT-01",      # No breaking CRT glass
        "SG-BATTERY-01",  # Lead acid handling
        "SG-BATTERY-02",  # Li-ion terminal taping
        "SG-BATTERY-03",  # Unknown battery containment
        "SG-DAMAGED-01",  # Stop handling damaged/leaking items
        "SG-PLASTIC-01",  # No burning e-waste plastics
        "SG-MIXED-01",    # No blind dismantling
    ]
    for gid in expected_guides:
        assert gid in guide_ids
        guide = guide_ids[gid]
        assert "audio_keys" in guide
        audio = guide["audio_keys"]
        assert "en" in audio and "hi" in audio and "mr" in audio
        assert guide["icon_asset_ref"]
        assert guide["text_key"]

    # Filter safety guides by material
    resp_mat_guide = client.get("/api/v1/safety-guides?material_id=MAT-CAB-01")
    assert resp_mat_guide.status_code == 200
    mat_guides = [g["id"] for g in resp_mat_guide.json()]
    assert "SG-CABLE-01" in mat_guides


def test_draft_lot_creation_links_to_catalog(client):
    """Test creating draft lots for every PS-named material type (AT-011)."""
    # Create a test collector user in test db
    collector_id = uuid.uuid4()
    with TestingSessionLocal() as session:
        user = User(
            id=collector_id,
            phone_normalized="+919876543210",
            pin_hash="peppered_test_pin_hash",
            role="COLLECTOR"
        )
        session.add(user)
        col = Collector(
            id=collector_id,
            user_id=collector_id,
            display_alias="Santosh Test",
            preferred_language="hi",
            general_area="Mayapuri, Delhi"
        )
        session.add(col)
        session.commit()
        token = create_access_token(subject=str(collector_id), role="COLLECTOR")
        headers = {"Authorization": f"Bearer {token}"}

    materials_to_test = [
        ("MAT-CRT-01", 12500, "CRACKED_GLASS", "HAZARDOUS_DISPOSAL"),
        ("MAT-LCD-01", 3400, "INTACT", "AUTHORIZED_EWASTE"),
        ("MAT-PCB-01", 1850, "INTACT", "AUTHORIZED_EWASTE"),
        ("MAT-CAB-01", 5200, "INSULATED", "GENERAL_RECYCLING"),
        ("MAT-BAT-01", 14000, "INTACT", "BATTERY_ISOLATION"),
        ("MAT-BAT-02", 450, "SWOLLEN", "BATTERY_ISOLATION"),
        ("MAT-MOT-01", 6200, "INTACT", "GENERAL_RECYCLING"),
        ("MAT-PLA-01", 8500, "CLEAN_CASING", "AUTHORIZED_EWASTE"),
        ("MAT-MIX-01", 11000, "PARTIALLY_DISMANTLED", "AUTHORIZED_EWASTE"),
        ("MAT-OTH-01", 2000, "SCRAP", "REVIEW_REQUIRED"),
        ("MAT-UNK-01", 1500, "UNKNOWN", "REVIEW_REQUIRED"),
    ]

    for mat_id, weight_g, condition, expected_route in materials_to_test:
        lot_id = uuid.uuid4()
        payload = {
            "id": str(lot_id),
            "collector_id": str(collector_id),
            "material_id": mat_id,
            "estimated_weight_g": weight_g,
            "condition": condition,
            "description": f"Test lot for {mat_id}",
            "is_demo": False
        }
        res = client.post("/api/v1/lots", json=payload, headers=headers)
        assert res.status_code == 201, f"Failed to create lot for {mat_id}: {res.text}"
        data = res.json()
        assert data["id"] == str(lot_id)
        assert data["material_id"] == mat_id
        assert data["estimated_weight_g"] == weight_g
        assert data["condition"] == condition
        assert data["regulatory_route"] == expected_route
        assert data["status"] == "DRAFT"

        # Verify lot can be retrieved
        get_res = client.get(f"/api/v1/lots/{lot_id}", headers=headers)
        assert get_res.status_code == 200
        get_data = get_res.json()
        assert get_data["material_id"] == mat_id

    # Test rejection of nonexistent material ID
    bad_payload = {
        "collector_id": str(collector_id),
        "material_id": "MAT-NONEXISTENT-99",
        "estimated_weight_g": 1000,
    }
    bad_res = client.post("/api/v1/lots", json=bad_payload, headers=headers)
    assert bad_res.status_code == 400
    assert "not found in curated catalog" in bad_res.json()["detail"]


def test_reference_catalog_distinct_from_observations(client):
    """Verify that creating lots/observations does not alter or pollute reference catalog entries."""
    # Count materials before
    resp1 = client.get("/api/v1/materials")
    before_count = len(resp1.json())

    # Create another lot
    collector_id = uuid.uuid4()
    with TestingSessionLocal() as session:
        user = User(id=collector_id, phone_normalized="+919876543219", pin_hash="hash", role="COLLECTOR")
        session.add(user)
        col = Collector(id=collector_id, user_id=collector_id, display_alias="Anil Test", preferred_language="mr", general_area="Kurla")
        session.add(col)
        session.commit()

    client.post("/api/v1/lots", json={
        "collector_id": str(collector_id),
        "material_id": "MAT-PCB-01",
        "estimated_weight_g": 9999,
        "condition": "BURNT"
    })

    # Count materials after
    resp2 = client.get("/api/v1/materials")
    after_count = len(resp2.json())
    assert before_count == after_count

    # Verify MAT-PCB-01 catalog entry remains completely pristine
    mat_detail = client.get("/api/v1/materials/MAT-PCB-01").json()
    assert mat_detail["subcategory_code"] == "PCB_HIGH_GRADE"
    assert mat_detail["default_route"] == "AUTHORIZED_EWASTE"
