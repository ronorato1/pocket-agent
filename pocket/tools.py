"""Tools the assistant can call. Anything that spends money asks first."""
from datetime import datetime

WEEKLY_CAP = 40.00  # dollars
ORDER_CAP = 20.00   # dollars per order

TOOL_SPECS = [
    {
        "name": "save_note",
        "description": "Save a short note for the user to read later.",
        "input_schema": {
            "type": "object",
            "properties": {"text": {"type": "string"}},
            "required": ["text"],
        },
    },
    {
        "name": "list_notes",
        "description": "List all saved notes.",
        "input_schema": {"type": "object", "properties": {}},
    },
    {
        "name": "add_reminder",
        "description": "Save a reminder with a free-text time, like 'tomorrow 8am'.",
        "input_schema": {
            "type": "object",
            "properties": {"text": {"type": "string"}, "when": {"type": "string"}},
            "required": ["text", "when"],
        },
    },
    {
        "name": "list_reminders",
        "description": "List all saved reminders.",
        "input_schema": {"type": "object", "properties": {}},
    },
    {
        "name": "current_time",
        "description": "Get the current local date and time.",
        "input_schema": {"type": "object", "properties": {}},
    },
    {
        "name": "save_usual",
        "description": "Remember a usual order the user likes.",
        "input_schema": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "place": {"type": "string"},
                "items": {"type": "array", "items": {"type": "string"}},
                "price": {"type": "number"},
            },
            "required": ["name", "place", "items", "price"],
        },
    },
    {
        "name": "list_usuals",
        "description": "List the user's saved usual orders and spending so far this week.",
        "input_schema": {"type": "object", "properties": {}},
    },
    {
        "name": "order_usual",
        "description": "Draft one of the user's usual orders. The user is asked to approve it. "
        "Nothing is actually ordered in this demo.",
        "input_schema": {
            "type": "object",
            "properties": {"name": {"type": "string"}},
            "required": ["name"],
        },
    },
]


def _order_usual(args, mem, approve):
    usual = mem.data["usuals"].get(args["name"])
    if not usual:
        known = ", ".join(mem.data["usuals"]) or "none"
        return f"No usual called '{args['name']}'. Known: {known}."
    price = usual["price"]
    if price > ORDER_CAP:
        return f"Blocked: ${price:.2f} is over the ${ORDER_CAP:.2f} per-order limit."
    if mem.data["spent"] + price > WEEKLY_CAP:
        return f"Blocked: that would pass the ${WEEKLY_CAP:.2f} weekly limit."
    summary = f"{', '.join(usual['items'])} from {usual['place']} (${price:.2f})"
    if not approve(summary):
        return "The user declined the order."
    mem.data["spent"] += price
    mem.save()
    return f"Approved: {summary}. (demo only, nothing was ordered)"


def run_tool(name, args, mem, approve):
    """Run one tool by name and return a text result for the model."""
    if name == "save_note":
        mem.data["notes"].append(args["text"])
        mem.save()
        return "Saved."
    if name == "list_notes":
        return "\n".join(mem.data["notes"]) or "No notes yet."
    if name == "add_reminder":
        mem.data["reminders"].append({"text": args["text"], "when": args["when"]})
        mem.save()
        return "Reminder saved."
    if name == "list_reminders":
        rows = [f"{r['when']}: {r['text']}" for r in mem.data["reminders"]]
        return "\n".join(rows) or "No reminders yet."
    if name == "current_time":
        return datetime.now().isoformat(timespec="minutes")
    if name == "save_usual":
        mem.data["usuals"][args["name"]] = {
            "place": args["place"],
            "items": args["items"],
            "price": float(args["price"]),
        }
        mem.save()
        return f"Saved usual '{args['name']}'."
    if name == "list_usuals":
        rows = [
            f"{n}: {', '.join(u['items'])} from {u['place']} (${u['price']:.2f})"
            for n, u in mem.data["usuals"].items()
        ]
        rows.append(f"Spent this week: ${mem.data['spent']:.2f} of ${WEEKLY_CAP:.2f}")
        return "\n".join(rows)
    if name == "order_usual":
        return _order_usual(args, mem, approve)
    return f"Unknown tool: {name}"
