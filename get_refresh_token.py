#!/usr/bin/env python3
"""
Mint long-lived Google refresh tokens for the deployed Marino 007.

Run this ONCE on a machine with a browser. The server can't do it itself -
there's nobody there to click "Allow". It prints the values to paste into
Render's environment variables.

    python get_refresh_token.py
"""

import sys
from google_auth_oauthlib.flow import InstalledAppFlow

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

TARGETS = [
    (
        'PHOTOS',
        'google_photos_credentials.json',
        ['https://www.googleapis.com/auth/photoslibrary.readonly'],
        'GOOGLE_PHOTOS_REFRESH_TOKEN',
    ),
    (
        'DRIVE',
        'google_drive_credentials.json',
        ['https://www.googleapis.com/auth/drive.readonly'],
        'GOOGLE_DRIVE_REFRESH_TOKEN',
    ),
]


def main():
    print("\n" + "=" * 62)
    print("  GOOGLE REFRESH TOKENS FOR DEPLOYMENT")
    print("=" * 62)
    print("\nA browser will open twice - approve both.\n")

    results = {}
    client_id = client_secret = None

    for label, creds_file, scopes, env_name in TARGETS:
        print(f"\n--- {label} ---")
        try:
            flow = InstalledAppFlow.from_client_secrets_file(creds_file, scopes)
            # access_type=offline is what makes Google issue a refresh token;
            # prompt=consent forces a fresh one even if you've approved before.
            creds = flow.run_local_server(
                port=0, access_type='offline', prompt='consent'
            )
        except FileNotFoundError:
            print(f"  ✗ {creds_file} not found - skipping")
            continue
        except Exception as e:
            print(f"  ✗ Failed: {e}")
            continue

        if not creds.refresh_token:
            print("  ✗ Google returned no refresh token. Revoke this app at")
            print("    https://myaccount.google.com/permissions and retry.")
            continue

        results[env_name] = creds.refresh_token
        client_id = creds.client_id
        client_secret = creds.client_secret
        print("  ✓ Got refresh token")

    if not results:
        print("\nNothing obtained. Nothing to paste.\n")
        return

    print("\n" + "=" * 62)
    print("  PASTE THESE INTO RENDER  (Environment tab)")
    print("=" * 62 + "\n")
    print(f"GOOGLE_OAUTH_CLIENT_ID={client_id}")
    print(f"GOOGLE_OAUTH_CLIENT_SECRET={client_secret}")
    for name, token in results.items():
        print(f"{name}={token}")
    print("\nTreat these like passwords. They don't expire on their own -")
    print("revoke at https://myaccount.google.com/permissions if leaked.\n")


if __name__ == "__main__":
    main()
