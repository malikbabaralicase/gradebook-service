
import pytest

from models import (
    Assessment,
    Mark,
    Student,
    parse_assessment,
    parse_mark,
    parse_number,
    parse_student,
)
from errors import ValidationError


@pytest.mark.parametrize(
    "value, expected",
    [
        pytest.param("15", 15.0, id="numeric-string"),
        pytest.param(15, 15.0, id="integer"),
        pytest.param("2.5", 2.5, id="decimal-string"),
    ],
)
def test_valid_numbers_are_accepted(value, expected):
    assert parse_number(value, "weight") == expected


@pytest.mark.parametrize(
    "value",
    [
        pytest.param("abc", id="text"),
        pytest.param(True, id="boolean"),
        pytest.param(None, id="none"),
        pytest.param([], id="list"),
        pytest.param("nan", id="nan"),
        pytest.param("inf", id="infinity"),
    ],
)
def test_invalid_numbers_are_rejected(value):
    with pytest.raises(ValidationError):
        parse_number(value, "weight")


def test_zero_assessment_total_rejected():
    with pytest.raises(ValidationError):
        Assessment(
            id="A1",
            title="Midterm",
            weight=50.0,
            total=0.0,
        )


def test_negative_mark_score_rejected():
    student = Student(id="S1", name="Ayesha")
    assessment = Assessment(
        id="A1",
        title="Midterm",
        weight=50.0,
        total=100.0,
    )

    with pytest.raises(ValidationError):
        Mark(
            student=student.id,
            assessment=assessment.id,
            score=-1.0,
        )


def test_missing_field_rejected():
    payload = {"id": "S1"}

    with pytest.raises(ValidationError):
        parse_student(payload)


def test_non_dictionary_payload_rejected():
    payload = []

    with pytest.raises(ValidationError):
        parse_student(payload)


def test_valid_assessment_parsed():
    payload = {
        "id": "A1",
        "title": "Midterm",
        "weight": 50.0,
        "total": 100.0,
    }

    assessment = parse_assessment(payload)

    assert assessment.id == "A1"
    assert assessment.title == "Midterm"
    assert assessment.weight == 50.0
    assert assessment.total == 100.0
