# ARQUIVO: omni_utils.py
import streamlit as st
import os
import base64
from datetime import date

# ==============================================================================
# 1. CONFIGURAÇÕES GLOBAIS E AMBIENTE
# ==============================================================================
APP_VERSION = "v116.0"

def verificar_ambiente():
    try: return st.secrets.get("ENV") == "TESTE"
    except: return False

IS_TEST_ENV = verificar_ambiente()

# ==============================================================================
# 2. FUNÇÕES DE UTILIDADE (IMAGENS)
# ==============================================================================
def get_base64_image(image_path):
    """Converte imagem para Base64 para uso em HTML"""
    if not image_path or not os.path.exists(image_path): return ""
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

def finding_logo():
    """Tenta encontrar a logo padrão se nenhuma for passada"""
    caminhos = ["omni_icone.png", "logo.png", "icone.png"]
    for c in caminhos:
        if os.path.exists(c): return c
    return None

# ==============================================================================
# 3. HEADER PADRONIZADO (CARD DA PÁGINA) - AJUSTADO
# ==============================================================================
def renderizar_header_padrao(titulo, subtitulo, nome_arquivo_imagem=None, cor_destaque="#0F52BA"):
    """
    Renderiza o cabeçalho no estilo 'Card' (Logo | Texto).
    AJUSTES FEITOS: Mais alto (padding) e mais próximo do topo.
    """
    
    # 1. Define qual imagem usar
    if nome_arquivo_imagem and os.path.exists(nome_arquivo_imagem):
        b64_logo = get_base64_image(nome_arquivo_imagem)
    else:
        padrao = finding_logo()
        b64_logo = get_base64_image(padrao) if padrao else ""

    # HTML da Imagem
    if b64_logo:
        img_html = f'<img src="data:image/png;base64,{b64_logo}" style="height: 90px; width: auto; object-fit: contain;">'
    else:
        img_html = '<div style="font-size: 70px;">🔷</div>'

    # 2. CSS Local (Específico do Header)
    st.markdown("""
    <style>
        .header-card {
            display: flex;
            align-items: center;
            gap: 30px;
            background-color: white;
            
            /* --- AJUSTE DE ALTURA E POSIÇÃO --- */
            padding: 40px 40px;       /* Mais alto (mais espaço interno) */
            margin-top: -30px;        /* Puxa para cima (diminui espaço do topo) */
            margin-bottom: 40px;
            /* ---------------------------------- */
            
            border-radius: 20px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.04);
            border: 1px solid #E2E8F0;
            transition: transform 0.3s ease;
        }
        .header-card:hover {
            transform: translateY(-3px);
            box-shadow: 0 15px 35px rgba(0,0,0,0.08);
        }
        .header-texts {
            display: flex; flex-direction: column;
            border-left: 2px solid #CBD5E0; /* Linha divisória */
            padding-left: 30px;
            height: 100%;
            justify-content: center;
        }
        .header-title {
            font-family: 'Nunito', sans-serif;
            font-weight: 800; font-size: 2.2rem; color: #2D3748;
            margin: 0; line-height: 1.1; letter-spacing: -0.5px;
        }
        .header-subtitle {
            font-family: 'Inter', sans-serif;
            font-size: 1.1rem; color: #718096;
            margin-top: 8px; font-weight: 500;
        }
        @media (max-width: 768px) {
            .header-card { flex-direction: column; text-align: center; gap: 20px; padding: 30px; }
            .header-texts { border-left: none; padding-left: 0; border-top: 2px solid #E2E8F0; padding-top: 20px; }
        }
    </style>
    """, unsafe_allow_html=True)

    # 3. Renderiza o HTML
    st.markdown(f"""
    <div class="header-card" style="border-left: 8px solid {cor_destaque} !important;">
        <div class="header-logo">
            {img_html}
        </div>
        <div class="header-texts">
            <div class="header-title">{titulo}</div>
            <div class="header-subtitle">{subtitulo}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ==============================================================================
# 4. CSS GLOBAL E SIDEBAR (A MATRIZ VISUAL)
# ==============================================================================
def aplicar_estilo_global(logo_pagina=None):
    """
    Aplica CSS global e cria a Sidebar.
    ARGUMENTO NOVO: 'logo_pagina' -> Nome da imagem para usar na Sidebar desta página específica.
    """
    
    if IS_TEST_ENV:
        footer_vis, card_bg, card_border, display_text = "visible", "rgba(255, 220, 50, 0.95)", "rgba(200, 160, 0, 0.5)", "OMNISFERA | TESTE"
    else:
        footer_vis, card_bg, card_border, display_text = "hidden", "rgba(255, 255, 255, 0.85)", "rgba(255, 255, 255, 0.6)", f"OMNISFERA {APP_VERSION}"

    # CSS MESTRE
    st.markdown(f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Nunito:wght@400;600;700&display=swap');
        html, body, [class*="css"] {{ font-family: 'Nunito', sans-serif; }}

        /* NUCLEAR: Ocultar Menu Nativo e Headers Originais */
        [data-testid="stSidebarNav"] {{ display: none !important; }}
        [data-testid="stHeader"] {{ background: transparent !important; z-index: 9999; pointer-events: none; }}
        [data-testid="stToolbar"] {{ display: none !important; }}
        
        section[data-testid="stSidebar"] {{ background-color: #FFFFFF !important; border-right: 1px solid #E2E8F0; }}
        [data-testid="stSidebarCollapsedControl"] {{ top: 110px !important; background: white !important; border: 1px solid #E2E8F0; padding: 4px; border-radius: 8px; pointer-events: auto; }}
        
        /* Ajuste do Bloco Principal (Espaço para o Header Vidro) */
        .block-container {{ padding-top: 140px !important; padding-bottom: 3rem !important; }}

        footer {{ visibility: {footer_vis} !important; }}

        /* Header Vidro Global (Fixo) */
        .logo-container {{
            position: fixed; top: 0; left: 0; width: 100%; height: 100px;
            background-color: rgba(247, 250, 252, 0.85); backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px);
            border-bottom: 1px solid rgba(255, 255, 255, 0.5); z-index: 9998; 
            display: flex; align-items: center; justify-content: center;
        }}
        .logo-icon-spin {{ height: 80px; animation: spin 60s linear infinite; }}
        .logo-text-static {{ height: 50px; }}
        @keyframes spin {{ from {{ transform: rotate(0deg); }} to {{ transform: rotate(360deg); }} }}

        /* Badge Superior */
        .omni-badge {{
            position: fixed; top: 20px; right: 20px;
            background: {card_bg}; border: 1px solid {card_border};
            backdrop-filter: blur(8px); padding: 6px 20px; border-radius: 12px;
            font-family: 'Inter'; font-weight: 800; font-size: 0.7rem; color: #2D3748;
            letter-spacing: 2px; z-index: 999990; pointer-events: none;
        }}
    </style>
    """, unsafe_allow_html=True)

    # Renderiza Elementos Fixos Globais (Header Vidro e Badge)
    st.markdown(f'<div class="omni-badge">{display_text}</div>', unsafe_allow_html=True)
    
    # Header Global (Sempre usa a logo geral do App no topo, a específica vai na sidebar e no card)
    img_app_icon = get_base64_image("omni_icone.png")
    img_app_text = get_base64_image("omni_texto.png")
    
    if img_app_icon and img_app_text:
        st.markdown(f"""<div class="logo-container"><img src="data:image/png;base64,{img_app_icon}" class="logo-icon-spin"><img src="data:image/png;base64,{img_app_text}" class="logo-text-static"></div>""", unsafe_allow_html=True)
    else:
        st.markdown("<div class='logo-container'><h1 style='color: #0F52BA;'>🌐 OMNISFERA</h1></div>", unsafe_allow_html=True)

    # Determina qual logo vai para a Sidebar (Especifica ou Padrão)
    logo_para_sidebar = logo_pagina if logo_pagina else "omni_icone.png"
    img_sidebar_b64 = get_base64_image(logo_para_sidebar)

    # Constrói a Sidebar Customizada
    construir_sidebar_manual(img_sidebar_b64)

def construir_sidebar_manual(img_sidebar_b64):
    with st.sidebar:
        st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
        
        # LOGO DA SIDEBAR (Agora Dinâmica)
        if img_sidebar_b64: 
            st.markdown(f"""<div style="text-align: center; margin-bottom: 20px; opacity: 1;"><img src="data:image/png;base64,{img_sidebar_b64}" width="70" style="filter: drop-shadow(0 4px 6px rgba(0,0,0,0.1));"></div>""", unsafe_allow_html=True)

        if st.session_state.get("autenticado"):
            nome = st.session_state["usuario_nome"].split()[0]
            cargo = st.session_state["usuario_cargo"]
            st.markdown(f"""<div style="background: #F8FAFC; border: 1px solid #E2E8F0; padding: 12px; border-radius: 10px; margin-bottom: 30px;"><div style="font-weight: bold; color: #2D3748; font-size: 0.9rem;">👋 Olá, {nome}</div><div style="font-size: 0.75rem; color: #718096; text-transform: uppercase;">{cargo}</div></div>""", unsafe_allow_html=True)

        st.markdown("<p style='font-size: 0.75rem; color: #A0AEC0; font-weight: 700; margin-bottom: 10px; padding-left: 5px;'>NAVEGAÇÃO</p>", unsafe_allow_html=True)
        
        st.page_link("Home.py", label="Dashboard", icon="🏠")
        st.page_link("pages/1_PEI.py", label="PEI 360º", icon="📘")
        st.page_link("pages/2_PAE.py", label="PAEE & T.A.", icon="🧩")
        st.page_link("pages/3_Hub_Inclusao.py", label="Hub Inclusão", icon="🚀")
        
        st.markdown("---")
        if st.button("🔒 Sair", use_container_width=True):
            st.session_state["autenticado"] = False
            st.rerun()

# ==============================================================================
# 5. SISTEMA DE LOGIN (CENTRALIZADO)
# ==============================================================================
def verificar_acesso():
    if st.session_state.get("autenticado", False): return True
    
    st.markdown("""<style>[data-testid="stHeader"] {visibility: hidden !important;}</style>""", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 1.5, 1])
    with c2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown(f"""<div style="background: white; padding: 30px; border-radius: 20px; border: 1px solid #E2E8F0; text-align: center; box-shadow: 0 10px 30px rgba(0,0,0,0.05);"><h2 style="color: #0F52BA;">{'🛠️ MODO TESTE' if IS_TEST_ENV else 'Bem-vindo'}</h2><p style="color: #718096; font-size: 0.9rem;">Ecossistema Omnisfera</p></div><br>""", unsafe_allow_html=True)

        if IS_TEST_ENV:
            st.info("Acesso Rápido (Desenvolvimento).")
            if st.button("🚀 ENTRAR", use_container_width=True, type="primary"):
                st.session_state.update({"autenticado": True, "usuario_nome": "Tester", "usuario_cargo": "Dev"})
                st.rerun()
        else:
            nome = st.text_input("Nome")
            cargo = st.text_input("Cargo")
            termo = st.checkbox("Aceito termos.")
            senha = st.text_input("Senha", type="password")
            if st.button("🔒 ACESSAR", use_container_width=True, type="primary"):
                hoje = date.today()
                senha_ok = "PEI_START_2026" if hoje <= date(2026, 1, 19) else "OMNI_PRO"
                if not termo or not nome or not cargo: st.warning("Preencha tudo.")
                elif senha != senha_ok: st.error("Senha errada.")
                else:
                    st.session_state.update({"autenticado": True, "usuario_nome": nome, "usuario_cargo": cargo})
                    st.rerun()
    return False
