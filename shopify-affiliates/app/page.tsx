'use client';

import { useState, useEffect } from 'react';
import SystemGrid from '@/components/SystemGrid';
import WhatsAppPanel from '@/components/WhatsAppPanel';
import AffiliatesList from '@/components/AffiliatesList';
import MessageBoard from '@/components/MessageBoard';
import SalesStats from '@/components/SalesStats';

const TABS = [
  { id: 'command', label: 'Command' },
  { id: 'affiliates', label: 'Affiliates' },
  { id: 'messages', label: 'Messages' },
  { id: 'sales', label: 'Sales' },
] as const;

type TabId = (typeof TABS)[number]['id'];

export default function Dashboard() {
  const [tab, setTab] = useState<TabId>('command');
  const [affiliates, setAffiliates] = useState([]);
  const [clock, setClock] = useState('');

  useEffect(() => {
    fetch('/api/affiliates')
      .then((r) => r.json())
      .then((d) => setAffiliates(d.affiliates || []))
      .catch(() => setAffiliates([]));
  }, []);

  useEffect(() => {
    const tick = () =>
      setClock(
        new Date().toLocaleTimeString('en-US', {
          hour: '2-digit',
          minute: '2-digit',
          second: '2-digit',
          hour12: false,
        })
      );
    tick();
    const timer = setInterval(tick, 1000);
    return () => clearInterval(timer);
  }, []);

  return (
    <>
      <div className="void-bg" />
      <div className="void-grid" />

      <div className="mx-auto min-h-screen max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
        <header className="mb-8">
          <div className="flex flex-wrap items-end justify-between gap-4">
            <div>
              <p className="eyebrow mb-2">Los Iconos de la Bachata</p>
              <h1
                className="glow-gold text-3xl font-bold tracking-tight sm:text-4xl"
                style={{ color: 'var(--gold-bright)' }}
              >
                MARINO 007
              </h1>
              <p className="mt-1 text-sm" style={{ color: 'var(--text-dim)' }}>
                Command center — every system, one screen.
              </p>
            </div>
            <div className="text-right">
              <p className="mono text-2xl" style={{ color: 'var(--cyan)' }}>
                {clock}
              </p>
              <p className="eyebrow mt-1">Local time</p>
            </div>
          </div>
        </header>

        <nav className="mb-8 border-b" style={{ borderColor: 'rgba(212,175,55,0.14)' }}>
          <div className="scroll-x flex gap-1">
            {TABS.map((t) => (
              <button
                key={t.id}
                onClick={() => setTab(t.id)}
                className={`whitespace-nowrap px-5 py-3 text-sm font-medium transition-colors ${
                  tab === t.id ? 'tab-active' : ''
                }`}
                style={tab === t.id ? undefined : { color: 'var(--text-dim)' }}
              >
                {t.label}
              </button>
            ))}
          </div>
        </nav>

        <main>
          {tab === 'command' && (
            <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
              <div className="lg:col-span-2">
                <SystemGrid />
              </div>
              <div className="space-y-6">
                <WhatsAppPanel />
              </div>
            </div>
          )}

          {tab === 'affiliates' && <AffiliatesList affiliates={affiliates} />}
          {tab === 'messages' && <MessageBoard affiliates={affiliates} />}
          {tab === 'sales' && <SalesStats affiliates={affiliates} />}
        </main>

        <footer
          className="mono mt-14 border-t pt-6 text-center text-[0.65rem]"
          style={{ borderColor: 'rgba(212,175,55,0.12)', color: 'var(--text-dim)' }}
        >
          MARINO 007 · BUILT BY MARINO SANTOS · LOS ICONOS DE LA BACHATA
        </footer>
      </div>
    </>
  );
}
