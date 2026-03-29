import logging

from .core.config import AuthConfig, RBACConfig, ABACConfig
from .core.manager import AuthManager

logging.getLogger("fastauth").addHandler(logging.NullHandler())
logging.getLogger("fastauth.audit").addHandler(logging.NullHandler())


__all__ = [
    "AuthManager",
    "AuthConfig",
]
