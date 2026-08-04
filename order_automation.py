"""
Order Automation Engine
Runs every hour to:
1. Check Shopify for new orders
2. Send to Printify for fulfillment
3. Send WhatsApp alerts to Marino Santos
"""

import os
import schedule
import time
import json
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

import shopify_api
import printify_api
import whatsapp_client
import paths

# Store processed orders to avoid duplicates
ORDERS_DB = Path(paths.PROCESSED_ORDERS)

def load_processed_orders():
    """Load the list of orders we've already processed"""
    if ORDERS_DB.exists():
        try:
            with open(ORDERS_DB, 'r') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_processed_orders(orders):
    """Save the list of processed orders"""
    with open(ORDERS_DB, 'w') as f:
        json.dump(orders, f, indent=2)

# Printify's native Shopify integration already pulls orders from this store -
# confirmed by orders sitting in Printify with external_id=None, which is what
# the native sync produces (an API-created order carries the external_id we
# send). Pushing over the API as well would create a SECOND copy of every
# order: duplicate prints, duplicate shipping, duplicate charges.
#
# So this stays off unless someone deliberately turns it on, and the default
# job is to watch and alert.
PRINTIFY_AUTO_PUSH = os.getenv("PRINTIFY_AUTO_PUSH", "false").lower() == "true"
PRINTIFY_SHOP_ID = os.getenv("PRINTIFY_SHOP_ID")


def check_and_fulfill_orders():
    """Check Shopify for new orders and alert. Does not push to Printify
    unless PRINTIFY_AUTO_PUSH is explicitly enabled."""
    print(f"\n{'='*60}")
    print(f"⏰ Order Check: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}")

    if PRINTIFY_AUTO_PUSH:
        print("⚠️  PRINTIFY_AUTO_PUSH is ON - orders will be pushed over the API.")
        print("    Printify's native Shopify sync may already be delivering them,")
        print("    in which case this creates duplicates. Verify before relying on it.\n")

    try:
        orders = shopify_api.get_orders_needing_fulfillment()

        if not orders:
            print("✓ No unfulfilled orders")
            return

        print(f"📦 {len(orders)} unfulfilled order(s)\n")

        processed = load_processed_orders()
        newly_seen = []

        for order in orders:
            order_num = str(order["order_number"])

            if order_num in processed:
                print(f"  · Order #{order_num} already seen")
                continue

            print(f"  📨 New order #{order_num}")

            record = {
                "timestamp": datetime.now().isoformat(),
                "customer": order["customer_email"],
                "amount": order["total_price"],
                "pushed_to_printify": False,
            }

            if PRINTIFY_AUTO_PUSH:
                if not PRINTIFY_SHOP_ID:
                    print("    ✗ PRINTIFY_SHOP_ID not set - skipping push")
                else:
                    result = printify_api.send_order_to_printify(
                        shop_id=PRINTIFY_SHOP_ID,
                        shopify_order=order,
                    )
                    if result.get("success"):
                        print(f"    ✓ Pushed to Printify ({result.get('printify_order_id')})")
                        record["printify_id"] = result.get("printify_order_id")
                        record["pushed_to_printify"] = True
                    else:
                        print(f"    ✗ Printify push failed: {result.get('error')}")

            fulfilment_line = (
                "✓ Pushed to Printify" if record["pushed_to_printify"]
                else "Printify handles fulfilment via its Shopify sync"
            )
            try:
                message = (
                    "🎉 NEW ORDER\n"
                    f"Order #{order_num}\n"
                    f"Customer: {order['customer_email']}\n"
                    f"Total: ${order['total_price']}\n"
                    f"Items: {len(order['line_items'])} product(s)\n\n"
                    f"{fulfilment_line}"
                )
                whatsapp_client.send_to_marino(message)
                print("    ✓ WhatsApp alert sent")
            except Exception as e:
                print(f"    ⚠️  WhatsApp alert failed: {e}")

            processed[order_num] = record
            newly_seen.append(order_num)

        if newly_seen:
            save_processed_orders(processed)
            print(f"\n✓ {len(newly_seen)} new order(s) recorded")
        else:
            print("\n✓ Nothing new")

    except Exception as e:
        print(f"\n✗ Error in order automation: {e}")
        # Alert Marino of the error
        try:
            whatsapp_client.send_to_marino(f"⚠️ Error in order automation: {str(e)}")
        except:
            pass

def send_daily_report():
    """Send a daily summary to Marino"""
    print(f"\n{'='*60}")
    print(f"📊 DAILY REPORT: {datetime.now().strftime('%Y-%m-%d')}")
    print(f"{'='*60}")

    try:
        processed = load_processed_orders()

        # Count today's orders
        today = datetime.now().strftime('%Y-%m-%d')
        today_orders = [
            order for order_id, order in processed.items()
            if order.get("timestamp", "").startswith(today)
        ]

        report = f"""
📊 DAILY ORDER REPORT
Date: {today}

📦 Orders Processed: {len(today_orders)}
💰 Total Revenue: ${sum(float(o.get('amount', 0)) for o in today_orders)}

Recent Orders:
"""
        for order in today_orders[-5:]:  # Last 5 orders
            report += f"• Order #{order_id}: ${order['amount']}\n"

        print(report)
        whatsapp_client.send_to_marino(report.strip())

    except Exception as e:
        print(f"Error generating report: {e}")

def start_automation():
    """Start the hourly automation scheduler"""
    print("\n🚀 Starting Order Automation Engine")
    print("📋 Schedule: Every hour at :00")
    print("✉️ WhatsApp alerts: Enabled")
    print("🎯 Printify integration: Enabled\n")

    # Schedule tasks
    schedule.every().hour.at(":00").do(check_and_fulfill_orders)
    schedule.every().day.at("18:00").do(send_daily_report)

    # Run immediately on startup
    check_and_fulfill_orders()

    # Keep scheduler running
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Shopify to Printify order automation")
    parser.add_argument(
        "--once",
        action="store_true",
        help="Run a single sweep and exit, instead of scheduling forever. "
             "The dashboard's 'Sweep orders' button uses this.",
    )
    args = parser.parse_args()

    if args.once:
        check_and_fulfill_orders()
    else:
        start_automation()
