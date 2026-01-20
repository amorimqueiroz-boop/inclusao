# ui_nav.py
from __future__ import annotations

import base64
from pathlib import Path
import streamlit as st

# =============================================================================
# CONFIG
# =============================================================================
TOPBAR_HEIGHT = 56
TOPBAR_PADDING = 12


# =============================================================================
# AUTH STATE
# =============================================================================
def ensure_auth_state():
    if "autenticado" not in st.session_state:
        st.session_state.autenticado = False
    if "user" not in st.session_state:
        st.session_state.user = None


# =============================================================================
# FILE / PATH UTILS
# =============================================================================
def _project_root() -> Path:
    return Path(__file__).resolve().parent


def _page_exists(relative_path: str) -> bool:
    p = _project_root() / relative_path
    return p.exists() and p.is_file()


def _get_qp(key: str, default: str | None = None) -> str | None:
    try:
        return st.query_params.get(key, default)
    except Exception:
        return default


def _img_to_data_uri(path: Path) -> str | None:
    if not path.exists() or not path.is_file():
        return None
    try:
        data = base64.b64encode(path.read_bytes()).decode("utf-8")
        return f"data:image/png;base64,{data}"
    except Exception:
        return None


# =============================================================================
# ICONS (FLATICON UICONS)
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
# CSS SHELL (HIDE STREAMLIT UI + TOPBAR)
# =============================================================================
def inject_shell_css():
    st.markdown(
        f"""
<style>
/* remove UI nativa */
[data-testid="stHeader"], header,
footer, #MainMenu,
[data-testid="stToolbar"],
[data-testid="stDecoration"] {{
  display: none !important;
}}

/* empurra conteúdo */
.main .block-container {{
  padding-top: {TOPBAR_HEIGHT + TOPBAR_PADDING}px !important;
}}

/* topbar base */
.omni-topbar {{
  position: fixed;
  top: 0; left: 0; right: 0;
  height: {TOPBAR_HEIGHT}px;
  z-index: 999999;

  display:flex;
  align-items:center;
  justify-content:space-between;

  padding: 0 14px;
  background: rgba(12,12,14,0.78);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border-bottom: 1px solid rgba(255,255,255,0.08);
}}

/* brand (logo + wordmark) */
.omni-brand {{
  display:flex;
  align-items:center;
  gap:10px;
  color: rgba(255,255,255,0.95);
  user-select:none;
}}

.omni-logo-wrap {{
  width: 34px;
  height: 34px;
  border-radius: 12px;
  display:flex;
  align-items:center;
  justify-content:center;

  background: rgba(255,255,255,0.06);
  border: 1px solid rgba(255,255,255,0.10);
  box-shadow:
    0 0 0 4px rgba(255,255,255,0.04),
    0 12px 30px rgba(0,0,0,0.20),
    0 0 26px rgba(255,255,255,0.14);
}}

.omni-logo {{
  width: 22px;
  height: 22px;
  object-fit: contain;
  filter: drop-shadow(0 0 14px rgba(255,255,255,0.25));
}}

.omni-wordmark {{
  display:flex;
  flex-direction:column;
  line-height: 1.05;
}}

.omni-wordmark .name {{
  font-weight: 950;
  font-size: 14px;
  letter-spacing: .2px;
}}

.omni-wordmark .tag {{
  font-size: 11px;
  opacity: .62;
  margin-top: 2px;
}}

/* pulse “gritando” com elegância */
@keyframes omniPulse {{
  0%   {{ box-shadow: 0 0 0 4px rgba(255,255,255,0.04), 0 12px 30px rgba(0,0,0,0.20), 0 0 18px rgba(255,255,255,0.10); }}
  50%  {{ box-shadow: 0 0 0 5px rgba(255,255,255,0.06), 0 14px 34px rgba(0,0,0,0.24), 0 0 30px rgba(255,255,255,0.18); }}
  100% {{ box-shadow: 0 0 0 4px rgba(255,255,255,0.04), 0 12px 30px rgba(0,0,0,0.20), 0 0 18px rgba(255,255,255,0.10); }}
}}
.omni-logo-wrap {{
  animation: omniPulse 3.2s ease-in-out infinite;
}}

/* nav */
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

  text-decoration:none;
  background: rgba(255,255,255,0.06);
  border: 1px solid rgba(255,255,255,0.08);

  transition: transform .12s ease, background .12s ease, border-color .12s ease, opacity .12s ease;
}}

.nav-item:hover {{
  transform: translateY(-1px);
  background: rgba(255,255,255,0.10);
  border-color: rgba(255,255,255,0.14);
}}

.nav-item.active {{
  background: rgba(255,255,255,0.14);
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


# =============================================================================
# ROUTES
# =============================================================================
def ROUTES():
    # Home atual: pages/home.py (como está no seu repo)
    return {
        "home": {
            "label": "Home",
            "page": "pages/home.py",
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
        # futuras (desabilita se não existir)
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
    go = _get_qp("go", default) or default
    if go not in ROUTES():
        return default
    return go


# =============================================================================
# TOPBAR RENDER
# =============================================================================
def render_topbar(active_go: str):
    routes = ROUTES()

    # logo embutida (base64) — funciona no Streamlit Cloud
    logo_path = _project_root() / "omni_icone.png"
    logo_uri = _img_to_data_uri(logo_path)
    logo_html = (
        f"<img class='omni-logo' src='{logo_uri}'/>"
        if logo_uri
        else "<span style='font-size:18px; line-height:1;'>🌿</span>"
    )

    def _item(go: str) -> str:
        r = routes[go]
        exists = _page_exists(r["page"])

        cls = ["nav-item"]
        if go == active_go:
            cls.append("active")
        if not exists:
            cls.append("disabled")

        href = f"?go={go}" if exists else "#"
        return f"""
<a class="{' '.join(cls)}" href="{href}" title="{r['label']}" aria-label="{r['label']}">
  <i class="{r['icon']}" style="color:{r['color']}"></i>
</a>
"""

    order = ["home", "alunos", "pei", "pae", "hub", "diario", "dados"]
    items_html = "\n".join(_item(go) for go in order if go in routes)

    st.markdown(
        f"""
<div class="omni-topbar">
  <div class="omni-brand">
    <div class="omni-logo-wrap">
      {logo_html}
    </div>
    <div class="omni-wordmark">
      <div class="name">Omnisfera</div>
      <div class="tag">Inclusão • PEI • Dados</div>
    </div>
  </div>

  <div class="omni-nav">
    {items_html}
  </div>
</div>
        """,
        unsafe_allow_html=True,
    )


# =============================================================================
# ROUTER
# =============================================================================
def route_from_query(default_go: str = "home"):
    # evita loop
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
# BOOTSTRAP
# =============================================================================
def boot_ui(do_route: bool = False):
    ensure_auth_state()
    inject_icons_cdn()
    inject_shell_css()

    active = get_active_go()

    # Só mostra topbar quando autenticado
    if st.session_state.autenticado:
        render_topbar(active)

    if do_route:
        route_from_query(default_go="home")
