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
    # se existir depois, você adiciona:
    # "diario": "pages/4_Diario_de_Bordo.py",
    # "dados":  "pages/5_Monitoramento_Avaliacao.py",
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
    "diario": "#F97316",
    "dados":  "#8B5CF6",
}

# =========================
# FLATICON (UMA SÓ FAMÍLIA: SOLID ROUNDED)
# =========================
FLATICON_CSS = """
<link rel="stylesheet" href="https://cdn-uicons.flaticon.com/3.0.0/uicons-solid-rounded/css/uicons-solid-rounded.css">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@600;800;900&display=swap" rel="stylesheet">
"""

# ÍCONES — todos "fi-sr-*" (mesma biblioteca = não quebra)
# (se algum não aparecer, trocamos por outro da mesma família rapidinho)
ICONS = {
    "home":   "fi fi-sr-home",
    "alunos": "fi fi-sr-users",
    "pei":    "fi fi-sr-puzzle-alt",
    "paee":   "fi fi-sr-route",
    "hub":    "fi fi-sr-lightbulb-on",
    "diario": "fi fi-sr-book-alt",
    "dados":  "fi fi-sr-chart-line-up",
    "sair":   "fi fi-sr-exit",
}

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

def _js_fix_top():
    components.html(
        """
<script>
(function(){
  function run(){
    try{
      document.documentElement.style.margin='0';
      document.documentElement.style.padding='0';
      document.body.style.margin='0';
      document.body.style.padding='0';

      const vc = document.querySelector('div[data-testid="stAppViewContainer"]');
      if(vc){ vc.style.paddingTop='0'; vc.style.marginTop='0'; }

      const main = document.querySelector('div[data-testid="stAppViewContainer"] > section.main');
      if(main){ main.style.paddingTop='0'; main.style.marginTop='0'; }
    }catch(e){}
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
# TOPBAR — APENAS ÍCONES
# =========================
def render_topbar_nav(active: str):
    _nav_if_requested()

    logo_b64 = _b64("omni_icone.png")
    logo_html = (
        f"<img class='omni-logo' src='data:image/png;base64,{logo_b64}' alt='Omnisfera'/>"
        if logo_b64 else "<div class='omni-logo omni-logo-fallback'></div>"
    )

    items = [
        ("home", "Home"),
        ("alunos", "Alunos"),
        ("pei", "Estratégias & PEI"),
        ("paee", "Plano de Ação"),
        ("hub", "Hub"),
        ("diario", "Diário"),
        ("dados", "Dados"),
    ]

    links = ""
    for key, label in items:
        if key not in PAGES:
            continue
        icon = ICONS.get(key, "fi fi-sr-circle")
        color = COLORS.get(key, "#111827")
        is_active = "active" if key == active else ""
        links += f"""
<a class="omni-ico-link {is_active}" href="?go={key}" aria-label="{label}" title="{label}">
  <i class="{icon}" style="color:{color};"></i>
  <span class="omni-tip">{label}</span>
</a>
"""

    st.markdown(
        f"""
{FLATICON_CSS}
<style>
html, body {{ margin:0!important; padding:0!important; }}
header[data-testid="stHeader"]{{display:none!important;height:0!important;}}
[data-testid="stToolbar"]{{display:none!important;}}
[data-testid="stSidebar"], [data-testid="stSidebarNav"]{{display:none!important;}}
div[data-testid="stAppViewContainer"]{{padding-top:0!important;margin-top:0!important;}}
div[data-testid="stAppViewContainer"] > section.main{{padding-top:0!important;margin-top:0!important;}}
.block-container{{padding-top:72px!important;}}

@keyframes spin{{from{{transform:rotate(0deg);}}to{{transform:rotate(360deg);}}}}

.omni-topbar{{
  position:fixed; top:0; left:0; right:0;
  height:64px;
  display:flex; align-items:center; justify-content:space-between;
  padding:0 22px;
  background:rgba(255,255,255,0.96);
  backdrop-filter:blur(14px);
  -webkit-backdrop-filter:blur(14px);
  border-bottom:1px solid rgba(226,232,240,0.95);
  box-shadow:0 8px 20px rgba(15,23,42,0.06);
  z-index:999999;
  font-family:Inter,system-ui,-apple-system,Segoe UI,Roboto,Arial;
}}

.omni-left{{display:flex; align-items:center; gap:12px;}}
.omni-logo{{
  width:32px; height:32px; border-radius:999px;
  animation:spin 45s linear infinite;
}}
.omni-logo-fallback{{
  background:conic-gradient(from 0deg,#3B82F6,#22C55E,#F59E0B,#F97316,#A855F7,#3B82F6);
}}
.omni-title{{
  font-weight:900; letter-spacing:.14em; text-transform:uppercase;
  font-size:.78rem; color:#0F172A;
}}

.omni-right{{display:flex; align-items:center; gap:14px;}}

.omni-ico-link{{
  width:44px; height:44px;
  display:flex; align-items:center; justify-content:center;
  border-radius:14px;
  text-decoration:none;
  opacity:.75;
  transition:transform .14s ease, opacity .14s ease, background .14s ease;
  position:relative;
}}
.omni-ico-link:hover{{opacity:1; transform:translateY(-1px); background:rgba(15,23,42,0.04);}}

.omni-ico-link i{{font-size:22px; line-height:1;}}

/* Ativo: bem discreto */
.omni-ico-link.active{{opacity:1; background:rgba(15,23,42,0.06);}}
.omni-ico-link.active::after{{
  content:"";
  position:absolute;
  bottom:6px;
  width:16px; height:2px;
  border-radius:999px;
  background:rgba(15,23,42,0.22);
}}

/* Tooltip (aparece no hover) */
.omni-tip{{
  position:absolute;
  top:52px;
  padding:6px 10px;
  background:rgba(15,23,42,0.92);
  color:#fff;
  font-size:12px;
  font-weight:700;
  border-radius:10px;
  white-space:nowrap;
  opacity:0;
  transform:translateY(-4px);
  pointer-events:none;
  transition:opacity .12s ease, transform .12s ease;
}}
.omni-ico-link:hover .omni-tip{{opacity:1; transform:translateY(0);}}

.omni-divider{{width:1px;height:22px;background:rgba(226,232,240,1); margin:0 2px;}}

@media (max-width: 860px){{
  .omni-title{{display:none;}}
}}
</style>

<div class="omni-topbar">
  <div class="omni-left">
    {logo_html}
    <div class="omni-title">OMNISFERA</div>
  </div>

  <div class="omni-right">
    {links}
    <div class="omni-divider"></div>
    <a class="omni-ico-link" href="?go=home" aria-label="Sair" title="Sair">
      <i class="{ICONS["sair"]}" style="color:rgba(15,23,42,0.55);"></i>
      <span class="omni-tip">Sair</span>
    </a>
  </div>
</div>
""",
        unsafe_allow_html=True,
    )

    _js_fix_top()
