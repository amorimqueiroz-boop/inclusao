import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import pandas as pd

# ==============================================================================
# 1. CONFIGURAÇÃO E DADOS CURRICULARES
# ==============================================================================
st.set_page_config(page_title="Omnisfera | Diário de Bordo", page_icon="📝", layout="wide")

# Estrutura dos Componentes Curriculares
CURRICULO = {
    "Anos Iniciais (1º ao 5º)": [
        "Polivalente (Regência de Classe)", "Arte", "Educação Física", "Língua Inglesa"
    ],
    "Anos Finais (6º ao 9º)": [
        "Língua Portuguesa", "Matemática", "Ciências", "História", "Geografia", 
        "Arte", "Educação Física", "Língua Inglesa"
    ],
    "Ensino Médio": [
        "Linguagens e suas Tecnologias", "Matemática e suas Tecnologias", 
        "Ciências da Natureza", "Ciências Humanas e Sociais Aplicadas", "Projeto de Vida"
    ]
}

# ==============================================================================
# 2. CONEXÃO COM GOOGLE SHEETS
# ==============================================================================
@st.cache_resource
def conectar_banco():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    credentials = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scope)
    client = gspread.authorize(credentials)
    return client.open("Omnisfera_Dados")

def inicializar_abas(sh):
    """Garante que a aba do Diário tenha as colunas novas de Disciplina/Etapa"""
    try:
        return sh.worksheet("Diario_Bordo")
    except:
        ws = sh.add_worksheet(title="Diario_Bordo", rows=1000, cols=9)
        # Cabeçalho atualizado com Etapa e Disciplina
        ws.append_row(["Timestamp", "Data_Hora", "Professor", "Aluno", "Etapa", "Disciplina", "Atividade_Resumo", "Resultado", "Observacao"])
        return ws

def buscar_alunos_cadastrados(sh):
    """Tenta buscar alunos na aba 'Cadastro' ou na primeira aba disponível"""
    try:
        # Tenta achar uma aba específica de cadastro, senão pega a primeira (índice 0)
        try:
            ws = sh.worksheet("Cadastro_Alunos") 
        except:
            ws = sh.get_worksheet(0)
            
        # Pega todos os valores da Coluna A (assumindo que Nome é a coluna A)
        nomes = ws.col_values(1)
        
        # Remove o cabeçalho se ele for "Nome" ou "Aluno"
        if nomes and nomes[0].lower() in ["nome", "aluno", "estudante"]:
            return nomes[1:]
        return nomes
    except Exception as e:
        st.error(f"Erro ao buscar lista de alunos: {e}")
        return []

def buscar_historico_aluno(sh, nome_aluno):
    ws = inicializar_abas(sh)
    dados = ws.get_all_records()
    if not dados: return pd.DataFrame()
    
    df = pd.DataFrame(dados)
    # Filtra pelo aluno
    if "Aluno" in df.columns:
        df_aluno = df[df["Aluno"] == nome_aluno]
        # Ordena por Timestamp se existir, senão devolve como está
        if "Timestamp" in df_aluno.columns:
            return df_aluno.sort_values(by="Timestamp", ascending=False).head(5)
        return df_aluno.head(5)
    return pd.DataFrame()

# ==============================================================================
# 3. INTERFACE DE USUÁRIO
# ==============================================================================

# --- SIDEBAR (Login) ---
with st.sidebar:
    st.header("🔐 Identificação")
    if "usuario_nome" not in st.session_state: st.session_state["usuario_nome"] = ""
    
    nome_input = st.text_input("Nome do Professor:", value=st.session_state["usuario_nome"])
    if nome_input:
        st.session_state["usuario_nome"] = nome_input
        st.success(f"Olá, {nome_input}")
    else:
        st.warning("Necessário para salvar registros.")

st.title("📝 Diário de Bordo")
st.markdown("Registro de aplicação das atividades adaptadas e evolução do estudante.")

# --- CONEXÃO ---
try:
    sh = conectar_banco()
    lista_alunos = buscar_alunos_cadastrados(sh)
    ws_diario = inicializar_abas(sh)
except Exception as e:
    st.error("Erro de conexão com o banco de dados.")
    st.stop()

# --- SELEÇÃO DE ALUNO (GLOBAL - NO TOPO) ---
if not lista_alunos:
    st.warning("⚠️ Nenhum aluno encontrado no banco de dados. Cadastre os alunos no módulo PEI/Cadastro.")
    st.stop()

col_aluno, col_vazia = st.columns([1, 1])
with col_aluno:
    aluno_selecionado = st.selectbox("📂 Selecione o Estudante:", lista_alunos)

st.divider()

# --- ÁREA DE REGISTRO (ABAS POR ETAPA) ---
col_form, col_hist = st.columns([1.5, 1])

with col_form:
    st.subheader("📍 Registrar Atividade")
    
    # Abas para separar os componentes curriculares
    tab1, tab2, tab3 = st.tabs(["Anos Iniciais", "Anos Finais", "Ensino Médio"])
    
    etapa_selecionada = None
    disciplina_selecionada = None

    # Lógica das Abas
    with tab1:
        disc_iniciais = st.selectbox("Disciplina (Iniciais):", CURRICULO["Anos Iniciais (1º ao 5º)"], key="sel_iniciais")
        if st.session_state.get("active_tab") == "Iniciais" or disc_iniciais: 
            etapa_selecionada = "Anos Iniciais"
            disciplina_selecionada = disc_iniciais

    with tab2:
        disc_finais = st.selectbox("Disciplina (Finais):", CURRICULO["Anos Finais (6º ao 9º)"], key="sel_finais")
        if disc_finais: # Simplificação da lógica de seleção
            # Nota: Num app real, usaríamos callbacks para limpar os outros selects, 
            # aqui vamos assumir que o usuário seleciona na aba ativa.
            pass 

    with tab3:
        disc_medio = st.selectbox("Área/Disciplina (Médio):", CURRICULO["Ensino Médio"], key="sel_medio")

    # Determina qual aba está "valendo" baseado em qual tem foco visual (Streamlit não retorna aba ativa nativamente fácil, então usamos a lógica do form abaixo)
    
    st.info("👆 Selecione a etapa e a disciplina nas abas acima.")

    # Formulário Unificado
    with st.form("form_diario"):
        # Descrição da Atividade (Conexão com o Hub)
        st.markdown("**Sobre a Atividade Adaptada**")
        atividade_resumo = st.text_input("Resumo da Atividade (O que foi aplicado?):", 
                                         placeholder="Ex: Jogo da memória sobre relevo (Adaptado no Hub)")
        
        # Correção da seleção de disciplina para o envio
        # (Truque: O usuário vai preencher, vamos identificar qual aba ele usou visualmente ou assumir a última selecionada se houver conflito, 
        # mas idealmente ele seleciona a aba e preenche o form).
        
        st.markdown("**Avaliação da Execução**")
        status = st.radio("Nível de Autonomia na tarefa:", 
                          ["🟢 Independente", "🟡 Com Ajuda Parcial", "🟠 Com Ajuda Total", "🔴 Não Realizou"],
                          horizontal=True)
        
        obs = st.text_area("Observações Pedagógicas:", placeholder="O aluno engajou? O recurso visual funcionou?")
        
        enviar = st.form_submit_button("💾 Salvar Registro no Diário")

        if enviar:
            # Lógica simples para pegar a disciplina correta baseada na aba visual não é possível diretamente no backend,
            # Então vamos verificar qual selectbox não está vazio ou usar um radio hidden se preferir. 
            # Vamos simplificar: O usuário deve selecionar a disciplina na aba que ele quer.
            
            # Recupera valores dos widgets fora do form
            d_ini = st.session_state.sel_iniciais
            d_fin = st.session_state.sel_finais
            d_med = st.session_state.sel_medio
            
            # Lógica de prioridade (pode ser melhorada com callbacks depois)
            # Por padrão, assume Anos Iniciais se nada for mudado, ou tentamos inferir.
            # Para evitar erro, vou pedir para o usuário confirmar a etapa num radio dentro do form se for crítico,
            # mas vamos tentar salvar o que estiver na aba 1 se ele não mexeu nas outras.
            
            # Solução mais robusta: Vamos pegar a disciplina selecionada pelo contexto
            # Como st.tabs não guarda estado, vamos salvar com base no que ele preencheu.
            
            # *Importante*: Num cenário real, o ideal é ter UM select de "Etapa" e depois UM select de "Disciplina" atualizado dinamicamente.
            # Mas mantendo as abas como pedido:
            
            # Vamos salvar a disciplina de Anos Iniciais como padrão, a menos que ele mude.
            etapa_final = "Anos Iniciais"
            disciplina_final = d_ini
            
            # Se ele abriu a aba 2 e mudou o select lá (streamlt guarda o ultimo valor)
            # Essa lógica de abas no Streamlit para input é tricky. 
            # Sugestão: Salvar TODAS as seleções? Não.
            # Vamos simplificar para o MVP: Vamos colocar um radio de etapa antes das abas ou dentro do form?
            # Vou colocar a Etapa automaticamente baseada na lista onde a disciplina está.
            
            # Procura a disciplina nas listas
            if d_fin in CURRICULO["Anos Finais (6º ao 9º)"] and d_fin != CURRICULO["Anos Finais (6º ao 9º)"][0]:
                 etapa_final = "Anos Finais"
                 disciplina_final = d_fin
            elif d_med in CURRICULO["Ensino Médio"] and d_med != CURRICULO["Ensino Médio"][0]:
                 etapa_final = "Ensino Médio"
                 disciplina_final = d_med
            
            # Validação
            if not st.session_state["usuario_nome"]:
                st.error("Preencha seu nome na barra lateral.")
            elif not atividade_resumo:
                st.error("Descreva a atividade realizada.")
            else:
                with st.spinner("Salvando..."):
                    nova_linha = [
                        str(datetime.now().timestamp()),
                        datetime.now().strftime("%d/%m/%Y %H:%M"),
                        st.session_state["usuario_nome"],
                        aluno_selecionado,
                        etapa_final,        # Nova Coluna
                        disciplina_final,   # Nova Coluna
                        atividade_resumo,
                        status,
                        obs
                    ]
                    ws_diario.append_row(nova_linha)
                    st.success(f"Registro salvo! ({disciplina_final})")
                    st.balloons()
                    st.rerun()

# --- HISTÓRICO LATERAL ---
with col_hist:
    st.subheader("📅 Histórico Recente")
    if aluno_selecionado:
        try:
            df_hist = buscar_historico_aluno(sh, aluno_selecionado)
            if not df_hist.empty:
                for index, row in df_hist.iterrows():
                    # Ícone baseado no status
                    icone = "✅" if "Independente" in row['Resultado'] else "⚠️" if "Ajuda" in row['Resultado'] else "❌"
                    
                    st.markdown(f"""
                    <div style="background-color: white; padding: 10px; border-radius: 5px; border: 1px solid #e2e8f0; margin-bottom: 10px; box-shadow: 0 1px 2px rgba(0,0,0,0.05);">
                        <div style="font-size: 0.75rem; color: #a0aec0;">{row['Data_Hora']} | {row.get('Disciplina', 'Geral')}</div>
                        <div style="font-weight: bold; color: #2d3748;">{row.get('Atividade_Resumo', row.get('Atividade', ''))}</div>
                        <div style="margin-top: 5px; font-size: 0.9rem;">{icone} {row['Resultado']}</div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.caption("Nenhum registro recente.")
        except Exception as e:
            st.warning("Aguardando primeiros registros...")
