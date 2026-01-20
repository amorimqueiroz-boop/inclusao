# ui_nav.py
import streamlit as st
import os, base64

def render_omnisfera_nav():
    ROUTES = {
        "home":   "Home.py",
        "pei":    "pages/1_PEI.py",
        "paee":   "pages/2_PAE.py",
        "hub":    "pages/3_Hub_Inclusao.py",
        "diario": "pages/4_Diario_de_Bordo.py",
        "mon":    "pages/5_Monitoramento_Avaliacao.py",
    }

    # --- Navegação (?go=) ---
    qp = st.query_params
    if "go" in qp:
        dest = qp["go"]
        if dest in ROUTES:
            st.query_params.clear()
            st.switch_page(ROUTES[dest])

    # --- Descobrir página atual (pelo path) ---
    # Em multipage, o Streamlit costuma expor o script atual.
    # Esse método é estável o suficiente para o "active".
    try:
        from streamlit.runtime.scriptrunner import get_script_run_ctx
        ctx = get_script_run_ctx()
        current_script = (ctx.script_path or "").replace("\\", "/") if ctx else ""
    except Exception:
        current_script = ""

    def active_key():
        s = current_script.lower()
        if s.endswith("/home.py") or s.endswith("home.py"):
            return "home"
        if s.endswith("/pages/1_pei.py") or s.endswith("1_pei.py"):
            return "pei"
        if s.endswith("/pages/2_pae.py") or s.endswith("2_pae.py"):
            return "paee"
        if s.endswith("/pages/3_hub_inclusao.py") or s.endswith("3_hub_inclusao.py"):
            return "hub"
        if s.endswith("/pages/4_diario_de_bordo.py") or s.endswith("4_diario_de_bordo.py"):
            return "diario"
        if s.endswith("/pages/5_monitoramento_avaliacao.py") or s.endswith("5_monitoramento_avaliacao.py"):
            return "mon"
        return "home"

    ACTIVE = active_key()

    # --- Logo base64 ---
    def logo_src():
        for f in ["omni_icone.png", "logo.png", "iconeaba.png", "omni.png", "ominisfera.png"]:
            if os.path.exists(f):
                with open(f, "rb") as img:
                    return f"data:image/png;base64,{base64.b64encode(img.read()).decode()}"
        return "https://cdn-icons-png.flaticon.com/512/1183/1183672.png"

    src = logo_src()

    TOP_PX = 8
    RIGHT_PX = 14

    # Cores por página
    COLORS = {
        "home":   "#111827",
        "pei":    "#3B82F6",
        "paee":   "#22C55E",
        "hub":    "#F59E0B",
        "diario": "#F97316",
        "mon":    "#A855F7",
    }

    def btn_style(key: str) -> str:
        # Neutro: cinza bem leve + ícone escuro
        # Ativo: fundo colorido + ícone branco + ring sutil
        if key == ACTIVE:
            return f"background:{COLORS[key]}; color:#FFFFFF; box-shadow: 0 0 0 3px rgba(255,255,255,0.9), 0 10px 22px rgba(15,23,42,0.12);"
        else:
            return "background:#F3F4F6; color:#111827; box-shadow: 0 2px 10px rgba(15,23,42,0.06);"

    st.markdown(f"""
<link href="https://cdn.jsdelivr.net/npm/remixicon@4.1.0/fonts/remixicon.css" rel="stylesheet">

<style>
/* Header do Streamlit mutado para não competir */
header[data-testid="stHeader"] {{
  background: transparent !important;
  box-shadow: none !important;
  z-index: 1 !important;
}}
header[data-testid="stHeader"] * {{
  visibility: hidden !important;
}}

/* Dock (fino) */
.omni-dock {{
  position: fixed !important;
  top: {TOP_PX}px !important;
  right: {RIGHT_PX}px !important;
  z-index: 2147483647 !important;

  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 12px;
  border-radius: 999px;

  background: #FFFFFF !important;
  border: 1px solid #E5E7EB !important;
  box-shadow: 0 10px 28px rgba(15, 23, 42, 0.12) !important;

  opacity: 1 !important;
  isolation: isolate !important;
  pointer-events: auto !important;
}}

/* Logo um pouco maior pra equilibrar */
@keyframes spin {{ from {{ transform: rotate(0deg); }} to {{ transform: rotate(360deg); }} }}
.omni-logo {{
  width: 28px;   /* ↑ voltou um pouco */
  height: 28px;
  animation: spin 10s linear infinite;
}}

.omni-sep {{
  width: 1px;
  height: 22px;
  background: #E5E7EB;
  margin: 0 2px;
}}

/* Botões */
.omni-ico {{
  width: 34px;
  height: 34px;
  border-radius: 999px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  text-decoration: none !important;
  border: 1px solid rgba(17,24,39,0.06) !important;
  transition: transform .12s ease, filter .12s ease, box-shadow .12s ease;
}}

.omni-ico:hover {{
  transform: translateY(-1px);
  filter: brightness(1.02);
}}

.omni-ic {{
  font-size: 18px;
  line-height: 1;
  color: inherit; /* cor vem do style inline */
}}
</style>

<div class="omni-dock" aria-label="Omnisfera Dock">
  <img src="{src}" class="omni-logo" alt="Omnisfera" />
  <div class="omni-sep"></div>

  <a class="omni-ico" href="?go=home"   target="_self" title="Home"
     style="{btn_style('home')}">
    <i class="ri-home-5-line omni-ic"></i>
  </a>

  <a class="omni-ico" href="?go=pei"    target="_self" title="Estratégias & PEI"
     style="{btn_style('pei')}">
    <i class="ri-puzzle-2-line omni-ic"></i>
  </a>

  <a class="omni-ico" href="?go=paee"   target="_self" title="Plano de Ação (PAEE)"
     style="{btn_style('paee')}">
    <i class="ri-map-pin-2-line omni-ic"></i>
  </a>

  <a class="omni-ico" href="?go=hub"    target="_self" title="Hub de Recursos"
     style="{btn_style('hub')}">
    <i class="ri-lightbulb-line omni-ic"></i>
  </a>

  <a class="omni-ico" href="?go=diario" target="_self" title="Diário de Bordo"
     style="{btn_style('diario')}">
    <i class="ri-compass-3-line omni-ic"></i>
  </a>

  <a class="omni-ico" href="?go=mon"    target="_self" title="Evolução & Acompanhamento"
     style="{btn_style('mon')}">
    <i class="ri-line-chart-line omni-ic"></i>
  </a>
</div>
""", unsafe_allow_html=True)
