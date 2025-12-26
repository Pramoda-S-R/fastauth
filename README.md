### stuff I plan to add
- [ ] oauth (multiple providers with challenge flow)
- [ ] refresh detection
- [ ] reuse detection
- [ ] rate limiting (per ip, per user)
- [ ] track user agent (httpagentparser)
- [ ] track ip address (X-Forwarded-For, X-Real-IP)
- [ ] track device fingerprint (soft, {useragent, lang, timezone, device}, sha256("|".join(material)))
- [ ] track last activity
- [ ] track created at
- [ ] __Host-access cookie
- [ ] __Host-refresh cookie
- [ ] csrf cookie (double submit cookie in request must match header)
- [ ] session_hint cookie (lightweight session identifier)
- [ ] sso (single sign-on for azure, google, etc.,)
- [ ] magic link (email with link to login)
- [ ] One user → many identities (multiple oauth accounts linked to one user)
- [ ] rbac (role based access control)
- [ ] abac (attribute based access control)
- [ ] resource scoped permissions
- [ ] multi tenant
- [ ] multi factor authentication (email, sms, totp, webauthn)
- [ ] audit logger
- [ ] key rotation (.well-known/jwks.json)

```
Auth
 ├─ SessionManager (required)
 ├─ TokenStrategy (JWT / Opaque)
 ├─ Store (Redis / Memory / Custom)
 ├─ IdentityProvider
 ├─ AuthorizationEngine
 ├─ AuditEmitter
 └─ SecuritySignals
```

### Issues
- [ ] redis set contains expired keys need a batch job or something to clean them up
- [ ] not tracking user agent and other device fingerprint information
- [ ] not implemented jti rotation on refresh
- [ ] can't decide if a token store is required or not for reuse and replay detection
- [ ] need to implement csrf protection and session_hint cookie

