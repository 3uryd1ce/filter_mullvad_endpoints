#!/usr/bin/env python3

"""
Receives a JSON file or standard input produced by this API.
https://api.mullvad.net/public/relays/wireguard/v2

Then, filters out the WireGuard endpoints based on user provided
criteria. Performs weighted sampling without replacement to gather
a list of random endpoints. Prints out the hostnames of those
selected endpoints, one per line.
"""

import json
import argparse
import sys
import re
import random
from typing import TextIO


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
        help="Number of matching endpoints to return.",
        dest="NUMBER_OF_ENDPOINTS",
        metavar="NUMBER_OF_ENDPOINTS",
        type=int,
    )

    return argparser.parse_args()


def compile_regex(potential_regex: str) -> re.Pattern:
    """
    Compiles a regular expression pattern.

    This function takes a potential regular expression pattern as
    input and compiles it into a regular expression object. If the
    compilation fails, an error message is printed to the standard
    error stream and the program exits with a status code of 1.

    Args:
        potential_regex:
        The potential regular expression pattern to compile.

    Returns:
        re.Pattern:
        The compiled regular expression object.

    Raises:
        re.error:
        If the regular expression pattern is invalid and cannot be
        compiled.
    """
    try:
        compiled_regex = re.compile(potential_regex)
    except re.error as err:
        print(f"regexp failed to compile: {err}", file=sys.stderr)
        sys.exit(1)
    return compiled_regex


def init_json_loader(json_file: str | TextIO) -> dict:
    """
    Loads a JSON file and returns its contents as a dictionary.

    Args:
        json_file:
        The path to the JSON file or a file-like object containing
        the JSON data.

    Returns:
        dict:
        A dictionary containing the contents of the JSON file.
    """
    if isinstance(json_file, str):
        with open(json_file, encoding="utf-8") as file:
            json_data = json.load(file)
    else:
        json_data = json.load(json_file)
    return json_data


def filter_relays(cli_args: argparse.Namespace, json_data: dict) -> list:
    """
    Filters a list of relays based on the provided command line
    arguments and JSON data.

    Parameters:
        cli_args:
        The command line arguments passed to the script.

        json_data:
        The JSON data containing the list of relays.

    Returns:
        filtered_relays:
        The filtered list of relays that match the specified criteria.
        For instance, if a regular expression for location was given
        on the command-line, only the relays with a location that
        matches that regex would be part of the returned list.
    """
    filtered_relays = []

    location_regex = None
    if cli_args.LOCATION_REGEX:
        location_regex = compile_regex(cli_args.LOCATION_REGEX)

    provider_regex = None
    if cli_args.PROVIDER_REGEX:
        provider_regex = compile_regex(cli_args.PROVIDER_REGEX)

    for relay in json_data["wireguard"]["relays"]:
        if cli_args.ACTIVE_ONLY and not relay["active"]:
            continue
        if cli_args.OWNED_ONLY and not relay["owned"]:
            continue
        if location_regex and not location_regex.match(relay["location"]):
            continue
        if provider_regex and not provider_regex.match(relay["provider"]):
            continue

        filtered_relays.append(relay)

    return filtered_relays


def transform_relays(filtered_relays: list) -> dict[str, dict]:
    """
    Transforms a list of relay dictionaries into a nested dictionary
    structure.

    Args:
        filtered_relays:
        A list of relay dictionaries. Each dictionary represents a
        relay and contains key-value pairs.

    Returns:
        dict[str, dict]:
        A nested dictionary structure where the keys are hostnames
        and the values are dictionaries containing relay information.
    """
    transformed_relays: dict = {}
    for relay in filtered_relays:
        transformed_relays["hostname"] = {}
        for relay_key, relay_value in relay.items():
            if relay_key != "hostname":
                transformed_relays["hostname"][relay_key] = relay_value
    return transformed_relays


# A-ES (algorithm of Efraimidis and Spirakis)
# https://maxhalford.github.io/blog/weighted-sampling-without-replacement/
def weighted_sample_without_replacement(
    population: list, weights: list, k: int
) -> list:
    """
    This function performs weighted sampling without replacement using
    the A-ES algorithm of Efraimidis and Spirakis.

    Args:
        population (list):
        A list of items to sample from.

        weights (list):
        A list of weights corresponding to each item in the population.
        The weights must be positive.

        k (int):
        The number of items to sample from the population.

    Returns:
        list:
        A list of k items sampled from the population.

    The A-ES algorithm works by assigning a value v to each item
    in the population based on its weight. The value v is calculated
    as the inverse of the weight raised to the power of the random
    number generated between 0 and 1. The items are then sorted in
    ascending order based on their values. The last k items in the
    sorted order are selected as the sampled items.
    """
    v = [random.random() ** (1 / w) for w in weights]
    order = sorted(range(len(population)), key=lambda i: v[i])
    return [population[i] for i in order[-k:]]


def get_random_weighted_endpoints(
    transformed_relays: dict, number_of_choices: int
) -> list:
    """
    Returns a list of randomly selected endpoints from a given
    dictionary of transformed relays, based on their weights.

    Args:
        transformed_relays (dict):
        A dictionary containing transformed relays as keys and their
        corresponding weight as values.

        number_of_choices (int):
        The number of endpoints to be randomly selected.

    Returns:
        list:
        A list of randomly selected endpoints.
    """
    population = list(transformed_relays.keys())

    weights = []
    for relay, _ in transformed_relays.items():
        weights.append(transformed_relays[relay]["weight"])

    return weighted_sample_without_replacement(
        population, weights, number_of_choices
    )


if __name__ == "__main__":
    args = parse_cli_arguments()

    data = init_json_loader(args.filename)
    relays_as_list = filter_relays(args, data)
    relays_as_dict = transform_relays(relays_as_list)
    endpoints = get_random_weighted_endpoints(
        relays_as_dict, args.NUMBER_OF_ENDPOINTS
    )

    for endpoint in endpoints:
        print(endpoint)
