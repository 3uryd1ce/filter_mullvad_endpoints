#!/usr/bin/env python3

"""
Tests to make sure the init_json_loader function in
random_mullvad_endpoints works properly.
"""


from io import StringIO
import json
import sys

import pytest

from random_mullvad_endpoints import init_json_loader


def test_valid_file(tmp_path):
    """Make sure that init_json_loader works with valid files."""
    tmpdir = tmp_path / "subdir"
    tmpdir.mkdir()
    json_file_path = f"{tmpdir}/test.json"
    expected_output = {"key": "value"}
    with open(json_file_path, "w", encoding="utf-8") as file:
        json.dump(expected_output, file)
    assert init_json_loader(json_file_path) == expected_output


def test_valid_file_object():
    """
    Make sure that init_json_loader works with valid file-like
    objects.
    """
    json_data = '{"key": "value"}'
    expected_output = {"key": "value"}
    json_file_object = StringIO(json_data)
    assert init_json_loader(json_file_object) == expected_output


def test_stdin(monkeypatch):
    """
    Make sure that init_json_loader can accept STDIN.
    """
    json_data = '{"key": "value"}'
    expected_output = {"key": "value"}
    monkeypatch.setattr(
        "sys.stdin", StringIO(json_data)
    )
    assert init_json_loader("-") == expected_output


def test_invalid_file():
    """
    Make sure that init_json_loader throws an exception when provided
    an invalid file path.
    """
    invalid_json_file_path = "invalid.json"
    try:
        init_json_loader(invalid_json_file_path)
        assert False, "Expected FileNotFoundError"
    except FileNotFoundError:
        pass


def test_invalid_file_object():
    """
    Make sure that init_json_loader throws an exception when provided
    an invalid file-like object.
    """
    invalid_json_data = '{"key": "value"'
    invalid_json_file_object = StringIO(invalid_json_data)
    try:
        init_json_loader(invalid_json_file_object)
        assert False, "Expected JSONDecodeError"
    except json.JSONDecodeError:
        pass


def test_empty_file_object():
    """
    Make sure that init_json_loader throws an exception when provided
    an empty file-like object.
    """
    empty_json_file_object = StringIO()
    try:
        init_json_loader(empty_json_file_object)
        assert False, "Expected JSONDecodeError"
    except json.JSONDecodeError:
        pass


def test_incorrect_type():
    """
    Make sure that init_json_loader throws an exception when provided
    an argument with a type that is incorrect.
    """
    try:
        init_json_loader(123)
        assert False, "Expected AttributeError"
    except AttributeError:
        pass
