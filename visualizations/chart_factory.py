"""
chart_factory.py — Plotly chart factory for the AI Data Analyst dashboard.
"""

import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go


TEMPLATE = "plotly_dark"
COLOR_PALETTE = px.colors.qualitative.Vivid


def histogram(df: pd.DataFrame, col: str, nbins: int = 30) -> go.Figure:
    fig = px.histogram(
        df, x=col, nbins=nbins, title=f"Distribution of {col}",
        template=TEMPLATE, color_discrete_sequence=COLOR_PALETTE,
        marginal="box",
    )
    fig.update_layout(bargap=0.05)
    return fig


def bar_chart(df: pd.DataFrame, x: str, y: str, color: str | None = None) -> go.Figure:
    fig = px.bar(
        df, x=x, y=y, color=color,
        title=f"{y} by {x}",
        template=TEMPLATE,
        color_discrete_sequence=COLOR_PALETTE,
        barmode="group",
    )
    fig.update_layout(xaxis_tickangle=-35)
    return fig


def line_chart(df: pd.DataFrame, x: str, y: str | list[str], color: str | None = None) -> go.Figure:
    fig = px.line(
        df, x=x, y=y, color=color,
        title=f"{y} over {x}" if isinstance(y, str) else f"Trends over {x}",
        template=TEMPLATE,
        color_discrete_sequence=COLOR_PALETTE,
        markers=True,
    )
    return fig


def scatter_plot(df: pd.DataFrame, x: str, y: str, color: str | None = None, size: str | None = None) -> go.Figure:
    fig = px.scatter(
        df, x=x, y=y, color=color, size=size,
        title=f"{y} vs {x}",
        template=TEMPLATE,
        color_discrete_sequence=COLOR_PALETTE,
    )
    return fig


def heatmap(corr_matrix: pd.DataFrame) -> go.Figure:
    fig = go.Figure(data=go.Heatmap(
        z=corr_matrix.values,
        x=corr_matrix.columns.tolist(),
        y=corr_matrix.index.tolist(),
        colorscale="RdBu",
        zmid=0,
        text=np.round(corr_matrix.values, 2),
        texttemplate="%{text}",
        showscale=True,
    ))
    fig.update_layout(
        title="Correlation Heatmap",
        template=TEMPLATE,
        xaxis_tickangle=-35,
    )
    return fig


def box_plot(df: pd.DataFrame, col: str, group_by: str | None = None) -> go.Figure:
    fig = px.box(
        df, y=col, x=group_by,
        title=f"Box Plot — {col}" + (f" by {group_by}" if group_by else ""),
        template=TEMPLATE,
        color=group_by,
        color_discrete_sequence=COLOR_PALETTE,
        points="outliers",
    )
    return fig


def pie_chart(df: pd.DataFrame, names: str, values: str) -> go.Figure:
    agg = df.groupby(names)[values].sum().reset_index()
    fig = px.pie(
        agg, names=names, values=values,
        title=f"{values} Composition by {names}",
        template=TEMPLATE,
        color_discrete_sequence=COLOR_PALETTE,
        hole=0.35,
    )
    fig.update_traces(textposition="inside", textinfo="percent+label")
    return fig


def area_chart(df: pd.DataFrame, x: str, y: str) -> go.Figure:
    fig = px.area(
        df, x=x, y=y,
        title=f"{y} Area Chart over {x}",
        template=TEMPLATE,
        color_discrete_sequence=COLOR_PALETTE,
    )
    return fig


def null_heatmap(null_map: dict) -> go.Figure:
    """Bar chart of null counts per column."""
    if not null_map:
        fig = go.Figure()
        fig.update_layout(title="No missing values detected!", template=TEMPLATE)
        return fig
    cols = list(null_map.keys())
    counts = list(null_map.values())
    fig = go.Figure(go.Bar(
        x=cols, y=counts,
        marker_color="#EF553B",
        text=counts,
        textposition="outside",
    ))
    fig.update_layout(
        title="Missing Values per Column",
        xaxis_title="Column",
        yaxis_title="Null Count",
        template=TEMPLATE,
        xaxis_tickangle=-35,
    )
    return fig


def anomaly_scatter(df: pd.DataFrame, col: str, flag_col: str) -> go.Figure:
    """Scatter showing normal vs anomaly points."""
    normal = df[~df[flag_col]]
    anomalies = df[df[flag_col]]

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=normal.index, y=normal[col],
        mode="markers", name="Normal",
        marker=dict(color="#00CC96", size=5, opacity=0.6),
    ))
    fig.add_trace(go.Scatter(
        x=anomalies.index, y=anomalies[col],
        mode="markers", name="Anomaly",
        marker=dict(color="#EF553B", size=9, symbol="x"),
    ))
    fig.update_layout(
        title=f"Anomaly Detection — {col}",
        xaxis_title="Index",
        yaxis_title=col,
        template=TEMPLATE,
    )
    return fig


def trend_line_chart(grouped_df: pd.DataFrame, col: str, freq_label: str) -> go.Figure:
    """Plots aggregated trend with rolling average overlay."""
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=grouped_df["period"], y=grouped_df[col],
        name=col, marker_color="#636EFA", opacity=0.7,
    ))
    if "rolling_avg" in grouped_df.columns:
        fig.add_trace(go.Scatter(
            x=grouped_df["period"], y=grouped_df["rolling_avg"],
            mode="lines+markers", name="Rolling Avg",
            line=dict(color="#FFA15A", width=2),
        ))
    fig.update_layout(
        title=f"{freq_label} Trend — {col}",
        template=TEMPLATE,
        xaxis_title="Period",
        yaxis_title=col,
        barmode="overlay",
    )
    return fig
