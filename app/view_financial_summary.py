# import plotly.express as px
import streamlit as st
from report_builder import ReportBuilder
from models import EnvironmentReader

# put into fragment to run independently of entire page


def render_financial_summary(env: EnvironmentReader) -> None:

    report = ReportBuilder(env.DATA_FILE_PATH, env.CURRENT_YYYY, env.MAX_MONTH)

    monthly_report_df = report.build_monthly_income_and_expense_df()

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