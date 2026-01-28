# ==============================================================================
# PARTE 1/4: CONFIGURAÇÕES, ESTILOS E AUTENTICAÇÃO
# ==============================================================================

import streamlit as st
import os
from openai import OpenAI
import json
import pandas as pd
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo
import base64
import requests
import time
import uuid

import omni_utils as ou  # módulo atualizado
from omni_utils import get_icon, icon_title

# 1. CONFIGURAÇÃO INICIAL (topo absoluto)
st.set_page_config(
    page_title="Omnisfera | PAE",
    page_icon="omni_icone.png",
    layout="wide",
    initial_sidebar_state="collapsed",
)

APP_VERSION = "v150.0 (SaaS Design)"

# 2. UI LOCKDOWN (opcional)
try:
    from ui_lockdown import hide_streamlit_chrome_if_needed, hide_default_sidebar_nav
    hide_streamlit_chrome_if_needed()
    hide_default_sidebar_nav()
except Exception:
    pass

# 3. HEADER E NAVBAR (do omni_utils)
ou.render_omnisfera_header()
ou.render_navbar(active_tab="Plano de Ação (AEE)")
ou.inject_compact_app_css()

# Adiciona classe no body para cores específicas das abas
st.markdown("<script>document.body.classList.add('page-purple');</script>", unsafe_allow_html=True)

# 4. VERIFICAÇÃO DE ACESSO
def verificar_acesso():
    if not st.session_state.get("autenticado"):
        st.error(f"{get_icon('erro', 18, '#DC2626')} Acesso Negado.")
        st.stop()

verificar_acesso()

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

            /* 2. Puxa todo o conteúdo para cima (O SEGREDO ESTÁ AQUI) - ESPECIFICIDADE MÁXIMA */
            body .main .block-container,
            body .block-container,
            .main .block-container,
            .block-container {
                padding-top: 0px !important; /* SEM espaço entre navbar e hero */
                padding-bottom: 1rem !important;
                margin-top: 0px !important;
            }
            
            /* 3. Remove qualquer espaçamento do Streamlit */
            [data-testid="stVerticalBlock"],
            div[data-testid="stVerticalBlock"] > div:first-child,
            .main .block-container > div:first-child,
            .main .block-container > *:first-child {
                padding-top: 0px !important;
                margin-top: 0px !important;
            }
            
            /* 4. Remove espaçamento do stMarkdown que renderiza o hero */
            .main .block-container > div:first-child .stMarkdown {
                margin-top: 0px !important;
                padding-top: 0px !important;
            }
            
            /* 5. Hero card colado no menu - margin negativo (ajustado para reduzir espaço) */
            body .mod-card-wrapper,
            .main .mod-card-wrapper,
            .block-container .mod-card-wrapper,
            .mod-card-wrapper {
                margin-top: -120px !important; /* Puxa o hero para cima, reduzindo espaço do navbar */
                position: relative;
                z-index: 1;
            }
            
            /* 6. Esconde o menu hambúrguer e rodapé */
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

# Garantir que RemixIcon está carregado para os ícones aparecerem
st.markdown("""
<link href="https://cdn.jsdelivr.net/npm/remixicon@4.1.0/fonts/remixicon.css" rel="stylesheet">
""", unsafe_allow_html=True)

# CSS adicional para garantir espaçamento reduzido do hero card (aplicado por último)
st.markdown("""
<style>
    /* Força o margin-top negativo após todos os outros CSS */
    body .main .block-container .mod-card-wrapper,
    body .block-container .mod-card-wrapper,
    .main .block-container .mod-card-wrapper,
    .block-container .mod-card-wrapper,
    .mod-card-wrapper:first-of-type {
        margin-top: -120px !important;
    }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# BLOCO VISUAL (GLOBAL) — CSS DO MÓDULO + GATE (REAPROVEITÁVEL)
# Mantém: card hero, tabs, caixas, timeline e tema de botões
# Remove: badge fixo + logo girando (porque conflita com ou.render_omnisfera_header)
# ==============================================================================

def inject_paee_css(theme: str = "teal"):
    """
    Injeta CSS do módulo (reaproveitável em outras páginas).
    - theme: "teal" (padrão) ou "purple" (se quiser alternar em outro módulo)
    """
    if theme == "purple":
        ACCENT = "#8B5CF6"
        ACCENT_DARK = "#7C3AED"
        ACCENT_SOFT = "#F5F3FF"
    else:
        ACCENT = "#0D9488"
        ACCENT_DARK = "#0F766E"
        ACCENT_SOFT = "#F0FDFA"

    st.markdown(
    f"""
<style>

 /* ===============================
    AJUSTE ENTRE MENU SUPERIOR E HERO (PADRONIZADO)
 ================================ */
/* margin-top já aplicado no forcar_layout_hub() - não sobrescrever aqui */
body .mod-card-wrapper,
.main .mod-card-wrapper,
.block-container .mod-card-wrapper,
.mod-card-wrapper {{
    margin-bottom: 20px !important;
    margin-top: -120px !important; /* Mantém o espaçamento reduzido do navbar */
}}


 /* ============================
     COMPONENTES BASE (REUSO)
     ============================ */

  /* CARD HERO (header do módulo) */
  body .mod-card-wrapper,
  .main .mod-card-wrapper,
  .block-container .mod-card-wrapper,
  .mod-card-wrapper {{
      display:flex; flex-direction:column;
      margin-bottom:20px;
      margin-top: -120px !important; /* Garante que não seja sobrescrito */
      border-radius:16px;
      overflow:hidden;
      box-shadow:0 4px 6px rgba(0,0,0,0.02);
  }}
  .mod-card-rect {{
      background:white;
      border-radius:16px 16px 0 0;
      padding:0;
      border:1px solid #E2E8F0;
      border-bottom:none;
      display:flex;
      flex-direction:row;
      align-items:center;
      height:130px !important;  /* 🔒 ALTURA FIXA PADRONIZADA */
      width:100%;
      position:relative;
      overflow:hidden;
      transition:all .25s cubic-bezier(.4,0,.2,1);
  }}
  .mod-card-rect:hover {{
      transform:translateY(-4px);
      box-shadow:0 12px 24px rgba(0,0,0,0.08);
      border-color:#CBD5E1;
  }}
  .mod-bar {{
      width:6px; height:100%; flex-shrink:0;
      background:{ACCENT} !important;
  }}
  .mod-icon-area {{
      width:90px; height:100%;
      display:flex; align-items:center; justify-content:center;
      font-size:1.8rem;
      flex-shrink:0;
      background:#FAFAFA !important;
      border-right:1px solid #F1F5F9;
      transition:all .3s ease;
      color:{ACCENT} !important;
  }}
  .mod-icon-area i {{
      color:{ACCENT} !important;
      font-size:2rem !important;
      display:inline-block !important;
      line-height:1 !important;
      visibility:visible !important;
      opacity:1 !important;
      font-style:normal !important;
      font-weight:normal !important;
  }}
  /* Classe bg-purple-soft para hero card */
  .bg-purple-soft {{
      background:#F3E8FF !important;
  }}
  .bg-purple-soft i {{
      color:#9333EA !important;
      visibility:visible !important;
      opacity:1 !important;
      display:inline-block !important;
      font-size:2rem !important;
  }}
  .mod-card-rect:hover .mod-icon-area {{
      background:white !important;
      transform:scale(1.05) !important;
  }}
  .mod-card-rect:hover .mod-icon-area i {{
      color:{ACCENT} !important;
  }}
  .mod-content {{
      flex-grow:1;
      padding:0 24px;
      display:flex; 
      flex-direction:column; 
      justify-content:center;
      align-items:flex-start;
      min-width:0; /* Previne overflow */
  }}
  .mod-title {{
      font-weight:800;
      font-size:1.1rem;
      color:#1E293B;
      margin-bottom:6px;
      letter-spacing:-0.3px;
      transition:color .2s;
  }}
  .mod-card-rect:hover .mod-title {{ color:{ACCENT}; }}
  .mod-desc {{
      font-size:.8rem;
      color:#64748B;
      line-height:1.4;
      display:-webkit-box;
      -webkit-line-clamp:2;
      -webkit-box-orient:vertical;
      overflow:hidden;
  }}

  /* BOX pedagógico e caixas */
  .pedagogia-box {{
      background-color:#F8FAFC;
      border-left:4px solid #CBD5E1;
      padding:20px;
      border-radius:0 12px 12px 0;
      margin-bottom:25px;
      font-size:.95rem;
      color:#4A5568;
  }}

  .resource-box {{
      background:#F8FAFC;
      border:1px solid #E2E8F0;
      border-radius:12px;
      padding:20px;
      margin:15px 0;
  }}

  .timeline-header {{
      background:white;
      border-radius:12px;
      padding:20px;
      margin-bottom:20px;
      border:1px solid #E2E8F0;
      display:flex;
      align-items:center;
      justify-content:space-between;
  }}

  /* ============================
     TABS E BOTÕES — PADRÃO VIA omni_utils.inject_unified_ui_css()
     ============================ */
  /* Estilos de tabs, botões, selects, etc. são aplicados via função padronizada */

  /* Responsividade do HERO */
  @media (max-width: 768px) {{
      .mod-card-rect {{ height:auto; flex-direction:column; padding:16px; }}
      .mod-icon-area {{ width:100%; height:60px; border-right:none; border-bottom:1px solid #F1F5F9; }}
      .mod-content {{ padding:16px 0 0 0; }}
  }}
</style>
        """,
        unsafe_allow_html=True,
    )


def verificar_acesso():
    # ✅ mantém o gate (importante)
    if not st.session_state.get("autenticado"):
        st.error("🔒 Acesso Negado. Por favor, faça login na Página Inicial.")
        st.stop()

    # ✅ se quiser esconder footer, ok (não mexe em padding)
    st.markdown(
        """
<style>
  footer {visibility:hidden !important;}
</style>
        """,
        unsafe_allow_html=True,
    )


# ==============================================================================
# HERO - PAE
# ==============================================================================
hora = datetime.now(ZoneInfo("America/Sao_Paulo")).hour
saudacao = "Bom dia" if 5 <= hora < 12 else "Boa tarde" if 12 <= hora < 18 else "Boa noite"
USUARIO_NOME = st.session_state.get("usuario_nome", "Visitante").split()[0]
WORKSPACE_NAME = st.session_state.get("workspace_name", "Workspace")

st.markdown(
    f"""
    <div class="mod-card-wrapper">
        <div class="mod-card-rect">
            <div class="mod-bar c-purple"></div>
            <div class="mod-icon-area bg-purple-soft" style="display: flex; align-items: center; justify-content: center;">
                <i class="ri-puzzle-fill" style="font-size: 2rem; color: #9333EA; display: inline-block; visibility: visible; opacity: 1; font-style: normal;"></i>
            </div>
            <div class="mod-content">
                <div class="mod-title">Atendimento Educacional Especializado (AEE) & Tecnologia Assistiva</div>
                <div class="mod-desc">
                    {saudacao}, <strong>{USUARIO_NOME}</strong>! Planeje e implemente estratégias de AEE para eliminação de barreiras 
                    no workspace <strong>{WORKSPACE_NAME}</strong>. Desenvolva recursos, adaptações e tecnologias assistivas 
                    para promover acessibilidade e participação plena.
                </div>
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# CSS específico do módulo PAE (após hero card)
inject_paee_css(theme="purple")

# Espaçamento após hero card
st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

# ==============================================================================
# PARTE 2/4: CONEXÃO COM BANCO DE DADOS E CARREGAMENTO DE ESTUDANTES
# ==============================================================================

# Funções _sb_url(), _sb_key(), _headers() removidas - usar ou._sb_url(), ou._sb_key(), ou._headers() do omni_utils
# Primeira definição duplicada de list_students_rest() e carregar_estudantes_supabase() removida - usar as definições mais abaixo

# ==============================================================================
# PEI DO ALUNO
# ==============================================================================
def carregar_pei_aluno(aluno_id):
    """Carrega o PEI do estudante do Supabase (campo pei_data na tabela students)."""
    try:
        url = f"{ou._sb_url()}/rest/v1/students"
        params = {"select": "id,pei_data", "id": f"eq.{aluno_id}"}
        r = requests.get(url, headers=ou._headers(), params=params, timeout=15)
        if r.status_code == 200 and r.json():
            return r.json()[0].get("pei_data", {}) or {}
        return {}
    except Exception as e:
        st.error(f"Erro ao carregar PEI: {str(e)}")
        return {}


# ==============================================================================
# PAEE — SALVAR / CARREGAR CICLOS
# ==============================================================================
def salvar_paee_ciclo(aluno_id, ciclo_data):
    """
    Salva um ciclo de PAEE no campo students.paee_ciclos (lista de ciclos).
    Mantém planejamento_ativo e status_planejamento.
    """
    try:
        # 1) Buscar estudante atual
        url = f"{ou._sb_url()}/rest/v1/students"
        params_get = {"select": "id,paee_ciclos,planejamento_ativo", "id": f"eq.{aluno_id}"}
        r = requests.get(url, headers=ou._headers(), params=params_get, timeout=15)

        if not (r.status_code == 200 and r.json()):
            return {"sucesso": False, "erro": "Estudante não encontrado"}

        aluno_row = r.json()[0]
        ciclos_existentes = aluno_row.get("paee_ciclos") or []
        ciclo_id = ciclo_data.get("ciclo_id")

        # 2) Criar ou atualizar
        if not ciclo_id:
            ciclo_id = str(uuid.uuid4())
            ciclo_data["ciclo_id"] = ciclo_id
            ciclo_data["criado_em"] = datetime.now().isoformat()
            ciclo_data["criado_por"] = st.session_state.get("user_id", "")
            ciclo_data["versao"] = 1
            ciclos_existentes.append(ciclo_data)
        else:
            # Atualiza ciclo existente
            updated = False
            for i, c in enumerate(ciclos_existentes):
                if c.get("ciclo_id") == ciclo_id:
                    ciclo_data["versao"] = (c.get("versao", 1) or 1) + 1
                    ciclo_data["atualizado_em"] = datetime.now().isoformat()
                    ciclos_existentes[i] = ciclo_data
                    updated = True
                    break
            if not updated:
                # se veio com id mas não achou, adiciona como novo
                ciclo_data["versao"] = 1
                ciclo_data["criado_em"] = datetime.now().isoformat()
                ciclos_existentes.append(ciclo_data)

        # 3) Preparar update
        cfg = (ciclo_data.get("config_ciclo") or {})
        update_data = {
            "paee_ciclos": ciclos_existentes,
            "planejamento_ativo": ciclo_id,
            "status_planejamento": ciclo_data.get("status", "rascunho"),
        }
        if cfg.get("data_inicio"):
            update_data["data_inicio_ciclo"] = cfg["data_inicio"]
        if cfg.get("data_fim"):
            update_data["data_fim_ciclo"] = cfg["data_fim"]

        # 4) PATCH
        params_patch = {"id": f"eq.{aluno_id}"}
        rp = requests.patch(url, headers=ou._headers(), params=params_patch, json=update_data, timeout=25)

        if rp.status_code == 204:
            return {"sucesso": True, "ciclo_id": ciclo_id}
        return {"sucesso": False, "erro": f"HTTP {rp.status_code}: {rp.text}"}

    except Exception as e:
        return {"sucesso": False, "erro": str(e)}


def carregar_ciclo_ativo(aluno_id):
    """Carrega o ciclo ativo (students.planejamento_ativo) dentro de students.paee_ciclos."""
    try:
        url = f"{ou._sb_url()}/rest/v1/students"
        params = {"select": "id,paee_ciclos,planejamento_ativo", "id": f"eq.{aluno_id}"}
        r = requests.get(url, headers=ou._headers(), params=params, timeout=15)

        if r.status_code == 200 and r.json():
            aluno_row = r.json()[0]
            ciclo_id = aluno_row.get("planejamento_ativo")
            ciclos = aluno_row.get("paee_ciclos") or []
            if ciclo_id and ciclos:
                for c in ciclos:
                    if c.get("ciclo_id") == ciclo_id:
                        return c
        return None
    except Exception as e:
        st.error(f"Erro ao carregar ciclo ativo: {str(e)}")
        return None


# ==============================================================================
# NOVO — HISTÓRICO DE CICLOS + DEFINIR ATIVO + HELPERS
# ==============================================================================
def listar_ciclos_aluno(aluno_id):
    """Lista todos os ciclos PAEE do estudante (students.paee_ciclos) e retorna (ciclos_ordenados, ciclo_ativo_id)."""
    try:
        url = f"{ou._sb_url()}/rest/v1/students"
        params = {"select": "id,paee_ciclos,planejamento_ativo", "id": f"eq.{aluno_id}"}
        r = requests.get(url, headers=ou._headers(), params=params, timeout=15)

        if r.status_code == 200 and r.json():
            aluno_row = r.json()[0]
            ciclos = aluno_row.get("paee_ciclos") or []
            ativo = aluno_row.get("planejamento_ativo")

            def _key(c):
                # ordena por atualizado_em > criado_em
                return (c.get("atualizado_em") or c.get("criado_em") or "")

            ciclos = sorted(ciclos, key=_key, reverse=True)
            return ciclos, ativo

        return [], None
    except Exception as e:
        st.error(f"Erro ao listar ciclos: {e}")
        return [], None


def definir_ciclo_ativo(aluno_id, ciclo_id, status="ativo"):
    """Define o ciclo ativo (students.planejamento_ativo) e status_planejamento."""
    try:
        url = f"{ou._sb_url()}/rest/v1/students"
        params = {"id": f"eq.{aluno_id}"}
        payload = {"planejamento_ativo": ciclo_id, "status_planejamento": status}
        r = requests.patch(url, headers=ou._headers(), params=params, json=payload, timeout=20)
        return r.status_code == 204
    except Exception as e:
        st.error(f"Erro ao definir ciclo ativo: {e}")
        return False


def _fmt_data_iso(d):
    try:
        return datetime.fromisoformat(str(d).replace("Z", "+00:00")).strftime("%d/%m/%Y")
    except:
        return str(d) if d else "-"


def _badge_status(status):
    s = (status or "rascunho").lower()
    mp = {
        "rascunho": ("🟡", "#F59E0B"),
        "ativo": ("🟢", "#10B981"),
        "concluido": ("🔵", "#3B82F6"),
        "arquivado": ("⚫", "#64748B"),
    }
    return mp.get(s, ("⚪", "#94A3B8"))

# ==============================================================================
# CARREGAR ESTUDANTES DO SUPABASE
# ==============================================================================
@st.cache_data(ttl=10, show_spinner=False)
def list_students_rest(workspace_id: str = ""):
    """Busca estudantes do Supabase incluindo o campo PEI_DATA. workspace_id no argumento para cache correto por escola."""
    if not (workspace_id and str(workspace_id).strip()):
        return []
    try:
        base = (
            f"{ou._sb_url()}/rest/v1/students"
            f"?select=id,name,grade,class_group,diagnosis,created_at,pei_data"
            f"&workspace_id=eq.{workspace_id}"
            f"&order=created_at.desc"
        )
        r = requests.get(base, headers=ou._headers(), timeout=20)
        return r.json() if r.status_code == 200 else []
    except Exception as e:
        st.error(f"Erro ao carregar estudantes: {str(e)}")
        return []

def carregar_estudantes_supabase():
    """Carrega e processa, extraindo dados ricos do PEI"""
    _workspace_id = st.session_state.get("workspace_id") or ""
    dados = list_students_rest(_workspace_id)
    estudantes = []
    
    for item in dados:
        pei_completo = item.get('pei_data') or {}
        contexto_ia = pei_completo.get('ia_sugestao', '')
        
        if not contexto_ia:
            diag = item.get('diagnosis', 'Não informado')
            serie = item.get('grade', '')
            contexto_ia = f"Estudante: {item.get('name')}. Série: {serie}. Diagnóstico: {diag}."

        estudante = {
            'nome': item.get('name', ''),
            'serie': item.get('grade', ''),
            'hiperfoco': item.get('diagnosis', ''),
            'ia_sugestao': contexto_ia,
            'id': item.get('id', ''),
            'pei_data': pei_completo
        }
        if estudante['nome']:
            estudantes.append(estudante)
            
    return estudantes

# ==============================================================================
# FUNÇÕES PARA PAEE NO SUPABASE
# ==============================================================================
def carregar_pei_aluno(aluno_id):
    """Carrega o PEI do estudante do Supabase"""
    try:
        url = f"{ou._sb_url()}/rest/v1/students"
        params = {
            "select": "id,pei_data",
            "id": f"eq.{aluno_id}"
        }
        
        response = requests.get(url, headers=ou._headers(), params=params, timeout=10)
        if response.status_code == 200 and response.json():
            return response.json()[0].get('pei_data', {})
        return {}
    except Exception as e:
        st.error(f"Erro ao carregar PEI: {str(e)}")
        return {}

def salvar_paee_ciclo(aluno_id, ciclo_data):
    """Salva um ciclo de PAEE no Supabase"""
    try:
        # Primeiro, carrega os ciclos existentes
        url = f"{ou._sb_url()}/rest/v1/students"
        params = {"id": f"eq.{aluno_id}"}
        
        response = requests.get(url, headers=ou._headers(), params=params, timeout=10)
        if response.status_code == 200 and response.json():
            aluno = response.json()[0]
            ciclos_existentes = aluno.get('paee_ciclos', []) if aluno.get('paee_ciclos') else []
            
            # Verifica se é um novo ciclo ou atualização
            ciclo_id = ciclo_data.get('ciclo_id')
            if not ciclo_id:
                ciclo_id = str(uuid.uuid4())
                ciclo_data['ciclo_id'] = ciclo_id
                ciclo_data['criado_em'] = datetime.now().isoformat()
                ciclo_data['criado_por'] = st.session_state.get("user_id", "")
                ciclo_data['versao'] = 1
                ciclos_existentes.append(ciclo_data)
            else:
                # Atualiza ciclo existente
                for i, ciclo in enumerate(ciclos_existentes):
                    if ciclo.get('ciclo_id') == ciclo_id:
                        ciclos_existentes[i] = ciclo_data
                        ciclos_existentes[i]['versao'] = ciclo.get('versao', 1) + 1
                        break
            
            # Atualiza o estudante
            update_data = {
                "paee_ciclos": ciclos_existentes,
                "planejamento_ativo": ciclo_id,
                "status_planejamento": ciclo_data.get('status', 'rascunho')
            }
            
            if ciclo_data.get('config_ciclo', {}).get('data_inicio'):
                update_data["data_inicio_ciclo"] = ciclo_data['config_ciclo']['data_inicio']
            if ciclo_data.get('config_ciclo', {}).get('data_fim'):
                update_data["data_fim_ciclo"] = ciclo_data['config_ciclo']['data_fim']
            
            update_response = requests.patch(
                url, 
                headers=ou._headers(), 
                params=params, 
                json=update_data,
                timeout=20
            )
            
            if update_response.status_code == 204:
                return {"sucesso": True, "ciclo_id": ciclo_id}
            else:
                return {"sucesso": False, "erro": f"HTTP {update_response.status_code}: {update_response.text}"}
                
        return {"sucesso": False, "erro": "Aluno não encontrado"}
        
    except Exception as e:
        return {"sucesso": False, "erro": str(e)}

def carregar_ciclo_ativo(aluno_id):
    """Carrega o ciclo ativo do estudante"""
    try:
        url = f"{ou._sb_url()}/rest/v1/students"
        params = {
            "select": "id,paee_ciclos,planejamento_ativo",
            "id": f"eq.{aluno_id}"
        }
        
        response = requests.get(url, headers=ou._headers(), params=params, timeout=10)
        if response.status_code == 200 and response.json():
            aluno = response.json()[0]
            ciclo_id = aluno.get('planejamento_ativo')
            ciclos = aluno.get('paee_ciclos', []) if aluno.get('paee_ciclos') else []
            
            if ciclo_id and ciclos:
                for ciclo in ciclos:
                    if ciclo.get('ciclo_id') == ciclo_id:
                        return ciclo
        return None
    except Exception as e:
        st.error(f"Erro ao carregar ciclo: {str(e)}")
        return None

# ==============================================================================
# CARREGAMENTO DOS DADOS DOS ESTUDANTES
# ==============================================================================
if 'banco_estudantes' not in st.session_state or not st.session_state.banco_estudantes:
    with st.spinner(f"{get_icon('configurar', 18, '#A855F7')} Lendo dados da nuvem..."):
        st.session_state.banco_estudantes = carregar_estudantes_supabase()

if not st.session_state.banco_estudantes:
    st.info("📋 **Plano de Ação (AEE)** — Nenhum estudante cadastrado neste workspace. Cadastre estudantes e preencha o PEI para usar este módulo.")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("📘 Ir para Estratégias & PEI", type="primary", key="btn_pae_pei"):
            st.switch_page("pages/1_PEI.py")
    with c2:
        if st.button("👥 Ir para Estudantes", key="btn_pae_alunos"):
            st.switch_page("pages/Alunos.py")
    st.stop()

# --- SELEÇÃO DE ALUNO ---
lista_alunos = [a['nome'] for a in st.session_state.banco_estudantes]
col_sel, col_info = st.columns([1, 2])
with col_sel:
    nome_aluno = st.selectbox("📂 Selecione o Estudante:", lista_alunos)

aluno = next((a for a in st.session_state.banco_estudantes if a.get('nome') == nome_aluno), None)

if not aluno: 
    st.error("Estudante não encontrado")
    st.stop()

# --- DETECTOR DE EDUCAÇÃO INFANTIL ---
serie_aluno = aluno.get('serie', '').lower()
is_ei = any(term in serie_aluno for term in ["infantil", "creche", "pré", "maternal", "berçario", "jardim"])

# --- HEADER DO ESTUDANTE ---
st.markdown(f"""
    <div style="background-color: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 16px; padding: 20px 30px; margin-bottom: 20px; display: flex; justify-content: space-between; align-items: center; box-shadow: 0 2px 4px rgba(0,0,0,0.02);">
        <div><div style="font-size: 0.8rem; color: #64748B; font-weight: 800; text-transform: uppercase; letter-spacing: 1px;">Nome</div><div style="font-size: 1.2rem; color: #1E293B; font-weight: 800;">{aluno.get('nome')}</div></div>
        <div><div style="font-size: 0.8rem; color: #64748B; font-weight: 800; text-transform: uppercase; letter-spacing: 1px;">Série</div><div style="font-size: 1.2rem; color: #1E293B; font-weight: 800;">{aluno.get('serie')}</div></div>
        <div><div style="font-size: 0.8rem; color: #64748B; font-weight: 800; text-transform: uppercase; letter-spacing: 1px;">Diagnóstico</div><div style="font-size: 1.2rem; color: #1E293B; font-weight: 800;">{aluno.get('hiperfoco', '-')}</div></div>
    </div>
""", unsafe_allow_html=True)

if is_ei:
    st.info("🧸 **Modo Educação Infantil:** Foco em Campos de Experiência (BNCC).")

with st.expander("📄 Ver Dados Completos do PEI", expanded=False):
    st.write(aluno.get('ia_sugestao', 'Sem dados detalhados.'))

# ==============================================================================
# PARTE 3/4: FUNÇÕES DE IA E SISTEMA DE ESTADOS
# ==============================================================================

# ==============================================================================
# FUNÇÕES DE IA ATUALIZADAS
# ==============================================================================
def gerar_diagnostico_barreiras(api_key, aluno, obs_prof, feedback=None):
    client = OpenAI(api_key=api_key)
    contexto = aluno.get('ia_sugestao', '')
    
    prompt = f"""
    ATUAR COMO: Especialista em AEE.
    ESTUDANTE: {aluno['nome']} | DIAGNÓSTICO: {aluno.get('hiperfoco')}
    CONTEXTO DO PEI: {contexto[:2500]}
    OBSERVAÇÃO ATUAL: {obs_prof}
    """
    
    if feedback:
        prompt += f"\nFEEDBACK PARA AJUSTE (revisão do professor): {feedback}\n"
    
    prompt += """
    CLASSIFIQUE AS BARREIRAS (LBI):
    1. Barreiras Comunicacionais - dificuldades na comunicação e linguagem
    2. Barreiras Metodológicas - métodos de ensino inadequados
    3. Barreiras Atitudinais - atitudes e preconceitos
    4. Barreiras Tecnológicas - falta de recursos tecnológicos adequados
    5. Barreiras Arquitetônicas - espaço físico inadequado
    
    Para cada barreira identificada, forneça:
    - Descrição específica da barreira
    - Impacto na aprendizagem do estudante
    - Sugestões de intervenção imediata práticas e aplicáveis
    - Recursos necessários para implementação
    
    FORMATO DE SAÍDA:
    IMPORTANTE: NÃO use tabelas Markdown. Use apenas texto formatado com:
    - Títulos claros para cada tipo de barreira (ex: "BARREIRAS METODOLÓGICAS")
    - Parágrafos descritivos
    - Listas com marcadores simples (-) para organizar informações
    - Quebras de linha para separar seções
    
    Estrutura sugerida:
    
    [TÍTULO DA BARREIRA]
    
    Descrição: [texto descritivo]
    
    Impacto na Aprendizagem: [texto descritivo]
    
    Sugestões de Intervenção:
    - [sugestão 1]
    - [sugestão 2]
    - [sugestão 3]
    
    Recursos Necessários:
    - [recurso 1]
    - [recurso 2]
    
    SAÍDA: Texto formatado de forma clara e legível, SEM tabelas Markdown.
    """
    
    try:
        resp = client.chat.completions.create(
            model="gpt-4o-mini", 
            messages=[{"role": "user", "content": prompt}], 
            temperature=0.5
        )
        return resp.choices[0].message.content
    except Exception as e: 
        return f"Erro: {str(e)}"

def gerar_projetos_ei_bncc(api_key, aluno, campo_exp, feedback=None):
    client = OpenAI(api_key=api_key)
    contexto = aluno.get('ia_sugestao', '')
    
    prompt = f"""
    ATUAR COMO: Especialista em Ed. Infantil Inclusiva.
    ESTUDANTE: {aluno['nome']} | CONTEXTO PEI: {contexto[:2000]}
    CAMPO DE EXPERIÊNCIA: "{campo_exp}".
    """
    
    if feedback:
        prompt += f"\nFEEDBACK PARA AJUSTE (revisão do professor): {feedback}\n"
    
    prompt += """
    Crie 3 EXPERIÊNCIAS LÚDICAS (Atividades) com estrutura completa:
    
    Para cada experiência, inclua:
    1. **Título da Atividade**
    2. **Objetivos de aprendizagem** (alinhados com BNCC)
    3. **Materiais necessários** (acessíveis e de baixo custo)
    4. **Passo a passo detalhado**
    5. **Adaptações específicas** para o aluno
    6. **Avaliação formativa** (como observar o progresso)
    7. **Dicas para o professor**
    
    FOQUE em:
    - Uso de interesses do aluno como motivação
    - Eliminação de barreiras sensoriais e comunicacionais
    - Atividades sensoriais e concretas
    - Inclusão de todos os estudantes da turma
    """
    
    try:
        resp = client.chat.completions.create(
            model="gpt-4o-mini", 
            messages=[{"role": "user", "content": prompt}], 
            temperature=0.7
        )
        return resp.choices[0].message.content
    except Exception as e: 
        return str(e)

def gerar_plano_habilidades(api_key, aluno, foco_treino, feedback=None):
    client = OpenAI(api_key=api_key)
    contexto = aluno.get('ia_sugestao', '')
    
    prompt = f"""
    CRIE PLANO DE INTERVENÇÃO AEE.
    FOCO: {foco_treino}.
    ESTUDANTE: {aluno['nome']} | CONTEXTO PEI: {contexto[:2000]}
    """
    
    if feedback:
        prompt += f"\nFEEDBACK PARA AJUSTE (revisão do professor): {feedback}\n"
    
    prompt += """
    GERE 3 METAS SMART (Curto, Médio, Longo prazo) com estrutura completa:
    
    Para cada meta, inclua:
    1. **Meta Específica** (o que será alcançado)
    2. **Indicadores de Progresso** (como medir)
    3. **Estratégias de Ensino** (como ensinar)
    4. **Recursos e Materiais**
    5. **Frequência de Intervenção**
    6. **Responsáveis** (AEE, sala regular, família)
    7. **Critérios de Sucesso**
    
    TEMPORALIDADE:
    - CURTO PRAZO (1-2 meses): Habilidades básicas
    - MÉDIO PRAZO (3-6 meses): Consolidação
    - LONGO PRAZO (6-12 meses): Generalização
    
    Inclua também:
    - Registro de observações
    - Sistema de monitoramento
    - Estratégias de generalização para outros contextos
    """
    
    try:
        resp = client.chat.completions.create(
            model="gpt-4o-mini", 
            messages=[{"role": "user", "content": prompt}], 
            temperature=0.7
        )
        return resp.choices[0].message.content
    except Exception as e: 
        return str(e)

def sugerir_tecnologia_assistiva(api_key, aluno, dificuldade, feedback=None):
    client = OpenAI(api_key=api_key)
    contexto = aluno.get('ia_sugestao', '')
    
    prompt = f"""
    SUGESTÃO DE TECNOLOGIA ASSISTIVA.
    Estudante: {aluno['nome']} | Dificuldade: {dificuldade}.
    Contexto PEI: {contexto[:1500]}
    """
    
    if feedback:
        prompt += f"\nFEEDBACK PARA AJUSTE (revisão do professor): {feedback}\n"
    
    prompt += """
    Sugira recursos em 3 níveis:
    
    1. **BAIXA TECNOLOGIA (DIY - Faça Você Mesmo)**
       - Materiais simples e de baixo custo
       - Instruções passo a passo
       - Tempo de confecção
       - Custo estimado
    
    2. **MÉDIA TECNOLOGIA**
       - Recursos prontos disponíveis no mercado
       - Aplicativos gratuitos ou de baixo custo
       - Adaptações simples de materiais existentes
       - Onde encontrar/comprar
    
    3. **ALTA TECNOLOGIA**
       - Equipamentos especializados
       - Softwares específicos
       - Recursos de acessibilidade avançados
       - Processo de solicitação/viabilidade
    
    Para cada sugestão, inclua:
    - Nome do recurso
    - Finalidade específica
    - Como usar na prática
    - Benefícios para o aluno
    - Dificuldades possíveis e soluções
    - Referências para aprofundamento
    """
    
    try:
        resp = client.chat.completions.create(
            model="gpt-4o-mini", 
            messages=[{"role": "user", "content": prompt}], 
            temperature=0.7
        )
        return resp.choices[0].message.content
    except Exception as e: 
        return str(e)

def gerar_documento_articulacao(api_key, aluno, frequencia, acoes, feedback=None):
    client = OpenAI(api_key=api_key)
    
    prompt = f"""
    CARTA DE ARTICULAÇÃO (AEE -> SALA REGULAR).
    Estudante: {aluno['nome']}. 
    Frequência no AEE: {frequencia}.
    Ações desenvolvidas no AEE: {acoes}.
    """
    
    if feedback:
        prompt += f"\nFEEDBACK PARA AJUSTE (revisão do professor): {feedback}\n"
    
    prompt += """
    ESTRUTURA DO DOCUMENTO:
    
    1. **Cabeçalho Institucional**
       - Nome da escola
       - Data
       - Destinatário (Professor Regente)
    
    2. **Resumo das Habilidades Desenvolvidas**
       - Competências trabalhadas
       - Progressos observados
       - Dificuldades persistentes
    
    3. **Estratégias de Generalização** (para sala regular)
       - Como transferir as habilidades
       - Adaptações necessárias
       - Sinais de alerta
    
    4. **Orientações Práticas** (3 dicas principais)
       - Para atividades em grupo
       - Para avaliações
       - Para gestão comportamental
    
    5. **Plano de Ação Conjunto**
       - Responsabilidades do AEE
       - Responsabilidades da sala regular
       - Envolvimento da família
    
    6. **Próximos Passos**
       - Reuniões de alinhamento
       - Avaliações periódicas
       - Ajustes necessários
    
    7. **Contatos e Suporte**
       - Horários de atendimento
       - Canal de comunicação
       - Emergências
    
    Formato: Documento formal mas acolhedor, com linguagem clara e objetiva.
    """
    
    try:
        resp = client.chat.completions.create(
            model="gpt-4o-mini", 
            messages=[{"role": "user", "content": prompt}], 
            temperature=0.7
        )
        return resp.choices[0].message.content
    except Exception as e: 
        return str(e)

def gerar_cronograma_inteligente(api_key, aluno, semanas, foco, metas):
    """Gera cronograma com IA baseado nas metas do PEI"""
    try:
        client = OpenAI(api_key=api_key)
        
        # Preparar prompt com metas
        metas_texto = "\n".join([f"- {m['tipo']}: {m['descricao']}" for m in metas[:5]])
        
        prompt = f"""
        Crie um cronograma de {semanas} semanas para AEE.
        
        ESTUDANTE: {aluno['nome']}
        DIAGNÓSTICO: {aluno.get('hiperfoco', '')}
        FOCO DO CICLO: {foco}
        
        METAS DO PEI:
        {metas_texto}
        
        Estruture em fases lógicas. Para cada semana, defina:
        1. Tema da semana
        2. Objetivo específico
        3. Atividades principais (2-3 atividades por semana)
        4. Recursos necessários
        5. Formas de avaliação
        
        Formato JSON:
        {{
            "fases": [
                {{
                    "nome": "Nome da fase",
                    "descricao": "Descrição",
                    "semanas": [1, 2, 3],
                    "objetivo_geral": "Objetivo da fase"
                }}
            ],
            "semanas": [
                {{
                    "numero": 1,
                    "tema": "Tema da semana",
                    "objetivo": "Objetivo específico",
                    "atividades": ["Atividade 1", "Atividade 2"],
                    "recursos": ["Recurso 1", "Recurso 2"],
                    "avaliacao": "Como avaliar o progresso"
                }}
            ]
        }}
        """
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        
        # Extrair e parsear JSON
        texto = response.choices[0].message.content
        
        # Extrair JSON do texto
        import re
        json_match = re.search(r'```json\n(.*?)\n```', texto, re.DOTALL)
        if json_match:
            texto = json_match.group(1)
        else:
            # Tenta encontrar qualquer JSON
            json_match = re.search(r'\{.*\}', texto, re.DOTALL)
            if json_match:
                texto = json_match.group(0)
        
        return json.loads(texto)
        
    except Exception as e:
        st.error(f"Erro na IA: {str(e)}")
        return None

# ==============================================================================
# FUNÇÕES AUXILIARES PARA PAEE
# ==============================================================================
def extrair_metas_do_pei(pei_data):
    """Extrai metas estruturadas do PEI"""
    if not pei_data:
        return []
    
    metas = []
    
    # Tenta diferentes formatos de PEI
    if isinstance(pei_data, dict):
        # Formato JSON estruturado
        if 'metas' in pei_data and isinstance(pei_data['metas'], list):
            return pei_data['metas']
        
        # Formato texto da IA
        if 'ia_sugestao' in pei_data:
            texto = pei_data['ia_sugestao']
        else:
            texto = str(pei_data)
    else:
        texto = str(pei_data)
    
    # Parse de texto
    linhas = texto.split('\n')
    for linha in linhas:
        linha = linha.strip()
        # Procura por padrões de metas
        if any(marker in linha.lower() for marker in ['meta:', 'objetivo:', 'habilidade:', '- ', '* ']):
            # Remove marcadores
            for marker in ['Meta:', 'meta:', 'Objetivo:', 'objetivo:', 'Habilidade:', 'habilidade:', '- ', '* ']:
                if linha.startswith(marker):
                    linha = linha[len(marker):].strip()
                    break
            
            if linha and len(linha) > 5:  # Evita linhas muito curtas
                # Tenta identificar tipo
                tipo = "GERAL"
                if 'social' in linha.lower():
                    tipo = "HABILIDADES SOCIAIS"
                elif 'comunicação' in linha.lower() or 'comunicacao' in linha.lower():
                    tipo = "COMUNICAÇÃO"
                elif 'leitura' in linha.lower() or 'escrita' in linha.lower() or 'matemática' in linha.lower():
                    tipo = "ACADÊMICO"
                elif 'motor' in linha.lower():
                    tipo = "MOTOR"
                elif 'autonomia' in linha.lower():
                    tipo = "AUTONOMIA"
                
                metas.append({
                    'id': f"meta_{len(metas)+1:03d}",
                    'tipo': tipo,
                    'descricao': linha[:200],
                    'prioridade': 'media',
                    'selecionada': True
                })
    
    # Se não encontrou metas, cria uma genérica
    if not metas:
        metas.append({
            'id': 'meta_001',
            'tipo': 'DESENVOLVIMENTO',
            'descricao': 'Desenvolver habilidades específicas conforme necessidades identificadas no PEI',
            'prioridade': 'alta',
            'selecionada': True
        })
    
    return metas[:10]  # Limita a 10 metas

def criar_cronograma_basico(semanas, metas):
    """Cria um cronograma básico sem IA"""
    cronograma = {
        "fases": [
            {
                "nome": "Fase 1: Avaliação e Adaptação",
                "descricao": "Período inicial de avaliação e adaptação das estratégias",
                "semanas": list(range(1, min(4, semanas) + 1)),
                "objetivo_geral": "Estabelecer rotina e avaliar necessidades imediatas"
            }
        ],
        "semanas": []
    }
    
    # Adiciona fases adicionais se houver mais semanas
    if semanas > 4:
        cronograma["fases"].append({
            "nome": "Fase 2: Desenvolvimento",
            "descricao": "Desenvolvimento intensivo das habilidades alvo",
            "semanas": list(range(5, min(9, semanas) + 1)),
            "objetivo_geral": "Desenvolver habilidades específicas"
        })
    
    if semanas > 8:
        cronograma["fases"].append({
            "nome": "Fase 3: Consolidação",
            "descricao": "Consolidação e generalização das habilidades",
            "semanas": list(range(9, semanas + 1)),
            "objetivo_geral": "Generalizar habilidades para outros contextos"
        })
    
    # Cria semanas básicas
    for semana in range(1, semanas + 1):
        cronograma["semanas"].append({
            "numero": semana,
            "tema": f"Semana {semana}: Desenvolvimento de habilidades",
            "objetivo": "Avançar nas metas estabelecidas",
            "atividades": ["Atividades personalizadas conforme plano"],
            "recursos": ["Materiais adaptados", "Recursos visuais"],
            "avaliacao": "Observação direta e registros"
        })
    
    return cronograma

# ==============================================================================
# SISTEMA DE GESTÃO DE RECURSOS (ESTADOS)
# ==============================================================================
def inicializar_estados():
    """Inicializa os estados para todos os recursos"""
    recursos = [
        'diagnostico_barreiras',
        'projetos_ei',
        'plano_habilidades',
        'tecnologia_assistiva',
        'documento_articulacao'
    ]
    
    for recurso in recursos:
        if f'status_{recurso}' not in st.session_state:
            st.session_state[f'status_{recurso}'] = 'rascunho'
        if f'conteudo_{recurso}' not in st.session_state:
            st.session_state[f'conteudo_{recurso}'] = ''
        if f'feedback_{recurso}' not in st.session_state:
            st.session_state[f'feedback_{recurso}'] = ''
        if f'input_original_{recurso}' not in st.session_state:
            st.session_state[f'input_original_{recurso}'] = {}

inicializar_estados()

# ==============================================================================
# PARTE 4/4: INTERFACE PRINCIPAL E COMPONENTES
# ==============================================================================

# ==============================================================================
# COMPONENTE DE VALIDAÇÃO/AJUSTE (HUB DE RECURSOS)
# ==============================================================================
def renderizar_hub_recurso(tipo_recurso, conteudo_gerado, aluno_nome, dados_entrada=None):
    """Renderiza o hub de recursos com validação, ajuste e download"""
    
    # Estados do recurso
    status = st.session_state.get(f'status_{tipo_recurso}', 'rascunho')
    
    # Container principal
    with st.container():
        st.markdown(f"<div class='resource-box'>", unsafe_allow_html=True)
        
        # TÍTULO DO RECURSO
        titulos = {
            'diagnostico_barreiras': f'{get_icon("buscar", 18, "#A855F7")} Diagnóstico de Barreiras',
            'projetos_ei': f'{get_icon("estudio_visual", 18, "#A855F7")} Banco de Experiências (BNCC)',
            'plano_habilidades': f'{get_icon("monitoramento", 18, "#A855F7")} Plano de Habilidades',
            'tecnologia_assistiva': f'{get_icon("configurar", 18, "#A855F7")} Tecnologia Assistiva',
            'documento_articulacao': f'{get_icon("download", 18, "#A855F7")} Documento de Articulação'
        }
        
        st.subheader(titulos.get(tipo_recurso, 'Recurso Gerado'))
        
        # 1. MODO REVISÃO (após geração inicial)
        if status == 'revisao':
            # Mostra o conteúdo gerado em container formatado
            st.markdown(f"### {icon_title('Conteúdo Gerado', 'pae', 20, '#A855F7')}", unsafe_allow_html=True)
            with st.container(border=True):
                # Usa st.markdown mas com escape para não renderizar tabelas
                # Remove formatação de tabela Markdown se houver
                conteudo_limpo = conteudo_gerado.replace('|', ' ').replace('---', '')
                st.markdown(conteudo_limpo)
            
            st.markdown("---")
            st.markdown(f"### {icon_title('Ações Disponíveis', 'configurar', 20, '#A855F7')}", unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("✅ **Validar e Finalizar**", key=f"validar_{tipo_recurso}", 
                           use_container_width=True, type="primary"):
                    st.session_state[f'status_{tipo_recurso}'] = 'aprovado'
                    st.success("Recurso validado com sucesso!")
                    time.sleep(1)
                    st.rerun()
            
            with col2:
                if st.button("🔄 **Solicitar Ajustes**", key=f"ajustar_{tipo_recurso}",
                           use_container_width=True):
                    st.session_state[f'status_{tipo_recurso}'] = 'ajustando'
                    st.rerun()
            
            with col3:
                if st.button("🗑️ **Descartar e Regenerar**", key=f"descartar_{tipo_recurso}",
                           use_container_width=True):
                    st.session_state[f'status_{tipo_recurso}'] = 'rascunho'
                    st.session_state[f'conteudo_{tipo_recurso}'] = ''
                    st.info("Recurso descartado. Você pode gerar novamente.")
                    st.rerun()
        
        # 2. MODO AJUSTANDO (professor solicitou ajustes)
        elif status == 'ajustando':
            st.warning("✏️ **Modo de Ajuste Ativo**")
            
            # Campo para feedback detalhado
            feedback = st.text_area(
                "**Descreva os ajustes necessários:**",
                placeholder="Exemplo: 'Preciso de mais exemplos práticos...'\n'Inclua atividades para trabalho em grupo...'\n'Foque mais na comunicação alternativa...'",
                height=150,
                key=f"feedback_input_{tipo_recurso}"
            )
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("🔄 **Regerar com Ajustes**", 
                           key=f"regerar_{tipo_recurso}",
                           use_container_width=True, type="primary"):
                    if feedback:
                        st.session_state[f'feedback_{tipo_recurso}'] = feedback
                        st.info("Regerando com os ajustes solicitados...")
                        st.session_state[f'status_{tipo_recurso}'] = 'regerando'
                        st.rerun()
                    else:
                        st.error("Por favor, descreva os ajustes desejados.")
            
            with col2:
                if st.button("↩️ **Cancelar Ajustes**", 
                           key=f"cancelar_{tipo_recurso}",
                           use_container_width=True):
                    st.session_state[f'status_{tipo_recurso}'] = 'revisao'
                    st.rerun()
        
        # 3. MODO APROVADO (recurso validado)
        elif status == 'aprovado':
            st.success("✅ **Recurso Validado e Pronto para Uso**")
            
            # Mostra o conteúdo final em container formatado
            st.markdown(f"### {icon_title('Conteúdo Final', 'pae', 20, '#A855F7')}", unsafe_allow_html=True)
            with st.container(border=True):
                # Remove formatação de tabela Markdown se houver
                conteudo_limpo = conteudo_gerado.replace('|', ' ').replace('---', '')
                st.markdown(conteudo_limpo)
            
            st.markdown("---")
            st.markdown(f"### {icon_title('Opções de Download', 'download', 20, '#A855F7')}", unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Download TXT
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                nome_arquivo = f"{tipo_recurso}_{aluno_nome}_{timestamp}.txt"
                st.download_button(
                    label="📥 **Baixar TXT**",
                    data=conteudo_gerado,
                    file_name=nome_arquivo,
                    mime="text/plain",
                    use_container_width=True
                )
            
            with col2:
                if st.button("✏️ **Editar Novamente**", 
                           key=f"reeditar_{tipo_recurso}",
                           use_container_width=True):
                    st.session_state[f'status_{tipo_recurso}'] = 'revisao'
                    st.rerun()
        
        # 4. MODO REGERANDO (processando ajustes)
        elif status == 'regerando':
            st.info(f"{get_icon('configurar', 18, '#2563EB')} **Processando ajustes solicitados...**")
            # Este estado é transitório, será tratado na função principal
        
        st.markdown("</div>", unsafe_allow_html=True)

# ==============================================================================
# INICIALIZAR API KEY (ANTES DAS ABAS)
# ==============================================================================
# Obter a chave API do OpenAI (Render: env var → Streamlit Cloud: secrets → sessão)
api_key = os.environ.get("OPENAI_API_KEY") or ou.get_setting("OPENAI_API_KEY", "") or st.session_state.get("OPENAI_API_KEY")
api_key = api_key if api_key else None

# ==============================================================================
# CRIAR AS ABAS PRINCIPAIS
# ==============================================================================

# Criar abas diferentes para EI e não-EI
if is_ei:
    tab_barreiras, tab_projetos, tab_rotina, tab_ponte, tab_planejamento = st.tabs([
        "BARREIRAS NO BRINCAR", "BANCO DE EXPERIÊNCIAS", "ROTINA & ADAPTAÇÃO", 
        "ARTICULAÇÃO", "PLANEJAMENTO DO CICLO"
    ])
else:
    tab_barreiras, tab_plano, tab_tec, tab_ponte, tab_planejamento = st.tabs([
        "MAPEAR BARREIRAS", "PLANO DE HABILIDADES", "TEC. ASSISTIVA", 
        "ARTICULAÇÃO", "PLANEJAMENTO DO CICLO"
    ])

# ==============================================================================
# ABA 1: BARREIRAS NO BRINCAR (EI) / MAPEAR BARREIRAS (NÃO EI)
# ==============================================================================
if is_ei:
    with tab_barreiras:
        st.markdown("<div class='pedagogia-box'><strong>Diagnóstico do Brincar:</strong> Identifique barreiras na interação e no brincar.</div>", unsafe_allow_html=True)
        
        status_atual = st.session_state.get('status_diagnostico_barreiras', 'rascunho')
        
        if status_atual == 'rascunho':
            # Modo inicial - coleta de dados
            obs_aee = st.text_area(
                "Observação do Brincar:", 
                height=100,
                placeholder="Exemplo: O estudante se recusa a escrever quando solicitado, demonstrando ansiedade e evitamento. Durante atividades de escrita, ele tenta sair da sala ou distrai os colegas. Quando consegue iniciar, abandona a tarefa após algumas linhas, dizendo que está cansado ou que não sabe fazer."
            )
            
            if st.button("🔍 Mapear Barreiras", type="primary", use_container_width=True):
                if not api_key:
                    st.error("Insira a chave OpenAI nas configurações.")
                elif not obs_aee:
                    st.warning("Por favor, descreva suas observações antes de mapear.")
                else:
                    with st.spinner("Analisando barreiras no brincar..."):
                        resultado = gerar_diagnostico_barreiras(api_key, aluno, obs_aee)
                        if "Erro:" in resultado:
                            st.error(resultado)
                        else:
                            st.session_state.conteudo_diagnostico_barreiras = resultado
                            st.session_state.status_diagnostico_barreiras = 'revisao'
                            st.session_state.input_original_diagnostico_barreiras = {'obs': obs_aee}
                            st.success("Diagnóstico gerado com sucesso!")
                            st.rerun()
        
        else:
            # Modo hub de recursos - já tem conteúdo gerado
            renderizar_hub_recurso(
                tipo_recurso='diagnostico_barreiras',
                conteudo_gerado=st.session_state.conteudo_diagnostico_barreiras,
                aluno_nome=aluno['nome']
            )
            
            # Tratamento especial para regeração com feedback
            if st.session_state.status_diagnostico_barreiras == 'regerando':
                feedback = st.session_state.get('feedback_diagnostico_barreiras', '')
                input_original = st.session_state.get('input_original_diagnostico_barreiras', {})
                obs_original = input_original.get('obs', '')
                
                with st.spinner("Aplicando ajustes solicitados..."):
                    resultado = gerar_diagnostico_barreiras(
                        api_key, aluno, obs_original, feedback
                    )
                    st.session_state.conteudo_diagnostico_barreiras = resultado
                    st.session_state.status_diagnostico_barreiras = 'revisao'
                    st.rerun()
else:
    with tab_barreiras:
        st.markdown("<div class='pedagogia-box'><strong>Diagnóstico de Acessibilidade:</strong> O que impede a participação plena do aluno?</div>", unsafe_allow_html=True)
        
        status_atual = st.session_state.get('status_diagnostico_barreiras', 'rascunho')
        
        if status_atual == 'rascunho':
            obs_aee = st.text_area(
                "Observações Iniciais do AEE:", 
                height=100,
                placeholder="Exemplo: O estudante se recusa a escrever quando solicitado, demonstrando ansiedade e evitamento. Durante atividades de escrita, ele tenta sair da sala ou distrai os colegas. Quando consegue iniciar, abandona a tarefa após algumas linhas, dizendo que está cansado ou que não sabe fazer."
            )
            
            if st.button("🔍 Analisar Barreiras", type="primary", use_container_width=True):
                if not api_key:
                    st.error("Insira a chave OpenAI nas configurações.")
                elif not obs_aee:
                    st.warning("Por favor, descreva suas observações antes de analisar.")
                else:
                    with st.spinner("Analisando barreiras de acessibilidade..."):
                        resultado = gerar_diagnostico_barreiras(api_key, aluno, obs_aee)
                        if "Erro:" in resultado:
                            st.error(resultado)
                        else:
                            st.session_state.conteudo_diagnostico_barreiras = resultado
                            st.session_state.status_diagnostico_barreiras = 'revisao'
                            st.session_state.input_original_diagnostico_barreiras = {'obs': obs_aee}
                            st.success("Análise de barreiras concluída!")
                            st.rerun()
        
        else:
            renderizar_hub_recurso(
                tipo_recurso='diagnostico_barreiras',
                conteudo_gerado=st.session_state.conteudo_diagnostico_barreiras,
                aluno_nome=aluno['nome']
            )
            
            if st.session_state.status_diagnostico_barreiras == 'regerando':
                feedback = st.session_state.get('feedback_diagnostico_barreiras', '')
                input_original = st.session_state.get('input_original_diagnostico_barreiras', {})
                obs_original = input_original.get('obs', '')
                
                with st.spinner("Aplicando ajustes..."):
                    resultado = gerar_diagnostico_barreiras(
                        api_key, aluno, obs_original, feedback
                    )
                    st.session_state.conteudo_diagnostico_barreiras = resultado
                    st.session_state.status_diagnostico_barreiras = 'revisao'
                    st.rerun()

# ==============================================================================
# ABA 2: BANCO DE EXPERIÊNCIAS (EI) / PLANO DE HABILIDADES (NÃO EI)
# ==============================================================================
if is_ei:
    with tab_projetos:
        st.markdown("<div class='pedagogia-box'><strong>Banco de Experiências (BNCC):</strong> Atividades lúdicas alinhadas aos Campos de Experiência.</div>", unsafe_allow_html=True)
        
        status_atual = st.session_state.get('status_projetos_ei', 'rascunho')
        
        if status_atual == 'rascunho':
            campo_bncc = st.selectbox(
                "Selecione o Campo de Experiência:",
                ["O eu, o outro e o nós", "Corpo, gestos e movimentos", 
                 "Traços, sons, cores e formas", "Escuta, fala, pensamento e imaginação", 
                 "Espaços, tempos, quantidades, relações e transformações"],
                key="campo_bncc_ei"
            )
            
            if st.button("✨ Gerar Atividades", type="primary", use_container_width=True):
                if not api_key:
                    st.error("Insira a chave OpenAI nas configurações.")
                else:
                    with st.spinner("Criando banco de experiências..."):
                        resultado = gerar_projetos_ei_bncc(api_key, aluno, campo_bncc)
                        if "Erro:" in resultado:
                            st.error(resultado)
                        else:
                            st.session_state.conteudo_projetos_ei = resultado
                            st.session_state.status_projetos_ei = 'revisao'
                            st.session_state.input_original_projetos_ei = {'campo': campo_bncc}
                            st.success("Banco de experiências gerado!")
                            st.rerun()
        
        else:
            renderizar_hub_recurso(
                tipo_recurso='projetos_ei',
                conteudo_gerado=st.session_state.conteudo_projetos_ei,
                aluno_nome=aluno['nome']
            )
            
            if st.session_state.status_projetos_ei == 'regerando':
                feedback = st.session_state.get('feedback_projetos_ei', '')
                input_original = st.session_state.get('input_original_projetos_ei', {})
                campo_original = input_original.get('campo', 'O eu, o outro e o nós')
                
                with st.spinner("Aplicando ajustes..."):
                    resultado = gerar_projetos_ei_bncc(
                        api_key, aluno, campo_original, feedback
                    )
                    st.session_state.conteudo_projetos_ei = resultado
                    st.session_state.status_projetos_ei = 'revisao'
                    st.rerun()
else:
    with tab_plano:
        st.markdown("<div class='pedagogia-box'><strong>Treino de Habilidades:</strong> Desenvolvimento de competências específicas no AEE.</div>", unsafe_allow_html=True)
        
        status_atual = st.session_state.get('status_plano_habilidades', 'rascunho')
        
        if status_atual == 'rascunho':
            foco = st.selectbox(
                "Foco do Atendimento:",
                ["Funções Executivas", "Autonomia", "Coordenação Motora", 
                 "Comunicação", "Habilidades Sociais", "Leitura e Escrita",
                 "Matemática", "Tecnologias Assistivas", "Organização e Planejamento"],
                key="foco_plano_naoei"
            )
            
            if st.button("📋 Gerar Plano", type="primary", use_container_width=True):
                if not api_key:
                    st.error("Insira a chave OpenAI nas configurações.")
                else:
                    with st.spinner("Elaborando plano de intervenção..."):
                        resultado = gerar_plano_habilidades(api_key, aluno, foco)
                        if "Erro:" in resultado:
                            st.error(resultado)
                        else:
                            st.session_state.conteudo_plano_habilidades = resultado
                            st.session_state.status_plano_habilidades = 'revisao'
                            st.session_state.input_original_plano_habilidades = {'foco': foco}
                            st.success("Plano de habilidades gerado!")
                            st.rerun()
        
        else:
            renderizar_hub_recurso(
                tipo_recurso='plano_habilidades',
                conteudo_gerado=st.session_state.conteudo_plano_habilidades,
                aluno_nome=aluno['nome']
            )
            
            if st.session_state.status_plano_habilidades == 'regerando':
                feedback = st.session_state.get('feedback_plano_habilidades', '')
                input_original = st.session_state.get('input_original_plano_habilidades', {})
                foco_original = input_original.get('foco', 'Funções Executivas')
                
                with st.spinner("Aplicando ajustes..."):
                    resultado = gerar_plano_habilidades(
                        api_key, aluno, foco_original, feedback
                    )
                    st.session_state.conteudo_plano_habilidades = resultado
                    st.session_state.status_plano_habilidades = 'revisao'
                    st.rerun()

# ==============================================================================
# ABA 3: ROTINA & ADAPTAÇÃO (EI) / TEC. ASSISTIVA (NÃO EI)
# ==============================================================================
if is_ei:
    with tab_rotina:
        st.markdown("<div class='pedagogia-box'><strong>Adaptação de Rotina:</strong> Recursos visuais e sensoriais para rotina da Educação Infantil.</div>", unsafe_allow_html=True)
        
        status_atual = st.session_state.get('status_tecnologia_assistiva', 'rascunho')
        
        if status_atual == 'rascunho':
            dif_rotina = st.text_input(
                "Dificuldade Específica na Rotina:",
                placeholder="Ex: Transições entre atividades, organização do material, comunicação de necessidades...",
                key="dif_rotina_ei"
            )
            
            if st.button("🛠️ Sugerir Adaptação", type="primary", use_container_width=True):
                if not api_key:
                    st.error("Insira a chave OpenAI nas configurações.")
                elif not dif_rotina:
                    st.warning("Por favor, descreva a dificuldade específica.")
                else:
                    with st.spinner("Buscando recursos de adaptação..."):
                        resultado = sugerir_tecnologia_assistiva(
                            api_key, aluno, f"Rotina EI: {dif_rotina}"
                        )
                        if "Erro:" in resultado:
                            st.error(resultado)
                        else:
                            st.session_state.conteudo_tecnologia_assistiva = resultado
                            st.session_state.status_tecnologia_assistiva = 'revisao'
                            st.session_state.input_original_tecnologia_assistiva = {'dificuldade': dif_rotina}
                            st.success("Sugestões de adaptação geradas!")
                            st.rerun()
        
        else:
            renderizar_hub_recurso(
                tipo_recurso='tecnologia_assistiva',
                conteudo_gerado=st.session_state.conteudo_tecnologia_assistiva,
                aluno_nome=aluno['nome']
            )
            
            if st.session_state.status_tecnologia_assistiva == 'regerando':
                feedback = st.session_state.get('feedback_tecnologia_assistiva', '')
                input_original = st.session_state.get('input_original_tecnologia_assistiva', {})
                dif_original = input_original.get('dificuldade', '')
                
                with st.spinner("Aplicando ajustes..."):
                    resultado = sugerir_tecnologia_assistiva(
                        api_key, aluno, f"Rotina EI: {dif_original}", feedback
                    )
                    st.session_state.conteudo_tecnologia_assistiva = resultado
                    st.session_state.status_tecnologia_assistiva = 'revisao'
                    st.rerun()
else:
    with tab_tec:
        st.markdown("<div class='pedagogia-box'><strong>Tecnologia Assistiva:</strong> Recursos para promover autonomia e participação.</div>", unsafe_allow_html=True)
        
        status_atual = st.session_state.get('status_tecnologia_assistiva', 'rascunho')
        
        if status_atual == 'rascunho':
            dif_especifica = st.text_input(
                "Dificuldade Específica:",
                placeholder="Ex: Dificuldade na escrita, comunicação, mobilidade, organização...",
                key="dif_especifica_naoei"
            )
            
            if st.button("🔧 Sugerir Recursos", type="primary", use_container_width=True):
                if not api_key:
                    st.error("Insira a chave OpenAI nas configurações.")
                elif not dif_especifica:
                    st.warning("Por favor, descreva a dificuldade específica.")
                else:
                    with st.spinner("Buscando tecnologias assistivas..."):
                        resultado = sugerir_tecnologia_assistiva(api_key, aluno, dif_especifica)
                        if "Erro:" in resultado:
                            st.error(resultado)
                        else:
                            st.session_state.conteudo_tecnologia_assistiva = resultado
                            st.session_state.status_tecnologia_assistiva = 'revisao'
                            st.session_state.input_original_tecnologia_assistiva = {'dificuldade': dif_especifica}
                            st.success("Sugestões de TA geradas!")
                            st.rerun()
        
        else:
            renderizar_hub_recurso(
                tipo_recurso='tecnologia_assistiva',
                conteudo_gerado=st.session_state.conteudo_tecnologia_assistiva,
                aluno_nome=aluno['nome']
            )
            
            if st.session_state.status_tecnologia_assistiva == 'regerando':
                feedback = st.session_state.get('feedback_tecnologia_assistiva', '')
                input_original = st.session_state.get('input_original_tecnologia_assistiva', {})
                dif_original = input_original.get('dificuldade', '')
                
                with st.spinner("Aplicando ajustes..."):
                    resultado = sugerir_tecnologia_assistiva(
                        api_key, aluno, dif_original, feedback
                    )
                    st.session_state.conteudo_tecnologia_assistiva = resultado
                    st.session_state.status_tecnologia_assistiva = 'revisao'
                    st.rerun()

# ==============================================================================
# ABA 4: ARTICULAÇÃO (para EI e não EI)
# ==============================================================================
with tab_ponte:
    st.markdown("<div class='pedagogia-box'><strong>Ponte com a Sala Regular:</strong> Documento colaborativo para articulação entre AEE e sala de aula.</div>", unsafe_allow_html=True)
    
    status_atual = st.session_state.get('status_documento_articulacao', 'rascunho')
    
    if status_atual == 'rascunho':
        c1, c2 = st.columns(2)
        with c1:
            freq = st.selectbox(
                "Frequência no AEE:",
                ["1x/sem", "2x/sem", "3x/sem", "Diário"],
                key='freq_articulacao'
            )
        with c2:
            turno = st.selectbox(
                "Turno:",
                ["Manhã", "Tarde", "Integral"],
                key='turno_articulacao'
            )
        
        acoes_resumo = st.text_area(
            "Trabalho Desenvolvido no AEE:",
            height=100,
            placeholder="Descreva as principais ações, estratégias e recursos utilizados no AEE...",
            key='acoes_articulacao'
        )
        
        if st.button("📄 Gerar Documento", type="primary", use_container_width=True):
            if not api_key:
                st.error("Insira a chave OpenAI na sidebar.")
            elif not acoes_resumo:
                st.warning("Por favor, descreva o trabalho desenvolvido no AEE.")
            else:
                with st.spinner("Gerando documento de articulação..."):
                    resultado = gerar_documento_articulacao(
                        api_key, aluno, f"{freq} ({turno})", acoes_resumo
                    )
                    if "Erro:" in resultado:
                        st.error(resultado)
                    else:
                        st.session_state.conteudo_documento_articulacao = resultado
                        st.session_state.status_documento_articulacao = 'revisao'
                        st.session_state.input_original_documento_articulacao = {
                            'freq': freq,
                            'turno': turno,
                            'acoes': acoes_resumo
                        }
                        st.success("Documento de articulação gerado!")
                        st.rerun()
    
    else:
        renderizar_hub_recurso(
            tipo_recurso='documento_articulacao',
            conteudo_gerado=st.session_state.conteudo_documento_articulacao,
            aluno_nome=aluno['nome']
        )
        
        if st.session_state.status_documento_articulacao == 'regerando':
            feedback = st.session_state.get('feedback_documento_articulacao', '')
            input_original = st.session_state.get('input_original_documento_articulacao', {})
            freq_original = input_original.get('freq', '1x/sem')
            turno_original = input_original.get('turno', 'Manhã')
            acoes_original = input_original.get('acoes', '')
            
            with st.spinner("Aplicando ajustes..."):
                resultado = gerar_documento_articulacao(
                    api_key, aluno, 
                    f"{freq_original} ({turno_original})", 
                    acoes_original, 
                    feedback
                )
                st.session_state.conteudo_documento_articulacao = resultado
                st.session_state.status_documento_articulacao = 'revisao'
                st.rerun()

with tab_planejamento:
    # ============================
    # HEADER TOP (mais clean)
    # ============================
    st.markdown(f"""
    <div class="timeline-header">
      <div>
        <div style="font-size:.78rem;color:#64748B;font-weight:800;letter-spacing:.08em;text-transform:uppercase;">
          Planejamento do Ciclo AEE
        </div>
        <div style="font-size:1.35rem;color:#0F172A;font-weight:900;margin-top:3px;">
          Culminação do PEI → Execução prática
        </div>
        <div style="font-size:.9rem;color:#64748B;margin-top:6px;">
          Gere, revise, salve e visualize ciclos diretamente do histórico do estudante.
        </div>
      </div>
      <div style="text-align:right;">
        <div style="font-size:.72rem;color:#94A3B8;font-weight:800;text-transform:uppercase;">Aluno</div>
        <div style="font-size:1.05rem;color:#0F172A;font-weight:900;">{aluno.get('nome','')}</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ============================
    # LAYOUT: 2 COLUNAS (painel + preview)
    # ============================
    col_left, col_right = st.columns([1.05, 1.35], gap="large")

    # ----------------------------
    # COLUNA ESQUERDA: HISTÓRICO + CONFIG
    # ----------------------------
    with col_left:
        st.markdown(f"### {icon_title('Histórico de ciclos (nuvem)', 'monitoramento', 20, '#A855F7')}", unsafe_allow_html=True)

        ciclos, ciclo_ativo_id = listar_ciclos_aluno(aluno["id"])
        ciclo_ativo = None
        if ciclo_ativo_id:
            ciclo_ativo = next((c for c in ciclos if c.get("ciclo_id") == ciclo_ativo_id), None)

        # Se existe ciclo ativo, mostra card
        if ciclo_ativo:
            ic, cor = _badge_status(ciclo_ativo.get("status"))
            cfg = ciclo_ativo.get("config_ciclo", {}) or {}
            st.markdown(f"""
            <div style="border:1px solid #E2E8F0;border-radius:14px;padding:14px 14px;margin-bottom:12px;background:#FFFFFF;">
              <div style="display:flex;align-items:center;justify-content:space-between;gap:10px;">
                <div style="font-weight:900;color:#0F172A;">{ic} Ciclo ativo</div>
                <div style="font-size:.75rem;font-weight:900;color:{cor};text-transform:uppercase;letter-spacing:.06em;">
                  {str(ciclo_ativo.get("status","rascunho")).upper()}
                </div>
              </div>
              <div style="margin-top:10px;color:#334155;font-size:.9rem;">
                <div><b>Foco:</b> {cfg.get("foco_principal","-")}</div>
                <div><b>Período:</b> {_fmt_data_iso(cfg.get("data_inicio"))} → {_fmt_data_iso(cfg.get("data_fim"))}</div>
                <div><b>Duração:</b> {cfg.get("duracao_semanas","-")} semanas</div>
              </div>
            </div>
            """, unsafe_allow_html=True)

        # Selecionar um ciclo para visualizar
        if ciclos:
            labels = []
            for c in ciclos:
                cfg = c.get("config_ciclo", {}) or {}
                ic, _ = _badge_status(c.get("status"))
                labels.append(
                    f"{ic} {cfg.get('foco_principal','Ciclo')} • {_fmt_data_iso(cfg.get('data_inicio'))} • v{c.get('versao',1)}"
                )
            idx_default = 0
            if ciclo_ativo_id:
                for i, c in enumerate(ciclos):
                    if c.get("ciclo_id") == ciclo_ativo_id:
                        idx_default = i
                        break

            escolha = st.selectbox(
                "Selecione um ciclo para visualizar:",
                options=list(range(len(ciclos))),
                format_func=lambda i: labels[i],
                index=idx_default,
                key="paee_ciclo_picker"
            )
            st.session_state["paee_ciclo_selecionado"] = ciclos[escolha]
        else:
            st.info("Ainda não há ciclos salvos para este estudante.")

        # Botão: marcar ciclo como ativo
        ciclo_sel = st.session_state.get("paee_ciclo_selecionado")
        if ciclo_sel and ciclo_sel.get("ciclo_id"):
            c_id = ciclo_sel["ciclo_id"]
            colA, colB = st.columns([1,1])
            with colA:
                if st.button("🟢 Definir como ciclo ativo", use_container_width=True, type="secondary"):
                    ok = definir_ciclo_ativo(aluno["id"], c_id, status="ativo")
                    if ok:
                        st.success("Ciclo definido como ativo.")
                        time.sleep(0.8)
                        st.rerun()
                    else:
                        st.error("Não consegui definir como ativo.")
            with colB:
                if st.button("🧹 Limpar seleção", use_container_width=True):
                    st.session_state.pop("paee_ciclo_selecionado", None)
                    st.rerun()

        st.markdown("---")

        # ============================
        # CONFIGURAÇÃO E GERAÇÃO (gera preview e só salva quando clicar)
        # ============================
        st.markdown(f"### {icon_title('Gerar novo ciclo (preview antes de salvar)', 'configurar', 20, '#A855F7')}", unsafe_allow_html=True)

        pei_data = carregar_pei_aluno(aluno["id"])
        metas_pei = extrair_metas_do_pei(pei_data)

        if not metas_pei:
            st.warning("Não encontrei metas no PEI. Gere/complete o PEI primeiro.")
        else:
            with st.expander("🎯 Selecionar metas do PEI", expanded=True):
                metas_selecionadas = []
                cols_m = st.columns(2)
                for i, meta in enumerate(metas_pei):
                    with cols_m[i % 2]:
                        sel = st.checkbox(
                            f"**{meta['tipo']}**",
                            value=meta.get("selecionada", True),
                            key=f"paee_meta_{meta['id']}"
                        )
                        st.caption(meta["descricao"])
                        if sel:
                            metas_selecionadas.append({
                                "id": meta["id"],
                                "tipo": meta["tipo"],
                                "descricao": meta["descricao"],
                                "prioridade": meta.get("prioridade", "media")
                            })

            recursos_disponiveis = {
                "diagnostico_barreiras": st.session_state.get("conteudo_diagnostico_barreiras", ""),
                "plano_habilidades": st.session_state.get("conteudo_plano_habilidades", ""),
                "tecnologia_assistiva": st.session_state.get("conteudo_tecnologia_assistiva", ""),
                "documento_articulacao": st.session_state.get("conteudo_documento_articulacao", ""),
            }
            recursos_nomes = {
                "diagnostico_barreiras": f"{get_icon('buscar', 18, '#A855F7')} Diagnóstico de Barreiras",
                "plano_habilidades": f"{get_icon('monitoramento', 18, '#A855F7')} Plano de Habilidades",
                "tecnologia_assistiva": f"{get_icon('configurar', 18, '#A855F7')} Tecnologia Assistiva",
                "documento_articulacao": f"{get_icon('dinamica', 18, '#A855F7')} Documento de Articulação",
            }
            recursos_com_conteudo = {k: v for k, v in recursos_disponiveis.items() if v and len(str(v)) > 120}

            with st.expander("🧩 Incorporar recursos (opcional)", expanded=False):
                recursos_selecionados = {}
                if recursos_com_conteudo:
                    for k, conteudo in recursos_com_conteudo.items():
                        marcado = st.checkbox(recursos_nomes.get(k, k), value=True, key=f"paee_rec_{k}")
                        if marcado:
                            resumo = str(conteudo)[:300] + ("..." if len(str(conteudo)) > 300 else "")
                            recursos_selecionados[k] = {
                                "resumo": resumo,
                                "completo": conteudo,
                                "data_incorporacao": datetime.now().isoformat()
                            }
                else:
                    st.caption("Nenhum recurso gerado nas abas anteriores ainda.")

            with st.form("config_ciclo_form_v2"):
                duracao = st.slider("Duração (semanas)", 4, 24, 12)
                freq = st.selectbox("Frequência do AEE", ["1x_semana","2x_semana","3x_semana","diario"], index=1)
                data_inicio = st.date_input("Data de início", value=date.today(), min_value=date.today())
                data_fim = st.date_input("Previsão de término", value=data_inicio + timedelta(weeks=duracao), min_value=data_inicio)
                foco_principal = st.text_input("Foco principal", value=aluno.get("hiperfoco") or "Desenvolvimento de habilidades específicas")
                descricao_ciclo = st.text_area("Descrição do ciclo", height=90)
                usar_ia = st.checkbox("🤖 Usar IA para cronograma", value=True)

                gerar = st.form_submit_button("✨ Gerar preview do planejamento", type="primary", use_container_width=True)

                if gerar:
                    if not metas_selecionadas:
                        st.error("Selecione pelo menos 1 meta.")
                    else:
                        ciclo_data = {
                            "ciclo_id": None,
                            "status": "rascunho",
                            "config_ciclo": {
                                "duracao_semanas": duracao,
                                "frequencia": freq,
                                "foco_principal": foco_principal,
                                "descricao": descricao_ciclo,
                                "data_inicio": data_inicio.isoformat(),
                                "data_fim": data_fim.isoformat(),
                                "metas_selecionadas": metas_selecionadas
                            },
                            "recursos_incorporados": recursos_selecionados if "recursos_selecionados" in locals() else {},
                            "criado_por": st.session_state.get("user_id", ""),
                            "versao": 1
                        }

                        if usar_ia and (api_key if "api_key" in globals() else None):
                            with st.spinner("🤖 IA planejando cronograma..."):
                                cronograma_ia = gerar_cronograma_inteligente(api_key, aluno, duracao, foco_principal, metas_selecionadas)
                                ciclo_data["cronograma"] = cronograma_ia or criar_cronograma_basico(duracao, metas_selecionadas)
                        else:
                            ciclo_data["cronograma"] = criar_cronograma_basico(duracao, metas_selecionadas)

                        st.session_state["ciclo_preview"] = ciclo_data
                        st.success("Preview gerado. Veja à direita e salve quando estiver pronto.")
                        st.rerun()

    # ----------------------------
    # COLUNA DIREITA: VISUALIZAÇÃO (ciclo selecionado OU preview)
    # ----------------------------
    with col_right:
        st.markdown(f"### {icon_title('Visualização do ciclo', 'visualizar', 20, '#A855F7')}", unsafe_allow_html=True)

        ciclo_preview = st.session_state.get("ciclo_preview")
        ciclo_sel = st.session_state.get("paee_ciclo_selecionado")

        # prioridade: preview (novo) -> selecionado (histórico) -> ativo
        ciclo_para_ver = ciclo_preview or ciclo_sel or ciclo_ativo

        if not ciclo_para_ver:
            st.info("Selecione um ciclo no histórico ou gere um preview.")
        else:
            cfg = (ciclo_para_ver.get("config_ciclo") or {})
            ic, cor = _badge_status(ciclo_para_ver.get("status"))

            st.markdown(f"""
            <div style="border:1px solid #E2E8F0;border-radius:16px;padding:16px;background:#FFFFFF;">
              <div style="display:flex;align-items:center;justify-content:space-between;">
                <div style="font-weight:900;color:#0F172A;font-size:1.05rem;">{ic} {cfg.get("foco_principal","Ciclo AEE")}</div>
                <div style="font-size:.75rem;font-weight:900;color:{cor};text-transform:uppercase;letter-spacing:.06em;">
                  {str(ciclo_para_ver.get("status","rascunho")).upper()}
                </div>
              </div>
              <div style="margin-top:8px;color:#334155;">
                <span style="font-weight:800;">Período:</span> {_fmt_data_iso(cfg.get("data_inicio"))} → {_fmt_data_iso(cfg.get("data_fim"))}
                &nbsp;•&nbsp;
                <span style="font-weight:800;">Duração:</span> {cfg.get("duracao_semanas","-")} sem
                &nbsp;•&nbsp;
                <span style="font-weight:800;">Freq:</span> {str(cfg.get("frequencia","-")).replace("_"," ").title()}
              </div>
            </div>
            """, unsafe_allow_html=True)

            # Metas
            with st.expander("🎯 Metas selecionadas", expanded=True):
                metas = cfg.get("metas_selecionadas") or []
                if metas:
                    for m in metas:
                        st.markdown(f"- **{m.get('tipo','')}**: {m.get('descricao','')}")
                else:
                    st.caption("Sem metas registradas.")

            # Recursos
            with st.expander("🧩 Recursos incorporados", expanded=False):
                recs = ciclo_para_ver.get("recursos_incorporados") or {}
                if recs:
                    for rid, d in recs.items():
                        nome = (rid or "").replace("_"," ").title()
                        st.markdown(f"**{nome}**")
                        st.caption(d.get("resumo",""))
                else:
                    st.caption("Nenhum recurso incorporado.")

            # Cronograma (fases + semanas)
            cron = ciclo_para_ver.get("cronograma") or {}
            with st.expander("🗓️ Cronograma", expanded=True):
                fases = cron.get("fases") or []
                semanas = cron.get("semanas") or []

                if fases:
                    st.markdown("**Fases**")
                    for f in fases:
                        st.markdown(f"- **{f.get('nome','Fase')}**: {f.get('objetivo_geral','')}")
                        st.caption(f.get("descricao",""))

                if semanas:
                    st.markdown("**Semanas (preview)**")
                    # mostra só as 6 primeiras para não ficar gigante
                    for w in semanas[:6]:
                        st.markdown(f"**Semana {w.get('numero')} — {w.get('tema','')}**")
                        st.caption(w.get("objetivo",""))
                        atv = w.get("atividades") or []
                        if atv:
                            st.markdown("• " + "\n• ".join(atv[:3]))
                        st.markdown("---")
                    if len(semanas) > 6:
                        st.info(f"Mostrando 6 de {len(semanas)} semanas.")

            # Botões (se for preview, salva na nuvem)
            if ciclo_preview:
                st.markdown(f"### {icon_title('Salvar este ciclo', 'salvar', 20, '#A855F7')}", unsafe_allow_html=True)
                c1, c2 = st.columns([1,1])
                with c1:
                    if st.button("💾 Salvar na nuvem (Supabase)", type="primary", use_container_width=True):
                        resultado = salvar_paee_ciclo(aluno["id"], ciclo_preview)
                        if resultado.get("sucesso"):
                            st.success(f"✅ Salvo! ID: {str(resultado.get('ciclo_id',''))[:8]}")
                            st.session_state.pop("ciclo_preview", None)
                            time.sleep(0.8)
                            st.rerun()
                        else:
                            st.error(f"❌ Erro ao salvar: {resultado.get('erro','')}")
                with c2:
                    if st.button("🧹 Descartar preview", use_container_width=True):
                        st.session_state.pop("ciclo_preview", None)
                        st.rerun()

# ==============================================================================
# RODAPÉ COM ASSINATURA
# ==============================================================================
ou.render_footer_assinatura()
