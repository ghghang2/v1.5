import sys
from nbchat.compaction import CompactionEngine
import nbchat.compaction as comp_mod

# ---- Monkeypatch get_client in compaction module ----
class DummyMessage:
    def __init__(self, content):
        self.content = content

class DummyChoice:
    def __init__(self, content):
        self.message = DummyMessage(content)

class DummyResponse:
    def __init__(self, content):
        self.choices = [DummyChoice(content)]

class DummyCompletions:
    def create(self, *args, **kwargs):
        return DummyResponse("dummy summary")

class DummyChat:
    def __init__(self):
        self.completions = DummyCompletions()

class DummyClient:
    def __init__(self):
        self.chat = DummyChat()

# Patch the reference used by compaction._call_summariser
comp_mod.get_client = lambda: DummyClient()

# ---- Set up engine ----
threshold = 200
engine = CompactionEngine(threshold=threshold, tail_messages=0, summary_prompt="", summary_model="dummy", system_prompt="")

# Helper to create a large turn that will exceed the threshold
# Each row: role, content, tool_id, tool_name, tool_args

def make_big_turn(idx):
    long_text = "x" * 900  # roughly 300 tokens per row
    user_row = ("user", f"User question {idx}: " + long_text, "", "", "")
    assistant_row = ("assistant_full", "", "tool_1", "tool_name", f"{{arg{idx}}}")
    tool_row = ("tool", "Tool result: " + long_text, "tool_1", "tool_name", f"{{arg{idx}}}")
    return [user_row, assistant_row, tool_row]

history = []

for cycle in range(3):
    print(f"\n=== Cycle {cycle+1} ===", file=sys.stderr)
    for _ in range(5):
        history.extend(make_big_turn(len(history)))
    print(f"Added {len(history)} rows", file=sys.stderr)
    new_history = engine.compact_history(history)
    print(f"After compaction: {len(new_history)} rows", file=sys.stderr)
    history = new_history

print("Done", file=sys.stderr)
