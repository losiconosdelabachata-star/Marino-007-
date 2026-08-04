#!/usr/bin/env python3
"""Check Google Photos access. Run from the dashboard's Operations panel."""

import sys

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

try:
    from google_photos_api import GooglePhotosClient
except Exception as e:
    print(f"Could not load the Google Photos client: {e}")
    sys.exit(1)

try:
    client = GooglePhotosClient()
except Exception as e:
    print(f"Authentication failed: {e}")
    sys.exit(1)

albums = client.get_albums()
print(f"Albums: {len(albums)}")
for a in albums[:5]:
    print(f"  - {a['title']} ({a['media_items_count']} items)")

photos = client.get_all_photos(limit=5)
print(f"Photos returned: {len(photos)}")
for p in photos:
    print(f"  - {p['filename']}  {p['created_time']}")

if not photos:
    print("")
    print("No photos came back. The usual cause is the Google One billing")
    print("failure, which makes the API return 403 even though OAuth works.")
    sys.exit(1)

print("")
print("Google Photos is reachable.")
