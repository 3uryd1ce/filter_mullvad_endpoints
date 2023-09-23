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
    population = range(1, 201)
    weights = range(1, 201)
    k = 50

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
