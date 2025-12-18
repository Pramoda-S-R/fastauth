# auth/config.py
from enum import Enum
from pydantic import BaseModel

class AuthConfig(BaseModel):
    session_ttl_seconds: int = 3600
    secure_cookies: bool = True
    login_fields: list[str] = ["email"]
    roles: type[Enum] | None = None
