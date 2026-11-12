import json
from types import SimpleNamespace

import oci
import pytest

from scripts.validate_output import fetch_from_bucket, fetch_latest_pacote, validate_output
from src.config import OCI_ASSETS_PREFIX
from src.validation.schema_validator import load_json
from src.config import OUTPUT_SCHEMA_PATH

VALID_PACKAGE = load_json(OUTPUT_SCHEMA_PATH)["examples"][0]
KEY = f"{OCI_ASSETS_PREFIX}/2026-W44/pacote-distribuicao-20261026T120000000000Z.json"


class FakeClient:
    """Cliente falso do bucket: lista, metadados e download configuráveis."""

    def __init__(self, objects=(), content=None, list_error=None, get_error=None):
        self.objects = list(objects)
        self.content = content
        self.list_error = list_error
        self.get_error = get_error
        self.requested_keys = []

    def list_objects(self, namespace, bucket, prefix, **kwargs):
        if self.list_error:
            raise self.list_error
        return SimpleNamespace(data=SimpleNamespace(objects=self.objects))

    def head_object(self, namespace, bucket, name, **kwargs):
        return SimpleNamespace(headers={"opc-meta-sha256": "abc"})

    def get_object(self, namespace, bucket, key, **kwargs):
        self.requested_keys.append(key)
        if self.get_error:
            raise self.get_error
        return SimpleNamespace(data=SimpleNamespace(content=self.content))


def _svc_error(status=500):
    return oci.exceptions.ServiceError(status, "Erro", {}, "mensagem")


def _obj(name):
    return SimpleNamespace(name=name)


def test_fetch_from_bucket_grava_conteudo_e_usa_chave_certa(tmp_path):
    client = FakeClient(content=b'{"ok": true}')

    path = fetch_from_bucket(KEY, client=client, dest_dir=tmp_path)

    assert path == tmp_path / "pacote-distribuicao-20261026T120000000000Z.json"
    assert path.read_bytes() == b'{"ok": true}'
    assert client.requested_keys == [KEY]


def test_fetch_from_bucket_propaga_erro_do_bucket(tmp_path):
    client = FakeClient(get_error=_svc_error(404))

    with pytest.raises(oci.exceptions.ServiceError):
        fetch_from_bucket(KEY, client=client, dest_dir=tmp_path)


def test_fetch_latest_pacote_baixa_o_mais_recente_da_semana(tmp_path):
    client = FakeClient(
        objects=[_obj(f"{OCI_ASSETS_PREFIX}/2026-W44/pacote-distribuicao-20261026T100000000000Z.json"),
                 _obj(KEY)],
        content=json.dumps(VALID_PACKAGE).encode("utf-8"),
    )

    path = fetch_latest_pacote("2026-W44", client=client, dest_dir=tmp_path)

    assert client.requested_keys == [KEY]
    assert validate_output(path) == []


def test_fetch_latest_pacote_sem_pacote_levanta_file_not_found(tmp_path):
    with pytest.raises(FileNotFoundError):
        fetch_latest_pacote("2026-W45", client=FakeClient(), dest_dir=tmp_path)


def test_fetch_latest_pacote_propaga_erro_de_listagem(tmp_path):
    client = FakeClient(list_error=_svc_error(403))

    with pytest.raises(oci.exceptions.ServiceError):
        fetch_latest_pacote("2026-W44", client=client, dest_dir=tmp_path)
