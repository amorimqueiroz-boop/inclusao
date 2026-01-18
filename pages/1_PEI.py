# 1_PEI.py - SISTEMA COMPLETO DE CRIAÇÃO DE PEI
"""
PLANO DE ENSINO INDIVIDUALIZADO (PEI) 360°
Sistema unificado usando apenas Google Sheets
"""

# ==============================================================================
# 1. IMPORTAR BIBLIOTECAS (TODAS NECESSÁRIAS)
# ==============================================================================
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
import random

# Importar nosso sistema de banco de dados
from db_google_sheets import (
    carregar_alunos_usuario,
    salvar_aluno,
    excluir_aluno,
    salvar_metas_pei,
    inicializar_sistema
)

# ==============================================================================
# 2. CONFIGURAÇÃO DA PÁGINA
# ==============================================================================
st.set_page_config(
    page_title="Omnisfera | PEI 360°",
    page_icon="🧩",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==============================================================================
# 3. INICIALIZAR SISTEMA E VERIFICAR LOGIN
# ==============================================================================
def verificar_login():
    """Verifica se usuário está logado"""
    if "autenticado" not in st.session_state or not st.session_state["autenticado"]:
        # Mostrar tela de login simplificada
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("""
            <div style="text-align: center; padding: 50px;">
                <h1>🔒 Omnisfera PEI</h1>
                <p>Faça login para continuar</p>
            </div>
            """, unsafe_allow_html=True)
            
            nome = st.text_input("Seu nome")
            senha = st.text_input("Senha", type="password")
            
            if st.button("Entrar", type="primary", use_container_width=True):
                # Senha temporária para teste
                if senha == "1234":
                    st.session_state["autenticado"] = True
                    st.session_state["usuario_nome"] = nome
                    st.session_state["usuario_cargo"] = "Professor"
                    st.rerun()
                else:
                    st.error("Senha incorreta. Use '1234' para teste.")
        
        st.stop()  # Para o resto da aplicação
    else:
        # Se já está logado, inicializar sistema
        inicializar_sistema()

# Chama a verificação
verificar_login()

# ==============================================================================
# 4. CONFIGURAÇÃO VISUAL (CSS E ESTILOS)
# ==============================================================================
def aplicar_estilos():
    """Aplica todos os estilos CSS da página"""
    st.markdown("""
    <style>
    /* Fonte principal */
    @import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Nunito', sans-serif;
        color: #2D3748;
        background-color: #F7FAFC;
    }
    
    /* Container principal */
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 3rem !important;
    }
    
    /* Cabeçalho bonito */
    .header-principal {
        background: linear-gradient(135deg, #0F52BA 0%, #062B61 100%);
        border-radius: 16px;
        padding: 25px 40px;
        color: white;
        margin-bottom: 25px;
        display: flex;
        align-items: center;
        gap: 20px;
        box-shadow: 0 4px 12px rgba(15, 82, 186, 0.15);
    }
    
    /* Cartões informativos */
    .card-info {
        background-color: white;
        border-radius: 12px;
        padding: 20px;
        border: 1px solid #E2E8F0;
        margin-bottom: 20px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.02);
    }
    
    .card-info h3 {
        color: #2C5282;
        margin-top: 0;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    
    /* Abas personalizadas */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: #F1F5F9;
        padding: 8px;
        border-radius: 10px;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px !important;
        background-color: white !important;
        border: 1px solid #E2E8F0 !important;
        font-weight: 700 !important;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #0F52BA !important;
        color: white !important;
        border-color: #0F52BA !important;
    }
    
    /* Botões */
    .stButton button {
        border-radius: 8px !important;
        font-weight: 700 !important;
    }
    
    .stButton button[kind="primary"] {
        background-color: #0F52BA !important;
        color: white !important;
        border: none !important;
    }
    
    /* Inputs */
    .stTextInput input, .stTextArea textarea {
        border-radius: 8px !important;
        border: 1px solid #E2E8F0 !important;
    }
    
    /* Barra de progresso */
    .barra-progresso {
        height: 8px;
        background-color: #E2E8F0;
        border-radius: 4px;
        margin: 20px 0;
        overflow: hidden;
    }
    
    .barra-preenchida {
        height: 100%;
        border-radius: 4px;
        background: linear-gradient(90deg, #0F52BA, #4C8BF5);
        transition: width 0.5s ease;
    }
    
    /* Indicador de etapa */
    .etapa-ativa {
        background-color: #0F52BA;
        color: white;
        padding: 5px 15px;
        border-radius: 20px;
        font-weight: bold;
        font-size: 0.9rem;
    }
    
    .etapa-inativa {
        background-color: #E2E8F0;
        color: #718096;
        padding: 5px 15px;
        border-radius: 20px;
        font-size: 0.9rem;
    }
    </style>
    """, unsafe_allow_html=True)

# Aplica os estilos
aplicar_estilos()

# ==============================================================================
# 5. LISTAS DE DADOS PARA OS FORMULÁRIOS
# ==============================================================================
LISTA_SERIES = [
    "Educação Infantil (Creche)", 
    "Educação Infantil (Pré-Escola)", 
    "1º Ano (Fund. I)", 
    "2º Ano (Fund. I)", 
    "3º Ano (Fund. I)", 
    "4º Ano (Fund. I)", 
    "5º Ano (Fund. I)", 
    "6º Ano (Fund. II)", 
    "7º Ano (Fund. II)", 
    "8º Ano (Fund. II)", 
    "9º Ano (Fund. II)", 
    "1ª Série (EM)", 
    "2ª Série (EM)", 
    "3ª Série (EM)", 
    "EJA (Educação de Jovens e Adultos)"
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
    "Funções Cognitivas": ["🎯 Atenção Sustentada", "🧠 Memória de Trabalho", "🔄 Flexibilidade Mental", "📅 Planejamento", "⚡ Velocidade de Processamento"],
    "Comunicação": ["🗣️ Linguagem Expressiva", "👂 Linguagem Receptiva", "💬 Pragmática", "🎧 Processamento Auditivo"],
    "Socioemocional": ["😡 Regulação Emocional", "⛔ Tolerância à Frustração", "🤝 Interação Social", "🪞 Autoestima"],
    "Sensorial e Motor": ["🏃 Praxias Globais", "✍️ Praxias Finas", "🔊 Hipersensibilidade", "🔍 Hipossensibilidade"],
    "Acadêmico": ["📖 Decodificação Leitora", "📜 Compreensão Textual", "➗ Raciocínio Matemático", "📝 Grafomotricidade"]
}

LISTA_POTENCIAS = [
    "📸 Memória Visual", "🎵 Musicalidade", "💻 Tecnologia", "🧱 Hiperfoco", 
    "👑 Liderança", "⚽ Esportes", "🎨 Arte", "🔢 Cálculo Mental", 
    "🗣️ Oralidade", "🚀 Criatividade", "❤️ Empatia", "🧩 Resolução Problemas"
]

LISTA_PROFISSIONAIS = [
    "Psicólogo", "Neuropsicólogo", "Fonoaudiólogo", "Terapeuta Ocupacional",
    "Neuropediatra", "Psiquiatra", "Psicopedagogo", "Professor de Apoio"
]

LISTA_FAMILIA = [
    "Mãe", "Pai", "Avó", "Avô", "Irmãos", "Tios", "Tutor Legal"
]

# ==============================================================================
# 6. CONFIGURAÇÃO INICIAL (ESTADO DA APLICAÇÃO)
# ==============================================================================
# Dados padrão para um novo aluno
DADOS_PADRAO = {
    'nome': '',
    'nasc': date(2015, 1, 1),
    'serie': None,
    'turma': '',
    'diagnostico': '',
    'lista_medicamentos': [],
    'composicao_familiar': [],
    'historico': '',
    'familia': '',
    'hiperfoco': '',
    'potencias': [],
    'rede_apoio': [],
    'orientacoes_especialistas': '',
    'checklist_evidencias': {},
    'nivel_alfabetizacao': 'Não se aplica (Educação Infantil)',
    'barreiras_selecionadas': {k: [] for k in LISTAS_BARREIRAS.keys()},
    'niveis_suporte': {},
    'estrategias_acesso': [],
    'estrategias_ensino': [],
    'estrategias_avaliacao': [],
    'ia_sugestao': '',
    'ia_mapa_texto': '',
    'status_validacao_pei': 'rascunho',
    'status_validacao_game': 'rascunho',
    'monitoramento_data': date.today(),
    'status_meta': 'Não Iniciado',
    'parecer_geral': 'Manter Estratégias'
}

# Inicializar dados se não existirem
if 'dados_aluno' not in st.session_state:
    st.session_state.dados_aluno = DADOS_PADRAO.copy()

if 'banco_alunos' not in st.session_state:
    st.session_state.banco_alunos = carregar_alunos_usuario()

if 'pdf_texto' not in st.session_state:
    st.session_state.pdf_texto = ""

# ==============================================================================
# 7. FUNÇÕES AUXILIARES IMPORTANTES
# ==============================================================================
def calcular_idade(data_nasc):
    """Calcula idade a partir da data de nascimento"""
    hoje = date.today()
    idade = hoje.year - data_nasc.year
    if (hoje.month, hoje.day) < (data_nasc.month, data_nasc.day):
        idade -= 1
    return idade

def calcular_progresso():
    """Calcula quanto do formulário está preenchido"""
    dados = st.session_state.dados_aluno
    pontos = 0
    total = 8  # Total de campos importantes
    
    if dados['nome']: pontos += 1
    if dados['serie']: pontos += 1
    if dados['diagnostico']: pontos += 1
    if dados['hiperfoco']: pontos += 1
    if any(dados['barreiras_selecionadas'].values()): pontos += 1
    if dados['potencias']: pontos += 1
    if dados['nivel_alfabetizacao'] != 'Não se aplica (Educação Infantil)': pontos += 1
    if dados['ia_sugestao']: pontos += 1
    
    return int((pontos / total) * 100)

def limpar_formulario():
    """Reseta todos os dados para começar novo aluno"""
    st.session_state.dados_aluno = DADOS_PADRAO.copy()
    st.session_state.pdf_texto = ""
    st.success("✅ Formulário limpo! Pode começar um novo aluno.")

def extrair_metas_smart(texto_ia):
    """Extrai metas SMART do texto da IA"""
    metas = {"Curto": "Definir...", "Medio": "Definir...", "Longo": "Definir..."}
    
    # Procura padrões no texto
    if "Curto Prazo" in texto_ia:
        partes = texto_ia.split("Curto Prazo")
        if len(partes) > 1:
            linha = partes[1].split("\n")[0].strip()
            metas["Curto"] = linha[:100]
    
    if "Médio Prazo" in texto_ia:
        partes = texto_ia.split("Médio Prazo")
        if len(partes) > 1:
            linha = partes[1].split("\n")[0].strip()
            metas["Medio"] = linha[:100]
    
    if "Longo Prazo" in texto_ia:
        partes = texto_ia.split("Longo Prazo")
        if len(partes) > 1:
            linha = partes[1].split("\n")[0].strip()
            metas["Longo"] = linha[:100]
    
    return metas

def gerar_pdf_simples(dados):
    """Gera PDF básico do PEI"""
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "PEI - PLANO DE ENSINO INDIVIDUALIZADO", 0, 1, 'C')
    pdf.set_font("Arial", '', 12)
    pdf.ln(10)
    
    # Dados básicos
    pdf.cell(0, 10, f"Aluno: {dados['nome']}", 0, 1)
    pdf.cell(0, 10, f"Série: {dados['serie']}", 0, 1)
    pdf.cell(0, 10, f"Diagnóstico: {dados['diagnostico']}", 0, 1)
    pdf.ln(10)
    
    # Barreiras
    if any(dados['barreiras_selecionadas'].values()):
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(0, 10, "Barreiras Identificadas:", 0, 1)
        pdf.set_font("Arial", '', 12)
        
        for area, itens in dados['barreiras_selecionadas'].items():
            if itens:
                pdf.cell(0, 10, f"• {area}:", 0, 1)
                for item in itens:
                    pdf.cell(10)  # Indentação
                    pdf.cell(0, 10, f"  - {item}", 0, 1)
    
    return pdf.output(dest='S').encode('latin-1')

# ==============================================================================
# 8. FUNÇÕES DE INTELIGÊNCIA ARTIFICIAL
# ==============================================================================
def configurar_api_openai():
    """Configura a chave da API OpenAI"""
    if 'OPENAI_API_KEY' in st.secrets:
        return st.secrets['OPENAI_API_KEY']
    else:
        # Usa sidebar para entrada
        with st.sidebar:
            api_key = st.text_input("🔑 Chave OpenAI:", type="password")
            if api_key:
                return api_key
        return None

def consultar_ia_pei(dados_aluno):
    """Consulta IA para gerar sugestões do PEI"""
    api_key = configurar_api_openai()
    if not api_key:
        return None, "❌ Configure a chave OpenAI na barra lateral"
    
    try:
        cliente = OpenAI(api_key=api_key)
        
        # Prepara prompt detalhado
        prompt = f"""
        Crie um Plano de Ensino Individualizado (PEI) para:
        
        NOME: {dados_aluno['nome']}
        SÉRIE: {dados_aluno['serie']}
        DIAGNÓSTICO: {dados_aluno['diagnostico']}
        HIPERFOCO: {dados_aluno['hiperfoco']}
        POTENCIALIDADES: {', '.join(dados_aluno['potencias'])}
        BARREIRAS: {json.dumps(dados_aluno['barreiras_selecionadas'])}
        
        Por favor, inclua:
        1. Perfil do estudante
        2. Metas SMART (Curto, Médio e Longo Prazo)
        3. Estratégias de ensino
        4. Adaptações necessárias
        5. Sugestões de avaliação
        
        Formato: Use títulos claros e seja objetivo.
        """
        
        resposta = cliente.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}]
        )
        
        return resposta.choices[0].message.content, None
        
    except Exception as e:
        return None, f"❌ Erro: {str(e)}"

# ==============================================================================
# 9. BARRA LATERAL (MENU PRINCIPAL)
# ==============================================================================
with st.sidebar:
    st.markdown("## 🧭 Navegação")
    
    # Logo
    try:
        st.image("omni_icone.png", width=100)
    except:
        st.markdown("### 🧩 OMNISFERA")
    
    st.markdown("---")
    
    # Informações do usuário
    if st.session_state.get("autenticado"):
        st.markdown(f"""
        **👤 Usuário:** {st.session_state['usuario_nome']}
        **🏢 Cargo:** {st.session_state['usuario_cargo']}
        """)
    
    st.markdown("---")
    
    # Menu principal
    st.markdown("### 📂 Ações Rápidas")
    
    if st.button("🆕 Novo Aluno", use_container_width=True):
        limpar_formulario()
        st.rerun()
    
    if st.button("💾 Salvar Tudo", type="primary", use_container_width=True):
        sucesso, mensagem = salvar_aluno(st.session_state.dados_aluno)
        if sucesso:
            st.success(mensagem)
            # Atualiza lista de alunos
            st.session_state.banco_alunos = carregar_alunos_usuario()
        else:
            st.error(mensagem)
    
    st.markdown("---")
    
    # Lista de alunos salvos
    st.markdown("### 👥 Alunos Salvos")
    
    if st.session_state.banco_alunos:
        nomes_alunos = [a['nome'] for a in st.session_state.banco_alunos if a.get('nome')]
        
        aluno_selecionado = st.selectbox(
            "Selecione para carregar:",
            nomes_alunos,
            index=None,
            placeholder="Escolha um aluno..."
        )
        
        col1, col2 = st.columns(2)
        
        if col1.button("📂 Carregar", use_container_width=True) and aluno_selecionado:
            # Encontra aluno
            aluno = next((a for a in st.session_state.banco_alunos 
                         if a.get('nome') == aluno_selecionado), None)
            if aluno:
                st.session_state.dados_aluno = aluno
                st.success(f"✅ {aluno_selecionado} carregado!")
                st.rerun()
        
        if col2.button("🗑️ Excluir", type="secondary", use_container_width=True) and aluno_selecionado:
            sucesso, mensagem = excluir_aluno(aluno_selecionado)
            if sucesso:
                st.success(mensagem)
                st.session_state.banco_alunos = carregar_alunos_usuario()
                st.rerun()
            else:
                st.error(mensagem)
    else:
        st.info("Nenhum aluno salvo ainda.")
    
    st.markdown("---")
    
    # Botão para outras páginas
    st.markdown("### 🌐 Outros Módulos")
    if st.button("🏠 Página Inicial"):
        st.switch_page("Home.py")
    if st.button("🚀 Hub de Inclusão"):
        st.switch_page("pages/3_Hub_Inclusao.py")

# ==============================================================================
# 10. CABEÇALHO PRINCIPAL DA PÁGINA
# ==============================================================================
st.markdown("""
<div class="header-principal">
    <div style="flex: 1;">
        <h1 style="margin: 0; color: white;">🧩 PEI 360°</h1>
        <p style="margin: 0; opacity: 0.9; font-size: 1.1rem;">
        Plano de Ensino Individualizado Inteligente
        </p>
    </div>
    <div style="text-align: right;">
        <div style="background: rgba(255,255,255,0.2); padding: 10px 20px; border-radius: 10px;">
            <div style="font-size: 0.9rem; opacity: 0.8;">Progresso</div>
            <div style="font-size: 1.5rem; font-weight: bold;">{}%</div>
        </div>
    </div>
</div>
""".format(calcular_progresso()), unsafe_allow_html=True)

# Barra de progresso visual
st.markdown(f"""
<div class="barra-progresso">
    <div class="barra-preenchida" style="width: {calcular_progresso()}%"></div>
</div>
""", unsafe_allow_html=True)

# ==============================================================================
# 11. ABAS PRINCIPAIS (INTERFACE DO USUÁRIO)
# ==============================================================================
# Criar abas
aba1, aba2, aba3, aba4, aba5, aba6, aba7 = st.tabs([
    "👤 Identificação", 
    "🏥 Diagnóstico", 
    "🎯 Potencialidades", 
    "🚧 Barreiras", 
    "🛠️ Estratégias", 
    "🤖 Consultoria IA", 
    "📄 Exportar"
])

# ==============================================================================
# ABA 1: IDENTIFICAÇÃO
# ==============================================================================
with aba1:
    st.markdown("### 👤 Identificação do Estudante")
    
    col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
    
    with col1:
        st.session_state.dados_aluno['nome'] = st.text_input(
            "Nome Completo*",
            value=st.session_state.dados_aluno['nome'],
            placeholder="Digite o nome completo do aluno"
        )
    
    with col2:
        st.session_state.dados_aluno['nasc'] = st.date_input(
            "Data de Nascimento*",
            value=st.session_state.dados_aluno['nasc']
        )
    
    with col3:
        # Encontrar índice correto na lista
        serie_atual = st.session_state.dados_aluno['serie']
        indice = LISTA_SERIES.index(serie_atual) if serie_atual in LISTA_SERIES else 0
        
        st.session_state.dados_aluno['serie'] = st.selectbox(
            "Série/Ano*",
            LISTA_SERIES,
            index=indice
        )
    
    with col4:
        st.session_state.dados_aluno['turma'] = st.text_input(
            "Turma",
            value=st.session_state.dados_aluno['turma'],
            placeholder="Ex: A"
        )
    
    st.markdown("---")
    
    # Histórico escolar
    col_hist, col_fam = st.columns(2)
    
    with col_hist:
        st.markdown("#### 📚 Histórico Escolar")
        st.session_state.dados_aluno['historico'] = st.text_area(
            "Descreva brevemente o histórico escolar:",
            value=st.session_state.dados_aluno['historico'],
            height=150
        )
    
    with col_fam:
        st.markdown("#### 👨‍👩‍👧‍👦 Contexto Familiar")
        st.session_state.dados_aluno['familia'] = st.text_area(
            "Descreva a dinâmica familiar:",
            value=st.session_state.dados_aluno['familia'],
            height=150
        )
        
        st.session_state.dados_aluno['composicao_familiar'] = st.multiselect(
            "Composição familiar:",
            LISTA_FAMILIA,
            default=st.session_state.dados_aluno['composicao_familiar']
        )
    
    # Upload de laudo PDF
    st.markdown("---")
    st.markdown("#### 📎 Laudo Médico (Opcional)")
    
    uploaded_pdf = st.file_uploader("Carregue laudo em PDF", type="pdf")
    
    if uploaded_pdf:
        # Lê PDF
        leitor = PdfReader(uploaded_pdf)
        texto = ""
        for pagina in leitor.pages[:3]:  # Lê apenas 3 páginas
            texto += pagina.extract_text()
        
        st.session_state.pdf_texto = texto[:2000]  # Guarda apenas parte
        st.success(f"✅ PDF carregado ({len(texto)} caracteres)")

# ==============================================================================
# ABA 2: DIAGNÓSTICO
# ==============================================================================
with aba2:
    st.markdown("### 🏥 Contexto Clínico e Diagnóstico")
    
    # Diagnóstico principal
    st.session_state.dados_aluno['diagnostico'] = st.text_input(
        "Diagnóstico Principal*",
        value=st.session_state.dados_aluno['diagnostico'],
        placeholder="Ex: TEA Nível 1, TDAH, Dislexia..."
    )
    
    # Medicamentos
    st.markdown("#### 💊 Medicamentos")
    
    tem_medicamento = st.toggle("O aluno usa medicação?", 
                               value=len(st.session_state.dados_aluno['lista_medicamentos']) > 0)
    
    if tem_medicamento:
        col_med1, col_med2, col_med3 = st.columns([3, 2, 1])
        
        with col_med1:
            novo_med = st.text_input("Nome do medicamento")
        
        with col_med2:
            nova_poso = st.text_input("Posologia")
        
        with col_med3:
            st.write("")  # Espaço
            st.write("")
            if st.button("➕ Adicionar"):
                if novo_med:
                    st.session_state.dados_aluno['lista_medicamentos'].append({
                        'nome': novo_med,
                        'posologia': nova_poso
                    })
                    st.rerun()
        
        # Lista de medicamentos
        if st.session_state.dados_aluno['lista_medicamentos']:
            st.markdown("**Medicamentos atuais:**")
            for i, med in enumerate(st.session_state.dados_aluno['lista_medicamentos']):
                col_med, col_del = st.columns([5, 1])
                with col_med:
                    st.info(f"**{med['nome']}** - {med['posologia']}")
                with col_del:
                    if st.button("❌", key=f"del_med_{i}"):
                        st.session_state.dados_aluno['lista_medicamentos'].pop(i)
                        st.rerun()
    
    # Rede de apoio
    st.markdown("---")
    st.markdown("#### 🏥 Rede de Apoio")
    
    st.session_state.dados_aluno['rede_apoio'] = st.multiselect(
        "Profissionais que acompanham o aluno:",
        LISTA_PROFISSIONAIS,
        default=st.session_state.dados_aluno['rede_apoio']
    )
    
    st.session_state.dados_aluno['orientacoes_especialistas'] = st.text_area(
        "Orientações dos especialistas:",
        value=st.session_state.dados_aluno['orientacoes_especialistas'],
        height=100
    )

# ==============================================================================
# ABA 3: POTENCIALIDADES
# ==============================================================================
with aba3:
    st.markdown("### 🎯 Potencialidades e Interesses")
    
    col_hiper, col_pot = st.columns(2)
    
    with col_hiper:
        st.markdown("#### 🚀 Hiperfoco")
        st.session_state.dados_aluno['hiperfoco'] = st.text_input(
            "Área de interesse intenso do aluno:",
            value=st.session_state.dados_aluno['hiperfoco'],
            placeholder="Ex: Dinossauros, Minecraft, Futebol..."
        )
        
        if st.session_state.dados_aluno['hiperfoco']:
            st.success(f"✨ Ótimo! Vamos usar isso nas estratégias.")
    
    with col_pot:
        st.markdown("#### 🌟 Potencialidades")
        st.session_state.dados_aluno['potencias'] = st.multiselect(
            "Pontos fortes do aluno:",
            LISTA_POTENCIAS,
            default=st.session_state.dados_aluno['potencias']
        )
    
    # Nível de alfabetização
    st.markdown("---")
    st.markdown("#### 📖 Nível de Alfabetização")
    
    nivel_atual = st.session_state.dados_aluno['nivel_alfabetizacao']
    indice_alf = LISTA_ALFABETIZACAO.index(nivel_atual) if nivel_atual in LISTA_ALFABETIZACAO else 0
    
    st.session_state.dados_aluno['nivel_alfabetizacao'] = st.selectbox(
        "Hipótese de escrita/alfabetização:",
        LISTA_ALFABETIZACAO,
        index=indice_alf
    )
    
    # Evidências observadas
    st.markdown("---")
    st.markdown("#### 🔍 Evidências Observadas")
    
    col_ev1, col_ev2, col_ev3 = st.columns(3)
    
    evidencias = [
        "Dificuldade de atenção", "Baixa tolerância à frustração",
        "Dependência de mediação", "Desorganização", 
        "Fadiga mental rápida", "Recusa de tarefas"
    ]
    
    # Inicializar se não existir
    if not st.session_state.dados_aluno['checklist_evidencias']:
        st.session_state.dados_aluno['checklist_evidencias'] = {e: False for e in evidencias}
    
    for i, evidencia in enumerate(evidencias):
        col = col_ev1 if i < 2 else col_ev2 if i < 4 else col_ev3
        with col:
            st.session_state.dados_aluno['checklist_evidencias'][evidencia] = st.checkbox(
                evidencia,
                value=st.session_state.dados_aluno['checklist_evidencias'].get(evidencia, False)
            )

# ==============================================================================
# ABA 4: BARREIRAS
# ==============================================================================
with aba4:
    st.markdown("### 🚧 Barreiras e Níveis de Suporte")
    st.markdown("Identifique as principais barreiras e o nível de suporte necessário.")
    
    # Para cada categoria de barreiras
    for categoria, itens in LISTAS_BARREIRAS.items():
        st.markdown(f"#### {categoria}")
        
        # Selecionar barreiras
        selecionadas = st.multiselect(
            f"Selecione barreiras em {categoria}:",
            itens,
            default=st.session_state.dados_aluno['barreiras_selecionadas'].get(categoria, []),
            key=f"ms_{categoria}"
        )
        
        st.session_state.dados_aluno['barreiras_selecionadas'][categoria] = selecionadas
        
        # Para cada barreira selecionada, definir nível de suporte
        for barreira in selecionadas:
            nivel_atual = st.session_state.dados_aluno['niveis_suporte'].get(f"{categoria}_{barreira}", "Monitorado")
            
            nivel = st.select_slider(
                f"Nível de suporte para: {barreira}",
                options=["Autônomo", "Monitorado", "Substancial", "Muito Substancial"],
                value=nivel_atual,
                key=f"sl_{categoria}_{barreira}"
            )
            
            st.session_state.dados_aluno['niveis_suporte'][f"{categoria}_{barreira}"] = nivel
    
    # Resumo visual
    if any(st.session_state.dados_aluno['barreiras_selecionadas'].values()):
        st.markdown("---")
        st.markdown("#### 📊 Resumo das Barreiras")
        
        total_barreiras = sum(len(v) for v in st.session_state.dados_aluno['barreiras_selecionadas'].values())
        
        col_res1, col_res2, col_res3 = st.columns(3)
        
        with col_res1:
            st.metric("Total de Barreiras", total_barreiras)
        
        with col_res2:
            # Contar níveis de suporte
            niveis = list(st.session_state.dados_aluno['niveis_suporte'].values())
            altos = sum(1 for n in niveis if n in ["Substancial", "Muito Substancial"])
            st.metric("Suporte Alto Necessário", altos)
        
        with col_res3:
            if total_barreiras > 5:
                st.warning("⚠️ Múltiplas barreiras")
            elif total_barreiras > 0:
                st.info("✅ Barreiras identificadas")
            else:
                st.success("🎉 Sem barreiras mapeadas")

# ==============================================================================
# ABA 5: ESTRATÉGIAS
# ==============================================================================
with aba5:
    st.markdown("### 🛠️ Estratégias e Adaptações")
    
    col_estr1, col_estr2, col_estr3 = st.columns(3)
    
    with col_estr1:
        st.markdown("#### 🔧 Estratégias de Acesso")
        estrategias_acesso = [
            "Tempo Estendido", "Apoio Leitura/Escrita", 
            "Material Ampliado", "Tecnologia Assistiva",
            "Sala Silenciosa", "Mobiliário Adaptado"
        ]
        
        st.session_state.dados_aluno['estrategias_acesso'] = st.multiselect(
            "Selecione:",
            estrategias_acesso,
            default=st.session_state.dados_aluno['estrategias_acesso'],
            label_visibility="collapsed"
        )
    
    with col_estr2:
        st.markdown("#### 📚 Estratégias de Ensino")
        estrategias_ensino = [
            "Fragmentação de Tarefas", "Pistas Visuais", 
            "Mapas Mentais", "Modelagem",
            "Ensino Híbrido", "Instrução Explícita"
        ]
        
        st.session_state.dados_aluno['estrategias_ensino'] = st.multiselect(
            "Selecione:",
            estrategias_ensino,
            default=st.session_state.dados_aluno['estrategias_ensino'],
            label_visibility="collapsed"
        )
    
    with col_estr3:
        st.markdown("#### 📝 Estratégias de Avaliação")
        estrategias_avaliacao = [
            "Prova Adaptada", "Prova Oral", 
            "Consulta Permitida", "Portfólio",
            "Autoavaliação", "Parecer Descritivo"
        ]
        
        st.session_state.dados_aluno['estrategias_avaliacao'] = st.multiselect(
            "Selecione:",
            estrategias_avaliacao,
            default=st.session_state.dados_aluno['estrategias_avaliacao'],
            label_visibility="collapsed"
        )
    
    # Monitoramento
    st.markdown("---")
    st.markdown("#### 📅 Monitoramento")
    
    col_mon1, col_mon2 = st.columns(2)
    
    with col_mon1:
        st.session_state.dados_aluno['monitoramento_data'] = st.date_input(
            "Próxima revisão do PEI:",
            value=st.session_state.dados_aluno['monitoramento_data']
        )
    
    with col_mon2:
        st.session_state.dados_aluno['status_meta'] = st.selectbox(
            "Status atual das metas:",
            ["Não Iniciado", "Em Andamento", "Parcialmente Atingido", "Atingido", "Superado"],
            index=["Não Iniciado", "Em Andamento", "Parcialmente Atingido", "Atingido", "Superado"]
                .index(st.session_state.dados_aluno['status_meta'])
        )

# ==============================================================================
# ABA 6: CONSULTORIA IA
# ==============================================================================
with aba6:
    st.markdown("### 🤖 Consultoria Pedagógica com IA")
    
    # Verificar se tem dados suficientes
    dados_necessarios = [
        st.session_state.dados_aluno['nome'],
        st.session_state.dados_aluno['serie'],
        st.session_state.dados_aluno['diagnostico']
    ]
    
    if not all(dados_necessarios):
        st.warning("⚠️ Preencha pelo menos: Nome, Série e Diagnóstico para usar a IA")
        st.stop()
    
    # Botão para gerar PEI com IA
    if not st.session_state.dados_aluno['ia_sugestao']:
        st.markdown("#### 🚀 Gerar Plano Completo")
        
        if st.button("✨ GERAR PEI COM INTELIGÊNCIA ARTIFICIAL", 
                    type="primary", 
                    use_container_width=True):
            
            with st.spinner("🤖 Analisando dados e criando PEI personalizado..."):
                resultado, erro = consultar_ia_pei(st.session_state.dados_aluno)
                
                if erro:
                    st.error(erro)
                else:
                    st.session_state.dados_aluno['ia_sugestao'] = resultado
                    st.session_state.dados_aluno['status_validacao_pei'] = 'revisao'
                    st.success("✅ PEI gerado com sucesso!")
                    st.rerun()
    
    # Se já tem sugestão da IA
    if st.session_state.dados_aluno['ia_sugestao']:
        st.markdown("#### 📝 Plano Gerado pela IA")
        
        # Mostrar status
        status = st.session_state.dados_aluno['status_validacao_pei']
        
        if status == 'rascunho':
            st.info("🔄 Rascunho gerado - revise abaixo")
        elif status == 'revisao':
            st.warning("👀 Em revisão - valide ou solicite ajustes")
        elif status == 'aprovado':
            st.success("✅ PEI aprovado e pronto!")
        
        # Mostrar texto da IA
        with st.expander("📋 Ver PEI Completo", expanded=True):
            st.markdown(st.session_state.dados_aluno['ia_sugestao'])
        
        # Controles de validação
        st.markdown("---")
        st.markdown("#### ✅ Validação do Plano")
        
        col_val1, col_val2, col_val3 = st.columns(3)
        
        with col_val1:
            if st.button("👍 APROVAR PEI", type="primary", use_container_width=True):
                st.session_state.dados_aluno['status_validacao_pei'] = 'aprovado'
                
                # Salvar metas automaticamente
                metas = extrair_metas_smart(st.session_state.dados_aluno['ia_sugestao'])
                if salvar_metas_pei(st.session_state.dados_aluno['nome'], metas):
                    st.success("✅ Metas salvas no banco de dados")
                
                st.rerun()
        
        with col_val2:
            if st.button("🔄 SOLICITAR AJUSTES", type="secondary", use_container_width=True):
                st.session_state.dados_aluno['status_validacao_pei'] = 'ajustando'
                st.rerun()
        
        with col_val3:
            if st.button("🗑️ DESCARTAR E REGERAR", type="secondary", use_container_width=True):
                st.session_state.dados_aluno['ia_sugestao'] = ''
                st.session_state.dados_aluno['status_validacao_pei'] = 'rascunho'
                st.rerun()
        
        # Se solicitou ajustes
        if st.session_state.dados_aluno['status_validacao_pei'] == 'ajustando':
            st.markdown("---")
            st.markdown("#### ✏️ Solicitação de Ajustes")
            
            feedback = st.text_area(
                "Descreva o que precisa ser ajustado:",
                placeholder="Ex: Foque mais na alfabetização... Inclua mais exemplos práticos..."
            )
            
            if st.button("🔄 REGERAR COM AJUSTES", type="primary"):
                # Aqui você implementaria a regeração com feedback
                st.info("Funcionalidade de regeração com feedback em desenvolvimento")
                st.session_state.dados_aluno['status_validacao_pei'] = 'revisao'
                st.rerun()

# ==============================================================================
# ABA 7: EXPORTAÇÃO
# ==============================================================================
with aba7:
    st.markdown("### 📄 Exportação e Finalização")
    
    if not st.session_state.dados_aluno['nome']:
        st.warning("Preencha pelo menos o nome do aluno para exportar")
        st.stop()
    
    # Resumo do aluno
    col_res1, col_res2 = st.columns(2)
    
    with col_res1:
        st.markdown("#### 👤 Resumo do Aluno")
        
        dados = st.session_state.dados_aluno
        
        st.markdown(f"""
        **Nome:** {dados['nome']}
        
        **Idade:** {calcular_idade(dados['nasc'])} anos
        
        **Série:** {dados['serie']}
        
        **Diagnóstico:** {dados['diagnostico']}
        
        **Hiperfoco:** {dados['hiperfoco']}
        
        **Potencialidades:** {', '.join(dados['potencias'][:3])}
        """)
    
    with col_res2:
        st.markdown("#### 📊 Estatísticas")
        
        total_barreiras = sum(len(v) for v in dados['barreiras_selecionadas'].values())
        total_estrategias = len(dados['estrategias_acesso']) + len(dados['estrategias_ensino']) + len(dados['estrategias_avaliacao'])
        
        st.metric("Barreiras Identificadas", total_barreiras)
        st.metric("Estratégias Propostas", total_estrategias)
        st.metric("Status do PEI", dados['status_validacao_pei'].upper())
    
    # Botões de exportação
    st.markdown("---")
    st.markdown("#### 📤 Exportar Documentos")
    
    col_exp1, col_exp2, col_exp3 = st.columns(3)
    
    with col_exp1:
        # PDF Simples
        if st.button("📄 Gerar PDF Básico", use_container_width=True):
            pdf_bytes = gerar_pdf_simples(dados)
            st.download_button(
                label="⬇️ Baixar PDF",
                data=pdf_bytes,
                file_name=f"PEI_{dados['nome']}.pdf",
                mime="application/pdf",
                use_container_width=True
            )
    
    with col_exp2:
        # JSON (backup)
        json_bytes = json.dumps(dados, default=str, indent=2).encode('utf-8')
        st.download_button(
            label="💾 Backup em JSON",
            data=json_bytes,
            file_name=f"PEI_{dados['nome']}.json",
            mime="application/json",
            use_container_width=True
        )
    
    with col_exp3:
        # Word (simplificado)
        if st.button("📝 Gerar Documento Word", use_container_width=True):
            doc = Document()
            doc.add_heading(f'PEI - {dados["nome"]}', 0)
            doc.add_paragraph(f"Série: {dados['serie']}")
            doc.add_paragraph(f"Diagnóstico: {dados['diagnostico']}")
            
            if dados['ia_sugestao']:
                doc.add_heading('Plano Pedagógico', 1)
                doc.add_paragraph(dados['ia_sugestao'][:5000])
            
            # Salvar em buffer
            buffer = BytesIO()
            doc.save(buffer)
            buffer.seek(0)
            
            st.download_button(
                label="⬇️ Baixar Word",
                data=buffer,
                file_name=f"PEI_{dados['nome']}.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                use_container_width=True
            )
    
    # Salvar no banco de dados
    st.markdown("---")
    st.markdown("#### 💾 Salvar no Sistema")
    
    if st.button("✅ SALVAR TUDO NO BANCO DE DADOS", type="primary", use_container_width=True):
        sucesso, mensagem = salvar_aluno(st.session_state.dados_aluno)
        
        if sucesso:
            st.success(mensagem)
            st.balloons()
            # Atualizar lista local
            st.session_state.banco_alunos = carregar_alunos_usuario()
        else:
            st.error(mensagem)

# ==============================================================================
# 12. RODAPÉ
# ==============================================================================
st.markdown("---")
st.markdown(
    """
    <div style="text-align: center; color: #718096; font-size: 0.9rem; padding: 20px;">
    🧩 <strong>Omnisfera PEI 360°</strong> | Sistema de Inclusão Escolar Inteligente<br>
    Desenvolvido para educadores • Versão 2.0 • Todos os direitos reservados
    </div>
    """,
    unsafe_allow_html=True
)
