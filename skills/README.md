# Skills

A skill is a folder with a `SKILL.md`: instructions plus the tools the skill is allowed to use.
The agent loads a skill's text into its context, so a skill is an instruction channel.

| Path | What it is |
| --- | --- |
| `_reviewed/` | The text that was security-reviewed. The registry pins the hash of these files |
| `price-compare/SKILL.md` | Matches its reviewed copy |
| `coupon-hunter/SKILL.md` | **Tampered on purpose.** A fourth step was added after review. Diff it against `_reviewed/coupon-hunter.md` |

Module 4 shows what happens when the agent loads the tampered skill, and how hash pinning and
declared-tool permissions each stop it.
