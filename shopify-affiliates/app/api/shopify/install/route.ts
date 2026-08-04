import { NextRequest, NextResponse } from 'next/server';
import crypto from 'crypto';

export const dynamic = 'force-dynamic';

/**
 * Kicks off Shopify's OAuth handshake.
 *
 * Dev Dashboard apps never display an Admin API access token - the token is
 * issued to the app's redirect URL during this exchange. SHOPIFY_API_KEY is
 * the Client ID and SHOPIFY_API_PASSWORD is the Client Secret; neither can
 * authenticate the Admin API on its own, which is why every request 401'd.
 */
export async function GET(request: NextRequest) {
  const store = process.env.SHOPIFY_STORE;
  const clientId = process.env.SHOPIFY_API_KEY;

  if (!store || !clientId) {
    return NextResponse.json(
      { error: 'SHOPIFY_STORE and SHOPIFY_API_KEY must be set.' },
      { status: 500 }
    );
  }

  const scopes = [
    'read_orders',
    'write_orders',
    'read_fulfillments',
    'write_fulfillments',
    'read_products',
    'read_customers',
  ].join(',');

  // Carried through the round trip and checked on the way back, so a third
  // party cannot walk us through an exchange we did not start.
  const state = crypto.randomBytes(16).toString('hex');
  const origin = request.nextUrl.origin;
  const redirectUri = `${origin}/api/shopify/callback`;

  const authorizeUrl =
    `https://${store}/admin/oauth/authorize` +
    `?client_id=${encodeURIComponent(clientId)}` +
    `&scope=${encodeURIComponent(scopes)}` +
    `&redirect_uri=${encodeURIComponent(redirectUri)}` +
    `&state=${state}`;

  const response = NextResponse.redirect(authorizeUrl);
  response.cookies.set('shopify_oauth_state', state, {
    httpOnly: true,
    sameSite: 'lax',
    path: '/',
    maxAge: 600,
  });
  return response;
}
