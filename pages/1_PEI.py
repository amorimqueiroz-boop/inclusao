import streamlit as st
from datetime import date
from io import BytesIO
from docx import Document
from docx.shared import Pt
from openai import OpenAI
from pypdf import PdfReader
from fpdf import FPDF
import base64
import json
import os
import re
import glob
import random
import requests

# ==============================================================================
# 0. CONFIGURAÇÃO DE PÁGINA
# ==============================================================================
st.set_page_config(
    page_title="[TESTE] Omnisfera | PEI",
    page_icon="🛠️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==============================================================================
# ### INICIO BLOCO TESTE: VISUAL DE ALERTA ###
# ==============================================================================
st.markdown("""
<style>
    /* Faixa de aviso no topo */
    .test-environment-bar {
        position: fixed; top: 0; left: 0; width: 100%; height: 12px;
        background: repeating-linear-gradient(45deg, #FFC107, #FFC107 10px, #FF9800 10px, #FF9800 20px);
        z-index: 9999999;
    }
    /* Selo de Teste */
    .test-badge {
        position: fixed; top: 20px; right: 20px; 
        background-color: #FF9800; color: white;
        padding: 5px 12px; border-radius: 8px;
        font-weight: 800; font-size: 0.8rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.2);
        z-index: 9999999; pointer-events: none;
    }
</style>
<div class="test-environment-bar"></div>
<div class="test-badge">🛠️ AMBIENTE DE TESTES</div>
""", unsafe_allow_html=True)
# ==============================================================================
# ### FIM BLOCO TESTE ###
# ==============================================================================

# ==============================================================================
# 1. VERIFICAÇÃO DE SEGURANÇA (SIMPLIFICADA)
# ==============================================================================
def verificar_acesso():
    # Verifica se o usuário passou pelo login da Home
    if "autenticado" not in st.session_state or not st.session_state["autenticado"]:
        st.error("🔒 Acesso Negado. Por favor, faça login na Página Inicial.")
        st.stop() # Para o carregamento aqui
    
    # NÃO ESCONDEMOS MAIS O CABEÇALHO.
    # Isso garante que o botão da sidebar (setinha) funcione nativamente.
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

# Executa a verificação
verificar_acesso()

# ==============================================================================
# 2. LÓGICA DO BANCO DE DADOS (INTEGRAÇÃO CENTRAL)
# ==============================================================================
ARQUIVO_DB_CENTRAL = "banco_alunos.json"
PASTA_BANCO = "banco_alunos_backup" # Pasta local

if not os.path.exists(PASTA_BANCO): os.makedirs(PASTA_BANCO)

def carregar_banco():
    # --- BLINDAGEM DE DADOS (Leitura filtrada) ---
    usuario_atual = st.session_state.get("usuario_nome", "")
    # ---------------------------------------------

    if os.path.exists(ARQUIVO_DB_CENTRAL):
        try:
            with open(ARQUIVO_DB_CENTRAL, "r", encoding="utf-8") as f:
                todos_alunos = json.load(f)
                
                # FILTRAGEM: Retorna apenas alunos deste usuário
                meus_alunos = [
                    aluno for aluno in todos_alunos 
                    if aluno.get('responsavel') == usuario_atual
                ]
                return meus_alunos
        except: return []
    return []

# Inicializa banco na memória
if 'banco_estudantes' not in st.session_state or not st.session_state.banco_estudantes:
    st.session_state.banco_estudantes = carregar_banco()

def salvar_aluno_integrado(dados):
    """Salva backup local E atualiza a Omnisfera"""
    if not dados['nome']: return False, "Nome é obrigatório."
    
    # 1. Backup Local (.json completo)
    nome_arq = re.sub(r'[^a-zA-Z0-9]', '_', dados['nome'].lower()) + ".json"
    try:
        with open(os.path.join(PASTA_BANCO, nome_arq), 'w', encoding='utf-8') as f:
            json.dump(dados, f, default=str, ensure_ascii=False, indent=4)
    except Exception as e: return False, f"Erro backup: {str(e)}"

    # 2. Integração Omnisfera (Banco Central)
    # Remove versão antiga se existir (para atualizar)
    st.session_state.banco_estudantes = [a for a in st.session_state.banco_estudantes if a['nome'] != dados['nome']]
    
    # Cria registro otimizado para o Hub/PAE
    novo_registro = {
        "nome": dados['nome'],
        "serie": dados.get('serie', ''),
        "hiperfoco": dados.get('hiperfoco', ''),
        "ia_sugestao": dados.get('ia_sugestao', ''), # Cérebro do aluno
        "diagnostico": dados.get('diagnostico', ''),
        
        # --- BLINDAGEM DE DADOS (INSERÇÃO CIRÚRGICA) ---
        "responsavel": st.session_state.get("usuario_nome", "Desconhecido"),
        "data_criacao": str(date.today())
        # -----------------------------------------------
    }
    st.session_state.banco_estudantes.append(novo_registro)
    
    # Salva no arquivo central (Sobrescreve com a lista atualizada)
    try:
        # Primeiro, precisamos carregar o banco COMPLETO do disco para não perder alunos de outros usuários
        banco_completo = []
        if os.path.exists(ARQUIVO_DB_CENTRAL):
            with open(ARQUIVO_DB_CENTRAL, "r", encoding="utf-8") as f:
                banco_completo = json.load(f)
        
        # Remove a versão antiga desse aluno do banco completo (se existir)
        banco_completo = [a for a in banco_completo if a['nome'] != dados['nome']]
        
        # Adiciona o novo registro ao banco completo
        banco_completo.append(novo_registro)
        
        # Salva tudo de volta
        with open(ARQUIVO_DB_CENTRAL, "w", encoding="utf-8") as f:
            json.dump(banco_completo, f, default=str, ensure_ascii=False, indent=4)
            
        return True, f"Aluno {dados['nome']} integrado à Omnisfera!"
    except Exception as e:
        return False, f"Erro integração: {str(e)}"

# ==============================================================================
# 2. LISTAS DE DADOS
# ==============================================================================
LISTA_SERIES = [
    "Educação Infantil (Creche)", "Educação Infantil (Pré-Escola)", 
    "1º Ano (Fund. I)", "2º Ano (Fund. I)", "3º Ano (Fund. I)", "4º Ano (Fund. I)", "5º Ano (Fund. I)", 
    "6º Ano (Fund. II)", "7º Ano (Fund. II)", "8º Ano (Fund. II)", "9º Ano (Fund. II)", 
    "1ª Série (EM)", "2ª Série (EM)", "3ª Série (EM)", "EJA (Educação de Jovens e Adultos)"
]

LISTA_ALFABETIZACAO = [
    "Não se aplica (Educação Infantil)",
    "Pré-Silábico (Garatuja/Desenho sem letras)",
    "Pré-Silábico (Letras aleatórias sem valor sonoro)",
    "Silábico (Sem valor sonoro convencional)",
    "Silábico (Com valor sonoro vogais/consoantes)",
    "Silábico-Alfabético (Transição)",
    "Alfabético (Escrita fonética, com erros ortográficos)",
    "Ortográfico (Escrita convencional consolidada)"
]

LISTAS_BARREIRAS = {
    "Funções Cognitivas": ["Atenção Sustentada/Focada", "Memória de Trabalho (Operacional)", "Flexibilidade Mental", "Planejamento e Organização", "Velocidade de Processamento", "Abstração e Generalização"],
    "Comunicação e Linguagem": ["Linguagem Expressiva (Fala)", "Linguagem Receptiva (Compreensão)", "Pragmática (Uso social da língua)", "Processamento Auditivo", "Intenção Comunicativa"],
    "Socioemocional": ["Regulação Emocional (Autocontrole)", "Tolerância à Frustração", "Interação Social com Pares", "Autoestima e Autoimagem", "Reconhecimento de Emoções"],
    "Sensorial e Motor": ["Praxias Globais (Coordenação Grossa)", "Praxias Finas (Coordenação Fina)", "Hipersensibilidade Sensorial", "Hipossensibilidade (Busca Sensorial)", "Planejamento Motor"],
    "Acadêmico": ["Decodificação Leitora", "Compreensão Textual", "Raciocínio Lógico-Matemático", "Grafomotricidade (Escrita manual)", "Produção Textual"]
}

LISTA_POTENCIAS = [
    "Memória Visual", "Musicalidade/Ritmo", "Interesse em Tecnologia", "Hiperfoco Construtivo", 
    "Liderança Natural", "Habilidades Cinestésicas (Esportes)", "Expressão Artística (Desenho)", 
    "Cálculo Mental Rápido", "Oralidade/Vocabulário", "Criatividade/Imaginação", 
    "Empatia/Cuidado com o outro", "Resolução de Problemas", "Curiosidade Investigativa"
]

LISTA_PROFISSIONAIS = [
    "Psicólogo Clínico", "Neuropsicólogo", "Fonoaudiólogo", "Terapeuta Ocupacional", 
    "Neuropediatra", "Psiquiatra Infantil", "Psicopedagogo Clínico", "Professor de Apoio (Mediador)", 
    "Acompanhante Terapêutico (AT)", "Musicoterapeuta", "Equoterapeuta", "Oftalmologista"
]

LISTA_FAMILIA = [
    "Mãe", "Pai", "Madrasta", "Padrasto", "Avó Materna", "Avó Paterna", "Avô Materno", "Avô Paterno", 
    "Irmãos", "Tios", "Primos", "Tutor Legal", "Abrigo Institucional"
]

# ==============================================================================
# 3. GERENCIAMENTO DE ESTADO
# ==============================================================================
default_state = {
    'nome': '', 'nasc': date(2015, 1, 1), 'serie': None, 'turma': '', 'diagnostico': '', 
    'lista_medicamentos': [], 'composicao_familiar_tags': [], 'historico': '', 'familia': '', 
    'hiperfoco': '', 'potencias': [], 'rede_apoio': [], 'orientacoes_especialistas': '',
    'checklist_evidencias': {}, 
    'nivel_alfabetizacao': 'Não se aplica (Educação Infantil)',
    'barreiras_selecionadas': {k: [] for k in LISTAS_BARREIRAS.keys()},
    'niveis_suporte': {}, 
    'estrategias_acesso': [], 'estrategias_ensino': [], 'estrategias_avaliacao': [], 
    'ia_sugestao': '',         # PEI TÉCNICO
    'ia_mapa_texto': '',       # ROTEIRO GAMIFICADO
    'outros_acesso': '', 'outros_ensino': '', 
    'monitoramento_data': date.today(), 
    'status_meta': 'Não Iniciado', 'parecer_geral': 'Manter Estratégias', 'proximos_passos_select': []
}

if 'dados' not in st.session_state: st.session_state.dados = default_state
else:
    for key, val in default_state.items():
        if key not in st.session_state.dados: st.session_state.dados[key] = val

if 'pdf_text' not in st.session_state: st.session_state.pdf_text = ""

# ==============================================================================
# 4. LÓGICA E UTILITÁRIOS
# ==============================================================================
PASTA_BANCO = "banco_alunos"
if not os.path.exists(PASTA_BANCO): os.makedirs(PASTA_BANCO)

def calcular_idade(data_nasc):
    if not data_nasc: return ""
    hoje = date.today()
    idade = hoje.year - data_nasc.year - ((hoje.month, hoje.day) < (data_nasc.month, data_nasc.day))
    return f"{idade} anos"

def get_hiperfoco_emoji(texto):
    if not texto: return "🚀"
    t = texto.lower()
    if "jogo" in t or "game" in t or "minecraft" in t or "roblox" in t: return "🎮"
    if "dino" in t: return "🦖"
    if "fute" in t or "bola" in t: return "⚽"
    if "desenho" in t or "arte" in t: return "🎨"
    if "músic" in t: return "🎵"
    if "anim" in t or "gato" in t or "cachorro" in t: return "🐾"
    if "carro" in t: return "🏎️"
    if "espaço" in t: return "🪐"
    return "🚀"

def detectar_nivel_ensino(serie_str):
    if not serie_str: return "INDEFINIDO"
    s = serie_str.lower()
    if "infantil" in s: return "EI"
    if "1º ano" in s or "2º ano" in s or "3º ano" in s or "4º ano" in s or "5º ano" in s: return "FI"
    if "6º ano" in s or "7º ano" in s or "8º ano" in s or "9º ano" in s: return "FII"
    if "série" in s or "médio" in s or "eja" in s: return "EM"
    return "INDEFINIDO"

def get_segmento_info_visual(serie):
    nivel = detectar_nivel_ensino(serie)
    if nivel == "EI":
        return "Educação Infantil", "#4299e1", "Foco: Campos de Experiência (BNCC) e Desenvolvimento Integral."
    elif nivel == "FI":
        return "Anos Iniciais (Fund. I)", "#48bb78", "Foco: Alfabetização, Letramento e Construção de Habilidades."
    elif nivel == "FII":
        return "Anos Finais (Fund. II)", "#ed8936", "Foco: Autonomia, Identidade e Abstração (Múltiplos Professores)."
    elif nivel == "EM":
        return "Ensino Médio / EJA", "#9f7aea", "Foco: Projeto de Vida e Preparação Acadêmica/Profissional."
    else:
        return "Selecione a Série", "grey", "Aguardando seleção..."

def calcular_complexidade_pei(dados):
    n_bar = sum(len(v) for v in dados['barreiras_selecionadas'].values())
    n_suporte_alto = sum(1 for v in dados['niveis_suporte'].values() if v in ["Substancial", "Muito Substancial"])
    recursos = 0
    if dados['rede_apoio']: recursos += 3
    if dados['lista_medicamentos']: recursos += 2
    saldo = (n_bar + n_suporte_alto) - recursos
    if saldo <= 2: return "FLUIDA", "#F0FFF4", "#276749"
    if saldo <= 7: return "ATENÇÃO", "#FFFFF0", "#D69E2E"
    return "CRÍTICA", "#FFF5F5", "#C53030"

def extrair_tag_ia(texto, tag):
    if not texto: return ""
    padrao = fr'\[{tag}\](.*?)(\[|$)'
    match = re.search(padrao, texto, re.DOTALL)
    if match: return match.group(1).strip()
    return ""

def extrair_metas_estruturadas(texto):
    bloco = extrair_tag_ia(texto, "METAS_SMART")
    if not bloco:
        bloco = extrair_tag_ia(texto, "OBJETIVOS_DESENVOLVIMENTO")
        if not bloco: return None
        return {"Curto": "Ver Objetivos de Desenvolvimento abaixo", "Medio": "...", "Longo": "..."}
    metas = {"Curto": "Definir...", "Medio": "Definir...", "Longo": "Definir..."}
    linhas = bloco.split('\n')
    for l in linhas:
        l_clean = re.sub(r'^[\-\*]+', '', l).strip()
        if "Curto" in l or "2 meses" in l: metas["Curto"] = l_clean.split(":")[-1].strip()
        elif "Médio" in l or "Semestre" in l: metas["Medio"] = l_clean.split(":")[-1].strip()
        elif "Longo" in l or "Ano" in l: metas["Longo"] = l_clean.split(":")[-1].strip()
    return metas

def extrair_bloom(texto):
    bloco = extrair_tag_ia(texto, "TAXONOMIA_BLOOM")
    if not bloco: return ["Identificar", "Compreender", "Aplicar"]
    return [v.strip() for v in bloco.split(',')]

def extrair_campos_experiencia(texto):
    bloco = extrair_tag_ia(texto, "CAMPOS_EXPERIENCIA_PRIORITARIOS")
    if not bloco: return ["O eu, o outro e o nós", "Corpo, gestos e movimentos"]
    linhas = [l.strip().replace('- ','') for l in bloco.split('\n') if l.strip()]
    return linhas[:3]

def get_pro_icon(nome_profissional):
    p = nome_profissional.lower()
    if "psic" in p: return "🧠"
    if "fono" in p: return "🗣️"
    if "terapeuta" in p or "equo" in p or "musico" in p: return "🧩"
    if "neuro" in p or "psiq" in p or "medico" in p: return "🩺"
    return "👨‍⚕️"

def finding_logo():
    possiveis = ["360.png", "360.jpg", "logo.png", "logo.jpg", "iconeaba.png"]
    for nome in possiveis:
        if os.path.exists(nome): return nome
    return None

def get_base64_image(image_path):
    if not image_path: return ""
    with open(image_path, "rb") as img_file: return base64.b64encode(img_file.read()).decode()

def ler_pdf(arquivo):
    try:
        reader = PdfReader(arquivo); texto = ""
        for i, page in enumerate(reader.pages):
            if i >= 6: break 
            texto += page.extract_text() + "\n"
        return texto
    except: return ""

def limpar_texto_pdf(texto):
    if not texto: return ""
    t = texto.replace('**', '').replace('__', '').replace('#', '')
    return t.encode('latin-1', 'ignore').decode('latin-1')

def salvar_aluno(dados):
    if not dados['nome']: return False, "Nome obrigatório."
    nome_arq = re.sub(r'[^a-zA-Z0-9]', '_', dados['nome'].lower()) + ".json"
    try:
        with open(os.path.join(PASTA_BANCO, nome_arq), 'w', encoding='utf-8') as f:
            json.dump(dados, f, default=str, ensure_ascii=False, indent=4)
        return True, f"Registro salvo: {dados['nome']}"
    except Exception as e: return False, str(e)

def carregar_aluno(nome_arq):
    return None

def excluir_aluno(nome_arq):
    try: os.remove(os.path.join(PASTA_BANCO, nome_arq)); return True
    except: return False

def calcular_progresso():
    if st.session_state.dados['ia_sugestao']: return 100
    pontos = 0; total = 7
    d = st.session_state.dados
    if d['nome']: pontos += 1
    if d['serie']: pontos += 1
    if d['nivel_alfabetizacao'] and d['nivel_alfabetizacao'] != 'Não se aplica (Educação Infantil)': pontos += 1
    if any(d['checklist_evidencias'].values()): pontos += 1
    if d['hiperfoco']: pontos += 1
    if any(d['barreiras_selecionadas'].values()): pontos += 1
    if d['estrategias_ensino']: pontos += 1
    return int((pontos / total) * 90)

def render_progresso():
    p = calcular_progresso()
    icon = "🌱"
    bar_color = "linear-gradient(90deg, #FF6B6B 0%, #FF8E53 100%)"
    if p >= 100: 
        icon = "🏆"
        bar_color = "linear-gradient(90deg, #00C6FF 0%, #0072FF 100%)" 
    st.markdown(f"""<div class="prog-container"><div class="prog-track"><div class="prog-fill" style="width: {p}%; background: {bar_color};"></div></div><div class="prog-icon" style="left: {p}%;">{icon}</div></div>""", unsafe_allow_html=True)

# ==============================================================================
# 5. ESTILO VISUAL (CLEAN + VIBRANT CARDS + GOLD TAB)
# ==============================================================================
def aplicar_estilo_visual():
    estilo = """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800&display=swap');
        html, body, [class*="css"] { font-family: 'Nunito', sans-serif; color: #2D3748; background-color: #F7FAFC; }
        .block-container { padding-top: 1.5rem !important; padding-bottom: 5rem !important; }
        
        /* 1. NAVEGAÇÃO "GLOW" CLEAN */
        div[data-baseweb="tab-border"], div[data-baseweb="tab-highlight"] { display: none !important; }
        
        .stTabs [data-baseweb="tab-list"] { 
            gap: 8px; 
            display: flex;
            flex-wrap: nowrap;
            overflow-x: auto;
            white-space: nowrap;
            padding: 10px 5px;
            -ms-overflow-style: none;
            scrollbar-width: none;
        }
        .stTabs [data-baseweb="tab-list"]::-webkit-scrollbar { display: none; }

        /* ESTILO PADRÃO DAS ABAS */
        .stTabs [data-baseweb="tab"] { 
            height: 38px; 
            border-radius: 20px !important; 
            background-color: #FFFFFF; 
            border: 1px solid #E2E8F0; 
            color: #718096; 
            font-weight: 700; 
            font-size: 0.8rem; 
            padding: 0 20px; 
            transition: all 0.2s ease;
            box-shadow: 0 1px 2px rgba(0,0,0,0.03);
            flex-shrink: 0;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .stTabs [data-baseweb="tab"]:hover {
            border-color: #CBD5E0;
            color: #4A5568;
            background-color: #EDF2F7;
        }

        /* ESTADO SELECIONADO (PADRÃO AZUL) */
        .stTabs [aria-selected="true"] { 
            background-color: transparent !important; 
            color: #3182CE !important; 
            border: 1px solid #3182CE !important; 
            font-weight: 800;
            box-shadow: 0 0 12px rgba(49, 130, 206, 0.4), inset 0 0 5px rgba(49, 130, 206, 0.1) !important;
        }

        /* === AJUSTE PARA A ÚLTIMA ABA (JORNADA GAMIFICADA) === */
        .stTabs [data-baseweb="tab"]:last-of-type {
            border-color: #F6E05E !important; /* Borda Amarela */
            color: #B7791F !important; /* Texto Ouro Escuro */
        }
        .stTabs [data-baseweb="tab"]:last-of-type[aria-selected="true"] {
            background-color: transparent !important;
            color: #D69E2E !important; /* Texto Ouro Vibrante */
            border: 1px solid #D69E2E !important;
            box-shadow: 0 0 12px rgba(214, 158, 46, 0.5), inset 0 0 5px rgba(214, 158, 46, 0.1) !important;
        }

        /* 2. CARD DE INSIGHT */
        .insight-card {
            background-color: #FFFFF0;
            border-radius: 12px;
            padding: 20px;
            color: #2D3748;
            display: flex;
            align-items: center;
            gap: 15px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.05);
            border-left: 5px solid #D69E2E;
            margin-top: 30px;
        }
        .insight-icon {
            font-size: 1.5rem;
            color: #D69E2E;
            background: rgba(214, 158, 46, 0.15);
            width: 40px; height: 40px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
        }

        /* 3. CARDS DA HOME */
        .home-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-top: 10px;
        }
        .rich-card {
            background: white;
            border-radius: 12px;
            padding: 20px;
            border: 1px solid #E2E8F0;
            box-shadow: 0 2px 4px rgba(0,0,0,0.02);
            transition: all 0.2s ease;
            text-decoration: none;
            color: inherit;
            display: flex;
            flex-direction: column;
            align-items: center;
            text-align: center;
            position: relative;
            overflow: hidden;
            height: 100%;
        }
        .rich-card:hover {
            transform: translateY(-3px);
            box-shadow: 0 8px 16px rgba(0,0,0,0.06);
            border-color: #CBD5E0;
        }
        .rich-card-top { width: 100%; height: 4px; position: absolute; top: 0; left: 0; }
        .rc-icon { width: 50px; height: 50px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 1.5rem; margin-bottom: 12px; }
        .rc-title { font-weight: 800; font-size: 1rem; color: #2D3748; margin-bottom: 5px; }
        .rc-desc { font-size: 0.8rem; color: #718096; line-height: 1.3; }

        /* OUTROS */
        .header-unified { background-color: white; padding: 20px 40px; border-radius: 16px; border: 1px solid #E2E8F0; box-shadow: 0 2px 10px rgba(0,0,0,0.02); margin-bottom: 20px; display: flex; align-items: center; gap: 20px; }
        .header-subtitle { font-size: 1.2rem; color: #718096; font-weight: 600; border-left: 2px solid #E2E8F0; padding-left: 20px; line-height: 1.2; }

        .prog-container { width: 100%; position: relative; margin: 0 0 30px 0; }
        .prog-track { width: 100%; height: 3px; background-color: #E2E8F0; border-radius: 1.5px; }
        .prog-fill { height: 100%; border-radius: 1.5px; transition: width 1.5s cubic-bezier(0.4, 0, 0.2, 1), background 1.5s ease; box-shadow: 0 1px 4px rgba(0,0,0,0.1); }
        .prog-icon { position: absolute; top: -23px; font-size: 1.8rem; transition: left 1.5s cubic-bezier(0.4, 0, 0.2, 1); transform: translateX(-50%); z-index: 10; filter: drop-shadow(0 2px 2px rgba(0,0,0,0.15)); }
        
        .stTextInput input, .stTextArea textarea, .stSelectbox div[data-baseweb="select"], .stMultiSelect div[data-baseweb="select"] { border-radius: 8px !important; border-color: #E2E8F0 !important; }
        div[data-testid="column"] .stButton button { border-radius: 8px !important; font-weight: 700 !important; height: 45px !important; background-color: #0F52BA !important; color: white !important; border: none !important; }
        div[data-testid="column"] .stButton button:hover { background-color: #0A3D8F !important; }
        .segmento-badge { display: inline-block; padding: 4px 10px; border-radius: 12px; font-weight: 700; font-size: 0.75rem; color: white; margin-top: 5px; }
        
        /* DASHBOARD - KPI ELEMENTS */
        .css-donut { --p: 0; --fill: #e5e7eb; width: 80px; height: 80px; border-radius: 50%; background: conic-gradient(var(--fill) var(--p), #F3F4F6 0); position: relative; display: flex; align-items: center; justify-content: center; margin-bottom: 10px; }
        .css-donut:after { content: ""; position: absolute; width: 60px; height: 60px; border-radius: 50%; background: white; }
        .d-val { position: relative; z-index: 10; font-weight: 800; font-size: 1.2rem; color: #2D3748; }
        .d-lbl { font-size: 0.75rem; font-weight: 700; color: #718096; text-transform: uppercase; letter-spacing: 0.5px; }
        .comp-icon-box { width: 50px; height: 50px; border-radius: 50%; background: rgba(255,255,255,0.2); display: flex; align-items: center; justify-content: center; margin-bottom: 10px; }
        .dna-bar-container { margin-bottom: 15px; }
        .dna-bar-flex { display: flex; justify-content: space-between; font-size: 0.8rem; margin-bottom: 3px; font-weight: 600; color: #4A5568; }
        .dna-bar-bg { width: 100%; height: 8px; background-color: #E2E8F0; border-radius: 4px; overflow: hidden; }
        .dna-bar-fill { height: 100%; border-radius: 4px; transition: width 1s ease; }
        .rede-chip { display: inline-flex; align-items: center; gap: 5px; background: white; padding: 5px 12px; border-radius: 20px; font-size: 0.85rem; font-weight: 600; color: #2D3748; box-shadow: 0 1px 2px rgba(0,0,0,0.05); border: 1px solid #E2E8F0; margin: 0 5px 5px 0; }
        .bloom-tag { display: inline-block; background: rgba(255,255,255,0.6); padding: 3px 8px; border-radius: 6px; font-size: 0.8rem; font-weight: 700; margin: 0 5px 5px 0; color: #2C5282; border: 1px solid rgba(49, 130, 206, 0.2); }

        .dash-hero { background: linear-gradient(135deg, #0F52BA 0%, #062B61 100%); border-radius: 16px; padding: 25px; color: white; margin-bottom: 20px; display: flex; justify-content: space-between; align-items: center; box-shadow: 0 4px 12px rgba(15, 82, 186, 0.15); }
        .apple-avatar { width: 60px; height: 60px; border-radius: 50%; background: rgba(255,255,255,0.15); border: 2px solid rgba(255,255,255,0.4); color: white; font-weight: 800; font-size: 1.6rem; display: flex; align-items: center; justify-content: center; }
        .metric-card { background: white; border-radius: 16px; padding: 15px; border: 1px solid #E2E8F0; display: flex; flex-direction: column; align-items: center; justify-content: center; height: 140px; box-shadow: 0 2px 5px rgba(0,0,0,0.02); }
        .soft-card { border-radius: 12px; padding: 20px; min-height: 220px; height: 100%; display: flex; flex-direction: column; box-shadow: 0 2px 5px rgba(0,0,0,0.02); border: 1px solid rgba(0,0,0,0.05); border-left: 5px solid; position: relative; overflow: hidden; }
        .sc-orange { background-color: #FFF5F5; border-left-color: #DD6B20; }
        .sc-blue { background-color: #EBF8FF; border-left-color: #3182CE; }
        .sc-yellow { background-color: #FFFFF0; border-left-color: #D69E2E; }
        .sc-cyan { background-color: #E6FFFA; border-left-color: #0BC5EA; }
        .sc-green { background-color: #F0FFF4; border-left-color: #38A169; }
        .footer-signature { margin-top: 50px; padding-top: 20px; border-top: 1px solid #E2E8F0; text-align: center; font-size: 0.8rem; color: #A0AEC0; }
        .meta-row { display: flex; align-items: center; gap: 10px; margin-bottom: 8px; font-size: 0.85rem; border-bottom: 1px solid rgba(0,0,0,0.05); padding-bottom: 5px; }
    </style>
    <link href="https://cdn.jsdelivr.net/npm/remixicon@4.1.0/fonts/remixicon.css" rel="stylesheet">
    """
    st.markdown(estilo, unsafe_allow_html=True)

aplicar_estilo_visual()

# ==============================================================================
# 6. INTELIGÊNCIA ARTIFICIAL (TÉCNICA, GAMIFICADA & EXTRAÇÃO)
# ==============================================================================

# CÉREBRO 0: EXTRATOR DE DADOS (PDF -> FORMULÁRIO)
def extrair_dados_pdf_ia(api_key, texto_pdf):
    if not api_key: return None, "Configure a Chave API."
    try:
        client = OpenAI(api_key=api_key)
        prompt = f"""
        Analise o texto deste laudo médico/escolar e extraia:
        1. A hipótese diagnóstica ou diagnóstico (CID se houver).
        2. Medicamentos mencionados (nome e posologia).
        
        Retorne APENAS um JSON neste formato:
        {{
            "diagnostico": "Texto do diagnóstico",
            "medicamentos": [
                {{"nome": "Nome do remédio", "posologia": "Dosagem"}}
            ]
        }}
        
        Texto do Laudo:
        {texto_pdf[:4000]}
        """
        
        res = client.chat.completions.create(
            model="gpt-4o-mini", 
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        return json.loads(res.choices[0].message.content), None
    except Exception as e: return None, str(e)


# CÉREBRO 1: O PEDAGOGO TÉCNICO (CONSULTORIA IA)
@st.cache_data(ttl=3600)
def gerar_saudacao_ia(api_key):
    if not api_key: return "Bem-vindo ao PEI 360º."
    try:
        client = OpenAI(api_key=api_key)
        res = client.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "user", "content": "Frase curta inspiradora para professor sobre inclusão."}], temperature=0.9)
        return res.choices[0].message.content
    except: return "A inclusão transforma vidas."

@st.cache_data(ttl=3600)
def gerar_noticia_ia(api_key):
    if not api_key: return "Dica: Mantenha o PEI sempre atualizado."
    try:
        client = OpenAI(api_key=api_key)
        res = client.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "user", "content": "Dica curta sobre legislação de inclusão ou neurociência (máx 2 frases)."}], temperature=0.7)
        return res.choices[0].message.content
    except: return "O cérebro aprende durante toda a vida."

def consultar_gpt_pedagogico(api_key, dados, contexto_pdf="", modo_pratico=False):
    if not api_key: return None, "⚠️ Configure a Chave API."
    try:
        client = OpenAI(api_key=api_key)
        familia = ", ".join(dados['composicao_familiar_tags']) if dados['composicao_familiar_tags'] else "Não informado"
        evid = "\n".join([f"- {k.replace('?', '')}" for k, v in dados['checklist_evidencias'].items() if v])
        
        meds_info = "Nenhuma medicação informada."
        if dados['lista_medicamentos']:
            meds_info = "\n".join([f"- {m['nome']} ({m['posologia']}). Admin Escola: {'Sim' if m.get('escola') else 'Não'}." for m in dados['lista_medicamentos']])

        # --- SELEÇÃO DE PERSONALIDADE POR SEGMENTO ---
        serie = dados['serie'] or ""
        nivel_ensino = detectar_nivel_ensino(serie)
        
        alfabetizacao = dados.get('nivel_alfabetizacao', 'Não Avaliado')
        
        # PROMPT DE IDENTIDADE
        prompt_identidade = """
        [PERFIL_NARRATIVO]
        Inicie OBRIGATORIAMENTE com uma seção "👤 QUEM É O ESTUDANTE?".
        Escreva um parágrafo humanizado sintetizando o histórico familiar, escolar e as potencialidades (pontos fortes).
        Mostre quem é a criança por trás do diagnóstico.
        [/PERFIL_NARRATIVO]
        """

        # LÓGICA DE ALFABETIZAÇÃO
        prompt_literacia = ""
        if "Alfabético" not in alfabetizacao and alfabetizacao != "Não se aplica (Educação Infantil)":
             prompt_literacia = f"""
             [ATENÇÃO CRÍTICA: ALFABETIZAÇÃO]
             O aluno está na fase: {alfabetizacao}.
             OBRIGATÓRIO: Dentro das estratégias de adaptação, inclua 2 ações específicas de consciência fonológica ou conversão grafema-fonema para avançar para a próxima hipótese de escrita.
             [/ATENÇÃO CRÍTICA]
             """

        if nivel_ensino == "EI":
            # === EDUCAÇÃO INFANTIL (BNCC) ===
            perfil_ia = """
            Você é um Especialista em EDUCAÇÃO INFANTIL e Inclusão.
            FOCO: BNCC (Campos de Experiência e Direitos de Aprendizagem).
            NÃO use Taxonomia de Bloom. NÃO foque em alfabetização formal ou notas.
            Foque em: Brincar heurístico, interações, corpo, gestos e movimentos.
            """
            estrutura_req = f"""
            ESTRUTURA OBRIGATÓRIA (EI):
            
            {prompt_identidade}
            
            1. 🌟 AVALIAÇÃO DE REPERTÓRIO:
            [ANALISE_FARMA] Analise os fármacos (se houver) e impacto no comportamento. [/ANALISE_FARMA]
            
            [CAMPOS_EXPERIENCIA_PRIORITARIOS]
            Destaque 2 ou 3 Campos de Experiência da BNCC essenciais para este caso.
            Use emojis para ilustrar cada campo.
            [/CAMPOS_EXPERIENCIA_PRIORITARIOS]
            
            [DIREITOS_APRENDIZAGEM]
            Liste como garantir: Conviver, Brincar, Participar, Explorar, Expressar, Conhecer-se.
            [/DIREITOS_APRENDIZAGEM]
            
            [OBJETIVOS_DESENVOLVIMENTO]
            - OBJETIVO 1: ...
            - OBJETIVO 2: ...
            [FIM_OBJETIVOS]
            
            2. 🧩 ESTRATÉGIAS DE ACOLHIMENTO E ROTINA:
            (Descreva adaptações sensoriais e de rotina).
            """
            
        else:
            # === FUNDAMENTAL E MÉDIO (BLOOM, SMART) ===
            if nivel_ensino == "FI":
                perfil_ia = "Você é um Especialista em ANOS INICIAIS (Fund I). Foco: Alfabetização, Letramento e BNCC."
            elif nivel_ensino == "FII":
                perfil_ia = "Você é um Especialista em ANOS FINAIS (Fund II). Foco: Autonomia, Identidade, Organização e Habilidades BNCC."
            elif nivel_ensino == "EM":
                perfil_ia = "Você é um Especialista em ENSINO MÉDIO. Foco: Projeto de Vida e Habilidades BNCC."
            else:
                perfil_ia = "Você é um Especialista em Inclusão Escolar."

            estrutura_req = f"""
            ESTRUTURA OBRIGATÓRIA (Padrão):
            
            {prompt_identidade}
            
            1. 🌟 AVALIAÇÃO DE REPERTÓRIO:
            [ANALISE_FARMA] Analise os fármacos. [/ANALISE_FARMA]
            
            [MAPEAMENTO_BNCC]
            - **Habilidades Basais (Defasagem/Anos Anteriores):** Quais pré-requisitos precisam ser resgatados?
            - **Habilidades Focais (Ano Atual):** Quais habilidades essenciais do ano devem ser priorizadas/adaptadas?
            [/MAPEAMENTO_BNCC]
            
            [TAXONOMIA_BLOOM] Liste 3 verbos de comando. [/TAXONOMIA_BLOOM]
            
            [METAS_SMART]
            - CURTO PRAZO (2 meses): ...
            - MÉDIO PRAZO (Semestre): ...
            - LONGO PRAZO (Ano): ...
            [FIM_METAS_SMART]
            
            2. 🧩 DIRETRIZES DE ADAPTAÇÃO:
            (Adaptações curriculares e de acesso).
            {prompt_literacia}
            """

        # --- SELEÇÃO DE FORMATO (TÉCNICO VS PRÁTICO) ---
        if modo_pratico:
            prompt_sys = f"""
            {perfil_ia}
            SUA MISSÃO: Criar um GUIA PRÁTICO E DIRETO para o professor usar em sala de aula AMANHÃ.
            
            ESTRUTURA DE RESPOSTA OBRIGATÓRIA (Texto corrido e tópicos, sem blocos técnicos):
            
            # GUIA PRÁTICO PARA {serie.upper()}
            
            {prompt_identidade}
            
            1. 🎯 O QUE FAZER AMANHÃ:
            (3 ações simples e imediatas para adaptação de atividade e comportamento).
            {prompt_literacia}
            
            2. 🗣️ COMO FALAR:
            (Exemplos de comandos ou feedbacks que funcionam para este perfil).
            
            3. 🏠 ROTINA E AMBIENTE:
            (Dicas de onde sentar, como organizar a mesa, pausas).
            """
        else:
            prompt_sys = f"""
            {perfil_ia}
            SUA MISSÃO: Cruzar dados para criar um PEI Técnico Oficial.
            {estrutura_req}
            """
        
        prompt_user = f"""
        ALUNO: {dados['nome']} | SÉRIE: {serie}
        HISTÓRICO ESCOLAR: {dados['historico']}
        DINÂMICA FAMILIAR: {dados['familia']}
        POTENCIALIDADES: {', '.join(dados['potencias'])}
        DIAGNÓSTICO: {dados['diagnostico']}
        NÍVEL ALFABETIZAÇÃO: {alfabetizacao}
        MEDICAÇÃO: {meds_info}
        HIPERFOCO: {dados['hiperfoco']}
        BARREIRAS: {json.dumps(dados['barreiras_selecionadas'], ensure_ascii=False)}
        EVIDÊNCIAS: {evid}
        LAUDO: {contexto_pdf[:3000] if contexto_pdf else "Nenhum."}
        """
        
        res = client.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "system", "content": prompt_sys}, {"role": "user", "content": prompt_user}])
        return res.choices[0].message.content, None
    except Exception as e: return None, str(e)

# CÉREBRO 2: GAME MASTER (SEGMENTADO E BLINDADO)
def gerar_roteiro_gamificado(api_key, dados, pei_tecnico):
    if not api_key: return None, "Configure a API."
    try:
        client = OpenAI(api_key=api_key)
        serie = dados['serie'] or ""
        nivel_ensino = detectar_nivel_ensino(serie) 
        hiperfoco = dados['hiperfoco'] or "brincadeiras"
        
        # --- FIREWALL DE CONTEXTO ---
        contexto_seguro = f"""
        ALUNO: {dados['nome'].split()[0]}
        HIPERFOCO: {hiperfoco}
        PONTOS FORTES: {', '.join(dados['potencias'])}
        """
        
        regras_ouro = """
        REGRA DE OURO: JAMAIS mencione medicamentos, laudos, CIDs, médicos ou termos clínicos. 
        Este documento é para a criança/jovem se sentir potente. Fale de habilidades e desafios como se fosse um jogo/história.
        """

        # --- LÓGICA DE SEGMENTAÇÃO DO MAPA ---
        if nivel_ensino == "EI":
            prompt_sys = f"""
            Você é um Criador de Histórias Visuais para crianças pequenas (4-5 anos).
            {regras_ouro}
            
            SUA MISSÃO: Criar um Roteiro Visual usando MUITOS EMOJIS e pouquíssimo texto.
            Estrutura obrigatória:
            
            # ☀️ MINHA AVENTURA DO DIA
            
            🧸 **Chegada:** (Emoji e frase curta sobre chegar na escola feliz)
            🎨 **Atividades:** (Emoji e frase sobre pintar/brincar)
            🍎 **Lanche:** (Emoji sobre comer e lavar as mãos)
            🧘 **Descanso:** (Emoji sobre ficar calmo/soneca)
            👋 **Saída:** (Emoji sobre abraçar a família)
            """
            
        elif nivel_ensino == "FI":
            prompt_sys = f"""
            Você é um Game Master para crianças de 6 a 10 anos.
            {regras_ouro}
            
            SUA MISSÃO: Criar um "Quadro de Missões" empolgante.
            Estrutura obrigatória:
            
            # 🗺️ MAPA DE EXPLORAÇÃO
            
            🎒 **Equipamento:** (Materiais escolares como itens de aventura)
            ⚡ **Super Poder:** (O ponto forte do aluno transformado em habilidade)
            🚧 **O Desafio:** (O que é difícil na escola, transformado em obstáculo a pular)
            🏆 **Recompensa:** (O que ganha ao terminar: tempo livre, estrelinha)
            🤝 **Aliados:** (Professora e amigos)
            """
            
        else: # FII e EM
            prompt_sys = f"""
            Você é um Narrador de RPG para adolescentes.
            {regras_ouro}
            
            SUA MISSÃO: Criar uma "Ficha de Personagem" ou "Jornada do Herói".
            Estrutura obrigatória:
            
            # ⚔️ FICHA DE PERSONAGEM
            
            📜 **A Quest (Missão):** (Terminar o ano, aprender tal coisa, ou foco pessoal)
            🔮 **Skills (Habilidades):** (Pontos fortes cognitivos e sociais)
            🛡️ **Buffs (Apoios):** (O que ajuda: fone de ouvido, sentar na frente, tempo extra)
            👹 **Boss (Desafio):** (A dificuldade principal: ansiedade, barulho, organização)
            🧪 **Mana (Energia):** (Como recarregar no intervalo)
            """
        
        res = client.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "system", "content": prompt_sys}, {"role": "user", "content": f"Gere o roteiro para: {contexto_seguro}"}])
        return res.choices[0].message.content, None
    except Exception as e: return None, str(e)

# ==============================================================================
# 7. GERADOR PDF (DESIGN FLAT & CLEAN - COMPATÍVEL ZAPFDINGBATS)
# ==============================================================================
class PDF_Classic(FPDF):
    def header(self):
        # Fundo do cabeçalho em cinza muito suave
        self.set_fill_color(248, 248, 248)
        self.rect(0, 0, 210, 40, 'F')
        
        # Logo ou Ícone Flat
        logo = finding_logo()
        if logo: 
            self.image(logo, 10, 8, 25)
            x_offset = 40
        else:
            x_offset = 12
            
        # Título Principal
        self.set_xy(x_offset, 12)
        self.set_font('Arial', 'B', 14)
        self.set_text_color(50, 50, 50) # Cinza Chumbo
        self.cell(0, 8, 'PEI - PLANO DE ENSINO INDIVIDUALIZADO', 0, 1, 'L')
        
        # Subtítulo
        self.set_xy(x_offset, 19)
        self.set_font('Arial', '', 9)
        self.set_text_color(100, 100, 100) # Cinza Médio
        self.cell(0, 5, 'Documento Oficial de Planejamento e Flexibilização Curricular', 0, 1, 'L')
        self.ln(15)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, f'Página {self.page_no()} | Gerado via Sistema PEI 360', 0, 0, 'C')

    def section_title(self, label):
        self.ln(6)
        # Faixa cinza lateral para dar destaque "Flat"
        self.set_fill_color(230, 230, 230)
        self.rect(10, self.get_y(), 190, 8, 'F')
        
        # Ícone Flat (Dingbats) - Um quadrado sólido
        self.set_font('ZapfDingbats', '', 10)
        self.set_text_color(80, 80, 80)
        self.set_xy(12, self.get_y() + 1)
        self.cell(5, 6, 'o', 0, 0) # 'o' em ZapfDingbats é um bullet quadrado pequeno
        
        # Texto do Título
        self.set_font('Arial', 'B', 11)
        self.set_text_color(50, 50, 50)
        self.cell(0, 6, label.upper(), 0, 1, 'L')
        self.ln(4)

    def add_flat_icon_item(self, texto, bullet_type='check'):
        """Adiciona um item com ícone flat nativo do PDF"""
        self.set_font('ZapfDingbats', '', 10)
        self.set_text_color(80, 80, 80)
        
        # Seleção de ícone flat
        char = '3' # Checkmark padrão
        if bullet_type == 'arrow': char = 'PARAGRAPH' # Seta
        elif bullet_type == 'dot': char = 'l' # Bolinha
        
        self.cell(6, 5, char, 0, 0)
        
        self.set_font('Arial', '', 10)
        self.set_text_color(0)
        self.multi_cell(0, 5, texto)
        self.ln(1)

class PDF_Simple_Text(FPDF):
    """Versão Gamificada Clean - Estilo Cartão de RPG Minimalista"""
    def header(self):
        self.set_font('Arial', 'B', 16)
        self.set_text_color(50)
        self.cell(0, 10, 'ROTEIRO DE MISSÃO', 0, 1, 'C')
        self.set_draw_color(150)
        self.line(10, 25, 200, 25)
        self.ln(10)

def gerar_pdf_final(dados, tem_anexo):
    pdf = PDF_Classic()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=20)

    # 1. IDENTIFICAÇÃO
    pdf.section_title("Identificação e Contexto")
    
    # Bloco de dados tabulados
    pdf.set_font("Arial", 'B', 10); pdf.cell(35, 6, "Estudante:", 0, 0); 
    pdf.set_font("Arial", '', 10); pdf.cell(0, 6, dados['nome'], 0, 1)
    
    pdf.set_font("Arial", 'B', 10); pdf.cell(35, 6, "Série/Turma:", 0, 0); 
    pdf.set_font("Arial", '', 10); pdf.cell(0, 6, f"{dados['serie']} - {dados['turma']}", 0, 1)
    
    pdf.set_font("Arial", 'B', 10); pdf.cell(35, 6, "Diagnóstico:", 0, 0); 
    pdf.set_font("Arial", '', 10); pdf.multi_cell(0, 6, dados['diagnostico'])
    
    pdf.ln(2)

    # 2. MEDICAMENTOS E EVIDÊNCIAS
    if dados['lista_medicamentos']:
        pdf.section_title("Atenção Farmacológica")
        for m in dados['lista_medicamentos']:
            txt = f"{m['nome']} ({m['posologia']})" + (" [NA ESCOLA]" if m['escola'] else "")
            pdf.add_flat_icon_item(txt, 'dot')

    evidencias = [k.replace('?', '') for k, v in dados['checklist_evidencias'].items() if v]
    if evidencias:
        pdf.section_title("Evidências Observadas")
        for ev in evidencias:
            pdf.add_flat_icon_item(ev, 'arrow')

    # 3. SUPORTES
    if any(dados['barreiras_selecionadas'].values()):
        pdf.section_title("Plano de Suporte (Barreiras x Nível)")
        for area, itens in dados['barreiras_selecionadas'].items():
            if itens:
                pdf.set_font("Arial", 'B', 10)
                pdf.cell(0, 8, area, 0, 1)
                for item in itens:
                    nivel = dados['niveis_suporte'].get(f"{area}_{item}", "Monitorado")
                    pdf.add_flat_icon_item(f"{item} (Nível: {nivel})", 'check')

    # 4. ESTRATÉGIA IA (Texto Limpo)
    if dados['ia_sugestao']:
        pdf.add_page()
        pdf.section_title("Estratégias Pedagógicas")
        
        texto_limpo = limpar_texto_pdf(dados['ia_sugestao'])
        # Remove tags técnicas do texto final
        texto_limpo = re.sub(r'\[.*?\]', '', texto_limpo) 
        
        linhas = texto_limpo.split('\n')
        for linha in linhas:
            l = linha.strip()
            if not l: continue
            
            # Detecção de títulos/tópicos para formatar
            if re.match(r'^[1-9]\.', l) or l.isupper():
                pdf.ln(3)
                pdf.set_font('Arial', 'B', 10)
                pdf.multi_cell(0, 6, l)
                pdf.set_font('Arial', '', 10)
            elif l.startswith('-') or l.startswith('*'):
                pdf.add_flat_icon_item(l.replace('-','').replace('*','').strip(), 'dot')
            else:
                pdf.multi_cell(0, 6, l)
                
    return pdf.output(dest='S').encode('latin-1', 'replace')

def gerar_pdf_tabuleiro_simples(texto):
    pdf = PDF_Simple_Text()
    pdf.add_page()
    pdf.set_font("Arial", size=11)
    
    # Limpa emojis do texto gamificado para o PDF ficar clean
    texto_sem_emoji = limpar_texto_pdf(texto)
    
    linhas = texto_sem_emoji.split('\n')
    for linha in linhas:
        l = linha.strip()
        if not l: continue
        
        if l.isupper() or "**" in linha:
            pdf.ln(4)
            pdf.set_font("Arial", 'B', 11)
            # Desenha uma caixa cinza suave ao redor dos títulos das missões
            pdf.set_fill_color(240, 240, 240)
            pdf.cell(0, 8, l.replace('**',''), 0, 1, 'L', fill=True)
            pdf.set_font("Arial", '', 11)
        else:
            pdf.multi_cell(0, 6, l)
            
    return pdf.output(dest='S').encode('latin-1', 'ignore')

def gerar_docx_final(dados):
    doc = Document(); doc.add_heading('PEI - ' + dados['nome'], 0)
    if dados['ia_sugestao']:
        t_limpo = re.sub(r'\[.*?\]', '', dados['ia_sugestao'])
        doc.add_paragraph(t_limpo)
    b = BytesIO(); doc.save(b); b.seek(0); return b

# ==============================================================================
# 8. INTERFACE UI (PRINCIPAL) - NAVEGAÇÃO CLEAN
# ==============================================================================
# SIDEBAR
with st.sidebar:
    logo = finding_logo()
    if logo: st.image(logo, width=120)
    if 'OPENAI_API_KEY' in st.secrets: api_key = st.secrets['OPENAI_API_KEY']; st.success("✅ OpenAI OK")
    else: api_key = st.text_input("Chave OpenAI:", type="password")
    
    st.info("⚠️ **Aviso de IA:** O conteúdo é gerado por inteligência artificial. Revise todas as informações antes de aplicar. O professor é o responsável final pelo documento.")
    
    st.markdown("### 📂 Carregar Backup")
    uploaded_json = st.file_uploader("Arquivo .json", type="json")
    if uploaded_json:
        try:
            d = json.load(uploaded_json)
            if 'nasc' in d: d['nasc'] = date.fromisoformat(d['nasc'])
            if d.get('monitoramento_data'): d['monitoramento_data'] = date.fromisoformat(d['monitoramento_data'])
            st.session_state.dados.update(d); st.success("Carregado!")
        except: st.error("Erro no arquivo.")
    st.markdown("---")
    st.markdown("### 💾 Salvar & Integrar")
    if st.button("🌐 INTEGRAR NA OMNISFERA", use_container_width=True, type="primary"):
        ok, msg = salvar_aluno_integrado(st.session_state.dados)
        if ok: 
            st.success(msg)
            st.balloons()
        else: 
            st.error(msg)
    st.markdown("---")

# HEADER
logo_path = finding_logo(); b64_logo = get_base64_image(logo_path); mime = "image/png"
img_html = f'<img src="data:{mime};base64,{b64_logo}" style="height: 110px;">' if logo_path else ""

st.markdown(f"""
<div class="header-unified">
    {img_html}
    <div class="header-subtitle">Ecossistema de Inteligência Pedagógica e Inclusiva</div>
</div>""", unsafe_allow_html=True)

# NAVEGAÇÃO CLEAN - SEM EMOJIS, APENAS TEXTO
abas = [
    "INÍCIO", 
    "ESTUDANTE", 
    "EVIDÊNCIAS", 
    "REDE DE APOIO", 
    "MAPEAMENTO", 
    "PLANO DE AÇÃO", 
    "MONITORAMENTO", 
    "CONSULTORIA IA", 
    "DASHBOARD & DOCS", 
    "JORNADA GAMIFICADA"
]
tab0, tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab_mapa = st.tabs(abas)

with tab0: # INÍCIO (SEM TÍTULO FUNDAMENTOS)
    if api_key:
        with st.spinner("Conectando à IA..."):
            try:
                client = OpenAI(api_key=api_key)
                saudacao = client.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "user", "content": "Frase muito curta e motivadora para professor de educação inclusiva."}], max_tokens=30).choices[0].message.content
                noticia = client.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "user", "content": "Dica relâmpago (1 frase) sobre neurociência na escola."}], max_tokens=40).choices[0].message.content
            except:
                saudacao = "A inclusão transforma vidas."
                noticia = "O cérebro aprende quando emocionado."
        
        # HERO BANNER
        st.markdown(f"""
        <div class="dash-hero">
            <div>
                <h2 style="color:white; margin:0;">Olá, Educador(a)!</h2>
                <p style="margin:5px 0 0 0; opacity:0.9;">{saudacao}</p>
            </div>
            <div style="font-size:3rem; opacity:0.2;"><i class="ri-heart-pulse-line"></i></div>
        </div>""", unsafe_allow_html=True)
    
    # GRID DE CARDS COLORIDOS
    st.markdown("""
    <div class="home-grid">
        <a href="https://diversa.org.br/educacao-inclusiva/" target="_blank" class="rich-card">
            <div class="rich-card-top" style="background-color: #3182CE;"></div>
            <div class="rc-icon" style="background-color:#EBF8FF; color:#3182CE;"><i class="ri-book-open-line"></i></div>
            <div class="rc-title">O que é PEI?</div>
            <div class="rc-desc">Conceitos fundamentais e estruturação.</div>
        </a>
        <a href="https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2015/lei/l13146.htm" target="_blank" class="rich-card">
            <div class="rich-card-top" style="background-color: #D69E2E;"></div>
            <div class="rc-icon" style="background-color:#FFFFF0; color:#D69E2E;"><i class="ri-scales-3-line"></i></div>
            <div class="rc-title">Legislação</div>
            <div class="rc-desc">LBI e Decretos sobre inclusão.</div>
        </a>
        <a href="https://institutoneurosaber.com.br/" target="_blank" class="rich-card">
            <div class="rich-card-top" style="background-color: #D53F8C;"></div>
            <div class="rc-icon" style="background-color:#FFF5F7; color:#D53F8C;"><i class="ri-brain-line"></i></div>
            <div class="rc-title">Neurociência</div>
            <div class="rc-desc">Artigos sobre desenvolvimento atípico.</div>
        </a>
        <a href="http://basenacionalcomum.mec.gov.br/" target="_blank" class="rich-card">
            <div class="rich-card-top" style="background-color: #38A169;"></div>
            <div class="rc-icon" style="background-color:#F0FFF4; color:#38A169;"><i class="ri-compass-3-line"></i></div>
            <div class="rc-title">BNCC</div>
            <div class="rc-desc">Currículo oficial e adaptações.</div>
        </a>
    </div>
    """, unsafe_allow_html=True)

    # INSIGHT CARD
    if api_key:
        st.markdown(f"""
        <div class="insight-card">
            <div class="insight-icon"><i class="ri-lightbulb-flash-line"></i></div>
            <div>
                <h4 style="margin:0; color:#2D3748;">Insight do Dia</h4>
                <p style="margin:5px 0 0 0; font-size:0.95rem; opacity:0.9; color:#4A5568;">{noticia}</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

with tab1: # ESTUDANTE
    render_progresso()
    # PADRONIZAÇÃO DE TÍTULO
    st.markdown("### <i class='ri-user-smile-line'></i> Dossiê do Estudante", unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns([3, 2, 2, 1])
    st.session_state.dados['nome'] = c1.text_input("Nome Completo", st.session_state.dados['nome'])
    st.session_state.dados['nasc'] = c2.date_input("Nascimento", value=st.session_state.dados.get('nasc', date(2015, 1, 1)))
    try: serie_idx = LISTA_SERIES.index(st.session_state.dados['serie']) if st.session_state.dados['serie'] in LISTA_SERIES else 0
    except: serie_idx = 0
    st.session_state.dados['serie'] = c3.selectbox("Série/Ano", LISTA_SERIES, index=serie_idx, placeholder="Selecione...", help="A escolha correta da série define como a IA vai estruturar o PEI (BNCC Infantil, Bloom ou Projetos).")
    
    # --- FEEDBACK VISUAL DO SEGMENTO ---
    if st.session_state.dados['serie']:
        nome_seg, cor_seg, desc_seg = get_segmento_info_visual(st.session_state.dados['serie'])
        c3.markdown(f"<div class='segmento-badge' style='background-color:{cor_seg}'>{nome_seg}</div>", unsafe_allow_html=True)
    # -----------------------------------

    st.session_state.dados['turma'] = c4.text_input("Turma", st.session_state.dados['turma'])
    
    st.markdown("##### Histórico & Contexto Familiar")
    c_hist, c_fam = st.columns(2)
    st.session_state.dados['historico'] = c_hist.text_area("Histórico Escolar", st.session_state.dados['historico'], help="Relate retenções, trocas de escola, avanços e desafios anteriores.")
    st.session_state.dados['familia'] = c_fam.text_area("Dinâmica Familiar", st.session_state.dados['familia'], help="Quem cuida, como é a rotina em casa, quem apoia nas tarefas.")
    st.session_state.dados['composicao_familiar_tags'] = st.multiselect("Quem convive com o aluno?", LISTA_FAMILIA, default=st.session_state.dados['composicao_familiar_tags'])
    
    st.divider()
    
    # --- NOVO BLOCO: UPLOAD DE LAUDO ---
    col_pdf, col_btn_ia = st.columns([2, 1])
    with col_pdf:
        st.markdown("**📎 Upload de Laudo Médico/Escolar (PDF)**")
        up = st.file_uploader("Arraste o arquivo aqui", type="pdf", label_visibility="collapsed")
        if up: st.session_state.pdf_text = ler_pdf(up)
    
    with col_btn_ia:
        st.write("") # Espaço para alinhar
        st.write("") 
        if st.button("✨ Extrair Dados do Laudo", type="primary", use_container_width=True, disabled=(not st.session_state.pdf_text), help="A IA lerá o PDF e preencherá automaticamente o Diagnóstico e a Medicação abaixo."):
            with st.spinner("Analisando laudo..."):
                dados_extraidos, erro = extrair_dados_pdf_ia(api_key, st.session_state.pdf_text)
                if dados_extraidos:
                    # Preenche Diagnóstico
                    if dados_extraidos.get("diagnostico"):
                        st.session_state.dados['diagnostico'] = dados_extraidos["diagnostico"]
                    
                    # Preenche Medicamentos (adiciona à lista existente)
                    if dados_extraidos.get("medicamentos"):
                        for med in dados_extraidos["medicamentos"]:
                            st.session_state.dados['lista_medicamentos'].append({
                                "nome": med.get("nome", "Não ident."),
                                "posologia": med.get("posologia", ""),
                                "obs": "Extraído do Laudo",
                                "escola": False
                            })
                    st.success("Dados extraídos com sucesso!")
                    st.rerun()
                else:
                    st.error(f"Erro na extração: {erro}")
    # -----------------------------------

    st.divider()
    
    st.markdown("##### Contexto Clínico")
    st.session_state.dados['diagnostico'] = st.text_input("Diagnóstico / Hipótese Diagnóstica", st.session_state.dados['diagnostico'], help="CID ou descrição da hipótese (ex: TDAH, TEA, Dislexia).")
    
    with st.container(border=True):
        usa_med = st.toggle("💊 O aluno faz uso contínuo de medicação?", value=len(st.session_state.dados['lista_medicamentos']) > 0)
        
        if usa_med:
            c1, c2, c3 = st.columns([3, 2, 2])
            nm = c1.text_input("Nome", key="nm_med")
            pos = c2.text_input("Posologia", key="pos_med")
            admin_escola = c3.checkbox("Administrado na escola?", key="adm_esc")
            if st.button("Adicionar"):
                st.session_state.dados['lista_medicamentos'].append({"nome": nm, "posologia": pos, "obs": "", "escola": admin_escola}); st.rerun()
        
        if st.session_state.dados['lista_medicamentos']:
            st.write("---")
            for i, m in enumerate(st.session_state.dados['lista_medicamentos']):
                tag = " [NA ESCOLA]" if m.get('escola') else ""
                c_txt, c_btn = st.columns([5, 1])
                c_txt.info(f"💊 **{m['nome']}** ({m['posologia']}){tag}")
                if c_btn.button("Excluir", key=f"del_{i}"): 
                    st.session_state.dados['lista_medicamentos'].pop(i); st.rerun()

with tab2: # EVIDÊNCIAS
    render_progresso()
    # PADRONIZAÇÃO DE TÍTULO
    st.markdown("### <i class='ri-search-eye-line'></i> Coleta de Evidências (Observação Dirigida)", unsafe_allow_html=True)
    
    st.markdown("##### Nível de Alfabetização")
    st.session_state.dados['nivel_alfabetizacao'] = st.selectbox(
        "Em qual hipótese de escrita o estudante se encontra?",
        LISTA_ALFABETIZACAO,
        index=LISTA_ALFABETIZACAO.index(st.session_state.dados['nivel_alfabetizacao']) if st.session_state.dados['nivel_alfabetizacao'] in LISTA_ALFABETIZACAO else 0,
        help="Classificação baseada na psicogênese da língua escrita (Ferreiro & Teberosky). Fundamental para definir as adaptações de prova."
    )
    st.divider()
    
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("**Pedagógico**")
        for q in ["Estagnação na aprendizagem", "Dificuldade de generalização", "Dificuldade de abstração", "Lacuna em pré-requisitos"]:
            st.session_state.dados['checklist_evidencias'][q] = st.toggle(q, value=st.session_state.dados['checklist_evidencias'].get(q, False))
    with c2:
        st.markdown("**Cognitivo**")
        for q in ["Oscilação de foco", "Fadiga mental rápida", "Dificuldade de iniciar tarefas", "Esquecimento recorrente"]:
            st.session_state.dados['checklist_evidencias'][q] = st.toggle(q, value=st.session_state.dados['checklist_evidencias'].get(q, False))
    with c3:
        st.markdown("**Comportamental**")
        for q in ["Dependência de mediação (1:1)", "Baixa tolerância à frustração", "Desorganização de materiais", "Recusa de tarefas"]:
            st.session_state.dados['checklist_evidencias'][q] = st.toggle(q, value=st.session_state.dados['checklist_evidencias'].get(q, False))

with tab3: # REDE
    render_progresso()
    st.markdown("### <i class='ri-team-line'></i> Rede de Apoio Multidisciplinar", unsafe_allow_html=True)
    st.session_state.dados['rede_apoio'] = st.multiselect("Profissionais que atendem o aluno:", LISTA_PROFISSIONAIS, default=st.session_state.dados['rede_apoio'])
    st.session_state.dados['orientacoes_especialistas'] = st.text_area("Orientações Clínicas Importantes (o que os terapeutas pediram?)", st.session_state.dados['orientacoes_especialistas'])

with tab4: # MAPEAMENTO (ANTIGA BARREIRAS)
    render_progresso()
    # PADRONIZAÇÃO DE TÍTULO
    st.markdown("### <i class='ri-radar-line'></i> Mapeamento Integral", unsafe_allow_html=True)
    
    with st.container(border=True):
        st.markdown("#### <i class='ri-lightbulb-flash-line' style='color:#0F52BA'></i> Potencialidades e Hiperfoco", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        st.session_state.dados['hiperfoco'] = c1.text_input("Hiperfoco (Interesse Restrito/Intenso)", st.session_state.dados['hiperfoco'], help="Ex: Dinossauros, Trens, Minecraft. Usado para engajamento.")
        p_val = [p for p in st.session_state.dados.get('potencias', []) if p in LISTA_POTENCIAS]
        st.session_state.dados['potencias'] = c2.multiselect("Pontos Fortes e Habilidades", LISTA_POTENCIAS, default=p_val)
    st.divider()
    with st.container(border=True):
        st.markdown("#### <i class='ri-barricade-line' style='color:#FF6B6B'></i> Barreiras e Nível de Suporte (CIF)", unsafe_allow_html=True)
        c_bar1, c_bar2, c_bar3 = st.columns(3)
        def render_cat_barreira(coluna, titulo, chave_json):
            with coluna:
                st.markdown(f"**{titulo}**")
                if chave_json in LISTAS_BARREIRAS:
                    itens = LISTAS_BARREIRAS[chave_json]
                    b_salvas = [b for b in st.session_state.dados['barreiras_selecionadas'].get(chave_json, []) if b in itens]
                    sel = st.multiselect("Selecione:", itens, key=f"ms_{chave_json}", default=b_salvas, label_visibility="collapsed")
                    st.session_state.dados['barreiras_selecionadas'][chave_json] = sel
                    if sel:
                        for x in sel:
                            st.session_state.dados['niveis_suporte'][f"{chave_json}_{x}"] = st.select_slider(x, ["Autônomo", "Monitorado", "Substancial", "Muito Substancial"], value=st.session_state.dados['niveis_suporte'].get(f"{chave_json}_{x}", "Monitorado"), key=f"sl_{chave_json}_{x}")
                    st.write("")
                else:
                    st.error(f"Erro de chave: {chave_json}")
        
        render_cat_barreira(c_bar1, "Funções Cognitivas", "Funções Cognitivas")
        render_cat_barreira(c_bar1, "Sensorial e Motor", "Sensorial e Motor")
        render_cat_barreira(c_bar2, "Comunicação e Linguagem", "Comunicação e Linguagem")
        render_cat_barreira(c_bar2, "Acadêmico", "Acadêmico")
        render_cat_barreira(c_bar3, "Socioemocional", "Socioemocional")

with tab5: # PLANO
    render_progresso()
    st.markdown("### <i class='ri-tools-line'></i> Plano de Ação Estratégico", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        with st.container(border=True):
            st.markdown("#### 1. Acesso")
            st.session_state.dados['estrategias_acesso'] = st.multiselect("Recursos", ["Tempo Estendido", "Apoio Leitura/Escrita", "Material Ampliado", "Tecnologia Assistiva", "Sala Silenciosa", "Mobiliário Adaptado"], default=st.session_state.dados['estrategias_acesso'])
            st.session_state.dados['outros_acesso'] = st.text_input("Prática Personalizada (Acesso)", st.session_state.dados['outros_acesso'])
    with c2:
        with st.container(border=True):
            st.markdown("#### 2. Ensino")
            st.session_state.dados['estrategias_ensino'] = st.multiselect("Metodologia", ["Fragmentação de Tarefas", "Pistas Visuais", "Mapas Mentais", "Modelagem", "Ensino Híbrido", "Instrução Explícita"], default=st.session_state.dados['estrategias_ensino'])
            st.session_state.dados['outros_ensino'] = st.text_input("Prática Pedagógica (Ensino)", st.session_state.dados['outros_ensino'])
    with c3:
        with st.container(border=True):
            st.markdown("#### 3. Avaliação")
            st.session_state.dados['estrategias_avaliacao'] = st.multiselect("Formato", ["Prova Adaptada", "Prova Oral", "Consulta Permitida", "Portfólio", "Autoavaliação", "Parecer Descritivo"], default=st.session_state.dados['estrategias_avaliacao'])

with tab6: # MONITORAMENTO
    render_progresso()
    st.markdown("### <i class='ri-loop-right-line'></i> Monitoramento e Metas", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1: st.session_state.dados['monitoramento_data'] = st.date_input("Data da Próxima Revisão", value=st.session_state.dados.get('monitoramento_data', None))
    with c2: st.session_state.dados['status_meta'] = st.selectbox("Status da Meta Atual", ["Não Iniciado", "Em Andamento", "Parcialmente Atingido", "Atingido", "Superado"], index=0)
    st.write("")
    c3, c4 = st.columns(2)
    with c3: st.session_state.dados['parecer_geral'] = st.selectbox("Parecer Geral", ["Manter Estratégias", "Aumentar Suporte", "Reduzir Suporte (Autonomia)", "Alterar Metodologia", "Encaminhar para Especialista"], index=0)
    with c4: st.session_state.dados['proximos_passos_select'] = st.multiselect("Ações Futuras", ["Reunião com Família", "Encaminhamento Clínico", "Adaptação de Material", "Mudança de Lugar em Sala", "Novo PEI", "Observação em Sala"])

with tab7: # IA (CONSULTORIA PEDAGÓGICA)
    render_progresso()
    st.markdown("### <i class='ri-robot-2-line'></i> Consultoria Pedagógica com IA", unsafe_allow_html=True)
    
    # Exibir qual segmento a IA detectou (agora com cor e texto)
    if st.session_state.dados['serie']:
        seg_nome, seg_cor, seg_desc = get_segmento_info_visual(st.session_state.dados['serie'])
        st.markdown(f"""
        <div style="background-color: #F7FAFC; border-left: 5px solid {seg_cor}; padding: 15px; border-radius: 5px; margin-bottom: 20px;">
            <strong style="color: {seg_cor}; font-size: 1.1rem;">ℹ️ Modo Especialista: {seg_nome}</strong><br>
            <span style="color: #4A5568;">{seg_desc}</span>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.warning("⚠️ Selecione a Série/Ano na aba 'Estudante' para ativar o especialista correto.")
    
    col_left, col_right = st.columns([1, 2])
    with col_left:
        nome_aluno = st.session_state.dados['nome'].split()[0] if st.session_state.dados['nome'] else "o estudante"
        
        st.warning("⚠️ **Atenção:** A IA pode cometer erros. Revise todo o conteúdo gerado.")

        # Botão 1: PEI Técnico Padrão
        if st.button(f"✨ Criar Estratégia Técnica (PEI)", type="primary", use_container_width=True):
            res, err = consultar_gpt_pedagogico(api_key, st.session_state.dados, st.session_state.pdf_text, modo_pratico=False)
            if res: 
                st.session_state.dados['ia_sugestao'] = res
                st.balloons()
            else: st.error(err)
            
        # Botão 2: PEI Prático (Novo)
        st.write("")
        st.markdown("**Opções Avançadas:**")
        if st.button("🔄 Criar Guia Prático (Chão de Sala)", use_container_width=True, help="Gera um guia direto de manejo e adaptação, sem termos técnicos complexos."):
             res, err = consultar_gpt_pedagogico(api_key, st.session_state.dados, st.session_state.pdf_text, modo_pratico=True)
             if res:
                 st.session_state.dados['ia_sugestao'] = res
                 st.toast("Estratégia Prática Gerada com Sucesso!")
             else: st.error(err)

        with st.expander("📚 Base Técnica & Legal"):
            st.markdown("""
            **1. Documentos Norteadores**
            * NOTA TÉCNICA SEESP/MEC nº 24/2010.
            * DUA - Desenho Universal para a Aprendizagem.
            """)

    with col_right:
        if st.session_state.dados['ia_sugestao']:
            with st.expander("🔍 Entenda a Lógica (Calibragem)"):
                st.markdown("""**Como este plano foi construído:**\n* **Filtro Vygotsky:** Identificação da Zona de Desenvolvimento Proximal.\n* **Análise Farmacológica:** Impacto da medicação na aprendizagem.""")
            st.markdown(st.session_state.dados['ia_sugestao'])
            st.info("📝 **Personalize:** O texto acima é editável.")
            novo_texto = st.text_area("Editor de Conteúdo", value=st.session_state.dados['ia_sugestao'], height=400, key="editor_ia")
            st.session_state.dados['ia_sugestao'] = novo_texto
        else:
            st.info(f"👈 Clique no botão ao lado para gerar o plano de {nome_aluno}.")

with tab8: # DASHBOARD & DOCS (RENOMEADO)
    render_progresso()
    st.markdown("### <i class='ri-file-pdf-line'></i> Dashboard e Exportação", unsafe_allow_html=True)
    
    if st.session_state.dados['nome']:
        init_avatar = st.session_state.dados['nome'][0].upper() if st.session_state.dados['nome'] else "?"
        idade_str = calcular_idade(st.session_state.dados['nasc'])
        
        st.markdown(f"""
        <div class="dash-hero">
            <div style="display:flex; align-items:center; gap:20px;">
                <div class="apple-avatar">{init_avatar}</div>
                <div style="color:white;"><h1>{st.session_state.dados['nome']}</h1><p>{st.session_state.dados['serie']}</p></div>
            </div>
            <div>
                <div style="text-align:right; font-size:0.8rem; opacity:0.8;">IDADE</div>
                <div style="font-size:1.2rem; font-weight:bold;">{idade_str}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        c_kpi1, c_kpi2, c_kpi3, c_kpi4 = st.columns(4)
        with c_kpi1:
            n_pot = len(st.session_state.dados['potencias'])
            color_p = "#38A169" if n_pot > 0 else "#CBD5E0"
            st.markdown(f"""<div class="metric-card"><div class="css-donut" style="--p: {n_pot*10}%; --fill: {color_p};"><div class="d-val">{n_pot}</div></div><div class="d-lbl">Potencialidades</div></div>""", unsafe_allow_html=True)
        with c_kpi2:
            n_bar = sum(len(v) for v in st.session_state.dados['barreiras_selecionadas'].values())
            color_b = "#E53E3E" if n_bar > 5 else "#DD6B20"
            st.markdown(f"""<div class="metric-card"><div class="css-donut" style="--p: {n_bar*5}%; --fill: {color_b};"><div class="d-val">{n_bar}</div></div><div class="d-lbl">Barreiras</div></div>""", unsafe_allow_html=True)
        with c_kpi3:
             hf = st.session_state.dados['hiperfoco'] or "-"
             hf_emoji = get_hiperfoco_emoji(hf)
             st.markdown(f"""<div class="metric-card"><div style="font-size:2.5rem;">{hf_emoji}</div><div style="font-weight:800; font-size:1.1rem; color:#2D3748; margin:10px 0;">{hf}</div><div class="d-lbl">Hiperfoco</div></div>""", unsafe_allow_html=True)
        with c_kpi4:
             txt_comp, bg_c, txt_c = calcular_complexidade_pei(st.session_state.dados)
             st.markdown(f"""<div class="metric-card" style="background-color:{bg_c}; border-color:{txt_c};"><div class="comp-icon-box"><i class="ri-error-warning-line" style="color:{txt_c}; font-size: 2rem;"></i></div><div style="font-weight:800; font-size:1.1rem; color:{txt_c}; margin:5px 0;">{txt_comp}</div><div class="d-lbl" style="color:{txt_c};">Nível de Atenção</div></div>""", unsafe_allow_html=True)

        st.write("")
        c_r1, c_r2 = st.columns(2)
        with c_r1:
            tem_med = len(st.session_state.dados['lista_medicamentos']) > 0
            if tem_med:
                st.markdown(f"""<div class="soft-card sc-orange"><div class="sc-head"><i class="ri-medicine-bottle-fill" style="color:#DD6B20;"></i> Atenção Farmacológica</div><div class="sc-body">Aluno em uso de medicação contínua. Verifique a aba Estudante para detalhes e posologia.</div><div class="bg-icon">💊</div></div>""", unsafe_allow_html=True)
            else:
                st.markdown(f"""<div class="soft-card sc-green"><div class="sc-head"><i class="ri-checkbox-circle-fill" style="color:#38A169;"></i> Medicação</div><div class="sc-body">Nenhuma medicação informada.</div><div class="bg-icon">✅</div></div>""", unsafe_allow_html=True)
            st.write("")
            metas = extrair_metas_estruturadas(st.session_state.dados['ia_sugestao'])
            if metas:
                html_metas = f"""<div class="meta-row"><span style="font-size:1.2rem;">🏁</span> <b>Curto:</b> {metas['Curto']}</div><div class="meta-row"><span style="font-size:1.2rem;">🧗</span> <b>Médio:</b> {metas['Medio']}</div><div class="meta-row"><span style="font-size:1.2rem;">🏔️</span> <b>Longo:</b> {metas['Longo']}</div>"""
            else: html_metas = "Gere o plano na aba IA."
            st.markdown(f"""<div class="soft-card sc-yellow"><div class="sc-head"><i class="ri-flag-2-fill" style="color:#D69E2E;"></i> Cronograma de Metas</div><div class="sc-body">{html_metas}</div></div>""", unsafe_allow_html=True)

        with c_r2:
            # LÓGICA DE EXIBIÇÃO BLOOM vs BNCC (CORRIGIDA)
            nivel = detecting_nivel_ensino = detectar_nivel_ensino(st.session_state.dados['serie'])
            is_ei = nivel == "EI"
            
            if is_ei:
                direitos = extrair_campos_experiencia(st.session_state.dados['ia_sugestao'])
                html_tags = "".join([f'<span class="bloom-tag">{d}</span>' for d in direitos])
                card_title = "Campos de Experiência (BNCC)"
                card_desc = "Foco pedagógico prioritário:"
                card_icon = "🧸"
            else:
                verbos = extrair_bloom(st.session_state.dados['ia_sugestao'])
                html_tags = "".join([f'<span class="bloom-tag">{v}</span>' for v in verbos])
                card_title = "Taxonomia de Bloom (Verbos)"
                card_desc = "Verbos de comando sugeridos para atividades:"
                card_icon = "🧠"

            st.markdown(f"""<div class="soft-card sc-blue"><div class="sc-head"><i class="ri-lightbulb-flash-fill" style="color:#3182CE;"></i> {card_title}</div><div class="sc-body"><div style="margin-bottom:10px; font-size:0.85rem; color:#4A5568;">{card_desc}</div>{html_tags}</div><div class="bg-icon">{card_icon}</div></div>""", unsafe_allow_html=True)
            
            st.write("")
            rede_html = ""
            if st.session_state.dados['rede_apoio']:
                for prof in st.session_state.dados['rede_apoio']:
                    icon = get_pro_icon(prof)
                    rede_html += f'<span class="rede-chip">{icon} {prof}</span> '
            else: rede_html = "<span style='opacity:0.6;'>Sem rede de apoio.</span>"
            st.markdown(f"""<div class="soft-card sc-cyan"><div class="sc-head"><i class="ri-team-fill" style="color:#0BC5EA;"></i> Rede de Apoio</div><div class="sc-body">{rede_html}</div><div class="bg-icon">🤝</div></div>""", unsafe_allow_html=True)

        st.write("")
        st.markdown("##### 🧬 DNA de Suporte (Detalhamento)")
        dna_c1, dna_c2 = st.columns(2)
        areas = list(LISTAS_BARREIRAS.keys())
        for i, area in enumerate(areas):
            qtd = len(st.session_state.dados['barreiras_selecionadas'].get(area, []))
            val = min(qtd * 20, 100)
            target = dna_c1 if i < 3 else dna_c2
            color = "#3182CE"
            if val > 40: color = "#DD6B20"
            if val > 70: color = "#E53E3E"
            target.markdown(f"""<div class="dna-bar-container"><div class="dna-bar-flex"><span>{area}</span><span>{qtd} barreiras</span></div><div class="dna-bar-bg"><div class="dna-bar-fill" style="width:{val}%; background:{color};"></div></div></div>""", unsafe_allow_html=True)
        
        st.divider()
        if st.session_state.dados['ia_sugestao']:
            c1, c2 = st.columns(2)
            with c1:
                pdf = gerar_pdf_final(st.session_state.dados, len(st.session_state.pdf_text)>0)
                st.download_button("📥 Baixar PDF Oficial", pdf, f"PEI_{st.session_state.dados['nome']}.pdf", "application/pdf", type="primary")
            with c2:
                docx = gerar_docx_final(st.session_state.dados)
                st.download_button("📥 Baixar Word Editável", docx, f"PEI_{st.session_state.dados['nome']}.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document")
                st.write("")
                json_dados = json.dumps(st.session_state.dados, default=str)
                st.download_button("💾 Baixar Arquivo do Aluno (.json)", json_dados, f"PEI_{st.session_state.dados['nome']}.json", "application/json")
                st.write("")
        
        st.markdown("---")
        # BOTÃO EXTRA PARA INTEGRAÇÃO
        c_integra, c_vazio = st.columns([2, 1])
        if c_integra.button("🚀 SALVAR E SINCRONIZAR (PAE/HUB)", type="primary"):
            ok, msg = salvar_aluno_integrado(st.session_state.dados)
            if ok: st.toast(msg, icon="✅")
            else: st.error(msg)

with tab_mapa: # ABA NOVA (JORNADA DO ALUNO)
    render_progresso()
    st.markdown(f"""
    <div style="background: linear-gradient(90deg, #F6E05E 0%, #D69E2E 100%); padding: 25px; border-radius: 20px; color: #2D3748; margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.05);">
        <h3 style="margin:0; color:#2D3748;">🗺️ Jornada do Aluno: {st.session_state.dados['nome']}</h3>
        <p style="margin:5px 0 0 0; font-weight:600;">Estratégias visuais e gamificadas para o estudante.</p>
    </div>
    """, unsafe_allow_html=True)
    
    seg_nome, seg_cor, seg_desc = get_segmento_info_visual(st.session_state.dados['serie'])
    st.markdown(f"""
    <div style="background-color: #F7FAFC; border-left: 5px solid {seg_cor}; padding: 10px; border-radius: 5px; margin-bottom: 20px; font-size:0.9rem;">
        🎮 <strong>Modo Gamificação:</strong> {seg_nome} <br>
        O roteiro será adaptado com linguagem e metáforas adequadas para essa faixa etária.
    </div>
    """, unsafe_allow_html=True)

    if st.session_state.dados['ia_sugestao']:
        # Botão para Gerar o Mapa (Chama a IA Gamificada)
        if st.button("🎮 Criar Roteiro Gamificado", type="primary"):
            with st.spinner("O Game Master está criando o roteiro..."):
                texto_game, err = gerar_roteiro_gamificado(api_key, st.session_state.dados, st.session_state.dados['ia_sugestao'])
                
                if texto_game:
                    clean = texto_game.replace("[MAPA_TEXTO_GAMIFICADO]", "").replace("[FIM_MAPA_TEXTO_GAMIFICADO]", "").strip()
                    st.session_state.dados['ia_mapa_texto'] = clean
                    st.rerun()
                else:
                    st.error(f"Erro ao gerar: {err}")
        
        # Exibição do Mapa (TEXTO PURO)
        if st.session_state.dados['ia_mapa_texto']:
            st.markdown("### 📜 Roteiro de Poderes")
            st.markdown(st.session_state.dados['ia_mapa_texto']) # Renderiza Markdown nativo
            
            st.divider()
            
            # Botão de Exportar PDF SIMPLES
            pdf_mapa_simples = gerar_pdf_tabuleiro_simples(st.session_state.dados['ia_mapa_texto'])
            st.download_button("📥 Baixar PDF da Missão", pdf_mapa_simples, f"Missao_{st.session_state.dados['nome']}.pdf", "application/pdf", type="primary")

            if st.button("Recomeçar Mapa"):
                st.session_state.dados['ia_mapa_texto'] = ""
                st.rerun()
            
    else:
        st.warning("⚠️ Gere o PEI Técnico na aba 'Consultoria IA' primeiro.")

# Footer final
st.markdown("<div class='footer-signature'>PEI 360º v116.0 Gold Edition - Desenvolvido por Rodrigo A. Queiroz</div>", unsafe_allow_html=True)
