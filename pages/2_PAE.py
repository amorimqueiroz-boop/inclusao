# ARQUIVO: pages/2_PAE.py
import streamlit as st
import omni_utils as core
# ... imports ...

st.set_page_config(page_title="PAEE", layout="wide")

# AQUI: Define logo da sidebar (pae.png) e DESLIGA a logo fixa do topo (False)
core.aplicar_estilo_global(logo_pagina="pae.png", exibir_header_global=False)

if not core.verificar_acesso(): st.stop()

# Agora usamos o Card Personalizado como cabeçalho
core.renderizar_header_padrao(
    titulo="PAEE & T.A.",
    subtitulo="Plano de Atendimento Educacional Especializado",
    nome_arquivo_imagem="pae.png",
    cor_destaque="#805AD5"
)

# ==============================================================================
# 1. CONFIGURAÇÃO E INICIALIZAÇÃO DA MATRIZ
# ==============================================================================
st.set_page_config(
    page_title="PAEE & T.A.", 
    page_icon="🧩", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

# Aplica o estilo global e define a logo da sidebar para esta página
core.aplicar_estilo_global(logo_pagina="pae.png")

# Verifica se o usuário está logado
if not core.verificar_acesso():
    st.stop()

# ==============================================================================
# 2. CABEÇALHO DA PÁGINA (VISUAL NOVO PADRONIZADO)
# ==============================================================================
core.renderizar_header_padrao(
    titulo="PAEE & T.A.",
    subtitulo="Plano de Atendimento Educacional Especializado e Sala de Recursos.",
    nome_arquivo_imagem="pae.png",
    cor_destaque="#805AD5"  # Roxo
)

# ==============================================================================
# 3. LÓGICA DE DADOS (BANCO DE ALUNOS)
# ==============================================================================
ARQUIVO_DB = "banco_alunos.json"

def carregar_banco():
    usuario_atual = st.session_state.get("usuario_nome", "")
    if os.path.exists(ARQUIVO_DB):
        try:
            with open(ARQUIVO_DB, "r", encoding="utf-8") as f:
                todos_alunos = json.load(f)
                # Filtra alunos do usuário logado
                meus_alunos = [
                    aluno for aluno in todos_alunos 
                    if aluno.get('responsavel') == usuario_atual
                ]
                return meus_alunos
        except: return []
    return []

# Inicializa o banco na sessão se não existir
if 'banco_estudantes' not in st.session_state or not st.session_state.banco_estudantes:
    st.session_state.banco_estudantes = carregar_banco()

# Se não tiver alunos, avisa e para
if not st.session_state.banco_estudantes:
    st.warning("⚠️ Nenhum aluno encontrado para o seu usuário. Cadastre no módulo PEI primeiro.")
    st.stop()

# ==============================================================================
# 4. SELEÇÃO E INFO DO ALUNO
# ==============================================================================
lista_alunos = [a['nome'] for a in st.session_state.banco_estudantes]

col_sel, col_vazia = st.columns([1, 2])
with col_sel:
    nome_aluno = st.selectbox("📂 Selecione o Estudante:", lista_alunos)

# Recupera o objeto aluno selecionado
aluno = next(a for a in st.session_state.banco_estudantes if a['nome'] == nome_aluno)

# CSS Específico para o Card do Aluno (Fundo Roxo Claro)
st.markdown("""
<style>
    .student-header { 
        background-color: #F3E8FF; 
        border: 1px solid #D6BCFA; 
        border-radius: 12px; 
        padding: 20px; 
        margin-bottom: 25px; 
        display: flex; 
        justify-content: space-between;
        align-items: center;
        box-shadow: 0 2px 5px rgba(0,0,0,0.02);
    }
    .student-info-box { text-align: left; }
    .student-label { font-size: 0.75rem; color: #6B46C1; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 2px; }
    .student-value { font-size: 1.1rem; color: #44337A; font-weight: 800; }
    
    /* Ajuste visual para botões roxos (PAEE) */
    div[data-testid="column"] .stButton button[kind="primary"] { 
        background-color: #805AD5 !important; 
        border-color: #805AD5 !important; 
        color: white !important; 
        font-weight: 700;
        border-radius: 10px;
    }
    div[data-testid="column"] .stButton button[kind="primary"]:hover {
        background-color: #6B46C1 !important;
        box-shadow: 0 4px 12px rgba(128, 90, 213, 0.3);
    }
</style>
""", unsafe_allow_html=True)

# Renderiza Card do Aluno
st.markdown(f"""
    <div class="student-header">
        <div class="student-info-box">
            <div class="student-label">Nome Completo</div>
            <div class="student-value">{aluno.get('nome')}</div>
        </div>
        <div class="student-info-box">
            <div class="student-label">Série / Ano</div>
            <div class="student-value">{aluno.get('serie', '-')}</div>
        </div>
        <div class="student-info-box">
            <div class="student-label">Hiperfoco / Interesse</div>
            <div class="student-value">{aluno.get('hiperfoco', '-')}</div>
        </div>
    </div>
""", unsafe_allow_html=True)

# Lógica Educação Infantil
serie_aluno = aluno.get('serie', '').lower()
is_ei = "infantil" in serie_aluno or "creche" in serie_aluno or "pré" in serie_aluno

if is_ei:
    st.info("🧸 **Modo Educação Infantil Ativado:** Foco em Campos de Experiência (BNCC) e Brincar Heurístico.")

# Expander com Resumo do PEI
with st.expander("📄 Ver Resumo do PEI (Base para o PAEE)", expanded=False):
    st.info(aluno.get('ia_sugestao', 'Nenhum dado de PEI processado ainda.'))

# ==============================================================================
# 5. INTELIGÊNCIA ARTIFICIAL (FUNÇÕES)
# ==============================================================================
# Gestão de Chave API
if 'OPENAI_API_KEY' in st.secrets: 
    api_key = st.secrets['OPENAI_API_KEY']
else: 
    api_key = st.text_input("Chave OpenAI:", type="password")

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
# 6. INTERFACE DE ABAS (FLUXO DE TRABALHO)
# ==============================================================================

if is_ei:
    # --- ABAS EDUCAÇÃO INFANTIL ---
    tab_barreiras, tab_projetos, tab_rotina, tab_ponte = st.tabs([
        "🔍 Barreiras no Brincar", 
        "🧸 Banco de Experiências", 
        "🏠 Rotina & Adaptação", 
        "🌉 Articulação"
    ])
    
    # 1. BARREIRAS (EI)
    with tab_barreiras:
        st.markdown("#### 🔍 Diagnóstico do Brincar (EI)")
        st.caption("Na Educação Infantil, a barreira não é 'não escrever', mas sim 'não participar da interação'.")
        obs_aee = st.text_area("Observação do Brincar:", placeholder="Ex: Isola-se no parquinho, não aceita texturas...", height=100)
        if st.button("Mapear Barreiras do Brincar", type="primary"):
            if not api_key: st.error("Insira a chave OpenAI."); st.stop()
            with st.spinner("Analisando..."):
                st.markdown(gerar_diagnostico_barreiras(api_key, aluno, obs_aee))

    # 2. PROJETOS (EI)
    with tab_projetos:
        st.markdown("#### 🧸 Banco de Experiências (BNCC)")
        
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
        st.markdown("#### 🏠 Adaptação de Rotina e AVDs")
        st.write("Recursos visuais e sensoriais para a rotina da creche/pré-escola.")
        dif_rotina = st.text_input("Dificuldade na Rotina:", placeholder="Ex: Hora do soninho, Desfralde, Alimentação")
        if st.button("Sugerir Adaptação", type="primary"):
            with st.spinner("Buscando recursos..."):
                st.markdown(sugerir_tecnologia_assistiva(api_key, aluno, f"Rotina EI: {dif_rotina}"))

else:
    # --- ABAS FUNDAMENTAL / MÉDIO ---
    tab_barreiras, tab_plano, tab_tec, tab_ponte = st.tabs([
        "🔍 Mapear Barreiras", 
        "🎯 Plano de Habilidades", 
        "🛠️ Tec. Assistiva", 
        "🌉 Cronograma & Articulação"
    ])

    # 1. BARREIRAS
    with tab_barreiras:
        st.markdown("#### 🔍 Diagnóstico de Acessibilidade")
        st.caption("O PAEE começa identificando o que impede o aluno de participar, não a doença dele.")
        obs_aee = st.text_area("Observações Iniciais do AEE (Opcional):", placeholder="Ex: O aluno se recusa a escrever...", height=100)
        if st.button("Analisar Barreiras via IA", type="primary"):
            if not api_key: st.error("Insira a chave OpenAI."); st.stop()
            with st.spinner("Analisando..."):
                st.markdown(gerar_diagnostico_barreiras(api_key, aluno, obs_aee))

    # 2. PLANO
    with tab_plano:
        st.markdown("#### 🎯 Treino de Habilidades")
        foco = st.selectbox("Foco do atendimento:", ["Funções Executivas", "Autonomia", "Coordenação Motora", "Comunicação", "Habilidades Sociais"])
        if st.button("Gerar Plano", type="primary"):
            with st.spinner("Planejando..."):
                st.markdown(gerar_plano_habilidades(api_key, aluno, foco))

    # 3. T.A.
    with tab_tec:
        st.markdown("#### 🛠️ Tecnologia Assistiva")
        dif_especifica = st.text_input("Dificuldade Específica:", placeholder="Ex: Não segura o lápis")
        if st.button("Sugerir Recursos", type="primary"):
            with st.spinner("Buscando T.A..."):
                st.markdown(sugerir_tecnologia_assistiva(api_key, aluno, dif_especifica))

# 4. ARTICULAÇÃO (COMUM)
with tab_ponte:
    st.markdown("#### 🌉 Ponte com a Sala Regular")
    c1, c2 = st.columns(2)
    with c1: freq = st.selectbox("Frequência:", ["1x/sem", "2x/sem", "3x/sem", "Diário"])
    with c2: turno = st.selectbox("Turno:", ["Manhã", "Tarde"])
    
    acoes_resumo = st.text_area("Trabalho no AEE:", placeholder="Ex: Comunicação alternativa...", height=70)
    
    if st.button("Gerar Carta de Articulação", type="primary"):
        with st.spinner("Escrevendo..."):
            carta = gerar_documento_articulacao(api_key, aluno, f"{freq} ({turno})", acoes_resumo)
            st.markdown("### 📄 Documento Gerado")
            st.markdown(carta)
            st.download_button("📥 Baixar Carta", carta, "Carta_Articulacao.txt")
