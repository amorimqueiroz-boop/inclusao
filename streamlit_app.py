# streamlit_app.py
# -----------------------------------------------------------------------------
# OMNISFERA — Entry point (PIN + Sidebar)
# - Sem menu/topbar (voltamos para Sidebar)
# - Acesso por PIN (Workspace)
# - Supabase “por trás” (anon key), sem login do Supabase
# - Depois do PIN validado, libera navegação para as páginas em /pages
# -----------------------------------------------------------------------------

import os
import streamlit as st
from datetime import datetime

# Supabase client (python)
# pip install supabase
try:
    from supabase import create_client
except Exception:
    create_client = None


# -----------------------------------------------------------------------------
# CONFIG
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Omnisfera",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Pequenos ajustes visuais (opcional)
st.markdown(
    """
    <style>
      /* sidebar um pouco mais limpa */
      section[data-testid="stSidebar"] { padding-top: 14px; }
      .omni-title { font-size: 44px; font-weight: 800; letter-spacing: -0.02em; margin: 0; }
      .omni-sub { color: rgba(0,0,0,.6); margin-top: 8px; font-size: 16px; }
      .card { border: 1px solid rgba(0,0,0,.08); border-radius: 16px; padding: 18px; background: white; }
      .muted { color: rgba(0,0,0,.55); }
      .pill { display:inline-block; padding: 6px 10px; border-radius: 999px; background: rgba(0,0,0,.04); font-size: 12px; }
    </style>
    """,
    unsafe_allow_html=True,
)


# -----------------------------------------------------------------------------
# SUPABASE CLIENT (cache)
# -----------------------------------------------------------------------------
@st.cache_resource
def get_supabase():
    """
    Usa APENAS ANON KEY (como você tem no secrets).
    Se quiser endurecer segurança depois, aí sim entra service role + backend.
    """
    if create_client is None:
        st.error("Dependência 'supabase' não instalada. Adicione em requirements.txt: supabase")
        return None

    url = st.secrets.get("SUPABASE_URL") or os.getenv("SUPABASE_URL")
    key = st.secrets.get("SUPABASE_ANON_KEY") or os.getenv("SUPABASE_ANON_KEY")

    if not url or not key:
        st.error("Faltou SUPABASE_URL / SUPABASE_ANON_KEY em secrets.toml.")
        return None

    try:
        return create_client(url, key)
    except Exception as e:
        st.error(f"Erro conectando Supabase: {e}")
        return None


supabase = get_supabase()


# -----------------------------------------------------------------------------
# STATE
# -----------------------------------------------------------------------------
def _ensure_state():
    if "pin_ok" not in st.session_state:
        st.session_state.pin_ok = False
    if "workspace_id" not in st.session_state:
        st.session_state.workspace_id = None
    if "workspace_name" not in st.session_state:
        st.session_state.workspace_name = None
    if "pin_last" not in st.session_state:
        st.session_state.pin_last = ""


# -----------------------------------------------------------------------------
# RPC: workspace_from_pin
# -----------------------------------------------------------------------------
def workspace_from_pin(pin: str):
    """
    Chama RPC no Supabase:
      select * from public.workspace_from_pin(p_pin => 'DEMO-2026');
    Retorna dict {"id":..., "name":...} ou None.
    """
    if not supabase:
        return None

    pin = (pin or "").strip()
    if not pin:
        return None

    try:
        res = supabase.rpc("workspace_from_pin", {"p_pin": pin}).execute()
        data = res.data or []
        return data[0] if len(data) else None
    except Exception as e:
        # Em Streamlit Cloud, detalhes podem ser “redacted”.
        # Mesmo assim, mostramos uma mensagem amigável.
        st.error("Erro ao validar PIN no Supabase. Verifique permissões da função (grant execute) e logs.")
        st.caption(str(e))
        return None


# -----------------------------------------------------------------------------
# UI: Tela PIN
# -----------------------------------------------------------------------------
def render_pin_screen():
    left, mid, right = st.columns([1, 1.2, 1])
    with mid:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("<div class='pill'>Acesso por PIN</div>", unsafe_allow_html=True)
        st.markdown("<h1 class='omni-title'>Omnisfera</h1>", unsafe_allow_html=True)
        st.markdown(
