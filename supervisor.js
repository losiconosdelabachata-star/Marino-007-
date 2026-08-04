/**
 * Runs the three long-lived Marino 007 processes inside one container:
 *
 *   1. WhatsApp bridge   (Baileys, port 3010)
 *   2. Dashboard         (Next.js, port 3003 - the port Render routes to)
 *   3. Blog scheduler    (Python daemon)
 *
 * Render gives a container one command, and a bare `npm start` would leave
 * the bridge and scheduler unstarted. This keeps all three alive, restarts
 * whichever dies, and takes the container down if one refuses to stay up so
 * the failure is visible instead of silent.
 */

const { spawn } = require('child_process');

const PROCS = [
  {
    name: 'whatsapp',
    cmd: 'node',
    args: ['whatsapp_server.js'],
    critical: true,
  },
  {
    name: 'dashboard',
    cmd: 'npm',
    args: ['start'],
    cwd: 'shopify-affiliates',
    critical: true,
  },
  {
    name: 'blog',
    cmd: 'python3',
    args: ['blog_scheduler.py', '--daemon'],
    // The blog engine is blocked on Google billing; if it can't start we
    // still want orders and the dashboard serving.
    critical: false,
  },
];

const MAX_RESTARTS = 5;
const RESTART_WINDOW_MS = 60_000;

const state = new Map();

function log(name, msg) {
  console.log(`[${new Date().toISOString()}] [${name}] ${msg}`);
}

function start(proc) {
  const s = state.get(proc.name) || { restarts: 0, first: Date.now() };
  state.set(proc.name, s);

  log(proc.name, `starting: ${proc.cmd} ${proc.args.join(' ')}`);

  const child = spawn(proc.cmd, proc.args, {
    cwd: proc.cwd ? `${__dirname}/${proc.cwd}` : __dirname,
    env: process.env,
    stdio: 'inherit',
    shell: process.platform === 'win32',
  });

  child.on('exit', (code, signal) => {
    log(proc.name, `exited (code=${code} signal=${signal})`);

    // Reset the counter if it had been stable for a while.
    if (Date.now() - s.first > RESTART_WINDOW_MS) {
      s.restarts = 0;
      s.first = Date.now();
    }

    s.restarts += 1;

    if (s.restarts > MAX_RESTARTS) {
      log(proc.name, `crash-looping (${s.restarts} restarts)`);
      if (proc.critical) {
        log('supervisor', 'critical process is crash-looping - exiting');
        process.exit(1);
      }
      log(proc.name, 'non-critical, giving up on it');
      return;
    }

    const delay = Math.min(1000 * 2 ** (s.restarts - 1), 30_000);
    log(proc.name, `restarting in ${delay / 1000}s`);
    setTimeout(() => start(proc), delay);
  });

  child.on('error', (err) => log(proc.name, `spawn error: ${err.message}`));
  return child;
}

for (const signal of ['SIGTERM', 'SIGINT']) {
  process.on(signal, () => {
    log('supervisor', `${signal} - shutting down`);
    process.exit(0);
  });
}

log('supervisor', 'Marino 007 starting');
PROCS.forEach(start);
