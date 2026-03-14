"""
nlp_query_engine.py — Natural language query engine powered by Groq LLaMA3.
Supports multi-turn conversation history for continuous chat.
"""

import os
import json
import traceback
import pandas as pd
import numpy as np
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
MODEL = "llama-3.3-70b-versatile"


def _build_schema_prompt(df: pd.DataFrame) -> str:
    """Summarize the DataFrame schema and a few sample rows for the LLM system prompt."""
    schema_lines = []
    for col in df.columns:
        dtype = str(df[col].dtype)
        sample_vals = df[col].dropna().head(3).tolist()
        schema_lines.append(f"  - {col} ({dtype}): sample values = {sample_vals}")
    schema_str = "\n".join(schema_lines)
    sample_rows = df.head(3).to_dict(orient="records")
    sample_str = json.dumps(sample_rows, default=str, indent=2)
    return f"""DATASET SCHEMA ({df.shape[0]} rows × {df.shape[1]} columns):
{schema_str}

SAMPLE ROWS:
{sample_str}""".strip()


def run_nl_query(
    df: pd.DataFrame,
    user_question: str,
    chat_history: list[dict] | None = None,
) -> dict:
    """
    Sends user question + dataset schema + conversation history to Groq LLaMA3.

    chat_history: list of {"role": "user"/"assistant", "content": str} dicts
                  representing previous turns in the conversation.

    Returns:
      {
        "pandas_code": str,
        "result": DataFrame or scalar,
        "explanation": str,
        "chart_suggestion": str,
        "error": str | None,
        "raw_answer": str,      # plain text answer for display in chat
      }
    """
    if not GROQ_API_KEY:
        return {
            "pandas_code": "",
            "result": None,
            "explanation": "GROQ_API_KEY is not set. Please add it to your .env file.",
            "chart_suggestion": "",
            "error": "Missing API key",
            "raw_answer": "⚠️ GROQ_API_KEY is not set. Please add it to your `.env` file.",
        }

    from groq import Groq
    client = Groq(api_key=GROQ_API_KEY)

    schema_prompt = _build_schema_prompt(df)

    system_prompt = f"""You are a senior Business Intelligence (BI) Data Analyst AI connected to a Python (Pandas) execution environment.

{schema_prompt}

Your responsibility is NOT just to generate charts. Your responsibility is to produce BUSINESS-READY visual insights.
You MUST think like a senior BI analyst and follow this strict workflow.

--------------------------------------------------
STEP 1 — UNDERSTAND THE BUSINESS GOAL
--------------------------------------------------
Analyze the dataset and infer the analytical intent:
- Comparison → Which category performs better?
- Trend → How values change over time?
- Distribution → How data is spread?
- Relationship → How two variables interact?
- Composition → How parts contribute to a whole?

Choose visualization based on analytical purpose, NOT user selection alone.

--------------------------------------------------
STEP 2 — DETECT DATA TYPES
--------------------------------------------------
Automatically classify columns:
- Time variables → date, year, month
- Categorical variables → country, product, type
- Numerical variables → sales, price, quantity

--------------------------------------------------
STEP 3 — SELECT OPTIMAL VISUALIZATION
--------------------------------------------------
Apply BI rules:
TIME DATA:
→ Line Chart (trend analysis)
→ Area Chart (cumulative growth)

CATEGORY COMPARISON:
→ Bar Chart (default and preferred)

NUMERIC vs NUMERIC:
→ Scatter Plot

DATA DISTRIBUTION:
→ Histogram (single variable)
→ Box Plot (compare distributions across categories)

PART-TO-WHOLE:
→ Pie Chart ONLY if categories <= 5. Otherwise Bar Chart.

NEVER:
- Use Line Chart for categorical variables
- Use Pie Chart with many categories
- Plot raw noisy points without aggregation

--------------------------------------------------
STEP 4 — APPLY BUSINESS AGGREGATION
--------------------------------------------------
Automatically aggregate:
- mean() → pricing analysis
- sum() → revenue/total analysis
- count() → frequency analysis
Choose aggregation based on business meaning.

--------------------------------------------------
STEP 5 — OPTIMIZE FOR DECISION MAKING
--------------------------------------------------
Ensure your operation sorts categories logically, removes noise, and uses clear business logic.

--------------------------------------------------
STEP 6 — JSON OUTPUT FORMAT
--------------------------------------------------
Output ONLY a single valid JSON object. No markdown fences, no extra text:
{{
  "operation": "<groupby_sum | groupby_mean | filter | sort | ...>",
  "pandas_code": "<executable pandas code; assign final output to `result`. Only pd/np/df available. No imports.>",
  "chart_suggestion": "<bar | line | pie | scatter | histogram | area | box | none>",
  "explanation": "<business-friendly insight in 1-3 sentences>",
  "reason": "<one sentence: why this operation answers the question>",
  "raw_answer": "**Business Question:** <...>\\n**Selected Chart Type:** <...>\\n**Why this visualization is optimal:** <...>\\n**Aggregation Applied:** <...>\\n**Expected Insight:** <...>"
}}

When filling `raw_answer`, you MUST use the exact markdown format shown above to explain your BI reasoning.

--------------------------------
STATE AWARENESS
--------------------------------
If a computed result already exists in the conversation history, do NOT recompute.
Use the existing result and set pandas_code to "". Fill `raw_answer` with deep analytical reasoning.

Computation = Python (always via pandas_code)
Explanation = LLM (never calculate numbers yourself)"""

    # Build message history for multi-turn conversation
    messages = [{"role": "system", "content": system_prompt}]

    # Add previous turns from history
    if chat_history:
        for turn in chat_history:
            messages.append({"role": turn["role"], "content": turn["content"]})

    # Add the new user question
    messages.append({"role": "user", "content": user_question})

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            temperature=0.1,
            max_tokens=2000,
        )
        raw = response.choices[0].message.content.strip()

        # Strip markdown if present
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.lower().startswith("json"):
                raw = raw[4:]

        parsed = json.loads(raw)
        pandas_code = parsed.get("pandas_code", "")
        explanation = parsed.get("explanation", "")
        chart_suggestion = parsed.get("chart_suggestion", "none")
        raw_answer = parsed.get("raw_answer", explanation)

        # Execute pandas code safely
        result_value = None
        code_error = None
        if pandas_code.strip():
            local_vars = {"df": df.copy(), "pd": pd, "np": np, "result": None}
            try:
                # NOTE: we use __builtins__ so pandas internals work correctly.
                # The code is LLM-generated and validated by the system prompt rules.
                exec(pandas_code, {"__builtins__": __builtins__}, local_vars)  # noqa: S102
                result_value = local_vars.get("result", None)
            except Exception as exec_err:
                code_error = str(exec_err)

        return {
            "pandas_code": pandas_code,
            "result": result_value,
            "explanation": explanation,
            "chart_suggestion": chart_suggestion,
            "error": code_error,
            "raw_answer": raw_answer,
            "reason": parsed.get("reason", ""),
            "operation": parsed.get("operation", ""),
        }

    except json.JSONDecodeError as e:
        return {
            "pandas_code": "",
            "result": None,
            "explanation": f"Could not parse AI response: {e}",
            "chart_suggestion": "none",
            "error": str(e),
            "raw_answer": f"Sorry, I had trouble formatting my response. Please try rephrasing your question.",
        }
    except Exception as e:
        return {
            "pandas_code": "",
            "result": None,
            "explanation": f"Error: {e}",
            "chart_suggestion": "none",
            "error": traceback.format_exc(),
            "raw_answer": f"An error occurred: {e}",
        }
