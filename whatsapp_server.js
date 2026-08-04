const express = require('express');
const cors = require('cors');
const fs = require('fs');
const path = require('path');
const QRCode = require('qrcode');
const { default: makeWASocket, useMultiFileAuthState, DisconnectReason } = require('@whiskeysockets/baileys');

const app = express();
app.use(express.json());
app.use(cors());

// 3000-3004 are taken by other local projects (Leon Business Center, eclat,
// barbershop, the dashboard), so default clear of them.
const PORT = process.env.WHATSAPP_PORT || 3010;
const AUTH_DIR = path.join(__dirname, 'auth_info');
const MESSAGES_FILE = path.join(__dirname, 'received_messages.json');

// Ensure auth directory exists
if (!fs.existsSync(AUTH_DIR)) {
  fs.mkdirSync(AUTH_DIR, { recursive: true });
}

// Store for received messages
let receivedMessages = [];
let socket = null;
let isConnected = false;

// Latest QR as a data URL so the dashboard can render it without terminal access
let currentQR = null;
let qrGeneratedAt = null;
let lastDisconnectReason = null;

// Load received messages from file
function loadMessages() {
  if (fs.existsSync(MESSAGES_FILE)) {
    try {
      receivedMessages = JSON.parse(fs.readFileSync(MESSAGES_FILE, 'utf-8'));
    } catch (err) {
      receivedMessages = [];
    }
  }
}

// Save received messages to file
function saveMessages() {
  fs.writeFileSync(MESSAGES_FILE, JSON.stringify(receivedMessages, null, 2));
}

// Guards against the runaway-socket bug: without these, every 'close' event
// spawned another socket while the old one kept its listeners attached, so
// sockets stacked up until they starved the event loop and Express stopped
// answering requests.
let connecting = false;
let reconnectDelay = 2000;
const MAX_RECONNECT_DELAY = 60000;

// Initialize WhatsApp connection
async function connectToWhatsApp() {
  if (connecting) {
    console.log('↩︎  Connect already in flight, skipping duplicate attempt');
    return;
  }
  connecting = true;

  // Tear down any previous socket so its listeners die with it.
  if (socket) {
    try {
      socket.ev.removeAllListeners();
      socket.end();
    } catch (_) {
      /* already dead */
    }
    socket = null;
  }

  const { state, saveCreds } = await useMultiFileAuthState(AUTH_DIR);

  socket = makeWASocket({
    auth: state,
  });

  socket.ev.on('connection.update', async (update) => {
    const { connection, lastDisconnect, qr } = update;

    if (qr) {
      // Render to a data URL so GET /qr can serve it to the dashboard
      try {
        currentQR = await QRCode.toDataURL(qr, { width: 400, margin: 2 });
        qrGeneratedAt = new Date().toISOString();
      } catch (err) {
        console.error('Failed to render QR:', err.message);
      }
      // The socket is live and simply waiting on a human, so the attempt is
      // no longer "in flight" - release the guard or /reconnect would refuse.
      connecting = false;
      console.log('\n📱 QR Code generated. Scan it with your WhatsApp on the dedicated phone.');
      console.log('Settings > Linked Devices > Link a Device');
      console.log('Or open the dashboard and scan it there.\n');
    }

    if (connection === 'close') {
      isConnected = false;
      connecting = false;
      const statusCode = (lastDisconnect?.error)?.output?.statusCode;
      const shouldReconnect = statusCode !== DisconnectReason.loggedOut;
      lastDisconnectReason = shouldReconnect ? 'connection_lost' : 'logged_out';
      console.log('Connection closed:', statusCode, '| reconnecting:', shouldReconnect);

      if (shouldReconnect) {
        // Backoff, so a persistent failure can't become a hot loop.
        console.log(`⏳ Reconnecting in ${reconnectDelay / 1000}s`);
        setTimeout(connectToWhatsApp, reconnectDelay);
        reconnectDelay = Math.min(reconnectDelay * 2, MAX_RECONNECT_DELAY);
      } else {
        console.log('🔒 Logged out. POST /reconnect with {"hard":true} to re-link.');
      }
    } else if (connection === 'open') {
      isConnected = true;
      connecting = false;
      reconnectDelay = 2000; // healthy again, reset backoff
      currentQR = null; // linked, so the QR is spent
      qrGeneratedAt = null;
      lastDisconnectReason = null;
      console.log('✓ Connected to WhatsApp!');
    }
  });

  socket.ev.on('messages.upsert', (m) => {
    const message = m.messages[0];
    if (!message.key.fromMe && message.message) {
      const text = message.message.conversation || message.message.extendedTextMessage?.text || '';
      const sender = message.key.remoteJid;

      const msgObj = {
        from: sender,
        text: text,
        timestamp: new Date().toISOString(),
        messageId: message.key.id,
      };

      receivedMessages.push(msgObj);
      saveMessages();

      console.log(`📨 New message from ${sender}: ${text}`);
    }
  });

  socket.ev.on('creds.update', saveCreds);
}

// HTTP Endpoints
app.get('/status', (req, res) => {
  res.json({
    connected: isConnected,
    awaiting_scan: !isConnected && currentQR !== null,
    last_disconnect_reason: lastDisconnectReason,
    timestamp: new Date().toISOString(),
  });
});

// Serve the pairing QR to the dashboard so re-linking never needs terminal access
app.get('/qr', (req, res) => {
  if (isConnected) {
    return res.json({ connected: true, qr: null, message: 'Already linked - no QR needed' });
  }
  if (!currentQR) {
    return res.json({
      connected: false,
      qr: null,
      message: 'No QR available yet. POST /reconnect to request one.',
    });
  }
  res.json({ connected: false, qr: currentQR, generated_at: qrGeneratedAt });
});

// Force a fresh pairing cycle. `hard` wipes stored creds for a full re-link.
app.post('/reconnect', async (req, res) => {
  try {
    const hard = req.body?.hard === true;

    if (hard && fs.existsSync(AUTH_DIR)) {
      fs.rmSync(AUTH_DIR, { recursive: true, force: true });
      fs.mkdirSync(AUTH_DIR, { recursive: true });
      console.log('🗑️  Cleared stored credentials for a full re-link');
    }

    isConnected = false;
    currentQR = null;
    connecting = false; // an explicit request always wins over the guard
    reconnectDelay = 2000;

    await connectToWhatsApp();
    res.json({
      success: true,
      hard_reset: hard,
      message: 'Reconnect started. Poll GET /qr for the pairing code.',
    });
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

app.post('/send', async (req, res) => {
  try {
    const { phone, message } = req.body;

    if (!phone || !message) {
      return res.status(400).json({ error: 'phone and message required' });
    }

    if (!isConnected) {
      return res.status(503).json({ error: 'WhatsApp not connected' });
    }

    // Format phone number (add @s.whatsapp.net if not present)
    const jid = phone.includes('@') ? phone : `${phone}@s.whatsapp.net`;

    await socket.sendMessage(jid, { text: message });
    res.json({ success: true, sent_to: phone, message: message });
    console.log(`✓ Sent message to ${phone}`);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

app.get('/messages', (req, res) => {
  res.json({ messages: receivedMessages, count: receivedMessages.length });
});

app.post('/messages/clear', (req, res) => {
  receivedMessages = [];
  saveMessages();
  res.json({ success: true, message: 'Messages cleared' });
});

app.get('/health', (req, res) => {
  res.json({ status: 'ok', whatsapp_connected: isConnected });
});

// Start server
app.listen(PORT, () => {
  console.log(`\n🚀 Marino 007 WhatsApp Server running on http://localhost:${PORT}`);
  console.log(`📡 Endpoints:`);
  console.log(`   GET  /status      - Check connection status`);
  console.log(`   POST /send        - Send WhatsApp message`);
  console.log(`   GET  /messages    - Get received messages`);
  console.log(`   POST /messages/clear - Clear message log`);
  console.log(`   GET  /health      - Health check\n`);
});

// Connect to WhatsApp
connectToWhatsApp();
