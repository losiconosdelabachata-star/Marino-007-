'use client';

import { useState, useEffect, useCallback } from 'react';

interface QRState {
  reachable: boolean;
  connected: boolean;
  qr: string | null;
  pairing_code?: string | null;
  pairing_for?: string | null;
  message?: string;
}

export default function WhatsAppPanel() {
  const [state, setState] = useState<QRState | null>(null);
  const [working, setWorking] = useState(false);
  const [note, setNote] = useState<string | null>(null);
  const [phone, setPhone] = useState('');
  const [showPair, setShowPair] = useState(false);

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

  async function requestPairingCode() {
    if (!phone.replace(/\D/g, '')) {
      setNote('Enter the phone number with country code.');
      return;
    }
    setWorking(true);
    setNote(null);
    try {
      const res = await fetch('/api/whatsapp', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ pair: phone }),
      });
      const data = await res.json();
      setNote(data.success ? null : data.error || 'Could not get a pairing code.');
      setTimeout(refresh, 800);
    } catch {
      setNote('Could not reach the bridge.');
    } finally {
      setWorking(false);
    }
  }

  const connected = state?.connected === true;
  const bridgeDown = state?.reachable === false;
  const code = state?.pairing_code;

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
      ) : code ? (
        <div className="text-center">
          <p className="eyebrow mb-3">Pairing code</p>
          <p
            className="mono mb-1 text-3xl font-bold tracking-[0.2em]"
            style={{ color: 'var(--gold-bright)' }}
          >
            {code}
          </p>
          {state?.pairing_for && (
            <p className="mono mb-4 text-xs" style={{ color: 'var(--text-dim)' }}>
              FOR +{state.pairing_for}
            </p>
          )}
          <div
            className="rounded-lg p-3 text-left text-xs leading-relaxed"
            style={{ background: 'rgba(6,9,20,0.7)', color: 'var(--text-dim)' }}
          >
            On that phone:
            <br />
            1. WhatsApp → Settings → Linked Devices
            <br />
            2. Link a Device
            <br />
            3. <span style={{ color: 'var(--cyan)' }}>Link with phone number instead</span>
            <br />
            4. Type the code above
          </div>
          <button onClick={() => setShowPair(false)} className="btn-ghost mt-4 px-4 py-2 text-xs">
            Show QR instead
          </button>
        </div>
      ) : state?.qr && !showPair ? (
        <div className="text-center">
          {/* Baileys hands us a data URL, so a plain img is all we need. */}
          <img
            src={state.qr}
            alt="WhatsApp pairing QR code"
            className="mx-auto rounded-xl"
            style={{ width: 200, height: 200, background: '#fff', padding: 10 }}
          />
          <p className="mt-4 text-sm font-medium">Scan with the dedicated phone</p>
          <p className="mt-1 text-xs leading-relaxed" style={{ color: 'var(--text-dim)' }}>
            WhatsApp → Settings → Linked Devices → Link a Device
          </p>
          <button onClick={() => setShowPair(true)} className="btn-ghost mt-4 px-4 py-2 text-xs">
            Can&apos;t scan? Use a code instead
          </button>
        </div>
      ) : showPair ? (
        <div>
          <p className="mb-3 text-sm" style={{ color: 'var(--text-dim)' }}>
            Get a code to type into the phone — no camera needed.
          </p>
          <input
            type="tel"
            value={phone}
            onChange={(e) => setPhone(e.target.value)}
            placeholder="Country code + number, e.g. 17868387137"
            className="field mb-3 w-full px-3 py-2 text-sm"
          />
          <button
            onClick={requestPairingCode}
            disabled={working}
            className="btn-gold w-full py-2.5 text-sm"
          >
            {working ? 'Requesting…' : 'Get pairing code'}
          </button>
          <button onClick={() => setShowPair(false)} className="btn-ghost mt-2 w-full py-2 text-xs">
            Back to QR
          </button>
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
