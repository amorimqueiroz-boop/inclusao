import streamlit as st
from datetime import date
from openai import OpenAI
import base64
import os
import time

# ==============================================================================
# 1. CONFIGURAÇÃO INICIAL E AMBIENTE
# ==============================================================================
APP_VERSION = "v116.0"

# Detecção de Ambiente (Secrets)
try:
    IS_TEST_ENV = st.secrets.get("ENV") == "TESTE"
except:
    IS_TEST_ENV = False

# Configurações da Página
titulo_pag = "[TESTE] Omnisfera" if IS_TEST_ENV else "Omnisfera | Ecossistema"
icone_pag = "omni_icone.png" if os.path.exists("omni_icone.png") else "🌐"

st.set_page_config(
    page_title=titulo_pag,
    page_icon=icone_pag,
    layout="wide",
    initial_sidebar_state="expanded" 
)

# ==============================================================================
# 2. UTILITÁRIOS E CORES
# ==============================================================================
def get_base64_image(image_path):
    if not os.path.exists(image_path): return ""
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

# Definição de Cores
if IS_TEST_ENV:
    card_bg = "rgba(255, 220, 50, 0.95)" 
    card_border = "rgba(200, 160, 0, 0.5)"
    display_text = "OMNISFERA | TESTE"
    footer_visibility = "visible" 
else:
    card_bg = "rgba(255, 255, 255, 0.85)"
    card_border = "rgba(255, 255, 255, 0.6)"
    display_text = f"OMNISFERA {APP_VERSION}"
    footer_visibility = "hidden"

# ==============================================================================
# 3. CSS GLOBAL (HEADER FIXO)
# ==============================================================================
css_estatico = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Nunito:wght@400;600;700&display=swap');
    
    html { scroll-behavior: smooth; }
    html, body, [class*="css"] { 
        font-family: 'Nunito', sans-serif; 
        color: #2D3748; 
        background-color: #F7FAFC;
    }

    /* Animações */
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    @keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }

    .hover-spring { transition: transform 0.4s cubic-bezier(0.34, 1.56, 0.64, 1), box-shadow 0.3s ease; }
    .hover-spring:hover { transform: translateY(-5px) scale(1.01); box-shadow: 0 15px 30px rgba(0,0,0,0.08) !important; z-index: 10; }

    /* Espaço para não esconder conteúdo atrás do header fixo */
    .block-container { 
        padding-top: 140px !important; 
        padding-bottom: 2rem !important; 
        margin-top: 0rem !important;
        animation: fadeInUp 0.8s cubic-bezier(0.2, 0.8, 0.2, 1);
    }

    /* --- HEADER FIXO (GLASSMORPHISM) --- */
    .logo-container {
        display: flex; align-items: center; justify-content: flex-start; 
        gap: 20px; 
        position: fixed; /* VOLTOU PARA FIXED */
        top: 0; left: 0; width: 100%; height: 100px;
        background-color: rgba(247, 250, 252, 0.85); /* Fundo semi-transparente */
        backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px); /* Efeito de vidro */
        border-bottom: 1px solid rgba(255, 255, 255, 0.5);
        z-index: 9999; 
        box-shadow: 0 4px 20px rgba(0,0,0,0.03);
        padding-left: 40px;
    }
    .header-subtitle-text {
        font-family: 'Nunito', sans-serif; font-weight: 600; font-size: 1.15rem;
        color: #718096; border-left: 2px solid #CBD5E0; padding-left: 20px;
        height: 50px; display: flex; align-items: center; letter-spacing: -0.3px;
    }
    .logo-icon-spin { height: 85px; width: auto; animation: spin 45s linear infinite; filter: drop-shadow(0 4px 8px rgba(0,0,0,0.1)); }
    .logo-text-static { height: 50px; width: auto; }

    /* Login Styles */
    .login-container { 
        background-color: white; padding: 40px 40px 50px 40px; 
        border-radius: 24px; box-shadow: 0 20px 50px rgba(0,0,0,0.08); 
        text-align: center; border: 1px solid #E2E8F0; 
        max-width: 500px; margin: 0 auto; margin-top: 60px;
        animation: fadeInUp 0.8s ease-out;
    }
    .login-logo-spin { height: 100px; width: auto; animation: spin 45s linear infinite; margin-bottom: 10px; }
    .login-logo-static { height: 60px; width: auto; margin-left: 10px; }
    .logo-wrapper { display: flex; justify-content: center; align-items: center; margin-bottom: 25px; }
    .manifesto-login { font-family: 'Nunito', sans-serif; font-size: 0.95rem; color: #64748B; font-style: italic; line-height: 1.6; margin-bottom: 30px; }
    
    /* Inputs */
    .stTextInput input { border-radius: 12px !important; border: 1px solid #E2E8F0 !important; padding: 12px !important; background-color: #F8FAFC !important; }
    .stTextInput input:focus { border-color: #3182CE !important; box-shadow: 0 0 0 3px rgba(49, 130, 206, 0.1); }
    
    /* --- BENTO GRID & CARDS --- */
    
    .dash-hero { 
        background: radial-gradient(circle at top right, #0F52BA, #062B61); 
        border-radius: 20px; 
        margin-bottom: 30px; 
        margin-top: 10px;
        box-shadow: 0 20px 40px -10px rgba(15, 82, 186, 0.4);
        color: white; position: relative; overflow: hidden; 
        padding: 40px 50px; 
        display: flex; align-items: center; justify-content: flex-start;
        border: 1px solid rgba(255,255,255,0.1);
    }
    .hero-title { 
        font-family: 'Inter', sans-serif; 
        font-weight: 700; font-size: 1.8rem; 
        margin: 0; line-height: 1.2; margin-bottom: 8px; 
    }
    .hero-subtitle { 
        font-family: 'Inter', sans-serif; 
        font-size: 1rem; opacity: 0.9; font-weight: 400; 
    }
    .hero-bg-icon { position: absolute; right: 30px; font-size: 8rem; opacity: 0.05; top: 10px; transform: rotate(-10deg); }

    .tool-card { 
        background: white; border-radius: 20px; padding: 25px 20px; 
        box-shadow: 0 2px 10px rgba(0,0,0,0.02); border: 1px solid #E2E8F0; 
        height: 100%; display: flex; flex-direction: column; justify-content: space-between; 
        text-align: center; position: relative; overflow: hidden;
    }
    .card-logo-box { height: 80px; display: flex; align-items: center; justify-content: center; margin-bottom: 15px; }
    .card-logo-img { max-height: 75px; width: auto; object-fit: contain; }
    .tool-desc-short { font-size: 0.9rem; color: #718096; font-weight: 500; margin-bottom: 20px; min-height: 40px; line-height: 1.4; }
    
    .border-blue { border-bottom: 5px solid #3182CE; } 
    .border-purple { border-bottom: 5px solid #805AD5; } 
    .border-teal { border-bottom: 5px solid #38B2AC; }

    /* BENTO GRID */
    .bento-grid { 
        display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); 
        gap: 15px; margin-bottom: 30px; 
    }
    .bento-item { 
        background: white; border-radius: 16px; padding: 20px; border: 1px solid #E2E8F0; 
        box-shadow: 0 4px 6px rgba(0,0,0,0.01); text-decoration: none; color: inherit; 
        display: flex; flex-direction: column; align-items: center; text-align: center; 
        position: relative; overflow: hidden; height: 100%; 
    }
    .bento-icon { 
        width: 45px; height: 45px; border-radius: 14px; display: flex; align-items: center; justify-content: center; 
        font-size: 1.4rem; margin-bottom: 12px; transition: transform 0.3s ease;
    }
    .bento-item:hover .bento-icon { transform: scale(1.1) rotate(5deg); }
    .bento-title { font-weight: 700; font-size: 0.95rem; color: #1A202C; margin-bottom: 4px; }
    .bento-desc { font-size: 0.8rem; color: #718096; line-height: 1.3; }

    /* Insight Card */
    .insight-card-end { 
        background: linear-gradient(135deg, #FFFBEB 0%, #FFFFFF 100%); 
        border-radius: 16px; padding: 25px; 
        color: #2D3748; display: flex; align-items: center; gap: 20px; 
        box-shadow: 0 10px 25px rgba(214, 158, 46, 0.1); 
        border: 1px solid rgba(214, 158, 46, 0.2); margin-bottom: 20px; 
    }
    .insight-icon-end { 
        font-size: 1.8rem; color: #D69E2E; background: rgba(214, 158, 46, 0.1); 
        width: 60px; height: 60px; border-radius: 50%; display: flex; align-items: center; justify-content: center;
    }
    .section-title { 
        font-family: 'Inter', sans-serif; font-weight: 700; font-size: 1.3rem; 
        color: #1A202C; margin-bottom: 20px; display: flex; align-items: center; gap: 10px; margin-top: 40px; 
    }

    /* Hide Default Streamlit Elements */
    [data-testid="stHeader"] { visibility: hidden !important; height: 0px !important; }
    [data-testid="stToolbar"] { visibility: hidden !important; display: none !important; }
</style>
<link href="https://cdn.jsdelivr.net/npm/remixicon@4.1.0/fonts/remixicon.css" rel="stylesheet">
"""
st.markdown(css_estatico, unsafe_allow_html=True)

# CSS DINÂMICO
st.markdown(f"""
<style>
    .omni-badge {{
        position: fixed; top: 20px; right: 20px;
        background: {card_bg}; border: 1px solid {card_border};
        backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px);
        padding: 6px 20px; min-width: 180px; border-radius: 14px;
        box-shadow: 0 8px 20px rgba(0,0,0,0.06); z-index: 999990;
        display: flex; align-items: center; justify-content: center;
        pointer-events: none; transition: transform 0.3s ease;
    }}
    .omni-text {{
        font-family: 'Inter', sans-serif; font-weight: 800; font-size: 0.65rem;
        color: #2D3748; letter-spacing: 2px; text-transform: uppercase;
    }}
    footer {{ visibility: {footer_visibility} !important; }}
    
    div[data-testid="column"] .stButton button {{
        width: 100%; border-radius: 12px !important; border: none !important;
        font-family: 'Inter', sans-serif; font-weight: 700 !important; font-size: 0.9rem !important;
        padding: 12px 0; transition: all 0.3s ease;
        background-color: #F1F5F9; color: #475569;
    }}
    div[data-testid="column"] .stButton button:hover {{ 
        background-color: #3182CE !important; color: white !important; 
        box-shadow: 0 8px 15px rgba(49, 130, 206, 0.25); transform: translateY(-2px);
    }}
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# 4. SISTEMA DE SEGURANÇA E LOGIN
# ==============================================================================
def sistema_seguranca():
    if "autenticado" not in st.session_state:
        st.session_state["autenticado"] = False

    if not st.session_state["autenticado"]:
        
        st.markdown("""
        <style>
            section[data-testid="stSidebar"] { display: none !important; }
            [data-testid="stSidebarCollapsedControl"] { display: none !important; }
        </style>
        """, unsafe_allow_html=True)

        btn_text = "🚀 ENTRAR (TESTE)" if IS_TEST_ENV else "🔒 ACESSAR OMNISFERA"
        btn_color = "#E65100" if IS_TEST_ENV else "#0F52BA"

        st.markdown(f"""
        <style>
            div.stButton > button {{
                background-color: {btn_color} !important; color: white !important; height: 50px !important;
            }}
            .login-container {{ border-color: #E2E8F0 !important; }}
        </style>
        """, unsafe_allow_html=True)

        c1, c_login, c2 = st.columns([1, 2, 1])
        
        with c_login:
            st.markdown("<div class='login-container'>", unsafe_allow_html=True)
            
            icone_b64_login = get_base64_image("omni_icone.png")
            texto_b64_login = get_base64_image("omni_texto.png")
            
            if icone_b64_login and texto_b64_login:
                st.markdown(f"""
                <div class="logo-wrapper">
                    <img src="data:image/png;base64,{icone_b64_login}" class="login-logo-spin">
                    <img src="data:image/png;base64,{texto_b64_login}" class="login-logo-static">
                </div>""", unsafe_allow_html=True)
            else:
                st.markdown(f"<h2 style='color:#0F52BA; margin:0; margin-bottom:10px;'>OMNISFERA</h2>", unsafe_allow_html=True)

            st.markdown("""<div class="manifesto-login">"A Omnisfera é um ecossistema vivo onde a <strong>Neurociência</strong> encontra a <strong>Pedagogia</strong>."</div>""", unsafe_allow_html=True)
            
            if IS_TEST_ENV:
                with st.expander("📝 Dados (Opcional)"):
                    nome_user = st.text_input("nome_fake", placeholder="Nome", label_visibility="collapsed")
                    cargo_user = st.text_input("cargo_fake", placeholder="Cargo", label_visibility="collapsed")
            else:
                st.markdown("<div style='text-align:left; font-weight:700; color:#475569; font-size:0.9rem; margin-bottom:5px;'>Identificação</div>", unsafe_allow_html=True)
                nome_user = st.text_input("nome_real", placeholder="Seu Nome", label_visibility="collapsed")
                st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
                cargo_user = st.text_input("cargo_real", placeholder="Seu Cargo", label_visibility="collapsed")
                st.markdown("---")
                st.caption("ℹ️ Software em fase Beta. Uso restrito.")
                concordo = st.checkbox("Concordo com os termos.")
                st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
                senha = st.text_input("senha_real", type="password", placeholder="Senha", label_visibility="collapsed")

            st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
            
            if st.button(btn_text):
                if IS_TEST_ENV:
                    st.session_state["autenticado"] = True
                    st.session_state["usuario_nome"] = nome_user if nome_user else "Visitante Teste"
                    st.session_state["usuario_cargo"] = cargo_user if cargo_user else "Dev"
                    st.rerun()
                else:
                    hoje = date.today()
                    senha_mestra = "PEI_START_2026" if hoje <= date(2026, 1, 19) else "OMNI_PRO"
                    if not concordo: st.warning("Aceite os termos.")
                    elif not nome_user or not cargo_user: st.warning("Preencha seus dados.")
                    elif senha != senha_mestra: st.error("Senha incorreta.")
                    else:
                        st.session_state["autenticado"] = True
                        st.session_state["usuario_nome"] = nome_user
                        st.session_state["usuario_cargo"] = cargo_user
                        st.rerun()
            
            st.markdown("</div>", unsafe_allow_html=True)
        return False
    return True

if not sistema_seguranca(): st.stop()

# ==============================================================================
# 5. CONTEÚDO DA HOME (SÓ CARREGA APÓS LOGIN)
# ==============================================================================

# CARD OMNISFERA (Canto Direito)
st.markdown(f"""<div class="omni-badge hover-spring"><span class="omni-text">{display_text}</span></div>""", unsafe_allow_html=True)

# HEADER LOGO (FIXO - VIDRO)
icone_b64 = get_base64_image("omni_icone.png")
texto_b64 = get_base64_image("omni_texto.png")

if icone_b64 and texto_b64:
    st.markdown(f"""
    <div class="logo-container">
        <img src="data:image/png;base64,{icone_b64}" class="logo-icon-spin">
        <img src="data:image/png;base64,{texto_b64}" class="logo-text-static">
        <div class="header-subtitle-text">Ecossistema de Inteligência Pedagógica e Inclusiva</div>
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown("<div class='logo-container'><h1 style='color: #0F52BA; margin:0;'>🌐 OMNISFERA</h1><div class='header-subtitle-text'>Ecossistema de Inteligência Pedagógica e Inclusiva</div></div>", unsafe_allow_html=True)

nome_display = st.session_state.get("usuario_nome", "Educador").split()[0]

# Banner Message
mensagem_banner = "Unindo ciência, dados e empatia para transformar a educação."
if 'OPENAI_API_KEY' in st.secrets:
    try:
        if 'banner_msg' not in st.session_state:
            client = OpenAI(api_key=st.secrets['OPENAI_API_KEY'])
            res = client.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "user", "content": f"Frase inspiradora curta para {nome_display} sobre inclusão."}])
            st.session_state['banner_msg'] = res.choices[0].message.content
        mensagem_banner = st.session_state['banner_msg']
    except: pass

# --- SIDEBAR (SÓ AGORA) ---
with st.sidebar:
    if "usuario_nome" in st.session_state:
        st.markdown(f"**👤 {st.session_state['usuario_nome']}**")
        st.caption(f"{st.session_state['usuario_cargo']}")
        st.markdown("---")

    st.markdown("### 📢 Central de Feedback")
    tipo = st.selectbox("Tipo:", ["Sugestão", "Erro", "Elogio"])
    msg = st.text_area("Mensagem:", height=100)
    if st.button("Enviar"):
        if msg: st.toast("Enviado!", icon="✅"); time.sleep(1)

# --- HERO SECTION ---
st.markdown(f"""
<div class="dash-hero hover-spring">
    <div class="hero-text-block">
        <div class="hero-title">Olá, {nome_display}!</div>
        <div class="hero-subtitle">"{mensagem_banner}"</div>
    </div>
    <i class="ri-heart-pulse-fill hero-bg-icon"></i>
</div>
""", unsafe_allow_html=True)

# FERRAMENTAS
st.markdown("<div class='section-title'><i class='ri-cursor-fill'></i> Acesso Rápido</div>", unsafe_allow_html=True)

logo_pei = get_base64_image("360.png")
logo_paee = get_base64_image("pae.png")
logo_hub = get_base64_image("hub.png")

c1, c2, c3 = st.columns(3)

with c1:
    img = f'<img src="data:image/png;base64,{logo_pei}" class="card-logo-img">' if logo_pei else '<i class="ri-book-read-line" style="font-size:4rem; color:#3182CE;"></i>'
    st.markdown(f"""<div class="tool-card border-blue hover-spring"><div class="card-logo-box">{img}</div><div class="tool-desc-short">Plano de Ensino Individualizado Oficial.</div></div>""", unsafe_allow_html=True)
    if st.button("➜ Acessar PEI", use_container_width=True): st.switch_page("pages/1_PEI.py")

with c2:
    img = f'<img src="data:image/png;base64,{logo_paee}" class="card-logo-img">' if logo_paee else '<i class="ri-puzzle-line" style="font-size:4rem; color:#805AD5;"></i>'
    st.markdown(f"""<div class="tool-card border-purple hover-spring"><div class="card-logo-box">{img}</div><div class="tool-desc-short">Sala de Recursos e Tecnologias Assistivas.</div></div>""", unsafe_allow_html=True)
    if st.button("➜ Acessar PAEE", use_container_width=True): st.switch_page("pages/2_PAE.py")

with c3:
    img = f'<img src="data:image/png;base64,{logo_hub}" class="card-logo-img">' if logo_hub else '<i class="ri-rocket-line" style="font-size:4rem; color:#38B2AC;"></i>'
    st.markdown(f"""<div class="tool-card border-teal hover-spring"><div class="card-logo-box">{img}</div><div class="tool-desc-short">Adaptação automática de provas e criação de roteiros.</div></div>""", unsafe_allow_html=True)
    if st.button("➜ Acessar Hub", use_container_width=True): st.switch_page("pages/3_Hub_Inclusao.py")

# BENTO GRID (BASE DE CONHECIMENTO - RESTAURADO)
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

# INSIGHT DO DIA (RESTAURADO)
noticia_insight = "A aprendizagem acontece quando o cérebro se emociona. Crie vínculos antes de cobrar conteúdos."
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

st.markdown("<div style='text-align: center; color: #CBD5E0; font-size: 0.8rem; margin-top: 60px;'>Criado e Desenvolvido por Rodrigo A. Queiroz</div>", unsafe_allow_html=True)import streamlit as st
import omni_utils as core
from openai import OpenAI

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
# Aplica apenas a sidebar branca e as fontes. Não mexe no header.
core.aplicar_estilo_global()

# Verifica Login
if not core.verificar_acesso():
    st.stop()

# ==============================================================================
# 3. CSS DA HOME (Animações e Bento Grid)
# ==============================================================================
# OBS: NÃO há nenhum comando aqui escondendo o header nativo.
st.markdown("""
<style>
    /* --- ANIMAÇÕES (Fade In e Hover) --- */
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    .animate-enter {
        animation: fadeInUp 0.6s cubic-bezier(0.2, 0.8, 0.2, 1) forwards;
    }

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
        margin-top: 10px; border: 1px solid rgba(255,255,255,0.1);
    }
    .hero-title { font-family: 'Nunito', sans-serif; font-weight: 800; font-size: 2.4rem; margin: 0; line-height: 1.1; letter-spacing: -1px; }
    .hero-bg-icon { position: absolute; right: 30px; font-size: 12rem; opacity: 0.05; top: -20px; transform: rotate(-10deg); pointer-events: none; }

    /* --- CARDS DOS MÓDULOS --- */
    .tool-card { 
        background: white; border-radius: 20px; padding: 30px 25px; 
        box-shadow: 0 4px 10px rgba(0,0,0,0.03); border: 1px solid #E2E8F0; 
        height: 100%; display: flex; flex-direction: column; justify-content: space-between; 
        text-align: center; position: relative; overflow: hidden;
    }
    .card-logo-box { height: 90px; display: flex; align-items: center; justify-content: center; margin-bottom: 20px; }
    .card-logo-img { max-height: 85px; width: auto; object-fit: contain; filter: drop-shadow(0 8px 12px rgba(0,0,0,0.1)); }
    .tool-desc-short { font-size: 0.95rem; color: #718096; font-weight: 500; margin-bottom: 25px; min-height: 45px; line-height: 1.4; }
    
    /* Botões */
    div[data-testid="column"] .stButton button {
        width: 100%; border-radius: 12px; border: none;
        background-color: #F8FAFC; color: #475569; font-family: 'Inter', sans-serif; font-weight: 700; 
        padding: 12px 0; transition: all 0.2s ease; border: 1px solid #E2E8F0;
    }
    div[data-testid="column"] .stButton button:hover { 
        background-color: #3182CE; color: white; border-color: #3182CE;
    }
    
    /* Bordas Coloridas */
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

    .section-title { font-family: 'Nunito', sans-serif; font-weight: 800; font-size: 1.4rem; color: #1A202C; margin-bottom: 25px; display: flex; align-items: center; gap: 10px; }
</style>
<link href="https://cdn.jsdelivr.net/npm/remixicon@4.1.0/fonts/remixicon.css" rel="stylesheet">
""", unsafe_allow_html=True)

# ==============================================================================
# 4. LOGO DA HOME (Integrada ao fluxo, não congelada)
# ==============================================================================
# Esta função (que está no omni_utils) desenha a logo grande no topo
# Se você removeu essa função do omni_utils, me avise que coloco o código direto aqui.
# Assumindo que ela existe no omni_utils conforme última versão:
try:
    core.renderizar_header_home()
except:
    # Fallback caso a função não exista
    st.markdown("<h1 style='text-align: center; color: #0F52BA; margin-bottom: 30px;'>🌐 OMNISFERA</h1>", unsafe_allow_html=True)

# ==============================================================================
# 5. DADOS & HERO SECTION
# ==============================================================================
nome_display = st.session_state.get("usuario_nome", "Educador").split()[0]
mensagem_banner = "Unindo ciência, dados e empatia para transformar a educação."

# IA para frase do dia (Opcional)
if 'OPENAI_API_KEY' in st.secrets:
    try:
        client = OpenAI(api_key=st.secrets['OPENAI_API_KEY'])
        if 'banner_msg' not in st.session_state:
            prompt = f"Frase muito curta e inspiradora para {nome_display} sobre educação inclusiva."
            res = client.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "user", "content": prompt}])
            st.session_state['banner_msg'] = res.choices[0].message.content
        mensagem_banner = st.session_state['banner_msg']
    except: pass

# Hero Card
st.markdown(f"""
<div class="dash-hero animate-enter">
    <div style="z-index: 2; max-width: 85%;">
        <div class="hero-title">Olá, {nome_display}!</div>
        <p style="font-size: 1.1rem; opacity: 0.95; font-style: italic; margin-top: 10px;">"{mensagem_banner}"</p>
    </div>
    <i class="ri-heart-pulse-fill hero-bg-icon"></i>
</div>
""", unsafe_allow_html=True)

# ==============================================================================
# 6. MÓDULOS PRINCIPAIS
# ==============================================================================
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

# ==============================================================================
# 7. BENTO GRID (Links Úteis)
# ==============================================================================
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
