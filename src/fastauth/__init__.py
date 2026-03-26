import logging

from .auth.config import AuthConfig
from .auth.manager import AuthManager

logging.getLogger("fastauth").addHandler(logging.NullHandler())
logging.getLogger("fastauth.audit").addHandler(logging.NullHandler())


__all__ = [
    "AuthManager",
    "AuthConfig",
]
