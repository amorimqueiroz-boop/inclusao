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
# 3. AUTENTICAÇÃO E DADOS
# ==============================================================================
def verificar_acesso():
    if "autenticado" not in st.session_state or not st.session_state["autenticado"]:
        st.error("🔒 Acesso Negado.")
        st.stop()
    
    st.markdown("""
        <style>
            footer {visibility: hidden !important;}
            [data-testid="stHeader"] { visibility: visible !important; background-color: transparent !important; }
            .block-container {padding-top: 2rem !important;}
        </style>
    """, unsafe_allow_html=True)

verificar_acesso()

with st.sidebar:
    try: st.image("ominisfera.png", width=150)
    except: st.write("🌐 OMNISFERA")
    st.markdown("---")
    if st.button("🏠 Voltar para Home", use_container_width=True): st.switch_page("Home.py")
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
# 4. FUNÇÕES CORE (Lógica e Prompts)
# ==============================================================================

# --- Helpers de Arquivo e Imagem ---
def get_img_tag(file_path, width):
    if os.path.exists(file_path):
        with open(file_path, "rb") as f:
            data = base64.b64encode(f.read()).decode("utf-8")
        return f'<img src="data:image/png;base64,{data}" width="{width}">'
    return "🚀"

def extrair_dados_arquivo(uploaded_file):
    uploaded_file.seek(0)
    nome_arquivo = uploaded_file.name.lower()
    imagens = []; texto = ""
    if nome_arquivo.endswith('.pdf'):
        try:
            reader = PdfReader(uploaded_file)
            for page in reader.pages:
                if page.extract_text(): texto += page.extract_text() + "\n"
        except: texto = "[Erro na leitura do PDF]"
    elif nome_arquivo.endswith('.docx') or nome_arquivo.endswith('.doc'):
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
    query_clean = re.sub(r'[^\w\s]', '', query).strip()
    url = f"https://api.unsplash.com/search/photos?query={query_clean}&per_page=1&client_id={access_key}&lang=pt"
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
        doc.add_paragraph("_"*50)
        doc.add_heading('Atividades', level=2)
    
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
                            r = p.add_run(); r.add_picture(BytesIO(img_bytes), width=Inches(4.5))
                        except: pass
                elif parte.strip(): doc.add_paragraph(parte.strip())
        else:
            if linha.strip(): doc.add_paragraph(linha.strip())
    buffer = BytesIO(); doc.save(buffer); buffer.seek(0)
    return buffer

# --- Gerenciador de Imagens Híbrido ---
def obter_recurso_visual(api_key, prompt, unsplash_key=None, modo="ia_strict", feedback_anterior=""):
    """
    MODOS:
    - 'ia_strict': Estúdio Visual/CAA. Só gera IA.
    - 'stock_first': Criar Prova. Tenta Unsplash, se falhar ou sem key, vai de IA.
    """
    client = OpenAI(api_key=api_key)
    prompt_final = f"{prompt}. Adjustment: {feedback_anterior}" if feedback_anterior else prompt
    
    # Prioridade Stock
    if modo == "stock_first" and unsplash_key:
        termo = prompt.split('.')[0] if '.' in prompt else prompt
        url = buscar_imagem_unsplash(termo, unsplash_key)
        if url: return url
    
    # Fallback ou Strict IA
    try:
        didactic_prompt = f"Educational illustration, clean flat vector style, white background. NO TEXT, NO LABELS. Visual representation of: {prompt_final}"
        resp = client.images.generate(model="dall-e-3", prompt=didactic_prompt, size="1024x1024", quality="standard", n=1)
        return resp.data[0].url
    except:
        # Se IA falhar e for stock_first, tenta stock como último recurso
        if modo == "stock_first" and unsplash_key: return buscar_imagem_unsplash(prompt, unsplash_key)
        return None

def gerar_pictograma_caa(api_key, conceito, feedback_anterior=""):
    client = OpenAI(api_key=api_key)
    ajuste = f" CORREÇÃO: {feedback_anterior}" if feedback_anterior else ""
    prompt = f"COMMUNICATION SYMBOL (AAC/PECS) for: '{conceito}'. {ajuste}. Flat vector icon (ARASAAC style), White background, Thick black outlines. MUTE IMAGE. NO TEXT."
    try:
        resp = client.images.generate(model="dall-e-3", prompt=prompt, size="1024x1024", quality="standard", n=1)
        return resp.data[0].url
    except: return None

# --- Funções de Texto (GPT) ---

def adaptar_conteudo_docx(api_key, aluno, texto, materia, tema, tipo_atv, remover_resp, questoes_mapeadas, modo_profundo=False, feedback_anterior=""):
    client = OpenAI(api_key=api_key)
    lista_q = ", ".join([str(n) for n in questoes_mapeadas])
    style = "Seja didático e use Cadeia de Pensamento." if modo_profundo else "Seja objetivo."
    ajuste = f"AJUSTE SOLICITADO: {feedback_anterior}" if feedback_anterior else ""
    prompt = f"""
    ESPECIALISTA EM DUA. {style} {ajuste}
    PERFIL: {aluno.get('ia_sugestao', '')[:1000]}
    ADAPTE A PROVA: Use hiperfoco ({aluno.get('hiperfoco')}) em 30%.
    IMAGENS: O professor indicou imagens nas questões: {lista_q}. Nessas, ESTRUTURA: 1. Enunciado -> 2. [[IMG_número]] -> 3. Alternativas.
    SAÍDA: [ANÁLISE PEDAGÓGICA] ... ---DIVISOR--- [ATIVIDADE] ...
    CONTEXTO: {materia} | {tema}. TEXTO ORIGINAL: {texto}
    """
    try:
        resp = client.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "user", "content": prompt}], temperature=0.7)
        full = resp.choices[0].message.content
        if "---DIVISOR---" in full:
            p = full.split("---DIVISOR---")
            return p[0].replace("[ANÁLISE PEDAGÓGICA]", "").strip(), p[1].replace("[ATIVIDADE]", "").strip()
        return "Análise indisponível.", full
    except Exception as e: return str(e), ""

def adaptar_conteudo_imagem(api_key, aluno, img_bytes, materia, tema, tipo_atv, livro_prof, modo_profundo=False, feedback_anterior=""):
    client = OpenAI(api_key=api_key)
    b64 = base64.b64encode(img_bytes).decode('utf-8')
    inst = "Remova respostas." if livro_prof else ""
    ajuste = f"AJUSTE: {feedback_anterior}" if feedback_anterior else ""
    prompt = f"""
    ESPECIALISTA EM ACESSIBILIDADE. {ajuste}
    1. Transcreva e adapte. {inst}
    2. PEI: {aluno.get('ia_sugestao', '')[:800]}.
    3. Use [[IMG_1]] UMA VEZ após o enunciado.
    SAÍDA: [ANÁLISE PEDAGÓGICA] ... ---DIVISOR--- [ATIVIDADE] ...
    """
    try:
        resp = client.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "user", "content": [{"type": "text", "text": prompt}, {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}}]}], temperature=0.7)
        full = resp.choices[0].message.content
        if "---DIVISOR---" in full:
            p = full.split("---DIVISOR---")
            return p[0].replace("[ANÁLISE PEDAGÓGICA]", "").strip(), garantir_tag_imagem(p[1].replace("[ATIVIDADE]", "").strip())
        return "Análise indisponível.", full
    except Exception as e: return str(e), ""

def criar_profissional(api_key, aluno, materia, objeto, qtd_total, tipo_q, qtd_imagens_desejada, modo_profundo=False, feedback_anterior=""):
    """
    Gera questões do zero com lógica reforçada de BNCC, Bloom e Posição da Imagem.
    """
    client = OpenAI(api_key=api_key)
    hiperfoco = aluno.get('hiperfoco', 'Geral')
    
    ajuste = f"AJUSTE SOLICITADO: {feedback_anterior}" if feedback_anterior else ""
    inst_tipo = "50% Objetivas e 50% Discursivas." if tipo_q == "Mista" else f"Questões do tipo {tipo_q}."

    inst_img = "Não inclua imagens."
    if qtd_imagens_desejada > 0:
        inst_img = f"""
        INSTRUÇÃO VISUAL (PRIORIDADE BANCO DE IMAGENS):
        Incluir EXATAMENTE {qtd_imagens_desejada} imagens distribuídas.
        Tag: [[GEN_IMG: keyword_english]].
        A KEYWORD deve ser simples (ex: "Apple", "Dog running") para busca em banco.
        REGRA POSICIONAMENTO: A tag [[GEN_IMG...]] deve vir IMEDIATAMENTE APÓS O ENUNCIADO e ANTES das alternativas.
        REGRA REPETIÇÃO: NÃO repita imagens.
        """

    prompt = f"""
    Atue como professor elaborador especialista em BNCC e Taxonomia de Bloom. {ajuste}
    Crie prova de {materia} ({objeto}). QTD: {qtd_total}. {inst_tipo}
    
    DIRETRIZES: 
    1. Baseie-se na BNCC e use a TAXONOMIA DE BLOOM adequada à série.
    2. Contexto Real. Hiperfoco ({hiperfoco}) em 30%.
    3. {inst_img}
    
    SAÍDA: [ANÁLISE PEDAGÓGICA] ... ---DIVISOR--- [ATIVIDADE] ...
    """
    try:
        resp = client.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "user", "content": prompt}], temperature=0.8)
        full = resp.choices[0].message.content
        if "---DIVISOR---" in full:
            p = full.split("---DIVISOR---")
            return p[0].replace("[ANÁLISE PEDAGÓGICA]", "").strip(), p[1].replace("[ATIVIDADE]", "").strip()
        return "Análise indisponível.", full
    except Exception as e: return str(e), ""

def gerar_plano_aula_completo(api_key, aluno, tempo, componente, tema, feedback_anterior=""):
    client = OpenAI(api_key=api_key)
    ajuste = f"AJUSTE: {feedback_anterior}" if feedback_anterior else ""
    prompt = f"""
    Crie um PLANO DE AULA (DUA) para a turma toda, mas inclusivo para {aluno['nome']}.
    TEMPO: {tempo}. COMPONENTE: {componente}. TEMA: {tema}.
    PEI DO ALUNO: {aluno.get('ia_sugestao','')[:600]}.
    EVITE GATILHOS.
    Estrutura: Objetivos (BNCC), Metodologia, Adaptação Específica, Avaliação. {ajuste}
    """
    try:
        resp = client.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "user", "content": prompt}], temperature=0.7)
        return resp.choices[0].message.content
    except Exception as e: return str(e)

def gerar_contextualizacao(api_key, aluno, componente, assunto, tema_interesse, feedback_anterior=""):
    client = OpenAI(api_key=api_key)
    ajuste = f"AJUSTE: {feedback_anterior}" if feedback_anterior else ""
    prompt = f"""
    Crie uma explicação/analogia (Papo de Mestre) conectando {componente}/{assunto} com o tema de interesse: {tema_interesse}.
    Público: {aluno['nome']} e turma. {ajuste}
    """
    try:
        resp = client.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "user", "content": prompt}], temperature=0.7)
        return resp.choices[0].message.content
    except Exception as e: return str(e)

def gerar_dinamica_turma(api_key, aluno, componente, tema, feedback_anterior=""):
    client = OpenAI(api_key=api_key)
    ajuste = f"AJUSTE: {feedback_anterior}" if feedback_anterior else ""
    prompt = f"""
    Crie uma DINÂMICA INCLUSIVA para toda a turma sobre {componente}: {tema}.
    O aluno {aluno['nome']} deve participar ativamente sem barreiras e sem gatilhos.
    PEI: {aluno.get('ia_sugestao','')[:600]}. {ajuste}
    """
    try:
        resp = client.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "user", "content": prompt}], temperature=0.7)
        return resp.choices[0].message.content
    except Exception as e: return str(e)

def gerar_experiencia_ei_bncc(api_key, aluno, campo, obj, feedback=""):
    client = OpenAI(api_key=api_key)
    ajuste = f"AJUSTE: {feedback}" if feedback else ""
    prompt = f"""
    Especialista EI (BNCC). Aluno: {aluno['nome']}. Hiperfoco: {aluno.get('hiperfoco')}.
    Crie EXPERIÊNCIA LÚDICA para Campo: {campo}. Objetivo: {obj}. {ajuste}
    SAÍDA MARKDOWN: ## 🧸 Experiência...
    """
    try:
        resp = client.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "user", "content": prompt}], temperature=0.7)
        return resp.choices[0].message.content
    except Exception as e: return str(e)

def gerar_roteiro_rotina_ei(api_key, aluno, rotina_txt, feedback=""):
    client = OpenAI(api_key=api_key)
    ajuste = f"AJUSTE: {feedback}" if feedback else ""
    prompt = f"Analise esta rotina de EI e sugira adaptações para {aluno['nome']}: {rotina_txt}. {ajuste}"
    try:
        resp = client.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "user", "content": prompt}], temperature=0.7)
        return resp.choices[0].message.content
    except Exception as e: return str(e)

# ==============================================================================
# 5. INTERFACE DO USUÁRIO
# ==============================================================================

with st.sidebar:
    if 'OPENAI_API_KEY' in st.secrets: api_key = st.secrets['OPENAI_API_KEY']; st.success("✅ OpenAI OK")
    else: api_key = st.text_input("Chave OpenAI:", type="password")
    
    st.markdown("---")
    if 'UNSPLASH_ACCESS_KEY' in st.secrets: unsplash_key = st.secrets['UNSPLASH_ACCESS_KEY']; st.success("✅ Unsplash OK")
    else: unsplash_key = st.text_input("Chave Unsplash (Opcional):", type="password")
    
    st.markdown("---")
    if st.button("🧹 Limpar Tudo", type="secondary"):
        for key in list(st.session_state.keys()):
            if key not in ['banco_estudantes', 'OPENAI_API_KEY', 'UNSPLASH_ACCESS_KEY', 'autenticado']: del st.session_state[key]
        st.rerun()

img_hub_html = get_img_tag("hub.png", "220") 
st.markdown(f"""<div class="header-hub"><div style="flex-shrink: 0;">{img_hub_html}</div><div style="flex-grow: 1; text-align: center;"><p style="margin:0; color:#2C5282; font-size: 1.3rem; font-weight: 700;">Adaptação de Materiais & Criação</p></div></div>""", unsafe_allow_html=True)

if not st.session_state.banco_estudantes: st.warning("⚠️ Nenhum aluno encontrado."); st.stop()

lista = [a['nome'] for a in st.session_state.banco_estudantes]
nome_aluno = st.selectbox("📂 Selecione o Estudante:", lista)
aluno = next(a for a in st.session_state.banco_estudantes if a['nome'] == nome_aluno)
serie_aluno = aluno.get('serie', '').lower()
is_ei = "infantil" in serie_aluno or "creche" in serie_aluno or "pré" in serie_aluno

st.markdown(f"""<div class="student-header"><div class="student-info-item"><div class="student-label">Nome</div><div class="student-value">{aluno.get('nome')}</div></div><div class="student-info-item"><div class="student-label">Série</div><div class="student-value">{aluno.get('serie', '-')}</div></div><div class="student-info-item"><div class="student-label">Hiperfoco</div><div class="student-value">{aluno.get('hiperfoco', '-')}</div></div></div>""", unsafe_allow_html=True)

# Inicialização de Estado Global
keys_init = ['res_scene_url', 'valid_scene', 'res_caa_url', 'valid_caa', 'res_ei_exp', 'res_roteiro', 'res_papo', 'res_dina', 'res_docx', 'res_img', 'res_create']
for k in keys_init:
    if k not in st.session_state: st.session_state[k] = None

# ==============================================================================
# 6. LÓGICA DE ABAS
# ==============================================================================

if is_ei:
    # --- MODO EDUCAÇÃO INFANTIL ---
    st.info("🧸 **Modo Educação Infantil:** Foco em Experiências e Brincar.")
    tabs = st.tabs(["🧸 Criar Experiência (BNCC)", "🎨 Estúdio Visual & CAA", "📝 Rotina & AVD", "🤝 Inclusão no Brincar"])
    
    with tabs[0]:
        st.markdown("<div class='pedagogia-box'>Pedagogia do Brincar (BNCC).</div>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        campo = c1.selectbox("Campo de Experiência", ["O eu, o outro e o nós", "Corpo, gestos e movimentos", "Traços, sons, cores e formas", "Escuta, fala, pensamento e imaginação", "Espaços, tempos, quantidades, relações e transformações"])
        obj = c2.text_input("Objetivo:")
        if st.button("✨ GERAR EXPERIÊNCIA", type="primary"):
            with st.spinner("Criando..."):
                st.session_state.res_ei_exp = {'txt': gerar_experiencia_ei_bncc(api_key, aluno, campo, obj), 'valid': False}
        if st.session_state.res_ei_exp:
            st.markdown(st.session_state.res_ei_exp['txt'])
            if st.session_state.res_ei_exp['valid']: st.markdown("<div class='validado-box'>✅ APROVADO</div>", unsafe_allow_html=True)
            else:
                c_v, c_r = st.columns([1,2])
                if c_v.button("✅ Validar"): st.session_state.res_ei_exp['valid'] = True; st.rerun()
                with c_r.expander("🔄 Refazer"):
                    fb = st.text_input("Ajuste:"); 
                    if st.button("Refazer"): 
                        st.session_state.res_ei_exp = {'txt': gerar_experiencia_ei_bncc(api_key, aluno, campo, obj, fb), 'valid': False}; st.rerun()

    with tabs[1]:
        st.markdown("<div class='pedagogia-box'>Apoio Visual: Cenas e Pictogramas. (Sempre IA).</div>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("#### 🖼️ Cena")
            desc = st.text_area("Descrição:")
            if st.button("🎨 Gerar Cena"):
                with st.spinner("Desenhando..."): st.session_state.res_scene_url = obter_recurso_visual(api_key, f"{desc} child education", unsplash_key, "ia_strict"); st.session_state.valid_scene = False
            if st.session_state.res_scene_url:
                st.image(st.session_state.res_scene_url)
                if st.session_state.valid_scene: st.success("✅ Validado")
                else:
                    if st.button("✅ Validar Cena"): st.session_state.valid_scene = True; st.rerun()
                    with st.expander("Refazer Cena"):
                        fb = st.text_input("Ajuste Cena"); 
                        if st.button("Refazer C"): st.session_state.res_scene_url = obter_recurso_visual(api_key, f"{desc} child education", unsplash_key, "ia_strict", fb); st.rerun()
        with c2:
            st.markdown("#### 🗣️ CAA")
            conc = st.text_input("Conceito:")
            if st.button("🧩 Gerar Picto"):
                with st.spinner("Criando..."): st.session_state.res_caa_url = gerar_pictograma_caa(api_key, conc); st.session_state.valid_caa = False
            if st.session_state.res_caa_url:
                st.image(st.session_state.res_caa_url, width=300)
                if st.session_state.valid_caa: st.success("✅ Validado")
                else:
                    if st.button("✅ Validar Picto"): st.session_state.valid_caa = True; st.rerun()
                    with st.expander("Refazer Picto"):
                        fb = st.text_input("Ajuste Picto"); 
                        if st.button("Refazer P"): st.session_state.res_caa_url = gerar_pictograma_caa(api_key, conc, fb); st.rerun()

    with tabs[2]:
        st.markdown("<div class='pedagogia-box'>Rotina & AVD.</div>", unsafe_allow_html=True)
        rotina = st.text_area("Rotina:"); 
        if st.button("📝 Adaptar"): st.session_state.res_roteiro = {'txt': gerar_roteiro_rotina_ei(api_key, aluno, rotina), 'valid': False}
        if st.session_state.res_roteiro:
            st.markdown(st.session_state.res_roteiro['txt'])
            if st.session_state.res_roteiro['valid']: st.markdown("<div class='validado-box'>✅ APROVADO</div>", unsafe_allow_html=True)
            else:
                if st.button("✅ Validar"): st.session_state.res_roteiro['valid'] = True; st.rerun()
                with st.expander("Refazer"):
                    fb = st.text_input("Ajuste R"); 
                    if st.button("Refazer"): st.session_state.res_roteiro = {'txt': gerar_roteiro_rotina_ei(api_key, aluno, rotina, fb), 'valid': False}; st.rerun()

    with tabs[3]:
        st.markdown("<div class='pedagogia-box'>Mediação Social e Brincar.</div>", unsafe_allow_html=True)
        tema = st.text_input("Tema/Brincadeira:"); 
        if st.button("🤝 Gerar"): st.session_state.res_dina = {'txt': gerar_dinamica_turma(api_key, aluno, "EI", tema), 'valid': False}
        if st.session_state.res_dina:
            st.markdown(st.session_state.res_dina['txt'])
            if st.session_state.res_dina['valid']: st.markdown("<div class='validado-box'>✅ APROVADO</div>", unsafe_allow_html=True)
            else:
                if st.button("✅ Validar"): st.session_state.res_dina['valid'] = True; st.rerun()
                with st.expander("Refazer"):
                    fb = st.text_input("Ajuste D"); 
                    if st.button("Refazer"): st.session_state.res_dina = {'txt': gerar_dinamica_turma(api_key, aluno, "EI", tema, fb), 'valid': False}; st.rerun()

else:
    # --- MODO PADRÃO (FUNDAMENTAL / MÉDIO) ---
    tabs = st.tabs(["📄 Adaptar Prova", "✂️ Adaptar Atividade", "✨ Criar do Zero", "🎨 Estúdio Visual", "📝 Roteiro de Aula", "🗣️ Papo de Mestre", "🤝 Dinâmica Inclusiva"])

    # 1. ADAPTAR PROVA
    with tabs[0]:
        st.markdown("<div class='pedagogia-box'>Adaptação Curricular (DUA).</div>", unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        mat = c1.selectbox("Matéria", ["Matemática", "Português", "Ciências", "História", "Geografia", "Artes", "Inglês"], key="m1")
        tema = c2.text_input("Tema", key="t1")
        tipo = c3.selectbox("Tipo", ["Prova", "Tarefa"], key="tp1")
        arq = st.file_uploader("Arquivo (DOCX, PDF, DOC)", type=["docx", "doc", "pdf"], key="f1")
        
        if 'docx_imgs' not in st.session_state: st.session_state.docx_imgs = []
        if 'docx_txt' not in st.session_state: st.session_state.docx_txt = None

        if arq and arq.file_id != st.session_state.get('last_d'):
            st.session_state.last_d = arq.file_id
            txt, imgs = extrair_dados_arquivo(arq)
            st.session_state.docx_txt = txt; st.session_state.docx_imgs = imgs
            st.success(f"{len(imgs)} imagens.")
        
        qs_d = []
        if st.session_state.docx_imgs:
            st.write("Mapeamento:"); cols = st.columns(3)
            for i, img in enumerate(st.session_state.docx_imgs):
                with cols[i%3]: st.image(img, width=80); q = st.number_input(f"Q:", 0, 50, key=f"d_{i}"); 
                if q>0: qs_d.append(int(q))

        if st.button("🚀 ADAPTAR", type="primary"):
            if not st.session_state.docx_txt: st.warning("Sem arquivo."); st.stop()
            with st.spinner("Adaptando..."):
                rac, txt = adaptar_conteudo_docx(api_key, aluno, st.session_state.docx_txt, mat, tema, tipo, True, qs_d)
                st.session_state.res_docx = {'rac': rac, 'txt': txt, 'valid': False}

        if st.session_state.res_docx:
            res = st.session_state.res_docx
            if res['valid']: st.markdown("<div class='validado-box'>✅ VALIDADO</div>", unsafe_allow_html=True)
            else:
                c_v, c_r = st.columns([1,2])
                if c_v.button("✅ Validar", key="v1"): st.session_state.res_docx['valid'] = True; st.rerun()
                with c_r.expander("🔄 Refazer"):
                    fb = st.text_input("Ajuste:", key="fb1")
                    if st.button("Refazer", key="b1"):
                        with st.spinner("..."):
                            rac, txt = adaptar_conteudo_docx(api_key, aluno, st.session_state.docx_txt, mat, tema, tipo, True, qs_d, feedback_anterior=fb)
                            st.session_state.res_docx = {'rac': rac, 'txt': txt, 'valid': False}; st.rerun()
            st.markdown(f"<div class='analise-box'>{res['rac']}</div>", unsafe_allow_html=True)
            st.download_button("📥 DOCX", construir_docx_final(res['txt'], aluno, mat, {}, None, tipo), "Adaptada.docx")

    # 2. ADAPTAR ATIVIDADE
    with tabs[1]:
        st.markdown("<div class='pedagogia-box'>OCR e Adaptação de Imagem.</div>", unsafe_allow_html=True)
        arq_i = st.file_uploader("Foto", type=["png","jpg"], key="f2")
        if arq_i:
            img = Image.open(arq_i); img.thumbnail((800,800))
            crop = st_cropper(img, box_color='#FF0000', key="c2")
            if st.button("🚀 ADAPTAR", type="primary"):
                buf = BytesIO(); crop.save(buf, format="JPEG"); b = buf.getvalue()
                rac, txt = adaptar_conteudo_imagem(api_key, aluno, b, "Geral", "Geral", "Ativ", False)
                st.session_state.res_img = {'rac': rac, 'txt': txt, 'img': b, 'valid': False}
        
        if st.session_state.res_img:
            res = st.session_state.res_img
            if res['valid']: st.markdown("<div class='validado-box'>✅ VALIDADO</div>", unsafe_allow_html=True)
            else:
                c_v, c_r = st.columns([1,2])
                if c_v.button("✅ Validar", key="v2"): st.session_state.res_img['valid'] = True; st.rerun()
                with c_r.expander("🔄 Refazer"):
                    fb = st.text_input("Ajuste:", key="fb2")
                    if st.button("Refazer", key="b2"):
                        with st.spinner("..."):
                            rac, txt = adaptar_conteudo_imagem(api_key, aluno, res['img'], "Geral", "Geral", "Ativ", False, feedback_anterior=fb)
                            st.session_state.res_img = {'rac': rac, 'txt': txt, 'img': res['img'], 'valid': False}; st.rerun()
            st.markdown(f"<div class='analise-box'>{res['rac']}</div>", unsafe_allow_html=True)
            st.image(res['img'], width=300)
            st.download_button("📥 DOCX", construir_docx_final(res['txt'], aluno, "Geral", {1:res['img']}, None, "Ativ"), "Atividade.docx")

    # 3. CRIAR DO ZERO
    with tabs[2]:
        st.markdown("<div class='pedagogia-box'>Criação com BNCC, Bloom e DUA. Prioridade Imagem: Stock -> IA.</div>", unsafe_allow_html=True)
        c1, c2 = st.columns(2); mat = c1.selectbox("Componente", ["Matemática", "Português", "Ciências", "História", "Geografia"], key="m3"); obj = c2.text_input("Assunto", key="t3")
        c3, c4 = st.columns(2); qtd = c3.slider("Qtd Questões", 1, 10, 5, key="q3"); tipo = c4.selectbox("Tipo", ["Objetiva", "Discursiva", "Mista"], key="tp3")
        st.write("---")
        qtd_img = st.slider("Quantidade de Imagens", 0, qtd, min(3, qtd))
        
        if st.button("✨ CRIAR", type="primary", key="b3"):
            with st.spinner("Criando..."):
                rac, txt = criar_profissional(api_key, aluno, mat, obj, qtd, tipo, qtd_img)
                # Processa imagens (STOCK FIRST)
                mapa = {}; cnt = 0; tags = re.findall(r'\[\[GEN_IMG: (.*?)\]\]', txt)
                for p in tags:
                    cnt+=1; u = obter_recurso_visual(api_key, p, unsplash_key, "stock_first")
                    if u: 
                        io = baixar_imagem_url(u)
                        if io: mapa[cnt] = io.getvalue()
                # Limpa tags
                txt_fin = txt
                for i in range(1, cnt+1): txt_fin = re.sub(r'\[\[GEN_IMG: .*?\]\]', f"[[IMG_G{i}]]", txt_fin, count=1)
                st.session_state.res_create = {'rac': rac, 'txt': txt_fin, 'map': mapa, 'valid': False}
        
        if st.session_state.res_create:
            res = st.session_state.res_create
            if res['valid']: st.markdown("<div class='validado-box'>✅ VALIDADO</div>", unsafe_allow_html=True)
            else:
                c_v, c_r = st.columns([1,2])
                if c_v.button("✅ Validar", key="v3"): st.session_state.res_create['valid'] = True; st.rerun()
                with c_r.expander("🔄 Refazer"):
                    fb = st.text_input("Ajuste:", key="fb3")
                    if st.button("Refazer", key="br3"):
                        with st.spinner("..."):
                            rac, txt = criar_profissional(api_key, aluno, mat, obj, qtd, tipo, qtd_img, feedback_anterior=fb)
                            mapa = {}; cnt = 0; tags = re.findall(r'\[\[GEN_IMG: (.*?)\]\]', txt)
                            for p in tags:
                                cnt+=1; u = obter_recurso_visual(api_key, p, unsplash_key, "stock_first")
                                if u: 
                                    io = baixar_imagem_url(u)
                                    if io: mapa[cnt] = io.getvalue()
                            txt_fin = txt
                            for i in range(1, cnt+1): txt_fin = re.sub(r'\[\[GEN_IMG: .*?\]\]', f"[[IMG_G{i}]]", txt_fin, count=1)
                            st.session_state.res_create = {'rac': rac, 'txt': txt_fin, 'map': mapa, 'valid': False}; st.rerun()
            st.markdown(f"<div class='analise-box'>{res['rac']}</div>", unsafe_allow_html=True)
            with st.container(border=True):
                pts = re.split(r'(\[\[IMG_G\d+\]\])', res['txt'])
                for p in pts:
                    tag = re.search(r'\[\[IMG_G(\d+)\]\]', p)
                    if tag:
                        i = int(tag.group(1)); im = res['map'].get(i)
                        if im: st.image(im, width=300)
                    elif p.strip(): st.markdown(p.strip())
            st.download_button("📥 DOCX", construir_docx_final(res['txt'], aluno, mat, res['map'], None, "Criada"), "Atividade.docx")

    # 4. ESTUDIO VISUAL (IA STRICT)
    with tabs[3]:
        st.markdown("<div class='pedagogia-box'>Recursos Visuais. (Sempre IA).</div>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("#### Cena")
            desc = st.text_area("Descrição:", key="d4")
            if st.button("🎨 Gerar", key="b4a"):
                 with st.spinner("..."): st.session_state.res_scene_url = obter_recurso_visual(api_key, f"{desc} education", unsplash_key, "ia_strict"); st.session_state.valid_scene = False
            if st.session_state.res_scene_url:
                st.image(st.session_state.res_scene_url)
                if st.session_state.valid_scene: st.success("Validado")
                else:
                    if st.button("✅", key="v4a"): st.session_state.valid_scene = True; st.rerun()
                    with st.expander("Refazer"):
                        fb = st.text_input("Ajuste", key="f4a")
                        if st.button("Refazer", key="br4a"): st.session_state.res_scene_url = obter_recurso_visual(api_key, f"{desc} education", unsplash_key, "ia_strict", fb); st.rerun()
        with c2:
            st.markdown("#### CAA")
            conc = st.text_input("Conceito:", key="c4")
            if st.button("🧩 Gerar", key="b4b"):
                 with st.spinner("..."): st.session_state.res_caa_url = gerar_pictograma_caa(api_key, conc); st.session_state.valid_caa = False
            if st.session_state.res_caa_url:
                st.image(st.session_state.res_caa_url)
                if st.session_state.valid_caa: st.success("Validado")
                else:
                    if st.button("✅", key="v4b"): st.session_state.valid_caa = True; st.rerun()
                    with st.expander("Refazer"):
                        fb = st.text_input("Ajuste", key="f4b")
                        if st.button("Refazer", key="br4b"): st.session_state.res_caa_url = gerar_pictograma_caa(api_key, conc, fb); st.rerun()

    st.markdown("---")
    st.markdown("### 🧩 Recursos DUA (Inclusão Global)")

    # 5. ROTEIRO
    with tabs[4]:
        st.markdown("<div class='pedagogia-box'>Plano de Aula Inclusivo.</div>", unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        tmp = c1.text_input("Tempo:", "50 min")
        comp = c2.text_input("Componente:", "História")
        tema = c3.text_input("Tema:", "Descobrimento")
        
        if st.button("📝 GERAR PLANO", type="primary"):
             st.session_state.res_roteiro = {'txt': gerar_plano_aula_completo(api_key, aluno, tmp, comp, tema), 'valid': False}
        
        if st.session_state.res_roteiro:
            res = st.session_state.res_roteiro
            if res['valid']: st.markdown("<div class='validado-box'>✅ APROVADO</div>", unsafe_allow_html=True)
            else:
                c_v, c_r = st.columns([1,2])
                if c_v.button("✅ Validar", key="v5"): st.session_state.res_roteiro['valid'] = True; st.rerun()
                with c_r.expander("🔄 Refazer"):
                    fb = st.text_input("Ajuste:", key="fb5")
                    if st.button("Refazer", key="br5"): 
                        st.session_state.res_roteiro = {'txt': gerar_plano_aula_completo(api_key, aluno, tmp, comp, tema, fb), 'valid': False}; st.rerun()
            st.markdown(res['txt'])

    # 6. PAPO DE MESTRE
    with tabs[5]:
        st.markdown("<div class='pedagogia-box'>Contextualização com Hiperfoco.</div>", unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        comp = c1.text_input("Componente:", key="pm1")
        ass = c2.text_input("Assunto:", key="pm2")
        hip = c3.text_input("Interesse/Hiperfoco:", value=aluno.get('hiperfoco',''), key="pm3")
        
        if st.button("🗣️ GERAR CONVERSA", type="primary"):
             st.session_state.res_papo = {'txt': gerar_contextualizacao(api_key, aluno, comp, ass, hip), 'valid': False}
        
        if st.session_state.res_papo:
            res = st.session_state.res_papo
            if res['valid']: st.markdown("<div class='validado-box'>✅ APROVADO</div>", unsafe_allow_html=True)
            else:
                c_v, c_r = st.columns([1,2])
                if c_v.button("✅ Validar", key="v6"): st.session_state.res_papo['valid'] = True; st.rerun()
                with c_r.expander("🔄 Refazer"):
                    fb = st.text_input("Ajuste:", key="fb6")
                    if st.button("Refazer", key="br6"): 
                        st.session_state.res_papo = {'txt': gerar_contextualizacao(api_key, aluno, comp, ass, hip, fb), 'valid': False}; st.rerun()
            st.markdown(res['txt'])

    # 7. DINAMICA
    with tabs[6]:
        st.markdown("<div class='pedagogia-box'>Dinâmica Inclusiva (Turma toda).</div>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        comp = c1.text_input("Componente:", key="d1")
        tema = c2.text_input("Tema:", key="d2")
        
        if st.button("🤝 GERAR DINÂMICA", type="primary"):
             st.session_state.res_dina = {'txt': gerar_dinamica_turma(api_key, aluno, comp, tema), 'valid': False}
        
        if st.session_state.res_dina:
            res = st.session_state.res_dina
            if res['valid']: st.markdown("<div class='validado-box'>✅ APROVADO</div>", unsafe_allow_html=True)
            else:
                c_v, c_r = st.columns([1,2])
                if c_v.button("✅ Validar", key="v7"): st.session_state.res_dina['valid'] = True; st.rerun()
                with c_r.expander("🔄 Refazer"):
                    fb = st.text_input("Ajuste:", key="fb7")
                    if st.button("Refazer", key="br7"): 
                        st.session_state.res_dina = {'txt': gerar_dinamica_turma(api_key, aluno, comp, tema, fb), 'valid': False}; st.rerun()
            st.markdown(res['txt'])
