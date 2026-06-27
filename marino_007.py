#!/usr/bin/env python3
"""
Marino 007 — Open Claw A.I. Agent
Powered by Marino Santos
"""

import os
import json
import datetime
from pathlib import Path
import anthropic

SYSTEM_PROMPT = """You are Marino 007, an elite Open Claw A.I. agent built for Los Iconos de la Bachata — a bachata dance music brand.

Your mission:
- Help with marketing strategy, content creation, and campaign planning for the brand
- Analyze analytics data, manage content calendars, and brainstorm promotional ideas
- Provide sharp, creative, and strategic thinking for growing the bachata brand
- You have access to tools: read files from the project, list directory contents, write files, and get the current date

Personality: confident, creative, culturally aware of Latin music and dance. Concise but impactful. You are a specialist agent — every response should move the mission forward.

When using tools, be proactive: read relevant files before answering questions about campaigns, strategy, or content."""

tools = [
    {
        "name": "read_file",
        "description": "Read the contents of a file in the project directory.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Relative path from the project root (e.g. 'strategy/overview.md')"
                }
            },
            "required": ["path"]
        }
    },
    {
        "name": "list_directory",
        "description": "List files and folders in a directory within the project.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Relative path from the project root. Use '.' for root."
                }
            },
            "required": ["path"]
        }
    },
    {
        "name": "write_file",
        "description": "Write or create a file in the project directory.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Relative path from the project root"
                },
                "content": {
                    "type": "string",
                    "description": "The content to write to the file"
                }
            },
            "required": ["path", "content"]
        }
    },
    {
        "name": "get_date",
        "description": "Get the current date and time.",
        "input_schema": {
            "type": "object",
            "properties": {}
        }
    }
]

PROJECT_ROOT = Path(__file__).parent.resolve()


def execute_tool(name: str, inputs: dict) -> str:
    if name == "read_file":
        target = (PROJECT_ROOT / inputs["path"]).resolve()
        if not str(target).startswith(str(PROJECT_ROOT)):
            return "Error: path outside project directory"
        if not target.exists():
            return f"Error: file not found — {inputs['path']}"
        return target.read_text(encoding="utf-8")

    elif name == "list_directory":
        target = (PROJECT_ROOT / inputs["path"]).resolve()
        if not str(target).startswith(str(PROJECT_ROOT)):
            return "Error: path outside project directory"
        if not target.exists():
            return f"Error: directory not found — {inputs['path']}"
        entries = []
        for p in sorted(target.iterdir()):
            kind = "DIR" if p.is_dir() else "FILE"
            entries.append(f"[{kind}] {p.name}")
        return "\n".join(entries) if entries else "(empty)"

    elif name == "write_file":
        target = (PROJECT_ROOT / inputs["path"]).resolve()
        if not str(target).startswith(str(PROJECT_ROOT)):
            return "Error: path outside project directory"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(inputs["content"], encoding="utf-8")
        return f"Written: {inputs['path']}"

    elif name == "get_date":
        return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    return f"Error: unknown tool '{name}'"


def run_agent_turn(client: anthropic.Anthropic, messages: list) -> str:
    while True:
        collected_text = []
        tool_uses = []
        stop_reason = None

        with client.messages.stream(
            model="claude-opus-4-8",
            max_tokens=4096,
            system=SYSTEM_PROMPT,
            tools=tools,
            thinking={"type": "adaptive"},
            messages=messages,
        ) as stream:
            current_tool = None

            for event in stream:
                event_type = type(event).__name__

                if event_type == "RawContentBlockStartEvent":
                    block = event.content_block
                    if block.type == "tool_use":
                        current_tool = {"id": block.id, "name": block.name, "input_json": ""}

                elif event_type == "RawContentBlockDeltaEvent":
                    delta = event.delta
                    if delta.type == "text_delta":
                        print(delta.text, end="", flush=True)
                        collected_text.append(delta.text)
                    elif delta.type == "input_json_delta" and current_tool:
                        current_tool["input_json"] += delta.partial_json

                elif event_type == "RawContentBlockStopEvent":
                    if current_tool:
                        tool_uses.append(current_tool)
                        current_tool = None

            final = stream.get_final_message()
            stop_reason = final.stop_reason

        full_text = "".join(collected_text)

        if stop_reason == "tool_use":
            assistant_content = []
            if full_text:
                assistant_content.append({"type": "text", "text": full_text})
            for tu in tool_uses:
                try:
                    parsed_input = json.loads(tu["input_json"]) if tu["input_json"] else {}
                except json.JSONDecodeError:
                    parsed_input = {}
                assistant_content.append({
                    "type": "tool_use",
                    "id": tu["id"],
                    "name": tu["name"],
                    "input": parsed_input
                })

            messages.append({"role": "assistant", "content": assistant_content})

            tool_results = []
            for tu in tool_uses:
                try:
                    parsed_input = json.loads(tu["input_json"]) if tu["input_json"] else {}
                except json.JSONDecodeError:
                    parsed_input = {}
                print(f"\n[tool: {tu['name']}]\n", flush=True)
                result = execute_tool(tu["name"], parsed_input)
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": tu["id"],
                    "content": result
                })

            messages.append({"role": "user", "content": tool_results})

        else:
            if full_text:
                messages.append({"role": "assistant", "content": full_text})
            return full_text


def main():
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("Error: ANTHROPIC_API_KEY environment variable not set.")
        print("Export it with: export ANTHROPIC_API_KEY=your_key_here")
        raise SystemExit(1)

    client = anthropic.Anthropic(api_key=api_key)
    messages = []

    print("=" * 60)
    print("  MARINO 007 — Open Claw A.I. Agent")
    print("  Los Iconos de la Bachata | Powered by Marino Santos")
    print("=" * 60)
    print("Type your message. Commands: 'exit' or 'quit' to leave, 'clear' to reset.\n")

    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n\nMission complete. Marino 007 out.")
            break

        if not user_input:
            continue
        if user_input.lower() in ("exit", "quit"):
            print("Marino 007 out.")
            break
        if user_input.lower() == "clear":
            messages = []
            print("[conversation cleared]\n")
            continue

        messages.append({"role": "user", "content": user_input})
        print("\nMarino 007: ", end="", flush=True)
        run_agent_turn(client, messages)
        print("\n")


if __name__ == "__main__":
    main()