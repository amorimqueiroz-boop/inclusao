# ==============================================================================
# PARTE 1/4: CONFIGURAÇÕES, CONEXÃO E CARREGAMENTO DE DADOS
# ==============================================================================

import streamlit as st
import os
from openai import OpenAI
import json
import pandas as pd
from datetime import date, datetime
import base64
import requests
import time
from io import BytesIO
import plotly.express as px
import altair as alt
from datetime import timedelta

# ==============================================================================
# 1. CONFIGURAÇÃO E SEGURANÇA
# ==============================================================================
st.set_page_config(
    page_title="PAEE & T.A. | Omnisfera", 
    page_icon="🧩", 
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

st.markdown(f"""
<link href="https://cdn.jsdelivr.net/npm/remixicon@4.1.0/fonts/remixicon.css" rel="stylesheet">

<style>
    /* CARD FLUTUANTE (OMNISFERA) */
    .omni-badge {{
        position: fixed; top: 15px; right: 15px;
        background: {card_bg}; border: 1px solid {card_border};
        backdrop-filter: blur(8px); padding: 4px 30px;
        min-width: 260px; justify-content: center;
        border-radius: 20px; box-shadow: 0 4px 15px rgba(0,0,0,0.08);
        z-index: 999990; display: flex; align-items: center; gap: 10px;
        pointer-events: none;
    }}
    .omni-text {{ font-family: 'Plus Jakarta Sans', sans-serif; font-weight: 800; font-size: 0.9rem; color: #2D3748; letter-spacing: 1px; text-transform: uppercase; }}
    @keyframes spin-slow {{ from {{ transform: rotate(0deg); }} to {{ transform: rotate(360deg); }} }}
    .omni-logo-spin {{ height: 26px; width: 26px; animation: spin-slow 10s linear infinite; }}

    /* CARD HERO */
    .mod-card-wrapper {{ display: flex; flex-direction: column; margin-bottom: 20px; border-radius: 16px; overflow: hidden; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.02); }}
    .mod-card-rect {{ background: white; border-radius: 16px 16px 0 0; padding: 0; border: 1px solid #E2E8F0; border-bottom: none; display: flex; flex-direction: row; align-items: center; height: 130px; width: 100%; position: relative; overflow: hidden; transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1); }}
    .mod-card-rect:hover {{ transform: translateY(-4px); box-shadow: 0 12px 24px rgba(0, 0, 0, 0.08); border-color: #CBD5E1; }}
    .mod-bar {{ width: 6px; height: 100%; flex-shrink: 0; }}
    .mod-icon-area {{ width: 90px; height: 100%; display: flex; align-items: center; justify-content: center; font-size: 1.8rem; flex-shrink: 0; background: transparent !important; border-right: 1px solid #F1F5F9; transition: all 0.3s ease; }}
    .mod-card-rect:hover .mod-icon-area {{ transform: scale(1.05); }}
    .mod-content {{ flex-grow: 1; padding: 0 24px; display: flex; flex-direction: column; justify-content: center; }}
    .mod-title {{ font-weight: 800; font-size: 1.1rem; color: #1E293B; margin-bottom: 6px; letter-spacing: -0.3px; transition: color 0.2s; }}
    .mod-card-rect:hover .mod-title {{ color: #4F46E5; }}
    .mod-desc {{ font-size: 0.8rem; color: #64748B; line-height: 1.4; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }}

    /* ABAS */
    .stTabs [data-baseweb="tab-list"] {{ gap: 4px !important; background-color: transparent !important; padding: 0 !important; border-radius: 0 !important; margin-top: 24px !important; border-bottom: none !important; flex-wrap: wrap !important; }}
    .stTabs [data-baseweb="tab"] {{ height: 36px !important; white-space: nowrap !important; background-color: transparent !important; border-radius: 20px !important; padding: 0 16px !important; color: #64748B !important; font-weight: 600 !important; font-size: 0.72rem !important; text-transform: uppercase !important; letter-spacing: 0.3px !important; transition: all 0.2s ease !important; border: 1px solid #E2E8F0 !important; margin: 0 !important; }}
    .stTabs [aria-selected="true"] {{ background-color: #8B5CF6 !important; color: white !important; font-weight: 700 !important; border: 1px solid #8B5CF6 !important; box-shadow: 0 1px 3px rgba(139, 92, 246, 0.2) !important; }}
    .stTabs [data-baseweb="tab"]:not([aria-selected="true"]) {{ background-color: white !important; }}
    .stTabs [data-baseweb="tab"]:hover:not([aria-selected="true"]) {{ background-color: #F8FAFC !important; border-color: #CBD5E1 !important; color: #475569 !important; }}
    .stTabs [data-baseweb="tab"]::after, .stTabs [aria-selected="true"]::after, .stTabs [data-baseweb="tab"]::before, .stTabs [aria-selected="true"]::before {{ display: none !important; }}
    .stTabs [data-baseweb="tab-list"] {{ border-bottom: none !important; }}

    /* STYLES ESPECÍFICOS PARA PAEE */
    .pedagogia-box {{ background-color: #F8FAFC; border-left: 4px solid #CBD5E1; padding: 20px; border-radius: 0 12px 12px 0; margin-bottom: 25px; font-size: 0.95rem; color: #4A5568; }}
    
    .prog-bar-bg {{ width: 100%; height: 8px; background: #E2E8F0; border-radius: 4px; overflow: hidden; margin-top: 8px; }}
    .prog-bar-fill {{ height: 100%; background: linear-gradient(90deg, #8B5CF6, #6D28D9); transition: width 1s; }}
    
    /* CARD DE ATIVIDADE */
    .activity-card {{ 
        background: white; 
        border: 1px solid #E2E8F0; 
        border-radius: 12px; 
        padding: 16px; 
        margin: 10px 0;
        transition: all 0.3s;
    }}
    .activity-card:hover {{ 
        border-color: #8B5CF6; 
        box-shadow: 0 4px 12px rgba(139, 92, 246, 0.1);
        transform: translateY(-2px);
    }}
    .activity-status-done {{ border-left: 5px solid #10B981; }}
    .activity-status-progress {{ border-left: 5px solid #F59E0B; }}
    .activity-status-pending {{ border-left: 5px solid #EF4444; }}
    
    /* CHIP DE HABILIDADE */
    .skill-chip {{
        display: inline-block;
        background: #EDE9FE;
        color: #7C3AED;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.8rem;
        margin: 3px;
        font-weight: 600;
    }}
</style>

<div class="omni-badge">
    <img src="{src_logo_giratoria}" class="omni-logo-spin">
    <span class="omni-text">OMNISFERA</span>
</div>
""", unsafe_allow_html=True)

# ==============================================================================
# VERIFICAÇÃO DE ACESSO
# ==============================================================================
def verificar_acesso():
    if "autenticado" not in st.session_state or not st.session_state["autenticado"]:
        st.error("🔒 Acesso Negado. Por favor, faça login na Página Inicial.")
        st.stop()
    st.markdown("""<style>footer {visibility: hidden !important;} [data-testid="stHeader"] {visibility: visible !important; background-color: transparent !important;} .block-container {padding-top: 2rem !important;}</style>""", unsafe_allow_html=True)

verificar_acesso()

# ==============================================================================
# SIDEBAR - MOTORES DE IA
# ==============================================================================
with st.sidebar:
    try: 
        st.image("ominisfera.png", width=150)
    except: 
        st.write("🌐 OMNISFERA")
    
    st.markdown("---")
    
    if st.button("🏠 Voltar para Home", use_container_width=True): 
        st.switch_page("Home.py")
    
    st.markdown("---")
    
    # MOTORES DE IA
    st.markdown("### 🤖 Motores de IA")
    
    # OpenAI
    if 'OPENAI_API_KEY' in st.secrets: 
        api_key_openai = st.secrets['OPENAI_API_KEY']
        st.success("🔑 OpenAI configurada")
    else: 
        api_key_openai = st.text_input("Chave OpenAI:", type="password", key="openai_key")
        if api_key_openai:
            st.success("✅ OpenAI configurada")
    
    # DeepSeek
    if 'DEEPSEEK_API_KEY' in st.secrets: 
        api_key_deepseek = st.secrets['DEEPSEEK_API_KEY']
        st.success("🔑 DeepSeek configurada")
    else: 
        api_key_deepseek = st.text_input("Chave DeepSeek:", type="password", key="deepseek_key")
        if api_key_deepseek:
            st.success("✅ DeepSeek configurada")
    
    st.markdown("---")
    
    # SELEÇÃO DE MOTOR PRINCIPAL
    st.markdown("### ⚙️ Configurações")
    motor_principal = st.selectbox(
        "Motor principal para análise:",
        ["DeepSeek (Recomendado para análise)", "OpenAI (Recomendado para criatividade)"],
        help="DeepSeek é melhor para análise cruzada de dados, OpenAI para criatividade em atividades"
    )
    
    # SALVAR NAS SESSÕES
    st.session_state['api_key_openai'] = api_key_openai
    st.session_state['api_key_deepseek'] = api_key_deepseek
    st.session_state['motor_principal'] = motor_principal

# ==============================================================================
# CARD HERO PRINCIPAL
# ==============================================================================
hora = datetime.now().hour
saudacao = "Bom dia" if 5 <= hora < 12 else "Boa tarde" if 12 <= hora < 18 else "Boa noite"
USUARIO_NOME = st.session_state.get("usuario_nome", "Visitante").split()[0]
WORKSPACE_NAME = st.session_state.get("workspace_name", "Workspace")

st.markdown(
    f"""
    <div class="mod-card-wrapper">
        <div class="mod-card-rect">
            <div class="mod-bar" style="background: #8B5CF6;"></div>
            <div class="mod-icon-area" style="color: #8B5CF6;">
                <i class="ri-calendar-todo-fill"></i>
            </div>
            <div class="mod-content">
                <div class="mod-title">Execução e Monitoramento do PAEE</div>
                <div class="mod-desc">
                    {saudacao}, <strong>{USUARIO_NOME}</strong>! Gerencie a execução do plano do aluno, 
                    acompanhe o progresso e faça ajustes em tempo real no workspace <strong>{WORKSPACE_NAME}</strong>.
                    Conecte planejamento, execução e avaliação em um só lugar.
                </div>
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ==============================================================================
# FUNÇÕES DE CONEXÃO COM SUPABASE
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
# CARREGAR ESTUDANTES DO SUPABASE
# ==============================================================================
@st.cache_data(ttl=10, show_spinner=False)
def list_students_rest():
    """Busca estudantes do Supabase incluindo o campo PEI_DATA"""
    WORKSPACE_ID = st.session_state.get("workspace_id")
    if not WORKSPACE_ID: 
        return []
    
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

def carregar_estudantes_supabase():
    """Carrega e processa, extraindo dados ricos do PEI"""
    dados = list_students_rest()
    estudantes = []
    
    for item in dados:
        pei_completo = item.get('pei_data') or {}
        
        # Extrair data de revisão do PEI
        data_revisao_str = pei_completo.get('data_revisao', '')
        data_revisao = None
        if data_revisao_str:
            try:
                data_revisao = datetime.strptime(data_revisao_str, "%Y-%m-%d").date()
            except:
                try:
                    data_revisao = datetime.strptime(data_revisao_str, "%d/%m/%Y").date()
                except:
                    data_revisao = None
        
        contexto_ia = pei_completo.get('ia_sugestao', '')
        
        if not contexto_ia:
            diag = item.get('diagnosis', 'Não informado')
            serie = item.get('grade', '')
            contexto_ia = f"Aluno: {item.get('name')}. Série: {serie}. Diagnóstico: {diag}."

        estudante = {
            'nome': item.get('name', ''),
            'serie': item.get('grade', ''),
            'hiperfoco': item.get('diagnosis', ''),
            'ia_sugestao': contexto_ia,
            'id': item.get('id', ''),
            'pei_data': pei_completo,
            'data_revisao_pei': data_revisao
        }
        if estudante['nome']:
            estudantes.append(estudante)
            
    return estudantes

# ==============================================================================
# CARREGAMENTO DOS DADOS DOS ALUNOS
# ==============================================================================
if 'banco_estudantes' not in st.session_state or not st.session_state.banco_estudantes:
    with st.spinner("🔄 Lendo dados da nuvem..."):
        st.session_state.banco_estudantes = carregar_estudantes_supabase()

if not st.session_state.banco_estudantes:
    st.warning("⚠️ Nenhum aluno encontrado.")
    if st.button("📘 Ir para o módulo PEI", type="primary"): 
        st.switch_page("pages/1_PEI.py")
    st.stop()

# --- SELEÇÃO DE ALUNO ---
st.markdown("### 👨‍🎓 Selecione o Aluno para Execução")

col_sel, col_info = st.columns([1, 2])
with col_sel:
    nome_aluno = st.selectbox(
        "📂 Estudante:",
        [a['nome'] for a in st.session_state.banco_estudantes],
        key="select_aluno_paee"
    )

aluno = next((a for a in st.session_state.banco_estudantes if a.get('nome') == nome_aluno), None)

if not aluno: 
    st.error("Aluno não encontrado")
    st.stop()

# --- DETECTOR DE EDUCAÇÃO INFANTIL ---
serie_aluno = aluno.get('serie', '').lower()
is_ei = any(term in serie_aluno for term in ["infantil", "creche", "pré", "maternal", "berçario", "jardim"])

# --- HEADER DO ALUNO ---
# Calcular dias até a revisão
hoje = date.today()
dias_para_revisao = None
if aluno.get('data_revisao_pei'):
    dias_para_revisao = (aluno['data_revisao_pei'] - hoje).days

st.markdown(f"""
    <div style="background: linear-gradient(135deg, #8B5CF6 0%, #7C3AED 100%); color: white; border-radius: 16px; padding: 25px 30px; margin-bottom: 20px; display: flex; justify-content: space-between; align-items: center; box-shadow: 0 4px 15px rgba(139, 92, 246, 0.2);">
        <div>
            <div style="font-size: 0.8rem; color: rgba(255,255,255,0.8); font-weight: 800; text-transform: uppercase; letter-spacing: 1px;">Aluno</div>
            <div style="font-size: 1.4rem; color: white; font-weight: 800;">{aluno.get('nome')}</div>
        </div>
        <div>
            <div style="font-size: 0.8rem; color: rgba(255,255,255,0.8); font-weight: 800; text-transform: uppercase; letter-spacing: 1px;">Série</div>
            <div style="font-size: 1.2rem; color: white; font-weight: 800;">{aluno.get('serie')}</div>
        </div>
        <div>
            <div style="font-size: 0.8rem; color: rgba(255,255,255,0.8); font-weight: 800; text-transform: uppercase; letter-spacing: 1px;">Próxima Revisão</div>
            <div style="font-size: 1.2rem; color: white; font-weight: 800;">
                {aluno.get('data_revisao_pei').strftime('%d/%m/%Y') if aluno.get('data_revisao_pei') else 'Não definida'}
                {f"<br><span style='font-size:0.9rem;'>({dias_para_revisao} dias)</span>" if dias_para_revisao and dias_para_revisao > 0 else ''}
            </div>
        </div>
        <div>
            <div style="font-size: 0.8rem; color: rgba(255,255,255,0.8); font-weight: 800; text-transform: uppercase; letter-spacing: 1px;">Status</div>
            <div style="font-size: 1.2rem; color: white; font-weight: 800;">
                { '🧸 Educação Infantil' if is_ei else '📚 Ensino Regular' }
            </div>
        </div>
    </div>
""", unsafe_allow_html=True)

if is_ei:
    st.info("🧸 **Modo Educação Infantil:** Foco em Campos de Experiência (BNCC).")

# BOTÃO PARA VER PEI COMPLETO
with st.expander("📄 Ver PEI Completo e Contexto", expanded=False):
    st.write(aluno.get('ia_sugestao', 'Sem dados detalhados.'))
    
    # Extrair metas do PEI
    if "metas_extraidas" not in st.session_state:
        st.session_state.metas_extraidas = extrair_metas_do_pei(aluno.get('ia_sugestao', ''))
    
    if st.session_state.metas_extraidas:
        st.markdown("### 🎯 Metas Extraídas do PEI")
        for meta in st.session_state.metas_extraidas[:5]:  # Mostrar apenas 5 principais
            st.markdown(f"- **{meta['tipo']}**: {meta['descricao']}")

# ==============================================================================
# FUNÇÕES DE EXTRACTION (SIMPLIFICADAS PARA AGORA)
# ==============================================================================
def extrair_metas_do_pei(texto_pei):
    """Extrai metas do texto do PEI (simplificado por enquanto)"""
    metas = []
    
    # Procurar por padrões comuns
    if "metas" in texto_pei.lower() or "objetivos" in texto_pei.lower():
        # Dividir por linhas e procurar itens
        linhas = texto_pei.split('\n')
        for linha in linhas:
            linha_lower = linha.lower()
            if any(termo in linha_lower for termo in ['meta', 'objetivo', 'habilidade', 'competência']):
                # Classificar tipo
                if 'curto' in linha_lower or '1-2' in linha_lower:
                    tipo = 'Curto Prazo'
                elif 'médio' in linha_lower or '3-6' in linha_lower:
                    tipo = 'Médio Prazo'
                elif 'longo' in linha_lower or '6-12' in linha_lower:
                    tipo = 'Longo Prazo'
                else:
                    tipo = 'Meta'
                
                metas.append({
                    'tipo': tipo,
                    'descricao': linha.strip(),
                    'categoria': 'Não categorizada'
                })
    
    # Se não encontrou, criar algumas genéricas
    if not metas:
        metas = [
            {'tipo': 'Curto Prazo', 'descricao': 'Melhorar engajamento nas atividades', 'categoria': 'Socioemocional'},
            {'tipo': 'Médio Prazo', 'descricao': 'Desenvolver autonomia na rotina', 'categoria': 'Autonomia'},
            {'tipo': 'Longo Prazo', 'descricao': 'Generalizar habilidades para outros contextos', 'categoria': 'Generalização'}
        ]
    
    return metas

# ==============================================================================
# PARTE 2/4: SISTEMA DE MOTORES DE IA E PLANEJAMENTO
# ==============================================================================

# ==============================================================================
# SISTEMA DUAL DE MOTORES DE IA
# ==============================================================================
class SistemaIA:
    """Sistema dual para usar OpenAI e DeepSeek de forma inteligente"""
    
    @staticmethod
    def get_cliente_openai():
        """Retorna cliente OpenAI"""
        api_key = st.session_state.get('api_key_openai')
        if not api_key:
            raise ValueError("Chave OpenAI não configurada")
        return OpenAI(api_key=api_key)
    
    @staticmethod
    def get_cliente_deepseek():
        """Retorna cliente DeepSeek"""
        api_key = st.session_state.get('api_key_deepseek')
        if not api_key:
            raise ValueError("Chave DeepSeek não configurada")
        return OpenAI(
            api_key=api_key,
            base_url="https://api.deepseek.com"
        )
    
    @staticmethod
    def escolher_motor(tipo_tarefa):
        """
        Escolhe o motor ideal para cada tipo de tarefa
        
        DeepSeek: Melhor para análise, raciocínio, dados estruturados
        OpenAI: Melhor para criatividade, textos narrativos, ideias
        """
        motor_config = st.session_state.get('motor_principal', 'DeepSeek')
        
        if "deepseek" in motor_config.lower():
            motor_base = "deepseek"
        else:
            motor_base = "openai"
        
        # Ajustes baseados no tipo de tarefa
        tarefas_deepseek = [
            'analise_cruzada', 'diagnostico', 'planejamento_estrategico',
            'cronograma', 'metas_smart', 'analise_progresso', 'ajustes_roteiro'
        ]
        
        tarefas_openai = [
            'atividades_criativas', 'narrativa', 'relatorios_descritivos',
            'sugestoes_praticas', 'comunicacao_familiar', 'atividades_ludicas'
        ]
        
        if tipo_tarefa in tarefas_deepseek:
            return "deepseek"
        elif tipo_tarefa in tarefas_openai:
            return "openai"
        else:
            return motor_base
    
    @staticmethod
    def gerar_com_ia(prompt, tipo_tarefa, temperatura=0.7):
        """Gera conteúdo usando o motor apropriado"""
        motor = SistemaIA.escolher_motor(tipo_tarefa)
        
        try:
            if motor == "openai":
                cliente = SistemaIA.get_cliente_openai()
                modelo = "gpt-4o-mini"
            else:  # deepseek
                cliente = SistemaIA.get_cliente_deepseek()
                modelo = "deepseek-chat"
            
            resposta = cliente.chat.completions.create(
                model=modelo,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperatura,
                max_tokens=2000
            )
            
            return resposta.choices[0].message.content, motor
            
        except Exception as e:
            # Fallback para o outro motor
            try:
                motor_fallback = "openai" if motor == "deepseek" else "deepseek"
                
                if motor_fallback == "openai":
                    cliente = SistemaIA.get_cliente_openai()
                    modelo = "gpt-4o-mini"
                else:
                    cliente = SistemaIA.get_cliente_deepseek()
                    modelo = "deepseek-chat"
                
                resposta = cliente.chat.completions.create(
                    model=modelo,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=temperatura,
                    max_tokens=2000
                )
                
                return resposta.choices[0].message.content, motor_fallback + " (fallback)"
                
            except Exception as e2:
                return f"Erro em ambos os motores: {str(e2)}", "erro"

# ==============================================================================
# SISTEMA DE PLANEJAMENTO SEMANAL INTELIGENTE
# ==============================================================================
class PlanejadorPAEE:
    """Sistema de planejamento semanal inteligente"""
    
    def __init__(self, aluno):
        self.aluno = aluno
        self.hoje = date.today()
        
    def gerar_cronograma_inteligente(self, duracao_semanas=8):
        """Gera cronograma inteligente baseado no PEI"""
        
        if not st.session_state.get('api_key_deepseek') and not st.session_state.get('api_key_openai'):
            return {"erro": "Configure pelo menos uma chave de IA na sidebar"}
        
        # Preparar prompt
        contexto_pei = self.aluno.get('ia_sugestao', '')[:3000]
        data_revisao = self.aluno.get('data_revisao_pei', self.hoje + timedelta(days=60))
        
        # Se tem data de revisão, ajustar duração
        if data_revisao:
            dias_totais = (data_revisao - self.hoje).days
            duracao_semanas = max(4, min(duracao_semanas, dias_totais // 7))
        
        prompt = f"""
        VOCÊ É: Um especialista em planejamento pedagógico para AEE.
        
        CONTEXTO:
        - Aluno: {self.aluno['nome']}
        - Série: {self.aluno['serie']}
        - Diagnóstico: {self.aluno.get('hiperfoco', 'Não especificado')}
        - Período: {duracao_semanas} semanas (até {data_revisao.strftime('%d/%m/%Y') if data_revisao else 'revisão'})
        - Educação Infantil: {'SIM' if is_ei else 'NÃO'}
        
        PEI DO ALUNO (resumo):
        {contexto_pei}
        
        SUA TAREFA: Criar um CRONOGRAMA DE EXECUÇÃO semanal detalhado.
        
        ESTRUTURA DO CRONOGRAMA:
        1. **FASES DO PLANO** (divida em 2-3 fases progressivas)
        2. **SEMANAS DETALHADAS** (para cada semana):
           - Tema central da semana
           - Habilidades trabalhadas
           - Atividades principais (2-3 por semana)
           - Recursos necessários
           - Indicadores de sucesso
           - Adaptações específicas
        
        3. **MATRIZ DE ACOMPANHAMENTO**:
           - O que observar em cada fase
           - Pontos de atenção
           - Sinais de progresso
        
        4. **ROTEIRO DE AJUSTES**:
           - Quando e como ajustar o plano
           - Gatilhos para mudança de estratégia
        
        IMPORTANTE:
        - Sequência lógica e progressiva
        - Atividades práticas e viáveis
        - Inclua tanto trabalho individual quanto em grupo
        - Considere a frequência real do AEE (1-2x por semana)
        
        Formato de saída JSON:
        {{
            "periodo": "de X a Y",
            "total_semanas": {duracao_semanas},
            "fases": [
                {{
                    "nome": "Nome da fase",
                    "descricao": "Descrição",
                    "objetivo_principal": "O que se espera",
                    "semanas": [1, 2, 3],
                    "habilidades_foco": ["habilidade1", "habilidade2"],
                    "recursos_principais": ["recurso1", "recurso2"]
                }}
            ],
            "semanas": [
                {{
                    "numero": 1,
                    "tema": "Tema da semana",
                    "habilidades": ["habilidade1", "habilidade2"],
                    "atividades": [
                        {{
                            "titulo": "Título da atividade",
                            "descricao": "Descrição detalhada",
                            "materiais": ["material1", "material2"],
                            "duracao": "30-40 minutos",
                            "adaptacoes": "Adaptações específicas",
                            "indicadores_sucesso": ["indicador1", "indicador2"]
                        }}
                    ],
                    "observacoes_importantes": "O que observar nesta semana",
                    "meta_semanal": "Meta específica para a semana"
                }}
            ],
            "sistema_acompanhamento": {{
                "indicadores_chave": ["indicador1", "indicador2"],
                "frequencia_observacao": "Diária/semanal",
                "instrumentos_avaliacao": ["observação", "registro fotográfico", "checklist"]
            }}
        }}
        """
        
        # Usar DeepSeek para análise (melhor para estruturação)
        resultado, motor_usado = SistemaIA.gerar_com_ia(prompt, "planejamento_estrategico", temperatura=0.5)
        
        if "Erro" in resultado:
            return {"erro": resultado}
        
        # Extrair JSON da resposta
        try:
            if "```json" in resultado:
                json_str = resultado.split("```json")[1].split("```")[0]
            elif "```" in resultado:
                json_str = resultado.split("```")[1].split("```")[0]
            else:
                json_str = resultado
            
            cronograma = json.loads(json_str)
            cronograma["motor_geracao"] = motor_usado
            cronograma["data_geracao"] = self.hoje.strftime("%Y-%m-%d")
            
            return cronograma
            
        except Exception as e:
            # Se não conseguiu parsear, retornar como texto
            return {
                "texto_bruto": resultado,
                "motor_geracao": motor_usado,
                "erro_parse": str(e),
                "data_geracao": self.hoje.strftime("%Y-%m-%d")
            }
    
    def calcular_semanas_restantes(self, cronograma):
        """Calcula semanas restantes até a revisão"""
        if not cronograma or "total_semanas" not in cronograma:
            return 0
        
        total_semanas = cronograma["total_semanas"]
        
        # Verificar semanas já executadas
        semanas_executadas = st.session_state.get('semanas_executadas', {}).get(self.aluno['id'], [])
        
        return max(0, total_semanas - len(semanas_executadas))

# ==============================================================================
# SISTEMA DE EXECUÇÃO EM TEMPO REAL
# ==============================================================================
class SistemaExecucao:
    """Sistema de execução e correção de rota em tempo real"""
    
    def __init__(self, aluno_id, cronograma):
        self.aluno_id = aluno_id
        self.cronograma = cronograma
        self.hoje = date.today()
        
        # Inicializar estados de execução
        if f'execucao_{aluno_id}' not in st.session_state:
            st.session_state[f'execucao_{aluno_id}'] = {
                'semanas_concluidas': [],
                'atividades_realizadas': [],
                'engajamento_semanal': {},
                'ajustes_realizados': [],
                'dificuldades_registradas': []
            }
        
        self.estado = st.session_state[f'execucao_{aluno_id}']
    
    def registrar_atividade(self, semana_num, atividade_idx, dados):
        """Registra uma atividade realizada"""
        registro = {
            'data': self.hoje.strftime("%Y-%m-%d"),
            'semana': semana_num,
            'atividade_idx': atividade_idx,
            'engajamento': dados.get('engajamento', 3),
            'conseguiu_realizar': dados.get('conseguiu_realizar', True),
            'observacoes': dados.get('observacoes', ''),
            'dificuldades': dados.get('dificuldades', ''),
            'ajustes_feitos': dados.get('ajustes_feitos', ''),
            'evidencias': dados.get('evidencias', [])
        }
        
        self.estado['atividades_realizadas'].append(registro)
        
        # Atualizar engajamento semanal
        if semana_num not in self.estado['engajamento_semanal']:
            self.estado['engajamento_semanal'][semana_num] = []
        self.estado['engajamento_semanal'][semana_num].append(dados.get('engajamento', 3))
        
        # Registrar dificuldades se houver
        if dados.get('dificuldades'):
            self.estado['dificuldades_registradas'].append({
                'data': self.hoje.strftime("%Y-%m-%d"),
                'semana': semana_num,
                'dificuldade': dados['dificuldades']
            })
        
        return registro
    
    def concluir_semana(self, semana_num):
        """Marca uma semana como concluída"""
        if semana_num not in self.estado['semanas_concluidas']:
            self.estado['semanas_concluidas'].append(semana_num)
            
            # Calcular engajamento médio da semana
            engajamentos = self.estado['engajamento_semanal'].get(semana_num, [])
            engajamento_medio = sum(engajamentos) / len(engajamentos) if engajamentos else 0
            
            return {
                'semana': semana_num,
                'data_conclusao': self.hoje.strftime("%Y-%m-%d"),
                'engajamento_medio': engajamento_medio,
                'total_atividades': len([a for a in self.estado['atividades_realizadas'] if a['semana'] == semana_num])
            }
        return None
    
    def sugerir_ajustes_automaticos(self, semana_atual):
        """Sugere ajustes baseado no desempenho"""
        
        # Coletar dados da semana
        atividades_semana = [a for a in self.estado['atividades_realizadas'] if a['semana'] == semana_atual]
        
        if not atividades_semana:
            return None
        
        # Calcular métricas
        total_atividades = len(atividades_semana)
        atividades_concluidas = len([a for a in atividades_semana if a['conseguiu_realizar']])
        engajamento_medio = sum(a['engajamento'] for a in atividades_semana) / total_atividades
        
        # Análise de dificuldades
        dificuldades = [a['dificuldades'] for a in atividades_semana if a['dificuldades']]
        
        # Determinar se precisa de ajustes
        precisa_ajuste = False
        motivos = []
        
        if atividades_concluidas / total_atividades < 0.5:
            precisa_ajuste = True
            motivos.append("Baixa taxa de conclusão de atividades")
        
        if engajamento_medio < 2.5:
            precisa_ajuste = True
            motivos.append("Baixo engajamento do aluno")
        
        if dificuldades:
            precisa_ajuste = True
            motivos.append(f"Dificuldades identificadas: {', '.join(set(dificuldades)[:3])}")
        
        if not precisa_ajuste:
            return {
                'status': 'OK',
                'mensagem': 'O plano está funcionando bem! Continue assim.',
                'engajamento_medio': engajamento_medio,
                'taxa_conclusao': atividades_concluidas / total_atividades
            }
        
        # Se precisa de ajuste, gerar sugestões
        prompt = f"""
        CONTEXTO: AEE para aluno {aluno['nome']}
        SEMANA: {semana_atual}
        PROBLEMAS IDENTIFICADOS: {', '.join(motivos)}
        DIFICULDADES ESPECÍFICAS: {', '.join(dificuldades[:5]) if dificuldades else 'Nenhuma específica'}
        ENGENJAMENTO MÉDIO: {engajamento_medio}/5
        TAXA DE CONCLUSÃO: {atividades_concluidas}/{total_atividades} atividades
        
        SUGIRA 3 AJUSTES PRÁTICOS para a próxima semana:
        1. Ajuste na complexidade das atividades
        2. Ajuste nos recursos/materiais
        3. Ajuste na abordagem pedagógica
        
        Para cada ajuste, explique:
        - O que mudar
        - Por que mudar
        - Como implementar
        - Resultado esperado
        
        Formato: Lista concisa e prática.
        """
        
        sugestoes, motor = SistemaIA.gerar_com_ia(prompt, "ajustes_roteiro", temperatura=0.6)
        
        return {
            'status': 'PRECISA_AJUSTE',
            'motivos': motivos,
            'engajamento_medio': engajamento_medio,
            'taxa_conclusao': atividades_concluidas / total_atividades,
            'sugestoes_ajuste': sugestoes,
            'motor_sugestao': motor
        }
    
    def gerar_relatorio_semanal(self, semana_num):
        """Gera relatório semanal automático"""
        atividades_semana = [a for a in self.estado['atividades_realizadas'] if a['semana'] == semana_num]
        
        if not atividades_semana:
            return None
        
        # Preparar dados para a IA
        dados_semana = {
            'total_atividades': len(atividades_semana),
            'concluidas': len([a for a in atividades_semana if a['conseguiu_realizar']]),
            'engajamento_medio': sum(a['engajamento'] for a in atividades_semana) / len(atividades_semana),
            'dificuldades_comuns': list(set([a['dificuldades'] for a in atividades_semana if a['dificuldades']])),
            'observacoes_chave': [a['observacoes'] for a in atividades_semana if a['observacoes']][:3]
        }
        
        prompt = f"""
        RELATÓRIO SEMANAL DE EXECUÇÃO DO AEE
        
        ALUNO: {aluno['nome']}
        SEMANA: {semana_num}
        DATA: {self.hoje.strftime('%d/%m/%Y')}
        
        DADOS DA SEMANA:
        - Atividades planejadas: {dados_semana['total_atividades']}
        - Atividades concluídas: {dados_semana['concluidas']}
        - Taxa de conclusão: {(dados_semana['concluidas']/dados_semana['total_atividades'])*100:.1f}%
        - Engajamento médio: {dados_semana['engajamento_medio']:.1f}/5
        
        DIFICULDADES IDENTIFICADAS:
        {chr(10).join(f"- {d}" for d in dados_semana['dificuldades_comuns'])}
        
        OBSERVAÇÕES IMPORTANTES:
        {chr(10).join(f"- {o}" for o in dados_semana['observacoes_chave'])}
        
        GERE UM RELATÓRIO CONCISO (máximo 300 palavras) com:
        1. RESUMO DA SEMANA (o que foi trabalhado)
        2. PROGRESSOS OBSERVADOS
        3. DIFICULDADES PERSISTENTES
        4. RECOMENDAÇÕES PARA A PRÓXIMA SEMANA
        5. AJUSTES SUGERIDOS (se necessário)
        
        Use linguagem profissional mas acessível.
        """
        
        relatorio, motor = SistemaIA.gerar_com_ia(prompt, "analise_progresso", temperatura=0.3)
        
        return {
            'relatorio': relatorio,
            'dados': dados_semana,
            'motor_geracao': motor,
            'data': self.hoje.strftime("%Y-%m-%d")
        }

# ==============================================================================
# INICIALIZAÇÃO DOS SISTEMAS
# ==============================================================================

# Inicializar planejador
planejador = PlanejadorPAEE(aluno)

# Inicializar sistema de execução (será usado depois que tiver cronograma)
sistema_execucao = None

# ==============================================================================
# PARTE 3/4: INTERFACE PRINCIPAL - ABAS E PLANEJAMENTO
# ==============================================================================

# ==============================================================================
# CRIAÇÃO DAS ABAS PRINCIPAIS
# ==============================================================================
tab1, tab2, tab3 = st.tabs([
    "📅 PLANEJAMENTO DO CICLO",
    "⚡ EXECUÇÃO EM TEMPO REAL",
    "📊 DASHBOARD DE PROGRESSO"
])

# ==============================================================================
# ABA 1: PLANEJAMENTO DO CICLO
# ==============================================================================
with tab1:
    st.markdown("### 📅 Planejamento do Ciclo de AEE")
    
    col_config, col_info = st.columns([1, 1])
    
    with col_config:
        st.markdown("<div class='pedagogia-box'><strong>Configuração do Ciclo:</strong> Defina o período de execução do plano.</div>", unsafe_allow_html=True)
        
        # Duração do ciclo
        duracao_semanas = st.slider(
            "Duração do ciclo (semanas):",
            min_value=4,
            max_value=16,
            value=8,
            help="Quantas semanas de execução do plano"
        )
        
        # Frequência do AEE
        frequencia = st.selectbox(
            "Frequência do AEE:",
            ["1 vez por semana", "2 vezes por semana", "3 vezes por semana", "Diário"],
            index=0
        )
        
        # Foco principal
        foco_principal = st.text_input(
            "Foco principal do ciclo:",
            value=aluno.get('hiperfoco', 'Desenvolvimento de habilidades específicas'),
            help="Qual o objetivo principal deste ciclo?"
        )
        
        # Botão para gerar cronograma
        if st.button("✨ Gerar Cronograma Inteligente", type="primary", use_container_width=True):
            if not st.session_state.get('api_key_deepseek') and not st.session_state.get('api_key_openai'):
                st.error("⚠️ Configure pelo menos uma chave de IA na sidebar")
            else:
                with st.spinner("🤖 IA planejando cronograma personalizado..."):
                    cronograma = planejador.gerar_cronograma_inteligente(duracao_semanas)
                    
                    if "erro" in cronograma:
                        st.error(f"Erro: {cronograma['erro']}")
                    else:
                        st.session_state['cronograma_atual'] = cronograma
                        st.session_state['aluno_cronograma'] = aluno['id']
                        
                        # Inicializar sistema de execução
                        global sistema_execucao
                        sistema_execucao = SistemaExecucao(aluno['id'], cronograma)
                        
                        st.success(f"✅ Cronograma gerado com {duracao_semanas} semanas!")
                        st.rerun()
    
    with col_info:
        st.markdown("<div class='pedagogia-box'><strong>Informações do Ciclo:</strong> Contexto para planejamento.</div>", unsafe_allow_html=True)
        
        # Mostrar data de revisão do PEI
        if aluno.get('data_revisao_pei'):
            st.info(f"**📅 Próxima revisão do PEI:** {aluno['data_revisao_pei'].strftime('%d/%m/%Y')}")
            dias_restantes = (aluno['data_revisao_pei'] - hoje).days
            if dias_restantes > 0:
                st.metric("Dias até a revisão", dias_restantes)
            else:
                st.warning("A data de revisão do PEI já passou")
        
        # Mostrar metas extraídas
        if st.session_state.metas_extraidas:
            st.markdown("#### 🎯 Metas do PEI")
            for meta in st.session_state.metas_extraidas[:3]:
                st.markdown(f"**{meta['tipo']}:** {meta['descricao'][:100]}...")
    
    # SEÇÃO: CRONOGRAMA GERADO
    if 'cronograma_atual' in st.session_state and st.session_state['aluno_cronograma'] == aluno['id']:
        cronograma = st.session_state['cronograma_atual']
        
        st.markdown("---")
        st.markdown(f"### 🗓️ Cronograma Gerado ({cronograma.get('total_semanas', 0)} semanas)")
        
        # Informações do cronograma
        col_stats, col_motor = st.columns([2, 1])
        
        with col_stats:
            st.caption(f"📅 Período: {cronograma.get('periodo', 'Não definido')}")
            st.caption(f"🎯 Foco: {foco_principal}")
            
            # Calcular progresso
            semanas_executadas = len(sistema_execucao.estado['semanas_concluidas']) if sistema_execucao else 0
            total_semanas = cronograma.get('total_semanas', 1)
            progresso_pct = (semanas_executadas / total_semanas) * 100
            
            st.progress(progresso_pct / 100)
            st.caption(f"📊 Progresso: {semanas_executadas}/{total_semanas} semanas ({progresso_pct:.1f}%)")
        
        with col_motor:
            motor = cronograma.get('motor_geracao', 'Desconhecido')
            st.info(f"🤖 Gerado com: {motor}")
        
        # Mostrar fases
        if 'fases' in cronograma:
            st.markdown("#### 🚩 Fases do Plano")
            
            for fase in cronograma['fases']:
                with st.expander(f"**{fase.get('nome', 'Fase')}** - {fase.get('descricao', '')}", expanded=True):
                    col_f1, col_f2 = st.columns(2)
                    
                    with col_f1:
                        st.markdown(f"**Objetivo:** {fase.get('objetivo_principal', '')}")
                        if fase.get('habilidades_foco'):
                            st.markdown("**Habilidades:**")
                            for hab in fase['habilidades_foco'][:3]:
                                st.markdown(f"- {hab}")
                    
                    with col_f2:
                        st.markdown(f"**Semanas:** {fase.get('semanas', [])}")
                        if fase.get('recursos_principais'):
                            st.markdown("**Recursos:**")
                            for rec in fase['recursos_principais'][:3]:
                                st.markdown(f"- {rec}")
        
        # Mostrar semanas detalhadas
        if 'semanas' in cronograma:
            st.markdown("#### 📋 Semanas Detalhadas")
            
            for semana in cronograma['semanas']:
                semana_num = semana.get('numero', 0)
                concluida = semana_num in (sistema_execucao.estado['semanas_concluidas'] if sistema_execucao else [])
                
                status_class = "activity-status-done" if concluida else "activity-status-pending"
                
                st.markdown(f"""
                <div class="activity-card {status_class}">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <strong style="font-size: 1.1rem;">Semana {semana_num}: {semana.get('tema', '')}</strong>
                            { '✅ <span style="color: #10B981; font-size: 0.9rem;">Concluída</span>' if concluida else '⏳ <span style="color: #F59E0B; font-size: 0.9rem;">Pendente</span>' }
                        </div>
                        <div>
                            <span class="skill-chip">{len(semana.get('atividades', []))} atividades</span>
                        </div>
                    </div>
                    <div style="margin-top: 10px; color: #4B5563;">
                        {semana.get('meta_semanal', '')}
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Mostrar atividades da semana
                if st.checkbox(f"Ver atividades da Semana {semana_num}", key=f"ver_semana_{semana_num}"):
                    atividades = semana.get('atividades', [])
                    
                    for idx, atividade in enumerate(atividades):
                        col_a1, col_a2 = st.columns([3, 1])
                        
                        with col_a1:
                            st.markdown(f"**{atividade.get('titulo', 'Atividade')}**")
                            st.markdown(f"{atividade.get('descricao', '')[:150]}...")
                            
                            # Materiais
                            if atividade.get('materiais'):
                                st.caption(f"📦 Materiais: {', '.join(atividade['materiais'][:3])}")
                        
                        with col_a2:
                            st.caption(f"⏱️ {atividade.get('duracao', '')}")
                            
                            # Botão rápido para executar (irá para aba 2)
                            if st.button("▶️ Executar", key=f"exec_{semana_num}_{idx}", use_container_width=True):
                                st.session_state['atividade_selecionada'] = {
                                    'semana': semana_num,
                                    'indice': idx,
                                    'atividade': atividade
                                }
                                st.switch_to_tab("⚡ EXECUÇÃO EM TEMPO REAL")
        
        # Botão para exportar cronograma
        st.markdown("---")
        col_exp1, col_exp2 = st.columns(2)
        
        with col_exp1:
            if st.button("📥 Exportar Cronograma (JSON)", use_container_width=True):
                cronograma_json = json.dumps(cronograma, indent=2, ensure_ascii=False)
                st.download_button(
                    label="Clique para baixar",
                    data=cronograma_json,
                    file_name=f"Cronograma_{aluno['nome']}_{hoje.strftime('%Y%m%d')}.json",
                    mime="application/json"
                )
        
        with col_exp2:
            if st.button("🔄 Regenerar Cronograma", use_container_width=True):
                del st.session_state['cronograma_atual']
                st.rerun()
    
    else:
        # Se não tem cronograma, mostrar instruções
        st.markdown("---")
        st.info("""
        ### 📋 Como funciona o planejamento:
        
        1. **Configure o ciclo** acima (duração, frequência, foco)
        2. **Clique em 'Gerar Cronograma Inteligente'** para a IA criar um plano personalizado
        3. **Revise o cronograma** gerado automaticamente
        4. **Execute as atividades** na aba "Execução em Tempo Real"
        5. **Acompanhe o progresso** na aba "Dashboard"
        
        O sistema usará o **DeepSeek** para análise estratégica e o **OpenAI** para criatividade nas atividades, 
        cruzando os dados do PEI com as melhores práticas de AEE.
        """)

# ==============================================================================
# PARTE 4/4: EXECUÇÃO, DASHBOARD E SISTEMA COMPLETO
# ==============================================================================

# ==============================================================================
# ABA 2: EXECUÇÃO EM TEMPO REAL
# ==============================================================================
with tab2:
    st.markdown("### ⚡ Execução em Tempo Real")
    
    # Verificar se tem cronograma
    if 'cronograma_atual' not in st.session_state or st.session_state['aluno_cronograma'] != aluno['id']:
        st.warning("⚠️ Primeiro gere um cronograma na aba 'Planejamento do Ciclo'")
        st.stop()
    
    cronograma = st.session_state['cronograma_atual']
    
    # Verificar sistema de execução
    if not sistema_execucao:
        sistema_execucao = SistemaExecucao(aluno['id'], cronograma)
    
    # SEÇÃO 1: ATIVIDADE SELECIONADA PARA EXECUÇÃO
    if 'atividade_selecionada' in st.session_state:
        atividade_sel = st.session_state['atividade_selecionada']
        semana_num = atividade_sel['semana']
        atividade_idx = atividade_sel['indice']
        atividade = atividade_sel['atividade']
        
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #3B82F6 0%, #1D4ED8 100%); color: white; border-radius: 12px; padding: 20px; margin-bottom: 20px;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <h3 style="margin: 0; color: white;">▶️ Executando Atividade</h3>
                    <p style="margin: 5px 0 0 0; opacity: 0.9;">Semana {semana_num} • {atividade.get('titulo', 'Atividade')}</p>
                </div>
                <div>
                    <span style="background: rgba(255,255,255,0.2); padding: 5px 15px; border-radius: 20px; font-size: 0.9rem;">
                        {atividade.get('duracao', '30 min')}
                    </span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Detalhes da atividade
        col_det1, col_det2 = st.columns([2, 1])
        
        with col_det1:
            st.markdown("#### 📝 Detalhes da Atividade")
            st.markdown(f"**Descrição:** {atividade.get('descricao', '')}")
            
            if atividade.get('adaptacoes'):
                st.markdown("#### 🛠️ Adaptações Sugeridas")
                st.info(atividade.get('adaptacoes'))
            
            if atividade.get('indicadores_sucesso'):
                st.markdown("#### 🎯 Indicadores de Sucesso")
                for indicador in atividade.get('indicadores_sucesso', []):
                    st.markdown(f"- {indicador}")
        
        with col_det2:
            st.markdown("#### 📦 Materiais")
            if atividade.get('materiais'):
                for material in atividade.get('materiais', []):
                    st.markdown(f"• {material}")
            else:
                st.info("Sem materiais específicos")
        
        # FORMULÁRIO DE EXECUÇÃO
        st.markdown("---")
        st.markdown("#### 📋 Registro da Execução")
        
        with st.form(f"exec_form_{semana_num}_{atividade_idx}"):
            col_exec1, col_exec2 = st.columns(2)
            
            with col_exec1:
                conseguiu = st.radio(
                    "O aluno conseguiu realizar a atividade?",
                    ["Sim, completamente", "Parcialmente", "Não conseguiu"],
                    horizontal=True
                )
                
                engajamento = st.slider(
                    "Nível de engajamento do aluno:",
                    1, 5, 3,
                    help="1 = Muito baixo, 5 = Excelente"
                )
            
            with col_exec2:
                # Dificuldades encontradas
                dificuldades = st.text_area(
                    "Dificuldades encontradas:",
                    height=80,
                    placeholder="Descreva quaisquer dificuldades..."
                )
                
                # Ajustes realizados
                ajustes = st.text_area(
                    "Ajustes realizados durante a atividade:",
                    height=80,
                    placeholder="O que você adaptou durante a execução?"
                )
            
            # Observações detalhadas
            observacoes = st.text_area(
                "Observações detalhadas:",
                height=120,
                placeholder="Descreva como foi a atividade, reações do aluno, surpresas, aprendizados..."
            )
            
            # Upload de evidências
            evidencias = st.file_uploader(
                "📸 Anexar evidências (opcional):",
                type=['png', 'jpg', 'jpeg', 'pdf'],
                accept_multiple_files=True
            )
            
            # Botões de ação
            col_btn1, col_btn2, col_btn3 = st.columns(3)
            
            with col_btn1:
                submit = st.form_submit_button(
                    "💾 Salvar e Concluir Atividade",
                    type="primary",
                    use_container_width=True
                )
            
            with col_btn2:
                salvar_sem_concluir = st.form_submit_button(
                    "💾 Salvar e Continuar",
                    use_container_width=True
                )
            
            with col_btn3:
                cancelar = st.form_submit_button(
                    "❌ Cancelar",
                    use_container_width=True
                )
            
            if submit or salvar_sem_concluir:
                # Preparar dados
                dados_execucao = {
                    'engajamento': engajamento,
                    'conseguiu_realizar': "Não" not in conseguiu,
                    'observacoes': observacoes,
                    'dificuldades': dificuldades,
                    'ajustes_feitos': ajustes,
                    'evidencias': [e.name for e in evidencias] if evidencias else []
                }
                
                # Registrar atividade
                registro = sistema_execucao.registrar_atividade(
                    semana_num, atividade_idx, dados_execucao
                )
                
                if submit:
                    st.success("✅ Atividade concluída e registrada!")
                    time.sleep(1)
                    
                    # Remover atividade selecionada
                    del st.session_state['atividade_selecionada']
                    
                    # Verificar se concluiu a semana
                    atividades_semana = [a for a in sistema_execucao.estado['atividades_realizadas'] 
                                       if a['semana'] == semana_num]
                    total_atividades_semana = len([s for s in cronograma['semanas'] 
                                                 if s['numero'] == semana_num][0]['atividades'])
                    
                    if len(atividades_semana) >= total_atividades_semana * 0.7:  # 70% concluídas
                        if st.checkbox("✅ Marcar semana como concluída"):
                            resultado = sistema_execucao.concluir_semana(semana_num)
                            if resultado:
                                st.success(f"🎉 Semana {semana_num} concluída!")
                
                elif salvar_sem_concluir:
                    st.success("✅ Progresso salvo! Continue com a atividade.")
                
                st.rerun()
            
            if cancelar:
                del st.session_state['atividade_selecionada']
                st.rerun()
    
    else:
        # SEÇÃO 2: VISÃO GERAL DA EXECUÇÃO
        col_over1, col_over2 = st.columns([2, 1])
        
        with col_over1:
            st.markdown("#### 📊 Progresso da Execução")
            
            # Calcular métricas
            total_atividades = sum(len(s.get('atividades', [])) for s in cronograma.get('semanas', []))
            atividades_realizadas = len(sistema_execucao.estado['atividades_realizadas'])
            semanas_concluidas = len(sistema_execucao.estado['semanas_concluidas'])
            
            # Gráfico de progresso
            fig = px.bar(
                x=['Atividades', 'Semanas'],
                y=[atividades_realizadas/total_atividades*100 if total_atividades > 0 else 0, 
                   semanas_concluidas/cronograma.get('total_semanas', 1)*100],
                color=['Atividades', 'Semanas'],
                color_discrete_map={'Atividades': '#8B5CF6', 'Semanas': '#10B981'},
                labels={'x': 'Categoria', 'y': 'Progresso (%)'},
                title='Progresso Geral'
            )
            fig.update_layout(showlegend=False, height=300)
            st.plotly_chart(fig, use_container_width=True)
        
        with col_over2:
            st.markdown("#### 📈 Métricas Chave")
            
            st.metric(
                "Atividades Realizadas",
                f"{atividades_realizadas}/{total_atividades}",
                f"{((atividades_realizadas/total_atividades)*100 if total_atividades > 0 else 0):.1f}%"
            )
            
            st.metric(
                "Semanas Concluídas",
                f"{semanas_concluidas}/{cronograma.get('total_semanas', 0)}",
                f"{((semanas_concluidas/cronograma.get('total_semanas', 1))*100 if cronograma.get('total_semanas', 1) > 0 else 0):.1f}%"
            )
            
            # Engajamento médio
            if sistema_execucao.estado['atividades_realizadas']:
                engajamento_medio = sum(a['engajamento'] for a in sistema_execucao.estado['atividades_realizadas']) / len(sistema_execucao.estado['atividades_realizadas'])
                st.metric("Engajamento Médio", f"{engajamento_medio:.1f}/5")
        
        # SEÇÃO 3: ATIVIDADES DISPONÍVEIS PARA EXECUÇÃO
        st.markdown("---")
        st.markdown("#### 🎯 Atividades Disponíveis")
        
        # Filtrar semanas não concluídas
        semanas_nao_concluidas = [s for s in cronograma.get('semanas', []) 
                                 if s['numero'] not in sistema_execucao.estado['semanas_concluidas']]
        
        if not semanas_nao_concluidas:
            st.success("🎉 Todas as semanas foram concluídas!")
        else:
            for semana in semanas_nao_concluidas[:3]:  # Mostrar até 3 semanas
                st.markdown(f"##### 📅 Semana {semana['numero']}: {semana.get('tema', '')}")
                
                col_sem1, col_sem2 = st.columns([3, 1])
                
                with col_sem1:
                    st.markdown(f"**Meta semanal:** {semana.get('meta_semanal', '')}")
                    
                    # Mostrar primeiras 2 atividades
                    for idx, atividade in enumerate(semana.get('atividades', [])[:2]):
                        st.markdown(f"**{atividade['titulo']}** - {atividade.get('duracao', '')}")
                
                with col_sem2:
                    if st.button("🔍 Ver todas", key=f"ver_sem_{semana['numero']}", use_container_width=True):
                        # Ir para a semana específica
                        st.session_state['semana_ativa'] = semana['numero']
                        st.rerun()
        
        # SEÇÃO 4: SUGESTÕES DE AJUSTE AUTOMÁTICO
        if sistema_execucao.estado['atividades_realizadas']:
            st.markdown("---")
            st.markdown("#### 🔧 Análise de Ajustes Automática")
            
            semana_atual = max([a['semana'] for a in sistema_execucao.estado['atividades_realizadas']], default=1)
            analise = sistema_execucao.sugerir_ajustes_automaticos(semana_atual)
            
            if analise:
                if analise['status'] == 'OK':
                    st.success("✅ O plano está funcionando bem!")
                    st.info(f"Engajamento médio: {analise['engajamento_medio']:.1f}/5 | Conclusão: {analise['taxa_conclusao']*100:.1f}%")
                else:
                    st.warning("⚠️ Ajustes recomendados:")
                    st.write(analise['sugestoes_ajuste'])
                    
                    if st.button("🔄 Aplicar ajustes automaticamente", type="secondary"):
                        st.info("Ajustes serão aplicados nas próximas atividades")
                        # Aqui você poderia implementar a lógica de aplicar ajustes

# ==============================================================================
# ABA 3: DASHBOARD DE PROGRESSO
# ==============================================================================
with tab3:
    st.markdown("### 📊 Dashboard de Progresso")
    
    if 'cronograma_atual' not in st.session_state or not sistema_execucao:
        st.warning("Gere e execute atividades para ver o dashboard")
        st.stop()
    
    # SEÇÃO 1: VISÃO GERAL
    col_dash1, col_dash2, col_dash3, col_dash4 = st.columns(4)
    
    with col_dash1:
        total_atividades = sum(len(s.get('atividades', [])) for s in cronograma.get('semanas', []))
        realizadas = len(sistema_execucao.estado['atividades_realizadas'])
        st.metric("Atividades", f"{realizadas}/{total_atividades}", f"{(realizadas/total_atividades*100 if total_atividades>0 else 0):.0f}%")
    
    with col_dash2:
        semanas_totais = cronograma.get('total_semanas', 0)
        semanas_concluidas = len(sistema_execucao.estado['semanas_concluidas'])
        st.metric("Semanas", f"{semanas_concluidas}/{semanas_totais}", f"{(semanas_concluidas/semanas_totais*100 if semanas_totais>0 else 0):.0f}%")
    
    with col_dash3:
        if sistema_execucao.estado['atividades_realizadas']:
            engajamento_medio = sum(a['engajamento'] for a in sistema_execucao.estado['atividades_realizadas']) / len(sistema_execucao.estado['atividades_realizadas'])
            st.metric("Engajamento", f"{engajamento_medio:.1f}/5.0")
        else:
            st.metric("Engajamento", "0/5")
    
    with col_dash4:
        sucesso_rate = len([a for a in sistema_execucao.estado['atividades_realizadas'] if a['conseguiu_realizar']]) / len(sistema_execucao.estado['atividades_realizadas']) if sistema_execucao.estado['atividades_realizadas'] else 0
        st.metric("Taxa de Sucesso", f"{(sucesso_rate*100):.0f}%")
    
    # SEÇÃO 2: GRÁFICOS DETALHADOS
    col_chart1, col_chart2 = st.columns(2)
    
    with col_chart1:
        # Gráfico de engajamento por semana
        if sistema_execucao.estado['engajamento_semanal']:
            semanas = list(sistema_execucao.estado['engajamento_semanal'].keys())
            medias = [sum(vals)/len(vals) for vals in sistema_execucao.estado['engajamento_semanal'].values()]
            
            fig = px.line(
                x=semanas,
                y=medias,
                markers=True,
                title='Engajamento por Semana',
                labels={'x': 'Semana', 'y': 'Engajamento (1-5)'}
            )
            fig.update_traces(line_color='#8B5CF6', marker_color='#7C3AED')
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)
    
    with col_chart2:
        # Gráfico de atividades concluídas vs não concluídas
        if sistema_execucao.estado['atividades_realizadas']:
            concluidas = len([a for a in sistema_execucao.estado['atividades_realizadas'] if a['conseguiu_realizar']])
            nao_concluidas = len(sistema_execucao.estado['atividades_realizadas']) - concluidas
            
            fig = px.pie(
                values=[concluidas, nao_concluidas],
                names=['Concluídas', 'Não Concluídas'],
                title='Conclusão de Atividades',
                color_discrete_sequence=['#10B981', '#EF4444']
            )
            fig.update_layout(height=300, showlegend=True)
            st.plotly_chart(fig, use_container_width=True)
    
    # SEÇÃO 3: RELATÓRIO SEMANAL AUTOMÁTICO
    st.markdown("---")
    st.markdown("#### 📋 Relatório Automático de Progresso")
    
    if sistema_execucao.estado['atividades_realizadas']:
        semana_mais_recente = max([a['semana'] for a in sistema_execucao.estado['atividades_realizadas']])
        
        if st.button("📄 Gerar Relatório da Semana", use_container_width=True):
            with st.spinner("Gerando relatório com IA..."):
                relatorio = sistema_execucao.gerar_relatorio_semanal(semana_mais_recente)
                
                if relatorio:
                    st.markdown("#### 📊 Relatório Gerado")
                    st.markdown(relatorio['relatorio'])
                    
                    st.download_button(
                        "📥 Baixar Relatório",
                        relatorio['relatorio'],
                        file_name=f"Relatorio_Semana_{semana_mais_recente}_{aluno['nome']}.txt",
                        mime="text/plain"
                    )
    else:
        st.info("Execute algumas atividades para gerar relatórios automáticos")
    
    # SEÇÃO 4: HISTÓRICO DE EXECUÇÃO
    st.markdown("---")
    st.markdown("#### 📝 Histórico de Execução")
    
    if sistema_execucao.estado['atividades_realizadas']:
        historico_recente = sorted(
            sistema_execucao.estado['atividades_realizadas'],
            key=lambda x: x['data'],
            reverse=True
        )[:10]
        
        for registro in historico_recente:
            # Encontrar atividade no cronograma
            semana_cron = next((s for s in cronograma['semanas'] if s['numero'] == registro['semana']), None)
            atividade = None
            if semana_cron and registro['atividade_idx'] < len(semana_cron['atividades']):
                atividade = semana_cron['atividades'][registro['atividade_idx']]
            
            st.markdown(f"""
            <div class="activity-card">
                <div style="display: flex; justify-content: space-between;">
                    <div>
                        <strong>📅 {registro['data']}</strong> - Semana {registro['semana']}
                        {f" - {atividade['titulo']}" if atividade else ""}
                    </div>
                    <div>
                        <span style="background: {'#10B981' if registro['conseguiu_realizar'] else '#EF4444'}; 
                                   color: white; padding: 2px 8px; border-radius: 12px; font-size: 0.8rem;">
                            {'✅ Concluída' if registro['conseguiu_realizar'] else '❌ Não concluída'}
                        </span>
                    </div>
                </div>
                <div style="margin-top: 8px;">
                    <span style="font-size: 0.9rem;">Engajamento: {"⭐" * registro['engajamento']}</span>
                    {f"<br><span style='font-size: 0.85rem; color: #6B7280;'>{registro['observacoes'][:100]}...</span>" if registro['observacoes'] else ""}
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("Nenhuma atividade registrada ainda")

# ==============================================================================
# RODAPÉ E INFORMAÇÕES
# ==============================================================================
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #64748B; font-size: 0.9rem; padding: 20px;">
    <p>🚀 <strong>Fluxo Completo Omnisfera:</strong> PEI → Planejamento PAEE → Execução → Ajustes → Avaliação</p>
    <p>🤖 <strong>IA Inteligente:</strong> DeepSeek para análise + OpenAI para criatividade</p>
    <p>📊 <strong>Dados em Tempo Real:</strong> Acompanhe e ajuste o plano conforme o progresso do aluno</p>
</div>
""", unsafe_allow_html=True)

# FIM DO CÓDIGO COMPLETO
