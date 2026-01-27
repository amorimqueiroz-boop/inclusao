# ==============================================================================
# HUB DE INCLUSÃO - VERSÃO MODULAR E ORGANIZADA
# ==============================================================================

# --- IMPORTS ---
import streamlit as st
from datetime import date, datetime
import os
import re
import base64
import json
import requests
import pandas as pd
from PIL import Image
from io import BytesIO

# Importações OpenAI e ML
from openai import OpenAI

# Importações para documentos
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Pt, Inches
from fpdf import FPDF
from pypdf import PdfReader

# Importações UI
from streamlit_cropper import st_cropper
import omni_utils as ou

# ==============================================================================
# CONFIGURAÇÃO INICIAL
# ==============================================================================

# ✅ set_page_config UMA VEZ SÓ, SEMPRE no topo
st.set_page_config(
    page_title="Omnisfera | Hub de Recursos",
    page_icon="📘",
    layout="wide",
    initial_sidebar_state="collapsed",
)

APP_VERSION = "v150.0 (SaaS Design)"

# ✅ UI lockdown (não quebra se faltar)
try:
    from ui_lockdown import hide_streamlit_chrome_if_needed, hide_default_sidebar_nav
    hide_streamlit_chrome_if_needed()
    hide_default_sidebar_nav()
except Exception:
    pass

# ✅ Header + Navbar (depois do page_config)
ou.render_omnisfera_header()
ou.render_navbar(active_tab="Hub de Recursos")
ou.inject_compact_app_css()

# Adiciona classe no body para cores específicas das abas
st.markdown("<script>document.body.classList.add('page-teal');</script>", unsafe_allow_html=True)

# ==============================================================================
# AJUSTE FINO DE LAYOUT (ANTES DO HERO - PADRONIZADO)
# ==============================================================================
def forcar_layout_hub():
    st.markdown("""
        <style>
            /* 1. Remove o cabeçalho padrão do Streamlit e a linha colorida */
            header[data-testid="stHeader"] {
                visibility: hidden !important;
                height: 0px !important;
            }

            /* 2. Puxa todo o conteúdo para cima (O SEGREDO ESTÁ AQUI) */
            .block-container {
                padding-top: 0.1rem !important; /* Espaço mínimo entre navbar e hero */
                padding-bottom: 1rem !important;
                margin-top: 0px !important;
            }

            /* 3. Remove padding extra se houver container de navegação */
            div[data-testid="stVerticalBlock"] > div:first-child {
                padding-top: 0px !important;
            }
            
            /* 4. Esconde o menu hambúrguer e rodapé */
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
        </style>
    """, unsafe_allow_html=True)

# CHAME ESTA FUNÇÃO ANTES DO HERO CARD (igual ao PEI)
forcar_layout_hub()

# Cores dos hero cards (paleta vibrante)
ou.inject_hero_card_colors()
# CSS padronizado: abas (pílulas), botões, selects, etc.
ou.inject_unified_ui_css()

# ==============================================================================
# HERO - HUB DE INCLUSÃO
# ==============================================================================
hora = datetime.now().hour
saudacao = "Bom dia" if 5 <= hora < 12 else "Boa tarde" if 12 <= hora < 18 else "Boa noite"
USUARIO_NOME = st.session_state.get("usuario_nome", "Visitante").split()[0]
WORKSPACE_NAME = st.session_state.get("workspace_name", "Workspace")

st.markdown(f"""
<div class="mod-card-wrapper">
    <div class="mod-card-rect">
        <div class="mod-bar c-teal"></div>
        <div class="mod-icon-area bg-teal-soft">
            <i class="ri-lightbulb-flash-fill"></i>
        </div>
        <div class="mod-content">
            <div class="mod-title">Hub de Recursos & Inteligência Artificial</div>
            <div class="mod-desc">
                {saudacao}, <strong>{USUARIO_NOME}</strong>! Acesse recursos, modelos e ferramentas de IA 
                para criar adaptações e estratégias personalizadas no workspace <strong>{WORKSPACE_NAME}</strong>.
            </div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# CSS específico do hero card do Hub
st.markdown("""
<style>
    /* CORES ESPECÍFICAS TEAL - Garantir que o ícone tenha cor correta */
    .c-teal { background: #0D9488 !important; }
    .bg-teal-soft {
        background: #CCFBF1 !important;
        color: #0D9488 !important;
    }
    .mod-icon-area i { color: inherit !important; }
    .bg-teal-soft i,
    .mod-icon-area.bg-teal-soft i,
    .mod-icon-area.bg-teal-soft i.ri-lightbulb-flash-fill {
        color: #0D9488 !important;
        font-size: 1.8rem !important;
    }
    .mod-content {
        min-width: 0;
        align-items: flex-start;
    }
    .mod-card-rect:hover .mod-title {
        color: #0D9488; /* Specific hover color */
    }
</style>
""", unsafe_allow_html=True)

# CSS específico do Hub (após hero card)
aplicar_estilos()

# Espaçamento após hero card
st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

# ==============================================================================
# CONSTANTES E DADOS GLOBAIS
# ==============================================================================

# Dados da Taxonomia de Bloom
TAXONOMIA_BLOOM = {
    "1. Lembrar (Memorizar)": ["Citar", "Definir", "Identificar", "Listar", "Nomear", "Reconhecer", "Recordar", "Relacionar", "Repetir", "Sublinhar"],
    "2. Entender (Compreender)": ["Classificar", "Descrever", "Discutir", "Explicar", "Expressar", "Identificar", "Localizar", "Narrar", "Reafirmar", "Reportar", "Resumir", "Traduzir"],
    "3. Aplicar": ["Aplicar", "Demonstrar", "Dramatizar", "Empregar", "Esboçar", "Ilustrar", "Interpretar", "Operar", "Praticar", "Programar", "Usar"],
    "4. Analisar": ["Analisar", "Calcular", "Categorizar", "Comparar", "Contrastar", "Criticar", "Diferenciar", "Discriminar", "Distinguir", "Examinar", "Experimentar", "Testar"],
    "5. Avaliar": ["Argumentar", "Avaliar", "Defender", "Escolher", "Estimar", "Julgar", "Prever", "Selecionar", "Suportar", "Validar", "Valorizar"],
    "6. Criar": ["Compor", "Construir", "Criar", "Desenhar", "Desenvolver", "Formular", "Investigar", "Planejar", "Produzir", "Propor"]
}

# Lista de disciplinas padrão
DISCIPLINAS_PADRAO = ["Matemática", "Português", "Ciências", "História", "Geografia", "Artes", "Educação Física", "Inglês", "Filosofia", "Sociologia"]

# Campos de Experiência (Educação Infantil)
CAMPOS_EXPERIENCIA_EI = [
    "O eu, o outro e o nós",
    "Corpo, gestos e movimentos",
    "Traços, sons, cores e formas",
    "Escuta, fala, pensamento e imaginação",
    "Espaços, tempos, quantidades, relações e transformações"
]

# Metodologias para Plano de Aula
METODOLOGIAS = [
    "Aula Expositiva Dialogada", 
    "Metodologia Ativa", 
    "Aprendizagem Baseada em Problemas", 
    "Ensino Híbrido",
    "Sala de Aula Invertida", 
    "Rotação por Estações"
]

# Técnicas Ativas
TECNICAS_ATIVAS = [
    "Gamificação", 
    "Sala de Aula Invertida", 
    "Aprendizagem Baseada em Projetos (PBL)", 
    "Rotação por Estações", 
    "Peer Instruction",
    "Estudo de Caso", 
    "Aprendizagem Cooperativa"
]

# Recursos disponíveis
RECURSOS_DISPONIVEIS = [
    "Quadro/Giz", 
    "Projetor/Datashow", 
    "Lousa Digital", 
    "Tablets/Celulares", 
    "Internet", 
    "Materiais Maker (Papel, Cola, etc)", 
    "Jogos de Tabuleiro", 
    "Laboratório", 
    "Material Dourado",
    "Recursos de CAA", 
    "Vídeos Educativos"
]

# ==============================================================================
# FUNÇÕES DE UTILIDADE GERAL
# ==============================================================================

def extrair_dados_docx(uploaded_file):
    """Extrai texto e imagens de um arquivo DOCX"""
    uploaded_file.seek(0)
    imagens = []
    texto = ""
    try:
        doc = Document(uploaded_file)
        texto = "\n".join([p.text for p in doc.paragraphs if p.text.strip() != ""])
        for rel in doc.part.rels.values():
            if "image" in rel.target_ref:
                img_data = rel.target_part.blob
                if len(img_data) > 1024:
                    imagens.append(img_data)
    except Exception as e:
        print(f"Erro ao extrair DOCX: {e}")
    return texto, imagens

def sanitizar_imagem(image_bytes):
    """Converte e otimiza imagem"""
    try:
        img = Image.open(BytesIO(image_bytes)).convert("RGB")
        out = BytesIO()
        img.save(out, format="JPEG", quality=90)
        return out.getvalue()
    except Exception as e:
        print(f"Erro ao sanitizar imagem: {e}")
        return None

def baixar_imagem_url(url):
    """Baixa imagem a partir de uma URL"""
    try:
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200:
            return BytesIO(resp.content)
    except Exception as e:
        print(f"Erro ao baixar imagem: {e}")
    return None

def buscar_imagem_unsplash(query, access_key):
    """Busca imagem no Unsplash"""
    if not access_key:
        return None
    url = f"https://api.unsplash.com/search/photos?query={query}&per_page=1&client_id={access_key}&lang=pt"
    try:
        resp = requests.get(url, timeout=5)
        data = resp.json()
        if data.get('results'):
            return data['results'][0]['urls']['regular']
    except Exception as e:
        print(f"Erro ao buscar no Unsplash: {e}")
    return None

def garantir_tag_imagem(texto):
    """Garante que o texto tenha pelo menos uma tag de imagem"""
    if "[[IMG" not in texto.upper() and "[[GEN_IMG" not in texto.upper():
        match = re.search(r'(\n|\. )', texto)
        if match:
            pos = match.end()
            return texto[:pos] + "\n\n[[IMG_1]]\n\n" + texto[pos:]
        return texto + "\n\n[[IMG_1]]"
    return texto

def construir_docx_final(texto_ia, aluno, materia, mapa_imgs, tipo_atv, sem_cabecalho=False):
    """Constrói documento DOCX final"""
    doc = Document()
    style = doc.styles['Normal']
    style.font.name = 'Arial'
    style.font.size = Pt(12)
    
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
                    if not img_bytes and len(mapa_imgs) == 1:
                        img_bytes = list(mapa_imgs.values())[0]
                    if img_bytes:
                        try:
                            p = doc.add_paragraph()
                            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                            r = p.add_run()
                            r.add_picture(BytesIO(img_bytes), width=Inches(4.5))
                        except Exception as e:
                            print(f"Erro ao adicionar imagem: {e}")
                elif parte.strip():
                    doc.add_paragraph(parte.strip())
        else:
            if linha.strip():
                doc.add_paragraph(linha.strip())
            
    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer

def criar_docx_simples(texto, titulo="Documento"):
    """Cria um DOCX simples a partir de texto"""
    doc = Document()
    doc.add_heading(titulo, 0)
    for para in texto.split('\n'):
        if para.strip():
            doc.add_paragraph(para.strip())
    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer

def criar_pdf_generico(texto):
    """Cria um PDF simples a partir de texto"""
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    texto_safe = texto.encode('latin-1', 'replace').decode('latin-1')
    pdf.multi_cell(0, 10, texto_safe)
    return pdf.output(dest='S').encode('latin-1')

# ==============================================================================
# FUNÇÕES DE CONEXÃO COM SUPABASE (CORRIGIDO PARA SEPARAR DIAGNÓSTICO DE HIPERFOCO)
# ==============================================================================
# Funções _sb_url(), _sb_key(), _headers() removidas - usar ou._sb_url(), ou._sb_key(), ou._headers() do omni_utils

@st.cache_data(ttl=10, show_spinner=False)
def list_students_rest():
    """
    Busca estudantes do Supabase.
    Removemos 'hiperfoco' da query direta para evitar erro se a coluna não existir,
    pois vamos pegar esse dado de dentro do JSON 'pei_data'.
    """
    WORKSPACE_ID = st.session_state.get("workspace_id")
    if not WORKSPACE_ID:
        return []

    try:
        base = (
            f"{ou._sb_url()}/rest/v1/students"
            f"?select=id,name,grade,class_group,diagnosis,created_at,pei_data,paee_ciclos,planejamento_ativo"
            f"&workspace_id=eq.{WORKSPACE_ID}"
            f"&order=created_at.desc"
        )
        r = requests.get(base, headers=ou._headers(), timeout=20)
        return r.json() if r.status_code == 200 else []
    except Exception as e:
        print(f"Erro ao carregar alunos: {str(e)}")
        return []

def carregar_estudantes_supabase():
    """Carrega e processa estudantes, separando Diagnóstico de Hiperfoco."""
    dados = list_students_rest()
    estudantes = []

    for item in dados:
        pei_completo = item.get("pei_data") or {}
        contexto_ia = ""

        # Tenta pegar texto de contexto da IA dentro do JSON do PEI
        if isinstance(pei_completo, dict):
            contexto_ia = pei_completo.get("ia_sugestao", "") or ""
        
        # 1. CAPTURA DO DIAGNÓSTICO (Vem da coluna do banco)
        diagnostico_real = item.get("diagnosis")
        if not diagnostico_real:
            diagnostico_real = "Não informado no cadastro"

        # 2. CAPTURA DO HIPERFOCO (Vem de dentro do JSON pei_data)
        # Tenta várias chaves possíveis onde o hiperfoco pode ter sido salvo
        hiperfoco_real = ""
        if isinstance(pei_completo, dict):
            hiperfoco_real = (
                pei_completo.get("hiperfoco") or 
                pei_completo.get("interesses") or 
                pei_completo.get("habilidades_interesses") or 
                ""
            )
        
        # Se não achou no JSON, coloca um padrão (mas NÃO usa o diagnóstico)
        if not hiperfoco_real:
            hiperfoco_real = "Interesses gerais (A descobrir)"

        # Montagem do resumo de fallback se não houver contexto da IA
        if not contexto_ia:
            serie = item.get("grade", "")
            contexto_ia = f"Aluno: {item.get('name')}. Série: {serie}. Diagnóstico: {diagnostico_real}."

        estudante = {
            "nome": item.get("name", ""),
            "serie": item.get("grade", ""),
            
            # AQUI ESTÁ A CORREÇÃO: Chaves separadas e limpas
            "diagnosis": diagnostico_real,  
            "hiperfoco": hiperfoco_real,
            
            "ia_sugestao": contexto_ia,
            "id": item.get("id", ""),
            "pei_data": pei_completo,
        }
        
        if estudante["nome"]:
            estudantes.append(estudante)

    return estudantes

# ==============================================================================
# FUNÇÕES DE IA (OPENAI)
# ==============================================================================

def gerar_imagem_inteligente(api_key, prompt, unsplash_key=None, feedback_anterior="", prioridade="IA"):
    """
    Gera imagem com prioridade: IA (DALL-E) ou BANCO (Unsplash)
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
        print(f"Erro ao gerar imagem: {e}")
        return None

def gerar_pictograma_caa(api_key, conceito, feedback_anterior=""):
    """
    Gera símbolo específico para Comunicação Aumentativa e Alternativa.
    """
    client = OpenAI(api_key=api_key)
    
    ajuste = f" CORREÇÃO PEDIDA: {feedback_anterior}" if feedback_anterior else ""
    
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
    except Exception as e:
        print(f"Erro ao gerar pictograma: {e}")
        return None

def adaptar_conteudo_docx(api_key, aluno, texto, materia, tema, tipo_atv, remover_resp, questoes_mapeadas, modo_profundo=False):
    """Adapta conteúdo de um DOCX para o aluno"""
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
        resp = client.chat.completions.create(
            model="gpt-4o-mini", 
            messages=[{"role": "user", "content": prompt}], 
            temperature=0.7 if modo_profundo else 0.4
        )
        full_text = resp.choices[0].message.content
        if "---DIVISOR---" in full_text:
            parts = full_text.split("---DIVISOR---")
            return parts[0].replace("[ANÁLISE PEDAGÓGICA]", "").strip(), parts[1].replace("[ATIVIDADE]", "").strip()
        return "Análise indisponível.", full_text
    except Exception as e:
        return str(e), ""

def adaptar_conteudo_imagem(api_key, aluno, imagem_bytes, materia, tema, tipo_atv, livro_professor, modo_profundo=False):
    """Adapta conteúdo de uma imagem para o aluno"""
    client = OpenAI(api_key=api_key)
    if not imagem_bytes:
        return "Erro: Imagem vazia", ""
    
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
    
    msgs = [
        {
            "role": "user", 
            "content": [
                {"type": "text", "text": prompt}, 
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}}
            ]
        }
    ]
    
    try:
        resp = client.chat.completions.create(
            model="gpt-4o-mini", 
            messages=msgs, 
            temperature=0.7 if modo_profundo else 0.4
        )
        full_text = resp.choices[0].message.content
        analise = "Análise indisponível."
        atividade = full_text
        if "---DIVISOR---" in full_text:
            parts = full_text.split("---DIVISOR---")
            analise = parts[0].replace("[ANÁLISE PEDAGÓGICA]", "").strip()
            atividade = parts[1].replace("[ATIVIDADE]", "").strip()
        atividade = garantir_tag_imagem(atividade)
        return analise, atividade
    except Exception as e:
        return str(e), ""

def criar_profissional(api_key, aluno, materia, objeto, qtd, tipo_q, qtd_imgs, verbos_bloom=None, habilidades_bncc=None, modo_profundo=False):
    """Cria atividade profissional do zero"""
    client = OpenAI(api_key=api_key)
    hiperfoco = aluno.get('hiperfoco', 'Geral')
    
    # Instrução de imagens
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
    
    # Instrução de habilidades BNCC
    instrucao_habilidades = ""
    if habilidades_bncc:
        habilidades_str = "\n".join([f"- {hab}" for hab in habilidades_bncc])
        instrucao_habilidades = f"""
        7. HABILIDADES BNCC (RIGOROSO):
           - Alinhe as questões com as seguintes habilidades da BNCC:
           {habilidades_str}
           - Inclua referências às habilidades nos enunciados quando pertinente.
        """
    
    # Formato baseado no tipo
    if tipo_q == "Discursiva":
        diretriz_tipo = "3. FORMATO DISCURSIVO (RIGOROSO): Crie apenas questões abertas. NÃO inclua alternativas, apenas linhas para resposta."
    else:
        diretriz_tipo = "3. FORMATO OBJETIVO: Crie questões de múltipla escolha com distratores inteligentes."
    
    style = "Atue como uma banca examinadora rigorosa." if modo_profundo else "Atue como professor elaborador."
    
    prompt = f"""
    {style}
    Crie prova de {materia} ({objeto}). QTD: {qtd} ({tipo_q}).
    
    DIRETRIZES: 
    1. Contexto Real. 
    2. Hiperfoco ({hiperfoco}) em 30%. 
    {diretriz_tipo}
    4. Imagens: {instrucao_img} (NUNCA repita a mesma imagem). 
    5. Divisão Clara.
    
    REGRA DE OURO GRAMATICAL (IMPERATIVO):
    - TODOS os comandos das questões devem estar no modo IMPERATIVO (Ex: "Cite", "Explique", "Calcule", "Analise", "Escreva").
    - JAMAIS use o infinitivo (Ex: "Citar", "Explicar", "Calcular").
    - Se houver verbos de Bloom selecionados, CONJUGUE-OS para o IMPERATIVO.
    - O verbo de comando deve vir no início do enunciado, em **NEGRITO E CAIXA ALTA** (Ex: **ANALISE**, **IDENTIFIQUE**).
    
    {instrucao_bloom}
    {instrucao_habilidades}
    
    SAÍDA OBRIGATÓRIA:
    [ANÁLISE PEDAGÓGICA]
    ...análise...
    ---DIVISOR---
    [ATIVIDADE]
    ...questões...
    """
    
    try:
        resp = client.chat.completions.create(
            model="gpt-4o-mini", 
            messages=[{"role": "user", "content": prompt}], 
            temperature=0.8 if modo_profundo else 0.6
        )
        full_text = resp.choices[0].message.content
        if "---DIVISOR---" in full_text:
            parts = full_text.split("---DIVISOR---")
            return parts[0].replace("[ANÁLISE PEDAGÓGICA]", "").strip(), parts[1].replace("[ATIVIDADE]", "").strip()
        return "Análise indisponível.", full_text
    except Exception as e:
        return str(e), ""

def gerar_experiencia_ei_bncc(api_key, aluno, campo_exp, objetivo, feedback_anterior=""):
    """Gera experiência para Educação Infantil"""
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
        resp = client.chat.completions.create(
            model="gpt-4o-mini", 
            messages=[{"role": "user", "content": prompt}], 
            temperature=0.7
        )
        return resp.choices[0].message.content
    except Exception as e:
        return str(e)

def gerar_roteiro_aula_completo(api_key, aluno, materia, assunto, habilidades_bncc=None, verbos_bloom=None, ano=None, unidade_tematica=None, objeto_conhecimento=None, feedback_anterior=""):
    """Gera roteiro de aula completo com BNCC"""
    client = OpenAI(api_key=api_key)
    
    # Construir informações da BNCC
    info_bncc = ""
    if habilidades_bncc:
        info_bncc += f"\nHabilidades BNCC:"
        for hab in habilidades_bncc:
            info_bncc += f"\n- {hab}"
    
    if ano:
        info_bncc += f"\nAno: {ano}"
    
    if unidade_tematica:
        info_bncc += f"\nUnidade Temática: {unidade_tematica}"
    
    if objeto_conhecimento:
        info_bncc += f"\nObjeto do Conhecimento: {objeto_conhecimento}"
    
    # Construir informações Bloom
    info_bloom = ""
    if verbos_bloom:
        info_bloom = f"\nVerbos da Taxonomia de Bloom: {', '.join(verbos_bloom)}"
    
    ajuste = f"\nAJUSTES SOLICITADOS: {feedback_anterior}" if feedback_anterior else ""
    
    prompt = f"""
    Crie um ROTEIRO DE AULA INDIVIDUALIZADO para {aluno['nome']}.
    
    INFORMAÇÕES DO ALUNO:
    - Perfil: {aluno.get('ia_sugestao', '')[:500]}
    - Hiperfoco: {aluno.get('hiperfoco', 'Geral')}
    
    INFORMAÇÕES DA AULA:
    - Componente: {materia}
    - Assunto: {assunto}
    {info_bncc}
    {info_bloom}
    {ajuste}
    
    ESTRUTURA OBRIGATÓRIA:
    
    1. **CONEXÃO INICIAL COM O HIPERFOCO** (2-3 minutos)
       - Como conectar o tema com o hiperfoco do estudante
    
    2. **OBJETIVOS DA AULA**
       - Objetivos claros e mensuráveis
    
    3. **DESENVOLVIMENTO PASSO A PASSO** (15-20 minutos)
       - Divida em 3-4 etapas claras
       - Inclua perguntas mediadoras
       - Use exemplos relacionados ao hiperfoco
    
    4. **ATIVIDADE PRÁTICA INDIVIDUAL** (5-7 minutos)
       - Tarefa que o estudante pode fazer sozinho
    
    5. **FECHAMENTO E REFLEXÃO** (3-5 minutos)
       - Verificação dos objetivos
       - Pergunta de reflexão
    
    6. **RECURSOS E MATERIAIS**
    
    7. **AVALIAÇÃO FORMATIVA**
       - Como avaliar durante a aula
    """
    
    try:
        resp = client.chat.completions.create(
            model="gpt-4o-mini", 
            messages=[{"role": "user", "content": prompt}], 
            temperature=0.7
        )
        return resp.choices[0].message.content
    except Exception as e:
        return str(e)

def gerar_dinamica_inclusiva_completa(api_key, aluno, materia, assunto, qtd_alunos, caracteristicas_turma, habilidades_bncc=None, verbos_bloom=None, ano=None, unidade_tematica=None, objeto_conhecimento=None, feedback_anterior=""):
    """Gera dinâmica inclusiva completa com BNCC"""
    client = OpenAI(api_key=api_key)
    
    # Construir informações da BNCC
    info_bncc = ""
    if habilidades_bncc:
        info_bncc += f"\nHabilidades BNCC:"
        for hab in habilidades_bncc:
            info_bncc += f"\n- {hab}"
    
    if ano:
        info_bncc += f"\nAno: {ano}"
    
    if unidade_tematica:
        info_bncc += f"\nUnidade Temática: {unidade_tematica}"
    
    if objeto_conhecimento:
        info_bncc += f"\nObjeto do Conhecimento: {objeto_conhecimento}"
    
    # Construir informações Bloom
    info_bloom = ""
    if verbos_bloom:
        info_bloom = f"\nVerbos da Taxonomia de Bloom: {', '.join(verbos_bloom)}"
    
    ajuste = f"\nAJUSTES SOLICITADOS: {feedback_anterior}" if feedback_anterior else ""
    
    prompt = f"""
    Crie uma DINÂMICA INCLUSIVA para {qtd_alunos} alunos.
    
    INFORMAÇÕES DO ALUNO FOCAL:
    - Nome: {aluno['nome']}
    - Perfil: {aluno.get('ia_sugestao', '')[:400]}
    - Hiperfoco: {aluno.get('hiperfoco', 'Geral')}
    
    INFORMAÇÕES DA DINÂMICA:
    - Componente: {materia}
    - Tema: {assunto}
    - Características da turma: {caracteristicas_turma}
    {info_bncc}
    {info_bloom}
    {ajuste}
    
    ESTRUTURA OBRIGATÓRIA:
    
    1. **NOME DA DINÂMICA E OBJETIVO**
       - Nome criativo
       - Objetivo claro
    
    2. **MATERIAIS NECESSÁRIOS**
    
    3. **PREPARAÇÃO**
       - Como preparar a sala/ambiente
    
    4. **PASSO A PASSO** (detalhado)
       - Instruções claras para o professor
       - Inclua adaptações para o aluno focal
    
    5. **DURAÇÃO ESTIMADA**
    
    6. **AVALIAÇÃO**
       - Como avaliar a participação de todos
    
    7. **VARIAÇÕES**
       - Sugestões para adaptar a dinâmica
    """
    
    try:
        resp = client.chat.completions.create(
            model="gpt-4o-mini", 
            messages=[{"role": "user", "content": prompt}], 
            temperature=0.7
        )
        return resp.choices[0].message.content
    except Exception as e:
        return str(e)

def gerar_plano_aula_completo(api_key, materia, assunto, metodologia, tecnica, qtd_alunos, recursos, habilidades_bncc=None, verbos_bloom=None, ano=None, unidade_tematica=None, objeto_conhecimento=None, aluno_info=None):
    """Gera plano de aula completo com BNCC"""
    client = OpenAI(api_key=api_key)
    
    # Construir informações da BNCC
    info_bncc = ""
    if habilidades_bncc:
        info_bncc += f"\nHABILIDADES BNCC:"
        for hab in habilidades_bncc:
            info_bncc += f"\n- {hab}"
    
    if ano:
        info_bncc += f"\nAno: {ano}"
    
    if unidade_tematica:
        info_bncc += f"\nUnidade Temática: {unidade_tematica}"
    
    if objeto_conhecimento:
        info_bncc += f"\nObjeto do Conhecimento: {objeto_conhecimento}"
    
    # Construir informações Bloom
    info_bloom = ""
    if verbos_bloom:
        info_bloom = f"\nVERBOS DA TAXONOMIA DE BLOOM: {', '.join(verbos_bloom)}"
    
    # Informações do aluno (para DUA)
    info_aluno = ""
    if aluno_info:
        info_aluno = f"""
    INFORMAÇÕES DO ALUNO (DUA):
    - Nome: {aluno_info.get('nome', '')}
    - Hiperfoco: {aluno_info.get('hiperfoco', '')}
    - Perfil: {aluno_info.get('ia_sugestao', '')[:300]}
        """
    
    prompt = f"""
    ATUAR COMO: Coordenador Pedagógico Especialista em BNCC, DUA e Metodologias Ativas.
    
    Crie um PLANO DE AULA COMPLETO com as seguintes informações:
    
    INFORMAÇÕES BÁSICAS:
    - Componente: {materia}
    - Tema/Assunto: {assunto}
    - Metodologia: {metodologia}
    - Técnica: {tecnica if tecnica else 'Não especificada'}
    - Quantidade de Alunos: {qtd_alunos}
    - Recursos Disponíveis: {', '.join(recursos)}
    
    {info_bncc}
    {info_bloom}
    {info_aluno}
    
    ESTRUTURA DO PLANO (Markdown):
    
    ## 📋 PLANO DE AULA: {assunto}
    
    ### 🎯 OBJETIVOS DE APRENDIZAGEM
    - Objetivo geral
    - Objetivos específicos (3-4)
    - Habilidades da BNCC trabalhadas
    
    ### 📚 CONTEÚDOS
    - Conteúdos conceituais
    - Conteúdos procedimentais
    - Conteúdos atitudinais
    
    ### ⏰ TEMPO ESTIMADO
    - Duração total: __ minutos
    
    ### 🛠 RECURSOS DIDÁTICOS
    - Lista de recursos necessários
    
    ### 🚀 DESENVOLVIMENTO DA AULA
    #### 1. ACOLHIDA E MOTIVAÇÃO (__ minutos)
    - Atividade de engajamento
    
    #### 2. APRESENTAÇÃO DO CONTEÚDO (__ minutos)
    - Explicação do tema
    - Conexões com conhecimentos prévios
    
    #### 3. ATIVIDADE PRÁTICA (__ minutos)
    - Descrição detalhada da atividade
    - Papel do professor
    - Papel dos alunos
    
    #### 4. SOCIALIZAÇÃO (__ minutos)
    - Compartilhamento dos resultados
    - Discussão coletiva
    
    #### 5. AVALIAÇÃO (__ minutos)
    - Instrumentos de avaliação
    - Critérios
    
    ### ♿ ADAPTAÇÕES DUA (DESIGN UNIVERSAL PARA APRENDIZAGEM)
    - Engajamento: Como manter todos motivados
    - Representação: Múltiplas formas de apresentar o conteúdo
    - Ação e Expressão: Múltiplas formas de expressar o aprendizado
    
    ### 📝 AVALIAÇÃO
    - Avaliação diagnóstica
    - Avaliação formativa
    - Avaliação somativa
    
    ### 🔄 RECUPERAÇÃO
    - Estratégias para alunos com dificuldades
    
    ### 📚 REFERÊNCIAS
    - Referências bibliográficas
    - Sites recomendados
    """
    
    try:
        resp = client.chat.completions.create(
            model="gpt-4o-mini", 
            messages=[{"role": "user", "content": prompt}], 
            temperature=0.7
        )
        return resp.choices[0].message.content
    except Exception as e:
        return str(e)

def gerar_quebra_gelo_profundo(api_key, aluno, materia, assunto, hiperfoco, tema_turma_extra=""):
    """Gera quebra-gelo profundo para engajamento"""
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
        resp = client.chat.completions.create(
            model="gpt-4o-mini", 
            messages=[{"role": "user", "content": prompt}], 
            temperature=0.8
        )
        return resp.choices[0].message.content
    except Exception as e:
        return str(e)

    # ==============================================================================
# FUNÇÕES DE BNCC (DROPDOWNS)
# ==============================================================================

def padronizar_ano(ano_str):
    """Converte diferentes formatos de ano para um padrão ordenável"""
    if not isinstance(ano_str, str):
        ano_str = str(ano_str)
    
    ano_str = ano_str.strip()
    
    # Padrões comuns
    padroes = [
        (r'(\d+)\s*º?\s*ano', 'ano'),
        (r'(\d+)\s*ª?\s*série', 'ano'),
        (r'(\d+)\s*em', 'em'),
        (r'ef\s*(\d+)', 'ano'),
        (r'(\d+)\s*período', 'ano'),
        (r'(\d+)\s*semestre', 'ano'),
    ]
    
    for padrao, tipo in padroes:
        match = re.search(padrao, ano_str.lower())
        if match:
            num = match.group(1)
            if tipo == 'em':
                return f"{int(num):02d}EM"
            else:
                return f"{int(num):02d}"
    
    return ano_str

def ordenar_anos(anos_lista):
    """Ordena anos de forma inteligente"""
    anos_padronizados = []
    
    for ano in anos_lista:
        padrao = padronizar_ano(str(ano))
        anos_padronizados.append((padrao, ano))
    
    anos_padronizados.sort(key=lambda x: x[0])
    return [ano_original for _, ano_original in anos_padronizados]

@st.cache_data
def carregar_bncc_completa():
    """Carrega o CSV da BNCC com todas as colunas necessárias"""
    try:
        if not os.path.exists('bncc.csv'):
            st.warning("📄 Arquivo 'bncc.csv' não encontrado na pasta do script")
            return None
        
        try:
            df = pd.read_csv('bncc.csv', delimiter=',', encoding='utf-8')
        except:
            try:
                df = pd.read_csv('bncc.csv', delimiter=';', encoding='utf-8')
            except Exception as e:
                st.error(f"❌ Erro ao ler CSV: {str(e)[:100]}")
                return None
        
        colunas_necessarias = ['Ano', 'Disciplina', 'Unidade Temática', 
                              'Objeto do Conhecimento', 'Habilidade']
        
        colunas_faltando = []
        for col in colunas_necessarias:
            if col not in df.columns:
                colunas_faltando.append(col)
        
        if colunas_faltando:
            st.error(f"❌ Colunas faltando: {colunas_faltando}")
            return None
        
        df = df.dropna(subset=['Ano', 'Disciplina', 'Objeto do Conhecimento'])
        df['Ano'] = df['Ano'].astype(str).str.strip()
        df['Disciplina'] = df['Disciplina'].str.replace('Ed. Física', 'Educação Física')
        
        return df
    
    except Exception as e:
        st.error(f"❌ Erro: {str(e)[:100]}")
        return None

def criar_dropdowns_bncc_completos_melhorado(key_suffix="", mostrar_habilidades=True):
    """
    Cria 5 dropdowns hierárquicos conectados com multiselect para habilidades
    """
    # Carregar dados se necessário
    if 'bncc_df_completo' not in st.session_state:
        st.session_state.bncc_df_completo = carregar_bncc_completa()
    
    dados = st.session_state.bncc_df_completo
    
    # Se não tem dados, mostrar campos básicos
    if dados is None or dados.empty:
        st.warning("⚠️ BNCC não carregada. Usando campos básicos.")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            ano = st.selectbox("Ano", ordenar_anos(["1", "2", "3", "4", "5", "6", "7", "8", "9", "1EM", "2EM", "3EM"]), 
                              key=f"ano_basico_{key_suffix}")
        with col2:
            disciplina = st.selectbox("Disciplina", DISCIPLINAS_PADRAO, key=f"disc_basico_{key_suffix}")
        with col3:
            objeto = st.text_input("Objeto do Conhecimento", placeholder="Ex: Frações", 
                                  key=f"obj_basico_{key_suffix}")
        
        col4, col5 = st.columns(2)
        with col4:
            unidade = st.text_input("Unidade Temática", placeholder="Ex: Números", 
                                   key=f"unid_basico_{key_suffix}")
        
        habilidades = []
        if mostrar_habilidades:
            with col5:
                habilidades_selecionadas = st.multiselect(
                    "Habilidades (selecione uma ou mais)",
                    ["Digite abaixo...", "Habilidade 1", "Habilidade 2"],
                    default=[],
                    key=f"hab_multi_basico_{key_suffix}"
                )
                
                if "Digite abaixo..." in habilidades_selecionadas:
                    habilidade_texto = st.text_area("Digite as habilidades:", 
                                                   placeholder="Uma por linha", 
                                                   key=f"hab_texto_basico_{key_suffix}")
                    habilidades = habilidade_texto.split('\n') if habilidade_texto else []
                else:
                    habilidades = habilidades_selecionadas
        
        return ano, disciplina, unidade, objeto, habilidades
    
    # TEMOS DADOS - criar dropdowns conectados
    
    # Linha 1: Ano, Disciplina, Unidade Temática
    col1, col2, col3 = st.columns(3)
    
    with col1:
        anos_originais = dados['Ano'].dropna().unique().tolist()
        anos_ordenados = ordenar_anos(anos_originais)
        ano_selecionado = st.selectbox("Ano", anos_ordenados, key=f"ano_bncc_{key_suffix}")
    
    with col2:
        if ano_selecionado:
            disc_filtradas = dados[dados['Ano'].astype(str) == str(ano_selecionado)]
            disciplinas = sorted(disc_filtradas['Disciplina'].dropna().unique())
            disciplina_selecionada = st.selectbox("Disciplina", disciplinas, key=f"disc_bncc_{key_suffix}")
        else:
            disciplina_selecionada = None
    
    with col3:
        if ano_selecionado and disciplina_selecionada:
            unid_filtradas = dados[
                (dados['Ano'].astype(str) == str(ano_selecionado)) & 
                (dados['Disciplina'] == disciplina_selecionada)
            ]
            unidades = sorted(unid_filtradas['Unidade Temática'].dropna().unique())
            unidade_selecionada = st.selectbox("Unidade Temática", unidades, key=f"unid_bncc_{key_suffix}")
        else:
            unidade_selecionada = None
    
    # Linha 2: Objeto do Conhecimento
    st.markdown("---")
    col4 = st.columns(1)[0]
    
    with col4:
        if ano_selecionado and disciplina_selecionada and unidade_selecionada:
            obj_filtrados = dados[
                (dados['Ano'].astype(str) == str(ano_selecionado)) & 
                (dados['Disciplina'] == disciplina_selecionada) & 
                (dados['Unidade Temática'] == unidade_selecionada)
            ]
            objetos = sorted(obj_filtrados['Objeto do Conhecimento'].dropna().unique())
            
            if objetos:
                objeto_selecionado = st.selectbox("Objeto do Conhecimento", objetos, key=f"obj_bncc_{key_suffix}")
            else:
                objeto_selecionado = st.text_input("Objeto do Conhecimento", 
                                                  placeholder="Não encontrado, digite", 
                                                  key=f"obj_input_bncc_{key_suffix}")
        else:
            objeto_selecionado = st.text_input("Objeto do Conhecimento", 
                                              placeholder="Selecione primeiro", 
                                              key=f"obj_wait_bncc_{key_suffix}")
    
    # Habilidades (opcional)
    habilidades_selecionadas = []
    if mostrar_habilidades:
        st.markdown("---")
        col5 = st.columns(1)[0]
        
        with col5:
            if (ano_selecionado and disciplina_selecionada and 
                unidade_selecionada and objeto_selecionado and 
                isinstance(objeto_selecionado, str) and not objeto_selecionado.startswith("Selecione")):
                
                hab_filtradas = dados[
                    (dados['Ano'].astype(str) == str(ano_selecionado)) & 
                    (dados['Disciplina'] == disciplina_selecionada) & 
                    (dados['Unidade Temática'] == unidade_selecionada) & 
                    (dados['Objeto do Conhecimento'] == objeto_selecionado)
                ]
                todas_habilidades = sorted(hab_filtradas['Habilidade'].dropna().unique())
                
                if todas_habilidades:
                    st.markdown(f"**🔍 {len(todas_habilidades)} habilidade(s) encontrada(s):**")
                    
                    opcoes_habilidades = st.multiselect(
                        "Selecione uma ou mais habilidades:",
                        todas_habilidades,
                        default=todas_habilidades[:min(3, len(todas_habilidades))],
                        key=f"hab_multi_bncc_{key_suffix}"
                    )
                    
                    with st.expander("➕ Adicionar habilidade personalizada"):
                        habilidade_extra = st.text_area(
                            "Digite habilidades adicionais (uma por linha):",
                            placeholder="Ex:\nEF05MA01 - Ler números\nEF05MA02 - Comparar números",
                            key=f"hab_extra_bncc_{key_suffix}"
                        )
                        
                        if habilidade_extra:
                            habilidades_extras = [h.strip() for h in habilidade_extra.split('\n') if h.strip()]
                            opcoes_habilidades.extend(habilidades_extras)
                    
                    habilidades_selecionadas = opcoes_habilidades
                else:
                    st.info("ℹ️ Nenhuma habilidade encontrada para este objeto.")
                    habilidades_padrao = st.multiselect(
                        "Selecione ou adicione habilidades:",
                        ["Digite abaixo..."],
                        default=[],
                        key=f"hab_vazio_bncc_{key_suffix}"
                    )
                    
                    if "Digite abaixo..." in habilidades_padrao:
                        habilidade_texto = st.text_area("Digite as habilidades:", 
                                                       placeholder="Uma por linha", 
                                                       key=f"hab_texto_{key_suffix}")
                        habilidades_selecionadas = habilidade_texto.split('\n') if habilidade_texto else []
                    else:
                        habilidades_selecionadas = habilidades_padrao
            else:
                st.info("ℹ️ Selecione Ano, Disciplina, Unidade e Objeto para ver as habilidades.")
                habilidades_selecionadas = []
    
    return (ano_selecionado, disciplina_selecionada, unidade_selecionada, 
            objeto_selecionado, habilidades_selecionadas)

def criar_dropdowns_bncc_simplificado(key_suffix=""):
    """Cria dropdowns simplificados da BNCC (apenas até objeto do conhecimento)"""
    return criar_dropdowns_bncc_completos_melhorado(key_suffix=key_suffix, mostrar_habilidades=False)

    # ==============================================================================
# COMPONENTES DE INTERFACE (UI)
# ==============================================================================

def aplicar_estilos():
    """Aplica estilos CSS específicos do Hub (sem hero card - já renderizado acima)"""
    st.markdown("""
    <style>
        /* PEDAGOGIA BOX */
        .pedagogia-box { 
            background-color: #F8FAFC; 
            border-left: 4px solid #CBD5E1; 
            padding: 20px; 
            border-radius: 0 12px 12px 0; 
            margin-bottom: 25px; 
            font-size: 0.95rem; 
            color: #4A5568; 
        }
    
        /* RESOURCE BOX */
        .resource-box { 
            background: #F8FAFC; 
            border: 1px solid #E2E8F0; 
            border-radius: 12px; 
            padding: 20px; 
            margin: 15px 0; 
        }
        
        /* ACTION BUTTONS */
        .action-buttons { 
            display: flex; 
            gap: 10px; 
            margin-top: 20px; 
            flex-wrap: wrap; 
        }
        
        /* TIMELINE STYLES */
        .timeline-header { 
            background: white; 
            border-radius: 12px; 
            padding: 20px;
            margin-bottom: 20px; 
            border: 1px solid #E2E8F0;
            display: flex; 
            align-items: center; 
            justify-content: space-between; 
        }
        .prog-bar-bg { 
            width: 100%; 
            height: 8px; 
            background: #E2E8F0; 
            border-radius: 4px; 
            overflow: hidden; 
            margin-top: 8px; 
        }
        .prog-bar-fill { 
            height: 100%; 
            background: linear-gradient(90deg, #06B6D4, #0891B2); 
            transition: width 1s; 
        }
        
        /* HEADER DO ALUNO */
        .student-header {
            background-color: #F8FAFC;
            border: 1px solid #E2E8F0;
            border-radius: 16px;
            padding: 18px 24px;
            margin-bottom: 18px;
            display: flex; 
            justify-content: space-between; 
            align-items: center;
            box-shadow: 0 2px 4px rgba(0,0,0,0.02);
        }
        .student-info-item {
            display: flex;
            flex-direction: column;
            gap: 4px;
        }
        .student-label {
            font-size: 0.78rem; 
            color: #64748B; 
            font-weight: 800;
            text-transform: uppercase; 
            letter-spacing: 1px;
        }
        .student-value { 
            font-size: 1.15rem; 
            color: #1E293B; 
            font-weight: 800; 
        }
        
        /* RESPONSIVIDADE */
        @media (max-width: 768px) { 
            .student-header { 
                flex-direction: column; 
                align-items:flex-start; 
                gap: 12px; 
            }
        }
    </style>
    """, unsafe_allow_html=True)

def render_cabecalho_aluno(aluno):
    """Renderiza o cabeçalho com informações do aluno"""
    st.markdown(f"""
        <div class="student-header">
            <div class="student-info-item"><div class="student-label">Nome</div><div class="student-value">{aluno.get('nome')}</div></div>
            <div class="student-info-item"><div class="student-label">Série</div><div class="student-value">{aluno.get('serie', '-')}</div></div>
            <div class="student-info-item"><div class="student-label">Hiperfoco</div><div class="student-value">{aluno.get('hiperfoco', '-')}</div></div>
        </div>
    """, unsafe_allow_html=True)

def criar_seletor_bloom(chave_prefixo):
    """Componente reutilizável para seleção da Taxonomia de Bloom"""
    usar_bloom = st.checkbox("🎯 Usar Taxonomia de Bloom (Revisada)", key=f"usar_bloom_{chave_prefixo}")
    
    if f'bloom_memoria_{chave_prefixo}' not in st.session_state:
        st.session_state[f'bloom_memoria_{chave_prefixo}'] = {cat: [] for cat in TAXONOMIA_BLOOM.keys()}
    
    verbos_finais = []
    
    if usar_bloom:
        col_b1, col_b2 = st.columns(2)
        with col_b1:
            cat_atual = st.selectbox("Categoria Cognitiva:", list(TAXONOMIA_BLOOM.keys()),
                                    key=f"cat_bloom_{chave_prefixo}")
        with col_b2:
            selecao_atual = st.multiselect(
                f"Verbos de '{cat_atual}':", 
                TAXONOMIA_BLOOM[cat_atual],
                default=st.session_state[f'bloom_memoria_{chave_prefixo}'][cat_atual],
                key=f"ms_bloom_{chave_prefixo}_{cat_atual}"
            )
            st.session_state[f'bloom_memoria_{chave_prefixo}'][cat_atual] = selecao_atual
        
        for cat in st.session_state[f'bloom_memoria_{chave_prefixo}']:
            verbos_finais.extend(st.session_state[f'bloom_memoria_{chave_prefixo}'][cat])
        
        if verbos_finais:
            st.info(f"**Verbos Selecionados:** {', '.join(verbos_finais)}")
        else:
            st.caption("Nenhum verbo selecionado ainda.")
    
    return verbos_finais if usar_bloom else None

def verificar_acesso():
    """Verifica se o usuário está autenticado"""
    if "autenticado" not in st.session_state or not st.session_state["autenticado"]:
        st.error("🔒 Acesso Negado. Por favor, faça login na Página Inicial.")
        st.stop()
    # CSS removido - agora controlado pela função forcar_layout_hub() (1rem padronizado)

    # ==============================================================================
# FUNÇÕES DAS ABAS PRINCIPAIS
# ==============================================================================

def render_aba_adaptar_prova(aluno, api_key):
    """Renderiza a aba de adaptação de prova"""
    st.markdown("""
    <div class="pedagogia-box">
        <div class="pedagogia-title"><i class="ri-file-edit-line"></i> Adaptação Curricular (DUA)</div>
        Transforme provas padrão em avaliações acessíveis. O sistema simplifica enunciados, 
        insere imagens de apoio e ajusta o layout para reduzir a carga cognitiva.
    </div>
    """, unsafe_allow_html=True)
    
    # Dropdowns BNCC simplificados
    ano_bncc, disciplina_bncc, unidade_bncc, objeto_bncc, _ = criar_dropdowns_bncc_completos_melhorado(key_suffix="adaptar_prova", mostrar_habilidades=False)
    
    st.markdown("---")
    
    # Layout simplificado (apenas Tipo e Upload)
    c1, c2 = st.columns([1, 2])
    tipo_d = c1.selectbox("Tipo de Documento", ["Prova", "Tarefa", "Avaliação"], key="dtp")
    arquivo_d = c2.file_uploader("Upload do Arquivo DOCX", type=["docx"], key="fd")
    
    # Definição automática baseada na BNCC
    materia_d = disciplina_bncc if disciplina_bncc else "Geral"
    tema_d = objeto_bncc if objeto_bncc else "Geral"
    
    if 'docx_imgs' not in st.session_state:
        st.session_state.docx_imgs = []
    if 'docx_txt' not in st.session_state:
        st.session_state.docx_txt = None
    
    if arquivo_d and arquivo_d.file_id != st.session_state.get('last_d'):
        st.session_state.last_d = arquivo_d.file_id
        txt, imgs = extrair_dados_docx(arquivo_d)
        st.session_state.docx_txt = txt
        st.session_state.docx_imgs = imgs
        st.success(f"{len(imgs)} imagens encontradas.")

    map_d = {}
    qs_d = []
    if st.session_state.docx_imgs:
        st.write("### Mapeamento de Imagens")
        cols = st.columns(3)
        for i, img in enumerate(st.session_state.docx_imgs):
            with cols[i % 3]:
                st.image(img, width=80)
                q = st.number_input(f"Pertence à Questão:", 0, 50, key=f"dq_{i}")
                if q > 0:
                    map_d[int(q)] = img
                    qs_d.append(int(q))

    st.markdown("---")

    if st.button("🚀 ADAPTAR PROVA", type="primary", key="btn_d", use_container_width=True):
        if not st.session_state.docx_txt:
            st.warning("Por favor, faça o upload de um arquivo DOCX.")
            st.stop()
        
        # Validação se BNCC foi preenchida
        if not disciplina_bncc or not objeto_bncc:
             st.warning("⚠️ Por favor, selecione a Disciplina e o Objeto do Conhecimento nos campos da BNCC acima para guiar a adaptação.")
             st.stop()

        with st.spinner("A IA está analisando e adaptando o conteúdo..."):
            rac, txt = adaptar_conteudo_docx(api_key, aluno, st.session_state.docx_txt, materia_d, tema_d, tipo_d, True, qs_d)
            st.session_state['res_docx'] = {'rac': rac, 'txt': txt, 'map': map_d, 'valid': False}
            st.rerun()

    if 'res_docx' in st.session_state:
        res = st.session_state['res_docx']
        if res.get('valid'):
            st.success("✅ **ATIVIDADE VALIDADA E PRONTA PARA USO**")
        else:
            col_v, col_r = st.columns([1, 1])
            if col_v.button("✅ Validar", key="val_d", use_container_width=True):
                st.session_state['res_docx']['valid'] = True
                st.rerun()
            if col_r.button("🧠 Refazer (+Profundo)", key="redo_d", use_container_width=True):
                with st.spinner("Refazendo com análise mais profunda..."):
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
                    if im:
                        st.image(im, width=300)
                elif p.strip():
                    st.markdown(p.strip())
        
        c_down1, c_down2 = st.columns(2)
        docx = construir_docx_final(res['txt'], aluno, materia_d, res['map'], tipo_d)
        c_down1.download_button(
            "📥 BAIXAR DOCX (Editável)", 
            docx, 
            "Prova_Adaptada.docx", 
            "primary",
            use_container_width=True
        )
        
        pdf_bytes = criar_pdf_generico(res['txt'])
        c_down2.download_button(
            "📕 BAIXAR PDF (Visualização)", 
            pdf_bytes, 
            "Prova_Adaptada.pdf", 
            mime="application/pdf", 
            type="secondary",
            use_container_width=True
        )

def render_aba_adaptar_atividade(aluno, api_key):
    """Renderiza a aba de adaptação de atividade"""
    st.markdown("""
    <div class="pedagogia-box">
        <div class="pedagogia-title"><i class="ri-scissors-cut-line"></i> OCR & Adaptação Visual</div>
        Tire foto de uma atividade do livro ou caderno. A IA extrai o texto, 
        remove poluição visual e reestrutura o conteúdo para o nível do aluno.
    </div>
    """, unsafe_allow_html=True)
    
    # Dropdowns BNCC simplificados
    ano_bncc, disciplina_bncc, unidade_bncc, objeto_bncc, _ = criar_dropdowns_bncc_completos_melhorado(key_suffix="adaptar_atividade", mostrar_habilidades=False)
    
    st.markdown("---")

    # Layout simplificado
    c1, c2 = st.columns([1, 2])
    tipo_i = c1.selectbox("Tipo", ["Atividade", "Tarefa", "Exercício"], key="itp")
    arquivo_i = c2.file_uploader("Upload da Imagem/Foto", type=["png","jpg","jpeg"], key="fi")
    livro_prof = st.checkbox("📖 É foto do Livro do Professor? (A IA removerá as respostas)", value=False)
    
    # Definição automática baseada na BNCC
    materia_i = disciplina_bncc if disciplina_bncc else "Geral"
    tema_i = objeto_bncc if objeto_bncc else "Geral"
    
    if 'img_raw' not in st.session_state:
        st.session_state.img_raw = None
    
    if arquivo_i and arquivo_i.file_id != st.session_state.get('last_i'):
        st.session_state.last_i = arquivo_i.file_id
        st.session_state.img_raw = sanitizar_imagem(arquivo_i.getvalue())

    cropped_res = None
    if st.session_state.img_raw:
        st.markdown("### ✂️ Recorte (Selecione a área da questão)")
        img_pil = Image.open(BytesIO(st.session_state.img_raw))
        img_pil.thumbnail((800, 800))
        cropped_res = st_cropper(img_pil, realtime_update=True, box_color='#FF0000', aspect_ratio=None, key="crop_i")
        if cropped_res:
            st.image(cropped_res, width=200, caption="Área selecionada")

    st.markdown("---")

    if st.button("🚀 ADAPTAR ATIVIDADE", type="primary", key="btn_i", use_container_width=True):
        if not st.session_state.img_raw:
            st.warning("Por favor, envie uma imagem.")
            st.stop()
        
        # Validação BNCC
        if not disciplina_bncc or not objeto_bncc:
             st.warning("⚠️ Selecione a Disciplina e o Objeto do Conhecimento (BNCC) acima.")
             st.stop()

        with st.spinner("Lendo imagem e adaptando conteúdo..."):
            buf_c = BytesIO()
            cropped_res.convert('RGB').save(buf_c, format="JPEG", quality=90)
            img_bytes = buf_c.getvalue()
            rac, txt = adaptar_conteudo_imagem(api_key, aluno, img_bytes, materia_i, tema_i, tipo_i, livro_prof)
            st.session_state['res_img'] = {'rac': rac, 'txt': txt, 'map': {1: img_bytes}, 'valid': False}
            st.rerun()

    if 'res_img' in st.session_state:
        res = st.session_state['res_img']
        if res.get('valid'):
            st.success("✅ **ATIVIDADE VALIDADA E PRONTA PARA USO**")
        else:
            col_v, col_r = st.columns([1, 1])
            if col_v.button("✅ Validar", key="val_i", use_container_width=True):
                st.session_state['res_img']['valid'] = True
                st.rerun()
            if col_r.button("🧠 Refazer (+Profundo)", key="redo_i", use_container_width=True):
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
                    if im:
                        st.image(im, width=300)
                elif p.strip():
                    st.markdown(p.strip())
        
        c_down1, c_down2 = st.columns(2)
        docx = construir_docx_final(res['txt'], aluno, materia_i, res['map'], tipo_i)
        c_down1.download_button("📥 BAIXAR DOCX (Editável)", docx, "Atividade.docx", "primary", use_container_width=True)
        
        pdf_bytes = criar_pdf_generico(res['txt'])
        c_down2.download_button(
            "📕 BAIXAR PDF (Visualização)", 
            pdf_bytes, 
            "Atividade.pdf", 
            mime="application/pdf", 
            type="secondary",
            use_container_width=True
        )

def render_aba_criar_do_zero(aluno, api_key, unsplash_key):
    """Renderiza a aba de criação do zero"""
    st.markdown("""
    <div class="pedagogia-box">
        <div class="pedagogia-title"><i class="ri-magic-line"></i> Criação com DUA</div>
        Crie atividades do zero alinhadas ao PEI. A IA gera questões contextualizadas, 
        usa o hiperfoco para engajamento e cria imagens ilustrativas automaticamente.
    </div>
    """, unsafe_allow_html=True)
    
    # Dropdowns BNCC completos
    ano_bncc, disciplina_bncc, unidade_bncc, objeto_bncc, habilidades_bncc = criar_dropdowns_bncc_completos_melhorado(key_suffix="criar_zero")
    
    # Mostrar resumo das seleções
    if unidade_bncc and objeto_bncc:
        with st.expander("📋 Resumo da seleção BNCC"):
            st.write(f"**Ano:** {ano_bncc}")
            st.write(f"**Disciplina:** {disciplina_bncc}")
            st.write(f"**Unidade Temática:** {unidade_bncc}")
            st.write(f"**Objeto do Conhecimento:** {objeto_bncc}")
            if habilidades_bncc:
                st.write(f"**Habilidades selecionadas:**")
                for i, hab in enumerate(habilidades_bncc, 1):
                    st.write(f"{i}. {hab}")
    
    # Usar os valores selecionados
    mat_c = disciplina_bncc
    obj_c = objeto_bncc
    
    # Configuração da atividade
    st.markdown("---")
    st.markdown("### ⚙️ Configuração da Atividade")
    
    cc3, cc4 = st.columns(2)
    with cc3:
        qtd_c = st.slider("Quantidade de Questões", 1, 10, 5, key="cq")
    
    with cc4:
        tipo_quest = st.selectbox("Tipo de Questão", ["Objetiva", "Discursiva"], key="ctq")
    
    # Configuração de imagens
    st.markdown("#### 🖼️ Imagens (Opcional)")
    col_img_opt, col_img_pct = st.columns([1, 2])
    
    with col_img_opt:
        usar_img = st.checkbox("Incluir Imagens?", value=True, key="usar_img")
    
    with col_img_pct:
        qtd_img_sel = st.slider("Quantas questões terão imagens?", 0, qtd_c, 
                               int(qtd_c/2) if qtd_c > 1 else 0, 
                               disabled=not usar_img,
                               key="qtd_img_slider")
    
    # Taxonomia de Bloom
    st.markdown("---")
    st.markdown("#### 🧠 Intencionalidade Pedagógica (Taxonomia de Bloom)")
    
    if 'bloom_memoria' not in st.session_state:
        st.session_state.bloom_memoria = {cat: [] for cat in TAXONOMIA_BLOOM.keys()}
    
    verbos_finais_para_ia = []
    
    usar_bloom = st.checkbox("🎯 Usar Taxonomia de Bloom (Revisada)", key="usar_bloom")
    
    if usar_bloom:
        col_b1, col_b2 = st.columns(2)
        
        with col_b1:
            cat_atual = st.selectbox("Categoria Cognitiva:", list(TAXONOMIA_BLOOM.keys()),
                                    key="cat_bloom")
        
        with col_b2:
            selecao_atual = st.multiselect(
                f"Verbos de '{cat_atual}':", 
                TAXONOMIA_BLOOM[cat_atual],
                default=st.session_state.bloom_memoria[cat_atual],
                key=f"ms_bloom_{cat_atual}"
            )
            
            st.session_state.bloom_memoria[cat_atual] = selecao_atual
        
        for cat in st.session_state.bloom_memoria:
            verbos_finais_para_ia.extend(st.session_state.bloom_memoria[cat])
        
        if verbos_finais_para_ia:
            st.info(f"**Verbos Selecionados:** {', '.join(verbos_finais_para_ia)}")
        else:
            st.caption("Nenhum verbo selecionado ainda.")
    
    # Botão para gerar
    st.markdown("---")
    col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 1])
    
    with col_btn2:
        if st.button("✨ CRIAR ATIVIDADE", type="primary", key="btn_c", use_container_width=True):
            if not api_key:
                st.error("❌ Insira a chave da OpenAI nas configurações")
            else:
                with st.spinner("Elaborando atividade..."):
                    qtd_final = qtd_img_sel if usar_img else 0
                    
                    rac, txt = criar_profissional(
                        api_key, 
                        aluno, 
                        mat_c, 
                        obj_c, 
                        qtd_c, 
                        tipo_quest, 
                        qtd_final, 
                        verbos_bloom=verbos_finais_para_ia if usar_bloom else None,
                        habilidades_bncc=habilidades_bncc
                    )
                    
                    # Processar imagens se houver
                    novo_map = {}
                    count = 0
                    tags = re.findall(r'\[\[GEN_IMG: (.*?)\]\]', txt)
                    
                    for p in tags:
                        count += 1
                        url = gerar_imagem_inteligente(api_key, p, unsplash_key, prioridade="BANCO")
                        if url:
                            io = baixar_imagem_url(url)
                            if io: 
                                novo_map[count] = io.getvalue()
                    
                    # Substituir tags GEN_IMG por IMG_G
                    txt_fin = txt
                    for i in range(1, count + 1): 
                        txt_fin = re.sub(r'\[\[GEN_IMG: .*?\]\]', f"[[IMG_G{i}]]", txt_fin, count=1)
                    
                    # Salvar no session state
                    st.session_state['res_create'] = {
                        'rac': rac, 
                        'txt': txt_fin, 
                        'map': novo_map, 
                        'valid': False,
                        'mat_c': mat_c,
                        'obj_c': obj_c
                    }
                    st.rerun()
    
    # Exibição do resultado
    if 'res_create' in st.session_state:
        res = st.session_state['res_create']
        
        st.markdown("---")
        st.markdown(f"### 📋 Atividade Criada: {res.get('mat_c', '')} - {res.get('obj_c', '')}")
        
        # Barra de status
        if res.get('valid'):
            st.success("✅ **ATIVIDADE VALIDADA E PRONTA PARA USO**")
        else:
            col_val, col_ajust, col_desc = st.columns(3)
            with col_val:
                if st.button("✅ Validar Atividade", key="val_c", use_container_width=True):
                    st.session_state['res_create']['valid'] = True
                    st.rerun()
            with col_ajust:
                if st.button("🔄 Refazer com Ajustes", key="redo_c", use_container_width=True):
                    st.session_state['res_create']['valid'] = False
                    st.info("Para ajustes, modifique os parâmetros acima e clique em 'CRIAR ATIVIDADE' novamente.")
            with col_desc:
                if st.button("🗑️ Descartar", key="del_c", use_container_width=True):
                    del st.session_state['res_create']
                    st.rerun()
        
        # Análise Pedagógica
        if res.get('rac'):
            with st.expander("🧠 Análise Pedagógica (clique para expandir)"):
                st.markdown(res['rac'])
        
        # Atividade Gerada
        st.markdown("#### 📝 Atividade Gerada")
        with st.container(border=True):
            partes = re.split(r'(\[\[IMG_G\d+\]\])', res['txt'])
            for p in partes:
                tag = re.search(r'\[\[IMG_G(\d+)\]\]', p)
                if tag:
                    i = int(tag.group(1))
                    im = res['map'].get(i)
                    if im: 
                        st.image(im, width=300)
                elif p.strip(): 
                    st.markdown(p.strip())
        
        # Botões de Download
        st.markdown("---")
        st.markdown("### 📥 Download")
        col_down1, col_down2, col_down3 = st.columns(3)
        
        with col_down1:
            docx = construir_docx_final(res['txt'], aluno, mat_c, {}, "Criada")
            st.download_button(
                label="📄 Baixar DOCX",
                data=docx,
                file_name=f"Atividade_{mat_c}_{date.today().strftime('%Y%m%d')}.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                use_container_width=True
            )
        
        with col_down2:
            pdf_bytes = criar_pdf_generico(res['txt'])
            st.download_button(
                label="📕 Baixar PDF",
                data=pdf_bytes,
                file_name=f"Atividade_{mat_c}_{date.today().strftime('%Y%m%d')}.pdf",
                mime="application/pdf",
                use_container_width=True
            )
        
        with col_down3:
            st.download_button(
                label="📝 Baixar Texto",
                data=res['txt'],
                file_name=f"Atividade_{mat_c}_{date.today().strftime('%Y%m%d')}.txt",
                mime="text/plain",
                use_container_width=True
            )

def render_aba_estudio_visual(aluno, api_key, unsplash_key):
    """Renderiza a aba de estúdio visual"""
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
                st.session_state.res_scene_url = gerar_imagem_inteligente(api_key, prompt_completo, unsplash_key, prioridade="IA")
                st.session_state.valid_scene = False

        if st.session_state.res_scene_url:
            st.image(st.session_state.res_scene_url)
            if st.session_state.valid_scene:
                st.success("Imagem validada!")
            else:
                c_vs1, c_vs2 = st.columns([1, 2])
                if c_vs1.button("✅ Validar", key="val_sc_pd"):
                    st.session_state.valid_scene = True
                    st.rerun()
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
                if c_vc1.button("✅ Validar", key="val_caa_pd"):
                    st.session_state.valid_caa = True
                    st.rerun()
                with c_vc2.expander("🔄 Refazer Picto"):
                    fb_caa = st.text_input("Ajuste:", key="fb_caa_pd")
                    if st.button("Refazer", key="ref_caa_pd"):
                        with st.spinner("Recriando..."):
                            st.session_state.res_caa_url = gerar_pictograma_caa(api_key, palavra_chave, feedback_anterior=fb_caa)
                            st.rerun()

def render_aba_roteiro_individual(aluno, api_key):
    """Renderiza a aba de roteiro individual"""
    st.markdown("""
    <div class="pedagogia-box">
        <div class="pedagogia-title"><i class="ri-user-follow-line"></i> Roteiro de Aula Individualizado</div>
        Crie um passo a passo de aula <strong>específico para este estudante</strong> do PEI. 
        A IA usará o hiperfoco como chave de acesso para o conteúdo selecionado na BNCC.
    </div>
    """, unsafe_allow_html=True)
    
    # Dropdowns BNCC completos
    ano_bncc, disciplina_bncc, unidade_bncc, objeto_bncc, habilidades_bncc = criar_dropdowns_bncc_completos_melhorado(key_suffix="roteiro")
    
    # Mostrar resumo das seleções
    if unidade_bncc and objeto_bncc:
        with st.expander("📋 Resumo da seleção BNCC"):
            st.write(f"**Ano:** {ano_bncc}")
            st.write(f"**Disciplina:** {disciplina_bncc}")
            st.write(f"**Unidade Temática:** {unidade_bncc}")
            st.write(f"**Objeto do Conhecimento:** {objeto_bncc}")
            if habilidades_bncc:
                st.write(f"**Habilidades selecionadas:**")
                for i, hab in enumerate(habilidades_bncc, 1):
                    st.write(f"{i}. {hab}")
    
    # Botão para gerar
    st.markdown("---")
    
    if st.button("📝 GERAR ROTEIRO INDIVIDUAL", type="primary", use_container_width=True):
        # Validação: Usa o objeto_bncc como assunto
        if objeto_bncc and habilidades_bncc:
            with st.spinner(f"Criando roteiro sobre '{objeto_bncc}'..."):
                res = gerar_roteiro_aula_completo(
                    api_key=api_key,
                    aluno=aluno,
                    materia=disciplina_bncc,
                    assunto=objeto_bncc, # Passa o objeto BNCC como assunto
                    habilidades_bncc=habilidades_bncc,
                    verbos_bloom=None, # Bloom removido
                    ano=ano_bncc,
                    unidade_tematica=unidade_bncc,
                    objeto_conhecimento=objeto_bncc
                )
                st.session_state['res_roteiro'] = res
                st.session_state['res_roteiro_valid'] = False
        else:
            st.warning("⚠️ Para gerar o roteiro, selecione a 'Disciplina', 'Objeto do Conhecimento' e pelo menos uma 'Habilidade' nos campos da BNCC acima.")
    
    # Exibição do resultado
    if 'res_roteiro' in st.session_state:
        res = st.session_state['res_roteiro']
        
        st.markdown("---")
        st.markdown("### 📋 Roteiro de Aula Individualizado")
        
        if st.session_state.get('res_roteiro_valid'):
            st.success("✅ **ROTEIRO VALIDADO E PRONTO PARA USO**")
        else:
            col_val, col_ajust, col_desc = st.columns(3)
            with col_val:
                if st.button("✅ Validar Roteiro", key="val_roteiro", use_container_width=True):
                    st.session_state['res_roteiro_valid'] = True
                    st.rerun()
            with col_ajust:
                if st.button("🔄 Refazer com Ajustes", key="redo_roteiro", use_container_width=True):
                    st.session_state['res_roteiro_valid'] = False
                    st.info("Para ajustes, modifique as seleções da BNCC e clique em 'GERAR ROTEIRO' novamente.")
            with col_desc:
                if st.button("🗑️ Descartar", key="del_roteiro", use_container_width=True):
                    del st.session_state['res_roteiro']
                    del st.session_state['res_roteiro_valid']
                    st.rerun()
        
        # Roteiro Gerado
        st.markdown(res)
        
        # Botões de Download
        st.markdown("---")
        st.markdown("### 📥 Download")
        col_down1, col_down2 = st.columns(2)
        
        with col_down1:
            docx_roteiro = criar_docx_simples(res, "Roteiro Individual")
            st.download_button(
                label="📄 Baixar DOCX",
                data=docx_roteiro,
                file_name=f"Roteiro_{disciplina_bncc}_{date.today().strftime('%Y%m%d')}.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                use_container_width=True
            )
        
        with col_down2:
            pdf_bytes_roteiro = criar_pdf_generico(res)
            st.download_button(
                label="📕 Baixar PDF",
                data=pdf_bytes_roteiro,
                file_name=f"Roteiro_{disciplina_bncc}_{date.today().strftime('%Y%m%d')}.pdf",
                mime="application/pdf",
                use_container_width=True
            )

def render_aba_papo_mestre(aluno, api_key):
    """Renderiza a aba de papo de mestre"""
    st.markdown("""
    <div class="pedagogia-box">
        <div class="pedagogia-title"><i class="ri-chat-smile-2-line"></i> Engajamento & DUA (Papo de Mestre)</div>
        O hiperfoco é um <strong>caminho neurológico</strong> já aberto. Use-o para conectar o aluno à matéria.
        Aqui você também pode adicionar um tema de interesse da turma toda (DUA) para criar conexões coletivas.
    </div>
    """, unsafe_allow_html=True)
    
    c1, c2 = st.columns(2)
    materia_papo = c1.selectbox("Componente", DISCIPLINAS_PADRAO, key="papo_mat")
    assunto_papo = c2.text_input("Assunto da Aula:", key="papo_ass")
    
    c3, c4 = st.columns(2)
    hiperfoco_papo = c3.text_input("Hiperfoco (Aluno):", value=aluno.get('hiperfoco', 'Geral'), key="papo_hip")
    tema_turma = c4.text_input("Interesse da Turma (Opcional - DUA):", placeholder="Ex: Minecraft, Copa do Mundo...", key="papo_turma")
    
    if st.button("🗣️ CRIAR CONEXÕES", type="primary"): 
        if assunto_papo:
            res = gerar_quebra_gelo_profundo(api_key, aluno, materia_papo, assunto_papo, hiperfoco_papo, tema_turma)
            st.session_state['res_papo'] = res
            st.session_state['res_papo_valid'] = False
        else:
            st.warning("Preencha o Assunto.")
    
    if 'res_papo' in st.session_state:
        res = st.session_state['res_papo']
        
        st.markdown("---")
        st.markdown("### 🗣️ Conexões para Engajamento")
        
        if st.session_state.get('res_papo_valid'):
            st.success("✅ **CONEXÕES VALIDADAS E PRONTAS PARA USO**")
        else:
            col_val, col_ajust, col_desc = st.columns(3)
            with col_val:
                if st.button("✅ Validar Conexões", key="val_papo", use_container_width=True):
                    st.session_state['res_papo_valid'] = True
                    st.rerun()
            with col_ajust:
                if st.button("🔄 Refazer com Ajustes", key="redo_papo", use_container_width=True):
                    st.session_state['res_papo_valid'] = False
                    st.info("Para ajustes, modifique os parâmetros acima e clique em 'CRIAR CONEXÕES' novamente.")
            with col_desc:
                if st.button("🗑️ Descartar", key="del_papo", use_container_width=True):
                    del st.session_state['res_papo']
                    del st.session_state['res_papo_valid']
                    st.rerun()
        
        st.markdown(res)
        
        # Botões de Download
        st.markdown("---")
        st.markdown("### 📥 Download")
        col_down1, col_down2 = st.columns(2)
        
        with col_down1:
            docx_papo = criar_docx_simples(res, "Papo de Mestre")
            st.download_button(
                label="📄 Baixar DOCX",
                data=docx_papo,
                file_name=f"Papo_Mestre_{date.today().strftime('%Y%m%d')}.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                use_container_width=True
            )
        
        with col_down2:
            pdf_bytes_papo = criar_pdf_generico(res)
            st.download_button(
                label="📕 Baixar PDF",
                data=pdf_bytes_papo,
                file_name=f"Papo_Mestre_{date.today().strftime('%Y%m%d')}.pdf",
                mime="application/pdf",
                use_container_width=True
            )

def render_aba_dinamica_inclusiva(aluno, api_key):
    """Renderiza a aba de dinâmica inclusiva"""
    st.markdown("""
    <div class="pedagogia-box">
        <div class="pedagogia-title"><i class="ri-group-line"></i> Dinâmica Inclusiva</div>
        Atividades em grupo onde todos participam, respeitando as singularidades.
        Baseado no Objeto do Conhecimento selecionado.
    </div>
    """, unsafe_allow_html=True)
    
    # Dropdowns BNCC completos
    ano_bncc, disciplina_bncc, unidade_bncc, objeto_bncc, habilidades_bncc = criar_dropdowns_bncc_completos_melhorado(key_suffix="dinamica")
    
    # Mostrar resumo das seleções
    if unidade_bncc and objeto_bncc:
        with st.expander("📋 Resumo da seleção BNCC"):
            st.write(f"**Ano:** {ano_bncc}")
            st.write(f"**Disciplina:** {disciplina_bncc}")
            st.write(f"**Unidade Temática:** {unidade_bncc}")
            st.write(f"**Objeto do Conhecimento:** {objeto_bncc}")
            if habilidades_bncc:
                st.write(f"**Habilidades selecionadas:**")
                for i, hab in enumerate(habilidades_bncc, 1):
                    st.write(f"{i}. {hab}")
    
    # Configuração (Simplificada)
    st.markdown("---")
    st.markdown("### ⚙️ Configuração da Turma")
    
    c3, c4 = st.columns(2)
    with c3:
        qtd_alunos = st.number_input("Número de Alunos:", min_value=5, max_value=50, value=25, key="din_qtd")
    with c4:
        carac_turma = st.text_input(
            "Características da Turma (Opcional):", 
            placeholder="Ex: Turma agitada, gostam de competição...", 
            key="din_carac"
        )
    
    # Botão para gerar
    st.markdown("---")
    
    if st.button("🤝 CRIAR DINÂMICA", type="primary", use_container_width=True): 
        if objeto_bncc and habilidades_bncc:
            with st.spinner(f"Criando dinâmica sobre '{objeto_bncc}'..."):
                res = gerar_dinamica_inclusiva_completa(
                    api_key=api_key,
                    aluno=aluno,
                    materia=disciplina_bncc,
                    assunto=objeto_bncc, # Passa o objeto BNCC como assunto
                    qtd_alunos=qtd_alunos,
                    caracteristicas_turma=carac_turma,
                    habilidades_bncc=habilidades_bncc,
                    verbos_bloom=None, # Bloom Removido
                    ano=ano_bncc,
                    unidade_tematica=unidade_bncc,
                    objeto_conhecimento=objeto_bncc
                )
                st.session_state['res_dinamica'] = res
                st.session_state['res_dinamica_valid'] = False
        else:
            st.warning("⚠️ Selecione a 'Disciplina', 'Objeto do Conhecimento' e pelo menos uma 'Habilidade' nos campos da BNCC acima.")
    
    # Exibição do resultado
    if 'res_dinamica' in st.session_state:
        res = st.session_state['res_dinamica']
        
        st.markdown("---")
        st.markdown("### 📋 Dinâmica Inclusiva")
        
        if st.session_state.get('res_dinamica_valid'):
            st.success("✅ **DINÂMICA VALIDADA E PRONTA PARA USO**")
        else:
            col_val, col_ajust, col_desc = st.columns(3)
            with col_val:
                if st.button("✅ Validar Dinâmica", key="val_dinamica", use_container_width=True):
                    st.session_state['res_dinamica_valid'] = True
                    st.rerun()
            with col_ajust:
                if st.button("🔄 Refazer com Ajustes", key="redo_dinamica", use_container_width=True):
                    st.session_state['res_dinamica_valid'] = False
                    st.info("Para ajustes, modifique os parâmetros e clique em 'CRIAR DINÂMICA' novamente.")
            with col_desc:
                if st.button("🗑️ Descartar", key="del_dinamica", use_container_width=True):
                    del st.session_state['res_dinamica']
                    del st.session_state['res_dinamica_valid']
                    st.rerun()
        
        st.markdown(res)
        
        # Botões de Download
        st.markdown("---")
        st.markdown("### 📥 Download")
        col_down1, col_down2 = st.columns(2)
        
        with col_down1:
            docx_din = criar_docx_simples(res, "Dinâmica Inclusiva")
            st.download_button(
                label="📄 Baixar DOCX",
                data=docx_din,
                file_name=f"Dinamica_{disciplina_bncc}_{date.today().strftime('%Y%m%d')}.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                use_container_width=True
            )
        
        with col_down2:
            pdf_bytes_din = criar_pdf_generico(res)
            st.download_button(
                label="📕 Baixar PDF",
                data=pdf_bytes_din,
                file_name=f"Dinamica_{disciplina_bncc}_{date.today().strftime('%Y%m%d')}.pdf",
                mime="application/pdf",
                use_container_width=True
            )

def render_aba_plano_aula(aluno, api_key):
    """Renderiza a aba de plano de aula"""
    st.markdown("""
    <div class="pedagogia-box">
        <div class="pedagogia-title"><i class="ri-book-open-line"></i> Plano de Aula DUA</div>
        Gere um planejamento completo alinhado à BNCC, selecionando metodologias ativas e recursos.
    </div>
    """, unsafe_allow_html=True)
    
    # Dropdowns BNCC completos
    ano_bncc, disciplina_bncc, unidade_bncc, objeto_bncc, habilidades_bncc = criar_dropdowns_bncc_completos_melhorado(key_suffix="plano")
    
    # Mostrar resumo das seleções
    if unidade_bncc and objeto_bncc:
        with st.expander("📋 Resumo da seleção BNCC"):
            st.write(f"**Ano:** {ano_bncc}")
            st.write(f"**Disciplina:** {disciplina_bncc}")
            st.write(f"**Unidade Temática:** {unidade_bncc}")
            st.write(f"**Objeto do Conhecimento:** {objeto_bncc}")
            if habilidades_bncc:
                st.write(f"**Habilidades selecionadas:**")
                for i, hab in enumerate(habilidades_bncc, 1):
                    st.write(f"{i}. {hab}")
    
    # Configuração (Simplificada)
    st.markdown("---")
    st.markdown("### ⚙️ Configuração Metodológica")
    
    c1, c2 = st.columns(2)
    with c1:
        metodologia = st.selectbox("Metodologia", METODOLOGIAS, key="plano_met")
    
    tecnica_ativa = ""
    if metodologia == "Metodologia Ativa":
        with c2:
            tecnica_ativa = st.selectbox("Técnica Ativa", TECNICAS_ATIVAS, key="plano_tec")
    else:
        c2.info(f"Metodologia selecionada: {metodologia}")

    c3, c4 = st.columns(2)
    with c3:
        qtd_alunos_plano = st.number_input("Qtd Alunos:", min_value=1, value=30, key="plano_qtd")
    with c4:
        recursos_plano = st.multiselect("Recursos Disponíveis:", RECURSOS_DISPONIVEIS, key="plano_rec")
    
    # Botão para gerar
    st.markdown("---")
    
    if st.button("📅 GERAR PLANO DE AULA", type="primary", use_container_width=True):
        if objeto_bncc and habilidades_bncc:
            with st.spinner(f"Consultando BNCC e planejando aula sobre '{objeto_bncc}'..."):
                res = gerar_plano_aula_completo(
                    api_key=api_key,
                    materia=disciplina_bncc,
                    assunto=objeto_bncc, # Passa o objeto BNCC como assunto
                    metodologia=metodologia,
                    tecnica=tecnica_ativa,
                    qtd_alunos=qtd_alunos_plano,
                    recursos=recursos_plano,
                    habilidades_bncc=habilidades_bncc,
                    verbos_bloom=None, # Bloom Removido
                    ano=ano_bncc,
                    unidade_tematica=unidade_bncc,
                    objeto_conhecimento=objeto_bncc,
                    aluno_info=aluno
                )
                st.session_state['res_plano'] = res
                st.session_state['res_plano_valid'] = False
        else:
            st.warning("⚠️ Selecione a 'Disciplina', 'Objeto do Conhecimento' e pelo menos uma 'Habilidade' nos campos da BNCC acima.")
    
    # Exibição do resultado
    if 'res_plano' in st.session_state:
        res = st.session_state['res_plano']
        
        st.markdown("---")
        st.markdown("### 📋 Plano de Aula DUA")
        
        if st.session_state.get('res_plano_valid'):
            st.success("✅ **PLANO VALIDADO E PRONTO PARA USO**")
        else:
            col_val, col_ajust, col_desc = st.columns(3)
            with col_val:
                if st.button("✅ Validar Plano", key="val_plano", use_container_width=True):
                    st.session_state['res_plano_valid'] = True
                    st.rerun()
            with col_ajust:
                if st.button("🔄 Refazer com Ajustes", key="redo_plano", use_container_width=True):
                    st.session_state['res_plano_valid'] = False
                    st.info("Para ajustes, modifique os parâmetros e clique em 'GERAR PLANO' novamente.")
            with col_desc:
                if st.button("🗑️ Descartar", key="del_plano", use_container_width=True):
                    del st.session_state['res_plano']
                    del st.session_state['res_plano_valid']
                    st.rerun()
        
        st.markdown(res)
        
        # Botões de Download
        st.markdown("---")
        st.markdown("### 📥 Download")
        col_down1, col_down2 = st.columns(2)
        
        with col_down1:
            docx_plano = criar_docx_simples(res, "Plano de Aula DUA")
            st.download_button(
                label="📄 Baixar DOCX",
                data=docx_plano,
                file_name=f"Plano_Aula_{disciplina_bncc}_{date.today().strftime('%Y%m%d')}.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                use_container_width=True
            )
        
        with col_down2:
            pdf_bytes_plano = criar_pdf_generico(res)
            st.download_button(
                label="📕 Baixar PDF",
                data=pdf_bytes_plano,
                file_name=f"Plano_Aula_{disciplina_bncc}_{date.today().strftime('%Y%m%d')}.pdf",
                mime="application/pdf",
                use_container_width=True
            )
    # ==============================================================================
# FUNÇÕES DA EDUCAÇÃO INFANTIL
# ==============================================================================

def render_aba_ei_experiencia(aluno, api_key):
    """Renderiza a aba de experiência da Educação Infantil"""
    st.markdown("""
    <div class="pedagogia-box">
        <div class="pedagogia-title"><i class="ri-lightbulb-line"></i> Pedagogia do Brincar (BNCC)</div>
        Na Educação Infantil, não fazemos "provas". Criamos <strong>experiências de aprendizagem</strong> intencionais. 
        Esta ferramenta usa a BNCC para criar brincadeiras que ensinam, usando o hiperfoco da criança.
    </div>
    """, unsafe_allow_html=True)
    
    col_ei1, col_ei2 = st.columns(2)
    campo_exp = col_ei1.selectbox("Campo de Experiência (BNCC)", CAMPOS_EXPERIENCIA_EI, key="campo_exp_ei")
    obj_aprendizagem = col_ei2.text_input("Objetivo de Aprendizagem:", placeholder="Ex: Compartilhar brinquedos, Identificar cores...", key="obj_aprendizagem_ei")
    
    if 'res_ei_exp' not in st.session_state:
        st.session_state.res_ei_exp = None
    if 'valid_ei_exp' not in st.session_state:
        st.session_state.valid_ei_exp = False

    if st.button("✨ GERAR EXPERIÊNCIA LÚDICA", type="primary", key="btn_exp_ei"):
        with st.spinner("Criando vivência..."):
            st.session_state.res_ei_exp = gerar_experiencia_ei_bncc(api_key, aluno, campo_exp=campo_exp, objetivo=obj_aprendizagem)
            st.session_state.valid_ei_exp = False

    if st.session_state.res_ei_exp:
        if st.session_state.valid_ei_exp:
            st.success("✅ EXPERIÊNCIA APROVADA!")
            st.markdown(st.session_state.res_ei_exp)
        else:
            st.markdown(st.session_state.res_ei_exp)
            st.write("---")
            c_val, c_ref = st.columns([1, 3])
            if c_val.button("✅ Validar Experiência", key="val_exp_ei"): 
                st.session_state.valid_ei_exp = True
                st.rerun()
            with c_ref.expander("🔄 Não gostou? Ensinar a IA"):
                feedback_ei = st.text_input("O que precisa melhorar?", placeholder="Ex: Ficou muito complexo, use materiais mais simples...", key="fb_exp_ei")
                if st.button("Refazer com Ajustes", key="refazer_exp_ei"):
                    with st.spinner("Reescrevendo..."):
                        st.session_state.res_ei_exp = gerar_experiencia_ei_bncc(api_key, aluno, campo_exp, obj_aprendizagem, feedback_anterior=feedback_ei)
                        st.rerun()

def render_aba_ei_estudio_visual(aluno, api_key, unsplash_key):
    """Renderiza a aba de estúdio visual da Educação Infantil"""
    st.markdown("""
    <div class="pedagogia-box">
        <div class="pedagogia-title"><i class="ri-eye-line"></i> Apoio Visual & Comunicação</div>
        Crianças atípicas processam melhor imagens do que fala. 
        Use <strong>Cenas</strong> para histórias sociais (comportamento) e <strong>Pictogramas (CAA)</strong> para comunicação.
    </div>
    """, unsafe_allow_html=True)
    
    col_scene, col_caa = st.columns(2)
    
    # Cenas
    with col_scene:
        st.markdown("#### 🖼️ Ilustração de Cena")
        desc_m = st.text_area("Descreva a cena ou rotina:", height=100, key="vdm_ei", placeholder="Ex: Crianças brincando de roda no parque...")
        
        if st.button("🎨 Gerar Cena", key="btn_cena_ei"):
            with st.spinner("Desenhando..."):
                prompt_completo = f"{desc_m}. Context: Child education, friendly style."
                st.session_state.res_scene_url = gerar_imagem_inteligente(api_key, prompt_completo, unsplash_key, prioridade="IA")
                st.session_state.valid_scene = False

        if st.session_state.res_scene_url:
            st.image(st.session_state.res_scene_url)
            if st.session_state.valid_scene:
                st.success("Imagem validada!")
            else:
                c_vs1, c_vs2 = st.columns([1, 2])
                if c_vs1.button("✅ Validar", key="val_sc_ei"):
                    st.session_state.valid_scene = True
                    st.rerun()
                with c_vs2.expander("🔄 Refazer Cena"):
                    fb_scene = st.text_input("Ajuste:", key="fb_sc_ei")
                    if st.button("Refazer", key="ref_sc_ei"):
                        with st.spinner("Redesenhando..."):
                            prompt_completo = f"{desc_m}. Context: Child education."
                            st.session_state.res_scene_url = gerar_imagem_inteligente(api_key, prompt_completo, unsplash_key, feedback_anterior=fb_scene, prioridade="IA")
                            st.rerun()

    # CAA
    with col_caa:
        st.markdown("#### 🗣️ Símbolo CAA (Comunicação)")
        palavra_chave = st.text_input("Conceito/Palavra:", placeholder="Ex: Quero Água, Banheiro", key="caa_input_ei")
        
        if st.button("🧩 Gerar Pictograma", key="btn_caa_ei"):
            with st.spinner("Criando símbolo acessível..."):
                st.session_state.res_caa_url = gerar_pictograma_caa(api_key, palavra_chave)
                st.session_state.valid_caa = False

        if st.session_state.res_caa_url:
            st.image(st.session_state.res_caa_url, width=300)
            if st.session_state.valid_caa:
                st.success("Pictograma validado!")
            else:
                c_vc1, c_vc2 = st.columns([1, 2])
                if c_vc1.button("✅ Validar", key="val_caa_ei"):
                    st.session_state.valid_caa = True
                    st.rerun()
                with c_vc2.expander("🔄 Refazer Picto"):
                    fb_caa = st.text_input("Ajuste:", key="fb_caa_ei")
                    if st.button("Refazer", key="ref_caa_ei"):
                        with st.spinner("Recriando..."):
                            st.session_state.res_caa_url = gerar_pictograma_caa(api_key, palavra_chave, feedback_anterior=fb_caa)
                            st.rerun()

def render_aba_ei_rotina(aluno, api_key):
    """Renderiza a aba de rotina da Educação Infantil"""
    st.markdown("""
    <div class="pedagogia-box">
        <div class="pedagogia-title"><i class="ri-calendar-check-line"></i> Rotina & Previsibilidade</div>
        A rotina organiza o pensamento da criança. Use esta ferramenta para identificar 
        pontos de estresse e criar estratégias de antecipação.
    </div>
    """, unsafe_allow_html=True)
    
    rotina_detalhada = st.text_area("Descreva a Rotina da Turma:", height=200, placeholder="Ex: \n8:00 - Chegada e Acolhida\n8:30 - Roda de Conversa\n9:00 - Lanche\n...", key="rotina_ei")
    topico_foco = st.text_input("Ponto de Atenção (Opcional):", placeholder="Ex: Transição para o parque", key="topico_foco_ei")
    
    if 'res_ei_rotina' not in st.session_state:
        st.session_state.res_ei_rotina = None
    if 'valid_ei_rotina' not in st.session_state:
        st.session_state.valid_ei_rotina = False

    if st.button("📝 ANALISAR E ADAPTAR ROTINA", type="primary", key="btn_rotina_ei"):
        with st.spinner("Analisando rotina..."):
            prompt_rotina = f"Analise esta rotina de Educação Infantil e sugira adaptações sensoriais e visuais:\n\n{rotina_detalhada}\n\nFoco específico: {topico_foco}"
            st.session_state.res_ei_rotina = gerar_roteiro_aula_completo(api_key, aluno, "Geral", "Rotina", feedback_anterior=prompt_rotina)
            st.session_state.valid_ei_rotina = False

    if st.session_state.res_ei_rotina:
        if st.session_state.valid_ei_rotina:
            st.success("✅ ROTINA VALIDADA!")
            st.markdown(st.session_state.res_ei_rotina)
        else:
            st.markdown(st.session_state.res_ei_rotina)
            st.write("---")
            c_val, c_ref = st.columns([1, 3])
            if c_val.button("✅ Validar Rotina", key="val_rotina_ei"):
                st.session_state.valid_ei_rotina = True
                st.rerun()
            with c_ref.expander("🔄 Refazer adaptação"):
                fb_rotina = st.text_input("O que ajustar na rotina?", key="fb_rotina_input_ei")
                if st.button("Refazer Rotina", key="refazer_rotina_ei"):
                    with st.spinner("Reajustando..."):
                        prompt_rotina = f"Analise esta rotina de Educação Infantil e sugira adaptações:\n\n{rotina_detalhada}\n\nFoco: {topico_foco}"
                        st.session_state.res_ei_rotina = gerar_roteiro_aula_completo(api_key, aluno, "Geral", "Rotina", feedback_anterior=prompt_rotina)
                        st.rerun()

def render_aba_ei_inclusao_brincar(aluno, api_key):
    """Renderiza a aba de inclusão no brincar da Educação Infantil"""
    st.markdown("""
    <div class="pedagogia-box">
        <div class="pedagogia-title"><i class="ri-group-line"></i> Mediação Social</div>
        Se a criança brinca isolada, o objetivo não é forçar a interação, mas criar 
        pontes através do interesse dela. A IA criará uma brincadeira onde ela é protagonista.
    </div>
    """, unsafe_allow_html=True)
    
    tema_d = st.text_input("Tema/Momento:", key="dina_ei", placeholder="Ex: Brincadeira de massinha")
    
    if 'res_ei_dina' not in st.session_state:
        st.session_state.res_ei_dina = None
    if 'valid_ei_dina' not in st.session_state:
        st.session_state.valid_ei_dina = False

    if st.button("🤝 GERAR DINÂMICA", type="primary", key="btn_dina_ei"): 
        with st.spinner("Criando ponte social..."):
            st.session_state.res_ei_dina = gerar_dinamica_inclusiva_completa(
                api_key, 
                aluno, 
                "Educação Infantil", 
                tema_d, 
                10,  # pequeno grupo
                "Crianças pequenas"
            )
            st.session_state.valid_ei_dina = False

    if st.session_state.res_ei_dina:
        if st.session_state.valid_ei_dina:
            st.success("✅ DINÂMICA VALIDADA!")
            st.markdown(st.session_state.res_ei_dina)
        else:
            st.markdown(st.session_state.res_ei_dina)
            st.write("---")
            c_val, c_ref = st.columns([1, 3])
            if c_val.button("✅ Validar Dinâmica", key="val_dina_ei"):
                st.session_state.valid_ei_dina = True
                st.rerun()
            with c_ref.expander("🔄 Refazer dinâmica"):
                fb_dina = st.text_input("O que ajustar?", key="fb_dina_input_ei")
                if st.button("Refazer Dinâmica", key="refazer_dina_ei"):
                    with st.spinner("Reajustando..."):
                        st.session_state.res_ei_dina = gerar_dinamica_inclusiva_completa(
                            api_key, 
                            aluno, 
                            "Educação Infantil", 
                            tema_d, 
                            10, 
                            "Crianças pequenas", 
                            feedback_anterior=fb_dina
                        )
                        st.rerun()

# ==============================================================================
# EXECUÇÃO PRINCIPAL
# ==============================================================================

# ==============================================================================
# VERIFICAÇÃO DE ACESSO
# ==============================================================================
def verificar_acesso():
    """Verifica se o usuário está autenticado"""
    if "autenticado" not in st.session_state or not st.session_state["autenticado"]:
        st.error("🔒 Acesso Negado. Por favor, faça login na Página Inicial.")
        st.stop()

verificar_acesso()

# ==============================================================================
# FUNÇÃO PRINCIPAL
# ==============================================================================
def main():
    """Função principal da aplicação - executa a lógica do Hub"""
    
    # Inicializar api_key antes de usar
    if 'OPENAI_API_KEY' in st.secrets:
        api_key = st.secrets['OPENAI_API_KEY']
    elif 'OPENAI_API_KEY' in st.session_state:
        api_key = st.session_state['OPENAI_API_KEY']
    else:
        api_key = None
    
    # Configurações de API (movidas da sidebar para expander no conteúdo principal)
    with st.expander("⚙️ Configurações de API", expanded=False):
        col_api1, col_api2 = st.columns(2)
        with col_api1:
            if 'OPENAI_API_KEY' in st.secrets:
                st.success("✅ OpenAI OK")
            else:
                api_key_input = st.text_input("Chave OpenAI:", type="password", key="openai_key")
                if api_key_input:
                    api_key = api_key_input
                    st.session_state['OPENAI_API_KEY'] = api_key
        
        with col_api2:
            if 'UNSPLASH_ACCESS_KEY' in st.secrets:
                unsplash_key = st.secrets['UNSPLASH_ACCESS_KEY']
                st.success("✅ Unsplash OK")
            else:
                unsplash_key = st.text_input("Chave Unsplash (Opcional):", type="password", key="unsplash_key")
                if unsplash_key:
                    st.session_state['UNSPLASH_ACCESS_KEY'] = unsplash_key
        
        if st.button("🧹 Limpar Tudo e Reiniciar", type="secondary"):
            for key in list(st.session_state.keys()):
                if key not in ['banco_estudantes', 'OPENAI_API_KEY', 'UNSPLASH_ACCESS_KEY', 'autenticado']:
                    del st.session_state[key]
            st.rerun()
    
    # Carregar dados dos alunos
    if 'banco_estudantes' not in st.session_state or not st.session_state.banco_estudantes:
        with st.spinner("🔄 Lendo dados da nuvem..."):
            st.session_state.banco_estudantes = carregar_estudantes_supabase()
    
    if not st.session_state.banco_estudantes:
        st.warning("⚠️ Nenhum aluno encontrado.")
        if st.button("📘 Ir para o módulo PEI", type="primary"): 
            st.switch_page("pages/1_PEI.py")
        st.stop()
    
    # Seleção de aluno
    lista_alunos = [a['nome'] for a in st.session_state.banco_estudantes]
    col_sel, col_info = st.columns([1, 2])
    with col_sel:
        nome_aluno = st.selectbox("📂 Selecione o Estudante:", lista_alunos)
    
    aluno = next((a for a in st.session_state.banco_estudantes if a.get('nome') == nome_aluno), None)
    
    if not aluno: 
        st.error("Aluno não encontrado")
        st.stop()
    
    # --- ÁREA DO ALUNO (Visual + Expander) ---
    
    # 1. Cabeçalho Visual (Nome e Série - Mantém visível para contexto rápido)
    render_cabecalho_aluno(aluno)
    
    # 2. PEI RETRÁTIL (Aqui está a mudança solicitada)
    # Mostra os detalhes pesados apenas se o usuário clicar
    with st.expander(f"📄 Ver Detalhes do PEI e Diagnóstico de {aluno['nome'].split()[0]}", expanded=False):
        
        c_diag, c_hip = st.columns(2)
        with c_diag:
            st.markdown(f"**🏥 Diagnóstico/CID:**")
            st.info(aluno.get('diagnosis', 'Não informado'))
            
        with c_hip:
            st.markdown(f"**🎯 Hiperfoco/Interesses:**")
            st.success(aluno.get('hiperfoco', 'Geral'))
            
        st.markdown("---")
        st.markdown("**🧠 Resumo das Estratégias (IA):**")
        # Mostra o texto da IA (ia_sugestao) formatado
        st.write(aluno.get('ia_sugestao', 'Sem resumo disponível.'))

    # --- FIM DA ÁREA DO ALUNO ---

    # Detector de Educação Infantil
    serie_aluno = aluno.get('serie', '').lower()
    is_ei = any(termo in serie_aluno for termo in ["infantil", "creche", "pré", "pre", "maternal", "berçário"])
    
    # Inicializar estado para imagens
    if 'res_scene_url' not in st.session_state:
        st.session_state.res_scene_url = None
    if 'valid_scene' not in st.session_state:
        st.session_state.valid_scene = False
    if 'res_caa_url' not in st.session_state:
        st.session_state.res_caa_url = None
    if 'valid_caa' not in st.session_state:
        st.session_state.valid_caa = False
    
    if is_ei:
        # Modo Educação Infantil
        st.info("🧸 **Modo Educação Infantil Ativado:** Foco em Experiências, BNCC e Brincar.")
        
        tabs = st.tabs(["🧸 Criar Experiência (BNCC)", "🎨 Estúdio Visual & CAA", "📝 Rotina & AVD", "🤝 Inclusão no Brincar"])
        
        with tabs[0]:
            render_aba_ei_experiencia(aluno, api_key)
        
        with tabs[1]:
            render_aba_ei_estudio_visual(aluno, api_key, unsplash_key)
        
        with tabs[2]:
            render_aba_ei_rotina(aluno, api_key)
        
        with tabs[3]:
            render_aba_ei_inclusao_brincar(aluno, api_key)
    
    else:
        # Modo Padrão (Fundamental / Médio)
        tabs = st.tabs([
            "📄 Adaptar Prova", 
            "✂️ Adaptar Atividade", 
            "✨ Criar do Zero", 
            "🎨 Estúdio Visual & CAA", 
            "📝 Roteiro Individual", 
            "🗣️ Papo de Mestre", 
            "🤝 Dinâmica Inclusiva", 
            "📅 Plano de Aula DUA"
        ])
        
        with tabs[0]:
            render_aba_adaptar_prova(aluno, api_key)
        
        with tabs[1]:
            render_aba_adaptar_atividade(aluno, api_key)
        
        with tabs[2]:
            render_aba_criar_do_zero(aluno, api_key, unsplash_key)

        with tabs[3]:
            render_aba_estudio_visual(aluno, api_key, unsplash_key)

        with tabs[4]:
            render_aba_roteiro_individual(aluno, api_key)

        with tabs[5]:
            render_aba_papo_mestre(aluno, api_key)

        with tabs[6]:
            render_aba_dinamica_inclusiva(aluno, api_key)

        with tabs[7]:
            render_aba_plano_aula(aluno, api_key)

# Executa a função principal
main()







    
