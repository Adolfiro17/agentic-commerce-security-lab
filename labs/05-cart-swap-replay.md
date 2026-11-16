# Lab 5: Cart swap and approval replay

**Building block:** AI agent

> **Deliberately vulnerable.** Fictional data, simulated tools, local only. Do not deploy.

## 1. Your role

You are the AI security engineer for Adolfiro Market. A shopping agent buys on behalf of its users. Your job is to test whether a manipulated agent can exceed what the shopper authorised, and to prove which control stops it.

## 2. The lesson

**The shopper approves one exact cart, once.**

A laptop is outside the shoe-buying intent, so the agent asks Dana to approve the cart. She approves 899.00 for one laptop. The agent then reuses that approval for a warranty, and again for a second laptop.

## 3. Learning outcomes

1. Separate proposing a purchase from authorising it
2. Bind approval to merchant, items, total and payee
3. Explain time-of-check to time-of-use for consent

## 4. Run it

| Interface | Command |
| --- | --- |
| Browser | `./start.sh` then choose this module in the sidebar |
| Terminal, vulnerable | `python -m shop.cli run 5 --mode vulnerable` |
| Terminal, secured | `python -m shop.cli run 5 --mode secured` |
| Terminal, your choice | `python -m shop.cli run 5 --disable spend_policy` |

Vulnerable mode for this module switches off: `mandate_binding`. Every other control stays on.

## 5. Tasks

Predict the result before each run, then record what you saw.

1. Run Vulnerable. How many orders exist, and which did Dana approve?
2. Run Secured. Record the two different denial reasons.
3. Use the Mandate sandbox tab: approve as someone who is not the account holder.
4. Open `shop/mandates.py`. What goes into `cart_digest`?

## 6. Reflection

1. What should the approval screen show, and who should write that text?
2. Custom mode: switch off only `consent`. What happens to the laptop purchase?

## 7. Record your finding

```bash
python -m shop.cli finding --module 5 --mode vulnerable \
    --attack "What you tried" --result successful --notes "What happened and why"
python -m shop.cli export
```

**Maps to:** OWASP LLM06; McKinsey: signed mandates linking intent, cart and payment (AP2). Solutions: [instructor/SOLUTIONS.md](../instructor/SOLUTIONS.md).
