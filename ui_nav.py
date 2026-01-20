# ui_nav.py
import streamlit as st
import streamlit.components.v1 as components
import os, base64

# =========================
# ROTAS DAS PÁGINAS
# =========================
PAGES = {
    "home":   "home_portal.py",
    "alunos": "pages/0_Alunos.py",
    "pei":    "pages/1_PEI.py",
    "paee":   "pages/2_PAE.py",
    "hub":    "pages/3_Hub_Inclusao.py",
}

# =========================
# CORES POR MÓDULO
# =========================
COLORS = {
    "home":   "#111827",
    "alunos": "#2563EB",
    "pei":    "#3B82F6",
    "paee":   "#10B981",
    "hub":    "#F59E0B",
}

# =========================
# ÍCONES (FLATICON)
# =========================
ICONS = {
    "home":   "fi fi-br-home",
    "alunos": "fi fi-br-users",
    "pei":    "fi fi-sr-puzzle-alt",
    "paee":   "fi fi-ss-route",
    "hub":    "fi fi-sr-lightbulb-on",
    "sair":   "fi fi-br-sign-out-alt",
}

FLATICON_CSS = """
<link rel="stylesheet" href="https://cdn-uicons.flaticon.com/3.0.0/uicons-bold-rounded/css/uicons-bold-rounded.css">
<link rel="stylesheet" href="https://cdn-uicons.flaticon.com/3.0.0/uicons-solid-rounded/css/uicons-solid-rounded.css">
<link rel="stylesheet" href="https://cdn-uicons.flaticon.com/3.0.0/uicons-solid-straight/css/uicons-solid-straight.css">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@500;700;800;900&display=swap" rel="stylesheet">
"""

# =========================
# UTIL
# =========================
def _b64(path: str) -> str:
    if not os.path.exists(path):
        return ""
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

def _get_qp(name: str):
    try:
        qp = st.query_params
        v = qp.get(name)
        if isinstance(v, list):
            return v[0] if v else None
        return v
    except Exception:
        return None

def _clear_qp():
    try:
        st.query_params.clear()
    except Exception:
        pass

def _nav_if_requested():
    go = _get_qp("go")
    if go and go in PAGES:
        _clear_qp()
        st.switch_page(PAGES[go])

# =========================
# JS – RESET TOTAL DO TOPO
# =========================
def _js_fix_top_and_cleanup():
    components.html(
        """
<script>
(function(){
  function hardResetTop(){
    try{
      document.documentElement.style.margin = '0';
      document.documentElement.style.padding = '0';
      document.body.style.margin = '0';
      document.body.style.padding = '0';

      const app = document.querySelector('.stApp');
      if(app){
        app.style.marginTop = '0';
        app.style.paddingTop = '0';
      }

      const vc = document.querySelector('div[data-testid="stAppViewContainer"]');
      if(vc){
        vc.style.paddingTop = '0';
        vc.style.marginTop = '0';
      }

      const main = document.querySelector('div[data-testid="stAppViewContainer"] > section.main');
      if(main){
        main.style.paddingTop = '0';
        main.style.marginTop = '0';
      }
    }catch(e){}
  }

  function cleanupLeaks(){
    try{
      const needles = ['<div class="omni-', '<i class="fi', '</a>', 'omni-underline', 'omni-label'];
      const blocks = document.querySelectorAll('[data-testid="stMarkdownContainer"], .stMarkdown, .element-container');
      blocks.forEach(b=>{
        b.querySelectorAll('p,div,span').forEach(n=>{
          const t = (n.innerText||'').trim();
          if(t.startsWith('<') && needles.some(x=>t.includes(x))) n.remove();
        });
      });
    }catch(e){}
  }

  function run(){
    hardResetTop();
    cleanupLeaks();
  }

  run();
  setTimeout(run, 50);
  setTimeout(run, 200);
  setTimeout(run, 600);
})();
</script>
""",
        height=0,
    )

# =========================
# RENDER DA TOPBAR
# =========================
def render_topbar_nav(active: str):
    _nav_if_requested()

    logo_b64 = _b64("omni_icone.png")
    logo_html = (
        f"<img class='omni-logo' src='data:image/png;base64,{logo_b64}' />"
        if logo_b64 else "<div class='omni-logo omni-logo-fallback'></div>"
    )

    items = [
        ("home", "Home"),
        ("alunos", "Alunos"),
        ("pei", "Estratégias & PEI"),
        ("paee", "Plano de Ação"),
        ("hub", "Hub"),
    ]

    links = ""
    for key, label in items:
        is_active = "active" if key == active else ""
        color = COLORS.get(key, "#111827")
        icon = ICONS.get(key, "fi fi-br-circle")

        links += f"""
<a class="omni-link {is_active}" href="?go={key}">
  <i class="{icon}" style="color:{color};"></i>
  <span>{label}</span>
  <div class="omni-underline"></div>
</a>
"""

    st.markdown(
        f"""
{FLATICON_CSS}
<style>

/* RESET STREAMLIT */
html, body {{ margin:0!important; padding:0!important; }}
header[data-testid="stHeader"]{{display:none!important;height:0!important;}}
[data-testid="stToolbar"]{{display:none!important;}}
[data-testid="stSidebar"], [data-testid="stSidebarNav"]{{display:none!important;}}

div[data-testid="stAppViewContainer"]{{padding-top:0!important;margin-top:0!important;}}
div[data-testid="stAppViewContainer"] > section.main{{padding-top:0!important;margin-top:0!important;}}

.block-container{{padding-top:72px!important;}}

/* TOPBAR */
.omni-topbar{{
  position:fixed; top:0; left:0; right:0;
  height:64px;
  display:flex; align-items:center; justify-content:space-between;
  padding:0 28px;
  background:rgba(255,255,255,0.96);
  backdrop-filter:blur(14px);
  border-bottom:1px solid #E5E7EB;
  z-index:999999;
}}

.omni-left{{display:flex; align-items:center; gap:12px;}}
.omni-logo{{width:32px; height:32px; border-radius:50%; animation:spin 40s linear infinite;}}
.omni-title{{font-weight:900; letter-spacing:.12em; font-size:.8rem;}}

.omni-right{{display:flex; align-items:flex-end; gap:20px;}}

.omni-link{{text-decoration:none; display:flex; flex-direction:column; align-items:center; gap:4px; opacity:.7;}}
.omni-link:hover{{opacity:1; transform:translateY(-1px);}}
.omni-link span{{font-size:11px; font-weight:700; color:#475569;}}
.omni-link.active span{{color:#0F172A; font-weight:800;}}

.omni-underline{{width:16px;height:2px;border-radius:999px;background:transparent;}}
.omni-link.active .omni-underline{{background:#CBD5E1;}}

@keyframes spin{{from{{transform:rotate(0deg);}}to{{transform:rotate(360deg);}}}}

</style>

<div class="omni-topbar">
  <div class="omni-left">
    {logo_html}
    <div class="omni-title">OMNISFERA</div>
  </div>
  <div class="omni-right">
    {links}
  </div>
</div>
""",
        unsafe_allow_html=True,
    )

    _js_fix_top_and_cleanup()
