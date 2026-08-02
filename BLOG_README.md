# Los Iconos de la Bachata - Daily Blog Engine

A complete automated system for generating daily blog posts from Google Photos, Google Drive materials, and web research, with promotional email blasts to your customer base.

## 🎯 Overview

This blog engine automates your content marketing workflow:

- **Daily posts**: One blog post generated automatically every day at 9 AM
- **Rich sources**: Pulls materials from Google Photos, Google Drive, and web searches
- **AI-powered**: Uses Claude AI to write engaging 800-1200 word blog posts
- **Email marketing**: Sends promotional blasts to your entire customer list with each post
- **Product integration**: Automatically includes featured product recommendations from your Shopify store
- **Brand consistent**: All content follows Los Iconos de la Bachata brand guidelines (gold #d4af37)

## 📚 Table of Contents

1. [Architecture](#architecture)
2. [Quick Start](#quick-start)
3. [Detailed Setup](#detailed-setup)
4. [Components](#components)
5. [Usage](#usage)
6. [Integration](#integration)
7. [Configuration](#configuration)
8. [Troubleshooting](#troubleshooting)

## 🏗️ Architecture

### System Components

```
blog_scheduler.py (Main Orchestrator)
    ├─ google_photos_api.py (Photos)
    ├─ google_drive_api.py (Documents)
    ├─ web_search_api.py (Research)
    ├─ blog_generator.py (Claude AI)
    └─ email_service.py (SMTP)
```

### Daily Workflow

```
START: 9:00 AM
    ↓
[1] Fetch oldest unprocessed photo from Google Photos
    ↓
[2] Find related Google Drive documents (same date)
    ↓
[3] Search web for context using DuckDuckGo
    ↓
[4] Generate blog post with Claude Sonnet-5 AI
    ↓
[5] Save HTML blog post to blogs/ directory
    ↓
[6] Create engaging email with blog excerpt
    ↓
[7] Send promotional email blast to customer list
    ↓
[8] Track photo in blog_tracker.json (prevents duplicates)
    ↓
[9] Sleep until 9:00 AM tomorrow
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Google account (for Photos and Drive APIs)
- Gmail account (for sending emails)
- Anthropic API key (Claude AI)

### Installation

```bash
# 1. Install dependencies
pip install anthropic python-dotenv google-auth-oauthlib \
  google-auth-httplib2 google-api-python-client requests

# 2. Download Google credentials
# See Detailed Setup section

# 3. Configure .env file
# Copy the template below and fill in your credentials

# 4. Create customer email list
echo "customer@example.com" > customer_emails.txt

# 5. Test it!
python blog_scheduler.py
```

## 🔧 Detailed Setup

### Step 1: Google Photos API

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project: "Los Iconos Blog"
3. Enable Google Photos Library API
4. Create OAuth 2.0 credentials (Desktop application)
5. Download JSON and save as `google_photos_credentials.json`
6. Update .env: `GOOGLE_PHOTOS_CREDENTIALS=google_photos_credentials.json`

**First run**: App will open browser for auth. Grant "Photos Library Access" permission. Token saves automatically for future runs.

### Step 2: Google Drive API

1. In same Google Cloud project
2. Enable Google Drive API
3. Use same OAuth credentials (or create new ones)
4. Save as `google_drive_credentials.json`
5. Update .env: `GOOGLE_DRIVE_CREDENTIALS=google_drive_credentials.json`

### Step 3: Gmail Setup

1. Enable 2-factor authentication on Gmail
2. Create app-specific password:
   - Go to [myaccount.google.com/security](https://myaccount.google.com/security)
   - App passwords → Mail → Windows Computer
   - Copy 16-character password
3. Update .env:
   ```
   EMAIL_SENDER=losiconosdelabachata@gmail.com
   EMAIL_PASSWORD=xxxx xxxx xxxx xxxx
   ```

### Step 4: Customer Email List

Create `customer_emails.txt` with one email per line:

```
customer1@gmail.com
customer2@gmail.com
customer3@gmail.com
```

Or export from Shopify:
- Admin → Customers → Export as CSV
- Extract email column → save to customer_emails.txt

### Step 5: Environment Configuration

Create/update `.env`:

```env
# Anthropic (already configured)
ANTHROPIC_API_KEY=sk-ant-...

# Google APIs
GOOGLE_PHOTOS_CREDENTIALS=google_photos_credentials.json
GOOGLE_DRIVE_CREDENTIALS=google_drive_credentials.json

# Email Service
EMAIL_SENDER=losiconosdelabachata@gmail.com
EMAIL_PASSWORD=your_app_password_here
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587

# Blog Configuration
BLOG_OUTPUT_DIR=blogs
BLOG_SCHEDULE_HOUR=9
BLOG_SCHEDULE_MINUTE=0
BLOG_POSTS_PER_DAY=1

# Web Search (Optional - defaults to free DuckDuckGo)
GOOGLE_SEARCH_API_KEY=
GOOGLE_SEARCH_ENGINE_ID=
```

## 🔌 Components

### 1. blog_scheduler.py
Main orchestrator that coordinates the workflow.

**Key Methods:**
- `generate_daily_blog()` - Generates one blog post
- `schedule_daily_run()` - Runs daily at configured time
- `load_tracking()` / `save_tracking()` - Prevents duplicate posts

**Usage:**
```python
from blog_scheduler import BlogScheduler

scheduler = BlogScheduler()

# Generate one blog now
scheduler.generate_daily_blog()

# Or schedule daily runs
scheduler.schedule_daily_run()
```

### 2. google_photos_api.py
Retrieves photos from Google Photos in chronological order.

**Methods:**
- `get_all_photos(limit=365)` - Get photos (oldest first)
- `get_albums()` - List photo albums
- `get_photos_from_album(album_id)` - Get album photos

**Returns:**
```python
{
    'id': 'photo_id',
    'filename': 'photo.jpg',
    'url': 'https://...',
    'created_time': '2026-08-02T10:30:00Z',
    'description': 'Photo description'
}
```

### 3. google_drive_api.py
Retrieves documents from Google Drive by date.

**Methods:**
- `list_all_documents()` - Get all docs (by creation date)
- `get_document_content(doc_id)` - Extract text from Google Docs
- `get_file_metadata(file_id)` - Get file details

**Returns:**
```python
{
    'id': 'doc_id',
    'name': 'Document Title',
    'createdTime': '2026-08-02T10:00:00Z',
    'webViewLink': 'https://...',
    'content': 'Full document text...'
}
```

### 4. web_search_api.py
Searches the web for related content.

**Methods:**
- `search_topic(topic)` - Search for a topic
- `search_member_news(member_name)` - Search member-specific news
- Uses DuckDuckGo (free, no key) or Google Custom Search (optional)

**Returns:**
```python
{
    'title': 'Article Title',
    'url': 'https://example.com',
    'snippet': 'Article summary...',
    'source': 'DuckDuckGo'
}
```

### 5. blog_generator.py
Generates blog content using Claude AI.

**Methods:**
- `generate_blog_post(topic, materials, research, images)` - Write blog
- `generate_blog_title(topic, materials)` - Create title
- `generate_email_subject(blog_title)` - Create email subject
- `save_blog_post(title, content, topic)` - Save HTML

**Output:**
- HTML file: `blogs/2026-08-02_topic.html` (800-1200 words)
- Styled with Los Iconos branding (#d4af37 gold)
- Ready to publish to your website

### 6. email_service.py
Sends promotional email blasts via SMTP.

**Methods:**
- `send_blast_email(emails, subject, title, content, url, products)` - Send emails
- `load_customer_emails(file)` - Read email list
- `add_customer_email(email)` - Add single email

**Email Features:**
- HTML template with brand styling
- Blog excerpt and link to full post
- Featured products with prices and links
- Unsubscribe/preferences footer

## 📖 Usage

### Generate One Blog Post

```bash
python blog_scheduler.py
```

Output:
```
============================================================
🎵 STARTING DAILY BLOG GENERATION
============================================================

1️⃣  Fetching next photo...
   ✅ Photo: Concert Performance (2025-06-15)

2️⃣  Gathering related materials...
   ✅ Found 2 related documents

3️⃣  Researching topic...
   ✅ Found 3 web articles

4️⃣  Generating blog post with Claude...
   ✅ Blog generated (1,250 tokens)

5️⃣  Creating title and metadata...
   ✅ Title: Los Iconos de la Bachata: The Concert That Moved Hearts

6️⃣  Saving blog post...
   ✅ Saved: blogs/2026-08-02_los_iconos_de_la_bachata_the_concert_that_moved_hearts.html

7️⃣  Sending promotional emails...
   ✅ Email sent to customer1@gmail.com
   ✅ Email sent to customer2@gmail.com
   ✅ Email sent to customer3@gmail.com
   ✅ Emails sent to 3 customers

8️⃣  Updating tracking...
   ✅ Tracking updated

============================================================
✅ DAILY BLOG COMPLETE!
============================================================
```

### Schedule Daily (Background)

Edit `blog_scheduler.py` (line ~231):

```python
if __name__ == "__main__":
    scheduler = BlogScheduler()
    # scheduler.generate_daily_blog()  # Comment out
    scheduler.schedule_daily_run()     # Uncomment
```

Run:
```bash
python blog_scheduler.py
```

Blog will generate daily at 9:00 AM (configurable via .env).

## 🔗 Integration

### Run with Marino 007

Edit `start_marino_007.py` and uncomment the blog scheduler:

```python
services = [
    { "name": "WhatsApp Server (Baileys)", ... },
    { "name": "Order Automation Engine", ... },
    {
        "name": "Daily Blog Scheduler",
        "command": "python blog_scheduler.py",
        "description": "Generates daily blog posts and promotional emails"
    }
]
```

Run:
```bash
python start_marino_007.py
```

Now WhatsApp, Orders, and Blog posting all run together!

### Manual Integration

```python
import threading
from blog_scheduler import BlogScheduler

# Start blog scheduler in background
scheduler = BlogScheduler()
blog_thread = threading.Thread(
    target=scheduler.schedule_daily_run,
    daemon=True
)
blog_thread.start()

print("Blog scheduler running in background")
```

## ⚙️ Configuration

### Schedule Time

Edit `.env`:
```env
BLOG_SCHEDULE_HOUR=9      # 24-hour format (0-23)
BLOG_SCHEDULE_MINUTE=0    # Minutes (0-59)
```

Examples:
- `BLOG_SCHEDULE_HOUR=9` → 9:00 AM
- `BLOG_SCHEDULE_HOUR=14` → 2:00 PM
- `BLOG_SCHEDULE_HOUR=20` → 8:00 PM

### Blog Settings

```env
BLOG_OUTPUT_DIR=blogs           # Where to save HTML files
BLOG_POSTS_PER_DAY=1            # Posts per day (currently fixed at 1)
```

### Email Branding

Edit `email_service.py` (line 31):

```python
# Change gold color to match your brand
"background-color: #d4af37;"  # ← Edit this color

# Change header text
<h1 style="color: white; margin: 0;">Your Brand Name</h1>
```

### Product Promotion

Edit `blog_scheduler.py` (line 166):

```python
products = [
    {'name': 'Latest Album', 'price': '29.99', 'url': 'https://...'},
    {'name': 'Merchandise', 'price': '19.99', 'url': 'https://...'},
    {'name': 'Concert Tickets', 'price': '75.00', 'url': 'https://...'},
]
```

Replace with your actual products from Shopify.

## 🆘 Troubleshooting

### Credentials Issues

**"AuthenticationError: credentials.json not found"**
- Download from Google Cloud Console
- Save as `google_photos_credentials.json` in project root
- Run `python google_photos_api.py` to test auth

**"Token has been revoked"**
- Delete `token.pickle` files
- Re-authenticate in browser on next run

### Email Issues

**"SMTP login failed"**
- Use 16-character app password (not regular Gmail password)
- Verify EMAIL_SENDER matches your Gmail
- Check 2-factor authentication is enabled
- Try again after 5 minutes

**"Connection timeout"**
- Check SMTP_SERVER and SMTP_PORT are correct
- Gmail uses `smtp.gmail.com:587`
- Use `starttls()` not SSL

### Photo Issues

**"No unprocessed photos found"**
- Upload photos to Google Photos
- Wait for sync (usually 10-30 mins)
- Or clear `blog_tracker.json` to reset

**"Photos not chronological"**
- Ensure photos have correct creation dates
- Oldest photos should appear first
- Check Google Photos sorting

### Generation Issues

**"Blog generation failed: Rate limit exceeded"**
- Claude API rate limit (wait 5 mins)
- Or schedule at different times
- Check your Anthropic account usage

**"No web search results found"**
- Topic might be too obscure
- Try DuckDuckGo fallback (automatic)
- Or add Google Custom Search API key

## 📊 Outputs

### Generated Blog Posts

Location: `blogs/YYYY-MM-DD_topic.html`

```html
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width">
    <title>Blog Post Title</title>
    <style>
        /* Los Iconos branding (#d4af37 gold) */
    </style>
</head>
<body>
    <h1>Blog Post Title</h1>
    <div class="blog-meta">Published on August 2, 2026 | Los Iconos de la Bachata</div>
    
    <!-- 800-1200 word HTML blog post -->
    
</body>
</html>
```

### Tracking File

Location: `blog_tracker.json`

```json
{
  "processed_photos": [
    "photo_id_1",
    "photo_id_2",
    "photo_id_3"
  ],
  "last_run": "2026-08-02T09:00:00.000000"
}
```

## 📋 File Structure

```
project/
├── blog_scheduler.py              # Main orchestrator
├── blog_generator.py              # Claude AI blog generation
├── blog_tracker.json              # Processed photos (auto-created)
├── customer_emails.txt            # Customer email list (create manually)
├── email_service.py               # SMTP email service
├── google_drive_api.py            # Google Drive integration
├── google_drive_credentials.json  # Google Drive OAuth (create yourself)
├── google_photos_api.py           # Google Photos integration
├── google_photos_credentials.json # Google Photos OAuth (create yourself)
├── web_search_api.py              # Web search (DuckDuckGo/Google)
├── .env                           # Configuration & credentials
├── BLOG_README.md                 # This file
├── BLOG_SETUP_GUIDE.md            # Detailed setup instructions
├── BLOG_QUICK_START.md            # Quick reference
├── start_marino_007.py            # Master startup script
└── blogs/                         # Output directory
    ├── 2026-08-02_topic1.html
    ├── 2026-08-03_topic2.html
    └── ...
```

## 🎯 Next Steps

1. ✅ Follow [BLOG_SETUP_GUIDE.md](BLOG_SETUP_GUIDE.md) for complete setup
2. ✅ Run `python blog_scheduler.py` to test
3. ✅ Review blog in `blogs/` directory
4. ✅ Review email preview
5. ✅ Customize styling and branding
6. ✅ Add to `start_marino_007.py` for daily runs
7. ✅ Monitor and optimize as needed

## 📞 Support

- **Setup issues?** See [BLOG_SETUP_GUIDE.md](BLOG_SETUP_GUIDE.md)
- **Quick reference?** See [BLOG_QUICK_START.md](BLOG_QUICK_START.md)
- **Error messages?** Check console output for details
- **API issues?** Verify credentials in `.env` file

## 📜 License

Part of the Marino 007 bot project.

---

**Los Iconos de la Bachata** 🎵  
*Timeless Music, Timeless Stories*

**Version:** 1.0  
**Last Updated:** 2026-08-02
