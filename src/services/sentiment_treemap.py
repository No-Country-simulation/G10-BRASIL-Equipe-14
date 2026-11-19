"""Hierarchical distribution of interaction/theme associations."""

import json
from html import escape

import plotly.graph_objects as go

from src.config import TREEMAP_DIMENSIONS as DIMENSIONS
from src.design import FONT_STACK, LIGHT_PALETTE, category_tone


def build_treemap(frame, dimensions=DIMENSIONS, label_maps=None):
    """Keep totals stable as levels are hidden; each interaction/theme counts once."""
    unknown = set(dimensions) - set(DIMENSIONS)
    if unknown:
        raise ValueError(f"Categorias desconhecidas: {sorted(unknown)}")
    selected = list(dimensions)
    if len(set(selected)) != len(selected):
        raise ValueError("Cada categoria deve aparecer apenas uma vez na hierarquia.")
    if not selected:
        raise ValueError("Selecione ao menos uma categoria de organização.")
    rows = frame.drop_duplicates(["identity", "theme"], keep="last").copy()
    rows[selected] = rows[selected].fillna("Não informado")
    label_maps = label_maps or {}
    ids, parents, labels, values = ["root"], [""], ["Todas as avaliações"], [len(rows)]
    colors, paths = ["#FFFFFF"], ["Todas as avaliações"]

    for depth in range(1, len(selected) + 1):
        columns = selected[:depth]
        grouped = rows.groupby(columns, dropna=False, sort=True).size().reset_index(name="total")
        for record in grouped.to_dict("records"):
            path = [str(record[column]) for column in columns]
            translated = [str(label_maps.get(column, {}).get(value, value)) for column, value in zip(columns, path)]
            ids.append(json.dumps(path, ensure_ascii=False))
            parents.append(json.dumps(path[:-1], ensure_ascii=False) if depth > 1 else "root")
            labels.append(escape(translated[-1]))
            values.append(int(record["total"]))
            colors.append(category_tone(columns[-1], record[columns[-1]])[0])
            paths.append(" → ".join(escape(label) for label in translated))

    figure = go.Figure(go.Treemap(
        ids=ids, parents=parents, labels=labels, values=values,
        branchvalues="total", sort=True,
        marker=dict(colors=colors, line=dict(color="#FFFFFF", width=2)),
        textfont=dict(color=LIGHT_PALETTE["text"], size=14, family=FONT_STACK),
        texttemplate="%{label}<br>%{value} associações",
        customdata=paths,
        hovertemplate="%{customdata}<br>%{value} associações<br>%{percentRoot:.1%} do total<extra></extra>",
        pathbar=dict(visible=True),
        tiling=dict(pad=4),
    ))
    figure.update_layout(height=580, margin=dict(l=8, r=8, t=16, b=8), uniformtext=dict(minsize=12, mode="hide"))
    return figure
