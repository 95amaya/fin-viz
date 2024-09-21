import streamlit as st
from models import EnvironmentReader, SessionStore
from report_builder import get_data_from_csv
from view_raw_data import render_raw_data_filters
from view_financial_summary import render_financial_summary


def _local_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)


def _startup() -> None:
    # refer to https://github.com/BugzTheBunny/streamlit_custom_gui
    # local_css('./css/streamlit.css')

    st.set_page_config(page_title="Finance Dashboard",
                       layout="wide")


def main(env: EnvironmentReader, session: SessionStore) -> None:
    print('Run')
    _startup()
    app_container = st.container()
    session.state.raw_df = get_data_from_csv(env.DATA_FILE_PATH)

    st.sidebar.header('Summary', divider=True)
    if st.sidebar.button('Run Summary', type="primary"):
        render_financial_summary(env, session.state.raw_df)

    st.sidebar.header("Raw Data", divider=True)
    with st.sidebar:
        render_raw_data_filters(session, app_container.empty())

    st.sidebar.write(st.session_state)


if __name__ == "__main__":
    main(EnvironmentReader(), SessionStore(st.session_state))
