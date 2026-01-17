import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import pandas as pd

# ==============================================================================
# 1. CONFIGURAÇÃO E CONEXÃO (A Base da Integração)
# ==============================================================================
st.set_page_config(page_title="Omnisfera | Diário de Bordo", page_icon="📝", layout="wide")

# Função de Conexão Blindada (Mesma chave do PEI)
@st.cache_resource
def conectar_banco():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    credentials = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scope)
    client = gspread.authorize(credentials)
    # Abre a planilha principal
    sh = client.open("Omnisfera_Dados")
    return sh

# Função Inteligente: Garante que as abas existam
def inicializar_abas(sh):
    try:
        # Tenta pegar a aba de Diário, se não existir, cria
        return sh.worksheet("Diario_Bordo")
    except:
        # Cria a aba com os cabeçalhos corretos
        ws = sh.add_worksheet(title="Diario_Bordo", rows=1000, cols=6)
        ws.append_row(["Timestamp", "Data_Hora", "Professor", "Aluno", "Atividade", "Resultado", "Observacao"])
        return ws

def buscar_alunos_cadastrados(sh):
    """Lê a aba 1 (Cadastros do PEI) para preencher o selectbox"""
    try:
        ws = sh.sheet1 # Assume que a aba 1 é a do PEI
        nomes = ws.col_values(1) # Coluna A é sempre o Nome
        if len(nomes) > 0:
            return nomes[1:] # Remove o cabeçalho se houver, ou ajusta conforme sua estrutura
        return []
    except:
        return []

def buscar_historico_aluno(sh, nome_aluno):
    """Busca os últimos registros deste aluno específico"""
    ws = inicializar_abas(sh)
    dados = ws.get_all_records()
    if not dados: return pd.DataFrame()
    
    df = pd.DataFrame(dados)
    # Filtra pelo aluno
    df_aluno = df[df["Aluno"] == nome_aluno]
    # Ordena por data (mais recente primeiro) e pega os top 5
    return df_aluno.sort_values(by="Timestamp", ascending=False).head(5)

# ==============================================================================
# 2. INTERFACE E LÓGICA DE USUÁRIO
# ==============================================================================
st.title("📝 Diário de Bordo & Avaliação Contínua")
st.markdown("Use este módulo para registrar a aplicação prática das estratégias do PEI.")

# --- BARRA LATERAL: LOGIN SIMPLES ---
with st.sidebar:
    st.header("🔐 Acesso do Educador")
    if "usuario_nome" not in st.session_state: st.session_state["usuario_nome"] = ""
    
    nome_input = st.text_input("Seu Nome (Professor/Mediador):", value=st.session_state["usuario_nome"])
    if nome_input:
        st.session_state["usuario_nome"] = nome_input
        st.success(f"Logado: {nome_input}")
    else:
        st.warning("Identifique-se para salvar.")

# --- CONEXÃO COM A NUVEM ---
try:
    sh = conectar_banco()
    lista_alunos = buscar_alunos_cadastrados(sh)
    ws_diario = inicializar_abas(sh)
    db_status = "🟢 Conectado à Omnisfera"
except Exception as e:
    lista_alunos = []
    db_status = "🔴 Erro de Conexão"
    st.error(f"Erro ao conectar com Google Sheets: {e}")

st.write(f"<small>{db_status}</small>", unsafe_allow_html=True)

# --- ÁREA PRINCIPAL ---
col_registro, col_historico = st.columns([1, 1.2])

with col_registro:
    st.subheader("📍 Novo Registro")
    
    if not lista_alunos:
        st.info("Nenhum aluno encontrado no banco PEI. Cadastre alguém no módulo principal primeiro.")
        st.stop()

    aluno_selecionado = st.selectbox("Selecione o Estudante:", lista_alunos)
    
    # Campo livre, mas com sugestão baseada no PEI (Futuro: Puxar metas do PEI aqui)
    atividade = st.text_input("Atividade / Meta Trabalhada:", placeholder="Ex: Frações com material dourado...")
    
    st.write("---")
    st.markdown("**Como foi a execução?**")
    status = st.radio("Nível de Suporte Necessário hoje:", 
                      ["🟢 Independente (Sucesso)", 
                       "🟡 Com Ajuda Verbal/Visual", 
                       "🟠 Com Ajuda Física/Total", 
                       "🔴 Não Realizou / Resistência"],
                      horizontal=True)
    
    obs = st.text_area("Observações Qualitativas (Opcional):", placeholder="O que funcionou? O que precisou adaptar?")

    if st.button("💾 Salvar no Histórico", type="primary", use_container_width=True):
        if not st.session_state["usuario_nome"]:
            st.error("Identifique-se na barra lateral!")
        elif not atividade:
            st.error("Descreva a atividade.")
        else:
            with st.spinner("Sincronizando com a Nuvem..."):
                nova_linha = [
                    str(datetime.now().timestamp()),          # ID único temporal
                    datetime.now().strftime("%d/%m/%Y %H:%M"), # Data Legível
                    st.session_state["usuario_nome"],          # Quem registrou
                    aluno_selecionado,                         # Quem é o aluno (Link com PEI)
                    atividade,
                    status,
                    obs
                ]
                ws_diario.append_row(nova_linha)
                st.success("✅ Registro salvo com sucesso!")
                st.balloons()
                # Força atualização da interface para mostrar no histórico
                st.rerun()

with col_historico:
    st.subheader(f"📅 Histórico Recente: {aluno_selecionado if lista_alunos else ''}")
    
    if lista_alunos and aluno_selecionado:
        try:
            df_hist = buscar_historico_aluno(sh, aluno_selecionado)
            
            if not df_hist.empty:
                for index, row in df_hist.iterrows():
                    # Card Visual do Histórico
                    cor_borda = "#48bb78" if "Independente" in row['Resultado'] else "#ed8936" if "Ajuda" in row['Resultado'] else "#e53e3e"
                    
                    st.markdown(f"""
                    <div style="border-left: 5px solid {cor_borda}; background-color: #f7fafc; padding: 15px; border-radius: 5px; margin-bottom: 10px;">
                        <div style="font-size: 0.8rem; color: #718096;">{row['Data_Hora']} | Prof. {row['Professor']}</div>
                        <div style="font-weight: bold; font-size: 1.1rem; color: #2d3748;">{row['Atividade']}</div>
                        <div style="margin: 5px 0;">{row['Resultado']}</div>
                        <div style="font-style: italic; color: #4a5568; font-size: 0.9rem;">"{row['Observacao']}"</div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("Nenhum registro encontrado para este aluno. Seja o primeiro a registrar!")
        except Exception as e:
            st.warning(f"Não foi possível carregar o histórico: {e}")
    else:
        st.write("Selecione um aluno para ver o histórico.")
