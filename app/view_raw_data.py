import streamlit as st
import pandas as pd
from pandas.api.types import (
    is_datetime64_any_dtype,
    is_numeric_dtype,
)
from models import Col, SessionStore
from typing import Any


def render_raw_data(session: SessionStore, raw_df: pd.DataFrame) -> None:
    df = raw_df.copy()

    st.header("Raw Data", divider=True)
    _render_sidebar(df, session)

    st.dataframe(_filter_dataframe(df, session), height=700, use_container_width=True, column_config={
        Col.TransactionDate.value: st.column_config.DatetimeColumn(
            format='YYYY-MM-DD')
    })

    st.sidebar.write(f'Count: {session.state.count}')
    st.sidebar.write(
        f'Amount Sum: {round(session.state.amount_sum, 2)}')


def _render_sidebar(df: pd.DataFrame, session: SessionStore) -> None:
    # print('render sidebar!')
    st.sidebar.header("Raw Data", divider=True)
    st.sidebar.checkbox("Add filters", key='enable_raw_data_filters')

    if session.state.enable_raw_data_filters:
        col_filter_container = st.sidebar.container()
        with col_filter_container:
            to_filter_columns = st.multiselect(
                "Filter dataframe on", df.columns, key='column_options')
            for column in to_filter_columns:
                left, right = st.columns((1, 20))
                left.write("↳")
                # Treat columns with < 10 unique values as categorical
                if df[column].nunique() < 10:
                    right.multiselect(
                        f"Values for {column}",
                        df[column].unique(),
                        default=list(df[column].unique()),
                        key=f"user_input_cat|{column}"
                    )
                elif is_numeric_dtype(df[column]):
                    _min = float(df[column].min())
                    _max = float(df[column].max())
                    step = (_max - _min) / 100
                    right.slider(
                        f"Values for {column}",
                        min_value=_min,
                        max_value=_max,
                        value=(_min, _max),
                        step=step,
                        key=f"user_input_num|{column}"
                    )
                elif is_datetime64_any_dtype(df[column]):
                    right.date_input(
                        f"Values for {column}",
                        value=(
                            df[column].min(),
                            df[column].max(),
                        ),
                        key=f"user_input_date|{column}"
                    )
                else:
                    right.text_input(
                        f"Substring or regex in {column}",
                        key=f"user_input_text|{column}"
                    )


def _filter_dataframe(df: pd.DataFrame, session: SessionStore) -> pd.DataFrame:
    # refer to https://github.com/tylerjrichards/st-filter-dataframe/blob/main/streamlit_app.py
    if not session.state.enable_raw_data_filters:
        _set_df_metrics(df, session)
        return df

    col_keys_to_filter: list[str] = [item for item in session.state.keys()
                                     if item.startswith('user_input')]
    # st.write(col_keys_to_filter)

    for column_key in col_keys_to_filter:
        key, column = column_key.split('|')
        filter_value = session.state[column_key]
        # print([key, column])
        match key:
            case 'user_input_cat':
                # print('cat search')
                df = df[df[column].isin(filter_value)]
            case 'user_input_num':
                # print('num search')
                df = df[df[column].between(*filter_value)]
            case 'user_input_date':
                # print('date search')
                if len(filter_value) == 2:  # type: ignore
                    filter_value = tuple(
                        map(pd.to_datetime, filter_value))  # type: ignore
                    start_date, end_date = filter_value  # type: ignore
                    df = df.loc[df[column].between(start_date, end_date)]
            case 'user_input_text':
                # print('text search')
                if filter_value:
                    df = df[df[column].astype(
                        str).str.contains(filter_value)]

    _set_df_metrics(df, session)
    return df


def _set_df_metrics(df: pd.DataFrame, session: SessionStore) -> None:
    # print('set df metrics called')
    session.state.count = df.size
    session.state.amount_sum = df[Col.Amount.value].sum()
