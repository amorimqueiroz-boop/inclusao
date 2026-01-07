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
    
    .hub-card {
        background: white; padding: 30px; border-radius: 20px;
        border: 1px solid #EDF2F7; border-left: 6px solid var(--brand-blue);
        box-shadow: 0 4px 6px rgba(0,0,0,0.03); transition: all 0.3s ease; height: 100%;
        cursor: pointer;
    }
    .hub-card:hover { transform: translateY(-5px); box-shadow: 0 15px 30px rgba(0,0,0,0.08); border-color: var(--brand-coral); }
    
    .icon-box {
        width: 60px; height: 60px; background: #E3F2FD; border-radius: 15px;
        display: flex; align-items: center; justify-content: center; margin-bottom: 20px;
    }
    .icon-box i { font-size: 30px; color: var(--brand-blue); }
    
    h3 { color: var(--brand-blue); font-weight: 800; }
    p { color: #718096; line-height: 1.6; }
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
        <h1 style="color: #004E92; font-size: 3rem; margin-bottom: 10px; margin-top: 0;">Ecossistema Inclusão 360º</h1>
        <p style="font-size: 1.2rem; color: #718096;">Uma plataforma completa para gestão, adaptação e conexão escolar.</p>
    </div>
    """, unsafe_allow_html=True)

st.write("")
st.write("")

# --- MÓDULOS ---
c1, c2 = st.columns(2)

with c1:
    st.markdown("""
    <div class="hub-card">
        <div class="icon-box"><i class="ri-file-user-line"></i></div>
        <h3>1. Gestão de PEI</h3>
        <p>O módulo clássico. Crie Planos de Ensino Individualizados cruzando LBI, Neurociência e BNCC. Gere documentos oficiais em PDF e Word.</p>
        <p style="color: #FF6B6B; font-weight: 700; margin-top: 15px;">👉 Acesse no menu lateral</p>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown("""
    <div class="hub-card">
        <div class="icon-box"><i class="ri-pencil-ruler-line"></i></div>
        <h3>2. Adaptador de Avaliações</h3>
        <p><b>NOVO!</b> Utilize Inteligência Artificial para adaptar provas e atividades. Transforme questões complexas em formatos acessíveis baseados no perfil do aluno.</p>
        <p style="color: #FF6B6B; font-weight: 700; margin-top: 15px;">👉 Acesse no menu lateral</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")
st.markdown("<div style='text-align:center; color:#A0AEC0;'>Versão 3.0 Alpha | Desenvolvido por Rodrigo Queiroz</div>", unsafe_allow_html=True)
