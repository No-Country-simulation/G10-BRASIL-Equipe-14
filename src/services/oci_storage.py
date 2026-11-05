from datetime import date, datetime, timezone
from pathlib import Path

import oci
from oci.object_storage import ObjectStorageClient

from src.config import OCI_ASSETS_PREFIX, OCI_BUCKET_NAME, OCI_NAMESPACE, OUTPUT_SCHEMA_PATH
from src.validation.schema_validator import validate_data

import hashlib
import json


def canonical_bytes(payload: dict) -> bytes:
    """Serialização determinística: mesmas chaves e valores geram sempre os mesmos bytes."""
    return json.dumps(
        payload, sort_keys=True, ensure_ascii=False, separators=(",", ":")
    ).encode("utf-8")


def sha256_hex(payload: dict) -> str:
    return hashlib.sha256(canonical_bytes(payload)).hexdigest()


def iso_week_label(d: date) -> str:
    year, week, _ = d.isocalendar()
    return f"{year}-W{week:02d}"

def _load_schema() -> dict:
    return json.loads(Path(OUTPUT_SCHEMA_PATH).read_text(encoding="utf-8"))


def _latest_pacote(client, bucket: str, prefix: str):
    """Retorna (nome, sha256) do pacote mais recente da semana, ou None."""
    objects = client.list_objects(OCI_NAMESPACE, bucket, prefix=prefix).data.objects
    if not objects:
        return None
    latest = max(objects, key=lambda o: o.name)  # timestamp de largura fixa ordena como texto
    head = client.head_object(OCI_NAMESPACE, bucket, latest.name)
    return latest.name, head.headers.get("opc-meta-sha256")

def publish_package(payload: dict, week: str | None = None, client=None,
                    base_prefix: str = OCI_ASSETS_PREFIX) -> str:
    now = datetime.now(timezone.utc)
    week = week or iso_week_label(now.date())
    prefix = f"{base_prefix}/{week}/"
    key = f"{prefix}pacote-distribuicao-{now:%Y%m%dT%H%M%S%fZ}.json"
    # 1. preencher storage antes de validar, porque o schema exige o bloco
    payload["storage"] = {"bucket": OCI_BUCKET_NAME, "object_path": key, "status": "success"}
    errors = validate_data(payload, _load_schema())
    if errors:
        raise ValueError("Payload inválido:\n" + "\n".join(errors))

    # 2. hash sobre o conteúdo sem o bloco storage (proposta, ainda a validar com o time)
    content = {k: v for k, v in payload.items() if k != "storage"}
    digest = sha256_hex(content)

    client = client or ObjectStorageClient(oci.config.from_file())
    latest = _latest_pacote(client, OCI_BUCKET_NAME, prefix)
    if latest and latest[1] == digest:
        return latest[0]  # mesmo conteúdo já gravado na semana: não regrava

    # 3. upload com o hash em metadado para a próxima comparação
    client.put_object(
        OCI_NAMESPACE,
        OCI_BUCKET_NAME,
        key,
        canonical_bytes(payload),
        opc_meta={"sha256": digest},
        if_none_match="*",  # falha se já existir um objeto com esta chave
    )
    return key
