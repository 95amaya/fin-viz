# import plotly.express as px
import streamlit as st
from environs import Env
from report_builder import ReportBuilder


env = Env()
env.read_env()
DATA_FILE_PATH: str = env.str('DATA_FILE_PATH')

# ----- Main Application ---------
st.set_page_config(page_title="Finance Dashboard",
                   layout="wide")

report = ReportBuilder(DATA_FILE_PATH, 2024, 4)

monthly_report_df = report.build_monthly_income_and_expense_df()

st.header("Monthly Summary")
monthly_report_df.T

# Monthly Breakdown
# TODO: Make Dynamic for any month
st.header("Monthly Breakdown")

col1, col2 = st.columns(2)

with col1:
    with st.expander("Income"):
        st.write('''
            Test Income
        ''')

    with st.expander("Savings"):
        st.write('''
            Test Savings
        ''')

with col2:
    with st.expander("Expenses"):
        st.write('''
            Test Expenses
        ''')


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

# ----- SIDEBAR -----
# Wrap this in a function
# st.sidebar.header("Please Filter Here")
# account = st.sidebar.multiselect(
#     "Select Account:",
#     options=df[Col.AccountType.value].unique(),
#     default=df[Col.AccountType.value].unique()
# )

# transaction_type = st.sidebar.multiselect(
#     "Select Transaction Type:",
#     options=df[Col.TransactionType.value].unique(),
#     default=df[Col.TransactionType.value].unique()
# )

# custom_tags = st.sidebar.multiselect(
#     "Select Custom Tags:",
#     options=df[Col.CustomTags.value].explode().unique(),
#     default=df[Col.CustomTags.value].explode().unique()
# )

# qry = f'`{Col.AccountType.value}` == @account & `{Col.TransactionType.value}` == @transaction_type & `{Col.CustomTags.value}`.explode() in @custom_tags'
# # print(qry)
# df_selected = df.query(qry)
# st.dataframe(df_selected, use_container_width=True)
# End function
