import { NextRequest, NextResponse } from 'next/server';
import crypto from 'crypto';
import fs from 'fs';
import path from 'path';
import { projectRoot } from '@/lib/systems';

export const dynamic = 'force-dynamic';

/** Shopify signs the callback. An unverified code could be planted by anyone. */
function verifyHmac(searchParams: URLSearchParams, secret: string): boolean {
  const received = searchParams.get('hmac');
  if (!received) return false;

  const message = [...searchParams.entries()]
    .filter(([k]) => k !== 'hmac' && k !== 'signature')
    .sort(([a], [b]) => a.localeCompare(b))
    .map(([k, v]) => `${k}=${v}`)
    .join('&');

  const computed = crypto.createHmac('sha256', secret).update(message).digest('hex');

  const a = Buffer.from(computed, 'utf-8');
  const b = Buffer.from(received, 'utf-8');
  return a.length === b.length && crypto.timingSafeEqual(a, b);
}

/** Writes the token into .env so the Python scripts pick it up too. */
function persistToken(token: string) {
  const envPath = path.join(projectRoot(), '.env');
  let contents = '';
  try {
    contents = fs.readFileSync(envPath, 'utf-8');
  } catch {
    /* no .env yet */
  }

  const line = `SHOPIFY_ACCESS_TOKEN=${token}`;
  contents = /^SHOPIFY_ACCESS_TOKEN=.*$/m.test(contents)
    ? contents.replace(/^SHOPIFY_ACCESS_TOKEN=.*$/m, line)
    : `${contents.trimEnd()}\n\n# Admin API access token from the OAuth handshake.\n${line}\n`;

  fs.writeFileSync(envPath, contents, 'utf-8');
}

export async function GET(request: NextRequest) {
  const params = request.nextUrl.searchParams;
  const secret = process.env.SHOPIFY_API_PASSWORD; // Client Secret
  const clientId = process.env.SHOPIFY_API_KEY; // Client ID
  const shop = params.get('shop');
  const code = params.get('code');

  if (!secret || !clientId) {
    return NextResponse.json({ error: 'Shopify client credentials missing.' }, { status: 500 });
  }
  if (!shop || !code) {
    return NextResponse.json({ error: 'Missing shop or code.' }, { status: 400 });
  }

  if (params.get('state') !== request.cookies.get('shopify_oauth_state')?.value) {
    return NextResponse.json({ error: 'State mismatch - restart the install.' }, { status: 400 });
  }

  if (!verifyHmac(params, secret)) {
    return NextResponse.json({ error: 'HMAC verification failed.' }, { status: 400 });
  }

  // Only ever talk to a real Shopify domain, whatever the callback claims.
  if (!/^[a-zA-Z0-9][a-zA-Z0-9-]*\.myshopify\.com$/.test(shop)) {
    return NextResponse.json({ error: 'Invalid shop domain.' }, { status: 400 });
  }

  try {
    const res = await fetch(`https://${shop}/admin/oauth/access_token`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        client_id: clientId,
        client_secret: secret,
        code,
      }),
    });

    if (!res.ok) {
      return NextResponse.json(
        { error: `Token exchange failed: HTTP ${res.status}` },
        { status: 502 }
      );
    }

    const data = await res.json();
    if (!data.access_token) {
      return NextResponse.json({ error: 'No access token in response.' }, { status: 502 });
    }

    persistToken(data.access_token);

    const html = `<!doctype html><meta charset="utf-8">
<style>
 body{background:#05060d;color:#e8ecf8;font-family:system-ui,sans-serif;
      display:grid;place-items:center;min-height:100vh;margin:0}
 .card{border:1px solid rgba(212,175,55,.3);border-radius:14px;padding:2.5rem;max-width:32rem}
 h1{color:#f2d675;margin:0 0 .5rem;font-size:1.25rem}
 code{background:rgba(6,9,20,.8);padding:.15rem .4rem;border-radius:4px;color:#35e8ff}
 p{color:#7d88a8;line-height:1.6}
 a{color:#f2d675}
</style>
<div class="card">
  <h1>Shopify connected</h1>
  <p>Access token saved to <code>.env</code> as <code>SHOPIFY_ACCESS_TOKEN</code>
     with scopes: ${(data.scope || '').split(',').join(', ')}</p>
  <p>Restart the dashboard so it picks up the new value, then
     <a href="/">return to the command center</a>.</p>
</div>`;

    return new NextResponse(html, { headers: { 'Content-Type': 'text/html' } });
  } catch (error) {
    return NextResponse.json({ error: String(error) }, { status: 500 });
  }
}
