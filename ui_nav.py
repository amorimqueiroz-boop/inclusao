# ui_nav.py
from __future__ import annotations

import os
from pathlib import Path
import streamlit as st

# =============================================================================
# CONFIGURAÇÃO GERAL
# =============================================================================

TOPBAR_HEIGHT = 56
TOPBAR_PADDING = 12


# =============================================================================
# ESTADO DE AUTENTICAÇÃO
# =============================================================================

def ensure_auth_state():
    if "autenticado" not in st.session_state:
        st.session_state.autenticado = False
    if "user" not in st.session_state:
        st.session_state.user = None


# =============================================================================
# UTILITÁRIOS
# =============================================================================

def _project_root() -> Path:
    return Path(__file__).resolve().parent


def _page_exists(relative_path: str) -> bool:
    p = _project_root() / relative_path
    return p.exists() and p.is_file()


def _get_query_param(key: str, default: str | None = None) -> str | None:
    try:
        return st.query_params.get(key, default)
    except Exception:
        return default


# =============================================================================
# ICONES (FLATICON)
# =============================================================================

def inject_icons_cdn():
    st.markdown(
        """
<link rel="stylesheet" href="https://cdn-uicons.flaticon.com/3.0.0/uicons-solid-rounded/css/uicons-solid-rounded.css">
<link rel="stylesheet" href="https://cdn-uicons.flaticon.com/3.0.0/uicons-bold-rounded/css/uicons-bold-rounded.css">
<link rel="stylesheet" href="https://cdn-uicons.flaticon.com/3.0.0/uicons-solid-straight/css/uicons-solid-straight.css">
        """,
        unsafe_allow_html=True,
    )


# =============================================================================
# CSS GLOBAL (DESATIVA UI NATIVA + TOPBAR)
# =============================================================================

def inject_shell_css():
    st.markdown(
        f"""
<style>
/* --- Remove UI nativa do Streamlit --- */
[data-testid="stHeader"],
header,
footer,
#MainMenu,
[data-testid="stToolbar"],
[data-testid="stDecoration"] {{
    display: none !important;
}}

/* --- Ajuste do conteúdo --- */
.main .block-container {{
    padding-top: {TOPBAR_HEIGHT + TOPBAR_PADDING}px !important;
}}

/* --- TOPBAR --- */
.omni-topbar {{
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    height: {TOPBAR_HEIGHT}px;
    z-index: 999999;

    display: flex;
    align-items: center;
    justify-content: space-between;

    padding: 0 14px;
    background: rgba(12,12,14,0.78);
    backdrop-filter: blur(10px);
    border-bottom: 1px solid rgba(255,255,255,0.08);
}}

.omni-brand {{
    display: flex;
    align-items: center;
    gap: 10px;
    font-weight: 700;
    font-size: 14px;
    color: rgba(255,255,255,0.95);
}}

.omni-dot {{
    width: 10px;
    height: 10px;
    border-radius: 50%;
    background: rgba(255,255,255,0.8);
    box-shadow: 0 0 12px rgba(255,255,255,0.25);
}}

.omni-nav {{
    display: flex;
    gap: 10px;
}}

.nav-item {{
    width: 36px;
    height: 36px;
    border-radius: 12px;

    display: flex;
    align-items: center;
    justify-content: center;

    background: rgba(255,255,255,0.06);
    border: 1px solid rgba(255,255,255,0.08);
    text-decoration: none;

    transition: all 0.15s ease;
}}

.nav-item:hover {{
    transform: translateY(-1px);
    background: rgba(255,255,255,0.10);
}}

.nav-item.active {{
    background: rgba(255,255,255,0.14);
    border-color: rgba(255,255,255,0.20);
}}

.nav-item.disabled {{
    opacity: 0.35;
    pointer-events: none;
    filter: grayscale(1);
}}

.nav-item i {{
    font-size: 18px;
    line-height: 1;
}}
</style>
        """,
        unsafe_allow_html=True,
    )


# =============================================================================
# ROTAS DO SISTEMA
# =============================================================================

def ROUTES():
    return {
        "home": {
            "label": "Home",
            "page": "home_portal.py",
            "icon": "fi fi-br-home",
            "color": "#EDEDED",
        },
        "alunos": {
            "label": "Alunos",
            "page": "pages/0_Alunos.py",
            "icon": "fi fi-sr-users",
            "color": "#8BE9FD",
        },
        "pei": {
            "label": "PEI",
            "page": "pages/1_PEI.py",
            "icon": "fi fi-sr-document-signed",
            "color": "#BD93F9",
        },
        "pae": {
            "label": "PAE",
            "page": "pages/2_PAE.py",
            "icon": "fi fi-ss-bullseye-arrow",
            "color": "#50FA7B",
        },
        "hub": {
            "label": "Hub",
            "page": "pages/3_Hub_Inclusao.py",
            "icon": "fi fi-sr-book-open-cover",
            "color": "#FFB86C",
        },
        # futuras
        "diario": {
            "label": "Diário",
            "page": "pages/4_Diario.py",
            "icon": "fi fi-br-notebook",
            "color": "#F1FA8C",
        },
        "dados": {
            "label": "Dados",
            "page": "pages/5_Dados.py",
            "icon": "fi fi-br-chart-histogram",
            "color": "#FF79C6",
        },
    }


def get_active_go(default: str = "home") -> str:
    go = _get_query_param("go", default)
    if go not in ROUTES():
        return default
    return go


# =============================================================================
# TOPBAR
# =============================================================================

def render_topbar(active_go: str):
    routes = ROUTES()

    def render_item(go: str):
        r = routes[go]
        exists = _page_exists(r["page"])

        classes = ["nav-item"]
        if go == active_go:
            classes.append("active")
        if not exists:
            classes.append("disabled")

        href = f"?go={go}" if exists else "#"

        return f"""
<a class="{' '.join(classes)}" href="{href}" title="{r['label']}">
  <i class="{r['icon']}" style="color:{r['color']}"></i>
</a>
"""

    order = ["home", "alunos", "pei", "pae", "hub", "diario", "dados"]
    items = "\n".join(render_item(go) for go in order if go in routes)

    st.markdown(
        f"""
<div class="omni-topbar">
  <div class="omni-brand">
    <div class="omni-dot"></div>
    <div>Omnisfera</div>
  </div>
  <div class="omni-nav">
    {items}
  </div>
</div>
        """,
        unsafe_allow_html=True,
    )


# =============================================================================
# ROTEAMENTO
# =============================================================================

def route_from_query(default_go: str = "home"):
    if st.session_state.get("_already_routed"):
        return

    routes = ROUTES()
    go = get_active_go(default_go)
    target = routes.get(go, routes[default_go])["page"]

    if not _page_exists(target):
        target = routes[default_go]["page"]

    st.session_state["_already_routed"] = True
    st.switch_page(target)


# =============================================================================
# BOOTSTRAP GLOBAL
# =============================================================================

def boot_ui(do_route: bool = False):
    ensure_auth_state()
    inject_icons_cdn()
    inject_shell_css()

    active = get_active_go()

    if st.session_state.autenticado:
        render_topbar(active)

    if do_route:
        route_from_query(default_go="home")
