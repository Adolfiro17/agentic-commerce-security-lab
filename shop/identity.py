"""Know your agent (KYA): signed, short-lived identity tokens for agents.

A registry issues a token to each genuine merchant agent. The gateway trusts a
verified token, never a name written in an offer.
"""
from __future__ import annotations

import hashlib
import hmac
import secrets
import time

AUDIENCE = "agent-registry"
TTL_SECONDS = 300


class IdentityService:
    def __init__(self) -> None:
        self._key = secrets.token_bytes(32)

    def _sign(self, body: str) -> str:
        return hmac.new(self._key, body.encode(), hashlib.sha256).hexdigest()

    def issue(self, agent_id: str, ttl: int = TTL_SECONDS, now: float | None = None) -> str:
        exp = int((time.time() if now is None else now) + ttl)
        body = f"{agent_id}|{AUDIENCE}|{exp}"
        return f"{body}|{self._sign(body)}"

    def verify(self, token: str, now: float | None = None) -> tuple[str | None, str]:
        try:
            agent_id, aud, exp, sig = token.split("|")
        except ValueError:
            return None, "malformed token"
        if not hmac.compare_digest(sig, self._sign(f"{agent_id}|{aud}|{exp}")):
            return None, "bad signature"
        if aud != AUDIENCE:
            return None, "wrong audience"
        if (time.time() if now is None else now) >= int(exp):
            return None, "token expired"
        return agent_id, "ok"
