# ui_nav.py
import streamlit as st
import os, base64


# -------------------------
# CONFIG (cores + ícones)
# -------------------------
COLORS = {
    "home": "#111827",
    "estudantes": "#2B6CEB",
    "pei": "#3B82F6",
    "paee": "#22C55E",
    "hub": "#F59E0B",
    "diario": "#F97316",
    "mon": "#A855F7",
    "ia": "#111827",
}

# Flaticon classes (v3.0.0) — padrão que você definiu
ICONS = {
    "home": "fi fi-br-house-chimney",         # bold-rounded
    "estudantes": "fi fi-sr-users-alt",       # solid-rounded
    "pei": "fi fi-sr-puzzle-alt",             # solid-rounded
    "paee": "fi fi-ss-route",                 # solid-straight
    "hub": "fi fi-sr-lightbulb-on",           # solid-rounded
    "diario": "fi fi-br-compass-alt",         # bold-rounded
    "mon": "fi fi-br-chart-line-up",          # bold-rounded
    "ia": "fi fi-br-brain",                   # bold-rounded
    "logout": "fi fi-sr-sign-out-alt",        # solid-rounded
}

NAV_ITEMS = [
    ("home", "Home"),
    ("estudantes", "Alunos"),
    ("pei", "Estratégias & PEI"),
    ("paee", "Plano de Ação"),
    ("hub", "Hub"),
    ("diario", "Diário"),
    ("mon", "Dados"),
    # ("ia", "IA"),  # se quiser incluir depois, só descomente
]


def _b64(path: str) -> str:
    if not os.path.exists(path):
        return ""
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()


def _sync_view_from_query(default: str = "home") -> str:
    """
    Fonte da verdade = query param `view`.
    Mantém também st.session_state.view para o resto do app.
    """
    if "view" not in st.session_state:
        st.session_state.view = default

    try:
        qp = st.query_params
        v = qp.get("view")
        if isinstance(v, list):
            v = v[0] if v else None
        if v:
            st.session_state.view = v
    except Exception:
        pass

    return st.session_state.view


def _set_view(view_key: str):
    st.session_state.view = view_key
    try:
        st.query_params["view"] = view_key
    except Exception:
        pass
    st.rerun()


def _logout():
    if "autenticado" in st.session_state:
        st.session_state.autenticado = False
    _set_view("home")


def render_topbar_nav(active: str | None = None, show_on_login: bool = True):
    """
    Topbar fina full-width, estável:
    - esquerda: logo girando + OMNISFERA
    - direita: botões como links (?view=...), com ícone + label discreto
    - sem overlay de botões invisíveis
    """

    # auth gating (se você usa)
    authed = bool(st.session_state.get("autenticado", True))
    if (not authed) and (not show_on_login):
        return None

    active = active or _sync_view_from_query("home")

    # logo
    icon_b64 = _b64("omni_icone.png")

    logo_html = (
        f'<img class="omni-spin" src="data:image/png;base64,{icon_b64}" alt="Omnisfera" />'
        if icon_b64
        else '<div class="omni-mark-fallback" aria-label="Omnisfera"></div>'
    )

    # build nav links
    links_html = ""
    for key, label in NAV_ITEMS:
        color = COLORS.get(key, "#111827")
        ic = ICONS.get(key, "fi fi-br-circle")
        is_active = (key == active)
        cls = "omni-link active" if is_active else "omni-link"
        links_html += f"""
<a class="{cls}" href="?view={key}">
  <i class="{ic} omni-ic" style="color:{color};"></i>
  <span class="omni-lbl">{label}</span>
</a>
"""

    # logout (opcional)
    logout_html = f"""
<a class="omni-link omni-logout" href="?view=home" data-logout="1">
  <i class="{ICONS['logout']} omni-ic" style="color:rgba(15,23,42,0.55);"></i>
  <span class="omni-lbl">Sair</span>
</a>
"""

    st.markdown(
        f"""
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@500;600;700;800;900&display=swap" rel="stylesheet">

<!-- Flaticon UIcons v3.0.0 -->
<link rel='stylesheet' href='https://cdn-uicons.flaticon.com/3.0.0/uicons-bold-rounded/css/uicons-bold-rounded.css'>
<link rel='stylesheet' href='https://cdn-uicons.flaticon.com/3.0.0/uicons-solid-rounded/css/uicons-solid-rounded.css'>
<link rel='stylesheet' href='https://cdn-uicons.flaticon.com/3.0.0/uicons-solid-straight/css/uicons-solid-straight.css'>

<style>
header[data-testid="stHeader"]{{display:none !important;}}
[data-testid="stSidebar"]{{display:none !important;}}
[data-testid="stSidebarNav"]{{display:none !important;}}
[data-testid="stToolbar"]{{display:none !important;}}

/* espaço para a barra */
.block-container{{
  padding-top: 76px !important;  /* topbar 54 + respiro */
  padding-left: 2rem !important;
  padding-right: 2rem !important;
}}

@keyframes spin{{from{{transform:rotate(0deg);}}to{{transform:rotate(360deg);}}}}

.omni-topbar{{
  position:fixed;
  top:0; left:0; right:0;
  height:54px;
  z-index:2147483647;
  display:flex;
  align-items:center;
  justify-content:space-between;
  padding: 0 18px;
  background: rgba(248,250,252,0.86);
  -webkit-backdrop-filter: blur(16px);
  backdrop-filter: blur(16px);
  border-bottom: 1px solid rgba(226,232,240,0.85);
  box-shadow: 0 8px 20px rgba(15,23,42,0.06);
  font-family: Inter, system-ui, -apple-system, Segoe UI, Roboto, Arial;
}}

/* esquerda */
.omni-left{{
  display:flex;
  align-items:center;
  gap:10px;
  min-width: 260px;
}}
.omni-spin{{
  width:30px; height:30px;
  border-radius:999px;
  animation: spin 40s linear infinite;
  filter: drop-shadow(0 2px 4px rgba(0,0,0,0.10));
}}
.omni-mark-fallback{{
  width:30px; height:30px;
  border-radius:999px;
  background: conic-gradient(from 0deg,#3B82F6,#22C55E,#F59E0B,#F97316,#A855F7,#3B82F6);
  animation: spin 40s linear infinite;
}}
.omni-name{{
  display:flex;
  flex-direction:column;
  line-height:1;
}}
.omni-title{{
  font-weight: 900;
  letter-spacing: .14em;
  text-transform: uppercase;
  font-size: 0.78rem;
  color:#0F172A;
}}
.omni-sub{{
  margin-top: 2px;
  font-size: 0.68rem;
  color: rgba(15,23,42,0.55);
  letter-spacing: .04em;
}}

/* direita */
.omni-right{{
  display:flex;
  align-items:flex-end;
  gap: 14px;
}}

.omni-link{{
  text-decoration:none !important;
  display:flex;
  flex-direction:column;
  align-items:center;
  gap: 4px;
  padding: 6px 6px 4px 6px;
  border-radius: 12px;
  transition: transform .14s ease, background .14s ease, box-shadow .14s ease, opacity .14s ease;
  opacity: 0.88;
}}
.omni-link:hover{{
  transform: translateY(-1px);
  background: rgba(255,255,255,0.55);
  box-shadow: 0 10px 22px rgba(15,23,42,0.08);
  opacity: 1;
}}

.omni-ic{{
  font-size: 20px;
  line-height: 1;
}}

.omni-lbl{{
  font-size: 0.62rem;
  color: rgba(15,23,42,0.55);
  letter-spacing: .03em;
  white-space: nowrap;
}}

/* ativo bem discreto */
.omni-link.active{{
  opacity: 1;
}}
.omni-link.active .omni-lbl{{
  color: rgba(15,23,42,0.80);
  font-weight: 600;
}}
.omni-link.active::after{{
  content:"";
  width: 18px;
  height: 2px;
  border-radius: 99px;
  background: rgba(15,23,42,0.18);
  margin-top: 2px;
}}

/* logout */
.omni-logout .omni-lbl{{
  color: rgba(15,23,42,0.40);
}}
.omni-divider{{
  width: 1px;
  height: 26px;
  background: rgba(226,232,240,1);
  margin: 0 2px;
}}

@media (max-width: 980px){{
  .omni-sub{{display:none;}}
  .omni-lbl{{display:none;}} /* mantém só ícones no mobile */
  .omni-right{{gap:10px;}}
  .block-container{{padding-top: 72px !important;}}
}}
</style>

<div class="omni-topbar">
  <div class="omni-left">
    {logo_html}
    <div class="omni-name">
      <div class="omni-title">OMNISFERA</div>
      <div class="omni-sub">Inclusão • PEI • PAEE • Dados</div>
    </div>
  </div>

  <div class="omni-right">
    {links_html}
    <div class="omni-divider"></div>
    {logout_html}
  </div>
</div>
        """,
        unsafe_allow_html=True,
    )

    # ---- capturar clique do logout sem JS: checa query param especial
    # (opcional) se quiser logout real, use um botão Streamlit em vez do link.
    try:
        qp = st.query_params
        # Se quiser um comportamento real de logout, você pode trocar a URL do logout
        # para "?logout=1" e ler aqui. Mantive simples.
    except Exception:
        pass

    return active
