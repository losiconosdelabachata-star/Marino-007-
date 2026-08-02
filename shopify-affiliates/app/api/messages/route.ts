import { NextRequest, NextResponse } from 'next/server';
import db from '@/lib/db';
import nodemailer from 'nodemailer';

const transporter = nodemailer.createTransport({
  service: 'gmail',
  auth: {
    user: process.env.EMAIL_SENDER,
    pass: process.env.EMAIL_PASSWORD,
  },
});

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const affiliateId = searchParams.get('affiliate_id');
    const limit = parseInt(searchParams.get('limit') || '50');

    let query = 'SELECT * FROM messages WHERE is_broadcast = 1';
    const params: any[] = [];

    if (affiliateId) {
      query += ' OR (is_broadcast = 0 AND to_id = ?)';
      params.push(affiliateId);
    }

    query += ' ORDER BY created_at DESC LIMIT ?';
    params.push(limit);

    const stmt = db.prepare(query);
    const messages = stmt.all(...params);

    return NextResponse.json({ messages });
  } catch (error) {
    return NextResponse.json({ error: String(error) }, { status: 500 });
  }
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { from_id, to_id, message, is_broadcast } = body;

    const messageId = `msg_${Date.now()}`;
    const stmt = db.prepare(`
      INSERT INTO messages (id, from_id, to_id, message, is_broadcast)
      VALUES (?, ?, ?, ?, ?)
    `);

    stmt.run(messageId, from_id, to_id || null, message, is_broadcast ? 1 : 0);

    if (is_broadcast) {
      const affiliates = db.prepare('SELECT email FROM affiliates WHERE status = ?').all('active');
      for (const affiliate of affiliates) {
        await transporter.sendMail({
          from: process.env.EMAIL_SENDER,
          to: affiliate.email,
          subject: 'New Message from Los Iconos de la Bachata',
          html: `<p>${message}</p>`,
        });
      }
    } else if (to_id) {
      const affiliate = db.prepare('SELECT email FROM affiliates WHERE id = ?').get(to_id);
      if (affiliate) {
        await transporter.sendMail({
          from: process.env.EMAIL_SENDER,
          to: affiliate.email,
          subject: 'New Message from Los Iconos de la Bachata',
          html: `<p>${message}</p>`,
        });
      }
    }

    return NextResponse.json({ messageId, success: true });
  } catch (error) {
    return NextResponse.json({ error: String(error) }, { status: 500 });
  }
}
