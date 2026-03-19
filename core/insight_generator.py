"""
insight_generator.py — AI-powered business insights via Groq LLaMA3.
"""

import os
import json
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
MODEL = "llama-3.3-70b-versatile"


def generate_insights(
    eda_result: dict,
    kpi_cards: list[dict],
    anomaly_summary: dict,
    correlation_pairs: list[dict],
    dataset_name: str = "Dataset",
) -> list[dict]:
    """
    Sends EDA summary, KPIs, anomalies, and correlations to Groq LLaMA3.
    Returns a list of up to 8 actionable insight dicts:
      [{title, insight, severity, action}, ...]
    severity: 'high', 'medium', 'low'
    """
    if not GROQ_API_KEY:
        return [{"title": "API Key Missing", "insight": "Set GROQ_API_KEY in .env to enable AI insights.",
                 "severity": "high", "action": "Add your Groq API key to the .env file."}]

    from groq import Groq
    client = Groq(api_key=GROQ_API_KEY)

    # Build a compact summary for the prompt
    kpi_str = json.dumps(kpi_cards[:5], default=str, indent=2) if kpi_cards else "No KPIs detected."
    anomaly_str = json.dumps({k: v for k, v in list(anomaly_summary.items())[:5]}, indent=2) if anomaly_summary else "No anomalies."
    top_corr = json.dumps(correlation_pairs[:5], indent=2) if correlation_pairs else "No correlations."
    numeric_stats = {k: v for k, v in list(eda_result.get("numeric_stats", {}).items())[:5]}
    stats_str = json.dumps(numeric_stats, default=str, indent=2)

    user_prompt = f"""Dataset: {dataset_name}
Shape: {eda_result.get("shape", "unknown")}
Total nulls: {eda_result.get("total_nulls", 0)}
Column types: {eda_result.get("column_types", {})}

KPI Metrics:
{kpi_str}

Top Anomalies:
{anomaly_str}

Top Correlations:
{top_corr}

Key Statistics (sample):
{stats_str}

Generate 6–8 actionable business insights as a JSON array. Each item must have:
- "title": short title (max 8 words)
- "insight": 1-2 sentence explanation of the finding
- "severity": "high", "medium", or "low"
- "action": specific recommended next step

Return ONLY valid JSON array. No markdown, no extra text."""

    system_prompt = "You are a senior business intelligence analyst. Analyze the provided data metrics and generate clear, concise, and actionable business insights."

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.3,
            max_tokens=1500,
        )
        raw = response.choices[0].message.content.strip()

        # Strip markdown if present
        if raw.startswith("```"):
            parts = raw.split("```")
            raw = parts[1] if len(parts) > 1 else raw
            if raw.lower().startswith("json"):
                raw = raw[4:]

        insights = json.loads(raw)
        return insights if isinstance(insights, list) else []

    except Exception as e:
        return [{
            "title": "Analysis Error",
            "insight": f"Could not generate insights: {e}",
            "severity": "medium",
            "action": "Check your Groq API key and try again.",
        }]
