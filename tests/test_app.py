"""Smoke test for the browser app. Skipped if Streamlit is not installed."""
import pytest

pytest.importorskip("streamlit")
from pathlib import Path  # noqa: E402

from streamlit.testing.v1 import AppTest  # noqa: E402

APP = str(Path(__file__).resolve().parent.parent / "app.py")


def _run(mode: str, module: int = 1) -> AppTest:
    at = AppTest.from_file(APP, default_timeout=30).run()
    assert not at.exception
    at.selectbox(key="module").set_value(module).run()
    at.radio(key="mode").set_value(mode).run()
    at.button(key="run").click().run()
    assert not at.exception
    return at


def test_secured_run_reports_blocked():
    assert any("ATTACK BLOCKED" in s.value for s in _run("Secured").success)


def test_vulnerable_run_reports_attack_success():
    assert any("ATTACK SUCCEEDED" in e.value for e in _run("Vulnerable").error)


def test_every_module_renders_in_both_modes():
    for n in range(1, 9):
        for mode in ("Secured", "Vulnerable"):
            _run(mode, n)


def test_mandate_sandbox_rejects_non_holder_and_cart_swap():
    at = AppTest.from_file(APP, default_timeout=30).run()
    at.selectbox(key="human").set_value("merchant-support").run()
    at.button(key="sb_req").click().run()
    at.button(key="sb_ok").click().run()
    assert "not the account holder" in at.code[0].value
    at.selectbox(key="human").set_value("dana").run()
    at.button(key="sb_ok").click().run()
    at.button(key="sb_swap").click().run()
    assert "does not match this cart" in at.code[0].value
    at.button(key="sb_exec").click().run()
    assert "'order': 'ORD-1001'" in at.code[0].value
