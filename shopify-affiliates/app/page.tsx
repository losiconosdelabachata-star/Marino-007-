'use client';

import { useState, useEffect } from 'react';
import AffiliatesList from '@/components/AffiliatesList';
import MessageBoard from '@/components/MessageBoard';
import SalesStats from '@/components/SalesStats';

export default function Dashboard() {
  const [activeTab, setActiveTab] = useState('overview');
  const [affiliates, setAffiliates] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchAffiliates();
  }, []);

  async function fetchAffiliates() {
    try {
      const res = await fetch('/api/affiliates');
      const data = await res.json();
      setAffiliates(data.affiliates);
    } catch (error) {
      console.error('Error fetching affiliates:', error);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <h1 className="text-3xl font-bold text-gray-900">Los Iconos Affiliate Hub</h1>
          <p className="text-gray-600">Manage affiliates, track sales, and communicate</p>
        </div>
      </header>

      <nav className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4">
          <div className="flex space-x-8">
            {['overview', 'affiliates', 'messages', 'sales'].map((tab) => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={`px-3 py-4 text-sm font-medium ${
                  activeTab === tab
                    ? 'border-b-2 border-blue-500 text-blue-600'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                {tab.charAt(0).toUpperCase() + tab.slice(1)}
              </button>
            ))}
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {loading ? (
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
            <p className="mt-4 text-gray-600">Loading dashboard...</p>
          </div>
        ) : (
          <>
            {activeTab === 'overview' && (
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                <div className="bg-white p-6 rounded-lg shadow">
                  <h3 className="text-gray-600 text-sm font-medium">Total Affiliates</h3>
                  <p className="text-3xl font-bold text-gray-900 mt-2">{affiliates.length}</p>
                </div>
                <div className="bg-white p-6 rounded-lg shadow">
                  <h3 className="text-gray-600 text-sm font-medium">Active Affiliates</h3>
                  <p className="text-3xl font-bold text-green-600 mt-2">
                    {affiliates.filter((a: any) => a.status === 'active').length}
                  </p>
                </div>
                <div className="bg-white p-6 rounded-lg shadow">
                  <h3 className="text-gray-600 text-sm font-medium">Messages</h3>
                  <p className="text-3xl font-bold text-blue-600 mt-2">0</p>
                </div>
              </div>
            )}

            {activeTab === 'affiliates' && <AffiliatesList affiliates={affiliates} />}
            {activeTab === 'messages' && <MessageBoard affiliates={affiliates} />}
            {activeTab === 'sales' && <SalesStats affiliates={affiliates} />}
          </>
        )}
      </main>
    </div>
  );
}
