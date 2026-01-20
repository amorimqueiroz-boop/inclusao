# ui_nav.py
import streamlit as st
import os, base64

# =========================
# Config
# =========================
FLATICON_CSS = """
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@600;700;800;900&display=swap" rel="stylesheet">

<link rel='stylesheet' href='https://cdn-uicons.flaticon.com/3.0.0/uicons-bold-rounded/css/uicons-bold-rounded.css'>
<link rel='stylesheet' href='https://cdn-uicons.flaticon.com/3.0.0/uicons-solid-rounded/css/uicons-solid-rounded.css'>
<link rel='stylesheet' href='https://cdn-uicons.flaticon.com/3.0.0/uicons-solid-straight/css/uicons-solid-straight.css'>
"""

COLORS = {
    "home": "#0F172A",
    "alunos": "#2B6CEB",
    "pei": "#2F7DF6",
    "paee": "#22A765",
    "hub": "#D98A0A",
    "diario": "#E05A1C",
    "dados": "#8B5CF6",
    "logout": "#64748B",
}

ICONS = {
    "home": "fi fi-br-house-chimney",     # bold-rounded
    "alunos": "fi fi-sr-users-alt",       # solid-rounded
    "pei": "fi fi-sr-puzzle-alt",         # solid-rounded
    "paee": "fi fi-ss-route",             # solid-straight
    "hub": "fi fi-sr-lightbulb-on",       # solid-rounded
    "diario": "fi fi-br-compass-alt",     # bold-rounded
    "dados": "fi fi-br-chart-line-up",    # bold-rounded
    "logout": "fi fi-sr-sign-out-alt",    # solid-rounded
}

NAV = [
    ("home",   "Home",               "Home.py"),
    ("alunos", "Alunos",             "pages/0_Alunos.py"),
    ("pei",    "Estratégias & PEI",  "pages/1_PEI.py"),
    ("paee",   "Plano de Ação",      "pages/2_PAE.py"),
    ("hub",    "Hub",                "pages/3_Hub_Inclusao.py"),
    ("diario", "Diário",             "pages/4_Diario_de_Bordo.py"),
    ("dados",  "Dados",              "pages/5_Monitoramento_Avaliacao.py"),
]

def _b64(path: str) -> str:
    if not os.path.exists(path):
        return ""
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

def render_topbar_nav(active_key: str, height_px: int = 54):
    """
    Topbar fina full-width para usar nas páginas (PAEE/PEI/etc).
    - NÃO use na Home (você quer Home limpa).
    - active_key: 'paee', 'pei', 'alunos', etc.
    """
    # Logo
    logo_b64 = _b64("omni_icone.png")
    if logo_b64:
        logo_html = f'<img class="omni-spin" src="data:image/png;base64,{logo_b64}" alt="Omnisfera" />'
    else:
        logo_html = '<div class="omni-mark-fallback" aria-label="Omnisfera"></div>'

    # HTML visual dos itens
    items_html = ""
    for k, label, _path in NAV:
        ic = ICONS.get(k, "fi fi-br-circle")
        color = COLORS.get(k, "#0F172A")
        cls = "omni-item active" if k == active_key else "omni-item"
        items_html += f"""
<div class="{cls}">
  <i class="{ic} omni-ic" style="color:{color};"></i>
  <span class="omni-lbl">{label}</span>
</div>
"""

    st.markdown(
        f"""
{FLATICON_CSS}
<style>
header[data-testid="stHeader"]{{display:none !important;}}
/* Sidebar fica escondida, mas vamos usar page_link no corpo (não cria caixinhas) */
[data-testid="stSidebar"]{{display:none !important;}}
[data-testid="stSidebarNav"]{{display:none !important;}}
[data-testid="stToolbar"]{{display:none !important;}}

.block-container{{
  padding-top: {height_px + 22}px !important;
  padding-left: 2rem !important;
  padding-right: 2rem !important;
}}

@keyframes spin{{from{{transform:rotate(0deg);}}to{{transform:rotate(360deg);}}}}

.omni-topbar{{
  position:fixed; top:0; left:0; right:0;
  height:{height_px}px;
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

.omni-left{{display:flex; align-items:center; gap:10px; min-width: 260px;}}
.omni-spin{{width:30px; height:30px; border-radius:999px; animation: spin 40s linear infinite;
  filter: drop-shadow(0 2px 4px rgba(0,0,0,0.10));}}
.omni-mark-fallback{{width:30px; height:30px; border-radius:999px;
  background: conic-gradient(from 0deg,#3B82F6,#22C55E,#F59E0B,#F97316,#A855F7,#3B82F6);
  animation: spin 40s linear infinite;}}
.omni-brand{{display:flex; flex-direction:column; line-height:1;}}
.omni-title{{font-weight: 900; letter-spacing: .14em; text-transform: uppercase;
  font-size: 0.78rem; color:#0F172A;}}
.omni-sub{{margin-top:2px; font-size:0.68rem; color: rgba(15,23,42,0.55); letter-spacing:.04em;}}

.omni-right{{display:flex; align-items:flex-end; gap: 14px;}}
.omni-item{{
  display:flex; flex-direction:column; align-items:center;
  gap: 4px;
  padding: 6px 6px 4px 6px;
  border-radius: 12px;
  opacity: 0.86;
}}
.omni-ic{{font-size: 20px; line-height: 1;}}
.omni-lbl{{font-size: 0.62rem; color: rgba(15,23,42,0.55); letter-spacing: .03em; white-space: nowrap;}}
.omni-item.active{{opacity: 1;}}
.omni-item.active .omni-lbl{{color: rgba(15,23,42,0.82); font-weight: 800;}}
.omni-item.active::after{{
  content:"";
  width: 18px; height: 2px;
  border-radius: 99px;
  background: rgba(15,23,42,0.18);
  margin-top: 2px;
}}

@media (max-width: 980px){{
  .omni-sub{{display:none;}}
  .omni-lbl{{display:none;}}
  .omni-right{{gap:10px;}}
}}
</style>

<div class="omni-topbar">
  <div class="omni-left">
    {logo_html}
    <div class="omni-brand">
      <div class="omni-title">OMNISFERA</div>
      <div class="omni-sub">Inclusão • PEI • PAEE • Dados</div>
    </div>
  </div>
  <div class="omni-right">
    {items_html}
  </div>
</div>
        """,
        unsafe_allow_html=True,
    )

    # Clique real (sem caixas visíveis): usamos page_link (se existir)
    # Renderiza uma linha escondida com os links clicáveis.
    st.markdown("<div style='height:0;overflow:hidden;position:fixed;top:0;right:0;z-index:2147483647;'>", unsafe_allow_html=True)
    try:
        cols = st.columns([1]*len(NAV), gap="small")
        for i, (_k, label, path) in enumerate(NAV):
            with cols[i]:
                st.page_link(path, label=label, icon=None)  # clique real sem botão
    except Exception:
        # fallback: se sua versão não tiver page_link, avisa
        st.warning("Sua versão do Streamlit não suporta st.page_link(). Atualize para evitar botões visíveis.")
    st.markdown("</div>", unsafe_allow_html=True)
