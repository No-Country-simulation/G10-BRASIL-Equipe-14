import json
import os
import uuid

import oci
import pytest
from oci.object_storage import ObjectStorageClient

from src.config import OCI_BUCKET_NAME, OCI_NAMESPACE, OCI_ASSETS_PREFIX
from src.services.oci_storage import publish_package

# Só roda com OCI_INTEGRATION=1, para o `uv run pytest` padrão não tocar o bucket
pytestmark = pytest.mark.skipif(
    os.getenv("OCI_INTEGRATION") != "1",
    reason="defina OCI_INTEGRATION=1 para usar o bucket real",
)

WEEK = "2026-W44"


def _payload():
    # package_id único por execução: cada rodada grava conteúdo novo
    return {
        "package_id": f"pkg_teste_{uuid.uuid4().hex[:8]}",
        "status": "success",
        "reference_period": "2026-10-26T00:00:00Z/2026-11-02T00:00:00Z",
        "processing_summary": {
            "total_interactions": 1,
            "sources_breakdown": {"stackoverflow": 1},
            "predominant_feeling": "positive",
            "main_topics": ["Teste integração"],
        },
        "suggested_content": [],
        "created_at": "2026-10-27T12:00:00Z",
    }


@pytest.fixture(scope="module")
def client():
    return ObjectStorageClient(oci.config.from_file())


def test_grava_em_tests_e_nao_toca_ativos(client):
    key = publish_package(_payload(), week=WEEK, client=client, base_prefix="tests")

    assert key.startswith(f"tests/{WEEK}/")
    assert not key.startswith(OCI_ASSETS_PREFIX)

    # relê o objeto e confere o conteúdo gravado
    body = client.get_object(OCI_NAMESPACE, OCI_BUCKET_NAME, key).data.content
    saved = json.loads(body)
    assert saved["storage"]["status"] == "success"
    assert saved["storage"]["object_path"] == key


def test_segunda_chamada_com_mesmo_conteudo_nao_regrava(client):
    payload = _payload()
    first = publish_package(payload, week=WEEK, client=client, base_prefix="tests")
    second = publish_package(payload, week=WEEK, client=client, base_prefix="tests")

    assert second == first
