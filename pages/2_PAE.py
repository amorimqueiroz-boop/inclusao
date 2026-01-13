import streamlit as st
import os
from openai import OpenAI
import json
import pandas as pd
from datetime import date
import base64  # <--- Adicionado para processar a imagem no HTML

# ==============================================================================
# 1. CONFIGURAÇÃO E SEGURANÇA
# ==============================================================================
st.set_page_config(page_title="Omnisfera | PAE", page_icon="🧩", layout="wide")

def verificar_acesso():
    if "autenticado" not in st.session_state or not st.session_state["autenticado"]:
        st.error("🔒 Acesso Negado. Por favor, faça login na Página Inicial.")
        st.stop()
    
    st.markdown("""
        <style>
            [data-testid="stHeader"] {visibility: hidden !important; height: 0px !important;}
            .block-container {padding-top: 1rem !important;}
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
# 2. SISTEMA PAE (Plano de Atendimento Educacional Especializado)
# ==============================================================================

# --- BANCO DE DADOS (Leitura do PEI) ---
ARQUIVO_DB = "banco_alunos.json"

def carregar_banco():
    if os.path.exists(ARQUIVO_DB):
        try:
            with open(ARQUIVO_DB, "r", encoding="utf-8") as f:
                return json.load(f)
        except: return []
    return []

if 'banco_estudantes' not in st.session_state or not st.session_state.banco_estudantes:
    st.session_state.banco_estudantes = carregar_banco()

# --- CSS PERSONALIZADO ---
st.markdown("""
    <style>
    /* Ajustei o header-pae para centralizar o conteúdo verticalmente */
    .header-pae { 
        background: white; 
        padding: 20px; 
        border-radius: 12px; 
        border-left: 6px solid #805AD5; 
        box-shadow: 0 2px 4px rgba(0,0,0,0.05); 
        margin-bottom: 20px; 
        display: flex; 
        flex-direction: column; /* Organiza logo em cima, subtítulo embaixo */
        align-items: center; 
        justify-content: center;
        text-align: center;
        gap: 10px;
    }
    .student-header { background-color: #F3E8FF; border: 1px solid #D6BCFA; border-radius: 10px; padding: 15px; margin-bottom: 20px; display: flex; justify-content: space-between; }
    .student-label { font-size: 0.8rem; color: #553C9A; font-weight: 700; text-transform: uppercase; }
    .student-value { font-size: 1.1rem; color: #44337A; font-weight: 800; }
    .pae-card { background-color: white; border: 1px solid #E2E8F0; border-radius: 8px; padding: 15px; margin-bottom: 10px; }
    .pae-title { color: #805AD5; font-weight: bold; font-size: 1.1rem; margin-bottom: 5px; }
    
    div[data-testid="column"] .stButton button[kind="primary"] { background-color: #805AD5 !important; border: none !important; color: white !important; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# --- CABEÇALHO (LOGO PAE + SUBTÍTULO NO BANNER) ---
# Função auxiliar para carregar imagem local dentro do HTML
def get_img_tag(file_path, width):
    if os.path.exists(file_path):
        with open(file_path, "rb") as f:
            data = base64.b64encode(f.read()).decode("utf-8")
        return f'<img src="data:image/png;base64,{data}" width="{width}">'
    return "🧩" # Fallback se a imagem não existir

img_html = get_img_tag("pae.png", "350") # Logo grande (350px)

st.markdown(f"""
    <div class="header-pae">
        {img_html}
        <p style="margin:0; color:#666; font-size: 1.2rem; font-weight: 500;">
            Sala de Recursos & Eliminação de Barreiras
        </p>
    </div>
""", unsafe_allow_html=True)


if not st.session_state.banco_estudantes:
    st.warning("⚠️ Nenhum aluno com PEI encontrado. Cadastre no módulo PEI primeiro.")
    st.stop()

# --- SELEÇÃO DE ALUNO ---
lista_alunos = [a['nome'] for a in st.session_state.banco_estudantes]
col_sel, col_info = st.columns([1, 2])
with col_sel:
    nome_aluno = st.selectbox("📂 Selecione o Estudante:", lista_alunos)

aluno = next(a for a in st.session_state.banco_estudantes if a['nome'] == nome_aluno)

# Exibe Resumo do PEI (A "Alimentação Inicial")
st.markdown(f"""
    <div class="student-header">
        <div><div class="student-label">Nome</div><div class="student-value">{aluno.get('nome')}</div></div>
        <div><div class="student-label">Série</div><div class="student-value">{aluno.get('serie', '-')}</div></div>
        <div><div class="student-label">Hiperfoco</div><div class="student-value">{aluno.get('hiperfoco', '-')}</div></div>
    </div>
""", unsafe_allow_html=True)

with st.expander("📄 Ver Resumo do PEI (Base para o PAE)", expanded=False):
    st.info(aluno.get('ia_sugestao', 'Nenhum dado de PEI processado ainda.'))

# --- GESTÃO DE CHAVES ---
if 'OPENAI_API_KEY' in st.secrets: api_key = st.secrets['OPENAI_API_KEY']
else: api_key = st.sidebar.text_input("Chave OpenAI:", type="password")

# --- FUNÇÕES DE IA DO PAE ---
def gerar_diagnostico_barreiras(api_key, aluno, obs_prof):
    client = OpenAI(api_key=api_key)
    prompt = f"""
    ATUAR COMO: Especialista em AEE (Atendimento Educacional Especializado).
    OBJETIVO: Analisar o PEI do aluno e o relato do professor para mapear BARREIRAS (não deficiências).
    
    ALUNO: {aluno['nome']} | HIPERFOCO: {aluno.get('hiperfoco')}
    RESUMO PEI: {aluno.get('ia_sugestao', '')[:1000]}
    OBSERVAÇÃO ATUAL DO PROFESSOR AEE: {obs_prof}
    
    CLASSIFIQUE AS BARREIRAS ENCONTRADAS (Lei Brasileira de Inclusão):
    1. **Barreiras Comunicacionais:** (Ex: falta de Libras, escrita, comunicação alternativa)
    2. **Barreiras Metodológicas:** (Ex: métodos de ensino que não atingem o aluno)
    3. **Barreiras Atitudinais:** (Ex: isolamento, bullying, descrença da capacidade)
    4. **Barreiras Tecnológicas/Instrumentais:** (Ex: falta de engrossador, material adaptado)
    
    SAÍDA: Tabela Markdown clara e direta.
    """
    try:
        resp = client.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "user", "content": prompt}], temperature=0.5)
        return resp.choices[0].message.content
    except Exception as e: return f"Erro: {str(e)}"

def gerar_plano_habilidades(api_key, aluno, foco_treino):
    client = OpenAI(api_key=api_key)
    prompt = f"""
    CRIE UM PLANO DE INTERVENÇÃO PARA SALA DE RECURSOS (AEE).
    FOCO: Desenvolvimento de Habilidades (Não reforço escolar).
    ÁREA DO TREINO: {foco_treino}
    
    ALUNO: {aluno['nome']}
    HIPERFOCO: {aluno.get('hiperfoco')} (USE O HIPERFOCO COMO ESTRATÉGIA DE ENGAJAMENTO).
    
    GERE 3 METAS SMART:
    1. **Meta de Longo Prazo:** (O que queremos em 6 meses?)
    2. **Estratégia com Hiperfoco:** (Como usar {aluno.get('hiperfoco')} para treinar isso?)
    3. **Recurso Necessário:** (O que construir ou usar?)
    """
    try:
        resp = client.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "user", "content": prompt}], temperature=0.7)
        return resp.choices[0].message.content
    except Exception as e: return str(e)

def sugerir_tecnologia_assistiva(api_key, aluno, dificuldade):
    client = OpenAI(api_key=api_key)
    prompt = f"""
    SUGESTÃO DE TECNOLOGIA ASSISTIVA E RECURSOS.
    Aluno: {aluno['nome']}. Dificuldade Específica relatada: {dificuldade}.
    
    Sugira 3 Níveis de Solução:
    1. **Baixa Tecnologia (DIY):** Algo que o professor pode fazer com papelão, velcro, garrafa PET.
    2. **Média Tecnologia:** Materiais pedagógicos estruturados ou adaptações físicas simples.
    3. **Alta Tecnologia:** Apps, softwares ou hardware específico.
    """
    try:
        resp = client.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "user", "content": prompt}], temperature=0.7)
        return resp.choices[0].message.content
    except Exception as e: return str(e)

def gerar_documento_articulacao(api_key, aluno, frequencia, acoes):
    client = OpenAI(api_key=api_key)
    prompt = f"""
    ESCREVA UMA CARTA DE ARTICULAÇÃO (AEE -> SALA REGULAR).
    De: Professor do AEE.
    Para: Professores da Sala Regular.
    Aluno: {aluno['nome']}.
    
    Conteúdo:
    - Informe que o aluno será atendido {frequencia}.
    - Explique que no AEE estamos trabalhando: {acoes}.
    - Dê 3 dicas práticas de como o professor da sala regular pode ajudar a generalizar essas conquistas na aula dele.
    - Tom: Colaborativo, profissional e parceiro.
    """
    try:
        resp = client.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "user", "content": prompt}], temperature=0.7)
        return resp.choices[0].message.content
    except Exception as e: return str(e)

# --- ABAS DO PAE ---
tab_barreiras, tab_plano, tab_tec, tab_ponte = st.tabs([
    "🔍 Mapear Barreiras", 
    "🎯 Plano de Habilidades", 
    "🛠️ Tec. Assistiva", 
    "🌉 Cronograma & Articulação"
])

# 1. BARREIRAS (Diagnóstico)
with tab_barreiras:
    st.write("### 🔍 Diagnóstico de Acessibilidade")
    st.info("O PAE começa identificando o que impede o aluno de participar, não a doença dele.")
    
    obs_aee = st.text_area("Observações Iniciais do AEE (Opcional):", placeholder="Ex: O aluno se recusa a escrever, mas fala muito sobre dinossauros. Tem dificuldade motora fina.", height=100)
    
    if st.button("Analisar Barreiras via IA", type="primary"):
        if not api_key: st.error("Insira a chave OpenAI."); st.stop()
        with st.spinner("Cruzando dados do PEI com Observações..."):
            res_barreiras = gerar_diagnostico_barreiras(api_key, aluno, obs_aee)
            st.markdown(res_barreiras)

# 2. PLANO DE HABILIDADES (Treino)
with tab_plano:
    st.write("### 🎯 Treino de Habilidades (Não Curricular)")
    st.info(f"Vamos usar o hiperfoco **({aluno.get('hiperfoco')})** para desenvolver funções mentais superiores.")
    
    foco = st.selectbox("Qual o foco do atendimento agora?", 
        ["Funções Executivas (Atenção/Memória)", "Autonomia e AVDs", "Coordenação Motora", "Comunicação Alternativa", "Habilidades Sociais"])
    
    if st.button("Gerar Plano de Intervenção", type="primary"):
        with st.spinner("Criando estratégias engajadoras..."):
            res_plano = gerar_plano_habilidades(api_key, aluno, foco)
            st.markdown(res_plano)

# 3. TECNOLOGIA ASSISTIVA
with tab_tec:
    st.write("### 🛠️ Caixa de Ferramentas")
    dif_especifica = st.text_input("Qual a dificuldade específica a ser superada?", placeholder="Ex: Não consegue segurar o lápis / Não consegue ler textos longos")
    
    if st.button("Sugerir Recursos", type="primary"):
        with st.spinner("Buscando soluções no banco de dados de TA..."):
            res_ta = sugerir_tecnologia_assistiva(api_key, aluno, dif_especifica)
            st.markdown(res_ta)

# 4. ARTICULAÇÃO (A Ponte)
with tab_ponte:
    st.write("### 🌉 A Ponte com a Sala Regular")
    c1, c2 = st.columns(2)
    freq = c1.selectbox("Frequência do Atendimento:", ["1x por semana", "2x por semana", "3x por semana", "Diário"])
    turno = c2.selectbox("Turno:", ["Contraturno Manhã", "Contraturno Tarde"])
    
    acoes_resumo = st.text_area("O que está sendo trabalhado no AEE?", placeholder="Ex: Uso de prancha de comunicação e treino de foco.", height=70)
    
    if st.button("Gerar Carta de Articulação", type="primary"):
        with st.spinner("Redigindo documento oficial..."):
            carta = gerar_documento_articulacao(api_key, aluno, f"{freq} ({turno})", acoes_resumo)
            st.markdown("### 📄 Documento Gerado")
            st.markdown(carta)
            st.download_button("📥 Baixar Carta (.txt)", carta, "Carta_Articulacao.txt")
