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
    page_title="Omnisfera | PEI",
    page_icon="📘",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==============================================================================
# ### BLOCO VISUAL E UTILITÁRIOS ###
# ==============================================================================
# 1. Detecção Automática de Ambiente
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

# 3. Definição Dinâmica de Cores
if IS_TEST_ENV:
    card_bg = "rgba(255, 220, 50, 0.95)" 
    card_border = "rgba(200, 160, 0, 0.5)"
else:
    card_bg = "rgba(255, 255, 255, 0.85)"
    card_border = "rgba(255, 255, 255, 0.6)"

# 4. Verificação de Acesso
def verificar_acesso():
    if "autenticado" not in st.session_state or not st.session_state["autenticado"]:
        st.error("🔒 Acesso Negado. Por favor, faça login na Página Inicial.")
        st.stop()

verificar_acesso()

# ==============================================================================
# 2. LÓGICA DO BANCO DE DADOS
# ==============================================================================
ARQUIVO_DB_CENTRAL = "banco_alunos.json"
PASTA_BANCO = "banco_alunos_backup"

if not os.path.exists(PASTA_BANCO): os.makedirs(PASTA_BANCO)

def carregar_banco():
    if os.path.exists(ARQUIVO_DB_CENTRAL):
        try:
            with open(ARQUIVO_DB_CENTRAL, "r", encoding="utf-8") as f:
                return json.load(f)
        except: return []
    return []

if 'banco_estudantes' not in st.session_state or not st.session_state.banco_estudantes:
    st.session_state.banco_estudantes = carregar_banco()

def salvar_aluno_integrado(dados):
    if not dados['nome']: return False, "Nome é obrigatório."
    
    # Backup Local
    nome_arq = re.sub(r'[^a-zA-Z0-9]', '_', dados['nome'].lower()) + ".json"
    try:
        with open(os.path.join(PASTA_BANCO, nome_arq), 'w', encoding='utf-8') as f:
            json.dump(dados, f, default=str, ensure_ascii=False, indent=4)
    except Exception as e: return False, f"Erro backup: {str(e)}"

    # Integração Omnisfera
    st.session_state.banco_estudantes = [a for a in st.session_state.banco_estudantes if a['nome'] != dados['nome']]
    novo_registro = {
        "nome": dados['nome'],
        "serie": dados.get('serie', ''),
        "hiperfoco": dados.get('hiperfoco', ''),
        "ia_sugestao": dados.get('ia_sugestao', ''),
        "diagnostico": dados.get('diagnostico', ''),
        "responsavel": st.session_state.get("usuario_nome", "Desconhecido"),
        "data_criacao": str(date.today())
    }
    st.session_state.banco_estudantes.append(novo_registro)
    
    try:
        with open(ARQUIVO_DB_CENTRAL, "w", encoding="utf-8") as f:
            json.dump(st.session_state.banco_estudantes, f, default=str, ensure_ascii=False, indent=4)
        return True, f"Aluno {dados['nome']} integrado à Omnisfera!"
    except Exception as e:
        return False, f"Erro integração: {str(e)}"

# ==============================================================================
# 3. LISTAS E GERENCIAMENTO DE ESTADO
# ==============================================================================
LISTA_SERIES = [
    "Educação Infantil (Creche)", "Educação Infantil (Pré-Escola)", 
    "1º Ano (Fund. I)", "2º Ano (Fund. I)", "3º Ano (Fund. I)", "4º Ano (Fund. I)", "5º Ano (Fund. I)", 
    "6º Ano (Fund. II)", "7º Ano (Fund. II)", "8º Ano (Fund. II)", "9º Ano (Fund. II)", 
    "1ª Série (EM)", "2ª Série (EM)", "3ª Série (EM)", "EJA (Educação de Jovens e Adultos)"
]
LISTA_ALFABETIZACAO = ["Não se aplica (EI)", "Pré-Silábico", "Silábico", "Silábico-Alfabético", "Alfabético", "Ortográfico"]
LISTAS_BARREIRAS = {
    "Funções Cognitivas": ["Atenção", "Memória", "Flexibilidade"],
    "Comunicação": ["Fala", "Compreensão", "Pragmática"],
    "Socioemocional": ["Regulação", "Interação", "Autoestima"],
    "Sensorial/Motor": ["Coordenação", "Hipersensibilidade", "Planejamento Motor"],
    "Acadêmico": ["Leitura", "Escrita", "Raciocínio"]
}
LISTA_POTENCIAS = ["Memória Visual", "Musicalidade", "Tecnologia", "Hiperfoco", "Liderança", "Esportes", "Artes", "Oralidade", "Criatividade", "Empatia"]
LISTA_PROFISSIONAIS = ["Psicólogo", "Fonoaudiólogo", "Terapeuta Ocupacional", "Neuropediatra", "Psicopedagogo", "Prof. Apoio"]
LISTA_FAMILIA = ["Mãe", "Pai", "Avós", "Irmãos", "Tios", "Tutor"]

default_state = {
    'nome': '', 'nasc': date(2015, 1, 1), 'serie': None, 'turma': '', 'diagnostico': '', 
    'lista_medicamentos': [], 'composicao_familiar_tags': [], 'historico': '', 'familia': '', 
    'hiperfoco': '', 'potencias': [], 'rede_apoio': [], 'orientacoes_especialistas': '',
    'checklist_evidencias': {}, 'nivel_alfabetizacao': 'Não se aplica (EI)',
    'barreiras_selecionadas': {k: [] for k in LISTAS_BARREIRAS.keys()},
    'niveis_suporte': {}, 'estrategias_acesso': [], 'estrategias_ensino': [], 'estrategias_avaliacao': [], 
    'ia_sugestao': '', 'ia_mapa_texto': '', 'outros_acesso': '', 'outros_ensino': '', 
    'monitoramento_data': date.today(), 'status_meta': 'Não Iniciado', 'parecer_geral': 'Manter Estratégias', 'proximos_passos_select': [],
    # CONTROLE DE FLUXO DE VALIDAÇÃO
    'status_validacao_pei': 'rascunho', 
    'feedback_ajuste': '',
    'status_validacao_game': 'rascunho',
    'feedback_ajuste_game': ''
}

if 'dados' not in st.session_state: st.session_state.dados = default_state
else:
    for key, val in default_state.items():
        if key not in st.session_state.dados: st.session_state.dados[key] = val

if 'pdf_text' not in st.session_state: st.session_state.pdf_text = ""

# ==============================================================================
# 4. FUNÇÕES UTILITÁRIAS
# ==============================================================================
def calcular_idade(data_nasc):
    if not data_nasc: return ""
    hoje = date.today()
    idade = hoje.year - data_nasc.year - ((hoje.month, hoje.day) < (data_nasc.month, data_nasc.day))
    return f"{idade} anos"

def get_hiperfoco_emoji(texto):
    if not texto: return "🚀"
    t = texto.lower()
    if "jogo" in t: return "🎮"
    if "dino" in t: return "🦖"
    return "🚀"

def detecting_nivel_ensino(serie_str):
    return detectar_nivel_ensino(serie_str)

def detectar_nivel_ensino(serie_str):
    if not serie_str: return "INDEFINIDO"
    s = serie_str.lower()
    if "infantil" in s: return "EI"
    if "1º" in s or "2º" in s or "3º" in s or "4º" in s or "5º" in s: return "FI"
    if "6º" in s or "7º" in s or "8º" in s or "9º" in s: return "FII"
    if "série" in s or "médio" in s or "eja" in s: return "EM"
    return "INDEFINIDO"

def get_segmento_info_visual(serie):
    nivel = detectar_nivel_ensino(serie)
    if nivel == "EI": return "Educação Infantil", "#4299e1", "Foco: Campos de Experiência (BNCC)."
    elif nivel == "FI": return "Anos Iniciais (Fund. I)", "#48bb78", "Foco: Alfabetização e BNCC."
    elif nivel == "FII": return "Anos Finais (Fund. II)", "#ed8936", "Foco: Autonomia e Identidade."
    elif nivel == "EM": return "Ensino Médio / EJA", "#9f7aea", "Foco: Projeto de Vida."
    return "Selecione a Série", "grey", "..."

def calcular_complexidade_pei(dados):
    n_bar = sum(len(v) for v in dados['barreiras_selecionadas'].values())
    saldo = n_bar - (3 if dados['rede_apoio'] else 0)
    if saldo <= 2: return "FLUIDA", "#F0FFF4", "#276749"
    if saldo <= 7: return "ATENÇÃO", "#FFFFF0", "#D69E2E"
    return "CRÍTICA", "#FFF5F5", "#C53030"

def extrair_tag_ia(texto, tag):
    match = re.search(fr'\[{tag}\](.*?)(\[|$)', texto, re.DOTALL)
    return match.group(1).strip() if match else ""

def extrair_metas_estruturadas(texto):
    raw = extrair_tag_ia(texto, "METAS_SMART")
    if not raw: return None
    metas = {"Curto": "...", "Medio": "...", "Longo": "..."}
    for l in raw.split('\n'):
        if "Curto" in l: metas["Curto"] = l.split(":")[-1].strip()
        elif "Médio" in l: metas["Medio"] = l.split(":")[-1].strip()
        elif "Longo" in l: metas["Longo"] = l.split(":")[-1].strip()
    return metas

def calcular_progresso():
    return 100 if st.session_state.dados['ia_sugestao'] else 20

# ----------------- BARRA DE PROGRESSO COM LOGO GIRATÓRIA -----------------
def render_progresso():
    p = calcular_progresso()
    # Usando a logo giratória carregada (Base64)
    icon_html = f'<img src="{src_logo_giratoria}" class="prog-logo-spin">'
    
    bar_color = "linear-gradient(90deg, #FF6B6B 0%, #FF8E53 100%)"
    if p >= 100: bar_color = "linear-gradient(90deg, #00C6FF 0%, #0072FF 100%)"
    
    st.markdown(f"""
    <div class="prog-container">
        <div class="prog-track">
            <div class="prog-fill" style="width: {p}%; background: {bar_color};"></div>
        </div>
        <div class="prog-icon" style="left: {p}%;">{icon_html}</div>
    </div>
    """, unsafe_allow_html=True)

# ==============================================================================
# 5. ESTILO VISUAL (DESIGN SYSTEM PREMIUM - AZUL SÓBRIO)
# ==============================================================================
def aplicar_estilo_visual():
    estilo = """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800&display=swap');
        
        /* 1. Fontes e Cores Base */
        html, body, [class*="css"] { 
            font-family: 'Nunito', sans-serif; 
            color: #2D3748; 
            background-color: #F7FAFC; 
        }
        .block-container { padding-top: 1.5rem !important; padding-bottom: 5rem !important; }
        
        /* 2. Navegação em Abas "Glow" Clean */
        div[data-baseweb="tab-border"], div[data-baseweb="tab-highlight"] { display: none !important; }
        
        /* CORREÇÃO DE SCROLL NAS ABAS - SOLUÇÃO PARA MENU LATERAL ABERTO */
        .stTabs [data-baseweb="tab-list"] { 
            gap: 8px; 
            display: flex; 
            flex-wrap: nowrap; 
            overflow-x: auto; 
            white-space: nowrap; 
            padding: 10px 5px; 
            -ms-overflow-style: none; 
            scrollbar-width: auto;
        }
        .stTabs [data-baseweb="tab-list"]::-webkit-scrollbar { height: 4px; }
        .stTabs [data-baseweb="tab-list"]::-webkit-scrollbar-thumb { background: #CBD5E0; border-radius: 4px; }

        /* ESTILO PADRÃO DAS ABAS (PÍLULA) */
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

        /* AJUSTE PARA A ÚLTIMA ABA (JORNADA GAMIFICADA) */
        .stTabs [data-baseweb="tab"]:last-of-type {
            border-color: #F6E05E !important; 
            color: #B7791F !important;
        }
        .stTabs [data-baseweb="tab"]:last-of-type[aria-selected="true"] {
            background-color: transparent !important;
            color: #D69E2E !important;
            border: 1px solid #D69E2E !important;
            box-shadow: 0 0 12px rgba(214, 158, 46, 0.5), inset 0 0 5px rgba(214, 158, 46, 0.1) !important;
        }

        /* 3. CARDS DA HOME */
        .soft-card { 
            border-radius: 12px; padding: 20px; display: flex; flex-direction: column; 
            position: relative; overflow: hidden; border: 1px solid rgba(0,0,0,0.05); border-left: 5px solid; 
        }
        .sc-blue { background-color: #EBF8FF; border-left-color: #3182CE; }
        .sc-yellow { background-color: #FFFFF0; border-left-color: #D69E2E; }
        .sc-orange { background-color: #FFF5F5; border-left-color: #DD6B20; }
        .sc-green { background-color: #F0FFF4; border-left-color: #38A169; }
        .sc-cyan { background-color: #E6FFFA; border-left-color: #0BC5EA; }
        
        .sc-head { display: flex; align-items: center; gap: 8px; font-weight: 800; font-size: 1rem; margin-bottom: 10px; color: #2D3748; }
        .sc-body { font-size: 0.85rem; color: #4A5568; line-height: 1.5; flex-grow: 1; }
        .bg-icon { position: absolute; bottom: -10px; right: 10px; font-size: 6rem; opacity: 0.08; pointer-events: none; }

        /* 4. HEADER UNIFICADO (CLEAN COM DIVISOR) */
        .header-unified { 
            background-color: white; 
            padding: 20px 40px; 
            border-radius: 16px; 
            border: 1px solid #E2E8F0; 
            box-shadow: 0 2px 10px rgba(0,0,0,0.02); 
            margin-bottom: 20px; 
            display: flex; 
            align-items: center; 
            gap: 20px; 
            justify-content: flex-start;
        }
        .header-subtitle { 
            font-size: 1.2rem; 
            color: #718096; 
            font-weight: 600; 
            border-left: 2px solid #E2E8F0; 
            padding-left: 20px; 
            line-height: 1.2; 
        }

        /* 5. BARRA DE PROGRESSO E LOGO */
        .prog-container { width: 100%; position: relative; margin: 0 0 35px 0; }
        .prog-track { width: 100%; height: 3px; background-color: #E2E8F0; border-radius: 1.5px; }
        .prog-fill { height: 100%; border-radius: 1.5px; transition: width 1s cubic-bezier(0.4, 0, 0.2, 1), background 1.5s ease; box-shadow: 0 1px 4px rgba(0,0,0,0.1); }
        .prog-icon { position: absolute; top: -16px; transition: left 1s cubic-bezier(0.4, 0, 0.2, 1); transform: translateX(-50%); z-index: 10; }
        .prog-logo-spin { height: 35px; width: 35px; animation: spin 10s linear infinite; filter: drop-shadow(0 2px 4px rgba(0,0,0,0.15)); }

        /* 6. INPUTS E BOTÕES */
        .stTextInput input, .stTextArea textarea, .stSelectbox div[data-baseweb="select"], .stMultiSelect div[data-baseweb="select"], .stNumberInput input { 
            border-radius: 8px !important; border-color: #E2E8F0 !important; 
        }
        div[data-testid="column"] .stButton button { 
            border-radius: 8px !important; font-weight: 700 !important; height: 45px !important; 
            background-color: #0F52BA !important; color: white !important; border: none !important; 
        }
        div[data-testid="column"] .stButton button:hover { background-color: #0A3D8F !important; }
        .segmento-badge { display: inline-block; padding: 4px 10px; border-radius: 12px; font-weight: 700; font-size: 0.75rem; color: white; margin-top: 5px; }
        
        /* DASHBOARD ELEMENTS */
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
        .footer-signature { margin-top: 50px; padding-top: 20px; border-top: 1px solid #E2E8F0; text-align: center; font-size: 0.8rem; color: #A0AEC0; }
        .meta-row { display: flex; align-items: center; gap: 10px; margin-bottom: 8px; font-size: 0.85rem; border-bottom: 1px solid rgba(0,0,0,0.05); padding-bottom: 5px; }
        
        .omni-badge {
            position: fixed; top: 15px; right: 15px; background: rgba(255,255,255,0.85); border: 1px solid rgba(255,255,255,0.6);
            backdrop-filter: blur(8px); padding: 4px 30px; border-radius: 20px; z-index: 9999; display: flex; align-items: center; gap: 10px;
        }
        .omni-text { font-family: 'Nunito'; font-weight: 800; font-size: 0.9rem; color: #2D3748; letter-spacing: 1px; }
        .omni-logo-spin { height: 26px; animation: spin 10s linear infinite; }
        @keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
    </style>
    <link href="https://cdn.jsdelivr.net/npm/remixicon@4.1.0/fonts/remixicon.css" rel="stylesheet">
    """
    st.markdown(estilo, unsafe_allow_html=True)

aplicar_estilo_visual()

# ==============================================================================
# 6. FUNÇÕES IA
# ==============================================================================
def extrair_dados_pdf_ia(api_key, texto_pdf):
    if not api_key: return None, "Configure a Chave API."
    try:
        client = OpenAI(api_key=api_key)
        prompt = f"Extraia do texto em JSON: {{'diagnostico': '...', 'medicamentos': [{{'nome':'...','posologia':'...'}}]}}. Texto: {texto_pdf[:3000]}"
        res = client.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "user", "content": prompt}], response_format={"type": "json_object"})
        return json.loads(res.choices[0].message.content), None
    except Exception as e: return None, str(e)

def consultar_gpt_pedagogico(api_key, dados, contexto_pdf="", modo_pratico=False, feedback_usuario=""):
    if not api_key: return None, "Configure a API."
    try:
        client = OpenAI(api_key=api_key)
        
        # --- PREPARAÇÃO DO CONTEXTO DO ALUNO ---
        familia = ", ".join(dados['composicao_familiar_tags']) if dados['composicao_familiar_tags'] else "Não informado"
        evid = "\n".join([f"- {k.replace('?', '')}" for k, v in dados['checklist_evidencias'].items() if v])
        meds_info = "Nenhuma medicação informada."
        if dados['lista_medicamentos']:
            meds_info = "\n".join([f"- {m['nome']} ({m['posologia']}). Admin Escola: {'Sim' if m.get('escola') else 'Não'}." for m in dados['lista_medicamentos']])

        serie = dados['serie'] or ""
        nivel_ensino = detectar_nivel_ensino(serie)
        alfabetizacao = dados.get('nivel_alfabetizacao', 'Não Avaliado')
        
        # --- PROMPTS DE DIRECIONAMENTO (SYSTEM PROMPTS) ---
        
        # 1. Identidade e Diagnóstico Contextual
        prompt_identidade = f"""
        [PERFIL_NARRATIVO]
        Inicie OBRIGATORIAMENTE com uma seção "👤 QUEM É O ESTUDANTE?".
        Escreva um parágrafo humanizado sintetizando o histórico familiar, escolar e as potencialidades (pontos fortes).
        
        LOGO EM SEGUIDA, crie uma subseção "**Contexto Clínico e Impacto na Aprendizagem**":
        - Analise o diagnóstico: {dados['diagnostico']}.
        - Explique TECNICAMENTE como este diagnóstico, neste nível de suporte específico, impacta a aprendizagem e a socialização.
        - Diferencie claramente (ex: Se for TEA Nível 2, explique a necessidade de mediação; se for TDAH, foco atencional).
        - NÃO apenas cite o CID, explique a funcionalidade para o professor.
        [/PERFIL_NARRATIVO]
        """

        # 2. Protocolo de Adaptação Curricular (Questionário)
        prompt_questionario_adaptacao = """
        [PROTOCOLO_ADAPTACAO_CURRICULAR]
        Com base nas evidências e no perfil do aluno, responda OBRIGATORIAMENTE a este questionário de diretrizes para o professor regente:

        1. **O estudante necessita de questões mais desafiadoras?** (Sim/Não) - Justifique brevemente.
        2. **O estudante compreende instruções complexas?** (Sim/Não)
        3. **O estudante necessita de instruções passo a passo de como realizar tarefas?** (Sim/Não)
        4. **Dividir a questão em etapas menores e mais gerenciáveis melhora o desempenho?** (Sim/Não)
        5. **Textos com parágrafos curtos melhoram a compreensão?** (Sim/Não)
        6. **O estudante precisa de dicas de apoio para resolver as questões?** (Sim/Não) - Ex: Banco de palavras, calculadora.
        7. **O estudante compreende figuras de linguagem e faz inferências?** (Sim/Não)
        8. **O estudante necessita de descrição de imagens?** (Sim/Não)
        9. **O estudante precisa de adaptação na formatação de textos?** (Sim/Não) - Se sim, especifique: (Ex: Espaçamento 1.5, Fonte Arial 14, Caixa Alta, Negrito em palavras-chave).
        [/PROTOCOLO_ADAPTACAO_CURRICULAR]
        """
        
        # 3. Lógica de Alfabetização
        prompt_literacia = ""
        if "Alfabético" not in alfabetizacao and alfabetizacao != "Não se aplica (Educação Infantil)":
             prompt_literacia = f"""
             [ATENÇÃO CRÍTICA: ALFABETIZAÇÃO]
             O aluno está na fase: {alfabetizacao}.
             OBRIGATÓRIO: Dentro das estratégias de adaptação, inclua 2 ações específicas de consciência fonológica ou conversão grafema-fonema para avançar para a próxima hipótese de escrita.
             [/ATENÇÃO CRÍTICA]
             """

        # 4. Definição do Perfil por Segmento
        if nivel_ensino == "EI":
            perfil_ia = """
            Você é um Especialista em EDUCAÇÃO INFANTIL e Inclusão.
            FOCO: BNCC (Campos de Experiência e Direitos de Aprendizagem).
            NÃO use Taxonomia de Bloom. NÃO foque em alfabetização formal ou notas.
            Foque em: Brincar heurístico, interações, corpo, gestos e movimentos.
            """
            estrutura_req = f"""
            ESTRUTURA OBRIGATÓRIA (EI):
            {prompt_identidade}
            {prompt_questionario_adaptacao}
            
            1. 🌟 AVALIAÇÃO DE REPERTÓRIO:
            [ANALISE_FARMA] Analise os fármacos (se houver) e impacto no comportamento. [/ANALISE_FARMA]
            [CAMPOS_EXPERIENCIA_PRIORITARIOS] Destaque 2 ou 3 Campos de Experiência da BNCC essenciais. Use emojis. [/CAMPOS_EXPERIENCIA_PRIORITARIOS]
            [DIREITOS_APRENDIZAGEM] Liste como garantir: Conviver, Brincar, Participar, Explorar, Expressar, Conhecer-se. [/DIREITOS_APRENDIZAGEM]
            [OBJETIVOS_DESENVOLVIMENTO] - OBJETIVO 1: ... - OBJETIVO 2: ... [FIM_OBJETIVOS]
            
            2. 🚀 PLANO DE INTERVENÇÃO E ESTRATÉGIAS:
            (Estratégias de acolhimento, rotina e adaptação sensorial).
            
            3. ⚠️ PONTOS DE ATENÇÃO FARMACOLÓGICA:
            [ANALISE_FARMA] Se houver medicação, cite efeitos colaterais (sono, sede, etc) e impactos em sala. [/ANALISE_FARMA]
            """
            
        else: # FI, FII, EM
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
            {prompt_questionario_adaptacao}
            
            1. 🌟 AVALIAÇÃO DE REPERTÓRIO:
            [ANALISE_FARMA] Analise os fármacos. [/ANALISE_FARMA]
            [MAPEAMENTO_BNCC]
            - **Habilidades Basais (Defasagem/Anos Anteriores):** Quais pré-requisitos precisam ser resgatados?
            - **Habilidades Focais (Ano Atual):** Quais habilidades essenciais do ano devem ser priorizadas/adaptadas?
            [/MAPEAMENTO_BNCC]
            [TAXONOMIA_BLOOM] Liste 3 verbos de comando. [/TAXONOMIA_BLOOM]
            [METAS_SMART] - CURTO PRAZO (2 meses): ... - MÉDIO PRAZO (Semestre): ... - LONGO PRAZO (Ano): ... [FIM_METAS_SMART]
            
            2. 🧩 DIRETRIZES DE ADAPTAÇÃO:
            (Adaptações curriculares e de acesso detalhadas).
            {prompt_literacia}
            """

        # --- SELEÇÃO DE FORMATO (TÉCNICO VS PRÁTICO) ---
        if modo_pratico:
            prompt_sys = f"""
            {perfil_ia}
            SUA MISSÃO: Criar um GUIA PRÁTICO E DIRETO para o professor usar em sala de aula AMANHÃ.
            ESTRUTURA:
            # GUIA PRÁTICO PARA {serie.upper()}
            {prompt_identidade}
            1. 🎯 O QUE FAZER AMANHÃ (3 ações simples).
            {prompt_literacia}
            2. 🗣️ COMO FALAR (Exemplos de comandos).
            3. 🏠 ROTINA E AMBIENTE (Organização).
            """
        else:
            prompt_sys = f"""
            {perfil_ia}
            SUA MISSÃO: Cruzar dados para criar um PEI Técnico Oficial e Profundo.
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
        
        # --- CHAMADA API COM O MODELO SELECIONADO NA HOME ---
        modelo_escolhido = st.session_state.get('nome_modelo', 'gpt-4o-mini')
        
        res = client.chat.completions.create(model=modelo_escolhido, messages=[{"role": "system", "content": prompt_sys}, {"role": "user", "content": prompt_user}])
        return res.choices[0].message.content, None
    except Exception as e: return None, str(e)

def gerar_roteiro_gamificado(api_key, dados, pei_tecnico, feedback_game=""):
    if not api_key: return None, "Configure a API."
    try:
        client = OpenAI(api_key=api_key)
        serie = dados['serie'] or ""
        nivel_ensino = detectar_nivel_ensino(serie) 
        hiperfoco = dados['hiperfoco'] or "brincadeiras"
        contexto_seguro = f"ALUNO: {dados['nome'].split()[0]} | HIPERFOCO: {hiperfoco} | PONTOS FORTES: {', '.join(dados['potencias'])}"
        
        prompt_feedback = f"AJUSTE: {feedback_game}" if feedback_game else ""
        
        if nivel_ensino == "EI": prompt_sys = "História Visual (4-5 anos) com emojis. # ☀️ AVENTURA ... Chegada, Atividades..."
        elif nivel_ensino == "FI": prompt_sys = "Quadro de Missões (6-10 anos) RPG. # 🗺️ MAPA ... Equipamento, Super Poder..."
        else: prompt_sys = "Ficha de Personagem RPG (Adolescente). # ⚔️ FICHA ... Quest, Skills, Buffs..."
        
        full_sys = f"{prompt_sys} {prompt_feedback}"
        res = client.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "system", "content": full_sys}, {"role": "user", "content": contexto_seguro}])
        return res.choices[0].message.content, None
    except Exception as e: return None, str(e)

# ==============================================================================
# 8. GERADOR PDF
# ==============================================================================
class PDF_Classic(FPDF):
    def header(self):
        self.set_fill_color(248, 248, 248); self.rect(0, 0, 210, 40, 'F')
        logo = finding_logo(); x_offset = 40 if logo else 12
        if logo: self.image(logo, 10, 8, 25)
        self.set_xy(x_offset, 12); self.set_font('Arial', 'B', 14); self.set_text_color(50, 50, 50)
        self.cell(0, 8, 'PEI - PLANO DE ENSINO INDIVIDUALIZADO', 0, 1, 'L')
        self.set_xy(x_offset, 19); self.set_font('Arial', '', 9); self.set_text_color(100, 100, 100)
        self.cell(0, 5, 'Documento Oficial de Planejamento e Flexibilização Curricular', 0, 1, 'L'); self.ln(15)
    def footer(self):
        self.set_y(-15); self.set_font('Arial', 'I', 8); self.set_text_color(150, 150, 150)
        self.cell(0, 10, f'Página {self.page_no()} | Gerado via Sistema PEI 360', 0, 0, 'C')
    def section_title(self, label):
        self.ln(6); self.set_fill_color(230, 230, 230); self.rect(10, self.get_y(), 190, 8, 'F')
        self.set_font('ZapfDingbats', '', 10); self.set_text_color(80, 80, 80); self.set_xy(12, self.get_y() + 1); self.cell(5, 6, 'o', 0, 0)
        self.set_font('Arial', 'B', 11); self.set_text_color(50, 50, 50); self.cell(0, 6, label.upper(), 0, 1, 'L'); self.ln(4)
    def add_flat_icon_item(self, texto, bullet_type='check'):
        self.set_font('ZapfDingbats', '', 10); self.set_text_color(80, 80, 80)
        char = '3' if bullet_type == 'check' else 'PARAGRAPH' if bullet_type == 'arrow' else 'l'
        self.cell(6, 5, char, 0, 0); self.set_font('Arial', '', 10); self.set_text_color(0); self.multi_cell(0, 5, texto); self.ln(1)
class PDF_Simple_Text(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 16); self.set_text_color(50); self.cell(0, 10, 'ROTEIRO DE MISSÃO', 0, 1, 'C'); self.set_draw_color(150); self.line(10, 25, 200, 25); self.ln(10)

def gerar_pdf_final(dados, tem_anexo):
    pdf = PDF_Classic(); pdf.add_page(); pdf.set_auto_page_break(auto=True, margin=20)
    pdf.section_title("Identificação e Contexto")
    pdf.set_font("Arial", 'B', 10); pdf.cell(35, 6, "Estudante:", 0, 0); pdf.set_font("Arial", '', 10); pdf.cell(0, 6, dados['nome'], 0, 1)
    pdf.set_font("Arial", 'B', 10); pdf.cell(35, 6, "Série/Turma:", 0, 0); pdf.set_font("Arial", '', 10); pdf.cell(0, 6, f"{dados['serie']} - {dados['turma']}", 0, 1)
    pdf.set_font("Arial", 'B', 10); pdf.cell(35, 6, "Diagnóstico:", 0, 0); pdf.set_font("Arial", '', 10); pdf.multi_cell(0, 6, dados['diagnostico']); pdf.ln(2)

    if any(dados['barreiras_selecionadas'].values()):
        pdf.section_title("Plano de Suporte (Barreiras x Nível)")
        for area, itens in dados['barreiras_selecionadas'].items():
            if itens:
                pdf.set_font("Arial", 'B', 10); pdf.cell(0, 8, limpar_texto_pdf(area), 0, 1)
                for item in itens:
                    nivel = dados['niveis_suporte'].get(f"{area}_{item}", "Monitorado")
                    pdf.add_flat_icon_item(limpar_texto_pdf(f"{item} (Nível: {nivel})"), 'check')

    if dados['ia_sugestao']:
        pdf.add_page(); pdf.section_title("Planejamento Pedagógico")
        texto_limpo = limpar_texto_pdf(dados['ia_sugestao'])
        texto_limpo = re.sub(r'\[.*?\]', '', texto_limpo) 
        for linha in texto_limpo.split('\n'):
            l = linha.strip()
            if not l: continue
            if re.match(r'^[1-9]\.', l) or l.isupper():
                pdf.ln(3); pdf.set_font('Arial', 'B', 10); pdf.multi_cell(0, 6, l); pdf.set_font('Arial', '', 10)
            elif l.startswith('-') or l.startswith('*'):
                pdf.add_flat_icon_item(l.replace('-','').replace('*','').strip(), 'dot')
            else: pdf.multi_cell(0, 6, l)
    return pdf.output(dest='S').encode('latin-1', 'replace')

def gerar_pdf_tabuleiro_simples(texto):
    pdf = PDF_Simple_Text(); pdf.add_page(); pdf.set_font("Arial", size=11)
    for linha in limpar_texto_pdf(texto).split('\n'):
        l = linha.strip()
        if not l: continue
        if l.isupper() or "**" in linha:
            pdf.ln(4); pdf.set_font("Arial", 'B', 11); pdf.set_fill_color(240, 240, 240); pdf.cell(0, 8, l.replace('**',''), 0, 1, 'L', fill=True); pdf.set_font("Arial", '', 11)
        else: pdf.multi_cell(0, 6, l)
    return pdf.output(dest='S').encode('latin-1', 'ignore')

def gerar_docx_final(dados):
    doc = Document(); doc.add_heading('PEI - ' + dados['nome'], 0)
    if dados['ia_sugestao']: doc.add_paragraph(re.sub(r'\[.*?\]', '', dados['ia_sugestao']))
    b = BytesIO(); doc.save(b); b.seek(0); return b

# ==============================================================================
# 9. INTERFACE UI
# ==============================================================================
with st.sidebar:
    logo = finding_logo()
    if logo: st.image(logo, width=120)
    if 'OPENAI_API_KEY' in st.secrets: api_key = st.secrets['OPENAI_API_KEY']; st.success("✅ OpenAI OK")
    else: api_key = st.text_input("Chave OpenAI:", type="password")
    
    st.info("⚠️ **Aviso de IA:** O conteúdo é gerado por inteligência artificial. Revise todas as informações antes de aplicar.")
    
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
        if ok: st.success(msg); st.balloons()
        else: st.error(msg)
    st.markdown("---")

logo_path = finding_logo(); b64_logo = get_base64_image(logo_path); mime = "image/png"
img_html = f'<img src="data:{mime};base64,{b64_logo}" style="height: 110px;">' if logo_path else ""

st.markdown(f"""<div class="header-unified">{img_html}<div class="header-subtitle">Planejamento Educacional Inclusivo Inteligente</div></div>""", unsafe_allow_html=True)

abas = ["INÍCIO", "ESTUDANTE", "EVIDÊNCIAS", "REDE DE APOIO", "MAPEAMENTO", "PLANO DE AÇÃO", "MONITORAMENTO", "CONSULTORIA IA", "DASHBOARD & DOCS", "JORNADA GAMIFICADA"]
tab0, tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab_mapa = st.tabs(abas)

with tab0:
    st.markdown("### 🏛️ Central de Fundamentos e Legislação")
    st.markdown("""<div class="soft-card sc-blue" style="min-height: auto; margin-bottom: 20px;"><div class="sc-head"><i class="ri-article-line" style="color:#3182CE;"></i> O que é o PEI? (Definição Técnica)</div><div class="sc-body">O <b>Plano de Ensino Individualizado (PEI)</b> é o instrumento norteador da inclusão escolar, baseado no DUA.</div><div class="bg-icon">📘</div></div>""", unsafe_allow_html=True)
    st.markdown("""<div class="soft-card sc-yellow" style="min-height: auto;"><div class="sc-head"><i class="ri-balance-line" style="color:#D69E2E;"></i> Marco Legal (2025)</div><div class="sc-body">LDB e LBI. <b>📢 Decretos 12.686 e 12.773 (Dez/2025).</b></div><div class="bg-icon">⚖️</div></div>""", unsafe_allow_html=True)

with tab1:
    render_progresso()
    st.markdown("### <i class='ri-user-smile-line'></i> Dossiê do Estudante", unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns([3, 2, 2, 1])
    st.session_state.dados['nome'] = c1.text_input("Nome Completo", st.session_state.dados['nome'])
    st.session_state.dados['nasc'] = c2.date_input("Nascimento", value=st.session_state.dados.get('nasc', date(2015, 1, 1)))
    try: serie_idx = LISTA_SERIES.index(st.session_state.dados['serie']) if st.session_state.dados['serie'] in LISTA_SERIES else 0
    except: serie_idx = 0
    st.session_state.dados['serie'] = c3.selectbox("Série/Ano", LISTA_SERIES, index=serie_idx, placeholder="Selecione...")
    if st.session_state.dados['serie']:
        nome_seg, cor_seg, desc_seg = get_segmento_info_visual(st.session_state.dados['serie'])
        c3.markdown(f"<div class='segmento-badge' style='background-color:{cor_seg}'>{nome_seg}</div>", unsafe_allow_html=True)
    st.session_state.dados['turma'] = c4.text_input("Turma", st.session_state.dados['turma'])
    st.markdown("##### Histórico & Contexto Familiar")
    c_hist, c_fam = st.columns(2)
    st.session_state.dados['historico'] = c_hist.text_area("Histórico Escolar", st.session_state.dados['historico'])
    st.session_state.dados['familia'] = c_fam.text_area("Dinâmica Familiar", st.session_state.dados['familia'])
    default_familia_valido = [x for x in st.session_state.dados['composicao_familiar_tags'] if x in LISTA_FAMILIA]
    st.session_state.dados['composicao_familiar_tags'] = st.multiselect("Quem convive com o aluno?", LISTA_FAMILIA, default=default_familia_valido)
    st.divider()
    col_pdf, col_btn_ia = st.columns([2, 1])
    with col_pdf:
        st.markdown("**📎 Upload de Laudo (PDF)**")
        up = st.file_uploader("Arraste o arquivo aqui", type="pdf", label_visibility="collapsed")
        if up: st.session_state.pdf_text = ler_pdf(up)
    with col_btn_ia:
        st.write(""); st.write("")
        if st.button("✨ Extrair Dados do Laudo", type="primary", use_container_width=True, disabled=(not st.session_state.pdf_text)):
            with st.spinner("Analisando laudo..."):
                dados_extraidos, erro = extrair_dados_pdf_ia(api_key, st.session_state.pdf_text)
                if dados_extraidos:
                    if dados_extraidos.get("diagnostico"): st.session_state.dados['diagnostico'] = dados_extraidos["diagnostico"]
                    if dados_extraidos.get("medicamentos"):
                        for med in dados_extraidos["medicamentos"]:
                            st.session_state.dados['lista_medicamentos'].append({"nome": med.get("nome", ""), "posologia": med.get("posologia", ""), "escola": False})
                    st.success("Dados extraídos!"); st.rerun()
                else: st.error(f"Erro: {erro}")
    st.divider(); st.markdown("##### Contexto Clínico"); st.session_state.dados['diagnostico'] = st.text_input("Diagnóstico", st.session_state.dados['diagnostico'])
    with st.container(border=True):
        usa_med = st.toggle("💊 O aluno faz uso contínuo de medicação?", value=len(st.session_state.dados['lista_medicamentos']) > 0)
        if usa_med:
            c1, c2, c3 = st.columns([3, 2, 2]); nm = c1.text_input("Nome", key="nm_med"); pos = c2.text_input("Posologia", key="pos_med"); admin_escola = c3.checkbox("Na escola?", key="adm_esc")
            if st.button("Adicionar"): st.session_state.dados['lista_medicamentos'].append({"nome": nm, "posologia": pos, "escola": admin_escola}); st.rerun()
        if st.session_state.dados['lista_medicamentos']:
            st.write("---")
            for i, m in enumerate(st.session_state.dados['lista_medicamentos']):
                tag = " [NA ESCOLA]" if m.get('escola') else ""; c_txt, c_btn = st.columns([5, 1]); c_txt.info(f"💊 **{m['nome']}** ({m['posologia']}){tag}")
                if c_btn.button("Excluir", key=f"del_{i}"): st.session_state.dados['lista_medicamentos'].pop(i); st.rerun()

with tab2:
    render_progresso(); st.markdown("### <i class='ri-search-eye-line'></i> Coleta de Evidências", unsafe_allow_html=True)
    st.session_state.dados['nivel_alfabetizacao'] = st.selectbox("Hipótese de Escrita", LISTA_ALFABETIZACAO, index=LISTA_ALFABETIZACAO.index(st.session_state.dados['nivel_alfabetizacao']) if st.session_state.dados['nivel_alfabetizacao'] in LISTA_ALFABETIZACAO else 0)
    st.divider(); c1, c2, c3 = st.columns(3)
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

with tab3:
    render_progresso(); st.markdown("### <i class='ri-team-line'></i> Rede de Apoio", unsafe_allow_html=True)
    st.session_state.dados['rede_apoio'] = st.multiselect("Profissionais:", LISTA_PROFISSIONAIS, default=st.session_state.dados['rede_apoio'])
    st.session_state.dados['orientacoes_especialistas'] = st.text_area("Orientações Clínicas", st.session_state.dados['orientacoes_especialistas'])

with tab4:
    render_progresso(); st.markdown("### <i class='ri-radar-line'></i> Mapeamento", unsafe_allow_html=True)
    with st.container(border=True):
        st.markdown("#### Potencialidades e Hiperfoco"); c1, c2 = st.columns(2); st.session_state.dados['hiperfoco'] = c1.text_input("Hiperfoco", st.session_state.dados['hiperfoco']); p_val = [p for p in st.session_state.dados.get('potencias', []) if p in LISTA_POTENCIAS]; st.session_state.dados['potencias'] = c2.multiselect("Pontos Fortes", LISTA_POTENCIAS, default=p_val)
    st.divider()
    with st.container(border=True):
        st.markdown("#### Barreiras e Nível de Suporte (CIF)"); c_bar1, c_bar2, c_bar3 = st.columns(3)
        def render_cat_barreira(coluna, titulo, chave_json):
            with coluna:
                st.markdown(f"**{titulo}**"); itens = LISTAS_BARREIRAS[chave_json]; b_salvas = [b for b in st.session_state.dados['barreiras_selecionadas'].get(chave_json, []) if b in itens]; sel = st.multiselect("Selecione:", itens, key=f"ms_{chave_json}", default=b_salvas, label_visibility="collapsed"); st.session_state.dados['barreiras_selecionadas'][chave_json] = sel
                if sel:
                    for x in sel: st.session_state.dados['niveis_suporte'][f"{chave_json}_{x}"] = st.select_slider(x, ["Autônomo", "Monitorado", "Substancial", "Muito Substancial"], value=st.session_state.dados['niveis_suporte'].get(f"{chave_json}_{x}", "Monitorado"), key=f"sl_{chave_json}_{x}")
        render_cat_barreira(c_bar1, "Funções Cognitivas", "Funções Cognitivas"); render_cat_barreira(c_bar1, "Sensorial e Motor", "Sensorial e Motor"); render_cat_barreira(c_bar2, "Comunicação e Linguagem", "Comunicação e Linguagem"); render_cat_barreira(c_bar2, "Acadêmico", "Acadêmico"); render_cat_barreira(c_bar3, "Socioemocional", "Socioemocional")

with tab5:
    render_progresso(); st.markdown("### <i class='ri-tools-line'></i> Plano de Ação", unsafe_allow_html=True); c1, c2, c3 = st.columns(3)
    with c1: st.markdown("#### 1. Acesso"); st.session_state.dados['estrategias_acesso'] = st.multiselect("Recursos", ["Tempo Estendido", "Apoio Leitura/Escrita", "Material Ampliado", "Tecnologia Assistiva", "Sala Silenciosa", "Mobiliário Adaptado"], default=st.session_state.dados['estrategias_acesso']); st.session_state.dados['outros_acesso'] = st.text_input("Personalizado (Acesso)", st.session_state.dados['outros_acesso'])
    with c2: st.markdown("#### 2. Ensino"); st.session_state.dados['estrategias_ensino'] = st.multiselect("Metodologia", ["Fragmentação de Tarefas", "Pistas Visuais", "Mapas Mentais", "Modelagem", "Ensino Híbrido", "Instrução Explícita"], default=st.session_state.dados['estrategias_ensino']); st.session_state.dados['outros_ensino'] = st.text_input("Personalizado (Ensino)", st.session_state.dados['outros_ensino'])
    with c3: st.markdown("#### 3. Avaliação"); st.session_state.dados['estrategias_avaliacao'] = st.multiselect("Formato", ["Prova Adaptada", "Prova Oral", "Consulta Permitida", "Portfólio", "Autoavaliação", "Parecer Descritivo"], default=st.session_state.dados['estrategias_avaliacao'])

with tab6:
    render_progresso(); st.markdown("### <i class='ri-loop-right-line'></i> Monitoramento", unsafe_allow_html=True); st.session_state.dados['monitoramento_data'] = st.date_input("Data da Próxima Revisão", value=st.session_state.dados.get('monitoramento_data', None)); st.divider(); st.warning("⚠️ **ATENÇÃO:** Preencher somente na revisão do PEI.")
    with st.container(border=True):
        c2, c3 = st.columns(2)
        with c2: st.session_state.dados['status_meta'] = st.selectbox("Status da Meta", ["Não Iniciado", "Em Andamento", "Parcialmente Atingido", "Atingido", "Superado"], index=0)
        with c3: st.session_state.dados['parecer_geral'] = st.selectbox("Parecer Geral", ["Manter Estratégias", "Aumentar Suporte", "Reduzir Suporte (Autonomia)", "Alterar Metodologia", "Encaminhar para Especialista"], index=0)
        st.session_state.dados['proximos_passos_select'] = st.multiselect("Ações Futuras", ["Reunião com Família", "Encaminhamento Clínico", "Adaptação de Material", "Mudança de Lugar em Sala", "Novo PEI", "Observação em Sala"])

with tab7: 
    render_progresso()
    st.markdown("### <i class='ri-robot-2-line'></i> Consultoria Pedagógica", unsafe_allow_html=True)
    if st.session_state.dados['serie']:
        seg_nome, seg_cor, seg_desc = get_segmento_info_visual(st.session_state.dados['serie'])
        st.markdown(f"<div style='background-color: #F7FAFC; border-left: 5px solid {seg_cor}; padding: 15px; border-radius: 5px; margin-bottom: 20px;'><strong style='color: {seg_cor};'>ℹ️ Modo Especialista: {seg_nome}</strong><br><span style='color: #4A5568;'>{seg_desc}</span></div>", unsafe_allow_html=True)
    else: st.warning("⚠️ Selecione a Série/Ano na aba 'Estudante'.")
    
    if not st.session_state.dados['ia_sugestao'] or st.session_state.dados.get('status_validacao_pei') == 'rascunho':
        col_btn, col_info = st.columns([1, 2])
        with col_btn:
            if st.button(f"✨ Gerar Estratégia Técnica", type="primary", use_container_width=True):
                res, err = consultar_gpt_pedagogico(api_key, st.session_state.dados, st.session_state.pdf_text, modo_pratico=False)
                if res: 
                    st.session_state.dados['ia_sugestao'] = res; st.session_state.dados['status_validacao_pei'] = 'revisao'; st.rerun()
                else: st.error(err)
            st.write("")
            if st.button("🔄 Gerar Guia Prático", use_container_width=True):
                 res, err = consultar_gpt_pedagogico(api_key, st.session_state.dados, st.session_state.pdf_text, modo_pratico=True)
                 if res:
                     st.session_state.dados['ia_sugestao'] = res; st.session_state.dados['status_validacao_pei'] = 'revisao'; st.rerun()
                 else: st.error(err)
    
    elif st.session_state.dados.get('status_validacao_pei') in ['revisao', 'aprovado']:
        
        with st.expander("🧠 Como a IA construiu este relatório"):
            st.markdown("""
            1. **Análise de Contexto:** Cruzamento entre diagnóstico, idade ({}) e série ({}).
            2. **Filtro Vygotsky:** Identificação da Zona de Desenvolvimento Proximal baseada nas barreiras citadas.
            3. **Mapeamento BNCC:** Seleção de códigos de habilidades compatíveis com o ano letivo.
            """.format(calcular_idade(st.session_state.dados['nasc']), st.session_state.dados['serie']))
            
        with st.expander("🛡️ Calibragem e Segurança"):
            st.markdown("""
            * **Verificação Farmacológica:** O sistema isola a análise de medicação para evitar viés pedagógico.
            * **Blindagem de Dados:** Nenhuma informação pessoal é retida pela IA após o processamento.
            * **Supervisão Humana:** Este rascunho exige validação obrigatória do professor.
            """)

        st.markdown("#### 📝 Revisão do Plano")
        texto_visual = re.sub(r'\[.*?\]', '', st.session_state.dados['ia_sugestao'])
        st.markdown(texto_visual)
        st.divider()
        st.markdown("**⚠️ Responsabilidade do Educador:** A IA pode cometer erros. Valide.")
        
        if st.session_state.dados.get('status_validacao_pei') == 'revisao':
            c_ok, c_ajuste = st.columns(2)
            if c_ok.button("✅ Aprovar Plano", type="primary", use_container_width=True):
                st.session_state.dados['status_validacao_pei'] = 'aprovado'; st.success("Plano aprovado!"); st.rerun()
            if c_ajuste.button("❌ Solicitar Ajuste", use_container_width=True):
                st.session_state.dados['status_validacao_pei'] = 'ajustando'; st.rerun()
        
        elif st.session_state.dados.get('status_validacao_pei') == 'aprovado':
             st.success("Plano Validado.")
             novo_texto = st.text_area("Edição Final Manual", value=st.session_state.dados['ia_sugestao'], height=300)
             st.session_state.dados['ia_sugestao'] = novo_texto
             if st.button("Regerar do Zero"):
                 st.session_state.dados['ia_sugestao'] = ''; st.session_state.dados['status_validacao_pei'] = 'rascunho'; st.rerun()

    elif st.session_state.dados.get('status_validacao_pei') == 'ajustando':
        st.warning("Descreva o ajuste:")
        feedback = st.text_area("Seu feedback:", placeholder="Ex: Foque mais na alfabetização...")
        if st.button("Regerar com Ajustes", type="primary"):
            res, err = consultar_gpt_pedagogico(api_key, st.session_state.dados, st.session_state.pdf_text, modo_pratico=False, feedback_usuario=feedback)
            if res:
                st.session_state.dados['ia_sugestao'] = res; st.session_state.dados['status_validacao_pei'] = 'revisao'; st.rerun()
            else: st.error(err)
        if st.button("Cancelar"):
            st.session_state.dados['status_validacao_pei'] = 'revisao'; st.rerun()

with tab8:
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
            <div><div style="text-align:right; font-size:0.8rem;">IDADE</div><div style="font-size:1.2rem; font-weight:bold;">{idade_str}</div></div>
        </div>""", unsafe_allow_html=True)
        
        c_kpi1, c_kpi2, c_kpi3, c_kpi4 = st.columns(4)
        with c_kpi1:
            n_pot = len(st.session_state.dados['potencias']); color_p = "#38A169" if n_pot > 0 else "#CBD5E0"
            st.markdown(f"""<div class="metric-card"><div class="css-donut" style="--p: {n_pot*10}%; --fill: {color_p};"><div class="d-val">{n_pot}</div></div><div class="d-lbl">Potencialidades</div></div>""", unsafe_allow_html=True)
        with c_kpi2:
            n_bar = sum(len(v) for v in st.session_state.dados['barreiras_selecionadas'].values()); color_b = "#E53E3E" if n_bar > 5 else "#DD6B20"
            st.markdown(f"""<div class="metric-card"><div class="css-donut" style="--p: {n_bar*5}%; --fill: {color_b};"><div class="d-val">{n_bar}</div></div><div class="d-lbl">Barreiras</div></div>""", unsafe_allow_html=True)
        with c_kpi3:
             hf = st.session_state.dados['hiperfoco'] or "-"; hf_emoji = get_hiperfoco_emoji(hf)
             st.markdown(f"""<div class="metric-card"><div style="font-size:2.5rem;">{hf_emoji}</div><div style="font-weight:800; font-size:1.1rem; color:#2D3748; margin:10px 0;">{hf}</div><div class="d-lbl">Hiperfoco</div></div>""", unsafe_allow_html=True)
        with c_kpi4:
             txt_comp, bg_c, txt_c = calcular_complexidade_pei(st.session_state.dados)
             st.markdown(f"""<div class="metric-card" style="background-color:{bg_c}; border-color:{txt_c};"><div class="comp-icon-box"><i class="ri-error-warning-line" style="color:{txt_c}; font-size: 2rem;"></i></div><div style="font-weight:800; font-size:1.1rem; color:{txt_c}; margin:5px 0;">{txt_comp}</div><div class="d-lbl" style="color:{txt_c};">Nível de Atenção (Execução)</div></div>""", unsafe_allow_html=True)

        st.write(""); c_r1, c_r2 = st.columns(2)
        with c_r1:
            if len(st.session_state.dados['lista_medicamentos']) > 0:
                st.markdown(f"""<div class="soft-card sc-orange"><div class="sc-head"><i class="ri-medicine-bottle-fill" style="color:#DD6B20;"></i> Atenção Farmacológica</div><div class="sc-body">Aluno em uso de medicação contínua.</div><div class="bg-icon">💊</div></div>""", unsafe_allow_html=True)
            else:
                st.markdown(f"""<div class="soft-card sc-green"><div class="sc-head"><i class="ri-checkbox-circle-fill" style="color:#38A169;"></i> Medicação</div><div class="sc-body">Nenhuma medicação informada.</div><div class="bg-icon">✅</div></div>""", unsafe_allow_html=True)
            st.write("")
            metas = extrair_metas_estruturadas(st.session_state.dados['ia_sugestao'])
            html_metas = f"""<div class="meta-row"><span style="font-size:1.2rem;">🏁</span> <b>Curto:</b> {metas['Curto']}</div><div class="meta-row"><span style="font-size:1.2rem;">🧗</span> <b>Médio:</b> {metas['Medio']}</div><div class="meta-row"><span style="font-size:1.2rem;">🏔️</span> <b>Longo:</b> {metas['Longo']}</div>""" if metas else "Gere o plano na aba IA."
            st.markdown(f"""<div class="soft-card sc-yellow"><div class="sc-head"><i class="ri-flag-2-fill" style="color:#D69E2E;"></i> Cronograma de Metas</div><div class="sc-body">{html_metas}</div></div>""", unsafe_allow_html=True)

        with c_r2:
            # SUBSTITUIÇÃO: HABILIDADES BNCC (Causava erro) -> ESTRATÉGIAS SELECIONADAS (Dados Reais)
            n_acc = len(st.session_state.dados['estrategias_acesso'])
            n_ens = len(st.session_state.dados['estrategias_ensino'])
            n_ava = len(st.session_state.dados['estrategias_avaliacao'])
            card_title = "Estratégias Ativas"; card_icon = "🛠️"
            
            html_tags = f"""
            <div style="display:flex; justify-content:space-between; border-bottom:1px solid #eee; padding:4px 0;"><span>Acesso/Recursos:</span> <b>{n_acc}</b></div>
            <div style="display:flex; justify-content:space-between; border-bottom:1px solid #eee; padding:4px 0;"><span>Ensino/Metodologia:</span> <b>{n_ens}</b></div>
            <div style="display:flex; justify-content:space-between; padding:4px 0;"><span>Avaliação:</span> <b>{n_ava}</b></div>
            """
            st.markdown(f"""<div class="soft-card sc-blue"><div class="sc-head"><i class="ri-tools-fill" style="color:#3182CE;"></i> {card_title}</div><div class="sc-body">{html_tags}</div><div class="bg-icon">{card_icon}</div></div>""", unsafe_allow_html=True)
            
            st.write("")
            rede_html = "".join([f'<span class="rede-chip">{get_pro_icon(p)} {p}</span> ' for p in st.session_state.dados['rede_apoio']]) if st.session_state.dados['rede_apoio'] else "<span style='opacity:0.6;'>Sem rede.</span>"
            st.markdown(f"""<div class="soft-card sc-cyan"><div class="sc-head"><i class="ri-team-fill" style="color:#0BC5EA;"></i> Rede de Apoio</div><div class="sc-body">{rede_html}</div><div class="bg-icon">🤝</div></div>""", unsafe_allow_html=True)

        st.write(""); st.markdown("##### 🧬 DNA de Suporte")
        dna_c1, dna_c2 = st.columns(2)
        for i, area in enumerate(LISTAS_BARREIRAS.keys()):
            qtd = len(st.session_state.dados['barreiras_selecionadas'].get(area, [])); val = min(qtd * 20, 100)
            target = dna_c1 if i < 3 else dna_c2; color = "#3182CE"
            if val > 40: color = "#DD6B20"
            if val > 70: color = "#E53E3E"
            target.markdown(f"""<div class="dna-bar-container"><div class="dna-bar-flex"><span>{area}</span><span>{qtd} barreiras</span></div><div class="dna-bar-bg"><div class="dna-bar-fill" style="width:{val}%; background:{color};"></div></div></div>""", unsafe_allow_html=True)
        
        st.divider()
        if st.session_state.dados['ia_sugestao']:
            # BOTÕES REORGANIZADOS POR GRUPOS
            st.markdown("#### 📤 Exportação e Salvar")
            col_docs, col_data, col_sys = st.columns(3)
            with col_docs:
                st.caption("📄 Documentos")
                pdf = gerar_pdf_final(st.session_state.dados, len(st.session_state.pdf_text)>0)
                st.download_button("Baixar PDF Oficial", pdf, f"PEI_{st.session_state.dados['nome']}.pdf", "application/pdf", use_container_width=True)
                docx = gerar_docx_final(st.session_state.dados)
                st.download_button("Baixar Word Editável", docx, f"PEI_{st.session_state.dados['nome']}.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document", use_container_width=True)
            with col_data:
                st.caption("💾 Backup Local")
                st.download_button("Salvar Arquivo .JSON", json.dumps(st.session_state.dados, default=str), f"PEI_{st.session_state.dados['nome']}.json", "application/json", use_container_width=True, help="Salve este arquivo no seu computador para editar depois.")
            with col_sys:
                st.caption("🌐 Sistema")
                if st.button("Sincronizar (Omnisfera)", type="primary", use_container_width=True):
                    ok, msg = salvar_aluno_integrado(st.session_state.dados)
                    if ok: st.toast(msg, icon="✅")
                    else: st.error(msg)
        else:
            st.info("Gere o Plano na aba Consultoria IA para liberar o download.")

with tab_mapa:
    render_progresso()
    st.markdown(f"<div style='background: linear-gradient(90deg, #F6E05E 0%, #D69E2E 100%); padding: 25px; border-radius: 20px; color: #2D3748; margin-bottom: 20px;'><h3 style='margin:0;'>🗺️ Jornada: {st.session_state.dados['nome']}</h3></div>", unsafe_allow_html=True)
    
    # EXPLICAÇÃO DA FERRAMENTA
    st.info("ℹ️ **O que é isso?** Esta ferramenta gera um material **para o estudante**. É uma tradução gamificada do PEI para que a própria criança/jovem entenda seus desafios e potências de forma lúdica. Imprima e cole no caderno!")

    if st.session_state.dados['ia_sugestao']:
        if st.session_state.dados.get('status_validacao_game') == 'rascunho':
            if st.button("🎮 Criar Roteiro Gamificado", type="primary"):
                with st.spinner("Game Master criando..."):
                    texto_game, err = gerar_roteiro_gamificado(api_key, st.session_state.dados, st.session_state.dados['ia_sugestao'])
                    if texto_game:
                        st.session_state.dados['ia_mapa_texto'] = texto_game.replace("[MAPA_TEXTO_GAMIFICADO]", "").strip()
                        st.session_state.dados['status_validacao_game'] = 'revisao'
                        st.rerun()
                    else: st.error(err)

        elif st.session_state.dados.get('status_validacao_game') == 'revisao':
            st.markdown("### 📜 Roteiro Gerado")
            st.markdown(st.session_state.dados['ia_mapa_texto'])
            st.divider()
            c_ok, c_refaz = st.columns(2)
            if c_ok.button("✅ Aprovar Missão"):
                st.session_state.dados['status_validacao_game'] = 'aprovado'; st.rerun()
            if c_refaz.button("❌ Refazer"):
                st.session_state.dados['status_validacao_game'] = 'ajustando'; st.rerun()

        elif st.session_state.dados.get('status_validacao_game') == 'aprovado':
            st.success("Missão Aprovada! Pronto para imprimir.")
            st.markdown(st.session_state.dados['ia_mapa_texto'])
            pdf_mapa = gerar_pdf_tabuleiro_simples(st.session_state.dados['ia_mapa_texto'])
            st.download_button("📥 Baixar Missão em PDF", pdf_mapa, f"Missao_{st.session_state.dados['nome']}.pdf", "application/pdf", type="primary")
            if st.button("Criar Nova Missão"):
                st.session_state.dados['status_validacao_game'] = 'rascunho'; st.rerun()

        elif st.session_state.dados.get('status_validacao_game') == 'ajustando':
            fb_game = st.text_input("O que mudar na história?", placeholder="Ex: Use super-heróis em vez de exploração...")
            if st.button("Regerar História"):
                with st.spinner("Reescrevendo..."):
                    texto_game, err = gerar_roteiro_gamificado(api_key, st.session_state.dados, st.session_state.dados['ia_sugestao'], fb_game)
                    if texto_game:
                        st.session_state.dados['ia_mapa_texto'] = texto_game.replace("[MAPA_TEXTO_GAMIFICADO]", "").strip()
                        st.session_state.dados['status_validacao_game'] = 'revisao'; st.rerun()

    else: st.warning("⚠️ Gere o PEI Técnico na aba 'Consultoria IA' primeiro.")

st.markdown("<div class='footer-signature'>PEI 360º v116.0 Gold Edition - Desenvolvido por Rodrigo A. Queiroz</div>", unsafe_allow_html=True)
