"""
Printify API Client
Sends orders to Printify for print-on-demand fulfillment
"""

import requests
import json
from typing import Dict, List
from dotenv import load_dotenv
import os

load_dotenv()

PRINTIFY_API_KEY = os.getenv("PRINTIFY_API_KEY")  # User must set this in .env

if not PRINTIFY_API_KEY:
    print("⚠️  Warning: PRINTIFY_API_KEY not set in .env file")
    PRINTIFY_API_KEY = "demo_key"  # Placeholder

BASE_URL = "https://api.printify.com/v1"
HEADERS = {
    "Authorization": f"Bearer {PRINTIFY_API_KEY}",
    "Content-Type": "application/json"
}

def get_shops() -> List[Dict]:
    """Get all connected Printify shops.

    /shops.json returns a bare JSON array. The previous version called
    .get("data", []) on it, which raised and silently returned [] every time.
    """
    try:
        url = f"{BASE_URL}/shops.json"
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        body = response.json()
        return body if isinstance(body, list) else body.get("data", [])
    except Exception as e:
        print(f"Error fetching shops: {e}")
        return []


def get_orders(shop_id: str, limit: int = 10) -> List[Dict]:
    """Orders Printify already holds for a shop.

    Useful for confirming the native Shopify sync is delivering, before
    anyone considers pushing orders over the API as well.
    """
    try:
        url = f"{BASE_URL}/shops/{shop_id}/orders.json"
        response = requests.get(url, headers=HEADERS, timeout=15)
        response.raise_for_status()
        body = response.json()
        orders = body if isinstance(body, list) else body.get("data", [])
        return orders[:limit]
    except Exception as e:
        print(f"Error fetching Printify orders: {e}")
        return []

def create_order(shop_id: str, order_data: Dict) -> Dict:
    """Create a print order in Printify"""
    try:
        url = f"{BASE_URL}/shops/{shop_id}/orders.json"

        # address_to is required by Printify. It was assembled by the caller
        # and then dropped from this payload, so every submission would have
        # been rejected. webhook_url pointed at localhost, which Printify's
        # servers cannot reach, so it is gone too.
        payload = {
            "external_id": order_data["order_id"],
            "line_items": order_data["line_items"],
            "shipping_method": 1,  # 1 = standard
            "send_shipping_notification": True,
            "address_to": order_data["shipping_address"],
        }

        response = requests.post(url, json=payload, headers=HEADERS, timeout=10)
        response.raise_for_status()

        result = response.json()
        return {
            "success": True,
            "printify_order_id": result.get("id"),
            "status": result.get("status"),
            "data": result
        }
    except Exception as e:
        print(f"Error creating Printify order: {e}")
        return {"success": False, "error": str(e)}

def get_order_status(shop_id: str, printify_order_id: str) -> Dict:
    """Check the status of a Printify order"""
    try:
        url = f"{BASE_URL}/shops/{shop_id}/orders/{printify_order_id}.json"
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error fetching order status: {e}")
        return {}

def send_order_to_printify(shop_id: str, shopify_order: Dict) -> Dict:
    """Convert Shopify order to Printify order and send"""
    try:
        # Transform Shopify order format to Printify format
        line_items = []
        for item in shopify_order.get("line_items", []):
            line_items.append({
                "product_id": item.get("product_id"),
                "variant_id": item.get("variant_id"),
                "quantity": item.get("quantity")
            })

        order_data = {
            "order_id": str(shopify_order["order_number"]),
            "line_items": line_items,
            "shipping_address": {
                "first_name": shopify_order.get("shipping_address", {}).get("first_name", ""),
                "last_name": shopify_order.get("shipping_address", {}).get("last_name", ""),
                "email": shopify_order.get("email", ""),
                "phone": shopify_order.get("shipping_address", {}).get("phone", ""),
                "address1": shopify_order.get("shipping_address", {}).get("address1", ""),
                "address2": shopify_order.get("shipping_address", {}).get("address2", ""),
                "city": shopify_order.get("shipping_address", {}).get("city", ""),
                "state": shopify_order.get("shipping_address", {}).get("province", ""),
                "zip": shopify_order.get("shipping_address", {}).get("zip", ""),
                "country": shopify_order.get("shipping_address", {}).get("country", "")
            }
        }

        result = create_order(shop_id, order_data)
        return result

    except Exception as e:
        print(f"Error sending order to Printify: {e}")
        return {"success": False, "error": str(e)}

# Test function
if __name__ == "__main__":
    print("Testing Printify API connection...")
    shops = get_shops()
    if shops:
        print(f"Found {len(shops)} connected shops:")
        for shop in shops:
            print(f"  - {shop.get('title')} (ID: {shop.get('id')})")
    else:
        print("⚠️  No shops connected. Set PRINTIFY_API_KEY in .env file.")
