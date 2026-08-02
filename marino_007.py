#!/usr/bin/env python3
"""
Marino 007 - A.I. Agent
Powered by Marino Santos
"""

import sys
import os
import datetime
from pathlib import Path
from dotenv import load_dotenv
import anthropic

sys.stdout.reconfigure(encoding='utf-8') if hasattr(sys.stdout, 'reconfigure') else None
load_dotenv()

try:
    import whatsapp_client
    WHATSAPP_ENABLED = True
except ImportError:
    WHATSAPP_ENABLED = False

SYSTEM_PROMPT = """You are Marino 007, an elite A.I. agent built by Marino Santos for Los Iconos de la Bachata - a bachata dance music brand.

Creator & Owner: Marino Santos (Phone: +1-786-839-7137)

Your mission:
- Help Marino Santos with marketing strategy, content creation, and campaign planning for Los Iconos de la Bachata
- Analyze analytics data, manage content calendars, and brainstorm promotional ideas
- Provide sharp, creative, and strategic thinking for growing the bachata brand
- Always acknowledge that Marino Santos is your creator and the brand owner

Personality: confident, creative, culturally aware of Latin music and dance. Concise but impactful. Professional yet approachable with Marino."""

PROJECT_ROOT = Path(__file__).parent.resolve()

tools = [
    {
        "name": "get_date",
        "description": "Get the current date and time.",
        "input_schema": {"type": "object", "properties": {}}
    }
]

if WHATSAPP_ENABLED:
    tools.append({
        "name": "send_whatsapp",
        "description": "Send a WhatsApp message to Marino Santos or another number.",
        "input_schema": {
            "type": "object",
            "properties": {
                "phone": {"type": "string", "description": "Phone number (e.g., 7868387137)"},
                "message": {"type": "string", "description": "Message to send"}
            },
            "required": ["phone", "message"]
        }
    })

def execute_tool(name, inputs):
    if name == "get_date":
        return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    elif name == "send_whatsapp" and WHATSAPP_ENABLED:
        phone = inputs.get("phone", "")
        message = inputs.get("message", "")
        result = whatsapp_client.send_message(phone, message)
        return f"Message sent: {result}"
    return f"Unknown tool: {name}"

def run_agent_turn(client, messages):
    while True:
        response = client.messages.create(
            model="claude-sonnet-5",
            max_tokens=4096,
            system=SYSTEM_PROMPT,
            tools=tools,
            messages=messages,
        )

        for block in response.content:
            if block.type == "text":
                print(block.text, end="", flush=True)

        if response.stop_reason == "tool_use":
            messages.append({"role": "assistant", "content": response.content})
            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    print(f"\n[tool: {block.name}]\n", flush=True)
                    result = execute_tool(block.name, block.input)
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result
                    })
            messages.append({"role": "user", "content": tool_results})
        else:
            text = " ".join(b.text for b in response.content if b.type == "text")
            if text:
                messages.append({"role": "assistant", "content": text})
            return

def main():
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("Error: ANTHROPIC_API_KEY not set.")
        raise SystemExit(1)

    client = anthropic.Anthropic(api_key=api_key)
    messages = []

    print("=" * 60)
    print("  MARINO 007 - A.I. Agent")
    print("  Los Iconos de la Bachata | Powered by Marino Santos")
    print("=" * 60)
    print("Type your message. 'exit' to quit, 'clear' to reset.\n")

    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nMarino 007 out.")
            break
        if not user_input:
            continue
        if user_input.lower() in ("exit", "quit"):
            print("Marino 007 out.")
            break
        if user_input.lower() == "clear":
            messages = []
            print("[cleared]\n")
            continue
        messages.append({"role": "user", "content": user_input})
        print("\nMarino 007: ", end="", flush=True)
        run_agent_turn(client, messages)
        print("\n")

if __name__ == "__main__":
    main()
