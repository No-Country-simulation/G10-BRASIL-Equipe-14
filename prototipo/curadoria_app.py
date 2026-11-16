"""Protótipo do Painel de Curadoria (S3-04). Standalone: não depende de src/."""
import json
from datetime import datetime
from pathlib import Path

import duckdb
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "aprovados"
DB_PATH = ROOT / "data" / "curadoria.duckdb"

# Suposição: ajustar aos valores reais de TARGETS_ENUM / output_schema.json
CHANNELS = {"social": "Redes Sociais", "newsletter": "Newsletter", "faq": "FAQ"}

EXEMPLO = {
    "package_id": "pkg-exemplo-001",
    "linked_batch_id": "2026-W46",
    "suggested_content": [
        {"title": "Dúvida sobre LlamaIndex", "target": "social",
         "body": "Quem já usou LlamaIndex com RAG? #llamaindex #rag"},
        {"title": "Destaque da semana", "target": "newsletter",
         "body": "Esta semana a comunidade discutiu validação de dados em pipelines."},
        {"title": "Como validar um JSON de saída?", "target": "faq",
         "body": "Use um JSON Schema e valide antes de publicar o pacote."},
    ],
}


def init_state(package: dict) -> None:
    """Cria o estado de revisão uma vez por pacote carregado."""
    if st.session_state.get("pkg_id") == package["package_id"]:
        return
    st.session_state.pkg_id = package["package_id"]
    st.session_state.review = {}
    for i, item in enumerate(package["suggested_content"]):
        cid = f"{package['package_id']}_{i}"
        st.session_state.review[cid] = {**item, "id": cid, "status": "pending"}
        # Inicializa o widget uma única vez: evita conflito entre value= e key=
        st.session_state.setdefault(f"body_{cid}", item["body"])


def approve(cid: str) -> None:
    # Lê o texto editado NO CALLBACK, antes de qualquer reexecução
    item = st.session_state.review[cid]
    item["body"] = st.session_state[f"body_{cid}"]
    item["status"] = "approved"


def reject(cid: str) -> None:
    st.session_state.review[cid]["status"] = "rejected"


def reopen(cid: str) -> None:
    st.session_state.review[cid]["status"] = "pending"


def save_json(package: dict, approved: list[dict]) -> Path:
    OUT_DIR.mkdir(exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    path = OUT_DIR / f"pacote-{package['linked_batch_id']}-{stamp}.json"
    payload = {
        "package_id": package["package_id"],
        "linked_batch_id": package["linked_batch_id"],
        "approved_at": datetime.now().isoformat(timespec="seconds"),
        "suggested_content": [
            {"target": c["target"], "title": c["title"], "body": c["body"]} for c in approved
        ],
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def save_duckdb(package: dict, approved: list[dict]) -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    rows = [(c["id"], package["package_id"], c["target"], c["title"], c["body"]) for c in approved]
    with duckdb.connect(str(DB_PATH)) as con:  # abre e fecha a cada gravação
        con.execute("""
            CREATE TABLE IF NOT EXISTS aprovados (
                content_id  VARCHAR PRIMARY KEY,
                package_id  VARCHAR,
                target      VARCHAR,
                title       VARCHAR,
                body        VARCHAR,
                approved_at TIMESTAMP DEFAULT current_timestamp
            )
        """)
        con.executemany(
            "INSERT OR REPLACE INTO aprovados (content_id, package_id, target, title, body) "
            "VALUES (?, ?, ?, ?, ?)",
            rows,
        )


def render_item(item: dict) -> None:
    cid = item["id"]
    with st.container(border=True):
        st.caption(CHANNELS.get(item["target"], item["target"]) + f" · status: {item['status']}")
        st.markdown(f"**{item['title']}**")
        if item["status"] == "pending":
            st.text_area("Texto", key=f"body_{cid}", height=140, label_visibility="collapsed")
            c1, c2 = st.columns(2)
            c1.button("Aprovar", key=f"ok_{cid}", on_click=approve, args=(cid,), type="primary")
            c2.button("Rejeitar", key=f"no_{cid}", on_click=reject, args=(cid,))
        else:
            st.write(item["body"])
            st.button("Refazer revisão", key=f"undo_{cid}", on_click=reopen, args=(cid,))


def main() -> None:
    st.set_page_config(page_title="Curadoria - Protótipo", layout="wide")
    st.header("Painel de Curadoria Humana (protótipo S3-04)")

    upload = st.file_uploader("Pacote JSON (opcional; sem arquivo usa o exemplo)", type="json")
    package = json.load(upload) if upload else EXEMPLO
    init_state(package)

    items = list(st.session_state.review.values())
    pending = [i for i in items if i["status"] == "pending"]
    approved = [i for i in items if i["status"] == "approved"]

    for channel, label in CHANNELS.items():
        group = [i for i in items if i["target"] == channel]
        if not group:
            continue
        st.subheader(label)
        for item in group:
            render_item(item)

    st.divider()
    st.write(f"Aprovados: {len(approved)} · Pendentes: {len(pending)}")
    if pending:
        st.warning("Ainda há conteúdos pendentes. Eles não entram no pacote final.")
    if st.button("Aprovar versão final", type="primary", disabled=not approved):
        json_path = save_json(package, approved)
        save_duckdb(package, approved)
        st.success(f"Salvo: {json_path.relative_to(ROOT)} e tabela 'aprovados' em data/curadoria.duckdb")


main()
