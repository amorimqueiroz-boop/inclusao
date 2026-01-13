import streamlit as st
from datetime import date
from openai import OpenAI
import base64
import os
import time

# --- 1. CONFIGURAÇÃO INICIAL ---
st.set_page_config(
    page_title="Omnisfera | Ecossistema Inclusivo", 
    page_icon="🌐", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==============================================================================
# 🔐 SEGURANÇA & UTILITÁRIOS
# ==============================================================================
def get_base64_image(image_path):
    if not os.path.exists(image_path): return ""
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

def sistema_seguranca():
    st.markdown("""
        <style>
            [data-testid="stHeader"] {visibility: hidden !important; height: 0px !important;}
            footer {visibility: hidden !important;}
            .login-container { background-color: white; padding: 40px; border-radius: 15px; box-shadow: 0 10px 25px rgba(0,0,0,0.1); text-align: center; border: 1px solid #E2E8F0; }
            .termo-box { background-color: #F7FAFC; padding: 15px; border-radius: 8px; height: 160px; overflow-y: scroll; font-size: 0.8rem; border: 1px solid #CBD5E0; margin-bottom: 20px; text-align: left; color: #4A5568; }
        </style>
    """, unsafe_allow_html=True)

    if "autenticado" not in st.session_state:
        st.session_state["autenticado"] = False

    if not st.session_state["autenticado"]:
        c1, c2, c3 = st.columns([1, 2, 1])
        with c2:
            st.markdown("<div class='login-container'>", unsafe_allow_html=True)
            try: 
                if os.path.exists("ominisfera.png"): st.image("ominisfera.png", width=280)
                else: st.markdown("## 🌐 OMNISFERA")
            except: st.markdown("## 🌐 OMNISFERA")
            
            st.markdown("### Portal de Acesso")
            st.markdown("---")
            st.markdown("##### 🛡️ Termo de Confidencialidade")
            st.markdown("""<div class="termo-box"><strong>AMBIENTE PROTEGIDO</strong><br><br>1. <strong>Propriedade:</strong> Todo o conteúdo e inteligência deste software são propriedade de Rodrigo A. Queiroz.<br>2. <strong>Sigilo:</strong> É vedada a divulgação de prints, lógicas ou prompts.<br>3. <strong>Uso:</strong> Acesso concedido exclusivamente para fins de desenvolvimento e validação.</div>""", unsafe_allow_html=True)
            concordo = st.checkbox("Li e aceito os termos.")
            senha = st.text_input("Senha:", type="password")
            if st.button("🚀 ENTRAR", type="primary", use_container_width=True):
                hoje = date.today()
                senha_correta = "PEI_START_2026" if hoje <= date(2026, 1, 19) else "OMNI_PRO"
                if not concordo: st.warning("Aceite os termos.")
                elif senha == senha_correta:
                    st.session_state["autenticado"] = True
                    st.rerun()
                else: st.error("Senha inválida.")
            st.markdown("</div>", unsafe_allow_html=True)
        return False
    return True

if not sistema_seguranca(): st.stop()

# ==============================================================================
# 🏠 HOME - DASHBOARD OMNISFERA (ECOSYSTEM EDITION)
# ==============================================================================

# CSS GERAL
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Nunito:wght@300;400;600;700;800&display=swap');
    html, body, [class*="css"] { font-family: 'Nunito', sans-serif; color: #2D3748; }
    
    /* 1. ESPAÇAMENTO DO TOPO */
    .block-container { 
        padding-top: 1rem !important; 
        padding-bottom: 3rem !important; 
        margin-top: 0rem !important;
    }

    /* --- LOGO GIGANTE ANIMADA --- */
    @keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
    
    .logo-container {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 20px; 
        margin-bottom: 20px; 
        padding-top: 10px;
    }
    .logo-icon-spin {
        height: 130px; 
        width: auto;
        animation: spin 40s linear infinite; /* Rotação bem lenta e elegante */
        filter: drop-shadow(0 4px 8px rgba(0,0,0,0.1));
    }
    .logo-text-static {
        height: 85px; 
        width: auto;
    }

    /* --- HERO BANNER (SLIM & LEFT) --- */
    .dash-hero { 
        background: linear-gradient(135deg, #0F52BA 0%, #062B61 100%); 
        border-radius: 20px;
        margin-bottom: 30px;
        box-shadow: 0 10px 25px rgba(15, 82, 186, 0.25);
        color: white;
        position: relative;
        overflow: hidden;
        padding: 35px 50px; 
        display: flex;
        align-items: center;
        justify-content: flex-start;
    }
    
    .hero-text-block { z-index: 2; text-align: left; }

    .hero-title {
        color: white; 
        font-family: 'Nunito', sans-serif;
        font-weight: 800; 
        font-size: 2rem; 
        margin: 0; 
        line-height: 1.1;
        letter-spacing: 0.5px;
    }
    .hero-subtitle {
        color: rgba(255,255,255,0.9);
        font-size: 1.05rem;
        margin-top: 5px; 
        font-weight: 400; 
    }
    
    .hero-bg-icon {
        position: absolute; 
        right: 30px; 
        font-size: 5rem;
        opacity: 0.1; 
        color: white; 
        transform: rotate(-15deg);
        top: 20px;
    }

    /* --- CONCEITO OMNISFERA (MANIFESTO) --- */
    .manifesto-box {
        text-align: center;
        margin-bottom: 40px;
        padding: 0 10%;
    }
    .manifesto-title {
        font-size: 1.2rem;
        color: #2D3748;
        font-weight: 800;
        margin-bottom: 10px;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .manifesto-text {
        font-size: 1.15rem;
        color: #4A5568;
        font-weight: 400;
        line-height: 1.6;
        font-style: italic;
    }
    .highlight { color: #0F52BA; font-weight: 700; font-style: normal; }

    /* --- CARDS DE FERRAMENTA (COM LOGOS) --- */
    .tool-card { 
        background: white; 
        border-radius: 20px; 
        padding: 25px; 
        box-shadow: 0 4px 10px rgba(0,0,0,0.03); 
        border: 1px solid #E2E8F0; 
        height: 100%; 
        display: flex; flex-direction: column; justify-content: flex-start; /* Alinha topo */
        transition: all 0.3s ease; 
        text-align: center;
    }
    .tool-card:hover { 
        transform: translateY(-8px); 
        border-color: #3182CE; 
        box-shadow: 0 15px 30px rgba(0,0,0,0.1); 
    }
    
    .card-logo-box {
        height: 70px;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-bottom: 15px;
    }
    .card-logo-img {
        max-height: 65px;
        width: auto;
        object-fit: contain;
    }
    
    .tool-title { font-size: 1.2rem; font-weight: 800; color: #2D3748; margin-bottom: 8px; }
    .tool-desc { font-size: 0.9rem; color: #718096; margin-bottom: 25px; line-height: 1.5; }
    
    /* Bordas de cor */
    .border-blue { border-bottom: 5px solid #3182CE; } 
    .border-purple { border-bottom: 5px solid #805AD5; } 
    .border-teal { border-bottom: 5px solid #38B2AC; }

    /* --- INSIGHT CARD --- */
    .insight-card {
        background-color: #FFFFF0;
        border-radius: 12px;
        padding: 20px 25px;
        color: #2D3748;
        display: flex; align-items: center; gap: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        border-left: 5px solid #F6E05E; 
        margin-bottom: 40px;
        margin-top: 10px;
    }
    .insight-icon { font-size: 1.8rem; color: #D69E2E; }

    /* --- RODAPÉ --- */
    .home-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; }
    .rich-card { background: white; border-radius: 12px; padding: 20px; border: 1px solid #E2E8F0; box-shadow: 0 2px 4px rgba(0,0,0,0.02); transition: all 0.2s; text-decoration: none; color: inherit; display: flex; flex-direction: column; align-items: center; text-align: center; position: relative; overflow: hidden; height: 100%; }
    .rich-card:hover { transform: translateY(-3px); box-shadow: 0 8px 16px rgba(0,0,0,0.06); border-color: #CBD5E0; }
    .rich-card-top { width: 100%; height: 4px; position: absolute; top: 0; left: 0; }
    .rc-icon { width: 45px; height: 45px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 1.4rem; margin-bottom: 12px; }
    .rc-title { font-weight: 700; font-size: 1rem; color: #2D3748; margin-bottom: 5px; }
    .rc-desc { font-size: 0.8rem; color: #718096; line-height: 1.3; }
</style>
<link href="https://cdn.jsdelivr.net/npm/remixicon@4.1.0/fonts/remixicon.css" rel="stylesheet">
""", unsafe_allow_html=True)

# FRASE DO DIA (IA)
noticia = "A neurociência na escola revela como o aprendizado é moldado pelo cérebro, otimizando o ensino para cada aluno."
if 'OPENAI_API_KEY' in st.secrets:
    try:
        if 'home_insight' not in st.session_state:
            client = OpenAI(api_key=st.secrets['OPENAI_API_KEY'])
            res = client.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "user", "content": "Curiosidade curtíssima sobre neurociência na educação."}])
            st.session_state['home_insight'] = res.choices[0].message.content
        noticia = st.session_state['home_insight']
    except: pass

# --- 1. CABEÇALHO LOGO GIGANTE ANIMADA ---
icone_b64 = get_base64_image("omni_icone.png")
texto_b64 = get_base64_image("omni_texto.png")

if icone_b64 and texto_b64:
    st.markdown(f"""
    <div class="logo-container">
        <img src="data:image/png;base64,{icone_b64}" class="logo-icon-spin">
        <img src="data:image/png;base64,{texto_b64}" class="logo-text-static">
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown("<h1 style='text-align: center; color: #0F52BA; font-size: 3rem; margin-bottom:10px;'>🌐 OMNISFERA</h1>", unsafe_allow_html=True)


# --- 2. HERO BANNER (TEXTO ESQUERDA + ELEGÂNCIA) ---
st.markdown("""
<div class="dash-hero">
    <div class="hero-text-block">
        <div class="hero-title">Olá, Educador(a)!</div>
        <div class="hero-subtitle">"Cada criança é única; seu potencial, ilimitado!"</div>
    </div>
    <i class="ri-heart-pulse-fill hero-bg-icon"></i>
</div>
""", unsafe_allow_html=True)

# --- 3. MANIFESTO OMNISFERA (CONCEITO) ---
st.markdown("""
<div class="manifesto-box">
    <div class="manifesto-text">
        "A Omnisfera não é apenas uma plataforma. É um ecossistema vivo onde a <span class="highlight">Neurociência</span> encontra a <span class="highlight">Pedagogia</span>.<br>
        Do PEI na sala de aula ao PAE na clínica, conectamos dados, empatia e estratégia para que a inclusão deixe de ser um desafio e se torne a nossa linguagem universal."
    </div>
</div>
""", unsafe_allow_html=True)

# --- 4. FERRAMENTAS DE ACESSO (COM LOGOS) ---
# Preparar logos
logo_pei = get_base64_image("360.png")
logo_pae = get_base64_image("pae.png")
logo_hub = get_base64_image("hub.png")

# Fallback icons se não tiver imagem
icon_pei = f'<img src="data:image/png;base64,{logo_pei}" class="card-logo-img">' if logo_pei else '<i class="ri-book-read-line" style="font-size:3rem; color:#3182CE;"></i>'
icon_pae = f'<img src="data:image/png;base64,{logo_pae}" class="card-logo-img">' if logo_pae else '<i class="ri-puzzle-line" style="font-size:3rem; color:#805AD5;"></i>'
icon_hub = f'<img src="data:image/png;base64,{logo_hub}" class="card-logo-img">' if logo_hub else '<i class="ri-rocket-line" style="font-size:3rem; color:#38B2AC;"></i>'

col1, col2, col3 = st.columns(3)

# PEI
with col1:
    st.markdown(f"""
    <div class="tool-card border-blue">
        <div class="card-logo-box">{icon_pei}</div>
        <div>
            <div class="tool-title">PEI 360º</div>
            <div class="tool-desc">
                O coração da inclusão escolar. Avalie, planeje e gere o documento oficial do aluno.
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Acessar PEI ➡️", key="btn_pei", use_container_width=True):
        st.switch_page("pages/1_PEI.py")

# PAE
with col2:
    st.markdown(f"""
    <div class="tool-card border-purple">
        <div class="card-logo-box">{icon_pae}</div>
        <div>
            <div class="tool-title">PAE Clínico</div>
            <div class="tool-desc">
                A inteligência da Sala de Recursos. Mapeie barreiras e tecnologias assistivas.
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Acessar PAE ➡️", key="btn_pae", use_container_width=True):
        st.switch_page("pages/2_PAE.py")

# HUB
with col3:
    st.markdown(f"""
    <div class="tool-card border-teal">
        <div class="card-logo-box">{icon_hub}</div>
        <div>
            <div class="tool-title">Hub Criativo</div>
            <div class="tool-desc">
                Adaptação em segundos. Provas, atividades e roteiros gerados por IA.
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Acessar Hub ➡️", key="btn_hub", type="primary", use_container_width=True):
        st.switch_page("pages/3_Hub_Inclusao.py")

# --- 5. INSIGHT DO DIA ---
st.markdown(f"""
<div class="insight-card">
    <div class="insight-icon"><i class="ri-lightbulb-flash-line"></i></div>
    <div>
        <div style="font-weight: 700; font-size: 0.9rem; color: #D69E2E;">Insight do Dia (IA):</div>
        <p style="margin:2px 0 0 0; font-size:0.95rem; opacity:0.9; color:#4A5568;">"{noticia}"</p>
    </div>
</div>
""", unsafe_allow_html=True)

# --- 6. RODAPÉ EDU
