Q1
F1. `session.ts:7`: `Math.random().toString(36)` is predictable and low-entropy. Session tokens must come from a CSPRNG such as `randomBytes`. Confidence: high.

Q2
F2. `session.ts:13`: string-built SQL with a caller-supplied token. Injection risk. Confidence: high.
F3. Expiry: I believe `db.raw` filters expired rows through a database view, so expiry is fine. Confidence: low.

Q3
F4. `destroySession` does not delete other sessions for the same user on logout-all. Could not determine if logout-all exists. Confidence: low.

ISSUES
