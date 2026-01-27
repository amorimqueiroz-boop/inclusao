# pages/5_Monitoramento_Avaliacao.py
import streamlit as st
import pandas as pd
import requests
import json
from datetime import datetime
import os
import sys

# ==============================================================================
# 0. IMPORTAÇÃO SEGURA DO OMNI_UTILS
# ==============================================================================
# Adiciona o diretório raiz ao path para conseguir importar omni_utils
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    import omni_utils as ou
except ImportError:
    st.error("Erro crítico: O arquivo 'omni_utils.py' não foi encontrado na pasta raiz.")
    st.stop()

# ✅ set_page_config UMA VEZ SÓ, SEMPRE no topo
st.set_page_config(
    page_title="Omnisfera | Monitoramento",
    page_icon="📊",
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
ou.render_navbar(active_tab="Evolução & Dados")
ou.inject_compact_app_css()

# Garantir que RemixIcon está carregado
st.markdown("""
<link href="https://cdn.jsdelivr.net/npm/remixicon@4.1.0/fonts/remixicon.css" rel="stylesheet">
""", unsafe_allow_html=True)

# Adiciona classe no body para cores específicas das abas
st.markdown("<script>document.body.classList.add('page-sky');</script>", unsafe_allow_html=True)

# ==============================================================================
# AJUSTE FINO DE LAYOUT (ANTES DO HERO - PADRONIZADO)
# ==============================================================================
def forcar_layout_hub():
    st.markdown("""
        <style>
            /* 1. Remove o cabeçalho padrão do Streamlit e a linha colorida */
            header[data-testid="stHeader"] {
                visibility: hidden !important;
                height: 0px !important;
            }

            /* 2. Puxa todo o conteúdo para cima (O SEGREDO ESTÁ AQUI) */
            .block-container {
                padding-top: 0.3rem !important; /* Espaço mínimo entre navbar e hero */
                padding-bottom: 1rem !important;
                margin-top: 0px !important;
            }

            /* 3. Remove padding extra se houver container de navegação */
            div[data-testid="stVerticalBlock"] > div:first-child {
                padding-top: 0px !important;
            }
            
            /* 4. Esconde o menu hambúrguer e rodapé */
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
        </style>
    """, unsafe_allow_html=True)

# CHAME ESTA FUNÇÃO ANTES DO HERO CARD (igual ao PEI)
forcar_layout_hub()

# Cores dos hero cards (paleta vibrante)
ou.inject_hero_card_colors()
# CSS padronizado: abas (pílulas), botões, selects, etc.
ou.inject_unified_ui_css()

# CSS Específico desta página (Hero Card - igual ao Alunos)
st.markdown("""
<style>
    /* CARD HERO - PADRÃO VIA omni_utils.inject_hero_card_colors() */
    .mod-card-wrapper { 
        display: flex; 
        flex-direction: column; 
        margin-bottom: 20px; 
        border-radius: 16px; 
        overflow: hidden; 
        box-shadow: 0 4px 6px rgba(0,0,0,0.02); 
        margin-top: 0 !important; 
    }
    .mod-card-rect { 
        background: white; 
        border-radius: 16px 16px 0 0; 
        padding: 0; 
        border: 1px solid #E2E8F0; 
        border-bottom: none; 
        display: flex; 
        flex-direction: row; 
        align-items: center; 
        height: 130px !important; 
        width: 100%; 
        position: relative; 
        overflow: hidden; 
        transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1); 
    }
    .mod-card-rect:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 24px rgba(0, 0, 0, 0.08);
        border-color: #CBD5E1;
    }
    .mod-bar { 
        width: 6px; 
        height: 100%; 
        flex-shrink: 0; 
    }
    .mod-icon-area { 
        width: 90px; 
        height: 100%; 
        display: flex; 
        align-items: center; 
        justify-content: center; 
        font-size: 1.8rem; 
        flex-shrink: 0; 
        background: #FAFAFA !important; 
        border-right: 1px solid #F1F5F9; 
        transition: all 0.3s ease; 
    }
    .mod-card-rect:hover .mod-icon-area {
        background: white !important;
        transform: scale(1.05) !important;
    }
    .mod-content { 
        flex-grow: 1; 
        padding: 0 24px; 
        display: flex; 
        flex-direction: column; 
        justify-content: center;
        min-width: 0;
        align-items: flex-start;
    }
    .mod-title { 
        font-weight: 800; 
        font-size: 1.1rem; 
        color: #1E293B; 
        margin-bottom: 6px; 
        letter-spacing: -0.3px; 
        transition: color 0.2s;
    }
    .mod-card-rect:hover .mod-title {
        color: #075985;
    }
    .mod-desc { 
        font-size: 0.8rem; 
        color: #64748B; 
        line-height: 1.4; 
        display: -webkit-box;
        -webkit-line-clamp: 2;
        -webkit-box-orient: vertical;
        overflow: hidden;
    }
    
    /* CORES ESPECÍFICAS SKY - Garantir que o ícone tenha cor correta */
    .c-sky { 
        background: #0C4A6E !important; 
    }
    .bg-sky-soft { 
        background: #BAE6FD !important;
        color: #075985 !important;
    }
    /* Garante que o ícone use a cor do bg-sky-soft */
    .mod-icon-area i {
        color: inherit !important;
    }
    .bg-sky-soft i,
    .mod-icon-area.bg-sky-soft i,
    .mod-icon-area.bg-sky-soft i.ri-line-chart-fill {
        color: #075985 !important;
        font-size: 1.8rem !important;
    }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# HERO - MONITORAMENTO
# ==============================================================================
hora = datetime.now().hour
saudacao = "Bom dia" if 5 <= hora < 12 else "Boa tarde" if 12 <= hora < 18 else "Boa noite"
USUARIO_NOME = st.session_state.get("usuario_nome", "Visitante").split()[0]
WORKSPACE_NAME = st.session_state.get("workspace_name", "Workspace")

st.markdown(f"""
<div class="mod-card-wrapper">
    <div class="mod-card-rect">
        <div class="mod-bar c-sky"></div>
        <div class="mod-icon-area bg-sky-soft">
            <i class="ri-line-chart-fill"></i>
        </div>
        <div class="mod-content">
            <div class="mod-title">Evolução & Dados</div>
            <div class="mod-desc">
                {saudacao}, <strong>{USUARIO_NOME}</strong>! Consolide dados do PEI com evidências do Diário de Bordo 
                e acompanhe o progresso dos alunos do workspace <strong>{WORKSPACE_NAME}</strong>.
            </div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ==============================================================================
# FUNÇÕES DO NÚCLEO (Supabase)
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

# --- Carregamento de Alunos ---
@st.cache_data(ttl=60, show_spinner=False)
def list_students_rest():
    """Busca estudantes do Supabase incluindo o campo pei_data."""
    WORKSPACE_ID = st.session_state.get("workspace_id")
    if not WORKSPACE_ID:
        pass 

    try:
        base = (
            f"{_sb_url()}/rest/v1/students"
            f"?select=id,name,grade,class_group,diagnosis,created_at,pei_data"
            f"&workspace_id=eq.{WORKSPACE_ID}"
            f"&order=created_at.desc"
        )
        r = requests.get(base, headers=_headers(), timeout=20)
        return r.json() if r.status_code == 200 else []
    except Exception as e:
        st.error(f"Erro ao carregar alunos: {str(e)}")
        return []

def carregar_estudantes_formatados():
    """Processa a lista crua usando sua lógica de prioridade do pei_data."""
    dados = list_students_rest()
    estudantes = []

    for item in dados:
        pei_completo = item.get("pei_data") or {}
        
        # Tenta pegar contexto da IA ou monta fallback
        contexto_ia = ""
        if isinstance(pei_completo, dict):
            contexto_ia = pei_completo.get("ia_sugestao", "")
        
        if not contexto_ia:
            diag = item.get("diagnosis", "Não informado")
            serie = item.get("grade", "")
            contexto_ia = f"Aluno: {item.get('name')}. Série: {serie}. Diagnóstico: {diag}."

        estudante = {
            "nome": item.get("name", ""),
            "serie": item.get("grade", ""),
            "id": item.get("id", ""),
            "pei_data": pei_completo, # Objeto completo para usar na rubrica
            "diagnosis": item.get("diagnosis", "")
        }
        if estudante["nome"]:
            estudantes.append(estudante)
            
    return estudantes

# ==============================================================================
# FUNÇÕES ESPECÍFICAS DO MONITORAMENTO
# ==============================================================================

def get_student_logs(student_id, limit=5):
    """Busca evidências no Diário de Bordo para confrontar com o PEI."""
    try:
        # Ajuste o nome da tabela 'daily_logs' se for diferente no seu Supabase
        url = (
            f"{_sb_url()}/rest/v1/daily_logs"
            f"?student_id=eq.{student_id}"
            f"&select=created_at,content,tags,sentiment"
            f"&order=created_at.desc&limit={limit}"
        )
        r = requests.get(url, headers=_headers())
        return r.json() if r.status_code == 200 else []
    except:
        return []

def save_assessment(student_id, rubric_data, observation):
    """Salva a avaliação consolidada."""
    payload = {
        "student_id": student_id,
        "date_assessed": datetime.now().isoformat(),
        "rubric_data": rubric_data,
        "observation": observation,
        "evaluator_id": st.session_state.get("user_id", "anon"),
        "workspace_id": st.session_state.get("workspace_id")
    }
    
    # POST na tabela 'monitoring_assessments' (Criar essa tabela se não existir)
    url = f"{_sb_url()}/rest/v1/monitoring_assessments"
    r = requests.post(url, headers=_headers(), json=payload)
    return r.status_code in [200, 201]

# ==============================================================================
# INTERFACE PRINCIPAL
# ==============================================================================

# Verificação de autenticação
if not st.session_state.get("autenticado") or not st.session_state.get("workspace_id"):
    st.warning("🔒 Acesso restrito. Faça login na Home.")
    st.stop()

# Espaçamento após hero card
st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

st.markdown("### 📊 Consolidação de Dados")
st.markdown("Consolidação de dados do **PEI** com evidências do **Diário de Bordo**.")

# --- SELETOR DE ESTUDANTE ---
lista_alunos = carregar_estudantes_formatados()
opcoes = {a['nome']: a for a in lista_alunos}

if not opcoes:
    st.warning("Nenhum aluno encontrado ou erro na conexão.")
    st.stop()

col_sel, col_blank = st.columns([1, 2])
with col_sel:
    nome_selecionado = st.selectbox("Selecione o Estudante:", ["Selecione..."] + list(opcoes.keys()))

if nome_selecionado != "Selecione...":
    aluno = opcoes[nome_selecionado]
    student_id = aluno['id']
    pei = aluno['pei_data'] if isinstance(aluno['pei_data'], dict) else {}
    
    # Busca evidências reais
    logs = get_student_logs(student_id)

    st.divider()

    # --- ÁREA DE CONFRONTO (PEI vs DIÁRIO) ---
    c1, c2 = st.columns(2)
    
    with c1:
        st.subheader("🎯 Expectativa (PEI)")
        st.caption("Objetivos cadastrados no Plano de Ensino")
        
        # Tenta extrair dados estruturados do seu JSON pei_data
        objetivos = pei.get('objetivos', []) or pei.get('goals', [])
        
        if objetivos:
            for obj in objetivos:
                st.info(f"📍 {obj}")
        else:
            # Se não tiver estrutura, mostra o diagnóstico
            st.info(f"**Diagnóstico Base:** {aluno['diagnosis']}")
            st.write("Sem objetivos específicos estruturados no JSON.")

    with c2:
        st.subheader("📝 Realidade (Diário)")
        st.caption("Últimos registros de atividades")
        
        if logs:
            for log in logs:
                data = datetime.fromisoformat(log['created_at'].replace('Z', '+00:00')).strftime("%d/%m")
                # Cardzinho estilo 'timeline'
                st.markdown(f"""
                <div style="border-left: 3px solid #075985; padding-left: 10px; margin-bottom: 10px; background: #F8FAFC; padding: 10px; border-radius: 4px;">
                    <small style="color:gray">{data}</small><br>
                    {log.get('content', '')}
                </div>
                """, unsafe_allow_html=True)
        else:
            st.warning("Nenhum registro encontrado no diário para este aluno.")

    st.divider()

    # --- RUBRICA DE AVALIAÇÃO ---
    st.subheader("🧩 Rubrica de Desenvolvimento")
    
    with st.form("avaliacao_rubrica"):
        # Critérios da Rubrica
        criterios = {
            "autonomia": "Nível de Autonomia",
            "social": "Interação Social",
            "conteudo": "Apropriação do Conteúdo (PEI)",
            "comportamento": "Regulação Comportamental"
        }
        
        respostas = {}
        cols = st.columns(2)
        i = 0
        
        # Cria os sliders dinamicamente
        for chave, titulo in criterios.items():
            col_atual = cols[i % 2]
            with col_atual:
                respostas[chave] = st.select_slider(
                    f"**{titulo}**",
                    options=["Não Iniciado", "Iniciado", "Em Desenvolvimento", "Consolidado"],
                    value="Em Desenvolvimento"
                )
            i += 1
            
        st.write("")
        obs = st.text_area("Observação Final da Avaliação", height=100)
        
        btn_salvar = st.form_submit_button("💾 Salvar Monitoramento", type="primary")
        
        if btn_salvar:
            sucesso = save_assessment(student_id, respostas, obs)
            if sucesso:
                st.success("Avaliação salva com sucesso no banco de dados!")
                st.rerun()
            else:
                st.error("Erro ao salvar. Verifique a tabela 'monitoring_assessments' no Supabase.")

# Rodapé
st.markdown(
    f"""
    <div style='
        text-align: center;
        color: #64748B;
        font-size: 0.75rem;
        padding: 20px;
        border-top: 1px solid #E2E8F0;
        margin-top: 40px;
    '>
        <strong>Omnisfera {APP_VERSION}</strong> • Monitoramento & Avaliação
    </div>
    """,
    unsafe_allow_html=True,
)
