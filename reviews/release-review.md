# Independent release review: Fixture Leak Check v0.1.0

**Recommendation: PASS**

**Reviewed PR head:** `87f24dc97408a8ba90ba1f63d73226643bfbb52c` (`feat/fixture-leak-check-v0.1.0`). This review applies to that exact code head only.

## Release gate

The implementation meets the frozen narrow contract at the reviewed head. It reads one UTF-8 file as text without parsing JSONL and reports only one-based line numbers and detector kinds. Findings are deduplicated by line and kind, then sorted by line and kind. The CLI emits compact JSON and does not echo matched values, source lines, input paths, or exception details in the exercised cases. Exit status is `0` for clear input, `1` for findings, and `2` for invalid input or CLI misuse.

The three detectors match the stated scope: email-shaped text; 13–19 digit card-shaped values, optionally separated with spaces or hyphens, accepted only when Luhn-valid; and `sk-`, `rk-`, or `pk-` tokens with at least 20 URL-safe suffix characters. The package has no runtime third-party dependencies; runtime imports are from Python's standard library. Source inspection found no network or model calls. The check is explicitly incomplete and is neither redaction nor a privacy or publication guarantee.

## Verification evidence

- Confirmed local `HEAD` and PR #5's `headRefOid` both equal `87f24dc97408a8ba90ba1f63d73226643bfbb52c` before review. PR #5 is [Hardik-S/fixture-leak-check#5](https://github.com/Hardik-S/fixture-leak-check/pull/5).
- Created a fresh temporary venv with Python 3.13.1 and installed `.[test]` from the checkout using `python -m pip install --disable-pip-version-check '.[test]'`. Installation and wheel build succeeded.
- Prepended that venv's `Scripts` directory to `PATH`; `python -m pytest -q` completed with **17 passed**. The suite therefore exercised its installed-console-script cases as well as module cases. The installed `fixture-leak-check --help` also returned 0.
- Ran synthetic end-to-end probes against the installed console script. Verified clear output/exit 0; findings output/exit 1; missing-argument and invalid UTF-8 output/exit 2; empty stderr and no path, matched value, or source-line echo; mixed and individual LF, CR, and CRLF line numbering; finding sort order and deduplication; Luhn-valid separated values at every length from 13 through 19; all three token prefixes at the 20-character suffix boundary and rejection at 19; and adversarial email, Luhn, card-length, token-prefix, token-length, and token-boundary near misses.
- Queried current PR checks with `gh pr checks 5 --repo Hardik-S/fixture-leak-check`. All eight matrix check runs passed across `ubuntu-latest` and `windows-latest` with Python 3.10 and 3.13 (two successful CI runs each); GitGuardian Security Checks also passed.
- Inspected the public example fixture and documentation; their email, payment-card-shaped value, and token-shaped value are explicitly synthetic placeholders.

All test and probe inputs used in this review were synthetic. No source, tests, examples, workflow, README/launch docs, package configuration, or state files were changed for this review.

## Limits and residual risk

This is a small set of pattern checks, not comprehensive sensitive-data detection. It does not parse JSONL, inspect Git history, redact data, prove the file is safe to publish, or provide a privacy guarantee. It can miss sensitive values outside the supported patterns and can flag harmless text that resembles them. Runtime offline behavior is supported by the standard-library-only implementation and absence of network calls in source; this review did not use an OS-level network sandbox.
