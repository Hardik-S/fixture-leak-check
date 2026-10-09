from fixture_leak_check.scanner import scan_text


def pairs(text):
    return [(item["line"], item["kind"]) for item in scan_text(text)]


def test_email_shapes_and_near_misses():
    text = "ok user@example.test\nnot-an-email @example.test\nname@localhost"
    assert pairs(text) == [(1, "email")]


def test_luhn_valid_and_invalid_sequences_with_separators():
    # These are payment processor test values; spaces and hyphens are intentional.
    valid = "4242 4242 4242 4242"
    invalid = "4242-4242-4242-4243"
    assert pairs(f"{valid}\n{invalid}") == [(1, "payment_card")]


def test_luhn_length_boundaries_from_13_through_19_digits():
    # Construct deterministic synthetic Luhn values, using no real account data.
    def luhn_value(length):
        payload = "4" + "1" * (length - 2)
        total = 0
        for offset, char in enumerate(reversed(payload)):
            digit = int(char) * (2 if offset % 2 == 0 else 1)
            total += digit - 9 if digit > 9 else digit
        return payload + str((-total) % 10)

    text = "\n".join(luhn_value(length) for length in range(13, 20))
    assert pairs(text) == [(line, "payment_card") for line in range(1, 8)]


def test_token_prefix_and_minimum_length_boundaries():
    accepted = [prefix + "SYNTHETIC_MARKER_123456" for prefix in ("sk-", "rk-", "pk-")]
    rejected = [
        "sk-SYNTHETIC_MARKER_12",  # 19 URL-safe characters after prefix
        "xk-SYNTHETIC_MARKER_123456",  # unsupported prefix
        "sk-contains space in synthetic marker",
    ]
    text = "\n".join(accepted + rejected)
    assert pairs(text) == [(1, "api_token"), (2, "api_token"), (3, "api_token")]


def test_multiple_patterns_deduplicate_by_line_and_kind():
    line = "user@example.test user@example.test 4242-4242-4242-4242"
    text = f"{line}\n{line}"
    assert pairs(text) == [
        (1, "email"),
        (1, "payment_card"),
        (2, "email"),
        (2, "payment_card"),
    ]


def test_unicode_and_newlines_keep_one_based_line_numbers():
    text = "雪\r\nuser@example.test\rtoken: pk-SYNTHETIC_MARKER_123456\n"
    assert pairs(text) == [(2, "email"), (3, "api_token")]


def test_results_are_sorted_and_deterministic():
    text = "pk-SYNTHETIC_MARKER_123456 user@example.test 4242 4242 4242 4242"
    expected = [(1, "api_token"), (1, "email"), (1, "payment_card")]
    assert pairs(text) == expected
    assert pairs(text) == expected


def test_scanner_returns_only_line_and_kind_without_value_echo():
    marker = "synthetic.user@example.test"
    result = scan_text(f"private-source-marker {marker}")
    assert result == [{"line": 1, "kind": "email"}]
    assert all(set(item) == {"line", "kind"} for item in result)
    assert marker not in repr(result)
