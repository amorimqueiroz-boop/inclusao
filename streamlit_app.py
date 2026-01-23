# streamlit_app.py
import os
import streamlit as st
from login_view import render_login

# ✅ centraliza o lockdown num arquivo só
try:
    from ui_lockdown import hide_streamlit_chrome_if_needed, hide_default_sidebar_nav
except Exception:
    hide_streamlit_chrome_if_needed = None
    hide_default_sidebar_nav = None


def get_env() -> str:
    try:
        v = st.secrets.get("ENV", None)
        if v:
            return str(v).strip().upper()
    except Exception:
        pass
    return (os.getenv("ENV") or "").strip().upper()


ENV = get_env()

st.set_page_config(
    page_title="Omnisfera | Ecossistema",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ✅ aplica o lockdown central (em vez de CSS solto aqui)
if hide_streamlit_chrome_if_needed:
    hide_streamlit_chrome_if_needed()

# ✅ esconde a navegação automática do multipage (a “sidebar antiga”)
if hide_default_sidebar_nav:
    hide_default_sidebar_nav()  # NÃO passe hide_sidebar_container=True aqui



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

HOME_PAGE = "pages/0_Home.py"

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
            st.error("Supabase não inicializou. Verifique Secrets e requirements.")
            st.code(str(e))
            st.stop()

        # Vai para Home real (multipage)
        st.switch_page(HOME_PAGE)
