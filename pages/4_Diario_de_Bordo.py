import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import pandas as pd
import time

st.set_page_config(page_title="Diário de Bordo", page_icon="📝", layout="wide")

# ==============================================================================
# 1. CONEXÃO DIRETA (SEM REGRAS COMPLEXAS)
# ==============================================================================
@st.cache_resource
def conectar_banco():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    credentials = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scope)
    client = gspread.authorize(credentials)
    return client.open("Omnisfera_Dados")

def carregar_peis_existentes(sh):
    """
    Busca APENAS os alunos que já possuem PEI salvo na aba 'Metas_PEI'.
    É a fonte única da verdade.
    """
    try:
        ws = sh.worksheet("Metas_PEI")
        dados = ws.get_all_records()
        df = pd.DataFrame(dados)
        return df
    except:
        # Se a aba não existir, retorna vazio
        return pd.DataFrame()

def preparar_diario(sh):
    try:
        return sh.worksheet("Diario_Bordo")
    except:
        ws = sh.add_worksheet("Diario_Bordo", 1000, 10)
        ws.append_row(["Timestamp", "Data", "Professor", "Aluno", "Turma", "Objetivo_PEI", "Atividade_Realizada", "Avaliacao", "Obs"])
        return ws

# ==============================================================================
# 2. INTERFACE
# ==============================================================================

# --- LOGIN SIMPLES ---
with st.sidebar:
    st.header("Identificação")
    if "prof_nome" not in st.session_state: st.session_state["prof_nome"] = ""
    st.session_state["prof_nome"] = st.text_input("Professor(a):", value=st.session_state["prof_nome"])

st.title("📝 Diário de Bordo")

# --- CARREGA DADOS ---
try:
    sh = conectar_banco()
    df_pei = carregar_peis_existentes(sh)
    ws_diario = preparar_diario(sh)
except Exception as e:
    st.error("Erro de conexão. Verifique se a aba 'Metas_PEI' existe.")
    st.stop()

if df_pei.empty:
    st.warning("⚠️ Nenhum PEI encontrado. Crie um PEI primeiro para liberar o Diário.")
    st.stop()

# --- SELEÇÃO DO ALUNO (Baseado no PEI) ---
# Cria uma lista formatada: "João (5º Ano)"
df_pei['label'] = df_pei['aluno_nome'] + " - " + df_pei['turma'].astype(str)
selecao = st.selectbox("Selecione o Aluno (PEI Ativo):", df_pei['label'].unique())

# --- RECUPERA AS INFORMAÇÕES DO PEI ---
# Pega a linha exata desse aluno
dados_aluno = df_pei[df_pei['label'] == selecao].iloc[0]

nome_real = dados_aluno['aluno_nome']
turma_real = dados_aluno['turma']
objetivo_pei = dados_aluno.get('objetivos_gerais', 'Não especificado')
estrategia_pei = dados_aluno.get('estrategias', 'Não especificado')

st.divider()

# --- EXIBIÇÃO DO PEI (O Contexto) ---
# Aqui mostramos o que o professor precisa saber para dar a aula
col_info, col_registro = st.columns([1, 1.5])

with col_info:
    st.markdown("### 🎯 Meta do PEI")
    st.info(f"**Objetivo:** {objetivo_pei}")
    st.markdown(f"**Estratégia Sugerida:** {estrategia_pei}")
    st.caption(f"Turma: {turma_real}")

with col_registro:
    st.subheader("📍 Registro da Aula")
    
    with st.form("form_diario"):
        # O professor descreve o que fez baseado na meta ao lado
        atividade = st.text_input("Atividade Realizada:", placeholder="Ex: Adaptação da prova de História...")
        
        st.markdown("**O aluno conseguiu atingir o objetivo hoje?**")
        avaliacao = st.select_slider(
            "Nível de Suporte:",
            options=["🔴 Não Realizou", "🟠 Ajuda Total", "🟡 Ajuda Parcial", "🟢 Independente"],
            value="🟡 Ajuda Parcial"
        )
        
        obs = st.text_area("Observações:", height=80)
        
        enviar = st.form_submit_button("💾 Salvar Diário", type="primary")

        if enviar:
            if not st.session_state["prof_nome"]:
                st.error("Preencha seu nome na barra lateral.")
            elif not atividade:
                st.error("Descreva a atividade.")
            else:
                with st.spinner("Salvando..."):
                    nova_linha = [
                        str(datetime.now().timestamp()),
                        datetime.now().strftime("%d/%m/%Y"),
                        st.session_state["prof_nome"],
                        nome_real,       # Vem do PEI
                        turma_real,      # Vem do PEI
                        objetivo_pei,    # Salva qual era a meta do dia
                        atividade,
                        avaliacao,
                        obs
                    ]
                    ws_diario.append_row(nova_linha)
                    st.success("✅ Registro salvo com sucesso!")
                    time.sleep(1)
                    st.rerun()

# --- HISTÓRICO RÁPIDO ---
st.divider()
st.subheader(f"Histórico Recente de {nome_real}")

try:
    df_hist = pd.DataFrame(ws_diario.get_all_records())
    if not df_hist.empty and "Aluno" in df_hist.columns:
        # Filtra pelo aluno atual
        historico_aluno = df_hist[df_hist["Aluno"] == nome_real].tail(5).iloc[::-1]
        
        if historico_aluno.empty:
            st.info("Nenhum registro anterior.")
        
        for i, row in historico_aluno.iterrows():
            st.markdown(f"""
            - **{row['Data']}**: {row['Atividade_Realizada']} ({row['Avaliacao']})
            """)
except:
    st.write("Histórico vazio.")
