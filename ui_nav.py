# ui_nav.py
import streamlit as st
import os, base64

def render_omnisfera_nav():
    """
    SPA-like navigation:
    - NÃO usa st.switch_page (isso troca de página e pode forçar login de novo)
    - Usa st.session_state["view"] + st.rerun() (igual sidebar)
    - Mantém o dock exatamente como está (HTML/CSS)
    - A camada de clique é feita com botões invisíveis por cima dos ícones
    """

    # -------------------------------
    # 1) Estado SPA (view atual)
    # -------------------------------
    if "view" not in st.session_state:
        st.session_state.view = "home"

    # função de navegação (igual sidebar)
    def go(view_key: str):
        st.session_state.view = view_key
        st.rerun()

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
    # 3) Visual do dock (igual o seu)
    # -------------------------------
    TOP_PX = 8
    RIGHT_PX = 14

    st.markdown(f"""
<link href="https://cdn.jsdelivr.net/npm/remixicon@4.1.0/fonts/remixicon.css" rel="stylesheet">

<style>
/* Header do Streamlit "mutado" para não competir com o dock */
header[data-testid="stHeader"] {{
  background: transparent !important;
  box-shadow: none !important;
  z-index: 1 !important;
}}
header[data-testid="stHeader"] * {{
  visibility: hidden !important;
}}

/* Dock (mais fino) */
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
  pointer-events: none !important; /* IMPORTANT: clique vai na camada de botões */
}}

/* Logo */
@keyframes spin {{
  from {{ transform: rotate(0deg); }}
  to {{ transform: rotate(360deg); }}
}}
.omni-logo {{
  width: 26px;
  height: 26px;
  animation: spin 10s linear infinite;
}}

/* Separador */
.omni-sep {{
  width: 1px;
  height: 22px;
  background: #E5E7EB;
  margin: 0 2px;
}}

/* Botões circulares coloridos (ícone branco) */
.omni-ico {{
  width: 34px;
  height: 34px;
  border-radius: 999px;
  display: inline-flex;
  align-items: center;
  justify-content: center;

  border: 1px solid rgba(17,24,39,0.06) !important;
  box-shadow: 0 2px 10px rgba(15, 23, 42, 0.06);
}}

.omni-ic {{
  font-size: 18px;
  line-height: 1;
  color: #FFFFFF !important;
}}
</style>

<div class="omni-dock" aria-label="Omnisfera Dock">
  <img src="{src}" class="omni-logo" alt="Omnisfera" />
  <div class="omni-sep"></div>

  <div class="omni-ico" style="background:#111827" title="Home">
    <i class="ri-home-5-line omni-ic"></i>
  </div>

  <div class="omni-ico" style="background:#3B82F6" title="Estratégias & PEI">
    <i class="ri-puzzle-2-line omni-ic"></i>
  </div>

  <div class="omni-ico" style="background:#22C55E" title="Plano de Ação (PAEE)">
    <i class="ri-map-pin-2-line omni-ic"></i>
  </div>

  <div class="omni-ico" style="background:#F59E0B" title="Hub de Recursos">
    <i class="ri-lightbulb-line omni-ic"></i>
  </div>

  <div class="omni-ico" style="background:#F97316" title="Diário de Bordo">
    <i class="ri-compass-3-line omni-ic"></i>
  </div>

  <div class="omni-ico" style="background:#A855F7" title="Evolução & Acompanhamento">
    <i class="ri-line-chart-line omni-ic"></i>
  </div>
</div>
""", unsafe_allow_html=True)

    # -------------------------------
    # 4) Camada clicável (SPA) por cima do dock
    #    - Botões invisíveis alinhados com a pílula
    #    - Ao clicar: st.session_state.view = ... e rerun (igual sidebar)
    # -------------------------------
    st.markdown(f"""
<style>
/* Camada clicável por cima do dock */
.omni-clicklayer {{
  position: fixed;
  top: {TOP_PX}px;
  right: {RIGHT_PX}px;
  z-index: 2147483647;
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 12px;
}}

/* Faz os st.button virarem áreas de clique sem visual */
.omni-clicklayer [data-testid="stButton"] button {{
  width: 34px !important;
  height: 34px !important;
  border-radius: 999px !important;
  padding: 0 !important;
  background: transparent !important;
  border: none !important;
  box-shadow: none !important;
}}
.omni-clicklayer [data-testid="stButton"] button:hover {{
  background: transparent !important;
}}
.omni-clicklayer [data-testid="stButton"] button p {{
  display: none !important;
}}

/* Primeiro botão: área da logo */
.omni-clicklayer .logo-area [data-testid="stButton"] button {{
  width: 26px !important;
  height: 26px !important;
}}
/* Área do separador (não clicável) */
.omni-clicklayer .sep-area {{
  width: 1px;
  height: 22px;
}}
</style>

<div class="omni-clicklayer"></div>
""", unsafe_allow_html=True)

    # A estrutura de colunas precisa reproduzir: logo + separador + 6 ícones
    # Os espaços aqui precisam bater com: gap/padding/tamanhos do CSS acima.
    with st.container():
        st.markdown('<div class="omni-clicklayer">', unsafe_allow_html=True)

        c_logo, c_sep, c1, c2, c3, c4, c5, c6 = st.columns(
            [0.55, 0.06, 0.75, 0.75, 0.75, 0.75, 0.75, 0.75],
            gap="small"
        )

        with c_logo:
            st.markdown('<div class="logo-area">', unsafe_allow_html=True)
            if st.button(" ", key="nav_home_logo", help="Home"):
                go("home")
            st.markdown('</div>', unsafe_allow_html=True)

        with c_sep:
            # separador visual já existe no dock; aqui só ocupa espaço
            st.markdown('<div class="sep-area"></div>', unsafe_allow_html=True)

        with c1:
            if st.button(" ", key="nav_home", help="Home"):
                go("home")
        with c2:
            if st.button(" ", key="nav_pei", help="Estratégias & PEI"):
                go("pei")
        with c3:
            if st.button(" ", key="nav_paee", help="Plano de Ação (PAEE)"):
                go("paee")
        with c4:
            if st.button(" ", key="nav_hub", help="Hub de Recursos"):
                go("hub")
        with c5:
            if st.button(" ", key="nav_diario", help="Diário de Bordo"):
                go("diario")
        with c6:
            if st.button(" ", key="nav_mon", help="Evolução & Acompanhamento"):
                go("mon")

        st.markdown('</div>', unsafe_allow_html=True)
