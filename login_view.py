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

    /* Container Centralizado */
    .wrap { 
        max-width: 480px; 
        margin: auto; 
        padding-top: 40px; 
        padding-bottom: 60px;
    }

    /* Logo Centralizada */
    .brand {
        display:flex;
        align-items:center;
        justify-content: center; /* Centraliza horizontalmente */
        gap:16px;
        margin-bottom: 24px;
    }

    .logoSpin img {
        width:58px;
        animation: spin 12s linear infinite;
    }

    @keyframes spin { to { transform: rotate(360deg); } }

    .logoText img {
        height: 42px;
    }

    .subtitle {
        text-align: center; /* Texto centralizado */
        margin-bottom: 20px;
        font-weight:700;
        color:#64748B;
        font-size:15px;
    }

    /* Cartão de Login */
    .card {
        background:white;
        border-radius:20px;
        border:1px solid #E2E8F0;
        padding: 30px;
        box-shadow: 0 10px 40px rgba(15,23,42,.06);
    }

    .card-h {
        font-weight:900;
        font-size:18px;
        color:#062B61;
        margin-bottom: 20px;
        text-align: center;
    }

    /* Termo de Confidencialidade (Caixa de Rolagem) */
    .termo-box {
        background-color: #F8FAFC; 
        padding: 15px; 
        border-radius: 10px;
        height: 120px; 
        overflow-y: auto; 
        font-size: 13px;
        border: 1px solid #E2E8F0; 
        margin: 15px 0;
        text-align: justify; 
        color: #475569;
        line-height: 1.5;
    }

    .err {
        margin-top:12px;
        padding:12px;
        border-radius:14px;
        background:#FEE2E2;
        border:1px solid #FCA5A5;
        color:#7F1D1D;
        font-weight:900;
        text-align: center;
    }
    
    /* Ajuste inputs */
    div[data-testid="stTextInput"] input {
        border-radius: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# ==============================================================================
# Render
# ==============================================================================
def render_login():
    hide_streamlit()
    inject_css()

    # Container Principal Centralizado
    st.markdown('<div class="wrap">', unsafe_allow_html=True)

    # 1. Logo Centralizada
    st.markdown(f"""
    <div class="brand">
        <div class="logoSpin"><img src="data:image/png;base64,{ICON}"></div>
        <div class="logoText"><img src="data:image/png;base64,{TEXT}"></div>
    </div>
    <div class="subtitle">Identifique-se para acessar seu workspace</div>
    """, unsafe_allow_html=True)

    # 2. Cartão de Login
    st.markdown('<div class="card">', unsafe_allow_html=True)
    
    # Inputs
    nome = st.text_input("Seu nome")
    cargo = st.text_input("Sua função")
    pin = st.text_input("PIN do Workspace", type="password")

    # 3. Termo de Confidencialidade (Caixa Restaurada)
    st.markdown("""
    <div class="termo-box">
        <strong>1. Confidencialidade:</strong> O usuário compromete-se a não inserir dados reais sensíveis (nomes completos, documentos) que identifiquem estudantes, exceto em ambiente seguro autorizado pela instituição.<br><br>
        <strong>2. Natureza Beta:</strong> O sistema está em evolução constante. Algumas funcionalidades podem sofrer alterações.<br><br>
        <strong>3. Responsabilidade:</strong> As sugestões geradas pela IA servem como apoio pedagógico e devem ser sempre validadas por um profissional humano qualificado.<br><br>
        <strong>4. Acesso:</strong> O PIN de acesso é pessoal e intransferível dentro da organização.
    </div>
    """, unsafe_allow_html=True)

    aceitar = st.checkbox("Li e aceito o Termo de Confidencialidade")

    st.markdown("<div style='height:15px'></div>", unsafe_allow_html=True)

    if st.button("Validar e entrar", use_container_width=True, type="primary"):
        if not (nome and cargo and aceitar and pin):
            st.markdown("<div class='err'>Preencha todos os campos e aceite o termo.</div>", unsafe_allow_html=True)
            st.stop()

        pin = pin.strip().upper()
        if len(pin) == 8 and "-" not in pin:
            pin = pin[:4] + "-" + pin[4:]

        # Validação via RPC
        ws = rpc_workspace_from_pin(pin)
        
        if not ws:
            st.markdown("<div class='err'>PIN inválido ou workspace não encontrado.</div>", unsafe_allow_html=True)
        else:
            # Sucesso
            st.session_state.usuario_nome = nome
            st.session_state.usuario_cargo = cargo
            st.session_state.autenticado = True
            st.session_state.workspace_id = ws["id"]
            st.session_state.workspace_name = ws["name"]
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True) # Fim Card
    
    # Info técnica discreta
    st.markdown(f"""
    <div style="text-align:center; margin-top:20px; color:#94A3B8; font-size:12px;">
        RPC: <code>{RPC_NAME}</code>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True) # Fim Wrap
