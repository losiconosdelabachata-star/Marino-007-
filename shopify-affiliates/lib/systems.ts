import fs from 'fs';
import path from 'path';

/**
 * The Python project root sits one level above this Next.js app.
 * Resolved lazily and marked ignorable so the bundler does not try to trace
 * the entire parent project into the build output.
 */
export function projectRoot(): string {
  return path.resolve(/*turbopackIgnore: true*/ process.cwd(), '..');
}

export type SystemStatus = 'online' | 'offline' | 'degraded' | 'not_configured';

export interface SystemInfo {
  id: string;
  name: string;
  blurb: string;
  status: SystemStatus;
  detail: string;
  lastActivity: string | null;
  /** Script this system's "run now" action executes, relative to PROJECT_ROOT. */
  script: string | null;
}

/** Code and config live at the project root. */
function projectFile(...parts: string[]) {
  return path.join(projectRoot(), ...parts);
}

/** Mutable state lives on the volume when deployed, alongside the code locally. */
function dataFile(...parts: string[]) {
  return path.join(process.env.DATA_DIR || projectRoot(), ...parts);
}

function readJSON<T>(relPath: string): T | null {
  try {
    const raw = fs.readFileSync(dataFile(relPath), 'utf-8');
    return JSON.parse(raw) as T;
  } catch {
    return null;
  }
}

/**
 * Reads a config value. Deployed, everything arrives as real environment
 * variables and there is no .env file at all; locally the .env is the source
 * of truth, so check the process environment first and fall back to the file.
 */
function envValue(key: string): string | null {
  const fromEnv = process.env[key];
  if (fromEnv) return fromEnv;

  try {
    const raw = fs.readFileSync(projectFile('.env'), 'utf-8');
    for (const line of raw.split(/\r?\n/)) {
      const trimmed = line.trim();
      if (!trimmed || trimmed.startsWith('#')) continue;
      const eq = trimmed.indexOf('=');
      if (eq === -1) continue;
      if (trimmed.slice(0, eq).trim() !== key) continue;
      const value = trimmed.slice(eq + 1).trim();
      return value === '' ? null : value;
    }
  } catch {
    /* .env absent */
  }
  return null;
}

/** A credential counts as configured only if it's present and not a placeholder. */
function isConfigured(key: string): boolean {
  const value = envValue(key);
  if (!value) return false;
  return !/^(WAITING|PENDING|WILL_ADD|your_|CHANGE_?ME)/i.test(value);
}

/**
 * Actually calls Shopify rather than checking that a variable is non-empty.
 *
 * Presence is not health: the store was reported "online" for days while
 * every request 404'd against a domain that does not exist, using a shared
 * secret that cannot authenticate the Admin API at all.
 */
async function checkShopify(): Promise<{ status: SystemStatus; detail: string }> {
  const store = envValue('SHOPIFY_STORE');
  const token = envValue('SHOPIFY_API_PASSWORD');

  if (!store || !token) {
    return { status: 'not_configured', detail: 'Store or access token missing' };
  }

  if (token.startsWith('shpss_')) {
    return {
      status: 'not_configured',
      detail: 'Token is a shared secret (shpss_) — needs an Admin API token (shpat_)',
    };
  }

  try {
    const res = await fetch(`https://${store}/admin/api/2025-01/shop.json`, {
      headers: { 'X-Shopify-Access-Token': token },
      signal: AbortSignal.timeout(4000),
      cache: 'no-store',
    });

    if (res.ok) {
      const data = await res.json();
      return { status: 'online', detail: `Connected to ${data.shop?.name ?? store}` };
    }
    if (res.status === 401) {
      return { status: 'offline', detail: 'Rejected: invalid API key or access token' };
    }
    if (res.status === 404) {
      return { status: 'offline', detail: `No such store: ${store}` };
    }
    return { status: 'degraded', detail: `Shopify returned HTTP ${res.status}` };
  } catch {
    return { status: 'offline', detail: 'Could not reach Shopify' };
  }
}

async function checkWhatsApp(): Promise<{ status: SystemStatus; detail: string }> {
  const url = envValue('WHATSAPP_SERVER_URL') || 'http://localhost:3000';
  try {
    const res = await fetch(`${url}/status`, {
      signal: AbortSignal.timeout(2500),
      cache: 'no-store',
    });
    if (!res.ok) return { status: 'degraded', detail: `Bridge returned HTTP ${res.status}` };

    const data = await res.json();
    if (data.connected) return { status: 'online', detail: 'Linked and receiving' };
    if (data.awaiting_scan) return { status: 'degraded', detail: 'Waiting for QR scan' };
    return { status: 'degraded', detail: 'Bridge up, WhatsApp not linked' };
  } catch {
    return { status: 'offline', detail: 'Bridge not running on ' + url };
  }
}

export async function getSystems(): Promise<SystemInfo[]> {
  const [whatsapp, shopify] = await Promise.all([checkWhatsApp(), checkShopify()]);

  const blogTracker = readJSON<{ processed_photos?: string[]; last_run?: string }>('blog_tracker.json');
  const orders = readJSON<Record<string, { timestamp?: string; amount?: string }>>('processed_orders.json');

  const orderEntries = Object.entries(orders || {});
  const lastOrderTs = orderEntries
    .map(([, o]) => o?.timestamp)
    .filter(Boolean)
    .sort()
    .pop();

  // Based on a live probe, not on a variable being non-empty.
  const shopifyReady = shopify.status === 'online';
  const printifyReady = isConfigured('PRINTIFY_API_KEY');
  const adsReady =
    isConfigured('GOOGLE_ADS_DEVELOPER_TOKEN') && isConfigured('GOOGLE_ADS_REFRESH_TOKEN');
  const claudeReady = isConfigured('ANTHROPIC_API_KEY');
  // Deployed, auth comes from a refresh token; locally it's a cached pickle.
  const photosReady =
    isConfigured('GOOGLE_PHOTOS_REFRESH_TOKEN') ||
    fs.existsSync(dataFile('google_photos_token.pickle'));

  return [
    {
      id: 'whatsapp',
      name: 'WhatsApp Bridge',
      blurb: 'Marino 007 alert channel',
      status: whatsapp.status,
      detail: whatsapp.detail,
      lastActivity: null,
      script: null,
    },
    {
      id: 'orders',
      name: 'Order Automation',
      blurb: 'Hourly Shopify sweep to Printify',
      status: shopifyReady && printifyReady ? 'online' : 'not_configured',
      detail: !shopifyReady
        ? `Blocked by Shopify: ${shopify.detail}`
        : !printifyReady
          ? 'Printify API key missing'
          : `${orderEntries.length} orders processed`,
      lastActivity: lastOrderTs || null,
      script: 'order_automation.py',
    },
    {
      id: 'shopify',
      name: 'Shopify Store',
      blurb: 'losiconosdelabachata.com',
      status: shopify.status,
      detail: shopify.detail,
      lastActivity: null,
      script: null,
    },
    {
      id: 'printify',
      name: 'Printify Fulfillment',
      blurb: 'Print-on-demand pipeline',
      status: printifyReady ? 'online' : 'not_configured',
      detail: printifyReady ? 'Connected' : 'Awaiting API key from Printify support',
      lastActivity: null,
      script: null,
    },
    {
      id: 'blog',
      name: 'Blog Engine',
      blurb: 'Photos to Claude to email blast',
      status: claudeReady && photosReady ? 'online' : 'not_configured',
      detail: !claudeReady
        ? 'Anthropic API key missing'
        : !photosReady
          ? 'Google Photos not authenticated'
          : `${blogTracker?.processed_photos?.length ?? 0} posts published`,
      lastActivity: blogTracker?.last_run || null,
      script: 'blog_scheduler.py',
    },
    {
      id: 'ads',
      name: 'Google Ads',
      blurb: 'Campaign automation',
      status: adsReady ? 'online' : 'not_configured',
      detail: adsReady ? 'Campaigns manageable' : 'Developer token not yet approved',
      lastActivity: null,
      script: null,
    },
    {
      id: 'affiliates',
      name: 'Affiliate Hub',
      blurb: 'Roster, messaging, commissions',
      status: 'online',
      detail: 'Running in this dashboard',
      lastActivity: null,
      script: null,
    },
  ];
}
