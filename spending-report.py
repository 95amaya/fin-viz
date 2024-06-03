# import plotly.express as px
import streamlit as st
from report_builder import ReportBuilder
from models import EnvironmentReader


def main(env: EnvironmentReader) -> None:
    # ----- Main Application ---------
    st.set_page_config(page_title="Finance Dashboard",
                       layout="wide")

    report = ReportBuilder(env.DATA_FILE_PATH, env.CURRENT_YYYY, env.MAX_MONTH)

    monthly_report_df = report.build_monthly_income_and_expense_df()

    st.header("Monthly Summary")
    monthly_report_df.T

    # Monthly Breakdown
    # TODO: Make Dynamic for any month
    monthly_report_breakdown = report.build_monthly_income_and_expense_breakdown_report(
        env.MAX_MONTH)

    st.header("Monthly Breakdown")

    col1, col2 = st.columns(2)

    with col1:
        with st.expander("Income"):
            st.dataframe(data=monthly_report_breakdown.income_df,
                         hide_index=True, column_config=monthly_report_breakdown.income_df_column_config)

        with st.expander("Savings"):
            st.write('''
                Test Savings
            ''')

    with col2:
        with st.expander("Expenses"):
            st.header(body='Debit')
            st.dataframe(data=monthly_report_breakdown.debit_df,
                         hide_index=True, column_config=monthly_report_breakdown.debit_df_column_config)
            st.header(body='Credit Needs')
            st.dataframe(
                data=monthly_report_breakdown.credit_needs_df, hide_index=True, column_config=monthly_report_breakdown.credit_needs_df_column_config)
            st.header(body='Credit Wants')
            st.dataframe(
                data=monthly_report_breakdown.credit_wants_df, hide_index=True, column_config=monthly_report_breakdown.credit_wants_df_column_config)


if __name__ == "__main__":
    main(EnvironmentReader())


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
