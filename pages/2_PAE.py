# ==============================================================================
# PARTE 1/4: CONFIGURAÇÕES, ESTILOS E AUTENTICAÇÃO
# ==============================================================================

import streamlit as st
import os
from openai import OpenAI
import json
import pandas as pd
from datetime import date, datetime, timedelta
import base64
import requests
import time
import uuid

# ==============================================================================
# 1. CONFIGURAÇÃO E SEGURANÇA
# ==============================================================================
st.set_page_config(
    page_title="PAEE & T.A. | Omnisfera", 
    page_icon="🧩", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==============================================================================
# BLOCO VISUAL INTELIGENTE: HEADER OMNISFERA
# ==============================================================================
try:
    IS_TEST_ENV = st.secrets.get("ENV") == "TESTE"
except:
    IS_TEST_ENV = False

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
<link href="https://cdn.jsdelivr.net/npm/remixicon@4.1.0/fonts/remixicon.css" rel="stylesheet">

<style>
    /* CARD FLUTUANTE (OMNISFERA) */
    .omni-badge {{
        position: fixed; top: 15px; right: 15px;
        background: {card_bg}; border: 1px solid {card_border};
        backdrop-filter: blur(8px); padding: 4px 30px;
        min-width: 260px; justify-content: center;
        border-radius: 20px; box-shadow: 0 4px 15px rgba(0,0,0,0.08);
        z-index: 999990; display: flex; align-items: center; gap: 10px;
        pointer-events: none;
    }}
    .omni-text {{ font-family: 'Plus Jakarta Sans', sans-serif; font-weight: 800; font-size: 0.9rem; color: #2D3748; letter-spacing: 1px; text-transform: uppercase; }}
    @keyframes spin-slow {{ from {{ transform: rotate(0deg); }} to {{ transform: rotate(360deg); }} }}
    .omni-logo-spin {{ height: 26px; width: 26px; animation: spin-slow 10s linear infinite; }}

    /* CARD HERO */
    .mod-card-wrapper {{ display: flex; flex-direction: column; margin-bottom: 20px; border-radius: 16px; overflow: hidden; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.02); }}
    .mod-card-rect {{ background: white; border-radius: 16px 16px 0 0; padding: 0; border: 1px solid #E2E8F0; border-bottom: none; display: flex; flex-direction: row; align-items: center; height: 130px; width: 100%; position: relative; overflow: hidden; transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1); }}
    .mod-card-rect:hover {{ transform: translateY(-4px); box-shadow: 0 12px 24px rgba(0, 0, 0, 0.08); border-color: #CBD5E1; }}
    .mod-bar {{ width: 6px; height: 100%; flex-shrink: 0; }}
    .mod-icon-area {{ width: 90px; height: 100%; display: flex; align-items: center; justify-content: center; font-size: 1.8rem; flex-shrink: 0; background: transparent !important; border-right: 1px solid #F1F5F9; transition: all 0.3s ease; }}
    .mod-card-rect:hover .mod-icon-area {{ transform: scale(1.05); }}
    .mod-content {{ flex-grow: 1; padding: 0 24px; display: flex; flex-direction: column; justify-content: center; }}
    .mod-title {{ font-weight: 800; font-size: 1.1rem; color: #1E293B; margin-bottom: 6px; letter-spacing: -0.3px; transition: color 0.2s; }}
    .mod-card-rect:hover .mod-title {{ color: #0D9488; }}
    .mod-desc {{ font-size: 0.8rem; color: #64748B; line-height: 1.4; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }}

    /* CORES */
    .c-teal {{ background: #0D9488 !important; }}
    .bg-teal-soft {{ background: transparent !important; color: #0D9488 !important; }}
    .c-purple {{ background: #8B5CF6 !important; }}
    .bg-purple-soft {{ background: transparent !important; color: #8B5CF6 !important; }}

    /* ABAS */
    .stTabs [data-baseweb="tab-list"] {{ 
        gap: 2px !important; 
        background-color: transparent !important; 
        padding: 0 !important; 
        border-radius: 0 !important; 
        margin-top: 24px !important; 
        border-bottom: 2px solid #E2E8F0 !important; 
        flex-wrap: wrap !important; 
    }}
    .stTabs [data-baseweb="tab"] {{ 
        height: 36px !important; 
        white-space: nowrap !important; 
        background-color: transparent !important; 
        border-radius: 8px 8px 0 0 !important; 
        padding: 0 20px !important; 
        color: #64748B !important; 
        font-weight: 600 !important; 
        font-size: 0.85rem !important; 
        text-transform: uppercase !important; 
        letter-spacing: 0.3px !important; 
        transition: all 0.2s ease !important; 
        border: none !important; 
        margin: 0 2px 0 0 !important; 
        position: relative !important;
    }}
    .stTabs [aria-selected="true"] {{ 
        background-color: transparent !important; 
        color: #0D9488 !important; 
        font-weight: 700 !important; 
        border: none !important; 
        box-shadow: none !important; 
    }}
    .stTabs [aria-selected="true"]::after {{
        content: '';
        position: absolute;
        bottom: -2px;
        left: 0;
        right: 0;
        height: 3px;
        background-color: #0D9488;
        border-radius: 2px 2px 0 0;
    }}
    .stTabs [data-baseweb="tab"]:not([aria-selected="true"]) {{ 
        background-color: transparent !important; 
    }}
    .stTabs [data-baseweb="tab"]:hover:not([aria-selected="true"]) {{ 
        background-color: #F8FAFC !important; 
        color: #475569 !important; 
    }}
    .stTabs [data-baseweb="tab"]::before, .stTabs [aria-selected="true"]::before {{ 
        display: none !important; 
    }}

    /* PEDAGOGIA BOX */
    .pedagogia-box {{ background-color: #F8FAFC; border-left: 4px solid #CBD5E1; padding: 20px; border-radius: 0 12px 12px 0; margin-bottom: 25px; font-size: 0.95rem; color: #4A5568; }}

    /* RESOURCE BOX */
    .resource-box {{ 
        background: #F8FAFC; 
        border: 1px solid #E2E8F0; 
        border-radius: 12px; 
        padding: 20px; 
        margin: 15px 0; 
    }}
    
    /* ACTION BUTTONS */
    .action-buttons {{ 
        display: flex; 
        gap: 10px; 
        margin-top: 20px; 
        flex-wrap: wrap; 
    }}
    
    /* TIMELINE STYLES */
    .timeline-header {{ 
        background: white; 
        border-radius: 12px; 
        padding: 20px;
        margin-bottom: 20px; 
        border: 1px solid #E2E8F0;
        display: flex; 
        align-items: center; 
        justify-content: space-between; 
    }}
    .prog-bar-bg {{ 
        width: 100%; 
        height: 8px; 
        background: #E2E8F0; 
        border-radius: 4px; 
        overflow: hidden; 
        margin-top: 8px; 
    }}
    .prog-bar-fill {{ 
        height: 100%; 
        background: linear-gradient(90deg, #0D9488, #14B8A6); 
        transition: width 1s; 
    }}
    
    /* BOTÕES PERSONALIZADOS */
    .stButton > button {{
        border-radius: 8px !important;
        font-weight: 600 !important;
        transition: all 0.2s ease !important;
    }}
    .stButton > button[kind="primary"] {{
        background: linear-gradient(135deg, #0D9488, #14B8A6) !important;
        border: none !important;
    }}
    .stButton > button[kind="primary"]:hover {{
        background: linear-gradient(135deg, #0F766E, #0D9488) !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 12px rgba(13, 148, 136, 0.2) !important;
    }}
    .stButton > button[kind="secondary"] {{
        background: white !important;
        color: #0D9488 !important;
        border: 1px solid #0D9488 !important;
    }}
    .stButton > button[kind="secondary"]:hover {{
        background: #F0FDFA !important;
        border-color: #0D9488 !important;
    }}
    
    /* RESPONSIVIDADE */
    @media (max-width: 768px) {{ 
        .mod-card-rect {{ height: auto; flex-direction: column; padding: 16px; }} 
        .mod-icon-area {{ width: 100%; height: 60px; border-right: none; border-bottom: 1px solid #F1F5F9; }} 
        .mod-content {{ padding: 16px 0 0 0; }} 
    }}
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

# ==============================================================================
# SIDEBAR
# ==============================================================================
with st.sidebar:
    try: 
        st.image("ominisfera.png", width=150)
    except: 
        st.write("🌐 OMNISFERA")
    st.markdown("---")
    if st.button("🏠 Voltar para Home", use_container_width=True): 
        st.switch_page("Home.py")
    st.markdown("---")
    
    # GESTÃO DE CHAVES
    if 'OPENAI_API_KEY' in st.secrets: 
        api_key = st.secrets['OPENAI_API_KEY']
        st.success("🔑 Chave OpenAI configurada")
    else: 
        api_key = st.text_input("Chave OpenAI:", type="password")
        if api_key:
            st.success("✅ Chave configurada")

# ==============================================================================
# CARD HERO PRINCIPAL
# ==============================================================================
hora = datetime.now().hour
saudacao = "Bom dia" if 5 <= hora < 12 else "Boa tarde" if 12 <= hora < 18 else "Boa noite"
USUARIO_NOME = st.session_state.get("usuario_nome", "Visitante").split()[0]
WORKSPACE_NAME = st.session_state.get("workspace_name", "Workspace")

st.markdown(
    f"""
    <div class="mod-card-wrapper">
        <div class="mod-card-rect">
            <div class="mod-bar c-teal"></div>
            <div class="mod-icon-area bg-teal-soft">
                <i class="ri-settings-5-fill"></i>
            </div>
            <div class="mod-content">
                <div class="mod-title">Atendimento Educacional Especializado (AEE) & Tecnologia Assistiva</div>
                <div class="mod-desc">
                    {saudacao}, <strong>{USUARIO_NOME}</strong>! Planeje e implemente estratégias de AEE para eliminação de barreiras 
                    no workspace <strong>{WORKSPACE_NAME}</strong>. Desenvolva recursos, adaptações e tecnologias assistivas 
                    para promover acessibilidade e participação plena.
                </div>
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ==============================================================================
# PARTE 2/4: CONEXÃO COM BANCO DE DADOS E CARREGAMENTO DE ALUNOS
# ==============================================================================

# ==============================================================================
# FUNÇÕES SUPABASE (REST)
# ==============================================================================
def _sb_url() -> str:
    url = str(st.secrets.get("SUPABASE_URL", "")).strip()
    if not url: 
        raise RuntimeError("SUPABASE_URL missing")
    return url.rstrip("/")

def _sb_key() -> str:
    key = str(st.secrets.get("SUPABASE_SERVICE_KEY", "") or st.secrets.get("SUPABASE_ANON_KEY", "")).strip()
    if not key: 
        raise RuntimeError("SUPABASE_KEY missing")
    return key

def _headers() -> dict:
    key = _sb_key()
    return {"apikey": key, "Authorization": f"Bearer {key}", "Content-Type": "application/json"}

# ==============================================================================
# CARREGAR ESTUDANTES DO SUPABASE
# ==============================================================================
@st.cache_data(ttl=10, show_spinner=False)
def list_students_rest():
    """Busca estudantes do Supabase incluindo o campo PEI_DATA"""
    WORKSPACE_ID = st.session_state.get("workspace_id")
    if not WORKSPACE_ID: 
        return []
    
    try:
        base = (
            f"{_sb_url()}/rest/v1/students"
            f"?select=id,name,grade,class_group,diagnosis,created_at,pei_data"
            f"&workspace_id=eq.{WORKSPACE_ID}"
            f"&order=created_at.desc"
        )
        r = requests.get(base, headers=_headers(), timeout=20)
        return r.json() if r.status_code == 200 else []
    except Exception as e:
        st.error(f"Erro ao carregar alunos: {str(e)}")
        return []

def carregar_estudantes_supabase():
    """Carrega e processa, extraindo dados ricos do PEI"""
    dados = list_students_rest()
    estudantes = []
    
    for item in dados:
        pei_completo = item.get('pei_data') or {}
        contexto_ia = pei_completo.get('ia_sugestao', '')
        
        if not contexto_ia:
            diag = item.get('diagnosis', 'Não informado')
            serie = item.get('grade', '')
            contexto_ia = f"Aluno: {item.get('name')}. Série: {serie}. Diagnóstico: {diag}."

        estudante = {
            'nome': item.get('name', ''),
            'serie': item.get('grade', ''),
            'hiperfoco': item.get('diagnosis', ''),
            'ia_sugestao': contexto_ia,
            'id': item.get('id', ''),
            'pei_data': pei_completo
        }
        if estudante['nome']:
            estudantes.append(estudante)
            
    return estudantes

# ==============================================================================
# FUNÇÕES PARA PAEE NO SUPABASE
# ==============================================================================
def carregar_pei_aluno(aluno_id):
    """Carrega o PEI do aluno do Supabase"""
    try:
        url = f"{_sb_url()}/rest/v1/students"
        params = {
            "select": "id,pei_data",
            "id": f"eq.{aluno_id}"
        }
        
        response = requests.get(url, headers=_headers(), params=params, timeout=10)
        if response.status_code == 200 and response.json():
            return response.json()[0].get('pei_data', {})
        return {}
    except Exception as e:
        st.error(f"Erro ao carregar PEI: {str(e)}")
        return {}

def salvar_paee_ciclo(aluno_id, ciclo_data):
    """Salva um ciclo de PAEE no Supabase"""
    try:
        # Primeiro, carrega os ciclos existentes
        url = f"{_sb_url()}/rest/v1/students"
        params = {"id": f"eq.{aluno_id}"}
        
        response = requests.get(url, headers=_headers(), params=params, timeout=10)
        if response.status_code == 200 and response.json():
            aluno = response.json()[0]
            ciclos_existentes = aluno.get('paee_ciclos', []) if aluno.get('paee_ciclos') else []
            
            # Verifica se é um novo ciclo ou atualização
            ciclo_id = ciclo_data.get('ciclo_id')
            if not ciclo_id:
                ciclo_id = str(uuid.uuid4())
                ciclo_data['ciclo_id'] = ciclo_id
                ciclo_data['criado_em'] = datetime.now().isoformat()
                ciclo_data['criado_por'] = st.session_state.get("user_id", "")
                ciclo_data['versao'] = 1
                ciclos_existentes.append(ciclo_data)
            else:
                # Atualiza ciclo existente
                for i, ciclo in enumerate(ciclos_existentes):
                    if ciclo.get('ciclo_id') == ciclo_id:
                        ciclos_existentes[i] = ciclo_data
                        ciclos_existentes[i]['versao'] = ciclo.get('versao', 1) + 1
                        break
            
            # Atualiza o aluno
            update_data = {
                "paee_ciclos": ciclos_existentes,
                "planejamento_ativo": ciclo_id,
                "status_planejamento": ciclo_data.get('status', 'rascunho')
            }
            
            if ciclo_data.get('config_ciclo', {}).get('data_inicio'):
                update_data["data_inicio_ciclo"] = ciclo_data['config_ciclo']['data_inicio']
            if ciclo_data.get('config_ciclo', {}).get('data_fim'):
                update_data["data_fim_ciclo"] = ciclo_data['config_ciclo']['data_fim']
            
            update_response = requests.patch(
                url, 
                headers=_headers(), 
                params=params, 
                json=update_data,
                timeout=20
            )
            
            if update_response.status_code == 204:
                return {"sucesso": True, "ciclo_id": ciclo_id}
            else:
                return {"sucesso": False, "erro": f"HTTP {update_response.status_code}: {update_response.text}"}
                
        return {"sucesso": False, "erro": "Aluno não encontrado"}
        
    except Exception as e:
        return {"sucesso": False, "erro": str(e)}

def carregar_ciclo_ativo(aluno_id):
    """Carrega o ciclo ativo do aluno"""
    try:
        url = f"{_sb_url()}/rest/v1/students"
        params = {
            "select": "id,paee_ciclos,planejamento_ativo",
            "id": f"eq.{aluno_id}"
        }
        
        response = requests.get(url, headers=_headers(), params=params, timeout=10)
        if response.status_code == 200 and response.json():
            aluno = response.json()[0]
            ciclo_id = aluno.get('planejamento_ativo')
            ciclos = aluno.get('paee_ciclos', []) if aluno.get('paee_ciclos') else []
            
            if ciclo_id and ciclos:
                for ciclo in ciclos:
                    if ciclo.get('ciclo_id') == ciclo_id:
                        return ciclo
        return None
    except Exception as e:
        st.error(f"Erro ao carregar ciclo: {str(e)}")
        return None

# ==============================================================================
# CARREGAMENTO DOS DADOS DOS ALUNOS
# ==============================================================================
if 'banco_estudantes' not in st.session_state or not st.session_state.banco_estudantes:
    with st.spinner("🔄 Lendo dados da nuvem..."):
        st.session_state.banco_estudantes = carregar_estudantes_supabase()

if not st.session_state.banco_estudantes:
    st.warning("⚠️ Nenhum aluno encontrado.")
    if st.button("📘 Ir para o módulo PEI", type="primary"): 
        st.switch_page("pages/1_PEI.py")
    st.stop()

# --- SELEÇÃO DE ALUNO ---
lista_alunos = [a['nome'] for a in st.session_state.banco_estudantes]
col_sel, col_info = st.columns([1, 2])
with col_sel:
    nome_aluno = st.selectbox("📂 Selecione o Estudante:", lista_alunos)

aluno = next((a for a in st.session_state.banco_estudantes if a.get('nome') == nome_aluno), None)

if not aluno: 
    st.error("Aluno não encontrado")
    st.stop()

# --- DETECTOR DE EDUCAÇÃO INFANTIL ---
serie_aluno = aluno.get('serie', '').lower()
is_ei = any(term in serie_aluno for term in ["infantil", "creche", "pré", "maternal", "berçario", "jardim"])

# --- HEADER DO ALUNO ---
st.markdown(f"""
    <div style="background-color: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 16px; padding: 20px 30px; margin-bottom: 20px; display: flex; justify-content: space-between; align-items: center; box-shadow: 0 2px 4px rgba(0,0,0,0.02);">
        <div><div style="font-size: 0.8rem; color: #64748B; font-weight: 800; text-transform: uppercase; letter-spacing: 1px;">Nome</div><div style="font-size: 1.2rem; color: #1E293B; font-weight: 800;">{aluno.get('nome')}</div></div>
        <div><div style="font-size: 0.8rem; color: #64748B; font-weight: 800; text-transform: uppercase; letter-spacing: 1px;">Série</div><div style="font-size: 1.2rem; color: #1E293B; font-weight: 800;">{aluno.get('serie')}</div></div>
        <div><div style="font-size: 0.8rem; color: #64748B; font-weight: 800; text-transform: uppercase; letter-spacing: 1px;">Diagnóstico</div><div style="font-size: 1.2rem; color: #1E293B; font-weight: 800;">{aluno.get('hiperfoco', '-')}</div></div>
    </div>
""", unsafe_allow_html=True)

if is_ei:
    st.info("🧸 **Modo Educação Infantil:** Foco em Campos de Experiência (BNCC).")

with st.expander("📄 Ver Dados Completos do PEI", expanded=False):
    st.write(aluno.get('ia_sugestao', 'Sem dados detalhados.'))

# ==============================================================================
# PARTE 3/4: FUNÇÕES DE IA E SISTEMA DE ESTADOS
# ==============================================================================

# ==============================================================================
# FUNÇÕES DE IA ATUALIZADAS
# ==============================================================================
def gerar_diagnostico_barreiras(api_key, aluno, obs_prof, feedback=None):
    client = OpenAI(api_key=api_key)
    contexto = aluno.get('ia_sugestao', '')
    
    prompt = f"""
    ATUAR COMO: Especialista em AEE.
    ALUNO: {aluno['nome']} | DIAGNÓSTICO: {aluno.get('hiperfoco')}
    CONTEXTO DO PEI: {contexto[:2500]}
    OBSERVAÇÃO ATUAL: {obs_prof}
    """
    
    if feedback:
        prompt += f"\nFEEDBACK PARA AJUSTE (revisão do professor): {feedback}\n"
    
    prompt += """
    CLASSIFIQUE AS BARREIRAS (LBI):
    1. **Barreiras Comunicacionais** - dificuldades na comunicação e linguagem
    2. **Barreiras Metodológicas** - métodos de ensino inadequados
    3. **Barreiras Atitudinais** - atitudes e preconceitos
    4. **Barreiras Tecnológicas** - falta de recursos tecnológicos adequados
    5. **Barreiras Arquitetônicas** - espaço físico inadequado
    
    Para cada barreira, forneça:
    - Descrição específica
    - Impacto na aprendizagem
    - Sugestões de intervenção imediata
    - Recursos necessários
    
    SAÍDA: Tabela Markdown organizada e clara.
    """
    
    try:
        resp = client.chat.completions.create(
            model="gpt-4o-mini", 
            messages=[{"role": "user", "content": prompt}], 
            temperature=0.5
        )
        return resp.choices[0].message.content
    except Exception as e: 
        return f"Erro: {str(e)}"

def gerar_projetos_ei_bncc(api_key, aluno, campo_exp, feedback=None):
    client = OpenAI(api_key=api_key)
    contexto = aluno.get('ia_sugestao', '')
    
    prompt = f"""
    ATUAR COMO: Especialista em Ed. Infantil Inclusiva.
    ALUNO: {aluno['nome']} | CONTEXTO PEI: {contexto[:2000]}
    CAMPO DE EXPERIÊNCIA: "{campo_exp}".
    """
    
    if feedback:
        prompt += f"\nFEEDBACK PARA AJUSTE (revisão do professor): {feedback}\n"
    
    prompt += """
    Crie 3 EXPERIÊNCIAS LÚDICAS (Atividades) com estrutura completa:
    
    Para cada experiência, inclua:
    1. **Título da Atividade**
    2. **Objetivos de aprendizagem** (alinhados com BNCC)
    3. **Materiais necessários** (acessíveis e de baixo custo)
    4. **Passo a passo detalhado**
    5. **Adaptações específicas** para o aluno
    6. **Avaliação formativa** (como observar o progresso)
    7. **Dicas para o professor**
    
    FOQUE em:
    - Uso de interesses do aluno como motivação
    - Eliminação de barreiras sensoriais e comunicacionais
    - Atividades sensoriais e concretas
    - Inclusão de todos os alunos da turma
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

def gerar_plano_habilidades(api_key, aluno, foco_treino, feedback=None):
    client = OpenAI(api_key=api_key)
    contexto = aluno.get('ia_sugestao', '')
    
    prompt = f"""
    CRIE PLANO DE INTERVENÇÃO AEE.
    FOCO: {foco_treino}.
    ALUNO: {aluno['nome']} | CONTEXTO PEI: {contexto[:2000]}
    """
    
    if feedback:
        prompt += f"\nFEEDBACK PARA AJUSTE (revisão do professor): {feedback}\n"
    
    prompt += """
    GERE 3 METAS SMART (Curto, Médio, Longo prazo) com estrutura completa:
    
    Para cada meta, inclua:
    1. **Meta Específica** (o que será alcançado)
    2. **Indicadores de Progresso** (como medir)
    3. **Estratégias de Ensino** (como ensinar)
    4. **Recursos e Materiais**
    5. **Frequência de Intervenção**
    6. **Responsáveis** (AEE, sala regular, família)
    7. **Critérios de Sucesso**
    
    TEMPORALIDADE:
    - CURTO PRAZO (1-2 meses): Habilidades básicas
    - MÉDIO PRAZO (3-6 meses): Consolidação
    - LONGO PRAZO (6-12 meses): Generalização
    
    Inclua também:
    - Registro de observações
    - Sistema de monitoramento
    - Estratégias de generalização para outros contextos
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

def sugerir_tecnologia_assistiva(api_key, aluno, dificuldade, feedback=None):
    client = OpenAI(api_key=api_key)
    contexto = aluno.get('ia_sugestao', '')
    
    prompt = f"""
    SUGESTÃO DE TECNOLOGIA ASSISTIVA.
    Aluno: {aluno['nome']} | Dificuldade: {dificuldade}.
    Contexto PEI: {contexto[:1500]}
    """
    
    if feedback:
        prompt += f"\nFEEDBACK PARA AJUSTE (revisão do professor): {feedback}\n"
    
    prompt += """
    Sugira recursos em 3 níveis:
    
    1. **BAIXA TECNOLOGIA (DIY - Faça Você Mesmo)**
       - Materiais simples e de baixo custo
       - Instruções passo a passo
       - Tempo de confecção
       - Custo estimado
    
    2. **MÉDIA TECNOLOGIA**
       - Recursos prontos disponíveis no mercado
       - Aplicativos gratuitos ou de baixo custo
       - Adaptações simples de materiais existentes
       - Onde encontrar/comprar
    
    3. **ALTA TECNOLOGIA**
       - Equipamentos especializados
       - Softwares específicos
       - Recursos de acessibilidade avançados
       - Processo de solicitação/viabilidade
    
    Para cada sugestão, inclua:
    - Nome do recurso
    - Finalidade específica
    - Como usar na prática
    - Benefícios para o aluno
    - Dificuldades possíveis e soluções
    - Referências para aprofundamento
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

def gerar_documento_articulacao(api_key, aluno, frequencia, acoes, feedback=None):
    client = OpenAI(api_key=api_key)
    
    prompt = f"""
    CARTA DE ARTICULAÇÃO (AEE -> SALA REGULAR).
    Aluno: {aluno['nome']}. 
    Frequência no AEE: {frequencia}.
    Ações desenvolvidas no AEE: {acoes}.
    """
    
    if feedback:
        prompt += f"\nFEEDBACK PARA AJUSTE (revisão do professor): {feedback}\n"
    
    prompt += """
    ESTRUTURA DO DOCUMENTO:
    
    1. **Cabeçalho Institucional**
       - Nome da escola
       - Data
       - Destinatário (Professor Regente)
    
    2. **Resumo das Habilidades Desenvolvidas**
       - Competências trabalhadas
       - Progressos observados
       - Dificuldades persistentes
    
    3. **Estratégias de Generalização** (para sala regular)
       - Como transferir as habilidades
       - Adaptações necessárias
       - Sinais de alerta
    
    4. **Orientações Práticas** (3 dicas principais)
       - Para atividades em grupo
       - Para avaliações
       - Para gestão comportamental
    
    5. **Plano de Ação Conjunto**
       - Responsabilidades do AEE
       - Responsabilidades da sala regular
       - Envolvimento da família
    
    6. **Próximos Passos**
       - Reuniões de alinhamento
       - Avaliações periódicas
       - Ajustes necessários
    
    7. **Contatos e Suporte**
       - Horários de atendimento
       - Canal de comunicação
       - Emergências
    
    Formato: Documento formal mas acolhedor, com linguagem clara e objetiva.
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

def gerar_cronograma_inteligente(api_key, aluno, semanas, foco, metas):
    """Gera cronograma com IA baseado nas metas do PEI"""
    try:
        client = OpenAI(api_key=api_key)
        
        # Preparar prompt com metas
        metas_texto = "\n".join([f"- {m['tipo']}: {m['descricao']}" for m in metas[:5]])
        
        prompt = f"""
        Crie um cronograma de {semanas} semanas para AEE.
        
        ALUNO: {aluno['nome']}
        DIAGNÓSTICO: {aluno.get('hiperfoco', '')}
        FOCO DO CICLO: {foco}
        
        METAS DO PEI:
        {metas_texto}
        
        Estruture em fases lógicas. Para cada semana, defina:
        1. Tema da semana
        2. Objetivo específico
        3. Atividades principais (2-3 atividades por semana)
        4. Recursos necessários
        5. Formas de avaliação
        
        Formato JSON:
        {{
            "fases": [
                {{
                    "nome": "Nome da fase",
                    "descricao": "Descrição",
                    "semanas": [1, 2, 3],
                    "objetivo_geral": "Objetivo da fase"
                }}
            ],
            "semanas": [
                {{
                    "numero": 1,
                    "tema": "Tema da semana",
                    "objetivo": "Objetivo específico",
                    "atividades": ["Atividade 1", "Atividade 2"],
                    "recursos": ["Recurso 1", "Recurso 2"],
                    "avaliacao": "Como avaliar o progresso"
                }}
            ]
        }}
        """
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        
        # Extrair e parsear JSON
        texto = response.choices[0].message.content
        
        # Extrair JSON do texto
        import re
        json_match = re.search(r'```json\n(.*?)\n```', texto, re.DOTALL)
        if json_match:
            texto = json_match.group(1)
        else:
            # Tenta encontrar qualquer JSON
            json_match = re.search(r'\{.*\}', texto, re.DOTALL)
            if json_match:
                texto = json_match.group(0)
        
        return json.loads(texto)
        
    except Exception as e:
        st.error(f"Erro na IA: {str(e)}")
        return None

# ==============================================================================
# FUNÇÕES AUXILIARES PARA PAEE
# ==============================================================================
def extrair_metas_do_pei(pei_data):
    """Extrai metas estruturadas do PEI"""
    if not pei_data:
        return []
    
    metas = []
    
    # Tenta diferentes formatos de PEI
    if isinstance(pei_data, dict):
        # Formato JSON estruturado
        if 'metas' in pei_data and isinstance(pei_data['metas'], list):
            return pei_data['metas']
        
        # Formato texto da IA
        if 'ia_sugestao' in pei_data:
            texto = pei_data['ia_sugestao']
        else:
            texto = str(pei_data)
    else:
        texto = str(pei_data)
    
    # Parse de texto
    linhas = texto.split('\n')
    for linha in linhas:
        linha = linha.strip()
        # Procura por padrões de metas
        if any(marker in linha.lower() for marker in ['meta:', 'objetivo:', 'habilidade:', '- ', '* ']):
            # Remove marcadores
            for marker in ['Meta:', 'meta:', 'Objetivo:', 'objetivo:', 'Habilidade:', 'habilidade:', '- ', '* ']:
                if linha.startswith(marker):
                    linha = linha[len(marker):].strip()
                    break
            
            if linha and len(linha) > 5:  # Evita linhas muito curtas
                # Tenta identificar tipo
                tipo = "GERAL"
                if 'social' in linha.lower():
                    tipo = "HABILIDADES SOCIAIS"
                elif 'comunicação' in linha.lower() or 'comunicacao' in linha.lower():
                    tipo = "COMUNICAÇÃO"
                elif 'leitura' in linha.lower() or 'escrita' in linha.lower() or 'matemática' in linha.lower():
                    tipo = "ACADÊMICO"
                elif 'motor' in linha.lower():
                    tipo = "MOTOR"
                elif 'autonomia' in linha.lower():
                    tipo = "AUTONOMIA"
                
                metas.append({
                    'id': f"meta_{len(metas)+1:03d}",
                    'tipo': tipo,
                    'descricao': linha[:200],
                    'prioridade': 'media',
                    'selecionada': True
                })
    
    # Se não encontrou metas, cria uma genérica
    if not metas:
        metas.append({
            'id': 'meta_001',
            'tipo': 'DESENVOLVIMENTO',
            'descricao': 'Desenvolver habilidades específicas conforme necessidades identificadas no PEI',
            'prioridade': 'alta',
            'selecionada': True
        })
    
    return metas[:10]  # Limita a 10 metas

def criar_cronograma_basico(semanas, metas):
    """Cria um cronograma básico sem IA"""
    cronograma = {
        "fases": [
            {
                "nome": "Fase 1: Avaliação e Adaptação",
                "descricao": "Período inicial de avaliação e adaptação das estratégias",
                "semanas": list(range(1, min(4, semanas) + 1)),
                "objetivo_geral": "Estabelecer rotina e avaliar necessidades imediatas"
            }
        ],
        "semanas": []
    }
    
    # Adiciona fases adicionais se houver mais semanas
    if semanas > 4:
        cronograma["fases"].append({
            "nome": "Fase 2: Desenvolvimento",
            "descricao": "Desenvolvimento intensivo das habilidades alvo",
            "semanas": list(range(5, min(9, semanas) + 1)),
            "objetivo_geral": "Desenvolver habilidades específicas"
        })
    
    if semanas > 8:
        cronograma["fases"].append({
            "nome": "Fase 3: Consolidação",
            "descricao": "Consolidação e generalização das habilidades",
            "semanas": list(range(9, semanas + 1)),
            "objetivo_geral": "Generalizar habilidades para outros contextos"
        })
    
    # Cria semanas básicas
    for semana in range(1, semanas + 1):
        cronograma["semanas"].append({
            "numero": semana,
            "tema": f"Semana {semana}: Desenvolvimento de habilidades",
            "objetivo": "Avançar nas metas estabelecidas",
            "atividades": ["Atividades personalizadas conforme plano"],
            "recursos": ["Materiais adaptados", "Recursos visuais"],
            "avaliacao": "Observação direta e registros"
        })
    
    return cronograma

# ==============================================================================
# SISTEMA DE GESTÃO DE RECURSOS (ESTADOS)
# ==============================================================================
def inicializar_estados():
    """Inicializa os estados para todos os recursos"""
    recursos = [
        'diagnostico_barreiras',
        'projetos_ei',
        'plano_habilidades',
        'tecnologia_assistiva',
        'documento_articulacao'
    ]
    
    for recurso in recursos:
        if f'status_{recurso}' not in st.session_state:
            st.session_state[f'status_{recurso}'] = 'rascunho'
        if f'conteudo_{recurso}' not in st.session_state:
            st.session_state[f'conteudo_{recurso}'] = ''
        if f'feedback_{recurso}' not in st.session_state:
            st.session_state[f'feedback_{recurso}'] = ''
        if f'input_original_{recurso}' not in st.session_state:
            st.session_state[f'input_original_{recurso}'] = {}

inicializar_estados()

# ==============================================================================
# PARTE 4/4: INTERFACE PRINCIPAL E COMPONENTES
# ==============================================================================

# ==============================================================================
# COMPONENTE DE VALIDAÇÃO/AJUSTE (HUB DE RECURSOS)
# ==============================================================================
def renderizar_hub_recurso(tipo_recurso, conteudo_gerado, aluno_nome, dados_entrada=None):
    """Renderiza o hub de recursos com validação, ajuste e download"""
    
    # Estados do recurso
    status = st.session_state.get(f'status_{tipo_recurso}', 'rascunho')
    
    # Container principal
    with st.container():
        st.markdown(f"<div class='resource-box'>", unsafe_allow_html=True)
        
        # TÍTULO DO RECURSO
        titulos = {
            'diagnostico_barreiras': '📋 Diagnóstico de Barreiras',
            'projetos_ei': '🎨 Banco de Experiências (BNCC)',
            'plano_habilidades': '📈 Plano de Habilidades',
            'tecnologia_assistiva': '🛠️ Tecnologia Assistiva',
            'documento_articulacao': '📄 Documento de Articulação'
        }
        
        st.subheader(titulos.get(tipo_recurso, 'Recurso Gerado'))
        
        # 1. MODO REVISÃO (após geração inicial)
        if status == 'revisao':
            # Mostra o conteúdo gerado
            st.markdown("### 📝 Conteúdo Gerado")
            st.markdown(conteudo_gerado)
            
            st.markdown("---")
            st.markdown("### 🔧 Ações Disponíveis")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("✅ **Validar e Finalizar**", key=f"validar_{tipo_recurso}", 
                           use_container_width=True, type="primary"):
                    st.session_state[f'status_{tipo_recurso}'] = 'aprovado'
                    st.success("Recurso validado com sucesso!")
                    time.sleep(1)
                    st.rerun()
            
            with col2:
                if st.button("🔄 **Solicitar Ajustes**", key=f"ajustar_{tipo_recurso}",
                           use_container_width=True):
                    st.session_state[f'status_{tipo_recurso}'] = 'ajustando'
                    st.rerun()
            
            with col3:
                if st.button("🗑️ **Descartar e Regenerar**", key=f"descartar_{tipo_recurso}",
                           use_container_width=True):
                    st.session_state[f'status_{tipo_recurso}'] = 'rascunho'
                    st.session_state[f'conteudo_{tipo_recurso}'] = ''
                    st.info("Recurso descartado. Você pode gerar novamente.")
                    st.rerun()
        
        # 2. MODO AJUSTANDO (professor solicitou ajustes)
        elif status == 'ajustando':
            st.warning("✏️ **Modo de Ajuste Ativo**")
            
            # Campo para feedback detalhado
            feedback = st.text_area(
                "**Descreva os ajustes necessários:**",
                placeholder="Exemplo: 'Preciso de mais exemplos práticos...'\n'Inclua atividades para trabalho em grupo...'\n'Foque mais na comunicação alternativa...'",
                height=150,
                key=f"feedback_input_{tipo_recurso}"
            )
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("🔄 **Regerar com Ajustes**", 
                           key=f"regerar_{tipo_recurso}",
                           use_container_width=True, type="primary"):
                    if feedback:
                        st.session_state[f'feedback_{tipo_recurso}'] = feedback
                        st.info("Regerando com os ajustes solicitados...")
                        st.session_state[f'status_{tipo_recurso}'] = 'regerando'
                        st.rerun()
                    else:
                        st.error("Por favor, descreva os ajustes desejados.")
            
            with col2:
                if st.button("↩️ **Cancelar Ajustes**", 
                           key=f"cancelar_{tipo_recurso}",
                           use_container_width=True):
                    st.session_state[f'status_{tipo_recurso}'] = 'revisao'
                    st.rerun()
        
        # 3. MODO APROVADO (recurso validado)
        elif status == 'aprovado':
            st.success("✅ **Recurso Validado e Pronto para Uso**")
            
            # Mostra o conteúdo final
            st.markdown("### 📋 Conteúdo Final")
            st.markdown(conteudo_gerado)
            
            st.markdown("---")
            st.markdown("### 💾 Opções de Download")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Download TXT
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                nome_arquivo = f"{tipo_recurso}_{aluno_nome}_{timestamp}.txt"
                st.download_button(
                    label="📥 **Baixar TXT**",
                    data=conteudo_gerado,
                    file_name=nome_arquivo,
                    mime="text/plain",
                    use_container_width=True
                )
            
            with col2:
                if st.button("✏️ **Editar Novamente**", 
                           key=f"reeditar_{tipo_recurso}",
                           use_container_width=True):
                    st.session_state[f'status_{tipo_recurso}'] = 'revisao'
                    st.rerun()
        
        # 4. MODO REGERANDO (processando ajustes)
        elif status == 'regerando':
            st.info("🔄 **Processando ajustes solicitados...**")
            # Este estado é transitório, será tratado na função principal
        
        st.markdown("</div>", unsafe_allow_html=True)

# ==============================================================================
# CRIAR AS ABAS PRINCIPAIS
# ==============================================================================

# Criar abas diferentes para EI e não-EI
if is_ei:
    tab_barreiras, tab_projetos, tab_rotina, tab_ponte, tab_planejamento = st.tabs([
        "BARREIRAS NO BRINCAR", "BANCO DE EXPERIÊNCIAS", "ROTINA & ADAPTAÇÃO", 
        "ARTICULAÇÃO", "PLANEJAMENTO DO CICLO"
    ])
else:
    tab_barreiras, tab_plano, tab_tec, tab_ponte, tab_planejamento = st.tabs([
        "MAPEAR BARREIRAS", "PLANO DE HABILIDADES", "TEC. ASSISTIVA", 
        "ARTICULAÇÃO", "PLANEJAMENTO DO CICLO"
    ])

# ==============================================================================
# ABA 1: BARREIRAS NO BRINCAR (EI) / MAPEAR BARREIRAS (NÃO EI)
# ==============================================================================
if is_ei:
    with tab_barreiras:
        st.markdown("<div class='pedagogia-box'><strong>Diagnóstico do Brincar:</strong> Identifique barreiras na interação e no brincar.</div>", unsafe_allow_html=True)
        
        status_atual = st.session_state.get('status_diagnostico_barreiras', 'rascunho')
        
        if status_atual == 'rascunho':
            # Modo inicial - coleta de dados
            obs_aee = st.text_area(
                "Observação do Brincar:", 
                height=100,
                placeholder="Descreva as observações sobre o brincar do aluno: interações, preferências, dificuldades..."
            )
            
            if st.button("🔍 Mapear Barreiras", type="primary", use_container_width=True):
                if not api_key:
                    st.error("Insira a chave OpenAI na sidebar.")
                elif not obs_aee:
                    st.warning("Por favor, descreva suas observações antes de mapear.")
                else:
                    with st.spinner("Analisando barreiras no brincar..."):
                        resultado = gerar_diagnostico_barreiras(api_key, aluno, obs_aee)
                        if "Erro:" in resultado:
                            st.error(resultado)
                        else:
                            st.session_state.conteudo_diagnostico_barreiras = resultado
                            st.session_state.status_diagnostico_barreiras = 'revisao'
                            st.session_state.input_original_diagnostico_barreiras = {'obs': obs_aee}
                            st.success("Diagnóstico gerado com sucesso!")
                            st.rerun()
        
        else:
            # Modo hub de recursos - já tem conteúdo gerado
            renderizar_hub_recurso(
                tipo_recurso='diagnostico_barreiras',
                conteudo_gerado=st.session_state.conteudo_diagnostico_barreiras,
                aluno_nome=aluno['nome']
            )
            
            # Tratamento especial para regeração com feedback
            if st.session_state.status_diagnostico_barreiras == 'regerando':
                feedback = st.session_state.get('feedback_diagnostico_barreiras', '')
                input_original = st.session_state.get('input_original_diagnostico_barreiras', {})
                obs_original = input_original.get('obs', '')
                
                with st.spinner("Aplicando ajustes solicitados..."):
                    resultado = gerar_diagnostico_barreiras(
                        api_key, aluno, obs_original, feedback
                    )
                    st.session_state.conteudo_diagnostico_barreiras = resultado
                    st.session_state.status_diagnostico_barreiras = 'revisao'
                    st.rerun()
else:
    with tab_barreiras:
        st.markdown("<div class='pedagogia-box'><strong>Diagnóstico de Acessibilidade:</strong> O que impede a participação plena do aluno?</div>", unsafe_allow_html=True)
        
        status_atual = st.session_state.get('status_diagnostico_barreiras', 'rascunho')
        
        if status_atual == 'rascunho':
            obs_aee = st.text_area(
                "Observações Iniciais do AEE:", 
                height=100,
                placeholder="Descreva suas observações sobre as barreiras encontradas..."
            )
            
            if st.button("🔍 Analisar Barreiras", type="primary", use_container_width=True):
                if not api_key:
                    st.error("Insira a chave OpenAI na sidebar.")
                elif not obs_aee:
                    st.warning("Por favor, descreva suas observações antes de analisar.")
                else:
                    with st.spinner("Analisando barreiras de acessibilidade..."):
                        resultado = gerar_diagnostico_barreiras(api_key, aluno, obs_aee)
                        if "Erro:" in resultado:
                            st.error(resultado)
                        else:
                            st.session_state.conteudo_diagnostico_barreiras = resultado
                            st.session_state.status_diagnostico_barreiras = 'revisao'
                            st.session_state.input_original_diagnostico_barreiras = {'obs': obs_aee}
                            st.success("Análise de barreiras concluída!")
                            st.rerun()
        
        else:
            renderizar_hub_recurso(
                tipo_recurso='diagnostico_barreiras',
                conteudo_gerado=st.session_state.conteudo_diagnostico_barreiras,
                aluno_nome=aluno['nome']
            )
            
            if st.session_state.status_diagnostico_barreiras == 'regerando':
                feedback = st.session_state.get('feedback_diagnostico_barreiras', '')
                input_original = st.session_state.get('input_original_diagnostico_barreiras', {})
                obs_original = input_original.get('obs', '')
                
                with st.spinner("Aplicando ajustes..."):
                    resultado = gerar_diagnostico_barreiras(
                        api_key, aluno, obs_original, feedback
                    )
                    st.session_state.conteudo_diagnostico_barreiras = resultado
                    st.session_state.status_diagnostico_barreiras = 'revisao'
                    st.rerun()

# ==============================================================================
# ABA 2: BANCO DE EXPERIÊNCIAS (EI) / PLANO DE HABILIDADES (NÃO EI)
# ==============================================================================
if is_ei:
    with tab_projetos:
        st.markdown("<div class='pedagogia-box'><strong>Banco de Experiências (BNCC):</strong> Atividades lúdicas alinhadas aos Campos de Experiência.</div>", unsafe_allow_html=True)
        
        status_atual = st.session_state.get('status_projetos_ei', 'rascunho')
        
        if status_atual == 'rascunho':
            campo_bncc = st.selectbox(
                "Selecione o Campo de Experiência:",
                ["O eu, o outro e o nós", "Corpo, gestos e movimentos", 
                 "Traços, sons, cores e formas", "Escuta, fala, pensamento e imaginação", 
                 "Espaços, tempos, quantidades, relações e transformações"],
                key="campo_bncc_ei"
            )
            
            if st.button("✨ Gerar Atividades", type="primary", use_container_width=True):
                if not api_key:
                    st.error("Insira a chave OpenAI na sidebar.")
                else:
                    with st.spinner("Criando banco de experiências..."):
                        resultado = gerar_projetos_ei_bncc(api_key, aluno, campo_bncc)
                        if "Erro:" in resultado:
                            st.error(resultado)
                        else:
                            st.session_state.conteudo_projetos_ei = resultado
                            st.session_state.status_projetos_ei = 'revisao'
                            st.session_state.input_original_projetos_ei = {'campo': campo_bncc}
                            st.success("Banco de experiências gerado!")
                            st.rerun()
        
        else:
            renderizar_hub_recurso(
                tipo_recurso='projetos_ei',
                conteudo_gerado=st.session_state.conteudo_projetos_ei,
                aluno_nome=aluno['nome']
            )
            
            if st.session_state.status_projetos_ei == 'regerando':
                feedback = st.session_state.get('feedback_projetos_ei', '')
                input_original = st.session_state.get('input_original_projetos_ei', {})
                campo_original = input_original.get('campo', 'O eu, o outro e o nós')
                
                with st.spinner("Aplicando ajustes..."):
                    resultado = gerar_projetos_ei_bncc(
                        api_key, aluno, campo_original, feedback
                    )
                    st.session_state.conteudo_projetos_ei = resultado
                    st.session_state.status_projetos_ei = 'revisao'
                    st.rerun()
else:
    with tab_plano:
        st.markdown("<div class='pedagogia-box'><strong>Treino de Habilidades:</strong> Desenvolvimento de competências específicas no AEE.</div>", unsafe_allow_html=True)
        
        status_atual = st.session_state.get('status_plano_habilidades', 'rascunho')
        
        if status_atual == 'rascunho':
            foco = st.selectbox(
                "Foco do Atendimento:",
                ["Funções Executivas", "Autonomia", "Coordenação Motora", 
                 "Comunicação", "Habilidades Sociais", "Leitura e Escrita",
                 "Matemática", "Tecnologias Assistivas", "Organização e Planejamento"],
                key="foco_plano_naoei"
            )
            
            if st.button("📋 Gerar Plano", type="primary", use_container_width=True):
                if not api_key:
                    st.error("Insira a chave OpenAI na sidebar.")
                else:
                    with st.spinner("Elaborando plano de intervenção..."):
                        resultado = gerar_plano_habilidades(api_key, aluno, foco)
                        if "Erro:" in resultado:
                            st.error(resultado)
                        else:
                            st.session_state.conteudo_plano_habilidades = resultado
                            st.session_state.status_plano_habilidades = 'revisao'
                            st.session_state.input_original_plano_habilidades = {'foco': foco}
                            st.success("Plano de habilidades gerado!")
                            st.rerun()
        
        else:
            renderizar_hub_recurso(
                tipo_recurso='plano_habilidades',
                conteudo_gerado=st.session_state.conteudo_plano_habilidades,
                aluno_nome=aluno['nome']
            )
            
            if st.session_state.status_plano_habilidades == 'regerando':
                feedback = st.session_state.get('feedback_plano_habilidades', '')
                input_original = st.session_state.get('input_original_plano_habilidades', {})
                foco_original = input_original.get('foco', 'Funções Executivas')
                
                with st.spinner("Aplicando ajustes..."):
                    resultado = gerar_plano_habilidades(
                        api_key, aluno, foco_original, feedback
                    )
                    st.session_state.conteudo_plano_habilidades = resultado
                    st.session_state.status_plano_habilidades = 'revisao'
                    st.rerun()

# ==============================================================================
# ABA 3: ROTINA & ADAPTAÇÃO (EI) / TEC. ASSISTIVA (NÃO EI)
# ==============================================================================
if is_ei:
    with tab_rotina:
        st.markdown("<div class='pedagogia-box'><strong>Adaptação de Rotina:</strong> Recursos visuais e sensoriais para rotina da Educação Infantil.</div>", unsafe_allow_html=True)
        
        status_atual = st.session_state.get('status_tecnologia_assistiva', 'rascunho')
        
        if status_atual == 'rascunho':
            dif_rotina = st.text_input(
                "Dificuldade Específica na Rotina:",
                placeholder="Ex: Transições entre atividades, organização do material, comunicação de necessidades...",
                key="dif_rotina_ei"
            )
            
            if st.button("🛠️ Sugerir Adaptação", type="primary", use_container_width=True):
                if not api_key:
                    st.error("Insira a chave OpenAI na sidebar.")
                elif not dif_rotina:
                    st.warning("Por favor, descreva a dificuldade específica.")
                else:
                    with st.spinner("Buscando recursos de adaptação..."):
                        resultado = sugerir_tecnologia_assistiva(
                            api_key, aluno, f"Rotina EI: {dif_rotina}"
                        )
                        if "Erro:" in resultado:
                            st.error(resultado)
                        else:
                            st.session_state.conteudo_tecnologia_assistiva = resultado
                            st.session_state.status_tecnologia_assistiva = 'revisao'
                            st.session_state.input_original_tecnologia_assistiva = {'dificuldade': dif_rotina}
                            st.success("Sugestões de adaptação geradas!")
                            st.rerun()
        
        else:
            renderizar_hub_recurso(
                tipo_recurso='tecnologia_assistiva',
                conteudo_gerado=st.session_state.conteudo_tecnologia_assistiva,
                aluno_nome=aluno['nome']
            )
            
            if st.session_state.status_tecnologia_assistiva == 'regerando':
                feedback = st.session_state.get('feedback_tecnologia_assistiva', '')
                input_original = st.session_state.get('input_original_tecnologia_assistiva', {})
                dif_original = input_original.get('dificuldade', '')
                
                with st.spinner("Aplicando ajustes..."):
                    resultado = sugerir_tecnologia_assistiva(
                        api_key, aluno, f"Rotina EI: {dif_original}", feedback
                    )
                    st.session_state.conteudo_tecnologia_assistiva = resultado
                    st.session_state.status_tecnologia_assistiva = 'revisao'
                    st.rerun()
else:
    with tab_tec:
        st.markdown("<div class='pedagogia-box'><strong>Tecnologia Assistiva:</strong> Recursos para promover autonomia e participação.</div>", unsafe_allow_html=True)
        
        status_atual = st.session_state.get('status_tecnologia_assistiva', 'rascunho')
        
        if status_atual == 'rascunho':
            dif_especifica = st.text_input(
                "Dificuldade Específica:",
                placeholder="Ex: Dificuldade na escrita, comunicação, mobilidade, organização...",
                key="dif_especifica_naoei"
            )
            
            if st.button("🔧 Sugerir Recursos", type="primary", use_container_width=True):
                if not api_key:
                    st.error("Insira a chave OpenAI na sidebar.")
                elif not dif_especifica:
                    st.warning("Por favor, descreva a dificuldade específica.")
                else:
                    with st.spinner("Buscando tecnologias assistivas..."):
                        resultado = sugerir_tecnologia_assistiva(api_key, aluno, dif_especifica)
                        if "Erro:" in resultado:
                            st.error(resultado)
                        else:
                            st.session_state.conteudo_tecnologia_assistiva = resultado
                            st.session_state.status_tecnologia_assistiva = 'revisao'
                            st.session_state.input_original_tecnologia_assistiva = {'dificuldade': dif_especifica}
                            st.success("Sugestões de TA geradas!")
                            st.rerun()
        
        else:
            renderizar_hub_recurso(
                tipo_recurso='tecnologia_assistiva',
                conteudo_gerado=st.session_state.conteudo_tecnologia_assistiva,
                aluno_nome=aluno['nome']
            )
            
            if st.session_state.status_tecnologia_assistiva == 'regerando':
                feedback = st.session_state.get('feedback_tecnologia_assistiva', '')
                input_original = st.session_state.get('input_original_tecnologia_assistiva', {})
                dif_original = input_original.get('dificuldade', '')
                
                with st.spinner("Aplicando ajustes..."):
                    resultado = sugerir_tecnologia_assistiva(
                        api_key, aluno, dif_original, feedback
                    )
                    st.session_state.conteudo_tecnologia_assistiva = resultado
                    st.session_state.status_tecnologia_assistiva = 'revisao'
                    st.rerun()

# ==============================================================================
# ABA 4: ARTICULAÇÃO (para EI e não EI)
# ==============================================================================
with tab_ponte:
    st.markdown("<div class='pedagogia-box'><strong>Ponte com a Sala Regular:</strong> Documento colaborativo para articulação entre AEE e sala de aula.</div>", unsafe_allow_html=True)
    
    status_atual = st.session_state.get('status_documento_articulacao', 'rascunho')
    
    if status_atual == 'rascunho':
        c1, c2 = st.columns(2)
        with c1:
            freq = st.selectbox(
                "Frequência no AEE:",
                ["1x/sem", "2x/sem", "3x/sem", "Diário"],
                key='freq_articulacao'
            )
        with c2:
            turno = st.selectbox(
                "Turno:",
                ["Manhã", "Tarde", "Integral"],
                key='turno_articulacao'
            )
        
        acoes_resumo = st.text_area(
            "Trabalho Desenvolvido no AEE:",
            height=100,
            placeholder="Descreva as principais ações, estratégias e recursos utilizados no AEE...",
            key='acoes_articulacao'
        )
        
        if st.button("📄 Gerar Documento", type="primary", use_container_width=True):
            if not api_key:
                st.error("Insira a chave OpenAI na sidebar.")
            elif not acoes_resumo:
                st.warning("Por favor, descreva o trabalho desenvolvido no AEE.")
            else:
                with st.spinner("Gerando documento de articulação..."):
                    resultado = gerar_documento_articulacao(
                        api_key, aluno, f"{freq} ({turno})", acoes_resumo
                    )
                    if "Erro:" in resultado:
                        st.error(resultado)
                    else:
                        st.session_state.conteudo_documento_articulacao = resultado
                        st.session_state.status_documento_articulacao = 'revisao'
                        st.session_state.input_original_documento_articulacao = {
                            'freq': freq,
                            'turno': turno,
                            'acoes': acoes_resumo
                        }
                        st.success("Documento de articulação gerado!")
                        st.rerun()
    
    else:
        renderizar_hub_recurso(
            tipo_recurso='documento_articulacao',
            conteudo_gerado=st.session_state.conteudo_documento_articulacao,
            aluno_nome=aluno['nome']
        )
        
        if st.session_state.status_documento_articulacao == 'regerando':
            feedback = st.session_state.get('feedback_documento_articulacao', '')
            input_original = st.session_state.get('input_original_documento_articulacao', {})
            freq_original = input_original.get('freq', '1x/sem')
            turno_original = input_original.get('turno', 'Manhã')
            acoes_original = input_original.get('acoes', '')
            
            with st.spinner("Aplicando ajustes..."):
                resultado = gerar_documento_articulacao(
                    api_key, aluno, 
                    f"{freq_original} ({turno_original})", 
                    acoes_original, 
                    feedback
                )
                st.session_state.conteudo_documento_articulacao = resultado
                st.session_state.status_documento_articulacao = 'revisao'
                st.rerun()

# ==============================================================================
# ABA 5: PLANEJAMENTO DO CICLO (CULMINAÇÃO)
# ==============================================================================
with tab_planejamento:
    col_titulo1, col_titulo2, col_titulo3 = st.columns([1, 2, 1])
    with col_titulo2:
        st.markdown("""
        <div style='text-align: center; margin-bottom: 25px;'>
            <h2 style='color: #1E293B; font-weight: 700; margin-bottom: 8px;'>📋 Planejamento do Ciclo AEE</h2>
            <p style='color: #64748B; font-size: 0.95rem;'>Culminação do PEI - Implementação prática das estratégias</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Adicionar uma linha divisória sutil
    st.markdown('<div style="border-top: 1px solid #E2E8F0; margin-bottom: 25px;"></div>', unsafe_allow_html=True)
    
    # Carregar PEI do aluno
    pei_data = carregar_pei_aluno(aluno['id'])
    
    # Seção 1: VISÃO GERAL DO PEI
    with st.expander("📋 Visão geral do PEI", expanded=True):
        col_visao1, col_visao2, col_visao3 = st.columns(3)
        
        with col_visao1:
            st.metric("Aluno", aluno['nome'])
            st.metric("Série/Turma", aluno.get('serie', 'Não informada'))
        
        with col_visao2:
            if aluno.get('hiperfoco'):
                st.metric("Diagnóstico", aluno['hiperfoco'][:20] + "..." if len(aluno['hiperfoco']) > 20 else aluno['hiperfoco'])
            
            # Data de revisão do PEI
            if pei_data and 'data_revisao' in pei_data:
                try:
                    data_revisao = datetime.fromisoformat(pei_data['data_revisao'].replace('Z', '+00:00')).date()
                    dias_para_revisao = (data_revisao - date.today()).days
                    st.metric("Revisão do PEI", f"{dias_para_revisao} dias")
                except:
                    pass
        
        with col_visao3:
            # Status do planejamento
            ciclo_ativo = carregar_ciclo_ativo(aluno['id'])
            if ciclo_ativo:
                status = ciclo_ativo.get('status', 'rascunho')
                status_color = {
                    'rascunho': '🟡',
                    'ativo': '🟢',
                    'concluido': '🔵',
                    'arquivado': '⚫'
                }.get(status, '⚪')
                st.metric("Status Ciclo", f"{status_color} {status.title()}")
            else:
                st.metric("Status Ciclo", "🆕 Não iniciado")
    
    # Seção 2: METAS DO PEI PARA O CICLO
    st.markdown("### 🎯 Metas do PEI selecionadas")
    
    # Extrair metas do PEI
    metas_pei = extrair_metas_do_pei(pei_data)
    
    if metas_pei:
        # Mostrar metas em cards selecionáveis
        cols_metas = st.columns(2)
        metas_selecionadas = []
        
        for idx, meta in enumerate(metas_pei):
            with cols_metas[idx % 2]:
                # Card de meta
                cor_tipo = {
                    'HABILIDADES SOCIAIS': '#3B82F6',
                    'COMUNICAÇÃO': '#10B981',
                    'ACADÊMICO': '#8B5CF6',
                    'MOTOR': '#F59E0B',
                    'AUTONOMIA': '#EF4444',
                    'GERAL': '#64748B',
                    'DESENVOLVIMENTO': '#0D9488'
                }.get(meta['tipo'], '#64748B')
                
                selecionada = st.checkbox(
                    f"**{meta['tipo']}**",
                    value=meta.get('selecionada', True),
                    key=f"meta_{meta['id']}",
                    help=meta['descricao']
                )
                
                if selecionada:
                    metas_selecionadas.append({
                        'id': meta['id'],
                        'tipo': meta['tipo'],
                        'descricao': meta['descricao'],
                        'prioridade': meta.get('prioridade', 'media')
                    })
                
                st.markdown(f"""
                <div style='border-left: 4px solid {cor_tipo}; padding-left: 10px; margin: 5px 0;'>
                    <div style='font-size: 0.9rem; color: #4B5563;'>
                        {meta['descricao']}
                    </div>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.warning("Nenhuma meta encontrada no PEI. Gere o PEI primeiro.")
        metas_selecionadas = []
    
    # Seção 3: RECURSOS GERADOS (das abas anteriores)
    st.markdown("### 🧩 Recursos incorporados")
    
    # Coletar recursos das outras abas (do session_state)
    recursos_disponiveis = {
        'diagnostico_barreiras': st.session_state.get('conteudo_diagnostico_barreiras', ''),
        'plano_habilidades': st.session_state.get('conteudo_plano_habilidades', ''),
        'tecnologia_assistiva': st.session_state.get('conteudo_tecnologia_assistiva', ''),
        'documento_articulacao': st.session_state.get('conteudo_documento_articulacao', '')
    }
    
    # Filtra recursos com conteúdo
    recursos_com_conteudo = {k: v for k, v in recursos_disponiveis.items() if v and len(str(v)) > 100}
    
    if recursos_com_conteudo:
        recursos_selecionados = {}
        
        col_rec1, col_rec2 = st.columns(2)
        recursos_nomes = {
            'diagnostico_barreiras': '🔍 Diagnóstico de Barreiras',
            'plano_habilidades': '📈 Plano de Habilidades',
            'tecnologia_assistiva': '💻 Tecnologia Assistiva',
            'documento_articulacao': '🤝 Documento de Articulação'
        }
        
        for idx, (recurso_id, conteudo) in enumerate(recursos_com_conteudo.items()):
            with col_rec1 if idx % 2 == 0 else col_rec2:
                # Checkbox para selecionar recurso
                selecionado = st.checkbox(
                    recursos_nomes.get(recurso_id, recurso_id),
                    value=True,
                    key=f"recurso_{recurso_id}"
                )
                
                if selecionado:
                    # Resumo do conteúdo
                    resumo = str(conteudo)[:300] + ("..." if len(str(conteudo)) > 300 else "")
                    recursos_selecionados[recurso_id] = {
                        'resumo': resumo,
                        'completo': conteudo,
                        'data_incorporacao': datetime.now().isoformat()
                    }
                    
                    # Mostrar preview
                    with st.expander("📄 Ver resumo", expanded=False):
                        st.text_area("", resumo, height=100, disabled=True)
    else:
        st.info("ℹ️ Gere recursos nas abas anteriores para incorporar ao ciclo.")
        recursos_selecionados = {}
    
    # Seção 4: CONFIGURAÇÃO DO CICLO
    st.markdown("### ⚙️ Configuração do ciclo")
    
    with st.form("config_ciclo_form"):
        col_config1, col_config2 = st.columns(2)
        
        with col_config1:
            duracao = st.slider(
                "Duração do ciclo (semanas):",
                min_value=4,
                max_value=24,
                value=12,
                help="Quantas semanas de execução do plano"
            )
            
            frequencia = st.selectbox(
                "Frequência do AEE:",
                options=[
                    ("1x_semana", "1 vez por semana"),
                    ("2x_semana", "2 vezes por semana"),
                    ("3x_semana", "3 vezes por semana"),
                    ("diario", "Atendimento diário")
                ],
                format_func=lambda x: x[1],
                index=1
            )
        
        with col_config2:
            data_inicio = st.date_input(
                "Data de início:",
                value=date.today(),
                min_value=date.today()
            )
            
            data_fim = st.date_input(
                "Previsão de término:",
                value=data_inicio + timedelta(weeks=duracao),
                min_value=data_inicio
            )
        
        foco_principal = st.text_input(
            "Foco principal do ciclo:",
            value=aluno.get('hiperfoco', 'Desenvolvimento de habilidades específicas'),
            help="Objetivo principal deste ciclo de intervenção"
        )
        
        descricao_ciclo = st.text_area(
            "Descrição detalhada do ciclo:",
            height=100,
            placeholder="Descreva os principais objetivos, abordagens e expectativas para este ciclo...",
            help="Esta descrição será usada para comunicação com a equipe e família"
        )
        
        # Botão para gerar cronograma com IA
        col_gen1, col_gen2 = st.columns(2)
        with col_gen1:
            usar_ia = st.checkbox("🤖 Usar IA para sugestão de cronograma", value=True)
        
        with col_gen2:
            if st.form_submit_button("✨ Gerar planejamento", type="primary", use_container_width=True):
                if not metas_selecionadas:
                    st.error("Selecione pelo menos uma meta do PEI para o ciclo.")
                else:
                    # Criar estrutura do ciclo
                    ciclo_data = {
                        'ciclo_id': None,  # Será gerado no salvamento
                        'status': 'rascunho',
                        'config_ciclo': {
                            'duracao_semanas': duracao,
                            'frequencia': frequencia[0],
                            'foco_principal': foco_principal,
                            'descricao': descricao_ciclo,
                            'data_inicio': data_inicio.isoformat(),
                            'data_fim': data_fim.isoformat(),
                            'metas_selecionadas': metas_selecionadas
                        },
                        'recursos_incorporados': recursos_selecionados,
                        'criado_por': st.session_state.get("user_id", ""),
                        'versao': 1
                    }
                    
                    # Se usar IA, gerar sugestão de cronograma
                    if usar_ia and api_key:
                        with st.spinner("🤖 IA planejando cronograma..."):
                            cronograma_ia = gerar_cronograma_inteligente(
                                api_key, aluno, duracao, foco_principal, metas_selecionadas
                            )
                            if cronograma_ia:
                                ciclo_data['cronograma'] = cronograma_ia
                            else:
                                # Cronograma básico se IA falhar
                                ciclo_data['cronograma'] = criar_cronograma_basico(duracao, metas_selecionadas)
                    else:
                        # Cronograma básico sem IA
                        ciclo_data['cronograma'] = criar_cronograma_basico(duracao, metas_selecionadas)
                    
                    # Salvar no session_state para preview
                    st.session_state.ciclo_preview = ciclo_data
                    st.success("Planejamento gerado! Revise abaixo e salve.")
    
    # Seção 5: PREVIEW E SALVAMENTO
    if 'ciclo_preview' in st.session_state:
        st.markdown("### 📋 Preview do planejamento")
        
        ciclo_preview = st.session_state.ciclo_preview
        
        # Mostrar preview
        col_prev1, col_prev2 = st.columns(2)
        
        with col_prev1:
            st.markdown("**📅 Configuração:**")
            config = ciclo_preview['config_ciclo']
            st.write(f"- **Duração:** {config['duracao_semanas']} semanas")
            st.write(f"- **Frequência:** {config['frequencia'].replace('_', ' ').title()}")
            st.write(f"- **Período:** {config['data_inicio']} a {config['data_fim']}")
            st.write(f"- **Foco:** {config['foco_principal']}")
            
            st.markdown("**🎯 Metas incluídas:**")
            for meta in config['metas_selecionadas'][:3]:
                st.write(f"- {meta['tipo']}: {meta['descricao'][:50]}...")
        
        with col_prev2:
            st.markdown("**🧩 Recursos incorporados:**")
            recursos = ciclo_preview.get('recursos_incorporados', {})
            if recursos:
                for recurso_id, dados in recursos.items():
                    nome = recursos_nomes.get(recurso_id, recurso_id)
                    st.write(f"- {nome}")
            else:
                st.write("Nenhum recurso incorporado")
            
            st.markdown("**🗓️ Cronograma:**")
            if 'cronograma' in ciclo_preview:
                cronograma = ciclo_preview['cronograma']
                if 'fases' in cronograma:
                    st.write(f"- {len(cronograma['fases'])} fases planejadas")
                if 'semanas' in cronograma:
                    st.write(f"- {len(cronograma['semanas'])} semanas com atividades")
        
        # Botão para salvar
        col_save1, col_save2, col_save3 = st.columns(3)
        
        with col_save2:
            if st.button("💾 Salvar planejamento", type="primary", use_container_width=True):
                # Salvar no Supabase
                resultado = salvar_paee_ciclo(aluno['id'], ciclo_preview)
                
                if resultado['sucesso']:
                    st.success(f"✅ Ciclo salvo com sucesso! ID: {resultado['ciclo_id'][:8]}")
                    
                    # Limpar preview
                    del st.session_state.ciclo_preview
                    
                    # Atualizar interface
                    time.sleep(2)
                    st.rerun()
                else:
                    st.error(f"❌ Erro ao salvar: {resultado.get('erro', 'Erro desconhecido')}")
        
        with col_save3:
            if st.button("🔄 Gerar novo", type="secondary", use_container_width=True):
                del st.session_state.ciclo_preview
                st.rerun()

# ==============================================================================
# RODAPÉ E INFORMAÇÕES
# ==============================================================================
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #64748B; font-size: 0.9rem; padding: 20px;">
    <p>📋 <strong>Planejamento do Ciclo AEE</strong> | Sistema Integrado Omnisfera</p>
    <p>🔗 <strong>Fluxo completo:</strong> PEI → Diagnóstico → Recursos → Planejamento do Ciclo → Execução → Avaliação</p>
    <p>💡 <strong>Integração:</strong> Todos os recursos são vinculados ao PEI e salvos no histórico do aluno.</p>
</div>
""", unsafe_allow_html=True)
