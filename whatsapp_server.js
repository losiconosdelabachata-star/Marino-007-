const express = require('express');
const cors = require('cors');
const fs = require('fs');
const path = require('path');
const { default: makeWASocket, useMultiFileAuthState, DisconnectReason } = require('@whiskeysockets/baileys');

const app = express();
app.use(express.json());
app.use(cors());

const PORT = 3000;
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

// Initialize WhatsApp connection
async function connectToWhatsApp() {
  const { state, saveCreds } = await useMultiFileAuthState(AUTH_DIR);

  socket = makeWASocket({
    auth: state,
    printQRInTerminal: true,
  });

  socket.ev.on('connection.update', (update) => {
    const { connection, lastDisconnect, qr } = update;

    if (qr) {
      console.log('\n📱 QR Code generated. Scan it with your WhatsApp on the dedicated phone.');
      console.log('Settings > Linked Devices > Link a Device\n');
    }

    if (connection === 'close') {
      const shouldReconnect = (lastDisconnect?.error)?.output?.statusCode !== DisconnectReason.loggedOut;
      console.log('Connection closed due to', lastDisconnect?.error, ', reconnecting:', shouldReconnect);
      if (shouldReconnect) {
        connectToWhatsApp();
      }
    } else if (connection === 'open') {
      isConnected = true;
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
  res.json({ connected: isConnected, timestamp: new Date().toISOString() });
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
