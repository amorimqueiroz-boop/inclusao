import streamlit as st
import os
import base64
from datetime import date

# ==============================================================================
# 1. CONFIGURAÇÕES E AMBIENTE
# ==============================================================================
APP_VERSION = "v116.0"

def verificar_ambiente():
    try: return st.secrets.get("ENV") == "TESTE"
    except: return False

IS_TEST_ENV = verificar_ambiente()

# ==============================================================================
# 2. UTILITÁRIOS (IMAGENS)
# ==============================================================================
def get_base64_image(image_path):
    if not image_path or not os.path.exists(image_path): return ""
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

# ==============================================================================
# 3. ESTILO GLOBAL (CSS LIMPO)
# ==============================================================================
def aplicar_estilo_global(logo_pagina=None):
    """
    Aplica apenas:
    1. Fontes Padrão (Nunito/Inter).
    2. Sidebar com fundo branco.
    3. Constrói o menu lateral personalizado.
    """
    
    # Define fonte e cores básicas
    st.markdown("""
    <style>
        /* Importação das Fontes */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Nunito:wght@400;600;700&display=swap');
        
        /* Aplicação Global da Fonte */
        html, body, [class*="css"] { 
            font-family: 'Nunito', sans-serif; 
        }
        
        /* Forçar Sidebar Branca */
        section[data-testid="stSidebar"] {
            background-color: #FFFFFF !important;
            border-right: 1px solid #E2E8F0;
        }
    </style>
    """, unsafe_allow_html=True)

    # Constrói a Sidebar (Logo + Navegação)
    logo_para_usar = logo_pagina if logo_pagina else "omni_icone.png"
    construir_sidebar_manual(get_base64_image(logo_para_usar))

# ==============================================================================
# 4. SIDEBAR E NAVEGAÇÃO
# ==============================================================================
def construir_sidebar_manual(img_b64):
    with st.sidebar:
        # Espaço no topo
        st.write("") 
        
        # Logo da Página (Se houver)
        if img_b64: 
            st.markdown(f"""
            <div style="text-align: center; margin-bottom: 20px;">
                <img src="data:image/png;base64,{img_b64}" width="70">
            </div>
            """, unsafe_allow_html=True)

        # Dados do Usuário (Se logado)
        if st.session_state.get("autenticado"):
            nome = st.session_state["usuario_nome"].split()[0]
            cargo = st.session_state["usuario_cargo"]
            st.markdown(f"""
            <div style="background: #F8FAFC; border: 1px solid #E2E8F0; padding: 10px; border-radius: 8px; margin-bottom: 20px;">
                <small style="color: #718096; font-weight: bold;">USUÁRIO</small><br>
                <span style="color: #2D3748; font-weight: bold;">{nome}</span><br>
                <span style="color: #718096; font-size: 0.8rem;">{cargo}</span>
            </div>
            """, unsafe_allow_html=True)

        # Links de Navegação
        st.markdown("---")
        st.caption("NAVEGAÇÃO")
        
        st.page_link("Home.py", label="Dashboard", icon="🏠")
        st.page_link("pages/1_PEI.py", label="PEI 360º", icon="📘")
        st.page_link("pages/2_PAE.py", label="PAEE & T.A.", icon="🧩")
        st.page_link("pages/3_Hub_Inclusao.py", label="Hub Inclusão", icon="🚀")
        
        # Botão Sair
        st.markdown("---")
        if st.button("🔒 Sair", use_container_width=True):
            st.session_state["autenticado"] = False
            st.rerun()

# ==============================================================================
# 5. SISTEMA DE LOGIN
# ==============================================================================
def verificar_acesso():
    if st.session_state.get("autenticado", False): return True
    
    # Layout de Login Limpo
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown(f"""
        <div style="text-align: center; border: 1px solid #E2E8F0; padding: 30px; border-radius: 15px; background: white;">
            <h2 style="color: #0F52BA;">{'🛠️ MODO TESTE' if IS_TEST_ENV else 'Bem-vindo'}</h2>
            <p>Faça login para continuar</p>
        </div>
        <br>
        """, unsafe_allow_html=True)

        if IS_TEST_ENV:
            if st.button("🚀 ENTRAR (RÁPIDO)", use_container_width=True, type="primary"):
                st.session_state.update({"autenticado": True, "usuario_nome": "Tester", "usuario_cargo": "Dev"})
                st.rerun()
        else:
            nome = st.text_input("Nome")
            cargo = st.text_input("Cargo")
            senha = st.text_input("Senha", type="password")
            
            if st.button("🔒 ACESSAR", use_container_width=True, type="primary"):
                hoje = date.today()
                senha_ok = "PEI_START_2026" if hoje <= date(2026, 1, 19) else "OMNI_PRO"
                
                if not nome or not cargo: 
                    st.warning("Preencha todos os campos.")
                elif senha != senha_ok: 
                    st.error("Senha incorreta.")
                else:
                    st.session_state.update({"autenticado": True, "usuario_nome": nome, "usuario_cargo": cargo})
                    st.rerun()
    
    return False
