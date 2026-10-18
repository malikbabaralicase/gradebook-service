
from unittest.mock import Mock

import pytest

from errors import NotFoundError, ValidationError
from gradebook import add_mark
from models import Mark


def fixed_now() -> str:
    return "2026-10-12 09:00:00"


def test_add_mark_records_mark_and_saves(state):
    save = Mock()
    mark = Mark(student="S1", assessment="A1", score=15)

    add_mark(state, mark, fixed_now, save)

    assert state["marks"] == [
        {
            "student": "S1",
            "assessment": "A1",
            "score": 15,
            "at": "2026-10-12 09:00:00",
        }
    ]
    save.assert_called_once_with()


@pytest.mark.parametrize(
    ("mark", "error", "message"),
    [
        (
            Mark(student="S9", assessment="A1", score=10),
            NotFoundError,
            "student not found",
        ),
        (
            Mark(student="S1", assessment="A9", score=10),
            NotFoundError,
            "assessment not found",
        ),
        (
            Mark(student="S1", assessment="A1", score=25),
            ValidationError,
            "score must not exceed total",
        ),
    ],
    ids=["unknown-student", "unknown-assessment", "score-too-high"],
)
def test_add_mark_rejects_invalid_mark(state, mark, error, message):
    save = Mock()
    original_marks = state["marks"].copy()

    with pytest.raises(error, match=message):
        add_mark(state, mark, fixed_now, save)

    assert state["marks"] == original_marks
    save.assert_not_called()
