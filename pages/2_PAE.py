import streamlit as st
import os
from openai import OpenAI
import json
import pandas as pd
from datetime import date
import base64

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
# 2. BLOCO VISUAL (DESIGN SYSTEM PREMIUM - AZUL SÓBRIO)
# ==============================================================================
import os
import base64
import streamlit as st

# 1. Detecção de Ambiente
try: IS_TEST_ENV = st.secrets.get("ENV") == "TESTE"
except: IS_TEST_ENV = False

# 2. Logo Base64 (Giratória)
def get_logo_base64():
    caminhos = ["omni_icone.png", "logo.png", "iconeaba.png"]
    for c in caminhos:
        if os.path.exists(c):
            with open(c, "rb") as f: return f"data:image/png;base64,{base64.b64encode(f.read()).decode()}"
    return "https://cdn-icons-png.flaticon.com/512/1183/1183672.png"

src_logo_giratoria = get_logo_base64()

# 3. Cores Dinâmicas (Badge)
if IS_TEST_ENV:
    card_bg, card_border = "rgba(255, 220, 50, 0.95)", "rgba(200, 160, 0, 0.5)"
else:
    card_bg, card_border = "rgba(255, 255, 255, 0.85)", "rgba(255, 255, 255, 0.6)"

# 4. Renderização CSS Global (Design System Premium - AZUL)
st.markdown(f"""
    <link href="https://cdn.jsdelivr.net/npm/remixicon@4.1.0/fonts/remixicon.css" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800&display=swap" rel="stylesheet">
    
    <style>
    /* VARIÁVEIS GLOBAIS - AZUL SÓBRIO */
    :root {{ 
        --brand-blue: #0F52BA; 
        --brand-hover: #0A3D8F;
        --card-radius: 16px; 
    }}
    
    /* 1. Fontes e Cores Base */
    html, body, [class*="css"] {{ 
        font-family: 'Nunito', sans-serif; 
        color: #2D3748; 
        background-color: #F7FAFC; 
    }}
    .block-container {{ 
        padding-top: 1.5rem !important; 
        padding-bottom: 5rem !important; 
    }}

    /* 2. Navegação em Abas "Glow" Clean */
    div[data-baseweb="tab-border"], div[data-baseweb="tab-highlight"] {{ display: none !important; }}
    
    .stTabs [data-baseweb="tab-list"] {{ 
        gap: 8px; 
        display: flex;
        flex-wrap: nowrap;
        overflow-x: auto;
        white-space: nowrap;
        padding: 10px 5px;
        -ms-overflow-style: none;
        scrollbar-width: none;
    }}
    .stTabs [data-baseweb="tab-list"]::-webkit-scrollbar {{ display: none; }}

    /* ESTILO PADRÃO DAS ABAS (Pílula) */
    .stTabs [data-baseweb="tab"] {{ 
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
    }}
    
    .stTabs [data-baseweb="tab"]:hover {{
        border-color: #CBD5E0;
        color: #4A5568;
        background-color: #EDF2F7;
    }}

    /* ESTADO SELECIONADO (AZUL COM GLOW) */
    .stTabs [aria-selected="true"] {{ 
        background-color: transparent !important; 
        color: var(--brand-blue) !important; 
        border: 1px solid var(--brand-blue) !important; 
        font-weight: 800;
        box-shadow: 0 0 12px rgba(15, 82, 186, 0.3), inset 0 0 5px rgba(15, 82, 186, 0.1) !important;
    }}

    /* 3. Header Unificado (Com Divisor Vertical - SEM barra lateral) */
    .header-unified {{ 
        background-color: white; 
        padding: 35px 40px; /* Altura ajustada */
        border-radius: 16px; 
        border: 1px solid #E2E8F0; 
        box-shadow: 0 2px 10px rgba(0,0,0,0.02); 
        margin-bottom: 20px; 
        display: flex; 
        align-items: center; 
        gap: 20px;
        justify-content: flex-start; 
    }}
    
    .header-subtitle {{ 
        font-size: 1.2rem; 
        color: #718096; 
        font-weight: 600; 
        border-left: 2px solid #E2E8F0; /* O DIVISOR VERTICAL */
        padding-left: 20px; 
        line-height: 1.2; 
    }}

    /* 5. Inputs e Botões (Arredondamento 8px) */
    .stTextInput input, .stTextArea textarea, .stSelectbox div[data-baseweb="select"], .stNumberInput input {{ 
        border-radius: 8px !important; 
        border-color: #E2E8F0 !important; 
    }}
    
    div[data-testid="column"] .stButton button {{ 
        border-radius: 8px !important; 
        font-weight: 800 !important; 
        text-transform: uppercase; 
        height: 50px !important; 
        background-color: var(--brand-blue) !important; /* Azul Sóbrio */
        color: white !important; 
        border: none !important;
        letter-spacing: 0.5px;
    }}
    div[data-testid="column"] .stButton button:hover {{ 
        background-color: var(--brand-hover) !important; 
    }}

    /* CARD FLUTUANTE (OMNISFERA) */
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
    
    /* PEDAGOGIA BOX (Atualizado para Azul) */
    .pedagogia-box {{ 
        background-color: #F8FAFC; border-left: 4px solid var(--brand-blue); 
        padding: 20px; border-radius: 0 12px 12px 0; margin-bottom: 25px; 
        font-size: 0.95rem; color: #4A5568; 
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

# --- BARRA LATERAL ---
with st.sidebar:
    try: st.image("ominisfera.png", width=150)
    except: st.write("🌐 OMNISFERA")
    st.markdown("---")
    if st.button("🏠 Voltar para Home", use_container_width=True): st.switch_page("Home.py")
    st.markdown("---")

# ==============================================================================
# 2. SISTEMA PAEE (Plano de Atendimento Educacional Especializado)
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

# --- HEADER UNIFICADO (CLEAN COM DIVISOR - AZUL) ---
def get_img_tag_custom(file_path, width):
    if os.path.exists(file_path):
        with open(file_path, "rb") as f:
            data = base64.b64encode(f.read()).decode("utf-8")
        return f'<img src="data:image/png;base64,{data}" width="{width}" style="object-fit: contain;">'
    return ""

img_pae = get_img_tag_custom("pae.png", "220") # <--- AUMENTADO PARA 220px

st.markdown(f"""
<div class="header-unified">
    <div style="flex-shrink: 0;">
        {img_pae}
    </div>
    <div class="header-subtitle">
        Sala de Recursos & Eliminação de Barreiras
    </div>
</div>
""", unsafe_allow_html=True)

if not st.session_state.banco_estudantes:
    st.warning("⚠️ Nenhum aluno encontrado para o seu usuário. Cadastre no módulo PEI primeiro.")
    st.stop()

# --- SELEÇÃO DE ALUNO ---
lista_alunos = [a['nome'] for a in st.session_state.banco_estudantes]
col_sel, col_info = st.columns([1, 2])
with col_sel:
    nome_aluno = st.selectbox("📂 Selecione o Estudante:", lista_alunos)

aluno = next(a for a in st.session_state.banco_estudantes if a['nome'] == nome_aluno)

# --- DETECTOR DE EDUCAÇÃO INFANTIL ---
serie_aluno = aluno.get('serie', '').lower()
is_ei = "infantil" in serie_aluno or "creche" in serie_aluno or "pré" in serie_aluno

# --- HEADER DO ALUNO (CORES AZUIS) ---
st.markdown(f"""
    <div style="background-color: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 16px; padding: 20px 30px; margin-bottom: 20px; display: flex; justify-content: space-between; align-items: center; box-shadow: 0 2px 4px rgba(0,0,0,0.02);">
        <div><div style="font-size: 0.8rem; color: #718096; font-weight: 800; text-transform: uppercase; letter-spacing: 1px;">Nome</div><div style="font-size: 1.2rem; color: #2D3748; font-weight: 800;">{aluno.get('nome')}</div></div>
        <div><div style="font-size: 0.8rem; color: #718096; font-weight: 800; text-transform: uppercase; letter-spacing: 1px;">Série</div><div style="font-size: 1.2rem; color: #2D3748; font-weight: 800;">{aluno.get('serie', '-')}</div></div>
        <div><div style="font-size: 0.8rem; color: #718096; font-weight: 800; text-transform: uppercase; letter-spacing: 1px;">Hiperfoco</div><div style="font-size: 1.2rem; color: #0F52BA; font-weight: 800;">{aluno.get('hiperfoco', '-')}</div></div>
    </div>
""", unsafe_allow_html=True)

if is_ei:
    st.info("🧸 **Modo Educação Infantil Ativado:** Foco em Campos de Experiência (BNCC) e Brincar Heurístico.")

with st.expander("📄 Ver Resumo do PEI (Base para o PAEE)", expanded=False):
    st.info(aluno.get('ia_sugestao', 'Nenhum dado de PEI processado ainda.'))

# --- GESTÃO DE CHAVES ---
if 'OPENAI_API_KEY' in st.secrets: api_key = st.secrets['OPENAI_API_KEY']
else: api_key = st.sidebar.text_input("Chave OpenAI:", type="password")

# --- FUNÇÕES DE IA ---

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
# LÓGICA CONDICIONAL DE ABAS (O CORAÇÃO DA MUDANÇA)
# ==============================================================================

if is_ei:
    # --- ABAS ESPECÍFICAS PARA EDUCAÇÃO INFANTIL ---
    tab_barreiras, tab_projetos, tab_rotina, tab_ponte = st.tabs([
        "🔍 Barreiras no Brincar", 
        "🧸 Banco de Experiências", 
        "🏠 Rotina & Adaptação", 
        "🌉 Articulação"
    ])
    
    # 1. BARREIRAS (EI)
    with tab_barreiras:
        st.markdown("<div class='pedagogia-box'><strong>Diagnóstico do Brincar:</strong> Na Educação Infantil, a barreira não é 'não escrever', mas sim 'não participar da interação'.</div>", unsafe_allow_html=True)
        obs_aee = st.text_area("Observação do Brincar:", placeholder="Ex: Isola-se no parquinho, não aceita texturas...", height=100)
        if st.button("Mapear Barreiras do Brincar", type="primary"):
            if not api_key: st.error("Insira a chave OpenAI."); st.stop()
            with st.spinner("Analisando..."):
                st.markdown(gerar_diagnostico_barreiras(api_key, aluno, obs_aee))

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
            with st.spinner("Criando experiências..."):
                atividades = gerar_projetos_ei_bncc(api_key, aluno, campo_bncc)
                st.markdown(atividades)

    # 3. ROTINA (EI)
    with tab_rotina:
        st.markdown("<div class='pedagogia-box'><strong>Adaptação de Rotina:</strong> Recursos visuais e sensoriais para a creche/pré-escola.</div>", unsafe_allow_html=True)
        dif_rotina = st.text_input("Dificuldade na Rotina:", placeholder="Ex: Hora do soninho, Desfralde, Alimentação")
        if st.button("Sugerir Adaptação", type="primary"):
            with st.spinner("Buscando recursos..."):
                st.markdown(sugerir_tecnologia_assistiva(api_key, aluno, f"Rotina EI: {dif_rotina}"))

else:
    # --- ABAS PADRÃO (FUNDAMENTAL / MÉDIO) ---
    tab_barreiras, tab_plano, tab_tec, tab_ponte = st.tabs([
        "🔍 Mapear Barreiras", 
        "🎯 Plano de Habilidades", 
        "🛠️ Tec. Assistiva", 
        "🌉 Cronograma & Articulação"
    ])

    # 1. BARREIRAS
    with tab_barreiras:
        st.markdown("<div class='pedagogia-box'><strong>Diagnóstico de Acessibilidade:</strong> Identifique o que impede o aluno de participar, não a doença.</div>", unsafe_allow_html=True)
        obs_aee = st.text_area("Observações Iniciais do AEE (Opcional):", placeholder="Ex: O aluno se recusa a escrever...", height=100)
        if st.button("Analisar Barreiras via IA", type="primary"):
            if not api_key: st.error("Insira a chave OpenAI."); st.stop()
            with st.spinner("Analisando..."):
                st.markdown(gerar_diagnostico_barreiras(api_key, aluno, obs_aee))

    # 2. PLANO
    with tab_plano:
        st.markdown("<div class='pedagogia-box'><strong>Treino de Habilidades:</strong> Desenvolvimento cognitivo, motor e social.</div>", unsafe_allow_html=True)
        foco = st.selectbox("Foco do atendimento:", ["Funções Executivas", "Autonomia", "Coordenação Motora", "Comunicação", "Habilidades Sociais"])
        if st.button("Gerar Plano", type="primary"):
            with st.spinner("Planejando..."):
                st.markdown(gerar_plano_habilidades(api_key, aluno, foco))

    # 3. T.A.
    with tab_tec:
        st.markdown("<div class='pedagogia-box'><strong>Tecnologia Assistiva:</strong> Recursos para autonomia.</div>", unsafe_allow_html=True)
        dif_especifica = st.text_input("Dificuldade Específica:", placeholder="Ex: Não segura o lápis")
        if st.button("Sugerir Recursos", type="primary"):
            with st.spinner("Buscando T.A..."):
                st.markdown(sugerir_tecnologia_assistiva(api_key, aluno, dif_especifica))

# 4. ARTICULAÇÃO (COMUM A TODOS)
with tab_ponte:
    st.markdown("<div class='pedagogia-box'><strong>Ponte com a Sala Regular:</strong> Documento de colaboração com os professores.</div>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    freq = c1.selectbox("Frequência:", ["1x/sem", "2x/sem", "3x/sem", "Diário"])
    turno = c2.selectbox("Turno:", ["Manhã", "Tarde"])
    acoes_resumo = st.text_area("Trabalho no AEE:", placeholder="Ex: Comunicação alternativa...", height=70)
    if st.button("Gerar Carta", type="primary"):
        with st.spinner("Escrevendo..."):
            carta = gerar_documento_articulacao(api_key, aluno, f"{freq} ({turno})", acoes_resumo)
            st.markdown("### 📄 Documento Gerado")
            st.markdown(carta)
            st.download_button("📥 Baixar Carta", carta, "Carta_Articulacao.txt")
