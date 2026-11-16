import pandas as pd

from src.services.sentiment_sankey import build_sankey


def test_flows_preserve_volume_at_each_theme():
    frame = pd.DataFrame([
        {"identity": "a", "source": "mastodon", "theme": "docker", "editorial": "faq"},
        {"identity": "a", "source": "mastodon", "theme": "docker", "editorial": "faq"},
        {"identity": "a", "source": "mastodon", "theme": "devops", "editorial": "newsletter"},
        {"identity": "b", "source": "hackernews", "theme": "docker", "editorial": "discard"},
    ])
    frame["sentiment"] = "Neutral"
    diagram = build_sankey(frame).data[0]
    assert sum(diagram.link.value) == 9
    assert diagram.node.color[diagram.node.label.index("Mastodon")] == "#293943"
    assert diagram.node.color[diagram.node.label.index("Hacker News")] == "#2DAC8A"
    assert "Neutral" in diagram.node.label
    for i, label in enumerate(diagram.node.label):
        if label in {"docker", "devops", "FAQ", "Newsletter", "Descarte"}:
            incoming = sum(v for t, v in zip(diagram.link.target, diagram.link.value) if t == i)
            outgoing = sum(v for s, v in zip(diagram.link.source, diagram.link.value) if s == i)
            assert incoming == outgoing
