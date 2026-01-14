import streamlit as st
import omni_utils as core  # Importa a nossa Matriz "Cérebro"
from openai import OpenAI
import time

# ==============================================================================
# 1. CONFIGURAÇÃO (Obrigatório ser a primeira linha)
# ==============================================================================
st.set_page_config(
    page_title="Omnisfera",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==============================================================================
# 2. INVOCANDO A MATRIZ (ESTILO, HEADER, SIDEBAR E LOGIN)
# ==============================================================================
# Isso carrega o Header de Vidro, a Sidebar Customizada e o CSS Base
core.aplicar_estilo_global()

# Verifica Segurança (Bloqueia o código se não logar)
if not core.verificar_acesso():
    st.stop()

# ==============================================================================
# 3. CSS ESPECÍFICO DO CONTEÚDO (BENTO GRID & MOTION)
# ==============================================================================
# Aqui colocamos APENAS o CSS que estiliza o Hero, os Cards e o Grid da Home.
# O CSS do Header e Sidebar já veio do omni_utils.
st.markdown("""
<style>
    /* --- ANIMAÇÕES TIPO FRAMER MOTION --- */
    .hover-spring {
        transition: transform 0.4s cubic-bezier(0.34, 1.56, 0.64, 1), box-shadow 0.3s ease;
    }
    .hover-spring:hover {
        transform: translateY(-8px) scale(1.01);
        box-shadow: 0 20px 40px rgba(0,0,0,0.08) !important;
        z-index: 10;
    }

    /* --- HERO SECTION --- */
    .dash-hero { 
        background: radial-gradient(circle at top right, #0F52BA, #062B61); 
        border-radius: 24px; margin-bottom: 40px; 
        box-shadow: 0 20px 40px -10px rgba(15, 82, 186, 0.4);
        color: white; position: relative; overflow: hidden;
        padding: 60px;
        display: flex; align-items: center; justify-content: flex-start;
        margin-top: 20px;
        border: 1px solid rgba(255,255,255,0.1);
    }
    .hero-title { font-family: 'Inter', sans-serif; font-weight: 800; font-size: 2.4rem; margin: 0; line-height: 1.1; margin-bottom: 15px; letter-spacing: -1px; }
    .hero-subtitle { font-family: 'Inter', sans-serif; font-size: 1.15rem; opacity: 0.9; font-weight: 400; max-width: 600px; }
    .hero-bg-icon { position: absolute; right: 30px; font-size: 10rem; opacity: 0.05; top: 10px; transform: rotate(-10deg); pointer-events: none; }

    /* --- TOOL CARDS (BENTO STYLE) --- */
    .tool-card { 
        background: white; border-radius: 24px; padding: 30px 25px; 
        box-shadow: 0 2px 10px rgba(0,0,0,0.02); border: 1px solid #E2E8F0; 
        height: 100%; display: flex; flex-direction: column; justify-content: space-between; 
        text-align: center; position: relative; overflow: hidden;
    }
    
    .card-logo-box { height: 90px; display: flex; align-items: center; justify-content: center; margin-bottom: 20px; }
    .card-logo-img { max-height: 85px; width: auto; object-fit: contain; filter: drop-shadow(0 10px 15px rgba(0,0,0,0.1)); }
    .tool-desc-short { font-size: 0.95rem; color: #718096; font-weight: 500; margin-bottom: 25px; min-height: 45px; line-height: 1.5; }
    
    /* Botões dentro dos cards */
    div[data-testid="column"] .stButton button {
        width: 100%; border-radius: 14px; border: none;
        background-color: #F1F5F9; color: #475569; font-family: 'Inter', sans-serif; font-weight: 700; 
        font-size: 0.95rem; padding: 14px 0; transition: all 0.3s ease;
        border: 1px solid transparent;
    }
    div[data-testid="column"] .stButton button:hover { 
        background-color: #3182CE; color: white; box-shadow: 0 8px 15px rgba(49, 130, 206, 0.25); transform: translateY(-2px);
    }
    
    .border-blue { border-bottom: 6px solid #3182CE; } 
    .border-purple { border-bottom: 6px solid #805AD5; } 
    .border-teal { border-bottom: 6px solid #38B2AC; }

    /* --- BENTO GRID (LINKS INFERIORES) --- */
    .bento-grid { 
        display: grid; 
        grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); 
        gap: 20px; margin-bottom: 40px; 
    }
    
    .bento-item { 
        background: white; border-radius: 20px; padding: 25px; 
        border: 1px solid #E2E8F0; 
        box-shadow: 0 4px 6px rgba(0,0,0,0.01); 
        text-decoration: none; color: inherit; 
        display: flex; flex-direction: column; align-items: center; text-align: center; 
        position: relative; overflow: hidden; height: 100%; 
    }
    
    .bento-icon { 
        width: 55px; height: 55px; border-radius: 18px; 
        display: flex; align-items: center; justify-content: center; 
        font-size: 1.6rem; margin-bottom: 15px; 
        transition: transform 0.3s ease;
    }
    .bento-item:hover .bento-icon { transform: scale(1.1) rotate(5deg); }
    
    .bento-title { font-weight: 800; font-size: 1.05rem; color: #1A202C; margin-bottom: 5px; }
    .bento-desc { font-size: 0.85rem; color: #718096; line-height: 1.4; }

    /* --- INSIGHT CARD --- */
    .insight-card-end { 
        background: linear-gradient(135deg, #FFFBEB 0%, #FFFFFF 100%); 
        border-radius: 20px; padding: 30px; 
        color: #2D3748; display: flex; align-items: center; gap: 30px; 
        box-shadow: 0 10px 25px rgba(214, 158, 46, 0.1); 
        border: 1px solid rgba(214, 158, 46, 0.2);
        margin-bottom: 30px; 
    }
    .insight-icon-end { 
        font-size: 2.2rem; color: #D69E2E; background: rgba(214, 158, 46, 0.1); 
        width: 70px; height: 70px; border-radius: 50%; 
        display: flex; align-items: center; justify-content: center;
    }

    .section-title { 
        font-family: 'Inter', sans-serif; font-weight: 800; font-size: 1.5rem; 
        color: #1A202C; margin-bottom: 30px; display: flex; align-items: center; gap: 12px; margin-top: 60px; 
    }
</style>
<link href="https://cdn.jsdelivr.net/npm/remixicon@4.1.0/fonts/remixicon.css" rel="stylesheet">
""", unsafe_allow_html=True)

# ==============================================================================
# 4. LÓGICA DE CONTEÚDO (IA & DADOS)
# ==============================================================================
# Recupera nome do usuário logado (gerenciado pelo omni_utils)
nome_display = st.session_state.get("usuario_nome", "Educador").split()[0]

# Banner Message
mensagem_banner = "Unindo ciência, dados e empatia para transformar a educação."
if 'OPENAI_API_KEY' in st.secrets:
    try:
        if 'banner_msg' not in st.session_state:
            client = OpenAI(api_key=st.secrets['OPENAI_API_KEY'])
            prompt_banner = f"Crie uma frase curta e inspiradora para {nome_display} sobre inclusão escolar. Máx 20 palavras."
            res = client.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "user", "content": prompt_banner}])
            st.session_state['banner_msg'] = res.choices[0].message.content
        mensagem_banner = st.session_state['banner_msg']
    except: pass

# ==============================================================================
# 5. RENDERIZAÇÃO DO DASHBOARD
# ==============================================================================

# --- HERO SECTION (MOTION) ---
st.markdown(f"""
<div class="dash-hero hover-spring">
    <div class="hero-text-block">
        <div class="hero-title">Olá, {nome_display}!</div>
        <div class="hero-subtitle">"{mensagem_banner}"</div>
    </div>
    <i class="ri-heart-pulse-fill hero-bg-icon"></i>
</div>
""", unsafe_allow_html=True)

# --- GRID DE FERRAMENTAS (BENTO CARDS) ---
st.markdown("<div class='section-title'><i class='ri-cursor-fill'></i> Acesso Rápido</div>", unsafe_allow_html=True)

# Usa o core.get_base64_image para pegar as imagens
logo_pei = core.get_base64_image("360.png")
logo_paee = core.get_base64_image("pae.png")
logo_hub = core.get_base64_image("hub.png")

col1, col2, col3 = st.columns(3)

# PEI
with col1:
    icon_pei = f'<img src="data:image/png;base64,{logo_pei}" class="card-logo-img">' if logo_pei else '<i class="ri-book-read-line" style="font-size:4rem; color:#3182CE;"></i>'
    st.markdown(f"""<div class="tool-card border-blue hover-spring"><div class="card-logo-box">{icon_pei}</div><div class="tool-desc-short">Avaliação, anamnese e geração do plano oficial do aluno.</div></div>""", unsafe_allow_html=True)
    if st.button("➜ Acessar PEI", key="btn_pei", use_container_width=True): st.switch_page("pages/1_PEI.py")

# PAEE
with col2:
    icon_paee = f'<img src="data:image/png;base64,{logo_paee}" class="card-logo-img">' if logo_paee else '<i class="ri-puzzle-line" style="font-size:4rem; color:#805AD5;"></i>'
    st.markdown(f"""<div class="tool-card border-purple hover-spring"><div class="card-logo-box">{icon_paee}</div><div class="tool-desc-short">Inteligência da Sala de Recursos e Tecnologias Assistivas.</div></div>""", unsafe_allow_html=True)
    if st.button("➜ Acessar PAEE", key="btn_paee", use_container_width=True): st.switch_page("pages/2_PAE.py")

# HUB
with col3:
    icon_hub = f'<img src="data:image/png;base64,{logo_hub}" class="card-logo-img">' if logo_hub else '<i class="ri-rocket-line" style="font-size:4rem; color:#38B2AC;"></i>'
    st.markdown(f"""<div class="tool-card border-teal hover-spring"><div class="card-logo-box">{icon_hub}</div><div class="tool-desc-short">Adaptação automática de provas e criação de roteiros.</div></div>""", unsafe_allow_html=True)
    if st.button("➜ Acessar Hub", key="btn_hub", use_container_width=True): st.switch_page("pages/3_Hub_Inclusao.py")

# --- RODAPÉ E INSIGHT (BENTO GRID REAL) ---
st.markdown("<div style='margin-top:50px;'></div>", unsafe_allow_html=True)
st.markdown("<div class='section-title'><i class='ri-book-mark-fill'></i> Base de Conhecimento</div>", unsafe_allow_html=True)

st.markdown("""
<div class="bento-grid">
    <a href="#" class="bento-item hover-spring">
        <div class="bento-icon" style="background:#EBF8FF; color:#3182CE;"><i class="ri-question-answer-line"></i></div>
        <div class="bento-title">PEI vs PAEE</div>
        <div class="bento-desc">Diferenças fundamentais.</div>
    </a>
    <a href="https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2015/lei/l13146.htm" target="_blank" class="bento-item hover-spring">
        <div class="bento-icon" style="background:#FFFFF0; color:#D69E2E;"><i class="ri-scales-3-line"></i></div>
        <div class="bento-title">Legislação</div>
        <div class="bento-desc">LBI e Decretos.</div>
    </a>
    <a href="https://institutoneurosaber.com.br/" target="_blank" class="bento-item hover-spring">
        <div class="bento-icon" style="background:#FFF5F7; color:#D53F8C;"><i class="ri-brain-line"></i></div>
        <div class="bento-title">Neurociência</div>
        <div class="bento-desc">Desenvolvimento atípico.</div>
    </a>
    <a href="http://basenacionalcomum.mec.gov.br/" target="_blank" class="bento-item hover-spring">
        <div class="bento-icon" style="background:#F0FFF4; color:#38A169;"><i class="ri-compass-3-line"></i></div>
        <div class="bento-title">BNCC</div>
        <div class="bento-desc">Currículo oficial.</div>
    </a>
</div>
""", unsafe_allow_html=True)

# Insight do Dia
noticia_insight = "A neuroplasticidade permite que o cérebro crie novos caminhos de aprendizado durante toda a vida."
if 'OPENAI_API_KEY' in st.secrets:
    try:
        if 'insight_dia' not in st.session_state:
            client = OpenAI(api_key=st.secrets['OPENAI_API_KEY'])
            res = client.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "user", "content": "Dica de 1 frase sobre neurociência para professores."}])
            st.session_state['insight_dia'] = res.choices[0].message.content
        noticia_insight = st.session_state['insight_dia']
    except: pass

st.markdown(f"""
<div class="insight-card-end hover-spring">
    <div class="insight-icon-end"><i class="ri-lightbulb-flash-line"></i></div>
    <div>
        <div style="font-weight: 800; font-size: 0.95rem; color: #D69E2E; letter-spacing: 0.5px; text-transform: uppercase;">Insight do Dia</div>
        <p style="margin:5px 0 0 0; font-size:1.05rem; opacity:0.9; color:#4A5568; font-style: italic; font-weight: 500;">"{noticia_insight}"</p>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("<div style='text-align: center; color: #CBD5E0; font-size: 0.8rem; margin-top: 60px; font-weight: 600;'>Omnisfera © 2026 - Tecnologia Assistiva & Inclusão</div>", unsafe_allow_html=True)
