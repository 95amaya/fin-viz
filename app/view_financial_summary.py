# import plotly.express as px
from datetime import datetime
import streamlit as st
import pandas as pd
from report_builder import ReportBuilder
from models import EnvironmentReader

# put into fragment to run independently of entire page


def render_financial_summary(env: EnvironmentReader, raw_df: pd.DataFrame) -> None:
    max_date = datetime(env.CURRENT_YYYY, env.MAX_MONTH, 1)
    report = ReportBuilder(raw_df, max_date)

    monthly_report_df = report.build_monthly_income_and_expense_df()

    st.header("Income Summary", divider=True)
    st.dataframe(report.income_per_month_df.T)

    st.header("Spend Summary", divider=True)
    st.dataframe(report.spend_per_month_df.T)

    # TODO Build pie chart of monthly spending
    # TODO Make % optional (compare to running avg. YTD, 3mo, 6mo)
    # TODO Use avg. spending AND median spending
    # TODO Insert Tabs
    # TODO Breakdown credit spending
    # TODO Add basic filters
    st.header("Monthly Summary", divider=True)
    st.dataframe(monthly_report_df.T)


# Plotting Prototype
# st.header('Income and Expense Chart')
# summary_chart_df = income_summary_df[["Month", "Total"]][:-1].copy()
# summary_chart_df[2] = expense_summary_df[["Total"]][:-1].copy()
# summary_chart_df.columns = ["Month", "Income", "Expense"]

# fig = px.bar(summary_chart_df, x="Month",
#              y=["Income", "Expense"], barmode="group", color_discrete_map={
#                  'Income': '#50C878',
#                  'Expense': '#f94449'
#              })
# st.plotly_chart(fig, use_container_width=True)

# summary_chart_df_display = summary_chart_df.T.copy().map(format_currency)
# summary_chart_df_display
