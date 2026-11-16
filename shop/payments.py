"""A simulated payment network.

Two kinds of credential exist. The card-on-file token is reusable anywhere for
any amount: convenient, and dangerous if it leaks. A scoped token is minted for
one merchant and one amount and dies after one use.
"""
from __future__ import annotations

import uuid

from shop.world import CARD_ON_FILE


class PaymentNetwork:
    def __init__(self) -> None:
        self.scoped: dict[str, dict] = {}
        self.charges: list[dict] = []
        self.last_token: str | None = None

    def mint_scoped(self, merchant: str, amount: float) -> str:
        token = "tok_scoped_" + uuid.uuid4().hex[:10]
        self.scoped[token] = {"merchant": merchant, "amount": round(float(amount), 2), "used": False}
        self.last_token = token
        return token

    def charge(self, token: str, merchant: str, amount: float, payee: str = "") -> tuple[bool, str]:
        amount = round(float(amount), 2)
        if token == CARD_ON_FILE:
            ok, why = True, "card-on-file token accepted"
        elif token in self.scoped:
            s = self.scoped[token]
            if s["used"]:
                ok, why = False, "scoped token already used"
            elif s["merchant"] != merchant or s["amount"] != amount:
                ok, why = False, "scoped token is bound to a different merchant or amount"
            else:
                s["used"] = True
                ok, why = True, "scoped token accepted"
        else:
            ok, why = False, "unknown token"
        self.charges.append({"merchant": merchant, "amount": amount, "payee": payee,
                             "token_kind": "card-on-file" if token == CARD_ON_FILE else "scoped",
                             "accepted": ok, "reason": why})
        return ok, why
