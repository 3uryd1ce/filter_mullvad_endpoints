#!/usr/bin/env python3

import re
import sys

import pytest

from filter_mullvad_endpoints import parse_cli_arguments


def test_with_file(monkeypatch):
    monkeypatch.setattr(
        "sys.argv",
        ["script.py", "tests/test.json"],
    )
    arguments = parse_cli_arguments()
    assert arguments.filename == "tests/test.json"


def test_stdin(monkeypatch):
    monkeypatch.setattr(
        "sys.argv",
        ["script.py"],
    )
    arguments = parse_cli_arguments()
    assert arguments.filename == sys.stdin


def test_active_only(monkeypatch):
    monkeypatch.setattr(
        "sys.argv",
        ["script.py", "-a"],
    )
    arguments = parse_cli_arguments()
    assert arguments.ACTIVE_ONLY is True


def test_owned_only(monkeypatch):
    monkeypatch.setattr(
        "sys.argv",
        ["script.py", "-o"],
    )
    arguments = parse_cli_arguments()
    assert arguments.OWNED_ONLY is True


def test_location_regex(monkeypatch):
    regex = "^it-(mil|rom)$"
    monkeypatch.setattr(
        "sys.argv",
        ["script.py", "-l", regex],
    )
    arguments = parse_cli_arguments()
    assert arguments.LOCATION_REGEX == re.compile(regex)


def test_invalid_location_regex(monkeypatch):
    regex = "^it-("
    monkeypatch.setattr(
        "sys.argv",
        ["script.py", "-l", regex],
    )
    with pytest.raises(SystemExit):
        parse_cli_arguments()


def test_provider_regex(monkeypatch):
    regex = "^(31173|DataPacket)$"
    monkeypatch.setattr(
        "sys.argv",
        ["script.py", "-p", regex],
    )
    arguments = parse_cli_arguments()
    assert arguments.PROVIDER_REGEX == re.compile(regex)


def test_invalid_provider_regex(monkeypatch):
    regex = "^(31173|"
    monkeypatch.setattr(
        "sys.argv",
        ["script.py", "-p", regex],
    )
    with pytest.raises(SystemExit):
        parse_cli_arguments()


def test_num_endpoints(monkeypatch):
    monkeypatch.setattr(
        "sys.argv",
        ["script.py", "-n", "10"],
    )
    arguments = parse_cli_arguments()
    assert arguments.NUMBER_OF_ENDPOINTS == 10


def test_invalid_num_endpoints(monkeypatch):
    monkeypatch.setattr(
        "sys.argv",
        ["script.py", "-n", "a"],
    )
    with pytest.raises(SystemExit):
        parse_cli_arguments()
