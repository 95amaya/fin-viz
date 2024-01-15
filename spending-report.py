import plotly.express as px
import streamlit as st
from decouple import config
from report_builder import *


DATA_FILE_PATH = config('DATA_FILE_PATH')

# ----- Main Application ---------
st.set_page_config(page_title="Finance Dashboard",
                   layout="wide")

report = ReportBuilder(DATA_FILE_PATH)

income_summary_df = report.build_income_summary_df()
expense_summary_df = report.build_expense_summary_df()

st.header('Income and Expense Chart')
summary_chart_df = income_summary_df[["Month", "Total"]][:-1].copy()
summary_chart_df[2] = expense_summary_df[["Total"]][:-1].copy()
summary_chart_df.columns = ["Month", "Income", "Expense"]

fig = px.bar(summary_chart_df, x="Month",
             y=["Income", "Expense"], barmode="group", color_discrete_map={
                 'Income': '#50C878',
                 'Expense': '#f94449'
             })
st.plotly_chart(fig, use_container_width=True)

# summary_chart_df_display = summary_chart_df.T.copy().map(format_currency)
# summary_chart_df_display

# st.header("Income")
# income_summary_df.T
st.header("Expenses")
expense_summary_df_display = expense_summary_df.T.copy().map(format_currency)
expense_summary_df_display
