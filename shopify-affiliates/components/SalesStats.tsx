'use client';

import { useState, useEffect } from 'react';

export default function SalesStats({ affiliates }: { affiliates: any[] }) {
  const [stats, setStats] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchStats();
  }, []);

  async function fetchStats() {
    try {
      const res = await fetch('/api/sales');
      const data = await res.json();
      setStats(data.stats);
    } catch (error) {
      console.error('Error fetching stats:', error);
    } finally {
      setLoading(false);
    }
  }

  const totalSales = stats.reduce((sum, s) => sum + (s.total_sales || 0), 0);
  const totalCommissions = stats.reduce((sum, s) => sum + (s.total_commissions || 0), 0);

  return (
    <div>
      <h2 className="text-2xl font-bold text-gray-900 mb-6">Sales & Commissions</h2>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-gray-600 text-sm font-medium">Total Sales</h3>
          <p className="text-3xl font-bold text-gray-900 mt-2">${totalSales.toFixed(2)}</p>
        </div>
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-gray-600 text-sm font-medium">Total Commissions</h3>
          <p className="text-3xl font-bold text-green-600 mt-2">${totalCommissions.toFixed(2)}</p>
        </div>
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-gray-600 text-sm font-medium">Avg Commission Rate</h3>
          <p className="text-3xl font-bold text-blue-600 mt-2">
            {affiliates.length > 0
              ? (affiliates.reduce((sum, a) => sum + a.commission_rate, 0) / affiliates.length).toFixed(1)
              : 0}%
          </p>
        </div>
      </div>

      <div className="bg-white rounded-lg shadow overflow-hidden">
        <table className="w-full">
          <thead className="bg-gray-100 border-b">
            <tr>
              <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">Affiliate</th>
              <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">Orders</th>
              <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">Total Sales</th>
              <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">Commission</th>
              <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">Avg Commission</th>
            </tr>
          </thead>
          <tbody>
            {stats.map((stat) => (
              <tr key={stat.id} className="border-b hover:bg-gray-50">
                <td className="px-6 py-4 text-sm text-gray-900 font-medium">{stat.name}</td>
                <td className="px-6 py-4 text-sm text-gray-600">{stat.order_count || 0}</td>
                <td className="px-6 py-4 text-sm text-gray-600">${(stat.total_sales || 0).toFixed(2)}</td>
                <td className="px-6 py-4 text-sm text-green-600 font-semibold">
                  ${(stat.total_commissions || 0).toFixed(2)}
                </td>
                <td className="px-6 py-4 text-sm text-gray-600">
                  ${(stat.avg_commission || 0).toFixed(2)}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
