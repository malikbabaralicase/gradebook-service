
import json
import pytest
import gradebook


@pytest.fixture
def storage_file(tmp_path, monkeypatch):
    data_file = tmp_path / "gradebook.json"
    monkeypatch.setattr(gradebook, "DATA", str(data_file))
    return data_file

def test_saved_gradebook_loads_unchanged(storage_file, monkeypatch):
    expected = {
        "students": {"S1": {"id": "S1", "name": "Ayesha"}},
        "assessments": {},
        "marks": [],
    }

    monkeypatch.setattr(gradebook, "STATE", expected.copy())
    gradebook.save()

    gradebook.STATE = {}
    gradebook.load()

    assert gradebook.STATE == expected

def test_load_returns_empty_state_when_file_is_missing(storage_file):
    gradebook.load()

    assert gradebook.STATE == {
        "students": {},
        "assessments": {},
        "marks": [],
    }

def test_load_raises_error_for_invalid_json(storage_file):
    storage_file.write_text("{bad", encoding="utf-8")

    with pytest.raises(json.JSONDecodeError):
        gradebook.load()
