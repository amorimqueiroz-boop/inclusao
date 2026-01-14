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
    if not os.path.exists(image_path): return ""
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

def finding_logo():
    """Tenta encontrar a logo padrão se nenhuma for passada"""
    caminhos = ["omni_icone.png", "logo.png", "icone.png"]
    for c in caminhos:
        if os.path.exists(c): return c
    return None

# ==============================================================================
# 3. HEADER PADRONIZADO DE PÁGINA (VISUAL SOLICITADO)
# ==============================================================================
def renderizar_header_padrao(titulo, subtitulo, nome_arquivo_imagem=None, cor_destaque="#0F52BA"):
    """
    Renderiza o cabeçalho no estilo 'Card' (Logo | Texto) 
    Permite passar imagens específicas (360.png, pae.png, etc).
    """
    
    # 1. Define qual imagem usar (a específica ou a padrão)
    if nome_arquivo_imagem and os.path.exists(nome_arquivo_imagem):
        b64_logo = get_base64_image(nome_arquivo_imagem)
    else:
        # Fallback para logo padrão se a específica não existir
        padrao = finding_logo()
        b64_logo = get_base64_image(padrao) if padrao else ""

    # HTML da Imagem
    if b64_logo:
        img_html = f'<img src="data:image/png;base64,{b64_logo}" style="height: 80px; width: auto; object-fit: contain;">'
    else:
        img_html = '<div style="font-size: 60px;">🔷</div>'

    # 2. CSS Local (Específico do Header)
    st.markdown("""
    <style>
        .header-card {
            display: flex;
            align-items: center;
            gap: 25px;
            background-color: white;
            padding: 25px 30px;
            border-radius: 16px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.03);
            border: 1px solid #E2E8F0;
            margin-bottom: 30px;
            transition: transform 0.3s ease;
        }
        .header-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(0,0,0,0.06);
        }
        .header-texts {
            display: flex; flex-direction: column;
            border-left: 2px solid #E2E8F0; /* Linha vertical separadora */
            padding-left: 25px;
        }
        .header-title {
            font-family: 'Nunito', sans-serif;
            font-weight: 800; font-size: 2rem; color: #2D3748;
            margin: 0; line-height: 1.1; letter-spacing: -0.5px;
        }
        .header-subtitle {
            font-family: 'Inter', sans-serif;
            font-size: 1rem; color: #718096;
            margin-top: 5px; font-weight: 500;
        }
        @media (max-width: 768px) {
            .header-card { flex-direction: column; text-align: center; gap: 15px; }
            .header-texts { border-left: none; padding-left: 0; border-top: 2px solid #E2E8F0; padding-top: 15px; }
        }
    </style>
    """, unsafe_allow_html=True)

    # 3. Renderiza o HTML
    st.markdown(f"""
    <div class="header-card" style="border-left: 6px solid {cor_destaque} !important;">
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
def aplicar_estilo_global():
    """Aplica CSS que vale para TODAS as páginas e cria a Sidebar"""
    
    if IS_TEST_ENV:
        footer_vis, card_bg, card_border, display_text = "visible", "rgba(255, 220, 50, 0.95)", "rgba(200, 160, 0, 0.5)", "OMNISFERA | TESTE"
    else:
        footer_vis, card_bg, card_border, display_text = "hidden", "rgba(255, 255, 255, 0.85)", "rgba(255, 255, 255, 0.6)", f"OMNISFERA {APP_VERSION}"

    # CSS MESTRE
    st.markdown(f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Nunito:wght@400;600;700&display=swap');
        html, body, [class*="css"] {{ font-family: 'Nunito', sans-serif; }}

        /* NUCLEAR: Ocultar Menu Nativo */
        [data-testid="stSidebarNav"] {{ display: none !important; }}
        section[data-testid="stSidebar"] {{ background-color: #FFFFFF !important; border-right: 1px solid #E2E8F0; }}
        
        /* Ajustes Gerais */
        footer {{ visibility: {footer_vis} !important; }}
        header[data-testid="stHeader"] {{ background: transparent !important; z-index: 9999; pointer-events: none; }}
        [data-testid="stToolbar"] {{ display: none !important; }}
        [data-testid="stSidebarCollapsedControl"] {{ top: 110px !important; background: white !important; border: 1px solid #E2E8F0; padding: 4px; border-radius: 8px; pointer-events: auto; }}
        .block-container {{ padding-top: 140px !important; padding-bottom: 3rem !important; }}

        /* Header Vidro Global */
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

    # Renderiza Elementos Fixos
    st.markdown(f'<div class="omni-badge">{display_text}</div>', unsafe_allow_html=True)
    img_icon = get_base64_image("omni_icone.png")
    img_text = get_base64_image("omni_texto.png")
    
    if img_icon and img_text:
        st.markdown(f"""<div class="logo-container"><img src="data:image/png;base64,{img_icon}" class="logo-icon-spin"><img src="data:image/png;base64,{img_text}" class="logo-text-static"></div>""", unsafe_allow_html=True)
    else:
        st.markdown("<div class='logo-container'><h1 style='color: #0F52BA;'>🌐 OMNISFERA</h1></div>", unsafe_allow_html=True)

    # Constrói a Sidebar Customizada
    construir_sidebar_manual(img_icon)

def construir_sidebar_manual(img_icon):
    with st.sidebar:
        st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
        if img_icon: st.markdown(f"""<div style="text-align: center; margin-bottom: 20px; opacity: 0.8;"><img src="data:image/png;base64,{img_icon}" width="50"></div>""", unsafe_allow_html=True)

        if st.session_state.get("autenticado"):
            nome = st.session_state["usuario_nome"].split()[0]
            cargo = st.session_state["usuario_cargo"]
            st.markdown(f"""<div style="background: #F8FAFC; border: 1px solid #E2E8F0; padding: 12px; border-radius: 10px; margin-bottom: 30px;"><div style="font-weight: bold; color: #2D3748; font-size: 0.9rem;">👋 Olá, {nome}</div><div style="font-size: 0.75rem; color: #718096; text-transform: uppercase;">{cargo}</div></div>""", unsafe_allow_html=True)

        st.markdown("<p style='font-size: 0.75rem; color: #A0AEC0; font-weight: 700; margin-bottom: 10px; padding-left: 5px;'>NAVEGAÇÃO</p>", unsafe_allow_html=True)
        
        # Links de Navegação usando st.page_link para performance nativa
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
