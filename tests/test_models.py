import math
import pytest

from models import parse_number
from errors import ValidationError
from models import (
    Assessment,
    Mark,
    Student,
    parse_assessment,
    parse_mark,
    parse_number,
    parse_student,
)


def test_numeric_string_accepted():
    result = parse_number("75", "weight")
    assert result == 75.0


def test_text_rejected():
    with pytest.raises(ValidationError):
        parse_number("hello", "weight")


def test_boolean_rejected():
    with pytest.raises(ValidationError):
        parse_number(True, "weight")


def test_nan_rejected():
    with pytest.raises(ValidationError):
        parse_number(math.nan, "weight")


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