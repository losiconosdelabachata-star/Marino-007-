# 🎵 Los Iconos Blog Engine Setup Guide

Complete guide to set up the daily blog posting system with Google Photos, Google Drive, web research, and promotional emails.

## Architecture Overview

The blog engine consists of 6 Python modules that work together:

1. **google_photos_api.py** - Retrieves photos chronologically from Google Photos
2. **google_drive_api.py** - Fetches related documents from Google Drive  
3. **web_search_api.py** - Researches topics using DuckDuckGo (free, no key needed)
4. **blog_generator.py** - Writes blog posts using Claude AI
5. **email_service.py** - Sends promotional email blasts to customers
6. **blog_scheduler.py** - Orchestrates everything daily

## Setup Steps

### Step 1: Google Photos API Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project: "Los Iconos Blog"
3. Enable the Google Photos Library API:
   - Search for "Photos Library API"
   - Click Enable
4. Create OAuth 2.0 credentials:
   - Go to Credentials → Create Credentials → OAuth 2.0 Client ID
   - Choose "Desktop application"
   - Download as JSON
5. Save the JSON file as `google_photos_credentials.json` in your project directory
6. Update .env:
   ```
   GOOGLE_PHOTOS_CREDENTIALS=google_photos_credentials.json
   ```

**First-time usage:** When you first run google_photos_api.py, it will open a browser asking for permissions. Grant access to "Google Photos Library Access (read-only)". The auth token will be saved for future runs.

### Step 2: Google Drive API Setup

1. In the same Google Cloud project:
2. Enable the Google Drive API:
   - Search for "Google Drive API"
   - Click Enable
3. Use the same OAuth 2.0 credentials (or create new ones)
4. Save as `google_drive_credentials.json` in your project directory
5. Update .env:
   ```
   GOOGLE_DRIVE_CREDENTIALS=google_drive_credentials.json
   ```

### Step 3: Gmail Setup (for Email Blasts)

1. Enable 2-factor authentication on your Gmail account (required for app passwords)
2. Create an app-specific password:
   - Go to [myaccount.google.com/security](https://myaccount.google.com/security)
   - Select "App passwords"
   - Choose "Mail" and "Windows Computer"
   - Google will generate a 16-character password
3. Update .env:
   ```
   EMAIL_SENDER=losiconosdelabachata@gmail.com
   EMAIL_PASSWORD=xxxx xxxx xxxx xxxx
   ```

### Step 4: Customer Email List

Create a file `customer_emails.txt` in your project directory with customer emails (one per line):

```
customer1@example.com
customer2@example.com
customer3@example.com
```

You can populate this manually or export from Shopify:
- Shopify Admin → Customers → Export customers as CSV
- Extract the email column and save to customer_emails.txt

### Step 5: Web Search (Optional - Uses DuckDuckGo by Default)

**DuckDuckGo (No setup needed)** - The system uses DuckDuckGo by default (free, no API key required).

**Google Custom Search (Optional)** - For better results:
1. Go to [programmablesearchengine.google.com](https://programmablesearchengine.google.com/)
2. Create a custom search engine
3. Get your Search Engine ID
4. Go to [Google Cloud Console](https://console.cloud.google.com/) and enable Custom Search API
5. Create an API key
6. Update .env:
   ```
   GOOGLE_SEARCH_API_KEY=your_api_key_here
   GOOGLE_SEARCH_ENGINE_ID=your_engine_id_here
   ```

### Step 6: Dependencies

Install required Python packages:

```bash
pip install anthropic python-dotenv google-auth-oauthlib google-auth-httplib2 google-api-python-client requests
```

## Running the Blog Engine

### Test Single Blog Generation

```bash
python blog_scheduler.py
```

This will:
1. Fetch the oldest unprocessed photo from Google Photos
2. Gather related materials from Google Drive
3. Search the web for context
4. Generate a blog post with Claude
5. Send promotional emails to your customer list
6. Save the blog as HTML in the `blogs/` directory
7. Track which photos have been posted (prevents duplicates)

### Schedule Daily Runs

Edit `blog_scheduler.py`:

```python
if __name__ == "__main__":
    scheduler = BlogScheduler()
    
    # Comment out to run once per day instead
    # print("Generating one blog now...")
    # scheduler.generate_daily_blog()
    
    # Uncomment to run daily at 9 AM
    scheduler.schedule_daily_run()
```

Then run:

```bash
python blog_scheduler.py
```

The scheduler will run indefinitely, generating a blog post every day at 9 AM (configurable in .env via `BLOG_SCHEDULE_HOUR` and `BLOG_SCHEDULE_MINUTE`).

### Run in Background (Production)

On Windows, use a task scheduler or run in a separate terminal with nohup:

```bash
# Windows
start /B python blog_scheduler.py

# Or use Windows Task Scheduler
```

On Mac/Linux:

```bash
nohup python blog_scheduler.py &
```

## Configuration

Edit `.env` to customize:

```env
# Blog posting time (24-hour format)
BLOG_SCHEDULE_HOUR=9
BLOG_SCHEDULE_MINUTE=0

# Output directory for blog HTML files
BLOG_OUTPUT_DIR=blogs

# Posts per day (currently fixed at 1)
BLOG_POSTS_PER_DAY=1
```

## Output

### Blog Posts
- Saved as HTML in `blogs/YYYY-MM-DD_topic.html`
- Styled with gold accent color (#d4af37) for Los Iconos branding
- Ready to publish to your blog website
- Include featured product recommendations

### Blog Tracker
- `blog_tracker.json` tracks which photos have been blogged
- Prevents duplicate posts
- Records last run timestamp

### Email Blasts
- Sent to all customers in `customer_emails.txt`
- HTML formatted with brand styling
- Includes blog excerpt, link to full post, and featured products
- Promotional CTAs for Shopify store

## Troubleshooting

### "AuthenticationError: credentials.json not found"
- Make sure `google_photos_credentials.json` and `google_drive_credentials.json` exist in project root
- Re-authenticate if needed by deleting `token.pickle` files

### "No unprocessed photos found"
- Make sure photos are uploaded to your Google Photos account
- Check that Google Photos Library API has access permission
- Verify credentials have correct scopes (photoslibrary.readonly)

### "EmailService: SMTP login failed"
- Verify EMAIL_PASSWORD is correct (16-char app password, not your regular password)
- Enable 2-factor authentication on Gmail
- Check that "Less secure apps" is disabled (shouldn't be needed with app passwords)

### "Blog generation failed: Rate limit exceeded"
- Claude API rate limit reached
- Wait a few minutes and try again
- Consider adjusting BLOG_POSTS_PER_DAY or scheduling at different time

### Emails not sending
- Check EMAIL_SENDER matches your Gmail account
- Verify customer_emails.txt is formatted correctly (one email per line)
- Make sure SMTP credentials are in .env

## Integration with Marino 007

To run the blog scheduler alongside your WhatsApp bot:

1. Uncomment the blog scheduler start in `start_marino_007.py` (see example below)
2. Run: `python start_marino_007.py`
3. Both WhatsApp server, order automation, AND blog scheduler will run simultaneously

Example integration:

```python
# In start_marino_007.py
import subprocess
import time
from blog_scheduler import BlogScheduler

# Start WhatsApp server
whatsapp_server = subprocess.Popen([...])

# Start order automation
order_automation = subprocess.Popen([...])

# Start blog scheduler
scheduler = BlogScheduler()
blog_thread = threading.Thread(target=scheduler.schedule_daily_run, daemon=True)
blog_thread.start()

print("✅ All services running...")
```

## File Structure

```
project/
├── blog_scheduler.py          # Main orchestrator
├── google_photos_api.py       # Google Photos integration
├── google_drive_api.py        # Google Drive integration
├── web_search_api.py          # Web search (DuckDuckGo/Google)
├── blog_generator.py          # Claude blog generation
├── email_service.py           # SMTP email blasting
├── .env                       # Credentials & configuration
├── customer_emails.txt        # Customer email list
├── blog_tracker.json          # Tracking which photos blogged
├── blogs/                     # Output directory for HTML blogs
│   ├── 2026-08-02_topic1.html
│   ├── 2026-08-03_topic2.html
│   └── ...
└── BLOG_SETUP_GUIDE.md       # This file
```

## Daily Workflow

1. **9:00 AM** - Blog scheduler wakes up
2. Gets oldest unposted photo from Google Photos
3. Finds related Google Drive documents
4. Searches web for context
5. Claude generates 800-1200 word blog post
6. Blog saved to `blogs/` directory
7. Email with blog excerpt + product promotion sent to all customers
8. Photo marked as processed in blog_tracker.json
9. Scheduler waits until next day at 9:00 AM

## Next Steps

1. ✅ Set up Google Photos credentials
2. ✅ Set up Google Drive credentials  
3. ✅ Configure email credentials
4. ✅ Create customer_emails.txt
5. ✅ Run `python blog_scheduler.py` for first test
6. ✅ Review generated blog in `blogs/` directory
7. ✅ Review email preview in console output
8. ✅ Schedule daily runs in production
9. ✅ Monitor performance and adjust if needed

## Support

For issues, check:
- Console output for detailed error messages
- .env file has correct format and credentials
- Google Cloud APIs are enabled
- Gmail app password is correct (not regular password)
- Customer email list is not empty
- Google Photos account has photos

---

**Los Iconos de la Bachata** 🎵  
*Timeless Music, Timeless Stories*
