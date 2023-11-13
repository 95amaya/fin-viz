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
    & (df[Col.TransactionDate.value] < datetime(2023, 11, 1))\
    & (df[Col.TransactionType.value] == 'DEBIT')
debit_grp = df.loc[debit_qry]
months = debit_grp[Col.TransactionDate.value].dt.month.unique()

income_grp = debit_grp.loc[(df[Col.Amount.value] > 0)]
income_per_month = pd.DataFrame(list(map(get_month_name, months)))
income_per_month[1] = income_grp.loc[(df[Col.Label.value] == "Michael's Income")]\
    .groupby(debit_grp[Col.TransactionDate.value].dt.month)[Col.Amount.value]\
    .sum()\
    .values

income_per_month[2] = income_grp.loc[(df[Col.Label.value] == "Stephanie's Income")]\
    .groupby(debit_grp[Col.TransactionDate.value].dt.month)[Col.Amount.value]\
    .sum()\
    .values

income_per_month_sum = income_grp.groupby(income_grp[Col.TransactionDate.value].dt.month)[Col.Amount.value]\
    .sum()\
    .values

income_per_month[3] = income_per_month_sum - \
    (income_per_month[1] + income_per_month[2])

income_per_month[4] = income_per_month_sum


ytd_sum = [
    'Y.T.D Sum'] + income_per_month.sum()[1:].explode().tolist()

df_len = len(income_per_month)
monthly_avg = ['Monthly Avg.'] + \
    list(map(lambda val: val / df_len, ytd_sum[1:]))

income_per_month.loc[len(income_per_month.index)] = ytd_sum

income_per_month.loc[len(income_per_month.index)] = monthly_avg

income_per_month[1] = income_per_month[1].apply(format_currency)
income_per_month[2] = income_per_month[2].apply(format_currency)
income_per_month[3] = income_per_month[3].apply(format_currency)
income_per_month[4] = income_per_month[4].apply(format_currency)

income_per_month.columns = [
    "Month", "Michael's Income", "Stephanie's Income", "Other", "Total"]
# income_per_month
income_per_month.T

##################################
#######  Spending report #########
##################################
spend_grp = debit_grp.loc[(df[Col.Amount.value] < 0)]

spend_per_month = pd.DataFrame(list(map(get_month_name, months)))
spend_per_month[1] = debit_grp.loc[(df[Col.Label.value] == "Mortgage Payment")]\
    .groupby(debit_grp[Col.TransactionDate.value].dt.month)[Col.Amount.value]\
    .apply(lambda val: val.abs().sum())\
    .values

spend_per_month[2] = debit_grp.loc[(df[Col.Label.value] == "Need's Payment")]\
    .groupby(debit_grp[Col.TransactionDate.value].dt.month)[Col.Amount.value]\
    .apply(lambda val: val.abs().sum())\
    .values

spend_per_month_sum = spend_grp.groupby(spend_grp[Col.TransactionDate.value].dt.month)[Col.Amount.value]\
    .apply(lambda val: val.abs().sum())\
    .values

spend_per_month[3] = spend_per_month_sum - \
    (spend_per_month[1] + spend_per_month[2])

spend_per_month[4] = spend_per_month_sum

spend_per_month[1] = spend_per_month[1].apply(format_currency)
spend_per_month[2] = spend_per_month[2].apply(format_currency)
spend_per_month[3] = spend_per_month[3].apply(format_currency)
spend_per_month[4] = spend_per_month[4].apply(format_currency)

spend_per_month.columns = [
    "Month", "Mortgage Payment", "Need's Payment", "Other", "Total"]
# spend_per_month
spend_per_month.T
