import Database from 'better-sqlite3';
import path from 'path';

/**
 * The connection is opened lazily, on first query.
 *
 * Opening it at module scope crashes `next build`: collecting page data
 * imports every route, which would open SQLite inside the build sandbox and
 * segfault the build worker. Nothing should touch the disk until a request
 * actually arrives.
 */
let instance: Database.Database | null = null;
let initialized = false;

function connect(): Database.Database {
  if (instance) return instance;

  // DATA_DIR points at the mounted volume in a container; without it the
  // database would be wiped on every deploy.
  const dataDir = process.env.DATA_DIR || process.cwd();
  const dbPath = path.join(dataDir, 'affiliates.db');

  instance = new Database(dbPath);
  instance.pragma('journal_mode = WAL');
  return instance;
}

export function initializeDatabase() {
  if (initialized) return;

  connect().exec(`
    CREATE TABLE IF NOT EXISTS affiliates (
      id TEXT PRIMARY KEY,
      shopify_id TEXT UNIQUE,
      name TEXT NOT NULL,
      email TEXT NOT NULL,
      phone TEXT,
      status TEXT DEFAULT 'active',
      commission_rate REAL DEFAULT 0,
      total_sales REAL DEFAULT 0,
      total_commissions REAL DEFAULT 0,
      created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
      updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS messages (
      id TEXT PRIMARY KEY,
      from_id TEXT NOT NULL,
      to_id TEXT,
      message TEXT NOT NULL,
      is_broadcast INTEGER DEFAULT 0,
      created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS affiliates_messages (
      affiliate_id TEXT NOT NULL,
      message_id TEXT NOT NULL,
      read_at DATETIME,
      PRIMARY KEY (affiliate_id, message_id)
    );

    CREATE TABLE IF NOT EXISTS sales (
      id TEXT PRIMARY KEY,
      affiliate_id TEXT NOT NULL,
      order_id TEXT,
      amount REAL NOT NULL,
      commission REAL NOT NULL,
      created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
      FOREIGN KEY (affiliate_id) REFERENCES affiliates(id)
    );

    CREATE INDEX IF NOT EXISTS idx_messages_created ON messages(created_at);
    CREATE INDEX IF NOT EXISTS idx_sales_affiliate ON sales(affiliate_id);
  `);

  initialized = true;
}

/** Connects and ensures the schema exists. Call this inside handlers. */
export function getDb(): Database.Database {
  const db = connect();
  initializeDatabase();
  return db;
}

/**
 * Back-compat shim so existing `db.prepare(...)` call sites keep working.
 * Each property access resolves through getDb(), so the connection is still
 * only created when a query actually runs.
 */
const lazyDb = new Proxy({} as Database.Database, {
  get(_target, prop) {
    const real = getDb() as unknown as Record<string | symbol, unknown>;
    const value = real[prop];
    return typeof value === 'function' ? value.bind(real) : value;
  },
});

export default lazyDb;
