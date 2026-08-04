'use client';

import { useState, useEffect, useCallback } from 'react';

interface SystemInfo {
  id: string;
  name: string;
  blurb: string;
  status: 'online' | 'offline' | 'degraded' | 'not_configured';
  detail: string;
  lastActivity: string | null;
  script: string | null;
}

const LED: Record<string, string> = {
  online: 'led-online',
  degraded: 'led-warn',
  offline: 'led-offline',
  not_configured: 'led-idle',
};

const LABEL: Record<string, string> = {
  online: 'ONLINE',
  degraded: 'ATTENTION',
  offline: 'OFFLINE',
  not_configured: 'SETUP NEEDED',
};

function relativeTime(iso: string | null): string | null {
  if (!iso) return null;
  const diff = Date.now() - new Date(iso).getTime();
  if (Number.isNaN(diff)) return null;
  const mins = Math.floor(diff / 60000);
  if (mins < 1) return 'just now';
  if (mins < 60) return `${mins}m ago`;
  const hrs = Math.floor(mins / 60);
  if (hrs < 24) return `${hrs}h ago`;
  return `${Math.floor(hrs / 24)}d ago`;
}

export default function SystemGrid() {
  const [systems, setSystems] = useState<SystemInfo[]>([]);
  const [loading, setLoading] = useState(true);

  const load = useCallback(async () => {
    try {
      const res = await fetch('/api/systems', { cache: 'no-store' });
      const data = await res.json();
      setSystems(data.systems || []);
    } catch {
      /* leave the previous snapshot on screen rather than blanking it */
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    load();
    const timer = setInterval(load, 15000);
    return () => clearInterval(timer);
  }, [load]);

  if (loading) {
    return (
      <div className="panel p-10 text-center">
        <p className="mono text-sm" style={{ color: 'var(--text-dim)' }}>
          SCANNING SYSTEMS…
        </p>
      </div>
    );
  }

  const online = systems.filter((s) => s.status === 'online').length;

  return (
    <div>
      <div className="mb-4 flex items-baseline justify-between">
        <p className="eyebrow">Systems</p>
        <p className="mono text-xs" style={{ color: 'var(--text-dim)' }}>
          {online}/{systems.length} ONLINE
        </p>
      </div>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-3">
        {systems.map((sys) => {
          const last = relativeTime(sys.lastActivity);

          return (
            <div key={sys.id} className="panel panel-hover p-5">
              <div className="mb-3 flex items-start justify-between gap-3">
                <div className="min-w-0">
                  <h3 className="truncate font-semibold">{sys.name}</h3>
                  <p className="truncate text-xs" style={{ color: 'var(--text-dim)' }}>
                    {sys.blurb}
                  </p>
                </div>
                <span className={`led ${LED[sys.status]} mt-1.5`} />
              </div>

              <p
                className="mono mb-2 text-[0.62rem] tracking-widest"
                style={{
                  color:
                    sys.status === 'online'
                      ? 'var(--online)'
                      : sys.status === 'degraded'
                        ? 'var(--warn)'
                        : sys.status === 'offline'
                          ? 'var(--offline)'
                          : 'var(--text-dim)',
                }}
              >
                {LABEL[sys.status]}
              </p>

              <p className="text-sm leading-relaxed" style={{ color: 'var(--text-dim)' }}>
                {sys.detail}
              </p>

              {last && (
                <p className="mono mt-2 text-[0.65rem]" style={{ color: 'var(--text-dim)' }}>
                  LAST RUN {last.toUpperCase()}
                </p>
              )}

            </div>
          );
        })}
      </div>
    </div>
  );
}
