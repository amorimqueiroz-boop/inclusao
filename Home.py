import streamlit as st
from supabase import create_client
from ui_nav import render_topbar_nav

st.set_page_config(page_title="Omnisfera", page_icon="🧩", layout="wide")

# -------------------------
# INIT SESSION
# -------------------------
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False
if "view" not in st.session_state:
    st.session_state.view = "login" if not st.session_state.autenticado else "home"

# força login quando não autenticado
if not st.session_state.autenticado:
    st.session_state.view = "login"

# -------------------------
# SUPABASE CLIENT (cache)
# -------------------------
@st.cache_resource
def get_supabase():
    url = st.secrets.get("SUPABASE_URL", "")
    key = st.secrets.get("SUPABASE_ANON_KEY", "")
    if not url or not key:
        raise RuntimeError("SUPABASE_URL / SUPABASE_ANON_KEY não configurados em secrets.toml")
    return create_client(url, key)

def supabase_login(email: str, password: str) -> tuple[bool, str]:
    """
    Login real no Supabase Auth.
    Retorna (ok, msg)
    """
    try:
        sb = get_supabase()
        resp = sb.auth.sign_in_with_password({"email": email, "password": password})
        # Se não lançar exceção, é ok. (resp contém session/user)
        if not resp or not getattr(resp, "session", None):
            return False, "Usuário ou senha inválidos."
        return True, "ok"
    except Exception as e:
        # Mensagem amigável (sem expor detalhes)
        return False, "Não foi possível autenticar. Verifique usuário e senha."

# TOPBAR (no ui_nav ela só aparece quando autenticado)
render_topbar_nav()

view = st.session_state.view

# -------------------------
# LOGIN VIEW
# -------------------------
if view == "login":
    st.markdown("## Acesso — Omnisfera")

    with st.container(border=True):
        st.markdown("### Termo de Confidencialidade")
        st.caption(
            "Ao acessar, você declara ciência de que as informações deste sistema são **confidenciais** "
            "e devem ser utilizadas exclusivamente para fins pedagógicos e institucionais."
        )
        aceitou = st.checkbox("Li e concordo com o Termo de Confidencialidade.", value=False)

        st.divider()

        c1, c2 = st.columns(2)
        with c1:
            nome = st.text_input("Nome", placeholder="Ex.: Rodrigo Amorim")
        with c2:
            cargo = st.text_input("Cargo", placeholder="Ex.: Consultor Pedagógico / Coordenação / AEE")

        st.divider()

        usuario = st.text_input(
            "Usuário (Email)",
            placeholder="seuemail@escola.com",
            help="Use o email cadastrado no sistema."
        )
        senha = st.text_input("Senha", type="password", help="Use a senha cadastrada no sistema.")

        st.divider()

        disabled = not (aceitou and nome.strip() and cargo.strip() and usuario.strip() and senha.strip())
        if st.button("Entrar", type="primary", use_container_width=True, disabled=disabled):
            ok, msg = supabase_login(usuario.strip(), senha)

            if ok:
                st.session_state.autenticado = True
                st.session_state.usuario_nome = nome.strip()
                st.session_state.usuario_cargo = cargo.strip()
                st.session_state.usuario_email = usuario.strip()
                st.session_state.view = "home"
                st.rerun()
            else:
                st.error(msg)

    st.stop()

# -------------------------
# ROUTER (PÓS-LOGIN)
# -------------------------
if view == "home":
    st.markdown("## Home")
    st.caption(
        f"Logado como: {st.session_state.get('usuario_nome','-')} — "
        f"{st.session_state.get('usuario_cargo','-')} ({st.session_state.get('usuario_email','-')})"
    )
    st.write("App rodando ✅")

elif view == "estudantes":
    st.markdown("## Estudantes")

elif view == "pei":
    st.markdown("## Estratégias & PEI")

elif view == "paee":
    st.markdown("## Plano de Ação (PAEE)")

elif view == "hub":
    st.markdown("## Hub de Recursos")

elif view == "diario":
    st.markdown("## Diário de Bordo")

elif view == "mon":
    st.markdown("## Evolução & Acompanhamento")
