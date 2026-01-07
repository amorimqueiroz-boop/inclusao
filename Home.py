import streamlit as st
import os

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="Ecossistema Inclusão 360º",
    page_icon="💠",
    layout="wide"
)

# --- 2. ESTILO VISUAL (CSS DIRETO) ---
# O segredo é manter este bloco grudado na esquerda e dentro do st.markdown
st.markdown("""
<style>
    /* Importando Fontes e Ícones */
    @import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800&display=swap');
    
    /* Configuração Global */
    html, body, [class*="css"] { 
        font-family: 'Nunito', sans-serif; 
        color: #2D3748; 
    }
    
    /* Card Principal (Hub) */
    .hub-card {
        background-color: white;
        padding: 30px;
        border-radius: 20px;
        border: 1px solid #EDF2F7;
        border-left: 6px solid #004E92; /* Azul Brand */
        box-shadow: 0 4px 6px rgba(0,0,0,0.03);
        transition: all 0.3s ease;
        height: 100%;
    }
    .hub-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 30px rgba(0,0,0,0.08);
        border-color: #FF6B6B; /* Coral Brand */
    }
    
    /* Ícones dentro dos Cards */
    .icon-box-css {
        width: 60px;
        height: 60px;
        background-color: #E3F2FD;
        border-radius: 15px;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-bottom: 20px;
        font-size: 30px;
        color: #004E92;
    }
    
    /* Tipografia */
    h3 { color: #004E92; font-weight: 800 !important; }
    p { color: #718096; line-height: 1.6; }
    
    /* Botão Falso */
    .fake-btn {
        display: inline-block;
        margin-top: 15px;
        color: #FF6B6B;
        font-weight: 700;
        font-size: 0.9rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. CABEÇALHO ---
# Usando colunas para organizar logo e título
c_logo, c_title = st.columns([1, 5])

with c_logo:
    # Se existir a imagem, mostra ela. Se não, mostra um emoji gigante.
    if os.path.exists("360.png"):
        st.image("360.png", width=100)
    else:
        st.markdown("# 💠")

with c_title:
    st.markdown("""
    # Ecossistema Inclusão 360º
    Uma plataforma completa para gestão, adaptação e conexão escolar.
    """)

st.write("---")

# --- 4. GRID DE MÓDULOS ---
c1, c2 = st.columns(2)

# Card 1: Gestão de PEI
with c1:
    st.markdown("""
    <div class="hub-card">
        <div class="icon-box-css">📄</div>
        <h3>1. Gestão de PEI</h3>
        <p>O módulo clássico. Crie Planos de Ensino Individualizados cruzando LBI, Neurociência e BNCC. Gere documentos oficiais em PDF e Word.</p>
        <div class="fake-btn">👉 Acesse no menu lateral</div>
    </div>
    """, unsafe_allow_html=True)

# Card 2: Adaptador de Avaliações
with c2:
    st.markdown("""
    <div class="hub-card">
        <div class="icon-box-css">📝</div>
        <h3>2. Adaptador de Avaliações</h3>
        <p><b>NOVO!</b> Utilize Inteligência Artificial para adaptar provas e atividades. Transforme questões complexas em formatos acessíveis.</p>
        <div class="fake-btn">👉 Acesse no menu lateral</div>
    </div>
    """, unsafe_allow_html=True)

st.write("")
st.markdown("---")
st.caption("Versão 3.0 Alpha | Desenvolvido por Rodrigo Queiroz")
