import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import pandas as pd
import time

# ==============================================================================
# 1. CONFIGURAÇÃO DA PÁGINA
# ==============================================================================
st.set_page_config(page_title="Diário de Bordo | Omnisfera", page_icon="📝", layout="wide")

# ==============================================================================
# 2. CONEXÃO E LEITURA (O CORAÇÃO DO SISTEMA)
# ==============================================================================
@st.cache_resource
def conectar_banco():
    """Conecta ao Google Sheets usando os segredos do Streamlit"""
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    credentials = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scope)
    client = gspread.authorize(credentials)
    return client.open("Omnisfera_Dados")

def carregar_peis_ativos(sh):
    """
    Busca APENAS os alunos que já possuem PEI salvo na aba 'Metas_PEI'.
    Essa é a nossa Fonte da Verdade.
    """
    try:
        ws = sh.worksheet("Metas_PEI")
        # Pega todos os registros como lista de dicionários
        dados = ws.get_all_records()
        df = pd.DataFrame(dados)
        
        # Garante que as colunas essenciais existem (normaliza nomes)
        # Se na planilha estiver 'Aluno' ou 'Nome', padronizamos para facilitar
        df.columns = [c.lower() for c in df.columns]
        
        return df
    except Exception as e:
        # Se a aba não existir ou der erro, retorna vazio
        st.error(f"Erro ao ler PEIs: {e}")
        return pd.DataFrame()

def preparar_aba_diario(sh):
    """Garante que a aba de registros existe"""
    try:
        return sh.worksheet("Diario_Bordo")
    except:
        # Cria a aba se não existir
        ws = sh.add_worksheet("Diario_Bordo", rows=1000, cols=10)
        ws.append_row(["Timestamp", "Data", "Professor", "Aluno", "Turma", "Meta_PEI", "Estrategia_PEI", "Atividade_Do_Dia", "Avaliacao", "Obs"])
        return ws

# ==============================================================================
# 3. INTERFACE DO PROFESSOR
# ==============================================================================

# --- BARRA LATERAL (IDENTIFICAÇÃO) ---
with st.sidebar:
    st.header("🔐 Acesso do Educador")
    if "prof_nome" not in st.session_state: st.session_state["prof_nome"] = ""
    st.session_state["prof_nome"] = st.text_input("Seu Nome:", value=st.session_state["prof_nome"])

st.title("📝 Diário de Bordo & Registro")
st.markdown("Registro da aplicação prática das metas definidas no PEI.")

# --- CARREGAMENTO DE DADOS ---
try:
    sh = conectar_banco()
    df_peis = carregar_peis_ativos(sh)
    ws_diario = preparar_aba_diario(sh)
except Exception as e:
    st.error("Erro de conexão com o Banco de Dados. Verifique os Segredos.")
    st.stop()

# Verifica se tem PEIs cadastrados
if df_peis.empty:
    st.warning("⚠️ Nenhum PEI encontrado no sistema.")
    st.info("O aluno só aparecerá aqui depois que você criar o PEI dele no módulo 'Plano Educacional'.")
    st.stop()

# --- SELEÇÃO DO ALUNO (Baseado nos PEIs existentes) ---
# Cria uma coluna de "Rótulo" para facilitar a seleção (Nome - Turma)
# Tenta achar as colunas certas, usando 'aluno_nome' (padrão que definimos antes) ou similar
col_nome = next((c for c in df_peis.columns if 'nome' in c or 'aluno' in c), None)
col_turma = next((c for c in df_peis.columns if 'turma' in c or 'série' in c or 'serie' in c), None)

if col_nome:
    # Cria lista para o Selectbox
    if col_turma:
        df_peis['label_select'] = df_peis[col_nome].astype(str) + " (" + df_peis[col_turma].astype(str) + ")"
    else:
        df_peis['label_select'] = df_peis[col_nome].astype(str)
        
    aluno_selecao = st.selectbox("📂 Selecione o Estudante (PEI Ativo):", df_peis['label_select'].unique())
    
    # Recupera os dados daquele aluno específico
    dados_aluno = df_peis[df_peis['label_select'] == aluno_selecao].iloc[0]
    
    # Extrai informações para salvar depois
    nome_real = dados_aluno[col_nome]
    turma_real = dados_aluno[col_turma] if col_turma else "Não inf."
    
    # Tenta pegar Objetivos e Estratégias (procura colunas com esses nomes)
    col_obj = next((c for c in df_peis.columns if 'objetivo' in c or 'meta' in c), None)
    col_est = next((c for c in df_peis.columns if 'estrat' in c or 'recurso' in c), None)
    
    meta_atual = dados_aluno[col_obj] if col_obj else "Meta não localizada no PEI"
    estrategia_atual = dados_aluno[col_est] if col_est else "Estratégia não localizada"

else:
    st.error("A planilha de PEI não tem uma coluna de 'Nome' identificável.")
    st.stop()

st.divider()

# --- ÁREA PRINCIPAL: VISUALIZAÇÃO E REGISTRO ---
col_pei, col_registro = st.columns([1, 1.5])

with col_pei:
    st.subheader("🎯 O que foi planejado (PEI)")
    st.info(f"**Meta Principal:**\n{meta_atual}")
    st.markdown(f"**Estratégia/Recurso Sugerido:**\n{estrategia_atual}")
    st.caption(f"Turma: {turma_real}")

with col_registro:
    st.subheader("📍 O que foi feito hoje?")
    
    with st.form("diario_form"):
        # Descrição da aula
        atividade = st.text_input("Atividade Realizada:", placeholder="Ex: Adaptação da atividade de Frações usando LEGO...")
        
        st.write("---")
        st.markdown("**Avaliação da Execução:**")
        
        # Slider de Avaliação (Mais visual)
        avaliacao = st.select_slider(
            "Nível de Suporte Necessário:",
            options=["🔴 Não Realizou", "🟠 Ajuda Total (Física)", "🟡 Ajuda Parcial (Verbal)", "🟢 Independente"],
            value="🟡 Ajuda Parcial (Verbal)"
        )
        
        obs = st.text_area("Observações (Opcional):", placeholder="Como o aluno reagiu? O que precisa ajustar?", height=80)
        
        enviar = st.form_submit_button("💾 Salvar Registro", type="primary", use_container_width=True)
        
        if enviar:
            if not st.session_state["prof_nome"]:
                st.error("⚠️ Por favor, identifique-se na barra lateral.")
            elif not atividade:
                st.error("⚠️ Descreva a atividade realizada.")
            else:
                with st.spinner("Salvando no histórico..."):
                    # Prepara a linha para salvar
                    nova_linha = [
                        str(datetime.now().timestamp()),          # ID
                        datetime.now().strftime("%d/%m/%Y"),      # Data
                        st.session_state["prof_nome"],            # Prof
                        nome_real,                                # Aluno
                        str(turma_real),                          # Turma
                        str(meta_atual),                          # Contexto (Meta)
                        str(estrategia_atual),                    # Contexto (Estratégia)
                        atividade,                                # O que foi feito
                        avaliacao,                                # Resultado
                        obs                                       # Obs
                    ]
                    
                    # Envia para o Google Sheets
                    ws_diario.append_row(nova_linha)
                    
                    st.success("✅ Registro salvo com sucesso!")
                    time.sleep(1)
                    st.rerun()

# --- HISTÓRICO RECENTE ---
st.divider()
st.subheader(f"📅 Histórico de {nome_real}")

try:
    # Lê a aba de diário para mostrar o histórico
    dados_hist = ws_diario.get_all_records()
    df_hist = pd.DataFrame(dados_hist)
    
    if not df_hist.empty and "Aluno" in df_hist.columns:
        # Filtra pelo aluno atual e pega os 3 últimos
        historico_aluno = df_hist[df_hist["Aluno"] == nome_real].tail(3).iloc[::-1]
        
        if historico_aluno.empty:
            st.caption("Nenhum registro anterior encontrado.")
        
        for i, row in historico_aluno.iterrows():
            # Define corzinha do card
            status = row.get('Avaliacao', '')
            cor = "#dcfce7" if "Independente" in status else "#fee2e2" if "Não" in status else "#fef9c3"
            
            st.markdown(f"""
            <div style="background-color: {cor}; padding: 10px; border-radius: 8px; margin-bottom: 10px; border: 1px solid #ddd;">
                <small><b>{row.get('Data', '')}</b> | Prof. {row.get('Professor', '')}</small><br>
                <div style="font-weight:bold; margin-top:5px;">{row.get('Atividade_Do_Dia', 'Atividade')}</div>
                <div>{status}</div>
                <small style="color:#555">"{row.get('Obs', '')}"</small>
            </div>
            """, unsafe_allow_html=True)
            
    else:
        st.caption("Ainda não há registros no sistema.")

except Exception as e:
    st.write("Histórico indisponível no momento.")
