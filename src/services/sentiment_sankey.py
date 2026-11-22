"""Fluxo das avaliações por fonte, tema da coleta e destino editorial."""

import plotly.graph_objects as go

from src.config import EDITORIALS, SENTIMENTS, THEMES, SOURCE_LABELS, EDITORIAL_LABELS
from src.design import (
    SANKEY_DEFAULT_COLOR,
    SANKEY_LEVEL_COLORS,
    SANKEY_NODE_COLORS,
    SANKEY_SOURCE_COLORS,
)


def build_sankey(frame):
    # Uma interação pode participar de várias buscas; cada associação é um fluxo.
    rows = frame.drop_duplicates(["identity", "theme"], keep="last")
    dimensions = ["source", "theme", "editorial", "sentiment"]
    orders = [list(SOURCE_LABELS), THEMES, EDITORIALS,
              SENTIMENTS + ["Sem avaliação"]]
    labels, colors, xs, ys, indexes = [], [], [], [], {}
    for level, (dimension, order) in enumerate(zip(dimensions, orders)):
        present = set(rows[dimension])
        values = [value for value in order if value in present] + \
            sorted(present - set(order))
        for i, value in enumerate(values):
            indexes[dimension, value] = len(labels)
            labels.append(SOURCE_LABELS.get(value, value) if level == 0 else EDITORIAL_LABELS.get(
                value, value) if level == 2 else value)
            level_color = SANKEY_LEVEL_COLORS.get(
                dimension, SANKEY_DEFAULT_COLOR)
            category_colors = SANKEY_NODE_COLORS.get(dimension, {})
            colors.append(category_colors.get(value, level_color))
            xs.append([0.01, 0.34, 0.67, 0.99][level])
            ys.append((i + 0.5) / len(values))
    sources, targets, totals, link_colors, origins = [], [], [], [], []
    for left, right in zip(dimensions, dimensions[1:]):
        grouping = list(dict.fromkeys(["source", left, right]))
        counts = rows.groupby(grouping).size().reset_index(name="total")
        for record in counts.to_dict("records"):
            a, b, origin, count = record[left], record[right], record["source"], record["total"]
            sources.append(indexes[left, a])
            targets.append(indexes[right, b])
            totals.append(int(count))
            hex_color = SANKEY_SOURCE_COLORS.get(
                origin, SANKEY_DEFAULT_COLOR).lstrip("#")
            r, g, blue = (int(hex_color[i:i + 2], 16) for i in (0, 2, 4))
            link_colors.append(f"rgba({r}, {g}, {blue}, 0.4)")
            origins.append(SOURCE_LABELS.get(origin, origin))
    figure = go.Figure(go.Sankey(
        arrangement="fixed",
        node={"label": labels, "color": colors, "x": xs, "y": ys, "pad": 22, "thickness": 20,
              "hovertemplate": "%{label}<br>%{value} associações<extra></extra>"},
        link={"source": sources, "target": targets, "value": totals, "color": link_colors, "customdata": origins,
              "hovertemplate": "%{source.label} → %{target.label}<br>Fonte: %{customdata}<br>%{value} associações<extra></extra>"},
    ))
    figure.update_layout(height=max(520, len(set(rows.theme)) * 65),
                         margin={"l": 15, "r": 15, "t": 40, "b": 20}, font={"size": 13})
    for x, text in [(0, "Fonte"), (0.34, "Tema da coleta"), (0.67, "Destino editorial sugerido"), (1, "Sentimento")]:
        figure.add_annotation(x=x, y=1.1, xref="paper",
                              yref="paper", text=text, showarrow=False)
    return figure
