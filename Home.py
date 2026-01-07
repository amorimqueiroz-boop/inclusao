import streamlit as st
import os

# --- FUNÇÃO FAVICON ---
def get_favicon():
    if os.path.exists("iconeaba.png"): return "iconeaba.png"
    return "💠"

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="Ecossistema Inclusão 360º",
    page_icon=get_favicon(),
    layout="wide"
)

# --- ESTILO VISUAL (CSS SIMPLIFICADO E BLINDADO) ---
st.markdown("""
<style>
    /* Estilo Geral */
    .stApp { background-color: #F7FAFC; }
    
    /* Cards */
    .hub-card {
        background-color: white;
        padding: 2rem;
        border-radius: 15px;
        border: 1px solid #E2E8F0;
        border-left: 6px solid #004E92;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        margin-bottom: 20px;
        height: 250px;
    }
    
    /* Ícones */
    .icon-box {
        font-size: 2rem;
        color: #004E92;
        margin-bottom: 1rem;
    }
    
    /* Títulos */
    h3 { color: #004E92 !important; font-weight: 800; }
    p { color: #4A5568; font-size: 1rem; }
    
    /* Botões */
    .stButton button {
        width: 100%;
        background-color: #FF6B6B !important;
        color: white !important;
        font-weight: bold;
        border-radius: 10px;
        border: none;
        padding: 0.5rem 1rem;
        transition: 0.3s;
    }
    .stButton button:hover {
        background-color: #E53E3E !important;
        transform: scale(1.02);
    }
</style>
<link href="https://cdn.jsdelivr.net/npm/remixicon@4.1.0/fonts/remixicon.css" rel="stylesheet">
""", unsafe_allow_html=True)

# --- CABEÇALHO ---
c_logo, c_title = st.columns([1, 5])
with c_logo:
    if os.path.exists("360.png"):
        st.image("360.png", width=100)
    else:
        st.header("💠")

with c_title:
    st.title("Ecossistema Inclusão 360º")
    st.markdown("Plataforma Integrada de Gestão, Adaptação e Inteligência Pedagógica.")

st.divider()

# --- MÓDULOS (COM BOTÕES QUE FUNCIONAM) ---
c1, c2 = st.columns(2)

# CARD 1: PEI
with c1:
    st.markdown("""
    <div class="hub-card">
        <div class="icon-box"><i class="ri-file-user-line"></i></div>
        <h3>1. Gestão de PEI</h3>
        <p>O módulo clássico. Crie Planos de Ensino Individualizados cruzando LBI, Neurociência e BNCC.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Botão de Navegação
    if st.button("Acessar Módulo PEI 🚀", key="btn_pei", use_container_width=True):
        st.switch_page("pages/2_Gestao_PEI.py")

# CARD 2: ADAPTADOR
with c2:
    st.markdown("""
    <div class="hub-card">
        <div class="icon-box"><i class="ri-pencil-ruler-2-line"></i></div>
        <h3>2. Adaptador de Avaliações</h3>
        <p><b>NOVO!</b> Utilize IA para transformar questões complexas em formatos acessíveis.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Botão de Navegação
    if st.button("Acessar Adaptador ✨", key="btn_adapt", use_container_width=True):
        st.switch_page("pages/1_Adaptador_Provas.py")

st.divider()
st.markdown("<div style='text-align:center; color:#A0AEC0;'>Versão 3.0 Alpha | Desenvolvido por Rodrigo Queiroz</div>", unsafe_allow_html=True)
