# ARQUIVO: omni_utils.py
import streamlit as st
import os
import base64
from datetime import date

# ==============================================================================
# 1. CONFIGURAÇÕES
# ==============================================================================
APP_VERSION = "v116.0"

def verificar_ambiente():
    try: return st.secrets.get("ENV") == "TESTE"
    except: return False

IS_TEST_ENV = verificar_ambiente()

# ==============================================================================
# 2. FUNÇÕES DE UTILIDADE
# ==============================================================================
def get_base64_image(image_path):
    if not os.path.exists(image_path): return ""
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

# ==============================================================================
# 3. CSS GLOBAL E SIDEBAR (MATRIZ)
# ==============================================================================
def aplicar_estilo_global():
    """Configura o visual base (Sidebar, Login, Fontes)"""
    
    # Cores e Textos por ambiente
    if IS_TEST_ENV:
        footer_vis, card_bg, card_border, display_text = "visible", "rgba(255, 220, 50, 0.95)", "rgba(200, 160, 0, 0.5)", "OMNISFERA | TESTE"
    else:
        footer_vis, card_bg, card_border, display_text = "hidden", "rgba(255, 255, 255, 0.85)", "rgba(255, 255, 255, 0.6)", f"OMNISFERA {APP_VERSION}"

    # CSS MESTRE
    st.markdown(f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Nunito:wght@400;600;700&display=swap');
        html, body, [class*="css"] {{ font-family: 'Nunito', sans-serif; }}

        /* --- SIDEBAR E NAV --- */
        [data-testid="stSidebarNav"] {{ display: none !important; }}
        section[data-testid="stSidebar"] {{ background-color: #FFFFFF !important; border-right: 1px solid #E2E8F0; padding-top: 0 !important; }}
        [data-testid="stSidebarCollapsedControl"] {{ top: 110px !important; background: white !important; border: 1px solid #E2E8F0; border-radius: 10px; padding: 2px; }}

        /* --- HEADER VIDRO (GLOBAL) --- */
        .logo-container {{
            position: fixed; top: 0; left: 0; width: 100%; height: 100px;
            background-color: rgba(247, 250, 252, 0.85); backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px);
            border-bottom: 1px solid rgba(255, 255, 255, 0.5); z-index: 9998; 
            display: flex; align-items: center; justify-content: center;
        }}
        .logo-icon-spin {{ height: 80px; animation: spin 60s linear infinite; }}
        .logo-text-static {{ height: 50px; }}
        @keyframes spin {{ from {{ transform: rotate(0deg); }} to {{ transform: rotate(360deg); }} }}

        /* --- BADGE CANTO DIREITO --- */
        .omni-badge {{
            position: fixed; top: 20px; right: 20px;
            background: {card_bg}; border: 1px solid {card_border};
            backdrop-filter: blur(8px); padding: 6px 20px; border-radius: 12px;
            font-family: 'Inter'; font-weight: 800; font-size: 0.7rem; color: #2D3748;
            letter-spacing: 2px; z-index: 999990; pointer-events: none;
        }}

        /* --- GERAIS --- */
        footer {{ visibility: {footer_vis} !important; }}
        header[data-testid="stHeader"] {{ background: transparent !important; z-index: 9999; }}
        [data-testid="stToolbar"] {{ display: none !important; }}
        .block-container {{ padding-top: 140px !important; }}
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

    construir_sidebar_manual(img_icon)

def construir_sidebar_manual(img_icon):
    with st.sidebar:
        st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
        if img_icon: st.markdown(f"""<div style="text-align: center; margin-bottom: 20px; opacity: 0.8;"><img src="data:image/png;base64,{img_icon}" width="50"></div>""", unsafe_allow_html=True)

        if st.session_state.get("autenticado"):
            nome = st.session_state["usuario_nome"].split()[0]
            cargo = st.session_state["usuario_cargo"]
            st.markdown(f"""<div style="background: #F8FAFC; border: 1px solid #E2E8F0; padding: 12px; border-radius: 10px; margin-bottom: 30px;"><div style="font-weight: bold; color: #2D3748; font-size: 0.9rem;">👋 Olá, {nome}</div><div style="font-size: 0.75rem; color: #718096; text-transform: uppercase;">{cargo}</div></div>""", unsafe_allow_html=True)

        st.markdown("<p style='font-size: 0.75rem; color: #A0AEC0; font-weight: 700; margin-bottom: 10px;'>NAVEGAÇÃO</p>", unsafe_allow_html=True)
        st.page_link("Home.py", label="Dashboard", icon="🏠")
        st.page_link("pages/1_PEI.py", label="PEI 360º", icon="📘")
        st.page_link("pages/2_PAE.py", label="PAEE & T.A.", icon="🧩")
        st.page_link("pages/3_Hub_Inclusao.py", label="Hub Inclusão", icon="🚀")
        st.markdown("---")
        if st.button("🔒 Sair", use_container_width=True):
            st.session_state["autenticado"] = False
            st.rerun()

# ==============================================================================
# 4. LOGIN
# ==============================================================================
def verificar_acesso():
    if st.session_state.get("autenticado", False): return True
    
    st.markdown("""<style>[data-testid="stHeader"] {visibility: hidden !important;}</style>""", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 1.5, 1])
    with c2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown(f"""<div style="background: white; padding: 30px; border-radius: 20px; border: 1px solid #E2E8F0; text-align: center; box-shadow: 0 10px 30px rgba(0,0,0,0.05);"><h2 style="color: #0F52BA;">{'🛠️ MODO TESTE' if IS_TEST_ENV else 'Bem-vindo'}</h2><p style="color: #718096; font-size: 0.9rem;">Ecossistema Omnisfera</p></div><br>""", unsafe_allow_html=True)

        if IS_TEST_ENV:
            st.info("Dev Mode.")
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

# ==============================================================================
# 5. HEADER ESPECÍFICO DE PÁGINA (ESTILO CARTÃO)
# ==============================================================================
def renderizar_header_padrao(nome_arquivo_imagem, texto_descritivo):
    """
    Renderiza o cabeçalho no estilo: [LOGO] | [TEXTO CINZA] dentro de um card branco.
    Args:
        nome_arquivo_imagem (str): Ex: "360.png", "pae.png", "hub.png"
        texto_descritivo (str): O subtítulo (ex: "Ecossistema de Inteligência...")
    """
    
    # 1. Carrega a imagem específica da página
    b64_img = get_base64_image(nome_arquivo_imagem)
    
    if b64_img:
        img_html = f'<img src="data:image/png;base64,{b64_img}" style="max-height: 50px; width: auto;">'
    else:
        img_html = '<span style="font-size: 40px;">🔷</span>' # Fallback se não achar a imagem

    # 2. CSS Local para este componente específico
    st.markdown("""
    <style>
        .page-header-card {
            background-color: white;
            padding: 20px 40px;
            border-radius: 12px;
            border: 1px solid #E2E8F0;
            box-shadow: 0 4px 6px rgba(0,0,0,0.02);
            display: flex;
            align-items: center;
            gap: 25px;
            margin-bottom: 30px;
        }
        
        .header-separator {
            height: 35px;
            border-left: 2px solid #CBD5E0; /* Linha vertical cinza */
            width: 1px;
        }
        
        .header-subtitle {
            font-family: 'Inter', sans-serif;
            font-size: 1.1rem;
            color: #718096; /* Cinza do texto */
            font-weight: 600;
            letter-spacing: -0.5px;
        }
        
        /* Ajuste Mobile */
        @media (max-width: 600px) {
            .page-header-card { flex-direction: column; text-align: center; gap: 10px; }
            .header-separator { display: none; }
        }
    </style>
    """, unsafe_allow_html=True)

    # 3. Renderiza o HTML (Logo | Texto)
    st.markdown(f"""
    <div class="page-header-card">
        <div>{img_html}</div>
        <div class="header-separator"></div>
        <div class="header-subtitle">{texto_descritivo}</div>
    </div>
    """, unsafe_allow_html=True)
