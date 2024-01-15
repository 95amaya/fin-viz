import streamlit as st
from decouple import config
from report_builder import *


DATA_FILE_PATH = config('DATA_FILE')

# ----- Main Application ---------
st.set_page_config(page_title="Finance Dashboard",
                   layout="wide")

report = ReportBuilder(DATA_FILE_PATH)

st.header("Income")
income_summary_df = report.build_income_summary_df()
income_summary_df.T

st.header("Expenses")
expense_summary_df = report.build_expense_summary_df()
expense_summary_df.T
