from unittest.mock import Mock

import gradebook
from models import Mark


def test_weak_pct_runs_but_checks_nothing(loaded):
    mark = Mark(student="S1", assessment="A1", score=15)
    add_mark_now = "2026-10-21 09:00:00"

    gradebook.add_mark(loaded, mark, lambda: add_mark_now, Mock())
    gradebook.pct("S1")