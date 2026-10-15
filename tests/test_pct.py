import pytest
import gradebook

def test_percentage_is_zero_when_student_has_no_marks(monkeypatch):
    # Arrange: create a small gradebook with no marks
    state = {
        "students": {"S1": {"id": "S1", "name": "Ayesha"}},
        "assessments": {},
        "marks": [],
    }

    # Replace the real gradebook state with our test state
    monkeypatch.setattr(gradebook, "STATE", state)

    # Act: calculate S1's percentage
    result = gradebook.pct("S1")

    # Assert: no marks means the percentage is zero
    assert result == "0"

def test_percentage_is_seven_point_five_for_one_mark(monkeypatch):
    # Arrange
    state = {
        "students": {"S1": {"id": "S1", "name": "Ayesha"}},
        "assessments": {
            "A1": {
                "id": "A1",
                "name": "Quiz",
                "weight": 10,
                "total": 20,
            }
        },
        "marks": [
            {"student": "S1", "assessment": "A1", "score": 15}
        ],
    }

    monkeypatch.setattr(gradebook, "STATE", state)

    # Act
    result = gradebook.pct("S1")

    # Assert
    assert result == "7.5"

def test_percentage_ignores_mark_for_missing_assessment(monkeypatch):
    # Arrange
    state = {
        "students": {"S1": {"id": "S1", "name": "Ayesha"}},
        "assessments": {},
        "marks": [
            {"student": "S1", "assessment": "A99", "score": 15}
        ],
    }

    monkeypatch.setattr(gradebook, "STATE", state)

    # Act
    result = gradebook.pct("S1")

    # Assert
    assert result == "0"
