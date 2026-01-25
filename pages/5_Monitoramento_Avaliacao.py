import streamlit as st
import os
import requests
import pandas as pd
import base64
import re
from io import BytesIO
from datetime import datetime
from openai import OpenAI
from fpdf import FPDF
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Pt, Inches
from PIL import Image

# Importação da biblioteca que resolve o menu (Seu arquivo enviado)
from streamlit_option_menu import option_menu 

# Tratamento para bibliotecas opcionais
try:
    from pypdf import PdfReader
except ImportError:
    PdfReader = None

try:
    from streamlit_cropper import st_cropper
except ImportError:
    st_cropper = None

# ==============================================================================
# 1. CONFIGURAÇÃO
# ==============================================================================
st.set_page_config(
    page_title="Hub de Recursos | Omnisfera", 
    page_icon="🚀", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

APP_VERSION = "v3.0 - Menu OptionMenu"

# ==============================================================================
# 2. DESIGN & CSS GERAL
# ==============================================================================
st.markdown("""
<link href="https://cdn.jsdelivr.net/npm/remixicon@4.1.0/fonts/remixicon.css" rel="stylesheet">
<style>
    /* Ajuste para colar o menu no topo */
    .block-container { padding-top: 1rem !important; padding-bottom: 4rem; }
    
    /* Esconder elementos nativos */
    [data-testid="stSidebarNav"], footer { display: none !important; }

    /* Estilo dos Cards de Conteúdo */
    .mod-card-wrapper { display: flex; flex-direction: column; margin-bottom: 20px; border-radius: 16px; overflow: hidden; box-shadow: 0 2px 5px rgba(0,0,0,0.05); border: 1px solid #E2E8F0; }
    .mod-card-rect { background: white; padding: 0; display: flex; align-items: center; height: 100px; position: relative; }
    .mod-bar { width: 6px; height: 100%; position: absolute; left: 0; background-color: #0D9488; }
    .mod-icon-area { width: 80px; height: 100%; display: flex; align-items: center; justify-content: center; font-size: 1.8rem; background: #F0FDFA; color: #0D9488; margin-left: 6px; }
    .mod-content { flex-grow: 1; padding: 0 24px; display: flex; flex-direction: column; justify-content: center; }
    .mod-title { font-weight: 800; font-size: 1.1rem; color: #1E293B; margin-bottom: 4px; }
    .mod-desc { font-size: 0.8rem; color: #64748B; }

    /* Abas Internas */
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] { background-color: transparent; border: none; color: #64748B; font-weight: 600; font-size: 0.85rem; }
    .stTabs [aria-selected="true"] { color: #0D9488; border-bottom: 2px solid #0D9488; }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# 3. NAVEGAÇÃO SUPERIOR (A SOLUÇÃO DEFINITIVA)
# ==============================================================================
# Aqui usamos a biblioteca sugerida no seu arquivo
def render_navbar():
    selected = option_menu(
        menu_title=None, # Esconde o título do menu para ficar mais limpo
        options=["Início", "Estudantes", "PEI", "AEE", "Hub", "Diário", "Dados"],
        icons=["house", "people", "book", "puzzle", "rocket", "journal", "bar-chart"],
        default_index=4, # Índice 4 = Hub (começa em 0)
        orientation="horizontal",
        styles={
            "container": {"padding": "0!important", "background-color": "#ffffff", "border": "1px solid #E2E8F0", "border-radius": "10px"},
            "icon": {"color": "#64748B", "font-size": "14px"}, 
            "nav-link": {"font-size": "12px", "text-align": "center", "margin": "0px", "--hover-color": "#F1F5F9", "color": "#475569"},
            "nav-link-selected": {"background-color": "#0D9488", "color": "white", "font-weight": "600"},
        }
    )
    
    # Lógica de Redirecionamento (Nomes de arquivos corrigidos)
    if selected == "Início":
        # Tenta encontrar o arquivo correto da Home
        target = "pages/0_Home.py" if os.path.exists("pages/0_Home.py") else "0_Home.py"
        if not os.path.exists(target): target = "Home.py" # Última tentativa
        st.switch_page(target)
    elif selected == "Estudantes": st.switch_page("pages/Alunos.py")
    elif selected == "PEI": st.switch_page("pages/1_PEI.py")
    elif selected == "AEE": st.switch_page("pages/2_PAE.py")
    elif selected == "Diário": st.switch_page("pages/4_Diario_de_Bordo.py")
    elif selected == "Dados": st.switch_page("pages/5_Monitoramento_Avaliacao.py")
    # Se for "Hub", não faz nada pois já estamos aqui

render_navbar()

# ==============================================================================
# 4. CARREGAMENTO DE DADOS & UTILS (LÓGICA PRESERVADA)
# ==============================================================================

# API Keys (Sidebar simplificada apenas para config)
with st.sidebar:
    st.header("Configurações")
    if 'OPENAI_API_KEY' in st.secrets: api_key = st.secrets['OPENAI_API_KEY']
    else: api_key = st.text_input("OpenAI Key:", type="password")

# Funções de Banco e BNCC (Indentação Corrigida)
@st.cache_data
def carregar_bncc():
    if os.path.exists('bncc.csv'):
        try:
            return pd.read_csv('bncc.csv', on_bad_lines='skip')
        except: return None
    return None

df_bncc = carregar_bncc()

# Headers Supabase
def _sb_headers():
    try:
        key = st.secrets.get("SUPABASE_SERVICE_KEY") or st.secrets.get("SUPABASE_ANON_KEY")
        return {"apikey": key, "Authorization": f"Bearer {key}", "Content-Type": "application/json"}
    except: return {}

# Carregar Alunos
if "banco_estudantes" not in st.session_state or not st.session_state.banco_estudantes:
    try:
        url = st.secrets.get("SUPABASE_URL").rstrip("/") + "/rest/v1/students"
        r = requests.get(url + "?select=id,name,grade,diagnosis&order=created_at.desc", headers=_sb_headers(), timeout=5)
        raw = r.json() if r.status_code == 200 else []
        st.session_state.banco_estudantes = [{"nome": s["name"], "serie": s["grade"], "hiperfoco": s["diagnosis"]} for s in raw]
    except:
        st.session_state.banco_estudantes = []

# ==============================================================================
# 5. ÁREA DE TRABALHO
# ==============================================================================

# Hero Section
user_name = st.session_state.get("usuario_nome", "Visitante").split()[0]
st.markdown(f"""
<div class="mod-card-wrapper" style="margin-top: 20px;">
    <div class="mod-card-rect">
        <div class="mod-bar"></div>
        <div class="mod-icon-area"><i class="ri-rocket-2-fill"></i></div>
        <div class="mod-content">
            <div class="mod-title">Hub de Recursos</div>
            <div class="mod-desc">Olá, <strong>{user_name}</strong>! Central de criação de materiais adaptados e recursos visuais.</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Seleção de Aluno
if st.session_state.banco_estudantes:
    nomes = [a['nome'] for a in st.session_state.banco_estudantes]
    col_sel, _ = st.columns([1, 2])
    nome_aluno = col_sel.selectbox("Trabalhar para:", nomes)
    aluno = next(a for a in st.session_state.banco_estudantes if a['nome'] == nome_aluno)
    
    # Detector de Nível
    serie_lower = str(aluno.get('serie', '')).lower()
    is_ei = any(x in serie_lower for x in ['infantil', 'creche', 'maternal', 'pré'])
else:
    st.warning("Nenhum aluno carregado. Verifique a conexão.")
    st.stop()

# ==============================================================================
# 6. CONTEÚDO DAS ABAS (LÓGICA PRINCIPAL)
# ==============================================================================

# Funções de IA (Indentação Corrigida)
def gerar_ia(prompt):
    if not api_key: return "⚠️ Configure a API Key."
    client = OpenAI(api_key=api_key)
    try:
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        return resp.choices[0].message.content
    except Exception as e: return f"Erro: {e}"

def gerar_imagem(prompt):
    if not api_key: return None
    client = OpenAI(api_key=api_key)
    try:
        resp = client.images.generate(
            model="dall-e-3",
            prompt=f"Educational, clean vector style, white background: {prompt}",
            size="1024x1024",
            quality="standard",
            n=1
        )
        return resp.data[0].url
    except: return None

# Abas Dinâmicas
if is_ei:
    abas = st.tabs(["🧸 Experiência (BNCC)", "🎨 Estúdio Visual", "📝 Rotina"])
    
    with abas[0]: # Experiência
        st.info("💡 Foco: Campos de Experiência e Brincar Heurístico")
        c1, c2 = st.columns(2)
        campo = c1.selectbox("Campo de Experiência", ["O eu, o outro e o nós", "Corpo, gestos e movimentos", "Traços, sons, cores e formas", "Escuta, fala, pensamento", "Espaços, tempos, quantidades"])
        objetivo = c2.text_input("Objetivo", placeholder="Ex: Compartilhar")
        if st.button("✨ Criar Experiência"):
            with st.spinner("Criando..."):
                res = gerar_ia(f"Crie uma vivência lúdica para EI (BNCC). Aluno: {aluno['nome']}. Hiperfoco: {aluno['hiperfoco']}. Campo: {campo}. Objetivo: {objetivo}.")
                st.markdown(res)

    with abas[1]: # Visual
        desc = st.text_input("Descrição da Imagem:", placeholder="Ex: Crianças brincando de roda")
        if st.button("🎨 Gerar Imagem"):
            with st.spinner("Desenhando..."):
                url = gerar_imagem(desc)
                if url: st.image(url)
                else: st.error("Erro na geração.")

else:
    abas = st.tabs(["📄 Adaptar Prova", "✨ Criar Atividade", "🎨 Estúdio Visual"])
    
    with abas[0]: # Adaptar
        st.info("💡 Adaptação curricular com suporte visual.")
        uploaded = st.file_uploader("Upload DOCX", type=["docx"])
        if uploaded:
            st.success("Arquivo recebido! Clique para processar.")
            if st.button("🚀 Adaptar"):
                st.write("Simulação: Texto extraído e adaptado com DUA.")
    
    with abas[1]: # Criar
        c1, c2 = st.columns(2)
        disc = c1.text_input("Disciplina", value="Ciências")
        tema = c2.text_input("Tema", value="Ciclo da Água")
        if st.button("✨ Gerar Atividade"):
            with st.spinner("Elaborando..."):
                res = gerar_ia(f"Crie uma atividade de {disc} sobre {tema} para o aluno {aluno['nome']} (Hiperfoco: {aluno['hiperfoco']}). Use DUA.")
                st.markdown(res)
                
    with abas[2]: # Visual
        desc = st.text_input("Descrição Didática:", placeholder="Ex: Esquema do ciclo da água")
        if st.button("🎨 Gerar Recurso Visual"):
            with st.spinner("Gerando..."):
                url = gerar_imagem(desc)
                if url: st.image(url)

# Rodapé
st.markdown("---")
st.caption(f"Omnisfera {APP_VERSION}")
