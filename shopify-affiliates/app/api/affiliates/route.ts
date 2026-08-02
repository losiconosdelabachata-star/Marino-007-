import { NextRequest, NextResponse } from 'next/server';
import db, { initializeDatabase } from '@/lib/db';

initializeDatabase();

export async function GET() {
  try {
    const stmt = db.prepare('SELECT * FROM affiliates ORDER BY created_at DESC');
    const affiliates = stmt.all();
    return NextResponse.json({ affiliates });
  } catch (error) {
    return NextResponse.json({ error: String(error) }, { status: 500 });
  }
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { shopify_id, name, email, phone, commission_rate } = body;

    const id = `aff_${Date.now()}`;
    const stmt = db.prepare(`
      INSERT INTO affiliates (id, shopify_id, name, email, phone, commission_rate)
      VALUES (?, ?, ?, ?, ?, ?)
    `);

    stmt.run(id, shopify_id, name, email, phone, commission_rate || 0);
    return NextResponse.json({ id, success: true });
  } catch (error) {
    return NextResponse.json({ error: String(error) }, { status: 500 });
  }
}
