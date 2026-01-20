# ui_nav.py
import streamlit as st
import os, base64

def render_omnisfera_nav():
    # -------------------------------
    # 1) Estado SPA
    # -------------------------------
    if "view" not in st.session_state:
        st.session_state.view = "home"

    def go(view_key: str):
        st.session_state.view = view_key
        st.rerun()

    ACTIVE = st.session_state.view

    # -------------------------------
    # 2) Logo base64
    # -------------------------------
    def logo_src():
        for f in ["omni_icone.png", "logo.png", "iconeaba.png", "omni.png", "ominisfera.png"]:
            if os.path.exists(f):
                with open(f, "rb") as img:
                    return f"data:image/png;base64,{base64.b64encode(img.read()).decode()}"
        return "https://cdn-icons-png.flaticon.com/512/1183/1183672.png"

    src = logo_src()

    # -------------------------------
    # 3) Config visual
    # -------------------------------
    TOP_PX = 8
    RIGHT_PX = 14

    COLORS = {
        "home": "#111827",
        "pei": "#3B82F6",
        "paee": "#22C55E",
        "hub": "#F59E0B",
        "diario": "#F97316",
        "mon": "#A855F7",
    }

    def style_for(key: str):
        """
        - Inativo: cor opaca (RGBA) + ícone branco com alpha
        - Ativo: cor sólida + ring/glow
        """
        solid = COLORS[key]
        # versão opaca: usamos alpha via CSS rgba aproximado com overlay (filter)
        if key == ACTIVE:
            return f"background:{solid}; color:#FFFFFF; box-shadow: 0 0 0 3px rgba(255,255,255,0.95), 0 10px 22px rgba(15,23,42,0.12); filter:none;"
        else:
            return f"background:{solid}; color:rgba(255,255,255,0.78); box-shadow: 0 2px 10px rgba(15,23,42,0.06); filter:saturate(0.65) brightness(1.12); opacity:0.72;"

    # -------------------------------
    # 4) CSS + dock (visual)
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
  width: 30px;   /* ↓ menor */
  height: 30px;  /* ↓ menor */
  border-radius: 999px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border: 1px solid rgba(17,24,39,0.06);
  box-shadow: 0 2px 10px rgba(15, 23, 42, 0.06);
}}

.omni-ic {{
  font-size: 16px; /* ↓ menor */
  line-height: 1;
  color: inherit;
}}
</style>

<div class="omni-dock" aria-label="Omnisfera Dock">
  <img src="{src}" class="omni-logo" alt="Omnisfera" />
  <div class="omni-sep"></div>

  <div class="omni-ico" style="{style_for('home')}"><i class="ri-home-5-line omni-ic"></i></div>
  <div class="omni-ico" style="{style_for('pei')}"><i class="ri-puzzle-2-line omni-ic"></i></div>
  <div class="omni-ico" style="{style_for('paee')}"><i class="ri-map-pin-2-line omni-ic"></i></div>
  <div class="omni-ico" style="{style_for('hub')}"><i class="ri-lightbulb-line omni-ic"></i></div>
  <div class="omni-ico" style="{style_for('diario')}"><i class="ri-compass-3-line omni-ic"></i></div>
  <div class="omni-ico" style="{style_for('mon')}"><i class="ri-line-chart-line omni-ic"></i></div>
</div>
""", unsafe_allow_html=True)

    # -------------------------------
    # 5) Camada clicável REAL (Streamlit) — agora fixada corretamente
    #    Estratégia: renderiza os botões e depois “sequestra” o bloco via CSS pelo id.
    # -------------------------------
    # cria um wrapper “âncora” que conseguimos selecionar com CSS
    st.markdown('<div id="omni-click-anchor"></div>', unsafe_allow_html=True)

    # Renderiza botões (no fluxo normal), mas vamos fixar com CSS mirando no bloco logo após a âncora.
    c_logo, c_sep, c1, c2, c3, c4, c5, c6 = st.columns(
        [0.6, 0.08, 0.7, 0.7, 0.7, 0.7, 0.7, 0.7],
        gap="small"
    )

    with c_logo:
        if st.button(" ", key="omni_nav_logo", help="Home"):
            go("home")
    with c_sep:
        st.write("")  # só ocupa espaço
    with c1:
        if st.button(" ", key="omni_nav_home", help="Home"):
            go("home")
    with c2:
        if st.button(" ", key="omni_nav_pei", help="Estratégias & PEI"):
            go("pei")
    with c3:
        if st.button(" ", key="omni_nav_paee", help="Plano de Ação (PAEE)"):
            go("paee")
    with c4:
        if st.button(" ", key="omni_nav_hub", help="Hub de Recursos"):
            go("hub")
    with c5:
        if st.button(" ", key="omni_nav_diario", help="Diário de Bordo"):
            go("diario")
    with c6:
        if st.button(" ", key="omni_nav_mon", help="Evolução & Acompanhamento"):
            go("mon")

    # CSS pós-render: fixa o “bloco” de botões imediatamente após a âncora
    st.markdown(f"""
<style>
/* Pega o bloco de colunas que vem logo depois da âncora e fixa no topo direito */
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

  /* invisível (o visual está no HTML do dock) */
  background: transparent !important;
  border: none !important;
  box-shadow: none !important;
}}

/* Botões viram áreas de clique do tamanho exato das bolinhas */
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

/* Logo: área clicável do tamanho da logo */
#omni-click-anchor + div [data-testid="column"]:nth-child(1) [data-testid="stButton"] button {{
  width: 28px !important;
  height: 28px !important;
}}
/* Coluna do separador (2ª): só ocupa espaço */
#omni-click-anchor + div [data-testid="column"]:nth-child(2) {{
  width: 1px !important;
}}
</style>
""", unsafe_allow_html=True)
