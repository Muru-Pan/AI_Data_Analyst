"""
report_generator.py — Generates a downloadable HTML report using Jinja2.
"""

import os
import json
from datetime import datetime
import pandas as pd
import plotly.io as pio
from jinja2 import Environment, FileSystemLoader


def generate_html_report(
    dataset_name: str,
    eda_result: dict,
    kpi_cards: list[dict],
    anomaly_result: dict,
    insights: list[dict],
    figures: list,  # list of plotly Figure objects
    output_path: str | None = None,
) -> str:
    """
    Renders a Jinja2 HTML report and returns the HTML string.
    Optionally saves to output_path.
    """
    templates_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates")
    env = Environment(loader=FileSystemLoader(templates_dir), autoescape=True)
    template = env.get_template("report_template.html")

    # Serialize Plotly figures to HTML divs
    chart_htmls = []
    for fig in figures:
        try:
            html_div = pio.to_html(fig, full_html=False, include_plotlyjs=False)
            chart_htmls.append(html_div)
        except Exception:
            pass

    # Format KPI for template
    kpi_formatted = []
    for card in kpi_cards:
        growth = card.get("growth_pct")
        growth_str = f"{growth:+.1f}%" if growth is not None else "N/A"
        kpi_formatted.append({**card, "growth_str": growth_str})

    html = template.render(
        dataset_name=dataset_name,
        generated_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        shape=eda_result.get("shape", (0, 0)),
        total_nulls=eda_result.get("total_nulls", 0),
        null_pct=eda_result.get("null_pct", 0),
        column_types=eda_result.get("column_types", {}),
        kpi_cards=kpi_formatted,
        anomaly_count=anomaly_result.get("anomaly_count", 0),
        anomaly_summary=anomaly_result.get("summary", {}),
        insights=insights,
        chart_htmls=chart_htmls,
    )

    if output_path:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html)

    return html
