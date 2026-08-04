import { spawn, ChildProcess } from 'child_process';
import path from 'path';

/**
 * Runs the ops scripts and keeps their output.
 *
 * The first version spawned detached with stdio:'ignore', so a click produced
 * a toast and nothing else - a script could fail immediately and the dashboard
 * would still look like it had worked. Output is captured here so the UI can
 * show what actually happened.
 */

export type JobState = 'running' | 'succeeded' | 'failed';

export interface Job {
  id: string;
  action: string;
  label: string;
  state: JobState;
  startedAt: string;
  finishedAt: string | null;
  exitCode: number | null;
  output: string[];
}

/** Strict allowlist: the client sends an action id, never a command. */
export const ACTIONS: Record<
  string,
  { cmd: string; args: string[]; label: string; danger?: string }
> = {
  'blog:run': {
    cmd: 'python',
    args: ['blog_scheduler.py', '--once'],
    label: 'Generate & publish blog post',
    danger: 'Emails your full customer list',
  },
  'orders:sweep': {
    cmd: 'python',
    args: ['order_automation.py', '--once'],
    label: 'Sweep Shopify for new orders',
    danger: 'Sends unfulfilled orders to Printify',
  },
  // Real script files, not `python -c`. Inline code gets mangled by the
  // Windows shell's re-quoting and dies with a SyntaxError.
  'whatsapp:test': {
    cmd: 'python',
    args: ['ops_test_whatsapp.py'],
    label: 'Send test WhatsApp message',
  },
  'shopify:orders': {
    cmd: 'python',
    args: ['ops_list_orders.py'],
    label: 'List unfulfilled orders',
  },
  'photos:check': {
    cmd: 'python',
    args: ['ops_check_photos.py'],
    label: 'Check Google Photos access',
  },
};

const MAX_LINES = 300;
const jobs = new Map<string, Job>();
const running = new Map<string, ChildProcess>();

function projectRoot() {
  return path.resolve(/*turbopackIgnore: true*/ process.cwd(), '..');
}

function append(job: Job, chunk: string) {
  for (const line of chunk.split(/\r?\n/)) {
    if (line.trim() === '') continue;
    job.output.push(line);
  }
  // Keep only the tail; these scripts are chatty and this lives in memory.
  if (job.output.length > MAX_LINES) {
    job.output = job.output.slice(-MAX_LINES);
  }
}

export function startJob(action: string): Job | { error: string } {
  const spec = ACTIONS[action];
  if (!spec) return { error: `Unknown action: ${action}` };

  const id = `job_${Date.now()}_${Math.random().toString(36).slice(2, 7)}`;
  const job: Job = {
    id,
    action,
    label: spec.label,
    state: 'running',
    startedAt: new Date().toISOString(),
    finishedAt: null,
    exitCode: null,
    output: [],
  };
  jobs.set(id, job);

  const child = spawn(spec.cmd, spec.args, {
    cwd: projectRoot(),
    // Force unbuffered output or Python holds prints until exit, which would
    // make a long job look frozen.
    env: { ...process.env, PYTHONUNBUFFERED: '1', PYTHONIOENCODING: 'utf-8' },
    shell: process.platform === 'win32',
  });

  running.set(id, child);
  child.stdout?.on('data', (d) => append(job, d.toString()));
  child.stderr?.on('data', (d) => append(job, d.toString()));

  child.on('error', (err) => {
    append(job, `spawn error: ${err.message}`);
    job.state = 'failed';
    job.finishedAt = new Date().toISOString();
    running.delete(id);
  });

  child.on('close', (code) => {
    job.exitCode = code;
    job.state = code === 0 ? 'succeeded' : 'failed';
    job.finishedAt = new Date().toISOString();
    if (job.output.length === 0) {
      append(job, code === 0 ? '(finished with no output)' : `(failed, exit ${code})`);
    }
    running.delete(id);
  });

  // Keep the map from growing forever.
  if (jobs.size > 40) {
    const oldest = [...jobs.values()]
      .filter((j) => j.state !== 'running')
      .sort((a, b) => a.startedAt.localeCompare(b.startedAt))[0];
    if (oldest) jobs.delete(oldest.id);
  }

  return job;
}

export function getJob(id: string): Job | null {
  return jobs.get(id) ?? null;
}

export function recentJobs(limit = 10): Job[] {
  return [...jobs.values()]
    .sort((a, b) => b.startedAt.localeCompare(a.startedAt))
    .slice(0, limit);
}

export function stopJob(id: string): boolean {
  const child = running.get(id);
  if (!child) return false;
  child.kill();
  return true;
}
