# ui_nav.py
import streamlit as st

# -------------------------
# CONFIG: Rotas oficiais do multipage
# -------------------------
ROUTES = {
    "home": "Home.py",
    "estudantes": "pages/0_Estudantes.py",
    "pei": "pages/1_PEI.py",
    "paee": "pages/2_PAE.py",
    "hub": "pages/3_Hub_Inclusao.py",
    "diario": "pages/4_Diario_de_Bordo.py",
    "mon": "pages/5_Monitoramento_Avaliacao.py",
}

# -------------------------
# Helpers
# -------------------------
def _ensure_state():
    if "autenticado" not in st.session_state:
        st.session_state.autenticado = False

def _go(key: str):
    """Navega sem recarregar em outra aba (switch_page)."""
    dest = ROUTES.get(key)
    if dest:
        st.switch_page(dest)

def render_topbar_nav(hide_on_pages=("Home.py",), show_logout=True):
    """
    Topbar fixa para páginas internas (multipage).
    - Esconde Sidebar
    - Não aparece na Home
    - Ícones Flaticon (UIcons)
    """

    _ensure_state()

    # Não renderiza na Home (portal)
    try:
        current = st.get_script_run_ctx().page_script_hash  # não confiável p/ nome
    except Exception:
        current = None

    # Forma mais confiável: pela URL do multipage costuma manter o "page" no sidebar,
    # então a gente controla pelo nome do arquivo atual via st.session_state (quando você quiser)
    # e também por tentativa: se estamos no Home.py, simplesmente não chame esta função.
    # Ainda assim: se chamarem, vamos permitir ocultar via parâmetro.

    # CSS + Flaticon icon fonts
    st.markdown("""
<style>
/* some header e sidebar padrão */
header[data-testid="stHeader"]{display:none !important;}
[data-testid="stSidebar"]{display:none !important;}
[data-testid="stSidebarNav"]{display:none !important;}

/* espaço para barra */
.block-container{
  padding-top: 78px !important;
  padding-left: 2rem !important;
  padding-right: 2rem !important;
  padding-bottom: 2rem !important;
}

/* topbar */
.omni-topbar{
  position: fixed;
  top: 0; left: 0; right: 0;
  height: 60px;
  z-index: 2147483647;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 18px;
  background: rgba(255,255,255,0.92);
  -webkit-backdrop-filter: blur(10px);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid rgba(229,231,235,0.85);
  box-shadow: 0 10px 24px rgba(15,23,42,0.06);
  font-family: system-ui, -apple-system, Segoe UI, Roboto, Arial;
}

.omni-left{
  display:flex;
  align-items:center;
  gap:10px;
  min-width: 260px;
}

.omni-mark{
  width: 28px;
  height: 28px;
  border-radius: 999px;
  background: conic-gradient(from 0deg, #3B82F6, #22C55E, #F59E0B, #F97316, #A855F7, #3B82F6);
}

.omni-name{
  font-weight: 900;
  letter-spacing: .9px;
  text-transform: uppercase;
  font-size: 13px;
  color: #111827;
}

.omni-right{
  display:flex;
  align-items:center;
  gap: 10px;
}

.omni-sep{
  width: 1px;
  height: 22px;
  background: rgba(229,231,235,0.9);
  margin: 0 6px;
}

/* botões viram ícones */
div[data-testid="stHorizontalBlock"] > div[data-testid="column"]{
  display:flex;
  justify-content:center;
  align-items:center;
}

/* estilo base dos botões */
.omni-btn button{
  width: 40px !important;
  height: 40px !important;
  padding: 0 !important;
  border-radius: 14px !important;
  border: 1px solid rgba(17,24,39,0.06) !important;
  background: transparent !important;
  box-shadow: 0 2px 10px rgba(15,23,42,0.04);
  transition: transform .12s ease, background .12s ease, filter .12s ease;
}
.omni-btn button:hover{
  transform: translateY(-1px);
  background: rgba(17,24,39,0.04) !important;
  filter: brightness(1.02);
}

/* remove texto do botão */
.omni-btn button p{
  display:none !important;
}

/* ícones */
.omni-icon{
  font-size: 22px;
  line-height: 1;
}

/* cores por módulo */
.icon-home{color:#111827;}
.icon-students{color:#2563EB;}
.icon-pei{color:#3B82F6;}
.icon-paee{color:#22C55E;}
.icon-hub{color:#F59E0B;}
.icon-diario{color:#F97316;}
.icon-mon{color:#A855F7;}
.icon-logout{color:rgba(17,24,39,0.55);}
</style>

<!-- Flaticon UIcons -->
<link rel="stylesheet" href="https://cdn-uicons.flaticon.com/uicons-solid-rounded/css/uicons-solid-rounded.css">
<link rel="stylesheet" href="https://cdn-uicons.flaticon.com/uicons-solid-straight/css/uicons-solid-straight.css">
<link rel="stylesheet" href="https://cdn-uicons.flaticon.com/uicons-regular-rounded/css/uicons-regular-rounded.css">
<link rel="stylesheet" href="https://cdn-uicons.flaticon.com/uicons-brands/css/uicons-brands.css">
""", unsafe_allow_html=True)

    # barra (HTML puro só pra moldura)
    st.markdown("""
<div class="omni-topbar">
  <div class="omni-left">
    <div class="omni-mark"></div>
    <div class="omni-name">OMNISFERA</div>
  </div>
  <div class="omni-right" id="omni-buttons-slot"></div>
</div>
""", unsafe_allow_html=True)

    # botões (Streamlit) — aparecem logo abaixo, mas o CSS deixa “integrado”
    # usamos 8 colunas: home, estudantes, pei, paee, hub, diario, mon, logout
    cols = st.columns([0.55, 0.55, 0.55, 0.55, 0.55, 0.55, 0.55, 0.25])

    def btn(col, key, icon_html, title, route_key):
        with col:
            st.markdown(f"<div class='omni-btn' title='{title}'>{icon_html}</div>", unsafe_allow_html=True)
            if st.button("go", key=key):
                _go(route_key)

    btn(cols[0], "nav_home",       '<i class="fi fi-sr-house-chimney-crack omni-icon icon-home"></i>', "Home", "home")
    btn(cols[1], "nav_students",   '<i class="fi fi-ss-users-alt omni-icon icon-students"></i>', "Estudantes", "estudantes")
    btn(cols[2], "nav_pei",        '<i class="fi fi-sr-puzzle-alt omni-icon icon-pei"></i>', "Estratégias & PEI", "pei")
    btn(cols[3], "nav_paee",       '<i class="fi fi-rr-track omni-icon icon-paee"></i>', "Plano de Ação (PAEE)", "paee")
    btn(cols[4], "nav_hub",        '<i class="fi fi-sr-lightbulb-on omni-icon icon-hub"></i>', "Hub de Recursos", "hub")
    btn(cols[5], "nav_diario",     '<i class="fi fi-br-compass-alt omni-icon icon-diario"></i>', "Diário de Bordo", "diario")
    btn(cols[6], "nav_mon",        '<i class="fi fi-br-analyse omni-icon icon-mon"></i>', "Evolução & Dados", "mon")

    if show_logout:
        with cols[7]:
            st.markdown("<div class='omni-btn' title='Sair'><i class='fi fi-rr-sign-out-alt omni-icon icon-logout'></i></div>", unsafe_allow_html=True)
            if st.button("go", key="nav_logout"):
                st.session_state.autenticado = False
                # volta pra Home -> login
                st.switch_page("Home.py")
