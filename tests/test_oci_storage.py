import copy
from datetime import date
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from src.config import OCI_ASSETS_PREFIX
from src.services.oci_storage import iso_week_label, publish_package, sha256_hex

WEEK = "2026-W44"
PREFIX = f"{OCI_ASSETS_PREFIX}/{WEEK}/"
ANTIGO = PREFIX + "pacote-distribuicao-20261026T120000Z.json"


def _valid_payload():
    # Sem o bloco storage: publish_package o preenche antes de validar
    return {
        "package_id": "pkg_2026_w44_001",
        "status": "success",
        "reference_period": "2026-10-26T00:00:00Z/2026-11-02T00:00:00Z",
        "processing_summary": {
            "total_interactions": 1,
            "sources_breakdown": {"stackoverflow": 1},
            "predominant_feeling": "positive",
            "main_topics": ["Teste"],
        },
        "suggested_content": [],
        "created_at": "2026-10-27T12:00:00Z",
    }


@pytest.fixture
def client():
    c = MagicMock()
    c.list_objects.return_value.data.objects = []  # semana sem pacotes
    return c


def _existing(client, name, sha):
    client.list_objects.return_value.data.objects = [SimpleNamespace(name=name)]
    client.head_object.return_value.headers = {"opc-meta-sha256": sha}


def test_objeto_novo_grava_uma_vez(client):
    key = publish_package(_valid_payload(), week=WEEK, client=client)

    assert key.startswith(PREFIX)
    assert key.endswith(".json")
    client.put_object.assert_called_once()
    args, kwargs = client.put_object.call_args
    assert args[2] == key
    assert kwargs["if_none_match"] == "*"


def test_mesmo_conteudo_nao_regrava(client):
    payload = _valid_payload()
    _existing(client, ANTIGO, sha256_hex(payload))  # hash do conteúdo sem storage

    key = publish_package(copy.deepcopy(payload), week=WEEK, client=client)

    client.put_object.assert_not_called()
    assert key == ANTIGO


def test_conteudo_diferente_grava_novo_objeto(client):
    _existing(client, ANTIGO, "sha-antigo")

    key = publish_package(_valid_payload(), week=WEEK, client=client)

    client.put_object.assert_called_once()
    assert key != ANTIGO
    assert client.put_object.call_args.args[2] == key


def test_payload_invalido_nao_chama_cliente(client):
    payload = _valid_payload()
    del payload["package_id"]

    with pytest.raises(ValueError, match="package_id"):
        publish_package(payload, week=WEEK, client=client)

    client.list_objects.assert_not_called()
    client.put_object.assert_not_called()


def test_semana_iso():
    assert iso_week_label(date(2026, 10, 26)) == "2026-W44"
    # virada de ano: 29/12/2025 já pertence à semana 1 de 2026
    assert iso_week_label(date(2025, 12, 29)) == "2026-W01"
