import streamlit as st
import omni_utils as core # Importa a nossa Matriz
from openai import OpenAI
import time

# ==============================================================================
# 1. CONFIGURAÇÃO DA PÁGINA
# ==============================================================================
# A configuração básica fica aqui, o resto vem da matriz
st.set_page_config(
    page_title="Omnisfera", 
    page_icon="🌐", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

# ==============================================================================
# 2. INVOCANDO A MATRIZ (ESTILO, HEADER, SIDEBAR E LOGIN)
# ==============================================================================
# Aplica CSS, Header de Vidro, Sidebar Nova e Rodapé
core.aplicar_estilo_global()

# Verifica Login (Se não logar, o script para aqui)
if not core.verificar_acesso():
    st.stop()

# ==============================================================================
# 3. DADOS DO USUÁRIO (PARTE 5 - CONTEÚDO)
# ==============================================================================
# Como já passamos pelo login da matriz, os dados estão seguros na sessão
nome_display = st.session_state["usuario_nome"].split()[0]

# Banner Message (IA ou Padrão)
mensagem_banner = "Unindo ciência, dados e empatia para transformar a educação."
if 'OPENAI_API_KEY' in st.secrets:
    try:
        if 'banner_msg' not in st.session_state:
            client = OpenAI(api_key=st.secrets['OPENAI_API_KEY'])
            prompt = f"Frase curta (max 20 palavras) de boas-vindas para {nome_display} sobre potencial humano e educação."
            res = client.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "user", "content": prompt}])
            st.session_state['banner_msg'] = res.choices[0].message.content
        mensagem_banner = st.session_state['banner_msg']
    except: pass

# ==============================================================================
# 4. DASHBOARD VISUAL (HERO E CARDS)
# ==============================================================================

# CSS Específico da Home (Só o que não é global)
st.markdown("""
<style>
    .dash-hero { 
        background: linear-gradient(135deg, #0F52BA 0%, #062B61 100%); 
        border-radius: 20px; margin-bottom: 40px; 
        box-shadow: 0 15px 30px rgba(15, 82, 186, 0.2);
        color: white; position: relative; overflow: hidden;
        padding: 50px 60px; margin-top: 20px;
        display: flex; align-items: center;
    }
    .hero-title { font-family: 'Inter', sans-serif; font-weight: 800; font-size: 2.2rem; margin: 0; margin-bottom: 10px; }
    .hero-subtitle { font-size: 1.1rem; opacity: 0.95; font-style: italic; }
    .hero-bg-icon { position: absolute; right: 40px; font-size: 8rem; opacity: 0.08; top: 20px; transform: rotate(-15deg); }

    .tool-card { 
        background: white; border-radius: 20px; padding: 30px 25px; 
        box-shadow: 0 4px 10px rgba(0,0,0,0.03); border: 1px solid #E2E8F0; 
        height: 100%; display: flex; flex-direction: column; justify-content: space-between; 
        text-align: center; transition: all 0.3s;
    }
    .tool-card:hover { transform: translateY(-5px); border-color: #3182CE; box-shadow: 0 20px 40px rgba(0,0,0,0.08); }
    
    .card-logo-box { height: 90px; display: flex; align-items: center; justify-content: center; margin-bottom: 15px; }
    .card-logo-img { max-height: 80px; width: auto; object-fit: contain; }
    .tool-desc { font-size: 0.9rem; color: #718096; margin-bottom: 20px; min-height: 40px; }
    
    .border-blue { border-bottom: 5px solid #3182CE; } 
    .border-purple { border-bottom: 5px solid #805AD5; } 
    .border-teal { border-bottom: 5px solid #38B2AC; }
    
    /* Botões */
    div[data-testid="column"] .stButton button {
        width: 100%; border-radius: 12px; background-color: #F8F9FA; color: #2D3748; border: 1px solid #E2E8F0; font-weight: 700;
    }
    div[data-testid="column"] .stButton button:hover { background-color: #3182CE; color: white; border-color: #3182CE; }
</style>
<link href="https://cdn.jsdelivr.net/npm/remixicon@4.1.0/fonts/remixicon.css" rel="stylesheet">
""", unsafe_allow_html=True)

# HERO SECTION
st.markdown(f"""
<div class="dash-hero">
    <div style="z-index: 2; max-width: 90%;">
        <div class="hero-title">Olá, {nome_display}!</div>
        <div class="hero-subtitle">"{mensagem_banner}"</div>
    </div>
    <i class="ri-heart-pulse-fill hero-bg-icon"></i>
</div>
""", unsafe_allow_html=True)

# ACESSO RÁPIDO
st.markdown("### 🚀 Acesso Rápido")

logo_pei = core.get_base64_image("360.png")
logo_paee = core.get_base64_image("pae.png")
logo_hub = core.get_base64_image("hub.png")

c1, c2, c3 = st.columns(3)

# Card PEI
with c1:
    img_tag = f'<img src="data:image/png;base64,{logo_pei}" class="card-logo-img">' if logo_pei else '<i class="ri-book-read-line" style="font-size:4rem; color:#3182CE;"></i>'
    st.markdown(f"""<div class="tool-card border-blue"><div class="card-logo-box">{img_tag}</div><div class="tool-desc">Plano de Ensino Individualizado Oficial.</div></div>""", unsafe_allow_html=True)
    if st.button("➜ Acessar PEI", use_container_width=True): st.switch_page("pages/1_PEI.py")

# Card PAEE
with c2:
    img_tag = f'<img src="data:image/png;base64,{logo_paee}" class="card-logo-img">' if logo_paee else '<i class="ri-puzzle-line" style="font-size:4rem; color:#805AD5;"></i>'
    st.markdown(f"""<div class="tool-card border-purple"><div class="card-logo-box">{img_tag}</div><div class="tool-desc">Sala de Recursos e Tecnologias Assistivas.</div></div>""", unsafe_allow_html=True)
    if st.button("➜ Acessar PAEE", use_container_width=True): st.switch_page("pages/2_PAE.py")

# Card Hub
with c3:
    img_tag = f'<img src="data:image/png;base64,{logo_hub}" class="card-logo-img">' if logo_hub else '<i class="ri-rocket-line" style="font-size:4rem; color:#38B2AC;"></i>'
    st.markdown(f"""<div class="tool-card border-teal"><div class="card-logo-box">{img_tag}</div><div class="tool-desc">Adaptação de Provas e Materiais.</div></div>""", unsafe_allow_html=True)
    if st.button("➜ Acessar Hub", use_container_width=True): st.switch_page("pages/3_Hub_Inclusao.py")

# INSIGHT FINAL
st.markdown("<br>", unsafe_allow_html=True)
st.markdown("""
<div style="background-color: #FFFFF0; border-left: 5px solid #D69E2E; padding: 20px; border-radius: 12px; display: flex; align-items: center; gap: 15px;">
    <i class="ri-lightbulb-flash-line" style="font-size: 1.5rem; color: #D69E2E;"></i>
    <div style="color: #4A5568; font-style: italic;">"A inclusão acontece quando aprendemos com as diferenças e não apesar delas."</div>
</div>
""", unsafe_allow_html=True)

# RODAPÉ
st.markdown("<div style='text-align: center; color: #CBD5E0; font-size: 0.8rem; margin-top: 50px;'>Omnisfera © 2026</div>", unsafe_allow_html=True)
