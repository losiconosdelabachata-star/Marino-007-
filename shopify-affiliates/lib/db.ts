import Database from 'better-sqlite3';
import path from 'path';

const dbPath = path.join(process.cwd(), 'affiliates.db');
const db = new Database(dbPath);

db.pragma('journal_mode = WAL');

export function initializeDatabase() {
  db.exec(`
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
      created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
      FOREIGN KEY (from_id) REFERENCES affiliates(id)
    );

    CREATE TABLE IF NOT EXISTS affiliates_messages (
      affiliate_id TEXT NOT NULL,
      message_id TEXT NOT NULL,
      read_at DATETIME,
      PRIMARY KEY (affiliate_id, message_id),
      FOREIGN KEY (affiliate_id) REFERENCES affiliates(id),
      FOREIGN KEY (message_id) REFERENCES messages(id)
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
}

export default db;
