import json
from itertools import permutations

import pandas as pd
import pytest

from src.services.sentiment_treemap import DIMENSIONS, build_treemap
from src.design import category_tone


@pytest.fixture
def frame():
    return pd.DataFrame([
        dict(identity="a", source="mastodon", theme="docker",
             editorial="faq", sentiment="Neutral"),
        dict(identity="a", source="mastodon", theme="docker",
             editorial="faq", sentiment="Happy"),
        dict(identity="a", source="mastodon", theme="devops",
             editorial="newsletter", sentiment="Happy"),
        dict(identity="b", source="hackernews", theme="docker",
             editorial="faq", sentiment="Neutral"),
    ])


LEVEL_COMBINATIONS = [levels for size in range(
    1, 5) for levels in permutations(DIMENSIONS, size)]


@pytest.mark.parametrize("levels", LEVEL_COMBINATIONS)
def test_every_level_combination_preserves_totals_and_order(frame, levels):
    diagram = build_treemap(frame, levels).data[0]
    nodes = dict(zip(diagram.ids, diagram.values))
    assert nodes["root"] == 3  # a/docker, a/devops, b/docker
    assert len(nodes) == len(diagram.ids)
    first_level = {json.loads(node_id)[0] for node_id, parent in zip(
        diagram.ids, diagram.parents) if parent == "root"}
    assert first_level == set(frame[levels[0]])
    for node_id, parent, color in zip(diagram.ids, diagram.parents, diagram.marker.colors):
        if parent:
            assert parent in nodes
            path = json.loads(node_id)
            assert color == category_tone(levels[len(path) - 1], path[-1])[0]
            assert len(path) <= len(levels)
            assert parent == (json.dumps(
                path[:-1], ensure_ascii=False) if len(path) > 1 else "root")
    for node_id, total in nodes.items():
        children = [value for parent, value in zip(
            diagram.parents, diagram.values) if parent == node_id]
        if children:
            assert sum(children) == total
    if len(levels) == 4:
        latest = dict(source="mastodon", theme="docker",
                      editorial="faq", sentiment="Happy")
        earlier = dict(latest, sentiment="Neutral")
        assert json.dumps([latest[column] for column in levels]) in nodes
        assert json.dumps([earlier[column] for column in levels]) not in nodes


def test_localizes_labels_without_combining_different_paths(frame):
    diagram = build_treemap(frame, ["source", "theme"], {
                            "source": {"mastodon": "Mastodon"}}).data[0]
    assert "Mastodon" in diagram.labels
    assert list(diagram.labels).count("docker") == 2


def test_requires_an_active_level(frame):
    with pytest.raises(ValueError, match="ao menos uma categoria"):
        build_treemap(frame, [])


def test_rejects_duplicate_levels(frame):
    with pytest.raises(ValueError, match="apenas uma vez"):
        build_treemap(frame, ["source", "source"])


def test_empty_frame_and_missing_category(frame):
    assert build_treemap(frame.iloc[:0]).data[0].values == (0,)
    frame.loc[0, "sentiment"] = None
    frame = frame.drop(index=1)
    assert "Não informado" in build_treemap(frame).data[0].labels


def test_category_colors_do_not_change_when_filtering(frame):
    before = build_treemap(frame, ["source", "sentiment"]).data[0]
    filtered = build_treemap(frame[frame.source.eq("mastodon")], [
                             "sentiment", "source"]).data[0]
    assert before.marker.colors[before.labels.index(
        "Happy")] == filtered.marker.colors[filtered.labels.index("Happy")]
    assert before.marker.colors[before.labels.index(
        "mastodon")] == filtered.marker.colors[filtered.labels.index("mastodon")]
    assert category_tone(
        "theme", "novo-tema") == category_tone("theme", "novo-tema")
