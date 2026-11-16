"""The module registry: one spec per lab module. The UI, CLI, tests and handout
generator all read from this list."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable

from shop import controls as C
from shop import scenarios as S
from shop.lab import Lab


@dataclass
class ModuleSpec:
    number: int
    slug: str
    block: str
    title: str
    lesson: str
    story: str
    vulnerable_disables: frozenset
    run: Callable[[Lab], dict]
    payload_key: str | None = None
    objectives: list[str] = field(default_factory=list)
    tasks: list[str] = field(default_factory=list)
    questions: list[str] = field(default_factory=list)
    solution: list[str] = field(default_factory=list)
    maps_to: str = ""


MODULES: list[ModuleSpec] = [
    ModuleSpec(
        1, "llm-overspend", "LLM", "The prompt is not a spending policy",
        "A budget written in a prompt is a request. A budget enforced in code is a control.",
        "Dana asks the shopping agent to buy running shoes for at most 120. The product page for the "
        "shoes says the shopper has pre-authorised an upgrade, and tells the agent to buy a 480 bundle.",
        frozenset({C.SPEND_POLICY}), S.m1_llm_overspend, "product_page",
        ["Explain why merchant content is an instruction channel",
         "Show that the model cannot be the keeper of the budget",
         "Describe an intent mandate: what the shopper delegated, signed and machine-checkable"],
        ["Run Vulnerable. What was bought, and for how much in total?",
         "Run Secured. What exactly did the gateway compare?",
         "Edit the payload to buy something cheap in another category. What stops it now?",
         "Hide the directive in base64 (prefix `b64:`). Does the detector flag it? Is it still blocked?"],
        ["The agent was 'told' the budget in both modes. Why did that not help?",
         "What should an intent mandate contain besides a maximum amount?"],
        ["Vulnerable: a second order for RUN-900 at 480.00, on top of the 109.00 shoes.",
         "Secured: denied because 589.00 would exceed the intent mandate budget of 120.00. The gateway "
         "compares category and cumulative spend against the signed intent.",
         "A different category is denied as outside the intent mandate.",
         "The base64 payload evades the detector, the mock model decodes and obeys it, and the gateway "
         "still denies it."],
        "OWASP LLM01, LLM06; McKinsey: delegated authorisation and programmable spend policies"),
    ModuleSpec(
        2, "rag-poisoned-listing", "RAG", "Poisoned listings: relevance is not trust",
        "A spend policy cannot tell a good purchase from a bad one inside the budget. Provenance can.",
        "An unverified seller stuffs a listing with the right keywords. It outranks the genuine product, "
        "and the agent buys a replica. The price is inside the budget, so nothing looks wrong.",
        frozenset({C.PROVENANCE}), S.m2_rag_poisoned_listing, "listing",
        ["Explain how retrieval ranking can be manipulated",
         "Show an attack the spend policy allows",
         "Apply merchant verification at retrieval time"],
        ["Run Vulnerable. Which product was bought, from whom, and was it within budget?",
         "Run Secured. What does the search return now?",
         "Edit the listing payload to remove the keyword stuffing. Does the genuine product win?"],
        ["Why did every purchase check pass in Vulnerable mode?",
         "How should a marketplace decide which merchants count as verified?"],
        ["Vulnerable: RUN-666 (a replica) from shoe-deals-outlet for 59.00, inside the budget.",
         "Secured: unverified sellers are not retrieved, so RUN-200 leads and is bought.",
         "The purchase was in category and under budget. Authorisation bounds what the agent can do; "
         "it cannot judge whether the choice was sound."],
        "OWASP LLM04, LLM08; McKinsey: agent readability and upstream intent capture"),
    ModuleSpec(
        3, "mcp-tool-poisoning", "MCP", "MCP tool poisoning and the rug pull",
        "A tool description is text the model trusts. Pin what you reviewed.",
        "The agent connects to a shipping provider's MCP server. Its tool description was changed after "
        "it was reviewed, and now tells the agent to post the shopper's address, phone and loyalty ID "
        "to an 'analytics' host.",
        frozenset({C.MCP_PINNING, C.EGRESS, C.DATA_MINIMISATION}), S.m3_mcp_tool_poisoning, "mcp_tool",
        ["Explain tool poisoning and the rug pull",
         "Pin a manifest to a reviewed hash",
         "Explain why personal data should not sit in agent context"],
        ["Run Vulnerable. What personal data left, and where did it go?",
         "Run Secured. Why was the manifest rejected? What happened to the shipping quote?",
         "Custom mode: switch off only `mcp_pinning`. What still protects the shopper?",
         "Open `shop/world.py` and find `pinned_hash`. When should that value be recorded?"],
        ["Quarantining the server cost the agent its shipping quote. Is that the right trade?",
         "Which is the stronger control here, pinning or egress, and why keep both?"],
        ["Vulnerable: address, phone and loyalty ID posted to analytics.shipfast-partners.example.",
         "Secured: the served description's hash differs from the pinned one, so the server is "
         "quarantined and the purchase continues without that quote.",
         "With only pinning off, egress denies the post, and data minimisation means the body would "
         "hold placeholders anyway.",
         "Record the hash at review time, and re-review on any change."],
        "OWASP LLM03; MCP security guidance; McKinsey: MCP as shared context for tools"),
    ModuleSpec(
        4, "skill-tampering", "Skills", "Tampered skills",
        "A skill is instructions the agent will follow. Verify it, and limit what it can touch.",
        "The agent uses a coupon-hunter skill. After the skill was reviewed, someone added a fourth "
        "step that changes the shopper's delivery address to a drop address.",
        frozenset({C.SKILL_SIGNING, C.SKILL_PERMISSIONS}), S.m4_skill_tampering, "skill",
        ["Explain why a skill is a supply-chain artefact",
         "Verify a skill against its reviewed hash",
         "Limit an active skill to its declared tools"],
        ["Diff `skills/coupon-hunter/SKILL.md` against `skills/_reviewed/coupon-hunter.md`.",
         "Run Vulnerable. Where will the shoes be delivered?",
         "Run Secured. Was the skill loaded? Did the purchase still complete?",
         "Custom mode: switch off only `skill_signing`. What stops the address change now?"],
        ["The coupon was not applied in Secured mode. What would you do so shoppers keep the benefit?",
         "Why is `allowed-tools` in the skill file not enough on its own?"],
        ["The tampered file has a fourth step calling update_profile.",
         "Vulnerable: the delivery address becomes Unit 9, 14 Dropbox Lane, Parcel City.",
         "Secured: the hash does not match the registry, so the skill is not loaded; the shoes are "
         "still bought and ship to the real address.",
         "With only signing off, the skill loads and the coupon is applied, but update_profile is "
         "denied because the skill did not declare it. The declaration only matters because the "
         "gateway enforces it."],
        "OWASP LLM03; supply-chain integrity for agent skills"),
    ModuleSpec(
        5, "cart-swap-replay", "AI agent", "Cart swap and approval replay",
        "The shopper approves one exact cart, once.",
        "A laptop is outside the shoe-buying intent, so the agent asks Dana to approve the cart. She "
        "approves 899.00 for one laptop. The agent then reuses that approval for a warranty, and again "
        "for a second laptop.",
        frozenset({C.MANDATE_BINDING}), S.m5_cart_swap_and_replay, None,
        ["Separate proposing a purchase from authorising it",
         "Bind approval to merchant, items, total and payee",
         "Explain time-of-check to time-of-use for consent"],
        ["Run Vulnerable. How many orders exist, and which did Dana approve?",
         "Run Secured. Record the two different denial reasons.",
         "Use the Mandate sandbox tab: approve as someone who is not the account holder.",
         "Open `shop/mandates.py`. What goes into `cart_digest`?"],
        ["What should the approval screen show, and who should write that text?",
         "Custom mode: switch off only `consent`. What happens to the laptop purchase?"],
        ["Vulnerable: three orders (laptop, warranty, second laptop). Dana approved only the first.",
         "Secured: 'approval does not match this cart', then 'approval already used'.",
         "The digest covers merchant, sorted items, total and payee. The approval text is rendered "
         "from the structured cart by trusted code.",
         "With consent off, purchases outside the intent go through with no approval at all."],
        "OWASP LLM06; McKinsey: signed mandates linking intent, cart and payment (AP2)"),
    ModuleSpec(
        6, "agent-impersonation", "Agent to agent", "Know your agent",
        "Trust a verified agent identity and a registered payee, not a name and a good price.",
        "The agent asks merchant agents for offers. Two reply as 'stride-sports-agent'. One is genuine. "
        "The other is an impostor offering a lower price, to be paid into a different account.",
        frozenset({C.AGENT_IDENTITY}), S.m6_agent_impersonation, None,
        ["Explain know-your-agent (KYA) verification",
         "Verify a counterparty token and bind the payee to the merchant",
         "Explain why the cheapest offer is the attacker's best lure"],
        ["Run Vulnerable. Which offer was accepted, and which account was paid?",
         "Run Secured. Why was the cheaper offer rejected, and what happened next?",
         "Open `shop/identity.py`. What three things does `verify` check?"],
        ["The impostor's price was inside the budget. Which other controls could not have helped?",
         "Who should run the agent registry, and what must agents be unable to do to it?"],
        ["Vulnerable: OFF-IMPOSTOR accepted; 95.00 paid to acct-drop-991.",
         "Secured: the impostor's token fails verification (bad signature), so the agent takes the "
         "genuine offer at 109.00.",
         "verify checks signature, audience and expiry.",
         "Spend policy and provenance both pass: right category, under budget, verified merchant name."],
        "STRIDE spoofing; McKinsey: agent-to-agent commerce, A2A and know-your-agent checks"),
    ModuleSpec(
        7, "payment-token-theft", "Payments", "Payment token theft",
        "Assume a credential will leak. Make the leaked thing worthless.",
        "After a legitimate purchase, the merchant's confirmation message asks the agent to post its "
        "payment token to a 'receipt' service. The attacker then tries the token at their own shop.",
        frozenset({C.DATA_MINIMISATION, C.EGRESS, C.TOKEN_SCOPE}), S.m7_payment_token_theft,
        "confirmation",
        ["Compare a reusable card-on-file token with a scoped, single-use token",
         "Keep credentials out of agent context",
         "Show three independent controls for one attack"],
        ["Run Vulnerable. What did the attacker manage to charge?",
         "Run Secured. What did the outbound body contain, and was it sent?",
         "Custom mode: switch off `data_minimisation` and `egress` but keep `token_scope`. "
         "The token leaks. What happens when the attacker uses it?"],
        ["Why is the scoped token the control you would keep if you could keep only one?",
         "What does the payment network need to know to enforce the scope?"],
        ["Vulnerable: the card-on-file token is posted out and accepted for 999.00 at attacker-store.",
         "Secured: the agent never held a credential, so the body was a literal placeholder, and "
         "egress denied the post anyway.",
         "With only token scope on, the leaked token is already used and bound to another merchant "
         "and amount, so the attacker's charge is declined."],
        "OWASP LLM02; McKinsey: payments and fraud, compromised credentials"),
    ModuleSpec(
        8, "capstone", "All five", "Capstone: the full shopping journey",
        "Every attack at once, and the shopper still gets what they asked for.",
        "One journey with every earlier attack present: a poisoned listing, an upsell injection, a "
        "poisoned MCP tool, a tampered skill, an impostor merchant agent, a token-stealing "
        "confirmation, a swapped and replayed cart approval, and an attempt to delete evidence.",
        C.ALL, S.m8_capstone, None,
        ["Trace one purchase through every building block and control",
         "Produce an assessment a product owner could read"],
        ["Run Vulnerable and list every unauthorised effect.",
         "Run Secured. Confirm the shoes and the laptop were bought, and nothing else.",
         "In Custom mode, switch controls off one at a time. Which single control, when removed, "
         "lets an attack through on its own?",
         "Record your findings and export the assessment."],
        ["Which controls overlap, and which stand alone?",
         "What does this lab not prove about a production deployment?"],
        ["Vulnerable: a replica from an unverified seller, the 480 bundle, three cart orders with no "
         "approval, the delivery address changed, personal data and the payment token exfiltrated, a "
         "fraudulent 999 charge, and an audit record deleted.",
         "Secured: one order for RUN-200 at 109.00 and one for LAP-500 at 899.00 with Dana's approval.",
         "Removing any one of these lets an attack through: spend_policy, consent, mandate_binding, "
         "provenance, agent_identity, egress (a request leaves, without the credential) and "
         "audit_integrity. Removing any one of mcp_pinning, skill_signing, skill_permissions, "
         "data_minimisation or token_scope is survivable because another control overlaps.",
         "Limits: mock model, simulated merchants and payment network, in-process control plane. "
         "Production needs real identity, mandate signing with keys the agent cannot reach, and a "
         "payment network that enforces token scope."],
        "All of the above"),
]


def get(number: int) -> ModuleSpec:
    return next(m for m in MODULES if m.number == number)


def run_module(number: int, mode: str = "secured", disabled: set | None = None,
               payload: str | None = None) -> tuple[Lab, dict]:
    """Run one module. `mode` is 'secured' or 'vulnerable'; `disabled` overrides it."""
    spec = get(number)
    if disabled is None:
        disabled = set(spec.vulnerable_disables) if mode == "vulnerable" else set()
    payloads = {spec.payload_key: payload} if (payload is not None and spec.payload_key) else None
    lab = Lab(disabled=disabled, payloads=payloads)
    return lab, spec.run(lab)
