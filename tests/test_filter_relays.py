#!/usr/bin/env python3

import pytest

from filter_mullvad_endpoints import (
    filter_relays,
    init_json_loader,
    parse_cli_arguments,
)


@pytest.fixture
def grab_test_json():
    return init_json_loader("tests/test.json")


def test_no_filter(grab_test_json, monkeypatch):
    test_json = grab_test_json
    monkeypatch.setattr(
        "sys.argv",
        ["script.py"],
    )
    arguments = parse_cli_arguments()
    filtered_relays = filter_relays(arguments, test_json)

    assert len(filtered_relays) == 3


def test_active_relays(grab_test_json, monkeypatch):
    test_json = grab_test_json
    monkeypatch.setattr(
        "sys.argv",
        ["script.py", "-a"],
    )
    arguments = parse_cli_arguments()
    filtered_relays = filter_relays(arguments, test_json)

    assert len(filtered_relays) == 1
    assert filtered_relays[0]["active"] is True


def test_owned_relays(grab_test_json, monkeypatch):
    test_json = grab_test_json
    monkeypatch.setattr(
        "sys.argv",
        ["script.py", "-o"],
    )
    arguments = parse_cli_arguments()
    filtered_relays = filter_relays(arguments, test_json)

    assert len(filtered_relays) == 1
    assert filtered_relays[0]["owned"] is True


def test_relay_one_location(grab_test_json, monkeypatch):
    test_json = grab_test_json
    monkeypatch.setattr(
        "sys.argv",
        ["script.py", "-l", "^it-rom$"],
    )
    arguments = parse_cli_arguments()
    filtered_relays = filter_relays(arguments, test_json)

    assert len(filtered_relays) == 1
    assert filtered_relays[0]["location"] == "it-rom"


def test_relay_two_locations(grab_test_json, monkeypatch):
    test_json = grab_test_json
    monkeypatch.setattr(
        "sys.argv",
        ["script.py", "-l", "^(it-rom|za-jnb)$"],
    )
    arguments = parse_cli_arguments()
    filtered_relays = filter_relays(arguments, test_json)

    assert len(filtered_relays) == 2
    acceptable_locations = ["it-rom", "za-jnb"]
    for relay in filtered_relays:
        assert relay["location"] in acceptable_locations


def test_relay_one_provider(grab_test_json, monkeypatch):
    test_json = grab_test_json
    monkeypatch.setattr(
        "sys.argv",
        ["script.py", "-p", "^DataPacket$"],
    )
    arguments = parse_cli_arguments()
    filtered_relays = filter_relays(arguments, test_json)

    assert len(filtered_relays) == 1
    assert filtered_relays[0]["provider"] == "DataPacket"


def test_relay_two_providers(grab_test_json, monkeypatch):
    test_json = grab_test_json
    monkeypatch.setattr(
        "sys.argv",
        ["script.py", "-p", "^(DataPacket|31173)$"],
    )
    arguments = parse_cli_arguments()
    filtered_relays = filter_relays(arguments, test_json)

    assert len(filtered_relays) == 2
    acceptable_providers = ["DataPacket", "31173"]
    for relay in filtered_relays:
        assert relay["provider"] in acceptable_providers


def test_multiple_filters(grab_test_json, monkeypatch):
    test_json = grab_test_json
    monkeypatch.setattr(
        "sys.argv",
        ["script.py", "-p", "^DataPacket$", "-l", "^za-jnb$"],
    )
    arguments = parse_cli_arguments()
    filtered_relays = filter_relays(arguments, test_json)
    assert len(filtered_relays) == 1
    assert filtered_relays[0]["provider"] == "DataPacket"
    assert filtered_relays[0]["location"] == "za-jnb"
