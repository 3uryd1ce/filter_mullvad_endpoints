#!/usr/bin/env python3

import json

import pytest

from filter_mullvad_endpoints import filter_relays, parse_cli_arguments


test_json = """
{
  "wireguard": {
    "relays": [
      {
        "hostname": "se-sto-wg-014",
        "location": "se-sto",
        "active": false,
        "owned": true,
        "provider": "31173",
        "ipv4_addr_in": "185.195.233.68",
        "include_in_country": true,
        "weight": 100,
        "public_key": "V6RHmYEXDDXvCPZENmhwk5VEn6KgSseTFHw/IkXFzGg=",
        "ipv6_addr_in": "2a03:1b20:4:f011::a28f"
      },
      {
        "hostname": "it-rom-wg-001",
        "location": "it-rom",
        "active": false,
        "owned": false,
        "provider": "c1vhosting",
        "ipv4_addr_in": "152.89.170.112",
        "include_in_country": true,
        "weight": 100,
        "public_key": "cGBz0+Uxqt82THeufy8deCQjAGo8fNoNISnTsKCz3VA=",
        "ipv6_addr_in": "2a05:4140:15::a01f"
      },
      {
        "hostname": "za-jnb-wg-002",
        "location": "za-jnb",
        "active": true,
        "owned": false,
        "provider": "DataPacket",
        "ipv4_addr_in": "154.47.30.143",
        "include_in_country": true,
        "weight": 100,
        "public_key": "lTq6+yUYfYsXwBpj/u3LnYqpLhW8ZJXQQ19N/ybP2B8=",
        "ipv6_addr_in": "2a02:6ea0:f207::a02f"
      }
    ]
  }
}
"""


def test_no_filter(monkeypatch):
    json_as_dict = json.loads(test_json)
    monkeypatch.setattr(
        "sys.argv",
        ["script.py"],
    )
    arguments = parse_cli_arguments()
    filtered_relays = filter_relays(arguments, json_as_dict)

    assert len(filtered_relays) == 3


def test_active_relays(monkeypatch):
    json_as_dict = json.loads(test_json)
    monkeypatch.setattr(
        "sys.argv",
        ["script.py", "-a"],
    )
    arguments = parse_cli_arguments()
    filtered_relays = filter_relays(arguments, json_as_dict)

    assert len(filtered_relays) == 1
    assert filtered_relays[0]["active"] is True


def test_owned_relays(monkeypatch):
    json_as_dict = json.loads(test_json)
    monkeypatch.setattr(
        "sys.argv",
        ["script.py", "-o"],
    )
    arguments = parse_cli_arguments()
    filtered_relays = filter_relays(arguments, json_as_dict)

    assert len(filtered_relays) == 1
    assert filtered_relays[0]["owned"] is True


def test_relay_one_location(monkeypatch):
    json_as_dict = json.loads(test_json)
    monkeypatch.setattr(
        "sys.argv",
        ["script.py", "-l", "^it-rom$"],
    )
    arguments = parse_cli_arguments()
    filtered_relays = filter_relays(arguments, json_as_dict)

    assert len(filtered_relays) == 1
    assert filtered_relays[0]["location"] == "it-rom"


def test_relay_two_locations(monkeypatch):
    json_as_dict = json.loads(test_json)
    monkeypatch.setattr(
        "sys.argv",
        ["script.py", "-l", "^(it-rom|za-jnb)$"],
    )
    arguments = parse_cli_arguments()
    filtered_relays = filter_relays(arguments, json_as_dict)

    assert len(filtered_relays) == 2
    acceptable_locations = ["it-rom", "za-jnb"]
    for relay in filtered_relays:
        assert relay["location"] in acceptable_locations


def test_relay_one_provider(monkeypatch):
    json_as_dict = json.loads(test_json)
    monkeypatch.setattr(
        "sys.argv",
        ["script.py", "-p", "^DataPacket$"],
    )
    arguments = parse_cli_arguments()
    filtered_relays = filter_relays(arguments, json_as_dict)

    assert len(filtered_relays) == 1
    assert filtered_relays[0]["provider"] == "DataPacket"


def test_relay_two_providers(monkeypatch):
    json_as_dict = json.loads(test_json)
    monkeypatch.setattr(
        "sys.argv",
        ["script.py", "-p", "^(DataPacket|31173)$"],
    )
    arguments = parse_cli_arguments()
    filtered_relays = filter_relays(arguments, json_as_dict)

    assert len(filtered_relays) == 2
    acceptable_providers = ["DataPacket", "31173"]
    for relay in filtered_relays:
        assert relay["provider"] in acceptable_providers


def test_multiple_filters(monkeypatch):
    json_as_dict = json.loads(test_json)
    monkeypatch.setattr(
        "sys.argv",
        ["script.py", "-p", "^DataPacket$", "-l", "^za-jnb$"],
    )
    arguments = parse_cli_arguments()
    filtered_relays = filter_relays(arguments, json_as_dict)
    assert len(filtered_relays) == 1
    assert filtered_relays[0]["provider"] == "DataPacket"
    assert filtered_relays[0]["location"] == "za-jnb"
