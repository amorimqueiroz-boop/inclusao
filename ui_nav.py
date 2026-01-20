# ui_nav.py
from __future__ import annotations

import base64
from pathlib import Path
import streamlit as st

# -----------------------------------------------------------------------------
# CONFIG
# -----------------------------------------------------------------------------
TOPBAR_HEIGHT = 56
TOPBAR_PADDING = 14


# -----------------------------------------------------------------------------
# AUTH STATE (simples)
# -----------------------------------------------------------------------------
def ensure_auth_state():
    if "autenticado" not in st.session_state:
        st.session_state.autenticado = False
    if "user" not in st.session_state:
        st.session_state.user = None


# -----------------------------------------------------------------------------
# ASSETS
# -----------------------------------------------------------------------------
def _root() -> Path:
    return Path(__file__).resolve().parent


def _img_data_uri(filename: str) -> str | None:
    path = _root() / filename
    if not path.exists():
        return None
    try:
        return "data:image/png;base64," + base64.b64encode(path.read_bytes()).decode()
    except Exception:
        return None


# -----------------------------------------------------------------------------
# CSS — ESCONDE SIDEBAR / HEADER E CRIA TOPBAR CLEAN
# -----------------------------------------------------------------------------
def inject_shell_css():
    st.markdown(
        f"""
<style>
/* esconde sidebar e header nativo */
[data-testid="stSidebar"],
[data-testid="stHeader"],
header,
#MainMenu,
footer {{
  display: none !important;
}}

/* respiro abaixo da topbar */
.main .block-container {{
  padding-top: {TOPBAR_HEIGHT + TOPBAR_PADDING}px !important;
}}

/* topbar */
.omni-topbar {{
  position: fixed;
  top: 0; left: 0; right: 0;
  height: {TOPBAR_HEIGHT}px;
  z-index: 9999;

  display: flex;
  align-items: center;
  justify-content: space-between;

  padding: 0 16px;

  background: rgba(255,255,255,0.85);
  backdrop-filter: blur(12px);
  border-bottom: 1px solid rgba(0,0,0,0.08);
}}

/* brand */
.omni-brand {{
  display: flex;
  align-items: center;
  gap: 10px;
}}

.omni-logo {{
  width: 28px;
  height: 28px;
  object-fit: contain;
}}

.omni-wordmark {{
  height: 16px;
  opacity: .9;
}}

/* nav area */
.omni-nav {{
  display: flex;
  gap: 14px;
}}

/* page_link style override */
.omni-nav a {{
  display: flex;
  align-items: center;
  justify-content: center;

  width: 36px;
  height: 36px;
  border-radius: 12px;

  background: rgba(0,0,0,0.04);
  border: 1px solid rgba(0,0,0,0.08);

  transition: background .12s ease, transform .12s ease;
}}

.omni-nav a:hover {{
  background: rgba(0,0,0,0.06);
  transform: translateY(-1px);
}}

.omni-nav a svg {{
  width: 18px;
  height: 18px;
}}
</style>
        """,
        unsafe_allow_html=True,
    )


# -----------------------------------------------------------------------------
# TOPBAR (VISUAL) + PAGE_LINK (FUNCIONAL)
# -----------------------------------------------------------------------------
def render_topbar():
    logo = _img_data_uri("assets/omni_icone.png") or _img_data_uri("omni_icone.png")
    word = _img_data_uri("assets/omni_texto.png") or _img_data_uri("omni_texto.png")

    inject_shell_css()

    st.markdown(
        f"""
<div class="omni-topbar">
  <div class="omni-brand">
    {"<img class='omni-logo' src='"+logo+"'/>" if logo else "🌿"}
    {"<img class='omni-wordmark' src='"+word+"'/>" if word else "<b>Omnisfera</b>"}
  </div>
  <div class="omni-nav"></div>
</div>
        """,
        unsafe_allow_html=True,
    )

    # LINKS FUNCIONAIS (igual sidebar)
    with st.container():
    cols = st.columns(7, gap="small")

    with cols[0]:
        st.page_link("pages/home.py", icon="🏠", label="")

    with cols[1]:
        st.page_link("pages/0_Alunos.py", icon="👥", label="")

    with cols[2]:
        st.page_link("pages/1_PEI.py", icon="🧠", label="")

    with cols[3]:
        st.page_link("pages/2_PAE.py", icon="🎯", label="")

    with cols[4]:
        st.page_link("pages/3_Hub_Inclusao.py", icon="📚", label="")

    with cols[5]:
        st.page_link("pages/4_Diario_de_Bordo.py", icon="📝", label="")

    with cols[6]:
        st.page_link("pages/5_Monitoramento_Avaliacao.py", icon="📈", label="")


# -----------------------------------------------------------------------------
# BOOT
# -----------------------------------------------------------------------------
def boot_ui():
    ensure_auth_state()
    if st.session_state.autenticado:
        render_topbar()
