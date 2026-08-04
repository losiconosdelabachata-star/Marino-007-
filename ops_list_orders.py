#!/usr/bin/env python3
"""List Shopify orders awaiting fulfilment. Read-only - changes nothing."""

import sys

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

try:
    import shopify_api
except Exception as e:
    print(f"Could not load the Shopify client: {e}")
    sys.exit(1)

try:
    orders = shopify_api.get_orders_needing_fulfillment()
except Exception as e:
    print(f"Shopify request failed: {e}")
    sys.exit(1)

if not orders:
    print("No unfulfilled orders.")
    sys.exit(0)

print(f"{len(orders)} order(s) awaiting fulfilment:")
print("")

total = 0.0
for o in orders:
    try:
        total += float(o.get("total_price") or 0)
    except (TypeError, ValueError):
        pass
    items = len(o.get("line_items") or [])
    print(f"  #{o['order_number']:<8} ${o['total_price']:<10} {items} item(s)  {o.get('customer_email') or '-'}")

print("")
print(f"Total value: ${total:.2f}")
