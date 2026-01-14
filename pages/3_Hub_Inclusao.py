import streamlit as st
import os
from openai import OpenAI
from datetime import date
from io import BytesIO
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Pt, Inches
from pypdf import PdfReader
from fpdf import FPDF
import base64
import re
import json
import requests
from PIL import Image
from streamlit_cropper import st_cropper

# ==============================================================================
# 1. CONFIGURAÇÃO E AMBIENTE
# ==============================================================================
st.set_page_config(page_title="Omnisfera | Hub", page_icon="🚀", layout="wide")

try:
    IS_TEST_ENV = st.secrets.get("ENV") == "TESTE"
except:
    IS_TEST_ENV = False

# ==============================================================================
# 2. UTILITÁRIOS VISUAIS E CSS
# ==============================================================================
def get_logo_base64():
    caminhos = ["omni_icone.png", "logo.png", "iconeaba.png"]
    for c in caminhos:
        if os.path.exists(c):
            with open(c, "rb") as f:
                return f"data:image/png;base64,{base64.b64encode(f.read()).decode()}"
    return "https://cdn-icons-png.flaticon.com/512/1183/1183672.png"

src_logo_giratoria = get_logo_base64()

# Cores do Tema
if IS_TEST_ENV:
    card_bg = "rgba(255, 220, 50, 0.95)" 
    card_border = "rgba(200, 160, 0, 0.5)"
else:
    card_bg = "rgba(255, 255, 255, 0.85)"
    card_border = "rgba(255, 255, 255, 0.6)"

st.markdown(f"""
<style>
    /* OMNISFERA BADGE */
    .omni-badge {{
        position: fixed; top: 15px; right: 15px;
        background: {card_bg}; border: 1px solid {card_border};
        backdrop-filter: blur(8px); -webkit-backdrop-filter: blur(8px);
        padding: 4px 30px; min-width: 260px; justify-content: center;
        border-radius: 20px; box-shadow: 0 4px 15px rgba(0,0,0,0.08);
        z-index: 999990; display: flex; align-items: center; gap: 10px;
        pointer-events: none;
    }}
    .omni-text {{ font-family: 'Nunito', sans-serif; font-weight: 800; font-size: 0.9rem; color: #2D3748; letter-spacing: 1px; text-transform: uppercase; }}
    @keyframes spin-slow {{ from {{ transform: rotate(0deg); }} to {{ transform: rotate(360deg); }} }}
    .omni-logo-spin {{ height: 26px; width: 26px; animation: spin-slow 10s linear infinite; }}

    /* ESTILO GERAL */
    html, body, [class*="css"] {{ font-family: 'Nunito', sans-serif; color: #2D3748; }}
    
    /* HEADER E CARDS */
    .header-hub {{ background: white; padding: 20px 30px; border-radius: 12px; border-left: 6px solid #3182CE; box-shadow: 0 2px 4px rgba(0,0,0,0.05); margin-bottom: 20px; display: flex; align-items: center; gap: 25px; }}
    .student-header {{ background-color: #EBF8FF; border: 1px solid #BEE3F8; border-radius: 12px; padding: 15px 25px; margin-bottom: 25px; display: flex; justify-content: space-between; align-items: center; }}
    .student-label {{ font-size: 0.85rem; color: #718096; font-weight: 700; text-transform: uppercase; }}
    .student-value {{ font-size: 1.1rem; color: #2C5282; font-weight: 800; }}
    .pedagogia-box {{ background-color: #F7FAFC; border-left: 4px solid #3182CE; padding: 15px; border-radius: 0 8px 8px 0; margin-bottom: 20px; font-size: 0.9rem; color: #4A5568; }}
    .pedagogia-title {{ color: #2C5282; font-weight: 700; display: flex; align-items: center; gap: 8px; margin-bottom: 5px; }}
    .validado-box {{ background-color: #C6F6D5; color: #22543D; padding: 15px; border-radius: 8px; text-align: center; font-weight: bold; margin-top: 15px; border: 1px solid #276749; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }}
    .analise-box {{ background-color: #F0FFF4; border: 1px solid #C6F6D5; border-radius: 8px; padding: 20px; margin-bottom: 20px; color: #22543D; }}
    .analise-title {{ font-weight: bold; font-size: 1.1rem; margin-bottom: 10px; display: flex; align-items: center; gap: 8px; }}

    /* ELEMENTOS UI */
    .stTabs [data-baseweb="tab-list"] {{ gap: 8px; flex-wrap: wrap; }}
    .stTabs [data-baseweb="tab"] {{ border-radius: 6px; padding: 8px 16px; background-color: white; border: 1px solid #E2E8F0; font-size: 0.9rem; transition: all 0.2s; }}
    .stTabs [aria-selected="true"] {{ background-color: #3182CE !important; color: white !important; border-color: #3182CE !important; }}
    div[data-testid="column"] .stButton button[kind="primary"] {{ border-radius: 10px !important; height: 50px; width: 100%; background-color: #3182CE !important; color: white !important; font-weight: 800 !important; border: none; transition: 0.3s; }}
    div[data-testid="column"] .stButton button[kind="primary"]:hover {{ background-color: #2B6CB0 !important; }}
    div[data-testid="column"] .stButton button[kind="secondary"] {{ border-radius: 10px !important; height: 50px; width: 100%; border: 2px solid #CBD5E0 !important; color: #4A5568 !important; font-weight: bold; }}
</style>

<div class="omni-badge">
    <img src="{src_logo_giratoria}" class="omni-logo-spin">
    <span class="omni-text">OMNISFERA</span>
</div>
""", unsafe_allow_html=True)

# ==============================================================================
# 3. AUTENTICAÇÃO E BANCO DE DADOS
# ==============================================================================
def verificar_acesso():
    if "autenticado" not in st.session_state or not st.session_state["autenticado"]:
        st.error("🔒 Acesso Negado. Por favor, faça login na Página Inicial.")
        st.stop()
    
    st.markdown("""
        <style>
            footer {visibility: hidden !important;}
            [data-testid="stHeader"] { visibility: visible !important; background-color: transparent !important; }
            .block-container {padding-top: 2rem !important;}
        </style>
    """, unsafe_allow_html=True)

verificar_acesso()

# Sidebar de Navegação
with st.sidebar:
    try:
        st.image("ominisfera.png", width=150)
    except:
        st.write("🌐 OMNISFERA")
    st.markdown("---")
    if st.button("🏠 Voltar para Home", use_container_width=True):
        st.switch_page("Home.py")
    st.markdown("---")

ARQUIVO_DB = "banco_alunos.json"

def carregar_banco():
    usuario_atual = st.session_state.get("usuario_nome", "")
    if os.path.exists(ARQUIVO_DB):
        try:
            with open(ARQUIVO_DB, "r", encoding="utf-8") as f:
                todos_alunos = json.load(f)
                return [aluno for aluno in todos_alunos if aluno.get('responsavel') == usuario_atual]
        except: return []
    return []

if 'banco_estudantes' not in st.session_state or not st.session_state.banco_estudantes:
    st.session_state.banco_estudantes = carregar_banco()

# ==============================================================================
# 4. FUNÇÕES CORE (IA & PROCESSAMENTO)
# ==============================================================================

# --- Helpers de Imagem e DOCX ---
def get_img_tag(file_path, width):
    if os.path.exists(file_path):
        with open(file_path, "rb") as f:
            data = base64.b64encode(f.read()).decode("utf-8")
        return f'<img src="data:image/png;base64,{data}" width="{width}">'
    return "🚀"

def extrair_dados_docx(uploaded_file):
    uploaded_file.seek(0); imagens = []; texto = ""
    try:
        doc = Document(uploaded_file)
        texto = "\n".join([p.text for p in doc.paragraphs if p.text.strip() != ""])
        for rel in doc.part.rels.values():
            if "image" in rel.target_ref:
                img_data = rel.target_part.blob
                if len(img_data) > 1024: imagens.append(img_data)
    except: pass
    return texto, imagens

def sanitizar_imagem(image_bytes):
    try:
        img = Image.open(BytesIO(image_bytes)).convert("RGB")
        out = BytesIO()
        img.save(out, format="JPEG", quality=90)
        return out.getvalue()
    except: return None

def baixar_imagem_url(url):
    try:
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200: return BytesIO(resp.content)
    except: pass
    return None

def buscar_imagem_unsplash(query, access_key):
    if not access_key: return None
    # Remove caracteres especiais para busca
    query_clean = re.sub(r'[^\w\s]', '', query).strip()
    url = f"https://api.unsplash.com/search/photos?query={query_clean}&per_page=1&client_id={access_key}&lang=pt"
    try:
        resp = requests.get(url, timeout=5)
        data = resp.json()
        if data.get('results'):
            return data['results'][0]['urls']['regular']
    except: pass
    return None

def garantir_tag_imagem(texto):
    if "[[IMG" not in texto.upper() and "[[GEN_IMG" not in texto.upper():
        match = re.search(r'(\n|\. )', texto)
        if match:
            pos = match.end()
            return texto[:pos] + "\n\n[[IMG_1]]\n\n" + texto[pos:]
        return texto + "\n\n[[IMG_1]]"
    return texto

def construir_docx_final(texto_ia, aluno, materia, mapa_imgs, img_dalle_url, tipo_atv, sem_cabecalho=False):
    doc = Document(); style = doc.styles['Normal']; style.font.name = 'Arial'; style.font.size = Pt(12)
    
    if not sem_cabecalho:
        doc.add_heading(f'{tipo_atv.upper()} ADAPTADA - {materia.upper()}', 0).alignment = WD_ALIGN_PARAGRAPH.CENTER
        doc.add_paragraph(f"Estudante: {aluno['nome']}").alignment = WD_ALIGN_PARAGRAPH.CENTER
        doc.add_paragraph("_"*50)
        doc.add_heading('Atividades', level=2)

    linhas = texto_ia.split('\n')
    for linha in linhas:
        # Lógica para detectar e inserir imagens
        tag_match = re.search(r'\[\[(IMG|GEN_IMG).*?(\d+)\]\]', linha, re.IGNORECASE)
        if tag_match:
            partes = re.split(r'(\[\[(?:IMG|GEN_IMG).*?\d+\]\])', linha, flags=re.IGNORECASE)
            for parte in partes:
                sub_match = re.search(r'(\d+)', parte)
                if ("IMG" in parte.upper() or "GEN_IMG" in parte.upper()) and sub_match:
                    num = int(sub_match.group(1))
                    img_bytes = mapa_imgs.get(num)
                    # Fallback se tiver apenas 1 imagem mapeada
                    if not img_bytes and len(mapa_imgs) == 1: img_bytes = list(mapa_imgs.values())[0]
                    if img_bytes:
                        try:
                            p = doc.add_paragraph()
                            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                            r = p.add_run()
                            r.add_picture(BytesIO(img_bytes), width=Inches(4.5))
                        except: pass
                elif parte.strip():
                    doc.add_paragraph(parte.strip())
        else:
            if linha.strip(): doc.add_paragraph(linha.strip())
            
    buffer = BytesIO(); doc.save(buffer); buffer.seek(0)
    return buffer

# --- Gerenciador Central de Imagens ---

def obter_recurso_visual(api_key, prompt, unsplash_key=None, modo="ia_strict", feedback_anterior=""):
    """
    Modos:
    - 'ia_strict': Força o uso do DALL-E (Estúdio Visual e CAA).
    - 'stock_first': Tenta Unsplash primeiro, fallback para DALL-E (Criação de Questões).
    """
    client = OpenAI(api_key=api_key)
    prompt_final = prompt
    if feedback_anterior:
        prompt_final = f"{prompt}. Adjustment requested by user: {feedback_anterior}"

    # 1. MODO STOCK FIRST (Prioridade Banco de Imagens)
    if modo == "stock_first" and unsplash_key:
        # Tenta extrair termo chave do prompt para busca
        termo = prompt.split('.')[0] if '.' in prompt else prompt
        url_stock = buscar_imagem_unsplash(termo, unsplash_key)
        if url_stock:
            return url_stock
    
    # 2. MODO IA / FALLBACK (DALL-E 3)
    try:
        didactic_prompt = f"Educational textbook illustration, clean flat vector style, white background. CRITICAL RULE: STRICTLY NO TEXT, NO TYPOGRAPHY, NO ALPHABET, NO NUMBERS. Visual representation of: {prompt_final}"
        resp = client.images.generate(model="dall-e-3", prompt=didactic_prompt, size="1024x1024", quality="standard", n=1)
        return resp.data[0].url
    except Exception as e:
        # Se IA falhar e estiver em stock_first mas não achou antes, tenta stock de novo como último recurso
        if modo == "stock_first" and unsplash_key:
             return buscar_imagem_unsplash(prompt, unsplash_key)
        return None

def gerar_pictograma_caa(api_key, conceito, feedback_anterior=""):
    client = OpenAI(api_key=api_key)
    ajuste = f" CORREÇÃO: {feedback_anterior}" if feedback_anterior else ""
    prompt_caa = f"""
    Create a COMMUNICATION SYMBOL (AAC/PECS) for: '{conceito}'. {ajuste}
    STYLE: Flat vector icon (ARASAAC style), White background, Thick black outlines, High contrast.
    CRITICAL: MUTE IMAGE. NO TEXT. NO WORDS. NO LETTERS. NO NUMBERS.
    """
    try:
        resp = client.images.generate(model="dall-e-3", prompt=prompt_caa, size="1024x1024", quality="standard", n=1)
        return resp.data[0].url
    except: return None

# --- Funções de Texto (GPT) ---

def adaptar_conteudo_docx(api_key, aluno, texto, materia, tema, tipo_atv, remover_resp, questoes_mapeadas, modo_profundo=False, feedback_anterior=""):
    client = OpenAI(api_key=api_key)
    lista_q = ", ".join([str(n) for n in questoes_mapeadas])
    style = "Seja didático e use Cadeia de Pensamento." if modo_profundo else "Seja objetivo."
    ajuste = f"IMPORTANTE - AJUSTE SOLICITADO PELO PROFESSOR: {feedback_anterior}" if feedback_anterior else ""
    
    prompt = f"""
    ESPECIALISTA EM DUA E INCLUSÃO. {style}
    {ajuste}
    
    1. ANALISE O PERFIL: {aluno.get('ia_sugestao', '')[:1000]}
    2. ADAPTE A PROVA: Use o hiperfoco ({aluno.get('hiperfoco', 'Geral')}) em 30% das questões.
    REGRA SAGRADA IMAGEM: O professor indicou imagens nas questões: {lista_q}.
    Nessas questões, a estrutura OBRIGATÓRIA: 1. Enunciado -> 2. [[IMG_número]] -> 3. Alternativas.
    
    SAÍDA OBRIGATÓRIA:
    [ANÁLISE PEDAGÓGICA] ...análise... ---DIVISOR--- [ATIVIDADE] ...atividade...
    
    CONTEXTO: {materia} | {tema}. {"REMOVA GABARITO." if remover_resp else ""}
    TEXTO ORIGINAL: {texto}
    """
    try:
        resp = client.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "user", "content": prompt}], temperature=0.7 if modo_profundo else 0.4)
        full = resp.choices[0].message.content
        if "---DIVISOR---" in full:
            p = full.split("---DIVISOR---")
            return p[0].replace("[ANÁLISE PEDAGÓGICA]", "").strip(), p[1].replace("[ATIVIDADE]", "").strip()
        return "Análise indisponível.", full
    except Exception as e: return str(e), ""

def adaptar_conteudo_imagem(api_key, aluno, imagem_bytes, materia, tema, tipo_atv, livro_professor, modo_profundo=False, feedback_anterior=""):
    client = OpenAI(api_key=api_key)
    if not imagem_bytes: return "Erro: Imagem vazia", ""
    b64 = base64.b64encode(imagem_bytes).decode('utf-8')
    instrucao_livro = "ATENÇÃO: Remova todo gabarito/respostas." if livro_professor else ""
    ajuste = f"IMPORTANTE - AJUSTE SOLICITADO: {feedback_anterior}" if feedback_anterior else ""

    prompt = f"""
    ATUAR COMO: Especialista em Acessibilidade e OCR.
    {ajuste}
    
    1. Transcreva o texto da imagem. {instrucao_livro}
    2. Adapte para o aluno (PEI: {aluno.get('ia_sugestao', '')[:800]}).
    3. Hiperfoco ({aluno.get('hiperfoco')}): Conecte levemente.
    4. REGRA: Insira [[IMG_1]] UMA ÚNICA VEZ após o enunciado principal.
    
    SAÍDA: [ANÁLISE PEDAGÓGICA] ... ---DIVISOR--- [ATIVIDADE] ...
    """
    msgs = [{"role": "user", "content": [{"type": "text", "text": prompt}, {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}}]}]
    try:
        resp = client.chat.completions.create(model="gpt-4o-mini", messages=msgs, temperature=0.7 if modo_profundo else 0.4)
        full = resp.choices[0].message.content
        if "---DIVISOR---" in full:
            p = full.split("---DIVISOR---")
            return p[0].replace("[ANÁLISE PEDAGÓGICA]", "").strip(), garantir_tag_imagem(p[1].replace("[ATIVIDADE]", "").strip())
        return "Análise indisponível.", full
    except Exception as e: return str(e), ""

def criar_profissional(api_key, aluno, materia, objeto, qtd_total, tipo_q, qtd_imagens_desejada, modo_profundo=False, feedback_anterior=""):
    """
    Gera questões do zero. 
    Lógica de Imagem: Prioriza Stock (Unsplash). O prompt pede KEYWORDS para facilitar a busca no banco.
    """
    client = OpenAI(api_key=api_key)
    hiperfoco = aluno.get('hiperfoco', 'Geral')
    
    ajuste = f"AJUSTE SOLICITADO: {feedback_anterior}" if feedback_anterior else ""
    instrucao_tipo = ""
    if tipo_q == "Mista":
        instrucao_tipo = "50% Questões Objetivas e 50% Discursivas/Dissertativas."
    else:
        instrucao_tipo = f"Questões do tipo {tipo_q}."

    instrucao_img = ""
    if qtd_imagens_desejada > 0:
        instrucao_img = f"""
        INSTRUÇÃO VISUAL (PRIORIDADE BANCO DE IMAGENS):
        Você deve incluir EXATAMENTE {qtd_imagens_desejada} imagens distribuídas entre as questões.
        Para pedir uma imagem, use a tag: [[GEN_IMG: termo_simples_em_ingles]].
        IMPORTANTE: O termo dentro da tag deve ser UMA ou DUAS palavras em inglês (ex: "Apple", "Dog running") para facilitar a busca no banco de imagens.
        REGRA DE POSICIONAMENTO: A imagem deve vir IMEDIATAMENTE APÓS O ENUNCIADO e ANTES das alternativas.
        REGRA: NÃO REPITA IMAGENS. Cada [[GEN_IMG]] deve ter um termo diferente.
        """
    else:
        instrucao_img = "Não inclua imagens."

    prompt = f"""
    Atue como professor elaborador. {ajuste}
    Crie prova de {materia} ({objeto}). QTD: {qtd_total}.
    TIPO DE PROVA: {instrucao_tipo}
    
    DIRETRIZES: 
    1. Contexto Real. 
    2. Hiperfoco ({hiperfoco}) em 30%.
    3. Distratores Inteligentes.
    4. {instrucao_img}
    
    SAÍDA: [ANÁLISE PEDAGÓGICA] ... ---DIVISOR--- [ATIVIDADE] ...
    """
    try:
        resp = client.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "user", "content": prompt}], temperature=0.8 if modo_profundo else 0.6)
        full = resp.choices[0].message.content
        if "---DIVISOR---" in full:
            p = full.split("---DIVISOR---")
            return p[0].replace("[ANÁLISE PEDAGÓGICA]", "").strip(), p[1].replace("[ATIVIDADE]", "").strip()
        return "Análise indisponível.", full
    except Exception as e: return str(e), ""

def gerar_experiencia_ei_bncc(api_key, aluno, campo_exp, objetivo, feedback_anterior=""):
    client = OpenAI(api_key=api_key)
    hiperfoco = aluno.get('hiperfoco', 'Brincar')
    ajuste_prompt = f"AJUSTE: {feedback_anterior}" if feedback_anterior else ""

    prompt = f"""
    ATUAR COMO: Especialista em Educação Infantil (BNCC) e Inclusão.
    ALUNO: {aluno['nome']} (EI). HIPERFOCO: {hiperfoco}.
    PEI: {aluno.get('ia_sugestao', '')[:600]}
    
    Crie uma EXPERIÊNCIA LÚDICA (Não prova) para o Campo: "{campo_exp}".
    Objetivo: {objetivo}. {ajuste_prompt}
    
    SAÍDA (Markdown):
    ## 🧸 Experiência: [Nome]
    **🎯 Intencionalidade:** ...
    **📦 Materiais:** ...
    **👣 Como Acontece:** ...
    **🎨 Adaptação:** ...
    """
    try:
        resp = client.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "user", "content": prompt}], temperature=0.7)
        return resp.choices[0].message.content
    except Exception as e: return str(e)

# Outros Geradores
def gerar_roteiro_aula(api_key, aluno, assunto, feedback_anterior=""):
    client = OpenAI(api_key=api_key)
    ajuste = f"Ajuste: {feedback_anterior}" if feedback_anterior else ""
    prompt = f"Roteiro de aula/rotina {assunto} para {aluno['nome']}. PEI: {aluno.get('ia_sugestao','')[:500]}. {ajuste}"
    try:
        resp = client.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "user", "content": prompt}], temperature=0.7)
        return resp.choices[0].message.content
    except Exception as e: return str(e)

def gerar_quebra_gelo_profundo(api_key, aluno, assunto, tema_extra=""):
    client = OpenAI(api_key=api_key)
    tema = tema_extra if tema_extra else aluno.get('hiperfoco', 'Geral')
    prompt = f"3 Tópicos profundos conectando {tema} e {assunto} para {aluno['nome']}."
    try:
        resp = client.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "user", "content": prompt}], temperature=0.8)
        return resp.choices[0].message.content
    except Exception as e: return str(e)

def gerar_dinamica_inclusiva(api_key, aluno, assunto, feedback_anterior=""):
    client = OpenAI(api_key=api_key)
    ajuste = f"Refaça considerando: {feedback_anterior}" if feedback_anterior else ""
    prompt = f"Dinâmica de grupo sobre {assunto} inclusiva para {aluno['nome']} (PEI: {aluno.get('ia_sugestao','')[:500]}). {ajuste}"
    try:
        resp = client.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "user", "content": prompt}], temperature=0.7)
        return resp.choices[0].message.content
    except Exception as e: return str(e)

# ==============================================================================
# 5. INTERFACE DO USUÁRIO (FRONT-END)
# ==============================================================================

with st.sidebar:
    if 'OPENAI_API_KEY' in st.secrets: api_key = st.secrets['OPENAI_API_KEY']; st.success("✅ OpenAI OK")
    else: api_key = st.text_input("Chave OpenAI:", type="password")
    
    st.markdown("---")
    if 'UNSPLASH_ACCESS_KEY' in st.secrets: unsplash_key = st.secrets['UNSPLASH_ACCESS_KEY']; st.success("✅ Unsplash OK")
    else: unsplash_key = st.text_input("Chave Unsplash (Opcional):", type="password")
    
    st.markdown("---")
    if st.button("🧹 Limpar Tudo e Reiniciar", type="secondary"):
        for key in list(st.session_state.keys()):
            if key not in ['banco_estudantes', 'OPENAI_API_KEY', 'UNSPLASH_ACCESS_KEY', 'autenticado']: del st.session_state[key]
        st.rerun()

# Header Hub
img_hub_html = get_img_tag("hub.png", "220") 
st.markdown(f"""
    <div class="header-hub">
        <div style="flex-shrink: 0;">{img_hub_html}</div>
        <div style="flex-grow: 1; text-align: center;">
            <p style="margin:0; color:#2C5282; font-size: 1.3rem; font-weight: 700;">Adaptação de Materiais & Criação</p>
        </div>
    </div>
""", unsafe_allow_html=True)

if not st.session_state.banco_estudantes:
    st.warning("⚠️ Nenhum aluno encontrado.")
    st.stop()

lista = [a['nome'] for a in st.session_state.banco_estudantes]
nome_aluno = st.selectbox("📂 Selecione o Estudante:", lista)
aluno = next(a for a in st.session_state.banco_estudantes if a['nome'] == nome_aluno)

# Dados do Aluno Header
serie_aluno = aluno.get('serie', '').lower()
is_ei = "infantil" in serie_aluno or "creche" in serie_aluno or "pré" in serie_aluno

st.markdown(f"""
    <div class="student-header">
        <div class="student-info-item"><div class="student-label">Nome</div><div class="student-value">{aluno.get('nome')}</div></div>
        <div class="student-info-item"><div class="student-label">Série</div><div class="student-value">{aluno.get('serie', '-')}</div></div>
        <div class="student-info-item"><div class="student-label">Hiperfoco</div><div class="student-value">{aluno.get('hiperfoco', '-')}</div></div>
    </div>
""", unsafe_allow_html=True)

# Inicialização de Estado
if 'res_scene_url' not in st.session_state: st.session_state.res_scene_url = None
if 'valid_scene' not in st.session_state: st.session_state.valid_scene = False
if 'res_caa_url' not in st.session_state: st.session_state.res_caa_url = None
if 'valid_caa' not in st.session_state: st.session_state.valid_caa = False

# ==============================================================================
# 6. LOGICA DE ABAS (EI vs PADRÃO)
# ==============================================================================

if is_ei:
    # --- MODO EDUCAÇÃO INFANTIL ---
    st.info("🧸 **Modo Educação Infantil:** Foco em Experiências e Brincar.")
    tabs = st.tabs(["🧸 Criar Experiência (BNCC)", "🎨 Estúdio Visual & CAA", "📝 Rotina & AVD", "🤝 Inclusão no Brincar"])
    
    # Aba 1: BNCC
    with tabs[0]:
        st.markdown("<div class='pedagogia-box'>Pedagogia do Brincar (BNCC): Crie experiências, não provas.</div>", unsafe_allow_html=True)
        col_ei1, col_ei2 = st.columns(2)
        campo_exp = col_ei1.selectbox("Campo de Experiência", ["O eu, o outro e o nós", "Corpo, gestos e movimentos", "Traços, sons, cores e formas", "Escuta, fala, pensamento e imaginação", "Espaços, tempos, quantidades, relações e transformações"])
        obj_aprendizagem = col_ei2.text_input("Objetivo:", placeholder="Ex: Compartilhar brinquedos")
        
        if 'res_ei_exp' not in st.session_state: st.session_state.res_ei_exp = None
        if 'valid_ei_exp' not in st.session_state: st.session_state.valid_ei_exp = False

        if st.button("✨ GERAR EXPERIÊNCIA", type="primary"):
            with st.spinner("Criando vivência..."):
                st.session_state.res_ei_exp = gerar_experiencia_ei_bncc(api_key, aluno, campo_exp, obj_aprendizagem)
                st.session_state.valid_ei_exp = False
        
        if st.session_state.res_ei_exp:
            st.markdown(st.session_state.res_ei_exp)
            if st.session_state.valid_ei_exp:
                st.markdown("<div class='validado-box'>✅ APROVADO</div>", unsafe_allow_html=True)
            else:
                c_v, c_r = st.columns([1,2])
                if c_v.button("✅ Validar Experiência"): st.session_state.valid_ei_exp = True; st.rerun()
                with c_r.expander("🔄 Refazer/Ajustar"):
                    fb_ei = st.text_input("Instrução:", key="fb_ei_input")
                    if st.button("Refazer"):
                         with st.spinner("Refazendo..."):
                            st.session_state.res_ei_exp = gerar_experiencia_ei_bncc(api_key, aluno, campo_exp, obj_aprendizagem, feedback_anterior=fb_ei)
                            st.rerun()

    # Aba 2: Estúdio Visual (EI)
    with tabs[1]:
        st.markdown("<div class='pedagogia-box'>Apoio Visual: Use Cenas para comportamento e Pictogramas para comunicação.</div>", unsafe_allow_html=True)
        col_scene, col_caa = st.columns(2)
        
        with col_scene:
            st.markdown("#### 🖼️ Cena (IA Gerada)")
            desc_m = st.text_area("Descreva:", height=100, key="vdm_ei")
            if st.button("🎨 Gerar Cena", key="btn_cena_ei"):
                with st.spinner("Desenhando..."):
                    # MODO: IA STRICT
                    st.session_state.res_scene_url = obter_recurso_visual(api_key, f"{desc_m}. Context: Child education", unsplash_key, modo="ia_strict")
                    st.session_state.valid_scene = False
            
            if st.session_state.res_scene_url: 
                st.image(st.session_state.res_scene_url)
                if st.session_state.valid_scene:
                    st.success("✅ Validado")
                else:
                    cv, cr = st.columns([1,2])
                    if cv.button("✅ Validar", key="val_s_ei"): st.session_state.valid_scene = True; st.rerun()
                    with cr.expander("🔄 Refazer"):
                        fb_s = st.text_input("Ajuste:", key="fb_s_ei")
                        if st.button("Refazer Cena"):
                            with st.spinner("Redesenhando..."):
                                st.session_state.res_scene_url = obter_recurso_visual(api_key, f"{desc_m}. Context: Child education", unsplash_key, modo="ia_strict", feedback_anterior=fb_s)
                                st.rerun()

        with col_caa:
            st.markdown("#### 🗣️ Símbolo CAA")
            palavra = st.text_input("Conceito:", key="caa_ei")
            if st.button("🧩 Gerar Pictograma", key="btn_caa_ei"):
                with st.spinner("Criando símbolo..."):
                    st.session_state.res_caa_url = gerar_pictograma_caa(api_key, palavra)
                    st.session_state.valid_caa = False

            if st.session_state.res_caa_url: 
                st.image(st.session_state.res_caa_url, width=300)
                if st.session_state.valid_caa:
                    st.success("✅ Validado")
                else:
                    cv2, cr2 = st.columns([1,2])
                    if cv2.button("✅ Validar", key="val_c_ei"): st.session_state.valid_caa = True; st.rerun()
                    with cr2.expander("🔄 Refazer"):
                        fb_c = st.text_input("Ajuste:", key="fb_c_ei")
                        if st.button("Refazer Picto"):
                            with st.spinner("Recriando..."):
                                st.session_state.res_caa_url = gerar_pictograma_caa(api_key, palavra, feedback_anterior=fb_c)
                                st.rerun()

    # Aba 3: Rotina
    with tabs[2]:
        rotina = st.text_area("Descreva a Rotina:", height=150)
        if st.button("📝 ADAPTAR ROTINA"):
            st.markdown(gerar_roteiro_aula(api_key, aluno, f"Analise esta rotina: {rotina}"))

    # Aba 4: Dinâmica
    with tabs[3]:
        tema_d = st.text_input("Tema:")
        if st.button("🤝 GERAR DINÂMICA"):
            st.markdown(gerar_dinamica_inclusiva(api_key, aluno, tema_d))

else:
    # --- MODO PADRÃO (ENSINO FUNDAMENTAL/MÉDIO) ---
    tabs = st.tabs(["📄 Adaptar Prova", "✂️ Adaptar Atividade", "✨ Criar do Zero", "🎨 Estúdio Visual & CAA", "📝 Roteiro", "🗣️ Conversa", "🤝 Dinâmica"])

    # 1. ADAPTAR PROVA
    with tabs[0]:
        st.markdown("<div class='pedagogia-box'>Adaptação Curricular (DUA): Simplificação e apoio visual.</div>", unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        materia_d = c1.selectbox("Matéria", ["Matemática", "Português", "Ciências", "História", "Geografia", "Artes", "Inglês"], key="dm")
        tema_d = c2.text_input("Tema", key="dt")
        tipo_d = c3.selectbox("Tipo", ["Prova", "Tarefa"], key="dtp")
        arquivo_d = st.file_uploader("Upload DOCX", type=["docx"], key="fd")
        
        if 'docx_imgs' not in st.session_state: st.session_state.docx_imgs = []
        if 'docx_txt' not in st.session_state: st.session_state.docx_txt = None

        if arquivo_d and arquivo_d.file_id != st.session_state.get('last_d'):
            st.session_state.last_d = arquivo_d.file_id
            txt, imgs = extrair_dados_docx(arquivo_d)
            st.session_state.docx_txt = txt; st.session_state.docx_imgs = imgs
            st.success(f"{len(imgs)} imagens extraídas.")

        qs_d = []
        if st.session_state.docx_imgs:
            st.write("### Mapeamento de Imagens")
            cols = st.columns(3)
            for i, img in enumerate(st.session_state.docx_imgs):
                with cols[i % 3]:
                    st.image(img, width=80)
                    q = st.number_input(f"Questão referente:", 0, 50, key=f"dq_{i}")
                    if q > 0: qs_d.append(int(q))

        if st.button("🚀 ADAPTAR PROVA", type="primary"):
            if not st.session_state.docx_txt: st.warning("Envie arquivo."); st.stop()
            with st.spinner("Adaptando..."):
                rac, txt = adaptar_conteudo_docx(api_key, aluno, st.session_state.docx_txt, materia_d, tema_d, tipo_d, True, qs_d)
                st.session_state['res_docx'] = {'rac': rac, 'txt': txt, 'valid': False}
                st.rerun()

        if 'res_docx' in st.session_state:
            res = st.session_state['res_docx']
            if res.get('valid'):
                st.markdown("<div class='validado-box'>✅ VALIDADO!</div>", unsafe_allow_html=True)
            else:
                col_v, col_r = st.columns([1, 2])
                if col_v.button("✅ Validar", key="val_d"): st.session_state['res_docx']['valid'] = True; st.rerun()
                with col_r.expander("🔄 Refazer/Ajustar"):
                    fb_d = st.text_input("O que ajustar?", key="fb_d")
                    if st.button("Refazer"):
                        with st.spinner("Refazendo..."):
                            rac, txt = adaptar_conteudo_docx(api_key, aluno, st.session_state.docx_txt, materia_d, tema_d, tipo_d, True, qs_d, feedback_anterior=fb_d)
                            st.session_state['res_docx'] = {'rac': rac, 'txt': txt, 'valid': False}
                            st.rerun()

            st.markdown(f"<div class='analise-box'>{res['rac']}</div>", unsafe_allow_html=True)
            st.download_button("📥 BAIXAR DOCX", construir_docx_final(res['txt'], aluno, materia_d, {}, None, tipo_d), "Prova_Adaptada.docx")

    # 2. ADAPTAR ATIVIDADE (OCR)
    with tabs[1]:
        st.markdown("<div class='pedagogia-box'>OCR & Adaptação: Transforme fotos de livros em atividades acessíveis.</div>", unsafe_allow_html=True)
        arquivo_i = st.file_uploader("Foto da Atividade", type=["png","jpg"], key="fi")
        if arquivo_i:
            img_pil = Image.open(arquivo_i)
            img_pil.thumbnail((800, 800))
            cropped = st_cropper(img_pil, box_color='#FF0000', key="crop_i")
            if st.button("🚀 ADAPTAR RECORTE", type="primary"):
                buf = BytesIO(); cropped.save(buf, format="JPEG"); img_bytes = buf.getvalue()
                rac, txt = adaptar_conteudo_imagem(api_key, aluno, img_bytes, "Geral", "Geral", "Atividade", False)
                st.session_state['res_img'] = {'rac': rac, 'txt': txt, 'img': img_bytes, 'valid': False}
                st.rerun()

        if 'res_img' in st.session_state:
            res = st.session_state['res_img']
            if res.get('valid'):
                st.markdown("<div class='validado-box'>✅ VALIDADO!</div>", unsafe_allow_html=True)
            else:
                col_v, col_r = st.columns([1, 2])
                if col_v.button("✅ Validar", key="val_i"): st.session_state['res_img']['valid'] = True; st.rerun()
                with col_r.expander("🔄 Refazer/Ajustar"):
                    fb_i = st.text_input("Instrução de ajuste:", key="fb_i")
                    if st.button("Refazer Recorte"):
                        with st.spinner("Refazendo..."):
                            img_bytes = res['img']
                            rac, txt = adaptar_conteudo_imagem(api_key, aluno, img_bytes, "Geral", "Geral", "Atividade", False, feedback_anterior=fb_i)
                            st.session_state['res_img'] = {'rac': rac, 'txt': txt, 'img': img_bytes, 'valid': False}
                            st.rerun()

            st.markdown(f"<div class='analise-box'>{res['rac']}</div>", unsafe_allow_html=True)
            st.image(res['img'], width=300)
            st.download_button("📥 BAIXAR DOCX", construir_docx_final(res['txt'], aluno, "Geral", {1: res['img']}, None, "Ativ"), "Atividade.docx")

    # 3. CRIAR DO ZERO (COM MISTA E VALIDAÇÃO)
    with tabs[2]:
        st.markdown("<div class='pedagogia-box'>Criação com DUA: Prioridade para imagens reais (Banco de Imagens).</div>", unsafe_allow_html=True)
        cc1, cc2 = st.columns(2)
        mat_c = cc1.selectbox("Componente", ["Matemática", "Português", "Ciências", "História", "Geografia"], key="cm")
        obj_c = cc2.text_input("Assunto", key="co")
        
        cc3, cc4 = st.columns(2)
        qtd_c = cc3.slider("Quantidade de Questões", 1, 10, 5, key="cq")
        # ADICIONADA OPÇÃO MISTA
        tipo_quest = cc4.selectbox("Tipo", ["Objetiva", "Discursiva", "Mista"], key="ctq")
        
        st.write("---")
        st.write("🖼️ **Configuração Visual**")
        qtd_imgs_selecionada = st.slider(
            "Quantas imagens deseja incluir?", 
            min_value=0, 
            max_value=qtd_c, 
            value=min(3, qtd_c), 
            help="Prioridade: Banco de Imagens. Caso não encontre, gera com IA."
        )

        if st.button("✨ CRIAR ATIVIDADE", type="primary", key="btn_c"):
            with st.spinner("Elaborando questões e buscando imagens..."):
                # 1. Gera Texto
                rac, txt = criar_profissional(api_key, aluno, mat_c, obj_c, qtd_c, tipo_quest, qtd_imgs_selecionada)
                
                # 2. Processa Imagens (Modo Stock First)
                novo_map = {}; count = 0
                tags = re.findall(r'\[\[GEN_IMG: (.*?)\]\]', txt)
                
                for p in tags:
                    count += 1
                    url = obter_recurso_visual(api_key, p, unsplash_key, modo="stock_first")
                    if url:
                        io = baixar_imagem_url(url)
                        if io: novo_map[count] = io.getvalue()
                
                txt_fin = txt
                for i in range(1, count + 1): 
                    txt_fin = re.sub(r'\[\[GEN_IMG: .*?\]\]', f"[[IMG_G{i}]]", txt_fin, count=1)
                
                st.session_state['res_create'] = {'rac': rac, 'txt': txt_fin, 'map': novo_map, 'valid': False}
                st.rerun()

        if 'res_create' in st.session_state:
            res = st.session_state['res_create']
            if res.get('valid'):
                st.markdown("<div class='validado-box'>✅ VALIDADO!</div>", unsafe_allow_html=True)
            else:
                col_v, col_r = st.columns([1, 2])
                if col_v.button("✅ Validar", key="val_c"): st.session_state['res_create']['valid'] = True; st.rerun()
                with col_r.expander("🔄 Refazer/Ajustar"):
                    fb_c = st.text_input("Instrução:", key="fb_c")
                    if st.button("Refazer Questões"):
                         with st.spinner("Refazendo..."):
                            rac, txt = criar_profissional(api_key, aluno, mat_c, obj_c, qtd_c, tipo_quest, qtd_imgs_selecionada, feedback_anterior=fb_c)
                            # (Reutiliza imagens se não mudar o prompt visual, mas aqui simplificamos regerando para garantir coerência)
                            # Para manter simples: regera imagens também para alinhar com novo texto
                            novo_map = {}; count = 0
                            tags = re.findall(r'\[\[GEN_IMG: (.*?)\]\]', txt)
                            for p in tags:
                                count += 1
                                url = obter_recurso_visual(api_key, p, unsplash_key, modo="stock_first")
                                if url:
                                    io = baixar_imagem_url(url)
                                    if io: novo_map[count] = io.getvalue()
                            txt_fin = txt
                            for i in range(1, count + 1): 
                                txt_fin = re.sub(r'\[\[GEN_IMG: .*?\]\]', f"[[IMG_G{i}]]", txt_fin, count=1)
                            
                            st.session_state['res_create'] = {'rac': rac, 'txt': txt_fin, 'map': novo_map, 'valid': False}
                            st.rerun()

            st.markdown(f"<div class='analise-box'>{res['rac']}</div>", unsafe_allow_html=True)
            
            with st.container(border=True):
                partes = re.split(r'(\[\[IMG_G\d+\]\])', res['txt'])
                for p in partes:
                    tag = re.search(r'\[\[IMG_G(\d+)\]\]', p)
                    if tag:
                        i = int(tag.group(1))
                        im = res['map'].get(i)
                        if im: st.image(im, width=300)
                    elif p.strip(): st.markdown(p.strip())
            
            doc_final = construir_docx_final(res['txt'], aluno, mat_c, res['map'], None, "Criada")
            st.download_button("📥 BAIXAR DOCX", doc_final, "Atividade_Criada.docx", "primary")

    # 4. ESTÚDIO VISUAL (IA ESTRITA)
    with tabs[3]:
        st.markdown("<div class='pedagogia-box'>Recursos Visuais: Geração exclusiva via IA (DALL-E 3) para personalização total.</div>", unsafe_allow_html=True)
        col_scene, col_caa = st.columns(2)
        
        with col_scene:
            st.markdown("#### 🖼️ Ilustração (IA)")
            desc_m = st.text_area("Descreva:", height=100, key="vdm_pad")
            if st.button("🎨 Gerar", key="btn_sc_pad"):
                with st.spinner("Desenhando..."):
                    st.session_state.res_scene_url = obter_recurso_visual(api_key, f"{desc_m}. Context: Education", unsplash_key, modo="ia_strict")
                    st.session_state.valid_scene = False
            
            if st.session_state.res_scene_url: 
                st.image(st.session_state.res_scene_url)
                if st.session_state.valid_scene:
                    st.success("✅ Validado")
                else:
                    cv, cr = st.columns([1,2])
                    if cv.button("✅ Validar", key="val_s_pd"): st.session_state.valid_scene = True; st.rerun()
                    with cr.expander("🔄 Refazer"):
                        fb_s = st.text_input("Ajuste:", key="fb_s_pd")
                        if st.button("Refazer Imagem"):
                             with st.spinner("Redesenhando..."):
                                st.session_state.res_scene_url = obter_recurso_visual(api_key, f"{desc_m}. Context: Education", unsplash_key, modo="ia_strict", feedback_anterior=fb_s)
                                st.rerun()
        
        with col_caa:
            st.markdown("#### 🗣️ Símbolo CAA")
            conceito = st.text_input("Conceito:", key="caa_pad")
            if st.button("🧩 Gerar", key="btn_caa_pad"):
                with st.spinner("Criando..."):
                    st.session_state.res_caa_url = gerar_pictograma_caa(api_key, conceito)
                    st.session_state.valid_caa = False

            if st.session_state.res_caa_url: 
                st.image(st.session_state.res_caa_url)
                if st.session_state.valid_caa:
                    st.success("✅ Validado")
                else:
                    cv, cr = st.columns([1,2])
                    if cv.button("✅ Validar", key="val_c_pd"): st.session_state.valid_caa = True; st.rerun()
                    with cr.expander("🔄 Refazer"):
                        fb_c = st.text_input("Ajuste:", key="fb_c_pd")
                        if st.button("Refazer Picto"):
                             with st.spinner("Recriando..."):
                                st.session_state.res_caa_url = gerar_pictograma_caa(api_key, conceito, feedback_anterior=fb_c)
                                st.rerun()

    # Abas Extras
    with tabs[4]:
        ass = st.text_input("Assunto:", key="rr")
        if st.button("📝 ROTEIRO"): st.markdown(gerar_roteiro_aula(api_key, aluno, ass))
    with tabs[5]:
        if st.button("🗣️ CONVERSA"): st.markdown(gerar_quebra_gelo_profundo(api_key, aluno, "Geral"))
    with tabs[6]:
        if st.button("🤝 DINÂMICA"): st.markdown(gerar_dinamica_inclusiva(api_key, aluno, "Inclusão"))
