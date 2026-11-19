"""The assistant loop: the model picks tools, we run them, repeat."""
import os

from .tools import TOOL_SPECS, run_tool

SYSTEM = (
    "You are a friendly personal assistant. Use your tools to remember things "
    "and get things done. Keep answers short. The order tool asks the user for "
    "approval itself, so never claim an order happened unless the tool says so."
)


class Agent:
    def __init__(self, client, memory, approve, model=None, max_steps=6):
        self.client = client
        self.memory = memory
        self.approve = approve
        self.model = model or os.environ.get("POCKET_MODEL", "claude-sonnet-5-5")
        self.max_steps = max_steps
        self.messages = []

    def chat(self, user_text):
        self.messages.append({"role": "user", "content": user_text})
        for _ in range(self.max_steps):
            resp = self.client.messages.create(
                model=self.model,
                max_tokens=1024,
                system=SYSTEM,
                tools=TOOL_SPECS,
                messages=self.messages,
            )
            self.messages.append({"role": "assistant", "content": resp.content})
            if resp.stop_reason != "tool_use":
                return "".join(b.text for b in resp.content if b.type == "text")
            results = []
            for block in resp.content:
                if block.type == "tool_use":
                    out = run_tool(block.name, block.input, self.memory, self.approve)
                    results.append(
                        {"type": "tool_result", "tool_use_id": block.id, "content": out}
                    )
            self.messages.append({"role": "user", "content": results})
        return "I stopped after too many steps. Try asking again."
