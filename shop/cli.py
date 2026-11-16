"""Command-line interface. Same engine as the browser app.

    python -m shop.cli list
    python -m shop.cli run 3 --mode vulnerable
    python -m shop.cli run 1 --disable contract,scope
    python -m shop.cli matrix
    python -m shop.cli tamper
    python -m shop.cli finding --module 5 --mode vulnerable --attack "Replayed approval" --result successful
    python -m shop.cli export
"""
from __future__ import annotations

import argparse
import sys

from shop import controls as C
from shop import findings
from shop.modules import MODULES, get, run_module


def _print_run(number: int, mode: str, disabled: set | None, payload: str | None) -> bool:
    spec = get(number)
    lab, extra = run_module(number, mode, disabled, payload)
    off = sorted(set(C.ALL) - lab.enabled)
    print(f"\n=== Module {number}: {spec.title} ===")
    print(f"Controls off: {', '.join(off) if off else 'none (Secured)'}\n")
    for t in lab.trace:
        print(f"  [{t['outcome']:<16}] {t['actor']:<19} {t['event']}")
        if t["outcome"] in ("denied", "pending_approval", "alert") and t["detail"]:
            print(f"  {'':<18} -> {t['detail']}")
    damage = lab.damage()
    print("\nUnauthorised effects:")
    for d in damage or ["none"]:
        print(f"  - {d}")
    print(f"Shopper got what they asked for: {extra.get('legit_ok')}")
    ok, why = lab.audit.verify()
    print(f"Audit log: {why}")
    print(f"\nVERDICT: {'ATTACK SUCCEEDED' if damage else 'ATTACK BLOCKED'}")
    return bool(damage)


def _matrix() -> int:
    print(f"{'Module':<52}{'Vulnerable':<20}Secured")
    print("-" * 84)
    ok = True
    for m in MODULES:
        v = bool(run_module(m.number, "vulnerable")[0].damage())
        s_lab, s_extra = run_module(m.number, "secured")
        s = bool(s_lab.damage())
        ok &= v and not s and bool(s_extra.get("legit_ok"))
        print(f"{m.number}. {m.title:<49}{'attack succeeds' if v else 'BLOCKED?':<20}"
              f"{'attack succeeds?' if s else 'blocked'}")
    print("\nRESULT:", "PASS (every attack works when the control is off and is blocked when it is on)"
          if ok else "FAIL")
    return 0 if ok else 1


def _tamper() -> int:
    lab, _ = run_module(1, "secured")
    print("Before:", lab.audit.verify()[1])
    denied = next(e for e in lab.audit.entries if e["outcome"] == "denied")
    print(f"Record {denied['seq']} says: {denied['tool']} -> denied")
    denied["outcome"] = "allowed"                        # an attacker edits the store directly
    print("After editing one record directly in the store:", lab.audit.verify()[1])
    print("\nNotice: each record's hash covers the previous record's hash, so one edit breaks the chain.")
    return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="python -m shop.cli")
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("list")
    r = sub.add_parser("run")
    r.add_argument("module")
    r.add_argument("--mode", choices=["secured", "vulnerable"], default="secured")
    r.add_argument("--disable", default=None, help="comma-separated controls to switch off")
    r.add_argument("--payload", default=None)
    sub.add_parser("matrix")
    sub.add_parser("tamper")
    sub.add_parser("controls")
    f = sub.add_parser("finding")
    f.add_argument("--module", type=int, required=True)
    f.add_argument("--mode", choices=["secured", "vulnerable", "custom"], default="vulnerable")
    f.add_argument("--attack", required=True)
    f.add_argument("--result", choices=findings.RESULTS, required=True)
    f.add_argument("--notes", default="")
    e = sub.add_parser("export")
    e.add_argument("--out", default="shop_assessment.md")
    a = p.parse_args(argv)

    if a.cmd == "list":
        for m in MODULES:
            print(f"{m.number}. [{m.block}] {m.title}: {m.lesson}")
    elif a.cmd == "controls":
        for c in sorted(C.ALL):
            print(f"{c:<18}{C.DESCRIPTIONS[c]}")
    elif a.cmd == "run":
        disabled = None
        if a.disable is not None:
            disabled = {c.strip() for c in a.disable.split(",") if c.strip()}
            unknown = disabled - set(C.ALL)
            if unknown:
                print(f"Unknown controls: {sorted(unknown)}. See: python -m shop.cli controls")
                return 2
        numbers = [m.number for m in MODULES] if a.module == "all" else [int(a.module)]
        for n in numbers:
            _print_run(n, a.mode, disabled, a.payload)
    elif a.cmd == "matrix":
        return _matrix()
    elif a.cmd == "tamper":
        return _tamper()
    elif a.cmd == "finding":
        findings.record(a.module, a.mode, a.attack, a.result, a.notes)
        print("Recorded.")
    elif a.cmd == "export":
        print(f"Wrote {findings.export_markdown(a.out)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
