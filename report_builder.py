from datetime import datetime
from models import Col, Label
import calendar
import pandas as pd
from rapidfuzz import fuzz


# ------- Helper Functions -------
# @st.cache_data


def get_data_from_csv(file_path) -> pd.DataFrame:
    df = pd.read_csv(file_path)
    df[Col.TransactionDate.value] = pd.to_datetime(
        df[Col.TransactionDate.value])
    return df


def get_month_name(month_num: int) -> str:
    return calendar.month_name[month_num]


def format_currency(val: any):
    if type(val) == int or type(val) == float:
        return "${:,.2f}".format(val)
    else:
        return val


def format_percentage(val: any):
    if type(val) == float and abs(val) <= 2:
        return "{:.1%}".format(val)
    else:
        return val


def format_breakdown_pct(total_series: pd.Series, part_series: pd.Series) -> pd.Series:
    pct_series_display = (part_series / total_series).map(format_percentage)
    part_series_display = part_series.copy().map(format_currency)
    # print(pct_series_display)
    # print(part_series_display)
    ret_val = part_series_display + " (" + pct_series_display + ")"
    # print(ret_val)
    return ret_val


# ----------------------------------------


class ReportBuilder:

    def __init__(self, file_path: str, yyyy: int) -> None:
        self.main_df = get_data_from_csv(file_path)
        self.year = yyyy
        normalize_qry = (self.main_df[Col.Label.value] != 'NOISE')\
            & (self.main_df[Col.TransactionDate.value] >= datetime(yyyy, 1, 1))\
            & (self.main_df[Col.TransactionDate.value] < datetime(yyyy + 1, 1, 1))
        debit_qry = (self.main_df[Col.TransactionType.value] == 'DEBIT')
        self.main_df = self.main_df.loc[normalize_qry]
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

        income_per_month.loc[len(income_per_month.index)] = monthly_avg
        income_per_month.loc[len(income_per_month.index)] = income_ytd_sum

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

        # spend_per_month[4] = spend_per_month_sum - \
        #     (spend_per_month[1] + spend_per_month[2] + spend_per_month[3])

        spend_per_month[4] = spend_per_month_sum

        spend_ytd_sum = [
            'Y.T.D Sum'] + spend_per_month.sum()[1:].explode().tolist()

        spend_df_len = len(spend_per_month)
        monthly_avg = ['Monthly Avg.'] + \
            list(map(lambda val: val / spend_df_len, spend_ytd_sum[1:]))

        spend_per_month.loc[len(spend_per_month.index)] = monthly_avg
        spend_per_month.loc[len(spend_per_month.index)] = spend_ytd_sum

        spend_per_month.columns = [
            "Month", Label.ExpenseMortgage.value, Label.ExpenseNeeds.value, Label.ExpenseWants.value, "Total"]

        self.expense_summary_df = spend_per_month
        return spend_per_month

    def build_fixed_cost_summary_df(self) -> pd.DataFrame:
        fixed_cost_per_month = self.months_as_df.copy()

        fixed_cost_per_month[1] = self.main_df.loc[(self.main_df[Col.Label.value] == Label.ExpenseUtility.value)]\
            .groupby(self.main_df[Col.TransactionDate.value].dt.month)[Col.Amount.value]\
            .apply(lambda val: val.abs().sum())\
            .values

        fixed_cost_per_month[2] = self.main_df.loc[(self.main_df[Col.Label.value] == Label.ExpenseSubscription.value)]\
            .groupby(self.main_df[Col.TransactionDate.value].dt.month)[Col.Amount.value]\
            .apply(lambda val: val.abs().sum())\
            .values

        fixed_cost_per_month[3] = fixed_cost_per_month[1] + \
            fixed_cost_per_month[2]

        fixed_cost_per_month.columns = [
            "Month", Label.ExpenseUtility.value, Label.ExpenseSubscription.value, "Total"]

        self.fixed_cost_summary_df = fixed_cost_per_month
        return fixed_cost_per_month

    def calculate_fuzzy_match(self, month_index: int) -> pd.DataFrame:
        col_fuzzy_match = 'fuzzy_match'
        df_distinct_text_labels = self.__get_distinct_labels(
            month_index=month_index-1)
        df = self.main_df

        # Get months to compare
        df_curr_month = df.loc[(df[Col.TransactionDate.value] >= datetime(self.year, month_index, 1)) & (
            df[Col.TransactionDate.value] < datetime(self.year, month_index + 1, 1))].copy()

        df_curr_month[col_fuzzy_match] = df_curr_month[Col.Description.value].apply(
            lambda descr: self.__get_closest_fuzzy_match(descr, df_distinct_text_labels))

        df_curr_month[Col.Label.value] = df_curr_month[col_fuzzy_match].map(
            lambda val: val[Col.Label.value] if val['MaxFuzzRatio'] >= 75 else '')

        # override temp in place
        # df_curr_month = df_curr_month_fuzzy_match_temp.drop(
        #     columns=[col_fuzzy_match])

        # print(df_curr_month)
        return df_curr_month

    def __get_distinct_labels(self, month_index: int) -> pd.DataFrame:
        df = self.main_df

        df_month = df.loc[(df[Col.TransactionDate.value] >= datetime(self.year, month_index, 1)) & (
            df[Col.TransactionDate.value] < datetime(self.year, month_index + 1, 1)) & (df[Col.Label.value])].copy()

        df_distinct_text_labels = df_month.drop_duplicates(subset=[Col.Label.value])[
            [Col.Label.value, Col.Description.value]].to_dict('records')

        # print(df_distinct_text_labels)
        return df_distinct_text_labels

    def __get_closest_fuzzy_match(self, text, df_distinct_text_labels):
        # print(text)
        fuzz_ratio_obj = {Col.Label.value: '',
                          'MaxFuzzRatio': 0}

        for row in df_distinct_text_labels:
            fuzz_ratio = fuzz.ratio(text, row[Col.Description.value])
            row['FuzzRatio'] = fuzz_ratio
            # print(row)
            if (fuzz_ratio > fuzz_ratio_obj['MaxFuzzRatio']):
                fuzz_ratio_obj = {Col.Label.value: row[Col.Label.value],
                                  'MaxFuzzRatio': fuzz_ratio}

        # print(fuzz_ratio_obj)
        return fuzz_ratio_obj
