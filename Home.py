import streamlit as st
import omni_utils as core  # Nossa Matriz Inteligente
from openai import OpenAI
import time

# ==============================================================================
# 1. CONFIGURAÇÃO (Obrigatório ser a 1ª linha)
# ==============================================================================
st.set_page_config(
    page_title="Omnisfera | Dashboard",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==============================================================================
# 2. INVOCANDO A MATRIZ
# ==============================================================================
# Na HOME, queremos:
# 1. Sidebar padrão (logo do app) -> logo_pagina=None
# 2. Header Global de Vidro -> exibir_header_global=True
core.aplicar_estilo_global(logo_pagina=None, exibir_header_global=True)

# Verifica Login
if not core.verificar_acesso():
    st.stop()

# ==============================================================================
# 3. CSS ESPECÍFICO DA HOME (Animações e Bento Grid)
# ==============================================================================
st.markdown("""
<style>
    /* --- ANIMAÇÕES DE SCROLL E HOVER (Nível "Framer Motion") --- */
    
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    /* Classe para animar entrada dos elementos */
    .animate-enter {
        animation: fadeInUp 0.6s cubic-bezier(0.2, 0.8, 0.2, 1) forwards;
    }

    /* Efeito de Mola ao passar o mouse */
    .hover-spring {
        transition: transform 0.4s cubic-bezier(0.34, 1.56, 0.64, 1), box-shadow 0.3s ease;
    }
    .hover-spring:hover {
        transform: translateY(-8px) scale(1.01);
        box-shadow: 0 20px 40px rgba(0,0,0,0.08) !important;
        z-index: 10;
        border-color: #3182CE !important;
    }

    /* --- HERO SECTION --- */
    .dash-hero { 
        background: radial-gradient(circle at top right, #0F52BA, #062B61); 
        border-radius: 24px; margin-bottom: 40px; 
        box-shadow: 0 15px 40px -10px rgba(15, 82, 186, 0.4);
        color: white; position: relative; overflow: hidden;
        padding: 60px; display: flex; align-items: center; 
        margin-top: 20px; border: 1px solid rgba(255,255,255,0.1);
    }
    .hero-title { font-family: 'Nunito', sans-serif; font-weight: 800; font-size: 2.4rem; margin: 0; line-height: 1.1; letter-spacing: -1px; }
    .hero-bg-icon { position: absolute; right: 30px; font-size: 12rem; opacity: 0.05; top: -20px; transform: rotate(-10deg); pointer-events: none; }

    /* --- TOOL CARDS (Estilo Apple/Bento) --- */
    .tool-card { 
        background: white; border-radius: 20px; padding: 30px 25px; 
        box-shadow: 0 4px 10px rgba(0,0,0,0.03); border: 1px solid #E2E8F0; 
        height: 100%; display: flex; flex-direction: column; justify-content: space-between; 
        text-align: center; position: relative; overflow: hidden;
    }
    .card-logo-box { height: 90px; display: flex; align-items: center; justify-content: center; margin-bottom: 20px; }
    .card-logo-img { max-height: 85px; width: auto; object-fit: contain; filter: drop-shadow(0 8px 12px rgba(0,0,0,0.1)); }
    .tool-desc-short { font-size: 0.95rem; color: #718096; font-weight: 500; margin-bottom: 25px; min-height: 45px; line-height: 1.4; }
    
    /* Botões Modernos */
    div[data-testid="column"] .stButton button {
        width: 100%; border-radius: 12px; border: none;
        background-color: #F8FAFC; color: #475569; font-family: 'Inter', sans-serif; font-weight: 700; 
        padding: 12px 0; transition: all 0.2s ease; border: 1px solid #E2E8F0;
    }
    div[data-testid="column"] .stButton button:hover { 
        background-color: #3182CE; color: white; border-color: #3182CE;
    }
    
    /* Bordas de destaque */
    .border-blue { border-bottom: 5px solid #3182CE; } 
    .border-purple { border-bottom: 5px solid #805AD5; } 
    .border-teal { border-bottom: 5px solid #38B2AC; }

    /* --- BENTO GRID LINKS --- */
    .bento-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 20px; margin-bottom: 40px; }
    .bento-item { 
        background: white; border-radius: 16px; padding: 25px; border: 1px solid #E2E8F0; 
        box-shadow: 0 2px 5px rgba(0,0,0,0.02); text-decoration: none; color: inherit; 
        display: flex; flex-direction: column; align-items: center; text-align: center; 
        height: 100%; transition: transform 0.3s;
    }
    .bento-item:hover { transform: translateY(-5px); border-color: #CBD5E0; box-shadow: 0 10px 20px rgba(0,0,0,0.05); }
    .bento-icon { width: 50px; height: 50px; border-radius: 14px; display: flex; align-items: center; justify-content: center; font-size: 1.5rem; margin-bottom: 15px; }

    /* Titulos de Seção */
    .section-title { font-family: 'Nunito', sans-serif; font-weight: 800; font-size: 1.4rem; color: #1A202C; margin-bottom: 25px; display: flex; align-items: center; gap: 10px; }
</style>
<link href="https://cdn.jsdelivr.net/npm/remixicon@4.1.0/fonts/remixicon.css" rel="stylesheet">
""", unsafe_allow_html=True)

# ==============================================================================
# 4. DADOS & IA
# ==============================================================================
nome_display = st.session_state.get("usuario_nome", "Educador").split()[0]
mensagem_banner = "Unindo ciência, dados e empatia para transformar a educação."

if 'OPENAI_API_KEY' in st.secrets:
    try:
        client = OpenAI(api_key=st.secrets['OPENAI_API_KEY'])
        # Cache de sessão para não gastar API à toa
        if 'banner_msg' not in st.session_state:
            prompt = f"Frase muito curta e inspiradora para {nome_display} sobre educação inclusiva."
            res = client.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "user", "content": prompt}])
            st.session_state['banner_msg'] = res.choices[0].message.content
        mensagem_banner = st.session_state['banner_msg']
    except: pass

# ==============================================================================
# 5. RENDERIZAÇÃO (CONTEÚDO)
# ==============================================================================

# --- HERO ---
st.markdown(f"""
<div class="dash-hero animate-enter">
    <div style="z-index: 2; max-width: 85%;">
        <div class="hero-title">Olá, {nome_display}!</div>
        <p style="font-size: 1.1rem; opacity: 0.95; font-style: italic; margin-top: 10px;">"{mensagem_banner}"</p>
    </div>
    <i class="ri-heart-pulse-fill hero-bg-icon"></i>
</div>
""", unsafe_allow_html=True)

# --- CARDS PRINCIPAIS ---
st.markdown("<div class='section-title animate-enter'><i class='ri-apps-2-line'></i> Módulos Principais</div>", unsafe_allow_html=True)

logo_pei = core.get_base64_image("360.png")
logo_paee = core.get_base64_image("pae.png")
logo_hub = core.get_base64_image("hub.png")

c1, c2, c3 = st.columns(3)

with c1:
    img_tag = f'<img src="data:image/png;base64,{logo_pei}" class="card-logo-img">' if logo_pei else '<i class="ri-book-read-line" style="font-size:4rem; color:#3182CE;"></i>'
    st.markdown(f"""<div class="tool-card border-blue hover-spring animate-enter"><div class="card-logo-box">{img_tag}</div><div class="tool-desc-short">Plano de Ensino Individualizado Oficial.</div></div>""", unsafe_allow_html=True)
    if st.button("➜ Acessar PEI", key="btn_pei", use_container_width=True): st.switch_page("pages/1_PEI.py")

with c2:
    img_tag = f'<img src="data:image/png;base64,{logo_paee}" class="card-logo-img">' if logo_paee else '<i class="ri-puzzle-line" style="font-size:4rem; color:#805AD5;"></i>'
    st.markdown(f"""<div class="tool-card border-purple hover-spring animate-enter"><div class="card-logo-box">{img_tag}</div><div class="tool-desc-short">Sala de Recursos e Tecnologias Assistivas.</div></div>""", unsafe_allow_html=True)
    if st.button("➜ Acessar PAEE", key="btn_paee", use_container_width=True): st.switch_page("pages/2_PAE.py")

with c3:
    img_tag = f'<img src="data:image/png;base64,{logo_hub}" class="card-logo-img">' if logo_hub else '<i class="ri-rocket-line" style="font-size:4rem; color:#38B2AC;"></i>'
    st.markdown(f"""<div class="tool-card border-teal hover-spring animate-enter"><div class="card-logo-box">{img_tag}</div><div class="tool-desc-short">Adaptação de Provas e Materiais.</div></div>""", unsafe_allow_html=True)
    if st.button("➜ Acessar Hub", key="btn_hub", use_container_width=True): st.switch_page("pages/3_Hub_Inclusao.py")

# --- BENTO GRID ---
st.markdown("<div style='margin-top:40px;'></div>", unsafe_allow_html=True)
st.markdown("<div class='section-title animate-enter'><i class='ri-book-open-line'></i> Central de Conhecimento</div>", unsafe_allow_html=True)

st.markdown("""
<div class="bento-grid animate-enter">
    <a href="#" class="bento-item hover-spring">
        <div class="bento-icon" style="background:#EBF8FF; color:#3182CE;"><i class="ri-question-answer-line"></i></div>
        <div style="font-weight:800; color:#2D3748;">PEI vs PAEE</div>
        <div style="font-size:0.85rem; color:#718096; margin-top:5px;">Qual a diferença?</div>
    </a>
    <a href="https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2015/lei/l13146.htm" target="_blank" class="bento-item hover-spring">
        <div class="bento-icon" style="background:#FFFFF0; color:#D69E2E;"><i class="ri-scales-3-line"></i></div>
        <div style="font-weight:800; color:#2D3748;">LBI (Lei 13.146)</div>
        <div style="font-size:0.85rem; color:#718096; margin-top:5px;">Lei de Inclusão.</div>
    </a>
    <a href="https://institutoneurosaber.com.br/" target="_blank" class="bento-item hover-spring">
        <div class="bento-icon" style="background:#FFF5F7; color:#D53F8C;"><i class="ri-brain-line"></i></div>
        <div style="font-weight:800; color:#2D3748;">Neurociência</div>
        <div style="font-size:0.85rem; color:#718096; margin-top:5px;">Como o cérebro aprende.</div>
    </a>
    <a href="http://basenacionalcomum.mec.gov.br/" target="_blank" class="bento-item hover-spring">
        <div class="bento-icon" style="background:#F0FFF4; color:#38A169;"><i class="ri-compass-3-line"></i></div>
        <div style="font-weight:800; color:#2D3748;">BNCC</div>
        <div style="font-size:0.85rem; color:#718096; margin-top:5px;">Currículo Oficial.</div>
    </a>
</div>
""", unsafe_allow_html=True)

st.markdown("<div style='text-align: center; color: #CBD5E0; font-size: 0.8rem; margin-top: 60px; font-weight: 600;'>Omnisfera © 2026 - Tecnologia Assistiva & Inclusão</div>", unsafe_allow_html=True)
