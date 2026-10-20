import pytest

from errors import ValidationError
from rules import ensure_weight_fits


def test_empty_weights_with_new_weight_50_fits():
    ensure_weight_fits([], 50)


def test_weight_exceeding_100_raises_validation_error():
    with pytest.raises(ValidationError, match="100"):
        ensure_weight_fits([60], 50)

def test_existing_weight_60_with_new_weight_40_fits():
    ensure_weight_fits([60], 40)

def test_decimal_weights_totaling_100_fit():
    ensure_weight_fits([9.3, 27.3, 33.7], 29.7)