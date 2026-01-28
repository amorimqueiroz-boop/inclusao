# login_view.py
import os
import base64
from datetime import datetime
import streamlit as st

# ✅ IMPORTS SUPABASE
from supabase_client import rpc_workspace_from_pin, RPC_NAME


# ==============================================================================
# Ambiente / Chrome
# ==============================================================================
def _env():
    try:
        return str(st.secrets.get("ENV", "")).upper()
    except Exception:
        return ""


def hide_streamlit():
    if _env() == "TESTE":
        return

    st.markdown(
        """
        <style>
            #MainMenu { visibility: hidden !important; }
            footer { visibility: hidden !important; }
            header[data-testid="stHeader"] { display: none !important; }
            [data-testid="stToolbar"] { visibility: hidden !important; }
            [data-testid="stDecoration"] { display: none !important; }
            [data-testid="stStatusWidget"] { display: none !important; }
            [data-testid="stDeployButton"] { display: none !important; }
            [data-testid="stSidebar"] { display: none !important; }
            section[data-testid="stSidebar"] { display: none !important; }
            [data-testid="stSidebarNav"] { display: none !important; }
            button[data-testid="collapsedControl"] { display: none !important; }
        </style>
        """,
        unsafe_allow_html=True
    )


# ==============================================================================
# Assets
# ==============================================================================
def b64(path: str) -> str:
    if path and os.path.exists(path):
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return ""


ICON = next((b64(f) for f in ["omni_icone.png", "omni.png", "logo.png"] if b64(f)), "")
TEXT = b64("omni_texto.png")


# ==============================================================================
# CSS GLOBAL (Vertical e Centralizado)
# ==============================================================================
def inject_css():
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800;900&display=swap');

        html, body, [class*="css"] {
            font-family: 'Nunito', sans-serif;
            background: #F7FAFC; /* Fundo cinza bem claro */
            color: #0f172a;
        }

        /* Container Principal: Flexbox Vertical Centralizado */
        .wrap {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            min-height: 100vh;
            padding: 20px;
            width: 100%;
        }
        
        /* Remove padding padrão do Streamlit */
        .block-container {
            padding: 0 !important;
            max-width: 100% !important;
            margin: 0 !important;
        }
        
        /* Branding no Topo */
        .brand {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            margin-bottom: 30px; /* Espaço entre logo e card */
        }

        .logoSpin img {
            width: 100px; /* Tamanho MENOR conforme pedido */
            animation: spin 15s linear infinite;
        }

        @keyframes spin { to { transform: rotate(360deg); } }

        .logoText img {
            height: 50px; /* Texto menor também para equilibrar */
            margin-top: 15px;
        }

        /* Cartão de Login */
        .card {
            background: white;
            border-radius: 16px;
            border: 1px solid #E2E8F0;
            padding: 35px;
            box-shadow: 0 10px 30px rgba(15,23,42,.06);
            width: 100%;
            max-width: 400px; /* Largura contida */
        }

        /* Título de Boas Vindas dentro do Card */
        .card-header {
            text-align: center;
            margin-bottom: 25px;
            color: #334155;
            font-size: 15px;
            font-weight: 600;
        }

        /* Inputs */
        div[data-testid="stTextInput"] {
            margin-bottom: 12px;
        }
        div[data-testid="stTextInput"] input {
            border-radius: 10px;
            border: 1px solid #CBD5E1;
            background-color: #F8FAFC;
            color: #334155;
            padding: 10px 12px;
            font-size: 14px;
        }
        div[data-testid="stTextInput"] input:focus {
            border-color: #94A3B8;
            background-color: #FFFFFF;
            box-shadow: 0 0 0 2px rgba(148, 163, 184, 0.2);
        }

        /* Termo de Confidencialidade */
        .termo-box {
            background-color: #F8FAFC;
            padding: 12px;
            border-radius: 10px;
            height: 100px;
            overflow-y: auto;
            font-size: 12px;
            border: 1px solid #E2E8F0;
            margin: 15px 0 15px 0;
            text-align: justify;
            color: #64748B;
            line-height: 1.4;
        }

        /* Mensagens */
        .err {
            margin-top: 15px;
            padding: 10px;
            border-radius: 8px;
            background: #FEE2E2;
            border: 1px solid #FCA5A5;
            color: #991B1B;
            font-weight: 700;
            font-size: 13px;
            text-align: center;
        }

        .warn {
            margin-top: 15px;
            padding: 10px;
            border-radius: 8px;
            background: #FEF3C7;
            border: 1px solid #FDE68A;
            color: #92400E;
            font-weight: 700;
            font-size: 13px;
            text-align: center;
        }

        /* Botão */
        div[data-testid="stButton"] button {
            width: 100%;
            border-radius: 10px;
            font-weight: 800;
            padding: 0.6rem 1rem;
            background: linear-gradient(135deg, #1E3A8A, #1E40AF) !important;
            border: none !important;
            color: #ffffff !important;
            font-size: 15px;
            margin-top: 10px;
        }
        div[data-testid="stButton"] button:hover {
            background: linear-gradient(135deg, #1E40AF, #1E3A8A) !important;
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(30, 58, 138, 0.25) !important;
        }
        
        label[data-testid="stCheckbox"] {
            font-size: 13px;
            color: #475569;
        }
        </style>
        """,
        unsafe_allow_html=True
    )


# ==============================================================================
# Supabase client opcional (não quebra login)
# ==============================================================================
def _try_init_supabase_client_into_session():
    try:
        from supabase_client import get_supabase
        sb = get_supabase()
        st.session_state["sb"] = sb
        return True, None
    except Exception as e:
        st.session_state.pop("sb", None)
        return False, str(e)


# ==============================================================================
# Render
# ==============================================================================
def render_login():
    hide_streamlit()
    inject_css()

    # Início do Container Centralizado
    st.markdown('<div class="wrap">', unsafe_allow_html=True)
    
    # 1. Branding (Logo Girando + Texto) - No Topo
    st.markdown(
        f"""
        <div class="brand">
            <div class="logoSpin"><img src="data:image/png;base64,{ICON}"></div>
            <div class="logoText"><img src="data:image/png;base64,{TEXT}"></div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # 2. Card de Login - Embaixo
    st.markdown('<div class="card">', unsafe_allow_html=True)
    
    # Mensagem de Boas Vindas dentro do card
    st.markdown(
        """
        <div class="card-header">
            Bem-vindo(a) à Omnisfera.<br>
            Faça login para continuar.
        </div>
        """, 
        unsafe_allow_html=True
    )

    # Inputs
    nome = st.text_input("Seu nome", placeholder="Nome completo")
    cargo = st.text_input("Sua função", placeholder="Ex: Professor, Coordenador")
    pin = st.text_input("PIN da Escola", type="password", placeholder="****")

    # Termo
    st.markdown(
        """
        <div class="termo-box">
            <strong>1. Confidencialidade:</strong> O usuário compromete-se a não inserir dados reais sensíveis (nomes completos, documentos) que identifiquem estudantes, exceto em ambiente seguro autorizado pela instituição.<br><br>
            <strong>2. Natureza Beta:</strong> O sistema está em evolução constante.<br><br>
            <strong>3. Responsabilidade:</strong> As sugestões geradas pela IA servem como apoio pedagógico e devem ser validadas.<br><br>
            <strong>4. Acesso:</strong> O PIN é pessoal e intransferível.
        </div>
        """,
        unsafe_allow_html=True
    )

    aceitar = st.checkbox("Li e aceito o Termo de Confidencialidade")
    
    if st.button("ENTRAR", use_container_width=True, type="primary"):
        if not (nome and cargo and aceitar and pin):
            st.markdown("<div class='err'>Preencha todos os campos e aceite o termo.</div>", unsafe_allow_html=True)
            st.stop()

        pin = pin.strip().upper()
        if len(pin) == 8 and "-" not in pin:
            pin = pin[:4] + "-" + pin[4:]

        # Validação via RPC
        ws = rpc_workspace_from_pin(pin)

        if not ws:
            st.markdown("<div class='err'>PIN inválido ou escola não encontrada.</div>", unsafe_allow_html=True)
        else:
            # Sucesso
            st.session_state.usuario_nome = nome
            st.session_state.usuario_cargo = cargo
            st.session_state.autenticado = True

            st.session_state.workspace_id = ws.get("id") or ws.get("workspace_id")
            st.session_state.workspace_name = ws.get("name") or ws.get("workspace_name") or ""

            ok_sb, err_sb = _try_init_supabase_client_into_session()
            if (not ok_sb) and (_env() == "TESTE"):
                st.markdown(f"<div class='warn'>Aviso (TESTE): erro no supabase client.<br>{err_sb}</div>", unsafe_allow_html=True)

            st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)  # Fim Card

    # Info técnica rodapé
    st.markdown(
        f"""
        <div style="text-align:center; margin-top:25px; color:#CBD5E1; font-size:10px; font-weight:500;">
            SECURE LOGIN • RPC: {RPC_NAME}
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("</div>", unsafe_allow_html=True)  # Fim Wrap
