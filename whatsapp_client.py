"""
WhatsApp Client for Marino 007
Communicates with the Baileys WhatsApp server via HTTP
"""

import requests
import json
from typing import Optional, Dict, List

WHATSAPP_SERVER_URL = "http://localhost:3000"

def send_message(phone: str, message: str) -> Dict:
    """Send a WhatsApp message via the Baileys server"""
    try:
        response = requests.post(
            f"{WHATSAPP_SERVER_URL}/send",
            json={"phone": phone, "message": message},
            timeout=10
        )
        return response.json()
    except Exception as e:
        return {"error": str(e), "success": False}

def get_messages() -> List[Dict]:
    """Get all received WhatsApp messages"""
    try:
        response = requests.get(
            f"{WHATSAPP_SERVER_URL}/messages",
            timeout=10
        )
        data = response.json()
        return data.get("messages", [])
    except Exception as e:
        return []

def check_status() -> Dict:
    """Check if WhatsApp server is connected"""
    try:
        response = requests.get(
            f"{WHATSAPP_SERVER_URL}/status",
            timeout=5
        )
        return response.json()
    except Exception as e:
        return {"connected": False, "error": str(e)}

def clear_messages() -> Dict:
    """Clear the message log"""
    try:
        response = requests.post(
            f"{WHATSAPP_SERVER_URL}/messages/clear",
            timeout=10
        )
        return response.json()
    except Exception as e:
        return {"error": str(e), "success": False}

def send_to_marino(message: str) -> Dict:
    """Send a message directly to Marino Santos"""
    marino_phone = "7868387137"
    return send_message(marino_phone, message)

# Example usage
if __name__ == "__main__":
    print("Testing WhatsApp Client...")
    status = check_status()
    print(f"Server Status: {status}")

    if status.get("connected"):
        result = send_to_marino("Hello Marino! Marino 007 is online.")
        print(f"Message sent: {result}")
    else:
        print("⚠️  WhatsApp server not connected. Start it first: node whatsapp_server.js")
