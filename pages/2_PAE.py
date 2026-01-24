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
    .mod-card-rect:hover .mod-title {{ color: #4F46E5; }}
    .mod-desc {{ font-size: 0.8rem; color: #64748B; line-height: 1.4; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }}

    /* CORES */
    .c-purple {{ background: #8B5CF6 !important; }}
    .bg-purple-soft {{ background: transparent !important; color: #8B5CF6 !important; }}

    /* ABAS */
    .stTabs [data-baseweb="tab-list"] {{ gap: 4px !important; background-color: transparent !important; padding: 0 !important; border-radius: 0 !important; margin-top: 24px !important; border-bottom: none !important; flex-wrap: wrap !important; }}
    .stTabs [data-baseweb="tab"] {{ height: 36px !important; white-space: nowrap !important; background-color: transparent !important; border-radius: 20px !important; padding: 0 16px !important; color: #64748B !important; font-weight: 600 !important; font-size: 0.72rem !important; text-transform: uppercase !important; letter-spacing: 0.3px !important; transition: all 0.2s ease !important; border: 1px solid #E2E8F0 !important; margin: 0 !important; }}
    .stTabs [aria-selected="true"] {{ background-color: #8B5CF6 !important; color: white !important; font-weight: 700 !important; border: 1px solid #8B5CF6 !important; box-shadow: 0 1px 3px rgba(139, 92, 246, 0.2) !important; }}
    .stTabs [data-baseweb="tab"]:not([aria-selected="true"]) {{ background-color: white !important; }}
    .stTabs [data-baseweb="tab"]:hover:not([aria-selected="true"]) {{ background-color: #F8FAFC !important; border-color: #CBD5E1 !important; color: #475569 !important; }}
    .stTabs [data-baseweb="tab"]::after, .stTabs [aria-selected="true"]::after, .stTabs [data-baseweb="tab"]::before, .stTabs [aria-selected="true"]::before {{ display: none !important; }}
    .stTabs [data-baseweb="tab-list"] {{ border-bottom: none !important; }}

    /* PEDAGOGIA BOX */
    .pedagogia-box {{ background-color: #F8FAFC; border-left: 4px solid #CBD5E1; padding: 20px; border-radius: 0 12px 12px 0; margin-bottom: 25px; font-size: 0.95rem; color: #4A5568; }}

    /* RESPONSIVIDADE */
    @media (max-width: 768px) {{ .mod-card-rect {{ height: auto; flex-direction: column; padding: 16px; }} .mod-icon-area {{ width: 100%; height: 60px; border-right: none; border-bottom: 1px solid #F1F5F9; }} .mod-content {{ padding: 16px 0 0 0; }} }}
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

with st.sidebar:
    try: st.image("ominisfera.png", width=150)
    except: st.write("🌐 OMNISFERA")
    st.markdown("---")
    if st.button("🏠 Voltar para Home", use_container_width=True): st.switch_page("Home.py")
    st.markdown("---")

# ==============================================================================
# CARD HERO
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
# FUNÇÕES SUPABASE (REST)
# ==============================================================================
def _sb_url() -> str:
    url = str(st.secrets.get("SUPABASE_URL", "")).strip()
    if not url: raise RuntimeError("SUPABASE_URL missing")
    return url.rstrip("/")

def _sb_key() -> str:
    key = str(st.secrets.get("SUPABASE_SERVICE_KEY", "") or st.secrets.get("SUPABASE_ANON_KEY", "")).strip()
    if not key: raise RuntimeError("SUPABASE_KEY missing")
    return key

def _headers() -> dict:
    key = _sb_key()
    return {"apikey": key, "Authorization": f"Bearer {key}", "Content-Type": "application/json"}

# ==============================================================================
# CARREGAR ESTUDANTES (AGORA LENDO O PEI_DATA)
# ==============================================================================
@st.cache_data(ttl=10, show_spinner=False)
def list_students_rest():
    """Busca estudantes do Supabase incluindo o campo PEI_DATA"""
    WORKSPACE_ID = st.session_state.get("workspace_id")
    if not WORKSPACE_ID: return []
    
    try:
        # AQUI MUDOU: Adicionado 'pei_data' no select
        base = (
            f"{_sb_url()}/rest/v1/students"
            f"?select=id,name,grade,class_group,diagnosis,created_at,pei_data"
            f"&workspace_id=eq.{WORKSPACE_ID}"
            f"&order=created_at.desc"
        )
        r = requests.get(base, headers=_headers(), timeout=20)
        return r.json() if r.status_code == 200 else []
    except:
        return []

def carregar_estudantes_supabase():
    """Carrega e processa, extraindo dados ricos do PEI"""
    dados = list_students_rest()
    estudantes = []
    
    for item in dados:
        # Tenta pegar dados do JSONB 'pei_data' salvo no módulo anterior
        pei_completo = item.get('pei_data') or {}
        
        # O contexto para IA vem preferencialmente do texto gerado no módulo PEI
        contexto_ia = pei_completo.get('ia_sugestao', '')
        
        # Se não tiver PEI gerado, monta um resumo básico
        if not contexto_ia:
            diag = item.get('diagnosis', 'Não informado')
            serie = item.get('grade', '')
            contexto_ia = f"Aluno: {item.get('name')}. Série: {serie}. Diagnóstico: {diag}."

        estudante = {
            'nome': item.get('name', ''),
            'serie': item.get('grade', ''),
            'hiperfoco': item.get('diagnosis', ''), # Usando diagnóstico como hiperfoco/contexto principal
            'ia_sugestao': contexto_ia, # AQUI ESTÁ O SEGREDO: O TEXTO RICO DO PEI
            'id': item.get('id', ''),
            'pei_data': pei_completo # Guarda tudo caso precise
        }
        if estudante['nome']:
            estudantes.append(estudante)
            
    return estudantes

# ==============================================================================
# CARREGAMENTO DOS DADOS
# ==============================================================================
if 'banco_estudantes' not in st.session_state or not st.session_state.banco_estudantes:
    with st.spinner("🔄 Lendo dados da nuvem..."):
        st.session_state.banco_estudantes = carregar_estudantes_supabase()

if not st.session_state.banco_estudantes:
    st.warning("⚠️ Nenhum aluno encontrado.")
    if st.button("📘 Ir para o módulo PEI", type="primary"): st.switch_page("pages/1_PEI.py")
    st.stop()

# --- SELEÇÃO DE ALUNO ---
lista_alunos = [a['nome'] for a in st.session_state.banco_estudantes]
col_sel, col_info = st.columns([1, 2])
with col_sel:
    nome_aluno = st.selectbox("📂 Selecione o Estudante:", lista_alunos)

aluno = next((a for a in st.session_state.banco_estudantes if a.get('nome') == nome_aluno), None)

if not aluno: st.stop()

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

# --- GESTÃO DE CHAVES ---
if 'OPENAI_API_KEY' in st.secrets: api_key = st.secrets['OPENAI_API_KEY']
else: api_key = st.sidebar.text_input("Chave OpenAI:", type="password")

# --- FUNÇÕES DE IA ---
def gerar_diagnostico_barreiras(api_key, aluno, obs_prof):
    client = OpenAI(api_key=api_key)
    # Usa o 'ia_sugestao' que agora contém o PEI completo
    contexto = aluno.get('ia_sugestao', '')
    prompt = f"""
    ATUAR COMO: Especialista em AEE.
    ALUNO: {aluno['nome']} | DIAGNÓSTICO: {aluno.get('hiperfoco')}
    CONTEXTO DO PEI: {contexto[:2500]}
    OBSERVAÇÃO ATUAL: {obs_prof}
    
    CLASSIFIQUE AS BARREIRAS (LBI):
    1. **Barreiras Comunicacionais**
    2. **Barreiras Metodológicas**
    3. **Barreiras Atitudinais**
    4. **Barreiras Tecnológicas**
    SAÍDA: Tabela Markdown.
    """
    try:
        resp = client.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "user", "content": prompt}], temperature=0.5)
        return resp.choices[0].message.content
    except Exception as e: return f"Erro: {str(e)}"

def gerar_projetos_ei_bncc(api_key, aluno, campo_exp):
    client = OpenAI(api_key=api_key)
    contexto = aluno.get('ia_sugestao', '')
    prompt = f"""
    ATUAR COMO: Especialista em Ed. Infantil Inclusiva.
    ALUNO: {aluno['nome']} | CONTEXTO PEI: {contexto[:2000]}
    CAMPO DE EXPERIÊNCIA: "{campo_exp}".
    
    Crie 3 EXPERIÊNCIAS LÚDICAS (Atividades):
    1. Use interesses do aluno.
    2. Elimine barreiras.
    3. Sensorial e concreto.
    """
    try:
        resp = client.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "user", "content": prompt}], temperature=0.7)
        return resp.choices[0].message.content
    except Exception as e: return str(e)

def gerar_plano_habilidades(api_key, aluno, foco_treino):
    client = OpenAI(api_key=api_key)
    contexto = aluno.get('ia_sugestao', '')
    prompt = f"""
    CRIE PLANO DE INTERVENÇÃO AEE.
    FOCO: {foco_treino}.
    ALUNO: {aluno['nome']} | CONTEXTO PEI: {contexto[:2000]}
    GERE 3 METAS SMART (Curto, Médio, Longo prazo).
    """
    try:
        resp = client.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "user", "content": prompt}], temperature=0.7)
        return resp.choices[0].message.content
    except Exception as e: return str(e)

def sugerir_tecnologia_assistiva(api_key, aluno, dificuldade):
    client = OpenAI(api_key=api_key)
    contexto = aluno.get('ia_sugestao', '')
    prompt = f"""
    SUGESTÃO DE TECNOLOGIA ASSISTIVA.
    Aluno: {aluno['nome']} | Dificuldade: {dificuldade}.
    Contexto PEI: {contexto[:1500]}
    Sugira: Baixa Tecnologia (DIY), Média e Alta.
    """
    try:
        resp = client.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "user", "content": prompt}], temperature=0.7)
        return resp.choices[0].message.content
    except Exception as e: return str(e)

def gerar_documento_articulacao(api_key, aluno, frequencia, acoes):
    client = OpenAI(api_key=api_key)
    prompt = f"""
    CARTA DE ARTICULAÇÃO (AEE -> SALA REGULAR).
    Aluno: {aluno['nome']}. Frequência: {frequencia}.
    Ações no AEE: {acoes}.
    Dê 3 dicas práticas para o professor regente.
    """
    try:
        resp = client.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "user", "content": prompt}], temperature=0.7)
        return resp.choices[0].message.content
    except Exception as e: return str(e)

# ==============================================================================
# INTERFACE
# ==============================================================================

if is_ei:
    tab_barreiras, tab_projetos, tab_rotina, tab_ponte = st.tabs([
        "BARREIRAS NO BRINCAR", "BANCO DE EXPERIÊNCIAS", "ROTINA & ADAPTAÇÃO", "ARTICULAÇÃO"
    ])
    
    with tab_barreiras:
        st.markdown("<div class='pedagogia-box'><strong>Diagnóstico do Brincar:</strong> Identifique barreiras na interação e no brincar.</div>", unsafe_allow_html=True)
        obs_aee = st.text_area("Observação do Brincar:", height=100)
        if st.button("Mapear Barreiras", type="primary"):
            if not api_key: st.error("Insira a chave OpenAI."); st.stop()
            with st.spinner("Analisando..."):
                st.markdown(gerar_diagnostico_barreiras(api_key, aluno, obs_aee))

    with tab_projetos:
        st.markdown("<div class='pedagogia-box'><strong>Banco de Experiências (BNCC):</strong> Atividades lúdicas.</div>", unsafe_allow_html=True)
        campo_bncc = st.selectbox("Campo de Experiência:", ["O eu, o outro e o nós", "Corpo, gestos e movimentos", "Traços, sons, cores e formas", "Escuta, fala, pensamento e imaginação", "Espaços, tempos, quantidades, relações e transformações"])
        if st.button("✨ Gerar Atividades", type="primary"):
            if not api_key: st.error("Insira a chave OpenAI."); st.stop()
            with st.spinner("Criando..."):
                st.markdown(gerar_projetos_ei_bncc(api_key, aluno, campo_bncc))

    with tab_rotina:
        st.markdown("<div class='pedagogia-box'><strong>Adaptação de Rotina:</strong> Recursos visuais e sensoriais.</div>", unsafe_allow_html=True)
        dif_rotina = st.text_input("Dificuldade na Rotina:")
        if st.button("Sugerir Adaptação", type="primary"):
            if not api_key: st.error("Insira a chave OpenAI."); st.stop()
            with st.spinner("Buscando recursos..."):
                st.markdown(sugerir_tecnologia_assistiva(api_key, aluno, f"Rotina EI: {dif_rotina}"))

else:
    tab_barreiras, tab_plano, tab_tec, tab_ponte = st.tabs([
        "MAPEAR BARREIRAS", "PLANO DE HABILIDADES", "TEC. ASSISTIVA", "CRONOGRAMA & ARTICULAÇÃO"
    ])

    with tab_barreiras:
        st.markdown("<div class='pedagogia-box'><strong>Diagnóstico de Acessibilidade:</strong> O que impede a participação?</div>", unsafe_allow_html=True)
        obs_aee = st.text_area("Observações Iniciais do AEE:", height=100)
        if st.button("Analisar Barreiras", type="primary"):
            if not api_key: st.error("Insira a chave OpenAI."); st.stop()
            with st.spinner("Analisando..."):
                st.markdown(gerar_diagnostico_barreiras(api_key, aluno, obs_aee))

    with tab_plano:
        st.markdown("<div class='pedagogia-box'><strong>Treino de Habilidades:</strong> Desenvolvimento cognitivo/motor.</div>", unsafe_allow_html=True)
        foco = st.selectbox("Foco do atendimento:", ["Funções Executivas", "Autonomia", "Coordenação Motora", "Comunicação", "Habilidades Sociais"])
        if st.button("Gerar Plano", type="primary"):
            if not api_key: st.error("Insira a chave OpenAI."); st.stop()
            with st.spinner("Planejando..."):
                st.markdown(gerar_plano_habilidades(api_key, aluno, foco))

    with tab_tec:
        st.markdown("<div class='pedagogia-box'><strong>Tecnologia Assistiva:</strong> Recursos para autonomia.</div>", unsafe_allow_html=True)
        dif_especifica = st.text_input("Dificuldade Específica:")
        if st.button("Sugerir Recursos", type="primary"):
            if not api_key: st.error("Insira a chave OpenAI."); st.stop()
            with st.spinner("Buscando T.A..."):
                st.markdown(sugerir_tecnologia_assistiva(api_key, aluno, dif_especifica))

with tab_ponte:
    st.markdown("<div class='pedagogia-box'><strong>Ponte com a Sala Regular:</strong> Documento colaborativo.</div>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    freq = c1.selectbox("Frequência:", ["1x/sem", "2x/sem", "3x/sem", "Diário"])
    turno = c2.selectbox("Turno:", ["Manhã", "Tarde"])
    acoes_resumo = st.text_area("Trabalho no AEE:", height=70)
    if st.button("Gerar Carta", type="primary"):
        if not api_key: st.error("Insira a chave OpenAI."); st.stop()
        with st.spinner("Escrevendo..."):
            carta = gerar_documento_articulacao(api_key, aluno, f"{freq} ({turno})", acoes_resumo)
            st.markdown("### 📄 Documento Gerado")
            st.markdown(carta)
            st.download_button("📥 Baixar Carta", carta, "Carta_Articulacao.txt")
