#!/usr/bin/env python3
"""
Simple credential adder - paste your Google OAuth JSON here
"""

import os
import json

def add_google_credentials():
    print("""
╔════════════════════════════════════════════════════════════╗
║  ADD GOOGLE OAUTH CREDENTIALS                             ║
╚════════════════════════════════════════════════════════════╝

STEPS:
1. Go to: https://console.cloud.google.com/
2. Create project: "Los Iconos Blog"
3. Enable: Google Photos Library API + Google Drive API
4. Create OAuth 2.0 credentials (Desktop)
5. Download JSON file
6. Open the JSON file in a text editor
7. Copy the ENTIRE content
8. Paste here when prompted

Paste your Google OAuth JSON (and press Enter twice when done):
""")

    lines = []
    while True:
        try:
            line = input()
            if line:
                lines.append(line)
            else:
                # Check if we have JSON
                if lines and lines[0].startswith("{"):
                    break
        except EOFError:
            break

    json_str = "\n".join(lines)

    try:
        # Validate JSON
        creds = json.loads(json_str)
        print("\n✅ Valid JSON detected!")

        # Save to both files (can use same for both Photos and Drive)
        for filename in ["google_photos_credentials.json", "google_drive_credentials.json"]:
            with open(filename, "w") as f:
                json.dump(creds, f, indent=2)
            print(f"✅ Saved: {filename}")

        return True

    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def add_email_password():
    print("""
╔════════════════════════════════════════════════════════════╗
║  ADD GMAIL APP PASSWORD                                   ║
╚════════════════════════════════════════════════════════════╝

STEPS:
1. Go to: https://myaccount.google.com/
2. Click: Security (left sidebar)
3. Enable: 2-Factor Verification (if not already)
4. Then: App passwords
5. Choose: Mail + Windows Computer
6. Generate password (Google gives 16 chars)
7. Copy the password

Paste your 16-character app password:
""")

    password = input().strip().replace(" ", "")

    if len(password) != 16:
        print(f"❌ Password should be 16 characters (got {len(password)})")
        return False

    try:
        from dotenv import set_key
        set_key(".env", "EMAIL_PASSWORD", password)
        print(f"✅ Password saved to .env")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def add_customer_emails():
    print("""
╔════════════════════════════════════════════════════════════╗
║  ADD CUSTOMER EMAILS                                      ║
╚════════════════════════════════════════════════════════════╝

Add one email per line (press Enter twice when done):
""")

    lines = []
    while True:
        try:
            line = input().strip()
            if line:
                if "@" in line:
                    lines.append(line)
                else:
                    print("⚠️  Invalid email, try again")
            else:
                if lines:
                    break
        except EOFError:
            break

    if lines:
        try:
            with open("customer_emails.txt", "w") as f:
                for email in lines:
                    f.write(email + "\n")
            print(f"\n✅ Saved {len(lines)} customer emails")
            return True
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    else:
        print("❌ No emails entered")
        return False

if __name__ == "__main__":
    print("""
╔════════════════════════════════════════════════════════════╗
║                                                            ║
║   🎵 ADD BLOG ENGINE CREDENTIALS 🎵                       ║
║                                                            ║
╚════════════════════════════════════════════════════════════╝

What would you like to add?
1. Google OAuth credentials (Photos + Drive)
2. Gmail app password (for emails)
3. Customer emails
4. All of the above
0. Exit

Choice: """)

    choice = input().strip()

    if choice == "1":
        add_google_credentials()
    elif choice == "2":
        add_email_password()
    elif choice == "3":
        add_customer_emails()
    elif choice == "4":
        add_google_credentials()
        add_email_password()
        add_customer_emails()
    else:
        print("Exiting...")
