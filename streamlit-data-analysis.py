import pandas as pd
import streamlit as st
import plotly.express as px
from enum import Enum
from datetime import datetime
from decouple import config
import calendar

DATA_FILE = config('DATA_FILE')

# print(DATA_FILE)


class Col(Enum):
    TransactionDate = "Transaction Date"
    Amount = "Amount"
    TransactionType = "Transaction Type"
    AccountType = "Account"
    Description = "Description"
    CustomTags = "Custom Tags"


def toList(val: str):
    return val.split(",")


# @st.cache_data
def get_data_from_csv():
    df = pd.read_csv(DATA_FILE)
    df[Col.TransactionDate.value] = pd.to_datetime(
        df[Col.TransactionDate.value])
    df[Col.CustomTags.value] = df.apply(lambda row: toList(str(
        row[Col.CustomTags.value])), axis=1)
    return df

# helpful commands
# print(df.head())
# print(df.info())


# ----- Main Application ---------
st.set_page_config(page_title="Finance Dashboard",
                   layout="wide")

df = get_data_from_csv()

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


def get_month_name(month_num: int):
    return calendar.month_name[month_num]


def get_df_grp(dfi: pd.DataFrame, filterByFunc, grpByFunc):
    return dfi.loc[filterByFunc].groupby(grpByFunc)[Col.Amount.value]


# print(df[Col.CustomTags.value].head())
# print(df[Col.CustomTags.value].explode().head())
# print(df[Col.CustomTags.value].explode() == 'NOISE')
# print(df[Col.CustomTags.value].explode() != 'NOISE')

# print(df[Col.TransactionDate.value] >= datetime(2023, 1, 1))

viz_qry = (df[Col.CustomTags.value].explode() != 'NOISE')\
    & (df[Col.TransactionDate.value] >= datetime(2023, 1, 1))\
    & (df[Col.TransactionDate.value] < datetime(2023, 11, 1))\
    & (df[Col.TransactionType.value] == 'DEBIT')
vis_grp = df.loc[viz_qry]

with st.container():
    left_column, right_column = st.columns(2)
    with left_column:
        curr_month_income = vis_grp.loc[(df[Col.TransactionDate.value] > datetime(
            2023, 10, 1)) & (vis_grp[Col.Amount.value] > 0)]
        curr_month_income_fig = px.pie(curr_month_income, values=Col.Amount.value,
                                       names=Col.Description.value, title="Current Month Income Breakdown")
        st.plotly_chart(curr_month_income_fig)

    with right_column:
        curr_month_spend = vis_grp.loc[(df[Col.TransactionDate.value] > datetime(
            2023, 10, 1)) & (vis_grp[Col.Amount.value] < 0)]
        curr_month_spend[Col.Description.value] = curr_month_spend.apply(
            lambda row: row[Col.Description.value][:30], axis=1)
        curr_month_spend[Col.Amount.value] = curr_month_spend[Col.Amount.value].abs()
        # curr_month_spend
        curr_month_spend_fig = px.pie(curr_month_spend, values=Col.Amount.value,
                                      names=Col.Description.value, title="Current Month Spend Breakdown")
        st.plotly_chart(curr_month_spend_fig)


xVals = vis_grp[Col.TransactionDate.value].dt.month.unique()
debit_per_month_group = pd.DataFrame(list(map(get_month_name, xVals)))
debit_per_month_group[1] = vis_grp.loc[(df[Col.Amount.value] > 0)]\
    .groupby(vis_grp[Col.TransactionDate.value].dt.month)[Col.Amount.value]\
    .sum()\
    .values

debit_per_month_group[2] = vis_grp.loc[(df[Col.Amount.value] < 0)]\
    .groupby(vis_grp[Col.TransactionDate.value].dt.month)[Col.Amount.value]\
    .apply(lambda val: val.abs().sum())\
    .values


debit_per_month_group.columns = ["Month", "Income", "Spent"]
debit_per_month_group

# https://plotly.com/python/bar-charts/#grouped-bar-chart:~:text=avg%20of%20total_bill-,Bar%20Charts%20with%20Text,-New%20in%20v5.5
# Ideal Plot
# Month Name, Amount > 0, Amount < 0, Surplus / Deficit
fig = px.bar(debit_per_month_group, x="Month",
             y=debit_per_month_group.columns[1:], barmode='group')
st.plotly_chart(fig, use_container_width=True)
