#!/usr/bin/env python3

"""
Tests to make sure that the weighted_sample_without_replacement function
in filter_mullvad_endpoints works properly.
"""


import pytest
from filter_mullvad_endpoints import weighted_sample_without_replacement


@pytest.fixture
def create_sample():
    """
    Fixture that creates the sample parameters needed for
    weighted_sample_without_replacement to run.
    """
    population = [i for i in range(1, 10)]
    weights = [i for i in range(1, 10)]
    k = 5

    return population, weights, k


def test_sample_size(create_sample):
    """
    Check if there are k items in the sample.
    """
    population, weights, k = create_sample
    sample = weighted_sample_without_replacement(population, weights, k)
    assert len(sample) == k


def test_sample_items(create_sample):
    """
    Check if all items in the sample are present in the population.
    """
    population, weights, k = create_sample
    sample = weighted_sample_without_replacement(population, weights, k)
    for item in sample:
        assert item in population


def test_sample_unique(create_sample):
    """
    Make sure there are no duplicates in the sample. There shouldn't
    be since this is weighted sampling without replacement.
    """
    population, weights, k = create_sample
    sample = weighted_sample_without_replacement(population, weights, k)
    assert len(set(sample)) == k


def test_empty_population(create_sample):
    """
    Make sure that weighted_sample_without_replacement throws an
    exception when provided an empty population.
    """
    _, weights, k = create_sample
    with pytest.raises(ValueError):
        weighted_sample_without_replacement([], weights, k)


def test_empty_weights(create_sample):
    """
    Make sure that weighted_sample_without_replacement throws an
    exception when provided an empty weights list.
    """
    population, _, k = create_sample
    with pytest.raises(ValueError):
        weighted_sample_without_replacement(population, [], k)


def test_empty_k(create_sample):
    """
    Make sure that weighted_sample_without_replacement throws an
    exception when provided 0 for k.
    """
    population, weights, _ = create_sample
    with pytest.raises(ValueError):
        weighted_sample_without_replacement(population, weights, 0)


def test_k_eq_population_len(create_sample):
    """
    Make sure that weighted_sample_without_replacement successfully
    returns all elements in the population when k is equal to the
    length of the entire population.
    """
    population, weights, _ = create_sample
    k = len(population)
    sample = weighted_sample_without_replacement(population, weights, k)
    assert len(sample) == len(population)
    assert set(sample) == set(population)


def test_negative_k(create_sample):
    """
    Make sure that weighted_sample_without_replacement throws an
    exception when k is a negative number.
    """
    population, weights, _ = create_sample
    k = -1
    with pytest.raises(ValueError):
        weighted_sample_without_replacement(population, weights, k)


def test_large_k(create_sample):
    """
    Make sure that weighted_sample_without_replacement successfully
    returns all elements in the population when k is greater than
    the length of the entire population.
    """
    population, weights, _ = create_sample
    k = 5000
    sample = weighted_sample_without_replacement(population, weights, k)
    assert len(sample) == len(population)
    assert set(sample) == set(population)
