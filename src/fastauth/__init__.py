import logging

from .auth.manager import AuthManager
from .auth.config import AuthConfig

logging.getLogger("fastauth").addHandler(logging.NullHandler())
logging.getLogger("fastauth.audit").addHandler(logging.NullHandler())


__all__ = [
    "AuthManager",
    "AuthConfig",
]