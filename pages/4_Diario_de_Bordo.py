import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime, date
import pandas as pd
import time

# ==============================================================================
# 1. CONFIGURAÇÃO E CONEXÃO
# ==============================================================================
st.set_page_config(page_title="Calendário de Validação", page_icon="📅", layout="wide")

@st.cache_resource
def conectar_banco():
    """Conecta ao Google Sheets"""
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        credentials = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scope)
        client = gspread.authorize(credentials)
        return client.open("Omnisfera_Dados")
    except Exception as e:
        st.error(f"Erro de conexão: {e}")
        return None

def garantir_abas(sh):
    """
    Garante que temos as abas necessárias:
    1. Logs_Hub: Onde o Hub salva automaticamente o que gerou (Meta-dados).
    2. Diario_Bordo: Onde o professor salva o feedback.
    """
    try:
        # Aba de LOGS DO HUB (Onde o sistema escreve sozinho)
        try:
            sh.worksheet("Logs_Hub")
        except:
            ws = sh.add_worksheet("Logs_Hub", 1000, 10)
            ws.append_row(["Timestamp", "Data", "Aluno", "Tipo_Recurso", "Qtd_Gerada", "Descricao", "Status_Validacao"])

        # Aba de DIÁRIO (Onde o professor valida)
        try:
            ws_diario = sh.worksheet("Diario_Bordo")
        except:
            ws_diario = sh.add_worksheet("Diario_Bordo", 1000, 10)
            ws_diario.append_row(["Timestamp", "Data_Validacao", "Professor", "Aluno", "Atividade_Ref_Hub", "Funcionou?", "Obs"])
            
        return sh.worksheet("Logs_Hub"), ws_diario
    except Exception as e:
        st.error(f"Erro ao criar abas: {e}")
        return None, None

def carregar_peis(sh):
    try:
        ws = sh.worksheet("Metas_PEI")
        df = pd.DataFrame(ws.get_all_records())
        df.columns = [str(c).lower().strip() for c in df.columns]
        return df
    except:
        return pd.DataFrame()

# ==============================================================================
# 2. INTERFACE (CALENDÁRIO & VALIDAÇÃO)
# ==============================================================================

# --- SIDEBAR: LOGIN ---
with st.sidebar:
    st.header("👤 Educador")
    if "prof_nome" not in st.session_state: st.session_state["prof_nome"] = ""
    st.session_state["prof_nome"] = st.text_input("Seu Nome:", value=st.session_state["prof_nome"])
    st.divider()
    st.info("📅 **Conceito:** Selecione o dia no calendário para ver o que o Hub gerou e validar se funcionou.")

st.title("📅 Calendário de Validação")

# --- CONEXÃO ---
sh = conectar_banco()
if not sh: st.stop()

ws_hub, ws_diario = garantir_abas(sh)
df_peis = carregar_peis(sh)

if df_peis.empty:
    st.warning("⚠️ Nenhum aluno com PEI encontrado.")
    st.stop()

# --- 1. SELEÇÃO DE ALUNO ---
col_aluno, col_data = st.columns([1, 1])

with col_aluno:
    # Identifica colunas de nome
    col_nome = next((c for c in df_peis.columns if 'nome' in c or 'aluno' in c), None)
    if col_nome:
        # Cria lista de alunos
        lista_alunos = df_peis[col_nome].unique()
        aluno_selecionado = st.selectbox("Estudante:", lista_alunos)
        
        # Pega dados do PEI para o Expander
        dados_aluno = df_peis[df_peis[col_nome] == aluno_selecionado].iloc[0]
        meta_pei = str(dados_aluno.get('objetivos_gerais', 'Não definida'))
        estrategia_pei = str(dados_aluno.get('estrategias', 'Não definida'))
    else:
        st.error("Erro na planilha PEI.")
        st.stop()

with col_data:
    # CALENDÁRIO VISUAL
    data_selecionada = st.date_input("Data da Aula:", value=date.today())
    data_str = data_selecionada.strftime("%d/%m/%Y")

# --- 2. PEI RECOLHIDO (EXPANDER) ---
# Fica sutil no topo, abre só se quiser ver
with st.expander(f"🎯 Ver Meta do PEI para {aluno_selecionado}", expanded=False):
    st.info(f"**Meta:** {meta_pei}")
    st.markdown(f"**Estratégia Base:** {estrategia_pei}")

st.divider()

# --- 3. LISTA DE ATIVIDADES DO HUB (SIMULAÇÃO DE LEITURA) ---
# Aqui o sistema busca na aba 'Logs_Hub' o que foi gerado para esse aluno nessa data
st.subheader(f"🤖 O que o Hub criou em {data_str}?")

# (Simulação: Vamos tentar ler da planilha, se não tiver nada, mostra mensagem)
try:
    df_hub = pd.DataFrame(ws_hub.get_all_records())
    
    # Filtra: Aluno + Data (Assumindo formato dd/mm/aaaa)
    # Obs: Num sistema real, trataríamos datas com mais rigor
    atividades_do_dia = pd.DataFrame()
    if not df_hub.empty:
        # Filtra pelo nome (convertendo para string para segurança)
        filtro_aluno = df_hub[df_hub["Aluno"].astype(str) == aluno_selecionado]
        # Tenta filtrar pela data (pode conter hora, então pegamos string parcial ou dia)
        # Simplificação: Filtramos se a string da data contém a data selecionada
        atividades_do_dia = filtro_aluno[filtro_aluno["Data"].astype(str).str.contains(data_str)]
except:
    atividades_do_dia = pd.DataFrame()

# SE NÃO TIVER NADA AUTOMÁTICO, PERMITE INSERÇÃO MANUAL RÁPIDA
if atividades_do_dia.empty:
    st.caption("Nenhuma atividade automática encontrada para esta data.")
    
    # Card de "Atividade Manual" caso o Hub não tenha sido usado
    with st.container():
        st.markdown(f"""
        <div style="border: 1px dashed #ccc; padding: 15px; border-radius: 10px; background-color: #fafafa;">
            <strong style="color: #666;">Registro Manual</strong><br>
            <small>O Hub não registrou atividades hoje. O que você aplicou?</small>
        </div>
        """, unsafe_allow_html=True)
        
        with st.form("form_manual"):
            atividade_manual = st.text_input("Resumo da Atividade:", placeholder="Ex: 5 Questões adaptadas de Geografia...")
            
            # AVALIAÇÃO SIMPLIFICADA (BOTÕES)
            st.write("Funcinou?")
            col_b1, col_b2, col_b3 = st.columns(3)
            
            # Usando Radio horizontal como se fossem botões
            avaliacao = st.radio("Avaliação:", 
                     ["🚀 Sim, fluiu bem!", "⚠️ Parcial (Com ajuda)", "❌ Não funcionou"],
                     horizontal=True, label_visibility="collapsed")
            
            obs = st.text_input("Obs rápida (Opcional):")
            
            if st.form_submit_button("✅ Validar Atividade"):
                if not st.session_state["prof_nome"]:
                    st.error("Identifique-se.")
                else:
                    ws_diario.append_row([
                        str(datetime.now()), 
                        data_str, 
                        st.session_state["prof_nome"], 
                        aluno_selecionado, 
                        atividade_manual, 
                        avaliacao, 
                        obs
                    ])
                    st.success("Registrado!")
                    time.sleep(1)
                    st.rerun()

else:
    # SE TIVER ATIVIDADES DO HUB, MOSTRA COMO CARDS PARA VALIDAR
    for idx, row in atividades_do_dia.iterrows():
        descricao = row.get('Descricao', 'Sem descrição')
        tipo = row.get('Tipo_Recurso', 'Recurso')
        qtd = row.get('Qtd_Gerada', '-')
        
        # O Card Visual
        st.markdown(f"""
        <div style="border-left: 5px solid #3b82f6; background-color: #eff6ff; padding: 15px; border-radius: 5px; margin-bottom: 10px;">
            <div style="font-weight: bold; color: #1e3a8a;">{tipo} ({qtd})</div>
            <div style="color: #4b5563;">{descricao}</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Botões de Ação para validar ESTA atividade específica
        with st.expander(f"Validar: {tipo}", expanded=True):
            with st.form(f"validar_{idx}"):
                st.write("**O recurso funcionou para o aluno?**")
                
                res_val = st.select_slider("Resultado:", 
                                         options=["❌ Não", "⚠️ Com Adaptação", "✅ Sim, Perfeito"],
                                         value="✅ Sim, Perfeito")
                
                obs_val = st.text_input("Observação (se houver):")
                
                if st.form_submit_button("💾 Confirmar Validação"):
                    # Salva no Diário
                    ws_diario.append_row([
                        str(datetime.now()), 
                        data_str, 
                        st.session_state["prof_nome"], 
                        aluno_selecionado, 
                        f"[HUB] {tipo} - {descricao}", 
                        res_val, 
                        obs_val
                    ])
                    st.success("Validado!")
                    time.sleep(1)
                    st.rerun()

# --- 4. HISTÓRICO DO MÊS (VISUALIZAÇÃO DE CALENDÁRIO) ---
st.divider()
st.subheader("🗓️ Visão do Mês")

try:
    df_logs = pd.DataFrame(ws_diario.get_all_records())
    if not df_logs.empty:
        # Filtra pelo aluno
        logs_aluno = df_logs[df_logs["Aluno"] == aluno_selecionado]
        
        if not logs_aluno.empty:
            # Exibe como uma tabelinha limpa
            st.dataframe(
                logs_aluno[["Data_Validacao", "Atividade_Ref_Hub", "Funcionou?", "Obs"]],
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("Nenhuma validação neste período.")
except:
    pass
