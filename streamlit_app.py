# streamlit_app.py
import streamlit as st

from omni_utils import ensure_state

# Views
from login_view import render_login
from home_view import render_home


st.set_page_config(
    page_title="Omnisfera",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="collapsed",
)

ensure_state()

# --- Roteamento simples por estado (sem multipage / sem switch_page) ---
view = st.session_state.get("view", "login")

if view == "login":
    render_login()
elif view == "home":
    render_home()
elif view == "pei":
    # PEI "intocado": importá-lo aqui faz o script do PEI rodar normalmente.
    # ✅ Recomendo renomear seu arquivo do PEI perfeito para: pei.py
    # (assim fica mais limpo e previsível)
    try:
        import pei  # noqa: F401  (apenas importar já executa o PEI se for script)
    except Exception as e:
        st.error("Não consegui abrir o PEI.")
        st.exception(e)
        if st.button("← Voltar para Home"):
            st.session_state.view = "home"
            st.rerun()
else:
    st.session_state.view = "login"
    st.rerun()
