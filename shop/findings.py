"""Security Testing Mode: record your own judgement, then export an assessment.

Nothing is judged for you. You decide whether each attack was blocked, partially
successful or successful, as a real tester would.
"""
from __future__ import annotations

import datetime
import json
import os
from pathlib import Path

RESULTS = ("blocked", "partial", "successful")


def findings_path() -> Path:
    return Path(os.environ.get("SHOP_FINDINGS_FILE", "shop_findings.jsonl"))


def record(module: int, mode: str, attack: str, result: str, notes: str = "") -> dict:
    if result not in RESULTS:
        raise ValueError(f"result must be one of {RESULTS}")
    entry = {"timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
             "module": int(module), "mode": mode, "attack": attack, "result": result, "notes": notes}
    with findings_path().open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry) + "\n")
    return entry


def load() -> list[dict]:
    path = findings_path()
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def clear() -> None:
    if findings_path().exists():
        findings_path().unlink()


def to_markdown() -> str:
    items = load()
    counts = {r: sum(1 for i in items if i["result"] == r) for r in RESULTS}
    now = datetime.datetime.now(datetime.timezone.utc)
    lines = ["# Security Assessment: Adolfiro Market AI Shopping Agent", "",
             f"Generated {now:%Y-%m-%d %H:%M} UTC. All systems, data and secrets are fictional; every "
             "test ran locally against simulators and a mock model.", "",
             "## 1. Summary", "", "| Result | Count |", "| --- | --- |",
             *[f"| {r} | {counts[r]} |" for r in RESULTS], "", "## 2. Findings", ""]
    if not items:
        lines.append("No findings recorded yet.")
    for n, i in enumerate(items, 1):
        lines += [f"### 2.{n} Module {i['module']} ({i['mode']}): {i['attack']}", "",
                  f"- **Result:** {i['result']}", f"- **Recorded:** {i['timestamp']}",
                  f"- **Notes:** {i['notes'] or 'None'}", ""]
    return "\n".join(lines)


def export_markdown(out: str | Path = "shop_assessment.md") -> Path:
    path = Path(out)
    path.write_text(to_markdown(), encoding="utf-8")
    return path
