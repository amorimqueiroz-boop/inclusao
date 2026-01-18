import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import pandas as pd
import time

# ==============================================================================
# 1. CONFIGURAÇÃO E CONEXÃO
# ==============================================================================
st.set_page_config(page_title="Diário & Feedback", page_icon="📝", layout="wide")

@st.cache_resource
def conectar_banco():
    """Conecta ao Google Sheets com tratamento de erro"""
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        credentials = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scope)
        client = gspread.authorize(credentials)
        return client.open("Omnisfera_Dados")
    except Exception as e:
        st.error(f"Erro fatal de conexão: {e}")
        return None

def carregar_peis(sh):
    """Lê as metas definidas no PEI"""
    try:
        ws = sh.worksheet("Metas_PEI")
        dados = ws.get_all_records()
        df = pd.DataFrame(dados)
        # Padroniza colunas para minúsculo
        df.columns = [str(c).lower().strip() for c in df.columns]
        return df
    except:
        return pd.DataFrame()

def preparar_aba_diario(sh):
    """Prepara a aba de destino garantindo que ela aceita os dados"""
    try:
        return sh.worksheet("Diario_Bordo")
    except:
        # Se não existir, cria com as colunas exatas que vamos usar
        ws = sh.add_worksheet("Diario_Bordo", rows=1000, cols=11)
        ws.append_row([
            "ID", "Data_Hora", "Professor", "Aluno", "Turma", 
            "Meta_PEI", "Estrategia_Base", "Atividade_Hub", 
            "Avaliacao_Suporte", "Observacao", "Status_Integracao"
        ])
        return ws

# ==============================================================================
# 2. INTERFACE
# ==============================================================================

# --- SIDEBAR ---
with st.sidebar:
    st.header("Identificação")
    if "prof_nome" not in st.session_state: st.session_state["prof_nome"] = ""
    st.session_state["prof_nome"] = st.text_input("Educador:", value=st.session_state["prof_nome"])

st.title("📝 Validação de Atividades do Hub")
st.markdown("Vincule a atividade gerada no Hub à meta do PEI e avalie o resultado.")

# --- CONEXÃO ---
sh = conectar_banco()
if not sh: st.stop()

df_peis = carregar_peis(sh)
ws_diario = preparar_aba_diario(sh)

if df_peis.empty:
    st.warning("Nenhum PEI encontrado. Crie o PEI antes de avaliar atividades.")
    st.stop()

# --- SELEÇÃO INTELIGENTE DO ALUNO ---
# Procura colunas de nome e turma
col_nome = next((c for c in df_peis.columns if 'nome' in c or 'aluno' in c), None)
col_turma = next((c for c in df_peis.columns if 'turma' in c or 'serie' in c), None)

if col_nome:
    # Cria rótulo visual
    df_peis['label'] = df_peis[col_nome].astype(str)
    if col_turma:
        df_peis['label'] += " - " + df_peis[col_turma].astype(str)
    
    aluno_selecao = st.selectbox("Selecione o Aluno:", df_peis['label'].unique())
    
    # Pega os dados do PEI desse aluno
    dados_aluno = df_peis[df_peis['label'] == aluno_selecao].iloc[0]
    
    # Extrai dados para contexto
    nome_real = str(dados_aluno[col_nome])
    turma_real = str(dados_aluno[col_turma]) if col_turma else ""
    
    # Busca Metas e Estratégias do PEI
    col_meta = next((c for c in df_peis.columns if 'meta' in c or 'objetivo' in c), None)
    col_estrat = next((c for c in df_peis.columns if 'estrat' in c or 'recurso' in c), None)
    
    meta_pei = str(dados_aluno[col_meta]) if col_meta else "Não definida"
    estrategia_pei = str(dados_aluno[col_estrat]) if col_estrat else "Não definida"

else:
    st.error("Erro na leitura das colunas do PEI. Verifique a planilha.")
    st.stop()

st.divider()

# --- ÁREA DE VÍNCULO (PEI <-> HUB) ---
col_contexto, col_form = st.columns([1, 1.5])

with col_contexto:
    st.markdown("### 📋 Contexto do PEI")
    st.info(f"**Meta:** {meta_pei}")
    st.caption(f"**Estratégia Base:** {estrategia_pei}")
    st.write("---")
    st.markdown("ℹ️ *Utilize este contexto para gerar a atividade no Hub de Inclusão e depois registre ao lado.*")

with col_form:
    st.subheader("🔗 Registro da Atividade (Hub)")
    
    with st.form("form_hub"):
        # Campo crucial para o vínculo
        atividade_hub = st.text_input(
            "Qual atividade foi gerada no Hub?", 
            placeholder="Ex: Texto simplificado sobre Fotossíntese (Nível 2)..."
        )
        
        st.write("---")
        st.markdown("**Feedback da Aplicação**")
        
        avaliacao = st.select_slider(
            "Como o aluno respondeu a essa atividade?",
            options=["🔴 Não engajou", "🟠 Com muita ajuda", "🟡 Com pouca ajuda", "🟢 Com autonomia"],
            value="🟡 Com pouca ajuda"
        )
        
        obs = st.text_area("Observações qualitativas:", height=80)
        
        enviar = st.form_submit_button("💾 Salvar Feedback", type="primary", use_container_width=True)

        if enviar:
            if not st.session_state["prof_nome"]:
                st.error("Identifique-se na barra lateral.")
            elif not atividade_hub:
                st.error("Descreva a atividade gerada no Hub.")
            else:
                with st.spinner("Enviando para a planilha..."):
                    try:
                        # DATA PREPARATION (O Segredo para não dar erro)
                        # Convertemos TUDO para string para o Google Sheets não rejeitar
                        nova_linha = [
                            str(datetime.now().timestamp()), # ID único
                            datetime.now().strftime("%d/%m/%Y %H:%M"), # Data Formatada
                            str(st.session_state["prof_nome"]),
                            str(nome_real),
                            str(turma_real),
                            str(meta_pei),        # Vínculo com PEI
                            str(estrategia_pei),  # Vínculo com PEI
                            str(atividade_hub),   # Vínculo com HUB
                            str(avaliacao),       # Feedback
                            str(obs),             # Feedback
                            "Integrado"           # Status
                        ]
                        
                        # Envio Seguro
                        ws_diario.append_row(nova_linha)
                        
                        st.success("✅ Atividade vinculada e avaliada com sucesso!")
                        time.sleep(1)
                        st.rerun()
                        
                    except Exception as e:
                        st.error(f"Erro ao salvar na planilha: {e}")
                        st.info("Dica: Verifique se você não excluiu colunas na aba 'Diario_Bordo'.")

# --- VISUALIZAÇÃO DO VÍNCULO ---
st.divider()
st.markdown(f"**Histórico de Atividades do Hub para {nome_real}**")

try:
    dados_log = ws_diario.get_all_records()
    df_log = pd.DataFrame(dados_log)
    
    if not df_log.empty and "Aluno" in df_log.columns:
        # Filtra pelo aluno
        meus_logs = df_log[df_log["Aluno"] == nome_real].tail(3).iloc[::-1]
        
        if meus_logs.empty:
            st.caption("Nenhuma atividade registrada.")
            
        for i, row in meus_logs.iterrows():
            st.markdown(f"""
            <div style="border:1px solid #eee; padding:10px; border-radius:5px; margin-bottom:10px;">
                <small>📅 {row.get('Data_Hora', '')}</small>
                <div style="font-weight:bold; color:#2c3e50;">Atividade Hub: {row.get('Atividade_Hub', '')}</div>
                <div style="font-size:0.9em; color:#555;">Meta PEI: {row.get('Meta_PEI', '')}</div>
                <div style="margin-top:5px; font-weight:bold;">Resultado: {row.get('Avaliacao_Suporte', '')}</div>
            </div>
            """, unsafe_allow_html=True)
except:
    pass
