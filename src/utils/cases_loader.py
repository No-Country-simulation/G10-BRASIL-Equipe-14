import json
from pathlib import Path
from typing import Any


def load_router_cases(paths: list[Path]) -> list[dict[str, Any]]:
    cases: list[dict[str, Any]] = []

    for path in paths:
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise ValueError(
                f"Não foi possível carregar {path}: {exc}") from exc

        if not isinstance(data, list):
            raise ValueError(
                f"O arquivo de casos deve conter uma lista: {path}")

        if not all(isinstance(item, dict) for item in data):
            raise ValueError(f"Todos os casos devem ser objetos JSON: {path}")

        cases.extend(data)

    return cases


def load_adapter_cases(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"Não foi possível carregar {path}: {exc}") from exc

    if not isinstance(data, dict):
        raise ValueError("O arquivo de adapters deve conter um objeto JSON.")

    if not isinstance(data.get("jobs"), list):
        raise ValueError("O arquivo de adapters deve conter a lista 'jobs'.")

    if not isinstance(data.get("items"), list):
        raise ValueError("O arquivo de adapters deve conter a lista 'items'.")

    return data


def load_replay(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(
            f"Não foi possível carregar o replay {path}: {exc}") from exc

    if not isinstance(data, dict):
        raise ValueError("O arquivo de replay deve conter um objeto JSON.")

    outputs = data.get("outputs")

    if not isinstance(outputs, dict):
        raise ValueError("O campo 'outputs' do replay deve ser um objeto.")

    return outputs
