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


def _img_data_uri(path_str: str) -> str | None:
    p = _root() / path_str
    if not p.exists():
        return None
    try:
        return "data:image/png;base64," + base64.b64encode(p.read_bytes()).decode()
    except Exception:
        return None


# -----------------------------------------------------------------------------
# CSS — ESCONDE SIDEBAR / HEADER E CRIA TOPBAR CLEAN
# -----------------------------------------------------------------------------
def _inject_shell_css():
    st.markdown(
        f"""
<style>
/* Esconde sidebar e header nativo (mantém multipage funcional por page_link) */
[data-testid="stSidebar"],
[data-testid="stHeader"],
header,
#MainMenu,
footer {{
  display: none !important;
}}

/* Garante espaço abaixo da topbar fixa */
.main .block-container {{
  padding-top: {TOPBAR_HEIGHT + TOPBAR_PADDING}px !important;
}}

/* TOPBAR */
.omni-topbar {{
  position: fixed;
  top: 0; left: 0; right: 0;
  height: {TOPBAR_HEIGHT}px;
  z-index: 9999;

  display: flex;
  align-items: center;
  justify-content: space-between;

  padding: 0 16px;

  background: rgba(255,255,255,0.88);
  backdrop-filter: blur(12px);
  border-bottom: 1px solid rgba(0,0,0,0.08);
}}

/* BRAND (logo + wordmark) */
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
  opacity: .92;
}}

/* NAV wrapper (só pra alinhamento) */
.omni-nav {{
  display: flex;
  align-items: center;
  gap: 10px;
}}

/* Ajusta o estilo dos page_link (eles viram <a>) */
.omni-nav a {{
  display: flex !important;
  align-items: center !important;
  justify-content: center !important;

  width: 36px !important;
  height: 36px !important;
  border-radius: 12px !important;

  background: rgba(0,0,0,0.04) !important;
  border: 1px solid rgba(0,0,0,0.08) !important;

  transition: background .12s ease, transform .12s ease, box-shadow .12s ease;
  text-decoration: none !important;
}}

.omni-nav a:hover {{
  background: rgba(0,0,0,0.06) !important;
  transform: translateY(-1px);
  box-shadow: 0 10px 24px rgba(0,0,0,0.08);
}}

.omni-nav a svg {{
  width: 18px !important;
  height: 18px !important;
}}

/* Remove espaços extras que o Streamlit pode colocar em links/botões */
.omni-nav [data-testid="stPageLink"] > div {{
  margin: 0 !important;
  padding: 0 !important;
}}
</style>
        """,
        unsafe_allow_html=True,
    )


# -----------------------------------------------------------------------------
# TOPBAR (VISUAL) + PAGE_LINK (FUNCIONAL)
# -----------------------------------------------------------------------------
def _render_topbar():
    # tenta achar arquivos em /assets ou na raiz (se você manteve lá)
    logo = _img_data_uri("assets/omni_icone.png") or _img_data_uri("omni_icone.png")
    word = _img_data_uri("assets/omni_texto.png") or _img_data_uri("omni_texto.png")

    _inject_shell_css()

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

    # Links funcionais (igual sidebar), na mesma aba e preservando session_state
    # IMPORTANTÍSSIMO: os caminhos precisam bater com os nomes reais em /pages
    with st.container():
        cols = st.columns(7, gap="small")

        with cols[0]:
            st.page_link("streamlit_app.py", icon="🏠", label="")

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
# PUBLIC BOOT
# -----------------------------------------------------------------------------
def boot_ui():
    """
    Chame isso no topo de cada página/arquivo.
    - Garante estado de auth
    - Renderiza topbar apenas quando autenticado
    """
    ensure_auth_state()

    if st.session_state.autenticado:
        _render_topbar()
