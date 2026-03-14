# 📊 AI Data Analyst

An AI-powered data analysis platform built with **Python + Streamlit**. Upload CSV/Excel datasets or connect to Supabase — the system automatically runs EDA, detects anomalies, tracks KPIs, identifies trends, and generates AI-powered business insights via **Groq LLaMA3**.

---

## ✨ Features

| Tab | Description |
|---|---|
| 📁 Data Overview | Upload data, view schema, clean missing values |
| 📊 EDA & Stats | Descriptive stats, distributions, column profiling |
| 📈 Visualizations | Interactive chart builder (7 chart types) |
| 🔗 Correlations | Heatmap, top pairs, Random Forest feature importance |
| 🚨 Anomalies | IQR + Z-score outlier detection with scatter plots |
| 🎯 KPI Dashboard | Auto-discovered KPI cards + time-series trends |
| 💬 AI Query | Ask questions in plain English — Groq answers with data + charts |
| 📄 Report | Generate & download a full HTML analytics report |

---

## 🚀 Quick Start

### 1. Clone / navigate to the project
```bash
cd E:\Big_Prj\AI_Data_Analyst
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure environment
```bash
copy .env.example .env
# Then edit .env and add your GROQ_API_KEY (and optionally SUPABASE credentials)
```

### 4. Run the app
```bash
streamlit run app.py
```

Navigate to **http://localhost:8501**

---

## 🔑 Environment Variables

Copy `.env.example` to `.env` and fill in:

| Variable | Description |
|---|---|
| `GROQ_API_KEY` | Get from [console.groq.com/keys](https://console.groq.com/keys) |
| `SUPABASE_URL` | Your Supabase project URL (optional) |
| `SUPABASE_KEY` | Your Supabase anon key (optional) |

---

## 📁 Project Structure

```
AI_Data_Analyst/
├── app.py                        # Streamlit main entry point
├── requirements.txt
├── .env.example
├── core/
│   ├── data_loader.py            # CSV / Excel / Supabase ingestion
│   ├── data_cleaner.py           # Cleaning & type inference
│   ├── eda_engine.py             # Automated EDA + stats
│   ├── correlation_engine.py     # Correlation matrix + feature importance
│   ├── anomaly_detector.py       # IQR + Z-score detection
│   ├── kpi_tracker.py            # KPI auto-discovery
│   ├── trend_analyzer.py         # Time-series trend analysis
│   ├── nlp_query_engine.py       # Groq NL query interface
│   ├── insight_generator.py      # AI business recommendations
│   └── report_generator.py       # HTML report (Jinja2)
├── visualizations/
│   └── chart_factory.py          # Plotly chart factory
├── templates/
│   └── report_template.html      # Report HTML template
└── data/
    ├── sample_sales.csv           # 500-row sales demo dataset
    └── sample_ecommerce.csv       # 300-row e-commerce dataset
```

---

## 🛠️ Tech Stack

- **UI**: Streamlit
- **Data**: Pandas, NumPy, SciPy
- **Visualizations**: Plotly Express + Graph Objects
- **AI / NLP**: Groq API (LLaMA3-70b-8192)
- **Reports**: Jinja2 HTML templates
- **Database**: Supabase (optional)
- **ML**: scikit-learn (feature importance)
