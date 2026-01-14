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
icone_pag = "🛠️" if IS_TEST_ENV else "🌐"

st.set_page_config(
    page_title=titulo_pag,
    page_icon=icone_pag,
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==============================================================================
# 2. DEFINIÇÃO DE ESTILO E FLUIDEZ (CSS DINÂMICO)
# ==============================================================================

# Definição Dinâmica de Cores do Card e Rodapé
if IS_TEST_ENV:
    # Ambiente de Teste: Amarelo e Rodapé Visível
    card_bg = "rgba(255, 220, 50, 0.95)" 
    card_border = "rgba(200, 160, 0, 0.5)"
    display_text = "OMNISFERA | TESTE"
    footer_visibility = "visible" 
else:
    # Ambiente Oficial: Branco Gelo e Rodapé Oculto
    card_bg = "rgba(255, 255, 255, 0.85)"
    card_border = "rgba(255, 255, 255, 0.6)"
    display_text = f"OMNISFERA {APP_VERSION}"
    footer_visibility = "hidden"

# CSS GLOBAL DE FLUIDEZ
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&family=Nunito:wght@400;600;700&display=swap');
    
    /* RESET E FLUIDEZ GERAL */
    html {{ scroll-behavior: smooth; }}
    html, body, [class*="css"] {{ font-family: 'Nunito', sans-serif; color: #2D3748; background-color: #F7FAFC; }}

    /* ANIMAÇÃO DE ENTRADA (FADE IN) - Evita o "pisco" na navegação */
    @keyframes fadeIn {{
        from {{ opacity: 0; transform: translateY(10px); }}
        to {{ opacity: 1; transform: translateY(0); }}
    }}
    
    .block-container {{ 
        padding-top: 180px !important; /* Espaço para o Header flutuante */
        padding-bottom: 3rem !important; 
        margin-top: 0rem !important;
        animation: fadeIn 0.6s ease-out; /* Suavidade ao carregar */
    }}

    /* --- HEADER DE VIDRO (GLASSMORPHISM) --- */
    .logo-container {{
        display: flex; align-items: center; justify-content: center;
        gap: 20px; 
        position: fixed; top: 0; left: 0; width: 100%;
        
        /* AQUI ESTÁ A MÁGICA DA TRANSIÇÃO (FIX) */
        background-color: rgba(247, 250, 252, 0.85); /* Semi-transparente */
        backdrop-filter: blur(12px);                  /* Desfoque do fundo */
        -webkit-backdrop-filter: blur(12px);
        border-bottom: 1px solid rgba(255, 255, 255, 0.5); /* Borda sutil */
        
        z-index: 9998; /* Abaixo do Badge, acima do conteúdo */
        padding-top: 15px; padding-bottom: 15px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.03);
        transition: all 0.3s ease;
    }}

    /* LOGO GIRATÓRIA (HOME) */
    @keyframes spin {{ from {{ transform: rotate(0deg); }} to {{ transform: rotate(360deg); }} }}
    .logo-icon-spin {{ height: 120px; width: auto; animation: spin 45s linear infinite; filter: drop-shadow(0 4px 8px rgba(0,0,0,0.1)); }}
    .logo-text-static {{ height: 80px; width: auto; }}

    /* --- CARD OMNISFERA (CANTO DIREITO) --- */
    .omni-badge {{
        position: fixed; top: 20px; right: 20px;
        background: {card_bg};
        border: 1px solid {card_border};
        backdrop-filter: blur(8px); -webkit-backdrop-filter: blur(8px);
        padding: 8px 25px;
        min-width: 200px;
        border-radius: 12px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08);
        z-index: 999990; /* Acima de tudo */
        display: flex; align-items: center; justify-content: center;
        pointer-events: none; /* Permite ver, mas clique passa (se precisar) */
        transition: transform 0.3s ease;
    }}
    
    .omni-text {{
        font-family: 'Inter', sans-serif; font-weight: 800; font-size: 0.75rem;
        color: #2D3748; letter-spacing: 2px; text-transform: uppercase;
    }}

    /* --- CONTROLES DO STREAMLIT (INTEGRAÇÃO) --- */
    footer {{ visibility: {footer_visibility} !important; }}
    
    /* Header invisível mas funcional (para clicks) */
    header[data-testid="stHeader"] {{ background-color: transparent !important; z-index: 9999 !important; pointer-events: none; }}
    
    /* Esconde Toolbar (Share/Deploy) */
    [data-testid="stToolbar"] {{ visibility: hidden !important; display: none !important; }}
    
    /* Botão Menu Lateral (Hambúrguer) - REPOSICIONADO */
    [data-testid="stSidebarCollapsedControl"] {{
        position: fixed !important;
        top: 110px !important;       /* Abaixo do Header de Vidro */
        left: 20px !important;
        z-index: 1000000 !important;
        visibility: visible !important;
        display: flex !important;
        background-color: white !important;
        border: 1px solid #E2E8F0 !important;
        border-radius: 12px !important;
        width: 40px !important; height: 40px !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05) !important;
        align-items: center !important; justify-content: center !important;
        color: #2D3748 !important;
        pointer-events: auto !important; 
        transition: all 0.2s ease !important;
    }}
    [data-testid="stSidebarCollapsedControl"]:hover {{
        background-color: #3182CE !important; color: white !important; transform: scale(1.05);
    }}

    /* --- HERO E CARDS --- */
    .dash-hero {{ 
        background: linear-gradient(135deg, #0F52BA 0%, #062B61 100%); 
        border-radius: 20px; margin-bottom: 40px; 
        box-shadow: 0 15px 30px rgba(15, 82, 186, 0.2);
        color: white; position: relative; overflow: hidden;
        padding: 50px 60px;
        display: flex; align-items: center; justify-content: flex-start;
        /* Espaço extra para não colar no vidro ao carregar */
        margin-top: 10px; 
    }}
    .hero-title {{ font-family: 'Inter', sans-serif; font-weight: 800; font-size: 2.2rem; margin: 0; line-height: 1.1; margin-bottom: 10px; letter-spacing: -1px; }}
    .hero-subtitle {{ font-family: 'Inter', sans-serif; font-size: 1.1rem; opacity: 0.9; font-weight: 400; }}
    .hero-bg-icon {{ position: absolute; right: 40px; font-size: 8rem; opacity: 0.08; top: 20px; transform: rotate(-15deg); }}

    .tool-card {{ 
        background: white; border-radius: 20px; padding: 30px 20px; 
        box-shadow: 0 4px 10px rgba(0,0,0,0.03); border: 1px solid #E2E8F0; 
        height: 100%; display: flex; flex-direction: column; justify-content: space-between; 
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1); text-align: center;
    }}
    .tool-card:hover {{ transform: translateY(-8px); border-color: #3182CE; box-shadow: 0 20px 40px rgba(0,0,0,0.08); }}
    
    .card-logo-box {{ height: 90px; display: flex; align-items: center; justify-content: center; margin-bottom: 15px; }}
    .card-logo-img {{ max-height: 80px; width: auto; object-fit: contain; filter: drop-shadow(0 4px 6px rgba(0,0,0,0.05)); }}
    .tool-desc-short {{ font-size: 0.9rem; color: #718096; font-weight: 500; margin-bottom: 20px; min-height: 40px; line-height: 1.4; }}
    
    div[data-testid="column"] .stButton button {{
        width: 100%; border-radius: 12px; border: none;
        background-color: #F8F9FA; color: #4A5568; font-family: 'Inter', sans-serif; font-weight: 700; 
        font-size: 0.95rem; padding: 12px 0; transition: all 0.2s; border: 1px solid #E2E8F0;
    }}
    div[data-testid="column"] .stButton button:hover {{ background-color: #3182CE; color: white; border-color: #3182CE; box-shadow: 0 4px 12px rgba(49, 130, 206, 0.3); }}
    
    .border-blue {{ border-bottom: 5px solid #3182CE; }} 
    .border-purple {{ border-bottom: 5px solid #805AD5; }} 
    .border-teal {{ border-bottom: 5px solid #38B2AC; }}

    .home-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 40px; }}
    .rich-card {{ background: white; border-radius: 16px; padding: 25px; border: 1px solid #E2E8F0; box-shadow: 0 2px 4px rgba(0,0,0,0.02); transition: all 0.2s; text-decoration: none; color: inherit; display: flex; flex-direction: column; align-items: center; text-align: center; position: relative; overflow: hidden; height: 100%; }}
    .rich-card:hover {{ transform: translateY(-5px); box-shadow: 0 10px 20px rgba(0,0,0,0.05); border-color: #CBD5E0; }}
    .rich-card-top {{ width: 100%; height: 4px; position: absolute; top: 0; left: 0; }}
    .rc-icon {{ width: 50px; height: 50px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 1.5rem; margin-bottom: 15px; }}
    .rc-title {{ font-weight: 800; font-size: 1rem; color: #2D3748; margin-bottom: 5px; }}
    .rc-desc {{ font-size: 0.85rem; color: #718096; line-height: 1.4; }}

    .insight-card-end {{ background-color: #FFFFF0; border-radius: 16px; padding: 25px; color: #2D3748; display: flex; align-items: center; gap: 25px; box-shadow: 0 4px 10px rgba(0,0,0,0.03); border-left: 6px solid #F6E05E; margin-bottom: 30px; }}
    .insight-icon-end {{ font-size: 2rem; color: #D69E2E; }}
    .section-title {{ font-family: 'Inter', sans-serif; font-weight: 800; font-size: 1.3rem; color: #1A202C; margin-bottom: 25px; display: flex; align-items: center; gap: 12px; margin-top: 40px; }}
    .section-title i {{ color: #3182CE; }}
</style>
<link href="https://cdn.jsdelivr.net/npm/remixicon@4.1.0/fonts/remixicon.css" rel="stylesheet">
""", unsafe_allow_html=True)

# ==============================================================================
# 3. UTILITÁRIOS (IMAGENS) E HEADER FIXO
# ==============================================================================
def get_base64_image(image_path):
    if not os.path.exists(image_path): return ""
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

# CARD OMNISFERA (Canto Direito)
st.markdown(f"""
<div class="omni-badge">
    <span class="omni-text">{display_text}</span>
</div>
""", unsafe_allow_html=True)

# HEADER LOGO (Centro/Topo - VIDRO)
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
    st.markdown("<div class='logo-container'><h1 style='color: #0F52BA; margin:0;'>🌐 OMNISFERA</h1></div>", unsafe_allow_html=True)

# ==============================================================================
# 4. SISTEMA DE SEGURANÇA E LOGIN (CONDICIONAL)
# ==============================================================================
def sistema_seguranca():
    # Definição de cores e textos para o Login
    if IS_TEST_ENV:
        border_color = "#FF9800"
        card_title = "🛠️ MODO TESTE"
        btn_text = "🚀 ENTRAR (TESTE)"
        btn_color = "#E65100"
    else:
        border_color = "#E2E8F0"
        card_title = "Bem-vindo de volta!"
        btn_text = "🔒 ACESSAR OMNISFERA"
        btn_color = "#0F52BA"

    st.markdown(f"""
        <style>
            /* Esconde header padrão na tela de login */
            [data-testid="stHeader"] {{visibility: hidden !important; height: 0px !important;}}
            
            .login-container {{ 
                background-color: white; 
                padding: 5px 40px 40px 40px; 
                border-radius: 20px; 
                box-shadow: 0 10px 30px rgba(0,0,0,0.08); 
                text-align: center; 
                border: 2px solid {border_color}; 
                max-width: 550px;
                margin: 0 auto;
                margin-top: 20px;
            }}

            .login-logo-spin {{ height: 110px; width: auto; animation: spin 45s linear infinite; filter: drop-shadow(0 4px 8px rgba(0,0,0,0.1)); }}
            .login-logo-static {{ height: 75px; width: auto; margin-left: 10px; }}
            .logo-wrapper {{ display: flex; justify-content: center; align-items: center; margin-bottom: 20px; margin-top: 10px; }}
            .manifesto-login {{ font-family: 'Nunito', sans-serif; font-size: 0.9rem; color: #4A5568; font-style: italic; line-height: 1.5; margin-bottom: 30px; padding: 0 15px; }}
            .stTextInput input {{ border-radius: 8px !important; border: 1px solid #CBD5E0 !important; padding: 10px !important; background-color: #F8FAFC !important; }}
            .termo-box {{ background-color: #F8FAFC; padding: 15px; border-radius: 8px; height: 120px; overflow-y: scroll; font-size: 0.75rem; border: 1px solid #E2E8F0; margin-bottom: 20px; text-align: left; color: #4A5568; line-height: 1.4; }}
            
            div[data-testid="column"] .stButton button {{
                width: 100%; background-color: {btn_color} !important; color: white !important;
                border-radius: 8px !important; font-weight: 700 !important; height: 50px !important; border: none !important;
            }}
            div[data-testid="column"] .stButton button:hover {{ opacity: 0.9; }}
            .teste-warning {{ color: #D69E2E; font-size: 0.8rem; font-weight: bold; margin-bottom: 10px; }}
        </style>
    """, unsafe_allow_html=True)

    if "autenticado" not in st.session_state:
        st.session_state["autenticado"] = False

    if not st.session_state["autenticado"]:
        c_vazio1, c_login, c_vazio2 = st.columns([1, 2, 1])
        
        with c_login:
            st.markdown("<div class='login-container'>", unsafe_allow_html=True)
            
            # LOGO LOGIN
            if icone_b64 and texto_b64:
                st.markdown(f"""<div class="logo-wrapper"><img src="data:image/png;base64,{icone_b64}" class="login-logo-spin"><img src="data:image/png;base64,{texto_b64}" class="login-logo-static"></div>""", unsafe_allow_html=True)
            else:
                st.markdown(f"<h2 style='color:#0F52BA; margin:0;'>{card_title}</h2>", unsafe_allow_html=True)

            # MANIFESTO
            st.markdown("""<div class="manifesto-login">"A Omnisfera é um ecossistema vivo onde a <strong>Neurociência</strong> encontra a <strong>Pedagogia</strong>."</div>""", unsafe_allow_html=True)
            
            # --- FORMULÁRIO CONDICIONAL ---
            nome_user = ""
            cargo_user = ""
            senha = ""
            concordo = False

            if IS_TEST_ENV:
                # MODO TESTE (Aberto)
                st.markdown("<div class='teste-warning'>🛠️ MODO TESTE ATIVADO: Acesso Rápido Liberado</div>", unsafe_allow_html=True)
                with st.expander("📝 Preencher dados (Opcional)"):
                    nome_user = st.text_input("nome_fake", placeholder="Nome (Opcional)", label_visibility="collapsed")
                    st.markdown("<div style='height:5px'></div>", unsafe_allow_html=True)
                    cargo_user = st.text_input("cargo_fake", placeholder="Cargo (Opcional)", label_visibility="collapsed")
            else:
                # MODO PÚBLICO (Rigoroso)
                st.markdown("<div style='text-align:left; font-weight:bold; color:#2D3748; font-size:0.9rem; margin-bottom:5px;'>👋 Sua Identidade</div>", unsafe_allow_html=True)
                nome_user = st.text_input("nome_real", placeholder="Como gostaria de ser chamado?", label_visibility="collapsed")
                st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
                cargo_user = st.text_input("cargo_real", placeholder="Seu Cargo (Ex: Professor, Coord...)", label_visibility="collapsed")
                
                st.markdown("---")
                st.markdown("<div style='text-align:left; font-weight:bold; color:#2D3748; font-size:0.9rem; margin-bottom:5px;'>🛡️ Termos de Uso (Beta)</div>", unsafe_allow_html=True)
                st.markdown("""<div class="termo-box"><strong>ACORDO DE CONFIDENCIALIDADE</strong><br><br>1. Software em desenvolvimento (BETA).<br>2. Proibida a comercialização.<br>3. Respeite a LGPD (use dados fictícios).</div>""", unsafe_allow_html=True)
                concordo = st.checkbox("Li, compreendi e concordo com os termos.")
                
                st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
                senha = st.text_input("senha_real", type="password", placeholder="Senha de Acesso", label_visibility="collapsed")

            st.markdown("<div style='height:15px'></div>", unsafe_allow_html=True)
            
            # VALIDAÇÃO DO BOTÃO
            if st.button(btn_text):
                if IS_TEST_ENV:
                    # Entra direto
                    st.session_state["autenticado"] = True
                    st.session_state["usuario_nome"] = nome_user if nome_user else "Visitante Teste"
                    st.session_state["usuario_cargo"] = cargo_user if cargo_user else "Dev"
                    st.rerun()
                else:
                    # Valida tudo
                    hoje = date.today()
                    senha_mestra = "PEI_START_2026" if hoje <= date(2026, 1, 19) else "OMNI_PRO"

                    if not concordo: st.warning("⚠️ Você precisa aceitar os termos de uso.")
                    elif not nome_user or not cargo_user: st.warning("⚠️ Preencha Nome e Cargo.")
                    elif senha != senha_mestra: st.error("🚫 Senha incorreta.")
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
# 5. CONTEÚDO DA HOME (DASHBOARD)
# ==============================================================================
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

# --- SIDEBAR ---
with st.sidebar:
    if "usuario_nome" in st.session_state:
        st.markdown(f"**👤 {st.session_state['usuario_nome']}**")
        st.caption(f"{st.session_state['usuario_cargo']}")
        st.markdown("---")

    st.markdown("### 📢 Central de Feedback")
    st.info("Encontrou um erro ou tem uma ideia? Conte para nós!")
    tipo_feedback = st.selectbox("Tipo:", ["Sugestão", "Reportar Erro", "Elogio"], label_visibility="collapsed")
    texto_feedback = st.text_area("Sua mensagem:", height=100, label_visibility="collapsed", placeholder="Digite aqui...")
    
    if st.button("Enviar Feedback", use_container_width=True):
        if texto_feedback:
            st.toast("Feedback enviado! Obrigado.", icon="✅")
            time.sleep(1)
        else:
            st.warning("Escreva uma mensagem.")

# --- HERO SECTION ---
st.markdown(f"""
<div class="dash-hero">
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

col1, col2, col3 = st.columns(3)

# PEI
with col1:
    icon_pei = f'<img src="data:image/png;base64,{logo_pei}" class="card-logo-img">' if logo_pei else '<i class="ri-book-read-line" style="font-size:4rem; color:#3182CE;"></i>'
    st.markdown(f"""<div class="tool-card border-blue"><div class="card-logo-box">{icon_pei}</div><div class="tool-desc-short">Avaliação, anamnese e geração do plano oficial do aluno.</div></div>""", unsafe_allow_html=True)
    if st.button("➜ Acessar PEI", key="btn_pei", use_container_width=True): st.switch_page("pages/1_PEI.py")

# PAEE
with col2:
    icon_paee = f'<img src="data:image/png;base64,{logo_paee}" class="card-logo-img">' if logo_paee else '<i class="ri-puzzle-line" style="font-size:4rem; color:#805AD5;"></i>'
    st.markdown(f"""<div class="tool-card border-purple"><div class="card-logo-box">{icon_paee}</div><div class="tool-desc-short">Inteligência da Sala de Recursos e Tecnologias Assistivas.</div></div>""", unsafe_allow_html=True)
    if st.button("➜ Acessar PAEE", key="btn_paee", use_container_width=True): st.switch_page("pages/2_PAE.py")

# HUB
with col3:
    icon_hub = f'<img src="data:image/png;base64,{logo_hub}" class="card-logo-img">' if logo_hub else '<i class="ri-rocket-line" style="font-size:4rem; color:#38B2AC;"></i>'
    st.markdown(f"""<div class="tool-card border-teal"><div class="card-logo-box">{icon_hub}</div><div class="tool-desc-short">Adaptação automática de provas e criação de roteiros.</div></div>""", unsafe_allow_html=True)
    if st.button("➜ Acessar Hub", key="btn_hub", use_container_width=True): st.switch_page("pages/3_Hub_Inclusao.py")

# RODAPÉ E INSIGHT
st.markdown("<div style='margin-top:40px;'></div>", unsafe_allow_html=True)
st.markdown("<div class='section-title'><i class='ri-book-mark-fill'></i> Base de Conhecimento</div>", unsafe_allow_html=True)

st.markdown("""
<div class="home-grid">
    <a href="#" class="rich-card">
        <div class="rich-card-top" style="background-color: #3182CE;"></div>
        <div class="rc-icon" style="background-color:#EBF8FF; color:#3182CE;"><i class="ri-question-answer-line"></i></div>
        <div class="rc-title">PEI vs PAEE</div>
        <div class="rc-desc">Diferenças fundamentais.</div>
    </a>
    <a href="https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2015/lei/l13146.htm" target="_blank" class="rich-card">
        <div class="rich-card-top" style="background-color: #D69E2E;"></div>
        <div class="rc-icon" style="background-color:#FFFFF0; color:#D69E2E;"><i class="ri-scales-3-line"></i></div>
        <div class="rc-title">Legislação</div>
        <div class="rc-desc">LBI e Decretos.</div>
    </a>
    <a href="https://institutoneurosaber.com.br/" target="_blank" class="rich-card">
        <div class="rich-card-top" style="background-color: #D53F8C;"></div>
        <div class="rc-icon" style="background-color:#FFF5F7; color:#D53F8C;"><i class="ri-brain-line"></i></div>
        <div class="rc-title">Neurociência</div>
        <div class="rc-desc">Desenvolvimento atípico.</div>
    </a>
    <a href="http://basenacionalcomum.mec.gov.br/" target="_blank" class="rich-card">
        <div class="rich-card-top" style="background-color: #38A169;"></div>
        <div class="rc-icon" style="background-color:#F0FFF4; color:#38A169;"><i class="ri-compass-3-line"></i></div>
        <div class="rc-title">BNCC</div>
        <div class="rc-desc">Currículo oficial.</div>
    </a>
</div>
""", unsafe_allow_html=True)

# Insight do Dia (Gerado na API ou fixo)
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
<div class="insight-card-end">
    <div class="insight-icon-end"><i class="ri-lightbulb-flash-line"></i></div>
    <div>
        <div style="font-weight: 700; font-size: 0.9rem; color: #D69E2E;">Insight do Dia (IA):</div>
        <p style="margin:2px 0 0 0; font-size:0.95rem; opacity:0.9; color:#4A5568; font-style: italic;">"{noticia_insight}"</p>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("<div style='text-align: center; color: #A0AEC0; font-size: 0.8rem; margin-top: 40px;'>Omnisfera © 2026 - Todos os direitos reservados.</div>", unsafe_allow_html=True)
