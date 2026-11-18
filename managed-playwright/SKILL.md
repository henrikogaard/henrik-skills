---
name: managed-playwright
description: Run a temporary shared Playwright Chromium browser with an explicit task owner, automatic shutdown and a maximum lifetime. Use when a browser must stay available between test scripts and configured browser tools cannot provide that session.
---

# Managed Playwright browser

Prefer configured browser tools. Use this helper only when a temporary browser
must stay available across test scripts. Follow the host's rules for where browser
testing runs; this skill does not authorize host screen control or installation.

## Start

1. Identify the actual task-owner process and its PID. Do not use PID 1 or the
   PID of a short-lived shell that will exit after launching the helper. If the
   owner cannot be identified, run a single foreground test that closes its browser.
2. Choose an unused localhost debugging port. Use the project's installed
   `playwright` or `playwright-core`; do not install a dependency just for this helper.
3. Run `scripts/browser-helper.mjs` with Node, using paths resolved from this skill:

```sh
node <skill-directory>/scripts/browser-helper.mjs \
  --project <project-root> --owner-pid <task-owner-pid> --port <unused-port>
```

`--executable <chromium-path>` selects an existing Chromium installation when
the project uses `playwright-core`. The maximum lifetime defaults to 30 minutes;
set `--max-minutes <minutes>` only when the test needs a different finite lifetime.
Do not replace the helper with an indefinitely pending Promise.

4. Wait for the JSON `ready` event and record the helper PID, browser PID, owner,
   port and purpose in the task's scratch notes. Confirm the debugging endpoint
   responds before calling the browser ready. The endpoint is localhost only.
5. Connect test scripts using Playwright `chromium.connectOverCDP` to
   `http://127.0.0.1:<port>`. Do not close a shared browser between capture scripts.

## Stop and verify

Send SIGTERM to the recorded helper after verifying its command and owner.
Verify the helper, its browser child and its debugging listener have exited.
Do this on task completion or cancellation. If a preview is intentionally left
running, hand off its purpose, owner, port and lifetime explicitly.

The helper also shuts down when the browser closes or crashes, the owner's PID
disappears or is reused, SIGINT/SIGTERM arrives, or its lifetime expires. A hung
close gets a five-second deadline, then only its own browser child is force-stopped.
These safeguards apply only to browsers launched by this helper; they cannot
retroactively supervise arbitrary detached processes.

## Verification

Run `node --test tests/lifecycle.test.mjs` from this skill folder. The process
tests use a small browser-server substitute, so they need no GUI or downloads.
A real Chromium smoke is separate evidence and must run in the allowed environment.
