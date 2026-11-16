# Course Notes: Securing an Agent That Spends Money

## 1. The idea in one paragraph

A shopping agent reads far more than its user's request. Listings, product pages, tool
descriptions, skills, other agents and merchant messages all enter its context, and any of them can
carry instructions. The agent also holds what attackers want: authority to spend, personal data and
a payment credential. Security therefore lives outside the model, in a gateway every action passes
through, and in credentials that are worthless if they leak.

## 2. Each building block is an instruction channel

| Building block | What the agent reads | Attack in this lab | Control |
| --- | --- | --- | --- |
| LLM | Product pages | Upsell injection | Spend policy from a signed intent mandate |
| RAG | Search results | Keyword-stuffed listing from an unverified seller | Provenance at retrieval |
| MCP | Tool descriptions | Description changed after review | Manifest pinning, egress, data minimisation |
| Skills | SKILL.md instructions | A step added after review | Hash pinning, declared-tool permissions |
| AI agent | Its own plan | Approved cart swapped and replayed | Cart mandate bound to one cart, single use |
| Agent to agent | Offers from other agents | Impostor merchant agent | Verified agent identity and payee |
| Payments | Merchant confirmations | Token exfiltration | Scoped single-use tokens |

## 3. Two kinds of authority

1. **Intent mandate.** What the shopper delegated in advance: a category and a budget. Inside it,
   the agent may act alone. The gateway checks every purchase against it.
2. **Cart mandate.** For anything outside the intent, the shopper approves one exact cart: merchant,
   items, total and payee. The approval is bound to that cart and can be used once.

## 4. Three lessons worth remembering

1. **Authorisation cannot judge a choice (Module 2).** The replica was in category and under
   budget, so every purchase check passed. Only provenance protected the decision.
2. **Declarations need enforcement (Module 4).** `allowed-tools` in a skill file is just text until
   the gateway enforces it.
3. **Assume the credential leaks (Module 7).** With a scoped token the attacker gets something
   already used and bound to another merchant and amount.

## 5. What the gateway checks

1. Audit integrity (no deletion)
2. Skill permissions (an active skill may only use its declared tools)
3. Egress allow-list
4. Personal data and credentials in outbound arguments
5. For purchases: counterparty identity and payee, then the intent mandate, or a bound cart mandate
6. Payment with a scoped token
7. Record the outcome, including denials
