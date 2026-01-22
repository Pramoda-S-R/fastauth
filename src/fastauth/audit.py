import logging
from typing import Any, Dict

audit_logger = logging.getLogger("fastauth.audit")


def audit_event(
    event: str,
    *,
    user_id: str | None = None,
    request_id: str | None = None,
    ip_address: str | None = None,
    success: bool | None = None,
    **extra_fields: Dict[str, Any],
) -> None:
    """
    Emit a structured audit event.

    This function NEVER raises and NEVER configures logging.
    """
    try:
        audit_logger.info(
            event,
            extra={
                "event": event,
                "user_id": user_id,
                "request_id": request_id,
                "ip_address": ip_address,
                "success": success,
                **extra_fields,
            },
        )
    except Exception:
        # audit logging must never break auth
        pass
