#!/usr/bin/env python3

"""
Tests to make sure that the compile_regex function in
filter_mullvad_endpoints works properly.
"""

import re
from filter_mullvad_endpoints import compile_regex


def test_valid_regex():
    """
    Make sure compile_regex returns a re.Pattern object when a valid
    regex is provided.
    """
    pattern = r"^it-(mil|rom)$"
    assert isinstance(compile_regex(pattern), re.Pattern)


def test_invalid_regex():
    """
    Make sure compile_regex throws an exception when an invalid
    regex is provided.
    """
    pattern = r"["
    try:
        compile_regex(pattern)
    except SystemExit as e:
        assert e.code == 1
    else:
        assert False, "Expected SystemExit exception"
