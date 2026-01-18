import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
import plotly.express as px # Biblioteca gráfica poderosa (já vem no Streamlit Cloud geralmente)

# ==============================================================================
# 1. CONFIGURAÇÃO
# ==============================================================================
st.set_page_config(page_title="Avaliação por Rubrica", page_icon="📊", layout="wide")

st.title("📊 Monitoramento de Resultados (Rubrica Dinâmica)")
st.markdown("Visualize a evolução do aluno baseada nas evidências coletadas no dia a dia.")

# ==============================================================================
# 2. CONEXÃO E PROCESSAMENTO DE DADOS
# ==============================================================================
@st.cache_resource
def conectar_banco():
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        credentials = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scope)
        client = gspread.authorize(credentials)
        return client.open("Omnisfera_Dados")
    except Exception as e:
        return None

def carregar_dados_diario(sh):
    """Lê as evidências do Diário de Bordo"""
    try:
        ws = sh.worksheet("Diario_Bordo")
        dados = ws.get_all_records()
        df = pd.DataFrame(dados)
        return df
    except:
        return pd.DataFrame()

# Conexão
sh = conectar_banco()
if not sh:
    st.error("Erro de conexão com a planilha.")
    st.stop()

df_diario = carregar_dados_diario(sh)

if df_diario.empty:
    st.info("📭 Ainda não há dados suficientes no Diário de Bordo para gerar relatórios.")
    st.markdown("Vá para a página **Diário de Bordo** e registre algumas validações primeiro.")
    st.stop()

# ==============================================================================
# 3. FILTROS
# ==============================================================================
# Tenta achar a coluna de Aluno (pode variar entre 'Aluno', 'Aluno_Nome', etc)
col_aluno = next((c for c in df_diario.columns if 'aluno' in str(c).lower()), None)

if not col_aluno:
    st.error("Não encontrei a coluna de Aluno na planilha.")
    st.stop()

lista_alunos = df_diario[col_aluno].unique()
aluno_selecionado = st.selectbox("Selecione o Estudante:", lista_alunos)

# Filtra dados do aluno
df_aluno = df_diario[df_diario[col_aluno] == aluno_selecionado].copy()

if df_aluno.empty:
    st.warning("Sem registros para este aluno.")
    st.stop()

st.divider()

# ==============================================================================
# 4. RUBRICA AUTOMÁTICA (O CORAÇÃO DA PÁGINA)
# ==============================================================================

# --- Processamento Matemático ---
# Vamos converter as respostas de texto em números para poder calcular médias
# Ajuste as strings abaixo conforme o que você colocou nos botões do Diário
mapa_validacao = {
    "❌ Não funcionou": 0,
    "❌ Não": 0,
    "⚠️ Funcionou parcialmente": 5,
    "⚠️ Com Adaptação": 5,
    "⚠️ Parcial (Com ajuda)": 5,
    "✅ Sim, funcionou bem": 10,
    "✅ Sim, Perfeito": 10,
    "🚀 Sim, fluiu bem!": 10
}

# Tenta achar a coluna de Validação
col_validacao = next((c for c in df_aluno.columns if 'validacao' in str(c).lower() or 'funcionou' in str(c).lower()), None)
col_engajamento = next((c for c in df_aluno.columns if 'engajamento' in str(c).lower()), None)
col_meta = next((c for c in df_aluno.columns if 'meta' in str(c).lower()), None)

if col_validacao:
    # Cria uma coluna numérica baseada no mapa
    df_aluno['Nota_Eficacia'] = df_aluno[col_validacao].map(lambda x: mapa_validacao.get(str(x).strip(), 5)) # 5 é o padrão se não achar
    
    # MÉTRICAS GERAIS
    c1, c2, c3 = st.columns(3)
    
    qtd_atividades = len(df_aluno)
    media_eficacia = df_aluno['Nota_Eficacia'].mean()
    
    # Define o Nível da Rubrica
    if media_eficacia >= 8:
        nivel_rubrica = "🟢 ESTRATÉGIA CONSOLIDADA"
        msg_rubrica = "As estratégias do PEI estão funcionando perfeitamente."
    elif media_eficacia >= 5:
        nivel_rubrica = "🟡 ESTRATÉGIA EM DESENVOLVIMENTO"
        msg_rubrica = "O aluno responde, mas precisa de suporte contínuo."
    else:
        nivel_rubrica = "🔴 ESTRATÉGIA PRECISA DE REVISÃO"
        msg_rubrica = "As barreiras persistem. Considere mudar o recurso no PEI."

    c1.metric("Evidências Coletadas", qtd_atividades)
    c2.metric("Taxa de Sucesso do PEI", f"{media_eficacia*10:.0f}%")
    c3.info(f"**Nível Atual:**\n\n{nivel_rubrica}")

    st.markdown(f"*{msg_rubrica}*")
    st.divider()

    # --- GRÁFICOS VISUAIS ---
    col_graf1, col_graf2 = st.columns(2)

    with col_graf1:
        st.subheader("📈 Evolução Temporal")
        # Gráfico de Linha: Mostra se o aluno está melhorando ou piorando ao longo do tempo
        # Precisamos converter Data
        col_data = next((c for c in df_aluno.columns if 'data' in str(c).lower()), None)
        if col_data:
            fig_evolucao = px.line(df_aluno, x=col_data, y='Nota_Eficacia', markers=True, title="Eficácia das Atividades (0 a 10)")
            fig_evolucao.update_yaxes(range=[0, 11])
            st.plotly_chart(fig_evolucao, use_container_width=True)

    with col_graf2:
        st.subheader("🎯 Análise por Meta do PEI")
        if col_meta:
            # Agrupa por Meta e calcula média
            df_metas = df_aluno.groupby(col_meta)['Nota_Eficacia'].mean().reset_index()
            fig_bar = px.bar(df_metas, x='Nota_Eficacia', y=col_meta, orientation='h', title="Qual Meta está sendo atingida?", color='Nota_Eficacia', color_continuous_scale='RdYlGn')
            fig_bar.update_xaxes(range=[0, 10])
            st.plotly_chart(fig_bar, use_container_width=True)
        else:
            st.warning("Não foi possível identificar as Metas nos registros.")

    # --- ENGAJAMENTO (SE HOUVER) ---
    if col_engajamento:
        st.subheader("⚡ Engajamento do Aluno")
        # Transforma engajamento em numérico se necessário
        df_aluno['Engajamento_Num'] = pd.to_numeric(df_aluno[col_engajamento], errors='coerce').fillna(0)
        
        col_tipo = next((c for c in df_aluno.columns if 'origem' in str(c).lower() or 'tipo' in str(c).lower()), None)
        
        if col_tipo:
            # Compara Hub vs Manual
            fig_radar = px.box(df_aluno, x=col_tipo, y='Engajamento_Num', title="Engajamento: Hub vs Atividades Manuais", points="all")
            st.plotly_chart(fig_radar, use_container_width=True)
            st.caption("Este gráfico ajuda a decidir se vale a pena continuar usando o Hub ou se o aluno prefere outro método.")

    # --- TABELA DETALHADA (RUBRICA ANALÍTICA) ---
    st.markdown("---")
    st.subheader("📑 Detalhamento das Evidências")
    
    # Mostra uma tabela limpa apenas com o essencial
    cols_to_show = [col for col in df_aluno.columns if col not in ['ID_Registro', 'Timestamp', 'Nota_Eficacia', 'Engajamento_Num']]
    st.dataframe(df_aluno[cols_to_show], use_container_width=True)

else:
    st.warning("Não encontrei dados de validação ('Funcionou?') na planilha. Verifique se os nomes das colunas estão corretos.")
