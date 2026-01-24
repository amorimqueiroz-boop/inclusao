import streamlit as st
import os
from openai import OpenAI
import json
import pandas as pd
from datetime import date, datetime
import base64
import requests

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
# BLOCO VISUAL INTELIGENTE: HEADER OMNISFERA (MESMO PADRÃO PEI)
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

# 4. Renderização do Header Flutuante
st.markdown(f"""
<style>
    /* CARD FLUTUANTE (OMNISFERA) - MESMO PADRÃO */
    .omni-badge {{
        position: fixed;
        top: 15px; 
        right: 15px;
        background: {card_bg};
        border: 1px solid {card_border};
        backdrop-filter: blur(8px);
        -webkit-backdrop-filter: blur(8px);
        padding: 4px 30px;
        min-width: 260px;
        justify-content: center;
        border-radius: 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08);
        z-index: 999990;
        display: flex;
        align-items: center;
        gap: 10px;
        pointer-events: none;
    }}

    .omni-text {{
        font-family: 'Plus Jakarta Sans', sans-serif;
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
        height: 26px;
        width: 26px;
        animation: spin-slow 10s linear infinite;
    }}

    /* CARD HERO PARA PAEE - COM FUNDO TRANSPARENTE NO ÍCONE */
    .mod-card-wrapper {{
        display: flex;
        flex-direction: column;
        margin-bottom: 20px;
        border-radius: 16px;
        overflow: hidden;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.02);
    }}

    .mod-card-rect {{
        background: white;
        border-radius: 16px 16px 0 0;
        padding: 0;
        border: 1px solid #E2E8F0;
        border-bottom: none;
        display: flex;
        flex-direction: row;
        align-items: center;
        height: 130px;
        width: 100%;
        position: relative;
        overflow: hidden;
        transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
    }}

    .mod-card-rect:hover {{
        transform: translateY(-4px);
        box-shadow: 0 12px 24px rgba(0, 0, 0, 0.08);
        border-color: #CBD5E1;
    }}

    .mod-bar {{
        width: 6px;
        height: 100%;
        flex-shrink: 0;
    }}

    .mod-icon-area {{
        width: 90px;
        height: 100%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.8rem;
        flex-shrink: 0;
        background: transparent !important; /* FUNDO TRANSPARENTE */
        border-right: 1px solid #F1F5F9;
        transition: all 0.3s ease;
    }}

    .mod-card-rect:hover .mod-icon-area {{
        background: transparent !important;
        transform: scale(1.05);
    }}

    .mod-content {{
        flex-grow: 1;
        padding: 0 24px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }}

    .mod-title {{
        font-weight: 800;
        font-size: 1.1rem;
        color: #1E293B;
        margin-bottom: 6px;
        letter-spacing: -0.3px;
        transition: color 0.2s;
    }}

    .mod-card-rect:hover .mod-title {{
        color: #8B5CF6;
    }}

    .mod-desc {{
        font-size: 0.8rem;
        color: #64748B;
        line-height: 1.4;
        display: -webkit-box;
        -webkit-line-clamp: 2;
        -webkit-box-orient: vertical;
        overflow: hidden;
    }}

    /* CORES DOS CARDS - ROXO PARA PAEE */
    .c-purple {{ background: #8B5CF6 !important; }}
    .bg-purple-soft {{ 
        background: transparent !important; /* FUNDO TRANSPARENTE */
        color: #8B5CF6 !important; /* COR ROXA MAIS INTENSA */
    }}

    /* ABAS EM FORMATO DE PÍLULAS - MESMO PADRÃO DO PEI */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 4px !important;
        background-color: transparent !important;
        padding: 0 !important;
        border-radius: 0 !important;
        margin-top: 24px !important;
        border-bottom: none !important;
        flex-wrap: wrap !important;
    }}

    .stTabs [data-baseweb="tab"] {{
        height: 36px !important;
        white-space: nowrap !important;
        background-color: transparent !important;
        border-radius: 20px !important;
        padding: 0 16px !important;
        color: #64748B !important;
        font-weight: 600 !important;
        font-size: 0.72rem !important;
        text-transform: uppercase !important;
        letter-spacing: 0.3px !important;
        transition: all 0.2s ease !important;
        border: 1px solid #E2E8F0 !important;
        position: relative !important;
        margin: 0 !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }}

    /* ABA ATIVA - FUNDO ROXO SÓLIDO (PAEE) */
    .stTabs [aria-selected="true"] {{
        background-color: #8B5CF6 !important;
        color: white !important;
        font-weight: 700 !important;
        border: 1px solid #8B5CF6 !important;
        box-shadow: 0 1px 3px rgba(139, 92, 246, 0.2) !important;
    }}

    /* ABA INATIVA - APENAS CONTORNO SUTIL */
    .stTabs [data-baseweb="tab"]:not([aria-selected="true"]) {{
        background-color: white !important;
        color: #64748B !important;
        border: 1px solid #E2E8F0 !important;
    }}

    /* HOVER SIMPLES E DIRETO */
    .stTabs [data-baseweb="tab"]:hover:not([aria-selected="true"]) {{
        background-color: #F8FAFC !important;
        border-color: #CBD5E1 !important;
        color: #475569 !important;
    }}

    .stTabs [aria-selected="true"]:hover {{
        background-color: #7C3AED !important;
        border-color: #7C3AED !important;
    }}

    /* PEDAGOGIA BOX (Atualizado para Roxo) */
    .pedagogia-box {{ 
        background-color: #F5F3FF; border-left: 4px solid #8B5CF6; 
        padding: 20px; border-radius: 0 12px 12px 0; margin-bottom: 25px; 
        font-size: 0.95rem; color: #5B21B6; 
    }}

    /* RESPONSIVIDADE PARA TELAS MENORES */
    @media (max-width: 1024px) {{
        .mod-card-rect {{ height: 120px; }}
        .mod-icon-area {{ width: 80px; }}
        .stTabs [data-baseweb="tab"] {{
            font-size: 0.68rem !important;
            padding: 0 14px !important;
            height: 34px !important;
        }}
    }}

    @media (max-width: 768px) {{
        .mod-card-rect {{ 
            height: 110px;
            flex-direction: column;
            height: auto;
            padding: 16px;
        }}
        .mod-bar {{ width: 100%; height: 6px; }}
        .mod-icon-area {{ 
            width: 100%; 
            height: 60px; 
            border-right: none;
            border-bottom: 1px solid #F1F5F9;
        }}
        .mod-content {{ padding: 16px 0 0 0; }}
        
        /* EM MOBILE, AS PÍLULAS FICAM EM GRID */
        .stTabs [data-baseweb="tab-list"] {{
            gap: 6px !important;
        }}
        
        .stTabs [data-baseweb="tab"] {{
            flex: 1 0 calc(33.333% - 4px) !important;
            min-width: calc(33.333% - 4px) !important;
            margin-bottom: 0 !important;
            height: 32px !important;
            border-radius: 16px !important;
            font-size: 0.65rem !important;
            padding: 0 10px !important;
        }}
    }}

    @media (max-width: 640px) {{
        .stTabs [data-baseweb="tab"] {{
            flex: 1 0 calc(50% - 4px) !important;
            min-width: calc(50% - 4px) !important;
            font-size: 0.62rem !important;
            padding: 0 8px !important;
            height: 30px !important;
        }}
    }}

    @media (max-width: 480px) {{
        .stTabs [data-baseweb="tab"] {{
            flex: 1 0 100% !important;
            min-width: 100% !important;
            border-radius: 12px !important;
            margin-bottom: 4px !important;
        }}
    }}
</style>

<!-- BADGE FLUTUANTE OMNISFERA -->
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
# CARD HERO PARA PAEE (MESMO DESIGN DOS ESTUDANTES)
# ==============================================================================
hora = datetime.now().hour
saudacao = "Bom dia" if 5 <= hora < 12 else "Boa tarde" if 12 <= hora < 18 else "Boa noite"
USUARIO_NOME = st.session_state.get("usuario_nome", "Visitante").split()[0]
WORKSPACE_NAME = st.session_state.get("workspace_name", "Workspace")

st.markdown(
    f"""
    <div class="mod-card-wrapper">
        <div class="mod-card-rect">
            <div class="mod-bar c-purple"></div>
            <div class="mod-icon-area bg-purple-soft">
                <i class="ri-wheelchair-fill"></i>
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
# FUNÇÕES DE ACESSO AO SUPABASE (MESMA LÓGICA DA PÁGINA DE ALUNOS)
# ==============================================================================
def _sb_url() -> str:
    url = str(st.secrets.get("SUPABASE_URL", "")).strip()
    if not url:
        raise RuntimeError("SUPABASE_URL não encontrado nos secrets.")
    return url.rstrip("/")

def _sb_key() -> str:
    key = str(st.secrets.get("SUPABASE_SERVICE_KEY", "")).strip()
    if not key:
        key = str(st.secrets.get("SUPABASE_ANON_KEY", "")).strip()
    if not key:
        raise RuntimeError("SUPABASE_SERVICE_KEY/ANON_KEY não encontrado nos secrets.")
    return key

def _headers() -> dict:
    key = _sb_key()
    return {
        "apikey": key,
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
    }

def _http_error(prefix: str, r: requests.Response):
    st.error(f"{prefix}: {r.status_code} {r.text}")
    return []

# ==============================================================================
# CARREGAR ESTUDANTES DO SUPABASE (USANDO STUDENTS TABELA)
# ==============================================================================
@st.cache_data(ttl=10, show_spinner=False)
def list_students_rest():
    """Busca estudantes do Supabase - MESMA LÓGICA DA PÁGINA DE ALUNOS"""
    WORKSPACE_ID = st.session_state.get("workspace_id")
    
    if not WORKSPACE_ID:
        st.error("Workspace ID não encontrado na sessão.")
        return []
    
    try:
        # Tenta a tabela 'students' primeiro (padrão da página Alunos)
        base = (
            f"{_sb_url()}/rest/v1/students"
            f"?select=id,name,grade,class_group,diagnosis,created_at"
            f"&workspace_id=eq.{WORKSPACE_ID}"
            f"&order=created_at.desc"
        )
        r = requests.get(base, headers=_headers(), timeout=20)
        
        if r.status_code == 200:
            data = r.json()
            return data if isinstance(data, list) else []
        else:
            # Tenta tabela alternativa 'planos_pei' se 'students' falhar
            st.warning(f"Tabela 'students' não encontrada (status {r.status_code}). Tentando 'planos_pei'...")
            
            # Usando o usuário atual para filtrar
            usuario_atual = st.session_state.get("usuario_nome", "")
            if usuario_atual:
                base_alt = (
                    f"{_sb_url()}/rest/v1/planos_pei"
                    f"?select=id,nome_aluno,serie,hiperfoco,conteudo_gerado,responsavel,created_at"
                    f"&responsavel=eq.{usuario_atual}"
                    f"&order=created_at.desc"
                )
                r_alt = requests.get(base_alt, headers=_headers(), timeout=20)
                
                if r_alt.status_code == 200:
                    data = r_alt.json()
                    return data if isinstance(data, list) else []
                else:
                    return _http_error("List planos_pei falhou", r_alt)
            else:
                st.error("Usuário não identificado na sessão.")
                return []
                
    except Exception as e:
        st.error(f"Erro na requisição: {e}")
        return []

def carregar_estudantes_supabase():
    """Carrega estudantes do Supabase convertendo para formato esperado"""
    dados = list_students_rest()
    
    estudantes = []
    for item in dados:
        # Verifica se vem da tabela 'students' ou 'planos_pei'
        if 'name' in item:  # Tabela 'students'
            estudante = {
                'nome': item.get('name', ''),
                'serie': item.get('grade', ''),
                'hiperfoco': item.get('diagnosis', ''),
                'ia_sugestao': f"Série: {item.get('grade', '')} | Turma: {item.get('class_group', '')} | Diagnóstico: {item.get('diagnosis', '')}",
                'responsavel': st.session_state.get("usuario_nome", ""),
                'id': item.get('id', ''),
                'created_at': item.get('created_at', '')
            }
        else:  # Tabela 'planos_pei'
            estudante = {
                'nome': item.get('nome_aluno', ''),
                'serie': item.get('serie', ''),
                'hiperfoco': item.get('hiperfoco', ''),
                'ia_sugestao': item.get('conteudo_gerado', ''),
                'responsavel': item.get('responsavel', ''),
                'id': item.get('id', ''),
                'created_at': item.get('created_at', '')
            }
        
        # Só adiciona se tiver nome
        if estudante['nome']:
            estudantes.append(estudante)
    
    return estudantes

# ==============================================================================
# CARREGAMENTO DOS DADOS
# ==============================================================================
if 'banco_estudantes' not in st.session_state or not st.session_state.banco_estudantes:
    with st.spinner("🔄 Carregando estudantes do Supabase..."):
        st.session_state.banco_estudantes = carregar_estudantes_supabase()

# Se não houver estudantes, mostra opção para ir ao PEI
if not st.session_state.banco_estudantes:
    st.warning("⚠️ Nenhum aluno encontrado. Você precisa criar Planos Educacionais Individualizados (PEI) primeiro.")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("📘 Ir para o módulo PEI", type="primary", use_container_width=True):
            st.switch_page("pages/1_PEI.py")
    
    st.stop()

# --- SELEÇÃO DE ALUNO ---
lista_alunos = [a['nome'] for a in st.session_state.banco_estudantes if a.get('nome')]
col_sel, col_info = st.columns([1, 2])
with col_sel:
    nome_aluno = st.selectbox("📂 Selecione o Estudante:", lista_alunos)

aluno = next((a for a in st.session_state.banco_estudantes if a.get('nome') == nome_aluno), None)

if not aluno:
    st.error("Estudante não encontrado nos dados.")
    st.stop()

# --- DETECTOR DE EDUCAÇÃO INFANTIL ---
serie_aluno = aluno.get('serie', '').lower()
is_ei = any(term in serie_aluno for term in ["infantil", "creche", "pré", "pré-escola", "maternal", "berçario", "jardim"])

# --- HEADER DO ALUNO (CORES ROXAS) ---
st.markdown(f"""
    <div style="background-color: #F5F3FF; border: 1px solid #C4B5FD; border-radius: 16px; padding: 20px 30px; margin-bottom: 20px; display: flex; justify-content: space-between; align-items: center; box-shadow: 0 2px 4px rgba(0,0,0,0.02);">
        <div><div style="font-size: 0.8rem; color: #8B5CF6; font-weight: 800; text-transform: uppercase; letter-spacing: 1px;">Nome</div><div style="font-size: 1.2rem; color: #2D3748; font-weight: 800;">{aluno.get('nome', 'Não informado')}</div></div>
        <div><div style="font-size: 0.8rem; color: #8B5CF6; font-weight: 800; text-transform: uppercase; letter-spacing: 1px;">Série</div><div style="font-size: 1.2rem; color: #2D3748; font-weight: 800;">{aluno.get('serie', '-')}</div></div>
        <div><div style="font-size: 0.8rem; color: #8B5CF6; font-weight: 800; text-transform: uppercase; letter-spacing: 1px;">Hiperfoco</div><div style="font-size: 1.2rem; color: #8B5CF6; font-weight: 800;">{aluno.get('hiperfoco', '-')}</div></div>
    </div>
""", unsafe_allow_html=True)

if is_ei:
    st.info("🧸 **Modo Educação Infantil Ativado:** Foco em Campos de Experiência (BNCC) e Brincar Heurístico.")

with st.expander("📄 Ver Resumo do PEI (Base para o PAEE)", expanded=False):
    st.info(aluno.get('ia_sugestao', 'Nenhum dado de PEI processado ainda.'))

# --- GESTÃO DE CHAVES ---
if 'OPENAI_API_KEY' in st.secrets: api_key = st.secrets['OPENAI_API_KEY']
else: api_key = st.sidebar.text_input("Chave OpenAI:", type="password")

# --- FUNÇÕES DE IA (MANTIDAS IGUAIS) ---

def gerar_diagnostico_barreiras(api_key, aluno, obs_prof):
    client = OpenAI(api_key=api_key)
    prompt = f"""
    ATUAR COMO: Especialista em AEE.
    ALUNO: {aluno['nome']} | HIPERFOCO: {aluno.get('hiperfoco')}
    RESUMO PEI: {aluno.get('ia_sugestao', '')[:1000]}
    OBSERVAÇÃO ATUAL: {obs_prof}
    
    CLASSIFIQUE AS BARREIRAS (Lei Brasileira de Inclusão):
    1. **Barreiras Comunicacionais**
    2. **Barreiras Metodológicas**
    3. **Barreiras Atitudinais**
    4. **Barreiras Tecnológicas/Instrumentais**
    SAÍDA: Tabela Markdown.
    """
    try:
        resp = client.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "user", "content": prompt}], temperature=0.5)
        return resp.choices[0].message.content
    except Exception as e: return f"Erro: {str(e)}"

def gerar_projetos_ei_bncc(api_key, aluno, campo_exp):
    client = OpenAI(api_key=api_key)
    prompt = f"""
    ATUAR COMO: Pedagogo Especialista em Educação Infantil e Inclusão.
    ALUNO: {aluno['nome']} (Educação Infantil).
    HIPERFOCO: {aluno.get('hiperfoco', 'Brincadeiras')}.
    RESUMO DAS NECESSIDADES (PEI): {aluno.get('ia_sugestao', '')[:800]}
    
    SUA MISSÃO: Criar 3 propostas de EXPERIÊNCIAS LÚDICAS (Atividades) focadas no Campo de Experiência: "{campo_exp}".
    
    REGRAS:
    1. As atividades devem usar o Hiperfoco para engajar.
    2. Devem eliminar barreiras de participação.
    3. Devem ser sensoriais e concretas.
    
    SAÍDA ESPERADA (Markdown):
    ### 🧸 Experiência 1: [Nome Criativo]
    * **Objetivo:** ...
    * **Como Fazer:** ...
    * **Adaptação:** ...
    
    (Repetir para 2 e 3)
    """
    try:
        resp = client.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "user", "content": prompt}], temperature=0.7)
        return resp.choices[0].message.content
    except Exception as e: return str(e)

def gerar_plano_habilidades(api_key, aluno, foco_treino):
    client = OpenAI(api_key=api_key)
    prompt = f"""
    CRIE UM PLANO DE INTERVENÇÃO AEE (Sala de Recursos).
    FOCO: Desenvolvimento de Habilidades ({foco_treino}).
    ALUNO: {aluno['nome']} | HIPERFOCO: {aluno.get('hiperfoco')}
    GERE 3 METAS SMART (Longo Prazo, Estratégia com Hiperfoco, Recurso).
    """
    try:
        resp = client.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "user", "content": prompt}], temperature=0.7)
        return resp.choices[0].message.content
    except Exception as e: return str(e)

def sugerir_tecnologia_assistiva(api_key, aluno, dificuldade):
    client = OpenAI(api_key=api_key)
    prompt = f"""
    SUGESTÃO DE TECNOLOGIA ASSISTIVA.
    Aluno: {aluno['nome']}. Dificuldade: {dificuldade}.
    Sugira: Baixa Tecnologia (DIY), Média Tecnologia, Alta Tecnologia.
    """
    try:
        resp = client.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "user", "content": prompt}], temperature=0.7)
        return resp.choices[0].message.content
    except Exception as e: return str(e)

def gerar_documento_articulacao(api_key, aluno, frequencia, acoes):
    client = OpenAI(api_key=api_key)
    prompt = f"""
    ESCREVA UMA CARTA DE ARTICULAÇÃO (AEE -> SALA REGULAR).
    Aluno: {aluno['nome']}. Frequência: {frequencia}.
    Ações no AEE: {acoes}.
    Dê 3 dicas para o professor regente. Tom colaborativo.
    """
    try:
        resp = client.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "user", "content": prompt}], temperature=0.7)
        return resp.choices[0].message.content
    except Exception as e: return str(e)

# ==============================================================================
# ABAS DO PAEE (MESMO PADRÃO DO PEI - TEXTO EM MAIÚSCULAS, SEM EMOJIS)
# ==============================================================================

if is_ei:
    # --- ABAS ESPECÍFICAS PARA EDUCAÇÃO INFANTIL ---
    tab_barreiras, tab_projetos, tab_rotina, tab_ponte = st.tabs([
        "BARREIRAS NO BRINCAR", 
        "BANCO DE EXPERIÊNCIAS", 
        "ROTINA & ADAPTAÇÃO", 
        "ARTICULAÇÃO"
    ])
    
    # 1. BARREIRAS (EI)
    with tab_barreiras:
        st.markdown("<div class='pedagogia-box'><strong>Diagnóstico do Brincar:</strong> Na Educação Infantil, a barreira não é 'não escrever', mas sim 'não participar da interação'.</div>", unsafe_allow_html=True)
        obs_aee = st.text_area("Observação do Brincar:", placeholder="Ex: Isola-se no parquinho, não aceita texturas...", height=100)
        if st.button("Mapear Barreiras do Brincar", type="primary"):
            if not api_key: st.error("Insira a chave OpenAI."); st.stop()
            with st.spinner("Analisando..."):
                resultado = gerar_diagnostico_barreiras(api_key, aluno, obs_aee)
                st.markdown(resultado)

    # 2. PROJETOS (EI)
    with tab_projetos:
        st.markdown("<div class='pedagogia-box'><strong>Banco de Experiências (BNCC):</strong> Atividades lúdicas usando o hiperfoco.</div>", unsafe_allow_html=True)
        
        campo_bncc = st.selectbox("Selecione o Campo de Experiência (BNCC):", [
            "O eu, o outro e o nós (Identidade e Interação)",
            "Corpo, gestos e movimentos (Motricidade)",
            "Traços, sons, cores e formas (Artes)",
            "Escuta, fala, pensamento e imaginação (Oralidade)",
            "Espaços, tempos, quantidades, relações e transformações (Cognição)"
        ])
        
        if st.button("✨ Gerar Atividades Lúdicas", type="primary"):
            if not api_key: st.error("Insira a chave OpenAI."); st.stop()
            with st.spinner("Criando experiências..."):
                atividades = gerar_projetos_ei_bncc(api_key, aluno, campo_bncc)
                st.markdown(atividades)

    # 3. ROTINA (EI)
    with tab_rotina:
        st.markdown("<div class='pedagogia-box'><strong>Adaptação de Rotina:</strong> Recursos visuais e sensoriais para a creche/pré-escola.</div>", unsafe_allow_html=True)
        dif_rotina = st.text_input("Dificuldade na Rotina:", placeholder="Ex: Hora do soninho, Desfralde, Alimentação")
        if st.button("Sugerir Adaptação", type="primary"):
            if not api_key: st.error("Insira a chave OpenAI."); st.stop()
            with st.spinner("Buscando recursos..."):
                resultado = sugerir_tecnologia_assistiva(api_key, aluno, f"Rotina EI: {dif_rotina}")
                st.markdown(resultado)

else:
    # --- ABAS PADRÃO (FUNDAMENTAL / MÉDIO) ---
    tab_barreiras, tab_plano, tab_tec, tab_ponte = st.tabs([
        "MAPEAR BARREIRAS", 
        "PLANO DE HABILIDADES", 
        "TEC. ASSISTIVA", 
        "CRONOGRAMA & ARTICULAÇÃO"
    ])

    # 1. BARREIRAS
    with tab_barreiras:
        st.markdown("<div class='pedagogia-box'><strong>Diagnóstico de Acessibilidade:</strong> Identifique o que impede o aluno de participar, não a doença.</div>", unsafe_allow_html=True)
        obs_aee = st.text_area("Observações Iniciais do AEE (Opcional):", placeholder="Ex: O aluno se recusa a escrever...", height=100)
        if st.button("Analisar Barreiras via IA", type="primary"):
            if not api_key: st.error("Insira a chave OpenAI."); st.stop()
            with st.spinner("Analisando..."):
                resultado = gerar_diagnostico_barreiras(api_key, aluno, obs_aee)
                st.markdown(resultado)

    # 2. PLANO
    with tab_plano:
        st.markdown("<div class='pedagogia-box'><strong>Treino de Habilidades:</strong> Desenvolvimento cognitivo, motor e social.</div>", unsafe_allow_html=True)
        foco = st.selectbox("Foco do atendimento:", ["Funções Executivas", "Autonomia", "Coordenação Motora", "Comunicação", "Habilidades Sociais"])
        if st.button("Gerar Plano", type="primary"):
            if not api_key: st.error("Insira a chave OpenAI."); st.stop()
            with st.spinner("Planejando..."):
                resultado = gerar_plano_habilidades(api_key, aluno, foco)
                st.markdown(resultado)

    # 3. T.A.
    with tab_tec:
        st.markdown("<div class='pedagogia-box'><strong>Tecnologia Assistiva:</strong> Recursos para autonomia.</div>", unsafe_allow_html=True)
        dif_especifica = st.text_input("Dificuldade Específica:", placeholder="Ex: Não segura o lápis")
        if st.button("Sugerir Recursos", type="primary"):
            if not api_key: st.error("Insira a chave OpenAI."); st.stop()
            with st.spinner("Buscando T.A..."):
                resultado = sugerir_tecnologia_assistiva(api_key, aluno, dif_especifica)
                st.markdown(resultado)

# 4. ARTICULAÇÃO (COMUM A TODOS)
with tab_ponte:
    st.markdown("<div class='pedagogia-box'><strong>Ponte com a Sala Regular:</strong> Documento de colaboração com os professores.</div>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    freq = c1.selectbox("Frequência:", ["1x/sem", "2x/sem", "3x/sem", "Diário"])
    turno = c2.selectbox("Turno:", ["Manhã", "Tarde"])
    acoes_resumo = st.text_area("Trabalho no AEE:", placeholder="Ex: Comunicação alternativa...", height=70)
    if st.button("Gerar Carta", type="primary"):
        if not api_key: st.error("Insira a chave OpenAI."); st.stop()
        with st.spinner("Escrevendo..."):
            carta = gerar_documento_articulacao(api_key, aluno, f"{freq} ({turno})", acoes_resumo)
            st.markdown("### 📄 Documento Gerado")
            st.markdown(carta)
            st.download_button("📥 Baixar Carta", carta, "Carta_Articulacao.txt")
