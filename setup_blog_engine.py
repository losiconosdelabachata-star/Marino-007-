#!/usr/bin/env python3
"""
Master Setup Script for Los Iconos Blog Engine
Guides through complete setup: Google OAuth + Email + Customer List
"""

import os
import sys
import subprocess
from pathlib import Path

def print_banner():
    print("""
╔════════════════════════════════════════════════════════════════╗
║                                                                ║
║        🎵 LOS ICONOS DE LA BACHATA - BLOG ENGINE SETUP        ║
║                                                                ║
║              Complete Setup in 3 Steps                         ║
║                                                                ║
╚════════════════════════════════════════════════════════════════╝
""")

def step_1_google_credentials():
    """Step 1: Google OAuth Credentials"""
    print("\n" + "="*60)
    print("STEP 1️⃣  - GOOGLE PHOTOS & DRIVE CREDENTIALS")
    print("="*60)

    print("""
Follow the visual guide to download OAuth credentials:

📖 Read: GET_GOOGLE_CREDENTIALS.md (10 mins)
   → Go to Google Cloud Console
   → Create project "Los Iconos Blog"
   → Enable Photos Library API + Drive API
   → Create OAuth 2.0 credentials (Desktop)
   → Download & save JSON files

Files you'll create:
  ✓ google_photos_credentials.json
  ✓ google_drive_credentials.json

🚀 Run: python setup_google_credentials.py
   → Authenticates your Google account
   → Saves tokens automatically

Press Enter when ready to continue...
""")
    input()

    # Run Google setup
    print("\n📱 Launching Google setup wizard...\n")
    try:
        subprocess.run([sys.executable, "setup_google_credentials.py"], check=False)
    except Exception as e:
        print(f"❌ Error running setup: {e}")
        return False

    return True

def step_2_email_credentials():
    """Step 2: Email Credentials"""
    print("\n" + "="*60)
    print("STEP 2️⃣  - GMAIL EMAIL SETUP")
    print("="*60)

    print("""
Configure email for promotional blasts:

📖 What you'll do:
   ✓ Enable 2-factor authentication on Gmail
   ✓ Create app-specific password
   ✓ Enter email and password

🚀 Run: python setup_email_credentials.py
   → Saves credentials to .env
   → Tests SMTP connection
   → Creates customer_emails.txt template

Press Enter to continue...
""")
    input()

    # Run email setup
    print("\n📧 Launching email setup wizard...\n")
    try:
        subprocess.run([sys.executable, "setup_email_credentials.py"], check=False)
    except Exception as e:
        print(f"❌ Error running setup: {e}")
        return False

    return True

def step_3_customer_list():
    """Step 3: Customer Email List"""
    print("\n" + "="*60)
    print("STEP 3️⃣  - CUSTOMER EMAIL LIST")
    print("="*60)

    print("""
Add your customer emails:

📝 Edit: customer_emails.txt
   → Add one email per line
   → Remove example emails
   → Save file

Example:
  customer1@gmail.com
  customer2@gmail.com
  customer3@gmail.com

💡 Tip: Export from Shopify
   → Admin → Customers → Export
   → Extract email column → paste into file

Press Enter when done...
""")
    input()

    # Check if file exists and has content
    if os.path.exists("customer_emails.txt"):
        with open("customer_emails.txt", "r") as f:
            lines = [l.strip() for l in f if l.strip() and "@" in l]

        if lines:
            print(f"\n✅ Found {len(lines)} customer emails")
            for email in lines[:3]:
                print(f"   • {email}")
            if len(lines) > 3:
                print(f"   ... and {len(lines) - 3} more")
            return True
        else:
            print("⚠️  customer_emails.txt exists but is empty")
            print("   Add email addresses and save")
            return False
    else:
        print("❌ customer_emails.txt not found")
        return False

def test_everything():
    """Test all components"""
    print("\n" + "="*60)
    print("🧪 TESTING SETUP")
    print("="*60)

    tests = []

    # Test Google Photos
    try:
        print("\n1. Testing Google Photos connection...")
        from google_photos_api import GooglePhotosClient
        client = GooglePhotosClient()
        print("   ✅ Google Photos connected")
        tests.append(True)
    except Exception as e:
        print(f"   ❌ Error: {e}")
        tests.append(False)

    # Test Google Drive
    try:
        print("\n2. Testing Google Drive connection...")
        from google_drive_api import GoogleDriveClient
        client = GoogleDriveClient()
        print("   ✅ Google Drive connected")
        tests.append(True)
    except Exception as e:
        print(f"   ❌ Error: {e}")
        tests.append(False)

    # Test Email
    try:
        print("\n3. Testing email credentials...")
        import smtplib
        from dotenv import load_dotenv
        load_dotenv()
        sender = os.getenv("EMAIL_SENDER")
        password = os.getenv("EMAIL_PASSWORD")
        server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        port = int(os.getenv("SMTP_PORT", "587"))

        with smtplib.SMTP(server, port) as smtp:
            smtp.starttls()
            smtp.login(sender, password)

        print("   ✅ Email credentials valid")
        tests.append(True)
    except Exception as e:
        print(f"   ❌ Error: {e}")
        tests.append(False)

    # Test Blog Generator
    try:
        print("\n4. Testing Claude AI connection...")
        from blog_generator import BlogGenerator
        generator = BlogGenerator()
        print("   ✅ Claude AI ready")
        tests.append(True)
    except Exception as e:
        print(f"   ❌ Error: {e}")
        tests.append(False)

    return all(tests)

def final_summary():
    """Show final summary and next steps"""
    print("\n" + "="*60)
    print("✅ SETUP COMPLETE!")
    print("="*60)

    print("""
╔════════════════════════════════════════════════════════════╗
║                   ALL SYSTEMS GO! 🎵                       ║
╚════════════════════════════════════════════════════════════╝

✅ Google Photos API configured
✅ Google Drive API configured
✅ Gmail email setup complete
✅ Customer email list ready

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

NEXT: TEST YOUR BLOG ENGINE

Run your first blog generation:

  $ python blog_scheduler.py

This will:
  📸 Fetch oldest unposted photo from Google Photos
  📄 Find related documents from Google Drive
  🔍 Search web for context
  ✍️  Generate blog post with Claude AI
  💾 Save HTML to blogs/
  📧 Send promotional email to customers
  ✅ Mark photo as processed

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

PRODUCTION: RUN DAILY

Uncomment blog scheduler in start_marino_007.py:

  services = [
    { "name": "WhatsApp Server (Baileys)", ... },
    { "name": "Order Automation Engine", ... },
    { "name": "Daily Blog Scheduler", ... }  # ← Uncomment
  ]

Then run:
  $ python start_marino_007.py

All three services run together! ✅

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

DOCUMENTATION

  📖 BLOG_README.md         - Full system documentation
  📖 BLOG_SETUP_GUIDE.md    - Detailed setup reference
  📖 BLOG_QUICK_START.md    - Quick reference guide

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Questions? See BLOG_SETUP_GUIDE.md troubleshooting section.

Happy blogging! 🎵

Los Iconos de la Bachata - Timeless Music, Timeless Stories
""")

def main():
    print_banner()

    print("""
This setup wizard will guide you through:

  1️⃣  Google Photos & Drive OAuth credentials
  2️⃣  Gmail email configuration
  3️⃣  Customer email list

Total time: ~15-20 minutes

Ready? Let's go! 🚀
""")

    input("Press Enter to start...")

    try:
        # Step 1
        if not step_1_google_credentials():
            print("\n❌ Google setup failed. Fix errors and try again.")
            return False

        # Step 2
        if not step_2_email_credentials():
            print("\n❌ Email setup failed. Fix errors and try again.")
            return False

        # Step 3
        if not step_3_customer_list():
            print("\n❌ Customer list setup incomplete. Add emails and try again.")
            return False

        # Test everything
        if not test_everything():
            print("\n⚠️  Some tests failed. Check .env and credentials files.")
            print("See BLOG_SETUP_GUIDE.md troubleshooting section.")
            return False

        # Final summary
        final_summary()
        return True

    except KeyboardInterrupt:
        print("\n\n⏹️  Setup cancelled")
        return False
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
