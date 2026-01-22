# streamlit_app.py
import os
import streamlit as st
from login_view import render_login


def get_env() -> str:
    try:
        v = st.secrets.get("ENV", None)
        if v:
            return str(v).strip().upper()
    except Exception:
        pass
    return (os.getenv("ENV") or "").strip().upper()


ENV = get_env()

st.set_page_config(
    page_title="Omnisfera | Ecossistema",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Esconde chrome só fora do TESTE
if ENV != "TESTE":
    st.markdown(
        """
        <style>
          #MainMenu {visibility: hidden;}
          footer {visibility: hidden;}
          header {visibility: hidden;}
          [data-testid="stToolbar"] {visibility: hidden;}
        </style>
        """,
        unsafe_allow_html=True,
    )

# Estado mínimo
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False
if "workspace_id" not in st.session_state:
    st.session_state.workspace_id = None
if "workspace_name" not in st.session_state:
    st.session_state.workspace_name = None

HOME_PAGE = "pages/0_Home.py"

# Router
if not st.session_state.autenticado:
    render_login()
else:
    # Se por algum motivo entrou sem workspace, força relogar
    if not st.session_state.workspace_id:
        st.session_state.autenticado = False
        st.warning("Workspace não encontrado. Faça login novamente.")
        render_login()
    else:
        # Vai para Home real (multipage)
        st.switch_page(HOME_PAGE)
