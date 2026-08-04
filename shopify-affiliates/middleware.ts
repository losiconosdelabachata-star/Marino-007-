import { NextRequest, NextResponse } from 'next/server';
import { SESSION_COOKIE, isValidSession, isAuthConfigured } from '@/lib/auth';

/**
 * Gates the whole dashboard. This matters most for /api/control, which can
 * publish blog posts and email customers, and for the WhatsApp QR - anyone
 * who scans that pairing code would take over the bot's session.
 */
// /api/shopify handles the OAuth round trip. Shopify redirects the browser
// back without our session cookie, so it cannot sit behind the password gate.
// It is protected instead by HMAC signature plus a state nonce, which is the
// stronger check for this particular flow.
const PUBLIC_PATHS = ['/login', '/api/auth', '/api/shopify'];

export async function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;

  if (PUBLIC_PATHS.some((p) => pathname.startsWith(p))) {
    return NextResponse.next();
  }

  // Refuse to serve at all rather than silently running unprotected.
  if (!isAuthConfigured()) {
    return new NextResponse(
      'DASHBOARD_PASSWORD is not set. Add it to .env.local and restart.',
      { status: 503, headers: { 'Content-Type': 'text/plain' } }
    );
  }

  const authed = await isValidSession(request.cookies.get(SESSION_COOKIE)?.value);
  if (authed) return NextResponse.next();

  // APIs get a status code; humans get the login page.
  if (pathname.startsWith('/api/')) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  }

  const url = request.nextUrl.clone();
  url.pathname = '/login';
  url.searchParams.set('next', pathname);
  return NextResponse.redirect(url);
}

export const config = {
  // Everything except Next internals and static files.
  matcher: ['/((?!_next/static|_next/image|favicon.ico|.*\\.svg).*)'],
};
