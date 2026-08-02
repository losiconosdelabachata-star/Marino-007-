'use client';

import { useState, useEffect, useCallback } from 'react';

interface QRState {
  reachable: boolean;
  connected: boolean;
  qr: string | null;
  message?: string;
}

export default function WhatsAppPanel() {
  const [state, setState] = useState<QRState | null>(null);
  const [working, setWorking] = useState(false);
  const [note, setNote] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    try {
      const res = await fetch('/api/whatsapp', { cache: 'no-store' });
      setState(await res.json());
    } catch {
      setState({ reachable: false, connected: false, qr: null, message: 'Dashboard could not reach its own API' });
    }
  }, []);

  useEffect(() => {
    refresh();
    // WhatsApp QRs expire roughly every 20s, so poll while unlinked.
    const timer = setInterval(refresh, 5000);
    return () => clearInterval(timer);
  }, [refresh]);

  async function reconnect(hard: boolean) {
    setWorking(true);
    setNote(null);
    try {
      const res = await fetch('/api/whatsapp', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ hard }),
      });
      const data = await res.json();
      setNote(data.success ? 'Reconnect started — QR incoming.' : data.error || 'Reconnect failed.');
      setTimeout(refresh, 1200);
    } catch {
      setNote('Could not reach the WhatsApp bridge.');
    } finally {
      setWorking(false);
    }
  }

  const connected = state?.connected === true;
  const bridgeDown = state?.reachable === false;

  return (
    <div className="panel p-6">
      <div className="flex items-start justify-between gap-4 mb-5">
        <div>
          <p className="eyebrow mb-1">Alert Channel</p>
          <h3 className="text-lg font-semibold">WhatsApp Link</h3>
        </div>
        <div className="flex items-center gap-2">
          <span
            className={`led ${
              connected ? 'led-online' : bridgeDown ? 'led-offline' : 'led-warn'
            }`}
          />
          <span className="mono text-xs" style={{ color: 'var(--text-dim)' }}>
            {connected ? 'LINKED' : bridgeDown ? 'BRIDGE DOWN' : 'UNLINKED'}
          </span>
        </div>
      </div>

      {connected ? (
        <div className="text-center py-8">
          <div
            className="mx-auto mb-4 flex h-14 w-14 items-center justify-center rounded-full text-2xl"
            style={{ background: 'rgba(53,255,168,0.1)', border: '1px solid rgba(53,255,168,0.4)' }}
          >
            ✓
          </div>
          <p className="font-medium" style={{ color: 'var(--online)' }}>
            Bot is linked
          </p>
          <p className="mt-1 text-sm" style={{ color: 'var(--text-dim)' }}>
            Order and blog alerts are flowing to your phone.
          </p>
          <button
            onClick={() => reconnect(true)}
            disabled={working}
            className="btn-ghost mt-5 px-4 py-2 text-sm"
          >
            Re-link a different phone
          </button>
        </div>
      ) : bridgeDown ? (
        <div className="py-6">
          <p className="mb-3 text-sm" style={{ color: 'var(--text-dim)' }}>
            {state?.message}
          </p>
          <p className="mb-2 text-sm">Start it from the project folder:</p>
          <code
            className="mono block rounded-lg px-3 py-2 text-xs"
            style={{ background: 'rgba(6,9,20,0.8)', color: 'var(--cyan)' }}
          >
            node whatsapp_server.js
          </code>
        </div>
      ) : state?.qr ? (
        <div className="text-center">
          {/* Baileys hands us a data URL, so a plain img is all we need. */}
          <img
            src={state.qr}
            alt="WhatsApp pairing QR code"
            className="mx-auto rounded-xl"
            style={{ width: 220, height: 220, background: '#fff', padding: 10 }}
          />
          <p className="mt-4 text-sm font-medium">Scan with the dedicated phone</p>
          <p className="mt-1 text-xs leading-relaxed" style={{ color: 'var(--text-dim)' }}>
            WhatsApp → Settings → Linked Devices → Link a Device
          </p>
          <p className="mono mt-3 text-[0.65rem]" style={{ color: 'var(--text-dim)' }}>
            REFRESHES AUTOMATICALLY
          </p>
        </div>
      ) : (
        <div className="py-6 text-center">
          <p className="mb-4 text-sm" style={{ color: 'var(--text-dim)' }}>
            {state?.message || 'Checking bridge…'}
          </p>
          <button
            onClick={() => reconnect(false)}
            disabled={working}
            className="btn-gold px-5 py-2 text-sm"
          >
            {working ? 'Requesting…' : 'Request QR Code'}
          </button>
        </div>
      )}

      {note && (
        <p className="mono mt-4 text-xs" style={{ color: 'var(--cyan)' }}>
          {note}
        </p>
      )}
    </div>
  );
}
