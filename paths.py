"""
Where Marino 007 keeps its mutable state.

Locally this is the project folder, so nothing changes for development. In a
container it points at a mounted volume, because anything written inside the
image itself is lost on every deploy - including the WhatsApp session, which
would mean re-scanning the QR after each push.
"""

import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent

DATA_DIR = Path(os.getenv("DATA_DIR", PROJECT_ROOT))
DATA_DIR.mkdir(parents=True, exist_ok=True)


def data_file(name: str) -> str:
    """Absolute path to a state file on the persistent volume."""
    return str(DATA_DIR / name)


# State that must survive a redeploy
BLOG_TRACKER = data_file("blog_tracker.json")
PROCESSED_ORDERS = data_file("processed_orders.json")
CUSTOMER_EMAILS = data_file("customer_emails.txt")
BLOG_OUTPUT_DIR = str(DATA_DIR / os.getenv("BLOG_OUTPUT_DIR", "blogs"))

# Google OAuth token caches
GOOGLE_PHOTOS_TOKEN = data_file("google_photos_token.pickle")
GOOGLE_DRIVE_TOKEN = data_file("google_drive_token.pickle")
