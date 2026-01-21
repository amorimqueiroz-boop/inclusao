from __future__ import annotations

import base64
from pathlib import Path
import streamlit as st

# -----------------------------
# PUBLIC API
# -----------------------------
def ensure_auth_state():
    """
    Estado mínimo.
    IMPORTANTE: começa deslogado por padrão.
    """
    if "autenticado" not in st.session_state:
        st.session_state.autenticado = False
    if "user" not in st.session_state:
        st.session_state.user = None


def boot_ui(do_route: bool = True):
    """
    Chame no topo do streamlit_app.py e de TODAS as páginas em /pages.
    - Injeta CSS (esconde UI nativa + topbar)
    - Opcionalmente roteia via ?go= (do_route=True)
    """
    ensure_auth_state()
    _inject_css()

    if st.session_state.get("autenticado") and do_route:
        _route_from_query()


# -----------------------------
# PATHS / ASSETS
# -----------------------------
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


# -----------------------------
# NAV MAP (SEUS ARQUIVOS)
# -----------------------------
NAV = [
    # key, label, page_path, flaticon_class, accent
    ("home", "Home", "streamlit_app.py", "fi fi-br-house-chimney", "#111827"),
    ("alunos", "Alunos", "pages/0_Alunos.py", "fi fi-br-users", "#2563EB"),
    ("pei", "PEI", "pages/1_PEI.py", "fi fi-br-brain", "#7C3AED"),
    ("pae", "PAE", "pages/2_PAE.py", "fi fi-br-bullseye", "#F97316"),
    ("hub", "Hub", "pages/3_Hub_Inclusao.py", "fi fi-br-book-open-cover", "#16A34A"),
    ("diario", "Diário", "pages/4_Diario_de_Bordo.py", "fi fi-br-notebook", "#0EA5E9"),
    ("dados", "Dados", "pages/5_Monitoramento_Avaliacao.py", "fi fi-br-chart-histogram", "#111827"),
]


def _safe_get_go() -> str | None:
    try:
        qp = st.query_params
        if "go" in qp:
            return str(qp["go"]).strip()
    except Exception:
        pass
    return None


def _route_from_query():
    """
    Router simples: ?go=pei → st.switch_page(pages/1_PEI.py)
    Mantém session_state (comportamento multipage do Streamlit).
    """
    go = _safe_get_go()
    if not go:
        return

    go = go.lower()
    for key, _, page_path, _, _ in NAV:
        if key == go:
            # evita loop: limpa query param antes de trocar
            try:
                st.query_params.pop("go", None)
            except Exception:
                pass
            st.switch_page(page_path)
            return


# -----------------------------
# CSS (CLEAN TOPBAR + FLATICON)
# -----------------------------
def _inject_css():
    logo = _img_data_uri("assets/omni_icone.png") or _img_data_uri("omni_icone.png")
    word = _img_data_uri("assets/omni_texto.png") or _img_data_uri("omni_texto.png")

    st.markdown(
        f"""
<style>
/* Esconde chrome nativo */
[data-testid="stSidebar"],
[data-testid="stHeader"],
header, footer,
#MainMenu {{
  display: none !important;
}}

/* espaço p/ topbar fixa (altura real da barra + respiro) */
.main .block-container {{
  padding-top: 78px !important;
  max-width: 1200px;
}}

/* Consistência de box model */
* {{ box-sizing: border-box; }}

/* Flaticon UIcons CDN v3.0.0 */
@import url("https://cdn-uicons.flaticon.com/3.0.0/uicons-bold-rounded/css/uicons-bold-rounded.css");
@import url("https://cdn-uicons.flaticon.com/3.0.0/uicons-solid-rounded/css/uicons-solid-rounded.css");
@import url("https://cdn-uicons.flaticon.com/3.0.0/uicons-solid-straight/css/uicons-solid-straight.css");
@import url("https://cdn-uicons.flaticon.com/3.0.0/uicons-bold-straight/css/uicons-bold-straight.css");

/* TOPBAR (full-width) */
.omni-topbar {{
  position: fixed;
  top: 0; left: 0; right: 0;
  height: 60px;
  z-index: 9999;

  background: rgba(255,255,255,0.88);
  backdrop-filter: blur(14px);
  border-bottom: 1px solid rgba(0,0,0,0.08);
}}

/* CONTEÚDO da barra (alinhado ao container do app) */
.omni-topbar-inner {{
  height: 60px;
  max-width: 1200px;
  margin: 0 auto;

  display: flex;
  align-items: center;
  justify-content: space-between;

  padding: 0 14px;
}}

/* Brand */
.omni-brand {{
  display:flex;
  align-items:center;
  gap: 10px;
  min-width: 220px;
}}
.omni-logo {{
  width: 28px; height: 28px;
  object-fit: contain;
}}
.omni-word {{
  height: 16px;
  opacity: .92;
}}

/* Nav icons */
.omni-nav {{
  display:flex;
  align-items:center;
  gap: 10px;
}}

.omni-ico {{
  width: 38px;
  height: 38px;
  border-radius: 14px;

  display:flex;
  align-items:center;
  justify-content:center;

  background: rgba(0,0,0,0.03);
  border: 1px solid rgba(0,0,0,0.08);

  transition: transform .12s ease, box-shadow .12s ease, background .12s ease;
  text-decoration: none !important;
}}
.omni-ico:hover {{
  transform: translateY(-1px);
  background: rgba(0,0,0,0.05);
  box-shadow: 0 14px 34px rgba(0,0,0,0.10);
}}

.omni-ico i {{
  font-size: 18px;
  line-height: 1;
  display:block;
}}

/* remove underline/link default */
.omni-ico:visited, .omni-ico:active {{
  text-decoration: none !important;
}}
</style>

<div class="omni-topbar">
  <div class="omni-topbar-inner">
    <div class="omni-brand">
      {"<img class='omni-logo' src='"+logo+"'/>" if logo else "🌿"}
      {"<img class='omni-word' src='"+word+"'/>" if word else "<b>Omnisfera</b>"}
    </div>

    <div class="omni-nav">
      { _nav_html() }
    </div>
  </div>
</div>
        """,
        unsafe_allow_html=True,
    )


def _nav_html() -> str:
    """
    Gera os <a href="?go=..."> com ícones coloridos.
    """
    parts = []
    for key, label, _, ico, accent in NAV:
        parts.append(
            f"""
<a class="omni-ico" href="?go={key}" title="{label}" aria-label="{label}">
  <i class="{ico}" style="color:{accent}"></i>
</a>
"""
        )
    return "\n".join(parts)


def nav_href(key: str) -> str:
    """
    Use isso na HOME para links dentro dos cards:
      st.markdown(f'<a href="{nav_href("alunos")}">Abrir</a>', unsafe_allow_html=True)
    """
    return f"?go={key}"
