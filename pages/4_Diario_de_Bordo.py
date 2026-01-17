import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import pandas as pd
import time

# ==============================================================================
# 1. CONFIGURAÇÃO E REGRAS DO CURRÍCULO
# ==============================================================================
st.set_page_config(page_title="Diário de Bordo | Omnisfera", page_icon="📝", layout="wide")

# Regras para identificar a etapa do aluno baseado no nome da turma/série
REGRAS_CURRICULO = {
    "iniciais": {
        "keywords": ["1º", "2º", "3º", "4º", "5º", "1o", "2o", "3o", "4o", "5o", "iniciais", "fund 1"],
        "label": "Anos Iniciais (Polivalente)",
        "materias": ["Regência de Classe (Polivalente)", "Educação Física", "Arte", "Inglês", "Projeto de Vida/Socioemocional"]
    },
    "finais": {
        "keywords": ["6º", "7º", "8º", "9º", "6o", "7o", "8o", "9o", "finais", "fund 2"],
        "label": "Anos Finais (Especialistas)",
        "materias": ["Língua Portuguesa", "Matemática", "Ciências", "Geografia", "História", "Inglês", "Ed. Física", "Arte"]
    },
    "medio": {
        "keywords": ["1ª", "2ª", "3ª", "1a", "2a", "3a", "médio", "medio", "em"],
        "label": "Ensino Médio (Áreas)",
        "materias": ["Linguagens e Tecnologias", "Matemática e Tecnologias", "Ciências da Natureza", "Ciências Humanas", "Projeto de Vida", "Itinerário Formativo"]
    }
}

# ==============================================================================
# 2. CONEXÃO E LEITURA DE DADOS (BACKEND BLINDADO)
# ==============================================================================
@st.cache_resource
def conectar_banco():
    """Conecta ao Google Sheets usando os segredos do Streamlit"""
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    credentials = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scope)
    client = gspread.authorize(credentials)
    return client.open("Omnisfera_Dados")

def carregar_dados_alunos(sh):
    """
    Lê a planilha de cadastro de forma inteligente.
    Resolve erros de 'Header Duplicate' e aceita 'Série' ou 'Turma'.
    """
    try:
        # 1. Tenta achar a aba correta
        try:
            ws = sh.worksheet("Cadastro_Alunos")
        except:
            ws = sh.get_worksheet(0) # Pega a primeira se não achar pelo nome
            
        # 2. TÉCNICA ANTI-ERRO: Pega tudo como texto cru (listas)
        # Isso evita o erro de "cabeçalhos duplicados" se tiver colunas vazias
        dados_brutos = ws.get_all_values()
        
        if not dados_brutos:
            return pd.DataFrame()
            
        # Cria o cabeçalho em minúsculo para facilitar a busca
        headers_originais = [str(h).strip().lower() for h in dados_brutos[0]]
        
        # Cria o DataFrame ignorando a primeira linha (que virou header)
        df = pd.DataFrame(dados_brutos[1:], columns=headers_originais)
        
        # 3. O "DETETIVE DE COLUNAS": Renomeia para o padrão do sistema
        mapa_renomeacao = {}
        for col in df.columns:
            # Variações de Nome
            if any(x in col for x in ['nome', 'aluno', 'estudante']):
                mapa_renomeacao[col] = 'nome'
            # Variações de Turma/Série
            elif any(x in col for x in ['turma', 'série', 'serie', 'ano', 'grade']):
                mapa_renomeacao[col] = 'turma'

        # Aplica a renomeação
        df = df.rename(columns=mapa_renomeacao)
        
        # Verifica se achou as colunas essenciais
        if 'nome' in df.columns and 'turma' in df.columns:
            # Remove linhas vazias (caso tenha sobrado lixo na planilha)
            df = df[df['nome'] != ""]
            return df
        else:
            st.error(f"⚠️ Erro de Leitura: O sistema procurou por colunas de 'Nome' e 'Turma/Série' mas não achou certeza.")
            st.write("Colunas encontradas:", headers_originais)
            return pd.DataFrame()
            
    except Exception as e:
        st.error(f"Erro técnico ao ler alunos: {e}")
        return pd.DataFrame()

def preparar_aba_diario(sh):
    """Garante que a aba de Diário existe e tem as colunas certas"""
    try:
        return sh.worksheet("Diario_Bordo")
    except:
        ws = sh.add_worksheet(title="Diario_Bordo", rows=1000, cols=9)
        ws.append_row(["Timestamp", "Data", "Professor", "Aluno", "Turma_Ref", "Disciplina", "Atividade", "Status", "Obs"])
        return ws

# ==============================================================================
# 3. INTERFACE DO USUÁRIO
# ==============================================================================

# --- BARRA LATERAL (LOGIN) ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=50)
    st.header("Identificação")
    if "prof_nome" not in st.session_state: st.session_state["prof_nome"] = ""
    st.session_state["prof_nome"] = st.text_input("Nome do Educador:", value=st.session_state["prof_nome"])

st.title("📝 Diário de Bordo")
st.markdown("Registro rápido de atividades adaptadas e avaliações.")

# --- CONEXÃO COM O BANCO ---
try:
    sh = conectar_banco()
    df_alunos = carregar_dados_alunos(sh)
    ws_diario = preparar_aba_diario(sh)
except Exception as e:
    st.error("Erro ao conectar com o Google Sheets. Verifique a internet e os Secrets.")
    st.stop()

if df_alunos.empty:
    st.warning("Não encontrei alunos cadastrados. Verifique se a planilha tem as colunas 'Nome' e 'Série/Ano'.")
    st.stop()

# --- SELEÇÃO DE ALUNO ---
lista_nomes = df_alunos['nome'].tolist()
aluno_selecionado = st.selectbox("📂 Selecione o Estudante:", lista_nomes)

# --- INTELIGÊNCIA: DETECTAR CURRÍCULO ---
# Pega os dados do aluno selecionado
dados_aluno = df_alunos[df_alunos['nome'] == aluno_selecionado].iloc[0]
turma_aluno = str(dados_aluno.get('turma', '')).lower() # Ex: "5º ano b"

# Lógica de detecção
materias_exibir = []
etapa_detectada = "Geral"
found = False

for chave, regra in REGRAS_CURRICULO.items():
    for keyword in regra['keywords']:
        if keyword in turma_aluno:
            materias_exibir = regra['materias']
            etapa_detectada = regra['label']
            found = True
            break
    if found: break

# Fallback se não detectar
if not materias_exibir:
    etapa_detectada = "Etapa não identificada (Mostrando Geral)"
    materias_exibir = ["Atividade Geral", "Atividade de Vida Diária", "Atividade Adaptada", "Outros"]

st.info(f"📍 Aluno do(a) **{turma_aluno.upper()}** → Carregando currículo: **{etapa_detectada}**")
st.divider()

# --- ÁREA DE REGISTRO E HISTÓRICO ---
col_form, col_hist = st.columns([1.5, 1])

with col_form:
    st.subheader("O que foi trabalhado?")
    
    # 1. Disciplina (Radio Button para ser visual e lógico)
    disciplina = st.radio(
        "Componente Curricular:",
        options=materias_exibir,
        index=None, # Nada selecionado por padrão
    )
    
    # 2. Atividade
    atividade = st.text_input("Descrição da Atividade (Hub):", placeholder="Ex: Jogo da memória sobre Relevo (Nível 2)")
    
    st.markdown("---")
    
    # 3. Avaliação (Slider é mais rápido)
    st.markdown("**Nível de Autonomia na execução:**")
    status = st.select_slider(
        "Arraste para avaliar:",
        options=["🔴 Não Realizou", "🟠 Ajuda Total", "🟡 Ajuda Parcial", "🟢 Independente"],
        value="🟡 Ajuda Parcial"
    )
    
    # 4. Observação
    obs = st.text_area("Observações (Opcional):", placeholder="Detalhes sobre a mediação...", height=100)
    
    # BOTÃO SALVAR
    if st.button("💾 Registrar no Diário", type="primary", use_container_width=True):
        if not st.session_state["prof_nome"]:
            st.error("⚠️ Identifique-se na barra lateral antes de salvar.")
        elif not disciplina:
            st.error("⚠️ Selecione a Disciplina.")
        elif not atividade:
            st.error("⚠️ Descreva a Atividade.")
        else:
            with st.spinner("Salvando na nuvem..."):
                nova_linha = [
                    str(datetime.now().timestamp()),
                    datetime.now().strftime("%d/%m/%Y"),
                    st.session_state["prof_nome"],
                    aluno_selecionado,
                    turma_aluno,
                    disciplina,
                    atividade,
                    status,
                    obs
                ]
                ws_diario.append_row(nova_linha)
                st.success("✅ Registro salvo com sucesso!")
                time.sleep(1) # Espera um pouco para o usuário ver
                st.rerun() # Atualiza a tela para mostrar no histórico

with col_hist:
    st.subheader(f"Histórico: {aluno_selecionado.split()[0]}")
    
    try:
        # Pega todos os registros para mostrar o histórico
        dados_todos = ws_diario.get_all_records()
        df_hist = pd.DataFrame(dados_todos)
        
        # Filtra se tiver a coluna 'Aluno'
        if not df_hist.empty and "Aluno" in df_hist.columns:
            # Filtra pelo aluno e pega os últimos 5 (invertido)
            df_aluno = df_hist[df_hist["Aluno"] == aluno_selecionado].tail(5).iloc[::-1]
            
            if df_aluno.empty:
                st.info("Nenhum registro ainda.")
            
            for i, row in df_aluno.iterrows():
                # Define cor baseada no status
                status_txt = str(row.get('Status', ''))
                cor_bg = "#f0fdf4" if "Independente" in status_txt else "#fef2f2" if "Não" in status_txt else "#fefce8"
                cor_border = "#22c55e" if "Independente" in status_txt else "#ef4444" if "Não" in status_txt else "#eab308"
                
                st.markdown(f"""
                <div style="background-color: {cor_bg}; padding: 12px; border-radius: 8px; margin-bottom: 10px; border-left: 5px solid {cor_border};">
                    <div style="font-size: 0.8em; color: #666;">📅 {row.get('Data', '')} • {row.get('Disciplina', '')}</div>
                    <div style="font-weight: bold; margin: 4px 0;">{row.get('Atividade', '')}</div>
                    <div style="font-size: 0.9em;">{status_txt}</div>
                    <div style="font-size: 0.8em; color: #555; font-style: italic; margin-top: 4px;">"{row.get('Obs', '')}"</div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.write("Aguardando primeiro registro...")
            
    except Exception as e:
        st.caption("O histórico aparecerá após o primeiro registro.")
