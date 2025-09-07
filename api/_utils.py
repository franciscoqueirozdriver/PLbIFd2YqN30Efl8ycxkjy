from datetime import datetime, timezone

def iso_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

def ok(data=None, status=200, **extra):
    payload = {"ok": True}
    if data is not None: payload["data"] = data
    payload.update(extra); return payload, status

def err(status: int, code: str, message: str, details=None):
    return {"ok": False, "error": {"code": code, "message": message, "details": details or {}}}, status

def next_id(prefix: str, seq: int) -> str:
    return f"{prefix}_{seq:04d}"
