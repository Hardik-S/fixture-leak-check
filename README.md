# Fixture Leak Check

Fixture Leak Check is a local command for spotting a few sensitive-looking patterns in one UTF-8 JSONL fixture before publication. It reports only line numbers and detector kinds; it never prints the input path, source lines, or matched values.

## Quick start

Install from this checkout, then scan a dataset:

```sh
python -m pip install .
fixture-leak-check DATASET.jsonl
```

The command reads the file as UTF-8. It does not parse the JSONL records. Output is one JSON line, suitable for scripts:

```json
{"status":"clear","findings":[]}
```

If patterns are found, the output contains their line number and category only, for example:

```json
{"status":"findings","findings":[{"line":1,"kind":"email"}]}
```

Exit codes are `0` for clear, `1` when findings exist, and `2` for missing, unreadable, or non-UTF-8 input and command misuse. `python -m fixture_leak_check --help` displays the concise command help.

## What it checks

The scanner has three narrow detectors:

- `email`: email-shaped text, such as the synthetic `person@example.test`.
- `payment_card`: a 13–19 digit sequence that passes the Luhn checksum.
- `api_token`: strings with common `sk-`, `rk-`, or `pk-` prefixes and token-shaped suffixes. Documentation and examples use synthetic placeholders only.

These patterns are incomplete and can miss sensitive information or flag harmless text. This tool does not redact data and provides no privacy or publication guarantee. Review the fixture and your release process separately. It scans only the supplied file; it does not inspect Git history.

## Runtime and data handling

The installed command uses only the Python standard library at runtime. Scanning is offline: it makes no network or model calls. The package reads the selected file locally and emits no file contents, matched values, file path, or exception details.

Keep fixtures and examples synthetic. Never use this check as the sole control for handling real personal data, credentials, or payment information.
