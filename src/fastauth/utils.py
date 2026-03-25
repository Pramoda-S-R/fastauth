"""
Utility functions for FastAuth.

Provides common functionality used across the library including
IP address resolution (with reverse proxy support), request metadata
extraction, and other helper functions.
"""

from typing import Optional
from fastapi import Request


def get_client_ip(request: Request) -> str:
    """Extract the client's real IP address from a request.

    Handles common reverse proxy scenarios by checking headers in order:
    1. X-Forwarded-For (most common, may contain multiple IPs)
    2. X-Real-IP (nginx and some other proxies)
    3. request.client.host (FastAPI's direct connection)

    For X-Forwarded-For, only the first IP (original client) is used.

    Args:
        request: FastAPI Request object

    Returns:
        The client's IP address as a string
    """
    # Check X-Forwarded-For header (may contain: client, proxy1, proxy2)
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        # Take first IP (original client), strip any port
        client_ip = forwarded_for.split(",")[0].strip()
        if client_ip:
            return client_ip

    # Check X-Real-IP header (nginx and others)
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip.strip()

    # Fall back to direct connection
    if request.client:
        return request.client.host

    return "unknown"


def get_user_agent(request: Request) -> Optional[str]:
    """Extract the User-Agent header from a request.

    Args:
        request: FastAPI Request object

    Returns:
        User-Agent string or None if not present
    """
    return request.headers.get("User-Agent")


def get_accept_language(request: Request) -> Optional[str]:
    """Extract the Accept-Language header from a request.

    Args:
        request: FastAPI Request object

    Returns:
        Accept-Language string or None if not present
    """
    return request.headers.get("Accept-Language")
