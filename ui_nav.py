# ui_nav.py
import streamlit as st
import os, base64

# =========================================================
# MAPA DE PÁGINAS (multipage real)
# =========================================================
PAGES = {
    "home":   "home_portal.py",
    "pei":    "pages/1_PEI.py",
    "paee":   "pages/2_PAE.py",
    "hub":    "pages/3_Hub_Inclusao.py",
    # opcionais (só aparecem se o arquivo existir)
    "diario": "pages/4_Diario_de_Bordo.py",
    "mon":    "pages/5_Monitoramento_Avaliacao.py",
}

# =========================================================
# CORES
# =========================================================
COLORS = {
    "home":   "#111827",
    "pei":    "#3B82F6",
    "paee":   "#22C55E",
    "hub":    "#F59E0B",
    "diario": "#F97316",
    "mon":    "#A855F7",
}

# =========================================================
# POSIÇÃO (igual ontem)
# =========================================================
TOP_PX = 8
RIGHT_PX = 14

def _b64_logo() -> str:
    for f in ["omni_icone.png", "logo.png", "iconeaba.png", "omni.png", "ominisfera.png"]:
        if os.path.exists(f):
            with open(f, "rb") as img:
                return f"data:image/png;base64,{base64.b64encode(img.read()).decode()}"
    return "https://cdn-icons-png.flaticon.com/512/1183/1183672.png"

def _exists(path: str) -> bool:
    try:
        return bool(path) and os.path.exists(path)
    except Exception:
        return False

def _goto(key: str):
    target = PAGES.get(key)
    if not target:
        return
    # se for página opcional e ainda não existe, não quebra
    if key in ("diario", "mon") and not _exists(target):
        st.toast("Página ainda não está nessa versão.", icon="⚠️")
        return
    st.switch_page(target)

def _style_for(active: str, key: str) -> str:
    solid = COLORS.get(key, "#111827")
    if key == active:
        return f"background:{solid}; color:#FFFFFF; box-shadow: 0 0 0 3px rgba(255,255,255,0.95), 0 10px 22px rgba(15,23,42,0.12); filter:none;"
    return f"background:{solid}; color:rgba(255,255,255,0.78); box-shadow: 0 2px 10px rgba(15,23,42,0.06); filter:saturate(0.65) brightness(1.12); opacity:0.72;"

def render_omnisfera_nav(active: str = "home"):
    """
    Dock igual ao de ontem (visual idêntico), mas com navegação multipage real:
    - Clique -> st.switch_page(...)
    - active vem da página: home/pei/paee/hub/diario/mon
    """

    src = _b64_logo()

    # -------------------------------
    # 1) VISUAL DO DOCK (HTML/CSS) — igual ontem
    # -------------------------------
    st.markdown(f"""
<link href="https://cdn.jsdelivr.net/npm/remixicon@4.1.0/fonts/remixicon.css" rel="stylesheet">

<style>
/* “Mute” no header do Streamlit para o dock dominar */
header[data-testid="stHeader"] {{
  background: transparent !important;
  box-shadow: none !important;
  z-index: 1 !important;
}}
header[data-testid="stHeader"] * {{
  visibility: hidden !important;
}}

/* DOCK (visual) */
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

  pointer-events: none !important; /* clique será nos botões do Streamlit */
  isolation: isolate !important;
}}

@keyframes spin {{
  from {{ transform: rotate(0deg); }}
  to {{ transform: rotate(360deg); }}
}}
.omni-logo {{
  width: 28px;
  height: 28px;
  animation: spin 10s linear infinite;
}}

.omni-sep {{
  width: 1px;
  height: 22px;
  background: #E5E7EB;
  margin: 0 2px;
}}

/* Bolinhas menores */
.omni-ico {{
  width: 30px;
  height: 30px;
  border-radius: 999px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border: 1px solid rgba(17,24,39,0.06);
  box-shadow: 0 2px 10px rgba(15, 23, 42, 0.06);
}}

.omni-ic {{
  font-size: 16px;
  line-height: 1;
  color: inherit;
}}
</style>

<div class="omni-dock" aria-label="Omnisfera Dock">
  <img src="{src}" class="omni-logo" alt="Omnisfera" />
  <div class="omni-sep"></div>

  <div class="omni-ico" style="{_style_for(active,'home')}"><i class="ri-home-5-line omni-ic"></i></div>
  <div class="omni-ico" style="{_style_for(active,'pei')}"><i class="ri-puzzle-2-line omni-ic"></i></div>
  <div class="omni-ico" style="{_style_for(active,'paee')}"><i class="ri-map-pin-2-line omni-ic"></i></div>
  <div class="omni-ico" style="{_style_for(active,'hub')}"><i class="ri-lightbulb-line omni-ic"></i></div>
  <div class="omni-ico" style="{_style_for(active,'diario')}"><i class="ri-compass-3-line omni-ic"></i></div>
  <div class="omni-ico" style="{_style_for(active,'mon')}"><i class="ri-line-chart-line omni-ic"></i></div>
</div>
""", unsafe_allow_html=True)

    # -------------------------------
    # 2) CAMADA CLICÁVEL REAL (Streamlit) — igual ontem
    # -------------------------------
    st.markdown('<div id="omni-click-anchor"></div>', unsafe_allow_html=True)

    c_logo, c_sep, c1, c2, c3, c4, c5, c6 = st.columns(
        [0.6, 0.08, 0.7, 0.7, 0.7, 0.7, 0.7, 0.7],
        gap="small"
    )

    with c_logo:
        if st.button(" ", key="omni_nav_logo", help="Home"):
            _goto("home")
    with c_sep:
        st.write("")
    with c1:
        if st.button(" ", key="omni_nav_home", help="Home"):
            _goto("home")
    with c2:
        if st.button(" ", key="omni_nav_pei", help="Estratégias & PEI"):
            _goto("pei")
    with c3:
        if st.button(" ", key="omni_nav_paee", help="Plano de Ação (PAEE)"):
            _goto("paee")
    with c4:
        if st.button(" ", key="omni_nav_hub", help="Hub de Recursos"):
            _goto("hub")
    with c5:
        if st.button(" ", key="omni_nav_diario", help="Diário de Bordo"):
            _goto("diario")
    with c6:
        if st.button(" ", key="omni_nav_mon", help="Evolução & Acompanhamento"):
            _goto("mon")

    st.markdown(f"""
<style>
/* fixa o bloco de colunas imediatamente após a âncora */
#omni-click-anchor + div {{
  position: fixed !important;
  top: {TOP_PX}px !important;
  right: {RIGHT_PX}px !important;
  z-index: 2147483647 !important;

  display: flex !important;
  align-items: center !important;

  gap: 10px !important;
  padding: 8px 12px !important;
  border-radius: 999px !important;

  background: transparent !important;
  border: none !important;
  box-shadow: none !important;
}}

/* botões = área de clique do tamanho das bolinhas */
#omni-click-anchor + div [data-testid="stButton"] button {{
  width: 30px !important;
  height: 30px !important;
  border-radius: 999px !important;
  padding: 0 !important;
  background: transparent !important;
  border: none !important;
  box-shadow: none !important;
}}
#omni-click-anchor + div [data-testid="stButton"] button p {{
  display: none !important;
}}

/* logo clicável */
#omni-click-anchor + div [data-testid="column"]:nth-child(1) [data-testid="stButton"] button {{
  width: 28px !important;
  height: 28px !important;
}}
/* separador (2ª coluna) só ocupa espaço */
#omni-click-anchor + div [data-testid="column"]:nth-child(2) {{
  width: 1px !important;
}}
</style>
""", unsafe_allow_html=True)
