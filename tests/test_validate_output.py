import copy
import json

import pytest

from scripts.validate_output import _main, validate_output
from src.config import OUTPUT_SCHEMA_PATH
from src.validation.schema_validator import load_json

SCHEMA = load_json(OUTPUT_SCHEMA_PATH)
VALID_PACKAGE = SCHEMA["examples"][0]


def _write(tmp_path, data, name="pacote.json"):
    path = tmp_path / name
    path.write_text(json.dumps(data), encoding="utf-8")
    return path


def test_schema_example_is_valid(tmp_path):
    assert validate_output(_write(tmp_path, VALID_PACKAGE)) == []


@pytest.mark.parametrize("field", SCHEMA["required"])
def test_missing_required_top_level_field_is_reported(tmp_path, field):
    package = copy.deepcopy(VALID_PACKAGE)
    del package[field]

    errors = validate_output(_write(tmp_path, package))

    assert any(f"'{field}' is a required property" in e for e in errors)


def test_invalid_status_enum_is_reported(tmp_path):
    package = copy.deepcopy(VALID_PACKAGE)
    package["status"] = "done"

    errors = validate_output(_write(tmp_path, package))

    assert any("'done' is not one of" in e for e in errors)


def test_invalid_reference_period_pattern_is_reported(tmp_path):
    package = copy.deepcopy(VALID_PACKAGE)
    package["reference_period"] = "2026-10-13/2026-10-20"

    errors = validate_output(_write(tmp_path, package))

    assert any("reference_period" in e for e in errors)


def test_missing_required_summary_field_is_reported(tmp_path):
    package = copy.deepcopy(VALID_PACKAGE)
    del package["processing_summary"]["main_topics"]

    errors = validate_output(_write(tmp_path, package))

    assert any("'main_topics' is a required property" in e for e in errors)


def test_negative_interaction_count_is_reported(tmp_path):
    package = copy.deepcopy(VALID_PACKAGE)
    package["processing_summary"]["total_interactions"] = -1

    errors = validate_output(_write(tmp_path, package))

    assert any("less than the minimum of 0" in e for e in errors)


def test_mastodon_target_is_accepted(tmp_path):
    package = copy.deepcopy(VALID_PACKAGE)
    package["suggested_content"][0]["target"] = "mastodon"

    assert validate_output(_write(tmp_path, package)) == []


def test_unknown_target_channel_is_reported(tmp_path):
    package = copy.deepcopy(VALID_PACKAGE)
    package["suggested_content"][0]["target"] = "orkut"

    errors = validate_output(_write(tmp_path, package))

    assert any("'orkut' is not one of" in e for e in errors)


def test_empty_content_body_is_reported(tmp_path):
    package = copy.deepcopy(VALID_PACKAGE)
    package["suggested_content"][0]["body"] = ""

    errors = validate_output(_write(tmp_path, package))

    assert any("should be non-empty" in e for e in errors)


def test_missing_storage_bucket_is_reported(tmp_path):
    package = copy.deepcopy(VALID_PACKAGE)
    del package["storage"]["bucket"]

    errors = validate_output(_write(tmp_path, package))

    assert any("'bucket' is a required property" in e for e in errors)


def test_unknown_top_level_property_is_rejected(tmp_path):
    package = copy.deepcopy(VALID_PACKAGE)
    package["linked_batch_id"] = "lote-se-001"  # campo presente nos samples, fora do contrato

    errors = validate_output(_write(tmp_path, package))

    assert any("Additional properties are not allowed" in e for e in errors)


def test_invalid_created_at_format_is_reported(tmp_path):
    package = copy.deepcopy(VALID_PACKAGE)
    package["created_at"] = "21/10/2026"

    errors = validate_output(_write(tmp_path, package))

    assert any("created_at" in e for e in errors)


def test_cli_exit_zero_for_valid_package(tmp_path, capsys):
    assert _main([str(_write(tmp_path, VALID_PACKAGE))]) == 0
    assert "Válido" in capsys.readouterr().out


def test_cli_exit_one_for_invalid_package(tmp_path, capsys):
    package = copy.deepcopy(VALID_PACKAGE)
    del package["package_id"]

    assert _main([str(_write(tmp_path, package))]) == 1
    assert "Inválido" in capsys.readouterr().out


def test_cli_exit_two_for_missing_file(tmp_path, capsys):
    assert _main([str(tmp_path / "nao_existe.json")]) == 2
