# login_view.py
import os
import base64
from datetime import datetime
import streamlit as st

# ✅ IMPORTS SUPABASE (somente o que existe com certeza no seu supabase_client.py)
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
    # Se ENV="TESTE" no secrets, NÃO esconde o menu (pra debugar)
    if _env() == "TESTE":
        return

    st.markdown(
        """
        <style>
            /* Esconde todos os menus e controles do Streamlit */
            #MainMenu { visibility: hidden !important; }
            footer { visibility: hidden !important; }
            header[data-testid="stHeader"] { display: none !important; }
            [data-testid="stToolbar"] { visibility: hidden !important; }
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
# CSS GLOBAL (Nunito)
# ==============================================================================
def inject_css():
    st.markdown(
        """
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
            padding-top: 30px;
            padding-bottom: 40px;
        }
        
        /* Remove espaço extra do Streamlit */
        .block-container {
            padding-top: 1rem !important;
            max-width: 480px !important;
            margin: 0 auto !important;
        }
        
        /* Centraliza e limita largura dos inputs */
        .element-container {
            max-width: 100% !important;
        }

        /* Logo Centralizada (Ícone EM CIMA do Texto) */
        .brand {
            display:flex;
            flex-direction: column;
            align-items:center;
            justify-content: center;
            gap: 12px;
            margin-bottom: 24px;
        }

        .logoSpin img {
            width: 70px;
            animation: spin 12s linear infinite;
        }

        @keyframes spin { to { transform: rotate(360deg); } }

        .logoText img {
            height: 38px;
        }

        .subtitle {
            text-align: center;
            margin-bottom: 20px;
            font-weight: 700;
            color: #64748B;
            font-size: 15px;
        }

        /* Cartão de Login */
        .card {
            background: white;
            border-radius: 20px;
            border: 1px solid #E2E8F0;
            padding: 28px;
            box-shadow: 0 10px 40px rgba(15,23,42,.06);
        }

        /* Inputs Elegantes */
        div[data-testid="stTextInput"] {
            max-width: 100% !important;
        }
        div[data-testid="stTextInput"] input {
            border-radius: 12px;
            border: 1px solid #CBD5E1;
            background-color: #F8FAFC;
            color: #334155;
            padding: 10px 12px;
            width: 100%;
        }
        div[data-testid="stTextInput"] input:focus {
            border-color: #94A3B8;
            background-color: #FFFFFF;
            box-shadow: 0 0 0 2px rgba(148, 163, 184, 0.2);
        }

        /* Termo de Confidencialidade */
        .termo-box {
            background-color: #F8FAFC;
            padding: 15px;
            border-radius: 12px;
            height: 120px;
            overflow-y: auto;
            font-size: 13px;
            border: 1px solid #E2E8F0;
            margin: 20px 0 15px 0;
            text-align: justify;
            color: #475569;
            line-height: 1.5;
        }

        .err {
            margin-top: 12px;
            padding: 12px;
            border-radius: 14px;
            background: #FEE2E2;
            border: 1px solid #FCA5A5;
            color: #7F1D1D;
            font-weight: 900;
            text-align: center;
        }

        .warn {
            margin-top: 12px;
            padding: 12px;
            border-radius: 14px;
            background: #FEF3C7;
            border: 1px solid #FDE68A;
            color: #92400E;
            font-weight: 900;
            text-align: center;
        }

        /* Botão - Cor padrão (azul marinho) */
        div[data-testid="stButton"] button {
            width: 100%;
            border-radius: 12px;
            font-weight: 800;
            padding: 0.5rem 1rem;
            background: linear-gradient(135deg, #1E3A8A, #1E40AF) !important;
            border: none !important;
            color: #ffffff !important;
        }
        div[data-testid="stButton"] button:hover {
            background: linear-gradient(135deg, #1E40AF, #1E3A8A) !important;
            transform: translateY(-1px);
            box-shadow: 0 10px 22px rgba(30, 58, 138, 0.3) !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )


# ==============================================================================
# Supabase client opcional (não quebra login)
# ==============================================================================
def _try_init_supabase_client_into_session():
    """
    Tenta criar st.session_state['sb'] usando supabase_client.get_supabase(),
    mas NÃO derruba o login se falhar (pois seu app pode estar usando REST).
    """
    try:
        from supabase_client import get_supabase  # existe no seu supabase_client.py
        sb = get_supabase()
        st.session_state["sb"] = sb
        return True, None
    except Exception as e:
        # não bloqueia o login: apenas não cria 'sb'
        st.session_state.pop("sb", None)
        return False, str(e)


# ==============================================================================
# Render
# ==============================================================================
def render_login():
    hide_streamlit()
    inject_css()

    # Container Principal
    st.markdown('<div class="wrap">', unsafe_allow_html=True)

    # 1. Logo Centralizada (Ícone acima do Texto)
    st.markdown(
        f"""
        <div class="brand">
            <div class="logoSpin"><img src="data:image/png;base64,{ICON}"></div>
            <div class="logoText"><img src="data:image/png;base64,{TEXT}"></div>
        </div>
        <div class="subtitle">Identifique-se para acessar seu workspace</div>
        """,
        unsafe_allow_html=True
    )

    # 2. Cartão de Login
    st.markdown('<div class="card">', unsafe_allow_html=True)

    # Inputs
    nome = st.text_input("Seu nome", placeholder="Nome completo")
    cargo = st.text_input("Sua função", placeholder="Ex: Professor, Coordenador")
    pin = st.text_input("PIN do Workspace", type="password", placeholder="****")

    # 3. Termo de Confidencialidade
    st.markdown(
        """
        <div class="termo-box">
            <strong>1. Confidencialidade:</strong> O usuário compromete-se a não inserir dados reais sensíveis (nomes completos, documentos) que identifiquem estudantes, exceto em ambiente seguro autorizado pela instituição.<br><br>
            <strong>2. Natureza Beta:</strong> O sistema está em evolução constante. Algumas funcionalidades podem sofrer alterações.<br><br>
            <strong>3. Responsabilidade:</strong> As sugestões geradas pela IA servem como apoio pedagógico e devem ser sempre validadas por um profissional humano qualificado.<br><br>
            <strong>4. Acesso:</strong> O PIN de acesso é pessoal e intransferível dentro da organização.
        </div>
        """,
        unsafe_allow_html=True
    )

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
            # ✅ Sucesso (estado mínimo)
            st.session_state.usuario_nome = nome
            st.session_state.usuario_cargo = cargo
            st.session_state.autenticado = True

            # ws pode vir com chaves diferentes dependendo da sua RPC
            st.session_state.workspace_id = ws.get("id") or ws.get("workspace_id")
            st.session_state.workspace_name = ws.get("name") or ws.get("workspace_name") or ""

            # ✅ opcional: tenta criar sb na sessão (sem quebrar o login)
            ok_sb, err_sb = _try_init_supabase_client_into_session()
            if (not ok_sb) and (_env() == "TESTE"):
                # Em TESTE, mostro um aviso técnico leve (pra você depurar)
                st.markdown(
                    f"<div class='warn'>Aviso (TESTE): não consegui iniciar supabase-py em st.session_state['sb'].<br>{err_sb}</div>",
                    unsafe_allow_html=True
                )

            st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)  # Fim Card

    # Info técnica discreta
    st.markdown(
        f"""
        <div style="text-align:center; margin-top:20px; color:#CBD5E1; font-size:11px; font-weight:500;">
            SECURE LOGIN • RPC: {RPC_NAME}
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("</div>", unsafe_allow_html=True)  # Fim Wrap
