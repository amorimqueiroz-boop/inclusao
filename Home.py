import streamlit as st
from datetime import date
from openai import OpenAI
import base64
import os

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
            .login-container { background-color: white; padding: 40px; border-radius: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); text-align: center; }
            .termo-box { background-color: #f8f9fa; padding: 15px; border-radius: 8px; height: 150px; overflow-y: scroll; font-size: 0.85rem; border: 1px solid #e9ecef; margin-bottom: 15px; text-align: left; }
        </style>
    """, unsafe_allow_html=True)

    if "autenticado" not in st.session_state:
        st.session_state["autenticado"] = False

    if not st.session_state["autenticado"]:
        c1, c2, c3 = st.columns([1, 2, 1])
        with c2:
            st.markdown("<div class='login-container'>", unsafe_allow_html=True)
            # Tenta carregar a logo completa ou o ícone para o login
            if os.path.exists("omni_icone.png"):
                st.image("omni_icone.png", width=100)
            st.markdown("### Acesso Restrito")
            st.markdown("---")
            st.markdown("##### 🛡️ Termo de Confidencialidade")
            st.markdown("""<div class="termo-box"><strong>AMBIENTE PROTEGIDO</strong><br>1. Propriedade Intelectual de Rodrigo A. Queiroz.<br>2. Proibido cópia ou engenharia reversa.<br>3. Uso exclusivo para testes autorizados.</div>""", unsafe_allow_html=True)
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
# 🏠 HOME - DASHBOARD OMNISFERA (ANIMATED HEADER)
# ==============================================================================

# CSS GERAL, CARDS E ANIMAÇÃO
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800&display=swap');
    html, body, [class*="css"] { font-family: 'Nunito', sans-serif; color: #2D3748; }
    
    /* --- ANIMAÇÃO DE ROTAÇÃO --- */
    @keyframes spin {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
    }
    
    .logo-container {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 15px; /* Espaço entre o círculo e o texto */
        margin-bottom: 25px;
        padding: 10px;
    }
    
    .logo-icon-spin {
        height: 90px; /* Tamanho do círculo */
        width: auto;
        animation: spin 20s linear infinite; /* Gira devagar e infinito */
        filter: drop-shadow(0 2px 4px rgba(0,0,0,0.1));
    }
    
    .logo-text-static {
        height: 60px; /* Tamanho do texto (ajuste proporcional) */
        width: auto;
    }

    /* --- HERO BANNER (MAIS ESTREITO/SLIM) --- */
    .dash-hero { 
        background: linear-gradient(135deg, #0F52BA 0%, #062B61 100%); 
        border-radius: 16px; 
        padding: 15px 30px; /* Padding reduzido na vertical (15px) */
        margin-bottom: 30px; 
        box-shadow: 0 4px 12px rgba(15, 82, 186, 0.2);
        color: white;
        position: relative;
        overflow: hidden;
        display: flex;
        align-items: center;
        justify-content: space-between;
        min-height: 100px; /* Altura mínima reduzida */
    }
    
    .hero-title {
        color: white;
        font-weight: 800;
        font-size: 1.8rem; /* Fonte um pouco menor para o banner slim */
        margin: 0;
        line-height: 1.1;
    }
    .hero-subtitle {
        color: rgba(255,255,255,0.9);
        font-size: 0.95rem;
        margin-top: 5px;
        font-weight: 600;
    }
    
    .hero-bg-icon {
        position: absolute;
        right: 20px;
        font-size: 4rem;
        opacity: 0.15;
        color: white;
        transform: rotate(-15deg);
    }

    /* --- BOTÕES DE FERRAMENTA --- */
    .tool-card {
        background-color: white;
        border-radius: 15px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        border: 1px solid #E2E8F0;
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        transition: transform 0.2s, box-shadow 0.2s;
    }
    .tool-card:hover { 
        transform: translateY(-5px); 
        border-color: #3182CE; 
        box-shadow: 0 15px 30px rgba(0,0,0,0.1);
    }
    .tool-title { font-size: 1.3rem; font-weight: 800; color: #2D3748; margin-bottom: 5px; }
    .tool-desc { font-size: 0.85rem; color: #718096; margin-bottom: 15px; line-height: 1.4; }
    
    .border-blue { border-top: 5px solid #3182CE; }
    .border-purple { border-top: 5px solid #805AD5; }
    .border-teal { border-top: 5px solid #38B2AC; }

    /* --- INSIGHT CARD --- */
    .insight-card {
        background-color: #FFFFF0;
        border-radius: 12px;
        padding: 15px 20px;
        color: #2D3748;
        display: flex;
        align-items: center;
        gap: 15px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        border-left: 5px solid #D69E2E;
        margin-top: 15px;
        margin-bottom: 30px;
    }
    .insight-icon {
        font-size: 1.5rem;
        color: #D69E2E;
        background: rgba(214, 158, 46, 0.15);
        width: 40px; height: 40px;
        border-radius: 50%;
        display: flex; align-items: center; justify-content: center;
    }

    /* --- CARDS INFORMATIVOS --- */
    .home-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 20px;
    }
    .rich-card {
        background: white;
        border-radius: 12px;
        padding: 20px;
        border: 1px solid #E2E8F0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
        transition: all 0.2s ease;
        text-decoration: none;
        color: inherit;
        display: flex;
        flex-direction: column;
        align-items: center;
        text-align: center;
        position: relative;
        overflow: hidden;
        height: 100%;
    }
    .rich-card:hover { transform: translateY(-3px); box-shadow: 0 8px 16px rgba(0,0,0,0.06); }
    .rich-card-top { width: 100%; height: 4px; position: absolute; top: 0; left: 0; }
    .rc-icon { width: 50px; height: 50px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 1.5rem; margin-bottom: 12px; }
    .rc-title { font-weight: 800; font-size: 1rem; color: #2D3748; margin-bottom: 5px; }
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

# --- 1. CABEÇALHO COM ANIMAÇÃO ---
icone_b64 = get_base64_image("omni_icone.png")
texto_b64 = get_base64_image("omni_texto.png")

# Se os arquivos existirem, monta o header animado. Se não, fallback texto.
if icone_b64 and texto_b64:
    st.markdown(f"""
    <div class="logo-container">
        <img src="data:image/png;base64,{icone_b64}" class="logo-icon-spin">
        <img src="data:image/png;base64,{texto_b64}" class="logo-text-static">
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown("<h1 style='text-align: center; color: #0F52BA; font-size: 3rem;'>🌐 OMNISFERA</h1>", unsafe_allow_html=True)


# --- 2. HERO BANNER (SLIM & AZUL) ---
st.markdown(f"""
<div class="dash-hero">
    <div style="z-index: 2;">
        <h1 class="hero-title">Olá, Educador(a)!</h1>
        <p class="hero-subtitle">"Cada criança é única; seu potencial, ilimitado!"</p>
    </div>
    <i class="ri-heart-pulse-fill hero-bg-icon"></i>
</div>
""", unsafe_allow_html=True)

# --- 3. FERRAMENTAS DE ACESSO ---
st.markdown("### 🎯 Acesso Rápido")
col1, col2, col3 = st.columns(3)

# PEI
with col1:
    st.markdown("""
    <div class="tool-card border-blue">
        <div>
            <div class="tool-title"><i class="ri-book-read-line" style="color:#3182CE; margin-right:5px;"></i> PEI 360º</div>
            <div class="tool-desc">
                <strong>Plano de Ensino Individualizado</strong><br>
                A porta de entrada. Realize a anamnese e gere o documento oficial.
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Acessar PEI ➡️", key="btn_pei", use_container_width=True):
        st.switch_page("pages/1_PEI.py")

# PAE
with col2:
    st.markdown("""
    <div class="tool-card border-purple">
        <div>
            <div class="tool-title"><i class="ri-puzzle-line" style="color:#805AD5; margin-right:5px;"></i> PAE</div>
            <div class="tool-desc">
                <strong>Plano de AEE</strong><br>
                Focado na Sala de Recursos. Identifique barreiras e tecnologias assistivas.
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Acessar PAE ➡️", key="btn_pae", use_container_width=True):
        st.switch_page("pages/2_PAE.py")

# HUB
with col3:
    st.markdown("""
    <div class="tool-card border-teal">
        <div>
            <div class="tool-title"><i class="ri-rocket-line" style="color:#38B2AC; margin-right:5px;"></i> Hub</div>
            <div class="tool-desc">
                <strong>Adaptação & Criação</strong><br>
                Adapte provas, crie atividades do zero e roteiros de aula num clique.
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Acessar Hub ➡️", key="btn_hub", type="primary", use_container_width=True):
        st.switch_page("pages/3_Hub_Inclusao.py")

# --- 4. INSIGHT DO DIA ---
st.markdown(f"""
<div class="insight-card">
    <div class="insight-icon"><i class="ri-lightbulb-flash-line"></i></div>
    <div>
        <h4 style="margin:0; color:#2D3748;">Insight do Dia</h4>
        <p style="margin:5px 0 0 0; font-size:0.95rem; opacity:0.9; color:#4A5568;">{noticia}</p>
    </div>
</div>
""", unsafe_allow_html=True)

# --- 5. RECURSOS EDUCATIVOS (CARDS INFORMATIVOS) ---
st.markdown("### 📚 Base de Conhecimento")
st.markdown("""
<div class="home-grid">
    <a href="#" class="rich-card">
        <div class="rich-card-top" style="background-color: #3182CE;"></div>
        <div class="rc-icon" style="background-color:#EBF8FF; color:#3182CE;"><i class="ri-question-answer-line"></i></div>
        <div class="rc-title">O que é PEI e PAE?</div>
        <div class="rc-desc">Entenda as diferenças fundamentais e como cada um apoia o aluno.</div>
    </a>
    <a href="https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2015/lei/l13146.htm" target="_blank" class="rich-card">
        <div class="rich-card-top" style="background-color: #D69E2E;"></div>
        <div class="rc-icon" style="background-color:#FFFFF0; color:#D69E2E;"><i class="ri-scales-3-line"></i></div>
        <div class="rc-title">Legislação</div>
        <div class="rc-desc">Lei Brasileira de Inclusão e Decretos atualizados (2025).</div>
    </a>
    <a href="https://institutoneurosaber.com.br/" target="_blank" class="rich-card">
        <div class="rich-card-top" style="background-color: #D53F8C;"></div>
        <div class="rc-icon" style="background-color:#FFF5F7; color:#D53F8C;"><i class="ri-brain-line"></i></div>
        <div class="rc-title">Neurociência</div>
        <div class="rc-desc">Como o cérebro atípico aprende? Artigos e estudos.</div>
    </a>
    <a href="http://basenacionalcomum.mec.gov.br/" target="_blank" class="rich-card">
        <div class="rich-card-top" style="background-color: #38A169;"></div>
        <div class="rc-icon" style="background-color:#F0FFF4; color:#38A169;"><i class="ri-compass-3-line"></i></div>
        <div class="rc-title">BNCC</div>
        <div class="rc-desc">Currículo oficial, competências e habilidades.</div>
    </a>
</div>
""", unsafe_allow_html=True)

st.markdown("---")
st.markdown("<div style='text-align: center; color: #A0AEC0; font-size: 0.8rem;'>Omnisfera © 2026 - Todos os direitos reservados.</div>", unsafe_allow_html=True)
