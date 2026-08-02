# Marino 007 - Los Iconos de la Bachata Order Automation Bot

## 🎯 What This Bot Does

Marino 007 is a fully automated order fulfillment bot that:

1. **📱 Receives WhatsApp Messages** - Direct communication via WhatsApp on your dedicated phone
2. **🛍️ Reads Shopify Orders** - Monitors losiconosdelabachata.com for new orders every hour
3. **📦 Sends to Printify** - Automatically fulfills orders via Printify's print-on-demand service
4. **✉️ Sends WhatsApp Alerts** - Notifies you of new orders, fulfillment status, and daily reports
5. **🎨 Manages Campaigns** - Creates and manages Google Ads & YouTube campaigns targeting Aventura fans

---

## ✅ What's Already Configured

- ✅ Node.js v22.22.2 (for WhatsApp/Baileys)
- ✅ Python 3.11 (for bot automation)
- ✅ Shopify API credentials
- ✅ WhatsApp Server (Baileys) ready to connect
- ✅ Claude AI integration (Sonnet-5)
- ✅ .env file with API keys

---

## ⚙️ What You Need to Add

### 1. **Printify API Key** (Required for order fulfillment)

Go to: https://dashboard.printify.com/account/api

- Click "Add new app"
- Name it "Marino 007"
- Copy the **API Key**
- Add to `.env`:
```
PRINTIFY_API_KEY=your_api_key_here
PRINTIFY_SHOP_ID=your_shop_id_here
```

### 2. **Scan WhatsApp QR Code** (Required for messaging)

This links your dedicated phone (7868387137) to the bot:

```bash
python start_marino_007.py
```

When prompted, scan the QR code with your dedicated phone:
- Go to WhatsApp
- Settings → Linked Devices → Link a Device
- Scan the QR code

### 3. **Google Ads API** (For campaign management - optional for now)

Will add later. For now, you can create campaigns manually in Google Ads and the bot will monitor them.

---

## 🚀 How to Start the Bot

### Option 1: Start Everything (Recommended)
```bash
python start_marino_007.py
```

This starts:
- WhatsApp Server on localhost:3000
- Order Automation (checks every hour)
- Shows you the startup status

### Option 2: Start Individual Services

**Start WhatsApp Server:**
```bash
node whatsapp_server.js
```

**Start Order Automation:**
```bash
python order_automation.py
```

**Start Interactive Chat Bot:**
```bash
python marino_007.py
```

---

## 📋 File Structure

```
Marino-007/
├── marino_007.py              # Main interactive chat bot
├── whatsapp_server.js         # WhatsApp/Baileys server
├── whatsapp_client.py         # Python WhatsApp client
├── shopify_api.py             # Shopify API integration
├── printify_api.py            # Printify API integration
├── order_automation.py        # Hourly order processing
├── start_marino_007.py        # Master startup script
├── .env                       # API keys (KEEP SECRET!)
├── .env.example               # Template (safe to share)
├── auth_info/                 # WhatsApp session storage
├── skills/                    # Bot skills/knowledge
├── MEMORY.md                  # Bot memory/persistence
└── processed_orders.json      # Order tracking (auto-created)
```

---

## 🔄 How the Bot Works

### Hourly Order Workflow

1. **Check Time:** Every hour at :00
2. **Get Orders:** Query Shopify API for unfulfilled orders
3. **Send to Printify:** Create fulfillment orders in Printify
4. **Alert Marino:** Send WhatsApp message with order details
5. **Track Status:** Save order ID to prevent duplicates

### Example WhatsApp Alert:
```
🎉 NEW ORDER RECEIVED
Order #1001
Customer: customer@email.com
Total: $45.99
Items: 2 product(s)

✓ Sent to Printify for fulfillment
Status: Processing
```

### Daily Report:
Sent at 6:00 PM with summary of all orders processed that day.

---

## 📱 WhatsApp Commands

Once linked, you can send messages to the bot:

- **"Check orders"** → Get unfulfilled orders
- **"Campaign status"** → See ad campaign performance
- **"Daily report"** → Get today's summary
- **"Help"** → List all commands

---

## 🔐 Security Notes

1. **Never share** your `.env` file (contains API keys)
2. **Use `.env.example`** as a template if sharing with team
3. **Keep PRINTIFY_API_KEY secret** - it can create orders
4. **WhatsApp linked device** - only one device can be linked at a time
5. **Shopify credentials** - read-only for safety

---

## 🧪 Testing

### Test Shopify Connection:
```bash
python -c "from shopify_api import *; print(get_orders_needing_fulfillment())"
```

### Test Printify Connection:
```bash
python -c "from printify_api import *; print(get_shops())"
```

### Test WhatsApp:
```bash
python -c "from whatsapp_client import *; send_to_marino('Test message')"
```

---

## 🐛 Troubleshooting

### WhatsApp not connecting?
- QR code expires after 60 seconds, try again
- Make sure your dedicated phone can reach the internet
- Restart: `node whatsapp_server.js`

### Orders not being processed?
- Check Shopify API credentials in `.env`
- Verify store URL is correct
- Check Printify API key is set

### Bot crashes?
- Check `.env` file has all required keys
- Look in terminal output for error messages
- Restart the service

---

## 📧 Configuration Files

### .env Template
```
ANTHROPIC_API_KEY=your_key
SHOPIFY_STORE=losiconosdelabachata.myshopify.com
SHOPIFY_API_KEY=your_key
SHOPIFY_API_PASSWORD=your_key
PRINTIFY_API_KEY=your_key
PRINTIFY_SHOP_ID=your_id
WHATSAPP_SERVER_URL=http://localhost:3000
MARINO_PHONE=7868387137
```

---

## 🎯 Next Steps

1. ✅ Get Printify API key and add to `.env`
2. ✅ Scan WhatsApp QR code to link your dedicated phone
3. ✅ Run `python start_marino_007.py` to start all services
4. ⏳ Test by creating an order in your Shopify store
5. 🔄 Monitor WhatsApp for alerts

---

## 📞 Support

If something doesn't work:
1. Check the terminal output for error messages
2. Verify all API keys are correct in `.env`
3. Test individual components (see Testing section above)
4. Restart the service

---

**Built with ❤️ for Marino Santos & Los Iconos de la Bachata**
Powered by Marino 007 | Claude Sonnet-5 | Shopify | Printify | WhatsApp
