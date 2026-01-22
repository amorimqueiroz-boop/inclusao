# login_view.py
import os
import base64
from datetime import datetime
import streamlit as st
from supabase_client import rpc_workspace_from_pin, RPC_NAME

# ==============================================================================
# Ambiente / Chrome
# ==============================================================================
def _env():
    try:
        return str(st.secrets.get("ENV", "")).upper()
    except:
        return ""

def hide_streamlit():
    if _env() == "TESTE":
        return
    st.markdown("""
    <style>
        #MainMenu, footer, header { visibility: hidden; }
        [data-testid="stToolbar"] { visibility: hidden; }
        .block-container { padding-top: 1.2rem; }
    </style>
    """, unsafe_allow_html=True)

# ==============================================================================
# Assets
# ==============================================================================
def b64(path):
    if path and os.path.exists(path):
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return ""

ICON = next((b64(f) for f in ["omni_icone.png","omni.png","logo.png"] if b64(f)), "")
TEXT = b64("omni_texto.png")

# ==============================================================================
# CSS GLOBAL (Nunito)
# ==============================================================================
def inject_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800;900&display=swap');

    html, body, [class*="css"] {
        font-family: 'Nunito', sans-serif;
        background: #F7FAFC;
        color: #0f172a;
    }

    .wrap { max-width: 1080px; margin: auto; padding: 22px 18px 64px; }

    .top-chip {
        display:inline-block;
        padding:6px 12px;
        border-radius:999px;
        font-size:13px;
        font-weight:800;
        color:#475569;
        background:#EDF2F7;
        border:1px solid #E2E8F0;
    }

    .brand {
        display:flex;
        align-items:center;
        gap:16px;
        margin-top:18px;
    }

    .logoSpin img {
        width:58px;
        animation: spin 12s linear infinite;
    }

    @keyframes spin { to { transform: rotate(360deg); } }

    .logoText img {
        height:42px;
    }

    .subtitle {
        margin-top:12px;
        font-weight:700;
        color:#64748B;
        font-size:16px;
    }

    .grid {
        display:grid;
        grid-template-columns: 1.1fr .9fr;
        gap:14px;
        margin-top:18px;
    }

    @media(max-width:980px){
        .grid { grid-template-columns:1fr; }
    }

    .card {
        background:white;
        border-radius:20px;
        border:1px solid #E2E8F0;
        padding:16px;
        box-shadow:0 18px 40px rgba(15,23,42,.08);
    }

    .card-h {
        font-weight:900;
        font-size:15px;
        color:#062B61;
    }

    .manifesto {
        background: radial-gradient(circle at top right, #E6F0FF, #FFFFFF);
        border-radius:20px;
        padding:16px;
        border:1px solid #DBEAFE;
        box-shadow:0 18px 44px rgba(15,82,186,.12);
    }

    .manifesto p {
        font-weight:700;
        font-size:14px;
        line-height:1.4rem;
        color:#1E293B;
        margin:0;
    }

    .pill {
        display:inline-block;
        margin-top:10px;
        margin-right:6px;
        padding:6px 12px;
        border-radius:999px;
        background:#EDF2F7;
        border:1px solid #E2E8F0;
        font-weight:900;
        font-size:12px;
    }

    .err {
        margin-top:12px;
        padding:12px;
        border-radius:14px;
        background:#FEE2E2;
        border:1px solid #FCA5A5;
        color:#7F1D1D;
        font-weight:900;
    }
    </style>
    """, unsafe_allow_html=True)

# ==============================================================================
# Manifesto
# ==============================================================================
MANIFESTO_HTML = """
<div class="manifesto">
  <p>
    A <b>Omnisfera</b> foi desenvolvida com carinho e cuidado — como um sonho que virou ferramenta.
    Acreditamos que <b>a educação é, de fato, um direito de todos</b> e que a inclusão precisa ser o padrão,
    não a exceção. Aqui, tecnologia e inteligência pedagógica existem para reduzir barreiras,
    fortalecer o professor e ampliar possibilidades para cada estudante.
  </p>
  <div>
    <span class="pill">BNCC</span>
    <span class="pill">DUA</span>
    <span class="pill">LBI</span>
    <span class="pill">PEI/PAEE</span>
  </div>
</div>
"""

# ==============================================================================
# Render
# ==============================================================================
def render_login():
    hide_streamlit()
    inject_css()

    # ---------- TOPO (HTML PURO) ----------
    st.markdown(f"""
    <div class="wrap">
      <span class="top-chip">Acesso por PIN • Supabase Workspace</span>

      <div class="brand">
        <div class="logoSpin"><img src="data:image/png;base64,{ICON}"></div>
        <div class="logoText"><img src="data:image/png;base64,{TEXT}"></div>
      </div>

      <div class="subtitle">
        Identifique-se, aceite o termo e valide seu PIN para entrar no workspace.
      </div>

      <div class="grid">
        <div class="card">
          <div class="card-h">Identificação & Acesso</div>
          <div style="font-size:13px;color:#64748B;font-weight:800;">
            RPC: <code>{RPC_NAME}(p_pin text)</code>
          </div>
        </div>

        {MANIFESTO_HTML}
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ---------- FORMULÁRIO ----------
    st.markdown('<div class="wrap">', unsafe_allow_html=True)

    nome = st.text_input("Seu nome")
    cargo = st.text_input("Sua função")
    pin = st.text_input("PIN do Workspace")
    aceitar = st.checkbox("Li e aceito o Termo de Confidencialidade")

    if st.button("Validar e entrar", use_container_width=True):
        if not (nome and cargo and aceitar and pin):
            st.markdown("<div class='err'>Preencha todos os campos e aceite o termo.</div>", unsafe_allow_html=True)
            st.stop()

        pin = pin.strip().upper()
        if len(pin) == 8 and "-" not in pin:
            pin = pin[:4] + "-" + pin[4:]

        ws = rpc_workspace_from_pin(pin)
        if not ws:
            st.markdown("<div class='err'>PIN inválido.</div>", unsafe_allow_html=True)
        else:
            st.session_state.usuario_nome = nome
            st.session_state.usuario_cargo = cargo
            st.session_state.autenticado = True
            st.session_state.workspace_id = ws["id"]
            st.session_state.workspace_name = ws["name"]
            st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)
