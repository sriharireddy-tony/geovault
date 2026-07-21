"""Production input/output guardrails for the RAG chatbot."""

from __future__ import annotations

import re
from dataclasses import dataclass, field


INJECTION_PATTERNS = [
    r"ignore\s+(all\s+)?(previous|prior|above)\s+instructions",
    r"disregard\s+(all\s+)?(previous|prior)\s+(rules|instructions)",
    r"you\s+are\s+now\s+(dan|jailbreak|unrestricted)",
    r"system\s*prompt\s*:",
    r"<\s*/?\s*system\s*>",
]

PII_PATTERNS = [
    (r"\b\d{3}-\d{2}-\d{4}\b", "ssn"),
    (r"\b(?:\d[ -]*?){13,19}\b", "card"),
]


@dataclass
class GuardrailResult:
    ok: bool
    reasons: list[str] = field(default_factory=list)
    sanitized_text: str = ""


def check_input(text: str) -> GuardrailResult:
    reasons: list[str] = []
    cleaned = text.strip()
    if not cleaned:
        reasons.append("empty_input")
    if len(cleaned) > 20_000:
        reasons.append("input_too_long")
    lower = cleaned.lower()
    for pat in INJECTION_PATTERNS:
        if re.search(pat, lower, flags=re.IGNORECASE):
            reasons.append("prompt_injection")
            break
    return GuardrailResult(ok=len(reasons) == 0, reasons=reasons, sanitized_text=cleaned)


def check_output(text: str) -> GuardrailResult:
    reasons: list[str] = []
    cleaned = text.strip()
    if not cleaned:
        reasons.append("empty_output")
    # Soft PII flag — do not hard-block by default, but record
    for pat, label in PII_PATTERNS:
        if re.search(pat, cleaned):
            reasons.append(f"possible_pii:{label}")
    # Only fail hard on empty
    hard = [r for r in reasons if r == "empty_output"]
    return GuardrailResult(ok=len(hard) == 0, reasons=reasons, sanitized_text=cleaned)


def redact_pii(text: str) -> str:
    out = text
    for pat, label in PII_PATTERNS:
        out = re.sub(pat, f"[REDACTED:{label}]", out)
    return out
