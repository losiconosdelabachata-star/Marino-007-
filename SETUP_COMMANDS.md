# 🚀 Blog Engine Setup - Quick Commands

Copy and paste these commands in PowerShell/Terminal to complete setup.

## Step 1: Install Dependencies

```bash
pip install anthropic python-dotenv google-auth-oauthlib google-auth-httplib2 google-api-python-client requests
```

**Expected:** Clean install, no errors

---

## Step 2: Download Google Credentials

📖 **Follow this visual guide:**
- Read: `GET_GOOGLE_CREDENTIALS.md`
- Go to: https://console.cloud.google.com/
- Create project: "Los Iconos Blog"
- Enable APIs: Photos Library + Google Drive
- Download OAuth credentials as JSON
- Save as: `google_photos_credentials.json` and `google_drive_credentials.json`

**Files to create:**
```
C:\Users\Fellito Rodriguez\Projects\google_photos_credentials.json
C:\Users\Fellito Rodriguez\Projects\google_drive_credentials.json
```

---

## Step 3: Run Master Setup Wizard

```bash
python setup_blog_engine.py
```

This will guide you through:
- ✅ Google OAuth authentication (auto-opens browser)
- ✅ Gmail email setup (app password)
- ✅ Customer email list creation
- ✅ Test all connections

**Takes:** ~20 minutes (mostly waiting for you to enter info)

---

## OR: Manual Setup (if you prefer)

### Option A: Setup Google Credentials Only

```bash
python setup_google_credentials.py
```

### Option B: Setup Email Only

```bash
python setup_email_credentials.py
```

### Option C: Skip Setup Scripts (Manual Config)

1. Download credentials manually
2. Edit `.env` with your credentials
3. Create `customer_emails.txt` with email addresses

---

## Step 4: Verify Setup

### Check if files exist:

```bash
# PowerShell
ls google_photos_credentials.json, google_drive_credentials.json, customer_emails.txt
```

### Test connections:

```bash
# Test Google Photos
python -c "from google_photos_api import GooglePhotosClient; client = GooglePhotosClient(); print('✅ Google Photos OK')"

# Test Google Drive
python -c "from google_drive_api import GoogleDriveClient; client = GoogleDriveClient(); print('✅ Google Drive OK')"

# Test Email
python -c "from email_service import EmailService; service = EmailService(); print('✅ Email OK')"

# Test Claude AI
python -c "from blog_generator import BlogGenerator; gen = BlogGenerator(); print('✅ Claude OK')"
```

---

## Step 5: Generate Your First Blog Post

```bash
python blog_scheduler.py
```

**Expected output:**
```
============================================================
🎵 STARTING DAILY BLOG GENERATION
============================================================

1️⃣  Fetching next photo...
   ✅ Photo: [Your photo description]

2️⃣  Gathering related materials...
   ✅ Found X related documents

3️⃣  Researching topic...
   ✅ Found X web articles

4️⃣  Generating blog post with Claude...
   ✅ Blog generated (X tokens)

5️⃣  Creating title and metadata...
   ✅ Title: [Generated title]

6️⃣  Saving blog post...
   ✅ Saved: blogs/2026-08-02_topic.html

7️⃣  Sending promotional emails...
   ✅ Email sent to customer1@gmail.com
   ✅ Email sent to customer2@gmail.com
   ✅ Emails sent to X customers

8️⃣  Updating tracking...
   ✅ Tracking updated

============================================================
✅ DAILY BLOG COMPLETE!
============================================================
```

### Check the output:

```bash
# View generated blog (opens in browser)
start blogs\2026-08-02_*.html

# List all blogs generated
ls blogs\

# View tracking file
type blog_tracker.json
```

---

## Step 6: Schedule Daily Runs (Optional)

### Option A: Run in Background

```bash
# Windows: Run and keep running
start /B python blog_scheduler.py

# Or in a new PowerShell window:
powershell -NoExit "python blog_scheduler.py"
```

### Option B: Integrate with Marino 007

Edit `start_marino_007.py` and uncomment the blog scheduler service, then run:

```bash
python start_marino_007.py
```

---

## Troubleshooting Commands

### Reset if something breaks:

```bash
# Clear Google auth tokens (will re-authenticate next run)
del token.pickle

# Reset blog tracking (will reprocess all photos)
del blog_tracker.json

# Clear Python cache
rmdir /s __pycache__
```

### Check .env file:

```bash
# View email configuration
findstr EMAIL .env

# View Google configuration
findstr GOOGLE .env
```

### Test specific component:

```bash
# Test just photo fetching
python -c "from google_photos_api import GooglePhotosClient; c = GooglePhotosClient(); print(c.get_all_photos(limit=1))"

# Test just email
python -c "from email_service import EmailService; s = EmailService(); print('Emails:', s.load_customer_emails())"

# Test just web search
python -c "from web_search_api import WebSearchClient; c = WebSearchClient(); r = c.search_topic('test'); print(f'Found {len(r)} results')"
```

---

## Complete Workflow Summary

```
1. pip install dependencies
   ↓
2. Download Google credentials JSON files
   ↓
3. python setup_blog_engine.py  (or manual setup)
   ↓
4. Verify: python -c "from blog_generator import BlogGenerator; print('✅')"
   ↓
5. python blog_scheduler.py  (test first run)
   ↓
6. Check blogs/ directory for generated HTML
   ↓
7. Uncomment in start_marino_007.py for daily runs
   ↓
8. python start_marino_007.py  (all services together)
```

---

## Command Cheat Sheet

```bash
# Setup
pip install anthropic python-dotenv google-auth-oauthlib google-auth-httplib2 google-api-python-client requests
python setup_blog_engine.py

# Test
python blog_scheduler.py
python -c "from blog_generator import BlogGenerator; print('✅')"

# Run in background
start /B python blog_scheduler.py

# View results
start blogs\
type blog_tracker.json
```

---

## .env Configuration Reference

```env
# Google APIs
GOOGLE_PHOTOS_CREDENTIALS=google_photos_credentials.json
GOOGLE_DRIVE_CREDENTIALS=google_drive_credentials.json

# Gmail
EMAIL_SENDER=losiconosdelabachata@gmail.com
EMAIL_PASSWORD=your_16_char_app_password
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587

# Blog Settings
BLOG_SCHEDULE_HOUR=9
BLOG_SCHEDULE_MINUTE=0
BLOG_OUTPUT_DIR=blogs

# Optional: Web Search (leave empty for free DuckDuckGo)
GOOGLE_SEARCH_API_KEY=
GOOGLE_SEARCH_ENGINE_ID=
```

---

## Support

- 📖 **Full docs:** `BLOG_README.md`
- 📖 **Setup guide:** `BLOG_SETUP_GUIDE.md`
- 📖 **Quick start:** `BLOG_QUICK_START.md`
- 📖 **Google creds:** `GET_GOOGLE_CREDENTIALS.md`

**Los Iconos de la Bachata** 🎵

---

**Need help?** Check the documentation or see BLOG_SETUP_GUIDE.md troubleshooting section.
