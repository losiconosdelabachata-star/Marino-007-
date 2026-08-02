"""
Order Automation Engine
Runs every hour to:
1. Check Shopify for new orders
2. Send to Printify for fulfillment
3. Send WhatsApp alerts to Marino Santos
"""

import schedule
import time
import json
from datetime import datetime
from pathlib import Path

import shopify_api
import printify_api
import whatsapp_client

# Store processed orders to avoid duplicates
ORDERS_DB = Path(__file__).parent / "processed_orders.json"

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

def check_and_fulfill_orders():
    """Main automation function - runs every hour"""
    print(f"\n{'='*60}")
    print(f"⏰ Order Check: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}")

    try:
        # Get orders that need fulfillment
        orders = shopify_api.get_orders_needing_fulfillment()

        if not orders:
            print("✓ No new orders to process")
            return

        print(f"📦 Found {len(orders)} orders to process\n")

        processed = load_processed_orders()
        new_orders = []

        # Process each order
        for order in orders:
            order_num = str(order["order_number"])

            # Skip if already processed
            if order_num in processed:
                print(f"  ✓ Order #{order_num} already processed")
                continue

            print(f"  📨 Processing Order #{order_num}...")

            # Send to Printify
            printify_result = printify_api.send_order_to_printify(
                shop_id="your_shop_id",  # User needs to set this
                shopify_order=order
            )

            if printify_result.get("success"):
                print(f"    ✓ Sent to Printify (ID: {printify_result.get('printify_order_id')})")
                new_orders.append(order_num)

                # Mark as processed
                processed[order_num] = {
                    "timestamp": datetime.now().isoformat(),
                    "printify_id": printify_result.get("printify_order_id"),
                    "customer": order["customer_email"],
                    "amount": order["total_price"]
                }

                # Send WhatsApp alert
                try:
                    message = f"""
🎉 NEW ORDER RECEIVED
Order #{order_num}
Customer: {order['customer_email']}
Total: ${order['total_price']}
Items: {len(order['line_items'])} product(s)

✓ Sent to Printify for fulfillment
Status: Processing
"""
                    whatsapp_client.send_to_marino(message.strip())
                    print(f"    ✓ WhatsApp alert sent to Marino")
                except Exception as e:
                    print(f"    ⚠️  WhatsApp alert failed: {e}")

            else:
                print(f"    ✗ Failed to send to Printify: {printify_result.get('error')}")

        # Save progress
        if new_orders:
            save_processed_orders(processed)
            print(f"\n✓ Successfully processed {len(new_orders)} new orders")
        else:
            print(f"\n✓ No new orders to process")

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
    start_automation()
