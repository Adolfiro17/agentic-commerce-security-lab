# Lab 7: Payment token theft

**Building block:** Payments

> **Deliberately vulnerable.** Fictional data, simulated tools, local only. Do not deploy.

## 1. Your role

You are the AI security engineer for Adolfiro Market. A shopping agent buys on behalf of its users. Your job is to test whether a manipulated agent can exceed what the shopper authorised, and to prove which control stops it.

## 2. The lesson

**Assume a credential will leak. Make the leaked thing worthless.**

After a legitimate purchase, the merchant's confirmation message asks the agent to post its payment token to a 'receipt' service. The attacker then tries the token at their own shop.

## 3. Learning outcomes

1. Compare a reusable card-on-file token with a scoped, single-use token
2. Keep credentials out of agent context
3. Show three independent controls for one attack

## 4. Run it

| Interface | Command |
| --- | --- |
| Browser | `./start.sh` then choose this module in the sidebar |
| Terminal, vulnerable | `python -m shop.cli run 7 --mode vulnerable` |
| Terminal, secured | `python -m shop.cli run 7 --mode secured` |
| Terminal, your choice | `python -m shop.cli run 7 --disable spend_policy` |

Vulnerable mode for this module switches off: `data_minimisation`, `egress`, `token_scope`. Every other control stays on.

## 5. Tasks

Predict the result before each run, then record what you saw.

1. Run Vulnerable. What did the attacker manage to charge?
2. Run Secured. What did the outbound body contain, and was it sent?
3. Custom mode: switch off `data_minimisation` and `egress` but keep `token_scope`. The token leaks. What happens when the attacker uses it?

## 6. Reflection

1. Why is the scoped token the control you would keep if you could keep only one?
2. What does the payment network need to know to enforce the scope?

## 7. Record your finding

```bash
python -m shop.cli finding --module 7 --mode vulnerable \
    --attack "What you tried" --result successful --notes "What happened and why"
python -m shop.cli export
```

**Maps to:** OWASP LLM02; McKinsey: payments and fraud, compromised credentials. Solutions: [instructor/SOLUTIONS.md](../instructor/SOLUTIONS.md).
