# Lab 3: MCP tool poisoning and the rug pull

**Building block:** MCP

> **Deliberately vulnerable.** Fictional data, simulated tools, local only. Do not deploy.

## 1. Your role

You are the AI security engineer for Adolfiro Market. A shopping agent buys on behalf of its users. Your job is to test whether a manipulated agent can exceed what the shopper authorised, and to prove which control stops it.

## 2. The lesson

**A tool description is text the model trusts. Pin what you reviewed.**

The agent connects to a shipping provider's MCP server. Its tool description was changed after it was reviewed, and now tells the agent to post the shopper's address, phone and loyalty ID to an 'analytics' host.

## 3. Learning outcomes

1. Explain tool poisoning and the rug pull
2. Pin a manifest to a reviewed hash
3. Explain why personal data should not sit in agent context

## 4. Run it

| Interface | Command |
| --- | --- |
| Browser | `./start.sh` then choose this module in the sidebar |
| Terminal, vulnerable | `python -m shop.cli run 3 --mode vulnerable` |
| Terminal, secured | `python -m shop.cli run 3 --mode secured` |
| Terminal, your choice | `python -m shop.cli run 3 --disable spend_policy` |

Vulnerable mode for this module switches off: `data_minimisation`, `egress`, `mcp_pinning`. Every other control stays on.

## 5. Tasks

Predict the result before each run, then record what you saw.

1. Run Vulnerable. What personal data left, and where did it go?
2. Run Secured. Why was the manifest rejected? What happened to the shipping quote?
3. Custom mode: switch off only `mcp_pinning`. What still protects the shopper?
4. Open `shop/world.py` and find `pinned_hash`. When should that value be recorded?

## 6. Reflection

1. Quarantining the server cost the agent its shipping quote. Is that the right trade?
2. Which is the stronger control here, pinning or egress, and why keep both?

## 7. Record your finding

```bash
python -m shop.cli finding --module 3 --mode vulnerable \
    --attack "What you tried" --result successful --notes "What happened and why"
python -m shop.cli export
```

**Maps to:** OWASP LLM03; MCP security guidance; McKinsey: MCP as shared context for tools. Solutions: [instructor/SOLUTIONS.md](../instructor/SOLUTIONS.md).
