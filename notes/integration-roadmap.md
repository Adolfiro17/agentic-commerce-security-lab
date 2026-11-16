# Integration Roadmap: From Simulators to Real Components

The lab runs offline so anyone can use it with one command. This note records how each simulator
maps to a real component. **None of these integrations is included or tested yet.**

| Simulator | Real component | What to build | Security note |
| --- | --- | --- | --- |
| Mock model in `shop/lab.py` | A hosted or local LLM | A planner that returns proposed tool calls | Keep it behind the gateway; never give it credentials |
| Keyword search | Embeddings and a vector store | Ingestion with merchant verification labels | Filter by provenance at retrieval time |
| `list_mcp_tools` | A real MCP client and server | Fetch manifests, hash and compare before loading | Re-review on any change; authenticate the server |
| `skills/` and the registry | A signed skill registry | Signatures over skill contents, verified on load | Enforce declared tools in the gateway |
| `MandateService` | Mandates signed with user-held keys | Signing on a device the agent cannot reach | The agent must never hold the signing key |
| `IdentityService` | An agent registry or identity provider | Verify agent credentials and registered payees | Agents cannot write to the registry |
| `PaymentNetwork` | A payment sandbox with network tokens | Mint per-transaction tokens bound to merchant and amount | Card data never enters model context |

Keep the offline mode as the default and keep `./start.sh matrix` passing. An integration is
finished only when the same attacks are still blocked with it switched on.
