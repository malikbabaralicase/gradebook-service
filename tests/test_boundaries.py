from unittest.mock import Mock

import pytest

from errors import ValidationError
from gradebook import add_mark
from models import Assessment, Mark


def fixed_now() -> str:
    return "2026-10-21 09:00:00"


@pytest.mark.parametrize("weight", [0, 100], ids=["weight-0", "weight-100"])
def test_weight_on_the_edge_is_accepted(weight):
    Assessment(id="A9", title="Edge", weight=weight, total=20)


@pytest.mark.parametrize(
    "weight", [-0.01, 100.01], ids=["weight-minus-0.01", "weight-100.01"]
)
def test_weight_outside_the_edge_is_rejected(weight):
    with pytest.raises(ValidationError):
        Assessment(id="A9", title="Edge", weight=weight, total=20)


def test_total_just_above_zero_is_accepted():
    Assessment(id="A9", title="Edge", weight=10, total=0.01)


def test_total_of_zero_is_rejected():
    with pytest.raises(ValidationError):
        Assessment(id="A9", title="Edge", weight=10, total=0)


@pytest.mark.parametrize("score", [0, 20], ids=["score-0", "score-20"])
def test_score_on_the_edge_is_accepted(state, score):
    save = Mock()

    add_mark(
        state,
        Mark(student="S1", assessment="A1", score=score),
        fixed_now,
        save,
    )

    assert len(state["marks"]) == 1
    save.assert_called_once_with()


@pytest.mark.parametrize(
    "score", [-0.01, 20.01], ids=["score-minus-0.01", "score-20.01"]
)
def test_score_outside_the_edge_is_rejected(state, score):
    save = Mock()

    with pytest.raises(ValidationError):
        add_mark(
            state,
            Mark(student="S1", assessment="A1", score=score),
            fixed_now,
            save,
        )

    assert state["marks"] == []
    save.assert_not_called()