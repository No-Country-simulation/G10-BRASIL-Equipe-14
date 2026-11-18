from __future__ import annotations

import json
from pathlib import Path
import pytest
from src.utils.cases_loader import load_router_cases, load_replay, load_adapter_cases


def test_load_router_cases_success(tmp_path):
    file_path = tmp_path / "cases.json"
    data = [{"id": 1, "text": "caso 1"}, {"id": 2, "text": "caso 2"}]
    file_path.write_text(json.dumps(data), encoding="utf-8")

    cases = load_router_cases([file_path])

    assert len(cases) == 2
    assert cases[0]["id"] == 1
    assert cases[1]["text"] == "caso 2"


def test_load_router_cases_invalid_json(tmp_path):
    file_path = tmp_path / "invalid.json"
    file_path.write_text("json inválido", encoding="utf-8")

    with pytest.raises(ValueError, match="Não foi possível carregar"):
        load_router_cases([file_path])


def test_load_router_cases_not_a_list(tmp_path):
    file_path = tmp_path / "not_a_list.json"
    file_path.write_text(json.dumps({"id": 1}), encoding="utf-8")

    with pytest.raises(ValueError, match="O arquivo de casos deve conter uma lista"):
        load_router_cases([file_path])


def test_load_router_cases_item_not_dict(tmp_path):
    file_path = tmp_path / "items_not_dicts.json"
    file_path.write_text(json.dumps([1, 2, 3]), encoding="utf-8")

    with pytest.raises(ValueError, match="Todos os casos devem ser objetos JSON"):
        load_router_cases([file_path])


def test_load_replay_success(tmp_path):
    file_path = tmp_path / "replay.json"
    data = {"outputs": {"caso_1": {"result": "ok"}}}
    file_path.write_text(json.dumps(data), encoding="utf-8")

    outputs = load_replay(file_path)

    assert outputs == {"caso_1": {"result": "ok"}}


def test_load_replay_not_dict(tmp_path):
    file_path = tmp_path / "replay_list.json"
    file_path.write_text(json.dumps([{"outputs": {}}]), encoding="utf-8")

    with pytest.raises(ValueError, match="O arquivo de replay deve conter um objeto JSON."):
        load_replay(file_path)


def test_load_replay_missing_outputs(tmp_path):
    file_path = tmp_path / "replay_no_outputs.json"
    file_path.write_text(json.dumps({"wrong_key": {}}), encoding="utf-8")

    with pytest.raises(ValueError, match="O campo 'outputs' do replay deve ser um objeto."):
        load_replay(file_path)


def test_load_adapter_cases_success(tmp_path: Path):
    file_path = tmp_path / "adapter_cases.json"
    file_path.write_text('{"jobs": [], "items": []}', encoding="utf-8")

    data = load_adapter_cases(file_path)
    assert "jobs" in data
    assert "items" in data


def test_load_adapter_cases_raises_missing_keys(tmp_path: Path):
    file_path = tmp_path / "adapter_cases.json"
    file_path.write_text('{"jobs": []}', encoding="utf-8")

    with pytest.raises(ValueError, match="deve conter a lista 'items'"):
        load_adapter_cases(file_path)
