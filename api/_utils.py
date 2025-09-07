from datetime import datetime, timezone
from typing import Any, Dict, Iterable

import phonenumbers
from flask import jsonify


def iso_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def normalize_phone_e164(raw: str, default_region: str = "BR") -> str:
    try:
        phone = phonenumbers.parse(raw, default_region)
        if not phonenumbers.is_valid_number(phone):
            raise ValueError
    except Exception as exc:  # noqa: BLE001
        raise ValueError("Telefone inválido") from exc
    return phonenumbers.format_number(phone, phonenumbers.PhoneNumberFormat.E164)


def parse_int(val: Any, default: int = 0) -> int:
    try:
        return int(val)
    except (TypeError, ValueError):
        return default


def parse_float(val: Any, default: float = 0.0) -> float:
    try:
        return float(val)
    except (TypeError, ValueError):
        return default


def parse_bool(val: Any, default: bool = False) -> bool:
    if isinstance(val, bool):
        return val
    if val is None:
        return default
    return str(val).lower() in {"1", "true", "t", "yes", "y", "on"}


def nonempty_str(val: Any) -> str | None:
    if val is None:
        return None
    s = str(val).strip()
    return s or None


def pick(d: Dict[str, Any], keys: Iterable[str]) -> Dict[str, Any]:
    return {k: d[k] for k in keys if k in d}


def ensure_required(d: Dict[str, Any], required: Iterable[str]) -> None:
    missing = [k for k in required if not nonempty_str(d.get(k))]
    if missing:
        raise ValueError("Campos obrigatórios: " + ", ".join(missing))


def _cors(resp):
    resp.headers["Access-Control-Allow-Origin"] = "*"
    resp.headers["Access-Control-Allow-Methods"] = "GET,POST,PUT,DELETE,OPTIONS"
    resp.headers["Access-Control-Allow-Headers"] = "Content-Type, X-User-Type"
    return resp


def json_error(status: int, code: str, message: str, details: Any | None = None):
    payload = {"ok": False, "error": {"code": code, "message": message}}
    if details is not None:
        payload["error"]["details"] = details
    resp = jsonify(payload)
    resp.status_code = status
    return _cors(resp)


def ok(data: Any | None = None, **extra: Any):
    payload: Dict[str, Any] = {"ok": True}
    if data is not None:
        payload["data"] = data
    payload.update(extra)
    resp = jsonify(payload)
    return _cors(resp)
