/**
 * Password gate for the shared dashboard.
 *
 * Uses Web Crypto only, so the same helpers run in Edge middleware and in
 * Node route handlers. The cookie carries an HMAC rather than the password,
 * so a stolen cookie never reveals the password itself.
 */

const encoder = new TextEncoder();

export const SESSION_COOKIE = 'liq_session';

function secret(): string {
  // Falls back to the password so a missing SESSION_SECRET degrades to
  // "still gated" rather than "wide open".
  return process.env.SESSION_SECRET || process.env.DASHBOARD_PASSWORD || '';
}

/** Deterministic token for the configured password. */
export async function makeToken(password: string): Promise<string> {
  const key = await crypto.subtle.importKey(
    'raw',
    encoder.encode(secret()),
    { name: 'HMAC', hash: 'SHA-256' },
    false,
    ['sign']
  );
  const sig = await crypto.subtle.sign('HMAC', key, encoder.encode(password));
  return Array.from(new Uint8Array(sig))
    .map((b) => b.toString(16).padStart(2, '0'))
    .join('');
}

/** Length-safe comparison so timing can't be used to guess the token. */
function timingSafeEqual(a: string, b: string): boolean {
  if (a.length !== b.length) return false;
  let diff = 0;
  for (let i = 0; i < a.length; i++) {
    diff |= a.charCodeAt(i) ^ b.charCodeAt(i);
  }
  return diff === 0;
}

export async function isValidSession(cookieValue: string | undefined): Promise<boolean> {
  const password = process.env.DASHBOARD_PASSWORD;
  if (!password) return false; // unset password means nobody gets in
  if (!cookieValue) return false;
  return timingSafeEqual(cookieValue, await makeToken(password));
}

export function isAuthConfigured(): boolean {
  return Boolean(process.env.DASHBOARD_PASSWORD);
}
