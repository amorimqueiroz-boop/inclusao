# ui_nav.py
import streamlit as st
import base64, os

# -------------------------
# CONFIG (paths + cores + ícones)
# -------------------------
PAGES = {
    "home":       "Home.py",
    "estudantes": "pages/0_Alunos.py",
    "pei":        "pages/1_PEI.py",
    "paee":       "pages/2_PAE.py",
    "hub":        "pages/3_Hub_Inclusao.py",
    "diario":     "pages/4_Diario_de_Bordo.py",
    "mon":        "pages/5_Monitoramento_Avaliacao.py",
}

COLORS = {
    "home": "#0F172A",       # neutro
    "estudantes": "#2B6CEB",
    "pei": "#2F7DF6",
    "paee": "#22A765",
    "hub": "#D98A0A",
    "diario": "#E05A1C",
    "mon": "#8B5CF6",
}

# ÍCONES (classes Flaticon). Mantemos classes por módulo;
# as FAMÍLIAS (bold-rounded / solid-rounded / solid-straight) são carregadas via <link>.
ICONS = {
    "home": "fi fi-br-house-chimney",        # bold-rounded
    "estudantes": "fi fi-sr-users-alt",      # solid-rounded
    "pei": "fi fi-sr-puzzle-alt",            # solid-rounded
    "paee": "fi fi-ss-route",                # solid-straight
    "hub": "fi fi-sr-lightbulb-on",          # solid-rounded
    "diario": "fi fi-br-compass-alt",        # bold-rounded
    "mon": "fi fi-br-chart-line-up",         # bold-rounded
    "logout": "fi fi-sr-sign-out-alt",       # solid-rounded neutro
}

def _b64(path: str) -> str:
    if not os.path.exists(path):
        return ""
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

def _goto(page_key: str):
    """Navegação multipage real (sem query params)."""
    target = PAGES.get(page_key)
    if not target:
        return
    st.switch_page(target)

def _logout():
    st.session_state.autenticado = False
    st.rerun()

def render_topbar_nav(active: str = "home", show_on_login: bool = False):
    """
    Topbar minimalista e fixa.
    - active: chave do módulo atual (home/estudantes/pei/paee/hub/diario/mon)
    - show_on_login: se False, não mostra a barra quando não autenticado

    ✅ IMPORTANTE:
    Aqui o clique funciona 100% porque:
    - Os botões reais do Streamlit são posicionados FIXOS na topbar (mas invisíveis).
    - Os ícones (HTML) ficam por cima (pointer-events:none) e o clique “passa” para os botões.
    """

    authed = bool(st.session_state.get("autenticado", False))
    if (not authed) and (not show_on_login):
        return

    # assets
    icon_b64 = _b64("omni_icone.png")

    # CSS + libs (Flaticon: famílias padrão Omnisfera)
    st.markdown("""
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@600;700;800;900&display=swap" rel="stylesheet">

<!-- Flaticon UIcons v3.0.0 — famílias padrão Omnisfera -->
<link rel='stylesheet' href='https://cdn-uicons.flaticon.com/3.0.0/uicons-bold-rounded/css/uicons-bold-rounded.css'>
<link rel='stylesheet' href='https://cdn-uicons.flaticon.com/3.0.0/uicons-solid-rounded/css/uicons-solid-rounded.css'>
<link rel='stylesheet' href='https://cdn-uicons.flaticon.com/3.0.0/uicons-solid-straight/css/uicons-solid-straight.css'>

<style>
header[data-testid="stHeader"]{display:none !important;}
[data-testid="stSidebar"]{display:none !important;}
[data-testid="stSidebarNav"]{display:none !important;}
[data-testid="stToolbar"]{display:none !important;}

/* espaço para a barra */
.block-container{
  padding-top: 86px !important;   /* topbar 58px + respiro */
  padding-left: 2rem !important;
  padding-right: 2rem !important;
}

/* topbar */
@keyframes spin{from{transform:rotate(0deg);}to{transform:rotate(360deg);} }

.omni-topbar{
  position:fixed;
  top:0; left:0; right:0;
  height:58px;
  z-index:2147483647;
  display:flex;
  align-items:center;
  justify-content:space-between;
  padding: 0 18px;
  background: rgba(247,250,252,0.88);
  -webkit-backdrop-filter: blur(14px);
  backdrop-filter: blur(14px);
  border-bottom: 1px solid rgba(226,232,240,0.85);
  box-shadow: 0 8px 20px rgba(15,23,42,0.06);
  font-family: Inter, system-ui, -apple-system, Segoe UI, Roboto, Arial;
}

/* esquerda */
.omni-left{
  display:flex;
  align-items:center;
  gap:10px;
  min-width: 240px;
}
.omni-spin{
  width:34px; height:34px;
  border-radius: 999px;
  animation: spin 45s linear infinite;
  filter: drop-shadow(0 2px 4px rgba(0,0,0,0.10));
}
.omni-mark-fallback{
  width:34px; height:34px;
  border-radius:999px;
  background: conic-gradient(from 0deg,#3B82F6,#22C55E,#F59E0B,#F97316,#A855F7,#3B82F6);
  animation: spin 45s linear infinite;
}
.omni-name{
  font-weight: 900;
  letter-spacing: .14em;
  text-transform: uppercase;
  font-size: 0.82rem;
  color:#0F172A;
}

/* ===== camada VISUAL (ícones) ===== */
.omni-btn{
  width: 38px;
  height: 38px;
  border-radius: 14px;
  display:flex;
  align-items:center;
  justify-content:center;
  border: 1px solid rgba(226,232,240,0.95);
  background: rgba(255,255,255,0.70);
  box-shadow: 0 6px 14px rgba(15,23,42,0.05);
  transition: transform .14s ease, box-shadow .14s ease, filter .14s ease;
  cursor:pointer;
  padding:0;
}

.omni-btn:hover{
  transform: translateY(-1px);
  box-shadow: 0 10px 22px rgba(15,23,42,0.10);
  filter: brightness(1.02);
}

.omni-ic{
  font-size: 18px;
  line-height: 1;
  display:flex;
}

/* ativo: halo sutil */
.omni-btn.active{
  border-color: rgba(15,23,42,0.16);
  background: rgba(255,255,255,0.92);
}

.omni-sep{
  width:1px;
  height: 22px;
  background: rgba(226,232,240,1);
  margin: 0 4px;
}

/* ===== camada de CLIQUE (botões Streamlit) =====
   A âncora (#omni-nav-anchor) vem imediatamente antes do bloco de colunas com botões.
   Então a gente move esse bloco FIXO pra topbar e deixa invisível (opacity:0).
   Resultado: clique perfeito “colado” no ícone. Sem caixas brancas no corpo da página.
*/
#omni-nav-anchor + div[data-testid="stHorizontalBlock"]{
  position: fixed !important;
  top: 10px !important;
  right: 18px !important;
  width: auto !important;
  z-index: 2147483646 !important; /* abaixo dos ícones visuais */
  opacity: 0 !important;          /* invisível */
  pointer-events: auto !important; /* recebe clique */
  margin: 0 !important;
  padding: 0 !important;
}

/* garante que os botões tenham exatamente o mesmo tamanho dos ícones */
#omni-nav-anchor + div[data-testid="stHorizontalBlock"] div[data-testid="stButton"] > button{
  width: 38px !important;
  height: 38px !important;
  border-radius: 14px !important;
  padding: 0 !important;
  border: 0 !important;
  background: transparent !important;
}

/* tira espaçamento extra do bloco de colunas */
#omni-nav-anchor + div[data-testid="stHorizontalBlock"] > div{
  gap: 10px !important;
}

/* ===== overlay de ícones (visual) ===== */
.omni-right-overlay{
  position: fixed;
  top: 10px;
  right: 18px;
  height: 38px;
  display:flex;
  align-items:center;
  gap: 10px;
  z-index: 2147483647;
  pointer-events: none; /* clique passa pra camada invisível dos botões */
}

@media (max-width: 900px){
  .omni-name{display:none;}
  .block-container{padding-top: 82px !important;}
}
</style>
""", unsafe_allow_html=True)

    # HTML topo (logo)
    if icon_b64:
        left_html = f'<img class="omni-spin" src="data:image/png;base64,{icon_b64}" />'
    else:
        left_html = '<div class="omni-mark-fallback"></div>'

    st.markdown(f"""
<div class="omni-topbar">
  <div class="omni-left">
    {left_html}
    <div class="omni-name">OMNISFERA</div>
  </div>
</div>
""", unsafe_allow_html=True)

    # ------------------------------------------------------------------
    # CAMADA DE CLIQUE (botões Streamlit) — ANCORADA e movida via CSS
    # ------------------------------------------------------------------
    st.markdown('<div id="omni-nav-anchor"></div>', unsafe_allow_html=True)

    cols = st.columns([1,1,1,1,1,1,1,0.2,1])  # 7 ícones + separador + sair

    items = [
        ("home", "Home"),
        ("estudantes", "Estudantes"),
        ("pei", "Estratégias & PEI"),
        ("paee", "Plano de Ação (PAEE)"),
        ("hub", "Hub de Recursos"),
        ("diario", "Diário de Bordo"),
        ("mon", "Evolução & Dados"),
    ]

    for i, (k, label) in enumerate(items):
        with cols[i]:
            if st.button(" ", key=f"nav_{k}", help=label, use_container_width=True):
                _goto(k)

    with cols[7]:
        st.markdown('<div class="omni-sep"></div>', unsafe_allow_html=True)

    with cols[8]:
        if st.button(" ", key="nav_logout", help="Sair", use_container_width=True):
            _logout()

    # ------------------------------------------------------------------
    # CAMADA VISUAL (ícones HTML) — por cima, sem capturar clique
    # ------------------------------------------------------------------
    icons_html = ""
    for k, label in [
        ("home","Home"),
        ("estudantes","Estudantes"),
        ("pei","Estratégias & PEI"),
        ("paee","Plano de Ação"),
        ("hub","Hub"),
        ("diario","Diário"),
        ("mon","Evolução & Dados"),
    ]:
        color = COLORS.get(k, "#0F172A")
        ic = ICONS.get(k, "fi fi-sr-circle")
        active_cls = "active" if (k == active) else ""
        icons_html += f"""
<div class="omni-btn {active_cls}">
  <i class="{ic} omni-ic" style="color:{color};"></i>
</div>
"""

    logout_html = f"""
<div class="omni-btn">
  <i class="{ICONS['logout']} omni-ic" style="color:rgba(15,23,42,0.55);"></i>
</div>
"""

    st.markdown(f"""
<div class="omni-right-overlay">
  {icons_html}
  <div class="omni-sep"></div>
  {logout_html}
</div>
""", unsafe_allow_html=True)
