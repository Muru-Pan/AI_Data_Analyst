import streamlit as st
import pandas as pd
import numpy as np
from visualizations.chart_factory import histogram, bar_chart, line_chart, scatter_plot, box_plot, pie_chart, area_chart
from core.trend_analyzer import find_date_columns

def render_tab_visualize(df):

    numeric_cols = df.select_dtypes(include=np.number).columns.tolist()
    all_cols = df.columns.tolist()
    categorical_cols = df.select_dtypes(include="object").columns.tolist()

    chart_type = st.selectbox("Chart type", [
        "Histogram", "Bar Chart", "Line Chart", "Scatter Plot",
        "Box Plot", "Pie Chart", "Area Chart"
    ])

    c1, c2, c3 = st.columns(3)

    if chart_type == "Histogram":
        col_h = c1.selectbox("Column", numeric_cols, key="hist_col")
        nbins = c2.slider("Bins", 10, 100, 30)
        if st.button("Generate Chart", key="gen_hist"):
            st.plotly_chart(histogram(df, col_h, nbins), width='stretch', key="viz_hist")

    elif chart_type == "Bar Chart":
        x_col = c1.selectbox("X (category)", categorical_cols or all_cols, key="bar_x")
        y_col = c2.selectbox("Y (value)", numeric_cols, key="bar_y")
        color_col = c3.selectbox("Color by", ["None"] + categorical_cols, key="bar_color")
        color_col = None if color_col == "None" else color_col
        if st.button("Generate Chart", key="gen_bar"):
            if color_col:
                agg = df.groupby([x_col, color_col])[y_col].sum().reset_index()
            else:
                agg = df.groupby(x_col)[y_col].sum().reset_index()
            st.plotly_chart(bar_chart(agg, x_col, y_col, color_col), width='stretch', key="viz_bar")

    elif chart_type == "Line Chart":
        dt_cols = find_date_columns(df)
        x_col = c1.selectbox("X (date/category)", dt_cols + all_cols, key="line_x")
        y_col = c2.selectbox("Y (value)", numeric_cols, key="line_y")
        color_col = c3.selectbox("Color by", ["None"] + categorical_cols, key="line_color")
        color_col = None if color_col == "None" else color_col
        if st.button("Generate Chart", key="gen_line"):
            sorted_df = df.sort_values(x_col) if x_col in df.columns else df
            st.plotly_chart(line_chart(sorted_df, x_col, y_col, color_col), width='stretch', key="viz_line")

    elif chart_type == "Scatter Plot":
        x_col = c1.selectbox("X", numeric_cols, key="scat_x")
        y_col = c2.selectbox("Y", numeric_cols, key="scat_y")
        color_col = c3.selectbox("Color by", ["None"] + categorical_cols, key="scat_color")
        color_col = None if color_col == "None" else color_col
        if st.button("Generate Chart", key="gen_scat"):
            st.plotly_chart(scatter_plot(df, x_col, y_col, color_col), width='stretch', key="viz_scatter")

    elif chart_type == "Box Plot":
        col_b = c1.selectbox("Column", numeric_cols, key="box_col")
        group_b = c2.selectbox("Group by", ["None"] + categorical_cols, key="box_grp")
        group_b = None if group_b == "None" else group_b
        if st.button("Generate Chart", key="gen_box"):
            st.plotly_chart(box_plot(df, col_b, group_b), width='stretch', key="viz_box")

    elif chart_type == "Pie Chart":
        names_c = c1.selectbox("Names (category)", categorical_cols or all_cols, key="pie_names")
        values_c = c2.selectbox("Values (numeric)", numeric_cols, key="pie_vals")
        if st.button("Generate Chart", key="gen_pie"):
            st.plotly_chart(pie_chart(df, names_c, values_c), width='stretch', key="viz_pie")

    elif chart_type == "Area Chart":
        x_col = c1.selectbox("X", all_cols, key="area_x")
        y_col = c2.selectbox("Y", numeric_cols, key="area_y")
        if st.button("Generate Chart", key="gen_area"):
            sorted_df = df.sort_values(x_col)
            st.plotly_chart(area_chart(sorted_df, x_col, y_col), width='stretch', key="viz_area")
