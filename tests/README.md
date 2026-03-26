# FastAuth Test Suite

This directory contains the automated test suite for the **FastAuth** library. The tests are designed to ensure high reliability for authentication, session management, and API security.

## 🚀 How to Run Tests

The test suite uses `pytest` and `pytest-asyncio`. Since this is a `uv` project, use the following commands:

```bash
# Run all tests
uv run pytest tests

# Run tests with verbose output
uv run pytest tests -v

# Run tests with coverage (if installed)
uv run pytest tests --cov=src/fastauth
```

## 📂 Directory Structure

The tests are organized logically by module for better maintainability:

```text
tests/
├── conftest.py              # Shared mocks and global fixtures
├── unit/
│   ├── api/                 # API dependencies and router integration
│   ├── auth/                # AuthManager and configuration validation
│   ├── sessions/            # Session stores (Memory, Redis, DB)
│   ├── strategies/          # Auth strategies (JWT, Opaque)
│   └── utils/               # Crypto and request utility functions
```

## 🧪 Components Tested

### **1. Sessions (`tests/unit/sessions/`)**
*   **MemorySessionStore**: CRUD operations and TTL-based expiration in memory.
*   **RedisSessionStore**: Interaction with Redis, session serialization, and TTL support.
*   **DBSessionStore**: Generic SQL database session logic using protocol-based mocks.

### **2. Strategies (`tests/unit/strategies/`)**
*   **JWTStrategy**: Token issuance (Access/Refresh), verification, extraction from headers/cookies, and expiration handling.
*   **OpaqueStrategy**: Server-side session ID persistence and revocation.

### **3. Auth & Config (`tests/unit/auth/`)**
*   **AuthManager**: Core initialization, role validation, and cross-component orchestration.
*   **AuthConfig**: Validation of Pydantic schemas for signup and login requests, slug formatting, and security settings.
*   **Flexible Schema**: Verification of custom user models and schema mapping.

### **4. API (`tests/unit/api/`)**
*   **Dependencies**: Extraction of current user and session from request context.
*   **Router**: Integration tests for signup, login, and logout endpoints using `fastapi.testclient.TestClient`.

### **5. Utils (`tests/unit/utils/`)**
*   **Crypto**: Password hashing (Argon2) and verification.
*   **Utilities**: IP address resolution (with proxy support) and metadata extraction.

## 🛠️ Mocking Strategy

To keep tests fast and isolated, we use **Protocol-based Mocking**:
- **Redis Mock**: A lightweight in-memory dictionary acting as a Redis client.
- **Database Mock**: Generic query/session mocks that follow the `DatabaseSession` protocol.
- **Schema Mocks**: Pre-configured Pydantic models with `__test__ = False` to prevent Pydantic-Pytest collection noise.

## ⚙️ Configuration

The test environment is configured via:
- `pyproject.toml`: Defines `asyncio` loop scopes and basic filtering.
- `pytest.ini`: Suppresses unavoidable third-party deprecation warnings (e.g., `passlib`/`argon2-cffi`).
