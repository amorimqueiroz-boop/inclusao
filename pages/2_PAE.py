import streamlit as st
from ui_nav import render_topbar_nav

render_topbar_nav(active_key="paee")

st.title("PAEE — teste mínimo")
st.success("Se você está vendo isso, o menu está rodando aqui ✅")
st.write("Conteúdo do PAEE entra aqui depois.")
