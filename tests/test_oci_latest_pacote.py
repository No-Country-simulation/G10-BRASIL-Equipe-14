from types import SimpleNamespace

import oci
import pytest

from src.services.oci_storage import _latest_pacote


class FakeClient:
    """Cliente falso: cada operação devolve o resultado ou lança o erro configurado."""

    def __init__(self, objects=(), list_error=None, head_error=None, sha="abc"):
        self.objects = list(objects)
        self.list_error = list_error
        self.head_error = head_error
        self.sha = sha
        self.calls = []

    def list_objects(self, namespace, bucket, prefix, **kwargs):
        self.calls.append(("list_objects", kwargs))
        if self.list_error:
            raise self.list_error
        return SimpleNamespace(data=SimpleNamespace(objects=self.objects))

    def head_object(self, namespace, bucket, name, **kwargs):
        self.calls.append(("head_object", kwargs))
        if self.head_error:
            raise self.head_error
        return SimpleNamespace(headers={"opc-meta-sha256": self.sha})


def _svc_error(status=500):
    return oci.exceptions.ServiceError(status, "Erro", {}, "mensagem")


def _obj(name):
    return SimpleNamespace(name=name)


def test_lista_vazia_retorna_none():
    assert _latest_pacote(FakeClient(), "bucket", "ativos/2026-W45/") is None


def test_retorna_nome_e_sha_do_mais_recente():
    client = FakeClient(
        objects=[_obj("ativos/2026-W45/pacote-20261101T000000Z.json"),
                 _obj("ativos/2026-W45/pacote-20261105T120000Z.json")],
        sha="deadbeef",
    )

    name, sha = _latest_pacote(client, "bucket", "ativos/2026-W45/")

    assert name == "ativos/2026-W45/pacote-20261105T120000Z.json"
    assert sha == "deadbeef"


def test_erro_na_listagem_propaga_em_vez_de_virar_none():
    client = FakeClient(list_error=_svc_error(403))

    with pytest.raises(oci.exceptions.ServiceError):
        _latest_pacote(client, "bucket", "ativos/2026-W45/")


def test_erro_no_head_propaga_em_vez_de_virar_none():
    client = FakeClient(objects=[_obj("ativos/2026-W45/pacote-x.json")],
                        head_error=_svc_error(500))

    with pytest.raises(oci.exceptions.ServiceError):
        _latest_pacote(client, "bucket", "ativos/2026-W45/")


def test_chamadas_usam_retry_strategy_do_sdk():
    client = FakeClient(objects=[_obj("ativos/2026-W45/pacote-x.json")])

    _latest_pacote(client, "bucket", "ativos/2026-W45/")

    assert len(client.calls) == 2
    for _, kwargs in client.calls:
        assert kwargs["retry_strategy"] is oci.retry.DEFAULT_RETRY_STRATEGY
