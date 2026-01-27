# omni_utils.py
import os
import base64
import requests
import streamlit as st
from streamlit_option_menu import option_menu

# =============================================================================
# 1) ESTADO E CONFIGURAÇÃO INICIAL
# =============================================================================
APP_VERSION = "omni_utils v2.5 (Layout colado: menu + hero bem perto)"

def ensure_state():
    if "autenticado" not in st.session_state:
        st.session_state.autenticado = False
    if "user" not in st.session_state:
        st.session_state.user = None
    if "workspace_id" not in st.session_state:
        st.session_state.workspace_id = None
    if "workspace_name" not in st.session_state:
        st.session_state.workspace_name = "Workspace"
    if "usuario_nome" not in st.session_state:
        st.session_state.usuario_nome = "Visitante"
    if "usuario_cargo" not in st.session_state:
        st.session_state.usuario_cargo = ""
    if "view" not in st.session_state:
        st.session_state.view = "login"

# =============================================================================
# 2) UI COMPONENTS (HEADER & NAVBAR) — PADRÃO ESTÁVEL
# =============================================================================
def get_base64_image(path: str) -> str | None:
    if not os.path.exists(path):
        return None
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

def _get_initials(nome: str) -> str:
    if not nome:
        return "U"
    parts = nome.strip().split()
    return f"{parts[0][0]}{parts[-1][0]}".upper() if len(parts) >= 2 else parts[0][:2].upper()

def _get_ws_short(max_len: int = 22) -> str:
    ws = st.session_state.get("workspace_name", "") or "Workspace"
    ws = str(ws).strip()
    return (ws[:max_len] + "...") if len(ws) > max_len else ws

def inject_layout_css(topbar_h: int = 56, navbar_h: int = 52, content_gap: int = 0):
    """
    CSS base do layout:
    - Topbar fixa
    - Navbar fixa
    - Espaço exato para navbar + conteúdo
    - NÃO mexe em inputs globalmente

    >>> content_gap controla o "respiro" entre a navbar e o primeiro conteúdo (HERO).
    >>> Deixei BEM PERTO: content_gap=2 (pode pôr 0 se quiser colar total).
    """
    st.markdown(
        f"""
<link href="https://cdn.jsdelivr.net/npm/remixicon@3.5.0/fonts/remixicon.css" rel="stylesheet">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800;900&display=swap" rel="stylesheet">

<style>
  :root {{
    --topbar-h: {topbar_h}px;
    --navbar-h: {navbar_h}px;
    --content-gap: {content_gap}px;
  }}

  /* Oculta chrome Streamlit (sem depender de classes internas) */
  #MainMenu {{ visibility: hidden; }}
  footer {{ visibility: hidden; }}
  header[data-testid="stHeader"] {{ display:none !important; }}
  [data-testid="stToolbar"] {{ display:none !important; }}
  section[data-testid="stSidebar"] {{ display:none !important; }}
  [data-testid="stSidebarNav"] {{ display:none !important; }}
  button[data-testid="collapsedControl"] {{ display:none !important; }}

  /* 🔥 CONTEÚDO: começa logo abaixo de topbar+navbar, com gap mínimo */
  .main .block-container {{
    padding-top: calc(var(--topbar-h) + var(--navbar-h) + var(--content-gap)) !important;
    padding-bottom: 2rem !important;
    padding-left: 2rem !important;
    padding-right: 2rem !important;
    max-width: 100% !important;
    font-family: 'Inter', sans-serif !important;
  }}

  /* (opcional) reduz margens padrão do primeiro elemento dentro do main */
  .main .block-container > div:first-child {{
    margin-top: 0 !important;
    padding-top: 0 !important;
  }}

  /* TOPBAR */
  .omni-topbar {{
    position: fixed !important;
    top: 0 !important; left: 0 !important; right: 0 !important;
    height: var(--topbar-h) !important;
    background: #ffffff !important;
    border-bottom: 1px solid #E2E8F0 !important;
    z-index: 999999 !important;
    display: flex !important;
    align-items: center !important;
    justify-content: space-between !important;
    padding: 0 24px !important;
    box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05) !important;
  }}
  .omni-brand {{
    display:flex !important;
    align-items:center !important;
    gap:12px !important;
    min-width: 0 !important;
  }}
  .omni-logo {{
    height: 32px !important;
    width: 32px !important;
    object-fit: contain !important;
  }}
  .omni-user-info {{
    display:flex !important;
    align-items:center !important;
    gap:12px !important;
  }}
  .omni-workspace {{
    background: #F8FAFC !important;
    border: 1px solid #E2E8F0 !important;
    padding: 5px 12px !important;
    border-radius: 10px !important;
    font-size: 12px !important;
    font-weight: 600 !important;
    color: #64748B !important;
    max-width: 220px !important;
    white-space: nowrap !important;
    overflow: hidden !important;
    text-overflow: ellipsis !important;
  }}
  .omni-avatar {{
    width: 32px !important; height: 32px !important;
    border-radius: 50% !important;
    background: linear-gradient(135deg, #3B82F6, #6366F1) !important;
    color: white !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    font-weight: 800 !important;
    font-size: 12px !important;
    box-shadow: 0 2px 4px rgba(59, 130, 246, 0.25) !important;
  }}

  /* NAVBAR WRAPPER (fixa abaixo da topbar) */
  .omni-navbar {{
    position: fixed !important;
    top: var(--topbar-h) !important;
    left: 0 !important;
    right: 0 !important;
    height: var(--navbar-h) !important;
    background: transparent !important;
    z-index: 999998 !important;
    display:flex !important;
    align-items:center !important;
    justify-content:center !important;
    pointer-events: none;
  }}
  .omni-navbar-inner {{
    width: min(1200px, calc(100% - 48px));
    pointer-events: auto;
  }}

  /* remove espaçamento fantasma do Streamlit no option_menu */
  .omni-navbar-inner .element-container {{
    margin: 0 !important;
    padding: 0 !important;
  }}

  /* Responsivo */
  @media (max-width: 900px) {{
    .main .block-container {{
      padding-left: 1rem !important;
      padding-right: 1rem !important;
    }}
    .omni-workspace {{ display:none !important; }}
  }}
</style>
        """,
        unsafe_allow_html=True,
    )

def inject_compact_app_css(accent: str = "#0D9488"):
    """
    CSS do app (páginas internas) para:
    - botões menores e consistentes
    - tabs compactas e bonitas
    IMPORTANTE: não altera inputs globalmente.
    """
    st.markdown(
        f"""
<style>
  /* =========================
     BOTÕES (compactos)
     ========================= */
  .stButton > button,
  .stDownloadButton > button {{
    border-radius: 10px !important;
    font-weight: 700 !important;
    font-size: 0.85rem !important;
    padding: 0.38rem 0.85rem !important;
    min-height: 36px !important;
    line-height: 1 !important;
    transition: transform .12s ease, box-shadow .12s ease, background .12s ease !important;
  }}

  /* Primary */
  .stButton > button[kind="primary"],
  .stDownloadButton > button[kind="primary"] {{
    background: linear-gradient(135deg, {accent}, #14B8A6) !important;
    border: none !important;
  }}
  .stButton > button[kind="primary"]:hover,
  .stDownloadButton > button[kind="primary"]:hover {{
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 16px rgba(13,148,136,.18) !important;
  }}

  /* Secondary */
  .stButton > button[kind="secondary"],
  .stDownloadButton > button[kind="secondary"] {{
    background: #ffffff !important;
    color: {accent} !important;
    border: 1px solid {accent} !important;
  }}
  .stButton > button[kind="secondary"]:hover,
  .stDownloadButton > button[kind="secondary"]:hover {{
    background: rgba(13,148,136,.06) !important;
  }}

  .stButton, .stDownloadButton {{
    margin: 0.15rem 0 !important;
  }}

  /* =========================
     TABS (compactas)
     ========================= */
  .stTabs [data-baseweb="tab-list"] {{
    gap: 2px !important;
    background: transparent !important;
    padding: 0 !important;
    border-bottom: 2px solid #E2E8F0 !important;
    flex-wrap: wrap !important;
    margin-top: 12px !important; /* mais colado */
  }}
  .stTabs [data-baseweb="tab"] {{
    height: 34px !important;
    padding: 0 16px !important;
    border-radius: 10px 10px 0 0 !important;
    font-size: 0.80rem !important;
    font-weight: 700 !important;
    letter-spacing: .3px !important;
    color: #64748B !important;
    border: none !important;
    background: transparent !important;
    position: relative !important;
  }}
  .stTabs [aria-selected="true"] {{
    color: {accent} !important;
  }}
  .stTabs [aria-selected="true"]::after {{
    content: '';
    position: absolute;
    bottom: -2px; left: 0; right: 0;
    height: 3px;
    background: {accent};
    border-radius: 3px 3px 0 0;
  }}
  .stTabs [data-baseweb="tab"]:hover:not([aria-selected="true"]) {{
    background: #F8FAFC !important;
    color: #475569 !important;
  }}

  .stDivider {{ margin: 0.75rem 0 !important; }}
</style>
        """,
        unsafe_allow_html=True,
    )

def render_omnisfera_header():
    """
    Topbar fixa (apenas render).
    O espaço do conteúdo é controlado por inject_layout_css().
    """
    ensure_state()

    TOPBAR_H = 56
    NAVBAR_H = 52

    # 🔥 BEM PERTO: content_gap=2 (se quiser mais ainda: 0)
    inject_layout_css(topbar_h=TOPBAR_H, navbar_h=NAVBAR_H, content_gap=2)

    icone = get_base64_image("omni_icone.png")
    texto = get_base64_image("omni_texto.png")

    ws_name = _get_ws_short()
    user_name = st.session_state.get("usuario_nome", "Visitante") or "Visitante"

    img_logo = (
        f'<img src="data:image/png;base64,{icone}" class="omni-logo">'
        if icone else
        '<div class="omni-logo">🌐</div>'
    )

    img_text = (
        f'<img src="data:image/png;base64,{texto}" style="height:18px;">'
        if texto else
        '<span style="font-weight:900;color:#0F172A;font-size:15px;letter-spacing:0.05em;">OMNISFERA</span>'
    )

    st.markdown(
        f"""
<div class="omni-topbar">
  <div class="omni-brand">
    {img_logo}
    {img_text}
  </div>
  <div class="omni-user-info">
    <div class="omni-workspace" title="{ws_name}">{ws_name}</div>
    <div class="omni-avatar" title="{user_name}">{_get_initials(user_name)}</div>
  </div>
</div>
        """,
        unsafe_allow_html=True,
    )

def render_navbar(active_tab: str = "Início"):
    """
    Navbar horizontal FIXA (abaixo da topbar), sem margin negativa.
    """
    ensure_state()

    opcoes = [
        "Início",
        "Estudantes",
        "Estratégias & PEI",
        "Plano de Ação (AEE)",
        "Hub de Recursos",
        "Diário de Bordo",
        "Evolução & Dados",
    ]
    icones = ["house", "people", "book", "puzzle", "rocket", "journal", "bar-chart"]

    try:
        default_idx = opcoes.index(active_tab)
    except ValueError:
        default_idx = 0

    st.markdown('<div class="omni-navbar"><div class="omni-navbar-inner">', unsafe_allow_html=True)

    selected = option_menu(
        menu_title=None,
        options=opcoes,
        icons=icones,
        default_index=default_idx,
        orientation="horizontal",
        styles={
            "container": {
                "padding": "6px 6px",
                "margin": "0px",
                "background-color": "#ffffff",
                "border": "1px solid #E2E8F0",
                "border-radius": "14px",
                "box-shadow": "0 1px 2px rgba(0,0,0,0.03)",
            },
            "icon": {"color": "#64748B", "font-size": "15px"},
            "nav-link": {
                "font-size": "12px",
                "text-align": "center",
                "margin": "0px",
                "padding": "8px 10px",
                "--hover-color": "#F8FAFC",
                "color": "#64748B",
                "white-space": "nowrap",
                "border-radius": "10px",
                "min-height": "38px",
                "display": "flex",
                "align-items": "center",
                "justify-content": "center",
                "border": "1px solid transparent",
                "gap": "6px",
            },
            "nav-link-selected": {
                "background-color": "#F1F5F9",
                "color": "#0F172A",
                "font-weight": "700",
                "border": "1px solid #E2E8F0",
            },
        },
    )

    st.markdown("</div></div>", unsafe_allow_html=True)

    if selected != active_tab:
        routes = {
            "Início": "pages/0_Home.py" if os.path.exists("pages/0_Home.py") else "Home.py",
            "Estudantes": "pages/Alunos.py",
            "Estratégias & PEI": "pages/1_PEI.py",
            "Plano de Ação (AEE)": "pages/2_PAE.py",
            "Hub de Recursos": "pages/3_Hub_Inclusao.py",
            "Diário de Bordo": "pages/4_Diario_de_Bordo.py",
            "Evolução & Dados": "pages/5_Monitoramento_Avaliacao.py",
        }
        target = routes.get(selected)
        if target:
            if selected == "Início" and not os.path.exists(target):
                target = "Home.py"
            st.switch_page(target)

# =============================================================================
# 3) SUPABASE & UTILS (LÓGICA PRESERVADA)
# =============================================================================
def _sb_url() -> str:
    url = str(st.secrets.get("SUPABASE_URL", "")).strip()
    if not url:
        raise RuntimeError("SUPABASE_URL não encontrado nos secrets.")
    return url.rstrip("/")

def _sb_key() -> str:
    key = str(st.secrets.get("SUPABASE_SERVICE_KEY", "")).strip()
    if not key:
        key = str(st.secrets.get("SUPABASE_ANON_KEY", "")).strip()
    if not key:
        raise RuntimeError("Key não encontrada.")
    return key

def _headers() -> dict:
    key = _sb_key()
    return {"apikey": key, "Authorization": f"Bearer {key}", "Content-Type": "application/json"}

def supabase_rpc(fn_name: str, payload: dict):
    url = f"{_sb_url()}/rest/v1/rpc/{fn_name}"
    r = requests.post(url, headers=_headers(), json=payload, timeout=20)
    if r.status_code >= 400:
        raise RuntimeError(f"RPC {fn_name} erro: {r.status_code} {r.text}")
    return r.json()

def supabase_insert(table: str, row: dict):
    url = f"{_sb_url()}/rest/v1/{table}"
    h = _headers()
    h["Prefer"] = "return=representation"
    r = requests.post(url, headers=h, json=row, timeout=20)
    if r.status_code >= 400:
        raise RuntimeError(f"Insert {table} erro: {r.status_code} {r.text}")
    return r.json()

def supabase_upsert(table: str, row: dict, on_conflict: str):
    url = f"{_sb_url()}/rest/v1/{table}?on_conflict={on_conflict}"
    h = _headers()
    h["Prefer"] = "resolution=merge-duplicates,return=representation"
    r = requests.post(url, headers=h, json=row, timeout=20)
    if r.status_code >= 400:
        raise RuntimeError(f"Upsert {table} erro: {r.status_code} {r.text}")
    data = r.json()
    return data[0] if isinstance(data, list) and data else (data if isinstance(data, dict) else None)

def supabase_workspace_from_pin(pin: str) -> str | None:
    pin = (pin or "").strip()
    if not pin:
        return None

    for p in ({"pin": pin}, {"p_pin": pin}, {"pincode": pin}):
        try:
            data = supabase_rpc("workspace_from_pin", p)
            if isinstance(data, dict) and data.get("workspace_id"):
                return data["workspace_id"]
            if isinstance(data, list) and data and isinstance(data[0], dict) and data[0].get("workspace_id"):
                return data[0]["workspace_id"]
        except Exception:
            continue
    return None

def supabase_log_access(workspace_id: str, nome: str, cargo: str, event: str, app_version: str = ""):
    try:
        ua = st.context.headers.get("User-Agent", "")[:500]
    except Exception:
        ua = ""
    row = {
        "workspace_id": workspace_id,
        "nome": (nome or "").strip(),
        "cargo": (cargo or "").strip(),
        "event": (event or "").strip(),
        "user_agent": ua,
        "app_version": (app_version or "").strip(),
    }
    return supabase_insert("access_logs", row)

def supa_save_pei(student_id: str, dados: dict, pdf_text: str = ""):
    if not student_id or not st.session_state.get("workspace_id"):
        raise RuntimeError("Dados incompletos.")
    row = {
        "student_id": student_id,
        "workspace_id": st.session_state.workspace_id,
        "pei_json": dados if isinstance(dados, dict) else {},
        "pdf_text": pdf_text or "",
    }
    return supabase_upsert("peis", row, on_conflict="student_id")

# =============================================================================
# 4) CSS PADRONIZADO DO HERO CARD (TODAS AS PÁGINAS)
# =============================================================================
def inject_hero_card_css():
    """
    CSS padronizado para o card hero em todas as páginas.
    Garante distância consistente do menu e altura fixa do hero.
    """
    st.markdown(
        """
<style>
/* ===============================
   PADRONIZAÇÃO: DISTÂNCIA MENU → HERO
================================ */
.block-container {
    padding-top: 0.3rem !important;
}

/* ===============================
   PADRONIZAÇÃO: HERO CARD
================================ */
.mod-card-wrapper {
    margin-top: 0 !important;
    margin-bottom: 20px !important;
    display: flex;
    flex-direction: column;
    border-radius: 16px;
    overflow: hidden;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.02);
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
    height: 130px !important;  /* 🔒 ALTURA FIXA PADRONIZADA */
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
    background: transparent !important;
    border-right: 1px solid #F1F5F9;
    transition: all 0.3s ease;
}

.mod-card-rect:hover .mod-icon-area {
    transform: scale(1.05);
}

.mod-content {
    flex-grow: 1;
    padding: 0 24px;
    display: flex;
    flex-direction: column;
    justify-content: center;
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
    color: #4F46E5;
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

/* Responsividade */
@media (max-width: 768px) {
    .mod-card-rect {
        height: auto !important;
        flex-direction: column;
        padding: 16px;
    }
    .mod-bar {
        width: 100%;
        height: 4px;
    }
    .mod-icon-area {
        width: 100%;
        height: 50px;
        border-right: none;
        border-bottom: 1px solid #F1F5F9;
    }
}
</style>
        """,
        unsafe_allow_html=True,
    )

def inject_hero_card_colors():
    """
    Injeta as classes de cores dos hero cards (mesmas da Home).
    Cada página deve usar sua cor específica no hero card.
    """
    st.markdown(
        """
<style>
/* ===============================
   CORES DOS CARDS DE MÓDULO (MESMAS DA HOME)
================================ */
.c-indigo { background: #4F46E5 !important; }
.bg-indigo-soft { 
    background: #EEF2FF !important; 
    color: #4F46E5 !important;
}

.c-blue { background: #3B82F6 !important; }
.bg-blue-soft { 
    background: #EFF6FF !important;
    color: #2563EB !important;
}

.c-purple { background: #8B5CF6 !important; }
.bg-purple-soft { 
    background: #F5F3FF !important;
    color: #7C3AED !important;
}

.c-teal { background: #14B8A6 !important; }
.bg-teal-soft { 
    background: #F0FDFA !important;
    color: #0D9488 !important;
}

.c-rose { background: #E11D48 !important; }
.bg-rose-soft { 
    background: #FFF1F2 !important;
    color: #BE123C !important;
}

.c-sky { background: #0284C7 !important; }
.bg-sky-soft { 
    background: #F0F9FF !important;
    color: #0369A1 !important;
}

/* ===============================
   MOVIMENTO DO HERO CARD (IGUAL À HOME)
================================ */
.mod-card-rect {
    transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
}

.mod-card-rect:hover {
    transform: translateY(-4px) !important;
    box-shadow: 0 12px 24px rgba(0, 0, 0, 0.08) !important;
    border-color: #CBD5E1 !important;
}

.mod-icon-area {
    background: #FAFAFA !important;
    transition: all 0.3s ease !important;
}

.mod-card-rect:hover .mod-icon-area {
    background: white !important;
    transform: scale(1.05) !important;
}

.mod-card-rect:hover .mod-title {
    color: #4F46E5 !important;
}
</style>
        """,
        unsafe_allow_html=True,
    )

def inject_unified_ui_css():
    """
    CSS padronizado para toda a UI: abas (pílulas), botões, selects, checkboxes, radio, tags, multiselect, slider.
    Usa cor neutra (#64748B - slate-500) que funciona com todas as cores dos cards da Home.
    """
    st.markdown(
        """
<style>
:root {
    --ui-neutral: #64748B;        /* slate-500 - cor neutra principal */
    --ui-neutral-dark: #475569;   /* slate-600 - mais escuro */
    --ui-neutral-light: #94A3B8;  /* slate-400 - mais claro */
    --ui-neutral-soft: #F1F5F9;   /* slate-100 - fundo suave */
    --ui-neutral-border: #E2E8F0; /* slate-200 - bordas */
}

/* ===============================
   TABS - PÍLULAS PADRONIZADAS
================================ */
div[data-baseweb="tab-border"],
div[data-baseweb="tab-highlight"] { 
    display: none !important; 
}

.stTabs [data-baseweb="tab-list"] {
    display: flex;
    flex-wrap: wrap !important;
    gap: 6px;
    padding: 3px 3px;
    width: 100%;
    margin-top: 0px !important;
    margin-bottom: 0.15rem !important;
    border-bottom: none !important;
}

.stTabs [data-baseweb="tab"] {
    height: 38px !important;
    border-radius: 20px !important;  /* PÍLULAS - estilo PEI */
    background-color: #FFFFFF !important;
    border: 1px solid var(--ui-neutral-border) !important;
    color: var(--ui-neutral) !important;
    font-weight: 700 !important;
    font-size: 0.75rem !important;
    padding: 0 18px !important;
    box-shadow: 0 1px 2px rgba(0,0,0,0.03) !important;
    text-transform: uppercase !important;
    letter-spacing: 0.5px !important;
    transition: all 0.2s ease !important;
}

.stTabs [data-baseweb="tab"]:hover:not([aria-selected="true"]) { 
    border-color: var(--ui-neutral-light) !important; 
    color: var(--ui-neutral-dark) !important; 
    background-color: var(--ui-neutral-soft) !important; 
}

.stTabs [aria-selected="true"] {
    background-color: var(--ui-neutral-soft) !important; 
    color: var(--ui-neutral-dark) !important;
    border: 1px solid var(--ui-neutral) !important; 
    font-weight: 800 !important;
    box-shadow: 0 2px 4px rgba(100,116,139,0.15) !important;
}

/* ===============================
   BOTÕES - COR NEUTRA
================================ */
.stButton > button {
    border-radius: 10px !important;
    font-weight: 700 !important;
    transition: all 0.18s ease !important;
}

.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, var(--ui-neutral), var(--ui-neutral-dark)) !important;
    border: none !important;
    color: #ffffff !important;
}

.stButton > button[kind="primary"]:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 10px 22px rgba(100,116,139,0.25) !important;
    background: linear-gradient(135deg, var(--ui-neutral-dark), var(--ui-neutral)) !important;
}

.stButton > button[kind="secondary"] {
    background: #ffffff !important;
    color: var(--ui-neutral-dark) !important;
    border: 1px solid var(--ui-neutral-border) !important;
}

.stButton > button[kind="secondary"]:hover {
    background: var(--ui-neutral-soft) !important;
    border-color: var(--ui-neutral) !important;
    color: var(--ui-neutral-dark) !important;
}

/* ===============================
   SELECTS / DROPDOWNS
================================ */
div[data-baseweb="select"] > div {
    border-radius: 8px !important;
    border-color: var(--ui-neutral-border) !important;
}

div[data-baseweb="select"] > div:focus-within {
    border-color: var(--ui-neutral) !important;
    box-shadow: 0 0 0 3px rgba(100,116,139,0.18) !important;
}

/* ===============================
   MULTISELECT
================================ */
div[data-baseweb="select"][aria-multiselectable="true"] > div {
    border-radius: 8px !important;
    border-color: var(--ui-neutral-border) !important;
}

div[data-baseweb="select"][aria-multiselectable="true"] > div:focus-within {
    border-color: var(--ui-neutral) !important;
    box-shadow: 0 0 0 3px rgba(100,116,139,0.18) !important;
}

/* ===============================
   SLIDER
================================ */
.stSlider {
    border-radius: 8px !important;
}

/* Track do slider */
.stSlider > div > div[data-baseweb="slider"] > div[data-baseweb="slider-track"] {
    background-color: var(--ui-neutral-border) !important;
}

/* Fill do slider (parte preenchida) */
.stSlider > div > div[data-baseweb="slider"] > div[data-baseweb="slider-track"] > div[data-baseweb="slider-fill"] {
    background: linear-gradient(135deg, var(--ui-neutral), var(--ui-neutral-dark)) !important;
}

/* Thumb do slider (bolinha) */
.stSlider > div > div[data-baseweb="slider"] > div[data-baseweb="slider-thumb"] {
    background-color: var(--ui-neutral) !important;
    border-color: var(--ui-neutral) !important;
}

.stSlider > div > div[data-baseweb="slider"] > div[data-baseweb="slider-thumb"]:hover {
    background-color: var(--ui-neutral-dark) !important;
    border-color: var(--ui-neutral-dark) !important;
}

/* Fallback para estrutura alternativa do slider */
.stSlider div[data-baseweb="slider-thumb"] {
    background-color: var(--ui-neutral) !important;
    border-color: var(--ui-neutral) !important;
}

.stSlider div[data-baseweb="slider-fill"] {
    background: linear-gradient(135deg, var(--ui-neutral), var(--ui-neutral-dark)) !important;
}

/* ===============================
   CHECKBOX
================================ */
div[role="checkbox"] {
    border-radius: 4px !important;
    border-color: var(--ui-neutral-border) !important;
}

div[role="checkbox"][aria-checked="true"] {
    background-color: var(--ui-neutral) !important;
    border-color: var(--ui-neutral) !important;
}

div[role="checkbox"]:hover {
    border-color: var(--ui-neutral) !important;
}

div[role="checkbox"][aria-checked="true"]:hover {
    background-color: var(--ui-neutral-dark) !important;
    border-color: var(--ui-neutral-dark) !important;
}

/* ===============================
   RADIO
================================ */
div[role="radio"] {
    border-color: var(--ui-neutral-border) !important;
}

div[role="radio"][aria-checked="true"] {
    background-color: var(--ui-neutral) !important;
    border-color: var(--ui-neutral) !important;
}

div[role="radio"]:hover {
    border-color: var(--ui-neutral) !important;
}

div[role="radio"][aria-checked="true"]:hover {
    background-color: var(--ui-neutral-dark) !important;
    border-color: var(--ui-neutral-dark) !important;
}

/* ===============================
   INPUTS / TEXTAREAS
================================ */
.stTextInput input,
.stTextArea textarea {
    border-radius: 8px !important;
    border-color: var(--ui-neutral-border) !important;
}

.stTextInput input:focus,
.stTextArea textarea:focus {
    border-color: var(--ui-neutral) !important;
    box-shadow: 0 0 0 3px rgba(100,116,139,0.18) !important;
}

/* ===============================
   MULTISELECT TAGS / CHIPS
================================ */
div[data-baseweb="tag"] {
    background: var(--ui-neutral-soft) !important;
    border: 1px solid var(--ui-neutral-border) !important;
    border-radius: 6px !important;
}

div[data-baseweb="tag"] span {
    color: var(--ui-neutral-dark) !important;
    font-weight: 700 !important;
}

/* ===============================
   FOCUS RING (remove vermelho)
================================ */
*:focus,
*:focus-visible {
    outline: none !important;
}

/* ===============================
   DIVIDERS
================================ */
hr {
    border-color: var(--ui-neutral-border) !important;
}

/* ===============================
   RESPONSIVIDADE
================================ */
@media (max-width: 768px) {
    .stTabs [data-baseweb="tab"] {
        font-size: 0.7rem !important;
        padding: 0 14px !important;
        height: 36px !important;
    }
}
</style>
        """,
        unsafe_allow_html=True,
    )

# =============================================================================
# 5) CSS DO LOGIN (ESCOPADO) — NÃO AFETA O APP TODO
# =============================================================================
def inject_base_css():
    """
    CSS do login / telas iniciais.
    IMPORTANTE: fica escopado em .omni-login para não “gordar” inputs no app inteiro.
    """
    st.markdown(
        """
<style>
  .omni-login .login-box {
    background: white;
    border-radius: 24px;
    padding: 40px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.05);
    text-align: center;
    border: 1px solid #E2E8F0;
    max-width: 650px;
    margin: 30px auto;
    font-family: 'Inter', sans-serif;
  }

  /* INPUTS SOMENTE NO LOGIN */
  .omni-login .stTextInput input,
  .omni-login .stTextArea textarea,
  .omni-login div[data-baseweb="select"] {
    border-radius: 12px !important;
  }
  .omni-login .stTextInput input { height: 44px !important; }
</style>
        """,
        unsafe_allow_html=True,
    )
