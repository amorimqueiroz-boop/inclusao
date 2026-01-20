# ui_nav.py
import streamlit as st
import os, base64

def render_omnisfera_nav():
    ROUTES = {
        "home":   "Home.py",
        "pei":    "pages/1_PEI.py",
        "paee":   "pages/2_PAE.py",
        "hub":    "pages/3_Hub_Inclusao.py",
        "diario": "pages/4_Diario_de_Bordo.py",
        "mon":    "pages/5_Monitoramento_Avaliacao.py",
    }

    # Navegação (?go=)
    qp = st.query_params
    if "go" in qp:
        dest = qp["go"]
        if dest in ROUTES:
            st.query_params.clear()
            st.switch_page(ROUTES[dest])

    # Logo base64
    def logo_src():
        for f in ["omni_icone.png", "logo.png", "iconeaba.png", "omni.png", "ominisfera.png"]:
            if os.path.exists(f):
                with open(f, "rb") as img:
                    return f"data:image/png;base64,{base64.b64encode(img.read()).decode()}"
        return "https://cdn-icons-png.flaticon.com/512/1183/1183672.png"

    src = logo_src()

    # Posição por cima do header do Streamlit
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

  gap: 10px;              /* ↓ era 12 */
  padding: 8px 12px;      /* ↓ era 10px 14px */
  border-radius: 999px;

  background: #FFFFFF !important;
  border: 1px solid #E5E7EB !important;
  box-shadow: 0 10px 28px rgba(15, 23, 42, 0.12) !important;

  opacity: 1 !important;
  isolation: isolate !important;
  pointer-events: auto !important;
}}

/* Logo */
@keyframes spin {{
  from {{ transform: rotate(0deg); }}
  to {{ transform: rotate(360deg); }}
}}
.omni-logo {{
  width: 26px;            /* ↓ era 28 */
  height: 26px;           /* ↓ era 28 */
  animation: spin 10s linear infinite;
}}

/* Separador */
.omni-sep {{
  width: 1px;
  height: 22px;           /* ↓ era 26 */
  background: #E5E7EB;
  margin: 0 2px;
}}

/* Botões circulares coloridos (ícone branco) */
.omni-ico {{
  width: 34px;            /* ↓ era 38 */
  height: 34px;           /* ↓ era 38 */
  border-radius: 999px;

  display: inline-flex;
  align-items: center;
  justify-content: center;

  text-decoration: none !important;

  /* borda sutil para manter o “dock premium” */
  border: 1px solid rgba(17,24,39,0.06) !important;
  box-shadow: 0 2px 10px rgba(15, 23, 42, 0.06);
  transition: transform .12s ease, box-shadow .12s ease, filter .12s ease;
}}

.omni-ico:hover {{
  transform: translateY(-1px);
  box-shadow: 0 10px 22px rgba(15, 23, 42, 0.10);
  filter: brightness(1.02);
}}

.omni-ic {{
  font-size: 18px;        /* ↓ era 20 */
  line-height: 1;
  color: #FFFFFF !important;  /* ícone branco */
}}

/* Acessibilidade: foco ao navegar com teclado */
.omni-ico:focus {{
  outline: 3px solid rgba(59,130,246,0.25);
  outline-offset: 2px;
}}
</style>

<div class="omni-dock" aria-label="Omnisfera Dock">
  <img src="{src}" class="omni-logo" alt="Omnisfera" />
  <div class="omni-sep"></div>

  <!-- target=_self garante abrir na mesma aba -->
  <a class="omni-ico" href="?go=home"   target="_self" title="Home" style="background:#111827">
    <i class="ri-home-5-line omni-ic"></i>
  </a>

  <a class="omni-ico" href="?go=pei"    target="_self" title="Estratégias & PEI" style="background:#3B82F6">
    <i class="ri-puzzle-2-line omni-ic"></i>
  </a>

  <a class="omni-ico" href="?go=paee"   target="_self" title="Plano de Ação (PAEE)" style="background:#22C55E">
    <i class="ri-map-pin-2-line omni-ic"></i>
  </a>

  <a class="omni-ico" href="?go=hub"    target="_self" title="Hub de Recursos" style="background:#F59E0B">
    <i class="ri-lightbulb-line omni-ic"></i>
  </a>

  <a class="omni-ico" href="?go=diario" target="_self" title="Diário de Bordo" style="background:#F97316">
    <i class="ri-compass-3-line omni-ic"></i>
  </a>

  <a class="omni-ico" href="?go=mon"    target="_self" title="Evolução & Acompanhamento" style="background:#A855F7">
    <i class="ri-line-chart-line omni-ic"></i>
  </a>
</div>
""", unsafe_allow_html=True)
