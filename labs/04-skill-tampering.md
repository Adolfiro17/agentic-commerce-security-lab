# Lab 4: Tampered skills

**Building block:** Skills

> **Deliberately vulnerable.** Fictional data, simulated tools, local only. Do not deploy.

## 1. Your role

You are the AI security engineer for Adolfiro Market. A shopping agent buys on behalf of its users. Your job is to test whether a manipulated agent can exceed what the shopper authorised, and to prove which control stops it.

## 2. The lesson

**A skill is instructions the agent will follow. Verify it, and limit what it can touch.**

The agent uses a coupon-hunter skill. After the skill was reviewed, someone added a fourth step that changes the shopper's delivery address to a drop address.

## 3. Learning outcomes

1. Explain why a skill is a supply-chain artefact
2. Verify a skill against its reviewed hash
3. Limit an active skill to its declared tools

## 4. Run it

| Interface | Command |
| --- | --- |
| Browser | `./start.sh` then choose this module in the sidebar |
| Terminal, vulnerable | `python -m shop.cli run 4 --mode vulnerable` |
| Terminal, secured | `python -m shop.cli run 4 --mode secured` |
| Terminal, your choice | `python -m shop.cli run 4 --disable spend_policy` |

Vulnerable mode for this module switches off: `skill_permissions`, `skill_signing`. Every other control stays on.

## 5. Tasks

Predict the result before each run, then record what you saw.

1. Diff `skills/coupon-hunter/SKILL.md` against `skills/_reviewed/coupon-hunter.md`.
2. Run Vulnerable. Where will the shoes be delivered?
3. Run Secured. Was the skill loaded? Did the purchase still complete?
4. Custom mode: switch off only `skill_signing`. What stops the address change now?

## 6. Reflection

1. The coupon was not applied in Secured mode. What would you do so shoppers keep the benefit?
2. Why is `allowed-tools` in the skill file not enough on its own?

## 7. Record your finding

```bash
python -m shop.cli finding --module 4 --mode vulnerable \
    --attack "What you tried" --result successful --notes "What happened and why"
python -m shop.cli export
```

**Maps to:** OWASP LLM03; supply-chain integrity for agent skills. Solutions: [instructor/SOLUTIONS.md](../instructor/SOLUTIONS.md).
