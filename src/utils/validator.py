"""Validate external JSON data against a JSON Schema contract."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
from jsonschema.validators import validator_for


def load_json(path: str | Path) -> Any:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def validate(data: Any, schema: dict[str, Any]) -> list[str]:
    """Validate `data` against `schema`, returning human-readable error messages (empty if valid)."""
    validator_cls = validator_for(schema, default=Draft202012Validator)
    validator_cls.check_schema(schema)
    errors = sorted(validator_cls(schema).iter_errors(data), key=lambda e: e.path)
    return [f"{'/'.join(map(str, e.path)) or '<root>'}: {e.message}" for e in errors]


def validate_file(data_path: str | Path, schema_path: str | Path) -> list[str]:
    """Load `data_path` and `schema_path` from disk and validate the former against the latter."""
    return validate(load_json(data_path), load_json(schema_path))


def is_valid(data: Any, schema: dict[str, Any]) -> bool:
    return not validate(data, schema)


def _main() -> int:
    parser = argparse.ArgumentParser(description="Validate a JSON file against a JSON Schema.")
    parser.add_argument("data", help="Path to the JSON file to validate.")
    parser.add_argument("schema", help="Path to the JSON Schema file.")
    args = parser.parse_args()

    errors = validate_file(args.data, args.schema)
    if errors:
        print(f"Invalid: {args.data} does not conform to {args.schema}")
        for error in errors:
            print(f"  - {error}")
        return 1

    print(f"Valid: {args.data} conforms to {args.schema}")
    return 0


if __name__ == "__main__":
    raise SystemExit(_main())
