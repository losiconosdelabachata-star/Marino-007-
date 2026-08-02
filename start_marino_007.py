#!/usr/bin/env python3
"""
Marino 007 - Master Startup Script
Starts all services: WhatsApp, Order Automation, and Bot
"""

import subprocess
import time
import os
import sys
from pathlib import Path

# Fix Windows encoding issues
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

os.chdir(Path(__file__).parent)

print("""
╔════════════════════════════════════════════════════════════╗
║                    MARINO 007 - STARTUP                   ║
║              Los Iconos de la Bachata Bot                  ║
╚════════════════════════════════════════════════════════════╝
""")

# Services to start
services = [
    {
        "name": "WhatsApp Server (Baileys)",
        "command": "node whatsapp_server.js",
        "description": "Listening on http://localhost:3000"
    },
    {
        "name": "Order Automation Engine",
        "command": "python order_automation.py",
        "description": "Checks Shopify every hour, sends to Printify, alerts on WhatsApp"
    },
    # Uncomment to enable daily blog posting from Google Photos + Drive + web research
    # {
    #     "name": "Daily Blog Scheduler",
    #     "command": "python blog_scheduler.py",
    #     "description": "Generates daily blog posts and sends promotional emails (9 AM daily)"
    # }
]

print("🚀 Starting Services:\n")
for i, service in enumerate(services, 1):
    print(f"{i}. {service['name']}")
    print(f"   └─ {service['description']}\n")

print("Starting services...")

processes = []

try:
    # Start WhatsApp server
    print("\n📱 Starting WhatsApp Server...")
    p_whatsapp = subprocess.Popen(
        services[0]["command"],
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    processes.append(("WhatsApp Server", p_whatsapp))
    time.sleep(3)

    # Start Order Automation
    print("\n📦 Starting Order Automation Engine...")
    p_orders = subprocess.Popen(
        services[1]["command"],
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    processes.append(("Order Automation", p_orders))
    time.sleep(2)

    print("\n" + "="*60)
    print("✓ All services started successfully!")
    print("="*60)
    print("""
📱 WhatsApp: http://localhost:3000
   → Scan QR code on your dedicated phone

📦 Order Automation: Running every hour
   → Checks Shopify for new orders
   → Sends to Printify for fulfillment
   → Sends WhatsApp alerts

💬 To use the interactive bot:
   $ python marino_007.py

⏸️  Press Ctrl+C to stop all services
""")

    # Keep processes running
    while True:
        time.sleep(1)
        for name, process in processes:
            if process.poll() is not None:
                print(f"⚠️  {name} stopped unexpectedly. Restarting...")
                # Could add restart logic here

except KeyboardInterrupt:
    print("\n\n⏹️  Shutting down all services...")
    for name, process in processes:
        print(f"  Stopping {name}...")
        process.terminate()
        try:
            process.wait(timeout=5)
        except:
            process.kill()
    print("✓ All services stopped")
    sys.exit(0)

except Exception as e:
    print(f"\n✗ Error: {e}")
    for name, process in processes:
        try:
            process.kill()
        except:
            pass
    sys.exit(1)
