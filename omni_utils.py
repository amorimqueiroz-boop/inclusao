import streamlit as st
from datetime import date

# =============================================================================
# ESTADO GLOBAL
# =============================================================================
def ensure_state():
    if "autenticado" not in st.session_state:
        st.session_state.autenticado = False
    if "user" not in st.session_state:
        st.session_state.user = None


# =============================================================================
# LOGIN
# =============================================================================
def verificar_acesso():
    ensure_state()

    if st.session_state.autenticado:
        return True

    st.markdown("## 🔐 Acesso ao Omnisfera")

    with st.form("login"):
        nome = st.text_input("Nome")
        cargo = st.text_input("Cargo")
        senha = st.text_input("Senha", type="password")
        ok = st.form_submit_button("Entrar")

    if ok:
        senha_ok = "OMNI2026"
        if not nome or not cargo:
            st.warning("Preencha todos os campos.")
        elif senha != senha_ok:
            st.error("Senha incorreta.")
        else:
            st.session_state.autenticado = True
            st.session_state.user = {
                "nome": nome,
                "cargo": cargo
            }
            st.rerun()

    st.stop()


# =============================================================================
# SIDEBAR
# =============================================================================
def render_sidebar():
    user = st.session_state.user

    with st.sidebar:
        st.markdown("## 🌿 Omnisfera")
        st.caption(f"{user['nome']} · {user['cargo']}")
        st.markdown("---")

        st.page_link("streamlit_app.py", label="🏠 Home")
        st.page_link("pages/0_Alunos.py", label="👥 Alunos")
        st.page_link("pages/1_PEI.py", label="🧠 PEI 360º")
        st.page_link("pages/2_PAE.py", label="🎯 PAE")
        st.page_link("pages/3_Hub_Inclusao.py", label="🚀 Hub Inclusão")
        st.page_link("pages/4_Diario.py", label="📓 Diário")
        st.page_link("pages/5_Dados.py", label="📊 Dados")

        st.markdown("---")
        if st.button("🔒 Sair"):
            st.session_state.autenticado = False
            st.session_state.user = None
            st.rerun()
