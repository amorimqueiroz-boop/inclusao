import streamlit as st
from openai import OpenAI
from io import BytesIO
from docx import Document
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from PIL import Image
from streamlit_cropper import st_cropper
import re
import requests
import json
import base64
import os
from datetime import date

# --- 1. CONFIGURAÇÃO INICIAL (Obrigatório ser a primeira linha) ---
st.set_page_config(page_title="Omnisfera | Ecossistema Inclusivo", page_icon="🌐", layout="wide")

# ==============================================================================
# 🔐 MÓDULO DE SEGURANÇA OMNISFERA
# ==============================================================================
def sistema_seguranca():
    # 1. CSS BASE: Limpa o topo, rodapé e ajusta o visual
    st.markdown("""
        <style>
            [data-testid="stHeader"] {visibility: hidden !important; height: 0px !important;}
            div[data-testid="stStatusWidget"] {display: none !important;}
            footer {visibility: hidden !important;}
            .stImage {display: flex; justify-content: center; margin-bottom: 20px;}
            
            /* Estilo do Termo de Aceite */
            .termo-box {
                background-color: #f8f9fa; 
                padding: 20px; 
                border-radius: 10px; 
                height: 200px; 
                overflow-y: scroll; 
                font-size: 0.9rem;
                border: 1px solid #e9ecef;
                margin-bottom: 15px;
            }
        </style>
    """, unsafe_allow_html=True)

    if "autenticado" not in st.session_state:
        st.session_state["autenticado"] = False

    # 2. SE NÃO ESTIVER LOGADO (Tela de Login Estreita)
    if not st.session_state["autenticado"]:
        st.markdown("""
            <style>
                /* Força largura estreita e centralizada para o Login */
                .block-container {max-width: 800px !important; padding-top: 3rem !important;}
                /* Esconde Sidebar no Login */
                section[data-testid="stSidebar"] {display: none !important;}
            </style>
        """, unsafe_allow_html=True)
        
        # --- Interface de Login ---
        # Tenta carregar o logo da Omnisfera
        try:
            # Certifique-se que o arquivo se chama 'ominisfera.png' ou ajuste aqui
            st.image("ominisfera.png", width=250) 
        except:
            st.markdown("<h1 style='text-align:center;'>🌐 OMNISFERA</h1>", unsafe_allow_html=True)

        st.markdown("<h3 style='text-align: center; color: #4A5568;'>Ecossistema de Gestão da Inclusão</h3>", unsafe_allow_html=True)
        st.markdown("---")
        
        st.info("""
        **Bem-vindo(a) à revolução da inclusão.**
        
        A Omnisfera foi desenvolvida para garantir que a inclusão real aconteça de forma individualizada e eficiente.
        Conforme a **Resolução do CNE (Dez/2025)**, o PEI é obrigatório e independente de laudo. Nós facilitamos essa jornada.
        """)

        # Termo com Rolagem
        st.markdown("##### 🛡️ Termo de Confidencialidade e Uso")
        termo_html = """
        <div class="termo-box">
            <strong>AMBIENTE PROTEGIDO OMNISFERA</strong><br><br>
            Ao acessar este sistema, você concorda que:<br>
            1. <strong>Propriedade Intelectual:</strong> Toda a lógica, prompts ("Engenharia de Prompt") e arquitetura do Ecossistema Omnisfera são propriedade exclusiva de <strong>Rodrigo A. Queiroz</strong>.<br>
            2. <strong>Sigilo:</strong> As metodologias aqui aplicadas são confidenciais.<br>
            3. <strong>Proibições:</strong> É estritamente proibido copiar, tirar prints (screenshots), realizar engenharia reversa ou compartilhar o acesso com terceiros não autorizados.<br>
            4. <strong>Proteção Legal:</strong> O uso indevido está sujeito às penalidades da Lei de Direitos Autorais (Lei nº 9.610/98) e medidas judiciais cabíveis.<br><br>
            <em>Este software está em fase de testes controlados.</em>
        </div>
        """
        st.markdown(termo_html, unsafe_allow_html=True)
        
        concordo = st.checkbox("Li, compreendi e aceito os termos de propriedade intelectual.")
        
        st.write("")
        
        c1, c2 = st.columns([3, 1])
        with c1:
            senha_digitada = st.text_input("Chave de Acesso:", type="password", placeholder="Digite sua credencial...")
        with c2:
            st.write(" ") 
            st.write(" ")
            if st.button("🚀 ACESSAR", type="primary", use_container_width=True):
                # Lógica de Senha (Data de Validade)
                hoje = date.today()
                # A senha muda automaticamente após 19/01/2026 para segurança
                senha_correta = "PEI_START_2026" if hoje <= date(2026, 1, 19) else "OMNISFERA_PRO"
                
                if not concordo:
                    st.warning("⚠️ É necessário aceitar os termos para prosseguir.")
                elif senha_digitada == senha_correta:
                    st.session_state["autenticado"] = True
                    st.toast("Acesso Liberado! Bem-vindo à Omnisfera.", icon="✅")
                    st.rerun()
                else:
                    st.error("🚫 Chave de acesso inválida.")
        return False

    # 3. SE ESTIVER LOGADO (Libera o App Completo)
    else:
        st.markdown("""
            <style>
                /* Libera largura total para o App (Wide Mode) */
                .block-container {max-width: 95% !important; padding-top: 1rem !important;}
                /* Mostra a Sidebar novamente */
                section[data-testid="stSidebar"] {display: flex !important;}
            </style>
        """, unsafe_allow_html=True)
        return True

# --- EXECUTA A SEGURANÇA ANTES DE TUDO ---
if not sistema_seguranca():
    st.stop() # Para o carregamento aqui se não estiver logado

# ==============================================================================
# 🚀 AQUI COMEÇA O SEU APP OMNISFERA (V18.1)
# ==============================================================================

# --- 2. BANCO DE DADOS ---
ARQUIVO_DB = "banco_alunos.json"

def carregar_banco():
    if os.path.exists(ARQUIVO_DB):
        try:
            with open(ARQUIVO_DB, "r", encoding="utf-8") as f:
                return json.load(f)
        except: return []
    return []

if 'banco_estudantes' not in st.session_state or not st.session_state.banco_estudantes:
    st.session_state.banco_estudantes = carregar_banco()

# ... (O RESTANTE DO CÓDIGO DA V18.1 CONTINUA EXATAMENTE AQUI) ...
# ... (Copie e cole todo o código da V18.1 abaixo desta linha) ...
