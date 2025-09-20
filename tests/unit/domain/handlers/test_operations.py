import pytest
from src.domain.handlers.operations import identity


@pytest.mark.parametrize("input_value", [True, False])
def test_identity_returns_same_value(input_value):
    # WHEN
    result = identity(input_value)

    # THEN
    assert result == input_value
