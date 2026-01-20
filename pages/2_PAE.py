import streamlit as st
from ui_nav import render_topbar_nav


render_topbar_nav(active="paee")

st.title("PAEE — teste mínimo")
st.success("Menu carregou aqui ✅")
st.write("Se clicar nos itens acima, deve trocar de página.")
