# Launch checklist

1. Install the project from its checkout with `python -m pip install .`.
2. Run `fixture-leak-check --help` to confirm the command is available.
3. Scan the intended UTF-8 JSONL dataset with `fixture-leak-check DATASET.jsonl`.
4. Check the exit code: `0` means no supported patterns were found, `1` means findings need review, and `2` means the input or invocation was invalid.
5. Treat a clear result only as a narrow pattern check. Review the data and use your normal release safeguards; this tool does not redact content or guarantee privacy.

The command emits one JSON line. For findings, it includes only line number and category (`email`, `payment_card`, or `api_token`). Missing, unreadable, non-UTF-8 input and CLI misuse produce `{"status":"invalid_input"}` without echoing the path or exception details.

Use synthetic fixtures for demos and documentation. The scan runs locally with the Python standard library and does not parse JSONL, contact a network service, or inspect Git history.
