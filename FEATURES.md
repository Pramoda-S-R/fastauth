# FastAuth - Current Features

## Overview

FastAuth is a flexible, plugin-based authentication library for FastAPI applications. It provides a complete authentication system with session management, multiple token strategies, and extensible user stores.

---

## Implemented Features

### Core Authentication

- **Email + Password Authentication**
  - Signup with validation
  - Login with credential verification
  - Password hashing using Argon2
  
- **Session Management**
  - Plugin-based session store architecture
  - Multiple storage backends:
    - `MemorySessionStore` - In-memory (development)
    - `RedisSessionStore` - Redis (production)
    - `DBSessionStore` - SQL database via SQLAlchemy
  - Automatic session expiration
  - Session refresh capability

- **Token Strategies**
  - `JWTStrategy` - Stateless JWT tokens with embedded claims
  - `OpaqueStrategy` - Server-side session storage with random tokens
  - Configurable cookie or bearer token authentication

### Security Features

- **HTTP-only Secure Cookies** - Tokens stored in secure cookies by default
- **Bearer Token Support** - Alternative to cookies for API authentication
- **Password Hashing** - Argon2 via passlib
- **Request Metadata Tracking** - User agent, IP, language tracking
- **Reverse Proxy Support** - Proper IP extraction from X-Forwarded-For and X-Real-IP headers
- **Configurable Password Validation** - Custom password strength rules

### Architecture

- **Plugin-Based Design**
  - UserStore protocol for custom user backends
  - SessionStore protocol for session storage
  - AuthStrategy protocol for token handling
  - OAuthProvider protocol for OAuth integration

- **Dependency Injection**
  - User dependencies (`get_current_user`)
  - Session dependencies (`get_current_session`)
  - AuthManager orchestrates all components

- **Configuration System**
  - Pydantic-based settings
  - Configurable login fields
  - Custom request/response models
  - Session TTL configuration

### Error Handling

- Proper HTTP status codes:
  - 400 - Bad Request (signup failures)
  - 401 - Unauthorized (invalid credentials, expired tokens)
  - 404 - Not Found (user not found)
  - 500 - Server errors (unexpected failures)
- Custom exception hierarchy mapped to HTTP exceptions

---

## Project Structure

```
src/fastauth/
├── api/
│   ├── router.py         # Auth endpoints (signup, login, logout)
│   └── dependencies.py    # FastAPI dependencies
├── auth/
│   ├── manager.py        # AuthManager orchestration
│   ├── config.py         # AuthConfig settings
│   ├── models.py        # Request/response models
│   └── types.py         # Type definitions
├── sessions/
│   ├── base.py          # SessionStore protocol
│   ├── memory.py        # In-memory implementation
│   ├── redis.py        # Redis implementation
│   └── db.py           # SQL database implementation
├── strategy/
│   ├── base.py         # AuthStrategy protocol
│   ├── jwt.py          # JWT implementation
│   └── opaque.py       # Opaque token implementation
├── users/
│   └── base.py         # UserStore protocol & BaseUser
├── oauth/
│   ├── base.py         # OAuthProvider protocol
│   └── registry.py     # OAuth provider registry
├── exceptions.py        # Custom exceptions
├── crypto.py          # Password hashing
├── utils.py           # Utility functions
└── audit.py           # Audit logging
```

---

## Quick Start

```python
from fastapi import FastAPI
from fastauth import AuthManager
from fastauth.auth import AuthConfig
from fastauth.sessions import MemorySessionStore
from fastauth.strategy import JWTStrategy
from fastauth.users import BaseUser
from pydantic import BaseModel

# Define user model
class User(BaseUser):
    email: str

# Configure auth
config = AuthConfig(
    slug="myapp",
    secret="your-secret-key",
    login_fields=["email"],
)

# Create auth manager
auth = AuthManager(
    config=config,
    user_store=YourUserStore(),
    session_store=MemorySessionStore(),
    strategy=JWTStrategy(secret="your-secret-key"),
    schema=User,
)

# Include router
app = FastAPI()
app.include_router(auth.router)
```

---

## Dependencies

- **fastapi** - Web framework
- **pydantic** - Data validation
- **passlib** - Password hashing (Argon2)
- **pyjwt** - JWT token handling
- **sqlalchemy** - Database ORM (optional)
- **redis** - Redis client (optional)

---

## Current Status

- **Phase 0**: ✅ Complete - Foundations & Contracts
- **Phase 1**: ✅ Complete - Core Authentication
- **Phase 2-9**: 🔄 Planned - See TODO.md for roadmap

---

## Next Steps (Phase 2+)

- RBAC (Role-Based Access Control)
- ABAC (Attribute-Based Access Control)
- OAuth providers (Google, GitHub)
- Magic link login
- MFA (TOTP, WebAuthn/passkeys)
- Multi-tenancy
- Rate limiting
- Advanced audit logging
