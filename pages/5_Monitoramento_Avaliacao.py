import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
import plotly.express as px

# ==============================================================================
# 1. CONFIGURAÇÃO E CONEXÃO
# ==============================================================================
st.set_page_config(page_title="Avaliação por Rubrica", page_icon="📊", layout="wide")

st.title("📊 Painel de Resultados (Rubrica Automática)")
st.markdown("Diagnóstico baseado nas validações diárias dos professores.")

@st.cache_resource
def conectar_banco():
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        credentials = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scope)
        client = gspread.authorize(credentials)
        return client.open("Omnisfera_Dados")
    except Exception as e:
        st.error(f"Erro de conexão: {e}")
        return None

# Conecta e carrega dados
sh = conectar_banco()
if not sh: st.stop()

try:
    ws = sh.worksheet("Diario_Bordo")
    dados = ws.get_all_records()
    df = pd.DataFrame(dados)
except:
    st.warning("Ainda não há dados no Diário de Bordo para analisar.")
    st.stop()

if df.empty:
    st.info("O Diário de Bordo está vazio. Comece a validar atividades para ver os gráficos.")
    st.stop()

# ==============================================================================
# 2. FILTROS
# ==============================================================================
# Identifica coluna de aluno
col_aluno = next((c for c in df.columns if 'aluno' in c.lower()), None)
if not col_aluno:
    st.error("Erro: Não encontrei a coluna de Aluno na planilha.")
    st.stop()

lista_alunos = df["Aluno"].unique()
aluno_selecionado = st.selectbox("Selecione o Estudante:", lista_alunos)

# Filtra dados do aluno
df_aluno = df[df["Aluno"] == aluno_selecionado].copy()

if df_aluno.empty:
    st.warning("Sem registros para este aluno.")
    st.stop()

st.divider()

# ==============================================================================
# 3. CÁLCULO DA RUBRICA (A MÁGICA)
# ==============================================================================

# Mapa de Conversão: Texto -> Nota (0 a 10)
# Ajustado para os textos que usamos no Diário
mapa_notas = {
    # Respostas do Calendário/Hub
    "🚀 Sim, fluiu bem!": 10,
    "✅ Sim, Perfeito": 10,
    "✅ Sim": 10,
    "⚠️ Parcial (Com ajuda)": 6,
    "⚠️ Com Adaptação": 6,
    "❌ Não funcionou": 2,
    "❌ Não": 2,
    # Respostas antigas (caso tenha)
    "🟢 Independente": 10,
    "🟡 Ajuda Parcial": 7,
    "🟠 Ajuda Total": 4,
    "🔴 Não Realizou": 0
}

# Procura a coluna de Validação/Resultado
col_resultado = next((c for c in df_aluno.columns if 'funcionou' in c.lower() or 'valida' in c.lower() or 'resultado' in c.lower()), None)

if col_resultado:
    # Cria coluna de Nota Numérica
    df_aluno['Nota_Calculada'] = df_aluno[col_resultado].map(lambda x: mapa_notas.get(str(x).strip(), 5))
    
    # 1. MÉTRICAS DE TOPO
    media = df_aluno['Nota_Calculada'].mean()
    total_atividades = len(df_aluno)
    taxa_sucesso = len(df_aluno[df_aluno['Nota_Calculada'] >= 7])
    
    # Define o Diagnóstico (Rubrica)
    if media >= 8:
        nivel = "🟢 CONSOLIDADO"
        msg = "O aluno responde muito bem às estratégias atuais."
    elif media >= 5:
        nivel = "🟡 EM CONSTRUÇÃO"
        msg = "Há progresso, mas o aluno ainda depende de muito suporte/adaptação."
    else:
        nivel = "🔴 NECESSITA REVISÃO DO PEI"
        msg = "As estratégias atuais não estão funcionando. É hora de pivotar."

    c1, c2, c3 = st.columns(3)
    c1.metric("Atividades Validadas", total_atividades)
    c2.metric("Eficácia Média", f"{media:.1f}/10")
    c3.metric("Nível Atual", nivel)
    
    st.info(f"💡 **Diagnóstico:** {msg}")
    
    st.divider()

    # 2. GRÁFICOS
    g1, g2 = st.columns(2)
    
    with g1:
        st.subheader("📈 Evolução da Autonomia")
        # Tenta achar coluna de data
        col_data = next((c for c in df_aluno.columns if 'data' in c.lower()), None)
        if col_data:
            fig = px.line(df_aluno, x=col_data, y='Nota_Calculada', markers=True, 
                          title="Histórico de Validação (0=Falha, 10=Sucesso)")
            fig.update_yaxes(range=[0, 11])
            st.plotly_chart(fig, use_container_width=True)
            
    with g2:
        st.subheader("🤖 Impacto do Hub")
        # Vamos verificar se a descrição diz que veio do HUB
        # Procura coluna de atividade/descrição
        col_desc = next((c for c in df_aluno.columns if 'atividade' in c.lower() or 'desc' in c.lower()), None)
        
        if col_desc:
            # Cria categoria simples
            df_aluno['Origem'] = df_aluno[col_desc].apply(lambda x: 'HUB/IA' if '[HUB]' in str(x) or 'Hub' in str(x) else 'Manual')
            
            # Compara as médias
            df_comp = df_aluno.groupby('Origem')['Nota_Calculada'].mean().reset_index()
            
            fig_bar = px.bar(df_comp, x='Origem', y='Nota_Calculada', 
                             title="Eficácia: Hub vs Manual", color='Origem',
                             range_y=[0, 11])
            st.plotly_chart(fig_bar, use_container_width=True)
            st.caption("Este gráfico mostra se as atividades do Hub funcionam melhor que as manuais.")

else:
    st.warning("Não consegui identificar a coluna de resultados ('Funcionou?') na planilha.")

# 3. TABELA ANALÍTICA
st.markdown("---")
st.subheader("📑 Detalhamento das Evidências")
st.dataframe(df_aluno, use_container_width=True)
