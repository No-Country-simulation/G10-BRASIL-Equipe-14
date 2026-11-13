import pytest
from pathlib import Path
from src.utils.cases_loader import load_router_cases, load_adapter_cases, load_replay


def test_load_router_cases_success(tmp_path: Path):
    file_path = tmp_path / "router_cases.json"
    file_path.write_text('[{"case": "test_1"}]', encoding="utf-8")

    cases = load_router_cases([file_path])
    assert len(cases) == 1
    assert cases[0]["case"] == "test_1"


def test_load_router_cases_raises_on_non_list(tmp_path: Path):
    file_path = tmp_path / "router_cases.json"
    file_path.write_text('{"case": "test_1"}', encoding="utf-8")

    with pytest.raises(ValueError, match="deve conter uma lista"):
        load_router_cases([file_path])


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
