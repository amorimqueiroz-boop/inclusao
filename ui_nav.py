# ui_nav.py
import streamlit as st
import os, base64


def render_omnisfera_nav(
    show_on_login: bool = True,
    top_px: int = 8,
    right_px: int = 14,
):
    """
    Dock / Topbar fixo no canto superior direito:
    - Camada VISUAL em HTML (Flaticon UIcons) com pointer-events:none
    - Camada CLICÁVEL real em Streamlit (botões) fixada via CSS por âncora
    - Estado SPA por st.session_state.view

    Retorna: view ativa (str)
    """

    # -------------------------------
    # 1) Estado SPA
    # -------------------------------
    if "view" not in st.session_state:
        st.session_state.view = "home"

    def go(view_key: str):
        st.session_state.view = view_key
        st.rerun()

    ACTIVE = st.session_state.view

    # Se você usa login
    authed = bool(st.session_state.get("autenticado", True))
    if (not authed) and (not show_on_login):
        return ACTIVE

    # -------------------------------
    # 2) Logo base64
    # -------------------------------
    def logo_src():
        for f in ["omni_icone.png", "logo.png", "iconeaba.png", "omni.png", "ominisfera.png"]:
            if os.path.exists(f):
                with open(f, "rb") as img:
                    return f"data:image/png;base64,{base64.b64encode(img.read()).decode()}"
        # fallback
        return "https://cdn-icons-png.flaticon.com/512/1183/1183672.png"

    src = logo_src()

    # -------------------------------
    # 3) Config visual (cores por módulo)
    # -------------------------------
    COLORS = {
        "home": "#111827",
        "estudantes": "#2B6CEB",
        "pei": "#3B82F6",
        "paee": "#22C55E",
        "hub": "#F59E0B",
        "diario": "#F97316",
        "mon": "#A855F7",
        "logout": "#6B7280",
    }

    # -------------------------------
    # 4) ÍCONES — padrão Flaticon UIcons v3.0.0
    #    (mantendo o mapeamento que você definiu)
    # -------------------------------
    ICONS = {
        # Home (bold-rounded)
        "home": "fi fi-br-house-chimney",

        # Estudantes (vamos de solid-rounded para manter o “core” do app)
        "estudantes": "fi fi-sr-users-alt",

        # Estratégias & PEI (solid-rounded)
        "pei": "fi fi-sr-puzzle-alt",

        # PAEE (solid-straight)
        "paee": "fi fi-ss-route",

        # Hub (solid-rounded)
        "hub": "fi fi-sr-lightbulb-on",

        # Diário (bold-rounded)
        "diario": "fi fi-br-compass-alt",

        # Evolução & Dados (bold-rounded)
        "mon": "fi fi-br-chart-line-up",

        # Logout (solid-rounded)
        "logout": "fi fi-sr-sign-out-alt",
    }

    def style_for(key: str):
        solid = COLORS.get(key, "#111827")
        if key == ACTIVE:
            return (
                f"background:{solid}; color:#FFFFFF;"
                "box-shadow: 0 0 0 3px rgba(255,255,255,0.95), 0 10px 22px rgba(15,23,42,0.12);"
                "filter:none; opacity:1;"
            )
        else:
            return (
                f"background:{solid}; color:rgba(255,255,255,0.78);"
                "box-shadow: 0 2px 10px rgba(15,23,42,0.06);"
                "filter:saturate(0.65) brightness(1.12); opacity:0.72;"
            )

    # -------------------------------
    # 5) CSS + DOCK visual (HTML)
    # -------------------------------
    st.markdown(
        f"""
<!-- Flaticon UIcons v3.0.0 — famílias padrão Omnisfera -->
<link rel='stylesheet' href='https://cdn-uicons.flaticon.com/3.0.0/uicons-bold-rounded/css/uicons-bold-rounded.css'>
<link rel='stylesheet' href='https://cdn-uicons.flaticon.com/3.0.0/uicons-solid-rounded/css/uicons-solid-rounded.css'>
<link rel='stylesheet' href='https://cdn-uicons.flaticon.com/3.0.0/uicons-solid-straight/css/uicons-solid-straight.css'>

<style>
/* “Mute” no header do Streamlit para o dock dominar (mesma estratégia do seu código) */
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
  top: {top_px}px !important;
  right: {right_px}px !important;
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

/* bolinhas */
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

  <div class="omni-ico" style="{style_for('home')}"><i class="{ICONS['home']} omni-ic"></i></div>
  <div class="omni-ico" style="{style_for('estudantes')}"><i class="{ICONS['estudantes']} omni-ic"></i></div>
  <div class="omni-ico" style="{style_for('pei')}"><i class="{ICONS['pei']} omni-ic"></i></div>
  <div class="omni-ico" style="{style_for('paee')}"><i class="{ICONS['paee']} omni-ic"></i></div>
  <div class="omni-ico" style="{style_for('hub')}"><i class="{ICONS['hub']} omni-ic"></i></div>
  <div class="omni-ico" style="{style_for('diario')}"><i class="{ICONS['diario']} omni-ic"></i></div>
  <div class="omni-ico" style="{style_for('mon')}"><i class="{ICONS['mon']} omni-ic"></i></div>

  <div class="omni-sep"></div>
  <div class="omni-ico" style="background:#F3F4F6; color:#6B7280; opacity:1; filter:none;">
    <i class="{ICONS['logout']} omni-ic"></i>
  </div>
</div>
        """,
        unsafe_allow_html=True,
    )

    # -------------------------------
    # 6) Camada clicável REAL (Streamlit) — fixada via âncora (igual ao seu)
    # -------------------------------
    st.markdown('<div id="omni-click-anchor"></div>', unsafe_allow_html=True)

    # Logo + separador + 7 botões + separador + logout
    c_logo, c_sep1, c1, c2, c3, c4, c5, c6, c7, c_sep2, c_out = st.columns(
        [0.6, 0.08, 0.7, 0.7, 0.7, 0.7, 0.7, 0.7, 0.7, 0.08, 0.7],
        gap="small",
    )

    with c_logo:
        if st.button(" ", key="omni_nav_logo", help="Home"):
            go("home")

    with c_sep1:
        st.write("")

    with c1:
        if st.button(" ", key="omni_nav_home", help="Home"):
            go("home")

    with c2:
        if st.button(" ", key="omni_nav_estudantes", help="Estudantes"):
            go("estudantes")

    with c3:
        if st.button(" ", key="omni_nav_pei", help="Estratégias & PEI"):
            go("pei")

    with c4:
        if st.button(" ", key="omni_nav_paee", help="Plano de Ação (PAEE)"):
            go("paee")

    with c5:
        if st.button(" ", key="omni_nav_hub", help="Hub de Recursos"):
            go("hub")

    with c6:
        if st.button(" ", key="omni_nav_diario", help="Diário de Bordo"):
            go("diario")

    with c7:
        if st.button(" ", key="omni_nav_mon", help="Evolução & Dados"):
            go("mon")

    with c_sep2:
        st.write("")

    with c_out:
        if st.button(" ", key="omni_nav_logout", help="Sair"):
            # se existir auth, desloga; senão só volta home
            if "autenticado" in st.session_state:
                st.session_state.autenticado = False
            st.session_state.view = "home"
            st.rerun()

    # -------------------------------
    # 7) CSS pós-render: fixa o bloco de botões logo após a âncora (mesma técnica “que deu certo”)
    # -------------------------------
    st.markdown(
        f"""
<style>
/* fixa o bloco de colunas que vem logo depois da âncora */
#omni-click-anchor + div {{
  position: fixed !important;
  top: {top_px}px !important;
  right: {right_px}px !important;
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

  opacity: 0 !important;           /* some com as “caixas brancas” */
  pointer-events: auto !important; /* mas continua clicável */
}}

/* botões viram áreas de clique do tamanho exato das bolinhas */
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

/* logo: área clicável do tamanho da logo */
#omni-click-anchor + div [data-testid="column"]:nth-child(1) [data-testid="stButton"] button {{
  width: 28px !important;
  height: 28px !important;
}}

/* colunas “separador”: só ocupam espaço */
#omni-click-anchor + div [data-testid="column"]:nth-child(2),
#omni-click-anchor + div [data-testid="column"]:nth-child(10) {{
  width: 1px !important;
}}
</style>
        """,
        unsafe_allow_html=True,
    )

    return ACTIVE
