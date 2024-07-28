import streamlit as st
import pandas as pd
from pandas.api.types import (
    is_datetime64_any_dtype,
    is_numeric_dtype,
    is_object_dtype,
)
from classes.report_builder import get_data_from_csv
from classes.models import EnvironmentReader, Col


def main(env: EnvironmentReader) -> None:
    if "count" not in st.session_state:
        st.session_state.count = 0

    if "amount_sum" not in st.session_state:
        st.session_state.amount_sum = 0.0

    # ----- Main Application ---------
    st.set_page_config(page_title="Finance Dashboard",
                       layout="wide")

    local_css('./css/streamlit.css')

    st.header("Raw Data", divider=True)
    st.sidebar.header("Raw Data", divider=True)

    raw_df = get_data_from_csv(env.DATA_FILE_PATH)

    st.dataframe(filter_dataframe(raw_df), height=700,
                 use_container_width=True)

    st.sidebar.write(f'Count: {st.session_state.count}')
    st.sidebar.write(f'Amount Sum: {round(st.session_state.amount_sum, 2)}')

    st.sidebar.header('Summary', divider=True)
    st.sidebar.button('Run Summary', type="primary")


# refer to https://github.com/tylerjrichards/st-filter-dataframe/blob/main/streamlit_app.py
def filter_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Adds a UI on top of a dataframe to let viewers filter columns

    Args:
        df (pd.DataFrame): Original dataframe

    Returns:
        pd.DataFrame: Filtered dataframe
    """
    modify = st.sidebar.checkbox("Add filters")

    if not modify:
        get_df_metrics(df)
        return df

    df = df.copy()

    # Try to convert datetimes into a standard format (datetime, no timezone)
    for col in df.columns:
        if is_object_dtype(df[col]):
            try:
                df[col] = pd.to_datetime(df[col])
            except Exception:
                pass

        if is_datetime64_any_dtype(df[col]):
            df[col] = df[col].dt.tz_localize(None)

    modification_container = st.sidebar.container()

    with modification_container:
        to_filter_columns = st.multiselect("Filter dataframe on", df.columns)
        for column in to_filter_columns:
            left, right = st.columns((1, 20))
            left.write("↳")
            # Treat columns with < 10 unique values as categorical
            if df[column].nunique() < 10:
                user_cat_input = right.multiselect(
                    f"Values for {column}",
                    df[column].unique(),
                    default=list(df[column].unique()),
                )
                df = df[df[column].isin(user_cat_input)]
            elif is_numeric_dtype(df[column]):
                _min = float(df[column].min())
                _max = float(df[column].max())
                step = (_max - _min) / 100
                user_num_input = right.slider(
                    f"Values for {column}",
                    min_value=_min,
                    max_value=_max,
                    value=(_min, _max),
                    step=step,
                )
                df = df[df[column].between(*user_num_input)]
            elif is_datetime64_any_dtype(df[column]):
                user_date_input = right.date_input(
                    f"Values for {column}",
                    value=(
                        df[column].min(),
                        df[column].max(),
                    ),
                )
                if len(user_date_input) == 2:  # type: ignore
                    user_date_input = tuple(
                        map(pd.to_datetime, user_date_input))  # type: ignore
                    start_date, end_date = user_date_input  # type: ignore
                    df = df.loc[df[column].between(start_date, end_date)]
            else:
                user_text_input = right.text_input(
                    f"Substring or regex in {column}",
                )
                if user_text_input:
                    df = df[df[column].astype(
                        str).str.contains(user_text_input)]

    get_df_metrics(df)
    return df


def get_df_metrics(df: pd.DataFrame):
    st.session_state.count = df.size
    st.session_state.amount_sum = df[Col.Amount.value].sum()

# refer to https://github.com/BugzTheBunny/streamlit_custom_gui


def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)


if __name__ == "__main__":
    main(EnvironmentReader())
