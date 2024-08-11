import streamlit as st
from models import EnvironmentReader, SessionStore
from report_builder import get_data_from_csv
from view_raw_data import render_raw_data
from view_financial_summary import render_financial_summary

# refer to https://github.com/BugzTheBunny/streamlit_custom_gui


def _local_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)


def _startup() -> None:
    # local_css('./css/streamlit.css')

    st.set_page_config(page_title="Finance Dashboard",
                       layout="wide")


def main(env: EnvironmentReader, session: SessionStore) -> None:
    print('Run')
    _startup()
    raw_df = get_data_from_csv(env.DATA_FILE_PATH)
    render_raw_data(session, raw_df)
    st.write(st.session_state)

    st.sidebar.header('Summary', divider=True)
    if st.sidebar.button('Run Summary', type="primary"):
        render_financial_summary(env)


if __name__ == "__main__":
    main(EnvironmentReader(), SessionStore(st.session_state))
