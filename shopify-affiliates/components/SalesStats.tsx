'use client';

import { useState, useEffect } from 'react';
import type { Affiliate, AffiliateStats } from '@/lib/types';

const money = (n: number | null) => `$${(n || 0).toFixed(2)}`;

export default function SalesStats({ affiliates }: { affiliates: Affiliate[] }) {
  const [stats, setStats] = useState<AffiliateStats[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch('/api/sales', { cache: 'no-store' })
      .then((r) => r.json())
      .then((d) => setStats(d.stats || []))
      .catch(() => setStats([]))
      .finally(() => setLoading(false));
  }, []);

  const totalSales = stats.reduce((sum, s) => sum + (s.total_sales || 0), 0);
  const totalCommissions = stats.reduce((sum, s) => sum + (s.total_commissions || 0), 0);
  const avgRate =
    affiliates.length > 0
      ? affiliates.reduce((sum, a) => sum + (a.commission_rate || 0), 0) / affiliates.length
      : 0;

  return (
    <div>
      <p className="eyebrow mb-4">Revenue</p>

      <div className="mb-6 grid grid-cols-1 gap-4 sm:grid-cols-3">
        {[
          { label: 'Total Sales', value: money(totalSales), color: 'var(--text)' },
          { label: 'Commissions Owed', value: money(totalCommissions), color: 'var(--online)' },
          { label: 'Avg Commission Rate', value: `${avgRate.toFixed(1)}%`, color: 'var(--cyan)' },
        ].map((card) => (
          <div key={card.label} className="panel p-5">
            <p className="eyebrow mb-2">{card.label}</p>
            <p className="mono text-2xl font-semibold" style={{ color: card.color }}>
              {card.value}
            </p>
          </div>
        ))}
      </div>

      <div className="panel scroll-x">
        {loading ? (
          <p className="mono p-8 text-center text-sm" style={{ color: 'var(--text-dim)' }}>
            LOADING…
          </p>
        ) : stats.length === 0 ? (
          <p className="p-8 text-center text-sm" style={{ color: 'var(--text-dim)' }}>
            No sales recorded yet.
          </p>
        ) : (
          <table className="w-full min-w-[38rem]">
            <thead>
              <tr style={{ borderBottom: '1px solid rgba(212,175,55,0.16)' }}>
                {['Affiliate', 'Orders', 'Sales', 'Commission', 'Avg'].map((h) => (
                  <th key={h} className="eyebrow px-5 py-3 text-left">
                    {h}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {stats.map((s) => (
                <tr key={s.id} style={{ borderBottom: '1px solid rgba(212,175,55,0.07)' }}>
                  <td className="px-5 py-3 text-sm font-medium">{s.name}</td>
                  <td className="mono px-5 py-3 text-sm" style={{ color: 'var(--text-dim)' }}>
                    {s.order_count || 0}
                  </td>
                  <td className="mono px-5 py-3 text-sm">{money(s.total_sales)}</td>
                  <td className="mono px-5 py-3 text-sm" style={{ color: 'var(--online)' }}>
                    {money(s.total_commissions)}
                  </td>
                  <td className="mono px-5 py-3 text-sm" style={{ color: 'var(--text-dim)' }}>
                    {money(s.avg_commission)}
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
