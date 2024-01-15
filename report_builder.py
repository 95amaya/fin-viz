from datetime import datetime
from models import Col, Label
import calendar
import pandas as pd


# ------- Helper Functions -------
# @st.cache_data


def get_data_from_csv(file_path):
    df = pd.read_csv(file_path)
    df[Col.TransactionDate.value] = pd.to_datetime(
        df[Col.TransactionDate.value])
    return df


def get_month_name(month_num: int):
    return calendar.month_name[month_num]


def format_currency(val: any):
    return "${:,.2f}".format(val)

# ----------------------------------------


class ReportBuilder:

    def __init__(self, file_path: str) -> None:
        self.main_df = get_data_from_csv(file_path)
        debit_qry = (self.main_df[Col.Label.value] != 'NOISE')\
            & (self.main_df[Col.TransactionDate.value] >= datetime(2023, 1, 1))\
            & (self.main_df[Col.TransactionDate.value] < datetime(2024, 1, 1))\
            & (self.main_df[Col.TransactionType.value] == 'DEBIT')
        self.debit_df = self.main_df.loc[debit_qry]
        self.months = self.main_df[Col.TransactionDate.value].dt.month.unique()
        self.months_as_df = pd.DataFrame(
            list(map(get_month_name, self.months)))

    def build_income_summary_df(self) -> pd.DataFrame:
        income_df = self.debit_df.loc[(self.debit_df[Col.Amount.value] > 0)]
        income_per_month = self.months_as_df.copy()

        income_per_month[1] = income_df.loc[(income_df[Col.Label.value] == Label.IncomeMichael.value)]\
            .groupby(income_df[Col.TransactionDate.value].dt.month)[Col.Amount.value]\
            .sum()\
            .values

        income_per_month[2] = income_df.loc[(income_df[Col.Label.value] == Label.IncomeStephanie.value)]\
            .groupby(income_df[Col.TransactionDate.value].dt.month)[Col.Amount.value]\
            .sum()\
            .values

        income_per_month_sum = income_df.groupby(income_df[Col.TransactionDate.value].dt.month)[Col.Amount.value]\
            .sum()\
            .values

        income_per_month[3] = income_per_month_sum - \
            (income_per_month[1] + income_per_month[2])

        income_per_month[4] = income_per_month_sum

        income_ytd_sum = [
            'Y.T.D Sum'] + income_per_month.sum()[1:].explode().tolist()

        income_df_len = len(income_per_month)
        monthly_avg = ['Monthly Avg.'] + \
            list(map(lambda val: val / income_df_len, income_ytd_sum[1:]))

        income_per_month.loc[len(income_per_month.index)] = income_ytd_sum

        income_per_month.loc[len(income_per_month.index)] = monthly_avg

        income_per_month[1] = income_per_month[1].apply(format_currency)
        income_per_month[2] = income_per_month[2].apply(format_currency)
        income_per_month[3] = income_per_month[3].apply(format_currency)
        income_per_month[4] = income_per_month[4].apply(format_currency)

        income_per_month.columns = [
            "Month", Label.IncomeMichael.value, Label.IncomeStephanie.value, "Other", "Total"]

        self.income_summary_df = income_per_month
        return income_per_month

    def build_expense_summary_df(self) -> pd.DataFrame:
        spend_df = self.debit_df.loc[(self.debit_df[Col.Amount.value] < 0)]
        spend_per_month = self.months_as_df.copy()

        spend_per_month[1] = spend_df.loc[(spend_df[Col.Label.value] == Label.ExpenseMortgage.value)]\
            .groupby(spend_df[Col.TransactionDate.value].dt.month)[Col.Amount.value]\
            .apply(lambda val: val.abs().sum())\
            .values

        spend_per_month[2] = spend_df.loc[(spend_df[Col.AccountType.value] == 'NEEDS') & (spend_df[Col.Label.value] != Label.ExpenseMortgage.value)]\
            .groupby(spend_df[Col.TransactionDate.value].dt.month)[Col.Amount.value]\
            .apply(lambda val: val.abs().sum())\
            .values

        spend_per_month[3] = spend_df.loc[(spend_df[Col.AccountType.value] == 'WANTS')]\
            .groupby(spend_df[Col.TransactionDate.value].dt.month)[Col.Amount.value]\
            .apply(lambda val: val.abs().sum())\
            .values

        spend_per_month_sum = spend_df.groupby(spend_df[Col.TransactionDate.value].dt.month)[Col.Amount.value]\
            .apply(lambda val: val.abs().sum())\
            .values

        spend_per_month[4] = spend_per_month_sum - \
            (spend_per_month[1] + spend_per_month[2] + spend_per_month[3])

        spend_per_month[5] = spend_per_month_sum

        spend_ytd_sum = [
            'Y.T.D Sum'] + spend_per_month.sum()[1:].explode().tolist()

        spend_df_len = len(spend_per_month)
        monthly_avg = ['Monthly Avg.'] + \
            list(map(lambda val: val / spend_df_len, spend_ytd_sum[1:]))

        spend_per_month.loc[len(spend_per_month.index)] = spend_ytd_sum

        spend_per_month.loc[len(spend_per_month.index)] = monthly_avg

        spend_per_month[1] = spend_per_month[1].apply(format_currency)
        spend_per_month[2] = spend_per_month[2].apply(format_currency)
        spend_per_month[3] = spend_per_month[3].apply(format_currency)
        spend_per_month[4] = spend_per_month[4].apply(format_currency)
        spend_per_month[5] = spend_per_month[5].apply(format_currency)

        spend_per_month.columns = [
            "Month", Label.ExpenseMortgage.value, Label.ExpenseNeeds.value, Label.ExpenseWants.value, "Other", "Total"]

        self.expense_summary_df = spend_per_month
        return spend_per_month
