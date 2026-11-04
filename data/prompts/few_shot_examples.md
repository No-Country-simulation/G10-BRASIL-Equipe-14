# Exemplos de Referência (Few-Shot)

## Exemplo 1 — Conquista de vaga (success_case)

### Entrada:

```json
{
    "id": "mst-001",
    "source": "mastodon",
    "url": "[https://mastodon.social/@ana_dev/1](https://mastodon.social/@ana_dev/1)",
    "interactions": [
        {
            "author": "ana_dev",
            "title": null,
            "content": "Depois de 8 meses estudando Python e montando meu portfólio com projetos de IA na OCI, fui contratada como Analista de Dados Jr na Totvs! Obrigada a todos da comunidade que revisaram meu currículo 💙",
            "tags": ["carreira", "python"],
            "created_at": "2026-10-19T14:00:00Z"
        }
    ]
}
```

### Saída:

```json
{
    "id": "mst-001",
    "source": "mastodon",
    "type": "job_achievement",
    "sentiment": "positive",
    "topic_category": "career",
    "topics": ["Primeira vaga em dados", "Portfólio de IA na OCI"],
    "original_language": "pt",
    "has_answer": false,
    "relevance_score": 95,
    "suggested_route": "success_case",
    "summary": "Membro conquistou vaga de Analista de Dados Jr após 8 meses de estudo e portfólio de IA na OCI.",
    "justification": "Faixa 80–100: conquista com empresa e cargo; regra 4 (success_case)."
}
```

## Exemplo 2 — Dúvida técnica com resposta aceita (faq)

### Entrada:

```json
{
    "id": "79612345",
    "source": "stackoverflow",
    "url": "[https://stackoverflow.com/questions/79612345](https://stackoverflow.com/questions/79612345)",
    "interactions": [
        {
            "author": "jdoe_dev",
            "title": "How to load JSON with dynamic schema into DuckDB?",
            "content": "How do I validate a JSON payload against a schema before loading it into DuckDB?",
            "tags": ["python", "json-schema", "duckdb"],
            "created_at": "2026-10-19T14:32:00Z",
            "raw_metadata": {
                "score": 12,
                "view_count": 340,
                "is_answered": true
            }
        },
        {
            "author": "asmith_qa",
            "content": "You can use the `jsonschema` library to validate the payload before calling `duckdb.read_json`.",
            "created_at": "2026-10-19T15:10:00Z",
            "raw_metadata": { "score": 7, "is_accepted": true }
        }
    ]
}
```

### Saída:

```json
{
    "id": "79612345",
    "source": "stackoverflow",
    "type": "technical_question",
    "sentiment": "neutral",
    "topic_category": "data",
    "topics": ["Validação com JSON Schema", "DuckDB"],
    "original_language": "en",
    "has_answer": true,
    "relevance_score": 88,
    "suggested_route": "faq",
    "summary": "Como validar um JSON com JSON Schema antes de carregá-lo no DuckDB; a resposta aceita sugere a biblioteca jsonschema.",
    "justification": "Faixa 80–100: resposta aceita e score 12 (>= 10); regra 5 (faq)."
}
```

## Exemplo 3 — Ruído / Spam (discard)

### Entrada:

```json
{
    "id": "mst-777",
    "source": "mastodon",
    "url": "[https://mastodon.social/@growth_bot/777](https://mastodon.social/@growth_bot/777)",
    "interactions": [
        {
            "author": "growth_bot",
            "title": null,
            "content": "Sigam meu perfil que eu sigo de volta!! 🚀🚀 #follow4follow",
            "created_at": "2026-10-19T10:00:00Z"
        }
    ]
}
```

### Saída:

```json
{
    "id": "mst-777",
    "source": "mastodon",
    "type": "noise",
    "sentiment": "neutral",
    "topic_category": "other",
    "topics": ["Spam"],
    "original_language": "pt",
    "has_answer": false,
    "relevance_score": 3,
    "suggested_route": "discard",
    "summary": "Pedido de seguidores sem relação com tecnologia.",
    "justification": "Faixa 0–19: spam; regra 1 (discard)."
}
```

## Exemplo 4 — Dúvida técnica com frustração (moderation)

### Entrada:

```json
{
    "id": "mst-002",
    "source": "mastodon",
    "url": "[https://mastodon.social/@bia_ml/2](https://mastodon.social/@bia_ml/2)",
    "interactions": [
        {
            "author": "bia_ml",
            "title": null,
            "content": "Faz uma semana que meu notebook trava sempre que rodo qualquer modelo no Ollama. Já reinstalei tudo e nada. Tô quase largando IA local.",
            "created_at": "2026-10-20T22:00:00Z"
        }
    ]
}
```

### Saída:

```json
{
    "id": "mst-002",
    "source": "mastodon",
    "type": "technical_question",
    "sentiment": "negative",
    "topic_category": "ai_ml",
    "topics": ["Ollama travando", "IA local"],
    "original_language": "pt",
    "has_answer": false,
    "relevance_score": 44,
    "suggested_route": "moderation",
    "summary": "Membro frustrado: o notebook trava ao rodar modelos no Ollama mesmo após reinstalar tudo.",
    "justification": "Faixa 40–59: dúvida sem resposta; regra 2 (moderation) por frustração explícita."
}
```
