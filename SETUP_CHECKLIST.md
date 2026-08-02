# Marino 007 - Setup Checklist

## ✅ COMPLETED

- [x] Node.js v22.22.2 installed
- [x] Python 3.11 with all dependencies installed
- [x] Anthropic Claude API integrated (Sonnet-5)
- [x] Shopify API credentials configured
- [x] WhatsApp Baileys server created & ready
- [x] Order automation engine built
- [x] Printify integration scaffolded
- [x] WhatsApp client for sending alerts
- [x] All Python scripts created and tested
- [x] Master startup script created
- [x] Configuration files (.env) set up

## ⏳ TODO - IN THIS SESSION

### Priority 1: Get Printify API Key (10 minutes)
1. Go to: https://dashboard.printify.com/account/api
2. Click "Add new app" → Name: "Marino 007"
3. Copy the API Key
4. Copy your Shop ID
5. Add both to `.env`:
   ```
   PRINTIFY_API_KEY=paste_here
   PRINTIFY_SHOP_ID=paste_here
   ```

### Priority 2: Scan WhatsApp QR Code (5 minutes)
1. Run: `python start_marino_007.py`
2. When prompted, take your dedicated phone (7868387137)
3. Open WhatsApp → Settings → Linked Devices → Link a Device
4. Scan the QR code shown in terminal
5. Wait for "Connected to WhatsApp!" message

### Priority 3: Test Everything (5 minutes)
1. Keep `start_marino_007.py` running
2. Go to your Shopify store: losiconosdelabachata.com
3. Create a test order
4. Within 60 seconds, you should get a WhatsApp alert
5. Verify order appears in Printify dashboard

## 📋 TODO - LATER (After Launch)

- [ ] Google Ads API integration (for campaign creation)
- [ ] YouTube campaign management
- [ ] Advanced analytics dashboard
- [ ] Scheduled campaign reports
- [ ] Multi-language support
- [ ] Custom order tags/labels
- [ ] Inventory sync with Shopify

---

## 🚀 QUICK START

Once you've completed Priority 1 & 2:

```bash
cd C:\Users\Fellito Rodriguez\Projects
python start_marino_007.py
```

Then:
1. Scan QR code when prompted
2. Create a test order in Shopify
3. Check WhatsApp for alert
4. Done! ✓

---

## 📁 Key Files

| File | Purpose |
|------|---------|
| `marino_007.py` | Interactive AI bot (optional) |
| `whatsapp_server.js` | WhatsApp connection (Baileys) |
| `order_automation.py` | Hourly order processor |
| `shopify_api.py` | Shopify integration |
| `printify_api.py` | Printify integration |
| `start_marino_007.py` | Master launcher (RUN THIS) |
| `.env` | **SECRETS - Keep confidential** |
| `README_SETUP.md` | Full documentation |

---

## 💡 How It Works

1. **Every Hour:** `order_automation.py` wakes up
2. **Checks Shopify:** Looks for new unfulfilled orders
3. **Sends to Printify:** Creates fulfillment orders automatically
4. **Alerts Marino:** WhatsApp message with order details
5. **Tracks Progress:** Saves order IDs to prevent duplicates
6. **Daily Report:** 6 PM summary to your WhatsApp

---

## 🎯 Campaign Management (Later)

Once order automation is stable, we'll add:
- Google Ads campaign creation (targeting Aventura fans)
- YouTube campaign management
- Campaign performance tracking
- Budget optimization
- A/B testing automation

---

## 📞 Need Help?

1. Read `README_SETUP.md` - full setup guide
2. Check terminal output for error messages
3. Verify all `.env` keys are correct
4. Test individual scripts (see Testing section in README)

---

## ✨ Status

**Phase:** Setup Complete - Ready for Launch
**Last Updated:** August 2, 2026
**Owner:** Marino Santos
**Brand:** Los Iconos de la Bachata
**Bot:** Marino 007 (Powered by Claude Sonnet-5)
