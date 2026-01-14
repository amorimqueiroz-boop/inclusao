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
st.set_page_config(page_title="[TESTE] Omnisfera | Hub", page_icon="🚀", layout="wide")

# ==============================================================================
# ### BLOCO VISUAL INTELIGENTE: HEADER OMNISFERA & ALERTA DE TESTE ###
# ==============================================================================
import os
import base64
import streamlit as st

# 1. Detecção Automática de Ambiente (Via st.secrets)
try:
    IS_TEST_ENV = st.secrets.get("ENV") == "TESTE"
except:
    IS_TEST_ENV = False

# 2. Função para carregar a logo em Base64
def get_logo_base64():
    caminhos = ["omni_icone.png", "logo.png", "iconeaba.png"]
    for c in caminhos:
        if os.path.exists(c):
            with open(c, "rb") as f:
                return f"data:image/png;base64,{base64.b64encode(f.read()).decode()}"
    return "https://cdn-icons-png.flaticon.com/512/1183/1183672.png"

src_logo_giratoria = get_logo_base64()

# 3. Definição Dinâmica de Cores (Card Branco ou Amarelo)
if IS_TEST_ENV:
    # Amarelo Vibrante (Aviso de Teste)
    card_bg = "rgba(255, 220, 50, 0.95)" 
    card_border = "rgba(200, 160, 0, 0.5)"
else:
    # Branco Gelo Transparente (Original)
    card_bg = "rgba(255, 255, 255, 0.85)"
    card_border = "rgba(255, 255, 255, 0.6)"

# 4. Renderização do CSS Global e Header Flutuante
st.markdown(f"""
<style>
    
    /* -------------------------------------------- */

    /* CARD FLUTUANTE (OMNISFERA) */
    .omni-badge {{
        position: fixed;
        top: 15px; 
        right: 15px;
        
        /* COR DINÂMICA (Mudança aqui) */
        background: {card_bg};
        border: 1px solid {card_border};
        
        backdrop-filter: blur(8px);
        -webkit-backdrop-filter: blur(8px);
        
        /* Dimensões: Fino e Largo */
        padding: 4px 30px;
        min-width: 260px;
        justify-content: center;
        
        border-radius: 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08);
        z-index: 999990; /* Acima do conteúdo */
        display: flex;
        align-items: center;
        gap: 10px;
        pointer-events: none; /* Deixa passar clique se necessário */
    }}

    .omni-text {{
        font-family: 'Nunito', sans-serif;
        font-weight: 800;
        font-size: 0.9rem;
        color: #2D3748;
        letter-spacing: 1px;
        text-transform: uppercase;
    }}

    @keyframes spin-slow {{
        from {{ transform: rotate(0deg); }}
        to {{ transform: rotate(360deg); }}
    }}
    
    .omni-logo-spin {{
        height: 26px; width: 26px; 
        animation: spin-slow 10s linear infinite;
    }}

</style>

<div class="omni-badge">
    <img src="{src_logo_giratoria}" class="omni-logo-spin">
    <span class="omni-text">OMNISFERA</span>
</div>
""", unsafe_allow_html=True)
# ==============================================================================
# ### FIM BLOCO VISUAL INTELIGENTE ###
# ==============================================================================

def verificar_acesso():
    if "autenticado" not in st.session_state or not st.session_state["autenticado"]:
        st.error("🔒 Acesso Negado. Por favor, faça login na Página Inicial.")
        st.stop()
    
    st.markdown("""
        <style>
            footer {visibility: hidden !important;}
            [data-testid="stHeader"] {
                visibility: visible !important;
                background-color: transparent !important;
            }
            .block-container {padding-top: 2rem !important;}
        </style>
    """, unsafe_allow_html=True)

verificar_acesso()

# --- BARRA LATERAL COM NAVEGAÇÃO ---
with st.sidebar:
    try:
        st.image("ominisfera.png", width=150)
    except:
        st.write("🌐 OMNISFERA")
        
    st.markdown("---")
    if st.button("🏠 Voltar para Home", use_container_width=True):
        st.switch_page("Home.py")
    st.markdown("---")

# ==============================================================================
# 2. O CÓDIGO DO HUB DE INCLUSÃO
# ==============================================================================

# --- DADOS BLOOM ---
TAXONOMIA_BLOOM = {
    "1. Lembrar (Memorizar)": ["Citar", "Definir", "Identificar", "Listar", "Nomear", "Reconhecer", "Recordar", "Relacionar", "Repetir", "Sublinhar"],
    "2. Entender (Compreender)": ["Classificar", "Descrever", "Discutir", "Explicar", "Expressar", "Identificar", "Localizar", "Narrar", "Reafirmar", "Reportar", "Resumir", "Traduzir"],
    "3. Aplicar": ["Aplicar", "Demonstrar", "Dramatizar", "Empregar", "Esboçar", "Ilustrar", "Interpretar", "Operar", "Praticar", "Programar", "Usar"],
    "4. Analisar": ["Analisar", "Calcular", "Categorizar", "Comparar", "Contrastar", "Criticar", "Diferenciar", "Discriminar", "Distinguir", "Examinar", "Experimentar", "Testar"],
    "5. Avaliar": ["Argumentar", "Avaliar", "Defender", "Escolher", "Estimar", "Julgar", "Prever", "Selecionar", "Suportar", "Validar", "Valorizar"],
    "6. Criar": ["Compor", "Construir", "Criar", "Desenhar", "Desenvolver", "Formular", "Investigar", "Planejar", "Produzir", "Propor"]
}

# --- BANCO DE DADOS ---
ARQUIVO_DB = "banco_alunos.json"

def carregar_banco():
    # --- BLINDAGEM DE DADOS ---
    usuario_atual = st.session_state.get("usuario_nome", "")
    # --------------------------

    if os.path.exists(ARQUIVO_DB):
        try:
            with open(ARQUIVO_DB, "r", encoding="utf-8") as f:
                todos_alunos = json.load(f)
                # FILTRAGEM: Retorna apenas alunos deste usuário
                meus_alunos = [
                    aluno for aluno in todos_alunos 
                    if aluno.get('responsavel') == usuario_atual
                ]
                return meus_alunos
        except: return []
    return []

if 'banco_estudantes' not in st.session_state or not st.session_state.banco_estudantes:
    st.session_state.banco_estudantes = carregar_banco()

# --- ESTILO VISUAL (CSS) ---
st.markdown("""
    <style>
    html, body, [class*="css"] { font-family: 'Nunito', sans-serif; color: #2D3748; }
    
    .header-hub { 
        background: white; padding: 20px 30px; border-radius: 12px; 
        border-left: 6px solid #3182CE; box-shadow: 0 2px 4px rgba(0,0,0,0.05); 
        margin-bottom: 20px; display: flex; align-items: center; gap: 25px; 
    }
    
    .student-header { background-color: #EBF8FF; border: 1px solid #BEE3F8; border-radius: 12px; padding: 15px 25px; margin-bottom: 25px; display: flex; justify-content: space-between; align-items: center; }
    .student-label { font-size: 0.85rem; color: #718096; font-weight: 700; text-transform: uppercase; }
    .student-value { font-size: 1.1rem; color: #2C5282; font-weight: 800; }
    
    .analise-box { background-color: #F0FFF4; border: 1px solid #C6F6D5; border-radius: 8px; padding: 20px; margin-bottom: 20px; color: #22543D; }
    .analise-title { font-weight: bold; font-size: 1.1rem; margin-bottom: 10px; display: flex; align-items: center; gap: 8px; }
    
    .crop-instruction { background: #FFF5F5; border-left: 4px solid #F56565; padding: 15px; color: #C53030; border-radius: 4px; margin-bottom: 10px; font-weight: 600; }
    
    .validado-box { background-color: #C6F6D5; color: #22543D; padding: 15px; border-radius: 8px; text-align: center; font-weight: bold; margin-top: 15px; border: 1px solid #276749; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }

    /* Caixas de Explicação Pedagógica */
    .pedagogia-box { 
        background-color: #F7FAFC; border-left: 4px solid #3182CE; 
        padding: 15px; border-radius: 0 8px 8px 0; margin-bottom: 20px; 
        font-size: 0.9rem; color: #4A5568; 
    }
    .pedagogia-title { color: #2C5282; font-weight: 700; display: flex; align-items: center; gap: 8px; margin-bottom: 5px; }

    /* Abas */
    .stTabs [data-baseweb="tab-list"] { gap: 8px; flex-wrap: wrap; }
    .stTabs [data-baseweb="tab"] { border-radius: 6px; padding: 8px 16px; background-color: white; border: 1px solid #E2E8F0; font-size: 0.9rem; transition: all 0.2s; }
    .stTabs [aria-selected="true"] { background-color: #3182CE !important; color: white !important; border-color: #3182CE !important; }

    /* Botões */
    div[data-testid="column"] .stButton button[kind="primary"] { border-radius: 10px !important; height: 50px; width: 100%; background-color: #3182CE !important; color: white !important; font-weight: 800 !important; border: none; transition: 0.3s; }
    div[data-testid="column"] .stButton button[kind="primary"]:hover { background-color: #2B6CB0 !important; }
    
    div[data-testid="column"] .stButton button[kind="secondary"] { border-radius: 10px !important; height: 50px; width: 100%; border: 2px solid #CBD5E0 !important; color: #4A5568 !important; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# --- FUNÇÕES DE UTILIDADE ---

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
    url = f"https://api.unsplash.com/search/photos?query={query}&per_page=1&client_id={access_key}&lang=pt"
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

# --- IA FUNCTIONS (BLINDADAS CONTRA TEXTO) ---

def gerar_imagem_inteligente(api_key, prompt, unsplash_key=None, feedback_anterior="", prioridade="IA"):
    """
    prioridade: 'IA' (DALL-E) ou 'BANCO' (Unsplash).
    Lógica: Se prioridade='BANCO', tenta Unsplash. Se falhar ou prioridade='IA', usa DALL-E 3.
    """
    client = OpenAI(api_key=api_key)
    
    prompt_final = prompt
    if feedback_anterior:
        prompt_final = f"{prompt}. Adjustment requested: {feedback_anterior}"

    # 1. TENTATIVA BANCO DE IMAGENS (Se solicitado e configurado)
    if prioridade == "BANCO" and unsplash_key:
        termo = prompt.split('.')[0] if '.' in prompt else prompt
        url_banco = buscar_imagem_unsplash(termo, unsplash_key)
        if url_banco:
            return url_banco

    # 2. TENTATIVA IA (DALL-E 3) - BLINDAGEM AGRESSIVA CONTRA TEXTO
    try:
        # Prompt com TRAVA DE TEXTO ("STRICTLY NO TEXT")
        didactic_prompt = f"Educational textbook illustration, clean flat vector style, white background. CRITICAL RULE: STRICTLY NO TEXT, NO TYPOGRAPHY, NO ALPHABET, NO NUMBERS, NO LABELS inside the image. Just the visual representation of: {prompt_final}"
        resp = client.images.generate(model="dall-e-3", prompt=didactic_prompt, size="1024x1024", quality="standard", n=1)
        return resp.data[0].url
    except Exception as e:
        # Se IA falhar e não tentamos banco ainda, tenta agora como fallback
        if prioridade == "IA" and unsplash_key:
            termo = prompt.split('.')[0] if '.' in prompt else prompt
            return buscar_imagem_unsplash(termo, unsplash_key)
        return None

def gerar_pictograma_caa(api_key, conceito, feedback_anterior=""):
    """
    Gera símbolo específico para Comunicação Aumentativa e Alternativa.
    Estilo: PECS/ARASAAC (Fundo branco, traço preto grosso, alto contraste).
    """
    client = OpenAI(api_key=api_key)
    
    ajuste = f" CORREÇÃO PEDIDA: {feedback_anterior}" if feedback_anterior else ""
    
    # Prompt otimizado para Símbolos Mudos
    prompt_caa = f"""
    Create a COMMUNICATION SYMBOL (AAC/PECS) for the concept: '{conceito}'. {ajuste}
    STYLE GUIDE:
    - Flat vector icon (ARASAAC/Noun Project style).
    - Solid WHITE background.
    - Thick BLACK outlines.
    - High contrast primary colors.
    - No background details, no shadows.
    - CRITICAL MANDATORY RULE: MUTE IMAGE. NO TEXT. NO WORDS. NO LETTERS. NO NUMBERS. 
    - The image must be a purely visual symbol.
    """
    try:
        resp = client.images.generate(model="dall-e-3", prompt=prompt_caa, size="1024x1024", quality="standard", n=1)
        return resp.data[0].url
    except Exception as e: return None

def adaptar_conteudo_docx(api_key, aluno, texto, materia, tema, tipo_atv, remover_resp, questoes_mapeadas, modo_profundo=False):
    client = OpenAI(api_key=api_key)
    lista_q = ", ".join([str(n) for n in questoes_mapeadas])
    style = "Seja didático e use uma Cadeia de Pensamento para adaptar." if modo_profundo else "Seja objetivo."
    prompt = f"""
    ESPECIALISTA EM DUA E INCLUSÃO. {style}
    1. ANALISE O PERFIL: {aluno.get('ia_sugestao', '')[:1000]}
    2. ADAPTE A PROVA: Use o hiperfoco ({aluno.get('hiperfoco', 'Geral')}) em 30% das questões.
    REGRA SAGRADA DE IMAGEM: O professor indicou imagens nas questões: {lista_q}.
    Nessas questões, a estrutura OBRIGATÓRIA é: 1. Enunciado -> 2. [[IMG_número]] -> 3. Alternativas.
    
    SAÍDA OBRIGATÓRIA (Use EXATAMENTE este divisor):
    [ANÁLISE PEDAGÓGICA]
    ...análise...
    ---DIVISOR---
    [ATIVIDADE]
    ...atividade...
    
    CONTEXTO: {materia} | {tema}. {"REMOVA GABARITO." if remover_resp else ""}
    TEXTO ORIGINAL: {texto}
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
    if not imagem_bytes: return "Erro: Imagem vazia", ""
    b64 = base64.b64encode(imagem_bytes).decode('utf-8')
    instrucao_livro = "ATENÇÃO: IMAGEM COM RESPOSTAS. Remova todo gabarito/respostas." if livro_professor else ""
    style = "Faça uma análise crítica para melhor adaptação." if modo_profundo else "Transcreva e adapte."
    prompt = f"""
    ATUAR COMO: Especialista em Acessibilidade e OCR. {style}
    1. Transcreva o texto da imagem. {instrucao_livro}
    2. Adapte para o aluno (PEI: {aluno.get('ia_sugestao', '')[:800]}).
    3. Hiperfoco ({aluno.get('hiperfoco')}): Conecte levemente.
    4. REGRA DE OURO: Insira a tag [[IMG_1]] UMA ÚNICA VEZ, logo após o enunciado principal.
    
    SAÍDA OBRIGATÓRIA (Respeite o divisor):
    [ANÁLISE PEDAGÓGICA]
    ...análise...
    ---DIVISOR---
    [ATIVIDADE]
    ...atividade...
    """
    msgs = [{"role": "user", "content": [{"type": "text", "text": prompt}, {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}}]}]
    try:
        resp = client.chat.completions.create(model="gpt-4o-mini", messages=msgs, temperature=0.7 if modo_profundo else 0.4)
        full_text = resp.choices[0].message.content
        analise = "Análise indisponível."
        atividade = full_text
        if "---DIVISOR---" in full_text:
            parts = full_text.split("---DIVISOR---")
            analise = parts[0].replace("[ANÁLISE PEDAGÓGICA]", "").strip()
            atividade = parts[1].replace("[ATIVIDADE]", "").strip()
        atividade = garantir_tag_imagem(atividade)
        return analise, atividade
    except Exception as e: return str(e), ""

def criar_profissional(api_key, aluno, materia, objeto, qtd, tipo_q, qtd_imgs, verbos_bloom=None, modo_profundo=False):
    client = OpenAI(api_key=api_key)
    hiperfoco = aluno.get('hiperfoco', 'Geral')
    
    # Nova lógica de instrução de imagem e posição
    instrucao_img = f"Incluir imagens em {qtd_imgs} questões (use [[GEN_IMG: termo]]). REGRA DE POSIÇÃO: A tag da imagem ([[GEN_IMG: termo]]) DEVE vir logo APÓS o enunciado e ANTES das alternativas." if qtd_imgs > 0 else "Sem imagens."
    
    # Instrução de Bloom
    instrucao_bloom = ""
    if verbos_bloom:
        lista_verbos = ", ".join(verbos_bloom)
        instrucao_bloom = f"""
        6. TAXONOMIA DE BLOOM (RIGOROSO):
           - Utilize OBRIGATORIAMENTE os seguintes verbos de ação selecionados: {lista_verbos}.
           - Distribua esses verbos entre as questões criadas.
           - REGRA DE FORMATAÇÃO: O verbo de comando deve vir no início do enunciado, em **NEGRITO E CAIXA ALTA** (Ex: **ANALISE**, **IDENTIFIQUE**, **EXPLIQUE**).
           - Use apenas UM verbo de comando por questão.
        """

    style = "Atue como uma banca examinadora rigorosa." if modo_profundo else "Atue como professor elaborador."
    prompt = f"""
    {style}
    Crie prova de {materia} ({objeto}). QTD: {qtd} ({tipo_q}).
    DIRETRIZES: 
    1. Contexto Real. 
    2. Hiperfoco ({hiperfoco}) em 30%. 
    3. Distratores Inteligentes. 
    4. Imagens: {instrucao_img} (NUNCA repita a mesma imagem). 
    5. Divisão Clara.
    {instrucao_bloom}
    
    SAÍDA OBRIGATÓRIA:
    [ANÁLISE PEDAGÓGICA]
    ...análise...
    ---DIVISOR---
    [ATIVIDADE]
    ...questões...
    """
    try:
        resp = client.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "user", "content": prompt}], temperature=0.8 if modo_profundo else 0.6)
        full_text = resp.choices[0].message.content
        if "---DIVISOR---" in full_text:
            parts = full_text.split("---DIVISOR---")
            return parts[0].replace("[ANÁLISE PEDAGÓGICA]", "").strip(), parts[1].replace("[ATIVIDADE]", "").strip()
        return "Análise indisponível.", full_text
    except Exception as e: return str(e), ""

# --- NOVA FUNÇÃO: GERADOR DE EXPERIÊNCIA LÚDICA (EI - BNCC) ---
def gerar_experiencia_ei_bncc(api_key, aluno, campo_exp, objetivo, feedback_anterior=""):
    client = OpenAI(api_key=api_key)
    hiperfoco = aluno.get('hiperfoco', 'Brincar')
    
    ajuste_prompt = ""
    if feedback_anterior:
        ajuste_prompt = f"AJUSTE SOLICITADO PELO PROFESSOR: {feedback_anterior}. Refaça considerando isso."

    prompt = f"""
    ATUAR COMO: Especialista em Educação Infantil (BNCC) e Inclusão.
    ALUNO: {aluno['nome']} (Educação Infantil).
    HIPERFOCO: {hiperfoco}.
    RESUMO DAS NECESSIDADES (PEI): {aluno.get('ia_sugestao', '')[:600]}
    
    SUA MISSÃO: Criar uma EXPERIÊNCIA LÚDICA, CONCRETA E VISUAL focada no Campo de Experiência: "{campo_exp}".
    Objetivo Específico: {objetivo}
    {ajuste_prompt}
    
    REGRAS:
    1. Não crie "provas" ou "folhinhas". Crie VIVÊNCIAS.
    2. Use o hiperfoco para engajar (ex: se gosta de dinossauros, conte dinossauros).
    3. Liste materiais concretos (massinha, tinta, blocos).
    4. Dê o passo a passo para o professor.
    
    SAÍDA ESPERADA (Markdown):
    ## 🧸 Experiência: [Nome Criativo]
    **🎯 Intencionalidade:** ...
    **📦 Materiais:** ...
    **👣 Como Acontece:** ...
    **🎨 Adaptação para {aluno['nome'].split()[0]}:** ...
    """
    try:
        resp = client.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "user", "content": prompt}], temperature=0.7)
        return resp.choices[0].message.content
    except Exception as e: return str(e)

# --- UTILS (ROTEIRO, ETC) ---
def gerar_roteiro_aula(api_key, aluno, materia, assunto, feedback_anterior=""):
    client = OpenAI(api_key=api_key)
    ajuste = f"Ajuste com base neste feedback: {feedback_anterior}" if feedback_anterior else ""
    prompt = f"""
    Crie um Roteiro de Aula INDIVIDUALIZADO para {aluno['nome']}.
    Componente: {materia}. Assunto: {assunto}.
    PEI/Necessidades: {aluno.get('ia_sugestao','')[:500]}. 
    Hiperfoco para engajamento: {aluno.get('hiperfoco', 'Geral')}.
    {ajuste}
    
    Estrutura:
    1. Objetivo da Aula (Individual)
    2. Estratégia de Apresentação (Como conectar com o hiperfoco)
    3. Atividade Prática (Passo a passo adaptado)
    4. Verificação de Aprendizagem
    """
    try:
        resp = client.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "user", "content": prompt}], temperature=0.7)
        return resp.choices[0].message.content
    except Exception as e: return str(e)

def gerar_quebra_gelo_profundo(api_key, aluno, materia, assunto, hiperfoco, tema_turma_extra=""):
    client = OpenAI(api_key=api_key)
    prompt = f"""
    Crie 3 sugestões de 'Papo de Mestre' (Quebra-gelo/Introdução) para conectar o estudante {aluno['nome']} à aula.
    Matéria: {materia}. Assunto: {assunto}.
    Hiperfoco do aluno: {hiperfoco}.
    Tema de interesse da turma (DUA): {tema_turma_extra if tema_turma_extra else 'Não informado'}.
    
    O objetivo é usar o hiperfoco ou o interesse da turma como UMA PONTE (estratégia DUA de engajamento) para explicar o conceito de {assunto}.
    Seja criativo e profundo.
    """
    try:
        resp = client.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "user", "content": prompt}], temperature=0.8)
        return resp.choices[0].message.content
    except Exception as e: return str(e)

def gerar_dinamica_inclusiva(api_key, aluno, materia, assunto, qtd_alunos, caracteristicas_turma, feedback_anterior=""):
    client = OpenAI(api_key=api_key)
    ajuste = f"Refaça considerando: {feedback_anterior}" if feedback_anterior else ""
    prompt = f"""
    Crie uma Dinâmica de Grupo Inclusiva para {qtd_alunos} alunos.
    Matéria: {materia}. Tema: {assunto}.
    Aluno foco da inclusão: {aluno['nome']} (PEI: {aluno.get('ia_sugestao','')[:400]}).
    Características da turma: {caracteristicas_turma}.
    
    O objetivo é que TODOS participem, mas que a atividade valorize as potências de {aluno['nome']}.
    {ajuste}
    """
    try:
        resp = client.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "user", "content": prompt}], temperature=0.7)
        return resp.choices[0].message.content
    except Exception as e: return str(e)

def gerar_plano_aula_bncc(api_key, materia, assunto, metodologia, tecnica, qtd_alunos, recursos):
    client = OpenAI(api_key=api_key)
    prompt = f"""
    ATUAR COMO: Coordenador Pedagógico Especialista em BNCC e Metodologias Ativas.
    Crie um PLANO DE AULA detalhado.
    
    DADOS:
    - Componente: {materia}
    - Tema/Assunto: {assunto}
    - Metodologia: {metodologia} ({tecnica if tecnica else 'Padrão'})
    - Quantidade de Alunos: {qtd_alunos}
    - Recursos Disponíveis: {', '.join(recursos)}
    
    SAÍDA ESPERADA (Markdown):
    1. **Habilidades BNCC:** (Identifique os códigos alfanuméricos e descrições pertinentes ao tema).
    2. **Objetivos de Aprendizagem:**
    3. **Desenvolvimento (Passo a Passo):** Como a aula acontece usando a metodologia escolhida e os recursos marcados.
    4. **Adaptação/Diferenciação:** Sugestão geral para alunos com dificuldades.
    """
    try:
        resp = client.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "user", "content": prompt}], temperature=0.7)
        return resp.choices[0].message.content
    except Exception as e: return str(e)

def sugerir_imagem_pei(api_key, aluno):
    client = OpenAI(api_key=api_key)
    prompt = f"Prompt DALL-E para recurso visual: {aluno.get('ia_sugestao','')[:500]}."
    try:
        resp = client.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "user", "content": prompt}], temperature=0.7)
        return resp.choices[0].message.content
    except: return "Educational illustration"

# --- INTERFACE ---
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

# --- HEADER COM LOGO HUB E APENAS SUBTÍTULO ---

img_hub_html = get_img_tag("hub.png", "220") 

st.markdown(f"""
    <div class="header-hub">
        <div style="flex-shrink: 0;">
            {img_hub_html}
        </div>
        <div style="flex-grow: 1; text-align: center;">
            <p style="margin:0; color:#2C5282; font-size: 1.3rem; font-weight: 700;">
                Adaptação de Materiais & Criação
            </p>
        </div>
    </div>
""", unsafe_allow_html=True)


if not st.session_state.banco_estudantes:
    st.warning("⚠️ Nenhum aluno encontrado para o seu usuário. Cadastre no módulo PEI primeiro.")
    st.stop()

lista = [a['nome'] for a in st.session_state.banco_estudantes]
nome_aluno = st.selectbox("📂 Selecione o Estudante:", lista)
aluno = next(a for a in st.session_state.banco_estudantes if a['nome'] == nome_aluno)

# --- DETECTOR DE EDUCAÇÃO INFANTIL ---
serie_aluno = aluno.get('serie', '').lower()
is_ei = "infantil" in serie_aluno or "creche" in serie_aluno or "pré" in serie_aluno

st.markdown(f"""
    <div class="student-header">
        <div class="student-info-item"><div class="student-label">Nome</div><div class="student-value">{aluno.get('nome')}</div></div>
        <div class="student-info-item"><div class="student-label">Série</div><div class="student-value">{aluno.get('serie', '-')}</div></div>
        <div class="student-info-item"><div class="student-label">Hiperfoco</div><div class="student-value">{aluno.get('hiperfoco', '-')}</div></div>
    </div>
""", unsafe_allow_html=True)

# === INICIALIZAÇÃO DE ESTADO PARA IMAGENS ===
if 'res_scene_url' not in st.session_state: st.session_state.res_scene_url = None
if 'valid_scene' not in st.session_state: st.session_state.valid_scene = False
if 'res_caa_url' not in st.session_state: st.session_state.res_caa_url = None
if 'valid_caa' not in st.session_state: st.session_state.valid_caa = False

if is_ei:
    # === MODO EDUCAÇÃO INFANTIL (ABAS ESPECIAIS) ===
    st.info("🧸 **Modo Educação Infantil Ativado:** Foco em Experiências, BNCC e Brincar.")
    
    tabs = st.tabs(["🧸 Criar Experiência (BNCC)", "🎨 Estúdio Visual & CAA", "📝 Rotina & AVD", "🤝 Inclusão no Brincar"])
    
    # 1. CRIAR EXPERIÊNCIA
    with tabs[0]:
        st.markdown("""
        <div class="pedagogia-box">
            <div class="pedagogia-title"><i class="ri-lightbulb-line"></i> Pedagogia do Brincar (BNCC)</div>
            Na Educação Infantil, não fazemos "provas". Criamos <strong>experiências de aprendizagem</strong> intencionais. 
            Esta ferramenta usa a BNCC para criar brincadeiras que ensinam, usando o hiperfoco da criança.
        </div>
        """, unsafe_allow_html=True)
        
        col_ei1, col_ei2 = st.columns(2)
        campo_exp = col_ei1.selectbox("Campo de Experiência (BNCC)", [
            "O eu, o outro e o nós",
            "Corpo, gestos e movimentos",
            "Traços, sons, cores e formas",
            "Escuta, fala, pensamento e imaginação",
            "Espaços, tempos, quantidades, relações e transformações"
        ])
        obj_aprendizagem = col_ei2.text_input("Objetivo de Aprendizagem:", placeholder="Ex: Compartilhar brinquedos, Identificar cores...")
        
        if 'res_ei_exp' not in st.session_state: st.session_state.res_ei_exp = None
        if 'valid_ei_exp' not in st.session_state: st.session_state.valid_ei_exp = False

        if st.button("✨ GERAR EXPERIÊNCIA LÚDICA", type="primary"):
            with st.spinner("Criando vivência..."):
                st.session_state.res_ei_exp = gerar_experiencia_ei_bncc(api_key, aluno, campo_exp=campo_exp, objetivo=obj_aprendizagem)
                st.session_state.valid_ei_exp = False

        if st.session_state.res_ei_exp:
            if st.session_state.valid_ei_exp:
                st.markdown("<div class='validado-box'>✅ EXPERIÊNCIA APROVADA!</div>", unsafe_allow_html=True)
                st.markdown(st.session_state.res_ei_exp)
            else:
                st.markdown(st.session_state.res_ei_exp)
                st.write("---")
                c_val, c_ref = st.columns([1, 3])
                if c_val.button("✅ Validar Experiência"): 
                    st.session_state.valid_ei_exp = True
                    st.rerun()
                with c_ref.expander("🔄 Não gostou? Ensinar a IA"):
                    feedback_ei = st.text_input("O que precisa melhorar?", placeholder="Ex: Ficou muito complexo, use materiais mais simples...")
                    if st.button("Refazer com Ajustes"):
                        with st.spinner("Reescrevendo..."):
                            st.session_state.res_ei_exp = gerar_experiencia_ei_bncc(api_key, aluno, campo_exp, obj_aprendizagem, feedback_anterior=feedback_ei)
                            st.rerun()

    # 2. ESTÚDIO VISUAL (ATUALIZADO COM FEEDBACK)
    with tabs[1]:
        st.markdown("""
        <div class="pedagogia-box">
            <div class="pedagogia-title"><i class="ri-eye-line"></i> Apoio Visual & Comunicação</div>
            Crianças atípicas processam melhor imagens do que fala. 
            Use <strong>Cenas</strong> para histórias sociais (comportamento) e <strong>Pictogramas (CAA)</strong> para comunicação.
        </div>
        """, unsafe_allow_html=True)
        
        col_scene, col_caa = st.columns(2)
        
        # --- COLUNA 1: CENAS ---
        with col_scene:
            st.markdown("#### 🖼️ Ilustração de Cena")
            desc_m = st.text_area("Descreva a cena ou rotina:", height=100, key="vdm_ei", placeholder="Ex: Crianças brincando de roda no parque...")
            
            if st.button("🎨 Gerar Cena", key="btn_cena_ei"):
                with st.spinner("Desenhando..."):
                    prompt_completo = f"{desc_m}. Context: Child education, friendly style."
                    # Prioridade IA (DALL-E)
                    st.session_state.res_scene_url = gerar_imagem_inteligente(api_key, prompt_completo, unsplash_key, prioridade="IA")
                    st.session_state.valid_scene = False

            # Exibição Cena
            if st.session_state.res_scene_url:
                st.image(st.session_state.res_scene_url)
                if st.session_state.valid_scene:
                    st.success("Imagem validada!")
                else:
                    c_vs1, c_vs2 = st.columns([1, 2])
                    if c_vs1.button("✅ Validar", key="val_sc_ei"): st.session_state.valid_scene = True; st.rerun()
                    with c_vs2.expander("🔄 Refazer Cena"):
                        fb_scene = st.text_input("Ajuste:", key="fb_sc_ei")
                        if st.button("Refazer", key="ref_sc_ei"):
                            with st.spinner("Redesenhando..."):
                                prompt_completo = f"{desc_m}. Context: Child education."
                                st.session_state.res_scene_url = gerar_imagem_inteligente(api_key, prompt_completo, unsplash_key, feedback_anterior=fb_scene, prioridade="IA")
                                st.rerun()

        # --- COLUNA 2: CAA ---
        with col_caa:
            st.markdown("#### 🗣️ Símbolo CAA (Comunicação)")
            palavra_chave = st.text_input("Conceito/Palavra:", placeholder="Ex: Quero Água, Banheiro", key="caa_input")
            
            if st.button("🧩 Gerar Pictograma", key="btn_caa"):
                with st.spinner("Criando símbolo acessível..."):
                    st.session_state.res_caa_url = gerar_pictograma_caa(api_key, palavra_chave)
                    st.session_state.valid_caa = False

            # Exibição CAA
            if st.session_state.res_caa_url:
                st.image(st.session_state.res_caa_url, width=300)
                if st.session_state.valid_caa:
                    st.success("Pictograma validado!")
                else:
                    c_vc1, c_vc2 = st.columns([1, 2])
                    if c_vc1.button("✅ Validar", key="val_caa_ei"): st.session_state.valid_caa = True; st.rerun()
                    with c_vc2.expander("🔄 Refazer Picto"):
                        fb_caa = st.text_input("Ajuste:", key="fb_caa_ei")
                        if st.button("Refazer", key="ref_caa_ei"):
                            with st.spinner("Recriando..."):
                                st.session_state.res_caa_url = gerar_pictograma_caa(api_key, palavra_chave, feedback_anterior=fb_caa)
                                st.rerun()

    # 3. ROTINA
    with tabs[2]:
        st.markdown("""
        <div class="pedagogia-box">
            <div class="pedagogia-title"><i class="ri-calendar-check-line"></i> Rotina & Previsibilidade</div>
            A rotina organiza o pensamento da criança. Use esta ferramenta para identificar 
            pontos de estresse e criar estratégias de antecipação.
        </div>
        """, unsafe_allow_html=True)
        
        rotina_detalhada = st.text_area("Descreva a Rotina da Turma:", height=200, placeholder="Ex: \n8:00 - Chegada e Acolhida\n8:30 - Roda de Conversa\n9:00 - Lanche\n...")
        topico_foco = st.text_input("Ponto de Atenção (Opcional):", placeholder="Ex: Transição para o parque")
        
        if 'res_ei_rotina' not in st.session_state: st.session_state.res_ei_rotina = None
        if 'valid_ei_rotina' not in st.session_state: st.session_state.valid_ei_rotina = False

        if st.button("📝 ANALISAR E ADAPTAR ROTINA", type="primary"):
            with st.spinner("Analisando rotina..."):
                prompt_rotina = f"Analise esta rotina de Educação Infantil e sugira adaptações sensoriais e visuais:\n\n{rotina_detalhada}\n\nFoco específico: {topico_foco}"
                st.session_state.res_ei_rotina = gerar_roteiro_aula(api_key, aluno, "Geral", "Rotina", feedback_anterior=prompt_rotina) # Adaptação simples para usar função existente
                st.session_state.valid_ei_rotina = False

        if st.session_state.res_ei_rotina:
            if st.session_state.valid_ei_rotina:
                st.markdown("<div class='validado-box'>✅ ROTINA VALIDADA!</div>", unsafe_allow_html=True)
                st.markdown(st.session_state.res_ei_rotina)
            else:
                st.markdown(st.session_state.res_ei_rotina)
                st.write("---")
                c_val, c_ref = st.columns([1, 3])
                if c_val.button("✅ Validar Rotina"): st.session_state.valid_ei_rotina = True; st.rerun()
                with c_ref.expander("🔄 Refazer adaptação"):
                    fb_rotina = st.text_input("O que ajustar na rotina?", key="fb_rotina_input")
                    if st.button("Refazer Rotina"):
                        with st.spinner("Reajustando..."):
                            prompt_rotina = f"Analise esta rotina de Educação Infantil e sugira adaptações:\n\n{rotina_detalhada}\n\nFoco: {topico_foco}"
                            st.session_state.res_ei_rotina = gerar_roteiro_aula(api_key, aluno, "Geral", "Rotina", feedback_anterior=prompt_rotina)
                            st.rerun()

    # 4. INCLUSÃO NO BRINCAR
    with tabs[3]:
        st.markdown("""
        <div class="pedagogia-box">
            <div class="pedagogia-title"><i class="ri-group-line"></i> Mediação Social</div>
            Se a criança brinca isolada, o objetivo não é forçar a interação, mas criar 
            pontes através do interesse dela. A IA criará uma brincadeira onde ela é protagonista.
        </div>
        """, unsafe_allow_html=True)
        
        tema_d = st.text_input("Tema/Momento:", key="dina_ei", placeholder="Ex: Brincadeira de massinha")
        if 'res_ei_dina' not in st.session_state: st.session_state.res_ei_dina = None
        if 'valid_ei_dina' not in st.session_state: st.session_state.valid_ei_dina = False

        if st.button("🤝 GERAR DINÂMICA", type="primary"): 
            with st.spinner("Criando ponte social..."):
                # Adaptação para usar função existente
                st.session_state.res_ei_dina = gerar_dinamica_inclusiva(api_key, aluno, "Educação Infantil", tema_d, "pequeno grupo", "Crianças pequenas")
                st.session_state.valid_ei_dina = False

        if st.session_state.res_ei_dina:
            if st.session_state.valid_ei_dina:
                st.markdown("<div class='validado-box'>✅ DINÂMICA VALIDADA!</div>", unsafe_allow_html=True)
                st.markdown(st.session_state.res_ei_dina)
            else:
                st.markdown(st.session_state.res_ei_dina)
                st.write("---")
                c_val, c_ref = st.columns([1, 3])
                if c_val.button("✅ Validar Dinâmica"): st.session_state.valid_ei_dina = True; st.rerun()
                with c_ref.expander("🔄 Refazer dinâmica"):
                    fb_dina = st.text_input("O que ajustar?", key="fb_dina_input")
                    if st.button("Refazer Dinâmica"):
                        with st.spinner("Reajustando..."):
                            st.session_state.res_ei_dina = gerar_dinamica_inclusiva(api_key, aluno, "Educação Infantil", tema_d, "pequeno grupo", "Crianças pequenas", feedback_anterior=fb_dina)
                            st.rerun()

else:
    # === MODO PADRÃO (FUNDAMENTAL / MÉDIO) ===
    # AQUI ESTÃO AS NOVAS ABAS SOLICITADAS: Roteiro Individual, Papo de Mestre, Dinâmica, Plano de Aula
    tabs = st.tabs(["📄 Adaptar Prova", "✂️ Adaptar Atividade", "✨ Criar do Zero", "🎨 Estúdio Visual & CAA", "📝 Roteiro Individual", "🗣️ Papo de Mestre", "🤝 Dinâmica Inclusiva", "📅 Plano de Aula (BNCC)"])

    # 1. ADAPTAR PROVA
    with tabs[0]:
        st.markdown("""
        <div class="pedagogia-box">
            <div class="pedagogia-title"><i class="ri-file-edit-line"></i> Adaptação Curricular (DUA)</div>
            Transforme provas padrão em avaliações acessíveis. O sistema simplifica enunciados, 
            insere imagens de apoio e ajusta o layout para reduzir a carga cognitiva.
        </div>
        """, unsafe_allow_html=True)
        
        c1, c2, c3 = st.columns(3)
        materia_d = c1.selectbox("Matéria", ["Matemática", "Português", "Ciências", "História", "Geografia", "Artes", "Ed. Física", "Inglês"], key="dm")
        tema_d = c2.text_input("Tema", placeholder="Ex: Frações", key="dt")
        tipo_d = c3.selectbox("Tipo", ["Prova", "Tarefa"], key="dtp")
        arquivo_d = st.file_uploader("Upload DOCX", type=["docx"], key="fd")
        
        if 'docx_imgs' not in st.session_state: st.session_state.docx_imgs = []
        if 'docx_txt' not in st.session_state: st.session_state.docx_txt = None
        
        if arquivo_d and arquivo_d.file_id != st.session_state.get('last_d'):
            st.session_state.last_d = arquivo_d.file_id
            txt, imgs = extrair_dados_docx(arquivo_d)
            st.session_state.docx_txt = txt; st.session_state.docx_imgs = imgs
            st.success(f"{len(imgs)} imagens encontradas.")

        map_d = {}; qs_d = []
        if st.session_state.docx_imgs:
            st.write("### Mapeamento")
            cols = st.columns(3)
            for i, img in enumerate(st.session_state.docx_imgs):
                with cols[i % 3]:
                    st.image(img, width=80)
                    q = st.number_input(f"Questão:", 0, 50, key=f"dq_{i}")
                    if q > 0: map_d[int(q)] = img; qs_d.append(int(q))

        if st.button("🚀 ADAPTAR PROVA", type="primary", key="btn_d"):
            if not st.session_state.docx_txt: st.warning("Envie arquivo."); st.stop()
            with st.spinner("Analisando e Adaptando..."):
                rac, txt = adaptar_conteudo_docx(api_key, aluno, st.session_state.docx_txt, materia_d, tema_d, tipo_d, True, qs_d)
                st.session_state['res_docx'] = {'rac': rac, 'txt': txt, 'map': map_d, 'valid': False}
                st.rerun()

        if 'res_docx' in st.session_state:
            res = st.session_state['res_docx']
            if res.get('valid'):
                st.markdown("<div class='validado-box'>✅ VALIDADO!</div>", unsafe_allow_html=True)
            else:
                col_v, col_r = st.columns([1, 1])
                if col_v.button("✅ Validar", key="val_d"): st.session_state['res_docx']['valid'] = True; st.rerun()
                if col_r.button("🧠 Refazer (+Profundo)", key="redo_d"):
                    with st.spinner("Refazendo..."):
                        rac, txt = adaptar_conteudo_docx(api_key, aluno, st.session_state.docx_txt, materia_d, tema_d, tipo_d, True, qs_d, modo_profundo=True)
                        st.session_state['res_docx'] = {'rac': rac, 'txt': txt, 'map': map_d, 'valid': False}
                        st.rerun()

            st.markdown(f"<div class='analise-box'><div class='analise-title'>🧠 Análise Pedagógica</div>{res['rac']}</div>", unsafe_allow_html=True)
            with st.container(border=True):
                partes = re.split(r'(\[\[IMG.*?\d+\]\])', res['txt'], flags=re.IGNORECASE)
                for p in partes:
                    if "IMG" in p.upper() and re.search(r'\d+', p):
                        num = int(re.search(r'\d+', p).group(0))
                        im = res['map'].get(num)
                        if im: st.image(im, width=300)
                    elif p.strip(): st.markdown(p.strip())
            docx = construir_docx_final(res['txt'], aluno, materia_d, res['map'], None, tipo_d)
            st.download_button("📥 BAIXAR DOCX (Só Atividade)", docx, "Prova_Adaptada.docx", "primary")

    # 2. ADAPTAR ATIVIDADE
    with tabs[1]:
        st.markdown("""
        <div class="pedagogia-box">
            <div class="pedagogia-title"><i class="ri-scissors-cut-line"></i> OCR & Adaptação Visual</div>
            Tire foto de uma atividade do livro ou caderno. A IA extrai o texto, 
            remove poluição visual e reestrutura o conteúdo para o nível do aluno.
        </div>
        """, unsafe_allow_html=True)
        
        c1, c2, c3 = st.columns(3)
        discip = ["Matemática", "Português", "Ciências", "História", "Geografia", "Artes", "Ed. Física", "Inglês", "Filosofia", "Sociologia"]
        materia_i = c1.selectbox("Matéria", discip, key="im")
        tema_i = c2.text_input("Tema", key="it")
        tipo_i = c3.selectbox("Tipo", ["Atividade", "Tarefa"], key="itp")
        arquivo_i = st.file_uploader("Upload", type=["png","jpg","jpeg"], key="fi")
        livro_prof = st.checkbox("📖 Livro do Professor (Remover Respostas)", value=False)
        
        if 'img_raw' not in st.session_state: st.session_state.img_raw = None
        if arquivo_i and arquivo_i.file_id != st.session_state.get('last_i'):
            st.session_state.last_i = arquivo_i.file_id
            st.session_state.img_raw = sanitizar_imagem(arquivo_i.getvalue())

        cropped_res = None
        if st.session_state.img_raw:
            st.markdown("### ✂️ Recorte")
            img_pil = Image.open(BytesIO(st.session_state.img_raw))
            img_pil.thumbnail((800, 800))
            cropped_res = st_cropper(img_pil, realtime_update=True, box_color='#FF0000', aspect_ratio=None, key="crop_i")
            if cropped_res: st.image(cropped_res, width=200, caption="Prévia")

        if st.button("🚀 ADAPTAR ATIVIDADE", type="primary", key="btn_i"):
            if not st.session_state.img_raw: st.warning("Envie imagem."); st.stop()
            with st.spinner("Analisando e Adaptando..."):
                buf_c = BytesIO()
                cropped_res.convert('RGB').save(buf_c, format="JPEG", quality=90)
                img_bytes = buf_c.getvalue()
                rac, txt = adaptar_conteudo_imagem(api_key, aluno, img_bytes, materia_i, tema_i, tipo_i, livro_prof)
                st.session_state['res_img'] = {'rac': rac, 'txt': txt, 'map': {1: img_bytes}, 'valid': False}
                st.rerun()

        if 'res_img' in st.session_state:
            res = st.session_state['res_img']
            if res.get('valid'):
                st.markdown("<div class='validado-box'>✅ VALIDADO!</div>", unsafe_allow_html=True)
            else:
                col_v, col_r = st.columns([1, 1])
                if col_v.button("✅ Validar", key="val_i"): st.session_state['res_img']['valid'] = True; st.rerun()
                if col_r.button("🧠 Refazer (+Profundo)", key="redo_i"):
                    with st.spinner("Refazendo..."):
                        img_bytes = res['map'][1]
                        rac, txt = adaptar_conteudo_imagem(api_key, aluno, img_bytes, materia_i, tema_i, tipo_i, livro_prof, modo_profundo=True)
                        st.session_state['res_img'] = {'rac': rac, 'txt': txt, 'map': {1: img_bytes}, 'valid': False}
                        st.rerun()

            st.markdown(f"<div class='analise-box'><div class='analise-title'>🧠 Análise Pedagógica</div>{res['rac']}</div>", unsafe_allow_html=True)
            with st.container(border=True):
                partes = re.split(r'(\[\[IMG.*?\]\])', res['txt'], flags=re.IGNORECASE)
                for p in partes:
                    if "IMG" in p.upper():
                        im = res['map'].get(1)
                        if im: st.image(im, width=300)
                    elif p.strip(): st.markdown(p.strip())
            docx = construir_docx_final(res['txt'], aluno, materia_i, res['map'], None, tipo_i)
            st.download_button("📥 BAIXAR DOCX (Só Atividade)", docx, "Atividade.docx", "primary")

    # 3. CRIAR DO ZERO
    with tabs[2]:
        st.markdown("""
        <div class="pedagogia-box">
            <div class="pedagogia-title"><i class="ri-magic-line"></i> Criação com DUA</div>
            Crie atividades do zero alinhadas ao PEI. A IA gera questões contextualizadas, 
            usa o hiperfoco para engajamento e cria imagens ilustrativas automaticamente.
        </div>
        """, unsafe_allow_html=True)
        
        cc1, cc2 = st.columns(2)
        mat_c = cc1.selectbox("Componente", discip, key="cm")
        obj_c = cc2.text_input("Assunto", key="co")
        
        cc3, cc4 = st.columns(2)
        qtd_c = cc3.slider("Qtd Questões", 1, 10, 5, key="cq")
        tipo_quest = cc4.selectbox("Tipo", ["Objetiva", "Discursiva", "Mista"], key="ctq")
        
        col_img_opt, col_img_pct = st.columns([1, 2])
        usar_img = col_img_opt.checkbox("📸 Incluir Imagens?", value=True)
        
        # MUDANÇA: Slider numérico (0 até Qtd Questões)
        qtd_img_sel = col_img_pct.slider("Quantas questões terão imagens?", 0, qtd_c, int(qtd_c/2), disabled=not usar_img)
        
        # --- BLOOM SECTION ---
        st.write("---")
        st.markdown("#### 🧠 Intencionalidade Pedagógica (Taxonomia de Bloom)")
        usar_bloom = st.checkbox("🎯 Usar Taxonomia de Bloom (Revisada)")
        
        # Inicializa memória de seleção no session state se não existir
        if 'bloom_memoria' not in st.session_state:
            st.session_state.bloom_memoria = {cat: [] for cat in TAXONOMIA_BLOOM.keys()}

        verbos_finais_para_ia = []

        if usar_bloom:
            col_b1, col_b2 = st.columns(2)
            
            # 1. Seleciona a Categoria (Gaveta)
            cat_atual = col_b1.selectbox("Categoria Cognitiva:", list(TAXONOMIA_BLOOM.keys()))
            
            # 2. Mostra Multiselect apenas para essa categoria, carregando o que já estava na memória
            selecao_atual = col_b2.multiselect(
                f"Verbos de '{cat_atual}':", 
                TAXONOMIA_BLOOM[cat_atual],
                default=st.session_state.bloom_memoria[cat_atual],
                key=f"ms_bloom_{cat_atual}" # Chave única para o widget
            )
            
            # 3. Atualiza a memória com o que o usuário acabou de mexer
            st.session_state.bloom_memoria[cat_atual] = selecao_atual
            
            # 4. Agrega tudo para mostrar ao usuário e enviar para a IA
            for cat in st.session_state.bloom_memoria:
                verbos_finais_para_ia.extend(st.session_state.bloom_memoria[cat])
            
            if verbos_finais_para_ia:
                st.info(f"**Verbos Tagueados (Total):** {', '.join(verbos_finais_para_ia)}")
            else:
                st.caption("Nenhum verbo selecionado ainda.")
        # ---------------------

        if st.button("✨ CRIAR ATIVIDADE", type="primary", key="btn_c"):
            with st.spinner("Elaborando..."):
                qtd_final = qtd_img_sel if usar_img else 0
                
                # Passamos a lista agregada 'verbos_finais_para_ia'
                rac, txt = criar_profissional(api_key, aluno, mat_c, obj_c, qtd_c, tipo_quest, qtd_final, verbos_bloom=verbos_finais_para_ia if usar_bloom else None)
                
                novo_map = {}; count = 0
                tags = re.findall(r'\[\[GEN_IMG: (.*?)\]\]', txt)
                for p in tags:
                    count += 1
                    # MUDANÇA: Prioridade BANCO, depois IA
                    url = gerar_imagem_inteligente(api_key, p, unsplash_key, prioridade="BANCO")
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
                col_v, col_r = st.columns([1, 1])
                if col_v.button("✅ Validar", key="val_c"): st.session_state['res_create']['valid'] = True; st.rerun()
                if col_r.button("🧠 Refazer (+Profundo)", key="redo_c"):
                    with st.spinner("Refazendo..."):
                        qtd_final = qtd_img_sel if usar_img else 0
                        # Mesmo aqui, passamos a lista agregada atualizada
                        verbos_profundos = []
                        if usar_bloom:
                             for cat in st.session_state.bloom_memoria:
                                verbos_profundos.extend(st.session_state.bloom_memoria[cat])

                        rac, txt = criar_profissional(api_key, aluno, mat_c, obj_c, qtd_c, tipo_quest, qtd_final, verbos_bloom=verbos_profundos if usar_bloom else None, modo_profundo=True)
                        st.session_state['res_create']['rac'] = rac
                        st.session_state['res_create']['txt'] = txt
                        st.session_state['res_create']['valid'] = False
                        st.rerun()

            st.markdown(f"<div class='analise-box'><div class='analise-title'>🧠 Análise Pedagógica</div>{res['rac']}</div>", unsafe_allow_html=True)
            with st.container(border=True):
                partes = re.split(r'(\[\[IMG_G\d+\]\])', res['txt'])
                for p in partes:
                    tag = re.search(r'\[\[IMG_G(\d+)\]\]', p)
                    if tag:
                        i = int(tag.group(1))
                        im = res['map'].get(i)
                        if im: st.image(im, width=300)
                    elif p.strip(): st.markdown(p.strip())
            
            c_down1, c_down2 = st.columns(2)
            docx = construir_docx_final(res['txt'], aluno, mat_c, {}, None, "Criada")
            c_down1.download_button("📥 DOCX", docx, "Criada.docx", "primary")
            docx_clean = construir_docx_final(res['txt'], aluno, mat_c, {}, None, "Criada", sem_cabecalho=True)
            c_down2.download_button("📥 DOCX (Sem Cabeçalho)", docx_clean, "Criada_Clean.docx", "secondary")

    # 4. ESTÚDIO VISUAL (ATUALIZADO COM FEEDBACK)
    with tabs[3]:
        st.markdown("""
        <div class="pedagogia-box">
            <div class="pedagogia-title"><i class="ri-image-line"></i> Recursos Visuais</div>
            Gere flashcards, rotinas visuais e símbolos de comunicação.
        </div>
        """, unsafe_allow_html=True)
        
        col_scene, col_caa = st.columns(2)
        
        with col_scene:
            st.markdown("#### 🖼️ Ilustração")
            desc_m = st.text_area("Descreva a imagem:", height=100, key="vdm_padrao", placeholder="Ex: Sistema Solar simplificado com planetas coloridos...")
            
            if st.button("🎨 Gerar Imagem", key="btn_cena_padrao"):
                with st.spinner("Desenhando..."):
                    prompt_completo = f"{desc_m}. Context: Education."
                    # Prioridade IA (DALL-E)
                    st.session_state.res_scene_url = gerar_imagem_inteligente(api_key, prompt_completo, unsplash_key, prioridade="IA")
                    st.session_state.valid_scene = False

            if st.session_state.res_scene_url:
                st.image(st.session_state.res_scene_url)
                if st.session_state.valid_scene:
                    st.success("Imagem validada!")
                else:
                    c_vs1, c_vs2 = st.columns([1, 2])
                    if c_vs1.button("✅ Validar", key="val_sc_pd"): st.session_state.valid_scene = True; st.rerun()
                    with c_vs2.expander("🔄 Refazer Cena"):
                        fb_scene = st.text_input("Ajuste:", key="fb_sc_pd")
                        if st.button("Refazer", key="ref_sc_pd"):
                            with st.spinner("Redesenhando..."):
                                prompt_completo = f"{desc_m}. Context: Education."
                                st.session_state.res_scene_url = gerar_imagem_inteligente(api_key, prompt_completo, unsplash_key, feedback_anterior=fb_scene, prioridade="IA")
                                st.rerun()

        with col_caa:
            st.markdown("#### 🗣️ Símbolo CAA")
            palavra_chave = st.text_input("Conceito:", placeholder="Ex: Silêncio", key="caa_input_padrao")
            
            if st.button("🧩 Gerar Pictograma", key="btn_caa_padrao"):
                with st.spinner("Criando símbolo..."):
                    st.session_state.res_caa_url = gerar_pictograma_caa(api_key, palavra_chave)
                    st.session_state.valid_caa = False

            if st.session_state.res_caa_url:
                st.image(st.session_state.res_caa_url, width=300)
                if st.session_state.valid_caa:
                    st.success("Pictograma validado!")
                else:
                    c_vc1, c_vc2 = st.columns([1, 2])
                    if c_vc1.button("✅ Validar", key="val_caa_pd"): st.session_state.valid_caa = True; st.rerun()
                    with c_vc2.expander("🔄 Refazer Picto"):
                        fb_caa = st.text_input("Ajuste:", key="fb_caa_pd")
                        if st.button("Refazer", key="ref_caa_pd"):
                            with st.spinner("Recriando..."):
                                st.session_state.res_caa_url = gerar_pictograma_caa(api_key, palavra_chave, feedback_anterior=fb_caa)
                                st.rerun()

    # 5. ROTEIRO DE AULA INDIVIDUAL
    with tabs[4]:
        st.markdown("""
        <div class="pedagogia-box">
            <div class="pedagogia-title"><i class="ri-user-follow-line"></i> Roteiro de Aula Individualizado</div>
            Crie um passo a passo de aula <strong>específico para este estudante</strong> do PEI. 
            A IA usará o hiperfoco como chave de acesso para o conteúdo.
        </div>
        """, unsafe_allow_html=True)
        
        c1, c2 = st.columns(2)
        materia_rotina = c1.selectbox("Componente Curricular", discip, key="rot_materia")
        tema_rotina = c2.text_input("Assunto/Tema da Aula:", key="rot_tema", placeholder="Ex: Ciclo da Água")
        
        if st.button("📝 GERAR ROTEIRO INDIVIDUAL", type="primary"): 
            if tema_rotina:
                st.markdown(gerar_roteiro_aula(api_key, aluno, materia_rotina, tema_rotina))
            else:
                st.warning("Preencha o Assunto/Tema.")

    # 6. PAPO DE MESTRE (QUEBRA-GELO DUA)
    with tabs[5]:
        st.markdown("""
        <div class="pedagogia-box">
            <div class="pedagogia-title"><i class="ri-chat-smile-2-line"></i> Engajamento & DUA (Papo de Mestre)</div>
            O hiperfoco é um <strong>caminho neurológico</strong> já aberto. Use-o para conectar o aluno à matéria.
            Aqui você também pode adicionar um tema de interesse da turma toda (DUA) para criar conexões coletivas.
        </div>
        """, unsafe_allow_html=True)
        
        c1, c2 = st.columns(2)
        materia_papo = c1.selectbox("Componente", discip, key="papo_mat")
        assunto_papo = c2.text_input("Assunto da Aula:", key="papo_ass")
        
        c3, c4 = st.columns(2)
        hiperfoco_papo = c3.text_input("Hiperfoco (Aluno):", value=aluno.get('hiperfoco', 'Geral'), key="papo_hip")
        tema_turma = c4.text_input("Interesse da Turma (Opcional - DUA):", placeholder="Ex: Minecraft, Copa do Mundo...", key="papo_turma")
        
        if st.button("🗣️ CRIAR CONEXÕES", type="primary"): 
            if assunto_papo:
                st.markdown(gerar_quebra_gelo_profundo(api_key, aluno, materia_papo, assunto_papo, hiperfoco_papo, tema_turma))
            else:
                st.warning("Preencha o Assunto.")

    # 7. DINÂMICA INCLUSIVA
    with tabs[6]:
        st.markdown("""
        <div class="pedagogia-box">
            <div class="pedagogia-title"><i class="ri-group-line"></i> Dinâmica Inclusiva</div>
            Atividades em grupo onde todos participam, respeitando as singularidades.
        </div>
        """, unsafe_allow_html=True)
        
        c1, c2 = st.columns(2)
        materia_din = c1.selectbox("Componente", discip, key="din_mat")
        assunto_din = c2.text_input("Assunto:", key="din_ass")
        
        c3, c4 = st.columns(2)
        qtd_alunos = c3.number_input("Número de Alunos:", min_value=5, max_value=50, value=25, key="din_qtd")
        carac_turma = c4.text_input("Características da Turma (Opcional):", placeholder="Ex: Turma agitada, gostam de competição...", key="din_carac")
        
        if st.button("🤝 CRIAR DINÂMICA", type="primary"): 
            if assunto_din:
                st.markdown(gerar_dinamica_inclusiva(api_key, aluno, materia_din, assunto_din, qtd_alunos, carac_turma))
            else:
                st.warning("Preencha o Assunto.")

    # 8. NOVO: PLANO DE AULA (BNCC)
    with tabs[7]:
        st.markdown("""
        <div class="pedagogia-box">
            <div class="pedagogia-title"><i class="ri-book-open-line"></i> Plano de Aula (BNCC)</div>
            Gere um planejamento completo alinhado à BNCC, selecionando metodologias ativas e recursos.
        </div>
        """, unsafe_allow_html=True)
        
        c1, c2 = st.columns(2)
        materia_plano = c1.selectbox("Componente Curricular", discip, key="plano_mat")
        assunto_plano = c2.text_input("Assunto/Tema:", key="plano_ass")
        
        c3, c4 = st.columns(2)
        metodologia = c3.selectbox("Metodologia", ["Aula Expositiva Dialogada", "Metodologia Ativa"], key="plano_met")
        
        tecnica_ativa = ""
        if metodologia == "Metodologia Ativa":
            tecnica_ativa = c4.selectbox("Técnica Ativa", ["Gamificação", "Sala de Aula Invertida", "Aprendizagem Baseada em Projetos (PBL)", "Rotação por Estações", "Peer Instruction"], key="plano_tec")
        else:
            c4.info("Metodologia tradicional selecionada.")

        c5, c6 = st.columns(2)
        qtd_alunos_plano = c5.number_input("Qtd Alunos:", min_value=1, value=30, key="plano_qtd")
        recursos_plano = c6.multiselect("Recursos Disponíveis:", ["Quadro/Giz", "Projetor/Datashow", "Lousa Digital", "Tablets/Celulares", "Internet", "Materiais Maker (Papel, Cola, etc)", "Jogos de Tabuleiro"], key="plano_rec")
        
        if st.button("📅 GERAR PLANO DE AULA", type="primary"):
            if assunto_plano:
                with st.spinner("Consultando BNCC e planejando..."):
                    st.markdown(gerar_plano_aula_bncc(api_key, materia_plano, assunto_plano, metodologia, tecnica_ativa, qtd_alunos_plano, recursos_plano))
            else:
                st.warning("Preencha o Assunto.")
