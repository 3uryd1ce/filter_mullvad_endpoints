#!/usr/bin/env python3

from filter_mullvad_endpoints import transform_relays

filtered_relays = [
    {
        "hostname": "se-sto-wg-014",
        "location": "se-sto",
        "active": False,
        "owned": True,
        "provider": "31173",
        "ipv4_addr_in": "185.195.233.68",
        "include_in_country": True,
        "weight": 100,
        "public_key": "V6RHmYEXDDXvCPZENmhwk5VEn6KgSseTFHw/IkXFzGg=",
        "ipv6_addr_in": "2a03:1b20:4:f011::a28f",
    }
]

transformed_relays = {
    "se-sto-wg-014": {
        "location": "se-sto",
        "active": False,
        "owned": True,
        "provider": "31173",
        "ipv4_addr_in": "185.195.233.68",
        "include_in_country": True,
        "weight": 100,
        "public_key": "V6RHmYEXDDXvCPZENmhwk5VEn6KgSseTFHw/IkXFzGg=",
        "ipv6_addr_in": "2a03:1b20:4:f011::a28f",
    }
}


def test_transform_relays():
    """
    Ensure that transform_relays transforms a sequence of relay
    mappings into a nested mapping structure.
    """
    assert transform_relays(filtered_relays) == transformed_relays
