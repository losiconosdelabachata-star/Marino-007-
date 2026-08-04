"""
Shopify Admin API Client
Reads orders from your Los Iconos de la Bachata store
"""

import os
import requests
import json
from typing import List, Dict
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

SHOPIFY_STORE = os.getenv("SHOPIFY_STORE", "1cddeb-2.myshopify.com")

# SHOPIFY_API_KEY / SHOPIFY_API_PASSWORD are the OAuth *Client ID* and *Client
# Secret*. Neither can authenticate the Admin API - basic-auth with them was
# the reason every request failed. The Admin API needs an access token from
# the OAuth handshake, sent in the X-Shopify-Access-Token header.
SHOPIFY_ACCESS_TOKEN = os.getenv("SHOPIFY_ACCESS_TOKEN")
API_VERSION = "2025-01"

BASE_URL = f"https://{SHOPIFY_STORE}/admin/api/{API_VERSION}"
AUTH_HEADERS = {
    "X-Shopify-Access-Token": SHOPIFY_ACCESS_TOKEN or "",
    "Content-Type": "application/json",
}

class ShopifyError(RuntimeError):
    """Raised when Shopify cannot be reached or refuses the request.

    This is deliberately not swallowed. Returning [] on an API failure makes
    a broken connection look identical to "no orders today" - which would
    quietly stop fulfilment while every dashboard read said things were fine.
    """


def get_recent_orders(hours: int = 1) -> List[Dict]:
    """Get orders from the last N hours. Raises ShopifyError on failure."""
    url = f"{BASE_URL}/orders.json"
    params = {
        "status": "any",
        "limit": 50,
        "fields": "id,order_number,email,created_at,total_price,line_items,shipping_address,fulfillment_status"
    }

    try:
        response = requests.get(url, params=params, headers=AUTH_HEADERS, timeout=10)
    except requests.RequestException as e:
        raise ShopifyError(f"Could not reach Shopify: {e}") from e

    if response.status_code == 401:
        raise ShopifyError(
            "Shopify rejected the credentials (401). SHOPIFY_ACCESS_TOKEN is "
            "missing or stale - visit /api/shopify/install on the dashboard to "
            "run the OAuth handshake and mint a new one."
        )
    if response.status_code == 404:
        raise ShopifyError(
            f"Shopify returned 404 for store '{SHOPIFY_STORE}'. Check SHOPIFY_STORE "
            "is the myshopify domain from Settings > Domains."
        )
    if not response.ok:
        raise ShopifyError(f"Shopify returned HTTP {response.status_code}")

    try:
        orders = response.json().get("orders", [])
    except ValueError as e:
        raise ShopifyError(f"Shopify returned a non-JSON response: {e}") from e

    # Filter for unfulfilled orders only
    return [
        order for order in orders
        if order.get("fulfillment_status") is None
        or order.get("fulfillment_status") in ["pending", "partial"]
    ]

def get_order_details(order_id: str) -> Dict:
    """Get full details for a specific order"""
    try:
        url = f"{BASE_URL}/orders/{order_id}.json"
        response = requests.get(url, headers=AUTH_HEADERS, timeout=10)
        response.raise_for_status()
        return response.json().get("order", {})
    except Exception as e:
        print(f"Error fetching order details: {e}")
        return {}

def create_fulfillment(order_id: str, line_items: List[Dict]) -> Dict:
    """Create a fulfillment for an order"""
    try:
        url = f"{BASE_URL}/orders/{order_id}/fulfillments.json"

        payload = {
            "fulfillment": {
                "line_items_by_fulfillment_order": [
                    {
                        "fulfillment_order_id": item["fulfillment_order_id"],
                        "fulfillment_order_line_items": [
                            {
                                "id": line_item["id"],
                                "quantity": line_item["quantity"]
                            }
                            for line_item in item.get("line_items", [])
                        ]
                    }
                    for item in line_items
                ]
            }
        }

        response = requests.post(url, json=payload, headers=AUTH_HEADERS, timeout=10)
        response.raise_for_status()
        return response.json().get("fulfillment", {})
    except Exception as e:
        print(f"Error creating fulfillment: {e}")
        return {}

def get_orders_needing_fulfillment() -> List[Dict]:
    """Get all orders that haven't been fulfilled yet"""
    orders = get_recent_orders(hours=24)  # Check last 24 hours

    needing_fulfillment = []
    for order in orders:
        if order.get("fulfillment_status") in [None, "pending", "partial"]:
            needing_fulfillment.append({
                "order_id": order["id"],
                "order_number": order["order_number"],
                "customer_email": order["email"],
                "total_price": order["total_price"],
                "created_at": order["created_at"],
                "line_items": order["line_items"],
                "shipping_address": order.get("shipping_address", {})
            })

    return needing_fulfillment

# Test function
if __name__ == "__main__":
    print("Testing Shopify API connection...")
    orders = get_orders_needing_fulfillment()
    print(f"Found {len(orders)} orders needing fulfillment:")
    for order in orders:
        print(f"  - Order #{order['order_number']}: ${order['total_price']}")
