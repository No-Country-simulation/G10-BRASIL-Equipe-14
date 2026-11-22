"""Upload de arquivos brutos para os workflows de triagem publicados."""

import hashlib
import hmac
import json
import os
import re
from datetime import datetime, timezone
from urllib.parse import quote

import requests

from src.config import MAX_UPLOAD_FILE_SIZE_BYTES, OCI_BUCKET_NAME, OCI_NAMESPACE, OCI_REGION

SOURCES = {
    "Mastodon": ("mastodon", "wf09_triagem-llm-router-mastodon", "id"),
    "Stack Exchange": ("stackoverflow", "wf10_triagem-llm-router_stackexchange", "source_id"),
    "Hacker News": ("hackernews", "wf11_triagem-llm-router_hackernews", "comment_id"),
}


def prepare_upload(source, tag, raw):
    prefix, _, id_field = SOURCES[source]
    tag = tag.strip().lower()
    if not re.fullmatch(r"[a-z0-9]+(?:[ -][a-z0-9]+)*", tag) or len(tag) > 80:
        raise ValueError("Informe um tema de até 80 caracteres com letras sem acento, números, espaços ou hífens.")
    if len(raw) > MAX_UPLOAD_FILE_SIZE_BYTES:
        raise ValueError("O arquivo excede o limite de tamanho.")
    try:
        payload = json.loads(raw.decode("utf-8-sig"))
        if not isinstance(payload, list) or not payload:
            raise ValueError
        records = payload[0]["posts"] if prefix == "mastodon" else payload
        if not isinstance(records, list) or not records or not all(
            isinstance(record, dict) and record.get(id_field) for record in records
        ):
            raise ValueError
        if prefix == "stackoverflow" and any(not isinstance(row.get("answers"), list) for row in records):
            raise ValueError
        if prefix == "hackernews" and any("pub_story_id" not in row or "comment_text" not in row for row in records):
            raise ValueError
        content = json.dumps(payload, ensure_ascii=False, separators=(",", ":"), allow_nan=False).encode("utf-8")
    except (ValueError, KeyError, TypeError):
        raise ValueError(f"Envie um JSON bruto no formato que o workflow de {source} espera.") from None
    digest = hashlib.sha256(content).hexdigest()
    workflow_tag = f"{tag.replace(' ', '-')}-upload{digest[:16]}"
    return workflow_tag, f"raw/{prefix}_{workflow_tag}.json", content, len(records)


def request_oci_object(method, key, content=b""):
    access = os.getenv("OCI_S3_ACCESS_KEY_ID", "").strip()
    secret = os.getenv("OCI_S3_SECRET_ACCESS_KEY", "").strip()
    if not access or not secret:
        raise ValueError("Configure as credenciais S3 da OCI no servidor do Streamlit.")
    host = f"{OCI_NAMESPACE}.compat.objectstorage.{OCI_REGION}.oci.customer-oci.com"
    path = quote(f"/{OCI_BUCKET_NAME}/{key}", safe="/")
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    day = timestamp[:8]
    digest = hashlib.sha256(content).hexdigest()
    headers = {
        "host": host,
        "x-amz-content-sha256": digest,
        "x-amz-date": timestamp,
    }
    if method == "PUT":
        headers.update({"content-type": "application/json", "if-none-match": "*"})
    fields = ";".join(sorted(headers))
    canonical = "".join(f"{name}:{headers[name]}\n" for name in sorted(headers))
    request = f"{method}\n{path}\n\n{canonical}\n{fields}\n{digest}"
    scope = f"{day}/{OCI_REGION}/s3/aws4_request"
    to_sign = f"AWS4-HMAC-SHA256\n{timestamp}\n{scope}\n{hashlib.sha256(request.encode()).hexdigest()}"
    signing_key = f"AWS4{secret}".encode()
    for part in (day, OCI_REGION, "s3", "aws4_request"):
        signing_key = hmac.digest(signing_key, part.encode(), "sha256")
    signature = hmac.digest(signing_key, to_sign.encode(), "sha256").hex()
    headers["Authorization"] = (
        f"AWS4-HMAC-SHA256 Credential={access}/{scope}, SignedHeaders={fields}, Signature={signature}"
    )
    return requests.request(method, f"https://{host}{path}", data=content,
                            headers=headers, timeout=(10, 60), allow_redirects=False)


def upload_raw(key, content):
    response = request_oci_object("PUT", key, content)
    if response.status_code == 412:
        raise ValueError("Já existe um objeto com esta chave na OCI. Use outro tema para um novo envio.")
    if not 200 <= response.status_code < 300:
        raise ValueError(f"A OCI não confirmou a gravação (HTTP {response.status_code}).")


def trigger_triage(source, workflow_tag, limit):
    api_key = os.getenv("N8N_API_KEY", "").strip()
    if not api_key:
        raise ValueError("Configure N8N_API_KEY no servidor do Streamlit.")
    base = os.getenv("N8N_TRIAGE_BASE_URL", "https://bot.rsa.ia.br").rstrip("/")
    _, path, _ = SOURCES[source]
    response = requests.post(
        f"{base}/webhook/{path}",
        headers={"communitylab-api-key": api_key},
        json={"tag": workflow_tag, "limit": limit},
        timeout=(10, 180),
        allow_redirects=False,
    )
    try:
        result = response.json()
    except ValueError:
        result = {}
    if not isinstance(result, dict):
        result = {}
    if response.status_code != 200 or result.get("success") is not True:
        execution_id = result.get("execution_id")
        suffix = f" Execução: {execution_id}." if execution_id else ""
        raise ValueError(f"O n8n não confirmou a triagem (HTTP {response.status_code}).{suffix}")
    return result
