# ui_nav.py
import streamlit as st
import os, base64

# =========================
# MAPA DE PÁGINAS (ajuste se mudar nomes)
# =========================
PAGES = {
    "home":       "home_portal.py",          # sua home fora de /pages
    "alunos":     "pages/0_Alunos.py",
    "pei":        "pages/1_PEI.py",
    "paee":       "pages/2_PAE.py",
    "hub":        "pages/3_Hub_Inclusao.py",
    "diario":     "pages/4_Diario_de_Bordo.py",        # se existir
    "dados":      "pages/5_Monitoramento_Avaliacao.py" # se existir
}

# Cores por módulo (discretas)
COLORS = {
    "home":   "#111827",
    "alunos": "#2563EB",
    "pei":    "#3B82F6",
    "paee":   "#10B981",
    "hub":    "#F59E0B",
    "diario": "#F97316",
    "dados":  "#8B5CF6",
}

# =========================
# ICONES (Flaticon UIcons v3.0.0)
# Padrão que você definiu:
# Home/Diário/Dados/IA = bold-rounded (fi-br-*)
# PEI/Hub = solid-rounded (fi-sr-*)
# PAEE = solid-straight (fi-ss-*)
# =========================
FLATICON_CSS = """
<link rel='stylesheet' href='https://cdn-uicons.flaticon.com/3.0.0/uicons-bold-rounded/css/uicons-bold-rounded.css'>
<link rel='stylesheet' href='https://cdn-uicons.flaticon.com/3.0.0/uicons-solid-rounded/css/uicons-solid-rounded.css'>
<link rel='stylesheet' href='https://cdn-uicons.flaticon.com/3.0.0/uicons-solid-straight/css/uicons-solid-straight.css'>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@500;700;800;900&display=swap" rel="stylesheet">
"""

ICONS = {
    "home":   "fi fi-br-home",
    "alunos": "fi fi-br-users",                 # bold-rounded
    "pei":    "fi fi-sr-puzzle-alt",            # solid-rounded
    "paee":   "fi fi-ss-route",                 # solid-straight (alternativa: fi-ss-rocket-lunch)
    "hub":    "fi fi-sr-lightbulb-on",          # solid-rounded
    "diario": "fi fi-br-book-alt",              # bold-rounded
    "dados":  "fi fi-br-chart-histogram",       # bold-rounded
    "sair":   "fi fi-br-sign-out-alt",          # bold-rounded
}

def _b64(path: str) -> str:
    if not os.path.exists(path):
        return ""
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

def _get_query_param(name: str):
    try:
        qp = st.query_params
        v = qp.get(name)
        if isinstance(v, list):
            return v[0] if v else None
        return v
    except Exception:
        return None

def _clear_query_params():
    try:
        st.query_params.clear()
    except Exception:
        pass

def _nav_if_requested():
    """
    Se a URL vier com ?go=paee, troca de página e limpa params
    """
    go = _get_query_param("go")
    if go:
        target = PAGES.get(go)
        _clear_query_params()
        if target:
            st.switch_page(target)

def render_topbar_nav(active: str, show_logout: bool = True):
    """
    Topbar fina, discreta, full-width.
    Navegação por links (?go=...) + switch_page.
    """

    # 1) Se chegou com ?go=..., navega e sai
    _nav_if_requested()

    # 2) Esconde sidebar/toolbar e cria espaço pro topo
    st.markdown(f"""
{FLATICON_CSS}
<style>
/* limpa UI padrão */
header[data-testid="stHeader"]{{display:none !important;}}
[data-testid="stSidebar"]{{display:none !important;}}
[data-testid="stSidebarNav"]{{display:none !important;}}
[data-testid="stToolbar"]{{display:none !important;}}

/* espaço pro conteúdo não ficar embaixo da barra */
.block-container{{
  padding-top: 88px !important;
  padding-left: 2rem !important;
  padding-right: 2rem !important;
}}

/* topbar */
@keyframes spin{{from{{transform:rotate(0deg);}}to{{transform:rotate(360deg);}}}}

.omni-topbar{{
  position: fixed;
  top:0; left:0; right:0;
  height: 62px;
  z-index: 2147483647;
  display:flex;
  align-items:center;
  justify-content:space-between;
  padding: 0 22px;
  background: rgba(247,250,252,0.86);
  backdrop-filter: blur(14px);
  -webkit-backdrop-filter: blur(14px);
  border-bottom: 1px solid rgba(226,232,240,0.85);
  box-shadow: 0 8px 20px rgba(15,23,42,0.06);
  font-family: Inter, system-ui, -apple-system, Segoe UI, Roboto, Arial;
}}

.omni-left{{
  display:flex; align-items:center; gap: 12px;
  min-width: 320px;
}}

.omni-mark{{
  width: 32px; height: 32px; border-radius: 999px;
  animation: spin 45s linear infinite;
  filter: drop-shadow(0 2px 4px rgba(0,0,0,0.10));
}}

.omni-title{{
  font-weight: 900;
  letter-spacing: .12em;
  text-transform: uppercase;
  font-size: .82rem;
  color: #0F172A;
}}

.omni-right{{
  display:flex; align-items:flex-end; gap: 18px;
}}

.omni-link{{
  text-decoration: none;
  display:flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  opacity: .72;
  transform: translateY(0);
  transition: opacity .16s ease, transform .16s ease;
}}

.omni-link:hover{{
  opacity: 1;
  transform: translateY(-1px);
}}

.omni-ic{{
  font-size: 20px;
  line-height: 1;
}}

.omni-label{{
  font-size: 10px;
  font-weight: 800;
  letter-spacing: .12em;
  text-transform: uppercase;
  color: rgba(15,23,42,0.52);
}}

.omni-link.active{{
  opacity: 1;
}}

.omni-link.active .omni-label{{
  color: rgba(15,23,42,0.82);
}}

.omni-dot{{
  width: 20px;
  height: 2px;
  border-radius: 999px;
  margin-top: 2px;
  background: rgba(15,23,42,0.18);
}}

.omni-divider{{
  width:1px; height: 22px;
  background: rgba(226,232,240,1);
  margin: 0 4px;
}}

@media (max-width: 980px){{
  .omni-label{{display:none;}}
  .omni-left{{min-width: 200px;}}
}}
</style>
""", unsafe_allow_html=True)

    # 3) Logo (arquivo omni_icone.png)
    logo_b64 = _b64("omni_icone.png")
    if logo_b64:
        logo_html = f"<img class='omni-mark' src='data:image/png;base64,{logo_b64}'/>"
    else:
        logo_html = "<div class='omni-mark' style='background:conic-gradient(from 0deg,#3B82F6,#22C55E,#F59E0B,#F97316,#A855F7,#3B82F6);'></div>"

    # 4) Monta itens
    items = [
        ("home",   "Home"),
        ("alunos", "Alunos"),
        ("pei",    "Estratégias & PEI"),
        ("paee",   "Plano de Ação"),
        ("hub",    "Hub"),
        ("diario", "Diário"),
        ("dados",  "Dados"),
    ]

    links_html = ""
    for key, label in items:
        # se a página não existir no seu projeto, pula
        if key not in PAGES:
            continue
        is_active = "active" if key == active else ""
        color = COLORS.get(key, "#111827")
        icon = ICONS.get(key, "fi fi-br-circle")
        dot = "<div class='omni-dot'></div>" if key == active else "<div style='height:2px;'></div>"

        links_html += f"""
<a class="omni-link {is_active}" href="?go={key}" target="_self" aria-label="{label}">
  <i class="{icon} omni-ic" style="color:{color};"></i>
  <div class="omni-label">{label}</div>
  {dot}
</a>
"""

    # 5) Logout (opcional)
    logout_html = ""
    if show_logout:
        logout_html = f"""
<div class="omni-divider"></div>
<a class="omni-link" href="?go=home" target="_self" aria-label="Sair">
  <i class="{ICONS['sair']} omni-ic" style="color:rgba(15,23,42,0.55);"></i>
  <div class="omni-label">Sair</div>
  <div style="height:2px;"></div>
</a>
"""

    st.markdown(f"""
<div class="omni-topbar">
  <div class="omni-left">
    {logo_html}
    <div class="omni-title">OMNISFERA</div>
  </div>
  <div class="omni-right">
    {links_html}
    {logout_html}
  </div>
</div>
""", unsafe_allow_html=True)
