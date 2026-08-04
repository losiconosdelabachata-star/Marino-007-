'use client';

import { useState, useEffect, useCallback, useRef } from 'react';

interface Action {
  id: string;
  label: string;
  danger: string | null;
}

interface Job {
  id: string;
  action: string;
  label: string;
  state: 'running' | 'succeeded' | 'failed';
  startedAt: string;
  exitCode: number | null;
  output: string[];
}

const STATE_COLOR: Record<string, string> = {
  running: 'var(--cyan)',
  succeeded: 'var(--online)',
  failed: 'var(--offline)',
};

export default function OpsConsole() {
  const [actions, setActions] = useState<Action[]>([]);
  const [job, setJob] = useState<Job | null>(null);
  const [confirming, setConfirming] = useState<Action | null>(null);
  const [starting, setStarting] = useState<string | null>(null);
  const logRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    fetch('/api/control', { cache: 'no-store' })
      .then((r) => r.json())
      .then((d) => setActions(d.actions || []))
      .catch(() => setActions([]));
  }, []);

  // Poll while a job runs so output appears as it is produced.
  const pollJob = useCallback((id: string) => {
    const timer = setInterval(async () => {
      try {
        const res = await fetch(`/api/control?job=${id}`, { cache: 'no-store' });
        const data = await res.json();
        if (data.job) {
          setJob(data.job);
          if (data.job.state !== 'running') clearInterval(timer);
        }
      } catch {
        clearInterval(timer);
      }
    }, 1000);
    return timer;
  }, []);

  useEffect(() => {
    if (logRef.current) logRef.current.scrollTop = logRef.current.scrollHeight;
  }, [job?.output.length]);

  async function run(action: Action) {
    setConfirming(null);
    setStarting(action.id);
    try {
      const res = await fetch('/api/control', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action: action.id }),
      });
      const data = await res.json();
      if (data.success) {
        setJob(data.job);
        pollJob(data.job.id);
      } else {
        setJob({
          id: 'err',
          action: action.id,
          label: action.label,
          state: 'failed',
          startedAt: new Date().toISOString(),
          exitCode: null,
          output: [data.error || 'Failed to start'],
        });
      }
    } finally {
      setStarting(null);
    }
  }

  function handleClick(action: Action) {
    // Anything with real-world side effects gets a confirm step - these
    // buttons email customers and send orders to production.
    if (action.danger) setConfirming(action);
    else run(action);
  }

  return (
    <div className="panel p-6">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <p className="eyebrow mb-1">Operations</p>
          <h3 className="text-lg font-semibold">Run a job</h3>
        </div>
        {job && (
          <span className="mono text-xs" style={{ color: STATE_COLOR[job.state] }}>
            {job.state.toUpperCase()}
            {job.exitCode !== null && job.state === 'failed' ? ` (${job.exitCode})` : ''}
          </span>
        )}
      </div>

      <div className="mb-4 grid grid-cols-1 gap-2 sm:grid-cols-2">
        {actions.map((a) => (
          <button
            key={a.id}
            onClick={() => handleClick(a)}
            disabled={starting !== null || job?.state === 'running'}
            className={`${a.danger ? 'btn-gold' : 'btn-ghost'} px-3 py-2.5 text-left text-xs`}
            title={a.danger || undefined}
          >
            {starting === a.id ? 'Starting…' : a.label}
            {a.danger && <span className="ml-1 opacity-70">⚠</span>}
          </button>
        ))}
      </div>

      {confirming && (
        <div
          className="mb-4 rounded-lg p-4"
          style={{ background: 'rgba(255,77,106,0.08)', border: '1px solid rgba(255,77,106,0.35)' }}
        >
          <p className="mb-1 text-sm font-semibold" style={{ color: 'var(--offline)' }}>
            This has real consequences
          </p>
          <p className="mb-3 text-sm" style={{ color: 'var(--text-dim)' }}>
            {confirming.label} — {confirming.danger}. This cannot be undone.
          </p>
          <div className="flex gap-2">
            <button onClick={() => run(confirming)} className="btn-gold px-4 py-2 text-xs">
              Yes, run it
            </button>
            <button onClick={() => setConfirming(null)} className="btn-ghost px-4 py-2 text-xs">
              Cancel
            </button>
          </div>
        </div>
      )}

      <div
        ref={logRef}
        className="scroll-y mono rounded-lg p-4 text-xs leading-relaxed"
        style={{
          background: 'rgba(3,5,12,0.85)',
          border: '1px solid rgba(212,175,55,0.12)',
          height: '15rem',
          color: 'var(--text-dim)',
        }}
      >
        {!job ? (
          <p style={{ color: 'var(--text-dim)' }}>
            Output appears here. Nothing has been run yet.
          </p>
        ) : (
          <>
            <p style={{ color: 'var(--gold-bright)' }}>
              $ {job.label}
            </p>
            {job.output.map((line, i) => (
              <p key={i} style={{ color: /error|failed|traceback|❌/i.test(line) ? 'var(--offline)' : undefined }}>
                {line}
              </p>
            ))}
            {job.state === 'running' && <p style={{ color: 'var(--cyan)' }}>▌</p>}
          </>
        )}
      </div>
    </div>
  );
}
