# auth/config.py
from enum import Enum
from pydantic import BaseModel
from typing import Callable

class AuthConfig(BaseModel):
    session_ttl_seconds: int = 3600
    secure_cookies: bool = True
    login_fields: list[str] = ["email"]
    login_after_signup: bool = True
    password_validator: Callable[[str], bool] = lambda x: True
    roles: type[Enum] | None = None
