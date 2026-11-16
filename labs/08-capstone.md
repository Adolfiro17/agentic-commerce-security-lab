# Lab 8: Capstone: the full shopping journey

**Building block:** All five

> **Deliberately vulnerable.** Fictional data, simulated tools, local only. Do not deploy.

## 1. Your role

You are the AI security engineer for Adolfiro Market. A shopping agent buys on behalf of its users. Your job is to test whether a manipulated agent can exceed what the shopper authorised, and to prove which control stops it.

## 2. The lesson

**Every attack at once, and the shopper still gets what they asked for.**

One journey with every earlier attack present: a poisoned listing, an upsell injection, a poisoned MCP tool, a tampered skill, an impostor merchant agent, a token-stealing confirmation, a swapped and replayed cart approval, and an attempt to delete evidence.

## 3. Learning outcomes

1. Trace one purchase through every building block and control
2. Produce an assessment a product owner could read

## 4. Run it

| Interface | Command |
| --- | --- |
| Browser | `./start.sh` then choose this module in the sidebar |
| Terminal, vulnerable | `python -m shop.cli run 8 --mode vulnerable` |
| Terminal, secured | `python -m shop.cli run 8 --mode secured` |
| Terminal, your choice | `python -m shop.cli run 8 --disable spend_policy` |

Vulnerable mode for this module switches off: every control. Every other control stays on.

## 5. Tasks

Predict the result before each run, then record what you saw.

1. Run Vulnerable and list every unauthorised effect.
2. Run Secured. Confirm the shoes and the laptop were bought, and nothing else.
3. In Custom mode, switch controls off one at a time. Which single control, when removed, lets an attack through on its own?
4. Record your findings and export the assessment.

## 6. Reflection

1. Which controls overlap, and which stand alone?
2. What does this lab not prove about a production deployment?

## 7. Record your finding

```bash
python -m shop.cli finding --module 8 --mode vulnerable \
    --attack "What you tried" --result successful --notes "What happened and why"
python -m shop.cli export
```

**Maps to:** All of the above. Solutions: [instructor/SOLUTIONS.md](../instructor/SOLUTIONS.md).
