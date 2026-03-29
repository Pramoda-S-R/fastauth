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
  - RoleStore protocol for role storage (RBAC)
  - AuthorizationEngine for policy evaluation (ABAC)

- **Dependency Injection**
  - User dependencies (`get_current_user`)
  - Session dependencies (`get_current_session`)
  - AuthManager orchestrates all components
  - Authorization dependencies (`require_permission`, `require_role`)

- **Configuration System**
  - Pydantic-based settings
  - Configurable login fields
  - Custom request/response models
  - Session TTL configuration
  - Opt-in RBAC/ABAC configuration

### Error Handling

- Proper HTTP status codes:
  - 400 - Bad Request (signup failures)
  - 401 - Unauthorized (invalid credentials, expired tokens)
  - 403 - Forbidden (insufficient permissions)
  - 404 - Not Found (user not found)
  - 500 - Server errors (unexpected failures)
- Custom exception hierarchy mapped to HTTP exceptions

### Authorization (RBAC/ABAC)

- **Role-Based Access Control (RBAC)**
  - Plugin-based role storage architecture
  - Multiple storage backends:
    - `MemoryRoleStore` - In-memory (development)
    - `SQLRoleStore` - SQL database via SQLAlchemy
  - Role definition with permissions
  - Role assignment to users
  - Default role configuration

- **Attribute-Based Access Control (ABAC)**
  - Policy-based authorization
  - Attribute evaluation engine
  - Condition-based rules
  - Action and resource matching
  - Allow/deny effects with proper evaluation order

- **Authorization Dependencies**
  - `require_permission` - FastAPI dependency for permission checks
  - `require_role` - FastAPI dependency for role checks
  - Context-aware authorization

---

## Project Structure

```
src/fastauth/
├── api/
│   ├── router.py         # Auth endpoints (signup, login, logout)
│   └── dependencies.py    # FastAPI dependencies
├── core/
│   ├── manager.py        # AuthManager orchestration
│   ├── config.py         # AuthConfig settings
│   ├── models.py        # Request/response models
│   └── types.py         # Type definitions
├── sessions/
│   ├── base.py          # SessionStore protocol
│   ├── memory.py        # In-memory implementation
│   ├── redis.py        # Redis implementation
│   └── sql.py           # SQL database implementation
├── strategies/
│   ├── base.py         # AuthStrategy protocol
│   ├── jwt.py          # JWT implementation
│   └── opaque.py       # Opaque token implementation
├── authorization/
│   ├── base.py         # RBAC/ABAC protocols (Role, Permission, ABACPolicy, RoleStore)
│   ├── engine.py       # Authorization engine
│   ├── dependencies.py # FastAPI authorization dependencies
│   └── stores/
│       ├── memory.py   # In-memory authorization store
│       └── sql.py      # SQL authorization store
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
from fastauth import AuthManager, AuthConfig
from fastauth.sessions import MemorySessionStore
from fastauth.strategies import JWTStrategy
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

## Authorization Examples

### RBAC Only (Role-Based Access Control)

```python
from fastapi import FastAPI, Depends
from fastauth import AuthManager, AuthConfig
from fastauth.authorization import (
    MemoryRoleStore,
    AuthorizationEngine,
    Role,
    Permission,
    require_role,
)

# Define roles with permissions
admin_role = Role(name="admin", permissions=[Permission.ADMIN, Permission.READ, Permission.WRITE])
user_role = Role(name="user", permissions=[Permission.READ])

# Create role store with default roles
role_store = MemoryRoleStore(default_roles=[admin_role, user_role])

# Create authorization engine
authorization = AuthorizationEngine(role_store=role_store)

# Configure auth with RBAC enabled
config = AuthConfig(
    slug="myapp",
    secret="your-secret-key",
    login_fields=["email"],
    rbac={"enabled": True, "default_roles": ["admin", "user"]},
)

# Create auth manager
auth = AuthManager(
    config=config,
    user_store=YourUserStore(),
    session_store=MemorySessionStore(),
    strategy=JWTStrategy(secret="your-secret-key"),
    schema=User,
    role_store=role_store,
    authorization_engine=authorization,
)

# Assign role to user
await role_store.assign_role("user_123", "admin")

# Use in FastAPI endpoints
@app.get("/admin")
async def admin_endpoint(user = Depends(require_role(auth, "admin"))):
    return {"message": "Welcome, admin!"}
```

### ABAC Only (Attribute-Based Access Control)

```python
from fastapi import FastAPI, Depends
from fastauth import AuthManager, AuthConfig
from fastauth.authorization import (
    MemoryRoleStore,
    AuthorizationEngine,
    ABACPolicy,
    require_permission,
)

# Create role store (required for ABAC context)
role_store = MemoryRoleStore()

# Create ABAC policies
engineering_policy = ABACPolicy(
    name="engineering_access",
    effect="allow",
    actions=["read", "write"],
    resources=["docs:*"],
    conditions={"user.department": "engineering"},
)

# Create authorization engine with policies
authorization = AuthorizationEngine(
    role_store=role_store,
    policies=[engineering_policy],
)

# Configure auth with ABAC enabled
config = AuthConfig(
    slug="myapp",
    secret="your-secret-key",
    login_fields=["email"],
    abac={"enabled": True},
)

# Create auth manager
auth = AuthManager(
    config=config,
    user_store=YourUserStore(),
    session_store=MemorySessionStore(),
    strategy=JWTStrategy(secret="your-secret-key"),
    schema=User,
    role_store=role_store,
    authorization_engine=authorization,
)

# Use in FastAPI endpoints with context
def get_resource_context():
    return {"resource": "docs:api", "user": {"department": "engineering"}}

@app.get("/docs")
async def docs_endpoint(
    user = Depends(require_permission(auth, Permission.READ, get_resource_context))
):
    return {"message": "Engineering docs"}
```

### Combined RBAC + ABAC

```python
from fastapi import FastAPI, Depends
from fastauth import AuthManager, AuthConfig
from fastauth.authorization import (
    MemoryRoleStore,
    AuthorizationEngine,
    Role,
    Permission,
    ABACPolicy,
    require_permission,
    require_role,
)

# Define roles
admin_role = Role(name="admin", permissions=[Permission.ADMIN])
viewer_role = Role(name="viewer", permissions=[Permission.READ])

# Create role store
role_store = MemoryRoleStore(default_roles=[admin_role, viewer_role])

# Create policies for fine-grained control
premium_policy = ABACPolicy(
    name="premium_feature",
    effect="allow",
    actions=["access"],
    resources=["premium:*"],
    conditions={"user.subscription": "premium"},
)

deny_contractor = ABACPolicy(
    name="deny_contractor",
    effect="deny",
    actions=["*"],
    resources=["admin:*"],
    conditions={"user.type": "contractor"},
)

# Create authorization engine with RBAC + ABAC
authorization = AuthorizationEngine(
    role_store=role_store,
    policies=[premium_policy, deny_contractor],
)

# Configure auth with both RBAC and ABAC enabled
config = AuthConfig(
    slug="myapp",
    secret="your-secret-key",
    login_fields=["email"],
    rbac={"enabled": True},
    abac={"enabled": True},
)

# Create auth manager
auth = AuthManager(
    config=config,
    user_store=YourUserStore(),
    session_store=MemorySessionStore(),
    strategy=JWTStrategy(secret="your-secret-key"),
    schema=User,
    role_store=role_store,
    authorization_engine=authorization,
)

# Use both role and permission checks
@app.get("/admin")
async def admin_endpoint(user = Depends(require_role(auth, "admin"))):
    return {"message": "Admin panel"}

@app.get("/premium")
async def premium_endpoint(user = Depends(require_permission(auth, Permission.ADMIN))):
    return {"message": "Premium content"}
```

### SQL Role Store (Production)

```python
from fastauth.authorization.stores import SQLRoleStore
from fastauth.authorization import AuthorizationEngine, Role

# Define your SQLAlchemy models
class RoleModel(Base):
    __tablename__ = "roles"
    name = Column(String, primary_key=True)
    permissions = Column(JSON)

class UserRoleModel(Base):
    __tablename__ = "user_roles"
    id = Column(Integer, primary_key=True)
    user_id = Column(String, index=True)
    role_name = Column(String, ForeignKey("roles.name"))
    attributes = Column(JSON)

# Create SQL role store
role_store = SQLRoleStore(
    role_model=RoleModel,
    user_role_model=UserRoleModel,
    db_session=db_session,
)

# Create authorization engine
authorization = AuthorizationEngine(role_store=role_store)
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
- **Phase 2**: ✅ Complete - RBAC/ABAC Authorization
- **Phase 3-9**: 🔄 Planned - See TODO.md for roadmap

---

## Next Steps (Phase 3+)

- OAuth providers (Google, GitHub)
- Magic link login
- MFA (TOTP, WebAuthn/passkeys)
- Multi-tenancy
- Rate limiting
- Advanced audit logging
