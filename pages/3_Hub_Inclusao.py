import streamlit as st
import os

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Omnisfera | Hub", page_icon="🚀", layout="wide")

# --- 2. VERIFICAÇÃO DE SEGURANÇA ---
def verificar_acesso():
    # Se a pessoa tentar entrar direto pelo link sem passar pela Home:
    if "autenticado" not in st.session_state or not st.session_state["autenticado"]:
        st.error("🔒 Acesso Negado. Por favor, faça login na Página Inicial.")
        st.stop() # Para o carregamento
    
    # Se estiver logado, garante o visual correto
    st.markdown("""
        <style>
            [data-testid="stHeader"] {visibility: hidden !important; height: 0px !important;}
            .block-container {padding-top: 1rem !important;}
        </style>
    """, unsafe_allow_html=True)

verificar_acesso()

# --- 3. BARRA LATERAL PADRÃO ---
with st.sidebar:
    st.image("ominisfera.png", width=150) # Certifique-se que a imagem está acessível ou na raiz
    st.markdown("---")
    if st.button("🏠 Voltar para Home"):
        st.switch_page("Home.py")
    st.markdown("---")

# =========================================================
# AQUI COMEÇA O CÓDIGO ORIGINAL DA PÁGINA (ADAPTADOR, ETC)
# =========================================================
# ... Cole o restante do código do Adaptador V18.1 daqui para baixo ...
