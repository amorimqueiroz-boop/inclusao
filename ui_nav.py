# ui_nav.py
from __future__ import annotations

import os
from pathlib import Path
import streamlit as st

# -----------------------------------------------------------------------------
# UI NAV — Topbar fixa + roteamento via query param (?go=...)
# - Sem sidebar
# - Esconde UI nativa Streamlit (header/menu/footer)
# - Ícones Flaticon UIcons (CDN)
# - Desabilita rotas cujas páginas não existem
# -----------------------------------------------------------------------------

TOPBAR_H = 56
TOPBAR_PAD = 12  # espaço extra entre topbar e conteúdo


def _project_root() -> Path:
    # assume que ui_nav.py está na raiz do projeto
    return Path(__file__).resolve().parent


def _page_exists(rel_path: str) -> bool:
    p = _project_root() / rel_path
    return p.exists() and p.is_file()


def _safe_query_get(key: str, default: str | None = None) -> str | None:
    try:
        qp = st.query_params
        val = qp.get(key, default)
        return val
    except Exception:
        return default


def set_go(go: str):
    """Atualiza query param go sem depender de JS."""
    try:
        st.query_params["go"] = go
    except Exception:
        pass


def inject_icons_cdn():
    # Mantém compatível com o seu padrão (v3.0.0)
    st.markdown(
        """
<link rel="stylesheet" href="https://cdn-uicons.flaticon.com/3.0.0/uicons-solid-rounded/css/uicons-solid-rounded.css">
<link rel="stylesheet" href="https://cdn-uicons.flaticon.com/3.0.0/uicons-bold-rounded/css/uicons-bold-rounded.css">
<link rel="stylesheet" href="https://cdn-uicons.flaticon.com/3.0.0/uicons-solid-straight/css/uicons-solid-straight.css">
        """,
        unsafe_allow_html=True,
    )


def inject_shell_css(topbar_h: int = TOPBAR_H, topbar_pad: int = TOPBAR_PAD):
    st.markdown(
        f"""
<style>
/* --- Remove UI nativa Streamlit (robusto por data-testid) --- */
[data-testid="stHeader"], header {{ display: none !important; }}
#MainMenu {{ display: none !important; }}
footer {{ display: none !important; }}
[data-testid="stToolbar"] {{ display: none !important; }}
[data-testid="stDecoration"] {{ display: none !important; }}

/* --- Ajuste de espaçamento do conteúdo para não ficar atrás da topbar --- */
.main .block-container {{
  padding-top: {int(topbar_h + topbar_pad)}px !important;
}}

/* --- Topbar Omnisfera --- */
.omni-topbar {{
  position: fixed;
  top: 0; left: 0; right: 0;
  height: {int(topbar_h)}px;
  z-index: 999999;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 14px;

  background: rgba(12, 12, 14, 0.78);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border-bottom: 1px solid rgba(255,255,255,0.08);
}}

.omni-brand {{
  display:flex;
  align-items:center;
  gap:10px;
  color: rgba(255,255,255,0.92);
  font-weight: 750;
  letter-spacing: .2px;
  font-size: 14px;
  user-select: none;
}}

.omni-dot {{
  width: 10px;
  height: 10px;
  border-radius: 999px;
  background: rgba(255,255,255,0.76);
  box-shadow: 0 0 14px rgba(255,255,255,0.22);
}}

.omni-nav {{
  display:flex;
  align-items:center;
  gap:10px;
}}

.nav-item {{
  width: 36px;
  height: 36px;
  border-radius: 12px;

  display:flex;
  align-items:center;
  justify-content:center;

  text-decoration: none;
  background: rgba(255,255,255,0.06);
  border: 1px solid rgba(255,255,255,0.08);

  transition: transform .12s ease, background .12s ease, border-color .12s ease, opacity .12s ease;
}}

.nav-item:hover {{
  transform: translateY(-1px);
  background: rgba(255,255,255,0.09);
  border-color: rgba(255,255,255,0.14);
}}

.nav-item.active {{
  background: rgba(255,255,255,0.12);
  border-color: rgba(255,255,255,0.18);
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


def _route_table():
    """
    Defina aqui a tabela de rotas.
    Mantenha paths relativos à raiz do projeto.
    """
    return {
        "home": {"label": "Home", "page": "home_portal.py", "icon": "fi fi-br-home", "color": "#EDEDED"},
        "alunos": {"label": "Alunos", "page": "pages/0_Alunos.py", "icon": "fi fi-sr-users", "color": "#8BE9FD"},
        "pei": {"label": "PEI", "page": "pages/1_PEI.py", "icon": "fi fi-sr-document-signed", "color": "#BD93F9"},
        "pae": {"label": "PAE", "page": "pages/2_PAE.py", "icon": "fi fi-ss-bullseye-arrow", "color": "#50FA7B"},
        "hub": {"label": "Hub", "page": "pages/3_Hub_Inclusao.py", "icon": "fi fi-sr-book-open-cover", "color": "#FFB86C"},

        # Futuro (deixa aqui, mas vai desabilitar se não existir)
        "diario": {"label": "Diário", "page": "pages/4_Diario.py", "icon": "fi fi-br-notebook", "color": "#F1FA8C"},
        "dados":  {"label": "Dados",  "page": "pages/5_Dados.py",  "icon": "fi fi-br-chart-histogram", "color": "#FF79C6"},
        "ia":     {"label": "IA",     "page": "pages/6_IA.py",     "icon": "fi fi-br-brain", "color": "#A78BFA"},
    }


def get_active_go(default: str = "home") -> str:
    go = _safe_query_get("go", default) or default
    routes = _route_table()
    if go not in routes:
        return default
    return go


def render_topbar(active_go: str | None = None):
    routes = _route_table()
    active = active_go or get_active_go()

    def nav_item(go: str) -> str:
        r = routes[go]
        exists = _page_exists(r["page"])
        cls = "nav-item"
        if go == active:
            cls += " active"
        if not exists:
            cls += " disabled"

        href = f'?go={go}' if exists else "#"
        icon = r["icon"]
        color = r.get("color", "#EDEDED")
        label = r["label"]

        return f"""
<a class="{cls}" href="{href}" title="{label}" aria-label="{label}">
  <i class="{icon}" style="color:{color}"></i>
</a>
"""

    # Ordem dos ícones (mantém coerência com seu mapeamento)
    order = ["home", "alunos", "pei", "pae", "hub", "diario", "dados", "ia"]
    items_html = "\n".join([nav_item(go) for go in order if go in routes])

    st.markdown(
        f"""
<div class="omni-topbar">
  <div class="omni-brand">
    <div class="omni-dot"></div>
    <div>Omnisfera</div>
  </div>
  <div class="omni-nav">
    {items_html}
  </div>
</div>
        """,
        unsafe_allow_html=True,
    )


def route_from_query(default_go: str = "home"):
    """
    Roteia baseado em ?go=...
    - Se rota inválida: volta para default
    - Se página não existe: volta para default
    - Evita loop: roda uma vez por ciclo
    """
    if st.session_state.get("_routed_once"):
        return

    routes = _route_table()
    go = get_active_go(default_go)

    target_rel = routes.get(go, routes[default_go])["page"]
    if not _page_exists(target_rel):
        go = default_go
        target_rel = routes[default_go]["page"]

    # se estiver na página alvo, não faz nada
    try:
        # Identifica a página atual pelo nome do script (best-effort)
        current = os.environ.get("STREAMLIT_SCRIPT_NAME", "")
        # Em Streamlit Cloud isso pode não existir; então usamos um fallback simples.
    except Exception:
        current = ""

    st.session_state["_routed_once"] = True
    try:
        st.switch_page(target_rel)
    except Exception:
        # Se switch_page falhar por alguma razão, pelo menos não quebra a UI
        st.session_state["_routed_once"] = False


def boot_ui(hide_on_go: tuple[str, ...] = ("login",), do_route: bool = False):
    """
    Chame isso no TOPO do streamlit_app.py e no TOPO de cada página.
    - injeta CDN e CSS global
    - renderiza topbar
    - opcional: roteia a partir do query param (use só no entrypoint)
    """
    inject_icons_cdn()
    inject_shell_css(TOPBAR_H, TOPBAR_PAD)

    active = get_active_go()
    if active not in hide_on_go:
        render_topbar(active)

    if do_route:
        route_from_query(default_go="home")

    def ensure_auth_state():
    if "autenticado" not in st.session_state:
        st.session_state.autenticado = False
    if "user" not in st.session_state:
        st.session_state.user = None


def route_gate(default_go: str = "home"):
    """
    Gateway de rota:
    - se não autenticado -> força go=login
    - se autenticado -> permite navegação normal
    """
    ensure_auth_state()

    go = get_active_go(default_go="home")

    if not st.session_state.autenticado:
        # força login
        try:
            st.query_params["go"] = "login"
        except Exception:
            pass
        return "login"

    return go


def boot_ui(hide_on_go: tuple[str, ...] = ("login",), do_route: bool = False):
    """
    Chame no topo do entrypoint e das páginas.
    """
    ensure_auth_state()
    inject_icons_cdn()
    inject_shell_css(TOPBAR_H, TOPBAR_PAD)

    # Se não estiver autenticado, esconda topbar
    active = get_active_go()
    if active not in hide_on_go and st.session_state.autenticado:
        render_topbar(active)

    # roteamento só no entrypoint
    if do_route:
        route_from_query(default_go="home")
