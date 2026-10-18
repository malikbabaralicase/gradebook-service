
import pytest

import gradebook


@pytest.mark.parametrize(
    "marks, expected",
    [
        pytest.param([], "0", id="no-marks"),
        pytest.param(
            [{"student": "S1", "assessment": "A1", "score": 15}],
            "7.5",
            id="one-mark",
        ),
        pytest.param(
            [{"student": "S1", "assessment": "A1", "score": 20}],
            "10.0",
            id="full-mark",
        ),
        pytest.param(
            [{"student": "S1", "assessment": "A1", "score": 0}],
            "0.0",
            id="zero-mark",
        ),
        pytest.param(
            [
                {"student": "S1", "assessment": "A1", "score": 15},
                {"student": "S1", "assessment": "A2", "score": 40},
            ],
            "31.5",
            id="two-marks",
        ),
    ],
)
def test_percentage_for_different_marks(loaded, marks, expected):
    loaded["marks"].extend(marks)

    assert gradebook.pct("S1") == expected


def test_percentage_ignores_mark_for_missing_assessment(loaded):
    loaded["marks"].append(
        {"student": "S1", "assessment": "A99", "score": 15}
    )

    assert gradebook.pct("S1") == "0"
