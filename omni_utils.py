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
# 2. FUNÇÕES DE UTILIDADE
# ==============================================================================
def get_base64_image(image_path):
    if not os.path.exists(image_path): return ""
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

# ==============================================================================
# 3. CSS GLOBAL E SIDEBAR CUSTOMIZADA
# ==============================================================================
def aplicar_estilo_global():
    """Aplica o CSS mestre e CONSTRÓI a sidebar customizada"""
    
    # Configurações Visuais por Ambiente
    if IS_TEST_ENV:
        footer_vis, card_bg, card_border, display_text = "visible", "rgba(255, 220, 50, 0.95)", "rgba(200, 160, 0, 0.5)", "OMNISFERA | TESTE"
    else:
        footer_vis, card_bg, card_border, display_text = "hidden", "rgba(255, 255, 255, 0.85)", "rgba(255, 255, 255, 0.6)", f"OMNISFERA {APP_VERSION}"

    # CSS MESTRE
    st.markdown(f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Nunito:wght@400;600;700&display=swap');
        
        /* RESET GERAL */
        html {{ scroll-behavior: smooth; }}
        html, body, [class*="css"] {{ font-family: 'Nunito', sans-serif; color: #2D3748; background-color: #F7FAFC; }}

        /* --- 1. SUMIR COM O MENU NATIVO (O SEGREDO) --- */
        [data-testid="stSidebarNav"] {{
            display: none !important;
        }}

        /* --- 2. SIDEBAR LIMPA --- */
        section[data-testid="stSidebar"] {{
            background-color: #FFFFFF !important;
            border-right: 1px solid #E2E8F0;
            box-shadow: 4px 0 20px rgba(0,0,0,0.02);
            padding-top: 0px !important;
        }}
        
        /* --- 3. ESTILIZAR NOSSOS BOTÕES DE MENU NA SIDEBAR --- */
        /* Transforma botões comuns em links elegantes */
        section[data-testid="stSidebar"] button {{
            width: 100%;
            background-color: transparent !important;
            color: #4A5568 !important;
            border: 1px solid transparent !important;
            border-radius: 8px !important;
            text-align: left !important;
            padding: 10px 15px !important;
            font-family: 'Inter', sans-serif !important;
            font-weight: 500 !important;
            margin-bottom: 4px !important;
            transition: all 0.2s ease !important;
            display: flex;
            justify-content: flex-start;
        }}
        
        /* Efeito Hover nos botões do menu */
        section[data-testid="stSidebar"] button:hover {{
            background-color: #F1F5F9 !important;
            color: #3182CE !important;
            border: 1px solid #E2E8F0 !important;
            padding-left: 20px !important; /* Desliza para direita */
        }}
        
        /* Botão "Sair" ou ações secundárias */
        .logout-btn button {{
            color: #E53E3E !important;
        }}
        .logout-btn button:hover {{
            background-color: #FFF5F5 !important;
            border-color: #FED7D7 !important;
        }}

        /* --- 4. HEADER E ELEMENTOS GERAIS --- */
        footer {{ visibility: {footer_vis} !important; }}
        header[data-testid="stHeader"] {{ background-color: transparent !important; z-index: 9999 !important; pointer-events: none; }}
        [data-testid="stToolbar"] {{ visibility: hidden !important; display: none !important; }}
        .block-container {{ padding-top: 140px !important; padding-bottom: 3rem !important; }}

        /* Menu Hambúrguer Customizado */
        [data-testid="stSidebarCollapsedControl"] {{
            position: fixed !important; top: 110px !important; left: 20px !important; z-index: 1000000 !important;
            visibility: visible !important; display: flex !important;
            background-color: white !important; border: 1px solid #E2E8F0 !important; border-radius: 12px !important;
            width: 40px !important; height: 40px !important;
            align-items: center !important; justify-content: center !important;
            color: #2D3748 !important; box-shadow: 0 4px 6px rgba(0,0,0,0.05) !important;
            pointer-events: auto !important; transition: all 0.2s ease !important;
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
    </style>
    """, unsafe_allow_html=True)

    # Renderiza HTML Fixo (Header/Badge)
    st.markdown(f'<div class="omni-badge"><span class="omni-text">{display_text}</span></div>', unsafe_allow_html=True)
    img_icon = get_base64_image("omni_icone.png")
    img_text = get_base64_image("omni_texto.png")
    
    if img_icon and img_text:
        html_header = f"""<div class="logo-container"><img src="data:image/png;base64,{img_icon}" class="logo-icon-spin"><img src="data:image/png;base64,{img_text}" class="logo-text-static"></div>"""
    else:
        html_header = "<div class='logo-container'><h1 style='color: #0F52BA; margin:0;'>🌐 OMNISFERA</h1></div>"
    st.markdown(html_header, unsafe_allow_html=True)

    # --- AQUI ESTÁ A MÁGICA: CONSTRUIR NOSSA SIDEBAR MANUALMENTE ---
    construir_sidebar_manual(img_icon)

def construir_sidebar_manual(img_icon):
    with st.sidebar:
        # 1. Logo no topo da sidebar
        st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
        if img_icon:
            st.markdown(f"""<div style="text-align: center; margin-bottom: 25px; opacity: 0.9;"><img src="data:image/png;base64,{img_icon}" width="60"></div>""", unsafe_allow_html=True)
        
        # 2. Cartão do Usuário
        if "usuario_nome" in st.session_state:
            nome = st.session_state["usuario_nome"].split()[0]
            cargo = st.session_state["usuario_cargo"]
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #F8FAFC 0%, #EFF6FF 100%); padding: 15px; border-radius: 12px; border: 1px solid #E2E8F0; margin-bottom: 30px; box-shadow: 0 2px 5px rgba(0,0,0,0.02);">
                <div style="font-family: 'Inter'; font-weight: 700; color: #2D3748; font-size: 0.95rem;">👋 Olá, {nome}</div>
                <div style="font-size: 0.75rem; color: #718096; font-weight: 600; text-transform: uppercase;">{cargo}</div>
            </div>
            """, unsafe_allow_html=True)

        # 3. MENU DE NAVEGAÇÃO (BOTÕES CUSTOMIZADOS)
        st.markdown("<div style='font-size: 0.75rem; color: #A0AEC0; font-weight: 700; margin-bottom: 10px; padding-left: 5px;'>MENU PRINCIPAL</div>", unsafe_allow_html=True)
        
        # Navegação Manual - Use st.switch_page para trocar de tela
        if st.button("🏠  Dashboard / Home"):
            st.switch_page("Home.py")
            
        if st.button("📘  PEI 360º (Plano)"):
            st.switch_page("pages/1_PEI.py")
            
        if st.button("🧩  PAEE & T.A."):
            st.switch_page("pages/2_PAE.py")
            
        if st.button("🚀  Hub de Inclusão"):
            st.switch_page("pages/3_Hub_Inclusao.py")

        # 4. BOTÃO SAIR / FEEDBACK
        st.markdown("<div style='margin-top: 40px; border-top: 1px solid #E2E8F0; padding-top: 20px;'></div>", unsafe_allow_html=True)
        
        # Feedback rápido dentro da própria sidebar (Expander)
        with st.expander("📢 Feedback Rápido"):
            st.caption("Ajude a melhorar o Omnisfera")
            txt_feed = st.text_area("msg", placeholder="Sua mensagem...", label_visibility="collapsed")
            if st.button("Enviar Feedback"):
                st.toast("Obrigado!", icon="✅")

        # Botão Sair (Exemplo visual)
        st.markdown('<div class="logout-btn">', unsafe_allow_html=True)
        if st.button("🔒 Sair do Sistema"):
            st.session_state["autenticado"] = False
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

# ==============================================================================
# 4. SISTEMA DE LOGIN (CENTRALIZADO)
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
