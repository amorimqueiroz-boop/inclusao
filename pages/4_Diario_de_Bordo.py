import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import pandas as pd

# ==============================================================================
# 1. CONFIGURAÇÃO E INTELIGÊNCIA CURRICULAR
# ==============================================================================
st.set_page_config(page_title="Diário de Bordo | Omnisfera", page_icon="📝", layout="wide")

# Mapeamento: Palavras-chave na Turma -> Lista de Matérias
# O sistema vai procurar "6º" na turma do aluno e saberá que é Anos Finais
REGRAS_CURRICULO = {
    "iniciais": {
        "keywords": ["1º", "2º", "3º", "4º", "5º", "iniciais", "fund 1"],
        "label": "Anos Iniciais (Polivalente)",
        "materias": ["Regência de Classe (Polivalente)", "Educação Física", "Arte", "Inglês", "Projeto de Vida/Socioemocional"]
    },
    "finais": {
        "keywords": ["6º", "7º", "8º", "9º", "finais", "fund 2"],
        "label": "Anos Finais (Especialistas)",
        "materias": ["Língua Portuguesa", "Matemática", "Ciências", "Geografia", "História", "Inglês", "Ed. Física", "Arte"]
    },
    "medio": {
        "keywords": ["1ª", "2ª", "3ª", "médio", "medio", "em"],
        "label": "Ensino Médio (Áreas)",
        "materias": ["Linguagens e Tecnologias", "Matemática e Tecnologias", "Ciências da Natureza", "Ciências Humanas", "Projeto de Vida", "Itinerário Formativo"]
    }
}

# ==============================================================================
# 2. CONEXÃO E LEITURA DE DADOS (BACKEND)
# ==============================================================================
@st.cache_resource
def conectar_banco():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    credentials = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scope)
    client = gspread.authorize(credentials)
    return client.open("Omnisfera_Dados")

def carregar_dados_alunos(sh):
    """
    Lê a planilha de cadastro inteira para pegar Nome e Turma.
    Retorna um DataFrame para podermos filtrar fácil.
    """
    try:
        # Tenta achar a aba de Cadastro
        try:
            ws = sh.worksheet("Cadastro_Alunos")
        except:
            ws = sh.get_worksheet(0) # Pega a primeira se não achar pelo nome
            
        dados = ws.get_all_records()
        df = pd.DataFrame(dados)
        
        # Normaliza nomes das colunas para evitar erros (tudo minúsculo)
        df.columns = [c.lower() for c in df.columns]
        
        # Garante que temos as colunas essenciais
        if 'nome' in df.columns and 'turma' in df.columns:
            return df
        elif 'aluno' in df.columns and 'ano' in df.columns: # Caso os nomes sejam diferentes
            df = df.rename(columns={'aluno': 'nome', 'ano': 'turma'})
            return df
        else:
            st.error("A planilha precisa ter colunas chamadas 'Nome' e 'Turma'")
            return pd.DataFrame()
            
    except Exception as e:
        st.error(f"Erro ao ler alunos: {e}")
        return pd.DataFrame()

def preparar_aba_diario(sh):
    try:
        return sh.worksheet("Diario_Bordo")
    except:
        ws = sh.add_worksheet(title="Diario_Bordo", rows=1000, cols=8)
        ws.append_row(["Timestamp", "Data", "Professor", "Aluno", "Turma_Ref", "Disciplina", "Atividade", "Status", "Obs"])
        return ws

# ==============================================================================
# 3. INTERFACE INTELIGENTE
# ==============================================================================

# --- SIDEBAR ---
with st.sidebar:
    st.header("Identificação")
    if "prof_nome" not in st.session_state: st.session_state["prof_nome"] = ""
    st.session_state["prof_nome"] = st.text_input("Professor(a):", value=st.session_state["prof_nome"])

st.title("📝 Diário de Bordo")

# Conecta e Puxa Dados
try:
    sh = conectar_banco()
    df_alunos = carregar_dados_alunos(sh)
    ws_diario = preparar_aba_diario(sh)
except:
    st.stop()

if df_alunos.empty:
    st.warning("Nenhum aluno cadastrado com Nome/Turma.")
    st.stop()

# --- 1. SELEÇÃO DO ALUNO ---
# Cria uma lista de nomes para o selectbox
lista_nomes = df_alunos['nome'].tolist()
aluno_selecionado = st.selectbox("Selecione o Estudante:", lista_nomes)

# --- 2. CÉREBRO DA OPERAÇÃO: DETECTAR CURRÍCULO ---
# Pega a linha desse aluno no DataFrame
dados_aluno = df_alunos[df_alunos['nome'] == aluno_selecionado].iloc[0]
turma_aluno = str(dados_aluno.get('turma', '')).lower() # Ex: "5º Ano B"

# Lógica de detecção automática
materias_exibir = []
etapa_detectada = "Geral"

# Verifica se a turma contém palavras chave (ex: "5º" está em iniciais)
found = False
for chave, regra in REGRAS_CURRICULO.items():
    for keyword in regra['keywords']:
        if keyword in turma_aluno:
            materias_exibir = regra['materias']
            etapa_detectada = regra['label']
            found = True
            break
    if found: break

# Fallback: Se não achar (ex: turma chama "Azul"), mostra lista genérica
if not materias_exibir:
    etapa_detectada = "Etapa não identificada automaticamente"
    materias_exibir = ["Atividade Geral", "Atividade de Vida Diária", "Outros"]

# Mostra o contexto para o professor (Feedback visual)
st.info(f"📍 **Aluno matriculado no:** {turma_aluno.upper()} → **Currículo:** {etapa_detectada}")

st.divider()

# --- 3. REGISTRO (VISUAL ABERTO) ---
col_esq, col_dir = st.columns([1.5, 1])

with col_esq:
    st.subheader("O que foi trabalhado?")
    
    # AQUI ESTÁ A MUDANÇA: RADIO (Lista aberta) ao invés de Selectbox
    # O index=None faz com que nada venha selecionado por padrão
    disciplina = st.radio(
        "Selecione o Componente Curricular:",
        options=materias_exibir,
        index=None, 
        horizontal=False # Vertical para facilitar leitura na lista lógica
    )

    st.markdown("---")
    
    # Campo de Atividade
    atividade = st.text_input("Qual atividade foi realizada?", placeholder="Ex: Atividade adaptada sobre Sistema Solar (Hub)")

    # Avaliação (Usando botões visuais se possível ou radio horizontal)
    st.markdown("**Como o aluno respondeu?**")
    status = st.select_slider(
        "Nível de Autonomia:",
        options=["🔴 Não Realizou", "🟠 Ajuda Total", "🟡 Ajuda Parcial", "🟢 Independente"],
        value="🟡 Ajuda Parcial"
    )

    obs = st.text_area("Observações (Opcional):", height=100)

    # Botão de Salvar
    if st.button("💾 Registrar no Diário", type="primary", use_container_width=True):
        if not st.session_state["prof_nome"]:
            st.error("Preencha seu nome na barra lateral.")
        elif not disciplina:
            st.error("Selecione a disciplina na lista acima.")
        elif not atividade:
            st.error("Descreva a atividade.")
        else:
            with st.spinner("Enviando..."):
                nova_linha = [
                    str(datetime.now().timestamp()),
                    datetime.now().strftime("%d/%m/%Y"),
                    st.session_state["prof_nome"],
                    aluno_selecionado,
                    turma_aluno, # Salva a turma também para histórico
                    disciplina,
                    atividade,
                    status,
                    obs
                ]
                ws_diario.append_row(nova_linha)
                st.success("✅ Registro salvo!")
                # st.rerun() # Descomente para limpar a tela após salvar

# --- 4. HISTÓRICO RÁPIDO ---
with col_dir:
    st.subheader(f"Histórico: {aluno_selecionado.split()[0]}")
    
    # Busca dados na planilha (Lógica simplificada para visualização)
    try:
        dados_todos = ws_diario.get_all_records()
        df_hist = pd.DataFrame(dados_todos)
        
        if not df_hist.empty and "Aluno" in df_hist.columns:
            # Filtra pelo aluno
            df_aluno = df_hist[df_hist["Aluno"] == aluno_selecionado].tail(5).iloc[::-1] # Últimos 5 invertidos
            
            for i, row in df_aluno.iterrows():
                cor = "#dcfce7" if "Independente" in row['Status'] else "#fee2e2" if "Não" in row['Status'] else "#fef9c3"
                st.markdown(f"""
                <div style="background-color: {cor}; padding: 10px; border-radius: 8px; margin-bottom: 8px; border: 1px solid #ddd;">
                    <small><b>{row['Data']}</b> - {row['Disciplina']}</small><br>
                    {row['Atividade']}<br>
                    <small><i>{row['Status']}</i></small>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.write("Nenhum registro anterior.")
    except:
        st.write("Histórico indisponível.")
