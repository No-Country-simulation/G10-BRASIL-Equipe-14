
import json
from pathlib import Path

import pytest
from jsonschema import validate

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = json.loads((ROOT / "data/schemas/input_schema.json").read_text(encoding="utf-8"))
FIXTURES = sorted((ROOT / "data/fixtures").glob("*.json"))


@pytest.mark.parametrize("path", FIXTURES, ids=lambda p: p.name)
def test_fixture_matches_schema(path):
    record = json.loads(path.read_text(encoding="utf-8"))
    validate(instance=record, schema=SCHEMA)
