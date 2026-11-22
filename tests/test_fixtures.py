
import json
import pytest
from jsonschema import validate
from src.config import FIXTURES_DIR, INPUT_SCHEMA_PATH

SCHEMA = json.loads(
    (INPUT_SCHEMA_PATH).read_text(encoding="utf-8"))
ALL_FIXTURES = sorted((FIXTURES_DIR).glob("*.json"))
NORMALIZED_FIXTURE_NAMES = {"sample_conquista_vaga.json"}
NORMALIZED_FIXTURES = [
    path for path in ALL_FIXTURES if path.name in NORMALIZED_FIXTURE_NAMES
]


@pytest.mark.parametrize("path", NORMALIZED_FIXTURES, ids=lambda p: p.name)
def test_normalized_fixture_matches_input_schema(path):
    record = json.loads(path.read_text(encoding="utf-8"))
    validate(instance=record, schema=SCHEMA)


@pytest.mark.parametrize("path", ALL_FIXTURES, ids=lambda p: p.name)
def test_fixture_is_valid_json(path):
    assert isinstance(json.loads(
        path.read_text(encoding="utf-8-sig")), (dict, list))
