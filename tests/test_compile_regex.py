#!/usr/bin/env python3

import re
from filter_mullvad_endpoints import compile_regex


def test_compile_regex():
    # Test valid regular expression pattern
    pattern = r"^it-(mil|rom)$"
    assert isinstance(compile_regex(pattern), re.Pattern)

    # Test invalid regular expression pattern
    pattern = r"["
    try:
        compile_regex(pattern)
    except SystemExit as e:
        assert e.code == 1
    else:
        assert False, "Expected SystemExit exception"

    # Test regular expression pattern with special characters
    pattern = r"[a-zA-Z0-9_]+"
    assert isinstance(compile_regex(pattern), re.Pattern)

    # Test regular expression pattern with quantifiers
    pattern = r"\d{3}-\d{3}-\d{4}"
    assert isinstance(compile_regex(pattern), re.Pattern)
