import csv
import io
import json
from functools import lru_cache
from typing import Any

import requests

from src.config import CSV_DELIMITERS, INPUT_SCHEMA_PATH, N8N_INGESTION_WEBHOOK_URL, N8N_REQUEST_TIMEOUT
from src.validation.schema_validator import load_json, validate_data


def _decode(raw: bytes | str) -> str:
    try:
        return raw.decode("utf-8-sig") if isinstance(raw, bytes) else raw
    except UnicodeDecodeError:
        raise ValueError("o arquivo não está em UTF-8") from None


def parse_json(raw: bytes | str) -> Any:
    try:
        return json.loads(_decode(raw))
    except json.JSONDecodeError as exc:
        raise ValueError(f"JSON inválido (linha {exc.lineno}, coluna {exc.colno}): {exc.msg}") from None


def _detect_delimiter(text: str) -> str:
    def columns(delimiter: str) -> int:
        try:
            return len(next(csv.reader(io.StringIO(text.lstrip()), delimiter=delimiter), []))
        except csv.Error:
            return 0

    return max(CSV_DELIMITERS, key=columns)


def parse_csv(raw: bytes | str) -> list[dict[str, str]]:
    text = _decode(raw)
    try:
        reader = csv.DictReader(io.StringIO(text), delimiter=_detect_delimiter(text))
        if not reader.fieldnames:
            raise ValueError("CSV está vazio")
        if len(set(reader.fieldnames)) != len(reader.fieldnames):
            raise ValueError("CSV inválido: cabeçalho com colunas repetidas")
        records = []
        for row in reader:
            if None in row or None in row.values():
                raise ValueError(f"CSV inválido (linha {reader.line_num}): número de colunas diferente do cabeçalho")
            records.append(row)
    except csv.Error as exc:
        raise ValueError(f"CSV inválido: {exc}") from None
    if not records:
        raise ValueError("CSV sem linhas de dados")
    return records


def parse_input(raw: bytes | str, as_csv: bool) -> Any:
    return parse_csv(raw) if as_csv else parse_json(raw)


def parse_pasted_text_with_format(text: str) -> tuple[Any, bool]:
    try:
        return parse_json(text), False
    except ValueError as json_error:
        try:
            return parse_csv(text), True
        except ValueError as csv_error:
            raise (json_error if text.lstrip().startswith(("{", "[")) else csv_error) from None


def parse_pasted_text(text: str) -> Any:
    return parse_pasted_text_with_format(text)[0]


def _normalize_csv_record(record: dict[str, str]) -> dict[str, Any]:
    normalized: dict[str, Any] = {}
    for key, value in record.items():
        value = value.strip()
        if not value:
            continue
        if value.startswith(("[", "{")):
            try:
                value = json.loads(value)
            except json.JSONDecodeError:
                pass
        normalized[key] = value
    return normalized


@lru_cache(maxsize=1)
def _input_schema() -> dict[str, Any]:
    return load_json(INPUT_SCHEMA_PATH)


def validate_input(data: Any, as_csv: bool = False) -> tuple[Any, list[str]]:
    if as_csv and isinstance(data, list):
        data = [_normalize_csv_record(r) if isinstance(r, dict) else r for r in data]
    schema = _input_schema()
    if not isinstance(data, list):
        return data, validate_data(data, schema)
    if not data:
        return data, ["<root>: a lista está vazia"]
    errors = [
        f"registro {index}: {error}"
        for index, record in enumerate(data, start=1)
        for error in validate_data(record, schema)
    ]
    return data, errors


def send_to_ingestion(data: Any, url: str = N8N_INGESTION_WEBHOOK_URL) -> int:
    return requests.post(url, json=data, timeout=N8N_REQUEST_TIMEOUT).status_code
