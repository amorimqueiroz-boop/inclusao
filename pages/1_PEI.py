# pages/1_PEI.py
import streamlit as st
from datetime import date
from io import BytesIO
from docx import Document
from openai import OpenAI
from pypdf import PdfReader
from fpdf import FPDF
import base64
import json
import os
import time
import re

# ✅ 1) set_page_config (UMA VEZ SÓ e sempre no topo)
st.set_page_config(
    page_title="Omnisfera | PEI",
    page_icon="📘",
    layout="wide",
    initial_sidebar_state="expanded",
)

APP_VERSION = "v150.0 (SaaS Design)"

# ✅ 2) UI lockdown (não quebra se faltar arquivo)
try:
    from ui_lockdown import hide_streamlit_chrome_if_needed, hide_default_sidebar_nav
    hide_streamlit_chrome_if_needed()
    hide_default_sidebar_nav()
except Exception:
    pass

# ✅ 3) Flag de ambiente (opcional)
try:
    IS_TEST_ENV = st.secrets.get("ENV") == "TESTE"
except Exception:
    IS_TEST_ENV = False

# ✅ 4) Gate mínimo: autenticado + workspace_id
if not st.session_state.get("autenticado"):
    st.error("🔒 Acesso negado. Faça login na Página Inicial.")
    st.stop()

ws_id = st.session_state.get("workspace_id")
if not ws_id:
    st.error("Workspace não definido. Volte ao Início e valide o PIN.")
    if st.button("Voltar para Login", key="pei_btn_voltar_login", use_container_width=True):
        for k in ["autenticado", "workspace_id", "workspace_name", "usuario_nome", "usuario_cargo", "supabase_jwt", "supabase_user_id"]:
            st.session_state.pop(k, None)
        st.switch_page("streamlit_app.py")
    st.stop()

# ✅ 5) Supabase (opcional: não bloqueia PEI se der ruim)
sb = None
try:
    from _client import get_supabase
    sb = get_supabase()  # <-- cliente (não é função)
except Exception:
    sb = None

# Guardas legadas (não travam)
def verificar_login_supabase():
    st.session_state.setdefault("supabase_jwt", "")
    st.session_state.setdefault("supabase_user_id", "")

verificar_login_supabase()
OWNER_ID = st.session_state.get("supabase_user_id", "")

# ✅ Sidebar UNIFICADA (navegação + sessão + salvar/carregar + sync)
with st.sidebar:
    st.markdown("### 🧭 Navegação")
    if st.button("🏠 Home", key="pei_nav_home", use_container_width=True):
        st.switch_page("streamlit_app.py")  # se sua home for pages/0_Home.py, troque aqui

    col1, col2 = st.columns(2)
    with col1:
        st.button("📘 PEI", key="pei_nav_pei", use_container_width=True, disabled=True)
    with col2:
        if st.button("🧩 PAEE", key="pei_nav_paee", use_container_width=True):
            st.switch_page("pages/2_PAE.py")

    if st.button("🚀 Hub", key="pei_nav_hub", use_container_width=True):
        st.switch_page("pages/3_Hub_Inclusao.py")

    st.markdown("---")
    st.markdown("### 👤 Sessão")
    st.caption(f"Usuário: **{st.session_state.get('usuario_nome','')}**")
    st.caption(f"Workspace: **{st.session_state.get('workspace_name','')}**")

    st.markdown("---")
    st.markdown("### 🔑 OpenAI")
    if 'OPENAI_API_KEY' in st.secrets:
        api_key = st.secrets['OPENAI_API_KEY']
        st.success("✅ OpenAI OK")
    else:
        api_key = st.text_input("Chave OpenAI:", type="password", key="pei_openai_key")

    st.markdown("---")
    st.markdown("### 🧾 Status do Aluno (Supabase)")
    st.session_state.setdefault("selected_student_id", None)
    st.session_state.setdefault("selected_student_name", "")

    student_id = st.session_state.get("selected_student_id")
    if student_id:
        st.success("✅ Vinculado ao Supabase")
        st.caption(f"student_id: {student_id[:8]}...")
    else:
        st.warning("📝 Rascunho (ainda não salvo no Supabase)")

    # Aviso se supabase não estiver pronto
    if sb is None:
        st.info("Supabase não inicializado (sb=None). O PEI funciona em rascunho, mas não salva/carrega.")

    st.markdown("---")
