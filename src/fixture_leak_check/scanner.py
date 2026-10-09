"""Value-free scans for common fixture leaks.

Findings intentionally contain only a one-based line number and a pattern
kind. Matched text is never included in the result.
"""

from __future__ import annotations

import re


_EMAIL = re.compile(
    r"(?<![A-Za-z0-9.!#$%&'*+/=?^_`{|}~-])"
    r"[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+"
    r"@"
    r"[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?"
    r"(?:\.[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?)+"
    r"(?![A-Za-z0-9_-])"
)
_PAYMENT_CARD = re.compile(r"(?<![A-Za-z0-9])(?:[0-9][ -]?){12,18}[0-9](?![A-Za-z0-9])")
_API_TOKEN = re.compile(r"(?<![A-Za-z0-9])(?:sk|rk|pk)-[A-Za-z0-9_-]{20,}(?![A-Za-z0-9_-])")


def _passes_luhn(digits: str) -> bool:
    total = 0
    parity = len(digits) % 2
    for index, char in enumerate(digits):
        value = ord(char) - ord("0")
        if index % 2 == parity:
            value *= 2
            if value > 9:
                value -= 9
        total += value
    return total % 10 == 0


def scan_text(text: str) -> list[dict]:
    """Return line/kind findings for supported patterns, without matched values."""
    findings: set[tuple[int, str]] = set()

    for kind, pattern in (("email", _EMAIL), ("api_token", _API_TOKEN)):
        for match in pattern.finditer(text):
            line = text.count("\n", 0, match.start()) + 1
            findings.add((line, kind))

    for match in _PAYMENT_CARD.finditer(text):
        digits = match.group().replace(" ", "").replace("-", "")
        if 13 <= len(digits) <= 19 and _passes_luhn(digits):
            line = text.count("\n", 0, match.start()) + 1
            findings.add((line, "payment_card"))

    return [{"line": line, "kind": kind} for line, kind in sorted(findings)]
