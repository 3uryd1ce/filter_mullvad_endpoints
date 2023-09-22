#!/usr/bin/env python3

import json
from io import StringIO
from filter_mullvad_endpoints import init_json_loader


def test_init_json_loader():
    # Test with a JSON file path
    json_file_path = "test.json"
    expected_output = {"key": "value"}
    with open(json_file_path, "w") as file:
        json.dump(expected_output, file)
    assert init_json_loader(json_file_path) == expected_output

    # Test with a file-like object
    json_data = '{"key": "value"}'
    json_file_object = StringIO(json_data)
    assert init_json_loader(json_file_object) == expected_output

    # Test with an invalid JSON file path
    invalid_json_file_path = "invalid.json"
    try:
        init_json_loader(invalid_json_file_path)
        assert False, "Expected FileNotFoundError"
    except FileNotFoundError:
        pass

    # Test with invalid JSON data in a file-like object
    invalid_json_data = '{"key": "value"'
    invalid_json_file_object = StringIO(invalid_json_data)
    try:
        init_json_loader(invalid_json_file_object)
        assert False, "Expected JSONDecodeError"
    except json.JSONDecodeError:
        pass

    # Test with an empty file-like object
    empty_json_file_object = StringIO()
    try:
        init_json_loader(empty_json_file_object)
        assert False, "Expected JSONDecodeError"
    except json.JSONDecodeError:
        pass

    # Test with a non-string and non-file-like object
    try:
        init_json_loader(123)
        assert False, "Expected AttributeError"
    except AttributeError:
        pass
