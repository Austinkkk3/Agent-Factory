"""
Guardrails for AP Orchestrator system.
These are Python @tool functions that act as input/output guards.
They are called by agents via instructions, or wired as pre/post processors.
"""
import re
from ibm_watsonx_orchestrate.agent_builder.tools import tool


# PII patterns
_PII_PATTERNS = [
    (r'\b\d{3}-\d{2}-\d{4}\b', '[SSN-REDACTED]'),                          # SSN
    (r'\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b', '[CARD-REDACTED]'),      # Credit card
    (r'\b[A-Z]{2}\d{6}[A-Z]?\b', '[PASSPORT-REDACTED]'),                   # Passport
    (r'\b\d{9,12}\b(?=.*account)', '[ACCOUNT-REDACTED]'),                   # Account numbers
    (r'(?i)\b(ssn|sin|tax.?id|passport|credit.?card)\s*[:\-]?\s*[\w\-]+', '[PII-REDACTED]'),
]

# Prompt injection patterns
_INJECTION_PATTERNS = [
    r'(?i)ignore\s+(all\s+)?(previous|prior|above)\s+instructions?',
    r'(?i)disregard\s+(all\s+)?(previous|prior|above)',
    r'(?i)you\s+are\s+now\s+a\s+different',
    r'(?i)pretend\s+(you\s+are|to\s+be)',
    r'(?i)act\s+as\s+(if\s+you\s+are|a\s+different)',
    r'(?i)jailbreak',
    r'(?i)system\s*prompt\s*:',
    r'(?i)new\s+instructions?\s*:',
    r'(?i)override\s+(all\s+)?instructions?',
    r'(?i)approve\s+all\s+invoices',
    r'(?i)bypass\s+(security|guardrail|policy|approval)',
]

# Off-scope topics for AP system
_OFF_SCOPE_PATTERNS = [
    r'(?i)\bweather\b',
    r'(?i)\bstock\s+(price|market)\b',
    r'(?i)\bsports?\b',
    r'(?i)\brecipe\b',
    r'(?i)\bjoke\b',
    r'(?i)\bpolitics?\b',
    r'(?i)tell\s+me\s+about\s+(?!invoice|vendor|payment|po|purchase)',
]


@tool
def pii_redact(text: str) -> dict:
    """Scan text for PII (SSN, card numbers, account numbers, tax IDs) and redact them. Returns cleaned text and a flag indicating whether redaction occurred."""
    redacted = text
    found = []
    for pattern, replacement in _PII_PATTERNS:
        new_text, count = re.subn(pattern, replacement, redacted)
        if count > 0:
            found.append(pattern)
            redacted = new_text
    return {
        "redacted_text": redacted,
        "pii_found": len(found) > 0,
        "redaction_count": len(found)
    }


@tool
def injection_filter(text: str) -> dict:
    """Detect prompt injection and jailbreak attempts in input text. Returns whether the input is safe to process."""
    for pattern in _INJECTION_PATTERNS:
        if re.search(pattern, text):
            return {
                "is_safe": False,
                "blocked": True,
                "reason": "Prompt injection or jailbreak attempt detected",
                "matched_pattern": pattern,
                "audit_event": "GUARDRAIL_INJECTION_BLOCK"
            }
    return {
        "is_safe": True,
        "blocked": False,
        "reason": "No injection patterns detected"
    }


@tool
def scope_filter(text: str) -> dict:
    """Check whether the input is within scope for the AP Invoice system. Blocks off-topic queries."""
    for pattern in _OFF_SCOPE_PATTERNS:
        if re.search(pattern, text):
            return {
                "in_scope": False,
                "blocked": True,
                "reason": "Query is outside the scope of the AP Invoice Exception Handling system. This system processes invoices, POs, and vendor payments only.",
                "audit_event": "GUARDRAIL_SCOPE_BLOCK"
            }
    return {
        "in_scope": True,
        "blocked": False,
        "reason": "Query is within AP system scope"
    }


@tool
def output_schema_validator(response: dict) -> dict:
    """Validate that an agent response contains the required fields for a valid AP disposition. Returns validation result."""
    required = ["disposition"]
    missing = [f for f in required if f not in response]
    
    valid_dispositions = {"auto_approve", "review", "escalate", "fraud_escalate", "blocked", "validation_failure"}
    disposition = response.get("disposition", "")
    
    if missing:
        return {
            "valid": False,
            "reason": f"Response missing required fields: {', '.join(missing)}",
            "audit_event": "GUARDRAIL_OUTPUT_SCHEMA_FAIL"
        }
    
    if disposition not in valid_dispositions:
        return {
            "valid": False,
            "reason": f"Invalid disposition value '{disposition}'. Must be one of: {valid_dispositions}",
            "audit_event": "GUARDRAIL_OUTPUT_INVALID_DISPOSITION"
        }
    
    return {
        "valid": True,
        "reason": "Response schema is valid"
    }
