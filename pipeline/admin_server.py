"""Admin backend server for Lupita.
Provides REST API endpoints to:
- List, inspect, create, update, and delete fish species profiles in data/species/<id>.json
- Upload and manage fish illustration/photo PNGs in web/fish/<id>.png
- Provide parameter registry definitions from data/parameters.json
- Seamlessly trigger database sync (species catalog and live prediction updates)
- Serve the admin dashboard web application
"""
from __future__ import annotations

import base64
import json
import logging
import mimetypes
import os
import re
from datetime import datetime, timezone
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlparse

from pipeline import catalog

ROOT = Path(__file__).resolve().parent.parent
SPECIES_DIR = ROOT / "data" / "species"
FISH_IMG_DIR = ROOT / "web" / "fish"
PARAMS_FILE = ROOT / "data" / "parameters.json"
WEB_DIR = ROOT / "web"

log = logging.getLogger("admin_server")

HEX_COLOR_RE = re.compile(r"^#[0-9a-fA-F]{6}$")
VALID_KINDS = {
    "range", "higher_is_better", "category", "season", "flag",
    "flag_penalty", "presence", "proximity", "closer_is_better"
}


def load_parameters() -> dict:
    """Return parameters registry."""
    if PARAMS_FILE.exists():
        try:
            return json.loads(PARAMS_FILE.read_text(encoding="utf-8"))
        except Exception as exc:
            log.error("Failed to load parameters.json: %s", exc)
    return {"parameters": []}


def get_parameter_keys() -> set[str]:
    reg = load_parameters()
    return {p["key"] for p in reg.get("parameters", []) if "key" in p}


def validate_species_profile(profile: dict, is_new: bool = False, current_id: str | None = None) -> list[str]:
    """Validate a species profile according to Lupita schema rules."""
    errors = []
    sid = profile.get("id")
    if not sid or not isinstance(sid, str) or not re.fullmatch(r"^[a-z0-9-]+$", sid):
        errors.append("Invalid or missing 'id'. Must be lowercase alphanumeric with hyphens (e.g. 'queen-snapper').")
    elif is_new and (SPECIES_DIR / f"{sid}.json").exists():
        errors.append(f"Species with id '{sid}' already exists.")
    elif current_id and sid != current_id:
        errors.append("Changing 'id' directly is not permitted in an update. Please keep 'id' consistent.")

    if not profile.get("common_name") or not isinstance(profile["common_name"], str):
        errors.append("Missing or invalid 'common_name'.")
    if not profile.get("scientific_name") or not isinstance(profile["scientific_name"], str):
        errors.append("Missing or invalid 'scientific_name'.")

    display = profile.get("display") or {}
    color = display.get("color", "")
    if not HEX_COLOR_RE.fullmatch(color):
        errors.append("Display color must be a valid 6-character hex code (e.g. '#ff6600').")
    else:
        # Check color uniqueness among other species
        target_color = color.lower()
        for p in SPECIES_DIR.glob("*.json"):
            if p.stem == sid:
                continue
            try:
                other_d = json.loads(p.read_text(encoding="utf-8"))
                other_col = other_d.get("display", {}).get("color", "").lower()
                if other_col == target_color:
                    errors.append(f"Color '{color}' is already used by species '{p.stem}'. Please pick a distinct color.")
                    break
            except Exception:
                continue

    factors = profile.get("factors")
    if factors is None or not isinstance(factors, list):
        errors.append("Profile must contain a 'factors' array.")
    else:
        active_factors = [f for f in factors if f.get("active")]
        if not active_factors:
            errors.append("Profile must have at least one active factor.")
        else:
            weight_sum = sum(f.get("weight", 0) for f in active_factors)
            if weight_sum > 1.0 + 1e-6:
                errors.append(f"Total active factor weight ({weight_sum:.3f}) exceeds maximum allowed of 1.0.")

        param_keys = get_parameter_keys()
        for idx, f in enumerate(factors):
            p_name = f.get("param")
            if not p_name or p_name not in param_keys:
                errors.append(f"Factor #{idx+1} uses unknown parameter '{p_name}'. Must be listed in data/parameters.json.")
            f_kind = f.get("kind")
            if f_kind not in VALID_KINDS:
                errors.append(f"Factor #{idx+1} has invalid kind '{f_kind}'. Valid kinds: {', '.join(sorted(VALID_KINDS))}.")
            if f.get("active") and f.get("weight", 0) <= 0:
                errors.append(f"Factor #{idx+1} ({p_name}) is active but has non-positive weight.")
            if f_kind == "range":
                rng = f.get("range")
                ideal = f.get("ideal")
                if not (isinstance(rng, list) and len(rng) == 2 and isinstance(ideal, list) and len(ideal) == 2):
                    errors.append(f"Factor #{idx+1} ({p_name}) range kind requires 2-element 'range' and 'ideal' arrays.")
                elif not (rng[0] <= ideal[0] <= ideal[1] <= rng[1]):
                    errors.append(f"Factor #{idx+1} ({p_name}) range error: condition range[0] <= ideal[0] <= ideal[1] <= range[1] violated.")
            if f_kind == "season":
                months = set(f.get("months", []))
                peaks = set(f.get("peak_months", []))
                if not months or not peaks.issubset(months):
                    errors.append(f"Factor #{idx+1} ({p_name}) season error: 'peak_months' must be subset of 'months'.")

    return errors


def sync_database() -> dict:
    """Rebuild database catalog and live exports."""
    results = {"catalog_updated": False, "species_count": 0, "errors": []}
    try:
        live = ROOT / "data" / "live"
        live.mkdir(parents=True, exist_ok=True)
        now = datetime.now(timezone.utc).isoformat()
        cat_data = catalog.build_catalog(SPECIES_DIR, now)
        (live / "species_catalog.json").write_text(json.dumps(cat_data, indent=2, allow_nan=False), encoding="utf-8")
        results["catalog_updated"] = True
        results["species_count"] = cat_data.get("total", 0)
    except Exception as exc:
        log.error("Database catalog sync error: %s", exc)
        results["errors"].append(str(exc))
    return results


class AdminHandler(SimpleHTTPRequestHandler):
    """HTTP request handler for Lupita Admin backend."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def _send_json(self, data: dict | list, status: int = HTTPStatus.OK):
        body = json.dumps(data, indent=2, allow_nan=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(body)

    def _send_error(self, message: str, status: int = HTTPStatus.BAD_REQUEST, errors: list[str] | None = None):
        payload = {"success": False, "error": message}
        if errors:
            payload["errors"] = errors
        self._send_json(payload, status=status)

    def do_OPTIONS(self):
        self.send_response(HTTPStatus.NO_CONTENT)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if path == "/admin" or path == "/admin/":
            self._serve_file(WEB_DIR / "admin.html", "text/html")
            return

        if path == "/api/admin/species":
            self._handle_list_species()
            return

        if path.startswith("/api/admin/species/"):
            sid = unquote(path[len("/api/admin/species/"):].strip("/"))
            if sid:
                self._handle_get_species(sid)
                return

        if path == "/api/admin/parameters":
            self._send_json(load_parameters())
            return

        # Fallback to static serving
        super().do_GET()

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if path == "/api/admin/species":
            self._handle_create_species()
            return

        if path.startswith("/api/admin/species/") and path.endswith("/image"):
            sid = unquote(path[len("/api/admin/species/"):-len("/image")].strip("/"))
            self._handle_upload_image(sid)
            return

        if path.startswith("/api/admin/species/"):
            sid = unquote(path[len("/api/admin/species/"):].strip("/"))
            self._handle_update_species(sid)
            return

        if path == "/api/admin/sync" or path == "/api/admin/rebuild":
            res = sync_database()
            self._send_json({"success": res["catalog_updated"], "result": res})
            return

        self._send_error(f"Endpoint not found: {path}", HTTPStatus.NOT_FOUND)

    def do_PUT(self):
        parsed = urlparse(self.path)
        path = parsed.path
        if path.startswith("/api/admin/species/"):
            sid = unquote(path[len("/api/admin/species/"):].strip("/"))
            self._handle_update_species(sid)
            return
        self._send_error(f"Endpoint not found: {path}", HTTPStatus.NOT_FOUND)

    def do_DELETE(self):
        parsed = urlparse(self.path)
        path = parsed.path
        if path.startswith("/api/admin/species/"):
            sid = unquote(path[len("/api/admin/species/"):].strip("/"))
            self._handle_delete_species(sid)
            return
        self._send_error(f"Endpoint not found: {path}", HTTPStatus.NOT_FOUND)

    def _read_json_body(self) -> dict | None:
        try:
            content_length = int(self.headers.get("Content-Length", 0))
            if content_length <= 0:
                return None
            data = self.rfile.read(content_length)
            return json.loads(data.decode("utf-8"))
        except Exception as exc:
            log.warning("JSON decode error: %s", exc)
            return None

    def _serve_file(self, file_path: Path, content_type: str):
        if not file_path.exists():
            self._send_error("File not found", HTTPStatus.NOT_FOUND)
            return
        data = file_path.read_bytes()
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", f"{content_type}; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _handle_list_species(self):
        species_list = []
        for p in sorted(SPECIES_DIR.glob("*.json")):
            try:
                d = json.loads(p.read_text(encoding="utf-8"))
                sid = d.get("id", p.stem)
                img_url = d.get("image", {}).get("url", f"fish/{sid}.png")
                img_path = ROOT / "web" / img_url
                species_list.append({
                    "id": sid,
                    "common_name": d.get("common_name", sid),
                    "scientific_name": d.get("scientific_name", ""),
                    "color": d.get("display", {}).get("color", "#ff6600"),
                    "habitat_zone": d.get("habitat_zone", "offshore"),
                    "model": d.get("model", "grid"),
                    "factors_count": len(d.get("factors", [])),
                    "active_factors_count": len([f for f in d.get("factors", []) if f.get("active")]),
                    "image_url": img_url,
                    "has_image": img_path.exists(),
                    "image_kind": d.get("image", {}).get("kind", "illustration"),
                    "image_status": d.get("image", {}).get("status", "placeholder"),
                })
            except Exception as exc:
                log.warning("Failed to parse species file %s: %s", p, exc)
                continue
        self._send_json({"total": len(species_list), "species": species_list})

    def _handle_get_species(self, sid: str):
        target = SPECIES_DIR / f"{sid}.json"
        if not target.exists():
            self._send_error(f"Species '{sid}' not found", HTTPStatus.NOT_FOUND)
            return
        try:
            d = json.loads(target.read_text(encoding="utf-8"))
            img_url = d.get("image", {}).get("url", f"fish/{sid}.png")
            d["_image_exists"] = (ROOT / "web" / img_url).exists()
            self._send_json(d)
        except Exception as exc:
            self._send_error(f"Failed to read species '{sid}': {exc}", HTTPStatus.INTERNAL_SERVER_ERROR)

    def _handle_create_species(self):
        payload = self._read_json_body()
        if not payload:
            self._send_error("Invalid or empty JSON body")
            return

        sid = payload.get("id")
        errors = validate_species_profile(payload, is_new=True)
        if errors:
            self._send_error("Validation failed", HTTPStatus.UNPROCESSABLE_ENTITY, errors=errors)
            return

        # Ensure schema_version
        if "schema_version" not in payload:
            payload["schema_version"] = 1

        target = SPECIES_DIR / f"{sid}.json"
        try:
            target.write_text(json.dumps(payload, indent=2, allow_nan=False), encoding="utf-8")
            sync_res = sync_database()
            self._send_json({
                "success": True,
                "message": f"Created species '{sid}' successfully.",
                "id": sid,
                "sync": sync_res
            }, status=HTTPStatus.CREATED)
        except Exception as exc:
            self._send_error(f"Failed to save species: {exc}", HTTPStatus.INTERNAL_SERVER_ERROR)

    def _handle_update_species(self, sid: str):
        target = SPECIES_DIR / f"{sid}.json"
        if not target.exists():
            self._send_error(f"Species '{sid}' not found", HTTPStatus.NOT_FOUND)
            return

        payload = self._read_json_body()
        if not payload:
            self._send_error("Invalid or empty JSON body")
            return

        # Clean any private helper keys
        payload.pop("_image_exists", None)

        errors = validate_species_profile(payload, is_new=False, current_id=sid)
        if errors:
            self._send_error("Validation failed", HTTPStatus.UNPROCESSABLE_ENTITY, errors=errors)
            return

        try:
            target.write_text(json.dumps(payload, indent=2, allow_nan=False), encoding="utf-8")
            sync_res = sync_database()
            self._send_json({
                "success": True,
                "message": f"Updated species '{sid}' successfully.",
                "id": sid,
                "sync": sync_res
            })
        except Exception as exc:
            self._send_error(f"Failed to update species: {exc}", HTTPStatus.INTERNAL_SERVER_ERROR)

    def _handle_delete_species(self, sid: str):
        target = SPECIES_DIR / f"{sid}.json"
        if not target.exists():
            self._send_error(f"Species '{sid}' not found", HTTPStatus.NOT_FOUND)
            return
        try:
            target.unlink()
            sync_res = sync_database()
            self._send_json({
                "success": True,
                "message": f"Deleted species '{sid}'.",
                "sync": sync_res
            })
        except Exception as exc:
            self._send_error(f"Failed to delete species '{sid}': {exc}", HTTPStatus.INTERNAL_SERVER_ERROR)

    def _handle_upload_image(self, sid: str):
        """Upload raw PNG or SVG or Base64 image payload."""
        target_sp = SPECIES_DIR / f"{sid}.json"
        if not target_sp.exists():
            self._send_error(f"Species '{sid}' not found", HTTPStatus.NOT_FOUND)
            return

        try:
            content_length = int(self.headers.get("Content-Length", 0))
            if content_length <= 0:
                self._send_error("Empty image content")
                return

            raw_bytes = self.rfile.read(content_length)
            content_type = self.headers.get("Content-Type", "")

            FISH_IMG_DIR.mkdir(parents=True, exist_ok=True)
            dest_png = FISH_IMG_DIR / f"{sid}.png"

            if "application/json" in content_type:
                data = json.loads(raw_bytes.decode("utf-8"))
                b64 = data.get("image_base64", "")
                if "," in b64:
                    b64 = b64.split(",", 1)[1]
                img_data = base64.b64decode(b64)
            else:
                img_data = raw_bytes

            # Check PNG header
            if img_data[:8] != b"\x89PNG\r\n\x1a\n":
                self._send_error("File is not a valid PNG image.")
                return

            dest_png.write_bytes(img_data)

            # Update profile image metadata if requested
            try:
                sp_json = json.loads(target_sp.read_text(encoding="utf-8"))
                img_obj = sp_json.setdefault("image", {})
                img_obj["url"] = f"fish/{sid}.png"
                img_obj["status"] = "photo"
                target_sp.write_text(json.dumps(sp_json, indent=2, allow_nan=False), encoding="utf-8")
                sync_database()
            except Exception as exc:
                log.warning("Could not update species image config: %s", exc)

            self._send_json({
                "success": True,
                "message": f"Saved image for species '{sid}'.",
                "url": f"fish/{sid}.png",
                "bytes": len(img_data)
            })
        except Exception as exc:
            self._send_error(f"Image upload failed: {exc}", HTTPStatus.INTERNAL_SERVER_ERROR)


def run_server(port: int = 8080, host: str = "0.0.0.0"):
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    server = ThreadingHTTPServer((host, port), AdminHandler)
    log.info(f"Lupita Admin Server running on http://{host}:{port}/admin")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        log.info("Admin server stopped by user.")
    finally:
        server.server_close()


if __name__ == "__main__":
    import sys
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
    run_server(port=port)
