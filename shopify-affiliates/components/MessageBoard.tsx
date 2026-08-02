'use client';

import { useState, useEffect, useCallback } from 'react';
import type { Affiliate, Message } from '@/lib/types';

export default function MessageBoard({ affiliates }: { affiliates: Affiliate[] }) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [messageText, setMessageText] = useState('');
  const [isBroadcast, setIsBroadcast] = useState(true);
  const [selectedAffiliate, setSelectedAffiliate] = useState('');
  const [sending, setSending] = useState(false);
  const [note, setNote] = useState<string | null>(null);

  const fetchMessages = useCallback(async () => {
    try {
      const res = await fetch('/api/messages', { cache: 'no-store' });
      const data = await res.json();
      setMessages(data.messages || []);
    } catch {
      /* keep whatever is already on screen */
    }
  }, []);

  useEffect(() => {
    fetchMessages();
  }, [fetchMessages]);

  async function handleSendMessage(e: React.FormEvent) {
    e.preventDefault();
    if (!messageText.trim()) return;
    if (!isBroadcast && !selectedAffiliate) {
      setNote('Pick an affiliate first.');
      return;
    }

    setSending(true);
    setNote(null);
    try {
      const res = await fetch('/api/messages', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          from_id: 'admin',
          to_id: isBroadcast ? null : selectedAffiliate,
          message: messageText,
          is_broadcast: isBroadcast,
        }),
      });
      const data = await res.json();
      if (data.success) {
        setMessageText('');
        setNote(isBroadcast ? 'Broadcast sent to all active affiliates.' : 'Message sent.');
        fetchMessages();
      } else {
        setNote(data.error || 'Send failed.');
      }
    } catch {
      setNote('Could not reach the server.');
    } finally {
      setSending(false);
    }
  }

  return (
    <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
      <div className="lg:col-span-2">
        <p className="eyebrow mb-4">Transmission Log</p>
        <div className="panel scroll-y max-h-[28rem] space-y-3 p-5">
          {messages.length === 0 ? (
            <p className="py-12 text-center text-sm" style={{ color: 'var(--text-dim)' }}>
              No messages yet.
            </p>
          ) : (
            messages.map((msg) => (
              <div
                key={msg.id}
                className="rounded-lg p-4"
                style={{
                  background: 'rgba(6,9,20,0.6)',
                  borderLeft: `2px solid ${msg.is_broadcast ? 'var(--gold)' : 'var(--cyan)'}`,
                }}
              >
                <div className="mb-1 flex items-center gap-2">
                  <span className="mono text-[0.65rem]" style={{ color: 'var(--gold-bright)' }}>
                    {msg.from_id.toUpperCase()}
                  </span>
                  {msg.is_broadcast === 1 && (
                    <span className="mono text-[0.6rem]" style={{ color: 'var(--text-dim)' }}>
                      · BROADCAST
                    </span>
                  )}
                </div>
                <p className="text-sm leading-relaxed">{msg.message}</p>
                <p className="mono mt-2 text-[0.6rem]" style={{ color: 'var(--text-dim)' }}>
                  {new Date(msg.created_at).toLocaleString()}
                </p>
              </div>
            ))
          )}
        </div>
      </div>

      <div className="panel h-fit p-6">
        <p className="eyebrow mb-4">Compose</p>
        <form onSubmit={handleSendMessage} className="space-y-4">
          <div className="space-y-2">
            <label className="flex cursor-pointer items-center gap-2 text-sm">
              <input
                type="radio"
                checked={isBroadcast}
                onChange={() => setIsBroadcast(true)}
                className="accent-amber-500"
              />
              Broadcast to all
            </label>
            <label className="flex cursor-pointer items-center gap-2 text-sm">
              <input
                type="radio"
                checked={!isBroadcast}
                onChange={() => setIsBroadcast(false)}
                className="accent-amber-500"
              />
              Send to one
            </label>
          </div>

          {!isBroadcast && (
            <select
              value={selectedAffiliate}
              onChange={(e) => setSelectedAffiliate(e.target.value)}
              className="field w-full px-3 py-2 text-sm"
            >
              <option value="">Select affiliate…</option>
              {affiliates.map((a) => (
                <option key={a.id} value={a.id}>
                  {a.name}
                </option>
              ))}
            </select>
          )}

          <textarea
            value={messageText}
            onChange={(e) => setMessageText(e.target.value)}
            placeholder="Type your message…"
            rows={5}
            className="field w-full resize-none px-3 py-2 text-sm"
          />

          <button
            type="submit"
            disabled={sending || !messageText.trim()}
            className="btn-gold w-full py-2.5 text-sm"
          >
            {sending ? 'Sending…' : isBroadcast ? 'Broadcast' : 'Send'}
          </button>
        </form>

        {note && (
          <p className="mono mt-3 text-xs" style={{ color: 'var(--cyan)' }}>
            {note}
          </p>
        )}
      </div>
    </div>
  );
}
