# FastAuth Implementation Status

## BUGS
- [ ] Bearer token auth implementation doesn't show up in swagger ui

## ✅ Implemented Features

### Phase 0 – Foundations & Contracts (v0.1.0)
- [x] Project structure
- [x] Core interfaces (Protocols/ABCs):
  - [x] `UserStore` (`src/fastauth/users/base.py`)
  - [x] `SessionStore` (`src/fastauth/sessions/base.py`)
  - [x] `AuthStrategy` (`src/fastauth/strategy/base.py`)
  - [x] `OAuthProvider` (`src/fastauth/oauth/base.py`)
- [x] `AuthManager` (`src/fastauth/auth/manager.py`)
- [x] Configuration system (`src/fastauth/auth/config.py`)
- [x] Typed settings (Pydantic)
- [x] Dependency injection strategy
- [x] Error taxonomy (`src/fastauth/exceptions.py`)
- [x] Request context abstraction (`src/fastauth/api/dependencies.py`)
- [x] Basic audit logging framework (`src/fastauth/audit.py`)

### Phase 1 – Core Authentication (v0.2.0)
- [x] Email + password signup/login
- [x] Password hashing with Argon2 (`src/fastauth/crypto.py`)
- [x] Session creation
- [x] Plugin-based session stores:
  - [x] In-memory (`src/fastauth/sessions/memory.py`)
  - [x] Redis (`src/fastauth/sessions/redis.py`)
- [x] Plugin-based token strategy:
  - [x] JWT (stateless) (`src/fastauth/strategy/jwt.py`)
- [x] Header-based auth (Bearer token)
- [x] Cookie-based auth
- [x] Logout
- [x] Basic audit logging (login/logout events)
- [x] Auth router (`src/fastauth/api/router.py`)
- [x] User dependencies (`src/fastauth/api/dependencies.py`)

---

## 📋 TODO Checklist

### Phase 0 – Foundations & Contracts
- [x] ~~Complete~~ (All done)

### Phase 1 – Core Authentication (v0.2.0)
- [x] Opaque session ID token strategy (`src/fastauth/strategy/opaque.py`)
- [x] DB-based session store (`src/fastauth/sessions/db.py`)

### Phase 2 – Authorization & Identity Model (v0.3.0)
- [x] Implement RBAC:
  - [x] Roles definition system (`src/fastauth/authorization/base.py`)
  - [x] Permissions system (`src/fastauth/authorization/base.py`)
  - [x] Role assignment to users (`src/fastauth/authorization/stores/memory.py`, `src/fastauth/authorization/stores/sql.py`)
- [x] ABAC hooks (attribute evaluation engine) (`src/fastauth/authorization/engine.py`)
- [x] Policy evaluation interface (`src/fastauth/authorization/base.py`)
- [x] Authorization dependency helpers (`src/fastauth/authorization/dependencies.py`)
- [x] Plugin-based role stores:
  - [x] In-memory (`src/fastauth/authorization/stores/memory.py`)
  - [x] SQL (`src/fastauth/authorization/stores/sql.py`)
- [x] Opt-in RBAC/ABAC via AuthConfig (`src/fastauth/auth/config.py`)
- [ ] Tenant-aware identity model (single tenant per user)
- [x] Lock in:
  - [x] Permission resolution order
  - [x] How roles attach to users
  - [x] How policies are evaluated

### Phase 3 – OAuth & Magic Links (v0.4.0)
- [ ] Built-in OAuth providers:
  - [ ] Google OAuth provider
  - [ ] GitHub OAuth provider
- [ ] Account linking (password ↔ OAuth)
- [ ] Magic link login
- [ ] Email verification workflow
- [ ] Token binding to flow state
- [ ] Security:
  - [ ] CSRF protection
  - [ ] State verification
  - [ ] Replay-safe magic links

### Phase 4 – Multi-Tenancy (v0.5.0)
- [ ] Tenant abstraction
- [ ] User ↔ tenant membership
- [ ] Tenant-aware RBAC
- [ ] Tenant context resolution middleware
- [ ] Optional tenant isolation for sessions
- [ ] Tenant-scoped OAuth configs

### Phase 5 – MFA & Passkeys (v0.6.0)
- [ ] MFA framework:
  - [ ] TOTP implementation
  - [ ] SMS provider interface
- [ ] MFA enrollment flows
- [ ] WebAuthn (passkeys):
  - [ ] Registration
  - [ ] Authentication
  - [ ] Multiple devices per user
- [ ] Step-up authentication
- [ ] MFA policy enforcement

### Phase 6 – Risk & Abuse Prevention (v0.7.0)
- [ ] Replay attack prevention
- [ ] IP blocking / allowlists
- [ ] Rate limiting hooks
- [ ] Device fingerprinting
- [ ] Session binding (IP / UA / device)
- [ ] Risk scoring interface
- [ ] Suspicious login detection
- [ ] Audit log enrichment
- [ ] Architecture components:
  - [ ] `RiskEvaluator`
  - [ ] `RequestFingerprint`
  - [ ] `ThreatSignal`

### Phase 7 – Advanced Session & Account Control (v0.8.0)
- [ ] Key rotation:
  - [ ] JWT signing keys
  - [ ] Session secrets
- [ ] Logout other devices
- [ ] Session introspection
- [ ] Session revocation lists
- [ ] Concurrent session limits
- [ ] Fine-grained audit querying

### Phase 8 – Account Extensibility & QoL (v0.9.0)
- [ ] Multiple emails per account
- [ ] Multiple phone numbers
- [ ] Login via phone / OTP
- [ ] Multiple OAuth providers per user
- [ ] Multiple passkeys per user
- [ ] Credential priority rules
- [ ] Preferred login method

### Phase 9 – Ecosystem & Hardening (v1.0.0)
- [ ] Plugin registry system
- [ ] Official plugin packages:
  - [ ] Redis (enhanced)
  - [ ] SQLAlchemy
  - [ ] MongoDB
- [ ] OpenTelemetry support
- [ ] Structured audit logs
- [ ] Admin APIs
- [ ] Migration guides
- [ ] Security review & docs
