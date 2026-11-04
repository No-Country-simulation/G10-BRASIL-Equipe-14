from copy import deepcopy

_OUTPUT_PACKAGES_SAMPLE = [
    {
        "package_id": "pkg_2026_w42_001",
        "linked_batch_id": "lote-se-001",
        "status": "success",
        "reference_period": "2026-10-13T00:00:00Z/2026-10-20T00:00:00Z",
        "processing_summary": {
            "total_interactions": 128,
            "sources_breakdown": {"stackoverflow": 128},
            "predominant_feeling": "neutral",
            "main_topics": ["DuckDB / Engenharia de dados", "JSON Schema / Validação", "pandas"],
        },
        "suggested_content": [
            {
                "target": "linkedin",
                "title": "Caso de sucesso: migração para DuckDB",
                "body": "Uma equipe reduziu de 40 min para 90 s o processamento diário de logs ao "
                        "migrar do pandas para o DuckDB. Veja o que aprendemos com a comunidade.\n\n"
                        "#DuckDB #DataEngineering #Comunidade",
                "potential_engagement": "high",
            },
            {
                "target": "faq",
                "title": "Como ler JSON aninhado no DuckDB?",
                "body": "Use json_extract e unnest para achatar arrays aninhados direto no SQL.",
                "potential_engagement": "low",
            },
            {
                "target": "newsletter",
                "title": "Perguntas mais votadas da semana",
                "body": "As dúvidas sobre DuckDB e validação de JSON que mais geraram discussão no "
                        "Stack Exchange, com as respostas aceitas.",
                "potential_engagement": "medium",
            },
        ],
    },
    {
        "package_id": "pkg_2026_w42_002",
        "linked_batch_id": "lote-ma-002",
        "status": "success",
        "reference_period": "2026-10-13T00:00:00Z/2026-10-20T00:00:00Z",
        "processing_summary": {
            "total_interactions": 342,
            "sources_breakdown": {"mastodon": 342},
            "predominant_feeling": "positive",
            "main_topics": ["Open source", "LLMs em code review", "Observabilidade"],
        },
        "suggested_content": [
            {
                "target": "x/twitter",
                "title": "Projeto open source ganha tração",
                "body": "Um mantenedor brasileiro chegou a 1k estrelas após documentar bem o onboarding. "
                        "#opensource #comunidade",
                "potential_engagement": "high",
            },
            {
                "target": "discord",
                "title": "Qual a sua dica de documentação?",
                "body": "A semana mostrou que onboarding bem documentado atrai contribuidores. "
                        "Quem mais tem dicas para compartilhar?",
                "potential_engagement": "medium",
            },
            {
                "target": "newsletter",
                "title": "O que a comunidade discutiu esta semana",
                "body": "Três temas dominaram as conversas: observabilidade com OpenTelemetry, custos "
                        "de nuvem e o uso de LLMs em code review.",
                "potential_engagement": "medium",
            },
        ],
    },
    {
        "package_id": "pkg_2026_w42_003",
        "linked_batch_id": "lote-hn-003",
        "status": "suspended",
        "reference_period": "2026-10-13T00:00:00Z/2026-10-20T00:00:00Z",
        "processing_summary": {
            "total_interactions": 76,
            "sources_breakdown": {"hackernews": 76},
            "predominant_feeling": "positive",
            "main_topics": ["Show HN", "IA", "Rust"],
        },
        "suggested_content": [
            {
                "target": "blog",
                "title": "Show HN da semana: benchmark open source de LLMs",
                "body": "Um novo conjunto de benchmarks abertos para LLMs chamou a atenção da "
                        "comunidade, com 145 pontos e 42 comentários.",
                "potential_engagement": "high",
            },
            {
                "target": "linkedin",
                "title": "Rust e IA: o que o Hacker News está comentando",
                "body": "Ferramentas de IA escritas em Rust aparecem cada vez mais nas discussões da "
                        "semana. #Rust #IA",
                "potential_engagement": "medium",
            },
        ],
    },
    {
        "package_id": "pkg_2026_w41_001",
        "linked_batch_id": "lote-se-004",
        "status": "success",
        "reference_period": "2026-10-06T00:00:00Z/2026-10-13T00:00:00Z",
        "processing_summary": {
            "total_interactions": 87,
            "sources_breakdown": {"stackoverflow": 87},
            "predominant_feeling": "negative",
            "main_topics": ["n8n / Webhooks", "Docker Compose / Volumes"],
        },
        "suggested_content": [
            {
                "target": "faq",
                "title": "FAQ: containers e volumes no Docker Compose",
                "body": "As dúvidas mais frequentes sobre persistência de dados com volumes nomeados "
                        "e bind mounts, com exemplos prontos para copiar.",
                "potential_engagement": "low",
            },
            {
                "target": "blog",
                "title": "n8n webhook retorna 404 em produção?",
                "body": "O endpoint de teste e o de produção são diferentes: ative o workflow antes de "
                        "chamar a URL /webhook/.",
                "potential_engagement": "medium",
            },
        ],
    },
]


def list_output_packages() -> list[dict]:
    return deepcopy(_OUTPUT_PACKAGES_SAMPLE)
