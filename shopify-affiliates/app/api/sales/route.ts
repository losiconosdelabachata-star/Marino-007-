import { NextRequest, NextResponse } from 'next/server';
import db from '@/lib/db';
import type { AffiliateStats } from '@/lib/types';

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const affiliateId = searchParams.get('affiliate_id');

    let query = `
      SELECT
        a.id, a.name, a.email,
        COUNT(s.id) as order_count,
        SUM(s.amount) as total_sales,
        SUM(s.commission) as total_commissions,
        AVG(s.commission) as avg_commission
      FROM affiliates a
      LEFT JOIN sales s ON a.id = s.affiliate_id
      WHERE a.status = 'active'
    `;

    const params: string[] = [];

    if (affiliateId) {
      query += ' AND a.id = ?';
      params.push(affiliateId);
    }

    query += ' GROUP BY a.id ORDER BY total_sales DESC';

    const stmt = db.prepare(query);
    const stats = stmt.all(...params) as AffiliateStats[];

    return NextResponse.json({ stats });
  } catch (error) {
    return NextResponse.json({ error: String(error) }, { status: 500 });
  }
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { affiliate_id, order_id, amount, commission } = body;

    const saleId = `sale_${Date.now()}`;
    const stmt = db.prepare(`
      INSERT INTO sales (id, affiliate_id, order_id, amount, commission)
      VALUES (?, ?, ?, ?, ?)
    `);

    stmt.run(saleId, affiliate_id, order_id, amount, commission);

    const updateStmt = db.prepare(`
      UPDATE affiliates
      SET total_sales = total_sales + ?,
          total_commissions = total_commissions + ?
      WHERE id = ?
    `);
    updateStmt.run(amount, commission, affiliate_id);

    return NextResponse.json({ saleId, success: true });
  } catch (error) {
    return NextResponse.json({ error: String(error) }, { status: 500 });
  }
}
