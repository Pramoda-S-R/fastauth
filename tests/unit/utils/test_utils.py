from fastapi import Request

from fastauth.crypto import hash_password, verify_password
from fastauth.utils import get_accept_language, get_client_ip, get_user_agent


def test_password_hashing():
    password = "secret_password"
    hashed = hash_password(password)
    assert hashed != password
    assert verify_password(password, hashed) is True
    assert verify_password("wrong_password", hashed) is False


def test_get_client_ip_direct():
    request = Request(
        scope={"type": "http", "client": ("127.0.0.1", 1234), "headers": []}
    )
    assert get_client_ip(request) == "127.0.0.1"


def test_get_client_ip_x_forwarded_for():
    request = Request(
        scope={"type": "http", "headers": [(b"x-forwarded-for", b"1.2.3.4, 5.6.7.8")]}
    )
    assert get_client_ip(request) == "1.2.3.4"


def test_get_client_ip_x_real_ip():
    request = Request(scope={"type": "http", "headers": [(b"x-real-ip", b"9.8.7.6")]})
    assert get_client_ip(request) == "9.8.7.6"


def test_get_user_agent():
    request = Request(
        scope={"type": "http", "headers": [(b"user-agent", b"Mozilla/5.0")]}
    )
    assert get_user_agent(request) == "Mozilla/5.0"


def test_get_accept_language():
    request = Request(
        scope={"type": "http", "headers": [(b"accept-language", b"en-US,en;q=0.9")]}
    )
    assert get_accept_language(request) == "en-US,en;q=0.9"
