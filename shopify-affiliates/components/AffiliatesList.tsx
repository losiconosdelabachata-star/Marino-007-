'use client';

import { useState } from 'react';
import type { Affiliate } from '@/lib/types';

export default function AffiliatesList({ affiliates }: { affiliates: Affiliate[] }) {
  const [showForm, setShowForm] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [form, setForm] = useState({ name: '', email: '', phone: '', commission_rate: '' });

  async function handleAdd(e: React.FormEvent) {
    e.preventDefault();
    setSaving(true);
    setError(null);
    try {
      const res = await fetch('/api/affiliates', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ...form,
          commission_rate: parseFloat(form.commission_rate) || 0,
        }),
      });
      const data = await res.json();
      if (data.success) {
        window.location.reload();
      } else {
        setError(data.error || 'Could not save.');
      }
    } catch {
      setError('Could not reach the server.');
    } finally {
      setSaving(false);
    }
  }

  return (
    <div>
      <div className="mb-4 flex items-center justify-between">
        <p className="eyebrow">Roster · {affiliates.length}</p>
        <button onClick={() => setShowForm(!showForm)} className="btn-ghost px-4 py-2 text-xs">
          {showForm ? 'Cancel' : '+ Add Affiliate'}
        </button>
      </div>

      {showForm && (
        <form onSubmit={handleAdd} className="panel mb-6 grid grid-cols-1 gap-3 p-5 sm:grid-cols-2">
          <input
            type="text"
            placeholder="Name"
            required
            value={form.name}
            onChange={(e) => setForm({ ...form, name: e.target.value })}
            className="field px-3 py-2 text-sm"
          />
          <input
            type="email"
            placeholder="Email"
            required
            value={form.email}
            onChange={(e) => setForm({ ...form, email: e.target.value })}
            className="field px-3 py-2 text-sm"
          />
          <input
            type="tel"
            placeholder="Phone (optional)"
            value={form.phone}
            onChange={(e) => setForm({ ...form, phone: e.target.value })}
            className="field px-3 py-2 text-sm"
          />
          <input
            type="number"
            step="0.1"
            placeholder="Commission %"
            value={form.commission_rate}
            onChange={(e) => setForm({ ...form, commission_rate: e.target.value })}
            className="field px-3 py-2 text-sm"
          />
          <button
            type="submit"
            disabled={saving}
            className="btn-gold py-2.5 text-sm sm:col-span-2"
          >
            {saving ? 'Saving…' : 'Add Affiliate'}
          </button>
          {error && (
            <p className="mono text-xs sm:col-span-2" style={{ color: 'var(--offline)' }}>
              {error}
            </p>
          )}
        </form>
      )}

      <div className="panel scroll-x">
        {affiliates.length === 0 ? (
          <p className="p-10 text-center text-sm" style={{ color: 'var(--text-dim)' }}>
            No affiliates yet. Add your first one above.
          </p>
        ) : (
          <table className="w-full min-w-[40rem]">
            <thead>
              <tr style={{ borderBottom: '1px solid rgba(212,175,55,0.16)' }}>
                {['Name', 'Email', 'Phone', 'Rate', 'Status'].map((h) => (
                  <th key={h} className="eyebrow px-5 py-3 text-left">
                    {h}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {affiliates.map((a) => (
                <tr key={a.id} style={{ borderBottom: '1px solid rgba(212,175,55,0.07)' }}>
                  <td className="px-5 py-3 text-sm font-medium">{a.name}</td>
                  <td className="px-5 py-3 text-sm" style={{ color: 'var(--text-dim)' }}>
                    {a.email}
                  </td>
                  <td className="px-5 py-3 text-sm" style={{ color: 'var(--text-dim)' }}>
                    {a.phone || '—'}
                  </td>
                  <td className="mono px-5 py-3 text-sm">{a.commission_rate}%</td>
                  <td className="px-5 py-3">
                    <span className="flex items-center gap-2">
                      <span className={`led ${a.status === 'active' ? 'led-online' : 'led-idle'}`} />
                      <span className="mono text-[0.65rem]" style={{ color: 'var(--text-dim)' }}>
                        {a.status.toUpperCase()}
                      </span>
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
