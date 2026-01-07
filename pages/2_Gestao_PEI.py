import streamlit as st
import os
import base64
from datetime import date
from io import BytesIO
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Pt
from openai import OpenAI
from pypdf import PdfReader
from fpdf import FPDF
import re

# --- CONFIGURAÇÃO ---
st.set_page_config(page_title="Gestão de PEI", page_icon="📄", layout="wide")

# --- ESTILO VISUAL ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800&display=swap');
    html, body, [class*="css"] { font-family: 'Nunito', sans-serif; color: #2D3748; }
    
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] { background-color: white; border-radius: 20px; border: 1px solid #CBD5E0; }
    .stTabs [aria-selected="true"] { background-color: #FF6B6B !important; color: white !important; border: none; }
    
    .stButton > button { background-color: #004E92 !important; color: white !important; border-radius: 12px; height: 3.5em; width: 100%; }
</style>
""", unsafe_allow_html=True)

# --- FUNÇÕES ---
def ler_pdf(arquivo):
    try:
        reader = PdfReader(arquivo)
        texto = ""
        for page in reader.pages: texto += page.extract_text() + "\n"
        return texto
    except: return ""

def consultar_ia(api_key, dados, contexto_pdf=""):
    if not api_key: return None, "⚠️ Sem Chave API"
    try:
        client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")
        prompt = f"Aluno: {dados['nome']}. Diag: {dados['diagnostico']}. Histórico: {dados['historico']}. Crie um parecer técnico para PEI com: Síntese, Análise Neurofuncional e Estratégias."
        res = client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": prompt}], temperature=0.7
        )
        return res.choices[0].message.content, None
    except Exception as e: return None, str(e)

# --- DOCX ---
def gerar_docx(dados):
    doc = Document()
    doc.add_heading('PEI - PLANO DE ENSINO', 0)
    doc.add_paragraph(f"Nome: {dados['nome']}")
    if dados['ia_sugestao']: doc.add_paragraph(dados['ia_sugestao'])
    b = BytesIO(); doc.save(b); b.seek(0)
    return b

# --- STATE ---
if 'dados' not in st.session_state:
    st.session_state.dados = {
        'nome': '', 'nasc': None, 'serie': None, 'diagnostico': '', 
        'historico': '', 'familia': '', 'hiperfoco': '', 
        'b_sensorial': [], 'b_cognitiva': [], 'b_social': [],
        'estrategias_acesso': [], 'estrategias_ensino': [],
        'ia_sugestao': ''
    }

# --- INTERFACE ---
with st.sidebar:
    if 'DEEPSEEK_API_KEY' in st.secrets:
        api_key = st.secrets['DEEPSEEK_API_KEY']; st.success("✅ Chave Segura")
    else: api_key = st.text_input("Chave API:", type="password")
    st.info("Gestão de PEI | V2.18")

st.markdown("### 📄 Gestão de PEI")

tab1, tab2, tab3, tab4 = st.tabs(["Estudante", "Mapeamento", "IA & Parecer", "Documento"])

with tab1:
    c1, c2 = st.columns([2, 1])
    st.session_state.dados['nome'] = c1.text_input("Nome", st.session_state.dados['nome'])
    st.session_state.dados['diagnostico'] = c2.text_input("Diagnóstico", st.session_state.dados['diagnostico'])
    st.session_state.dados['historico'] = st.text_area("Histórico Escolar")
    
    file = st.file_uploader("Anexar Laudo (PDF)", type="pdf")
    if file: st.session_state.pdf_text = ler_pdf(file)

with tab2:
    st.session_state.dados['hiperfoco'] = st.text_input("Hiperfoco")
    st.session_state.dados['estrategias_ensino'] = st.multiselect("Estratégias de Ensino", ["Pistas Visuais", "Material Ampliado", "Tempo Estendido", "Ledor"])

with tab3:
    if st.button("✨ Gerar Parecer com IA"):
        res, err = consultar_ia(api_key, st.session_state.dados, st.session_state.get('pdf_text', ''))
        if err: st.error(err)
        else: st.session_state.dados['ia_sugestao'] = res; st.success("Gerado!")
    
    if st.session_state.dados['ia_sugestao']:
        st.text_area("Resultado:", st.session_state.dados['ia_sugestao'], height=300)

with tab4:
    if st.session_state.dados['nome']:
        st.download_button("📥 Baixar DOCX", gerar_docx(st.session_state.dados), "pei.docx")
