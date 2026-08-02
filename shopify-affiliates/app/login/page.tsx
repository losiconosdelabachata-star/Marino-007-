'use client';

import { useState, useRef, Suspense } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';

function LoginForm() {
  const router = useRouter();
  const params = useSearchParams();
  const inputRef = useRef<HTMLInputElement>(null);
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  async function submit(e: React.FormEvent) {
    e.preventDefault();

    // Read straight from the DOM. Browser autofill and password managers set
    // the input value without firing React's onChange, so component state can
    // still be empty while the field visibly contains the password.
    const value = inputRef.current?.value ?? password;

    if (!value) {
      setError('Enter the password.');
      return;
    }

    setBusy(true);
    setError(null);
    try {
      const res = await fetch('/api/auth', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ password: value }),
      });
      const data = await res.json();
      if (data.success) {
        router.push(params.get('next') || '/');
        router.refresh();
      } else {
        setError(data.error || 'Incorrect password.');
      }
    } catch {
      setError('Could not reach the server.');
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center px-4">
      <div className="panel w-full max-w-sm p-8">
        <div className="mb-7 text-center">
          <p className="eyebrow mb-2">Los Iconos de la Bachata</p>
          <h1 className="glow-gold text-2xl font-bold" style={{ color: 'var(--gold-bright)' }}>
            MARINO 007
          </h1>
          <p className="mt-2 text-sm" style={{ color: 'var(--text-dim)' }}>
            Command center access
          </p>
        </div>

        <form onSubmit={submit} className="space-y-4">
          <input
            ref={inputRef}
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="Password"
            autoFocus
            autoComplete="current-password"
            className="field w-full px-4 py-3 text-sm"
          />
          {/* Only `busy` gates this. Gating on state would leave the button
              dead whenever autofill populated the field without React
              noticing - a filled form with an unclickable button. */}
          <button type="submit" disabled={busy} className="btn-gold w-full py-3 text-sm">
            {busy ? 'Verifying…' : 'Enter'}
          </button>
        </form>

        {error && (
          <p className="mono mt-4 text-center text-xs" style={{ color: 'var(--offline)' }}>
            {error}
          </p>
        )}
      </div>
    </div>
  );
}

export default function LoginPage() {
  return (
    <>
      <div className="void-bg" />
      <div className="void-grid" />
      <Suspense fallback={null}>
        <LoginForm />
      </Suspense>
    </>
  );
}
