import streamlit as st
from ui_nav import boot_ui, ensure_auth_state

ensure_auth_state()
boot_ui(do_route=False)

if not st.session_state.autenticado:
    st.query_params["go"] = "login"
    st.stop()

boot_ui(do_route=False)

# 1. Configuração da página DEVE ser a primeira linha do Streamlit
st.set_page_config(layout="wide", page_title="Omnisfera")

# 2. Chame a barra imediatamente
render_topbar_nav(active_page="alunos") # Mude o nome conforme a página

# 3. O resto do seu código vem aqui...
st.title("Gestão de Alunos")

st.title("PAEE — teste mínimo")
st.success("Menu carregou aqui ✅")
st.write("Se clicar nos itens acima, deve trocar de página.")
