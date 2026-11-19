import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from pocket.memory import Memory
from pocket.tools import run_tool


class ToolTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.mem = Memory(Path(self.tmp.name) / "memory.json")

    def tearDown(self):
        self.tmp.cleanup()

    def run_it(self, name, args=None, approve=lambda s: True):
        return run_tool(name, args or {}, self.mem, approve)

    def usual(self, price=11.5):
        self.run_it("save_usual", {"name": "lunch", "place": "Sample Burger",
                                   "items": ["burger"], "price": price})

    def test_notes_are_saved_and_persist(self):
        self.run_it("save_note", {"text": "buy milk"})
        self.assertIn("buy milk", self.run_it("list_notes"))
        self.assertEqual(Memory(self.mem.path).data["notes"], ["buy milk"])

    def test_reminders(self):
        self.run_it("add_reminder", {"text": "call mom", "when": "tomorrow 8am"})
        self.assertIn("tomorrow 8am: call mom", self.run_it("list_reminders"))

    def test_approved_order_adds_to_weekly_spend(self):
        self.usual()
        self.assertIn("Approved", self.run_it("order_usual", {"name": "lunch"}))
        self.assertEqual(self.mem.data["spent"], 11.5)

    def test_declined_order_costs_nothing(self):
        self.usual()
        out = self.run_it("order_usual", {"name": "lunch"}, approve=lambda s: False)
        self.assertIn("declined", out)
        self.assertEqual(self.mem.data["spent"], 0.0)

    def test_per_order_limit_blocks_without_asking(self):
        self.usual(price=45)
        asked = []
        out = self.run_it("order_usual", {"name": "lunch"}, approve=lambda s: asked.append(s))
        self.assertIn("Blocked", out)
        self.assertEqual(asked, [])

    def test_weekly_limit_blocks(self):
        self.usual()
        self.mem.data["spent"] = 35.0
        self.assertIn("Blocked", self.run_it("order_usual", {"name": "lunch"}))

    def test_unknown_usual_and_unknown_tool(self):
        self.assertIn("No usual", self.run_it("order_usual", {"name": "nope"}))
        self.assertIn("Unknown tool", self.run_it("nothing"))


if __name__ == "__main__":
    unittest.main()
