# ==============================================================================
# DIÁRIO DE BORDO PAEE - SUPABASE INTEGRATION
# ==============================================================================

import streamlit as st
import os
import json
import pandas as pd
from datetime import datetime, date, timedelta
import requests
import time
import plotly.express as px
import base64
import plotly.graph_objects as go
from plotly.subplots import make_subplots


import omni_utils as ou  # módulo atualizado

# ✅ set_page_config UMA VEZ SÓ, SEMPRE no topo
st.set_page_config(
    page_title="Omnisfera | Diário de Bordo",
    page_icon="📘",
    layout="wide",
    initial_sidebar_state="collapsed",
)

APP_VERSION = "v150.0 (SaaS Design)"

# ✅ UI lockdown (não quebra se faltar)
try:
    from ui_lockdown import hide_streamlit_chrome_if_needed, hide_default_sidebar_nav
    hide_streamlit_chrome_if_needed()
    hide_default_sidebar_nav()
except Exception:
    pass

# ✅ Header + Navbar (depois do page_config)
ou.render_omnisfera_header()
ou.render_navbar(active_tab="Diário de Bordo")


# ==============================================================================
# 1. CONFIGURAÇÃO E SEGURANÇA
# ==============================================================================
st.set_page_config(
    page_title="Diário de Bordo PAEE | Omnisfera", 
    page_icon="📘", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==============================================================================
# BLOCO VISUAL INTELIGENTE: HEADER OMNISFERA
# ==============================================================================
try:
    IS_TEST_ENV = st.secrets.get("ENV") == "TESTE"
except:
    IS_TEST_ENV = False

def get_logo_base64():
    caminhos = ["omni_icone.png", "logo.png", "iconeaba.png"]
    for c in caminhos:
        if os.path.exists(c):
            with open(c, "rb") as f:
                return f"data:image/png;base64,{base64.b64encode(f.read()).decode()}"
    return "https://cdn-icons-png.flaticon.com/512/1183/1183672.png"

src_logo_giratoria = get_logo_base64()

if IS_TEST_ENV:
    card_bg = "rgba(255, 220, 50, 0.95)" 
    card_border = "rgba(200, 160, 0, 0.5)"
else:
    card_bg = "rgba(255, 255, 255, 0.85)"
    card_border = "rgba(255, 255, 255, 0.6)"

st.markdown("""
<link href="https://cdn.jsdelivr.net/npm/remixicon@4.1.0/fonts/remixicon.css" rel="stylesheet">

<style>
    /* CARD HERO */
    .mod-card-wrapper { display: flex; flex-direction: column; margin-bottom: 20px; border-radius: 16px; overflow: hidden; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.02); }
    .mod-card-rect { background: white; border-radius: 16px 16px 0 0; padding: 0; border: 1px solid #E2E8F0; border-bottom: none; display: flex; flex-direction: row; align-items: center; height: 130px; width: 100%; position: relative; overflow: hidden; transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1); }
    .mod-card-rect:hover { transform: translateY(-4px); box-shadow: 0 12px 24px rgba(0, 0, 0, 0.08); border-color: #CBD5E1; }
    .mod-bar { width: 6px; height: 100%; flex-shrink: 0; }
    .mod-icon-area { width: 90px; height: 100%; display: flex; align-items: center; justify-content: center; font-size: 1.8rem; flex-shrink: 0; background: transparent !important; border-right: 1px solid #F1F5F9; transition: all 0.3s ease; }
    .mod-card-rect:hover .mod-icon-area { transform: scale(1.05); }
    .mod-content { flex-grow: 1; padding: 0 24px; display: flex; flex-direction: column; justify-content: center; }
    .mod-title { font-weight: 800; font-size: 1.1rem; color: #1E293B; margin-bottom: 6px; letter-spacing: -0.3px; transition: color 0.2s; }
    .mod-card-rect:hover .mod-title { color: #4F46E5; }
    .mod-desc { font-size: 0.8rem; color: #64748B; line-height: 1.4; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }

    /* CORES */
    .c-teal { background: #0D9488 !important; }
    .bg-teal-soft { background: transparent !important; color: #0D9488 !important; }

    /* CARD DE DIÁRIO */
    .diario-card {
        background: white;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 15px;
        transition: all 0.2s ease;
    }
    .diario-card:hover {
        border-color: #0D9488;
        box-shadow: 0 4px 12px rgba(13, 148, 136, 0.1);
    }

    /* BADGES */
    .badge-individual { background: #DBEAFE; color: #1E40AF; }
    .badge-grupo { background: #D1FAE5; color: #065F46; }
    .badge-observacao { background: #FEF3C7; color: #92400E; }

    /* PROGRESS BAR */
    .prog-bar-bg {
        width: 100%;
        height: 8px;
        background: #E2E8F0;
        border-radius: 4px;
        overflow: hidden;
        margin-top: 8px;
    }
    .prog-bar-fill {
        height: 100%;
        background: linear-gradient(90deg, #0D9488, #14B8A6);
        transition: width 1s;
    }

    /* STATS CARDS */
    .stat-card {
        background: white;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 20px;
        text-align: center;
    }
    .stat-value {
        font-size: 2rem;
        font-weight: 800;
        color: #0D9488;
        margin-bottom: 5px;
    }
    .stat-label {
        font-size: 0.85rem;
        color: #64748B;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    /* FORM STYLES */
    .form-section {
        background: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 25px;
        margin-bottom: 20px;
    }

    /* TIMELINE */
    .timeline-item {
        position: relative;
        padding-left: 30px;
        margin-bottom: 20px;
    }
    .timeline-dot {
        position: absolute;
        left: 0;
        top: 5px;
        width: 12px;
        height: 12px;
        border-radius: 50%;
        background: #0D9488;
    }
    .timeline-content {
        background: white;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        padding: 15px;
    }
</style>
""", unsafe_allow_html=True)


# ==============================================================================
# FUNÇÃO DE VERIFICAÇÃO DE ACESSO
# ==============================================================================
def verificar_acesso():
    if not st.session_state.get("autenticado"):
        st.error("🔒 Acesso Negado. Por favor, faça login na Página Inicial.")
        st.stop()

    # Não mexe no .block-container (senão quebra o padding do ou.inject_layout_css)
    st.markdown("""
    <style>
      footer {visibility: hidden !important;}
      header[data-testid="stHeader"] {display:none !important;}
      [data-testid="stToolbar"] {display:none !important;}
    </style>
    """, unsafe_allow_html=True)

verificar_acesso()


# ==============================================================================
# CARD HERO PRINCIPAL
# ==============================================================================
hora = datetime.now().hour
saudacao = "Bom dia" if 5 <= hora < 12 else "Boa tarde" if 12 <= hora < 18 else "Boa noite"
USUARIO_NOME = (st.session_state.get("usuario_nome", "Visitante") or "Visitante").split()[0]
WORKSPACE_NAME = st.session_state.get("workspace_name", "Workspace") or "Workspace"

st.markdown(
    f"""
    <div class="mod-card-wrapper">
        <div class="mod-card-rect">
            <div class="mod-bar c-teal"></div>
            <div class="mod-icon-area bg-teal-soft">
                <i class="ri-book-2-fill"></i>
            </div>
            <div class="mod-content">
                <div class="mod-title">Diário de Bordo PAEE</div>
                <div class="mod-desc">
                    {saudacao}, <strong>{USUARIO_NOME}</strong>! Registre sessões, acompanhe progresso e documente intervenções
                    no workspace <strong>{WORKSPACE_NAME}</strong>. Sistema integrado para registro profissional do Atendimento Educacional Especializado.
                </div>
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ==============================================================================
# FUNÇÕES SUPABASE (REST)
# ==============================================================================
def _sb_url() -> str:
    url = str(st.secrets.get("SUPABASE_URL", "")).strip()
    if not url: 
        raise RuntimeError("SUPABASE_URL missing")
    return url.rstrip("/")

def _sb_key() -> str:
    key = str(st.secrets.get("SUPABASE_SERVICE_KEY", "") or st.secrets.get("SUPABASE_ANON_KEY", "")).strip()
    if not key: 
        raise RuntimeError("SUPABASE_KEY missing")
    return key

def _headers() -> dict:
    key = _sb_key()
    return {"apikey": key, "Authorization": f"Bearer {key}", "Content-Type": "application/json"}

# ==============================================================================
# FUNÇÕES DO DIÁRIO DE BORDO
# ==============================================================================
def carregar_alunos_workspace():
    """Carrega alunos do workspace atual"""
    WORKSPACE_ID = st.session_state.get("workspace_id")
    if not WORKSPACE_ID: 
        return []
    
    try:
        url = f"{_sb_url()}/rest/v1/students"
        params = {
            "select": "id,name,grade,class_group,diagnosis,created_at,pei_data",
            "workspace_id": f"eq.{WORKSPACE_ID}",
            "order": "name.asc"
        }
        
        response = requests.get(url, headers=_headers(), params=params, timeout=20)
        if response.status_code == 200:
            return response.json()
        return []
    except Exception as e:
        st.error(f"Erro ao carregar alunos: {str(e)}")
        return []

def salvar_registro_diario(registro):
    """Salva um registro no diário de bordo"""
    try:
        url = f"{_sb_url()}/rest/v1/diario_bordo"
        
        # Garantir que o workspace_id está no registro
        registro['workspace_id'] = st.session_state.get("workspace_id")
        registro['professor_id'] = USER_ID
        
        response = requests.post(url, headers=_headers(), json=registro, timeout=20)
        
        if response.status_code in [200, 201]:
            return {"sucesso": True, "id": response.json().get('id')}
        else:
            return {"sucesso": False, "erro": f"HTTP {response.status_code}: {response.text}"}
    except Exception as e:
        return {"sucesso": False, "erro": str(e)}

def atualizar_registro_diario(registro_id, dados):
    """Atualiza um registro existente"""
    try:
        url = f"{_sb_url()}/rest/v1/diario_bordo"
        params = {"id": f"eq.{registro_id}"}
        
        response = requests.patch(url, headers=_headers(), params=params, json=dados, timeout=20)
        return response.status_code in [200, 204]
    except Exception as e:
        st.error(f"Erro ao atualizar registro: {str(e)}")
        return False

def carregar_registros_aluno(aluno_id, limite=50):
    """Carrega registros de um aluno específico"""
    try:
        url = f"{_sb_url()}/rest/v1/diario_bordo"
        params = {
            "select": "*",
            "aluno_id": f"eq.{aluno_id}",
            "order": "data_sessao.desc",
            "limit": str(limite)
        }
        
        response = requests.get(url, headers=_headers(), params=params, timeout=20)
        if response.status_code == 200:
            return response.json()
        return []
    except Exception as e:
        st.error(f"Erro ao carregar registros: {str(e)}")
        return []

def carregar_todos_registros(limite=100):
    """Carrega todos os registros do workspace"""
    WORKSPACE_ID = st.session_state.get("workspace_id")
    if not WORKSPACE_ID: 
        return []
    
    try:
        url = f"{_sb_url()}/rest/v1/diario_bordo"
        params = {
            "select": "*,students(name,grade,class_group)",
            "workspace_id": f"eq.{WORKSPACE_ID}",
            "order": "data_sessao.desc,created_at.desc",
            "limit": str(limite)
        }
        
        response = requests.get(url, headers=_headers(), params=params, timeout=20)
        if response.status_code == 200:
            return response.json()
        return []
    except Exception as e:
        st.error(f"Erro ao carregar registros: {str(e)}")
        return []

def excluir_registro_diario(registro_id):
    """Exclui um registro do diário"""
    try:
        url = f"{_sb_url()}/rest/v1/diario_bordo"
        params = {"id": f"eq.{registro_id}"}
        
        response = requests.delete(url, headers=_headers(), params=params, timeout=20)
        return response.status_code in [200, 204]
    except Exception as e:
        st.error(f"Erro ao excluir registro: {str(e)}")
        return False

# ==============================================================================
# SIDEBAR - FILTROS E NAVEGAÇÃO
# ==============================================================================
with st.sidebar:
    try: 
        st.image("ominisfera.png", width=150)
    except: 
        st.markdown("### 🌐 OMNISFERA PAEE")
    
    st.markdown("---")
    
    # Navegação
    col_nav1, col_nav2 = st.columns(2)
    with col_nav1:
        if st.button("🏠 Home", use_container_width=True):
            st.switch_page("Home.py")
    with col_nav2:
        if st.button("📋 PAE", use_container_width=True):
            st.switch_page("pages/2_PAE.py")
    
    st.markdown("---")
    
    # Filtros
    st.markdown("### 🔍 Filtros")
    
    # Carregar alunos
    if 'alunos_cache' not in st.session_state:
        with st.spinner("Carregando alunos..."):
            st.session_state.alunos_cache = carregar_alunos_workspace()
    
    alunos = st.session_state.alunos_cache
    
    if not alunos:
        st.warning("Nenhum aluno encontrado.")
        st.stop()
    
    # Filtro por aluno
    nomes_alunos = [f"{a['name']} ({a.get('grade', 'N/I')})" for a in alunos]
    aluno_filtro = st.selectbox("Aluno:", ["Todos"] + nomes_alunos)
    
    # Filtro por período
    periodo = st.selectbox("Período:", 
                          ["Últimos 7 dias", "Últimos 30 dias", "Este mês", "Mês passado", "Personalizado", "Todos"])
    
    if periodo == "Personalizado":
        col_data1, col_data2 = st.columns(2)
        with col_data1:
            data_inicio = st.date_input("De:", value=date.today() - timedelta(days=30))
        with col_data2:
            data_fim = st.date_input("Até:", value=date.today())
    
    # Filtro por modalidade
    modalidade = st.multiselect(
        "Modalidade:",
        ["individual", "grupo", "observacao_sala", "consultoria"],
        default=["individual", "grupo"]
    )
    
    st.markdown("---")
    
    # Estatísticas rápidas
    st.markdown("### 📊 Estatísticas")
    
    # Carregar registros para estatísticas
    registros = carregar_todos_registros(limite=500)
    
    if registros:
        total_registros = len(registros)
        registros_ultimos_30 = len([r for r in registros 
                                  if datetime.fromisoformat(r['created_at'].replace('Z', '+00:00')).date() > date.today() - timedelta(days=30)])
        
        col_stat1, col_stat2 = st.columns(2)
        with col_stat1:
            st.metric("Total", total_registros)
        with col_stat2:
            st.metric("Últimos 30d", registros_ultimos_30)
    else:
        st.info("Nenhum registro encontrado.")

# ==============================================================================
# ABA PRINCIPAL - DIÁRIO DE BORDO
# ==============================================================================

# Criar abas
tab_novo, tab_lista, tab_relatorios, tab_config = st.tabs([
    "📝 Novo Registro", "📋 Lista de Registros", "📊 Relatórios", "⚙️ Configurações"
])

# ==============================================================================
# ABA 1: NOVO REGISTRO
# ==============================================================================
with tab_novo:
    st.markdown("### 📝 Nova Sessão de AEE")
    
    with st.form("form_nova_sessao", clear_on_submit=True):
        st.markdown("<div class='form-section'>", unsafe_allow_html=True)
        
        # Seção 1: Informações básicas
        st.markdown("#### 1. Informações da Sessão")
        
        col_info1, col_info2, col_info3 = st.columns(3)
        
        with col_info1:
            # Seleção do aluno
            aluno_options = {f"{a['name']} ({a.get('grade', 'N/I')})": a for a in alunos}
            aluno_selecionado_label = st.selectbox(
                "Aluno *",
                options=list(aluno_options.keys()),
                help="Selecione o aluno atendido"
            )
            
            aluno_selecionado = aluno_options[aluno_selecionado_label]
            aluno_id = aluno_selecionado['id']
        
        with col_info2:
            data_sessao = st.date_input(
                "Data da Sessão *",
                value=date.today(),
                help="Data em que a sessão foi realizada"
            )
            
            duracao = st.number_input(
                "Duração (minutos) *",
                min_value=15,
                max_value=240,
                value=45,
                step=15,
                help="Duração da sessão em minutos"
            )
        
        with col_info3:
            modalidade = st.selectbox(
                "Modalidade *",
                options=[
                    ("individual", "Individual"),
                    ("grupo", "Grupo"),
                    ("observacao_sala", "Observação em Sala"),
                    ("consultoria", "Consultoria")
                ],
                format_func=lambda x: x[1],
                help="Modalidade de atendimento"
            )[0]
            
            engajamento = st.slider(
                "Engajamento do Aluno",
                min_value=1,
                max_value=5,
                value=3,
                help="1 = Baixo engajamento, 5 = Alto engajamento"
            )
        
        st.divider()
        
        # Seção 2: Conteúdo da sessão
        st.markdown("#### 2. Conteúdo da Sessão")
        
        atividade = st.text_area(
            "Atividade Principal *",
            height=100,
            placeholder="Descreva a atividade principal realizada...",
            help="Ex: Jogo de memória com figuras geométricas, leitura compartilhada, exercício de coordenação motora..."
        )
        
        col_conteudo1, col_conteudo2 = st.columns(2)
        
        with col_conteudo1:
            objetivos = st.text_area(
                "Objetivos Trabalhados *",
                height=120,
                placeholder="Quais objetivos foram trabalhados nesta sessão?",
                help="Ex: Desenvolver atenção sustentada, melhorar coordenação visomotora, ampliar vocabulário..."
            )
        
        with col_conteudo2:
            estrategias = st.text_area(
                "Estratégias Utilizadas *",
                height=120,
                placeholder="Quais estratégias pedagógicas foram utilizadas?",
                help="Ex: Modelagem, dicas visuais, fragmentação da tarefa, reforço positivo..."
            )
        
        recursos = st.text_input(
            "Recursos e Materiais",
            placeholder="Recursos utilizados (separados por vírgula)",
            help="Ex: Tablets, jogos pedagógicos, materiais concretos, recursos visuais..."
        )
        
        st.divider()
        
        # Seção 3: Avaliação e observações
        st.markdown("#### 3. Avaliação e Observações")
        
        col_avaliacao1, col_avaliacao2 = st.columns(2)
        
        with col_avaliacao1:
            nivel_dificuldade = st.selectbox(
                "Nível de Dificuldade",
                options=[
                    ("muito_facil", "Muito Fácil"),
                    ("facil", "Fácil"),
                    ("adequado", "Adequado"),
                    ("desafiador", "Desafiador"),
                    ("muito_dificil", "Muito Difícil")
                ],
                format_func=lambda x: x[1],
                index=2
            )[0]
        
        with col_avaliacao2:
            competencias = st.multiselect(
                "Competências Trabalhadas",
                options=[
                    "atenção", "memória", "raciocínio", "linguagem",
                    "socialização", "autonomia", "motricidade", "percepção",
                    "organização", "regulação emocional"
                ],
                default=["atenção", "memória"]
            )
        
        col_obs1, col_obs2 = st.columns(2)
        
        with col_obs1:
            pontos_positivos = st.text_area(
                "Pontos Positivos",
                height=100,
                placeholder="O que funcionou bem?",
                help="Registre os aspectos positivos da sessão"
            )
        
        with col_obs2:
            dificuldades = st.text_area(
                "Dificuldades Identificadas",
                height=100,
                placeholder="Quais dificuldades foram observadas?",
                help="Registre desafios encontrados durante a sessão"
            )
        
        observacoes = st.text_area(
            "Observações Gerais",
            height=120,
            placeholder="Outras observações relevantes...",
            help="Registre qualquer informação adicional importante"
        )
        
        st.divider()
        
        # Seção 4: Próximos passos
        st.markdown("#### 4. Próximos Passos")
        
        proximos_passos = st.text_area(
            "Plano para Próxima Sessão",
            height=100,
            placeholder="O que planejar para a próxima sessão?",
            help="Sugestões e planejamento para continuidade do trabalho"
        )
        
        encaminhamentos = st.text_input(
            "Encaminhamentos Necessários",
            placeholder="Encaminhamentos para outros profissionais",
            help="Ex: Encaminhar para fonoaudiólogo, solicitar avaliação psicológica..."
        )
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Botões de ação
        col_botoes1, col_botoes2, col_botoes3 = st.columns([1, 1, 1])
        
        with col_botoes2:
            salvar = st.form_submit_button(
                "💾 Salvar Registro",
                type="primary",
                use_container_width=True
            )
        
        if salvar:
            # Validações
            if not atividade or not objetivos or not estrategias:
                st.error("Por favor, preencha os campos obrigatórios (*)")
            else:
                # Preparar registro
                registro = {
                    "aluno_id": aluno_id,
                    "data_sessao": data_sessao.isoformat(),
                    "duracao_minutos": duracao,
                    "modalidade_atendimento": modalidade,
                    "atividade_principal": atividade,
                    "objetivos_trabalhados": objetivos,
                    "estrategias_utilizadas": estrategias,
                    "recursos_materiais": recursos,
                    "engajamento_aluno": engajamento,
                    "nivel_dificuldade": nivel_dificuldade,
                    "competencias_trabalhadas": competencias,
                    "pontos_positivos": pontos_positivos,
                    "dificuldades_identificadas": dificuldades,
                    "observacoes": observacoes,
                    "proximos_passos": proximos_passos,
                    "encaminhamentos": encaminhamentos,
                    "status": "finalizado",
                    "tags": competencias  # Usar competências como tags
                }
                
                # Salvar no Supabase
                with st.spinner("Salvando registro..."):
                    resultado = salvar_registro_diario(registro)
                    
                    if resultado["sucesso"]:
                        st.success("✅ Registro salvo com sucesso!")
                        
                        # Mostrar resumo
                        with st.expander("📋 Ver Resumo do Registro", expanded=True):
                            col_resumo1, col_resumo2 = st.columns(2)
                            with col_resumo1:
                                st.markdown(f"**Aluno:** {aluno_selecionado_label}")
                                st.markdown(f"**Data:** {data_sessao.strftime('%d/%m/%Y')}")
                                st.markdown(f"**Duração:** {duracao} minutos")
                                st.markdown(f"**Modalidade:** {modalidade}")
                            
                            with col_resumo2:
                                st.markdown(f"**Engajamento:** {'⭐' * engajamento}")
                                st.markdown(f"**Competências:** {', '.join(competencias)}")
                                st.markdown(f"**ID do Registro:** {resultado.get('id', 'N/A')}")
                        
                        time.sleep(2)
                        st.rerun()
                    else:
                        st.error(f"❌ Erro ao salvar: {resultado.get('erro', 'Erro desconhecido')}")

# ==============================================================================
# ABA 2: LISTA DE REGISTROS
# ==============================================================================
with tab_lista:
    st.markdown("### 📋 Registros de Atendimento")
    
    # Carregar registros com filtros
    todos_registros = carregar_todos_registros(limite=200)
    
    if not todos_registros:
        st.info("Nenhum registro encontrado. Crie seu primeiro registro na aba 'Novo Registro'.")
    else:
        # Aplicar filtros
        registros_filtrados = todos_registros.copy()
        
        # Filtro por aluno
        if aluno_filtro != "Todos":
            aluno_nome = aluno_filtro.split("(")[0].strip()
            registros_filtrados = [r for r in registros_filtrados 
                                 if r.get('students', {}).get('name') == aluno_nome]
        
        # Filtro por período
        if periodo != "Todos":
            hoje = date.today()
            if periodo == "Últimos 7 dias":
                data_corte = hoje - timedelta(days=7)
                registros_filtrados = [r for r in registros_filtrados 
                                     if datetime.fromisoformat(r['data_sessao']).date() >= data_corte]
            elif periodo == "Últimos 30 dias":
                data_corte = hoje - timedelta(days=30)
                registros_filtrados = [r for r in registros_filtrados 
                                     if datetime.fromisoformat(r['data_sessao']).date() >= data_corte]
            elif periodo == "Este mês":
                registros_filtrados = [r for r in registros_filtrados 
                                     if datetime.fromisoformat(r['data_sessao']).date().month == hoje.month]
            elif periodo == "Mês passado":
                mes_passado = hoje.month - 1 if hoje.month > 1 else 12
                registros_filtrados = [r for r in registros_filtrados 
                                     if datetime.fromisoformat(r['data_sessao']).date().month == mes_passado]
            elif periodo == "Personalizado":
                registros_filtrados = [r for r in registros_filtrados 
                                     if data_inicio <= datetime.fromisoformat(r['data_sessao']).date() <= data_fim]
        
        # Filtro por modalidade
        if modalidade:
            registros_filtrados = [r for r in registros_filtrados 
                                 if r.get('modalidade_atendimento') in modalidade]
        
        # Estatísticas dos filtrados
        col_stats1, col_stats2, col_stats3, col_stats4 = st.columns(4)
        with col_stats1:
            st.metric("Total Filtrado", len(registros_filtrados))
        with col_stats2:
            total_minutos = sum(r.get('duracao_minutos', 0) for r in registros_filtrados)
            st.metric("Horas de Atendimento", f"{total_minutos // 60}h")
        with col_stats3:
            media_engajamento = sum(r.get('engajamento_aluno', 0) for r in registros_filtrados) / len(registros_filtrados) if registros_filtrados else 0
            st.metric("Engajamento Médio", f"{media_engajamento:.1f}/5")
        with col_stats4:
            if registros_filtrados:
                ultimo_registro = max(registros_filtrados, key=lambda x: x['data_sessao'])
                st.metric("Última Sessão", datetime.fromisoformat(ultimo_registro['data_sessao']).strftime('%d/%m'))
        
        st.divider()
        
        # Exibir registros
        for registro in registros_filtrados:
            aluno_nome = registro.get('students', {}).get('name', 'Aluno não encontrado')
            data_formatada = datetime.fromisoformat(registro['data_sessao']).strftime('%d/%m/%Y')
            
            # Determinar classe CSS baseada na modalidade
            modalidade_classe = {
                'individual': 'badge-individual',
                'grupo': 'badge-grupo',
                'observacao_sala': 'badge-observacao'
            }.get(registro.get('modalidade_atendimento'), '')
            
            with st.expander(f"📅 {data_formatada} | {aluno_nome} | {registro.get('atividade_principal', '')[:50]}...", expanded=False):
                col_reg1, col_reg2 = st.columns([3, 1])
                
                with col_reg1:
                    st.markdown(f"**Atividade:** {registro.get('atividade_principal', '')}")
                    st.markdown(f"**Objetivos:** {registro.get('objetivos_trabalhados', '')}")
                    st.markdown(f"**Estratégias:** {registro.get('estrategias_utilizadas', '')}")
                    
                    if registro.get('observacoes'):
                        st.markdown(f"**Observações:** {registro.get('observacoes')}")
                    
                    if registro.get('proximos_passos'):
                        st.markdown(f"**Próximos Passos:** {registro.get('proximos_passos')}")
                
                with col_reg2:
                    st.markdown(f"<span class='{modalidade_classe}' style='padding: 4px 8px; border-radius: 12px; font-size: 0.8rem;'>{registro.get('modalidade_atendimento', '').replace('_', ' ').title()}</span>", unsafe_allow_html=True)
                    st.markdown(f"**Duração:** {registro.get('duracao_minutos', 0)} min")
                    st.markdown(f"**Engajamento:** {'⭐' * registro.get('engajamento_aluno', 0)}")
                    
                    if registro.get('competencias_trabalhadas'):
                        competencias = ', '.join(registro.get('competencias_trabalhadas', []))
                        st.markdown(f"**Competências:** {competencias}")
                    
                    # Botões de ação
                    col_btn1, col_btn2 = st.columns(2)
                    with col_btn1:
                        if st.button("✏️ Editar", key=f"edit_{registro['id']}", use_container_width=True):
                            st.session_state.editar_registro_id = registro['id']
                            st.switch_page("#")  # Poderia abrir modal de edição
                    
                    with col_btn2:
                        if st.button("🗑️ Excluir", key=f"del_{registro['id']}", type="secondary", use_container_width=True):
                            if excluir_registro_diario(registro['id']):
                                st.success("Registro excluído!")
                                time.sleep(1)
                                st.rerun()
                            else:
                                st.error("Erro ao excluir registro")
        
        # Paginação (simplificada)
        if len(registros_filtrados) > 10:
            st.markdown(f"**Mostrando {min(10, len(registros_filtrados))} de {len(registros_filtrados)} registros**")

# ==============================================================================
# ABA 3: RELATÓRIOS
# ==============================================================================
with tab_relatorios:
    st.markdown("### 📊 Relatórios e Análises")
    
    # Carregar dados
    registros = carregar_todos_registros(limite=500)
    
    if not registros:
        st.info("Nenhum dado disponível para gerar relatórios.")
    else:
        # Converter para DataFrame
        df = pd.DataFrame(registros)
        
        # Converter datas
        df['data_sessao'] = pd.to_datetime(df['data_sessao'])
        df['mes'] = df['data_sessao'].dt.to_period('M')
        
        col_rel1, col_rel2 = st.columns(2)
        
        with col_rel1:
            # Gráfico de atendimentos por mês
            st.markdown("#### 📅 Atendimentos por Mês")
            atendimentos_mes = df.groupby('mes').size().reset_index(name='count')
            atendimentos_mes['mes'] = atendimentos_mes['mes'].astype(str)
            
            fig1 = px.bar(
                atendimentos_mes,
                x='mes',
                y='count',
                title="Quantidade de Atendimentos por Mês",
                color='count',
                color_continuous_scale='teal'
            )
            fig1.update_layout(showlegend=False, height=300)
            st.plotly_chart(fig1, use_container_width=True)
        
        with col_rel2:
            # Distribuição por modalidade
            st.markdown("#### 📊 Distribuição por Modalidade")
            modalidade_counts = df['modalidade_atendimento'].value_counts().reset_index()
            modalidade_counts.columns = ['modalidade', 'count']
            
            fig2 = px.pie(
                modalidade_counts,
                values='count',
                names='modalidade',
                title="Distribuição por Modalidade de Atendimento",
                color_discrete_sequence=px.colors.sequential.Teal
            )
            fig2.update_layout(showlegend=True, height=300)
            st.plotly_chart(fig2, use_container_width=True)
        
        # Gráfico de engajamento ao longo do tempo
        st.markdown("#### 📈 Evolução do Engajamento")
        
        if 'aluno_id' in df.columns:
            # Selecionar aluno específico para análise
            alunos_unicos = df['aluno_id'].unique()
            if len(alunos_unicos) > 0:
                aluno_selecionado_id = st.selectbox(
                    "Selecione o aluno para análise:",
                    options=alunos_unicos,
                    format_func=lambda x: alunos_dict.get(x, f"Aluno {x[:8]}") if 'alunos_dict' in locals() else f"Aluno {x[:8]}"
                )
                
                # Filtrar dados do aluno
                df_aluno = df[df['aluno_id'] == aluno_selecionado_id].sort_values('data_sessao')
                
                if len(df_aluno) > 1:
                    fig3 = px.line(
                        df_aluno,
                        x='data_sessao',
                        y='engajamento_aluno',
                        title=f"Evolução do Engajamento - {alunos_dict.get(aluno_selecionado_id, 'Aluno')}",
                        markers=True,
                        line_shape='spline'
                    )
                    fig3.update_layout(height=400)
                    st.plotly_chart(fig3, use_container_width=True)
                    
                    # Estatísticas do aluno
                    col_aluno1, col_aluno2, col_aluno3, col_aluno4 = st.columns(4)
                    with col_aluno1:
                        st.metric("Total Sessões", len(df_aluno))
                    with col_aluno2:
                        st.metric("Engajamento Médio", f"{df_aluno['engajamento_aluno'].mean():.1f}/5")
                    with col_aluno3:
                        st.metric("Duração Média", f"{df_aluno['duracao_minutos'].mean():.0f} min")
                    with col_aluno4:
                        ultima_sessao = df_aluno.iloc[0]['data_sessao']
                        st.metric("Última Sessão", ultima_sessao.strftime('%d/%m'))
        
        # Competências mais trabalhadas
        st.markdown("#### 🎯 Competências Trabalhadas")
        
        # Extrair todas as competências
        todas_competencias = []
        for competencias in df['competencias_trabalhadas']:
            if competencias:
                todas_competencias.extend(competencias)
        
        if todas_competencias:
            competencias_df = pd.DataFrame({'competencia': todas_competencias})
            competencias_counts = competencias_df['competencia'].value_counts().reset_index()
            competencias_counts.columns = ['competencia', 'count']
            
            fig4 = px.bar(
                competencias_counts.head(10),
                x='count',
                y='competencia',
                orientation='h',
                title="Top 10 Competências Trabalhadas",
                color='count',
                color_continuous_scale='teal'
            )
            fig4.update_layout(height=400)
            st.plotly_chart(fig4, use_container_width=True)
        
        # Exportar dados
        st.divider()
        st.markdown("#### 📥 Exportar Dados")
        
        col_exp1, col_exp2, col_exp3 = st.columns(3)
        
        with col_exp1:
            # Exportar como CSV
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📄 Exportar CSV",
                data=csv,
                file_name=f"diario_bordo_{date.today()}.csv",
                mime="text/csv",
                use_container_width=True
            )
        
        with col_exp2:
            # Exportar como JSON
            json_data = df.to_json(orient='records', indent=2, force_ascii=False)
            st.download_button(
                label="📋 Exportar JSON",
                data=json_data,
                file_name=f"diario_bordo_{date.today()}.json",
                mime="application/json",
                use_container_width=True
            )
        
        with col_exp3:
            # Gerar relatório resumido
            if st.button("📊 Gerar Relatório Resumido", use_container_width=True):
                with st.spinner("Gerando relatório..."):
                    # Criar relatório resumido
                    relatorio = {
                        "data_geracao": datetime.now().isoformat(),
                        "total_registros": len(df),
                        "periodo_analisado": f"{df['data_sessao'].min().date()} a {df['data_sessao'].max().date()}",
                        "total_alunos": df['aluno_id'].nunique(),
                        "total_horas": int(df['duracao_minutos'].sum() / 60),
                        "engajamento_medio": float(df['engajamento_aluno'].mean()),
                        "modalidades": df['modalidade_atendimento'].value_counts().to_dict(),
                        "top_competencias": competencias_counts.head(5).to_dict('records') if 'competencias_counts' in locals() else []
                    }
                    
                    st.json(relatorio)

# ==============================================================================
# ABA 4: CONFIGURAÇÕES
# ==============================================================================
with tab_config:
    st.markdown("### ⚙️ Configurações do Diário")
    
    col_config1, col_config2 = st.columns(2)
    
    with col_config1:
        st.markdown("#### 📋 Configurações de Registro")
        
        # Configurações padrão
        if 'config_diario' not in st.session_state:
            st.session_state.config_diario = {
                'duracao_padrao': 45,
                'modalidade_padrao': 'individual',
                'competencias_padrao': ['atenção', 'memória'],
                'notificacoes': True
            }
        
        duracao_padrao = st.number_input(
            "Duração Padrão (minutos)",
            min_value=15,
            max_value=120,
            value=st.session_state.config_diario['duracao_padrao'],
            step=15
        )
        
        modalidade_padrao = st.selectbox(
            "Modalidade Padrão",
            options=['individual', 'grupo', 'observacao_sala', 'consultoria'],
            index=['individual', 'grupo', 'observacao_sala', 'consultoria'].index(
                st.session_state.config_diario['modalidade_padrao']
            )
        )
        
        competencias_padrao = st.multiselect(
            "Competências Padrão",
            options=['atenção', 'memória', 'raciocínio', 'linguagem', 'socialização', 
                    'autonomia', 'motricidade', 'percepção', 'organização', 'regulação emocional'],
            default=st.session_state.config_diario['competencias_padrao']
        )
        
        notificacoes = st.toggle(
            "Receber lembretes de registro",
            value=st.session_state.config_diario['notificacoes']
        )
    
    with col_config2:
        st.markdown("#### 🔧 Configurações de Exportação")
        
        formato_export = st.selectbox(
            "Formato Padrão de Exportação",
            options=['CSV', 'JSON', 'PDF', 'Excel']
        )
        
        incluir_dados = st.multiselect(
            "Campos para Exportação",
            options=['dados_aluno', 'conteudo_sessao', 'avaliacoes', 'observacoes', 'proximos_passos'],
            default=['dados_aluno', 'conteudo_sessao', 'avaliacoes']
        )
        
        auto_backup = st.toggle("Backup Automático", value=True)
        
        if auto_backup:
            freq_backup = st.selectbox(
                "Frequência do Backup",
                options=['Diário', 'Semanal', 'Mensal']
            )
    
    st.divider()
    
    # Botões de ação
    col_save, col_reset, col_help = st.columns(3)
    
    with col_save:
        if st.button("💾 Salvar Configurações", type="primary", use_container_width=True):
            st.session_state.config_diario = {
                'duracao_padrao': duracao_padrao,
                'modalidade_padrao': modalidade_padrao,
                'competencias_padrao': competencias_padrao,
                'notificacoes': notificacoes
            }
            st.success("Configurações salvas com sucesso!")
    
    with col_reset:
        if st.button("🔄 Restaurar Padrões", type="secondary", use_container_width=True):
            st.session_state.config_diario = {
                'duracao_padrao': 45,
                'modalidade_padrao': 'individual',
                'competencias_padrao': ['atenção', 'memória'],
                'notificacoes': True
            }
            st.success("Configurações restauradas para os padrões!")
            st.rerun()
    
    with col_help:
        if st.button("❓ Ajuda", use_container_width=True):
            st.info("""
            **Guia de Uso do Diário de Bordo:**
            
            1. **Novo Registro:** Preencha todos os campos obrigatórios (*) para criar um registro
            2. **Lista de Registros:** Visualize, filtre e gerencie todos os registros
            3. **Relatórios:** Acompanhe métricas e gere análises
            4. **Configurações:** Personalize o comportamento do sistema
            
            **Dicas:**
            - Use tags e competências para facilitar buscas
            - Exporte regularmente seus dados
            - Mantenha observações detalhadas para acompanhamento longitudinal
            """)

# ==============================================================================
# RODAPÉ
# ==============================================================================
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #64748B; font-size: 0.9rem; padding: 20px;">
    <p>📘 <strong>Diário de Bordo PAEE - Sistema Profissional de Registro</strong> | Omnisfera Educação Inclusiva</p>
    <p>💡 <strong>Dica:</strong> Registre imediatamente após cada sessão para maior precisão. Use as tags para organizar por competências.</p>
    <p>🔒 <strong>Segurança:</strong> Todos os dados são criptografados e armazenados em conformidade com a LGPD.</p>
</div>
""", unsafe_allow_html=True)
