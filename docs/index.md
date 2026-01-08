# High-Level Architecture Principles (Before Phases)

These influence every phase:

### 1. Everything Is an Interface

Define **protocols / ABCs** early for:

* Identity store
* Credential verifiers
* Session store
* Token strategy
* MFA provider
* Audit sink
* Risk engine

Concrete implementations come later.

### 2. Feature Flags, Not Branching Logic

Every “advanced” feature should be:

* Disabled by default
* Registered explicitly
* Injectable via dependency container

### 3. Auth Is a Pipeline

Request → identity resolution → credential verification → risk checks → session issuance → audit

---

# Phase Breakdown & Release Timeline

## **Phase 0 – Foundations & Contracts**

📦 **v0.1.0 – Internal Alpha (Not for Public Use)**

> Goal: define the *shape* of the system, not features

### Deliverables

* Project structure
* Core interfaces (no real auth yet)
* Configuration system
* Dependency injection strategy
* Error taxonomy

### Features

* `AuthManager`
* Protocols / ABCs:

  * `UserStore`
  * `CredentialVerifier`
  * `SessionStore`
  * `TokenStrategy`
  * `AuditLogger`
* Request context abstraction
* Typed settings (Pydantic)
* Minimal middleware integration
* No FastAPI routes yet

### Why This Matters

This phase decides whether your project survives long-term.
Breaking changes are expected here.

---

## **Phase 1 – Core Authentication (Password + Sessions)**

📦 **v0.2.0 – Public Alpha**

> Goal: usable, boring, reliable auth

### Features

* Email + password signup/login
* Password hashing (argon2/bcrypt)
* Session creation
* Plugin-based session stores:

  * In-memory
  * Redis
* Plugin-based token strategy:

  * JWT (stateless)
  * Opaque session ID
* Header-based auth
* Cookie-based auth
* Logout
* Basic audit logging (login, logout)

### Explicitly Excluded

* OAuth
* MFA
* Multi-tenant
* RBAC
* Risk mitigation

### API Stability

* **SessionStore & TokenStrategy APIs become stable**
* Breaking changes discouraged after this

---

## **Phase 2 – Authorization & Identity Model**

📦 **v0.3.0 – Beta**

> Goal: define *who* the user is and *what* they can do

### Features

* Core user model abstraction
* RBAC:

  * Roles
  * Permissions
* ABAC hooks (attribute evaluation engine)
* Policy evaluation interface
* Authorization dependency helpers for FastAPI
* Tenant-aware identity model (single tenant per user for now)

### Key Decisions Locked In

* Permission resolution order
* How roles attach to users
* How policies are evaluated

---

## **Phase 3 – OAuth & Magic Links**

📦 **v0.4.0 – Beta**

> Goal: modern login flows without increasing core complexity

### Features

* OAuth provider interface
* Built-in OAuth providers:

  * Google
  * GitHub
* Account linking (password ↔ oauth)
* Magic link login
* Email verification workflow
* Token binding to flow state

### Security

* CSRF protection
* State verification
* Replay-safe magic links

---

## **Phase 4 – Multi-Tenancy**

📦 **v0.5.0 – Beta**

> Goal: SaaS-ready identity isolation

### Features

* Tenant abstraction
* User ↔ tenant membership
* Tenant-aware RBAC
* Tenant context resolution middleware
* Optional tenant isolation for sessions
* Tenant-scoped OAuth configs

### Important

This is where **data modeling becomes expensive to change**.
After this version, backward compatibility matters.

---

## **Phase 5 – MFA & Passkeys**

📦 **v0.6.0 – RC**

> Goal: strong authentication without breaking ergonomics

### Features

* MFA framework:

  * TOTP
  * SMS (via provider interface)
* MFA enrollment flows
* WebAuthn (passkeys):

  * Registration
  * Authentication
  * Multiple devices per user
* Step-up authentication
* MFA policy enforcement

### Design Focus

* MFA as a *challenge pipeline*, not a boolean
* Passkeys as first-class credentials

---

## **Phase 6 – Risk & Abuse Prevention**

📦 **v0.7.0 – RC**

> Goal: prevent service-level attacks

### Features

* Replay attack prevention
* IP blocking / allowlists
* Rate limiting hooks
* Device fingerprinting
* Session binding (IP / UA / device)
* Risk scoring interface
* Suspicious login detection
* Audit log enrichment

### Architecture

Introduce:

* `RiskEvaluator`
* `RequestFingerprint`
* `ThreatSignal`

---

## **Phase 7 – Advanced Session & Account Control**

📦 **v0.8.0 – Stable**

> Goal: account safety & UX polish

### Features

* Key rotation:

  * JWT signing keys
  * Session secrets
* Logout other devices
* Session introspection
* Session revocation lists
* Concurrent session limits
* Fine-grained audit querying

---

## **Phase 8 – Account Extensibility & QoL**

📦 **v0.9.0 – Stable**

> Goal: user convenience features without core risk

### Features

* Multiple emails per account
* Multiple phone numbers
* Login via phone / OTP
* Multiple OAuth providers per user
* Multiple passkeys per user
* Credential priority rules
* Preferred login method

---

## **Phase 9 – Ecosystem & Hardening**

📦 **v1.0.0 – Stable Release**

> Goal: production-ready, extensible auth platform

### Features

* Plugin registry system
* Official plugin packages:

  * Redis
  * SQLAlchemy
  * Mongo
* OpenTelemetry support
* Structured audit logs
* Admin APIs
* Migration guides
* Security review & docs

---

# Versioning Strategy

| Version | Stability         |
| ------- | ----------------- |
| 0.1–0.2 | Experimental      |
| 0.3–0.6 | Beta              |
| 0.7–0.9 | Release Candidate |
| 1.0+    | Stable            |

---

# Key Points

1. **Do NOT bake storage decisions into auth logic**
2. **Never assume user = human**
3. **Avoid “if mfa_enabled” flags — use challenges**
4. **Auth bugs come from coupling, not crypto**
5. **Audit logging should be impossible to bypass**

