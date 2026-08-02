#!/usr/bin/env python3
"""
Google Ads OAuth Refresh Token Generator
Run this after adding Client ID and Client Secret to .env
"""

import os
from google.auth.oauthlib.flow import InstalledAppFlow
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

CLIENT_ID = os.getenv("GOOGLE_ADS_CLIENT_ID")
CLIENT_SECRET = os.getenv("GOOGLE_ADS_CLIENT_SECRET")

if not CLIENT_ID or not CLIENT_SECRET:
    print("❌ Error: CLIENT_ID or CLIENT_SECRET not found in .env")
    print("Make sure both are set before running this script")
    exit(1)

print("🔐 Google Ads OAuth Refresh Token Generator")
print("=" * 50)
print(f"Client ID: {CLIENT_ID[:20]}...")
print()

try:
    # Create OAuth flow
    flow = InstalledAppFlow.from_client_config(
        {
            "installed": {
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": ["http://localhost"]
            }
        },
        scopes=['https://www.googleapis.com/auth/adwords']
    )

    print("📱 Opening browser for authentication...")
    print("Please approve access in your browser window")
    print()

    creds = flow.run_local_server(port=0)

    if creds.refresh_token:
        print("✅ SUCCESS! Refresh Token Generated:")
        print("=" * 50)
        print(f"Refresh Token: {creds.refresh_token}")
        print("=" * 50)
        print()
        print("📝 Add this to your .env file:")
        print(f"GOOGLE_ADS_REFRESH_TOKEN={creds.refresh_token}")
        print()
        print("✨ Your Marino 007 Google Ads integration is ready!")
    else:
        print("❌ Error: No refresh token generated")
        exit(1)

except Exception as e:
    print(f"❌ Error: {e}")
    exit(1)
