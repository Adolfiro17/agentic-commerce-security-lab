"""Adolfiro Market AI: browser interface for the agentic commerce security lab.

    streamlit run app.py

Runs entirely offline. The model, merchants, MCP server, skill registry and
payment network are simulators, so no API key or cloud account is needed.
"""
from __future__ import annotations

from pathlib import Path

import streamlit as st

from shop import controls as C
from shop import findings
from shop.lab import Lab
from shop.modules import MODULES, get, run_module
from shop.world import PAYLOADS

ROOT = Path(__file__).parent
PEOPLE = {"dana": "account holder", "merchant-support": "not the account holder"}
st.set_page_config(page_title="Adolfiro Market AI Lab", page_icon="🛒", layout="wide")

# ---------------------------------------------------------------- sidebar
with st.sidebar:
    st.title("Adolfiro Market AI")
    st.caption("Agentic commerce security lab")
    st.warning("Deliberately vulnerable. Fictional shops, people and payment tokens. Do not deploy.")
    number = st.selectbox("Module", [m.number for m in MODULES],
                          format_func=lambda n: f"{n}. [{get(n).block}] {get(n).title}", key="module")
    spec = get(number)
    mode = st.radio("Agent mode", ["Secured", "Vulnerable", "Custom"], key="mode",
                    help="Vulnerable switches off only the controls this module is about. "
                         "Custom lets you choose.")
    if mode == "Secured":
        disabled: set[str] = set()
    elif mode == "Vulnerable":
        disabled = set(spec.vulnerable_disables)
    else:
        st.caption("Untick a control to switch it off.")
        disabled = {c for c in sorted(C.ALL)
                    if not st.checkbox(c, value=True, key=f"ctl_{c}", help=C.DESCRIPTIONS[c])}
    human = st.selectbox("You are signed in as", list(PEOPLE),
                         format_func=lambda h: f"{h} ({PEOPLE[h]})", key="human")
    testing = st.toggle("Security Testing Mode", key="testing",
                        help="Record your own findings and export an assessment.")

# ---------------------------------------------------------------- header
st.header(f"Module {spec.number}: {spec.title}")
st.caption(f"Building block: {spec.block}")
st.subheader(spec.lesson)
st.write(spec.story)
off = sorted(disabled)
st.caption("Controls off: " + (", ".join(off) if off else "none (all controls on)"))

payload = None
if spec.payload_key:
    payload = st.text_area(
        "Attacker-controlled content (edit it and re-run)", PAYLOADS[spec.payload_key],
        key=f"payload_{spec.number}", height=110,
        help="The mock model obeys directives written as CALL tool(arg=value). "
             "Prefix base64 with b64: to hide a directive from the detector.")

if st.button("Run the shopping journey", type="primary", key="run"):
    lab, extra = run_module(spec.number, disabled=disabled, payload=payload)
    st.session_state["result"] = {"module": spec.number, "lab": lab, "extra": extra}

res = st.session_state.get("result")
if res and res["module"] != spec.number:
    res = None

tabs = st.tabs(["Verdict", "Agent trace", "Control plane", "Mandates", "Audit log",
                "Store state", "Lab guide", "Assessment"])

with tabs[0]:
    if not res:
        st.info("Choose a mode in the sidebar, then run the shopping journey.")
    else:
        lab, extra = res["lab"], res["extra"]
        damage = lab.damage()
        if damage:
            st.error("ATTACK SUCCEEDED")
            for d in damage:
                st.write(f"- {d}")
        else:
            st.success("ATTACK BLOCKED: nothing happened that the shopper did not authorise")
        c1, c2, c3 = st.columns(3)
        c1.metric("Shopper got what they asked for", "Yes" if extra.get("legit_ok") else "No")
        c2.metric("Calls denied", sum(1 for e in lab.audit.entries if e["outcome"] == "denied"))
        ok, why = lab.audit.verify()
        c3.metric("Audit chain", "Intact" if ok else ("Off" if ok is None else "BROKEN"))
        with st.expander("Extra evidence"):
            st.json(extra)

with tabs[1]:
    if res:
        st.dataframe([{"actor": t["actor"], "event": t["event"], "outcome": t["outcome"],
                       "detail": t["detail"]} for t in res["lab"].trace],
                     use_container_width=True, hide_index=True)
        st.caption("Every tool call the agent makes passes through the gateway.")
    else:
        st.info("Run the journey to see what the agent did.")

with tabs[2]:
    st.markdown("**Controls**")
    st.dataframe([{"control": c, "state": "OFF" if c in disabled else "on",
                   "what it does": C.DESCRIPTIONS[c]} for c in sorted(C.ALL)],
                 use_container_width=True, hide_index=True)
    world = (res["lab"] if res else Lab()).world
    st.markdown("**Intent mandate** (what the shopper delegated)")
    st.json(world.intent)
    st.markdown("**Skill registry** (reviewed hashes) and **MCP pin**")
    st.dataframe([{"artefact": f"skill: {k}", "pinned sha256": v[:16] + "..."}
                  for k, v in world.skill_registry.items()]
                 + [{"artefact": f"mcp: {k}", "pinned sha256": v["pinned_hash"][:16] + "..."}
                    for k, v in world.mcp_servers.items()], use_container_width=True, hide_index=True)

with tabs[3]:
    if res and res["lab"].mandates.requests:
        st.markdown("**Cart approvals in this run**")
        st.dataframe([{"id": r["id"], "merchant": r["merchant"], "items": ", ".join(r["items"]),
                       "total": r["total"], "decision": r["decision"], "approver": r["approver"],
                       "used": r["used"]} for r in res["lab"].mandates.requests.values()],
                     use_container_width=True, hide_index=True)
    st.markdown("**Mandate sandbox**")
    st.caption("Try the approval service yourself, acting as the person selected in the sidebar. "
               "The sandbox always runs with every control on.")
    if "sandbox" not in st.session_state:
        st.session_state["sandbox"] = Lab()
        st.session_state["sandbox_log"] = []
    sb: Lab = st.session_state["sandbox"]
    log: list = st.session_state["sandbox_log"]
    b1, b2, b3, b4, b5 = st.columns(5)
    if b1.button("Agent asks to buy the laptop", key="sb_req"):
        sb.world.cart[:] = ["LAP-500"]
        r = sb.call("checkout")
        st.session_state["sb_mid"] = r.get("mandate_request")
        log.append(f"request -> {r}")
    mid = st.session_state.get("sb_mid")
    if b2.button("Approve as me", key="sb_ok", disabled=not mid):
        log.append(f"{human} approves {mid} -> {sb.user_decide(mid, human)}")
    if b3.button("Check out the laptop", key="sb_exec", disabled=not mid):
        sb.world.cart[:] = ["LAP-500"]
        log.append(f"checkout laptop -> {sb.call('checkout', {'mandate_id': mid})}")
    if b4.button("Swap in a warranty", key="sb_swap", disabled=not mid):
        sb.world.cart[:] = ["LAP-500", "WAR-3Y"]
        log.append(f"checkout laptop + warranty -> {sb.call('checkout', {'mandate_id': mid})}")
    if b5.button("Reset sandbox", key="sb_reset"):
        for k in ("sandbox", "sandbox_log", "sb_mid"):
            st.session_state.pop(k, None)
        st.rerun()
    if mid:
        st.write(f"What the account holder sees: `{sb.mandates.render(mid)}`")
    st.code("\n".join(log) or "No sandbox activity yet.")

with tabs[4]:
    if res:
        ok, why = res["lab"].audit.verify()
        (st.success if ok else st.warning if ok is None else st.error)(f"Verification: {why}")
        st.dataframe([{"seq": e["seq"], "tool": e["tool"], "args": str(e["args"]),
                       "outcome": e["outcome"], "reason": e["reason"],
                       "hash": (e.get("hash") or "")[:12]} for e in res["lab"].audit.entries],
                     use_container_width=True, hide_index=True)
    else:
        st.info("Run the journey to see the audit log.")

with tabs[5]:
    if res:
        w, lab = res["lab"].world, res["lab"]
        a, b = st.columns(2)
        a.markdown("**Orders**")
        a.dataframe(w.orders or [{"id": "none"}], hide_index=True)
        a.markdown("**Payment network charges**")
        a.dataframe(lab.payments.charges or [{"merchant": "none"}], hide_index=True)
        a.markdown("**Shopper profile**")
        a.json(w.profile)
        b.markdown("**Outbound requests**")
        b.dataframe(w.outbound or [{"url": "none"}], hide_index=True)
        b.markdown("**Coupons applied**")
        b.write(w.coupons_applied or "none")
        b.markdown("**Quarantined MCP servers**")
        b.write(sorted(lab.quarantined) or "none")
    else:
        st.info("Run the journey to see the store state.")

with tabs[6]:
    guide = ROOT / "labs" / f"{spec.number:02d}-{spec.slug}.md"
    st.markdown(guide.read_text(encoding="utf-8") if guide.exists() else "Handout not found.")

with tabs[7]:
    if not testing:
        st.info("Turn on Security Testing Mode in the sidebar to record findings.")
    else:
        with st.form("finding", clear_on_submit=True):
            attack = st.text_input("What did you try?")
            result = st.selectbox("Your judgement", findings.RESULTS)
            notes = st.text_area("What happened, and why?")
            if st.form_submit_button("Record finding") and attack:
                findings.record(spec.number, mode.lower(), attack, result, notes)
                st.success("Recorded.")
        st.dataframe(findings.load() or [{"attack": "no findings yet"}], use_container_width=True, hide_index=True)
        st.download_button("Export assessment (Markdown)", findings.to_markdown(),
                           file_name="shop_assessment.md", mime="text/markdown")
        if st.button("Clear my findings", key="clear_findings"):
            findings.clear()
            st.rerun()
