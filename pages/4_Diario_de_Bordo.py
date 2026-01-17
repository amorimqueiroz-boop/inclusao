import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import pandas as pd
import time

# ==============================================================================
# 1. CONFIGURAÇÃO
# ==============================================================================
st.set_page_config(page_title="Diário de Bordo | Omnisfera", page_icon="📝", layout="wide")

# ==============================================================================
# 2. CONEXÃO E LEITURA (O PEI É A FONTE)
# ==============================================================================
@st.cache_resource
def conectar_banco():
    """Conecta ao Google Sheets"""
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    credentials = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scope)
    client = gspread.authorize(credentials)
    return client.open("Omnisfera_Dados")

def carregar_peis_ativos(sh):
    """Busca alunos com PEI criado na aba 'Metas_PEI'"""
    try:
        ws = sh.worksheet("Metas_PEI")
        dados = ws.get_all_records()
        df = pd.DataFrame(dados)
        # Normaliza colunas para minúsculo para evitar erros
        df.columns = [c.lower() for c in df.columns]
        return df
    except Exception as e:
        st.error(f"Erro ao ler PEIs: {e}")
        return pd.DataFrame()

def preparar_aba_diario(sh):
    """Garante que a aba de registros existe"""
    try:
        return sh.worksheet("Diario_Bordo")
    except:
        ws = sh.add_worksheet("Diario_Bordo", rows=1000, cols=10)
        ws.append_row(["Timestamp", "Data", "Professor", "Aluno", "Turma", "Meta_PEI", "Estrategia_Hub", "Atividade_Realizada", "Avaliacao", "Obs"])
        return ws

# ==============================================================================
# 3. INTERFACE
# ==============================================================================

# --- SIDEBAR ---
with st.sidebar:
    st.header("🔐 Identificação")
    if "prof_nome" not in st.session_state: st.session_state["prof_nome"] = ""
    st.session_state["prof_nome"] = st.text_input("Nome do Educador:", value=st.session_state["prof_nome"])

st.title("📝 Diário de Bordo")
st.markdown("Avaliação das estratégias do Hub de Inclusão aplicadas em sala.")

# --- CARREGAMENTO ---
try:
    sh = conectar_banco()
    df_peis = carregar_peis_ativos(sh)
    ws_diario = preparar_aba_diario(sh)
except:
    st.stop()

if df_peis.empty:
    st.warning("⚠️ Nenhum PEI encontrado. Crie um PEI primeiro.")
    st.stop()

# --- SELEÇÃO DO ALUNO ---
# Tenta identificar as colunas automaticamente
col_nome = next((c for c in df_peis.columns if 'nome' in c or 'aluno' in c), None)
col_turma = next((c for c in df_peis.columns if 'turma' in c or 'serie' in c), None)

if col_nome:
    # Cria rótulo para o selectbox
    label_col = df_peis[col_nome].astype(str)
    if col_turma:
        label_col = label_col + " - " + df_peis[col_turma].astype(str)
    
    df_peis['select_label'] = label_col
    aluno_selecao = st.selectbox("📂 Selecione o Estudante:", df_peis['select_label'].unique())

    # Pega os dados do aluno selecionado
    dados_aluno = df_peis[df_peis['select_label'] == aluno_selecao].iloc[0]
    
    # Extrai dados vitais
    nome_real = dados_aluno[col_nome]
    turma_real = dados_aluno[col_turma] if col_turma else ""
    
    # --- BUSCA INFORMAÇÕES DO HUB (Estratégias salvas no PEI) ---
    col_obj = next((c for c in df_peis.columns if 'objetivo' in c or 'meta' in c), None)
    col_est = next((c for c in df_peis.columns if 'estrat' in c or 'recurso' in c or 'hub' in c), None)
    
    meta_pei = dados_aluno[col_obj] if col_obj else "Meta não definida"
    # AQUI ESTÁ A INFORMAÇÃO DO HUB QUE VAMOS AVALIAR
    estrategia_hub = dados_aluno[col_est] if col_est else "Estratégia não definida"

else:
    st.error("Erro na leitura da planilha PEI.")
    st.stop()

st.divider()

# --- ÁREA RETRÁTIL DO PEI (NOVIDADE) ---
# Usamos st.expander para deixar fechado ou aberto
with st.expander(f"ℹ️ Ver Detalhes do PEI e Estratégias do Hub para {nome_real}", expanded=False):
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**🎯 Objetivo de Aprendizagem (PEI):**")
        st.info(meta_pei)
    with c2:
        st.markdown("**💡 Sugestão do Hub de Inclusão:**")
        st.success(estrategia_hub)
    st.caption(f"Turma: {turma_real}")

# --- FORMULÁRIO DE AVALIAÇÃO ---
st.subheader("📍 Avaliação da Estratégia")

with st.form("form_avaliacao"):
    # Mostramos a estratégia do Hub novamente aqui para contexto imediato
    st.markdown(f"**Estratégia Avaliada:** _{estrategia_hub}_")
    
    atividade = st.text_input("Como essa estratégia foi aplicada hoje?", placeholder="Ex: Fizemos o jogo sugerido, mas em grupo...")
    
    st.markdown("---")
    st.markdown("**A estratégia do Hub funcionou para este aluno?**")
    
    # Avaliação focada na eficácia do recurso
    avaliacao = st.select_slider(
        "Nível de Resposta do Aluno:",
        options=["🔴 Não Funcionou/Recusou", "🟠 Funcionou com muito suporte", "🟡 Funcionou com pouco suporte", "🟢 Funcionou Perfeitamente"],
        value="🟡 Funcionou com pouco suporte"
    )
    
    obs = st.text_area("Observações / Ajustes necessários:", height=80, placeholder="O aluno engajou? O material precisa ser maior? Menor?")
    
    enviar = st.form_submit_button("💾 Salvar Avaliação", type="primary", use_container_width=True)

    if enviar:
        if not st.session_state["prof_nome"]:
            st.error("Identifique-se na barra lateral.")
        elif not atividade:
            st.error("Descreva como aplicou a estratégia.")
        else:
            with st.spinner("Registrando avaliação..."):
                nova_linha = [
                    str(datetime.now().timestamp()),
                    datetime.now().strftime("%d/%m/%Y"),
                    st.session_state["prof_nome"],
                    nome_real,
                    str(turma_real),
                    str(meta_pei),
                    str(estrategia_hub), # Salvamos o que foi avaliado
                    atividade,
                    avaliacao,
                    obs
                ]
                ws_diario.append_row(nova_linha)
                st.success("✅ Avaliação salva com sucesso!")
                time.sleep(1)
                st.rerun()

# --- HISTÓRICO VISUAL ---
st.markdown("---")
st.subheader("📅 Últimas Avaliações")

try:
    df_hist = pd.DataFrame(ws_diario.get_all_records())
    if not df_hist.empty and "Aluno" in df_hist.columns:
        hist_aluno = df_hist[df_hist["Aluno"] == nome_real].tail(3).iloc[::-1]
        
        if hist_aluno.empty:
            st.info("Nenhuma avaliação registrada ainda.")
        
        for i, row in hist_aluno.iterrows():
            status = row.get('Avaliacao', '')
            cor = "#dcfce7" if "Perfeitamente" in status else "#fee2e2" if "Não" in status else "#fef9c3"
            
            st.markdown(f"""
            <div style="background-color: {cor}; padding: 12px; border-radius: 8px; margin-bottom: 8px; border: 1px solid #ddd;">
                <div style="font-weight:bold; font-size:0.9rem;">{row.get('Data', '')} - {row.get('Atividade_Realizada', '')}</div>
                <div style="font-size:0.85rem; margin-top:4px;"><i>Estratégia: {row.get('Estrategia_Hub', '')}</i></div>
                <div style="margin-top:5px; font-weight:bold;">{status}</div>
            </div>
            """, unsafe_allow_html=True)
except:
    pass
