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
# 1. CONFIGURAÇÃO E SEGURANÇA
# ==============================================================================
st.set_page_config(
    page_title="Hub de Inclusão | Omnisfera", 
    page_icon="🚀", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==============================================================================
# 2. BLOCO VISUAL (DESIGN SYSTEM PREMIUM - AZUL SÓBRIO)
# ==============================================================================
# 1. Detecção de Ambiente
try: IS_TEST_ENV = st.secrets.get("ENV") == "TESTE"
except: IS_TEST_ENV = False

# 2. Logo Base64
def get_logo_base64():
    caminhos = ["omni_icone.png", "logo.png", "iconeaba.png"]
    for c in caminhos:
        if os.path.exists(c):
            with open(c, "rb") as f: return f"data:image/png;base64,{base64.b64encode(f.read()).decode()}"
    return "https://cdn-icons-png.flaticon.com/512/1183/1183672.png"

src_logo_giratoria = get_logo_base64()

# 3. Cores Dinâmicas
if IS_TEST_ENV:
    card_bg, card_border = "rgba(255, 220, 50, 0.95)", "rgba(200, 160, 0, 0.5)"
else:
    card_bg, card_border = "rgba(255, 255, 255, 0.85)", "rgba(255, 255, 255, 0.6)"

# 4. Renderização CSS Global
st.markdown(f"""
    <link href="https://cdn.jsdelivr.net/npm/remixicon@4.1.0/fonts/remixicon.css" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800&display=swap" rel="stylesheet">
    
    <style>
    /* VARIÁVEIS GLOBAIS */
    :root {{ --brand-blue: #0F52BA; --brand-hover: #0A3D8F; }}
    
    /* 1. Fontes e Cores Base */
    html, body, [class*="css"] {{ font-family: 'Nunito', sans-serif; color: #2D3748; background-color: #F7FAFC; }}
    .block-container {{ padding-top: 1.5rem !important; padding-bottom: 5rem !important; }}

    /* 2. Navegação em Abas "Pílula" */
    div[data-baseweb="tab-border"], div[data-baseweb="tab-highlight"] {{ display: none !important; }}
    
    .stTabs [data-baseweb="tab-list"] {{ 
        gap: 8px; display: flex; flex-wrap: nowrap; overflow-x: auto; 
        white-space: nowrap; padding: 10px 5px; scrollbar-width: none; 
    }}
    
    .stTabs [data-baseweb="tab"] {{ 
        height: 38px; border-radius: 20px !important; background-color: #FFFFFF; 
        border: 1px solid #E2E8F0; color: #718096; font-weight: 700; font-size: 0.8rem; 
        padding: 0 20px; transition: all 0.2s ease; box-shadow: 0 1px 2px rgba(0,0,0,0.03); 
        flex-shrink: 0; text-transform: uppercase; letter-spacing: 0.5px; 
    }}
    
    .stTabs [data-baseweb="tab"]:hover {{ border-color: #CBD5E0; color: #4A5568; background-color: #EDF2F7; }}

    .stTabs [aria-selected="true"] {{ 
        background-color: transparent !important; color: var(--brand-blue) !important; 
        border: 1px solid var(--brand-blue) !important; font-weight: 800; 
        box-shadow: 0 0 12px rgba(15, 82, 186, 0.3), inset 0 0 5px rgba(15, 82, 186, 0.1) !important; 
    }}

    /* 3. Header Unificado */
    .header-unified {{ 
        background-color: white; padding: 35px 40px; border-radius: 16px; 
        border: 1px solid #E2E8F0; box-shadow: 0 2px 10px rgba(0,0,0,0.02); 
        margin-bottom: 20px; display: flex; align-items: center; gap: 20px; 
    }}
    .header-subtitle {{ 
        font-size: 1.2rem; color: #718096; font-weight: 600; 
        border-left: 2px solid #E2E8F0; padding-left: 20px; line-height: 1.2; 
    }}

    /* 4. Inputs e Botões */
    .stTextInput input, .stTextArea textarea, .stSelectbox div[data-baseweb="select"], .stNumberInput input {{ 
        border-radius: 8px !important; border-color: #E2E8F0 !important; 
    }}
    div[data-testid="column"] .stButton button {{ 
        border-radius: 8px !important; font-weight: 800 !important; text-transform: uppercase; 
        height: 50px !important; background-color: var(--brand-blue) !important; color: white !important; 
        border: none !important; letter-spacing: 0.5px; 
    }}
    div[data-testid="column"] .stButton button:hover {{ background-color: var(--brand-hover) !important; }}

    /* 5. Card Aluno */
    .student-header {{ 
        background-color: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 16px; 
        padding: 20px 30px; margin-bottom: 20px; display: flex; justify-content: space-between; 
        align-items: center; box-shadow: 0 2px 4px rgba(0,0,0,0.02); 
    }}
    
    /* 6. Boxes de Pedagogia */
    .pedagogia-box {{ 
        background-color: #F8FAFC; border-left: 4px solid var(--brand-blue); 
        padding: 20px; border-radius: 0 12px 12px 0; margin-bottom: 25px; 
        font-size: 0.95rem; color: #4A5568; 
    }}
    .pedagogia-title {{ color: var(--brand-blue); font-weight: 800; display: flex; align-items: center; gap: 10px; margin-bottom: 8px; font-size: 1rem; }}
    .analise-box {{ background-color: #F0FFF4; border: 1px solid #C6F6D5; border-radius: 12px; padding: 20px; margin-bottom: 20px; color: #22543D; }}

    /* Badge Flutuante */
    .omni-badge {{
        position: fixed; top: 15px; right: 15px; background: {card_bg}; border: 1px solid {card_border};
        backdrop-filter: blur(8px); padding: 4px 30px; min-width: 260px; justify-content: center;
        border-radius: 20px; box-shadow: 0 4px 15px rgba(0,0,0,0.08); z-index: 999990; 
        display: flex; align-items: center; gap: 10px; pointer-events: none;
    }}
    .omni-text {{ font-family: 'Nunito'; font-weight: 800; font-size: 0.9rem; color: #2D3748; letter-spacing: 1px; }}
    .omni-logo-spin {{ height: 26px; width: 26px; animation: spin-slow 10s linear infinite; }}
    @keyframes spin-slow {{ from {{ transform: rotate(0deg); }} to {{ transform: rotate(360deg); }} }}
    </style>
    
    <div class="omni-badge">
        <img src="{src_logo_giratoria}" class="omni-logo-spin">
        <span class="omni-text">OMNISFERA</span>
    </div>
""", unsafe_allow_html=True)

def verificar_acesso():
    if "autenticado" not in st.session_state or not st.session_state["autenticado"]:
        st.error("🔒 Acesso Negado. Por favor, faça login na Página Inicial.")
        st.stop()
    st.markdown("""<style>footer {visibility: hidden !important;} [data-testid="stHeader"] {visibility: visible !important; background-color: transparent !important;} .block-container {padding-top: 2rem !important;}</style>""", unsafe_allow_html=True)

verificar_acesso()

# --- BARRA LATERAL ---
with st.sidebar:
    try: st.image("ominisfera.png", width=150)
    except: st.write("🌐 OMNISFERA")
    st.markdown("---")
    if st.button("🏠 Voltar para Home", use_container_width=True): st.switch_page("Home.py")
    st.markdown("---")

# ==============================================================================
# 2. LÓGICA DO HUB (PRESERVADA INTEGRALMENTE)
# ==============================================================================

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

# --- HEADER UNIFICADO (CLEAN) ---
def get_img_tag_custom(file_path, width):
    if os.path.exists(file_path):
        with open(file_path, "rb") as f:
            data = base64.b64encode(f.read()).decode("utf-8")
        return f'<img src="data:image/png;base64,{data}" width="{width}" style="object-fit: contain;">'
    return ""

img_hub = get_img_tag_custom("hub.png", "220")

st.markdown(f"""
<div class="header-unified">
    <div style="flex-shrink: 0;">
        {img_hub}
    </div>
    <div class="header-subtitle">
        Adaptação de Materiais & Criação
    </div>
</div>
""", unsafe_allow_html=True)

if not st.session_state.banco_estudantes:
    st.warning("⚠️ Nenhum aluno encontrado. Cadastre no módulo PEI primeiro.")
    st.stop()

# --- SELEÇÃO DE ALUNO ---
lista_alunos = [a['nome'] for a in st.session_state.banco_estudantes]
col_sel, col_info = st.columns([1, 2])
with col_sel:
    nome_aluno = st.selectbox("📂 Selecione o Estudante:", lista_alunos)

aluno = next(a for a in st.session_state.banco_estudantes if a['nome'] == nome_aluno)

serie_aluno = aluno.get('serie', '').lower()
is_ei = "infantil" in serie_aluno or "creche" in serie_aluno or "pré" in serie_aluno

# --- HEADER DO ALUNO (ESTILO CARD) ---
st.markdown(f"""
    <div class="student-header">
        <div><div style="font-size: 0.8rem; color: #718096; font-weight: 800; text-transform: uppercase; letter-spacing: 1px;">Nome</div><div style="font-size: 1.2rem; color: #2D3748; font-weight: 800;">{aluno.get('nome')}</div></div>
        <div><div style="font-size: 0.8rem; color: #718096; font-weight: 800; text-transform: uppercase; letter-spacing: 1px;">Série</div><div style="font-size: 1.2rem; color: #2D3748; font-weight: 800;">{aluno.get('serie', '-')}</div></div>
        <div><div style="font-size: 0.8rem; color: #718096; font-weight: 800; text-transform: uppercase; letter-spacing: 1px;">Hiperfoco</div><div style="font-size: 1.2rem; color: #0F52BA; font-weight: 800;">{aluno.get('hiperfoco', '-')}</div></div>
    </div>
""", unsafe_allow_html=True)

with st.expander("📄 Ver Resumo do PEI (Base para Adaptação)", expanded=False):
    st.info(aluno.get('ia_sugestao', 'Nenhum dado de PEI processado ainda.'))

# --- INTERFACE CHAVES ---
if 'OPENAI_API_KEY' in st.secrets: api_key = st.secrets['OPENAI_API_KEY']
else: api_key = st.sidebar.text_input("Chave OpenAI:", type="password")
if 'UNSPLASH_ACCESS_KEY' in st.secrets: unsplash_key = st.secrets['UNSPLASH_ACCESS_KEY']
else: unsplash_key = st.sidebar.text_input("Chave Unsplash (Opcional):", type="password")

if st.sidebar.button("🧹 Limpar Tudo e Reiniciar"):
    for key in list(st.session_state.keys()):
        if key not in ['banco_estudantes', 'OPENAI_API_KEY', 'UNSPLASH_ACCESS_KEY', 'autenticado']: del st.session_state[key]
    st.rerun()

# === FUNÇÕES DO HUB (MANTIDAS) ===
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
        out = BytesIO(); img.save(out, format="JPEG", quality=90); return out.getvalue()
    except: return None

def baixar_imagem_url(url):
    try:
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200: return BytesIO(resp.content)
    except: pass
    return None

def buscar_imagem_unsplash(query, access_key):
    if not access_key: return None
    url = f"https://api.unsplash.com/search/photos?query={query}&per_page=1&client_id={access_key}&lang=pt"
    try:
        resp = requests.get(url, timeout=5)
        data = resp.json()
        if data.get('results'): return data['results'][0]['urls']['regular']
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
        doc.add_paragraph("_"*50); doc.add_heading('Atividades', level=2)

    linhas = texto_ia.split('\n')
    for linha in linhas:
        tag_match = re.search(r'\[\[(IMG|GEN_IMG).*?(\d+)\]\]', linha, re.IGNORECASE)
        if tag_match:
            partes = re.split(r'(\[\[(?:IMG|GEN_IMG).*?\d+\]\])', linha, flags=re.IGNORECASE)
            for parte in partes:
                sub_match = re.search(r'(\d+)', parte)
                if ("IMG" in parte.upper() or "GEN_IMG" in parte.upper()) and sub_match:
                    num = int(sub_match.group(1))
                    img_bytes = mapa_imgs.get(num)
                    if not img_bytes and len(mapa_imgs) == 1: img_bytes = list(mapa_imgs.values())[0]
                    if img_bytes:
                        try:
                            p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                            r = p.add_run(); r.add_picture(BytesIO(img_bytes), width=Inches(3.5))
                        except: pass
                elif parte.strip(): doc.add_paragraph(parte.strip())
        else:
            if linha.strip(): doc.add_paragraph(linha.strip())
    buffer = BytesIO(); doc.save(buffer); buffer.seek(0)
    return buffer

# --- IA FUNCTIONS ---
def gerar_imagem_inteligente(api_key, prompt, unsplash_key=None, feedback_anterior="", prioridade="IA"):
    client = OpenAI(api_key=api_key)
    prompt_final = f"{prompt}. Adjustment requested: {feedback_anterior}" if feedback_anterior else prompt

    if prioridade == "BANCO" and unsplash_key:
        termo = prompt.split('.')[0] if '.' in prompt else prompt
        url_banco = buscar_imagem_unsplash(termo, unsplash_key)
        if url_banco: return url_banco

    try:
        didactic_prompt = f"Educational textbook illustration, clean flat vector style, white background. CRITICAL RULE: STRICTLY NO TEXT, NO TYPOGRAPHY. Just visual: {prompt_final}"
        resp = client.images.generate(model="dall-e-3", prompt=didactic_prompt, size="1024x1024", quality="standard", n=1)
        return resp.data[0].url
    except:
        if prioridade == "IA" and unsplash_key:
            termo = prompt.split('.')[0] if '.' in prompt else prompt
            return buscar_imagem_unsplash(termo, unsplash_key)
        return None

def gerar_pictograma_caa(api_key, conceito, feedback_anterior=""):
    client = OpenAI(api_key=api_key)
    ajuste = f" CORREÇÃO PEDIDA: {feedback_anterior}" if feedback_anterior else ""
    prompt_caa = f"""
    Create a COMMUNICATION SYMBOL (AAC/PECS) for: '{conceito}'. {ajuste}
    STYLE: Flat vector icon (ARASAAC style), Solid WHITE background, Thick BLACK outlines, High contrast. CRITICAL: MUTE IMAGE. NO TEXT.
    """
    try:
        resp = client.images.generate(model="dall-e-3", prompt=prompt_caa, size="1024x1024", quality="standard", n=1)
        return resp.data[0].url
    except Exception as e: return None

def adaptar_conteudo_docx(api_key, aluno, texto, materia, tema, tipo_atv, remover_resp, questoes_mapeadas, modo_profundo=False):
    client = OpenAI(api_key=api_key)
    lista_q = ", ".join([str(n) for n in questoes_mapeadas])
    style = "Seja didático." if modo_profundo else "Seja objetivo."
    prompt = f"""
    ESPECIALISTA EM DUA. {style}
    PERFIL: {aluno.get('ia_sugestao', '')[:1000]}
    REGRA IMAGEM: O professor indicou imagens nas questões: {lista_q}.
    ESTRUTURA OBRIGATÓRIA: 1. Enunciado -> 2. [[IMG_número]] -> 3. Alternativas.
    SAÍDA: [ANÁLISE PEDAGÓGICA]...---DIVISOR---[ATIVIDADE]...
    CONTEXTO: {materia} | {tema}. TEXTO: {texto}
    """
    try:
        resp = client.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "user", "content": prompt}], temperature=0.7 if modo_profundo else 0.4)
        full_text = resp.choices[0].message.content
        if "---DIVISOR---" in full_text:
            parts = full_text.split("---DIVISOR---")
            return parts[0].replace("[ANÁLISE PEDAGÓGICA]", "").strip(), parts[1].replace("[ATIVIDADE]", "").strip()
        return "Análise indisponível.", full_text
    except Exception as e: return str(e), ""

def adaptar_conteudo_imagem(api_key, aluno, imagem_bytes, materia, tema, tipo_atv, livro_professor, modo_profundo=False):
    client = OpenAI(api_key=api_key)
    b64 = base64.b64encode(imagem_bytes).decode('utf-8')
    prompt = f"""
    ATUAR COMO: Especialista em Acessibilidade.
    1. Transcreva e Adapte para (PEI: {aluno.get('ia_sugestao', '')[:800]}).
    2. REGRA DE OURO: Insira a tag [[IMG_1]] UMA ÚNICA VEZ, logo após o enunciado.
    SAÍDA: [ANÁLISE PEDAGÓGICA]...---DIVISOR---[ATIVIDADE]...
    """
    msgs = [{"role": "user", "content": [{"type": "text", "text": prompt}, {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}}]}]
    try:
        resp = client.chat.completions.create(model="gpt-4o-mini", messages=msgs, temperature=0.4)
        full_text = resp.choices[0].message.content
        if "---DIVISOR---" in full_text:
            parts = full_text.split("---DIVISOR---")
            return parts[0].replace("[ANÁLISE PEDAGÓGICA]", "").strip(), garantir_tag_imagem(parts[1].replace("[ATIVIDADE]", "").strip())
        return "Análise indisponível.", full_text
    except Exception as e: return str(e), ""

def criar_profissional(api_key, aluno, materia, objeto, qtd, tipo_q, qtd_imgs, modo_profundo=False):
    client = OpenAI(api_key=api_key)
    hiperfoco = aluno.get('hiperfoco', 'Geral')
    instrucao_img = f"Incluir imagens em {qtd_imgs} questões (use [[GEN_IMG: termo]]). POSIÇÃO: Tag APÓS enunciado." if qtd_imgs > 0 else "Sem imagens."
    diretriz_tipo = "FORMATO DISCURSIVO (Sem alternativas)." if tipo_q == "Discursiva" else "FORMATO OBJETIVO (Múltipla escolha)."
    
    prompt = f"""
    Crie prova de {materia} ({objeto}). QTD: {qtd} ({tipo_q}).
    DIRETRIZES: 1. Contexto Real. 2. Hiperfoco ({hiperfoco}). 3. {diretriz_tipo}. 4. Imagens: {instrucao_img}.
    REGRA: COMANDOS NO IMPERATIVO (Ex: Analise, Calcule).
    SAÍDA: [ANÁLISE PEDAGÓGICA]...---DIVISOR---[ATIVIDADE]...
    """
    try:
        resp = client.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "user", "content": prompt}], temperature=0.8 if modo_profundo else 0.6)
        full_text = resp.choices[0].message.content
        if "---DIVISOR---" in full_text:
            parts = full_text.split("---DIVISOR---")
            return parts[0].replace("[ANÁLISE PEDAGÓGICA]", "").strip(), parts[1].replace("[ATIVIDADE]", "").strip()
        return "Análise indisponível.", full_text
    except Exception as e: return str(e), ""

def gerar_experiencia_ei_bncc(api_key, aluno, campo_exp, objetivo, feedback_anterior=""):
    client = OpenAI(api_key=api_key)
    prompt = f"Crie EXPERIÊNCIA LÚDICA (BNCC) para {aluno['nome']} (EI). Campo: {campo_exp}. Objetivo: {objetivo}. Hiperfoco: {aluno.get('hiperfoco')}. SAÍDA: Markdown."
    try:
        resp = client.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "user", "content": prompt}], temperature=0.7)
        return resp.choices[0].message.content
    except Exception as e: return str(e)

def gerar_roteiro_aula(api_key, aluno, materia, assunto, feedback_anterior=""):
    client = OpenAI(api_key=api_key)
    prompt = f"Roteiro de aula {assunto} para {aluno['nome']}. PEI: {aluno.get('ia_sugestao','')[:500]}. Estrutura: Objetivo, Estratégia, Prática, Verificação."
    try:
        resp = client.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "user", "content": prompt}], temperature=0.7)
        return resp.choices[0].message.content
    except Exception as e: return str(e)

def gerar_quebra_gelo_profundo(api_key, aluno, materia, assunto, hiperfoco, tema_turma_extra=""):
    client = OpenAI(api_key=api_key)
    prompt = f"3 'Papos de Mestre' para conectar {aluno['nome']} ({hiperfoco}) ao tema {assunto} ({materia})."
    try:
        resp = client.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "user", "content": prompt}], temperature=0.8)
        return resp.choices[0].message.content
    except Exception as e: return str(e)

def gerar_dinamica_inclusiva(api_key, aluno, materia, assunto, qtd_alunos, caracteristicas_turma, feedback_anterior=""):
    client = OpenAI(api_key=api_key)
    prompt = f"Dinâmica Inclusiva ({assunto}) para {qtd_alunos} alunos. Foco inclusão de {aluno['nome']}."
    try:
        resp = client.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "user", "content": prompt}], temperature=0.7)
        return resp.choices[0].message.content
    except Exception as e: return str(e)

def gerar_plano_aula_bncc(api_key, materia, assunto, metodologia, tecnica, qtd_alunos, recursos):
    client = OpenAI(api_key=api_key)
    prompt = f"PLANO DE AULA (BNCC). Componente: {materia}. Assunto: {assunto}. Metodologia: {metodologia}. Alunos: {qtd_alunos}. Saída Markdown."
    try:
        resp = client.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "user", "content": prompt}], temperature=0.7)
        return resp.choices[0].message.content
    except Exception as e: return str(e)

# === ESTADOS ===
if 'res_scene_url' not in st.session_state: st.session_state.res_scene_url = None
if 'valid_scene' not in st.session_state: st.session_state.valid_scene = False
if 'res_caa_url' not in st.session_state: st.session_state.res_caa_url = None
if 'valid_caa' not in st.session_state: st.session_state.valid_caa = False

# === LÓGICA DE ABAS (CONDICIONAL EI vs PADRÃO) ===
if is_ei:
    st.info("🧸 **Modo Educação Infantil Ativado:** Foco em Experiências, BNCC e Brincar.")
    tabs = st.tabs(["🧸 Criar Experiência", "🎨 Estúdio Visual & CAA", "📝 Rotina", "🤝 Inclusão"])
    
    with tabs[0]: # Criar Experiência
        st.markdown("<div class='pedagogia-box'><div class='pedagogia-title'><i class='ri-lightbulb-line'></i> Pedagogia do Brincar</div>Criar vivências intencionais.</div>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        campo = c1.selectbox("Campo de Experiência", ["O eu, o outro e o nós", "Corpo, gestos e movimentos", "Traços, sons, cores e formas", "Escuta, fala, pensamento e imaginação", "Espaços, tempos, quantidades, relações e transformações"])
        obj = c2.text_input("Objetivo:")
        if st.button("✨ GERAR EXPERIÊNCIA", type="primary"):
            with st.spinner("Criando..."): st.session_state.res_ei_exp = gerar_experiencia_ei_bncc(api_key, aluno, campo, obj)
        if st.session_state.get('res_ei_exp'): st.markdown(st.session_state.res_ei_exp)

    with tabs[1]: # Visual EI
        st.markdown("<div class='pedagogia-box'><div class='pedagogia-title'><i class='ri-eye-line'></i> Apoio Visual</div>Cenas e Pictogramas.</div>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("#### 🖼️ Cena")
            desc = st.text_area("Descreva:", height=100, key="vdmei")
            if st.button("🎨 Gerar", key="btnei"): 
                with st.spinner("."): st.session_state.res_scene_url = gerar_imagem_inteligente(api_key, f"{desc}. Context: Child education.", unsplash_key)
            if st.session_state.res_scene_url: st.image(st.session_state.res_scene_url)
        with c2:
            st.markdown("#### 🗣️ CAA")
            st.caption("Gere símbolos claros e sem texto.")
            pal = st.text_input("Palavra:", key="caaei")
            if st.button("🧩 Gerar", key="btncaaei"):
                with st.spinner("."): st.session_state.res_caa_url = gerar_pictograma_caa(api_key, pal)
            if st.session_state.res_caa_url: st.image(st.session_state.res_caa_url, width=300)

    with tabs[2]: # Rotina EI
        st.markdown("<div class='pedagogia-box'>Rotina & Previsibilidade</div>", unsafe_allow_html=True)
        rot = st.text_area("Rotina:")
        if st.button("📝 ADAPTAR", type="primary"): st.markdown(gerar_roteiro_aula(api_key, aluno, "Geral", "Rotina", feedback_anterior=rot))

    with tabs[3]: # Inclusão
        st.markdown("<div class='pedagogia-box'>Mediação Social</div>", unsafe_allow_html=True)
        tem = st.text_input("Tema:")
        if st.button("🤝 DINÂMICA", type="primary"): st.markdown(gerar_dinamica_inclusiva(api_key, aluno, "EI", tem, "Pequeno grupo", "Crianças"))

else:
    # === MODO PADRÃO (FUNDAMENTAL / MÉDIO) ===
    tabs = st.tabs([
        "📄 Adaptar Prova", 
        "✂️ Adaptar Atividade", 
        "✨ Criar do Zero", 
        "🎨 Estúdio Visual & CAA", 
        "📝 Roteiro Individual", 
        "🧠 DUA | Plano de Aula", 
        "🧠 DUA | Papo de Mestre", 
        "🧠 DUA | Dinâmica Inclusiva"
    ])

    # 1. PROVA
    with tabs[0]:
        st.markdown("<div class='pedagogia-box'><div class='pedagogia-title'><i class='ri-file-edit-line'></i> Adaptação Curricular</div>Transforme provas padrão em avaliações acessíveis.</div>", unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        mat = c1.selectbox("Matéria", ["Matemática", "Português", "Ciências", "História", "Geografia", "Artes", "Ed. Física", "Inglês"], key="m1")
        tem = c2.text_input("Tema", key="t1")
        tip = c3.selectbox("Tipo", ["Prova", "Tarefa"], key="tp1")
        arq = st.file_uploader("Upload DOCX", type=["docx"], key="f1")
        
        if arq and arq.file_id != st.session_state.get('ld'):
            st.session_state.ld = arq.file_id
            txt, imgs = extrair_dados_docx(arq)
            st.session_state.dt = txt; st.session_state.di = imgs
            st.success(f"{len(imgs)} imagens.")
        
        qs_d = []
        if st.session_state.get('di'):
            st.write("### Mapeamento Imagens")
            cols = st.columns(3)
            for i, img in enumerate(st.session_state.di):
                with cols[i%3]:
                    st.image(img, width=80)
                    q = st.number_input("Questão:", 0, 50, key=f"q{i}")
                    if q > 0: qs_d.append(int(q))

        if st.button("🚀 ADAPTAR", type="primary", key="b1"):
            if not st.session_state.get('dt'): st.warning("Arquivo?"); st.stop()
            with st.spinner("Adaptando..."):
                r, t = adaptar_conteudo_docx(api_key, aluno, st.session_state.dt, mat, tem, tip, True, qs_d)
                st.session_state['rd'] = {'rac': r, 'txt': t}
        
        if 'rd' in st.session_state:
            st.markdown(f"<div class='analise-box'>{st.session_state['rd']['rac']}</div>", unsafe_allow_html=True)
            doc = construir_docx_final(st.session_state['rd']['txt'], aluno, mat, {}, None, tip)
            st.download_button("📥 BAIXAR DOCX", doc, "Adaptada.docx", "primary")

    # 2. ATIVIDADE (OCR)
    with tabs[1]:
        st.markdown("<div class='pedagogia-box'><div class='pedagogia-title'><i class='ri-scissors-cut-line'></i> OCR & Adaptação</div>Foto do livro/caderno.</div>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        mat = c1.selectbox("Matéria", ["Matemática", "Português", "Ciências", "História"], key="m2")
        arq = st.file_uploader("Upload Imagem", type=["png","jpg"], key="f2")
        
        if arq:
            img = Image.open(arq)
            st.image(img, width=300)
            if st.button("🚀 ADAPTAR", type="primary", key="b2"):
                with st.spinner("Lendo..."):
                    r, t = adaptar_conteudo_imagem(api_key, aluno, arq.getvalue(), mat, "", "Atividade", False)
                    st.session_state['ri'] = {'rac': r, 'txt': t}
        
        if 'ri' in st.session_state:
            st.markdown(f"<div class='analise-box'>{st.session_state['ri']['rac']}</div>", unsafe_allow_html=True)
            doc = construir_docx_final(st.session_state['ri']['txt'], aluno, mat, {}, None, "Atividade")
            st.download_button("📥 BAIXAR DOCX", doc, "Atividade.docx", "primary")

    # 3. CRIAR DO ZERO
    with tabs[2]:
        st.markdown("<div class='pedagogia-box'><div class='pedagogia-title'><i class='ri-magic-line'></i> Criação com DUA</div>Prioridade: Banco de Imagens > IA.</div>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        mat = c1.selectbox("Matéria", ["Matemática", "Português", "Ciências", "História"], key="m3")
        obj = c2.text_input("Assunto", key="o3")
        c3, c4 = st.columns(2)
        qtd = c3.slider("Qtd", 1, 10, 5)
        tip = c4.selectbox("Tipo", ["Objetiva", "Discursiva"])
        
        use_img = st.checkbox("Incluir Imagens?")
        qtd_img = st.slider("Quantas com imagem?", 0, qtd, 2, disabled=not use_img)

        if st.button("✨ CRIAR", type="primary", key="b3"):
            with st.spinner("Criando..."):
                r, t = criar_profissional(api_key, aluno, mat, obj, qtd, tip, qtd_img if use_img else 0)
                st.session_state['rc'] = {'rac': r, 'txt': t}
                
                # Processa imagens (Banco > IA)
                tags = re.findall(r'\[\[GEN_IMG: (.*?)\]\]', t)
                new_map = {}; cnt = 0
                for tg in tags:
                    cnt += 1
                    url = gerar_imagem_inteligente(api_key, tg, unsplash_key, prioridade="BANCO")
                    if url:
                        io = baixar_imagem_url(url)
                        if io: new_map[cnt] = io.getvalue()
                
                ft = t
                for i in range(1, cnt+1): ft = re.sub(r'\[\[GEN_IMG: .*?\]\]', f"[[IMG_G{i}]]", ft, count=1)
                st.session_state['rc']['txt'] = ft
                st.session_state['rc']['map'] = new_map

        if 'rc' in st.session_state:
            st.markdown(f"<div class='analise-box'>{st.session_state['rc']['rac']}</div>", unsafe_allow_html=True)
            doc = construir_docx_final(st.session_state['rc']['txt'], aluno, mat, st.session_state['rc']['map'], None, "Criada")
            st.download_button("📥 BAIXAR DOCX", doc, "Criada.docx", "primary")

    # 4. ESTUDIO VISUAL
    with tabs[3]:
        st.markdown("<div class='pedagogia-box'><div class='pedagogia-title'><i class='ri-image-line'></i> Recursos Visuais</div>Flashcards e CAA.</div>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("#### 🖼️ Ilustração")
            d = st.text_area("Descreva:", key="d4")
            if st.button("🎨 Gerar", key="b4"):
                with st.spinner("."): st.session_state.res_scene_url = gerar_imagem_inteligente(api_key, f"{d}. Education context.", unsplash_key)
            if st.session_state.res_scene_url: st.image(st.session_state.res_scene_url)
        with c2:
            st.markdown("#### 🗣️ Símbolo CAA")
            st.caption("Gere símbolos de comunicação alternativa claros, com alto contraste e sem texto.")
            p = st.text_input("Conceito:", key="p4")
            if st.button("🧩 Gerar", key="b4b"):
                with st.spinner("."): st.session_state.res_caa_url = gerar_pictograma_caa(api_key, p)
            if st.session_state.res_caa_url: st.image(st.session_state.res_caa_url, width=300)

    # 5. ROTEIRO
    with tabs[4]:
        st.markdown("<div class='pedagogia-box'>Roteiro Individualizado</div>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        m = c1.selectbox("Matéria", ["Matemática", "Português"], key="m5")
        a = c2.text_input("Assunto:", key="a5")
        if st.button("📝 GERAR ROTEIRO", type="primary"):
            st.markdown(gerar_roteiro_aula(api_key, aluno, m, a))

    # 6. PLANO DE AULA DUA
    with tabs[5]:
        st.markdown("<div class='pedagogia-box'><div class='pedagogia-title'><i class='ri-book-open-line'></i> Plano de Aula DUA</div>Planejamento BNCC completo.</div>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        m = c1.selectbox("Matéria", ["Matemática", "Português"], key="m6")
        a = c2.text_input("Assunto:", key="a6")
        c3, c4 = st.columns(2)
        met = c3.selectbox("Metodologia", ["Ativa", "Expositiva"], key="met6")
        tec = c4.selectbox("Técnica", ["Gamificação", "Rotação"], key="tec6") if met == "Ativa" else None
        if st.button("📅 GERAR PLANO", type="primary"):
            st.markdown(gerar_plano_aula_bncc(api_key, m, a, met, tec, 30, ["Projetor"]))

    # 7. PAPO DE MESTRE
    with tabs[6]:
        st.markdown("<div class='pedagogia-box'>Engajamento & DUA</div>", unsafe_allow_html=True)
        if st.button("🗣️ GERAR CONEXÕES", type="primary"):
            st.markdown(gerar_quebra_gelo_profundo(api_key, aluno, "Geral", "Aula", aluno.get('hiperfoco')))

    # 8. DINAMICA
    with tabs[7]:
        st.markdown("<div class='pedagogia-box'>Dinâmica Inclusiva</div>", unsafe_allow_html=True)
        if st.button("🤝 GERAR DINÂMICA", type="primary"):
            st.markdown(gerar_dinamica_inclusiva(api_key, aluno, "Geral", "Inclusão", 30, "Mista"))
