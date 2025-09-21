import pytest
from src.domain.handlers.operations import (
    description_contains,
    description_does_not_contain,
    identity,
    title_contains,
    title_does_not_contain,
)


@pytest.mark.parametrize("input_value", [True, False])
def test_identity_returns_same_value(input_value):
    # WHEN
    result = identity(input_value)

    # THEN
    assert result == input_value


@pytest.mark.parametrize(
    ("title", "expression", "count", "expected"),
    [
        ("this title has exoplanet", "exoplanet", 1, True),
        ("this title has exoplanet exoplanet", "exoplanet", 2, True),
        ("this title has no match", "exoplanet", 1, False),
        ("this title has one exoplanet", "exoplanet", 2, False),
    ],
)
def test_title_contains(title, expression, count, expected):
    # WHEN
    result = title_contains(True, title, expression, count)

    # THEN
    assert result == expected


@pytest.mark.parametrize(
    ("description", "expression", "count", "expected"),
    [
        ("description with keyword", "keyword", 1, True),
        ("keyword keyword description", "keyword", 2, True),
        ("no match here", "keyword", 1, False),
        ("only one keyword", "keyword", 2, False),
    ],
)
def test_description_contains(description, expression, count, expected):
    # WHEN
    result = description_contains(True, description, expression, count)

    # THEN
    assert result == expected


@pytest.mark.parametrize(
    ("title", "expression", "count", "expected"),
    [
        ("this title has keyword", "keyword", 1, False),
        ("keyword keyword title", "keyword", 2, False),
        ("title without it", "keyword", 1, True),
        ("only one keyword", "keyword", 2, True),
    ],
)
def test_title_does_not_contain(title, expression, count, expected):
    # WHEN
    result = title_does_not_contain(True, title, expression, count)

    # THEN
    assert result == expected


@pytest.mark.parametrize(
    ("description", "expression", "count", "expected"),
    [
        ("this description has keyword", "keyword", 1, False),
        ("keyword keyword description", "keyword", 2, False),
        ("no match here", "keyword", 1, True),
        ("only one keyword", "keyword", 2, True),
    ],
)
def test_description_does_not_contain(description, expression, count, expected):
    # WHEN
    result = description_does_not_contain(True, description, expression, count)

    # THEN
    assert result == expected
