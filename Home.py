# ui_nav.py
import streamlit as st
# ui_nav.py
import streamlit as st
import os, base64

def _b64_img(paths):
    for p in paths:
        if p and os.path.exists(p):
            with open(p, "rb") as f:
                return "data:image/png;base64," + base64.b64encode(f.read()).decode()
    return None

def render_topbar_nav():
    # --- Estado SPA ---
    if "view" not in st.session_state:
        st.session_state.view = "login"

    # lê ?view=... (não limpa params para não quebrar login)
    qp = st.query_params
    if "view" in qp:
        v = qp["view"]
        if v in {"login","home","estudantes","pei","paee","hub","diario","mon","logout"}:
            st.session_state.view = v

    # logout por view
    if st.session_state.view == "logout":
        st.session_state.autenticado = False
        st.session_state.view = "login"
        st.rerun()

    active = st.session_state.view
    authed = bool(st.session_state.get("autenticado", False))

    # --- Assets (opcionais) ---
    logo_spin = _b64_img(["omni_icone.png","logo.png","iconeaba.png","omni.png","ominisfera.png"]) \
                or "https://cdn-icons-png.flaticon.com/512/1183/1183672.png"
    wordmark = _b64_img(["omnisfera_wordmark.png","omnisfera_nome.png"])  # se existir, usa; senão texto

    # --- Cores por módulo ---
    COLORS = {
        "home": "#111827",
        "estudantes": "#2563EB",
        "pei": "#3B82F6",
        "paee": "#22C55E",
        "hub": "#F59E0B",
        "diario": "#F97316",
        "mon": "#A855F7",
    }

    def ic_color(key: str) -> str:
        if key == active:
            return COLORS.get(key, "#111827")
        return "rgba(17,24,39,0.42)"  # inativo bem opaco

    # --- Layout ---
    BAR_H = 58

    html = """
<link href="https://cdn.jsdelivr.net/npm/remixicon@4.1.0/fonts/remixicon.css" rel="stylesheet">

<style>
/* some com o header do streamlit */
header[data-testid="stHeader"]{display:none !important;}

/* some com sidebar (visual) — mesmo se o multipage existir */
[data-testid="stSidebar"]{display:none !important;}
[data-testid="stSidebarNav"]{display:none !important;}

/* empurra conteúdo pra baixo */
.block-container{
  padding-top: {pad_top}px !important;
  padding-left: 2rem !important;
  padding-right: 2rem !important;
}

/* topbar */
.omni-topbar{
  position:fixed; top:0; left:0; right:0; height:{bar_h}px;
  z-index:2147483647;
  display:flex; align-items:center; justify-content:space-between;
  padding:0 16px;

  background: rgba(255,255,255,0.92);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border-bottom: 1px solid rgba(229,231,235,0.85);
  box-shadow: 0 8px 24px rgba(15,23,42,0.06);
  font-family: system-ui, -apple-system, Segoe UI, Roboto, Arial;
}

.omni-left{
  display:flex; align-items:center; gap:10px;
  min-width: 240px;
}

@keyframes spin{from{transform:rotate(0deg);}to{transform:rotate(360deg);}}
.omni-logo{
  width: 26px; height:26px;
  animation: spin 12s linear infinite;
}

.omni-word{
  font-weight: 900;
  letter-spacing: .7px;
  text-transform: uppercase;
  font-size: 14px;
  color: #111827;
}

.omni-wordmark{
  height: 18px;
  width: auto;
  object-fit: contain;
}

.omni-right{
  display:flex; align-items:center; gap: 14px;
}

.omni-link{
  width: 32px; height: 32px;
  display:inline-flex; align-items:center; justify-content:center;
  border-radius: 12px;
  text-decoration:none !important;
  transition: transform .12s ease, filter .12s ease, background .12s ease;
}
.omni-link:hover{
  transform: translateY(-1px);
  filter: brightness(1.04);
  background: rgba(17,24,39,0.04);
}

.omni-ic{ font-size: 22px; line-height:1; }

.omni-sep{
  width:1px; height:22px; background: rgba(229,231,235,0.9);
}
</style>

<div class="omni-topbar">
  <div class="omni-left">
    <img src="{logo}" class="omni-logo" alt="Omnisfera"/>
    <div class="omni-word">
      {wordmark_html}
    </div>
  </div>

  <div class="omni-right">
    {menu_html}
  </div>
</div>
"""

    # se tiver wordmark png, usa; se não, texto
    wordmark_html = f"<img src='{wordmark}' class='omni-wordmark' alt='Omnisfera'/>" if wordmark else "OMNISFERA"

    # menu só aparece autenticado (pra não “poluir” login)
    if authed:
        menu_html = f"""
        <a class="omni-link" href="?view=home" target="_self" title="Home">
          <i class="ri-home-5-fill omni-ic" style="color:{ic_color('home')}"></i>
        </a>
        <a class="omni-link" href="?view=estudantes" target="_self" title="Estudantes">
          <i class="ri-group-fill omni-ic" style="color:{ic_color('estudantes')}"></i>
        </a>
        <a class="omni-link" href="?view=pei" target="_self" title="Estratégias & PEI">
          <i class="ri-puzzle-2-fill omni-ic" style="color:{ic_color('pei')}"></i>
        </a>
        <a class="omni-link" href="?view=paee" target="_self" title="Plano de Ação (PAEE)">
          <i class="ri-map-pin-2-fill omni-ic" style="color:{ic_color('paee')}"></i>
        </a>
        <a class="omni-link" href="?view=hub" target="_self" title="Hub de Recursos">
          <i class="ri-lightbulb-flash-fill omni-ic" style="color:{ic_color('hub')}"></i>
        </a>
        <a class="omni-link" href="?view=diario" target="_self" title="Diário de Bordo">
          <i class="ri-compass-3-fill omni-ic" style="color:{ic_color('diario')}"></i>
        </a>
        <a class="omni-link" href="?view=mon" target="_self" title="Evolução & Acompanhamento">
          <i class="ri-line-chart-fill omni-ic" style="color:{ic_color('mon')}"></i>
        </a>
        <span class="omni-sep"></span>
        <a class="omni-link" href="?view=logout" target="_self" title="Sair">
          <i class="ri-logout-circle-r-line omni-ic" style="color:rgba(17,24,39,0.55)"></i>
        </a>
        """
    else:
        menu_html = ""  # no login, só a marca

    st.markdown(
        html.format(
            pad_top=BAR_H + 18,
            bar_h=BAR_H,
            logo=logo_spin,
            wordmark_html=wordmark_html,
            menu_html=menu_html
        ),
        unsafe_allow_html=True
    )

import os, base64

def _b64_img(paths):
    for p in paths:
        if p and os.path.exists(p):
            with open(p, "rb") as f:
                return "data:image/png;base64," + base64.b64encode(f.read()).decode()
    return None

def render_topbar_nav():
    # --- Estado SPA ---
    if "view" not in st.session_state:
        st.session_state.view = "login"

    # lê ?view=... (não limpa params para não quebrar login)
    qp = st.query_params
    if "view" in qp:
        v = qp["view"]
        if v in {"login","home","estudantes","pei","paee","hub","diario","mon","logout"}:
            st.session_state.view = v

    # logout por view
    if st.session_state.view == "logout":
        st.session_state.autenticado = False
        st.session_state.view = "login"
        st.rerun()

    active = st.session_state.view
    authed = bool(st.session_state.get("autenticado", False))

    # --- Assets (opcionais) ---
    logo_spin = _b64_img(["omni_icone.png","logo.png","iconeaba.png","omni.png","ominisfera.png"]) \
                or "https://cdn-icons-png.flaticon.com/512/1183/1183672.png"
    wordmark = _b64_img(["omnisfera_wordmark.png","omnisfera_nome.png"])  # se existir, usa; senão texto

    # --- Cores por módulo ---
    COLORS = {
        "home": "#111827",
        "estudantes": "#2563EB",
        "pei": "#3B82F6",
        "paee": "#22C55E",
        "hub": "#F59E0B",
        "diario": "#F97316",
        "mon": "#A855F7",
    }

    def ic_color(key: str) -> str:
        if key == active:
            return COLORS.get(key, "#111827")
        return "rgba(17,24,39,0.42)"  # inativo bem opaco

    # --- Layout ---
    BAR_H = 58

    html = """
<link href="https://cdn.jsdelivr.net/npm/remixicon@4.1.0/fonts/remixicon.css" rel="stylesheet">

<style>
/* some com o header do streamlit */
header[data-testid="stHeader"]{display:none !important;}

/* some com sidebar (visual) — mesmo se o multipage existir */
[data-testid="stSidebar"]{display:none !important;}
[data-testid="stSidebarNav"]{display:none !important;}

/* empurra conteúdo pra baixo */
.block-container{
  padding-top: {pad_top}px !important;
  padding-left: 2rem !important;
  padding-right: 2rem !important;
}

/* topbar */
.omni-topbar{
  position:fixed; top:0; left:0; right:0; height:{bar_h}px;
  z-index:2147483647;
  display:flex; align-items:center; justify-content:space-between;
  padding:0 16px;

  background: rgba(255,255,255,0.92);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border-bottom: 1px solid rgba(229,231,235,0.85);
  box-shadow: 0 8px 24px rgba(15,23,42,0.06);
  font-family: system-ui, -apple-system, Segoe UI, Roboto, Arial;
}

.omni-left{
  display:flex; align-items:center; gap:10px;
  min-width: 240px;
}

@keyframes spin{from{transform:rotate(0deg);}to{transform:rotate(360deg);}}
.omni-logo{
  width: 26px; height:26px;
  animation: spin 12s linear infinite;
}

.omni-word{
  font-weight: 900;
  letter-spacing: .7px;
  text-transform: uppercase;
  font-size: 14px;
  color: #111827;
}

.omni-wordmark{
  height: 18px;
  width: auto;
  object-fit: contain;
}

.omni-right{
  display:flex; align-items:center; gap: 14px;
}

.omni-link{
  width: 32px; height: 32px;
  display:inline-flex; align-items:center; justify-content:center;
  border-radius: 12px;
  text-decoration:none !important;
  transition: transform .12s ease, filter .12s ease, background .12s ease;
}
.omni-link:hover{
  transform: translateY(-1px);
  filter: brightness(1.04);
  background: rgba(17,24,39,0.04);
}

.omni-ic{ font-size: 22px; line-height:1; }

.omni-sep{
  width:1px; height:22px; background: rgba(229,231,235,0.9);
}
</style>

<div class="omni-topbar">
  <div class="omni-left">
    <img src="{logo}" class="omni-logo" alt="Omnisfera"/>
    <div class="omni-word">
      {wordmark_html}
    </div>
  </div>

  <div class="omni-right">
    {menu_html}
  </div>
</div>
"""

    # se tiver wordmark png, usa; se não, texto
    wordmark_html = f"<img src='{wordmark}' class='omni-wordmark' alt='Omnisfera'/>" if wordmark else "OMNISFERA"

    # menu só aparece autenticado (pra não “poluir” login)
    if authed:
        menu_html = f"""
        <a class="omni-link" href="?view=home" target="_self" title="Home">
          <i class="ri-home-5-fill omni-ic" style="color:{ic_color('home')}"></i>
        </a>
        <a class="omni-link" href="?view=estudantes" target="_self" title="Estudantes">
          <i class="ri-group-fill omni-ic" style="color:{ic_color('estudantes')}"></i>
        </a>
        <a class="omni-link" href="?view=pei" target="_self" title="Estratégias & PEI">
          <i class="ri-puzzle-2-fill omni-ic" style="color:{ic_color('pei')}"></i>
        </a>
        <a class="omni-link" href="?view=paee" target="_self" title="Plano de Ação (PAEE)">
          <i class="ri-map-pin-2-fill omni-ic" style="color:{ic_color('paee')}"></i>
        </a>
        <a class="omni-link" href="?view=hub" target="_self" title="Hub de Recursos">
          <i class="ri-lightbulb-flash-fill omni-ic" style="color:{ic_color('hub')}"></i>
        </a>
        <a class="omni-link" href="?view=diario" target="_self" title="Diário de Bordo">
          <i class="ri-compass-3-fill omni-ic" style="color:{ic_color('diario')}"></i>
        </a>
        <a class="omni-link" href="?view=mon" target="_self" title="Evolução & Acompanhamento">
          <i class="ri-line-chart-fill omni-ic" style="color:{ic_color('mon')}"></i>
        </a>
        <span class="omni-sep"></span>
        <a class="omni-link" href="?view=logout" target="_self" title="Sair">
          <i class="ri-logout-circle-r-line omni-ic" style="color:rgba(17,24,39,0.55)"></i>
        </a>
        """
    else:
        menu_html = ""  # no login, só a marca

    st.markdown(
        html.format(
            pad_top=BAR_H + 18,
            bar_h=BAR_H,
            logo=logo_spin,
            wordmark_html=wordmark_html,
            menu_html=menu_html
        ),
        unsafe_allow_html=True
    )
