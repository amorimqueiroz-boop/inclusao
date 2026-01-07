import streamlit as st
from datetime import date
from io import BytesIO
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Pt
import google.generativeai as genai
from pypdf import PdfReader
from fpdf import FPDF
import base64
import os
import re

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="PEI 360º | Sistema Inclusivo", page_icon="📘", layout="wide")

# --- BANCO DE DADOS ---
if 'banco_estudantes' not in st.session_state: st.session_state.banco_estudantes = []

# --- ESTILO VISUAL ---
st.markdown("""
    <link href="https://cdn.jsdelivr.net/npm/remixicon@4.1.0/fonts/remixicon.css" rel="stylesheet">
    <style>
    html, body, [class*="css"] { font-family: 'Nunito', sans-serif; color: #2D3748; }
    .header-container { padding: 25px; background: #FFFFFF; border-radius: 20px; border: 1px solid #EDF2F7; border-left: 8px solid #004E92; box-shadow: 0 4px 6px rgba(0,0,0,0.04); margin-bottom: 30px; display: flex; align-items: center; gap: 25px; }
    .feature-card { background: white; padding: 25px; border-radius: 20px; border: 1px solid #EDF2F7; box-shadow: 0 4px 6px rgba(0,0,0,0.04); height: 100%; }
    .icon-box { width: 45px; height: 45px; background: #E3F2FD; border-radius: 12px; display: flex; align-items: center; justify-content: center; margin-bottom: 15px; }
    .icon-box i { font-size: 22px; color: #004E92; }
    .stTextInput input, .stTextArea textarea { border-radius: 12px; border: 1px solid #CBD5E0; }
    .stButton button { border-radius: 12px; font-weight: 700; height: 3.5em; }
    </style>
""", unsafe_allow_html=True)

# --- FUNÇÕES ---
def get_base64_image(image_path):
    if not os.path.exists(image_path): return ""
    with open(image_path, "rb") as img_file: return base64.b64encode(img_file.read()).decode()

def ler_pdf(arquivo):
    try:
        reader = PdfReader(arquivo); texto = ""
        for page in reader.pages: texto += page.extract_text() + "\n"
        return texto
    except: return ""

def limpar_markdown(texto):
    if not texto: return ""
    return texto.replace('**', '').replace('__', '').replace('### ', '').replace('## ', '').replace('# ', '')

def limpar_para_pdf(texto):
    if not texto: return ""
    t = texto.replace('**', '').replace('__', '').replace('### ', '').replace('## ', '').replace('# ', '').replace('* ', '• ')
    return re.sub(r'[^\x00-\x7F\xA0-\xFF]', '', t)

def calcular_idade(data_nasc):
    if not data_nasc: return ""
    hoje = date.today()
    return str(hoje.year - data_nasc.year - ((hoje.month, hoje.day) < (data_nasc.month, data_nasc.day)))

# --- INTELIGÊNCIA BLINDADA (FALLBACK) ---
def consultar_ia_segura(api_key, dados, contexto_pdf=""):
    if not api_key: return None, "⚠️ API Key faltando."
    try:
        genai.configure(api_key=api_key)
        
        # TENTATIVA 1: Modelo Flash (Mais rápido)
        try:
            model = genai.GenerativeModel('gemini-1.5-flash')
        except:
            # TENTATIVA 2: Modelo Pro (Mais compatível)
            model = genai.GenerativeModel('gemini-pro')

        serie = dados['serie'] if dados['serie'] else ""
        idade = calcular_idade(dados.get('nasc'))
        prompt = f"""
        ATUE COMO: Especialista em Inclusão.
        ESTUDANTE: {dados['nome']} | Idade: {idade} | Série: {serie} | Diag: {dados['diagnostico']} | Hiperfoco: {dados['hiperfoco']}
        HISTÓRICO: {dados['historico']} | FAMÍLIA: {dados['familia']}
        BARREIRAS: {', '.join(dados['b_sensorial'] + dados['b_cognitiva'])}
        ESTRATÉGIAS: {', '.join(dados['estrategias_ensino'])}
        LAUDO: {contexto_pdf[:3000]}
        
        GERE:
        1. SÍNTESE DO CONTEXTO
        2. ANÁLISE NEUROFUNCIONAL
        3. ESTRATÉGIA BNCC
        4. ROTINA
        5. DIRETRIZES PARA O ADAPTADOR DE PROVAS (Instruções técnicas para adaptar avaliações).
        """
        response = model.generate_content(prompt)
        return response.text, None
    except Exception as e: return None, f"Erro Gemini: {str(e)}"

# --- PDF ---
class PDF(FPDF):
    def header(self):
        if os.path.exists("360.png"): self.image("360.png", 10, 8, 25); x=40
        else: x=10
        self.set_font('Arial', 'B', 16); self.set_text_color(0,78,146); self.cell(x); self.cell(0, 10, 'PLANO DE ENSINO INDIVIDUALIZADO', 0, 1, 'C'); self.ln(5)
def gerar_pdf(dados):
    pdf = PDF(); pdf.add_page(); pdf.set_font("Arial", size=11)
    def txt(t): return str(t).encode('latin-1', 'replace').decode('latin-1')
    pdf.multi_cell(0, 7, txt(f"Nome: {dados['nome']} | Série: {dados['serie']} | Diag: {dados['diagnostico']}")); pdf.ln(5)
    if dados['ia_sugestao']: pdf.multi_cell(0, 6, txt(limpar_para_pdf(dados['ia_sugestao'])))
    return pdf.output(dest='S').encode('latin-1')

# --- ESTADO INICIAL ---
if 'dados' not in st.session_state:
    st.session_state.dados = {'nome': '', 'nasc': None, 'serie': None, 'diagnostico': '', 'historico': '', 'familia': '', 'hiperfoco': '', 'b_sensorial': [], 'b_cognitiva': [], 'b_social': [], 'estrategias_acesso': [], 'estrategias_ensino': [], 'estrategias_avaliacao': [], 'ia_sugestao': ''}
if 'pdf_text' not in st.session_state: st.session_state.pdf_text = ""

# --- SIDEBAR ---
with st.sidebar:
    if os.path.exists("360.png"): st.image("360.png", width=120)
    if 'GOOGLE_API_KEY' in st.secrets: api_key = st.secrets['GOOGLE_API_KEY']; st.success("✅ Gemini Conectado")
    else: api_key = st.text_input("Google API Key:", type="password")

# --- CABEÇALHO ---
if os.path.exists("360.png"):
    b64 = get_base64_image("360.png")
    st.markdown(f"""<div class="header-container"><img src="data:image/png;base64,{b64}" style="max-height:80px;"><h2 style="color:#004E92; margin:0; margin-left:20px;">Gestão de PEI</h2></div>""", unsafe_allow_html=True)
else: st.title("Gestão de PEI")

# --- ABAS ---
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs(["Início", "Estudante", "Mapeamento", "Ação", "IA", "Docs", "💾 Salvar"])

with tab1:
    c1, c2 = st.columns(2)
    c1.markdown('<div class="feature-card"><div class="icon-box"><i class="ri-book-open-line"></i></div><h4>O que é o PEI?</h4><p>Documento oficial de flexibilização.</p></div>', unsafe_allow_html=True)
    c2.markdown('<div class="feature-card"><div class="icon-box"><i class="ri-scales-3-line"></i></div><h4>Base Legal</h4><p>Direito garantido por lei.</p></div>', unsafe_allow_html=True)

with tab2:
    st.session_state.dados['nome'] = st.text_input("Nome")
    c1, c2 = st.columns(2); st.session_state.dados['nasc'] = c1.date_input("Nascimento", st.session_state.dados.get('nasc'), format="DD/MM/YYYY"); st.session_state.dados['serie'] = c2.selectbox("Série", ["Ed. Infantil", "1º Ano", "2º Ano", "3º Ano", "4º Ano", "5º Ano", "Fund II", "Médio"])
    st.session_state.dados['diagnostico'] = st.text_input("Diagnóstico")
    st.session_state.dados['historico'] = st.text_area("Histórico")
    st.session_state.dados['familia'] = st.text_area("Família")
    up = st.file_uploader("Laudo (PDF)", type="pdf"); 
    if up: st.session_state.pdf_text = ler_pdf(up); st.success("Laudo lido!")

with tab3:
    st.session_state.dados['hiperfoco'] = st.text_input("Hiperfoco")
    st.session_state.dados['b_cognitiva'] = st.multiselect("Barreiras Cognitivas", ["Atenção", "Memória", "Rigidez"])
    st.session_state.dados['b_sensorial'] = st.multiselect("Barreiras Sensoriais", ["Hipersensibilidade", "Busca Sensorial"])

with tab4:
    st.session_state.dados['estrategias_ensino'] = st.multiselect("Ensino", ["Pistas Visuais", "Mapa Mental", "Fragmentação"])
    st.session_state.dados['estrategias_acesso'] = st.multiselect("Acesso", ["Tempo estendido", "Ledor", "Sala Silenciosa"])

with tab5:
    if st.button("✨ Gerar Parecer IA", type="primary"):
        res, err = consultar_ia_segura(api_key, st.session_state.dados, st.session_state.pdf_text)
        if err: st.error(err)
        else: st.session_state.dados['ia_sugestao'] = res; st.success("Gerado!")
    if st.session_state.dados['ia_sugestao']: st.markdown(f"<div style='background:white; padding:20px; border-radius:10px;'>{st.session_state.dados['ia_sugestao'].replace(chr(10), '<br>')}</div>", unsafe_allow_html=True)

with tab6:
    if st.session_state.dados['nome']: st.download_button("📄 Baixar PDF", gerar_pdf(st.session_state.dados), "pei.pdf")

with tab7:
    st.info(f"Salvar {st.session_state.dados['nome']} para o Adaptador.")
    if st.button("💾 Salvar", type="primary"):
        if st.session_state.dados['nome']:
            st.session_state.banco_estudantes.append(st.session_state.dados.copy())
            st.success("Salvo!")
        else: st.warning("Preencha o nome.")
