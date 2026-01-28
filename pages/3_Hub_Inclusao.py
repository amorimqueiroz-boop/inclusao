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
from omni_utils import get_icon, icon_title

# Importações OpenAI e ML
from openai import OpenAI

# Importações para documentos
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Pt, Inches, RGBColor
try:
    from docx.oxml.ns import qn
except ImportError:
    # Fallback se qn não estiver disponível
    qn = lambda x: x, RGBColor
from docx.oxml.ns import qn
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
    page_icon="omni_icone.png" if os.path.exists("omni_icone.png") else "📘",
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

            /* 2. Puxa todo o conteúdo para cima (O SEGREDO ESTÁ AQUI) - ESPECIFICIDADE MÁXIMA */
            body .main .block-container,
            body .block-container,
            .main .block-container,
            .block-container {
                padding-top: 0px !important; /* SEM espaço entre navbar e hero */
                padding-bottom: 1rem !important;
                margin-top: 0px !important;
            }
            
            /* 3. Remove qualquer espaçamento do Streamlit */
            [data-testid="stVerticalBlock"],
            div[data-testid="stVerticalBlock"] > div:first-child,
            .main .block-container > div:first-child,
            .main .block-container > *:first-child {
                padding-top: 0px !important;
                margin-top: 0px !important;
            }
            
            /* 4. Remove espaçamento do stMarkdown que renderiza o hero */
            .main .block-container > div:first-child .stMarkdown {
                margin-top: 0px !important;
                padding-top: 0px !important;
            }
            
            /* 5. Hero card colado no menu - margin negativo (ajustado para não ficar muito colado) */
            .mod-card-wrapper {
                margin-top: -96px !important; /* Puxa o hero para cima, mas não tanto quanto antes */
                position: relative;
                z-index: 1;
            }
            
            /* 6. Esconde o menu hambúrguer e rodapé */
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
    /* CARD HERO - PADRÃO */
    .mod-card-wrapper { 
        display: flex; 
        flex-direction: column; 
        margin-bottom: 4px; 
        /* margin-top já aplicado no forcar_layout_hub() - não duplicar aqui */
        border-radius: 16px; 
        overflow: hidden; 
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.02); 
        position: relative;
        z-index: 1;
    }
    .mod-card-rect { 
        background: white; 
        border-radius: 16px 16px 0 0; 
        padding: 0; 
        border: 1px solid #E2E8F0; 
        border-bottom: none; 
        display: flex; 
        flex-direction: row; 
        align-items: center; 
        height: 130px !important; 
        width: 100%; 
        position: relative; 
        overflow: hidden; 
        transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1); 
    }
    .mod-card-rect:hover { 
        transform: translateY(-4px); 
        box-shadow: 0 12px 24px rgba(0, 0, 0, 0.08); 
        border-color: #CBD5E1; 
    }
    .mod-bar { 
        width: 6px; 
        height: 100%; 
        flex-shrink: 0; 
    }
    .mod-icon-area { 
        width: 90px; 
        height: 100%; 
        display: flex; 
        align-items: center; 
        justify-content: center; 
        font-size: 1.8rem; 
        flex-shrink: 0; 
        background: #FAFAFA !important; 
        border-right: 1px solid #F1F5F9; 
        transition: all 0.3s ease; 
    }
    .mod-card-rect:hover .mod-icon-area { 
        background: white !important;
        transform: scale(1.05) !important;
    }
    .mod-content { 
        flex-grow: 1; 
        padding: 0 24px; 
        display: flex; 
        flex-direction: column; 
        justify-content: center; 
        min-width: 0;
        align-items: flex-start;
    }
    .mod-title { 
        font-weight: 800; 
        font-size: 1.1rem; 
        color: #1E293B; 
        margin-bottom: 6px; 
        letter-spacing: -0.3px; 
        transition: color 0.2s; 
    }
    .mod-desc { 
        font-size: 0.8rem; 
        color: #64748B; 
        line-height: 1.4; 
        display: -webkit-box; 
        -webkit-line-clamp: 2; 
        -webkit-box-orient: vertical; 
        overflow: hidden; 
    }
    
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
    .mod-card-rect:hover .mod-title {
        color: #0D9488; /* Specific hover color */
    }
</style>
""", unsafe_allow_html=True)

# Espaçamento após hero card
st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

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

# Lista de componentes curriculares padrão
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

def construir_docx_final(texto_ia, aluno, materia, mapa_imgs, tipo_atv, sem_cabecalho=False, checklist_adaptacao=None):
    """Constrói documento DOCX final com formatação melhorada baseada no checklist"""
    doc = Document()
    
    # Determinar formatação baseada no checklist
    usar_caixa_alta = False
    usar_opendyslexic = False
    espacamento_linhas = 1.5  # padrão
    
    if checklist_adaptacao:
        # Se precisa de adaptação visual, usar formatação especial
        if checklist_adaptacao.get("paragrafos_curtos") or not checklist_adaptacao.get("compreende_instrucoes_complexas"):
            usar_caixa_alta = True
            usar_opendyslexic = True
            espacamento_linhas = 1.8
    
    # Estilos personalizados
    style = doc.styles['Normal']
    if usar_opendyslexic:
        # Tentar usar OpenDyslexic, fallback para Arial se não disponível
        try:
            style.font.name = 'OpenDyslexic'
            # Tentar registrar fonte alternativa (pode não funcionar se fonte não estiver instalada)
            try:
                rFonts = style.element.rPr.rFonts
                if rFonts is not None:
                    rFonts.set(qn('w:ascii'), 'OpenDyslexic')
                    rFonts.set(qn('w:hAnsi'), 'OpenDyslexic')
            except:
                pass  # Se não conseguir registrar, continua com o nome
        except:
            style.font.name = 'Arial'
    else:
        style.font.name = 'Arial'
    
    style.font.size = Pt(14)  # Aumentado para melhor legibilidade
    style.paragraph_format.space_after = Pt(8)
    style.paragraph_format.line_spacing = espacamento_linhas
    
    if not sem_cabecalho:
        # Título principal
        titulo = doc.add_heading(f'{tipo_atv.upper()} ADAPTADA - {materia.upper()}', 0)
        titulo.alignment = WD_ALIGN_PARAGRAPH.CENTER
        if titulo.runs:
            titulo.runs[0].font.size = Pt(16)
            titulo.runs[0].bold = True
        
        # Informações do estudante
        p_estudante = doc.add_paragraph(f"Estudante: {aluno['nome']}")
        p_estudante.alignment = WD_ALIGN_PARAGRAPH.CENTER
        if p_estudante.runs:
            p_estudante.runs[0].font.size = Pt(11)
        
        # Linha separadora
        linha_sep = doc.add_paragraph("_"*50)
        linha_sep.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        # Título de seção
        secao = doc.add_heading('Atividades', level=2)
        if secao.runs:
            secao.runs[0].font.size = Pt(14)

    linhas = texto_ia.split('\n')
    for linha in linhas:
        linha_limpa = linha.strip()
        if not linha_limpa:
            # Linha vazia - adiciona espaço
            doc.add_paragraph()
            continue
            
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
                            # Espaço após imagem
                            doc.add_paragraph()
                        except Exception as e:
                            print(f"Erro ao adicionar imagem: {e}")
                elif parte.strip():
                    # Formatar texto com títulos e listas (passando parâmetros de formatação)
                    _adicionar_paragrafo_formatado(doc, parte.strip(), usar_caixa_alta, usar_opendyslexic, espacamento_linhas)
        else:
            # Formatar texto com títulos e listas (passando parâmetros de formatação)
            _adicionar_paragrafo_formatado(doc, linha_limpa, usar_caixa_alta, usar_opendyslexic, espacamento_linhas)
            
    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer

def _adicionar_paragrafo_formatado(doc, texto, usar_caixa_alta=False, usar_opendyslexic=False, espacamento=1.5):
    """Adiciona parágrafo formatado com detecção de títulos e listas"""
    try:
        # Aplicar caixa alta se necessário
        texto_formatado = texto.upper() if usar_caixa_alta else texto
        
        # Detectar títulos (começam com # ou são números seguidos de ponto)
        if re.match(r'^#{1,3}\s+', texto_formatado):
            nivel = len(re.match(r'^(#+)', texto_formatado).group(1))
            texto_limpo = re.sub(r'^#+\s+', '', texto_formatado)
            heading = doc.add_heading(texto_limpo, level=min(nivel, 3))
            if heading.runs:
                heading.runs[0].font.size = Pt(16 - nivel)
                if usar_opendyslexic:
                    heading.runs[0].font.name = 'OpenDyslexic'
        elif re.match(r'^\d+[\.\)]\s+', texto_formatado):
            # Lista numerada
            p = doc.add_paragraph(texto_formatado, style='List Number')
            if p.runs:
                p.runs[0].font.size = Pt(14)
                p.runs[0].font.name = 'OpenDyslexic' if usar_opendyslexic else 'Arial'
                p.paragraph_format.line_spacing = espacamento
        elif re.match(r'^[-•*]\s+', texto_formatado):
            # Lista com marcadores
            texto_limpo = re.sub(r'^[-•*]\s+', '', texto_formatado)
            p = doc.add_paragraph(texto_limpo, style='List Bullet')
            if p.runs:
                p.runs[0].font.size = Pt(14)
                p.runs[0].font.name = 'OpenDyslexic' if usar_opendyslexic else 'Arial'
                p.paragraph_format.line_spacing = espacamento
        elif texto_formatado.isupper() and len(texto_formatado) < 100:
            # Título em maiúsculas
            p = doc.add_paragraph(texto_formatado)
            if p.runs:
                p.runs[0].font.size = Pt(15)
                p.runs[0].bold = True
                p.runs[0].font.name = 'OpenDyslexic' if usar_opendyslexic else 'Arial'
                p.paragraph_format.line_spacing = espacamento
        else:
            # Texto normal
            p = doc.add_paragraph(texto_formatado)
            if p.runs:
                p.runs[0].font.size = Pt(14)
                p.runs[0].font.name = 'OpenDyslexic' if usar_opendyslexic else 'Arial'
                p.paragraph_format.line_spacing = espacamento
    except Exception as e:
        # Fallback: adiciona como parágrafo simples
        doc.add_paragraph(texto_formatado if usar_caixa_alta else texto)

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
        print(f"Erro ao carregar estudantes: {str(e)}")
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
        
        # 1. CAPTURA DO DIAGNÓSTICO 
        # Primeiro tenta dentro do pei_data (onde o PEI salva como "diagnostico")
        diagnostico_real = ""
        if isinstance(pei_completo, dict):
            diagnostico_real = pei_completo.get("diagnostico") or ""
        
        # Se não encontrou no pei_data, tenta da coluna do banco
        if not diagnostico_real:
            diagnostico_real = item.get("diagnosis") or ""
        
        # Se ainda não encontrou, mostra mensagem
        if not diagnostico_real:
            diagnostico_real = "Não informado no cadastro"

        # 2. CAPTURA DO HIPERFOCO (Vem APENAS de dentro do JSON pei_data)
        # IMPORTANTE: NÃO usar diagnóstico como fallback para hiperfoco
        hiperfoco_real = ""
        if isinstance(pei_completo, dict):
            hiperfoco_real = (
                pei_completo.get("hiperfoco") or 
                pei_completo.get("interesses") or 
                pei_completo.get("habilidades_interesses") or 
                ""
            )
        
        # Se não achou no JSON, coloca um padrão (NUNCA usa o diagnóstico)
        if not hiperfoco_real:
            hiperfoco_real = "Interesses gerais (A descobrir)"

        # Montagem do resumo de fallback se não houver contexto da IA
        if not contexto_ia:
            serie = item.get("grade", "")
            contexto_ia = f"Estudante: {item.get('name')}. Série: {serie}. Diagnóstico: {diagnostico_real}."

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

def adaptar_conteudo_docx(api_key, aluno, texto, materia, tema, tipo_atv, remover_resp, questoes_mapeadas, modo_profundo=False, checklist_adaptacao=None):
    """Adapta conteúdo de um DOCX para o estudante"""
    client = OpenAI(api_key=api_key)
    lista_q = ", ".join([str(n) for n in questoes_mapeadas]) if questoes_mapeadas else ""
    style = "Seja didático e use uma Cadeia de Pensamento para adaptar." if modo_profundo else "Seja objetivo."
    
    # Montar instruções baseadas no checklist de adaptação
    instrucoes_checklist = ""
    if checklist_adaptacao and isinstance(checklist_adaptacao, dict):
        necessidades_ativas = []
        
        if checklist_adaptacao.get("questoes_desafiadoras"):
            necessidades_ativas.append("Aumentar o nível de desafio das questões")
        else:
            necessidades_ativas.append("Manter ou reduzir o nível de dificuldade")
        
        if not checklist_adaptacao.get("compreende_instrucoes_complexas"):
            necessidades_ativas.append("Simplificar instruções complexas")
        
        if checklist_adaptacao.get("instrucoes_passo_a_passo"):
            necessidades_ativas.append("Fornecer instruções passo a passo")
        
        if checklist_adaptacao.get("dividir_em_etapas"):
            necessidades_ativas.append("Dividir questões em etapas menores e mais gerenciáveis")
        
        if checklist_adaptacao.get("paragrafos_curtos"):
            necessidades_ativas.append("Usar parágrafos curtos para melhor compreensão")
        
        if checklist_adaptacao.get("dicas_apoio"):
            necessidades_ativas.append("Incluir dicas de apoio para resolver questões")
        
        if not checklist_adaptacao.get("compreende_figuras_linguagem"):
            necessidades_ativas.append("Reduzir ou eliminar figuras de linguagem e inferências")
        
        if checklist_adaptacao.get("descricao_imagens"):
            necessidades_ativas.append("Incluir descrição detalhada de imagens")
        
        if necessidades_ativas:
            instrucoes_checklist = f"""
    
    CHECKLIST DE ADAPTAÇÃO (baseado no PEI):
    {chr(10).join([f"- {n}" for n in necessidades_ativas])}
    
    REGRA CRÍTICA: NÃO aplique todas as necessidades em uma única questão. 
    Para cada questão, escolha APENAS 1-2 necessidades que façam mais sentido no contexto.
    Analise cada questão individualmente e selecione as adaptações mais relevantes.
    """
    
    prompt = f"""
    ESPECIALISTA EM DUA E INCLUSÃO. {style}
    1. ANALISE O PERFIL: {aluno.get('ia_sugestao', '')[:1000]}
    2. ADAPTE A PROVA: Use o hiperfoco ({aluno.get('hiperfoco', 'Geral')}) em 30% das questões.
    {instrucoes_checklist}
    
    REGRA ABSOLUTA DE IMAGENS: O professor indicou imagens nas questões: {lista_q if lista_q else "nenhuma"}.
    MANTENHA AS IMAGENS NO MESMO LOCAL ONDE ESTAVAM NA PROVA ORIGINAL.
    Para questões com imagens, a estrutura OBRIGATÓRIA é: 1. Enunciado -> 2. [[IMG_número]] -> 3. Alternativas.
    NUNCA remova ou mova imagens de sua posição original.
    
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

def adaptar_conteudo_imagem(api_key, aluno, imagem_bytes, materia, tema, tipo_atv, livro_professor, modo_profundo=False, checklist_adaptacao=None, imagem_separada=None):
    """Adapta conteúdo de uma imagem para o estudante"""
    client = OpenAI(api_key=api_key)
    if not imagem_bytes:
        return "Erro: Imagem vazia", ""
    
    b64 = base64.b64encode(imagem_bytes).decode('utf-8')
    instrucao_livro = "ATENÇÃO: IMAGEM COM RESPOSTAS. Remova todo gabarito/respostas." if livro_professor else ""
    style = "Faça uma análise crítica para melhor adaptação." if modo_profundo else "Transcreva e adapte."
    
    # Buscar hiperfoco do aluno
    hiperfoco = aluno.get('hiperfoco', 'Geral') or 'Geral'
    
    # Instrução sobre imagem separada
    instrucao_imagem_separada = ""
    if imagem_separada:
        instrucao_imagem_separada = "\n    - O professor recortou a imagem separadamente para melhor qualidade. Use a tag [[IMG_2]] para inserir esta imagem recortada no local apropriado da questão adaptada."
    
    # Montar instruções baseadas no checklist de adaptação (específico para questão única)
    instrucoes_checklist = ""
    if checklist_adaptacao and isinstance(checklist_adaptacao, dict):
        necessidades_ativas = []
        
        if checklist_adaptacao.get("questoes_desafiadoras"):
            necessidades_ativas.append("Aumentar o nível de desafio da questão")
        else:
            necessidades_ativas.append("Manter ou reduzir o nível de dificuldade")
        
        if not checklist_adaptacao.get("compreende_instrucoes_complexas"):
            necessidades_ativas.append("Simplificar instruções complexas")
        
        if checklist_adaptacao.get("instrucoes_passo_a_passo"):
            necessidades_ativas.append("Fornecer instruções passo a passo detalhadas")
        
        if checklist_adaptacao.get("dividir_em_etapas"):
            necessidades_ativas.append("Dividir a questão em etapas menores e mais gerenciáveis")
        
        if checklist_adaptacao.get("paragrafos_curtos"):
            necessidades_ativas.append("Usar parágrafos curtos para melhor compreensão")
        
        if checklist_adaptacao.get("dicas_apoio"):
            necessidades_ativas.append("Incluir dicas de apoio específicas para resolver esta questão")
        
        if not checklist_adaptacao.get("compreende_figuras_linguagem"):
            necessidades_ativas.append("Reduzir ou eliminar figuras de linguagem e inferências")
        
        if checklist_adaptacao.get("descricao_imagens"):
            necessidades_ativas.append("Incluir descrição detalhada da imagem presente na questão")
        
        if necessidades_ativas:
            instrucoes_checklist = f"""
    
    CHECKLIST DE ADAPTAÇÃO (baseado no PEI - QUESTÃO ÚNICA):
    {chr(10).join([f"- {n}" for n in necessidades_ativas])}
    
    REGRA CRÍTICA: Como esta é uma questão única, aplique as adaptações selecionadas de forma específica e pontual.
    Selecione as 2-3 adaptações mais relevantes para esta questão específica e aplique-as de forma integrada.
    """
    
    prompt = f"""
    ATUAR COMO: Especialista em Acessibilidade e OCR. {style}
    1. Transcreva o texto da imagem. {instrucao_livro}
    2. Adapte para o estudante (PEI: {aluno.get('ia_sugestao', '')[:800]}).
    3. HIPERFOCO ({hiperfoco}): Use o hiperfoco do estudante sempre que possível para conectar e engajar na questão. 
       Se o hiperfoco for relevante ao conteúdo, integre-o naturalmente na adaptação.
    {instrucoes_checklist}
    4. REGRA ABSOLUTA DE IMAGEM: 
    - Se a questão original tinha imagem, detecte-a na imagem fornecida e insira a tag [[IMG_1]] no mesmo local onde estava.
    {instrucao_imagem_separada}
    - MANTENHA AS IMAGENS NO MESMO LOCAL ONDE ESTAVAM NA QUESTÃO ORIGINAL.
    
    SAÍDA OBRIGATÓRIA (Respeite o divisor):
    [ANÁLISE PEDAGÓGICA]
    ...análise...
    ---DIVISOR---
    [ATIVIDADE]
    ...atividade...
    """
    
    # Preparar mensagens com imagem(s)
    content_msgs = [
        {"type": "text", "text": prompt}, 
        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}}
    ]
    
    # Se houver imagem separada, adicionar também
    if imagem_separada:
        b64_separada = base64.b64encode(imagem_separada).decode('utf-8')
        content_msgs.append({
            "type": "text", 
            "text": "IMAGEM RECORTADA SEPARADAMENTE PELO PROFESSOR (use tag [[IMG_2]] para inserir no local apropriado):"
        })
        content_msgs.append({
            "type": "image_url", 
            "image_url": {"url": f"data:image/jpeg;base64,{b64_separada}"}
        })
    
    msgs = [
        {
            "role": "user", 
            "content": content_msgs
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

def criar_profissional(api_key, aluno, materia, objeto, qtd, tipo_q, qtd_imgs, verbos_bloom=None, habilidades_bncc=None, modo_profundo=False, checklist_adaptacao=None):
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
    
    # Montar instruções do checklist de adaptação (criação já considerando PEI)
    instrucoes_checklist = ""
    if checklist_adaptacao and isinstance(checklist_adaptacao, dict):
        necessidades_ativas = []
        if checklist_adaptacao.get("questoes_desafiadoras"):
            necessidades_ativas.append("Incluir questões mais desafiadoras")
        else:
            necessidades_ativas.append("Manter nível de dificuldade acessível")
        if not checklist_adaptacao.get("compreende_instrucoes_complexas"):
            necessidades_ativas.append("Usar instruções simples e diretas")
        if checklist_adaptacao.get("instrucoes_passo_a_passo"):
            necessidades_ativas.append("Fornecer instruções passo a passo")
        if checklist_adaptacao.get("dividir_em_etapas"):
            necessidades_ativas.append("Dividir em etapas menores")
        if checklist_adaptacao.get("paragrafos_curtos"):
            necessidades_ativas.append("Usar parágrafos curtos")
        if checklist_adaptacao.get("dicas_apoio"):
            necessidades_ativas.append("Incluir dicas de apoio")
        if not checklist_adaptacao.get("compreende_figuras_linguagem"):
            necessidades_ativas.append("Evitar figuras de linguagem complexas")
        if checklist_adaptacao.get("descricao_imagens"):
            necessidades_ativas.append("Incluir descrição de imagens quando houver")
        if necessidades_ativas:
            instrucoes_checklist = f"""
    8. CHECKLIST DE ADAPTAÇÃO (baseado no PEI):
       {chr(10).join([f"- {n}" for n in necessidades_ativas])}
       Aplique essas orientações de forma coerente nas questões criadas.
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
    {instrucoes_checklist}
    
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
    ESTUDANTE: {aluno['nome']} (Educação Infantil).
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
    
    INFORMAÇÕES DO ESTUDANTE:
    - Perfil: {aluno.get('ia_sugestao', '')[:500]}
    - Hiperfoco: {aluno.get('hiperfoco', 'Geral')}
    
    INFORMAÇÕES DA AULA:
    - Componente Curricular: {materia}
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
    Crie uma DINÂMICA INCLUSIVA para {qtd_alunos} estudantes.
    
    INFORMAÇÕES DO ESTUDANTE FOCAL:
    - Nome: {aluno['nome']}
    - Perfil: {aluno.get('ia_sugestao', '')[:400]}
    - Hiperfoco: {aluno.get('hiperfoco', 'Geral')}
    
    INFORMAÇÕES DA DINÂMICA:
    - Componente Curricular: {materia}
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
       - Inclua adaptações para o estudante focal
    
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
    INFORMAÇÕES DO ESTUDANTE (DUA):
    - Nome: {aluno_info.get('nome', '')}
    - Hiperfoco: {aluno_info.get('hiperfoco', '')}
    - Perfil: {aluno_info.get('ia_sugestao', '')[:300]}
        """
    
    prompt = f"""
    ATUAR COMO: Coordenador Pedagógico Especialista em BNCC, DUA e Metodologias Ativas.
    
    Crie um PLANO DE AULA COMPLETO com as seguintes informações:
    
    INFORMAÇÕES BÁSICAS:
    - Componente Curricular: {materia}
    - Tema/Assunto: {assunto}
    - Metodologia: {metodologia}
    - Técnica: {tecnica if tecnica else 'Não especificada'}
    - Quantidade de Estudantes: {qtd_alunos}
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
    - Papel dos estudantes
    
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
    - Estratégias para estudantes com dificuldades
    
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
    Componente Curricular: {materia}. Assunto: {assunto}.
    Hiperfoco do estudante: {hiperfoco}.
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
            disciplina = st.selectbox("Componente Curricular", DISCIPLINAS_PADRAO, key=f"disc_basico_{key_suffix}")
        with col2:
            ano = st.selectbox("Ano", ordenar_anos(["1", "2", "3", "4", "5", "6", "7", "8", "9", "1EM", "2EM", "3EM"]), 
                              key=f"ano_basico_{key_suffix}")
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
    
    # TEMOS DADOS - criar dropdowns conectados (Componente → Ano)
    
    # Linha 1: Componente Curricular, Ano, Unidade Temática
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Primeiro: Componente Curricular (sem filtro)
        disciplinas = sorted(dados['Disciplina'].dropna().unique())
        disciplina_selecionada = st.selectbox("Componente Curricular", disciplinas, key=f"disc_bncc_{key_suffix}")
    
    with col2:
        # Segundo: Ano (filtrado por Componente)
        if disciplina_selecionada:
            disc_filtradas = dados[dados['Disciplina'] == disciplina_selecionada]
            anos_originais = disc_filtradas['Ano'].dropna().unique().tolist()
            anos_ordenados = ordenar_anos(anos_originais)
            ano_selecionado = st.selectbox("Ano", anos_ordenados, key=f"ano_bncc_{key_suffix}")
        else:
            ano_selecionado = None
    
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
                st.info("ℹ️ Selecione Ano, Componente Curricular, Unidade e Objeto para ver as habilidades.")
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
        
        /* HEADER DO ESTUDANTE */
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
    
    # BNCC + Assunto em expander compacto
    with st.expander("📚 BNCC e Assunto", expanded=True):
        if 'bncc_df_completo' not in st.session_state:
            st.session_state.bncc_df_completo = carregar_bncc_completa()
        dados = st.session_state.bncc_df_completo
        
        # Linha 1: Componente, Ano, Unidade
        col_bncc1, col_bncc2, col_bncc3 = st.columns(3)
        with col_bncc1:
            if dados is not None and not dados.empty:
                disciplinas = sorted(dados['Disciplina'].dropna().unique())
                disciplina_bncc = st.selectbox("Componente Curricular", disciplinas, key="disc_adaptar_prova_compact")
            else:
                disciplina_bncc = st.selectbox("Componente Curricular", 
                                             ["Língua Portuguesa", "Matemática", "Ciências", "História", "Geografia", "Arte", "Educação Física", "Inglês"],
                                             key="disc_adaptar_prova_compact")
        with col_bncc2:
            if dados is not None and not dados.empty and disciplina_bncc:
                disc_filtradas = dados[dados['Disciplina'] == disciplina_bncc]
                anos_originais = disc_filtradas['Ano'].dropna().unique().tolist()
                anos_ordenados = ordenar_anos(anos_originais)
                ano_bncc = st.selectbox("Ano", anos_ordenados, key="ano_adaptar_prova_compact")
            else:
                ano_bncc = st.selectbox("Ano", ordenar_anos(["1", "2", "3", "4", "5", "6", "7", "8", "9", "1EM", "2EM", "3EM"]), 
                                      key="ano_adaptar_prova_compact")
        with col_bncc3:
            if dados is not None and not dados.empty and ano_bncc and disciplina_bncc:
                unid_filtradas = dados[
                    (dados['Ano'].astype(str) == str(ano_bncc)) & 
                    (dados['Disciplina'] == disciplina_bncc)
                ]
                unidades = sorted(unid_filtradas['Unidade Temática'].dropna().unique())
                if unidades:
                    unidade_bncc = st.selectbox("Unidade Temática", unidades, key="unid_adaptar_prova_compact")
                else:
                    unidade_bncc = st.text_input("Unidade Temática", placeholder="Ex: Números", 
                                               key="unid_adaptar_prova_compact")
            else:
                unidade_bncc = st.text_input("Unidade Temática", placeholder="Ex: Números", 
                                           key="unid_adaptar_prova_compact")
        
        # Linha 2: Objeto do Conhecimento e Assunto
        col_obj, col_ass = st.columns(2)
        with col_obj:
            if dados is not None and not dados.empty and ano_bncc and disciplina_bncc and unidade_bncc:
                obj_filtrados = dados[
                    (dados['Ano'].astype(str) == str(ano_bncc)) & 
                    (dados['Disciplina'] == disciplina_bncc) & 
                    (dados['Unidade Temática'] == unidade_bncc)
                ]
                objetos = sorted(obj_filtrados['Objeto do Conhecimento'].dropna().unique())
                if objetos:
                    objeto_bncc = st.selectbox("Objeto do Conhecimento", objetos, key="obj_adaptar_prova_compact")
                else:
                    objeto_bncc = st.text_input("Objeto do Conhecimento", placeholder="Ex: Frações", 
                                               key="obj_adaptar_prova_compact")
            else:
                objeto_bncc = st.text_input("Objeto do Conhecimento", placeholder="Ex: Frações", 
                                           key="obj_adaptar_prova_compact")
        with col_ass:
            assunto_livre = st.text_input(
                "📝 Assunto (opcional)",
                value="",
                placeholder="Ex: Frações, Sistema Solar...",
                help="Preencha se quiser direcionar a adaptação para um assunto específico.",
                key="assunto_adaptar_prova_compact"
            )
    
    # Configuração (Tipo e Upload)
    st.markdown("---")
    c1, c2 = st.columns([1, 2])
    tipo_d = c1.selectbox("Tipo de Documento", ["Prova", "Tarefa", "Avaliação"], key="dtp")
    arquivo_d = c2.file_uploader("Upload do Arquivo DOCX", type=["docx"], key="fd")
    
    # Definição automática baseada na BNCC
    materia_d = disciplina_bncc if disciplina_bncc else "Geral"
    tema_d = objeto_bncc if objeto_bncc else "Geral"
    
    # Se assunto livre foi preenchido, usa ele como tema
    if assunto_livre and assunto_livre.strip():
        tema_d = assunto_livre.strip()
    
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

    # Inicializar checklist
    checklist_respostas = {}
    
    # Checklist de adaptação - em expander retrátil com checkboxes (4 colunas)
    with st.expander("🎯 Checklist de Adaptação (baseado no PEI)", expanded=False):
        st.info("""
        ⚠️ **IMPORTANTE:** Marque apenas as adaptações que devem ser aplicadas. 
        A IA escolherá pontualmente 1-2 necessidades por questão, evitando sobrecarga.
        """)
        
        # Organizar em 4 colunas para otimizar espaço
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            precisa_desafio = st.checkbox(
                "Questões mais desafiadoras",
                value=False,
                key="check_desafio"
            )
            precisa_passo = st.checkbox(
                "Instruções passo a passo",
                value=False,
                key="check_passo"
            )
        
        with col2:
            compreende_complexas = st.checkbox(
                "Compreende instruções complexas",
                value=False,
                key="check_complexas"
            )
            precisa_etapas = st.checkbox(
                "Dividir em etapas menores",
                value=False,
                key="check_etapas"
            )
        
        with col3:
            precisa_paragrafos_curtos = st.checkbox(
                "Parágrafos curtos",
                value=False,
                key="check_paragrafos"
            )
            precisa_dicas = st.checkbox(
                "Dicas de apoio",
                value=False,
                key="check_dicas"
            )
        
        with col4:
            compreende_figuras = st.checkbox(
                "Compreende figuras de linguagem",
                value=False,
                key="check_figuras"
            )
            precisa_descricao_img = st.checkbox(
                "Descrição de imagens",
                value=False,
                key="check_descricao"
            )
        
        # Compilar respostas em um dicionário
        checklist_respostas = {
            "questoes_desafiadoras": precisa_desafio,
            "compreende_instrucoes_complexas": compreende_complexas,
            "instrucoes_passo_a_passo": precisa_passo,
            "dividir_em_etapas": precisa_etapas,
            "paragrafos_curtos": precisa_paragrafos_curtos,
            "dicas_apoio": precisa_dicas,
            "compreende_figuras_linguagem": compreende_figuras,
            "descricao_imagens": precisa_descricao_img
        }
    
    st.markdown("---")

    if st.button("🚀 ADAPTAR PROVA", type="primary", key="btn_d", use_container_width=True):
        if not st.session_state.docx_txt:
            st.warning("Por favor, faça o upload de um arquivo DOCX.")
            st.stop()
        
        # Validação se BNCC foi preenchida (ou assunto livre)
        if not disciplina_bncc:
             st.warning("⚠️ Por favor, selecione a Disciplina nos campos da BNCC acima.")
             st.stop()
        
        if not objeto_bncc and not (assunto_livre and assunto_livre.strip()):
             st.warning("⚠️ Por favor, selecione o Objeto do Conhecimento (BNCC) ou preencha o campo Assunto acima para guiar a adaptação.")
             st.stop()

        with st.spinner("A IA está analisando e adaptando o conteúdo..."):
            # Salvar checklist no session_state para uso no refazer
            st.session_state['checklist_adaptacao_prova'] = checklist_respostas
            rac, txt = adaptar_conteudo_docx(
                api_key, aluno, st.session_state.docx_txt, materia_d, tema_d, tipo_d, True, qs_d,
                checklist_adaptacao=checklist_respostas
            )
            st.session_state['res_docx'] = {'rac': rac, 'txt': txt, 'map': map_d, 'valid': False}
            st.rerun()

    if 'res_docx' in st.session_state:
        res = st.session_state['res_docx']
        if res.get('valid'):
            st.success(f"{get_icon('validar', 20, '#16A34A')} **ATIVIDADE VALIDADA E PRONTA PARA USO**")
        else:
            col_v, col_r = st.columns([1, 1])
            if col_v.button(f"{get_icon('validar', 16, '#16A34A')} Validar", key="val_d", use_container_width=True):
                st.session_state['res_docx']['valid'] = True
                st.rerun()
            if col_r.button(f"{get_icon('configurar', 16, '#06B6D4')} Refazer (+Profundo)", key="redo_d", use_container_width=True):
                with st.spinner("Refazendo com análise mais profunda..."):
                    # Recuperar checklist do session_state se disponível
                    checklist_redo = st.session_state.get('checklist_adaptacao_prova', {})
                    rac, txt = adaptar_conteudo_docx(
                        api_key, aluno, st.session_state.docx_txt, materia_d, tema_d, tipo_d, True, qs_d, 
                        modo_profundo=True, checklist_adaptacao=checklist_redo
                    )
                    st.session_state['res_docx'] = {'rac': rac, 'txt': txt, 'map': map_d, 'valid': False}
                    st.rerun()

        st.markdown(f"<div class='analise-box'><div class='analise-title'>{get_icon('pedagogia', 20, '#06B6D4')} Análise Pedagógica</div>{res['rac']}</div>", unsafe_allow_html=True)
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
        # Recuperar checklist para formatação do Word
        checklist_formatacao = st.session_state.get('checklist_adaptacao_prova', {})
        docx = construir_docx_final(res['txt'], aluno, materia_d, res['map'], tipo_d, sem_cabecalho=False, checklist_adaptacao=checklist_formatacao)
        c_down1.download_button(
            f"{get_icon('download', 18, 'white')} BAIXAR DOCX (Editável)", 
            docx, 
            "Prova_Adaptada.docx", 
            "primary",
            use_container_width=True
        )
        
        pdf_bytes = criar_pdf_generico(res['txt'])
        c_down2.download_button(
            f"{get_icon('download', 18, 'white')} BAIXAR PDF (Visualização)", 
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
    
    # BNCC + Assunto em expander compacto
    with st.expander("📚 BNCC e Assunto", expanded=True):
        if 'bncc_df_completo' not in st.session_state:
            st.session_state.bncc_df_completo = carregar_bncc_completa()
        dados = st.session_state.bncc_df_completo
        
        # Linha 1: Componente, Ano, Unidade
        col_bncc1, col_bncc2, col_bncc3 = st.columns(3)
        with col_bncc1:
            if dados is not None and not dados.empty:
                disciplinas = sorted(dados['Disciplina'].dropna().unique())
                disciplina_bncc = st.selectbox("Componente Curricular", disciplinas, key="disc_adaptar_atividade_compact")
            else:
                disciplina_bncc = st.selectbox("Componente Curricular", 
                                         ["Língua Portuguesa", "Matemática", "Ciências", "História", "Geografia", "Arte", "Educação Física", "Inglês"],
                                         key="disc_adaptar_atividade_compact")
        with col_bncc2:
            if dados is not None and not dados.empty and disciplina_bncc:
                disc_filtradas = dados[dados['Disciplina'] == disciplina_bncc]
                anos_originais = disc_filtradas['Ano'].dropna().unique().tolist()
                anos_ordenados = ordenar_anos(anos_originais)
                ano_bncc = st.selectbox("Ano", anos_ordenados, key="ano_adaptar_atividade_compact")
            else:
                ano_bncc = st.selectbox("Ano", ordenar_anos(["1", "2", "3", "4", "5", "6", "7", "8", "9", "1EM", "2EM", "3EM"]), 
                                  key="ano_adaptar_atividade_compact")
        with col_bncc3:
            if dados is not None and not dados.empty and ano_bncc and disciplina_bncc:
                unid_filtradas = dados[
                    (dados['Ano'].astype(str) == str(ano_bncc)) & 
                    (dados['Disciplina'] == disciplina_bncc)
                ]
                unidades = sorted(unid_filtradas['Unidade Temática'].dropna().unique())
                if unidades:
                    unidade_bncc = st.selectbox("Unidade Temática", unidades, key="unid_adaptar_atividade_compact")
                else:
                    unidade_bncc = st.text_input("Unidade Temática", placeholder="Ex: Números", 
                                               key="unid_adaptar_atividade_compact")
            else:
                unidade_bncc = st.text_input("Unidade Temática", placeholder="Ex: Números", 
                                           key="unid_adaptar_atividade_compact")
        
        # Linha 2: Objeto do Conhecimento e Assunto
        col_obj, col_ass = st.columns(2)
        with col_obj:
            if dados is not None and not dados.empty and ano_bncc and disciplina_bncc and unidade_bncc:
                obj_filtrados = dados[
                    (dados['Ano'].astype(str) == str(ano_bncc)) & 
                    (dados['Disciplina'] == disciplina_bncc) & 
                    (dados['Unidade Temática'] == unidade_bncc)
                ]
                objetos = sorted(obj_filtrados['Objeto do Conhecimento'].dropna().unique())
                if objetos:
                    objeto_bncc = st.selectbox("Objeto do Conhecimento", objetos, key="obj_adaptar_atividade_compact")
                else:
                    objeto_bncc = st.text_input("Objeto do Conhecimento", placeholder="Ex: Frações", 
                                               key="obj_adaptar_atividade_compact")
            else:
                objeto_bncc = st.text_input("Objeto do Conhecimento", placeholder="Ex: Frações", 
                                           key="obj_adaptar_atividade_compact")
        with col_ass:
            assunto_livre = st.text_input(
                "📝 Assunto (opcional)",
                value="",
                placeholder="Ex: Frações, Sistema Solar...",
                help="Preencha se quiser direcionar a adaptação para um assunto específico.",
                key="assunto_adaptar_atividade_compact"
            )
    
    # Configuração (Tipo e Upload)
    st.markdown("---")
    c1, c2 = st.columns([1, 2])
    tipo_i = c1.selectbox("Tipo", ["Atividade", "Tarefa", "Exercício"], key="itp")
    arquivo_i = c2.file_uploader("Upload da Imagem/Foto", type=["png","jpg","jpeg"], key="fi")
    livro_prof = st.checkbox(f"{get_icon('livro', 16, '#06B6D4')} É foto do Livro do Professor? (A IA removerá as respostas)", value=False)
    
    # Definição automática baseada na BNCC
    materia_i = disciplina_bncc if disciplina_bncc else "Geral"
    tema_i = objeto_bncc if objeto_bncc else "Geral"
    
    # Se assunto livre foi preenchido, usa ele como tema
    if assunto_livre and assunto_livre.strip():
        tema_i = assunto_livre.strip()
    
    if 'img_raw' not in st.session_state:
        st.session_state.img_raw = None
    
    if arquivo_i and arquivo_i.file_id != st.session_state.get('last_i'):
        st.session_state.last_i = arquivo_i.file_id
        st.session_state.img_raw = sanitizar_imagem(arquivo_i.getvalue())

    # Processo de recorte
    cropped_res = None
    imagem_recortada = None
    
    if st.session_state.img_raw:
        st.markdown(f"### {icon_title('Passo 1: Recortar a Questão', 'adaptar_atividade', 20, '#06B6D4')}", unsafe_allow_html=True)
        st.info("💡 **Importante:** Recorte a área da questão completa.")
        
        img_pil = Image.open(BytesIO(st.session_state.img_raw))
        img_pil.thumbnail((800, 800))
        cropped_res = st_cropper(img_pil, realtime_update=True, box_color='#FF0000', aspect_ratio=None, key="crop_i")
        if cropped_res:
            st.image(cropped_res, width=200, caption="Questão recortada")
            
            # Se a questão foi recortada, oferecer opção de recortar imagem separadamente
            st.markdown("### 🖼️ Passo 2: Recortar Imagem (Opcional)")
            st.caption("Se a questão tem imagem e você quer recortá-la separadamente para melhor qualidade, clique abaixo.")
            
            tem_imagem_na_questao = st.checkbox(
                "A questão tem imagem e quero recortá-la separadamente",
                value=False,
                key="tem_imagem_separada"
            )
            
            if tem_imagem_na_questao:
                st.info("💡 Recorte apenas a área da imagem na questão. Esta imagem será inserida na questão adaptada.")
                # Abrir a imagem original novamente para recortar só a imagem
                img_pil_original = Image.open(BytesIO(st.session_state.img_raw))
                img_pil_original.thumbnail((800, 800))
                imagem_recortada = st_cropper(img_pil_original, realtime_update=True, box_color='#00FF00', aspect_ratio=None, key="crop_img_separada")
                if imagem_recortada:
                    st.image(imagem_recortada, width=200, caption="Imagem recortada separadamente")

    # Inicializar checklist
    checklist_respostas = {}
    
    # Checklist de adaptação - em expander retrátil com checkboxes (4 colunas)
    with st.expander("🎯 Checklist de Adaptação (baseado no PEI) - Questão Única", expanded=False):
        st.info("""
        ⚠️ **IMPORTANTE:** Marque apenas as adaptações que devem ser aplicadas nesta questão. 
        A IA aplicará as adaptações selecionadas de forma pontual e específica.
        """)
        
        # Organizar em 4 colunas para otimizar espaço
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            precisa_desafio = st.checkbox(
                "Questões mais desafiadoras",
                value=False,
                key="check_desafio_atividade"
            )
            precisa_passo = st.checkbox(
                "Instruções passo a passo",
                value=False,
                key="check_passo_atividade"
            )
        
        with col2:
            compreende_complexas = st.checkbox(
                "Compreende instruções complexas",
                value=False,
                key="check_complexas_atividade"
            )
            precisa_etapas = st.checkbox(
                "Dividir em etapas menores",
                value=False,
                key="check_etapas_atividade"
            )
        
        with col3:
            precisa_paragrafos_curtos = st.checkbox(
                "Parágrafos curtos",
                value=False,
                key="check_paragrafos_atividade"
            )
            precisa_dicas = st.checkbox(
                "Dicas de apoio",
                value=False,
                key="check_dicas_atividade"
            )
        
        with col4:
            compreende_figuras = st.checkbox(
                "Compreende figuras de linguagem",
                value=False,
                key="check_figuras_atividade"
            )
            precisa_descricao_img = st.checkbox(
                "Descrição de imagens",
                value=False,
                key="check_descricao_atividade"
            )
        
        # Compilar respostas em um dicionário
        checklist_respostas = {
            "questoes_desafiadoras": precisa_desafio,
            "compreende_instrucoes_complexas": compreende_complexas,
            "instrucoes_passo_a_passo": precisa_passo,
            "dividir_em_etapas": precisa_etapas,
            "paragrafos_curtos": precisa_paragrafos_curtos,
            "dicas_apoio": precisa_dicas,
            "compreende_figuras_linguagem": compreende_figuras,
            "descricao_imagens": precisa_descricao_img
        }
        # Salvar no session_state para uso posterior
        st.session_state['checklist_adaptacao_atividade'] = checklist_respostas
    
    # Garantir que checklist_respostas está definido
    if not checklist_respostas:
        checklist_respostas = st.session_state.get('checklist_adaptacao_atividade', {})

    st.markdown("---")

    if st.button("🚀 ADAPTAR ATIVIDADE", type="primary", key="btn_i", use_container_width=True):
        if not st.session_state.img_raw:
            st.warning("Por favor, envie uma imagem.")
            st.stop()
        
        # Validação BNCC (ou assunto livre)
        if not disciplina_bncc:
             st.warning("⚠️ Por favor, selecione a Disciplina nos campos da BNCC acima.")
             st.stop()
        
        if not objeto_bncc and not (assunto_livre and assunto_livre.strip()):
             st.warning("⚠️ Por favor, selecione o Objeto do Conhecimento (BNCC) ou preencha o campo Assunto acima para guiar a adaptação.")
             st.stop()

        if not cropped_res:
            st.warning("⚠️ Por favor, recorte a área da questão primeiro.")
            st.stop()
        
        with st.spinner("Lendo imagem e adaptando conteúdo..."):
            buf_c = BytesIO()
            cropped_res.convert('RGB').save(buf_c, format="JPEG", quality=90)
            img_bytes = buf_c.getvalue()
            
            # Processar imagem recortada separadamente se houver
            img_separada_bytes = None
            if imagem_recortada:
                buf_img = BytesIO()
                imagem_recortada.convert('RGB').save(buf_img, format="JPEG", quality=90)
                img_separada_bytes = buf_img.getvalue()
            
            # Salvar checklist no session_state para uso no refazer
            st.session_state['checklist_adaptacao_atividade'] = checklist_respostas
            st.session_state['img_separada_atividade'] = img_separada_bytes
            
            rac, txt = adaptar_conteudo_imagem(
                api_key, aluno, img_bytes, materia_i, tema_i, tipo_i, livro_prof, 
                checklist_adaptacao=checklist_respostas,
                imagem_separada=img_separada_bytes
            )
            
            # Mapear imagens: 1 = questão recortada, 2 = imagem recortada separadamente (se houver)
            mapa_imgs = {1: img_bytes}
            if img_separada_bytes:
                mapa_imgs[2] = img_separada_bytes
            
            st.session_state['res_img'] = {'rac': rac, 'txt': txt, 'map': mapa_imgs, 'valid': False}
            st.rerun()

    if 'res_img' in st.session_state:
        res = st.session_state['res_img']
        if res.get('valid'):
            st.success(f"{get_icon('validar', 20, '#16A34A')} **ATIVIDADE VALIDADA E PRONTA PARA USO**")
        else:
            col_v, col_r = st.columns([1, 1])
            if col_v.button(f"{get_icon('validar', 16, '#16A34A')} Validar", key="val_i", use_container_width=True):
                st.session_state['res_img']['valid'] = True
                st.rerun()
            if col_r.button(f"{get_icon('configurar', 16, '#06B6D4')} Refazer (+Profundo)", key="redo_i", use_container_width=True):
                with st.spinner("Refazendo..."):
                    img_bytes = res['map'][1]
                    img_separada_redo = res['map'].get(2)  # Recuperar imagem separada se houver
                    # Recuperar checklist do session_state se disponível
                    checklist_redo = st.session_state.get('checklist_adaptacao_atividade', {})
                    rac, txt = adaptar_conteudo_imagem(
                        api_key, aluno, img_bytes, materia_i, tema_i, tipo_i, livro_prof, 
                        modo_profundo=True, checklist_adaptacao=checklist_redo, imagem_separada=img_separada_redo
                    )
                    st.session_state['res_img'] = {'rac': rac, 'txt': txt, 'map': res['map'], 'valid': False}
                    st.rerun()

        st.markdown(f"<div class='analise-box'><div class='analise-title'>{get_icon('pedagogia', 20, '#06B6D4')} Análise Pedagógica</div>{res['rac']}</div>", unsafe_allow_html=True)
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
        # Recuperar checklist para formatação do Word
        checklist_formatacao = st.session_state.get('checklist_adaptacao_atividade', {})
        docx = construir_docx_final(res['txt'], aluno, materia_i, res['map'], tipo_i, sem_cabecalho=False, checklist_adaptacao=checklist_formatacao)
        c_down1.download_button("📥 BAIXAR DOCX (Editável)", docx, "Atividade.docx", "primary", use_container_width=True)
        
        pdf_bytes = criar_pdf_generico(res['txt'])
        c_down2.download_button(
            f"{get_icon('download', 18, 'white')} BAIXAR PDF (Visualização)", 
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
        usa o hiperfoco para engajamento. Imagens: prioridade no banco (Unsplash), IA só em último caso.
    </div>
    """, unsafe_allow_html=True)
    
    # BNCC + Assunto em expander compacto
    with st.expander("📚 BNCC e Assunto", expanded=True):
        if 'bncc_df_completo' not in st.session_state:
            st.session_state.bncc_df_completo = carregar_bncc_completa()
        dados = st.session_state.bncc_df_completo
        
        # Linha 1: Componente, Ano, Unidade
        c1, c2, c3 = st.columns(3)
        with c1:
            if dados is not None and not dados.empty:
                disciplinas = sorted(dados['Disciplina'].dropna().unique())
                disciplina_bncc = st.selectbox("Componente Curricular", disciplinas, key="disc_criar_zero")
            else:
                disciplina_bncc = st.selectbox("Componente Curricular", 
                    ["Língua Portuguesa", "Matemática", "Ciências", "História", "Geografia", "Arte", "Educação Física", "Inglês"], key="disc_criar_zero")
        with c2:
            if dados is not None and not dados.empty and disciplina_bncc:
                disc_f = dados[dados['Disciplina'] == disciplina_bncc]
                anos_ord = ordenar_anos(disc_f['Ano'].dropna().unique().tolist())
                ano_bncc = st.selectbox("Ano", anos_ord, key="ano_criar_zero")
            else:
                ano_bncc = st.selectbox("Ano", ordenar_anos(["1", "2", "3", "4", "5", "6", "7", "8", "9", "1EM", "2EM", "3EM"]), key="ano_criar_zero")
        with c3:
            if dados is not None and not dados.empty and ano_bncc and disciplina_bncc:
                unid_f = dados[(dados['Ano'].astype(str) == str(ano_bncc)) & (dados['Disciplina'] == disciplina_bncc)]
                unidades = sorted(unid_f['Unidade Temática'].dropna().unique())
                unidade_bncc = st.selectbox("Unidade Temática", unidades, key="unid_criar_zero") if unidades else st.text_input("Unidade Temática", placeholder="Ex: Números", key="unid_criar_zero")
            else:
                unidade_bncc = st.text_input("Unidade Temática", placeholder="Ex: Números", key="unid_criar_zero")
        
        # Linha 2: Objeto do Conhecimento, Assunto (opcional)
        c4, c5 = st.columns(2)
        with c4:
            if dados is not None and not dados.empty and ano_bncc and disciplina_bncc and unidade_bncc:
                obj_f = dados[(dados['Ano'].astype(str) == str(ano_bncc)) & (dados['Disciplina'] == disciplina_bncc) & (dados['Unidade Temática'] == unidade_bncc)]
                objetos = sorted(obj_f['Objeto do Conhecimento'].dropna().unique())
                objeto_bncc = st.selectbox("Objeto do Conhecimento", objetos, key="obj_criar_zero") if objetos else st.text_input("Objeto do Conhecimento", placeholder="Ex: Frações", key="obj_criar_zero")
            else:
                objeto_bncc = st.text_input("Objeto do Conhecimento", placeholder="Ex: Frações", key="obj_criar_zero")
        with c5:
            assunto_criar = st.text_input("📝 Assunto (opcional)", value="", placeholder="Ex: Frações, Sistema Solar...", key="assunto_criar_zero", help="Direciona melhor o tema da atividade.")
        
        # Habilidades (compacto)
        habilidades_bncc = []
        if dados is not None and not dados.empty and ano_bncc and disciplina_bncc and unidade_bncc and objeto_bncc:
            hab_f = dados[(dados['Ano'].astype(str) == str(ano_bncc)) & (dados['Disciplina'] == disciplina_bncc) & (dados['Unidade Temática'] == unidade_bncc) & (dados['Objeto do Conhecimento'] == objeto_bncc)]
            todas_hab = sorted(hab_f['Habilidade'].dropna().unique())
            if todas_hab:
                habilidades_bncc = st.multiselect("Habilidades BNCC", todas_hab, default=todas_hab[:min(3, len(todas_hab))], key="hab_criar_zero")
    
    mat_c = disciplina_bncc
    obj_c = assunto_criar.strip() if assunto_criar and assunto_criar.strip() else objeto_bncc
    
    # Configuração da atividade (uma linha)
    st.markdown("---")
    r1, r2, r3, r4 = st.columns(4)
    with r1:
        qtd_c = st.slider("Quantidade de Questões", 1, 10, 5, key="cq")
    with r2:
        tipo_quest = st.selectbox("Tipo de Questão", ["Objetiva", "Discursiva"], key="ctq")
    with r3:
        usar_img = st.checkbox("Incluir Imagens?", value=True, key="usar_img")
    with r4:
        qtd_img_sel = st.slider("Qtd. imagens", 0, qtd_c, int(qtd_c/2) if qtd_c > 1 else 0, disabled=not usar_img, key="qtd_img_slider")
    
    # Inicializar variáveis antes dos expanders
    checklist_criar = {}
    verbos_finais_para_ia = []
    usar_bloom = False
    
    # Checklist e Taxonomia de Bloom juntos embaixo (lado a lado)
    col_check, col_bloom = st.columns(2)
    
    with col_check:
        with st.expander("🎯 Checklist de Adaptação (opcional)", expanded=False):
            st.info("Marque as adaptações que devem ser consideradas na criação da atividade.")
            col_c1, col_c2, col_c3, col_c4 = st.columns(4)
            with col_c1:
                check_desafio = st.checkbox("Questões mais desafiadoras", value=False, key="c0_desafio")
                check_passo = st.checkbox("Instruções passo a passo", value=False, key="c0_passo")
            with col_c2:
                check_complexas = st.checkbox("Compreende instruções complexas", value=False, key="c0_complexas")
                check_etapas = st.checkbox("Dividir em etapas menores", value=False, key="c0_etapas")
            with col_c3:
                check_paragrafos = st.checkbox("Parágrafos curtos", value=False, key="c0_paragrafos")
                check_dicas = st.checkbox("Dicas de apoio", value=False, key="c0_dicas")
            with col_c4:
                check_figuras = st.checkbox("Compreende figuras de linguagem", value=False, key="c0_figuras")
                check_descricao = st.checkbox("Descrição de imagens", value=False, key="c0_descricao")
            checklist_criar = {
                "questoes_desafiadoras": check_desafio, "compreende_instrucoes_complexas": check_complexas,
                "instrucoes_passo_a_passo": check_passo, "dividir_em_etapas": check_etapas,
                "paragrafos_curtos": check_paragrafos, "dicas_apoio": check_dicas,
                "compreende_figuras_linguagem": check_figuras, "descricao_imagens": check_descricao
            }
    
    with col_bloom:
        with st.expander("🧠 Taxonomia de Bloom (opcional)", expanded=False):
            if 'bloom_memoria' not in st.session_state:
                st.session_state.bloom_memoria = {cat: [] for cat in TAXONOMIA_BLOOM.keys()}
            usar_bloom = st.checkbox(f"{get_icon('configurar', 16, '#06B6D4')} Usar Taxonomia de Bloom (Revisada)", key="usar_bloom")
            if usar_bloom:
                col_b1, col_b2 = st.columns(2)
                with col_b1:
                    cat_atual = st.selectbox("Categoria Cognitiva:", list(TAXONOMIA_BLOOM.keys()), key="cat_bloom")
                with col_b2:
                    selecao_atual = st.multiselect(f"Verbos de '{cat_atual}':", TAXONOMIA_BLOOM[cat_atual], default=st.session_state.bloom_memoria[cat_atual], key=f"ms_bloom_{cat_atual}")
                    st.session_state.bloom_memoria[cat_atual] = selecao_atual
                for cat in st.session_state.bloom_memoria:
                    verbos_finais_para_ia.extend(st.session_state.bloom_memoria[cat])
                if verbos_finais_para_ia:
                    st.info(f"**Verbos:** {', '.join(verbos_finais_para_ia)}")
    
    st.markdown("---")
    if st.button("✨ CRIAR ATIVIDADE", type="primary", key="btn_c", use_container_width=True):
        if not api_key:
            st.error("❌ Insira a chave da OpenAI nas configurações")
        else:
            with st.spinner("Elaborando atividade..."):
                qtd_final = qtd_img_sel if usar_img else 0
                rac, txt = criar_profissional(
                    api_key, aluno, mat_c, obj_c, qtd_c, tipo_quest, qtd_final,
                    verbos_bloom=verbos_finais_para_ia if usar_bloom else None,
                    habilidades_bncc=habilidades_bncc,
                    checklist_adaptacao=checklist_criar
                )
                novo_map = {}
                count = 0
                tags = re.findall(r'\[\[GEN_IMG: (.*?)\]\]', txt)
                for p in tags:
                    count += 1
                    # Prioridade: BANCO (Unsplash) primeiro; IA só em último caso
                    url = gerar_imagem_inteligente(api_key, p, unsplash_key, prioridade="BANCO")
                    if not url and unsplash_key:
                        url = gerar_imagem_inteligente(api_key, p, unsplash_key, prioridade="IA")
                    if url:
                        io = baixar_imagem_url(url)
                        if io:
                            novo_map[count] = io.getvalue()
                txt_fin = txt
                for i in range(1, count + 1):
                    txt_fin = re.sub(r'\[\[GEN_IMG: .*?\]\]', f"[[IMG_G{i}]]", txt_fin, count=1)
                st.session_state['res_create'] = {'rac': rac, 'txt': txt_fin, 'map': novo_map, 'valid': False, 'mat_c': mat_c, 'obj_c': obj_c, 'checklist': checklist_criar}
                st.rerun()
    
    # Exibição do resultado
    if 'res_create' in st.session_state:
        res = st.session_state['res_create']
        
        st.markdown("---")
        titulo_atividade = f"Atividade Criada: {res.get('mat_c', '')} - {res.get('obj_c', '')}"
        st.markdown(f"### {icon_title(titulo_atividade, 'criar_zero', 20, '#06B6D4')}", unsafe_allow_html=True)
        
        # Barra de status
        if res.get('valid'):
            st.success(f"{get_icon('validar', 20, '#16A34A')} **ATIVIDADE VALIDADA E PRONTA PARA USO**")
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
            docx = construir_docx_final(res['txt'], aluno, mat_c, res.get('map', {}), "Criada", checklist_adaptacao=res.get('checklist'))
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
    
    # BNCC em expander
    with st.expander("📚 BNCC e Habilidades", expanded=True):
        ano_bncc, disciplina_bncc, unidade_bncc, objeto_bncc, habilidades_bncc = criar_dropdowns_bncc_completos_melhorado(key_suffix="roteiro")
    
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
        O hiperfoco é um <strong>caminho neurológico</strong> já aberto. Use-o para conectar o estudante ao componente curricular.
        Aqui você também pode adicionar um tema de interesse da turma toda (DUA) para criar conexões coletivas.
    </div>
    """, unsafe_allow_html=True)
    
    c1, c2 = st.columns(2)
    materia_papo = c1.selectbox("Componente Curricular", DISCIPLINAS_PADRAO, key="papo_mat")
    assunto_papo = c2.text_input("Assunto da Aula:", key="papo_ass")
    
    c3, c4 = st.columns(2)
    hiperfoco_papo = c3.text_input("Hiperfoco (Estudante):", value=aluno.get('hiperfoco', 'Geral'), key="papo_hip")
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
    
    # BNCC em expander
    with st.expander("📚 BNCC e Habilidades", expanded=True):
        ano_bncc, disciplina_bncc, unidade_bncc, objeto_bncc, habilidades_bncc = criar_dropdowns_bncc_completos_melhorado(key_suffix="dinamica")
    
    # Configuração da Turma
    st.markdown("---")
    
    c3, c4 = st.columns(2)
    with c3:
        qtd_alunos = st.number_input("Número de Estudantes:", min_value=5, max_value=50, value=25, key="din_qtd")
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
    
    # BNCC em expander
    with st.expander("📚 BNCC e Habilidades", expanded=True):
        ano_bncc, disciplina_bncc, unidade_bncc, objeto_bncc, habilidades_bncc = criar_dropdowns_bncc_completos_melhorado(key_suffix="plano")
    
    # Configuração Metodológica
    st.markdown("---")
    
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
        qtd_alunos_plano = st.number_input("Qtd Estudantes:", min_value=1, value=30, key="plano_qtd")
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

# CSS específico do Hub (chamado após a definição da função)
aplicar_estilos()

# ==============================================================================
# FUNÇÃO PRINCIPAL
# ==============================================================================
def main():
    """Função principal da aplicação - executa a lógica do Hub"""
    
    # Inicializar api_key e unsplash_key antes de usar
    if 'OPENAI_API_KEY' in st.secrets:
        api_key = st.secrets['OPENAI_API_KEY']
    elif 'OPENAI_API_KEY' in st.session_state:
        api_key = st.session_state['OPENAI_API_KEY']
    else:
        api_key = None
    
    if 'UNSPLASH_ACCESS_KEY' in st.secrets:
        unsplash_key = st.secrets['UNSPLASH_ACCESS_KEY']
    elif 'UNSPLASH_ACCESS_KEY' in st.session_state:
        unsplash_key = st.session_state['UNSPLASH_ACCESS_KEY']
    else:
        unsplash_key = None
    
    # Configurações de API (ocultas - apenas busca dos secrets)
    # O expander foi removido conforme solicitado
    
    # Carregar dados dos estudantes
    if 'banco_estudantes' not in st.session_state or not st.session_state.banco_estudantes:
        with st.spinner("🔄 Lendo dados da nuvem..."):
            st.session_state.banco_estudantes = carregar_estudantes_supabase()
    
    if not st.session_state.banco_estudantes:
        st.warning("⚠️ Nenhum estudante encontrado.")
        if st.button("📘 Ir para o módulo PEI", type="primary"): 
            st.switch_page("pages/1_PEI.py")
        st.stop()
    
    # Seleção de aluno + Botão de Limpar Formulários
    lista_alunos = [a['nome'] for a in st.session_state.banco_estudantes]
    col_sel, col_btn_limpar, col_info = st.columns([2, 1, 2])
    with col_sel:
        nome_aluno = st.selectbox("📂 Selecione o Estudante:", lista_alunos)
    
    with col_btn_limpar:
        st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)  # Alinhar com selectbox
        if st.button("🧹 Limpar Formulários", type="secondary", use_container_width=True, help="Limpa todos os formulários e resultados da página atual"):
            # Limpar todos os estados relacionados a formulários e resultados
            chaves_para_limpar = [
                # Resultados de adaptação
                'res_docx', 'res_img', 'res_create', 
                # Validações
                'valid_scene', 'valid_caa', 'valid_d', 'valid_i', 'valid_c',
                # Uploads e arquivos
                'docx_txt', 'docx_imgs', 'last_d', 'last_i', 'img_raw', 'cropped_img',
                # Educação Infantil
                'res_ei_experiencia', 'valid_ei_experiencia', 'res_ei_rotina', 
                'valid_ei_rotina', 'res_ei_dina', 'valid_ei_dina',
                # Outras abas
                'res_roteiro', 'res_roteiro_valid', 'res_papo', 'res_papo_valid',
                'res_dinamica', 'res_dinamica_valid', 'res_plano_aula', 'res_plano_aula_valid',
                # Configurações de adaptação
                'necessidades_selecionadas_adaptar_prova',
                # Estados de Bloom (limpar todos os prefixos)
            ]
            
            # Limpar chaves específicas
            for key in chaves_para_limpar:
                if key in st.session_state:
                    del st.session_state[key]
            
            # Limpar estados de Bloom (todos os prefixos)
            keys_to_remove = []
            for key in st.session_state.keys():
                if key.startswith('bloom_memoria_') or key.startswith('usar_bloom_') or key.startswith('cat_bloom_') or key.startswith('ms_bloom_'):
                    keys_to_remove.append(key)
            for key in keys_to_remove:
                del st.session_state[key]
            
            st.success("✅ Formulários limpos!")
            st.rerun()
    
    aluno = next((a for a in st.session_state.banco_estudantes if a.get('nome') == nome_aluno), None)
    
    if not aluno: 
        st.error("Estudante não encontrado")
        st.stop()
    
    # --- ÁREA DO ALUNO (Visual + Expander) ---
    
    # 1. Cabeçalho Visual (Nome e Série - Mantém visível para contexto rápido)
    render_cabecalho_aluno(aluno)
    
    # 2. PEI RETRÁTIL (Aqui está a mudança solicitada)
    # Mostra os detalhes pesados apenas se o usuário clicar
    with st.expander(f"📄 Ver Detalhes do PEI e Diagnóstico de {aluno['nome'].split()[0]}", expanded=False):
        
        # Buscar diagnóstico - IMPORTANTE: usar diretamente do aluno que já foi processado
        # O diagnóstico já foi extraído corretamente na função carregar_estudantes_supabase
        diagnostico_pei = aluno.get('diagnosis', '') or ""
        
        # Se não encontrou ou está vazio, tenta buscar diretamente do pei_data como fallback
        if not diagnostico_pei or diagnostico_pei == "Não informado no cadastro":
            pei_data_local = aluno.get('pei_data', {}) or {}
            if isinstance(pei_data_local, dict):
                diagnostico_pei = pei_data_local.get('diagnostico', '') or ""
        
        # Se ainda não encontrou, mostra mensagem
        if not diagnostico_pei:
            diagnostico_pei = "Não informado no cadastro"
        
        # Buscar hiperfoco - IMPORTANTE: usar diretamente do aluno que já foi processado
        # O hiperfoco já foi extraído corretamente do pei_data na função carregar_estudantes_supabase
        hiperfoco_aluno = aluno.get('hiperfoco', '') or ""
        
        # Se não encontrou, tenta buscar diretamente do pei_data como fallback
        if not hiperfoco_aluno or hiperfoco_aluno == "Interesses gerais (A descobrir)":
            pei_data_local = aluno.get('pei_data', {}) or {}
            if isinstance(pei_data_local, dict):
                hiperfoco_aluno = (
                    pei_data_local.get('hiperfoco') or 
                    pei_data_local.get('interesses') or 
                    pei_data_local.get('habilidades_interesses') or 
                    ""
                )
        
        # Se ainda não encontrou hiperfoco, mostra padrão
        if not hiperfoco_aluno:
            hiperfoco_aluno = "Interesses gerais (A descobrir)"
        
        c_diag, c_hip = st.columns(2)
        with c_diag:
            st.markdown(f"**🏥 Diagnóstico/CID:**")
            # Garantir que está usando o campo correto
            diag_final = diagnostico_pei if diagnostico_pei and diagnostico_pei != "Não informado no cadastro" else "Não informado no cadastro"
            st.info(diag_final)
            
        with c_hip:
            st.markdown(f"**🎯 Hiperfoco/Interesses:**")
            # Garantir que está usando o campo correto - NÃO usar diagnóstico aqui
            hip_final = hiperfoco_aluno if hiperfoco_aluno and hiperfoco_aluno != "Não informado no cadastro" else "Interesses gerais (A descobrir)"
            st.success(hip_final)
            
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
        
        tabs = st.tabs([
            f"{get_icon('experiencia', 18, '#06B6D4')} Criar Experiência (BNCC)", 
            f"{get_icon('estudio_visual', 18, '#06B6D4')} Estúdio Visual & CAA", 
            f"{get_icon('rotina', 18, '#06B6D4')} Rotina & AVD", 
            f"{get_icon('brincar', 18, '#06B6D4')} Inclusão no Brincar"
        ])
        
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
            f"{get_icon('adaptar_prova', 18, '#06B6D4')} Adaptar Prova", 
            f"{get_icon('adaptar_atividade', 18, '#06B6D4')} Adaptar Atividade", 
            f"{get_icon('criar_zero', 18, '#06B6D4')} Criar do Zero", 
            f"{get_icon('estudio_visual', 18, '#06B6D4')} Estúdio Visual & CAA", 
            f"{get_icon('roteiro', 18, '#06B6D4')} Roteiro Individual", 
            f"{get_icon('papo_mestre', 18, '#06B6D4')} Papo de Mestre", 
            f"{get_icon('dinamica', 18, '#06B6D4')} Dinâmica Inclusiva", 
            f"{get_icon('plano_aula', 18, '#06B6D4')} Plano de Aula DUA"
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

# ==============================================================================
# RODAPÉ COM ASSINATURA
# ==============================================================================
ou.render_footer_assinatura()







    
