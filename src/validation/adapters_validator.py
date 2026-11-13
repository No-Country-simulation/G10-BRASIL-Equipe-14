import argparse
import json
import sys
from pathlib import Path

from src.config import (
    CHANNEL_LIMITS,
    INPUT_SCHEMA_PATH,
    SCHEMA_KEYS,
    TARGETS_SCHEMA,
    FORBIDDEN,
    REVIEW_TAG,
    OUTPUT_SCHEMA_PATH,
    CASES_DIR,
)

from src.utils.regex_patterns import (
    EMOJI_RE,
    HASHTAG_RE,
    MENTION_RE,
    NUMBER_RE,
    URL_RE,
    VERSION_RE,
    DIGIT_CLEANUP_RE,
    get_current_year_re,
    FAQ_TITLE_START_RE,
)


def load_sources() -> dict:
    sources = {}
    # Procura em todos os JSONs de casos dentro da estrutura data/prompts/cases/
    if CASES_DIR.exists():
        for path in CASES_DIR.glob("**/*.json"):
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
                if isinstance(data, list):
                    items_list = data
                elif isinstance(data, dict):
                    items_list = data.get("items", [])
                else:
                    continue
                for case in items_list:
                    if not isinstance(case, dict):
                        continue
                    if isinstance(case.get("input"), dict):
                        sources[case["input"]["id"]] = case["input"]
                    elif "id" in case and "interactions" in case:
                        sources[case["id"]] = case
            except (OSError, json.JSONDecodeError, KeyError, TypeError):
                continue
    return sources


def source_text(items: list[dict]) -> str:
    return " ".join(json.dumps(item, ensure_ascii=False) for item in items)


def unknown_numbers(body: str, src: str) -> list[str]:
    text = URL_RE.sub(" ", body).replace("CC BY-SA 4.0", " ")
    text = VERSION_RE.sub(" ", text)
    current_year_re = get_current_year_re()
    text = current_year_re.sub(" ", text)

    src_digits = DIGIT_CLEANUP_RE.sub("", src)
    missing = []
    for token in set(NUMBER_RE.findall(text)):
        candidates = {
            token,
            token.replace(",", "."),
            token.replace(".", "").replace(",", ""),
        }
        if (
            not any(c in src for c in candidates)
            and token.replace(".", "").replace(",", "") not in src_digits
        ):
            missing.append(token)
    return sorted(missing)


def item_schema():
    if not OUTPUT_SCHEMA_PATH.exists():
        return None

    try:
        import jsonschema
    except ImportError:
        return None

    schema = json.loads(OUTPUT_SCHEMA_PATH.read_text(encoding="utf-8"))

    return jsonschema.Draft202012Validator(
        schema["properties"]["suggested_content"]["items"],
        format_checker=jsonschema.FormatChecker(),
    )


def invalid_inputs(data: dict) -> list[str]:
    problems: list[str] = []
    items = data.get("items", [])
    jobs = data.get("jobs", [])
    job_names: set[str] = set()
    items_by_id = {
        item.get("id"): item
        for item in items
        if isinstance(item, dict) and isinstance(item.get("id"), str)
    }

    if not isinstance(items, list):
        return ["campo 'items' deve ser uma lista"]
    if not isinstance(jobs, list):
        return ["campo 'jobs' deve ser uma lista"]

    item_ids: set[str] = set()
    schema_validator = None
    if INPUT_SCHEMA_PATH.exists():
        try:
            import jsonschema

            schema = json.loads(INPUT_SCHEMA_PATH.read_text(encoding="utf-8"))
            schema_validator = jsonschema.Draft202012Validator(schema)
        except (OSError, json.JSONDecodeError, KeyError, ImportError):
            schema_validator = None

    for index, item in enumerate(items):
        label = f"item[{index}]"
        if not isinstance(item, dict):
            problems.append(f"{label}: deve ser um objeto")
            continue
        item_id = item.get("id")
        if not isinstance(item_id, str) or not item_id:
            problems.append(f"{label}: campo 'id' deve ser uma string")
        elif item_id in item_ids:
            problems.append(f"{label}: id duplicado: {item_id}")
        else:
            item_ids.add(item_id)
        if not isinstance(item.get("input"), dict):
            problems.append(f"{label}: campo 'input' deve ser um objeto")
        if not isinstance(item.get("classification"), dict):
            problems.append(f"{label}: campo 'classification' deve ser um objeto")
        if schema_validator is not None and isinstance(item.get("input"), dict):
            for error in schema_validator.iter_errors(item["input"]):
                location = "/".join(str(part) for part in error.path)
                suffix = f" em {location}" if location else ""
                problems.append(f"{label}: {error.message}{suffix}")

    items_by_id = {
        item.get("id"): item
        for item in items
        if isinstance(item, dict) and isinstance(item.get("id"), str)
    }

    for index, job in enumerate(jobs):
        label = f"job[{index}]"
        if not isinstance(job, dict):
            problems.append(f"{label}: deve ser um objeto")
            continue

        job_name_val = job.get("nome")
        if not isinstance(job_name_val, str) or not job_name_val:
            problems.append(f"{label}: campo 'nome' deve ser uma string")
        elif job_name_val in job_names:
            problems.append(f"{label}: nome de job duplicado: {job_name_val}")
        else:
            job_names.add(job_name_val)

        channel = job.get("canal")
        if channel not in CHANNEL_LIMITS:
            problems.append(f"{label}: canal desconhecido: {channel!r}")

        references = job.get("itens")
        if not isinstance(references, list) or not references:
            problems.append(f"{label}: campo 'itens' deve ser uma lista não vazia")
        else:
            for item_id in references:
                if item_id not in items_by_id:
                    problems.append(
                        f"{label}: item de origem não encontrado: {item_id!r}"
                    )
                    continue

                # Validação de rota restrita para adapters
                referenced_item = items_by_id[item_id]
                classification = referenced_item.get("classification", {})
                route = classification.get("suggested_route")
                if route in {"discard", "moderation"}:
                    problems.append(
                        f"{label}: item {item_id!r} possui rota sugerida {route!r} "
                        "e não deve ser processado por um job de adapter"
                    )

    return problems


def check_output(
    example: dict,
    sources: dict,
    validator=None,
) -> tuple[list[str], list[str]]:
    errors, warnings = [], []
    out = example["output"]
    if not isinstance(out, dict):
        return ["output deve ser um objeto JSON"], warnings

    expected_channel = example.get("canal")
    target = out.get("target")

    if expected_channel and target != expected_channel:
        errors.append(
            f"target incompatível com o job: esperado "
            f"{expected_channel!r}, veio {target!r}"
        )
        return errors, warnings

    target, body, title = out.get("target"), out.get("body", ""), out.get("title", "")

    extra = set(out) - SCHEMA_KEYS
    if extra == {"source_link"} and target == "faq":
        warnings.append(
            "campo source_link fora do output_schema: o n8n deve removê-lo (ou o time adiciona ao schema)"
        )
    elif extra:
        errors.append(f"campos fora do output_schema: {sorted(extra)}")
    if SCHEMA_KEYS - set(out):
        errors.append(f"campos ausentes: {sorted(SCHEMA_KEYS - set(out))}")
    if target not in TARGETS_SCHEMA:
        warnings.append(
            f"target {target!r} ainda não está no enum do output_schema.json (decisão do time)"
        )
    validator = validator or item_schema()
    if validator is not None and target in TARGETS_SCHEMA:
        for err in validator.iter_errors({k: out[k] for k in SCHEMA_KEYS if k in out}):
            errors.append(f"output_schema: {err.message}")
    if target not in CHANNEL_LIMITS:
        errors.append(f"canal desconhecido: {target!r}")
        return errors, warnings

    min_c, max_c, min_h, max_h, max_e, max_title = CHANNEL_LIMITS[target]
    n_chars, hashtags, emojis = (
        len(body),
        HASHTAG_RE.findall(URL_RE.sub(" ", body)),
        EMOJI_RE.findall(body),
    )
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
        errors.append(
            f"menção com @ ({', '.join(sorted(set(mentions)))}): marcaria outra conta na rede; escreva o nome sem @"
        )
    for phrase in FORBIDDEN:
        if phrase in body.lower():
            errors.append(f"frase proibida (tom de voz): {phrase!r}")

    origin = [sources[i] for i in example.get("itens_de_origem", []) if i in sources]
    if len(origin) < len(example.get("itens_de_origem", [])):
        warnings.append("algum item de origem não foi encontrado nos arquivos de casos")
    needs_review = body.startswith(REVIEW_TAG)

    if target == "faq":
        if needs_review:
            if out.get("potential_engagement") != "low":
                errors.append("FAQ em revisão deve ter potential_engagement = 'low'")
            if "**Resposta curta:**" in body:
                errors.append("FAQ em revisão não pode trazer resposta")
        else:
            normalize_body = body
            for error_answer in ("**Resposta:**", "**Explicação:**", "**Solução:**"):
                if error_answer in normalize_body:
                    normalize_body = normalize_body.replace(error_answer, "**Resposta curta:**")
            for section in ("**Pergunta:**", "**Resposta curta:**", "**Fonte:**"):
                if section not in normalize_body:
                    errors.append(f"card de FAQ sem a seção {section}")
            if not FAQ_TITLE_START_RE.match(title):
                errors.append(
                    "title do FAQ deve começar com 'Como', 'Por que' ou 'O que'"
                )
            has_accepted = any(
                (i.get("raw_metadata") or {}).get("is_accepted")
                for item in origin
                for i in item["interactions"][1:]
            )
            if origin and not has_accepted:
                errors.append(
                    f"FAQ respondido sem resposta aceita na entrada: deveria começar com {REVIEW_TAG}"
                )

    from_so = any(item.get("source") == "stackoverflow" for item in origin)
    if (
        from_so
        and not needs_review
        and target in ("linkedin", "faq", "newsletter", "instagram")
        and "CC BY-SA" not in body
    ):
        errors.append("conteúdo do Stack Overflow sem linha de crédito (CC BY-SA 4.0)")

    if origin:
        missing = unknown_numbers(body, source_text(origin))
        if missing:
            errors.append(
                f"números que não aparecem na entrada (possível invenção): {missing}"
            )
    return errors, warnings


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser()
    parser.add_argument("arquivo", type=Path)
    args = parser.parse_args()

    if not args.arquivo.exists():
        print(f"Erro: Arquivo de saída não encontrado: {args.arquivo}")
        return 2

    examples = json.loads(args.arquivo.read_text(encoding="utf-8"))["exemplos"]
    sources, validator = load_sources(), item_schema()
    if validator is None:
        print(
            "(aviso: output_schema.json ou jsonschema indisponível; checagem do schema pulada)"
        )
    ok = 0
    for ex in examples:
        errors, warnings = check_output(ex, sources, validator)
        out = ex["output"]
        print(
            f"[{'OK   ' if not errors else 'FALHA'}] {ex['nome']} ({out.get('target')}, {len(out.get('body', ''))} caracteres)"
        )
        for e in errors:
            print(f"        erro: {e}")
        for w in warnings:
            print(f"        aviso: {w}")
        ok += not errors
    print(f"\n{ok}/{len(examples)} saídas aprovadas")
    return 0 if ok == len(examples) else 1


if __name__ == "__main__":
    sys.exit(main())
