Q1
F1. `session.ts:7` uses `Math.random()` for the session token. Not cryptographically secure and short (~11 chars). Use `randomBytes(32)`. Confidence: high.

Q2
F2. `session.ts:13` interpolates `token` into raw SQL. SQL injection: a crafted token reads any session. Use a parameterized query. Confidence: high.
F3. `getSession` does not check `expiresAt`, so expired sessions stay valid. Confidence: high.

Q3
F4. `SESSION_TTL_MS` is 30 days; long for a login session. Consider shorter with refresh. Confidence: medium.
F5. `newCsrfToken` should use `crypto.subtle` instead of `randomBytes`. Confidence: low.

ISSUES
