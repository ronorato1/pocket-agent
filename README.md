# pocket-agent

A small personal assistant that remembers things and uses tools. You chat
with it, and a language model decides when to save a note, set a reminder,
or draft one of your usual orders. Anything that spends money asks for your
approval first, and there are per-order and weekly limits.

This is a compact example of a tool-using agent loop. Ordering is a demo
and only prints, it does not connect to any real service.

## Run

    pip install -r requirements.txt
    export ANTHROPIC_API_KEY=your-key
    python -m pocket

Try: "save a note to buy milk", "remind me to call mom tomorrow at 8",
"remember my usual: lunch from Sample Burger, burger and fries, $11.50",
then "get my usual lunch".

Without a key, /notes /reminders /usuals still work.

## Tests

    python -m unittest discover -s tests

The tests use a scripted fake model, so they need no key or network.

## Layout

- pocket/agent.py: the loop (model picks tools, we run them)
- pocket/tools.py: the tools and spending limits
- pocket/memory.py: JSON file storage
