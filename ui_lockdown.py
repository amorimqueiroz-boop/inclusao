# ui_lockdown.py
import streamlit as st

def hide_streamlit_chrome_if_needed():
    """
    Se ENV != TESTE (ou não existir), esconde menus nativos do Streamlit.
    """
    try:
        is_test = (st.secrets.get("ENV") == "TESTE")
    except Exception:
        is_test = False

    if not is_test:
        st.markdown(
            """
            <style>
              #MainMenu { visibility: hidden; }
              footer { visibility: hidden; }
              header { visibility: hidden; }
            </style>
            """,
            unsafe_allow_html=True
        )

def hide_default_sidebar_nav():
    st.markdown(
        """
        <style>
          [data-testid="stSidebarNav"] { display: none !important; }
        </style>
        """,
        unsafe_allow_html=True
    )
