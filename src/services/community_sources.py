from copy import deepcopy

_COMMUNITY_SOURCES_SAMPLE = [
    {
        "id": "lote-se-001",
        "source_key": "stackoverflow",
        "source": "Stack Exchange",
        "url": "https://stackoverflow.com/questions/tagged/duckdb",
        "period": ("2026-10-13", "2026-10-20"),
        "interactions": 128,
        "authors": 94,
        "with_content": 121,
        "avg_score": 3.4,
        "top_tags": [("duckdb", 52), ("python", 41), ("json-schema", 18), ("pandas", 15), ("sql", 12)],
    },
    {
        "id": "lote-ma-002",
        "source_key": "mastodon",
        "source": "Mastodon",
        "url": "https://mastodon.social/tags/opensource",
        "period": ("2026-10-13", "2026-10-20"),
        "interactions": 342,
        "authors": 207,
        "with_content": 342,
        "avg_score": 7.9,
        "top_tags": [("opensource", 120), ("python", 64), ("llm", 58), ("devops", 33), ("observability", 21)],
    },
    {
        "id": "lote-hn-003",
        "source_key": "hackernews",
        "source": "Hacker News",
        "url": "https://news.ycombinator.com/",
        "period": ("2026-10-13", "2026-10-20"),
        "interactions": 76,
        "authors": 61,
        "with_content": 49,
        "avg_score": 112.6,
        "top_tags": [("show_hn", 24), ("story", 76), ("ai", 19), ("rust", 11)],
    },
    {
        "id": "lote-se-004",
        "source_key": "stackoverflow",
        "source": "Stack Exchange",
        "url": "https://stackoverflow.com/questions/tagged/n8n",
        "period": ("2026-10-06", "2026-10-13"),
        "interactions": 87,
        "authors": 70,
        "with_content": 84,
        "avg_score": 2.1,
        "top_tags": [("n8n", 44), ("docker", 29), ("webhook", 17), ("automation", 14)],
    },
]


def list_community_sources() -> list[dict]:
    return deepcopy(_COMMUNITY_SOURCES_SAMPLE)


def get_community_source(batch_id: str) -> dict:
    return next(b for b in list_community_sources() if b["id"] == batch_id)
