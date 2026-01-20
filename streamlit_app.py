import streamlit as st
from ui_nav import boot_ui, ensure_auth_state, route_from_query

st.set_page_config(page_title="Omnisfera", layout="wide")

ensure_auth_state()
boot_ui(do_route=False)  # NÃO roteia aqui ainda

def render_login():
    st.markdown("## Entrar")
    st.caption("Acesso restrito ao painel Omnisfera.")

    with st.form("login_form", clear_on_submit=False):
        email = st.text_input("E-mail", placeholder="seu@email.com")
        senha = st.text_input("Senha", type="password", placeholder="••••••••")
        ok = st.form_submit_button("Entrar")

    if ok:
        # ✅ LOGIN SIMPLES (placeholder)
        # aqui você depois pluga Supabase Auth ou seu sistema real
        if email.strip() and senha.strip():
            st.session_state.autenticado = True
            st.session_state.user = {"email": email.strip()}
            st.query_params["go"] = "home"
            st.switch_page("home_portal.py")
        else:
            st.error("Preencha e-mail e senha.")

# --- GATE ---
go = st.query_params.get("go", "login")

if not st.session_state.autenticado:
    # sempre login se não autenticado
    st.query_params["go"] = "login"
    render_login()
else:
    # autenticado: manda pra home ou rota solicitada
    if go == "login":
        st.query_params["go"] = "home"
        st.switch_page("home_portal.py")
    else:
        # deixa o router do Streamlit fazer via multipage
        # se quiser rotear por go aqui, fazemos agora:
        from ui_nav import route_from_query
        route_from_query(default_go="home")
        # fallback: se por algum motivo não trocar, mostra um link
        st.markdown("Redirecionando…")
