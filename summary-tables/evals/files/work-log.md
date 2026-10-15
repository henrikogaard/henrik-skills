# Work log — issue #88 "CSV import for members"

Acceptance criteria on #88:
1. Admin can upload a CSV of members.
2. Rows with errors are listed with the row number and reason.
3. Duplicate emails are skipped, not imported twice.
4. Import of 5,000 rows finishes in under 30 s.

What happened today:
- Added `src/import/parseCsv.ts` and `src/import/importMembers.ts`. Upload route `POST /admin/import` wired in `src/routes/admin.ts`.
- `ImportErrors.tsx` shows failing rows with row number + reason. Checked by hand in the browser at /admin/import with a broken file.
- Duplicate emails: wrote the check in `importMembers.ts`, but the unit test `skips duplicate emails` is failing (expects 2 imported, got 3). Not fixed yet.
- Perf: haven't run the 5,000-row test; the seed script for big files isn't written.
- Tests: `npm test` → 41 passed, 1 failed (the duplicate test). Typecheck clean.
- Committed as `9f3e2a1` on branch `feature/88-csv-import`, pushed. Draft PR #93 open, CI running.
- Left out on purpose: `scratch/members-sample.csv` (has real emails), not committed.
