"""Gera conteúdo com os adapters (issues #9 [S1-04] e #10 [S1-05]) e valida cada saída.

Lê data/prompts/tests/adapters_cases.json (threads reais e sintéticas já classificadas pelo Router),
monta o prompt de cada canal a partir de data/prompts/social.md e data/prompts/newsletter_faq.md,
chama o Gemini (ou o Groq), valida com src/pipeline/validate_adapters.py e salva tudo em
data/prompts/tests/outputs/adapters_gemini_<data>.json.

Uso (na raiz do repositório):
    uv run python -m src.pipeline.run_adapters                  # Gemini (GEMINI_API_KEY no .env)
    uv run python -m src.pipeline.run_adapters --provider groq  # Groq (GROQ_API_KEY no .env)
    uv run python -m src.pipeline.run_adapters --only faq       # só os jobs cujo nome contém "faq"
    uv run python -m src.pipeline.run_adapters --dry-run        # monta os prompts sem chamar a API
"""
import argparse
import html
import json
import os
import re
import sys
import time
from datetime import datetime
from pathlib import Path
from urllib import error, request

from src.pipeline import validate_adapters as va

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None

ROOT = Path(__file__).resolve().parents[2]
PROMPTS_DIR = ROOT / "data/prompts"
CASES_FILE = PROMPTS_DIR / "tests/adapters_cases.json"
OUTPUTS_DIR = PROMPTS_DIR / "tests/outputs"
SOCIAL_HEADINGS = {
    "linkedin": "## Adapter LinkedIn",
    "x/twitter": "## Adapter X",
    "mastodon": "## Adapter Mastodon",
    "instagram": "## Adapter Instagram",
}


# ---------- prompts ----------

def text_block_after(markdown: str, heading: str) -> str:
    start = markdown.index(heading)
    match = re.search(r"```text\n(.*?)```", markdown[start:], re.S)
    return match.group(1).strip()


def version_of(markdown: str) -> str:
    match = re.search(r"^versao:\s*(\S+)", markdown, re.M)
    return match.group(1) if match else "?"


def system_prompt(channel: str, social: str, nl_faq: str) -> str:
    if channel == "faq":
        return text_block_after(nl_faq, "## Adapter FAQ")
    if channel == "newsletter":
        return text_block_after(nl_faq, "## Adapter Newsletter")
    common = text_block_after(social, "## Bloco comum")
    return common + "\n\n" + text_block_after(social, SOCIAL_HEADINGS[channel])


def plain(text: str | None, limit: int) -> str:
    text = re.sub(r"<[^>]+>", " ", text or "")
    text = re.sub(r"\s+", " ", html.unescape(text)).strip()
    return text[:limit]


def newsletter_item(item: dict) -> dict:
    """Versão enxuta do item para a newsletter (limite de contexto do free tier, ver newsletter_faq.md)."""
    thread, cls = item["input"], item["classification"]
    first = thread["interactions"][0]
    entry = {k: cls.get(k) for k in ("type", "sentiment", "topics", "summary", "relevance_score", "suggested_route", "has_answer")}
    entry |= {"id": thread["id"], "source": thread["source"], "url": thread.get("url"), "author": first.get("author"),
              "title": first.get("title"), "content": plain(first.get("content"), 500),
              "view_count": (first.get("raw_metadata") or {}).get("view_count"),
              "answer_count": (first.get("raw_metadata") or {}).get("answer_count")}
    accepted = [i for i in thread["interactions"][1:] if (i.get("raw_metadata") or {}).get("is_accepted")]
    if accepted:
        entry["accepted_answer"] = {"author": accepted[0].get("author"), "content": plain(accepted[0].get("content"), 800)}
    return entry


def user_prompt(job: dict, items: list[dict], period: str | None) -> str:
    if job["canal"] == "newsletter":
        batch = sorted((newsletter_item(i) for i in items), key=lambda e: -(e.get("relevance_score") or 0))[:15]
        return f"Gere a edição da newsletter.\nPERÍODO: {period}\nITENS: {json.dumps(batch, ensure_ascii=False)}"
    item = items[0]
    cls = json.dumps(item["classification"], ensure_ascii=False)
    thread = json.dumps(item["input"], ensure_ascii=False)
    if job["canal"] == "faq":
        return f"Gere o card de FAQ.\nCLASSIFICAÇÃO: {cls}\nITEM ORIGINAL: {thread}"
    return f"Gere o conteúdo para o canal indicado.\n\nCLASSIFICAÇÃO:\n{cls}\n\nITEM ORIGINAL:\n{thread}"


# ---------- chamadas ao modelo ----------

def _post(url: str, payload: dict, headers: dict, retries: int = 3) -> dict:
    data = json.dumps(payload).encode()
    for attempt in range(retries + 1):
        req = request.Request(url, data=data, headers={"Content-Type": "application/json", **headers})
        try:
            with request.urlopen(req, timeout=120) as resp:
                return json.loads(resp.read())
        except error.HTTPError as exc:
            if exc.code in (429, 500, 503) and attempt < retries:
                wait = 15 * (attempt + 1)
                print(f"  HTTP {exc.code}: limite ou instabilidade; aguardando {wait}s...")
                time.sleep(wait)
                continue
            raise RuntimeError(f"HTTP {exc.code}: {exc.read().decode(errors='replace')[:300]}") from None
    raise RuntimeError("sem resposta")


def temperature(model: str) -> float:
    if os.getenv("LLM_TEMPERATURE"):
        return float(os.environ["LLM_TEMPERATURE"])
    return 1.0 if model.startswith("gemini-3") else 0.7


def call_gemini(system: str, turns: list[tuple[str, str]], model: str) -> str:
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    payload = {
        "system_instruction": {"parts": [{"text": system}]},
        "contents": [{"role": role, "parts": [{"text": text}]} for role, text in turns],
        "generationConfig": {"temperature": temperature(model), "responseMimeType": "application/json"},
    }
    data = _post(url, payload, {"x-goog-api-key": os.environ["GEMINI_API_KEY"]})
    candidates = data.get("candidates") or []
    if not candidates:
        raise RuntimeError(f"resposta sem candidatos: {json.dumps(data.get('promptFeedback', data))[:300]}")
    parts = candidates[0].get("content", {}).get("parts", [])
    text = "".join(p.get("text", "") for p in parts if not p.get("thought"))
    if not text:
        raise RuntimeError(f"resposta vazia (finishReason={candidates[0].get('finishReason')})")
    return text


def call_groq(system: str, turns: list[tuple[str, str]], model: str) -> str:
    messages = [{"role": "system", "content": system}] + [
        {"role": "assistant" if role == "model" else "user", "content": text} for role, text in turns]
    payload = {"model": model, "temperature": temperature(model), "response_format": {"type": "json_object"}, "messages": messages}
    data = _post("https://api.groq.com/openai/v1/chat/completions", payload,
                 {"Authorization": f"Bearer {os.environ['GROQ_API_KEY']}"})
    return data["choices"][0]["message"]["content"]


def parse_json(text: str) -> dict:
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text)
    return json.loads(text)


def fix_request(errors: list[str], channel: str) -> str | None:
    """Pedido de correção para os erros que o modelo consegue consertar sozinho (o que o n8n também fará)."""
    asks = []
    if any(e.startswith("body com ") for e in errors):
        low, high = va.LIMITS[channel][0], va.LIMITS[channel][1]
        asks.append(f"o campo body ficou fora do limite deste canal ({low} a {high} caracteres)")
    if any(e.startswith("menção com @") for e in errors):
        asks.append('há nomes com "@" no body, o que marcaria outra conta; escreva os nomes sem "@"')
    if not asks:
        return None
    return ("Corrija: " + "; ".join(asks) + ". Mantenha os mesmos fatos e regras. Responda no mesmo formato JSON.")


# ---------- execução ----------

def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if load_dotenv:
        load_dotenv(ROOT / ".env")

    parser = argparse.ArgumentParser()
    parser.add_argument("--provider", choices=["gemini", "groq"], default="gemini")
    parser.add_argument("--only", help="roda só os jobs cujo nome contém este texto")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--sleep", type=float, default=5.0, help="pausa entre chamadas (rate limit do free tier)")
    args = parser.parse_args()

    social = (PROMPTS_DIR / "social.md").read_text(encoding="utf-8")
    nl_faq = (PROMPTS_DIR / "newsletter_faq.md").read_text(encoding="utf-8")
    cases = json.loads(CASES_FILE.read_text(encoding="utf-8"))
    items = {i["id"]: i for i in cases["items"]}
    jobs = [j for j in cases["jobs"] if not args.only or args.only in j["nome"]]
    sources = va.load_sources()
    validator = va.item_schema()

    key_name = "GEMINI_API_KEY" if args.provider == "gemini" else "GROQ_API_KEY"
    if not args.dry_run and not os.getenv(key_name):
        print(f"Falta a chave {key_name}. Crie o arquivo .env na raiz do repositório com a linha:\n{key_name}=sua_chave_aqui")
        return 2
    model = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite") if args.provider == "gemini" else os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
    call = call_gemini if args.provider == "gemini" else call_groq
    versions = {"social": version_of(social), "newsletter_faq": version_of(nl_faq)}
    print(f"Adapters social v{versions['social']} e newsletter_faq v{versions['newsletter_faq']} | "
          f"modo: {'dry-run' if args.dry_run else f'{args.provider}/{model}'} | {len(jobs)} saídas\n")

    results, approved = [], 0
    for job in jobs:
        job_items = [items[i] for i in job["itens"]]
        system = system_prompt(job["canal"], social, nl_faq)
        turns = [("user", user_prompt(job, job_items, cases.get("reference_period_newsletter")))]
        entry = {"nome": job["nome"], "canal": job["canal"], "itens_de_origem": job["itens"],
                 "origem": sorted({i["origem"] for i in job_items}), "tentativas": []}
        if job.get("nota"):
            entry["nota"] = job["nota"]
        if args.dry_run:
            print(f"[dry-run] {job['nome']}: system {len(system)} caracteres, user {len(turns[0][1])} caracteres")
            continue

        output, errors, warnings = {}, ["sem resposta"], []
        for attempt in range(2):
            try:
                raw = call(system, turns, model)
                output = parse_json(raw)
                errors, warnings = va.validate({"nome": job["nome"], "itens_de_origem": job["itens"], "output": output},
                                               sources, validator)
            except Exception as exc:  # resposta inválida conta como falha
                raw, output, errors, warnings = "", {}, [f"erro na chamada/JSON: {exc}"], []
            entry["tentativas"].append({"output": output, "errors": errors})
            time.sleep(args.sleep)
            fix = fix_request(errors, job["canal"]) if attempt == 0 else None
            if not fix:
                break
            print(f"  {job['nome']}: {errors[0]}; pedindo nova versão ao modelo")
            turns += [("model", raw), ("user", fix)]

        entry |= {"output": output, "validation": {"ok": not errors, "errors": errors, "warnings": warnings}}
        results.append(entry)
        approved += not errors
        body_len = len(output.get("body", "")) if isinstance(output, dict) else 0
        print(f"[{'OK   ' if not errors else 'FALHA'}] {job['nome']} ({job['canal']}, {body_len} caracteres"
              f"{', 2 tentativas' if len(entry['tentativas']) > 1 else ''})"
              + ("" if not errors else " -> " + "; ".join(errors)))
        for w in warnings:
            print(f"        aviso: {w}")

    if args.dry_run:
        return 0
    print(f"\n{approved}/{len(results)} saídas aprovadas pelo validador")
    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
    out_file = OUTPUTS_DIR / f"adapters_{args.provider}_{datetime.now().strftime('%Y%m%d-%H%M')}.json"
    meta = {"prompt_versions": versions, "model": model, "temperature": temperature(model),
            "ran_at": datetime.now().isoformat(timespec="seconds"), "approved": f"{approved}/{len(results)}",
            "router_run": cases.get("router_run")}
    out_file.write_text(json.dumps(meta | {"exemplos": results}, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Saídas salvas em {out_file.relative_to(ROOT)}")
    return 0 if approved == len(results) else 1


if __name__ == "__main__":
    sys.exit(main())
