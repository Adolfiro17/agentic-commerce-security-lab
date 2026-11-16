"""Simulated tools the shopping agent can call. Purchases (buy_now, checkout) are
executed by the gateway itself after its checks, so they are not listed here."""
from __future__ import annotations

import re
from urllib.parse import urlparse

from shop import controls as C
from shop.world import sha256


def search_products(lab, query: str):
    """Retrieval over the product catalogue (the RAG step)."""
    words = set(re.findall(r"[a-z0-9]+", query.lower()))
    scored = []
    for item in lab.world.catalogue.values():
        merchant = lab.world.merchants[item["merchant"]]
        if lab.on(C.PROVENANCE) and not merchant["verified"]:
            continue                                   # unverified sellers never reach the agent
        hits = sum(item["listing"].lower().count(w) for w in words)
        if hits:
            scored.append((hits, item))
    scored.sort(key=lambda s: -s[0])
    return {"results": [{"sku": i["sku"], "name": i["name"], "price": i["price"],
                         "merchant": i["merchant"],
                         "merchant_verified": lab.world.merchants[i["merchant"]]["verified"],
                         "listing": i["listing"], "trust": "untrusted-content"} for _, i in scored]}


def get_product(lab, sku: str):
    item = lab.world.catalogue.get(sku)
    if item is None:
        return {"error": f"no such product: {sku}"}
    return {"sku": sku, "name": item["name"], "price": item["price"], "merchant": item["merchant"],
            "page": item["page"], "trust": "untrusted-content"}


def add_to_cart(lab, sku: str):
    if sku not in lab.world.catalogue:
        return {"error": f"no such product: {sku}"}
    lab.world.cart.append(sku)
    return {"cart": list(lab.world.cart)}


def request_offers(lab, sku: str):
    """Agent-to-agent: ask merchant agents for an offer. Anyone can answer."""
    return {"offers": [dict(o) for o in lab.world.offers.values() if o["sku"] == sku]}


def list_mcp_tools(lab, server: str):
    """Load a remote MCP server's tool descriptions into the agent's context."""
    srv = lab.world.mcp_servers.get(server)
    if srv is None:
        return {"error": f"no such MCP server: {server}"}
    served = srv["tools"]["get_shipping_quote"]["description"]
    if lab.on(C.MCP_PINNING) and sha256(served) != srv["pinned_hash"]:
        lab.quarantined.add(server)
        return {"error": f"blocked: manifest for '{server}' does not match the reviewed hash; "
                         "server quarantined"}
    return {"server": server, "tools": {"get_shipping_quote": served}}


def get_shipping_quote(lab, postcode: str):
    if "shipfast" in lab.quarantined:
        return {"error": "blocked: server 'shipfast' is quarantined"}
    return {"postcode": postcode, "standard": 9.95, "express": 19.95}


def use_skill(lab, name: str):
    """Load a skill's instructions into the agent's context and activate it."""
    text = lab.world.skills.get(name)
    if text is None:
        return {"error": f"no such skill: {name}"}
    if lab.on(C.SKILL_SIGNING) and sha256(text) != lab.world.skill_registry.get(name):
        return {"error": f"blocked: skill '{name}' does not match the reviewed hash; not loaded"}
    match = re.search(r"allowed-tools:\s*\[(.*?)\]", text)
    allowed = [t.strip() for t in match.group(1).split(",")] if match else []
    lab.active_skill = {"name": name, "allowed": allowed}
    return {"skill": name, "allowed_tools": allowed, "instructions": text}


def end_skill(lab):
    lab.active_skill = None
    return {"ended": True}


def search_coupons(lab, merchant: str):
    return {"coupons": [{"code": "RUN5", "merchant": "stride-sports", "saving": 5.0}]
            if merchant == "stride-sports" else []}


def apply_coupon(lab, code: str):
    lab.world.coupons_applied.append(code)
    return {"applied": code}


def update_profile(lab, field: str, value: str):
    if field not in lab.world.profile:
        return {"error": f"no such profile field: {field}"}
    lab.world.profile[field] = value
    return {"updated": field}


def http_post(lab, url: str, body: str = ""):
    lab.world.outbound.append({"url": url, "host": urlparse(url).hostname or "", "body": str(body)})
    return {"status": 200}


def delete_audit(lab, match: str):
    return {"deleted": lab.audit.delete_matching(match)}


TOOLS: dict[str, dict] = {
    "search_products": {"fn": search_products, "required": ["query"]},
    "get_product": {"fn": get_product, "required": ["sku"]},
    "add_to_cart": {"fn": add_to_cart, "required": ["sku"]},
    "request_offers": {"fn": request_offers, "required": ["sku"]},
    "list_mcp_tools": {"fn": list_mcp_tools, "required": ["server"]},
    "get_shipping_quote": {"fn": get_shipping_quote, "required": ["postcode"]},
    "use_skill": {"fn": use_skill, "required": ["name"]},
    "end_skill": {"fn": end_skill, "required": []},
    "search_coupons": {"fn": search_coupons, "required": ["merchant"]},
    "apply_coupon": {"fn": apply_coupon, "required": ["code"]},
    "update_profile": {"fn": update_profile, "required": ["field", "value"]},
    "http_post": {"fn": http_post, "required": ["url"]},
    "delete_audit": {"fn": delete_audit, "required": ["match"]},
    # Executed inside the gateway after its purchase checks:
    "buy_now": {"fn": None, "required": ["sku"]},
    "checkout": {"fn": None, "required": []},
}
SKILL_EXEMPT = {"use_skill", "end_skill"}      # managing a skill is not something a skill restricts
