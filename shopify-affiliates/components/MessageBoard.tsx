'use client';

import { useState, useEffect } from 'react';

export default function MessageBoard({ affiliates }: { affiliates: any[] }) {
  const [messages, setMessages] = useState([]);
  const [messageText, setMessageText] = useState('');
  const [isBroadcast, setIsBroadcast] = useState(true);
  const [selectedAffiliate, setSelectedAffiliate] = useState('');

  useEffect(() => {
    fetchMessages();
  }, []);

  async function fetchMessages() {
    try {
      const res = await fetch('/api/messages');
      const data = await res.json();
      setMessages(data.messages);
    } catch (error) {
      console.error('Error fetching messages:', error);
    }
  }

  async function handleSendMessage(e: React.FormEvent) {
    e.preventDefault();
    if (!messageText.trim()) return;

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

      if (res.ok) {
        setMessageText('');
        fetchMessages();
      }
    } catch (error) {
      console.error('Error sending message:', error);
    }
  }

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <div className="lg:col-span-2">
        <h2 className="text-2xl font-bold text-gray-900 mb-6">Messages</h2>
        <div className="bg-white rounded-lg shadow p-6 space-y-4 h-96 overflow-y-auto">
          {messages.length === 0 ? (
            <p className="text-gray-500 text-center py-8">No messages yet</p>
          ) : (
            messages.map((msg) => (
              <div key={msg.id} className={`p-4 rounded-lg ${msg.from_id === 'admin' ? 'bg-blue-50' : 'bg-gray-50'}`}>
                <p className="text-sm font-semibold text-gray-900">{msg.from_id}</p>
                <p className="text-gray-700 mt-2">{msg.message}</p>
                <p className="text-xs text-gray-500 mt-2">
                  {new Date(msg.created_at).toLocaleString()}
                </p>
              </div>
            ))
          )}
        </div>
      </div>

      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Send Message</h3>
        <form onSubmit={handleSendMessage} className="space-y-4">
          <div>
            <label className="flex items-center">
              <input
                type="radio"
                checked={isBroadcast}
                onChange={() => setIsBroadcast(true)}
                className="mr-2"
              />
              <span className="text-sm text-gray-700">Broadcast to All</span>
            </label>
            <label className="flex items-center mt-2">
              <input
                type="radio"
                checked={!isBroadcast}
                onChange={() => setIsBroadcast(false)}
                className="mr-2"
              />
              <span className="text-sm text-gray-700">Send to One</span>
            </label>
          </div>

          {!isBroadcast && (
            <select
              value={selectedAffiliate}
              onChange={(e) => setSelectedAffiliate(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            >
              <option value="">Select Affiliate</option>
              {affiliates.map((aff) => (
                <option key={aff.id} value={aff.id}>
                  {aff.name}
                </option>
              ))}
            </select>
          )}

          <textarea
            value={messageText}
            onChange={(e) => setMessageText(e.target.value)}
            placeholder="Type your message..."
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 resize-none"
            rows={4}
          />

          <button
            type="submit"
            className="w-full bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700 font-medium"
          >
            Send Message
          </button>
        </form>
      </div>
    </div>
  );
}
