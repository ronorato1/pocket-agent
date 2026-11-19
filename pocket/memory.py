import json
from pathlib import Path


class Memory:
    """Everything the assistant remembers, stored in one JSON file."""

    def __init__(self, path="memory.json"):
        self.path = Path(path)
        self.data = {"notes": [], "reminders": [], "usuals": {}, "spent": 0.0}
        if self.path.exists():
            self.data.update(json.loads(self.path.read_text()))

    def save(self):
        self.path.write_text(json.dumps(self.data, indent=2))
