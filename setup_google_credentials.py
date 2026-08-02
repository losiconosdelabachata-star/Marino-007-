#!/usr/bin/env python3
"""
Google OAuth Credentials Setup Helper
Guides you through setting up Google Photos and Drive OAuth 2.0 credentials
"""

import os
import json
import webbrowser
from pathlib import Path
from google_auth_oauthlib.flow import InstalledAppFlow

def setup_google_photos():
    """Set up Google Photos API credentials"""
    print("\n" + "="*60)
    print("📸 GOOGLE PHOTOS API SETUP")
    print("="*60)

    print("""
Follow these steps:
1. Go to: https://console.cloud.google.com/
2. Create new project: "Los Iconos Blog"
3. Enable "Google Photos Library API"
4. Create OAuth 2.0 credentials (Desktop application)
5. Download as JSON
6. Rename to: google_photos_credentials.json
7. Place in: """ + str(Path.cwd()))

    print("\n✓ When ready, press Enter to authenticate...")
    input()

    # Check if credentials file exists
    if not os.path.exists("google_photos_credentials.json"):
        print("❌ google_photos_credentials.json not found!")
        print("   Please download it from Google Cloud Console first")
        return False

    # Authenticate
    try:
        print("\n🔐 Authenticating with Google Photos...")
        SCOPES = ['https://www.googleapis.com/auth/photoslibrary.readonly']

        flow = InstalledAppFlow.from_client_secrets_file(
            'google_photos_credentials.json',
            SCOPES
        )

        creds = flow.run_local_server(port=0)

        print("✅ Google Photos authentication successful!")
        print(f"   Token saved to: token.pickle")
        return True

    except Exception as e:
        print(f"❌ Authentication failed: {e}")
        return False

def setup_google_drive():
    """Set up Google Drive API credentials"""
    print("\n" + "="*60)
    print("📄 GOOGLE DRIVE API SETUP")
    print("="*60)

    print("""
Follow these steps:
1. Go to: https://console.cloud.google.com/
2. In same project (Los Iconos Blog)
3. Enable "Google Drive API"
4. Use SAME OAuth credentials (or create new)
5. Download as JSON (if creating new)
6. Rename to: google_drive_credentials.json
7. Place in: """ + str(Path.cwd()))

    print("\n✓ When ready, press Enter to authenticate...")
    input()

    # Check if credentials file exists
    if not os.path.exists("google_drive_credentials.json"):
        print("❌ google_drive_credentials.json not found!")
        print("   Please download it from Google Cloud Console first")
        return False

    # Authenticate
    try:
        print("\n🔐 Authenticating with Google Drive...")
        SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

        flow = InstalledAppFlow.from_client_secrets_file(
            'google_drive_credentials.json',
            SCOPES
        )

        creds = flow.run_local_server(port=0)

        print("✅ Google Drive authentication successful!")
        print(f"   Token saved to: token.pickle")
        return True

    except Exception as e:
        print(f"❌ Authentication failed: {e}")
        return False

def verify_setup():
    """Verify all credentials are set up"""
    print("\n" + "="*60)
    print("✅ VERIFYING SETUP")
    print("="*60)

    checks = {
        "google_photos_credentials.json": os.path.exists("google_photos_credentials.json"),
        "google_drive_credentials.json": os.path.exists("google_drive_credentials.json"),
        ".env file": os.path.exists(".env"),
    }

    all_good = True
    for check, result in checks.items():
        status = "✅" if result else "❌"
        print(f"{status} {check}")
        if not result:
            all_good = False

    if all_good:
        print("\n✅ All credentials configured!")
        print("\nNext steps:")
        print("1. Create customer_emails.txt with email addresses")
        print("2. Run: python blog_scheduler.py")
    else:
        print("\n⚠️  Some files missing. Complete setup above first.")

    return all_good

if __name__ == "__main__":
    print("""
╔════════════════════════════════════════════════════════════╗
║                                                            ║
║           GOOGLE OAUTH CREDENTIALS SETUP                  ║
║                                                            ║
║      Los Iconos de la Bachata - Blog Engine              ║
║                                                            ║
╚════════════════════════════════════════════════════════════╝
""")

    try:
        # Setup Google Photos
        photos_ok = setup_google_photos()

        # Setup Google Drive
        drive_ok = setup_google_drive()

        # Verify
        if photos_ok and drive_ok:
            verify_setup()
            print("\n✅ Setup complete! Ready to generate blogs.")
        else:
            print("\n❌ Setup incomplete. Check errors above.")

    except KeyboardInterrupt:
        print("\n\n⏹️  Setup cancelled")
    except Exception as e:
        print(f"\n❌ Error: {e}")
