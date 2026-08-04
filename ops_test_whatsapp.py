#!/usr/bin/env python3
"""Send a test WhatsApp message, to prove alerts actually deliver.

"Connected" only means the socket is open. This confirms a message reaches
the phone, which is the thing that actually matters for order alerts.
"""

import sys
from datetime import datetime

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

try:
    import whatsapp_client
except Exception as e:
    print(f"Could not load the WhatsApp client: {e}")
    sys.exit(1)

status = whatsapp_client.check_status()
print(f"Bridge: {whatsapp_client.WHATSAPP_SERVER_URL}")

if not status.get("connected"):
    print("Not linked to WhatsApp.")
    if status.get("error"):
        print(f"  {status['error']}")
    print("")
    print("Scan the QR in the WhatsApp panel with the dedicated phone first.")
    sys.exit(1)

print("Linked. Sending test message...")

message = (
    "Marino 007 test message\n"
    f"Sent {datetime.now().strftime('%b %d, %Y at %I:%M %p')}\n\n"
    "If you can read this, order and blog alerts will reach you."
)

result = whatsapp_client.send_to_marino(message)

if result.get("success"):
    print(f"Delivered to {result.get('sent_to')}")
else:
    print(f"Send failed: {result.get('error', 'unknown error')}")
    sys.exit(1)
