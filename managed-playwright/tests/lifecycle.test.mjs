import assert from 'node:assert/strict';
import { spawn, spawnSync } from 'node:child_process';
import { once } from 'node:events';
import { mkdtemp, mkdir, writeFile, rm } from 'node:fs/promises';
import os from 'node:os';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import test from 'node:test';

const helper = fileURLToPath(new URL('../scripts/browser-helper.mjs', import.meta.url));
const runtime = process.env.HELPER_RUNTIME || process.execPath;
const sleep = ms => new Promise(resolve => setTimeout(resolve, ms));
function alive(pid) {
  try { process.kill(pid, 0); return true; } catch { return false; }
}

test('rejects an unowned helper before loading a browser', () => {
  const result = spawnSync(runtime, [helper, '--project', os.tmpdir(),
    '--owner-pid', '1', '--port', '19439'], { encoding: 'utf8', timeout: 3000 });
  assert.equal(result.status, 1);
  assert.doesNotMatch(result.stdout, /ready/);
  assert.match(result.stderr, /owner-pid/);
});

async function launch(t, { minutes = 5, hangClose = false } = {}) {
  const project = await mkdtemp(path.join(os.tmpdir(), 'managed-playwright-test-'));
  await mkdir(path.join(project, 'node_modules/playwright-core'), { recursive: true });
  await writeFile(path.join(project, 'package.json'), '{}');
  await writeFile(path.join(project, 'browser.cjs'),
    'setInterval(() => {}, 1000); process.send("ready");');
  await writeFile(path.join(project, 'node_modules/playwright-core/index.js'), `
const { fork } = require('node:child_process');
const { once, EventEmitter } = require('node:events');
exports.chromium = { async launchServer() {
  const child = fork(${JSON.stringify(path.join(project, 'browser.cjs'))}, [], {
    execPath: ${JSON.stringify(process.execPath)}, stdio: ['ignore', 'ignore', 'ignore', 'ipc']
  });
  await once(child, 'message');
  const server = new EventEmitter();
  child.once('exit', () => server.emit('close'));
  server.process = () => child;
  server.close = async () => {
    if (process.env.FAKE_CLOSE_HANG) return new Promise(() => {});
    if (child.exitCode !== null || child.signalCode !== null) return;
    const exited = once(child, 'exit');
    child.kill('SIGTERM');
    await exited;
  };
  return server;
} };
`);
  const owner = spawn(process.execPath, ['-e', 'setInterval(() => {}, 1000)'], { stdio: 'ignore' });
  const child = spawn(runtime, [helper, '--project', project, '--owner-pid', String(owner.pid),
    '--port', '19439', '--max-minutes', String(minutes)], {
    env: { ...process.env, ...(hangClose ? { FAKE_CLOSE_HANG: '1' } : {}) },
    stdio: ['ignore', 'pipe', 'pipe'],
  });
  let stdout = '', stderr = '', browserPid;
  const exited = once(child, 'exit');
  child.stdout.on('data', chunk => { stdout += chunk; });
  child.stderr.on('data', chunk => { stderr += chunk; });
  t.after(async () => {
    for (const pid of [browserPid, child.pid, owner.pid]) {
      if (pid && alive(pid)) process.kill(pid, 'SIGKILL');
    }
    await rm(project, { recursive: true, force: true });
  });
  for (let attempt = 0; attempt < 150; attempt++) {
    const ready = stdout.split('\n').filter(Boolean).map(line => JSON.parse(line))
      .find(event => event.event === 'ready');
    if (ready) { browserPid = ready.browserPid; break; }
    if (child.exitCode !== null) assert.fail(`Helper exited before ready: ${stderr}`);
    await sleep(20);
  }
  assert.ok(browserPid, `Helper did not become ready: ${stderr}`);
  return { child, owner, browserPid, exited, output: () => stdout };
}

for (const signal of ['SIGTERM', 'SIGINT']) {
  test(`${signal} closes only its browser and exits`, { timeout: 10000 }, async t => {
    const run = await launch(t);
    run.child.kill(signal);
    assert.deepEqual(await run.exited, [0, null]);
    assert.equal(alive(run.browserPid), false);
    assert.equal(alive(run.owner.pid), true);
  });
}

test('browser exit ends the helper instead of keeping it alive', { timeout: 10000 }, async t => {
  const run = await launch(t);
  process.kill(run.browserPid, 'SIGTERM');
  assert.deepEqual(await run.exited, [0, null]);
  assert.match(run.output(), /browser-disconnected/);
  assert.equal(alive(run.owner.pid), true);
});

test('owner exit closes its browser and helper', { timeout: 10000 }, async t => {
  const run = await launch(t);
  run.owner.kill('SIGTERM');
  assert.deepEqual(await run.exited, [0, null]);
  assert.equal(alive(run.browserPid), false);
  assert.match(run.output(), /owner-exited/);
});

test('maximum lifetime closes the browser with a live owner', { timeout: 10000 }, async t => {
  const run = await launch(t, { minutes: 0.01 });
  assert.deepEqual(await run.exited, [0, null]);
  assert.equal(alive(run.browserPid), false);
  assert.equal(alive(run.owner.pid), true);
  assert.match(run.output(), /lifetime-expired/);
});

test('a hung close forcibly stops only its own browser', { timeout: 12000 }, async t => {
  const run = await launch(t, { hangClose: true });
  run.child.kill('SIGTERM');
  assert.deepEqual(await run.exited, [1, null]);
  for (let n = 0; n < 50 && alive(run.browserPid); n++) await sleep(20);
  assert.equal(alive(run.browserPid), false);
  assert.equal(alive(run.owner.pid), true);
});
