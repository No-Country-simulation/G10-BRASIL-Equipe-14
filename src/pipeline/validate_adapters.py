"""Valida saídas dos adapters (issues #9 [S1-04] e #10 [S1-05]).

Confere, para cada conteúdo gerado:
- formato do item de suggested_content (output_schema.json) e target no enum;
- limites de caracteres, hashtags e emojis por canal;
- frases proibidas (tom de voz) e menções com @ (o handle é de outra rede);
- estrutura do card de FAQ e a regra do "[PRECISA DE REVISÃO TÉCNICA]";
- linha de crédito quando o conteúdo vem do Stack Overflow (CC BY-SA 4.0);
- números no texto que não aparecem na entrada (sinal de dado inventado).

Uso (na raiz do repositório):
    uv run python -m src.pipeline.validate_adapters data/prompts/tests/outputs/<arquivo>.json

Formato esperado do arquivo:
    {"exemplos": [{"nome": "...", "itens_de_origem": ["se-79838505"], "output": {target, title, body, potential_engagement}}]}
Os itens de origem são procurados em data/prompts/tests/adapters_cases.json e em data/prompts/tests/router_cases*.json.
O src/pipeline/run_adapters.py chama a função validate() deste arquivo para cada saída que gera.
"""
import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TESTS_DIR = ROOT / "data/prompts/tests"
OUTPUT_SCHEMA = ROOT / "data/schemas/output_schema.json"

SCHEMA_KEYS = {"target", "title", "body", "potential_engagement"}
TARGETS_SCHEMA = {"linkedin", "newsletter", "faq", "instagram", "x/twitter", "discord", "blog"}  # enum do output_schema.json (merge da PR #54)
# canal: (mín. caracteres, máx. caracteres, mín. hashtags, máx. hashtags, máx. emojis, máx. caracteres do título)
LIMITS = {
    "linkedin": (600, 1300, 3, 5, 3, 80),
    "x": (1, 280, 1, 2, None, 80),
    "x/twitter": (1, 280, 1, 2, None, 80),
    "mastodon": (1, 500, 0, 2, None, 80),
    "bluesky": (1, 300, 0, 2, None, 80),
    "instagram": (1, 2200, 5, 10, 5, 120),
    "faq": (1, 1200, 0, 0, None, 80),
    "newsletter": (1, 3000, 0, 0, None, 60),
}
FORBIDDEN = ["é com grande alegria", "gratidão!", "nada nos dá mais orgulho", "venha fazer parte", "não perca",
             "esperamos que esteja bem", "imperdível", "clique aqui"]
REVIEW_TAG = "[PRECISA DE REVISÃO TÉCNICA]"
EMOJI_RE = re.compile("[\U0001F300-\U0001FAFF\U00002600-\U000027BF\U0001F000-\U0001F2FF]")
HASHTAG_RE = re.compile(r"(?<![\w&/])#(\w+)")
URL_RE = re.compile(r"https?://\S+")
NUMBER_RE = re.compile(r"\d+(?:[.,]\d+)*")
MENTION_RE = re.compile(r"(?<![\w.@/])@[A-Za-z0-9_][\w.]*")


def load_sources() -> dict:
    sources = {}
    for path in TESTS_DIR.glob("router_cases*.json"):
        for case in json.loads(path.read_text(encoding="utf-8")):
            sources[case["input"]["id"]] = case["input"]
    adapters_cases = TESTS_DIR / "adapters_cases.json"
    if adapters_cases.exists():
        for item in json.loads(adapters_cases.read_text(encoding="utf-8"))["items"]:
            sources[item["id"]] = item["input"]
    return sources


def source_text(items: list[dict]) -> str:
    return " ".join(json.dumps(item, ensure_ascii=False) for item in items)


def unknown_numbers(body: str, src: str) -> list[str]:
    text = URL_RE.sub(" ", body).replace("CC BY-SA 4.0", " ")
    text = re.sub(r"(?m)^\s*\d+\.\s", " ", text)  # marcadores de lista "1. "
    src_digits = re.sub(r"[.,\s]", "", src)
    missing = []
    for token in set(NUMBER_RE.findall(text)):
        candidates = {token, token.replace(",", "."), token.replace(".", "").replace(",", "")}
        if not any(c in src for c in candidates) and token.replace(".", "").replace(",", "") not in src_digits:
            missing.append(token)
    return sorted(missing)


def item_schema():
    if not OUTPUT_SCHEMA.exists():
        return None
    try:
        import jsonschema
    except ImportError:
        return None
    schema = json.loads(OUTPUT_SCHEMA.read_text(encoding="utf-8"))
    return jsonschema.Draft202012Validator(schema["properties"]["suggested_content"]["items"])


def validate(example: dict, sources: dict, validator) -> tuple[list[str], list[str]]:
    errors, warnings = [], []
    out = example["output"]
    target, body, title = out.get("target"), out.get("body", ""), out.get("title", "")

    extra = set(out) - SCHEMA_KEYS
    if extra == {"source_link"} and target == "faq":
        warnings.append("campo source_link fora do output_schema: o n8n deve removê-lo (ou o time adiciona ao schema)")
    elif extra:
        errors.append(f"campos fora do output_schema: {sorted(extra)}")
    if SCHEMA_KEYS - set(out):
        errors.append(f"campos ausentes: {sorted(SCHEMA_KEYS - set(out))}")
    if target not in TARGETS_SCHEMA:
        warnings.append(f"target {target!r} ainda não está no enum do output_schema.json (decisão do time)")
    if validator is not None and target in TARGETS_SCHEMA:
        for err in validator.iter_errors({k: out[k] for k in SCHEMA_KEYS if k in out}):
            errors.append(f"output_schema: {err.message}")
    if target not in LIMITS:
        errors.append(f"canal desconhecido: {target!r}")
        return errors, warnings

    min_c, max_c, min_h, max_h, max_e, max_title = LIMITS[target]
    n_chars, hashtags, emojis = len(body), HASHTAG_RE.findall(URL_RE.sub(" ", body)), EMOJI_RE.findall(body)
    if not min_c <= n_chars <= max_c:
        errors.append(f"body com {n_chars} caracteres (limite {min_c}–{max_c})")
    if not min_h <= len(hashtags) <= max_h:
        errors.append(f"{len(hashtags)} hashtags (limite {min_h}–{max_h})")
    if max_e is not None and len(emojis) > max_e:
        errors.append(f"{len(emojis)} emojis (máx. {max_e})")
    if len(title) > max_title:
        errors.append(f"title com {len(title)} caracteres (máx. {max_title})")
    mentions = MENTION_RE.findall(URL_RE.sub(" ", body))
    if mentions:
        errors.append(f"menção com @ ({', '.join(sorted(set(mentions)))}): marcaria outra conta na rede; escreva o nome sem @")
    for phrase in FORBIDDEN:
        if phrase in body.lower():
            errors.append(f"frase proibida (tom de voz): {phrase!r}")

    origin = [sources[i] for i in example.get("itens_de_origem", []) if i in sources]
    if len(origin) < len(example.get("itens_de_origem", [])):
        warnings.append("algum item de origem não foi encontrado nos router_cases*.json")
    needs_review = body.startswith(REVIEW_TAG)

    if target == "faq":
        if needs_review:
            if out.get("potential_engagement") != "low":
                errors.append("FAQ em revisão deve ter potential_engagement = 'low'")
            if "**Resposta curta:**" in body:
                errors.append("FAQ em revisão não pode trazer resposta")
        else:
            for section in ("**Pergunta:**", "**Resposta curta:**", "**Fonte:**"):
                if section not in body:
                    errors.append(f"card de FAQ sem a seção {section}")
            if not re.match(r"(Como|Por que|O que)\b", title):
                errors.append("title do FAQ deve começar com 'Como', 'Por que' ou 'O que'")
            has_accepted = any((i.get("raw_metadata") or {}).get("is_accepted")
                               for item in origin for i in item["interactions"][1:])
            if origin and not has_accepted:
                errors.append(f"FAQ respondido sem resposta aceita na entrada: deveria começar com {REVIEW_TAG}")

    from_so = any(item.get("source") == "stackoverflow" for item in origin)
    if from_so and not needs_review and target in ("linkedin", "faq", "newsletter", "instagram") and "CC BY-SA" not in body:
        errors.append("conteúdo do Stack Overflow sem linha de crédito (CC BY-SA 4.0)")

    if origin:
        missing = unknown_numbers(body, source_text(origin))
        if missing:
            errors.append(f"números que não aparecem na entrada (possível invenção): {missing}")
    return errors, warnings


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser()
    parser.add_argument("arquivo", type=Path)
    args = parser.parse_args()

    examples = json.loads(args.arquivo.read_text(encoding="utf-8"))["exemplos"]
    sources, validator = load_sources(), item_schema()
    if validator is None:
        print("(aviso: data/schemas/output_schema.json ou jsonschema indisponível; checagem do schema pulada)")
    ok = 0
    for ex in examples:
        errors, warnings = validate(ex, sources, validator)
        out = ex["output"]
        print(f"[{'OK   ' if not errors else 'FALHA'}] {ex['nome']} ({out.get('target')}, {len(out.get('body', ''))} caracteres)")
        for e in errors:
            print(f"        erro: {e}")
        for w in warnings:
            print(f"        aviso: {w}")
        ok += not errors
    print(f"\n{ok}/{len(examples)} saídas aprovadas")
    return 0 if ok == len(examples) else 1


if __name__ == "__main__":
    sys.exit(main())
