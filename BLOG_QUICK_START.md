# 🚀 Blog Engine Quick Start

## What's New

You now have a complete **automated daily blog posting system** for Los Iconos de la Bachata that:

✅ **Pulls** photos from Google Photos (oldest first)  
✅ **Gathers** related materials from Google Drive  
✅ **Researches** topics via web search (free DuckDuckGo)  
✅ **Generates** 800-1200 word blog posts using Claude AI  
✅ **Saves** HTML blog files to `blogs/` directory  
✅ **Emails** promotional blasts to your customer list  
✅ **Tracks** which photos have been blogged (no duplicates)  

## Files Created

| File | Purpose |
|------|---------|
| `blog_scheduler.py` | Main orchestrator - runs daily blog workflow |
| `google_photos_api.py` | Fetches photos from Google Photos API |
| `google_drive_api.py` | Retrieves documents from Google Drive |
| `web_search_api.py` | Searches the web (DuckDuckGo/Google) |
| `blog_generator.py` | Generates blog posts with Claude AI |
| `email_service.py` | Sends promotional email blasts via SMTP |
| `BLOG_SETUP_GUIDE.md` | Comprehensive setup instructions |
| `blog_tracker.json` | Tracks processed photos (auto-created) |
| `customer_emails.txt` | Customer email list (create manually) |
| `blogs/` | Output directory for HTML blog files |

## 5-Minute Setup

### 1. Install Dependencies
```bash
pip install anthropic python-dotenv google-auth-oauthlib google-auth-httplib2 google-api-python-client requests
```

### 2. Set Google Credentials
- Download `google_photos_credentials.json` from [Google Cloud Console](https://console.cloud.google.com/)
- Download `google_drive_credentials.json` (or same file can work for both)
- Save in your project directory

### 3. Set Email Credentials
Update `.env`:
```env
EMAIL_SENDER=losiconosdelabachata@gmail.com
EMAIL_PASSWORD=your_16_char_app_password
```

### 4. Add Customer Emails
Create `customer_emails.txt`:
```
customer1@gmail.com
customer2@gmail.com
customer3@gmail.com
```

### 5. Test It!
```bash
python blog_scheduler.py
```

## Daily Workflow

```
9:00 AM Daily Trigger
    ↓
📸 Fetch oldest unposted photo from Google Photos
    ↓
📄 Find related docs in Google Drive (same date)
    ↓
🔍 Research topic via web search
    ↓
✍️  Claude generates 800-1200 word blog post
    ↓
💾 Save HTML to blogs/2026-08-02_topic.html
    ↓
📧 Send promotional email blast to all customers
    ↓
✅ Mark photo as processed in blog_tracker.json
```

## Integration with Marino 007

To run alongside your WhatsApp bot and order automation:

Edit `start_marino_007.py` and uncomment the blog scheduler:

```python
services = [
    { "name": "WhatsApp Server (Baileys)", ... },
    { "name": "Order Automation Engine", ... },
    { "name": "Daily Blog Scheduler", ... }  # ← Uncomment this
]
```

Then run:
```bash
python start_marino_007.py
```

Now WhatsApp + Orders + Blog posting all run together!

## Configuration

All settings in `.env`:

```env
# When to post blogs (24-hour format)
BLOG_SCHEDULE_HOUR=9
BLOG_SCHEDULE_MINUTE=0

# Number of posts per day
BLOG_POSTS_PER_DAY=1

# Output directory
BLOG_OUTPUT_DIR=blogs

# Email settings
EMAIL_SENDER=losiconosdelabachata@gmail.com
EMAIL_PASSWORD=your_app_password
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587

# Web search (optional - defaults to free DuckDuckGo)
GOOGLE_SEARCH_API_KEY=  # Leave empty for DuckDuckGo
GOOGLE_SEARCH_ENGINE_ID=  # Leave empty for DuckDuckGo
```

## Sample Output

### Blog Post
```html
<!DOCTYPE html>
<html>
<head>
    <title>Los Iconos de la Bachata: A Night to Remember</title>
</head>
<body>
    <h1 style="color: #d4af37;">Los Iconos de la Bachata: A Night to Remember</h1>
    <p>Since 1985, Los Iconos de la Bachata has been...</p>
    <!-- 800-1200 word blog post -->
</body>
</html>
```

### Email
```
To: customer1@gmail.com
Subject: 🎵 Timeless Moments: New Blog!
From: Los Iconos de la Bachata

📖 NEW BLOG POST
Title: Los Iconos de la Bachata: A Night to Remember
Read the full story at: https://blog.losiconosdelabachata.com/...

🎵 FEATURED PRODUCTS
- Latest Album ($29.99)
- Merchandise ($19.99)  
- Concert Tickets ($75.00)

© 2026 Los Iconos de la Bachata
```

## Testing

### Test Blog Generation (One Post)
```bash
python blog_scheduler.py
```
Output:
- One blog post generated
- Saved to `blogs/YYYY-MM-DD_topic.html`
- Email preview in console
- `blog_tracker.json` created with photo ID marked

### Run Daily (Background)
Edit `blog_scheduler.py`:
```python
if __name__ == "__main__":
    scheduler = BlogScheduler()
    scheduler.schedule_daily_run()  # Runs daily at 9 AM
```

### Next Blog (Skip to Tomorrow)
Edit `blog_tracker.json` to remove the last photo ID:
```json
{
  "processed_photos": [],
  "last_run": null
}
```

## Troubleshooting

| Problem | Solution |
|---------|----------|
| "credentials.json not found" | Download from Google Cloud Console, save in project root |
| "SMTP login failed" | Use 16-char app password (not regular Gmail password) |
| "No unprocessed photos found" | Upload photos to Google Photos, or clear `blog_tracker.json` |
| "Rate limit exceeded" | Wait 5 mins, or schedule at different time |
| "No customer emails" | Create `customer_emails.txt` with email addresses |

## Next Steps

1. Follow [BLOG_SETUP_GUIDE.md](BLOG_SETUP_GUIDE.md) for detailed setup
2. Run `python blog_scheduler.py` to test
3. Review generated blog in `blogs/` directory  
4. Check email preview in console
5. Uncomment in `start_marino_007.py` to enable daily runs
6. Customize email templates and blog styling as needed

---

**Questions?** See [BLOG_SETUP_GUIDE.md](BLOG_SETUP_GUIDE.md) for complete documentation.

**Los Iconos de la Bachata** 🎵  
*Timeless Music, Timeless Stories*
