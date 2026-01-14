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
    """Detecta se é Teste ou Produção via Secrets"""
    try:
        return st.secrets.get("ENV") == "TESTE"
    except:
        return False

# Variável Global para ser usada nas páginas
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
    """Aplica CSS que vale para TODAS as páginas (Header, Footer, Menu, Fontes)"""
    
    # Lógica do Rodapé e Cores
    if IS_TEST_ENV:
        footer_vis = "visible"
        card_bg = "rgba(255, 220, 50, 0.95)" # Amarelo Teste
        card_border = "rgba(200, 160, 0, 0.5)"
        display_text = "OMNISFERA | TESTE"
    else:
        footer_vis = "hidden" # ESCONDE NO PÚBLICO
        card_bg = "rgba(255, 255, 255, 0.85)"
        card_border = "rgba(255, 255, 255, 0.6)"
        display_text = f"OMNISFERA {APP_VERSION}"

    # CSS MESTRE
    st.markdown(f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&family=Nunito:wght@400;600;700&display=swap');
        
        /* RESET BÁSICO */
        html {{ scroll-behavior: smooth; }}
        html, body, [class*="css"] {{ font-family: 'Nunito', sans-serif; color: #2D3748; background-color: #F7FAFC; }}

        /* --- CONTROLE GLOBAL DE VISIBILIDADE --- */
        footer {{ visibility: {footer_vis} !important; }}
        header[data-testid="stHeader"] {{ background-color: transparent !important; z-index: 9999 !important; pointer-events: none; }}
        [data-testid="stToolbar"] {{ visibility: hidden !important; display: none !important; }}

        /* --- MENU LATERAL (HAMBURGUER) REPOSICIONADO --- */
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
        [data-testid="stSidebarCollapsedControl"]:hover {{ background-color: #3182CE !important; color: white !important; }}

        /* --- HEADER DE VIDRO (GLOBAL) --- */
        .logo-container {{
            display: flex; align-items: center; justify-content: center; gap: 20px; 
            position: fixed; top: 0; left: 0; width: 100%; height: 100px;
            background-color: rgba(247, 250, 252, 0.85); backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px);
            border-bottom: 1px solid rgba(255, 255, 255, 0.5);
            z-index: 9998; box-shadow: 0 4px 20px rgba(0,0,0,0.03);
        }}
        .logo-icon-spin {{ height: 80px; width: auto; animation: spin 45s linear infinite; }}
        .logo-text-static {{ height: 50px; width: auto; }}
        @keyframes spin {{ from {{ transform: rotate(0deg); }} to {{ transform: rotate(360deg); }} }}

        /* --- CARD OMNISFERA (GLOBAL) --- */
        .omni-badge {{
            position: fixed; top: 20px; right: 20px;
            background: {card_bg}; border: 1px solid {card_border};
            backdrop-filter: blur(8px); padding: 8px 25px; min-width: 200px;
            border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.08);
            z-index: 999990; display: flex; align-items: center; justify-content: center; pointer-events: none;
        }}
        .omni-text {{ font-family: 'Inter', sans-serif; font-weight: 800; font-size: 0.75rem; color: #2D3748; letter-spacing: 2px; text-transform: uppercase; }}
        
        /* Ajuste de topo para todas as páginas */
        .block-container {{ padding-top: 140px !important; padding-bottom: 3rem !important; }}
    </style>
    """, unsafe_allow_html=True)

    # Renderiza os elementos HTML fixos (Logo e Badge)
    st.markdown(f'<div class="omni-badge"><span class="omni-text">{display_text}</span></div>', unsafe_allow_html=True)
    
    img_icon = get_base64_image("omni_icone.png")
    img_text = get_base64_image("omni_texto.png")
    
    if img_icon and img_text:
        html_header = f"""
        <div class="logo-container">
            <img src="data:image/png;base64,{img_icon}" class="logo-icon-spin">
            <img src="data:image/png;base64,{img_text}" class="logo-text-static">
        </div>"""
    else:
        html_header = "<div class='logo-container'><h1 style='color: #0F52BA; margin:0;'>🌐 OMNISFERA</h1></div>"
    
    st.markdown(html_header, unsafe_allow_html=True)

# ==============================================================================
# 4. SISTEMA DE LOGIN (CENTRALIZADO)
# ==============================================================================
def verificar_acesso():
    """Função ÚNICA de login para ser chamada em qualquer página"""
    
    # Se já estiver autenticado, retorna True e segue o baile
    if st.session_state.get("autenticado", False):
        return True

    # Se não, exibe a tela de login
    renderizar_tela_login()
    return False # Para a execução da página

def renderizar_tela_login():
    # CSS Específico do Login (Só carrega se não estiver logado)
    st.markdown("""<style>[data-testid="stHeader"] {visibility: hidden !important;}</style>""", unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        # Define estilo baseado no ambiente
        cor_borda = "#FF9800" if IS_TEST_ENV else "#E2E8F0"
        titulo = "🛠️ MODO TESTE" if IS_TEST_ENV else "Bem-vindo!"
        btn_txt = "🚀 ENTRAR (TESTE)" if IS_TEST_ENV else "🔒 ACESSAR"
        
        st.markdown(f"""
        <div style="background: white; padding: 40px; border-radius: 20px; border: 2px solid {cor_borda}; text-align: center; box-shadow: 0 10px 30px rgba(0,0,0,0.1); margin-top: 50px;">
            <h2 style="color: #0F52BA; margin: 0;">{titulo}</h2>
            <p style="color: #718096; font-size: 0.9rem;">Ecossistema Omnisfera</p>
            <hr style="margin: 20px 0;">
        </div>
        """, unsafe_allow_html=True)
        
        nome = st.text_input("Nome", placeholder="Seu nome")
        cargo = st.text_input("Cargo", placeholder="Seu cargo")
        
        if not IS_TEST_ENV:
            st.markdown("<div style='font-size: 0.8rem; color: #4A5568; background: #F7FAFC; padding: 10px; border-radius: 8px; margin: 10px 0;'>📜 Aceito os termos de uso e confidencialidade.</div>", unsafe_allow_html=True)
            termo = st.checkbox("Li e concordo")
            senha = st.text_input("Senha", type="password")
        
        if st.button(btn_txt, use_container_width=True, type="primary"):
            if IS_TEST_ENV:
                # Login Teste: Libera Geral
                st.session_state["autenticado"] = True
                st.session_state["usuario_nome"] = nome if nome else "Tester"
                st.session_state["usuario_cargo"] = cargo if cargo else "Dev"
                st.rerun()
            else:
                # Login Prod: Valida tudo
                hoje = date.today()
                senha_ok = "PEI_START_2026" if hoje <= date(2026, 1, 19) else "OMNI_PRO"
                
                if not termo: st.warning("Aceite os termos.")
                elif not nome or not cargo: st.warning("Preencha seus dados.")
                elif senha != senha_ok: st.error("Senha incorreta.")
                else:
                    st.session_state["autenticado"] = True
                    st.session_state["usuario_nome"] = nome
                    st.session_state["usuario_cargo"] = cargo
                    st.rerun()
