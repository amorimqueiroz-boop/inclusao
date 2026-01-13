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
    page_title="[TESTE] Omnisfera | PAEE", 
    page_icon="🛠️", 
    layout="wide",
    initial_sidebar_state="expanded"
)

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
    /* --- AJUSTE CRÍTICO: MENU LATERAL VISÍVEL --- */
    
    /* 1. Header principal transparente (permite ver o botão da sidebar) */
    header[data-testid="stHeader"] {{
        background-color: transparent !important;
        z-index: 9999 !important; /* Garante que fique acessível */
    }}
    
    /* 2. Esconde APENAS a barra de ferramentas da direita (Share, Deploy, etc) */
    [data-testid="stToolbar"] {{
        visibility: hidden !important;
        display: none !important;
    }}
    
    /* 3. Garante que o botão de abrir/fechar a sidebar esteja visível e clicável */
    [data-testid="stSidebarCollapsedControl"] {{
        visibility: visible !important;
        display: block !important;
        color: #2D3748 !important; /* Cor do ícone */
    }}
    
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
        </style>
    """, unsafe_allow_html=True)

verificar_acesso()

# --- BARRA LATERAL ---
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
# 2. SISTEMA PAEE (Plano de Atendimento Educacional Especializado)
# ==============================================================================

ARQUIVO_DB = "banco_alunos.json"

def carregar_banco():
    usuario_atual = st.session_state.get("usuario_nome", "")
    if os.path.exists(ARQUIVO_DB):
        try:
            with open(ARQUIVO_DB, "r", encoding="utf-8") as f:
                todos_alunos = json.load(f)
                meus_alunos = [
                    aluno for aluno in todos_alunos 
                    if aluno.get('responsavel') == usuario_atual
                ]
                return meus_alunos
        except: return []
    return []

if 'banco_estudantes' not in st.session_state or not st.session_state.banco_estudantes:
    st.session_state.banco_estudantes = carregar_banco()

# --- CSS PERSONALIZADO ---
st.markdown("""
    <style>
    .header-paee { 
        background: white; padding: 15px 25px; border-radius: 12px; 
        border-left: 6px solid #805AD5; box-shadow: 0 2px 4px rgba(0,0,0,0.05); 
        margin-bottom: 20px; margin-top: 10px; display: flex; align-items: center; gap: 20px; 
    }
    .student-header { background-color: #F3E8FF; border: 1px solid #D6BCFA; border-radius: 10px; padding: 15px; margin-bottom: 20px; display: flex; justify-content: space-between; }
    .student-label { font-size: 0.8rem; color: #553C9A; font-weight: 700; text-transform: uppercase; }
    .student-value { font-size: 1.1rem; color: #44337A; font-weight: 800; }
    div[data-testid="column"] .stButton button[kind="primary"] { background-color: #805AD5 !important; border: none !important; color: white !important; font-weight: bold; }
    
    /* CARD DE PROJETO EI */
    .ei-card { border: 2px dashed #F6E05E; background-color: #FFFFF0; padding: 15px; border-radius: 10px; margin-bottom: 10px; }
    </style>
""", unsafe_allow_html=True)

def get_img_tag(file_path, width):
    if os.path.exists(file_path):
        with open(file_path, "rb") as f:
            data = base64.b64encode(f.read()).decode("utf-8")
        return f'<img src="data:image/png;base64,{data}" width="{width}">'
    return "🧩"

img_html = get_img_tag("pae.png", "160") 

st.markdown(f"""
    <div class="header-paee">
        <div style="flex-shrink: 0;"> {img_html} </div>
        <div style="flex-grow: 1; text-align: center;"> 
            <p style="margin:0; color:#44337A; font-size: 1.4rem; font-weight: 600;">
                Sala de Recursos & Eliminação de Barreiras
            </p>
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
# Lógica para verificar se é criança pequena
serie_aluno = aluno.get('serie', '').lower()
is_ei = "infantil" in serie_aluno or "creche" in serie_aluno or "pré" in serie_aluno

# Exibe Resumo do PEI
st.markdown(f"""
    <div class="student-header">
        <div><div class="student-label">Nome</div><div class="student-value">{aluno.get('nome')}</div></div>
        <div><div class="student-label">Série</div><div class="student-value">{aluno.get('serie', '-')}</div></div>
        <div><div class="student-label">Hiperfoco</div><div class="student-value">{aluno.get('hiperfoco', '-')}</div></div>
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

# --- NOVA FUNÇÃO: GERADOR DE PROJETOS EI (BNCC) ---
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
        st.write("### 🔍 Diagnóstico do Brincar (EI)")
        st.caption("Na Educação Infantil, a barreira não é 'não escrever', mas sim 'não participar da interação'.")
        obs_aee = st.text_area("Observação do Brincar:", placeholder="Ex: Isola-se no parquinho, não aceita texturas...", height=100)
        if st.button("Mapear Barreiras do Brincar", type="primary"):
            if not api_key: st.error("Insira a chave OpenAI."); st.stop()
            with st.spinner("Analisando..."):
                st.markdown(gerar_diagnostico_barreiras(api_key, aluno, obs_aee))

    # 2. PROJETOS (EI) - NOVIDADE!
    with tab_projetos:
        st.write("### 🧸 Banco de Experiências (BNCC)")
        st.info(f"Hiperfoco para engajamento: **{aluno.get('hiperfoco')}**")
        
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
        st.write("### 🏠 Adaptação de Rotina e AVDs")
        st.write("Recursos visuais e sensoriais para a rotina da creche/pré-escola.")
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
        st.write("### 🔍 Diagnóstico de Acessibilidade")
        st.info("O PAEE começa identificando o que impede o aluno de participar, não a doença dele.")
        obs_aee = st.text_area("Observações Iniciais do AEE (Opcional):", placeholder="Ex: O aluno se recusa a escrever...", height=100)
        if st.button("Analisar Barreiras via IA", type="primary"):
            if not api_key: st.error("Insira a chave OpenAI."); st.stop()
            with st.spinner("Analisando..."):
                st.markdown(gerar_diagnostico_barreiras(api_key, aluno, obs_aee))

    # 2. PLANO
    with tab_plano:
        st.write("### 🎯 Treino de Habilidades")
        st.info(f"Hiperfoco Ativo: **{aluno.get('hiperfoco')}**")
        foco = st.selectbox("Foco do atendimento:", ["Funções Executivas", "Autonomia", "Coordenação Motora", "Comunicação", "Habilidades Sociais"])
        if st.button("Gerar Plano", type="primary"):
            with st.spinner("Planejando..."):
                st.markdown(gerar_plano_habilidades(api_key, aluno, foco))

    # 3. T.A.
    with tab_tec:
        st.write("### 🛠️ Tecnologia Assistiva")
        dif_especifica = st.text_input("Dificuldade Específica:", placeholder="Ex: Não segura o lápis")
        if st.button("Sugerir Recursos", type="primary"):
            with st.spinner("Buscando T.A..."):
                st.markdown(sugerir_tecnologia_assistiva(api_key, aluno, dif_especifica))

# 4. ARTICULAÇÃO (COMUM A TODOS)
with tab_ponte:
    st.write("### 🌉 Ponte com a Sala Regular")
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
