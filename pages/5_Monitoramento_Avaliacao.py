import streamlit as st
import pandas as pd
# Tenta importar as funções. Se der erro, avisa amigavelmente.
try:
    from services import buscar_logs
except ImportError:
    st.error("Erro: O arquivo 'services.py' não foi encontrado na raiz do projeto.")
    st.stop()

st.set_page_config(page_title="Monitoramento", page_icon="📊", layout="wide")

st.title("📊 Painel de Avaliação & Anamnese")
st.markdown("Visualize o progresso dos alunos e identifique onde corrigir a rota.")

# 1. Carregar Dados da Planilha
with st.spinner("Buscando dados atualizados..."):
    df = buscar_logs()

# Verifica se a planilha está vazia ou com erro
if df.empty or "aluno_nome" not in df.columns:
    st.info("👋 Olá! Ainda não há dados suficientes na planilha.")
    st.markdown("Vá até o **Diário de Bordo** e faça alguns registros de teste para ver os gráficos aparecerem aqui.")
    st.stop()

# 2. Filtros (Barra Lateral)
with st.sidebar:
    st.header("🔍 Filtros")
    # Pega a lista de alunos única
    alunos = df["aluno_nome"].unique()
    aluno_selecionado = st.selectbox("Selecione o Aluno:", alunos)

# 3. Análise do Aluno
if aluno_selecionado:
    # Filtra só as linhas desse aluno
    dados_aluno = df[df["aluno_nome"] == aluno_selecionado]
    
    # --- MÉTRICAS ---
    col1, col2, col3 = st.columns(3)
    
    total = len(dados_aluno)
    # Conta quantos sucessos (procura a palavra 'Sucesso' ou 'Fluiu')
    sucessos = len(dados_aluno[dados_aluno["resultado"].str.contains("Sucesso|Fluiu", case=False, na=False)])
    # Conta dificuldades
    dificuldades = len(dados_aluno[dados_aluno["resultado"].str.contains("Dificuldade|Não realizou", case=False, na=False)])
    
    col1.metric("Atividades Registradas", total)
    col2.metric("Autonomia/Sucesso", sucessos)
    col3.metric("Pontos de Atenção", dificuldades, delta_color="inverse")
    
    st.divider()
    
    # --- ALERTA DE ROTA (INTELIGÊNCIA) ---
    st.subheader("🚨 Radar de Intervenção")
    
    # Lógica: Se mais de 50% das últimas atividades foram difíceis
    if dificuldades > 0:
        ultimas_3 = dados_aluno.tail(3)
        falhas_recentes = len(ultimas_3[ultimas_3["resultado"].str.contains("Dificuldade|Não", case=False, na=False)])
        
        if falhas_recentes >= 2:
            st.error(f"⚠️ **ATENÇÃO:** O aluno apresentou dificuldade em {falhas_recentes} das últimas 3 atividades.")
            with st.expander("💡 Sugestões da Ominisfera (Clique para abrir)", expanded=True):
                st.write("**O padrão indica barreira na execução. Tente:**")
                st.markdown("1. Quebrar a atividade em passos menores.")
                st.markdown("2. Mudar o suporte de entrada (ex: se usou texto, tente vídeo).")
                st.markdown("3. Verificar se há fatores ambientais (barulho, luz).")
        else:
            st.success("✅ O aluno está progredindo bem. Nenhuma intervenção urgente necessária.")
    else:
        st.success("✅ O aluno está progredindo bem. Nenhuma intervenção urgente necessária.")

    # --- GRÁFICOS E TABELA ---
    c1, c2 = st.columns([2, 1])
    
    with c1:
        st.subheader("Histórico Detalhado")
        # Mostra a tabela limpa
        st.dataframe(dados_aluno[["data_hora", "disciplina", "resultado", "observacao"]], use_container_width=True)
        
    with c2:
        st.subheader("Distribuição")
        # Gráfico simples
        if not dados_aluno.empty:
            contagem = dados_aluno["resultado"].value_counts()
            st.bar_chart(contagem)

else:
    st.warning("Selecione um aluno para começar.")
