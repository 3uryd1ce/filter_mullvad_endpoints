#!/usr/bin/env python3

import json
import argparse
import sys
import re
import random
from typing import TextIO


def parse_cli_arguments() -> argparse.Namespace:
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
    try:
        compiled_regex = re.compile(potential_regex)
    except re.error as err:
        print(f"regexp failed to compile: {err}", file=sys.stderr)
        sys.exit(1)
    return compiled_regex


def init_json_loader(json_file: str | TextIO) -> dict:
    if isinstance(json_file, str):
        with open(json_file, "r", encoding="utf-8") as file:
            json_data = json.load(file)
    else:
        json_data = json.load(json_file)
    return json_data


def filter_relays(cli_args: argparse.Namespace, json_data: dict) -> list:
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
    transformed_relays: dict = {}
    for relay in filtered_relays:
        hostname = relay["hostname"]
        transformed_relays[hostname] = {}
        for relay_key, relay_value in relay.items():
            if relay_key != "hostname":
                transformed_relays[hostname][relay_key] = relay_value
    return transformed_relays


# A-ES (algorithm of Efraimidis and Spirakis)
# https://maxhalford.github.io/blog/weighted-sampling-without-replacement/
def weighted_sample_without_replacement(population, weights, k):
    v = [random.random() ** (1 / w) for w in weights]
    order = sorted(range(len(population)), key=lambda i: v[i])
    return [population[i] for i in order[-k:]]


def get_random_weighted_endpoints(
    transformed_relays: dict, number_of_choices: int
) -> list:
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
