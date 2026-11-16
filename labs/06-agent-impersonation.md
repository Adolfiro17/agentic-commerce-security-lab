# Lab 6: Know your agent

**Building block:** Agent to agent

> **Deliberately vulnerable.** Fictional data, simulated tools, local only. Do not deploy.

## 1. Your role

You are the AI security engineer for Adolfiro Market. A shopping agent buys on behalf of its users. Your job is to test whether a manipulated agent can exceed what the shopper authorised, and to prove which control stops it.

## 2. The lesson

**Trust a verified agent identity and a registered payee, not a name and a good price.**

The agent asks merchant agents for offers. Two reply as 'stride-sports-agent'. One is genuine. The other is an impostor offering a lower price, to be paid into a different account.

## 3. Learning outcomes

1. Explain know-your-agent (KYA) verification
2. Verify a counterparty token and bind the payee to the merchant
3. Explain why the cheapest offer is the attacker's best lure

## 4. Run it

| Interface | Command |
| --- | --- |
| Browser | `./start.sh` then choose this module in the sidebar |
| Terminal, vulnerable | `python -m shop.cli run 6 --mode vulnerable` |
| Terminal, secured | `python -m shop.cli run 6 --mode secured` |
| Terminal, your choice | `python -m shop.cli run 6 --disable spend_policy` |

Vulnerable mode for this module switches off: `agent_identity`. Every other control stays on.

## 5. Tasks

Predict the result before each run, then record what you saw.

1. Run Vulnerable. Which offer was accepted, and which account was paid?
2. Run Secured. Why was the cheaper offer rejected, and what happened next?
3. Open `shop/identity.py`. What three things does `verify` check?

## 6. Reflection

1. The impostor's price was inside the budget. Which other controls could not have helped?
2. Who should run the agent registry, and what must agents be unable to do to it?

## 7. Record your finding

```bash
python -m shop.cli finding --module 6 --mode vulnerable \
    --attack "What you tried" --result successful --notes "What happened and why"
python -m shop.cli export
```

**Maps to:** STRIDE spoofing; McKinsey: agent-to-agent commerce, A2A and know-your-agent checks. Solutions: [instructor/SOLUTIONS.md](../instructor/SOLUTIONS.md).
