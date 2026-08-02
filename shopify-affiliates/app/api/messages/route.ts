import { NextRequest, NextResponse } from 'next/server';
import db from '@/lib/db';
import nodemailer from 'nodemailer';
import type { Message } from '@/lib/types';

function transport() {
  return nodemailer.createTransport({
    service: 'gmail',
    auth: {
      user: process.env.EMAIL_SENDER,
      pass: process.env.EMAIL_PASSWORD,
    },
  });
}

function emailConfigured(): boolean {
  const pass = process.env.EMAIL_PASSWORD;
  return Boolean(process.env.EMAIL_SENDER && pass && !/^your_/i.test(pass));
}

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const affiliateId = searchParams.get('affiliate_id');
    const limit = Math.min(parseInt(searchParams.get('limit') || '50', 10) || 50, 200);

    const rows = affiliateId
      ? (db
          .prepare(
            `SELECT * FROM messages
             WHERE is_broadcast = 1 OR (is_broadcast = 0 AND to_id = ?)
             ORDER BY created_at DESC LIMIT ?`
          )
          .all(affiliateId, limit) as Message[])
      : (db
          .prepare(`SELECT * FROM messages ORDER BY created_at DESC LIMIT ?`)
          .all(limit) as Message[]);

    return NextResponse.json({ messages: rows });
  } catch (error) {
    return NextResponse.json({ error: String(error) }, { status: 500 });
  }
}

export async function POST(request: NextRequest) {
  try {
    const { from_id, to_id, message, is_broadcast } = await request.json();

    if (!message?.trim()) {
      return NextResponse.json({ success: false, error: 'Message is empty.' }, { status: 400 });
    }

    const messageId = `msg_${Date.now()}`;
    db.prepare(
      `INSERT INTO messages (id, from_id, to_id, message, is_broadcast) VALUES (?, ?, ?, ?, ?)`
    ).run(messageId, from_id || 'admin', to_id || null, message, is_broadcast ? 1 : 0);

    // The message is already saved. Email delivery is best-effort from here -
    // a missing Gmail app password must not throw away a recorded message.
    let emailed = 0;
    let emailError: string | null = null;

    if (!emailConfigured()) {
      emailError = 'EMAIL_PASSWORD not configured — message saved, no email sent.';
    } else {
      const recipients = is_broadcast
        ? (db.prepare(`SELECT email FROM affiliates WHERE status = 'active'`).all() as {
            email: string;
          }[])
        : (db.prepare(`SELECT email FROM affiliates WHERE id = ?`).all(to_id) as {
            email: string;
          }[]);

      const mailer = transport();
      for (const r of recipients) {
        try {
          await mailer.sendMail({
            from: process.env.EMAIL_SENDER,
            to: r.email,
            subject: 'New Message from Los Iconos de la Bachata',
            html: `<p>${message}</p>`,
          });
          emailed += 1;
        } catch (err) {
          emailError = `Some emails failed: ${String(err)}`;
        }
      }
    }

    return NextResponse.json({ success: true, messageId, emailed, emailError });
  } catch (error) {
    return NextResponse.json({ success: false, error: String(error) }, { status: 500 });
  }
}
