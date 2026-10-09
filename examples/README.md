# Synthetic fixture

From the repository root, run the installed CLI with:

```text
fixture-leak-check examples/synthetic-fixture.jsonl
```

This intentionally reports synthetic email, payment processor test-number, and
API-token-shaped examples. A findings result exits with status 1. The fixture
contains no real personal or credential data.
