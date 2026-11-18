#!/usr/bin/env node
// A task-owned, bounded Playwright browser. Never starts or stops shared browsers.
import { execFile } from 'node:child_process';
import { createRequire } from 'node:module';
import path from 'node:path';
import { parseArgs, promisify } from 'node:util';

const exec = promisify(execFile);
const { values } = parseArgs({ options: {
  project: { type: 'string' },
  'owner-pid': { type: 'string' },
  port: { type: 'string' },
  'max-minutes': { type: 'string', default: '30' },
  executable: { type: 'string' },
} });
const ownerPid = Number(values['owner-pid']);
const port = Number(values.port);
const lifetime = Number(values['max-minutes']) * 60000;
if (!values.project || !Number.isInteger(ownerPid) || ownerPid <= 1 || ownerPid === process.pid ||
    !Number.isInteger(port) || port < 1024 || port > 65535 ||
    !Number.isFinite(lifetime) || lifetime < 1 || lifetime > 2147483647) {
  console.error('Usage: browser-helper.mjs --project <project-root> --owner-pid <task-pid> --port <1024..65535> [--max-minutes 30] [--executable <chromium>]');
  process.exit(1);
}

async function ownerIdentity() {
  try {
    process.kill(ownerPid, 0);
    const { stdout } = await exec('ps', ['-p', String(ownerPid), '-o', 'lstart=', '-o', 'stat='],
                                 { timeout: 1000 });
    const identity = stdout.trim();
    return !identity || /\bZ\S*$/.test(identity) ? null : identity;
  } catch { return null; }
}

const identity = await ownerIdentity();
if (!identity) {
  console.error('The owning task is not running; no browser started.');
  process.exit(1);
}
// Process state changes as the owner works. Only its start time identifies it.
const startedAt = identity.split(/\s+/).slice(0, 5).join(' ');
let server, stopping = false, poll, deadline, checking = false;
let stopRequested;
const pendingStop = new Promise(resolve => { stopRequested = resolve; });
const report = event => console.log(JSON.stringify({ ...event, pid: process.pid }));

function requestStop(reason) {
  if (!stopping) { stopping = true; stopRequested(reason); }
}
process.once('SIGTERM', () => requestStop('SIGTERM'));
process.once('SIGINT', () => requestStop('SIGINT'));
deadline = setTimeout(() => requestStop('lifetime-expired'), lifetime);
poll = setInterval(async () => {
  if (checking || stopping) return;
  checking = true;
  const current = await ownerIdentity();
  checking = false;
  if (!current || current.split(/\s+/).slice(0, 5).join(' ') !== startedAt)
    requestStop('owner-exited');
}, 1000);

try {
  const require = createRequire(path.join(path.resolve(values.project), 'package.json'));
  let chromium;
  try { ({ chromium } = require('playwright')); }
  catch (error) {
    if (error.code !== 'MODULE_NOT_FOUND') throw error;
    ({ chromium } = require('playwright-core'));
  }
  // The server exposes its child process, so a hung graceful close has a scoped fallback.
  server = await chromium.launchServer({
    host: '127.0.0.1',
    headless: true,
    handleSIGINT: false, handleSIGTERM: false, handleSIGHUP: true,
    ...(values.executable ? { executablePath: path.resolve(values.executable) } : {}),
    args: [`--remote-debugging-port=${port}`, '--remote-debugging-address=127.0.0.1'],
    timeout: 15000,
  });
  server.once('close', () => requestStop('browser-disconnected'));
  const browserProcess = server.process();
  if (browserProcess.exitCode !== null || browserProcess.signalCode !== null)
    requestStop('browser-disconnected');
  if (!stopping) report({ event: 'ready', browserPid: browserProcess.pid, ownerPid, port });
  const reason = await pendingStop;
  clearInterval(poll);
  clearTimeout(deadline);
  report({ event: 'stopping', reason });
  // Keep the deadline active even if browser.close never settles.
  const fallback = setTimeout(() => {
    if (browserProcess.exitCode === null && browserProcess.signalCode === null)
      browserProcess.kill('SIGKILL');
    process.exit(1);
  }, 5000);
  await server.close();
  clearTimeout(fallback);
  process.exit(0);
} catch (error) {
  clearInterval(poll);
  clearTimeout(deadline);
  // Playwright handles failed launch cleanup; an established browser is our own child.
  const child = server?.process();
  if (child && child.exitCode === null && child.signalCode === null) child.kill('SIGKILL');
  console.error(error.message);
  process.exit(1);
}
