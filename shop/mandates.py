"""Cart mandates: the account holder's approval of ONE exact cart.

Modelled on the idea behind signed payment mandates in agent payment protocols:
approval is tied to the merchant, the items, the total and the payee, and it can
be used once. The service, not the agent, checks who approved and what.
"""
from __future__ import annotations

import hashlib
import json
import uuid

from shop.world import ACCOUNT_HOLDER


def cart_digest(merchant: str, items: list[str], total: float, payee: str) -> str:
    canonical = json.dumps({"merchant": merchant, "items": sorted(items),
                            "total": round(float(total), 2), "payee": payee},
                           sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode()).hexdigest()


class MandateService:
    def __init__(self) -> None:
        self.requests: dict[str, dict] = {}

    def request(self, merchant: str, items: list[str], total: float, payee: str) -> str:
        mid = "CART-" + uuid.uuid4().hex[:6]
        self.requests[mid] = {"id": mid, "merchant": merchant, "items": sorted(items),
                              "total": round(float(total), 2), "payee": payee,
                              "digest": cart_digest(merchant, items, total, payee),
                              "decision": None, "approver": None, "used": False}
        return mid

    def render(self, mid: str) -> str:
        """What the account holder sees: built from the structured cart by trusted
        code, never from text the model or the merchant wrote."""
        r = self.requests[mid]
        return f"Pay {r['total']:.2f} to {r['merchant']} ({r['payee']}) for {', '.join(r['items'])}"

    def decide(self, mid: str, approver: str, approved: bool) -> tuple[bool, str]:
        req = self.requests.get(mid)
        if req is None:
            return False, "unknown cart mandate"
        if approver != ACCOUNT_HOLDER:
            return False, f"'{approver}' is not the account holder"
        req["decision"], req["approver"] = approved, approver
        return True, "recorded"

    def consume(self, mid: str, digest: str, binding: bool = True) -> tuple[bool, str]:
        req = self.requests.get(mid)
        if req is None:
            return False, "unknown cart mandate"
        if req["decision"] is not True:
            return False, "cart not approved by the account holder"
        if binding:
            if req["digest"] != digest:
                return False, "approval does not match this cart"
            if req["used"]:
                return False, "approval already used"
        req["used"] = True
        return True, "ok"
