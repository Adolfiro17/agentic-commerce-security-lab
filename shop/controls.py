"""The security controls the lab can switch on and off.

In Secured mode every control is on. Each module's Vulnerable mode switches off
only the controls that module is about, so the rest keep working and you can
see defence in depth.
"""
from __future__ import annotations

SPEND_POLICY = "spend_policy"            # purchases checked against the signed intent mandate
CONSENT = "consent"                      # anything outside the intent needs the user's cart approval
MANDATE_BINDING = "mandate_binding"      # cart approval bound to one exact cart, single use
PROVENANCE = "provenance"                # retrieval limited to verified merchants
MCP_PINNING = "mcp_pinning"              # MCP tool manifests pinned to the reviewed hash
SKILL_SIGNING = "skill_signing"          # skills load only if they match the reviewed hash
SKILL_PERMISSIONS = "skill_permissions"  # an active skill may only use its declared tools
AGENT_IDENTITY = "agent_identity"        # know-your-agent: verified counterparty and payee
TOKEN_SCOPE = "token_scope"              # payment tokens bound to merchant and amount, single use
DATA_MINIMISATION = "data_minimisation"  # personal data and credentials kept out of agent context
EGRESS = "egress"                        # outbound allow-list
AUDIT_INTEGRITY = "audit_integrity"      # append-only, hash-chained audit log

ALL = frozenset({SPEND_POLICY, CONSENT, MANDATE_BINDING, PROVENANCE, MCP_PINNING, SKILL_SIGNING,
                 SKILL_PERMISSIONS, AGENT_IDENTITY, TOKEN_SCOPE, DATA_MINIMISATION, EGRESS,
                 AUDIT_INTEGRITY})

DESCRIPTIONS = {
    SPEND_POLICY: "Purchases checked against the signed intent mandate (category and budget)",
    CONSENT: "Anything outside the intent mandate needs the account holder's cart approval",
    MANDATE_BINDING: "Cart approval bound to one exact cart, single use",
    PROVENANCE: "Product retrieval limited to verified merchants",
    MCP_PINNING: "MCP tool manifests pinned to the reviewed hash",
    SKILL_SIGNING: "Skills load only if they match the reviewed hash",
    SKILL_PERMISSIONS: "An active skill may only use the tools it declared",
    AGENT_IDENTITY: "Know your agent: verified counterparty agent and payee",
    TOKEN_SCOPE: "Payment tokens bound to merchant and amount, single use",
    DATA_MINIMISATION: "Personal data and payment credentials kept out of agent context",
    EGRESS: "Outbound allow-list",
    AUDIT_INTEGRITY: "Append-only, hash-chained audit log",
}
