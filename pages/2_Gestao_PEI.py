import streamlit as st
import requests
import json
from datetime import date
from io import BytesIO
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Pt
from pypdf import PdfReader
from fpdf import FPDF
import base64
import os
import re

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="PEI 360º | Sistema Inclusivo",
    page_icon="📘",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- BANCO DE DADOS ---
if 'banco_estudantes' not in st.session_state:
    st.session_state.banco_estudantes = []

# --- ESTILO VISUAL ---
st.markdown("""
    <link href="https://cdn.jsdelivr.net/npm/remixicon@4.1.0/fonts/remixicon.css" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800&display=swap" rel="stylesheet">
    <style>
    html, body, [class*="css"] { font-family: 'Nunito', sans-serif; color: #2D3748; }
    :root { --brand-blue: #004E92; --brand-coral: #FF6B6B; --bg-light: #F7FAFC; }
    .header-container { padding: 25px; background: #FFFFFF; border-radius: 20px; border: 1px solid #EDF2F7; border-left: 8px solid var(--brand-blue); box-shadow: 0 4px 6px rgba(0,0,0,0.04); margin-bottom: 30px; display: flex; align-items: center; gap: 25px; }
    .stTabs [data-baseweb="tab-list"] { gap: 10px; background-color: transparent; padding: 10px 0; justify-content: flex-start; flex-wrap: wrap; }
    .stTabs [data-baseweb="tab"] { height: 42px; background-color: #FFFFFF; border-radius: 20px; border: 1px solid #CBD5E0; color: #4A5568; padding: 0 20px; font-weight: 700; font-size: 0.9rem; flex-grow: 0; }
    .stTabs [aria-selected="true"] { background-color: var(--brand-coral) !important; color: white !important; border-color: var(--brand-coral) !important; }
    .feature-card { background: white; padding: 25px; border-radius: 20px; border: 1px solid #EDF2F7; height: 100%; display: flex; flex-direction: column; }
    .icon-box { width: 45px; height: 45px; background: #E3F2FD; border-radius: 12px; display: flex; align-items: center; justify-content: center; margin-bottom: 15px; }
    .icon-box i { font-size: 22px; color: var(--brand-blue); }
    .stTextInput input, .stTextArea textarea { border-radius: 12px !important; border: 1px solid #CBD5E0 !important; }
    div[data-testid="column"] .stButton button { border-radius: 12px !important; font-weight: 700 !important; height: 3.5em !important; width: 100%; }
    </style>
""", unsafe_allow_html=True)

# --- FUNÇÕES AUXILIARES ---
def get_base64_image(image_path):
    if not os.path.exists(image_path): return ""
    with open(image_path, "rb") as img_file: return base64.b64encode(img_file.read()).decode()

def ler_pdf(arquivo):
    if arquivo is None: return ""
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

# --- INTEGRAÇÃO IA (GEMINI 1.5 FLASH - VALIDADO PELO SEU TESTE) ---
def consultar_ia_final(api_key, dados, contexto_pdf=""):
    if not api_key: return None, "⚠️ Chave API faltando. Verifique o Secrets."
    
    # URL do modelo que apareceu na sua lista de sucesso
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    headers = {'Content-Type': 'application/json'}
    
    serie = dados['serie'] if dados['serie'] else ""
    idade = calcular_idade(dados.get('nasc'))
    
    prompt_text = f"""
    ATUE COMO: Especialista em Inclusão e Neurociência.
    ESTUDANTE: {dados['nome']} | Idade: {idade} | Série: {serie} | Diagnóstico: {dados['diagnostico']}
    HISTÓRICO: {dados['historico']} | FAMÍLIA: {dados['familia']}
    BARREIRAS: {', '.join(dados['b_sensorial'] + dados['b_cognitiva'])}
    ESTRATÉGIAS: {', '.join(dados['estrategias_acesso'] + dados['estrategias_ensino'])}
    LAUDO: {contexto_pdf[:4000]}
    
    GERE UM RELATÓRIO TÉCNICO ESTRUTURADO (Use Markdown):
    1. SÍNTESE DO CONTEXTO
    2. ANÁLISE NEUROFUNCIONAL
    3. ESTRATÉGIA BNCC
    4. ROTINA
    5. DIRETRIZES PARA O ADAPTADOR DE PROVAS (Instruções técnicas claras: tamanho de fonte, tipo de enunciado, suporte visual).
    """
    
    payload = {"contents": [{"parts": [{"text": prompt_text}]}]}
    
    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        
        if response.status_code == 200:
            try:
                return response.json()['candidates'][0]['content']['parts'][0]['text'], None
            except:
                return None, "O Google respondeu, mas o formato estava vazio. Tente novamente."
        else:
            return None, f"Erro Google ({response.status_code}): {response.text}"
            
    except Exception as e:
        return None, f"Erro de Conexão: {str(e)}"

# --- PDF & DOCX ---
class PDF(FPDF):
    def header(self):
        if os.path.exists("360.png"): self.image("360.png", 10, 8, 25); x=40
        else: x=10
        self.set_font('Arial', 'B', 16); self.set_text_color(0, 78, 146); self.cell(x); self.cell(0, 10, 'PLANO DE ENSINO INDIVIDUALIZADO', 0, 1, 'C'); self.ln(5)
    def footer(self):
        self.set_y(-15); self.set_font('Arial', 'I', 8); self.set_text_color(128); self.cell(0, 10, f'Página {self.page_no()} | Documento Confidencial', 0, 0, 'C')

def gerar_pdf(dados):
    pdf = PDF(); pdf.add_page(); pdf.set_font("Arial", size=11)
    def txt(t): return str(t).encode('latin-1', 'replace').decode('latin-1')
    idade = calcular_idade(dados.get('nasc'))
    pdf.set_font("Arial", 'B', 12); pdf.set_text_color(0, 78, 146); pdf.cell(0, 10, txt("1. IDENTIFICAÇÃO"), 0, 1)
    pdf.set_font("Arial", size=11); pdf.set_text_color(0)
    pdf.multi_cell(0, 7, txt(f"Nome: {dados['nome']} | Idade: {idade} | Série: {dados['serie']}\nDiag: {dados['diagnostico']}")); pdf.ln(3)
    pdf.set_font("Arial", 'B', 12); pdf.set_text_color(0, 78, 146); pdf.cell(0, 10, txt("2. ESTRATÉGIAS"), 0, 1)
    pdf.set_font("Arial", size=11); pdf.set_text_color(0)
    if dados['estrategias_acesso']: pdf.multi_cell(0, 7, txt("Acesso: " + limpar_para_pdf(', '.join(dados['estrategias_acesso']))))
    if dados['estrategias_ensino']: pdf.multi_cell(0, 7, txt("Ensino: " + limpar_para_pdf(', '.join(dados['estrategias_ensino']))))
    if dados['ia_sugestao']:
        pdf.ln(5); pdf.set_font("Arial", 'B', 12); pdf.set_text_color(0, 78, 146); pdf.cell(0, 10, txt("3. PARECER TÉCNICO"), 0, 1)
        pdf.set_font("Arial", size=11); pdf.set_text_color(50); pdf.multi_cell(0, 6, txt(limpar_para_pdf(dados['ia_sugestao'])))
    return pdf.output(dest='S').encode('latin-1')

def gerar_docx(dados):
    doc = Document(); style = doc.styles['Normal']; style.font.name = 'Arial'; style.font.size = Pt(11)
    doc.add_heading('PLANO DE ENSINO INDIVIDUALIZADO', 0).alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_paragraph(f"Nome: {dados['nome']}")
    if dados['ia_sugestao']: doc.add_heading('Parecer Técnico', level=1); doc.add_paragraph(limpar_markdown(dados['ia_sugestao']))
    buffer = BytesIO(); doc.save(buffer); buffer.seek(0)
    return buffer

# --- ESTADO INICIAL ---
if 'dados' not in st.session_state:
    st.session_state.dados = {'nome': '', 'nasc': None, 'serie': None, 'diagnostico': '', 'historico': '', 'familia': '', 'hiperfoco': '', 'b_sensorial': [], 'b_cognitiva': [], 'b_social': [], 'estrategias_acesso': [], 'estrategias_ensino': [], 'estrategias_avaliacao': [], 'ia_sugestao': ''}
if 'pdf_text' not in st.session_state: st.session_state.pdf_text = ""

# --- SIDEBAR ---
with st.sidebar:
    if os.path.exists("360.png"): st.image("360.png", width=120)
    if 'GOOGLE_API_KEY' in st.secrets: api_key = st.secrets['GOOGLE_API_KEY']; st.success("✅ Chave Conectada")
    else: api_key = st.text_input("Cole a Google API Key:", type="password")

# --- CABEÇALHO ---
if os.path.exists("360.png"):
    b64 = get_base64_image("360.png")
    st.markdown(f"""<div class="header-container"><img src="data:image/png;base64,{b64}" style="max-height:80px;"><h2 style="color:#004E92; margin:0; margin-left:20px;">Gestão de PEI</h2></div>""", unsafe_allow_html=True)
else: st.title("Gestão de PEI")

# --- ABAS ---
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs(["Início", "Estudante", "Mapeamento", "Ação", "IA", "Docs", "💾 Salvar"])

with tab1:
    c1, c2 = st.columns(2)
    c1.markdown('<div class="feature-card"><div class="icon-box"><i class="ri-book-open-line"></i></div><h4>O que é o PEI?</h4><p>Documento oficial de flexibilização escolar.</p></div>', unsafe_allow_html=True)
    c2.markdown('<div class="feature-card"><div class="icon-box"><i class="ri-scales-3-line"></i></div><h4>Base Legal</h4><p>Garantia de direitos de aprendizagem.</p></div>', unsafe_allow_html=True)

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
    st.markdown("### <i class='ri-robot-line'></i> Consultor Inteligente (Gemini Flash)", unsafe_allow_html=True)
    if st.button("✨ Gerar Parecer IA", type="primary"):
        # CHAMA A FUNÇÃO FINAL (GEMINI FLASH)
        res, err = consultar_ia_final(api_key, st.session_state.dados, st.session_state.pdf_text)
        if err: st.error(err)
        else: st.session_state.dados['ia_sugestao'] = res; st.success("Gerado com Sucesso!")
    
    if st.session_state.dados['ia_sugestao']:
        st.markdown(f"<div style='background:white; padding:20px; border-radius:10px;'>{st.session_state.dados['ia_sugestao'].replace(chr(10), '<br>')}</div>", unsafe_allow_html=True)

with tab6:
    if st.session_state.dados['nome']: 
        c1, c2 = st.columns(2)
        c1.download_button("📄 PDF", gerar_pdf(st.session_state.dados), "pei.pdf")
        c2.download_button("📥 Word", gerar_docx(st.session_state.dados), "pei.docx")

with tab7:
    st.markdown("### <i class='ri-save-3-line'></i> Integração", unsafe_allow_html=True)
    st.info(f"Salvar **{st.session_state.dados['nome']}** para o Adaptador de Provas.")
    if st.button("💾 Salvar Aluno", type="primary"):
        if st.session_state.dados['nome']:
            perfil = st.session_state.dados.copy()
            perfil['idade_calculada'] = calcular_idade(st.session_state.dados.get('nasc'))
            st.session_state.banco_estudantes.append(perfil)
            st.success("Salvo!")
        else: st.warning("Preencha o nome.")

st.markdown("""<div style="text-align: center; margin-top: 50px; color: #A0AEC0; font-size: 0.85rem; border-top: 1px solid #E2E8F0; padding-top: 20px;">V2.26 Final (Gemini Flash)</div>""", unsafe_allow_html=True)
