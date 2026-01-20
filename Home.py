# Home.py
import streamlit as st

st.set_page_config(page_title="Omnisfera", page_icon="🧩", layout="wide")

# ✅ Garantia visual imediata
st.write("BOOT OK ✅ (se você está vendo isso, Home carregou)")

# init state
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False
if "view" not in st.session_state:
    st.session_state.view = "login" if not st.session_state.autenticado else "home"

# lê view da URL (se tiver)
try:
    if "view" in st.query_params:
        st.session_state.view = st.query_params["view"]
except Exception:
    pass

# força login se não autenticado
if not st.session_state.autenticado:
    st.session_state.view = "login"

# ✅ Import protegido: se quebrar, você vê o erro (não fica branco)
try:
    from ui_nav import render_topbar_nav
except Exception as e:
    st.error("Erro ao importar ui_nav.py")
    st.exception(e)
    st.stop()

# Render topbar minimal fora da Home/Login
try:
    render_topbar_nav(hide_on_views=("home", "login"))
except Exception as e:
    st.error("Erro ao renderizar topbar")
    st.exception(e)
    st.stop()

view = st.session_state.view

# LOGIN
if view == "login":
    st.markdown("## Acesso — Omnisfera")

    with st.container(border=True):
        st.markdown("### Termo de Confidencialidade")
        aceitou = st.checkbox("Li e concordo com o Termo de Confidencialidade.", value=False)

        c1, c2 = st.columns(2)
        with c1:
            nome = st.text_input("Nome")
        with c2:
            cargo = st.text_input("Cargo")

        usuario = st.text_input("Usuário (Email)")
        senha = st.text_input("Senha", type="password")

        disabled = not (aceitou and nome.strip() and cargo.strip() and usuario.strip() and senha.strip())
        if st.button("Entrar", type="primary", use_container_width=True, disabled=disabled):
            # ✅ Por enquanto: só simula login (você pluga Supabase aqui)
            st.session_state.autenticado = True
            st.session_state.usuario_nome = nome.strip()
            st.session_state.usuario_cargo = cargo.strip()
            st.session_state.usuario_email = usuario.strip()
            st.session_state.view = "home"
            st.rerun()

    st.stop()

# HOME PORTAL
if view == "home":
    st.markdown("## Home (Portal)")
    st.caption("Aqui entra seu portal com cards grandes e conteúdo de inclusão.")
    st.write("Se isso aparece, o branco foi resolvido ✅")

    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("Estudantes", use_container_width=True):
            st.session_state.view = "estudantes"
            st.rerun()
    with c2:
        if st.button("Estratégias & PEI", use_container_width=True):
            st.session_state.view = "pei"
            st.rerun()
    with c3:
        if st.button("Plano de Ação (PAEE)", use_container_width=True):
            st.session_state.view = "paee"
            st.rerun()

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
else:
    st.warning(f"View desconhecida: {view}")
