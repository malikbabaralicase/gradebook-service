
import pytest
import gradebook


def test_percentage_is_zero_when_student_has_no_marks(loaded):
    # Act
    result = gradebook.pct("S1")

    # Assert
    assert result == "0"


def test_percentage_is_seven_point_five_for_one_mark(loaded):
    # Arrange
    loaded["marks"].append(
        {"student": "S1", "assessment": "A1", "score": 15}
    )

    # Act
    result = gradebook.pct("S1")

    # Assert
    assert result == "7.5"


def test_percentage_ignores_mark_for_missing_assessment(loaded):
    # Arrange
    loaded["marks"].append(
        {"student": "S1", "assessment": "A99", "score": 15}
    )

    # Act
    result = gradebook.pct("S1")

    # Assert
    assert result == "0"
