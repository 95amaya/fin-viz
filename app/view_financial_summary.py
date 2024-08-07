# import plotly.express as px
import streamlit as st
from report_builder import ReportBuilder
from models import EnvironmentReader

# put into fragment to run independently of entire page


def main(env: EnvironmentReader) -> None:
    # ----- Main Application ---------
    st.set_page_config(page_title="Finance Dashboard",
                       layout="wide")

    report = ReportBuilder(env.DATA_FILE_PATH, env.CURRENT_YYYY, env.MAX_MONTH)

    monthly_report_df = report.build_monthly_income_and_expense_df()

    st.header("Monthly Summary", divider=True)
    monthly_report_df.T

    # Monthly Breakdown
    # TODO: Make Dynamic for any month
    monthly_report_breakdown = report.build_monthly_income_and_expense_breakdown_report(
        env.MAX_MONTH)

    st.header("Monthly Breakdown", divider=True)

    with st.expander("Income"):
        st.dataframe(data=monthly_report_breakdown.income_df,
                     hide_index=True, column_config=monthly_report_breakdown.income_df_column_config)

    with st.expander("Expenses"):
        st.subheader(body='Debit')
        st.dataframe(data=monthly_report_breakdown.debit_df,
                     hide_index=True, column_config=monthly_report_breakdown.debit_df_column_config)
        col1, col2 = st.columns(2)
        with col1:
            st.subheader(body='Credit Needs')
            st.dataframe(
                data=monthly_report_breakdown.credit_needs_df, hide_index=True, column_config=monthly_report_breakdown.credit_needs_df_column_config)
        with col2:
            st.subheader(body='Credit Wants')
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
