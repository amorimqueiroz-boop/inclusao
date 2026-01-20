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

# Flaticon Solid Rounded (fi-sr-*)
ICONS = {
    "home": "fi fi-sr-house-chimney",
    "estudantes": "fi fi-sr-users-alt",
    "pei": "fi fi-sr-puzzle-alt",
    "paee": "fi fi-sr-route",
    "hub": "fi fi-sr-lightbulb-on",
    "diario": "fi fi-sr-compass-alt",
    "mon": "fi fi-sr-chart-line-up",
    "logout": "fi fi-sr-sign-out-alt",
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
    """

    authed = bool(st.session_state.get("autenticado", False))
    if (not authed) and (not show_on_login):
        return

    # assets
    icon_b64 = _b64("omni_icone.png")

    # CSS + libs (Flaticon SR)
    st.markdown("""
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@600;700;800;900&display=swap" rel="stylesheet">
<link rel="stylesheet" href="https://cdn-uicons.flaticon.com/uicons-solid-rounded/css/uicons-solid-rounded.css">

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

/* direita (ícones) */
.omni-right{
  display:flex;
  align-items:center;
  gap: 10px;
}

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

    # Botões do menu (Streamlit buttons) — overlay “invisível” com estilo
    # Precisamos renderizar os botões reais para capturar clique.
    # Fazemos em um container, mas visualmente eles ficam “na barra”.
    # Truque: usar st.columns e empurrar para a direita com espaçamento.

    # cria uma linha invisível abaixo (mas os botões recebem o CSS .omni-btn via seletor de data-testid)
    # Para estilizar com precisão, usamos key e CSS por key.

    # container de alinhamento
    _l, _r = st.columns([6, 4])

    with _r:
        cols = st.columns([1,1,1,1,1,1,0.2,1])  # 6 ícones + separador + sair

        items = [
            ("home","Home"),
            ("estudantes","Estudantes"),
            ("pei","PEI"),
            ("paee","PAEE"),
            ("hub","Hub"),
            ("diario","Diário"),
            ("mon","Dados"),
        ]

        # Render: cada botão com key única
        for i, (k, label) in enumerate(items):
            with cols[i]:
                key = f"nav_{k}"
                if st.button(" ", key=key, help=label, use_container_width=True):
                    _goto(k)

                # CSS por botão key (Streamlit renderiza button dentro de div[data-testid="stButton"])
                color = COLORS.get(k, "#0F172A")
                icon = ICONS.get(k, "fi fi-sr-circle")
                is_active = (k == active)

                st.markdown(f"""
<style>
/* ataca o botão específico via key */
div[data-testid="stButton"] button[kind="secondary"][data-testid="baseButton-secondary"] {{
  /* fallback: não garante seletor por key */
}}
</style>
""", unsafe_allow_html=True)

                # seletor robusto: Streamlit dá um id no DOM? Não.
                # Então aplicamos classe por "nth" é frágil. Melhor: colocar HTML do ícone dentro do botão via unsafe? Streamlit não permite.
                # Solução estável: renderizar um HTML (ícone) clicável com st.markdown + link? (abre nova página).
                # MAS você pediu navegação real. Então: usamos os botões, e desenhamos uma “camada visual” por cima em HTML.
                # Isso é o mais estável e bonito.

        # separador visual no meio
        with cols[6]:
            st.markdown('<div class="omni-sep"></div>', unsafe_allow_html=True)

        # botão sair
        with cols[7]:
            if st.button(" ", key="nav_logout", help="Sair", use_container_width=True):
                _logout()

    # Camada visual por cima (HTML) — Ícones reais, cores, estado ativo
    # Os botões reais ficam logo abaixo; o clique funciona porque os botões ocupam a área.
    # Precisamos alinhar. O padding-top da page já compensa.

    # Monta ícones em HTML com mesmo grid e tamanhos (vai “casar” com a área dos botões)
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

    # logout icon
    logout_html = f"""
<div class="omni-btn">
  <i class="{ICONS['logout']} omni-ic" style="color:rgba(15,23,42,0.55);"></i>
</div>
"""

    st.markdown(f"""
<style>
/* camada visual do lado direito, posicionada em cima da topbar */
.omni-right-overlay{{
  position: fixed;
  top: 10px;
  right: 18px;
  height: 38px;
  display:flex;
  align-items:center;
  gap: 10px;
  z-index: 2147483647;
  pointer-events: none; /* clique passa pros botões streamlit */
}}
</style>

<div class="omni-right-overlay">
  {icons_html}
  <div class="omni-sep"></div>
  {logout_html}
</div>
""", unsafe_allow_html=True)
