# Fixture Leak Check

An offline, standard-library CLI that flags a few explicit sensitive-looking patterns in one UTF-8 JSONL file. It reports line number and detector kind only; values, line text, and the supplied path are not emitted.

Supported patterns are email-shaped text, Luhn-valid 13–19 digit payment-card-shaped sequences, and common `sk-`, `rk-`, or `pk-` token-shaped strings. This is a narrow pattern check, not comprehensive secret or PII detection, redaction, or a privacy guarantee. It does not parse JSONL, inspect Git history, call a model or network, or use third-party runtime dependencies.

Public examples and tests use synthetic values only.

## Status

The CLI implementation and examples are in progress under the frozen 24-hour acceptance contract.
