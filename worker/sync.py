import json
import re
from pathlib import Path

LAB = Path(r"F:\Lab")
ORG = LAB / "org"
STATE = LAB / "state"
TRANSPORT = LAB / "transport"

def parse_frontmatter(path):
    text = path.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---", text, re.S)
    if not m:
        return None
    fields = {}
    for line in m.group(1).splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            fields[k.strip()] = v.strip().strip('"')
    return fields

def build_outbound():
    cards = []
    cards_dir = ORG / "cards"
    if cards_dir.exists():
        for p in sorted(cards_dir.glob("*.md")):
            f = parse_frontmatter(p)
            if f:
                cards.append(f)
    agents = {}
    agents_dir = ORG / "agents"
    if agents_dir.exists():
        for p in sorted(agents_dir.glob("*.md")):
            f = parse_frontmatter(p)
            if f:
                agents[f.get("id", p.stem)] = {
                    "role": f.get("role", ""),
                    "status": f.get("status", ""),
                    "focus": f.get("focus", ""),
                }
    outbound = {"cards": cards, "inbox": {}, "agents": agents}
    (TRANSPORT / "outbound").mkdir(parents=True, exist_ok=True)
    with open(TRANSPORT / "outbound" / "state.json", "w", encoding="utf-8") as f:
        json.dump(outbound, f, indent=2)

def apply_inbound():
    inbound_file = TRANSPORT / "inbound" / "updates.json"
    if not inbound_file.exists():
        return
    with open(inbound_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    inbound_file.unlink()

if __name__ == "__main__":
    build_outbound()
    apply_inbound()
