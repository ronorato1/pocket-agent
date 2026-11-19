import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace as NS

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from pocket.agent import Agent
from pocket.memory import Memory


class FakeClient:
    """Plays back scripted model replies so tests need no API key."""

    def __init__(self, replies):
        self.replies = list(replies)
        self.messages = NS(create=self._create)
        self.calls = []

    def _create(self, **kwargs):
        self.calls.append(kwargs)
        return self.replies.pop(0)


def text(t):
    return NS(stop_reason="end_turn", content=[NS(type="text", text=t)])


def tool(name, args, id="t1"):
    return NS(stop_reason="tool_use",
              content=[NS(type="tool_use", id=id, name=name, input=args)])


class AgentTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.mem = Memory(Path(self.tmp.name) / "memory.json")

    def tearDown(self):
        self.tmp.cleanup()

    def test_plain_reply(self):
        agent = Agent(FakeClient([text("Hi!")]), self.mem, lambda s: True)
        self.assertEqual(agent.chat("hello"), "Hi!")

    def test_tool_call_then_answer(self):
        client = FakeClient([tool("save_note", {"text": "dentist friday"}), text("Noted.")])
        agent = Agent(client, self.mem, lambda s: True)
        self.assertEqual(agent.chat("remind me about the dentist"), "Noted.")
        self.assertEqual(self.mem.data["notes"], ["dentist friday"])
        result = client.calls[1]["messages"][2]["content"][0]
        self.assertEqual(result["type"], "tool_result")
        self.assertEqual(result["tool_use_id"], "t1")

    def test_order_goes_through_approval(self):
        self.mem.data["usuals"]["lunch"] = {"place": "Sample Burger", "items": ["burger"], "price": 9.0}
        asked = []
        client = FakeClient([tool("order_usual", {"name": "lunch"}), text("Done.")])
        agent = Agent(client, self.mem, lambda s: asked.append(s) or False)
        agent.chat("get my usual")
        self.assertEqual(len(asked), 1)
        self.assertEqual(self.mem.data["spent"], 0.0)

    def test_stops_after_max_steps(self):
        replies = [tool("current_time", {}, id=f"t{i}") for i in range(10)]
        agent = Agent(FakeClient(replies), self.mem, lambda s: True, max_steps=3)
        self.assertIn("too many steps", agent.chat("loop"))


if __name__ == "__main__":
    unittest.main()
