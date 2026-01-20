import streamlit as st
from ui_nav import render_omnisfera_nav

render_omnisfera_nav(active="paee")

st.title("PAEE — teste mínimo")
st.success("Menu carregou aqui ✅")
st.write("Se clicar nos itens acima, deve trocar de página.")
