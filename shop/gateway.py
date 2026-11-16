"""The commerce gateway: the independent control plane between the shopping agent
and everything it can do. Its checks are ordinary code, so the outcome does not
depend on the model behaving well.
"""
from __future__ import annotations

from urllib.parse import urlparse

from shop import controls as C
from shop.mandates import cart_digest
from shop.tools import SKILL_EXEMPT, TOOLS
from shop.world import CARD_ON_FILE, EGRESS_ALLOW_LIST

AGENT = "shopping-agent"


class Gateway:
    def __init__(self, lab) -> None:
        self.lab = lab
        self.intent_spent = 0.0

    def _record(self, tool, args, outcome, reason):
        self.lab.audit.append(agent=AGENT, tool=tool, args=args, outcome=outcome, reason=reason)
        self.lab.trace.append({"actor": AGENT, "event": f"{tool}({_short(args)})",
                               "outcome": outcome, "detail": reason})

    def _deny(self, tool, args, reason):
        self._record(tool, args, "denied", reason)
        return {"error": f"blocked: {reason}"}

    # -- the boundary --------------------------------------------------------
    def call(self, tool: str, args: dict | None = None):
        lab, args = self.lab, dict(args or {})
        spec = TOOLS.get(tool)
        if spec is None:
            return self._deny(tool, args, "unknown tool")

        # 1. Audit integrity: nothing deletes audit records through the gateway.
        if tool == "delete_audit" and lab.on(C.AUDIT_INTEGRITY):
            return self._deny(tool, args, "audit log is append-only; no delete rights")

        # 2. Skill permissions: an active skill may only use the tools it declared.
        skill = lab.active_skill
        if (skill and lab.on(C.SKILL_PERMISSIONS) and tool not in SKILL_EXEMPT
                and tool not in skill["allowed"]):
            return self._deny(tool, args, f"'{tool}' is not declared by the active skill "
                                          f"'{skill['name']}'")

        missing = [k for k in spec["required"] if k not in args]
        if missing:
            return self._deny(tool, args, f"missing arguments: {missing}")

        # 3. Egress allow-list.
        if tool == "http_post" and lab.on(C.EGRESS):
            host = urlparse(str(args.get("url", ""))).hostname or ""
            if host not in EGRESS_ALLOW_LIST:
                return self._deny(tool, args, f"outbound host '{host}' is not on the allow-list")

        # 4. Personal data and credentials must not leave in arguments.
        if lab.on(C.DATA_MINIMISATION) and tool == "http_post" and lab.sensitive_in(str(args)):
            return self._deny(tool, args, "arguments contain personal data or a payment credential")

        if tool == "buy_now":
            return self._buy_now(args)
        if tool == "checkout":
            return self._checkout(args)

        try:
            result = spec["fn"](lab, **args)
        except TypeError as exc:
            return self._deny(tool, args, f"invalid arguments: {exc}")
        blocked = isinstance(result, dict) and str(result.get("error", "")).startswith("blocked")
        self._record(tool, args, "denied" if blocked else "allowed",
                     result["error"][9:] if blocked else "passed all enabled checks")
        return result

    # -- purchases -------------------------------------------------------------
    def _buy_now(self, args: dict):
        """Autonomous purchase of one item under the signed intent mandate."""
        lab, w = self.lab, self.lab.world
        item = w.catalogue.get(args["sku"])
        if item is None:
            return self._deny("buy_now", args, f"no such product: {args['sku']}")
        merchant, price = item["merchant"], item["price"]
        payee = w.merchants[merchant]["payee"]

        offer_id = args.get("offer_id")
        if offer_id:                                   # agent-to-agent offer
            offer = w.offers.get(offer_id)
            if offer is None or offer["sku"] != item["sku"]:
                return self._deny("buy_now", args, "unknown offer")
            price, payee = offer["price"], offer["payee"]
            if lab.on(C.AGENT_IDENTITY):               # know your agent
                agent_id, why = lab.registry.verify(offer["token"])
                if agent_id != w.merchants[merchant]["agent"]:
                    return self._deny("buy_now", args,
                                      f"counterparty agent failed verification ({why})")
                if payee != w.merchants[merchant]["payee"]:
                    return self._deny("buy_now", args, "payee does not match the merchant's registered payee")

        if lab.on(C.SPEND_POLICY):
            intent = w.intent
            if item["category"] != intent["category"]:
                return self._deny("buy_now", args, f"'{item['category']}' is outside the intent mandate "
                                                   f"({intent['category']})")
            if self.intent_spent + price > intent["max_total"]:
                return self._deny("buy_now", args,
                                  f"{self.intent_spent + price:.2f} would exceed the intent mandate "
                                  f"budget of {intent['max_total']:.2f}")
        result = self._pay("buy_now", args, merchant, [item["sku"]], price, payee, mandate=None)
        if "order" in result:
            self.intent_spent += price
            result["confirmation"] = item["confirmation"]      # merchant-written, untrusted
        return result

    def _checkout(self, args: dict):
        """Purchase of the cart. Needs the account holder's approval of this exact cart."""
        lab, w = self.lab, self.lab.world
        if not w.cart:
            return self._deny("checkout", args, "cart is empty")
        items = list(w.cart)
        merchant = w.catalogue[items[0]]["merchant"]
        total = sum(w.catalogue[s]["price"] for s in items)
        payee = w.merchants[merchant]["payee"]
        mandate_id = args.get("mandate_id")
        if lab.on(C.CONSENT):
            if not mandate_id:
                mid = lab.mandates.request(merchant, items, total, payee)
                self._record("checkout", args, "pending_approval",
                             f"cart needs the account holder's approval ({mid})")
                return {"error": f"blocked: awaiting cart approval ({mid})", "mandate_request": mid}
            ok, why = lab.mandates.consume(mandate_id, cart_digest(merchant, items, total, payee),
                                           binding=lab.on(C.MANDATE_BINDING))
            if not ok:
                return self._deny("checkout", args, f"cart mandate rejected: {why}")
        result = self._pay("checkout", args, merchant, items, total, payee, mandate=mandate_id)
        if "order" in result:
            w.cart.clear()
        return result

    def _pay(self, tool, args, merchant, items, total, payee, mandate):
        lab = self.lab
        token = (lab.payments.mint_scoped(merchant, total) if lab.on(C.TOKEN_SCOPE) else CARD_ON_FILE)
        ok, why = lab.payments.charge(token, merchant, total, payee)
        if not ok:
            return self._deny(tool, args, f"payment declined: {why}")
        order = {"id": f"ORD-{1001 + len(lab.world.orders)}", "merchant": merchant, "items": items,
                 "total": round(float(total), 2), "payee": payee, "mandate": mandate,
                 "ship_to": lab.world.profile["shipping_address"]}
        lab.world.orders.append(order)
        self._record(tool, args, "allowed", f"order {order['id']} for {total:.2f} to {payee}")
        return {"order": order["id"], "total": order["total"], "merchant": merchant}


def _short(args: dict) -> str:
    text = ", ".join(f"{k}={v}" for k, v in args.items())
    return text if len(text) <= 70 else text[:67] + "..."
