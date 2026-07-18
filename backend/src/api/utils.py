from __future__ import annotations

from datetime import datetime, timezone


def api_success(data):
    return {
        "status": "success",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "data": data,
    }


def api_error(message, status_code=500, details=None):
    payload = {
        "status": "error",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "error": {
            "message": message,
        },
    }
    if details is not None:
        payload["error"]["details"] = details
    return payload