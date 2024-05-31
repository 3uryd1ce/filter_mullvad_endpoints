#!/usr/bin/env python3
# Copyright (c) 2023-2024 Ashlen <dev@anthes.is>
#
# Permission to use, copy, modify, and distribute this software for
# any purpose with or without fee is hereby granted, provided that
# the above copyright notice and this permission notice appear in all
# copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL
# WARRANTIES WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE
# AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL
# DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE, DATA
# OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER
# TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR
# PERFORMANCE OF THIS SOFTWARE.

"""
Receives a JSON file or standard input produced by this API.
https://api.mullvad.net/public/relays/wireguard/v2

Then, filters out the WireGuard endpoints based on user provided
criteria. Performs weighted sampling without replacement to gather
a list of random endpoints. Prints out the hostnames of those
selected endpoints, one per line.
"""

import argparse
import copy
import json
import random
import re
import sys
import typing


def parse_cli_arguments() -> argparse.Namespace:
    """
    Parses command line arguments and returns a Namespace object
    containing the parsed values.

    Returns:
        argparse.Namespace:
        A Namespace object containing the parsed values.
    """
    argparser = argparse.ArgumentParser()
    argparser.add_argument(
        "filename",
        nargs="?",
        default=sys.stdin,
    )
    argparser.add_argument(
        "-a",
        help="Only select active Mullvad endpoints.",
        action="store_true",
        dest="ACTIVE_ONLY",
    )
    argparser.add_argument(
        "-o",
        help="Only select Mullvad endpoints that are owned by Mullvad.",
        action="store_true",
        dest="OWNED_ONLY",
    )
    argparser.add_argument(
        "-l",
        help="Only include locations that match the given regular expression.",
        dest="LOCATION_REGEX",
        metavar="LOCATION_REGEX",
    )
    argparser.add_argument(
        "-p",
        help="Only include providers that match the given regular expression.",
        dest="PROVIDER_REGEX",
        metavar="PROVIDER_REGEX",
    )
    argparser.add_argument(
        "-n",
        help="Number of matching endpoints to return (5 by default).",
        dest="NUMBER_OF_ENDPOINTS",
        metavar="NUMBER_OF_ENDPOINTS",
        type=int,
        default=5,
    )
    argparser.add_argument(
        "-N",
        help="Only print hostnames, rather than the filtered JSON.",
        dest="PRINT_HOSTNAMES_ONLY",
        action="store_true",
    )

    arguments = argparser.parse_args()

    if arguments.LOCATION_REGEX:
        try:
            arguments.LOCATION_REGEX = re.compile(arguments.LOCATION_REGEX)
        except re.error as err:
            print(f"-l regexp failed to compile: {err}", file=sys.stderr)
            sys.exit(1)

    if arguments.PROVIDER_REGEX:
        try:
            arguments.PROVIDER_REGEX = re.compile(arguments.PROVIDER_REGEX)
        except re.error as err:
            print(f"-p regexp failed to compile: {err}", file=sys.stderr)
            sys.exit(1)

    return arguments


def init_json_loader(json_file: str | typing.TextIO) -> dict:
    """
    Loads a JSON file and returns its contents as a mapping.

    Args:
        json_file (str | typing.TextIO):
        The path to the JSON file or file-like object containing
        the JSON data.

    Returns:
        dict:
        A JSON object that holds the contents of the JSON file.
    """
    if json_file == "-":
        json_file = sys.stdin

    if isinstance(json_file, str):
        with open(json_file, encoding="utf-8") as file:
            json_data = json.load(file)
    else:
        json_data = json.load(json_file)
    return json_data


def is_matching_relay(
    relay: dict,
    cli_args: typing.Optional[argparse.Namespace] = None,
    allowed_hostnames: typing.Optional[typing.Sequence] = None,
) -> bool:
    """
    Determines if a WireGuard relay matches the specified criteria.

    Args:
        relay (dict):
        A dictionary representing a WireGuard relay.

        cli_args (argparse.Namespace, optional):
        Command line arguments. Defaults to None.

        allowed_hostnames (typing.Sequence, optional):
        A sequence of allowed hostnames. Defaults to None.

    Returns:
        bool: True if the relay matches the criteria, False otherwise.

    Notes:
        If no criteria is given, the function will return True for
        any relay.

        If allowed_hostnames is provided, the function checks if
        the relay's hostname is in the list.

        If cli_args is provided, the function applies additional
        criteria to determine if the relay matches. For instance,
        if -l was passed on the command line, the location is
        checked against the provided regular expression.
    """
    if allowed_hostnames and relay["hostname"] not in allowed_hostnames:
        return False

    if cli_args:
        location_regex = cli_args.LOCATION_REGEX
        provider_regex = cli_args.PROVIDER_REGEX

        if cli_args.ACTIVE_ONLY and not relay["active"]:
            return False
        if cli_args.OWNED_ONLY and not relay["owned"]:
            return False
        if location_regex and not location_regex.match(relay["location"]):
            return False
        if provider_regex and not provider_regex.match(relay["provider"]):
            return False

    return True


def create_filtered_json(
    json_data: dict,
    cli_args: typing.Optional[argparse.Namespace] = None,
    allowed_hostnames: typing.Optional[typing.Sequence] = None,
) -> dict:
    """
    Create a filtered version of the given JSON data, based on the
    specified criteria.

    Args:
        json_data (dict):
        The JSON data containing WireGuard relays and their locations.

        cli_args (argparse.Namespace, optional):
        The command line arguments specifying additional filtering
        criteria. Defaults to None.

        allowed_hostnames (Sequence, optional):
        The list of allowed hostnames for filtering. Defaults to
        None.

    Returns:
        filtered_relays (dict):
        The filtered JSON data. The relays and locations are modified
        such that only those that match the specified criteria are
        included.

    Notes:
        The function creates a deep copy of the JSON data to avoid
        modifying the original data.

        If json_data was the only parameter provided, the function
        simply returns json_data as is.
    """
    try:
        filter_opts = [cli_args, allowed_hostnames]
        assert any(opt is not None for opt in filter_opts)
    except AssertionError:
        return json_data

    new_json = copy.deepcopy(json_data)
    new_json["wireguard"]["relays"] = []
    new_json["locations"] = {}

    for relay in json_data["wireguard"]["relays"]:
        if is_matching_relay(relay, cli_args, allowed_hostnames):
            new_json["wireguard"]["relays"].append(relay)
            place = relay["location"]
            new_json["locations"][place] = json_data["locations"][place]

    return new_json


# A-ES (algorithm of Efraimidis and Spirakis)
# https://maxhalford.github.io/blog/weighted-sampling-without-replacement/
def weighted_sample_without_replacement(
    population: typing.Sequence, weights: typing.Sequence[int], k: int
) -> typing.Sequence:
    """
    This function performs weighted sampling without replacement using
    the A-ES algorithm of Efraimidis and Spirakis.

    Args:
        population (typing.Sequence):
        A sequence of items to sample from.

        weights (typing.Sequence[int]):
        A sequence of weights corresponding to each item in the population.
        The weights must be integers.

        k (int):
        The number of items to sample from the population.

    Returns:
        typing.Sequence:
        A sequence of k items sampled from the population.

    The A-ES algorithm works by assigning a value v to each item
    in the population based on its weight. The value v is calculated
    as the inverse of the weight raised to the power of the random
    number generated between 0 and 1. The items are then sorted in
    ascending order based on their values. The last k items in the
    sorted order are selected as the sampled items.
    """
    if not isinstance(population, typing.Sequence):
        raise TypeError("population must be a Sequence.")

    if not isinstance(weights, typing.Sequence):
        raise TypeError("weights must be a Sequence.")

    if not isinstance(k, int):
        raise TypeError("k must be an integer.")

    if not population:
        raise ValueError("population must not be empty.")

    if not weights:
        raise ValueError("weights must not be empty.")

    if k <= 0:
        raise ValueError("k must be a positive integer greater than zero.")

    if len(population) != len(weights):
        raise ValueError("population and weights must be equal length.")

    v = []
    for weight in weights:
        if not isinstance(weight, int):
            raise TypeError("weights must be integers.")

        # XXX: dumb hack to make the program work with weights less than
        # or equal to 0. The problem is that division by zero is invalid,
        # and weights below 0 screw up the weighting system. A random number
        # between 0 and 1 to a negative power will always be greater than
        # 1. This results in something counterintuitive: a number with
        # a negative weight will actually be prioritized over those with
        # positive weights.
        #
        # Rather than completely failing to use the data, which probably
        # isn't useful... convert everything less than or equal to 0
        # back to 1. This should appear in the documentation so that this
        # limitation is more visible, otherwise people may be expecting
        # this program to handle negative weights in a different way.
        if weight <= 0:
            weight = 1

        v.append(random.random() ** (1 / weight))

    order = sorted(range(len(population)), key=lambda i: v[i])
    return [population[i] for i in order[-k:]]


def get_random_weighted_endpoints(
    filtered_relays: typing.Mapping, number_of_endpoints: int
) -> typing.Sequence:
    """
    Returns a sequence of randomly selected endpoints from a given
    mapping of transformed relays, based on their weights.

    Args:
        transformed_relays (typing.Mapping):
        A mapping containing transformed relays as keys and their
        corresponding weight as values.

        number_of_endpoints (int):
        The number of endpoints to be randomly selected.

    Returns:
        typing.Sequence:
        A sequence of randomly selected endpoints.
    """
    population = []
    weights = []
    for relay in filtered_relays["wireguard"]["relays"]:
        population.append(relay["hostname"])
        weights.append(relay["weight"])

    return weighted_sample_without_replacement(
        population, weights, number_of_endpoints
    )


if __name__ == "__main__":
    args = parse_cli_arguments()

    data = init_json_loader(args.filename)
    filtered_json = create_filtered_json(data, args)
    endpoint_hostnames = get_random_weighted_endpoints(
        filtered_json, args.NUMBER_OF_ENDPOINTS
    )

    if args.PRINT_HOSTNAMES_ONLY:
        for hostname in endpoint_hostnames:
            print(hostname)
        sys.exit(0)

    filtered_json = create_filtered_json(
        filtered_json, allowed_hostnames=endpoint_hostnames
    )
    json.dump(filtered_json, sys.stdout)
    print()
