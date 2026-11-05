import csv
import io
import json
from typing import Any

import requests

from src.config import N8N_INGESTION_WEBHOOK_URL, N8N_REQUEST_TIMEOUT


CSV_DELIMITERS = ",;\t|"


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


def parse_pasted_text(text: str) -> Any:
    try:
        return parse_json(text)
    except ValueError as json_error:
        try:
            return parse_csv(text)
        except ValueError as csv_error:
            raise (json_error if text.lstrip().startswith(("{", "[")) else csv_error) from None


def send_to_ingestion(data: Any, url: str = N8N_INGESTION_WEBHOOK_URL) -> int:
    return requests.post(url, json=data, timeout=N8N_REQUEST_TIMEOUT).status_code
