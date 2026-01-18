import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import pandas as pd
import time

# ==============================================================================
# 1. CONFIGURAÇÃO E CONEXÃO INTELIGENTE
# ==============================================================================
st.set_page_config(page_title="Validador PEI & Diário", page_icon="🧬", layout="wide")

@st.cache_resource
def conectar_banco():
    """Conecta ao Google Sheets e trata erros de autenticação"""
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        credentials = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scope)
        client = gspread.authorize(credentials)
        return client.open("Omnisfera_Dados")
    except Exception as e:
        st.error(f"Erro de conexão (Secrets/API): {e}")
        return None

def verificar_e_criar_abas(sh):
    """
    AUTOCORREÇÃO: Garante que a aba existe e tem as colunas certas.
    Isso resolve o problema de 'não estar salvando nada'.
    """
    nome_aba = "Diario_Bordo"
    colunas_necessarias = [
        "ID_Registro", "Data_Hora", "Professor_Autor", "Aluno_Nome", "Turma", 
        "Meta_PEI_Vinculada", "Origem_Atividade", "Descricao_Atividade", 
        "Engajamento_0_5", "Validacao_Estrategia", "Observacao_Qualitativa", "Necessita_Revisao_PEI"
    ]
    
    try:
        ws = sh.worksheet(nome_aba)
        # Se a aba existe, vamos confiar nela por enquanto (ou poderíamos validar headers)
        return ws
    except:
        # Se não existe, cria do zero com a estrutura perfeita
        ws = sh.add_worksheet(title=nome_aba, rows=1000, cols=15)
        ws.append_row(colunas_necessarias)
        return ws

def carregar_peis_ativos(sh):
    """Fonte da Verdade: Só traz alunos com PEI Ativo"""
    try:
        ws = sh.worksheet("Metas_PEI")
        dados = ws.get_all_records()
        df = pd.DataFrame(dados)
        # Normaliza colunas
        df.columns = [str(c).lower().strip() for c in df.columns]
        return df
    except:
        return pd.DataFrame()

# ==============================================================================
# 2. INTERFACE "FORA DA CURVA"
# ==============================================================================

# --- SIDEBAR ---
with st.sidebar:
    st.header("🧬 Validação de Estratégias")
    if "prof_nome" not in st.session_state: st.session_state["prof_nome"] = ""
    st.session_state["prof_nome"] = st.text_input("Educador Responsável:", value=st.session_state["prof_nome"])
    
    st.info("💡 **Conceito:** Este módulo não é apenas um diário. É onde validamos se o PEI está funcionando na prática. Seus registros aqui alimentarão os gráficos de avaliação automaticamente.")

st.title("🧬 Laboratório Pedagógico (Feedback & Diário)")

# --- CONEXÃO ---
sh = conectar_banco()
if not sh: st.stop()

ws_diario = verificar_e_criar_abas(sh) # Chama a autocorreção
df_peis = carregar_peis_ativos(sh)

if df_peis.empty:
    st.warning("⚠️ Nenhum PEI ativo encontrado. O sistema precisa de um PEI para vincular as evidências.")
    st.stop()

# --- SELEÇÃO DE ALUNO (Baseado no PEI) ---
# Tenta achar colunas de nome e turma
col_nome = next((c for c in df_peis.columns if 'nome' in c or 'aluno' in c), None)
col_turma = next((c for c in df_peis.columns if 'turma' in c or 'serie' in c), None)

if col_nome:
    df_peis['rotulo'] = df_peis[col_nome].astype(str)
    if col_turma: df_peis['rotulo'] += " - " + df_peis[col_turma].astype(str)
    
    aluno_selecionado = st.selectbox("Selecione o Estudante para Avaliar:", df_peis['rotulo'].unique())
    
    # Dados do Aluno
    dados_aluno = df_peis[df_peis['rotulo'] == aluno_selecionado].iloc[0]
    nome_real = dados_aluno[col_nome]
    turma_real = dados_aluno[col_turma] if col_turma else "N/A"
    
    # PEI Contexto
    col_meta = next((c for c in df_peis.columns if 'meta' in c or 'objetivo' in c), None)
    col_estrat = next((c for c in df_peis.columns if 'estrat' in c or 'recurso' in c), None)
    
    meta_pei = dados_aluno[col_meta] if col_meta else "Não definida"
    estrategia_pei = dados_aluno[col_estrat] if col_estrat else "Não definida"
else:
    st.error("Erro nos dados do PEI.")
    st.stop()

st.divider()

# --- LAYOUT "THINK OUTSIDE THE BOX" ---
# Esquerda: A Teoria (PEI) | Direita: A Prática (Validação)

c_teoria, c_pratica = st.columns([1, 1.5])

with c_teoria:
    st.markdown("### 📋 A Hipótese (PEI)")
    st.markdown(f"""
    <div style="background-color:#f0f9ff; padding:15px; border-radius:10px; border-left:5px solid #0ea5e9;">
        <small style="color:#0284c7; font-weight:bold;">META ESTABELECIDA</small><br>
        <div style="font-size:1.1em; margin-bottom:10px;">{meta_pei}</div>
        <small style="color:#0284c7; font-weight:bold;">ESTRATÉGIA SUGERIDA</small><br>
        <i>{estrategia_pei}</i>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.caption("🔍 O objetivo deste registro é confirmar se essa estratégia acima está funcionando ou se precisamos pivotar o PEI.")

with c_pratica:
    st.subheader("🧪 Feedback da Aplicação")
    
    # Seletor de Origem: Aqui conectamos com o Hub
    origem = st.radio("Qual recurso foi aplicado?", 
             ["🤖 Gerado no Hub de Inclusão", "🍎 Atividade Manual / Outro"], 
             horizontal=True)
    
    with st.form("form_validacao"):
        
        if "Hub" in origem:
            st.info("Cole abaixo o resumo da atividade que o Hub gerou para você.")
            atividade_desc = st.text_area("Atividade do Hub:", placeholder="Ex: Texto adaptado sobre Fotossíntese nível 2...", height=70)
        else:
            atividade_desc = st.text_input("Descrição da Atividade:", placeholder="Ex: Prova adaptada com consulta...")

        # AVALIAÇÃO TÉCNICA (Inputs para os Gráficos)
        c1, c2 = st.columns(2)
        with c1:
            engajamento = st.slider("Nível de Engajamento:", 0, 5, 3, help="0 = Recusa total, 5 = Hiperfoco/Participação total")
        with c2:
            # Essa pergunta é chave para a revisão do PEI
            validacao = st.selectbox("A Estratégia do PEI funcionou?", 
                                     ["✅ Sim, funcionou bem", 
                                      "⚠️ Funcionou parcialmente (com suporte)", 
                                      "❌ Não funcionou (Barreira)", 
                                      "🔄 Pivô (Tive que mudar tudo na hora)"])
        
        obs_qualitativa = st.text_area("Evidências / Observações:", placeholder="O que observou no comportamento? Onde ele travou?", height=100)
        
        # Checkbox estratégico
        flag_revisao = st.checkbox("🚩 Sinalizar para Revisão do PEI (Importante para a Coordenação)")
        
        btn_salvar = st.form_submit_button("💾 Salvar Evidência", type="primary", use_container_width=True)

        if btn_salvar:
            if not st.session_state["prof_nome"]:
                st.error("Identifique-se na barra lateral.")
            elif not atividade_desc:
                st.error("Descreva a atividade.")
            else:
                with st.spinner("Registrando evidência no banco de dados..."):
                    try:
                        # Prepara dados (Tudo string para segurança)
                        nova_linha = [
                            str(datetime.now().timestamp()),         # ID
                            datetime.now().strftime("%d/%m/%Y"),     # Data
                            str(st.session_state["prof_nome"]),      # Autor
                            str(nome_real),                          # Aluno
                            str(turma_real),                         # Turma
                            str(meta_pei),                           # Vínculo PEI
                            str(origem),                             # Hub vs Manual
                            str(atividade_desc),                     # O que foi feito
                            str(engajamento),                        # Métrica 1
                            str(validacao),                          # Métrica 2
                            str(obs_qualitativa),                    # Qualitativo
                            "SIM" if flag_revisao else "NÃO"         # Flag de Alerta
                        ]
                        
                        # Envio direto e seguro
                        ws_diario.append_row(nova_linha)
                        
                        st.success("✅ Evidência salva! Isso ajudará a calcular a eficácia do PEI.")
                        time.sleep(1)
                        st.rerun()
                        
                    except Exception as e:
                        st.error(f"Erro ao salvar: {e}")

# --- FEEDBACK VISUAL RÁPIDO ---
st.markdown("---")
st.subheader(f"📊 Linha do Tempo: {nome_real}")

try:
    df_logs = pd.DataFrame(ws_diario.get_all_records())
    
    # Filtro inteligente de colunas (caso mude nomes)
    col_aluno_log = next((c for c in df_logs.columns if 'aluno' in c.lower()), None)
    
    if not df_logs.empty and col_aluno_log:
        meus_logs = df_logs[df_logs[col_aluno_log] == nome_real].tail(3).iloc[::-1]
        
        if meus_logs.empty:
            st.info("Ainda sem registros para este aluno.")
        
        cols = st.columns(3)
        for i, (idx, row) in enumerate(meus_logs.iterrows()):
            with cols[i % 3]:
                # Card Visual
                validacao_txt = str(row.get('Validacao_Estrategia', ''))
                cor = "#dcfce7" if "Sim" in validacao_txt else "#fee2e2" if "Não" in validacao_txt else "#fef9c3"
                icone = "🤖" if "Hub" in str(row.get('Origem_Atividade', '')) else "📝"
                
                st.markdown(f"""
                <div style="background-color: {cor}; padding: 15px; border-radius: 10px; border: 1px solid #ddd; height: 100%;">
                    <div style="font-size:0.8em; color:#555;">{row.get('Data_Hora', '')}</div>
                    <div style="font-weight:bold; margin-top:5px;">{icone} {row.get('Descricao_Atividade', '')[:40]}...</div>
                    <div style="margin-top:10px; font-size:0.9em;"><b>Resultado:</b> {validacao_txt}</div>
                    <div style="margin-top:5px; font-size:0.9em;"><b>Engajamento:</b> {row.get('Engajamento_0_5', '')}/5</div>
                </div>
                """, unsafe_allow_html=True)
except:
    pass
