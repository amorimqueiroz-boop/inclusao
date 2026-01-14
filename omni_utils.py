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
    if not os.path.exists(image_path): return ""
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

# ==============================================================================
# 3. CSS GLOBAL (A "MATRIZ" VISUAL)
# ==============================================================================
def aplicar_estilo_global():
    """Aplica CSS que vale para TODAS as páginas"""
    
    # Lógica Visual
    if IS_TEST_ENV:
        footer_vis, card_bg, card_border, display_text = "visible", "rgba(255, 220, 50, 0.95)", "rgba(200, 160, 0, 0.5)", "OMNISFERA | TESTE"
    else:
        footer_vis, card_bg, card_border, display_text = "hidden", "rgba(255, 255, 255, 0.85)", "rgba(255, 255, 255, 0.6)", f"OMNISFERA {APP_VERSION}"

    # --- CSS AGRESSIVO PARA SIDEBAR ---
    st.markdown(f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&family=Nunito:wght@400;600;700&display=swap');
        
        html, body, [class*="css"] {{ font-family: 'Nunito', sans-serif; }}

        /* 1. FORÇAR A SIDEBAR A SER BRANCA (CSS Nuclear) */
        section[data-testid="stSidebar"] {{
            background-color: #FFFFFF !important; /* Fundo Branco */
            border-right: 1px solid #E2E8F0 !important; /* Borda sutil */
            box-shadow: 4px 0 20px rgba(0,0,0,0.03) !important; /* Sombra suave */
        }}
        
        /* Garante que o container interno também seja branco */
        section[data-testid="stSidebar"] > div {{
            background-color: #FFFFFF !important;
        }}

        /* 2. ESTILIZAR OS LINKS DE NAVEGAÇÃO (Páginas) */
        /* Link Normal */
        [data-testid="stSidebarNav"] a {{
            background-color: transparent !important;
            color: #4A5568 !important; /* Cinza Escuro */
            font-family: 'Inter', sans-serif !important;
            font-weight: 500 !important;
            border-radius: 8px !important;
            padding: 10px 15px !important;
            margin-bottom: 5px !important;
            transition: all 0.3s ease !important;
            border: 1px solid transparent !important;
        }}
        
        /* Link ao passar o mouse (Hover) */
        [data-testid="stSidebarNav"] a:hover {{
            background-color: #EBF8FF !important; /* Azul bem clarinho */
            color: #3182CE !important; /* Azul forte */
            border: 1px solid #BEE3F8 !important;
            padding-left: 20px !important; /* Efeito de deslizar para a direita */
        }}
        
        /* Link Ativo (Página Atual) */
        [data-testid="stSidebarNav"] a[aria-current="page"] {{
            background-color: #3182CE !important;
            color: white !important;
            font-weight: 700 !important;
            box-shadow: 0 4px 10px rgba(49, 130, 206, 0.3) !important;
        }}

        /* 3. TÍTULOS E TEXTOS NA SIDEBAR */
        [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {{
            color: #1A202C !important;
            font-family: 'Inter', sans-serif !important;
        }}
        
        [data-testid="stSidebar"] p, [data-testid="stSidebar"] span {{
            color: #4A5568 !important;
        }}

        /* --- RESTO DO CSS (VIDRO, LOGIN, ETC) --- */
        
        /* Header e Footer */
        footer {{ visibility: {footer_vis} !important; }}
        header[data-testid="stHeader"] {{ background-color: transparent !important; z-index: 9999 !important; pointer-events: none; }}
        [data-testid="stToolbar"] {{ visibility: hidden !important; display: none !important; }}

        /* Menu Hambúrguer */
        [data-testid="stSidebarCollapsedControl"] {{
            position: fixed !important; top: 110px !important; left: 20px !important; z-index: 1000000 !important;
            visibility: visible !important; display: flex !important;
            background-color: white !important; border: 1px solid #E2E8F0 !important; border-radius: 12px !important;
            width: 40px !important; height: 40px !important;
            align-items: center !important; justify-content: center !important;
            color: #2D3748 !important; pointer-events: auto !important; 
            box-shadow: 0 4px 6px rgba(0,0,0,0.05) !important;
            transition: all 0.2s ease !important;
        }}
        [data-testid="stSidebarCollapsedControl"]:hover {{ background-color: #3182CE !important; color: white !important; transform: scale(1.05); }}

        /* Header de Vidro */
        .logo-container {{
            display: flex; align-items: center; justify-content: center; gap: 20px; 
            position: fixed; top: 0; left: 0; width: 100%; height: 100px;
            background-color: rgba(247, 250, 252, 0.85); backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px);
            border-bottom: 1px solid rgba(255, 255, 255, 0.5); z-index: 9998; box-shadow: 0 4px 20px rgba(0,0,0,0.03);
        }}
        .logo-icon-spin {{ height: 80px; width: auto; animation: spin 45s linear infinite; }}
        .logo-text-static {{ height: 50px; width: auto; }}
        @keyframes spin {{ from {{ transform: rotate(0deg); }} to {{ transform: rotate(360deg); }} }}

        /* Badge Omnisfera */
        .omni-badge {{
            position: fixed; top: 20px; right: 20px;
            background: {card_bg}; border: 1px solid {card_border};
            backdrop-filter: blur(8px); padding: 8px 25px; min-width: 200px;
            border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.08);
            z-index: 999990; display: flex; align-items: center; justify-content: center; pointer-events: none;
        }}
        .omni-text {{ font-family: 'Inter', sans-serif; font-weight: 800; font-size: 0.75rem; color: #2D3748; letter-spacing: 2px; text-transform: uppercase; }}
        
        .block-container {{ padding-top: 140px !important; padding-bottom: 3rem !important; }}
    </style>
    """, unsafe_allow_html=True)

    # --- RENDERIZA ELEMENTOS FIXOS DA UI ---
    st.markdown(f'<div class="omni-badge"><span class="omni-text">{display_text}</span></div>', unsafe_allow_html=True)
    
    img_icon = get_base64_image("omni_icone.png")
    img_text = get_base64_image("omni_texto.png")
    
    if img_icon and img_text:
        html_header = f"""<div class="logo-container"><img src="data:image/png;base64,{img_icon}" class="logo-icon-spin"><img src="data:image/png;base64,{img_text}" class="logo-text-static"></div>"""
    else:
        html_header = "<div class='logo-container'><h1 style='color: #0F52BA; margin:0;'>🌐 OMNISFERA</h1></div>"
    
    st.markdown(html_header, unsafe_allow_html=True)

    # --- SIDEBAR INTERNA (CONTEÚDO) ---
    with st.sidebar:
        # Espaço no topo para não colar no header
        st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
        
        # Logo Pequena na Sidebar (Opcional, dá charme)
        if img_icon:
            st.markdown(f"""
            <div style="text-align: center; margin-bottom: 30px;">
                <img src="data:image/png;base64,{img_icon}" width="50" style="opacity: 0.8;">
            </div>
            """, unsafe_allow_html=True)
        
        # Card do Usuário (Glass na Sidebar)
        if "usuario_nome" in st.session_state:
            nome = st.session_state["usuario_nome"].split()[0]
            cargo = st.session_state["usuario_cargo"]
            st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, #F8FAFC 0%, #EFF6FF 100%);
                padding: 15px; border-radius: 12px; border: 1px solid #E2E8F0;
                margin-bottom: 30px; box-shadow: 0 2px 5px rgba(0,0,0,0.02);">
                <div style="font-family: 'Inter'; font-weight: 700; color: #2D3748; font-size: 0.95rem; margin-bottom: 2px;">👋 Olá, {nome}</div>
                <div style="font-size: 0.75rem; color: #718096; text-transform: uppercase; letter-spacing: 0.5px; font-weight: 600;">{cargo}</div>
            </div>
            """, unsafe_allow_html=True)

# ==============================================================================
# 4. SISTEMA DE LOGIN
# ==============================================================================
def verificar_acesso():
    if st.session_state.get("autenticado", False): return True
    renderizar_tela_login()
    return False

def renderizar_tela_login():
    st.markdown("""<style>[data-testid="stHeader"] {visibility: hidden !important;}</style>""", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        cor_borda = "#FF9800" if IS_TEST_ENV else "#E2E8F0"
        titulo = "🛠️ MODO TESTE" if IS_TEST_ENV else "Bem-vindo!"
        btn_txt = "🚀 ENTRAR (TESTE)" if IS_TEST_ENV else "🔒 ACESSAR"
        btn_color = "#E65100" if IS_TEST_ENV else "#0F52BA"
        
        st.markdown(f"""
        <div style="background: white; padding: 40px; border-radius: 20px; border: 2px solid {cor_borda}; text-align: center; box-shadow: 0 10px 30px rgba(0,0,0,0.1); margin-top: 50px;">
            <h2 style="color: #0F52BA; margin: 0;">{titulo}</h2>
            <p style="color: #718096; font-size: 0.9rem;">Ecossistema Omnisfera</p>
            <hr style="margin: 20px 0;">
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""<style>div[data-testid="column"] .stButton button {{ width: 100%; background-color: {btn_color} !important; color: white !important; border-radius: 8px !important; font-weight: 700 !important; height: 50px !important; border: none !important; }}</style>""", unsafe_allow_html=True)

        nome, cargo, senha, termo = "", "", "", False

        if IS_TEST_ENV:
            st.info("Acesso liberado.")
            with st.expander("Preencher dados (Opcional)"):
                nome = st.text_input("Nome", placeholder="Opcional")
                cargo = st.text_input("Cargo", placeholder="Opcional")
        else:
            st.markdown("<div style='font-size: 0.9rem; font-weight: bold; color: #4A5568;'>Identificação</div>", unsafe_allow_html=True)
            nome = st.text_input("Nome", placeholder="Seu nome")
            cargo = st.text_input("Cargo", placeholder="Ex: Professor")
            st.markdown("<br><div style='font-size: 0.8rem; background: #F7FAFC; padding: 10px; border-radius: 8px;'>📜 Termos de uso e LGPD.</div>", unsafe_allow_html=True)
            termo = st.checkbox("Concordo")
            senha = st.text_input("Senha", type="password")
        
        st.markdown("<br>", unsafe_allow_html=True)

        if st.button(btn_txt, use_container_width=True):
            if IS_TEST_ENV:
                st.session_state["autenticado"] = True
                st.session_state["usuario_nome"] = nome if nome else "Tester"
                st.session_state["usuario_cargo"] = cargo if cargo else "Dev"
                st.rerun()
            else:
                hoje = date.today()
                senha_ok = "PEI_START_2026" if hoje <= date(2026, 1, 19) else "OMNI_PRO"
                
                if not termo: st.warning("Aceite os termos.")
                elif not nome or not cargo: st.warning("Preencha dados.")
                elif senha != senha_ok: st.error("Senha incorreta.")
                else:
                    st.session_state["autenticado"] = True
                    st.session_state["usuario_nome"] = nome
                    st.session_state["usuario_cargo"] = cargo
                    st.rerun()
