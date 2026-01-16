import streamlit as st
import pandas as pd
from services import buscar_logs
import plotly.express as px # Biblioteca de gráficos bonitos

st.set_page_config(page_title="Monitoramento", page_icon="📊", layout="wide")

st.title("📊 Avaliação e Correção de Rota")

# 1. Carregar Dados
df = buscar_logs()

if df.empty:
    st.warning("Ainda não há dados suficientes na planilha para gerar gráficos.")
    st.stop()

# 2. Filtros (Sidebar)
with st.sidebar:
    st.header("Filtros")
    # Pega lista única de alunos que têm registro
    lista_alunos = df["aluno_nome"].unique() if "aluno_nome" in df.columns else []
    
    if len(lista_alunos) > 0:
        aluno_selecionado = st.selectbox("Selecione o Aluno:", lista_alunos)
    else:
        aluno_selecionado = None

# 3. Painel Principal
if aluno_selecionado:
    # Filtra apenas os dados desse aluno
    df_aluno = df[df["aluno_nome"] == aluno_selecionado]
    
    # Métricas de Topo
    total_atividades = len(df_aluno)
    # Conta quantos sucessos (ajuste o texto conforme o que salvamos no checkin)
    sucessos = len(df_aluno[df_aluno["resultado"].str.contains("Sucesso", na=False)])
    dificuldades = len(df_aluno[df_aluno["resultado"].str.contains("Dificuldade", na=False)])
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Atividades Realizadas", total_atividades)
    col2.metric("Sucesso/Autonomia", sucessos)
    col3.metric("Pontos de Atenção", dificuldades, delta_color="inverse")

    st.divider()

    # --- CORREÇÃO DE ROTA (A Lógica Inteligente) ---
    st.subheader("🚨 Radar de Correção de Rota")
    
    # Se tiver muitas dificuldades recentes, avisa
    if dificuldades > 0:
        # Pega os ultimos 3 registros
        ultimos = df_aluno.tail(3)
        falhas_recentes = len(ultimos[ultimos["resultado"].str.contains("Dificuldade", na=False)])
        
        if falhas_recentes >= 2:
            st.error(f"⚠️ **ALERTA DE ROTA:** O aluno apresentou dificuldade em {falhas_recentes} das últimas 3 atividades.")
            with st.expander("Ver Sugestão da Ominisfera", expanded=True):
                st.write("Sugestão: As estratégias atuais podem não estar funcionando. Considere:")
                st.markdown("- [ ] Reduzir a carga de leitura.")
                st.markdown("- [ ] Alterar o suporte (de Visual para Auditivo).")
                st.button("Revisar PEI deste Aluno")
        else:
            st.success("O aluno está evoluindo dentro do esperado. Mantenha a estratégia.")
    else:
        st.success("Nenhuma barreira crítica detectada recentemente.")

    # --- GRÁFICOS ---
    c1, c2 = st.columns([2, 1])
    
    with c1:
        st.subheader("Evolução Temporal")
        # Gráfico simples de linha ou barra
        if "data_hora" in df_aluno.columns:
            st.bar_chart(df_aluno, x="data_hora", y="resultado")
            
    with c2:
        st.subheader("Distribuição")
        # Gráfico de Pizza simples
        contagem = df_aluno["resultado"].value_counts()
        st.write(contagem)

    # --- TABELA DETALHADA ---
    st.subheader("Histórico Completo (Anamnese)")
    st.dataframe(df_aluno[["data_hora", "disciplina", "atividade_resumo", "resultado", "observacao"]])

else:
    st.info("Selecione um aluno na barra lateral para ver o dossiê.")
