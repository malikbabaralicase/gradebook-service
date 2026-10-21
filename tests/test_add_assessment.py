
from unittest.mock import Mock

import pytest

from errors import ConflictError, ValidationError
from gradebook import add_assessment


def test_valid_assessment_is_stored_and_saved_once(state):
    save = Mock()
    assessment = {
        "id": "A3",
        "title": "Coursework",
        "weight": 20,
        "total": 10,
    }

    add_assessment(state, assessment, save)

    assert state["assessments"]["A3"] == assessment
    save.assert_called_once_with()


def test_assessment_over_100_is_not_stored_or_saved(state):
    save = Mock()
    assessment = {
        "id": "A3",
        "title": "Coursework",
        "weight": 61,
        "total": 10,
    }

    with pytest.raises(ValidationError):
        add_assessment(state, assessment, save)

    assert "A3" not in state["assessments"]
    save.assert_not_called()


def test_duplicate_assessment_id_raises_conflict_and_is_not_saved(state):
    save = Mock()
    assessment = {
        "id": "A1",
        "title": "Duplicate Quiz",
        "weight": 20,
        "total": 10,
    }

    with pytest.raises(ConflictError):
        add_assessment(state, assessment, save)

    assert state["assessments"]["A1"]["name"] == "Quiz"
    save.assert_not_called()
