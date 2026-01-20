# ui_nav.py
import streamlit as st

def _safe_get_query_view():
    try:
        qp = st.query_params
        if "view" in qp:
            return qp["view"]
    except Exception:
        pass
    return None

def _ensure_state():
    if "autenticado" not in st.session_state:
        st.session_state.autenticado = False
    if "view" not in st.session_state:
        st.session_state.view = "login" if not st.session_state.autenticado else "home"

def render_topbar_nav(hide_on_views=("home", "login")):
    """
    Topbar minimal (para views internas).
    NÃO aparece em: home + login (portal/login).
    """

    _ensure_state()

    v = _safe_get_query_view()
    if v in ("login", "home", "estudantes", "pei", "paee", "hub", "diario", "mon", "logout"):
        st.session_state.view = v

    if st.session_state.view == "logout":
        st.session_state.autenticado = False
        st.session_state.view = "login"
        st.rerun()

    authed = bool(st.session_state.get("autenticado", False))
    active = st.session_state.get("view", "login")

    if active in set(hide_on_views):
        return

    colors = {
        "home": "#111827",
        "estudantes": "#2563EB",
        "pei": "#3B82F6",
        "paee": "#22C55E",
        "hub": "#F59E0B",
        "diario": "#F97316",
        "mon": "#A855F7",
    }

    def ic_color(key: str):
        if key == active:
            return colors.get(key, "#111827")
        return "rgba(17,24,39,0.42)"

    st.markdown(
        """
<style>
header[data-testid="stHeader"]{display:none !important;}
[data-testid="stSidebar"]{display:none !important;}
[data-testid="stSidebarNav"]{display:none !important;}
.block-container{padding-top:76px !important; padding-left:2rem !important; padding-right:2rem !important;}

.omni-topbar{
  position:fixed; top:0; left:0; right:0; height:58px;
  z-index:2147483647;
  display:flex; align-items:center; justify-content:space-between;
  padding:0 16px;
  background: rgba(255,255,255,0.92);
  -webkit-backdrop-filter: blur(10px);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid rgba(229,231,235,0.85);
  box-shadow: 0 8px 24px rgba(15,23,42,0.06);
  font-family: system-ui, -apple-system, Segoe UI, Roboto, Arial;
}
.omni-left{display:flex; align-items:center; gap:10px; min-width:240px;}
.omni-mark{
  width:26px; height:26px; border-radius:999px;
  background: conic-gradient(from 0deg, #3B82F6, #22C55E, #F59E0B, #F97316, #A855F7, #3B82F6);
}
.omni-name{font-weight:900; letter-spacing:.7px; text-transform:uppercase; font-size:14px; color:#111827;}
.omni-right{display:flex; align-items:center; gap:14px;}
.omni-link{
  width:32px; height:32px;
  display:inline-flex; align-items:center; justify-content:center;
  border-radius:12px;
  text-decoration:none !important;
  transition: transform .12s ease, filter .12s ease, background .12s ease;
}
.omni-link:hover{transform: translateY(-1px); filter: brightness(1.04); background: rgba(17,24,39,0.04);}
.omni-ic{font-size:22px; line-height:1; font-weight:900;}
.omni-sep{width:1px; height:22px; background: rgba(229,231,235,0.9);}
</style>
""",
        unsafe_allow_html=True,
    )

    if not authed:
        return

    st.markdown(
        f"""
<div class="omni-topbar">
  <div class="omni-left">
    <div class="omni-mark"></div>
    <div class="omni-name">OMNISFERA</div>
  </div>

  <div class="omni-right">
    <a class="omni-link" href="?view=home" target="_self" title="Home"><span class="omni-ic" style="color:{ic_color('home')}">⌂</span></a>
    <a class="omni-link" href="?view=estudantes" target="_self" title="Estudantes"><span class="omni-ic" style="color:{ic_color('estudantes')}">◉</span></a>
    <a class="omni-link" href="?view=pei" target="_self" title="Estratégias & PEI"><span class="omni-ic" style="color:{ic_color('pei')}">🧩</span></a>
    <a class="omni-link" href="?view=paee" target="_self" title="Plano de Ação (PAEE)"><span class="omni-ic" style="color:{ic_color('paee')}">📍</span></a>
    <a class="omni-link" href="?view=hub" target="_self" title="Hub de Recursos"><span class="omni-ic" style="color:{ic_color('hub')}">💡</span></a>
    <a class="omni-link" href="?view=diario" target="_self" title="Diário de Bordo"><span class="omni-ic" style="color:{ic_color('diario')}">🧭</span></a>
    <a class="omni-link" href="?view=mon" target="_self" title="Evolução & Acompanhamento"><span class="omni-ic" style="color:{ic_color('mon')}">📈</span></a>
    <span class="omni-sep"></span>
    <a class="omni-link" href="?view=logout" target="_self" title="Sair"><span class="omni-ic" style="color:rgba(17,24,39,0.55)">⎋</span></a>
  </div>
</div>
""",
        unsafe_allow_html=True,
    )
