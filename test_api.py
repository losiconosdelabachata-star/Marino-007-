import os
from dotenv import load_dotenv

load_dotenv()

if not os.getenv("ANTHROPIC_API_KEY"):
    raise SystemExit("ANTHROPIC_API_KEY missing. Add it to .env before running.")

from anthropic import Anthropic

client = Anthropic()
print("Testing Marino 007 connection to Claude API...")
print("=" * 50)

response = client.messages.create(
    model="claude-opus-4-8",
    max_tokens=100,
    messages=[
        {"role": "user", "content": "Hello! What is your name and what brand do you represent?"}
    ],
    system="You are Marino 007, an AI agent for Los Iconos de la Bachata."
)

print(response.content[0].text)
print("=" * 50)
print("✓ Connection successful!")
