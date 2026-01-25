# pages/Alunos.py
import streamlit as st
import requests
from datetime import datetime
import base64
import os

# ==============================================================================
# CONFIG
# ==============================================================================
st.set_page_config(
    page_title="Omnisfera • Estudantes",
    page_icon="👥",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ==============================================================================
# CSS (Visual Limpo)
# ==============================================================================
st.markdown("""
<style>
    /* Remove padding do topo */
    .block-container { padding-top: 2rem !important; }
    
    /* Esconde elementos padrão */
    [data-testid="stSidebarNav"], footer { display: none !important; }
    
    /* Estilo das Abas de Navegação (Radio Button Horizontal) */
    div.row-widget.stRadio > div { flex-direction: row; justify-content: center; gap: 10px; }
    div.row-widget.stRadio > div > label {
        background-color: #F1F5F9; border: 1px solid #E2E8F0;
        padding: 8px 16px; border-radius: 8px; cursor: pointer;
        font-weight: 700; color: #64748B; font-size: 0.8rem;
        transition: all 0.2s;
    }
    div.row-widget.stRadio > div > label:hover { background-color: #E2E8F0; }
    div.row-widget.stRadio > div > label[data-baseweb="radio"] > div { display: none; } /* Esconde a bolinha */
    
    /* Quando selecionado (Simula Aba Ativa) */
    div.row-widget.stRadio > div > label[aria-checked="true"] {
        background-color: #4F46E5 !important; color: white !important; border-color: #4F46E5 !important;
        box-shadow: 0 4px 6px rgba(79, 70, 229, 0.2);
    }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# NAVEGAÇÃO SUPERIOR (ESTILO ABAS)
# ==============================================================================
# Mapeamento: Nome da Aba -> Caminho do Arquivo
PAGES = {
    "Início": "pages/0_Home.py",
    "Estudantes": "pages/Alunos.py",
    "PEI": "pages/1_PEI.py",
    "AEE": "pages/2_PAE.py",
    "Recursos": "pages/3_Hub_Inclusao.py",
    "Diário": "pages/4_Diario_de_Bordo.py",
    "Dados": "pages/5_Monitoramento_Avaliacao.py"
}

col_nav, _ = st.columns([4, 1])
with col_nav:
    # O truque: Usar radio button horizontal como menu
    selection = st.radio(
        "Navegação", 
        list(PAGES.keys()), 
        index=1, # Índice 1 = Estudantes (Aba atual)
        label_visibility="collapsed",
        key="nav_radio"
    )

# Lógica de Redirecionamento
if selection != "Estudantes": # Se mudou a seleção
    st.switch_page(PAGES[selection])

st.markdown("---") # Linha separadora

# ==============================================================================
# CONTEÚDO DA PÁGINA (Mantido igual)
# ==============================================================================
# (Aqui entraria todo o seu código de lógica de Alunos, tabelas, etc.)
st.title("Gestão de Estudantes")
st.write("Conteúdo da página de estudantes aqui...")
# ... (Cole sua lógica de tabela aqui)
