from datetime import datetime
from typing import Any, Hashable

from models import Col, Label
import calendar
from dataclasses import dataclass
import numpy as np
import pandas as pd
from pandas.core.groupby import DataFrameGroupBy
from rapidfuzz import fuzz
from streamlit.elements.lib.column_config_utils import ColumnConfigMappingInput
import streamlit as st


# ------- Helper Functions -------
# @st.cache_data


def get_data_from_csv(file_path) -> pd.DataFrame:
    df = pd.read_csv(file_path)
    df[Col.TransactionDate.value] = pd.to_datetime(
        df[Col.TransactionDate.value])
    return df


def get_month_name(month_num: int) -> str:
    return calendar.month_name[month_num]


def format_currency(val: Any):
    if type(val) == int or type(val) == float:
        return "${:,.2f}".format(val)
    else:
        return val


def format_percentage(val: Any):
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

@dataclass
class MonthlyReportBreakdown:
    income_df: pd.DataFrame
    income_df_column_config: ColumnConfigMappingInput
    debit_df: pd.DataFrame
    debit_df_column_config: ColumnConfigMappingInput
    credit_needs_df: pd.DataFrame
    credit_needs_df_column_config: ColumnConfigMappingInput
    credit_wants_df: pd.DataFrame
    credit_wants_df_column_config: ColumnConfigMappingInput


class ReportBuilder:
    credit_df_grp: DataFrameGroupBy
    debit_df: pd.DataFrame
    income_per_month_df: pd.DataFrame
    main_df: pd.DataFrame
    monthly_report_df: pd.DataFrame
    monthly_report_breakdown_df: pd.DataFrame
    raw_income_df: pd.DataFrame
    raw_spend_df: pd.DataFrame
    spend_per_month_df: pd.DataFrame
    year: int

    def __init__(self, file_path: str, yyyy: int, max_month: int) -> None:
        raw_df = get_data_from_csv(file_path)
        base_filter_qry = (raw_df[Col.Label.value] != 'NOISE')\
            & (raw_df[Col.TransactionDate.value] >= datetime(yyyy, 1, 1))\
            & (raw_df[Col.TransactionDate.value] < datetime(yyyy, max_month + 1, 1))

        self.year = yyyy
        self.main_df = raw_df.loc[base_filter_qry]
        self.debit_df = self.main_df.loc[(
            self.main_df[Col.TransactionType.value] == 'DEBIT')]
        self.credit_df_grp = self.main_df.loc[(
            self.main_df[Col.TransactionType.value] == 'CREDIT')].groupby(by=Col.AccountType.value)
        self.raw_income_df = self.debit_df.loc[(
            self.debit_df[Col.Amount.value] > 0)]
        self.raw_spend_df = self.debit_df.loc[(
            self.debit_df[Col.Amount.value] < 0)]
        self.months_as_labels = list(
            map(get_month_name, range(1, max_month + 1)))

    def build_monthly_income_summary_df(self) -> pd.DataFrame:
        income_df = self.raw_income_df

        income_per_month_sum = income_df.groupby(income_df[Col.TransactionDate.value].dt.month)[Col.Amount.value]\
            .sum()\
            .values

        income_per_month_1 = income_df.loc[(income_df[Col.Label.value] == Label.IncomeMichael.value)]\
            .groupby(income_df[Col.TransactionDate.value].dt.month)[Col.Amount.value]\
            .sum()\
            .values

        income_per_month_2 = income_df.loc[(income_df[Col.Label.value] == Label.IncomeStephanie.value)]\
            .groupby(income_df[Col.TransactionDate.value].dt.month)[Col.Amount.value]\
            .sum()\
            .values
        # TODO: Create array pad function to append 0 values to array
        if (income_per_month_2.size < income_per_month_sum.size):  # type: ignore
            diff = income_per_month_sum.size - income_per_month_2.size  # type: ignore
            income_per_month_2 = np.append(
                income_per_month_2, [0] * diff)  # type: ignore

        income_per_month_3 = income_per_month_sum - \
            (income_per_month_1 + income_per_month_2)  # type: ignore

        retval = pd.DataFrame(
            data={
                "Month": self.months_as_labels,
                Label.IncomeMichael.value: income_per_month_1,
                Label.IncomeStephanie.value: income_per_month_2,
                "Other": income_per_month_3,
                "Total": income_per_month_sum,
            }
        )

        self.__add_calculated_rows(retval)
        # print(retval)

        self.income_per_month_df = retval

        return self.income_per_month_df

    def build_monthly_expense_summary_df(self) -> pd.DataFrame:
        spend_df = self.raw_spend_df

        spend_per_month_1 = spend_df.loc[(spend_df[Col.Label.value] == Label.ExpenseMortgage.value)]\
            .groupby(spend_df[Col.TransactionDate.value].dt.month)[Col.Amount.value]\
            .apply(lambda val: val.abs().sum())\
            .values

        spend_per_month_2 = spend_df.loc[(spend_df[Col.AccountType.value] == 'NEEDS') & (spend_df[Col.Label.value] != Label.ExpenseMortgage.value)]\
            .groupby(spend_df[Col.TransactionDate.value].dt.month)[Col.Amount.value]\
            .apply(lambda val: val.abs().sum())\
            .values

        spend_per_month_3 = spend_df.loc[(spend_df[Col.AccountType.value] == 'WANTS')]\
            .groupby(spend_df[Col.TransactionDate.value].dt.month)[Col.Amount.value]\
            .apply(lambda val: val.abs().sum())\
            .values

        spend_per_month_sum = spend_df.groupby(spend_df[Col.TransactionDate.value].dt.month)[Col.Amount.value]\
            .apply(lambda val: val.abs().sum())\
            .values

        retval = pd.DataFrame(
            data={
                "Month": self.months_as_labels,
                Label.ExpenseMortgage.value: spend_per_month_1,
                Label.ExpenseNeeds.value: spend_per_month_2,
                Label.ExpenseWants.value: spend_per_month_3,
                "Total": spend_per_month_sum,
            }
        )

        self.__add_calculated_rows(retval)
        # print(retval)

        self.spend_per_month_df = retval

        return self.spend_per_month_df

    def __add_calculated_rows(self, df: pd.DataFrame) -> None:
        # sum each column in dataframe and convert format to dataframe row
        ytd_sum = [
            'Y.T.D Sum'] + df.sum()[1:].explode().tolist()

        df_len = len(df)
        monthly_avg = ['Monthly Avg.'] + \
            list(map(lambda val: val / df_len, ytd_sum[1:]))

        df.loc[len(df.index)] = monthly_avg
        df.loc[len(df.index)] = ytd_sum

    def build_monthly_income_and_expense_df(self) -> pd.DataFrame:
        income_summary_df = self.build_monthly_income_summary_df()
        expense_summary_df = self.build_monthly_expense_summary_df()

        total_income = income_summary_df["Total"]
        retval = pd.DataFrame(
            data={
                "Month": income_summary_df.iloc[:, 0],
                "Income Total": total_income.map(format_currency),
                Label.ExpenseMortgage.value: format_breakdown_pct(total_income, expense_summary_df[Label.ExpenseMortgage.value]),
                Label.ExpenseNeeds.value: format_breakdown_pct(total_income, expense_summary_df[Label.ExpenseNeeds.value]),
                Label.ExpenseWants.value: format_breakdown_pct(total_income, expense_summary_df[Label.ExpenseWants.value]),
                "Payment Total": format_breakdown_pct(total_income, expense_summary_df["Total"]),
                "Savings": format_breakdown_pct(total_income, total_income - expense_summary_df["Total"])
            }
        )
        # print(retval)

        self.monthly_report_df = retval
        return self.monthly_report_df

    def build_monthly_income_and_expense_breakdown_report(self, month: int) -> MonthlyReportBreakdown:
        income_df = self.raw_income_df.loc[(self.raw_income_df[Col.TransactionDate.value].dt.month == month)].sort_values(
            by=[Col.Amount.value, Col.TransactionDate.value], ascending=[False, True])

        income_df_column_config: ColumnConfigMappingInput = {
            Col.TransactionDate.value: st.column_config.DatetimeColumn(
                format='YYYY-MM-DD'),
            Col.TransactionType.value: None
        }

        # print('------ DEBIT INCOME ------')
        # print(income_df.head())
        # print()

        debit_df = self.raw_spend_df.loc[(self.raw_spend_df[Col.TransactionDate.value].dt.month == month)].sort_values(
            by=Col.Amount.value, ascending=True)

        debit_df_column_config: ColumnConfigMappingInput = {
            Col.TransactionDate.value: st.column_config.DatetimeColumn(
                format='YYYY-MM-DD'),
            Col.TransactionType.value: None
        }

        # print('------ DEBIT SPEND ------')
        # print(debit_df.head())
        # print()

        needs_df = self.credit_df_grp.get_group('NEEDS')
        credit_needs_df = needs_df.loc[(needs_df[Col.TransactionDate.value].dt.month == month)].sort_values(
            by=Col.Amount.value, ascending=True)

        credit_needs_df_column_config: ColumnConfigMappingInput = {
            Col.TransactionDate.value: st.column_config.DatetimeColumn(
                format='YYYY-MM-DD'),
            Col.TransactionType.value: None,
            Col.AccountType.value: None,
            Col.Label.value: None
        }

        # print('------ CREDIT NEEDS -------')
        # print(credit_needs_df.head())
        # print()

        wants_df = self.credit_df_grp.get_group('WANTS')
        credit_wants_df = wants_df.loc[(wants_df[Col.TransactionDate.value].dt.month == month)].sort_values(
            by=Col.Amount.value, ascending=True)

        credit_wants_df_column_config: ColumnConfigMappingInput = {
            Col.TransactionDate.value: st.column_config.DatetimeColumn(
                format='YYYY-MM-DD'),
            Col.TransactionType.value: None,
            Col.AccountType.value: None,
            Col.Label.value: None
        }

        # print('------ CREDIT WANTS -------')
        # print(credit_wants_df.head())
        # print()

        return MonthlyReportBreakdown(
            income_df=income_df, income_df_column_config=income_df_column_config,
            debit_df=debit_df, debit_df_column_config=debit_df_column_config,
            credit_needs_df=credit_needs_df, credit_needs_df_column_config=credit_needs_df_column_config,
            credit_wants_df=credit_wants_df, credit_wants_df_column_config=credit_wants_df_column_config)

    # Matches labels for current month based on last month's using a fuzzy match

    def get_fuzzy_matched_rows(self, month_index: int) -> pd.DataFrame:
        col_fuzzy_match = 'fuzzy_match'
        df_distinct_text_labels = self.__get_distinct_labels(
            month_index=month_index-1)
        df = self.main_df

        df_curr_month = df.loc[(df[Col.TransactionDate.value] >= datetime(self.year, month_index, 1)) & (
            df[Col.TransactionDate.value] < datetime(self.year, month_index + 1, 1))].copy()

        df_curr_month[col_fuzzy_match] = df_curr_month[Col.Description.value].apply(
            lambda descr: self.__get_closest_fuzzy_match(descr, df_distinct_text_labels))

        df_curr_month[Col.Label.value] = df_curr_month[col_fuzzy_match].map(
            lambda val: val[Col.Label.value] if val['MaxFuzzRatio'] >= 75 else '')

        df_curr_month = df_curr_month.loc[df_curr_month[Col.Label.value] != ''].drop(
            columns=[col_fuzzy_match])

        # print(df_curr_month)
        return df_curr_month

    def __get_distinct_labels(self, month_index: int) -> list[dict[Hashable, Any]]:
        df = self.main_df

        df_month = df.loc[(df[Col.TransactionDate.value] >= datetime(self.year, month_index, 1)) & (
            df[Col.TransactionDate.value] < datetime(self.year, month_index + 1, 1)) & (df[Col.Label.value])].copy()

        df_distinct_text_labels = df_month.drop_duplicates(subset=[Col.AccountType.value, Col.Label.value])[
            [Col.Label.value, Col.Description.value]].to_dict('records')

        # Print label, description key value pairs
        # for item in df_distinct_text_labels:
        #     print(item)

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
