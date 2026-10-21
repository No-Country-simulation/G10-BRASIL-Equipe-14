import copy
import json
import sys
from pathlib import Path

from src.utils.validator import _main, is_valid, load_json, validate, validate_file

SCHEMA_PATH = Path(__file__).resolve().parent.parent / "data" / "schemas" / "input_schema.json"
SCHEMA = load_json(SCHEMA_PATH)
VALID_RECORD = SCHEMA["examples"][0]


def test_validate_returns_no_errors_for_valid_record():
    assert validate(VALID_RECORD, SCHEMA) == []


def test_validate_reports_missing_required_top_level_property():
    record = copy.deepcopy(VALID_RECORD)
    del record["source"]

    errors = validate(record, SCHEMA)

    assert any("'source' is a required property" in error for error in errors)


def test_validate_reports_invalid_source_enum_value():
    record = copy.deepcopy(VALID_RECORD)
    record["source"] = "twitter"

    errors = validate(record, SCHEMA)

    assert any("'twitter' is not one of" in error for error in errors)


def test_validate_reports_missing_required_interaction_property():
    record = copy.deepcopy(VALID_RECORD)
    del record["interactions"][0]["author"]

    errors = validate(record, SCHEMA)

    assert any("interactions/0" in error and "'author' is a required property" in error for error in errors)


def test_validate_reports_malformed_reference_period():
    record = copy.deepcopy(VALID_RECORD)
    record["reference_period"] = "not-a-period"

    errors = validate(record, SCHEMA)

    assert any("reference_period" in error for error in errors)


def test_validate_rejects_unknown_top_level_property():
    record = copy.deepcopy(VALID_RECORD)
    record["unexpected"] = "nope"

    errors = validate(record, SCHEMA)

    assert any("Additional properties are not allowed" in error for error in errors)


def test_is_valid_true_for_conforming_record():
    assert is_valid(VALID_RECORD, SCHEMA) is True


def test_is_valid_false_for_non_conforming_record():
    assert is_valid({}, SCHEMA) is False


def test_load_json_reads_file(tmp_path):
    path = tmp_path / "data.json"
    path.write_text(json.dumps(VALID_RECORD), encoding="utf-8")

    assert load_json(path) == VALID_RECORD


def test_validate_file_valid(tmp_path):
    data_path = tmp_path / "data.json"
    data_path.write_text(json.dumps(VALID_RECORD), encoding="utf-8")

    assert validate_file(data_path, SCHEMA_PATH) == []


def test_validate_file_invalid(tmp_path):
    data_path = tmp_path / "data.json"
    data_path.write_text(json.dumps({}), encoding="utf-8")

    assert validate_file(data_path, SCHEMA_PATH)


def test_main_exits_zero_and_prints_valid_for_conforming_file(tmp_path, capsys, monkeypatch):
    data_path = tmp_path / "data.json"
    data_path.write_text(json.dumps(VALID_RECORD), encoding="utf-8")
    monkeypatch.setattr(sys, "argv", ["validator.py", str(data_path), str(SCHEMA_PATH)])

    assert _main() == 0
    assert "Valid" in capsys.readouterr().out


def test_main_exits_one_and_prints_errors_for_invalid_file(tmp_path, capsys, monkeypatch):
    data_path = tmp_path / "data.json"
    data_path.write_text(json.dumps({}), encoding="utf-8")
    monkeypatch.setattr(sys, "argv", ["validator.py", str(data_path), str(SCHEMA_PATH)])

    assert _main() == 1
    out = capsys.readouterr().out
    assert "Invalid" in out
    assert "is a required property" in out
