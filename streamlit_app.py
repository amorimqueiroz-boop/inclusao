import streamlit as st
import importlib.util
import os

st.set_page_config(page_title="Omnisfera | Boot", layout="wide")

st.markdown("## Boot do Omnisfera")
st.write("✅ `streamlit_app.py` carregou.")
st.write("📁 Arquivos na raiz:", sorted([f for f in os.listdir(".") if not f.startswith(".")]))

TARGET = "home_portal.py"  # <-- ajuste aqui se seu arquivo tiver outro nome

if not os.path.exists(TARGET):
    st.error(f"❌ Não encontrei `{TARGET}` na raiz do projeto.")
    st.stop()

st.success(f"✅ Encontrei `{TARGET}`. Vou carregar agora...")

spec = importlib.util.spec_from_file_location("home_module", TARGET)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

st.success("✅ `home_portal.py` foi executado.")
