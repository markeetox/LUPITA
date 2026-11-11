"""Unit tests for Lupita Admin backend API server, authentication, and validation."""
from __future__ import annotations

import base64
import json
import threading
from http import HTTPStatus
from http.server import ThreadingHTTPServer
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError

import pytest

from pipeline import admin_server

ROOT = Path(__file__).resolve().parent.parent
SPECIES_DIR = ROOT / "data" / "species"


@pytest.fixture(scope="module")
def admin_api_server():
    server = ThreadingHTTPServer(("127.0.0.1", 0), admin_server.AdminHandler)
    host, port = server.server_address
    t = threading.Thread(target=server.serve_forever, daemon=True)
    t.start()
    base_url = f"http://{host}:{port}"
    yield base_url
    server.shutdown()
    server.server_close()


def get_auth_token(base_url: str) -> str:
    req = Request(
        f"{base_url}/api/admin/login",
        data=json.dumps({"password": admin_server.ADMIN_PASSWORD}).encode(),
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    with urlopen(req) as resp:
        data = json.loads(resp.read().decode())
        return data["token"]


def test_auth_login_success_and_failure(admin_api_server):
    # Invalid password
    req_fail = Request(
        f"{admin_api_server}/api/admin/login",
        data=json.dumps({"password": "wrongpassword"}).encode(),
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    with pytest.raises(HTTPError) as exc:
        urlopen(req_fail)
    assert exc.value.code == HTTPStatus.UNAUTHORIZED

    # Valid password
    token = get_auth_token(admin_api_server)
    assert isinstance(token, str) and len(token) > 0

    # Verify auth status
    req_status = Request(
        f"{admin_api_server}/api/admin/auth-status",
        headers={"Authorization": f"Bearer {token}"}
    )
    with urlopen(req_status) as resp:
        status_data = json.loads(resp.read().decode())
        assert status_data["authenticated"] is True


def test_unauthenticated_requests_are_rejected(admin_api_server):
    # Unauthenticated create should fail with 401
    req = Request(
        f"{admin_api_server}/api/admin/species",
        data=json.dumps({"id": "unauth-test"}).encode(),
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    with pytest.raises(HTTPError) as exc:
        urlopen(req)
    assert exc.value.code == HTTPStatus.UNAUTHORIZED


def test_validation_accepts_valid_profile():
    valid = {
        "id": "test-valid-fish",
        "common_name": "Test Valid Fish",
        "scientific_name": "Pisces testus",
        "display": {"color": "#abcdef"},
        "factors": [
            {
                "param": "sst_c",
                "kind": "range",
                "range": [15, 30],
                "ideal": [20, 25],
                "weight": 0.4,
                "active": True
            }
        ]
    }
    errors = admin_server.validate_species_profile(valid, is_new=False)
    assert errors == []


def test_validation_rejects_missing_fields_and_invalid_color():
    invalid = {
        "id": "Invalid ID!",
        "factors": []
    }
    errors = admin_server.validate_species_profile(invalid, is_new=False)
    assert any("id" in e.lower() for e in errors)
    assert any("common_name" in e.lower() for e in errors)
    assert any("scientific_name" in e.lower() for e in errors)
    assert any("color" in e.lower() for e in errors)
    assert any("at least one active factor" in e.lower() for e in errors)


def test_validation_rejects_weight_over_1():
    invalid = {
        "id": "heavy-fish",
        "common_name": "Heavy Fish",
        "scientific_name": "Pisces ponderosus",
        "display": {"color": "#123abc"},
        "factors": [
            {
                "param": "sst_c",
                "kind": "range",
                "range": [15, 30],
                "ideal": [20, 25],
                "weight": 0.8,
                "active": True
            },
            {
                "param": "chlorophyll",
                "kind": "range",
                "range": [0.1, 5],
                "ideal": [0.2, 2],
                "weight": 0.5,
                "active": True
            }
        ]
    }
    errors = admin_server.validate_species_profile(invalid, is_new=False)
    assert any("weight" in e.lower() and "exceeds" in e.lower() for e in errors)


def test_validation_rejects_unknown_parameter():
    invalid = {
        "id": "unknown-param-fish",
        "common_name": "Unknown Param Fish",
        "scientific_name": "Pisces ignotus",
        "display": {"color": "#123abc"},
        "factors": [
            {
                "param": "super_fake_ocean_parameter",
                "kind": "higher_is_better",
                "weight": 0.5,
                "active": True
            }
        ]
    }
    errors = admin_server.validate_species_profile(invalid, is_new=False)
    assert any("unknown parameter" in e.lower() for e in errors)


def test_get_parameters_endpoint(admin_api_server):
    req = Request(f"{admin_api_server}/api/admin/parameters")
    with urlopen(req) as resp:
        assert resp.status == HTTPStatus.OK
        data = json.loads(resp.read().decode())
        assert "parameters" in data
        assert len(data["parameters"]) > 0
        keys = [p["key"] for p in data["parameters"]]
        assert "sst_c" in keys


def test_list_species_endpoint(admin_api_server):
    req = Request(f"{admin_api_server}/api/admin/species")
    with urlopen(req) as resp:
        assert resp.status == HTTPStatus.OK
        data = json.loads(resp.read().decode())
        assert "species" in data
        assert data["total"] > 0
        ids = [s["id"] for s in data["species"]]
        assert "mahi-mahi" in ids


def test_get_species_endpoint(admin_api_server):
    req = Request(f"{admin_api_server}/api/admin/species/mahi-mahi")
    with urlopen(req) as resp:
        assert resp.status == HTTPStatus.OK
        data = json.loads(resp.read().decode())
        assert data["id"] == "mahi-mahi"
        assert "factors" in data
        assert "profile" in data


def test_create_update_delete_species_flow(admin_api_server):
    token = get_auth_token(admin_api_server)
    auth_headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    test_id = "test-crud-amberjack"
    test_file = SPECIES_DIR / f"{test_id}.json"
    if test_file.exists():
        test_file.unlink()

    # 1. Create species
    new_sp = {
        "schema_version": 1,
        "id": test_id,
        "common_name": "Test Amberjack",
        "scientific_name": "Seriola testus",
        "aliases": ["amberjack", "testjack"],
        "habitat_zone": "reef",
        "model": "grid",
        "display": {"color": "#556677"},
        "profile": {
            "size": "Up to 40 lb",
            "diet": "Squid, baitfish"
        },
        "factors": [
            {
                "param": "depth_m",
                "kind": "range",
                "range": [10, 150],
                "ideal": [30, 80],
                "weight": 0.6,
                "active": True,
                "value_status": "sourced",
                "sources": []
            }
        ]
    }

    req = Request(
        f"{admin_api_server}/api/admin/species",
        data=json.dumps(new_sp).encode(),
        headers=auth_headers,
        method="POST"
    )
    with urlopen(req) as resp:
        assert resp.status == HTTPStatus.CREATED
        res_data = json.loads(resp.read().decode())
        assert res_data["success"] is True
        assert res_data["id"] == test_id
        assert test_file.exists()

    # 2. Update species
    new_sp["profile"]["size"] = "Up to 55 lb"
    req_update = Request(
        f"{admin_api_server}/api/admin/species/{test_id}",
        data=json.dumps(new_sp).encode(),
        headers=auth_headers,
        method="POST"
    )
    with urlopen(req_update) as resp:
        assert resp.status == HTTPStatus.OK
        res_data = json.loads(resp.read().decode())
        assert res_data["success"] is True

    updated_on_disk = json.loads(test_file.read_text())
    assert updated_on_disk["profile"]["size"] == "Up to 55 lb"

    # 3. Image upload test (valid 1x1 transparent PNG)
    png_bytes = (
        b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06"
        b"\x00\x00\x00\x1f\x15c4\x00\x00\x00\rIDATx\x9cc`\x00\x00\x00\x02\x00\x01H\xaf"
        b"\xa4q\x00\x00\x00\x00IEND\xaeB`\x82"
    )
    req_img = Request(
        f"{admin_api_server}/api/admin/species/{test_id}/image",
        data=json.dumps({"image_base64": base64.b64encode(png_bytes).decode()}).encode(),
        headers=auth_headers,
        method="POST"
    )
    with urlopen(req_img) as resp:
        assert resp.status == HTTPStatus.OK
        res_data = json.loads(resp.read().decode())
        assert res_data["success"] is True

    img_file = ROOT / "web" / "fish" / f"{test_id}.png"
    assert img_file.exists()

    # 4. Trigger database sync
    req_sync = Request(
        f"{admin_api_server}/api/admin/sync",
        data=b"{}",
        headers=auth_headers,
        method="POST"
    )
    with urlopen(req_sync) as resp:
        assert resp.status == HTTPStatus.OK
        sync_data = json.loads(resp.read().decode())
        assert sync_data["success"] is True

    # 5. Delete species
    req_del = Request(
        f"{admin_api_server}/api/admin/species/{test_id}",
        headers={"Authorization": f"Bearer {token}"},
        method="DELETE"
    )
    with urlopen(req_del) as resp:
        assert resp.status == HTTPStatus.OK
        del_data = json.loads(resp.read().decode())
        assert del_data["success"] is True
        assert not test_file.exists()

    # Clean up test image
    if img_file.exists():
        img_file.unlink()

    # Re-sync catalog after test cleanup
    admin_server.sync_database()


def test_admin_dashboard_served(admin_api_server):
    req = Request(f"{admin_api_server}/admin")
    with urlopen(req) as resp:
        assert resp.status == HTTPStatus.OK
        content = resp.read().decode("utf-8")
        assert "L.U.P.I.T.A." in content
        assert "admin" in content.lower() or "command center" in content.lower()
        assert "species-list-container" in content
