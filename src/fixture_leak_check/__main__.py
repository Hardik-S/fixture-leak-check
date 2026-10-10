"""Support ``python -m fixture_leak_check``."""

from .cli import main


if __name__ == "__main__":
    raise SystemExit(main())
