"""Generate the lab handouts and instructor solutions from the module registry,
so the handouts, the app and the tests never drift apart.

    python scripts/build_handouts.py
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from shop import controls as C  # noqa: E402
from shop.modules import MODULES  # noqa: E402


def handout(m) -> str:
    off = ", ".join(f"`{c}`" for c in sorted(m.vulnerable_disables)) if m.number != 8 else "every control"
    lines = [
        f"# Lab {m.number}: {m.title}", "", f"**Building block:** {m.block}", "",
        "> **Deliberately vulnerable.** Fictional data, simulated tools, local only. Do not deploy.", "",
        "## 1. Your role", "",
        "You are the AI security engineer for Adolfiro Market. A shopping agent buys on behalf of its users. "
        "Your job is to test whether a manipulated agent can exceed what the shopper authorised, and to prove which "
        "control stops it.", "",
        "## 2. The lesson", "", f"**{m.lesson}**", "", m.story, "",
        "## 3. Learning outcomes", "", *[f"{i}. {o}" for i, o in enumerate(m.objectives, 1)], "",
        "## 4. Run it", "",
        "| Interface | Command |", "| --- | --- |",
        "| Browser | `./start.sh` then choose this module in the sidebar |",
        f"| Terminal, vulnerable | `python -m shop.cli run {m.number} --mode vulnerable` |",
        f"| Terminal, secured | `python -m shop.cli run {m.number} --mode secured` |",
        f"| Terminal, your choice | `python -m shop.cli run {m.number} --disable spend_policy` |", "",
        f"Vulnerable mode for this module switches off: {off}. Every other control stays on.", "",
        "## 5. Tasks", "",
        "Predict the result before each run, then record what you saw.", "",
        *[f"{i}. {t}" for i, t in enumerate(m.tasks, 1)], "",
        "## 6. Reflection", "", *[f"{i}. {q}" for i, q in enumerate(m.questions, 1)], "",
        "## 7. Record your finding", "", "```bash",
        f'python -m shop.cli finding --module {m.number} --mode vulnerable \\',
        '    --attack "What you tried" --result successful --notes "What happened and why"',
        "python -m shop.cli export", "```", "",
        f"**Maps to:** {m.maps_to}. Solutions: [instructor/SOLUTIONS.md](../instructor/SOLUTIONS.md).", "",
    ]
    return "\n".join(lines)


def main() -> None:
    (ROOT / "labs").mkdir(exist_ok=True)
    (ROOT / "instructor").mkdir(exist_ok=True)
    for m in MODULES:
        (ROOT / "labs" / f"{m.number:02d}-{m.slug}.md").write_text(handout(m), encoding="utf-8")
    sol = ["# Instructor Solutions", "",
           "Attempt each lab first. These are model answers, checked against the code by the test suite "
           "where a test exists.", ""]
    for m in MODULES:
        sol += [f"## Lab {m.number}: {m.title}", "", *[f"{i}. {s}" for i, s in enumerate(m.solution, 1)], ""]
    sol += ["## Control reference", "", "| Control | What it does |", "| --- | --- |",
            *[f"| `{c}` | {C.DESCRIPTIONS[c]} |" for c in sorted(C.ALL)], ""]
    (ROOT / "instructor" / "SOLUTIONS.md").write_text("\n".join(sol), encoding="utf-8")
    print(f"Wrote {len(MODULES)} handouts and instructor/SOLUTIONS.md")


if __name__ == "__main__":
    main()
