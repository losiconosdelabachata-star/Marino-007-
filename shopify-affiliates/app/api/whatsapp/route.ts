import { NextRequest, NextResponse } from 'next/server';

const BRIDGE = process.env.WHATSAPP_SERVER_URL || 'http://localhost:3000';

export const dynamic = 'force-dynamic';

/** Fetches the current pairing QR (and link state) from the Baileys bridge. */
export async function GET() {
  try {
    const res = await fetch(`${BRIDGE}/qr`, {
      signal: AbortSignal.timeout(3000),
      cache: 'no-store',
    });
    const data = await res.json();
    return NextResponse.json({ reachable: true, ...data });
  } catch {
    return NextResponse.json({
      reachable: false,
      connected: false,
      qr: null,
      message: `WhatsApp bridge unreachable at ${BRIDGE}. Start it with: node whatsapp_server.js`,
    });
  }
}

/**
 * Triggers a reconnect, or requests a pairing code.
 *
 * `{ pair: "17868387137" }` asks for an 8-character code to type into the
 * phone - easier than a QR when nobody is sitting in front of the dashboard.
 * `{ hard: true }` wipes creds so a brand-new phone can link.
 */
export async function POST(request: NextRequest) {
  try {
    const body = await request.json().catch(() => ({}));

    if (body.pair) {
      const res = await fetch(`${BRIDGE}/pair`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ phone: body.pair }),
        signal: AbortSignal.timeout(15000),
      });
      return NextResponse.json(await res.json());
    }

    const res = await fetch(`${BRIDGE}/reconnect`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ hard: body.hard === true }),
      signal: AbortSignal.timeout(8000),
    });
    const data = await res.json();
    return NextResponse.json(data);
  } catch (error) {
    return NextResponse.json(
      { success: false, error: `Could not reach the bridge at ${BRIDGE}` },
      { status: 502 }
    );
  }
}
