import pandas as pd
import streamlit as st
import plotly.express as px
from enum import Enum
from datetime import datetime
from decouple import config
import calendar
import locale

# print(locale.setlocale(locale.LC_ALL, 'C.UTF-8'))
# locale.LC_MONETARY

DATA_FILE = config('DATA_FILE')

# print(DATA_FILE)


class Col(Enum):
    TransactionDate = "Transaction Date"
    Amount = "Amount"
    TransactionType = "Transaction Type"
    AccountType = "Account"
    Description = "Description"
    Label = "Label"


class Label(Enum):
    IncomeMichael = "Michael's Income"
    IncomeStephanie = "Stephanie's Income"
    ExpenseMortgage = "Mortgage Payment"
    ExpenseNeeds = "Need's Payment"
    ExpenseWants = "Want's Payment"


# @st.cache_data
def get_data_from_csv():
    df = pd.read_csv(DATA_FILE)
    df[Col.TransactionDate.value] = pd.to_datetime(
        df[Col.TransactionDate.value])
    return df


def get_month_name(month_num: int):
    return calendar.month_name[month_num]


def format_currency(val: any):
    return "${:,.2f}".format(val)

# helpful commands
# print(df.head())
# print(df.info())


# ----- Main Application ---------
st.set_page_config(page_title="Finance Dashboard",
                   layout="wide")

df = get_data_from_csv()


debit_qry = (df[Col.Label.value] != 'NOISE')\
    & (df[Col.TransactionDate.value] >= datetime(2023, 1, 1))\
    & (df[Col.TransactionDate.value] < datetime(2023, 12, 1))\
    & (df[Col.TransactionType.value] == 'DEBIT')
debit_grp = df.loc[debit_qry]
months = debit_grp[Col.TransactionDate.value].dt.month.unique()

income_grp = debit_grp.loc[(df[Col.Amount.value] > 0)]
income_per_month = pd.DataFrame(list(map(get_month_name, months)))
income_per_month[1] = income_grp.loc[(df[Col.Label.value] == Label.IncomeMichael.value)]\
    .groupby(debit_grp[Col.TransactionDate.value].dt.month)[Col.Amount.value]\
    .sum()\
    .values

income_per_month[2] = income_grp.loc[(df[Col.Label.value] == Label.IncomeStephanie.value)]\
    .groupby(debit_grp[Col.TransactionDate.value].dt.month)[Col.Amount.value]\
    .sum()\
    .values

income_per_month_sum = income_grp.groupby(income_grp[Col.TransactionDate.value].dt.month)[Col.Amount.value]\
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
# income_per_month
st.header("Income")
income_per_month.T

##################################
#######  Spending report #########
##################################
spend_grp = debit_grp.loc[(df[Col.Amount.value] < 0)]

spend_per_month = pd.DataFrame(list(map(get_month_name, months)))
spend_per_month[1] = debit_grp.loc[(df[Col.Label.value] == Label.ExpenseMortgage.value)]\
    .groupby(debit_grp[Col.TransactionDate.value].dt.month)[Col.Amount.value]\
    .apply(lambda val: val.abs().sum())\
    .values

spend_per_month[2] = debit_grp.loc[(df[Col.Label.value] == Label.ExpenseNeeds.value)]\
    .groupby(debit_grp[Col.TransactionDate.value].dt.month)[Col.Amount.value]\
    .apply(lambda val: val.abs().sum())\
    .values

spend_per_month[3] = debit_grp.loc[(df[Col.Label.value] == "Want's Payment")]\
    .groupby(debit_grp[Col.TransactionDate.value].dt.month)[Col.Amount.value]\
    .apply(lambda val: val.abs().sum())\
    .values

spend_per_month_sum = spend_grp.groupby(spend_grp[Col.TransactionDate.value].dt.month)[Col.Amount.value]\
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
# spend_per_month
st.header("Expenses")
spend_per_month.T
