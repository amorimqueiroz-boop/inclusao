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

# --- ESTILO VISUAL ---
st.markdown("""
    <link href="https://cdn.jsdelivr.net/npm/remixicon@4.1.0/fonts/remixicon.css" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800&display=swap" rel="stylesheet">
    <style>
    html, body, [class*="css"] { font-family: 'Nunito', sans-serif; color: #2D3748; }
    :root { --brand-blue: #004E92; --brand-coral: #FF6B6B; }
    
    /* CARDS */
    .hub-card {
        background: white; padding: 30px; border-radius: 20px;
        border: 1px solid #EDF2F7; border-left: 6px solid var(--brand-blue);
        box-shadow: 0 4px 6px rgba(0,0,0,0.03); 
        height: 220px; /* Altura fixa para alinhar */
        margin-bottom: 15px;
    }
    
    .icon-box {
        width: 50px; height: 50px; background: #E3F2FD; border-radius: 12px;
        display: flex; align-items: center; justify-content: center; margin-bottom: 15px;
    }
    .icon-box i { font-size: 26px; color: var(--brand-blue); }
    
    h3 { color: var(--brand-blue); font-weight: 800; font-size: 1.2rem; margin-bottom: 10px; }
    p { color: #718096; line-height: 1.5; font-size: 0.95rem; }
    
    /* ESTILO DOS BOTÕES DE NAVEGAÇÃO */
    div[data-testid="column"] .stButton button {
        background-color: var(--brand-coral); 
        color: white; 
        border-radius: 12px; 
        border: none;
        height: 3em;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1px;
        width: 100%;
        transition: all 0.3s;
    }
    div[data-testid="column"] .stButton button:hover {
        background-color: #E53E3E;
        transform: scale(1.02);
        box-shadow: 0 4px 10px rgba(0,0,0,0.1);
    }
    
    /* BOTÃO DESATIVADO (EM BREVE) */
    .disabled-btn {
        background-color: #CBD5E0; color: white; padding: 12px; 
        border-radius: 12px; text-align: center; font-weight: 700;
    }
    </style>
""", unsafe_allow_html=True)

# --- CABEÇALHO ---
c_logo, c_title = st.columns([1, 5])
with c_logo:
    if os.path.exists("360.png"):
        st.image("360.png", width=100)
    else:
        st.markdown("<div style='font-size: 4rem; text-align: center;'>💠</div>", unsafe_allow_html=True)

with c_title:
    st.markdown("""
    <div style="padding-top: 10px;">
        <h1 style="color: #004E92; font-size: 3rem; margin-bottom: 5px; margin-top: 0;">Ecossistema Inclusão 360º</h1>
        <p style="font-size: 1.1rem; color: #718096;">Hub de Inteligência Pedagógica e Adaptação Escolar</p>
    </div>
    """, unsafe_allow_html=True)

st.write("")
st.write("")

# --- GRID DE MÓDULOS ---
c1, c2, c3 = st.columns(3)

# CARD 1: GESTÃO DE PEI
with c1:
    st.markdown("""
    <div class="hub-card">
        <div class="icon-box"><i class="ri-file-user-line"></i></div>
        <h3>1. Gestão de PEI</h3>
        <p>Crie Planos de Ensino Individualizados cruzando LBI, Neurociência e BNCC. Gere documentos oficiais em PDF e Word.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # O BOTÃO REAL DE NAVEGAÇÃO
    if st.button("Acessar Módulo PEI 🚀", key="btn_pei"):
        st.switch_page("pages/2_Gestao_PEI.py")

# CARD 2: ADAPTADOR DE AVALIAÇÕES
with c2:
    st.markdown("""
    <div class="hub-card">
        <div class="icon-box"><i class="ri-pencil-ruler-2-line"></i></div>
        <h3>2. Adaptador de Avaliações</h3>
        <p>Utilize Inteligência Artificial para adaptar provas. Transforme questões complexas em formatos acessíveis (múltipla escolha, lacunas).</p>
    </div>
    """, unsafe_allow_html=True)
    
    # O BOTÃO REAL DE NAVEGAÇÃO
    if st.button("Acessar Adaptador ✨", key="btn_adapt"):
        st.switch_page("pages/1_Adaptador_Provas.py")

# CARD 3: EM BREVE
with c3:
    st.markdown("""
    <div class="hub-card" style="opacity: 0.7; border-left-color: #CBD5E0;">
        <div class="icon-box" style="background: #EDF2F7;"><i class="ri-home-heart-line" style="color: #A0AEC0;"></i></div>
        <h3 style="color: #718096;">Família & Escola</h3>
        <p><i>Em Breve.</i> Portal para conectar pais e professores, com diário de bordo compartilhado e orientações parentais.</p>
    </div>
    <div class="disabled-btn">EM DESENVOLVIMENTO 🔒</div>
    """, unsafe_allow_html=True)

st.markdown("---")
st.markdown("<div style='text-align:center; color:#A0AEC0; font-size:0.8rem;'>Versão 3.0 Alpha | Desenvolvido por Rodrigo Queiroz</div>", unsafe_allow_html=True)
