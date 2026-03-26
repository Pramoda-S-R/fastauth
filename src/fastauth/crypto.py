from passlib.context import CryptContext
import hashlib
import secrets

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, hashed: str) -> bool:
    return pwd_context.verify(password, hashed)


def hash_string(input_string: str) -> str:
    """Hash a string using SHA-256."""
    return hashlib.sha256(input_string.encode()).hexdigest()

def compare_hash(hash1: str, hash2: str) -> bool:
    """Compare two hashes."""
    return secrets.compare_digest(hash1, hash2)

def soft_fingerprint(user_agent: str, ip: str, accept_language: str, accept_encoding: str) -> str:
    """Generate a soft fingerprint for a user agent and IP address."""
    return hash_string(f"{user_agent}:{ip}:{accept_language}:{accept_encoding}")