"""Command-line entry point for the value-free fixture scan."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import NoReturn

from .scanner import scan_text


class _SafeArgumentParser(argparse.ArgumentParser):
    """Keep argparse errors from printing arguments or paths to stderr."""

    def error(self, message: str) -> NoReturn:
        del message
        _emit({"status": "invalid_input"})
        raise SystemExit(2)


def _emit(payload: dict[str, object]) -> None:
    """Write exactly one compact JSON record to stdout."""
    sys.stdout.write(json.dumps(payload, separators=(",", ":")) + "\n")


def _parser() -> argparse.ArgumentParser:
    parser = _SafeArgumentParser(
        prog="fixture-leak-check",
        description="Check one UTF-8 JSONL fixture for a few sensitive-looking patterns.",
        add_help=True,
    )
    parser.add_argument("dataset", metavar="DATASET.jsonl", help="UTF-8 JSONL file to scan")
    return parser


def main() -> int:
    """Run the scanner and return its documented process status."""
    try:
        args = _parser().parse_args()
        text = Path(args.dataset).read_text(encoding="utf-8")
        scanned = scan_text(text)
        # Emit only the public, value-free fields, even if the scanner carries
        # additional internal metadata in a finding.
        findings = [
            {"line": finding["line"], "kind": finding["kind"]}
            for finding in scanned
        ]
    except Exception:
        # Keep malformed/unreadable input and unexpected scanner failures
        # content-safe; neither exception messages nor paths belong in output.
        _emit({"status": "invalid_input"})
        return 2

    if findings:
        findings.sort(key=lambda finding: (finding["line"], finding["kind"]))
        _emit({"status": "findings", "findings": findings})
        return 1

    _emit({"status": "clear", "findings": []})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
