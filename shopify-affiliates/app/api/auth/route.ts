import { NextRequest, NextResponse } from 'next/server';
import { SESSION_COOKIE, makeToken, isAuthConfigured } from '@/lib/auth';

// Small in-memory throttle. Enough to make guessing over a public tunnel
// impractical; it resets on restart, which is fine for a single-host app.
const attempts = new Map<string, { count: number; first: number }>();
const WINDOW_MS = 60_000;
const MAX_ATTEMPTS = 8;

function rateLimited(ip: string): boolean {
  const now = Date.now();
  const record = attempts.get(ip);

  if (!record || now - record.first > WINDOW_MS) {
    attempts.set(ip, { count: 1, first: now });
    return false;
  }

  record.count += 1;
  return record.count > MAX_ATTEMPTS;
}

export async function POST(request: NextRequest) {
  if (!isAuthConfigured()) {
    return NextResponse.json(
      { success: false, error: 'DASHBOARD_PASSWORD is not set on the server.' },
      { status: 503 }
    );
  }

  const ip =
    request.headers.get('cf-connecting-ip') ||
    request.headers.get('x-forwarded-for')?.split(',')[0].trim() ||
    'local';

  if (rateLimited(ip)) {
    return NextResponse.json(
      { success: false, error: 'Too many attempts. Wait a minute.' },
      { status: 429 }
    );
  }

  const { password } = await request.json().catch(() => ({ password: '' }));

  if (password !== process.env.DASHBOARD_PASSWORD) {
    return NextResponse.json({ success: false, error: 'Incorrect password.' }, { status: 401 });
  }

  const response = NextResponse.json({ success: true });
  response.cookies.set(SESSION_COOKIE, await makeToken(password), {
    httpOnly: true,
    sameSite: 'lax',
    // The tunnel terminates TLS, so this is safe over the public URL and
    // still works when browsing http://localhost directly.
    secure: request.nextUrl.protocol === 'https:',
    path: '/',
    maxAge: 60 * 60 * 12,
  });
  return response;
}

export async function DELETE() {
  const response = NextResponse.json({ success: true });
  response.cookies.delete(SESSION_COOKIE);
  return response;
}
