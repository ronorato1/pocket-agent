"""Chat from the terminal: python -m pocket"""
import os

from .agent import Agent
from .memory import Memory
from .tools import run_tool


def ask_approval(summary):
    return input(f"Approve this order? {summary} [y/N] ").strip().lower() == "y"


def main():
    memory = Memory()
    agent = None
    if os.environ.get("ANTHROPIC_API_KEY"):
        import anthropic

        agent = Agent(anthropic.Anthropic(), memory, ask_approval)
    else:
        print("No ANTHROPIC_API_KEY set. Chat is off, offline commands still work.")
    print("pocket-agent. Commands: /notes /reminders /usuals /quit")
    while True:
        try:
            line = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if line == "/quit":
            break
        offline = {"/notes": "list_notes", "/reminders": "list_reminders", "/usuals": "list_usuals"}
        if line in offline:
            print(run_tool(offline[line], {}, memory, ask_approval))
        elif line and agent:
            print(agent.chat(line))
        elif line:
            print("Set ANTHROPIC_API_KEY to chat.")


if __name__ == "__main__":
    main()
