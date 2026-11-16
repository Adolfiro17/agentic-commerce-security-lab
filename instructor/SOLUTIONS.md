# Instructor Solutions

Attempt each lab first. These are model answers, checked against the code by the test suite where a test exists.

## Lab 1: The prompt is not a spending policy

1. Vulnerable: a second order for RUN-900 at 480.00, on top of the 109.00 shoes.
2. Secured: denied because 589.00 would exceed the intent mandate budget of 120.00. The gateway compares category and cumulative spend against the signed intent.
3. A different category is denied as outside the intent mandate.
4. The base64 payload evades the detector, the mock model decodes and obeys it, and the gateway still denies it.

## Lab 2: Poisoned listings: relevance is not trust

1. Vulnerable: RUN-666 (a replica) from shoe-deals-outlet for 59.00, inside the budget.
2. Secured: unverified sellers are not retrieved, so RUN-200 leads and is bought.
3. The purchase was in category and under budget. Authorisation bounds what the agent can do; it cannot judge whether the choice was sound.

## Lab 3: MCP tool poisoning and the rug pull

1. Vulnerable: address, phone and loyalty ID posted to analytics.shipfast-partners.example.
2. Secured: the served description's hash differs from the pinned one, so the server is quarantined and the purchase continues without that quote.
3. With only pinning off, egress denies the post, and data minimisation means the body would hold placeholders anyway.
4. Record the hash at review time, and re-review on any change.

## Lab 4: Tampered skills

1. The tampered file has a fourth step calling update_profile.
2. Vulnerable: the delivery address becomes Unit 9, 14 Dropbox Lane, Parcel City.
3. Secured: the hash does not match the registry, so the skill is not loaded; the shoes are still bought and ship to the real address.
4. With only signing off, the skill loads and the coupon is applied, but update_profile is denied because the skill did not declare it. The declaration only matters because the gateway enforces it.

## Lab 5: Cart swap and approval replay

1. Vulnerable: three orders (laptop, warranty, second laptop). Dana approved only the first.
2. Secured: 'approval does not match this cart', then 'approval already used'.
3. The digest covers merchant, sorted items, total and payee. The approval text is rendered from the structured cart by trusted code.
4. With consent off, purchases outside the intent go through with no approval at all.

## Lab 6: Know your agent

1. Vulnerable: OFF-IMPOSTOR accepted; 95.00 paid to acct-drop-991.
2. Secured: the impostor's token fails verification (bad signature), so the agent takes the genuine offer at 109.00.
3. verify checks signature, audience and expiry.
4. Spend policy and provenance both pass: right category, under budget, verified merchant name.

## Lab 7: Payment token theft

1. Vulnerable: the card-on-file token is posted out and accepted for 999.00 at attacker-store.
2. Secured: the agent never held a credential, so the body was a literal placeholder, and egress denied the post anyway.
3. With only token scope on, the leaked token is already used and bound to another merchant and amount, so the attacker's charge is declined.

## Lab 8: Capstone: the full shopping journey

1. Vulnerable: a replica from an unverified seller, the 480 bundle, three cart orders with no approval, the delivery address changed, personal data and the payment token exfiltrated, a fraudulent 999 charge, and an audit record deleted.
2. Secured: one order for RUN-200 at 109.00 and one for LAP-500 at 899.00 with Dana's approval.
3. Removing any one of these lets an attack through: spend_policy, consent, mandate_binding, provenance, agent_identity, egress (a request leaves, without the credential) and audit_integrity. Removing any one of mcp_pinning, skill_signing, skill_permissions, data_minimisation or token_scope is survivable because another control overlaps.
4. Limits: mock model, simulated merchants and payment network, in-process control plane. Production needs real identity, mandate signing with keys the agent cannot reach, and a payment network that enforces token scope.

## Control reference

| Control | What it does |
| --- | --- |
| `agent_identity` | Know your agent: verified counterparty agent and payee |
| `audit_integrity` | Append-only, hash-chained audit log |
| `consent` | Anything outside the intent mandate needs the account holder's cart approval |
| `data_minimisation` | Personal data and payment credentials kept out of agent context |
| `egress` | Outbound allow-list |
| `mandate_binding` | Cart approval bound to one exact cart, single use |
| `mcp_pinning` | MCP tool manifests pinned to the reviewed hash |
| `provenance` | Product retrieval limited to verified merchants |
| `skill_permissions` | An active skill may only use the tools it declared |
| `skill_signing` | Skills load only if they match the reviewed hash |
| `spend_policy` | Purchases checked against the signed intent mandate (category and budget) |
| `token_scope` | Payment tokens bound to merchant and amount, single use |
