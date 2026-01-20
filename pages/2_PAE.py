import streamlit as st
from ui_nav import render_topbar_nav

st.set_page_config(page_title="Omnisfera | PAEE", page_icon="🧩", layout="wide")

render_topbar_nav("paee")  # <-- ATENÇÃO: aqui é sem "active="

st.title("PAEE — teste mínimo")
st.success("Menu carregou aqui ✅")
st.write("Se clicar nos itens acima, deve trocar de página.")
