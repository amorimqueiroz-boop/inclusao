# streamlit_app.py
import os
import streamlit as st
from login_view import render_login


def get_env() -> str:
    v = (os.environ.get("ENV") or "").strip()
    if v:
        return v.upper()
    try:
        v2 = st.secrets.get("ENV", None)
        return str(v2).strip().upper() if v2 else ""
    except Exception:
        return ""


ENV = get_env()

# Desabilita menu completamente se não estiver em TESTE
menu_items = {} if ENV != "TESTE" else None

st.set_page_config(
    page_title="Omnisfera | Ecossistema",
    page_icon="iconeaba.png" if os.path.exists("iconeaba.png") else "🌐",
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items=menu_items,
)

# Esconde chrome só fora do TESTE
if ENV != "TESTE":
    st.markdown(
        """
        <style>
          #MainMenu {visibility: hidden !important; display: none !important;}
          footer {visibility: hidden !important; display: none !important;}
          header {visibility: hidden !important; display: none !important;}
          [data-testid="stToolbar"] {visibility: hidden !important; display: none !important;}
          [data-testid="stDecoration"] {display: none !important; visibility: hidden !important;}
          [data-testid="stStatusWidget"] {display: none !important; visibility: hidden !important;}
          [data-testid="stDeployButton"] {display: none !important; visibility: hidden !important;}
          button[title="View app source"] {display: none !important; visibility: hidden !important;}
          button[title="Get help"] {display: none !important; visibility: hidden !important;}
          button[title="Report a bug"] {display: none !important; visibility: hidden !important;}
          button[title="Settings"] {display: none !important; visibility: hidden !important;}
          [data-testid="stHeader"] {display: none !important; visibility: hidden !important;}
          [data-testid="stToolbarActions"] {display: none !important; visibility: hidden !important;}
        </style>
        """,
        unsafe_allow_html=True,
    )


def acesso_bloqueado(msg: str):
    st.markdown(
        f"""
        <div style="
            max-width:520px;
            margin: 120px auto;
            padding: 28px;
            background: white;
            border-radius: 18px;
            border: 1px solid #E2E8F0;
            box-shadow: 0 20px 40px rgba(15,82,186,0.12);
            text-align: center;
        ">
            <div style="font-size:2.2rem; margin-bottom:10px;">🔐</div>
            <div style="font-weight:900; font-size:1.1rem; margin-bottom:6px; color:#0f172a;">
                Acesso restrito
            </div>
            <div style="color:#4A5568; font-weight:700; font-size:0.95rem; margin-bottom:18px;">
                {msg}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🔑 Voltar para o Login", use_container_width=True, type="primary"):
            # 1) limpa sessão
            for k in ["autenticado", "workspace_id", "workspace_name", "usuario_nome", "usuario_cargo", "sb", "sb_error"]:
                st.session_state.pop(k, None)

            # 2) tenta ir para o começo (streamlit_app.py)
            try:
                st.switch_page("streamlit_app.py")
            except Exception:
                # 3) fallback SUPER confiável: link para raiz
                st.markdown(
                    """
                    <div style="text-align:center; margin-top:12px;">
                      <a href="/" target="_self"
                         style="display:inline-block; padding:10px 14px; border-radius:12px;
                                background:#0F52BA; color:white; font-weight:900; text-decoration:none;">
                        Clique aqui para voltar ao Login
                      </a>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                st.stop()

    st.stop()


# ------------------------------------------------------------------------------
# Estado mínimo
# ------------------------------------------------------------------------------
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False
if "workspace_id" not in st.session_state:
    st.session_state.workspace_id = None
if "workspace_name" not in st.session_state:
    st.session_state.workspace_name = None

# Em ambiente de TESTE: pula o login e usa sessão fictícia (só local/teste)
if ENV == "TESTE":
    st.session_state.autenticado = True
    st.session_state.workspace_id = st.session_state.workspace_id or "ambiente-teste"
    st.session_state.workspace_name = st.session_state.workspace_name or "Ambiente de Teste"
    if "usuario_nome" not in st.session_state or not st.session_state.usuario_nome:
        st.session_state.usuario_nome = "Visitante (Teste)"
    if "usuario_cargo" not in st.session_state or not st.session_state.usuario_cargo:
        st.session_state.usuario_cargo = "Teste"

HOME_PAGE = "pages/0_Home.py"
# Chaves de navegação (mesmo padrão do navbar em omni_utils) — login uma vez, navega sem pedir de novo
VALID_NAV_KEYS = {"0_Home", "Alunos", "1_PEI", "2_PAE", "3_Hub_Inclusao", "4_Diario_de_Bordo", "5_Monitoramento_Avaliacao"}

# ------------------------------------------------------------------------------
# Router
# ------------------------------------------------------------------------------
if not st.session_state.autenticado:
    render_login()
else:
    # Se por algum motivo entrou sem workspace, força relogar
    if not st.session_state.workspace_id:
        st.session_state.autenticado = False
        st.warning("Workspace não encontrado. Faça login novamente.")
        render_login()
    else:
        # ✅ GARANTE O CLIENT SUPABASE NA SESSÃO (resolve has_sb:false)
        try:
            from supabase_client import get_sb

            get_sb()  # salva em st.session_state["sb"]
        except Exception as e:
            if ENV == "TESTE":
                st.session_state["sb"] = None  # em teste, segue sem Supabase
            else:
                st.error("Supabase não inicializou. Verifique Secrets e requirements.")
                st.code(str(e))
                st.stop()

        # Se veio com ?nav=X (ex: clique no menu), vai para essa página; senão vai para Home
        nav_param = st.query_params.get("nav", "").strip()
        if nav_param and nav_param in VALID_NAV_KEYS:
            st.switch_page(f"pages/{nav_param}.py")
        else:
            st.switch_page(HOME_PAGE)
