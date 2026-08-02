#!/usr/bin/env python3
"""
Gmail App Password Setup Helper
Sets up email credentials for promotional blasts
"""

import os
from dotenv import load_dotenv, set_key

def setup_email():
    """Interactive email setup"""
    print("""
╔════════════════════════════════════════════════════════════╗
║                                                            ║
║              GMAIL EMAIL SETUP                            ║
║                                                            ║
║     Configure email for promotional blasts               ║
║                                                            ║
╚════════════════════════════════════════════════════════════╝
""")

    print("""
STEP 1: ENABLE 2-FACTOR AUTHENTICATION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. Go to: https://myaccount.google.com/
2. Click "Security" (left sidebar)
3. Find "2-Step Verification"
4. Click "Enable"
5. Follow Google's verification process
   (You'll need your phone)

Press Enter when 2-factor is enabled...
""")
    input()

    print("""
STEP 2: CREATE APP PASSWORD
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. Go to: https://myaccount.google.com/apppasswords
2. At the top, select:
   - App: "Mail"
   - Device: "Windows Computer"
3. Click "Generate"
4. Google will show a 16-character password
5. Copy the password (ignore spaces)

Your 16-character app password: """)

    app_password = input().strip()

    if len(app_password.replace(" ", "")) != 16:
        print("❌ App password should be 16 characters (ignoring spaces)")
        return False

    app_password = app_password.replace(" ", "")

    print(f"\nPassword: {app_password}")

    # Email sender
    print("""
STEP 3: VERIFY EMAIL ADDRESS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
What email address should send the promotional emails?
(default: losiconosdelabachata@gmail.com)

Email address: """)

    email = input().strip() or "losiconosdelabachata@gmail.com"

    if "@gmail.com" not in email:
        print("⚠️  Warning: Email doesn't have @gmail.com domain")
        print("   You'll need to use an SMTP server that works with this domain")

    # Save to .env
    print("""
STEP 4: SAVING CREDENTIALS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Saving credentials to .env file...
""")

    try:
        env_file = ".env"

        # Load current .env
        load_dotenv(env_file)

        # Update credentials
        set_key(env_file, "EMAIL_SENDER", email)
        set_key(env_file, "EMAIL_PASSWORD", app_password)
        set_key(env_file, "SMTP_SERVER", "smtp.gmail.com")
        set_key(env_file, "SMTP_PORT", "587")

        print("✅ Credentials saved to .env:")
        print(f"   EMAIL_SENDER={email}")
        print(f"   EMAIL_PASSWORD={app_password}")
        print(f"   SMTP_SERVER=smtp.gmail.com")
        print(f"   SMTP_PORT=587")

        return True

    except Exception as e:
        print(f"❌ Error saving to .env: {e}")
        return False

def test_email():
    """Test email connection"""
    print("""
STEP 5: TEST EMAIL CONNECTION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Testing SMTP connection...
""")

    try:
        import smtplib

        load_dotenv()
        sender = os.getenv("EMAIL_SENDER")
        password = os.getenv("EMAIL_PASSWORD")
        server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        port = int(os.getenv("SMTP_PORT", "587"))

        print(f"Connecting to {server}:{port}...")

        with smtplib.SMTP(server, port) as smtp:
            smtp.starttls()
            smtp.login(sender, password)

        print("✅ Email connection successful!")
        print(f"   Sender: {sender}")
        print("   Ready to send promotional blasts")
        return True

    except Exception as e:
        print(f"❌ Connection failed: {e}")
        print("""
Troubleshooting:
- Verify 2-factor authentication is enabled
- Double-check app password (16 chars, no spaces)
- Make sure you copied the full password from Google
- Wait 5 minutes for Google to propagate changes
- Try again
""")
        return False

def create_customer_emails():
    """Create customer emails template"""
    print("""
STEP 6: CREATE CUSTOMER EMAIL LIST
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Creating customer_emails.txt template...
""")

    template = """# Los Iconos de la Bachata - Customer Email List
# Add one email per line

customer1@example.com
customer2@example.com
customer3@example.com
"""

    try:
        if not os.path.exists("customer_emails.txt"):
            with open("customer_emails.txt", "w") as f:
                f.write(template)
            print("✅ Created: customer_emails.txt")
            print("""
Next: Edit customer_emails.txt and add your customer emails
(one per line, remove the examples)
""")
        else:
            print("⚠️  customer_emails.txt already exists")
            print("   Edit it to add your customer emails")

        return True

    except Exception as e:
        print(f"❌ Error creating file: {e}")
        return False

if __name__ == "__main__":
    try:
        # Setup email
        email_ok = setup_email()

        if email_ok:
            # Test connection
            test_ok = test_email()

            if test_ok:
                # Create customer list
                create_customer_emails()

                print("""
╔════════════════════════════════════════════════════════════╗
║                   ✅ SETUP COMPLETE!                      ║
╚════════════════════════════════════════════════════════════╝

Next steps:
1. Edit customer_emails.txt with your customer list
2. Run: python blog_scheduler.py

Your promotional emails are ready to send! 🎵
""")

    except KeyboardInterrupt:
        print("\n\n⏹️  Setup cancelled")
    except Exception as e:
        print(f"\n❌ Error: {e}")
