from unittest.mock import Mock, patch

from hypothesis import given
from hypothesis import strategies as st

import gradebook
from models import Mark


def fixed_now() -> str:
    return "2026-10-21 09:00:00"


@given(
    scores=st.lists(
        st.integers(min_value=0, max_value=20),
        min_size=1,
        max_size=5,
    )
)
def test_percentage_never_exceeds_assessment_weight(scores):
    state = {
        "students": {"S1": {"id": "S1", "name": "Ayesha"}},
        "assessments": {
            "A1": {"id": "A1", "title": "Quiz", "weight": 10, "total": 20}
        },
        "marks": [],
    }
    save = Mock()

    for score in scores:
        gradebook.add_mark(
            state,
            Mark(student="S1", assessment="A1", score=score),
            fixed_now,
            save,
        )

    with patch.object(gradebook, "STATE", state):
        assert float(gradebook.pct("S1")) <= 10