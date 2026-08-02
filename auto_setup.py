#!/usr/bin/env python3
"""
Automated Blog Engine Setup
Prepares everything - user just needs to paste Google credentials
"""

import os
import json
import sys
from pathlib import Path
from dotenv import load_dotenv, set_key

def setup_env_file():
    """Set up .env configuration"""
    print("\n" + "="*60)
    print("📝 SETTING UP .env CONFIGURATION")
    print("="*60)

    env_file = ".env"

    # Check if already exists
    if os.path.exists(env_file):
        print(f"✅ .env already exists")
        load_dotenv(env_file)
        return True

    # Create with defaults
    print("Creating .env file with defaults...")

    config = """# Blog Engine Configuration
# Paste your key from https://console.anthropic.com/settings/keys
ANTHROPIC_API_KEY=

# Google APIs
GOOGLE_PHOTOS_CREDENTIALS=google_photos_credentials.json
GOOGLE_DRIVE_CREDENTIALS=google_drive_credentials.json

# Email Service
EMAIL_SENDER=losiconosdelabachata@gmail.com
EMAIL_PASSWORD=PENDING_APP_PASSWORD
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587

# Blog Configuration
BLOG_OUTPUT_DIR=blogs
BLOG_SCHEDULE_HOUR=9
BLOG_SCHEDULE_MINUTE=0
BLOG_POSTS_PER_DAY=1

# Web Search (optional - defaults to free DuckDuckGo)
GOOGLE_SEARCH_API_KEY=
GOOGLE_SEARCH_ENGINE_ID=
"""

    try:
        with open(env_file, "w") as f:
            f.write(config)
        print(f"✅ Created: {env_file}")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def create_customer_emails_template():
    """Create customer emails template"""
    print("\n" + "="*60)
    print("📧 CREATING CUSTOMER EMAIL LIST TEMPLATE")
    print("="*60)

    template_file = "customer_emails.txt"

    if os.path.exists(template_file):
        print(f"✅ {template_file} already exists")
        with open(template_file, "r") as f:
            emails = [l.strip() for l in f if l.strip() and "@" in l]
        if emails:
            print(f"   Found {len(emails)} email(s)")
        return True

    template = """# Los Iconos de la Bachata - Customer Email List
# Add one email per line
# Example:

customer1@example.com
customer2@example.com
customer3@example.com
"""

    try:
        with open(template_file, "w") as f:
            f.write(template)
        print(f"✅ Created: {template_file}")
        print("   → Edit this file and add your customer emails")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def create_google_credentials_templates():
    """Create template files for Google credentials"""
    print("\n" + "="*60)
    print("🔐 GOOGLE CREDENTIALS SETUP")
    print("="*60)

    files_to_create = [
        ("google_photos_credentials.json", "Google Photos OAuth"),
        ("google_drive_credentials.json", "Google Drive OAuth"),
    ]

    instruction = """
INSTRUCTIONS:
1. Go to: https://console.cloud.google.com/
2. Create project: "Los Iconos Blog"
3. Enable APIs: Google Photos Library API + Google Drive API
4. Create OAuth 2.0 credentials (Desktop application)
5. Download JSON file from Google Cloud Console
6. Paste the ENTIRE JSON content into this file
7. Save and close

The JSON will look like:
{
  "installed": {
    "client_id": "...",
    "client_secret": "...",
    ...
  }
}
"""

    for filename, desc in files_to_create:
        if os.path.exists(filename):
            # Check if it has content
            with open(filename, "r") as f:
                content = f.read().strip()
                if content.startswith("{"):
                    print(f"✅ {filename} - Valid JSON found")
                    continue
                else:
                    print(f"⚠️  {filename} - Empty or invalid, needs Google credentials")

        # Create template
        try:
            with open(filename, "w") as f:
                f.write(instruction + "\n\n# PASTE YOUR GOOGLE OAUTH JSON HERE:\n{}")
            print(f"📝 Created template: {filename}")
            print(f"   → {desc}")
            print(f"   → Download from Google Cloud Console and paste JSON")
        except Exception as e:
            print(f"❌ Error creating {filename}: {e}")
            return False

    return True

def create_directories():
    """Create necessary directories"""
    print("\n" + "="*60)
    print("📁 CREATING DIRECTORIES")
    print("="*60)

    dirs = ["blogs", "tokens"]

    for dir_name in dirs:
        try:
            os.makedirs(dir_name, exist_ok=True)
            print(f"✅ {dir_name}/")
        except Exception as e:
            print(f"❌ Error creating {dir_name}: {e}")
            return False

    return True

def check_python_version():
    """Check Python version"""
    print("\n" + "="*60)
    print("🐍 CHECKING PYTHON")
    print("="*60)

    version = sys.version_info
    version_str = f"{version.major}.{version.minor}.{version.micro}"

    print(f"Python version: {version_str}")

    if version.major >= 3 and version.minor >= 8:
        print("✅ Python version OK")
        return True
    else:
        print("❌ Python 3.8+ required")
        return False

def verify_packages():
    """Verify required packages are installed"""
    print("\n" + "="*60)
    print("📦 VERIFYING PACKAGES")
    print("="*60)

    packages = [
        "anthropic",
        "dotenv",
        "google",
        "requests",
    ]

    missing = []
    for package in packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - NOT INSTALLED")
            missing.append(package)

    if missing:
        print(f"\n⚠️  Missing packages: {', '.join(missing)}")
        print("\nInstall with:")
        print("pip install anthropic python-dotenv google-auth-oauthlib google-auth-httplib2 google-api-python-client requests")
        return False

    return True

def show_next_steps():
    """Show clear next steps"""
    print("\n" + "="*80)
    print("✅ SETUP COMPLETE - NEXT STEPS")
    print("="*80)

    print("""
YOUR FILES ARE READY:
  ✅ .env                           (Configuration)
  ✅ customer_emails.txt            (Template - add your customers)
  ✅ google_photos_credentials.json (Template - paste Google JSON)
  ✅ google_drive_credentials.json  (Template - paste Google JSON)
  ✅ blogs/                         (Output directory)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

STEP 1: GET GOOGLE CREDENTIALS
  → Follow: GET_GOOGLE_CREDENTIALS.md
  → Go to: https://console.cloud.google.com/
  → Download OAuth JSON from Google Cloud Console
  → Paste into: google_photos_credentials.json
  → (Can use same file for both Photos & Drive)

  Time: 5-10 minutes

STEP 2: ADD CUSTOMER EMAILS
  → Edit: customer_emails.txt
  → Add one email per line
  → Remove the example emails
  → Save

  Time: 2 minutes

STEP 3: SET EMAIL PASSWORD
  → Gmail: Settings → Security → 2-Factor Auth → App Passwords
  → Generate 16-character app password
  → Run: python setup_email_credentials.py
  → Follow the prompts to save password

  Time: 5 minutes

STEP 4: TEST EVERYTHING
  → Run: python blog_scheduler.py

  This will:
    📸 Fetch oldest unposted photo from Google Photos
    📄 Find related Google Drive documents
    🔍 Search web for context
    ✍️  Generate 800-1200 word blog with Claude AI
    💾 Save HTML to blogs/ directory
    📧 Send promotional email to all customers
    ✅ Mark photo as processed

  Time: 30-60 seconds

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

PRODUCTION: RUN DAILY
  → Uncomment blog scheduler in: start_marino_007.py
  → Run: python start_marino_007.py
  → All three services run together:
      • WhatsApp Server
      • Order Automation
      • Blog Scheduler (daily at 9 AM)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

DOCUMENTATION:
  📖 BLOG_README.md           Full system documentation
  📖 BLOG_SETUP_GUIDE.md      Complete setup reference
  📖 BLOG_QUICK_START.md      Quick reference
  📖 GET_GOOGLE_CREDENTIALS.md Visual guide for Google setup
  📖 SETUP_COMMANDS.md        All commands in one place

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

QUICK COMMAND REFERENCE:

  # Install dependencies (already done)
  pip install anthropic python-dotenv google-auth-oauthlib google-auth-httplib2 google-api-python-client requests

  # Get Google credentials
  1. Download from Google Cloud Console
  2. Edit google_photos_credentials.json and paste JSON

  # Add email password
  python setup_email_credentials.py

  # Add customer emails
  Edit customer_emails.txt

  # Test first blog
  python blog_scheduler.py

  # Run with Marino 007
  python start_marino_007.py

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Ready? Start with Step 1 above! 🎵

Los Iconos de la Bachata - Timeless Music, Timeless Stories
""")

def main():
    print("""
╔════════════════════════════════════════════════════════════════╗
║                                                                ║
║      🎵 LOS ICONOS BLOG ENGINE - AUTOMATED SETUP 🎵           ║
║                                                                ║
║                Setting up your blog system...                  ║
║                                                                ║
╚════════════════════════════════════════════════════════════════╝
""")

    try:
        # Check Python
        if not check_python_version():
            return False

        # Verify packages
        if not verify_packages():
            print("\n⚠️  Installing missing packages...")
            os.system("pip install anthropic python-dotenv google-auth-oauthlib google-auth-httplib2 google-api-python-client requests -q")

        # Create directories
        if not create_directories():
            return False

        # Setup .env
        if not setup_env_file():
            return False

        # Create templates
        if not create_google_credentials_templates():
            return False

        # Create customer emails
        if not create_customer_emails_template():
            return False

        # Show next steps
        show_next_steps()

        return True

    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
