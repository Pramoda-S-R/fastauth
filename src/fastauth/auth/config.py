# auth/config.py
from pydantic import BaseModel
from enum import Enum

class AuthMode(str, Enum):
    TOKEN = "token"
    COOKIE = "cookie"

class AuthConfig(BaseModel):
    auth_mode: AuthMode
    session_ttl_seconds: int = 3600
    secure_cookies: bool = True
