"""Exercise navigation and editorial actions without calling external services."""

from streamlit.testing.v1 import AppTest

from src.config import PROJECT_ROOT, STREAMLIT_MAIN_PATH


def test_all_pages_render_with_only_light_appearance():
    app = AppTest.from_file(str(STREAMLIT_MAIN_PATH), default_timeout=30).run()
    assert not app.exception
    for page in ["home", "ingestion", "community_sources", "sentiment_dashboard", "curation"]:
        app.switch_page(f"views/{page}.py").run()
        assert not app.exception, (page, app.exception)
        assert all(widget.label != "Aparência" for widget in app.sidebar.selectbox)
        assert all("�" not in title.value for title in app.title)


def test_text_and_action_colors_have_readable_contrast():
    from src.ui import tokens

    def luminance(color):
        channels = [int(color[i:i + 2], 16) / 255 for i in (1, 3, 5)]
        linear = [v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4 for v in channels]
        return sum(v * weight for v, weight in zip(linear, [0.2126, 0.7152, 0.0722]))

    palette = tokens()
    for foreground in ["text", "muted", "link", "action"]:
        for background in ["bg", "surface", "soft"]:
            light, dark = sorted([luminance(palette[foreground]), luminance(palette[background])], reverse=True)
            assert (light + 0.05) / (dark + 0.05) >= 4.5, (foreground, background)
    assert (luminance("#FFFFFF") + 0.05) / (luminance(palette["action"]) + 0.05) >= 4.5


def test_review_keeps_edits_and_allows_undo():
    app = AppTest.from_file(str(STREAMLIT_MAIN_PATH), default_timeout=30).run()
    app.switch_page("views/curation.py").run()
    content_id = "pkg_2026_w42_001_0"
    app.text_area(key=f"body_{content_id}").set_value("Conteúdo revisado pela equipe.").run()
    app.button(key=f"ok_{content_id}").click().run()
    assert not app.exception
    item = app.session_state["packages"][0]["suggested_content"][0]
    assert item["review_status"] == "approved"
    assert item["body"] == "Conteúdo revisado pela equipe."
    app.radio(key="curation_status_pkg_2026_w42_001").set_value("approved").run()
    app.button(key=f"undo_{content_id}").click().run()
    assert not app.exception
    assert item["review_status"] == "pending"


def test_treemap_positions_swap_and_respect_disabled_categories(monkeypatch):
    import pandas as pd
    from src.services.sentiment_dashboard import normalize

    rows = list(normalize(
        {"source": "mastodon.social", "post_id": "1", "clean_text": "Texto", "sentiment": "Happy"},
        "result_mastodon_docker.json", "2026-11-15",
    ))
    monkeypatch.setattr("src.services.sentiment_dashboard.load_snapshot", lambda: (pd.DataFrame(rows), {"records": 1, "conflicts": 0}))
    app = AppTest.from_file(str(STREAMLIT_MAIN_PATH), default_timeout=30).run()
    app.switch_page("views/sentiment_dashboard.py").run()
    app.selectbox(key="treemap_position_source").select(4).run()
    assert not app.exception
    assert app.selectbox(key="treemap_position_sentiment").value == 1
    assert app.session_state["treemap_order"] == ["sentiment", "theme", "editorial", "source"]
    app.checkbox(key="treemap_theme").uncheck().run()
    assert app.session_state["treemap_applied_levels"] == ["source", "theme", "editorial", "sentiment"]
    assert any(c.value == "Hierarquia atual: Fonte → Tema da coleta → Editorial → Sentimento" for c in app.caption)
    app.button(key="treemap_apply").click().run()
    assert any(c.value == "Hierarquia atual: Sentimento → Editorial → Fonte" for c in app.caption)
    app.selectbox(key="treemap_position_editorial").select(1).run()
    assert not app.exception
    assert app.selectbox(key="treemap_position_sentiment").value == 3
    assert any(c.value == "Hierarquia atual: Sentimento → Editorial → Fonte" for c in app.caption)
    app.button(key="treemap_apply").click().run()
    assert any(c.value == "Hierarquia atual: Editorial → Sentimento → Fonte" for c in app.caption)
    for category in ["source", "editorial", "sentiment"]:
        app.checkbox(key=f"treemap_{category}").uncheck().run()
    assert len(app.get("plotly_chart")) == 1
    app.button(key="treemap_apply").click().run()
    assert not app.exception
    assert not app.get("plotly_chart")
    assert any("Selecione ao menos uma categoria" in message.value for message in app.info)


def test_local_and_docker_share_official_theme():
    import tomllib
    from src.design import LIGHT_PALETTE

    root = PROJECT_ROOT
    local = tomllib.loads((root / ".streamlit/config.toml").read_text(encoding="utf-8"))
    docker = tomllib.loads((root / ".setup/docker/streamlit/config.toml").read_text(encoding="utf-8"))
    assert local["theme"] == docker["theme"]
    assert local["client"] == docker["client"]
    assert local["theme"]["primaryColor"] == LIGHT_PALETTE["action"]
    assert local["theme"]["backgroundColor"] == LIGHT_PALETTE["bg"]
    assert docker["server"]["maxUploadSize"] == 10


def test_categorical_and_operational_text_contrast():
    from src.design import CATEGORY_TONES, OPERATIONAL_TONES

    def luminance(color):
        values = [int(color[i:i + 2], 16) / 255 for i in (1, 3, 5)]
        return sum(weight * (v / 12.92 if v <= .04045 else ((v + .055) / 1.055) ** 2.4) for weight, v in zip([.2126, .7152, .0722], values))

    for name, (background, foreground) in {**CATEGORY_TONES, **OPERATIONAL_TONES}.items():
        assert (luminance(background) + .05) / (luminance(foreground) + .05) >= 4.5, name
