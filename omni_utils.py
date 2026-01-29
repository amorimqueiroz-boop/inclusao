# omni_utils.py
import os
import base64
import requests
import streamlit as st

# =============================================================================
# 0) BIBLIOTECA DE ÍCONES FLAT (REMIXICON) - SISTEMA CENTRALIZADO
# =============================================================================
ICON_LIBRARY = {
    # Módulos Principais
    "estudantes": {"icon": "ri-user-star-line", "color": "#2563EB"},
    "pei": {"icon": "ri-book-open-line", "color": "#0EA5E9"},
    "pae": {"icon": "ri-puzzle-line", "color": "#A855F7"},
    "hub": {"icon": "ri-rocket-line", "color": "#06B6D4"},
    "diario": {"icon": "ri-edit-box-line", "color": "#F43F5E"},
    "monitoramento": {"icon": "ri-line-chart-line", "color": "#0C4A6E"},
    
    # Central de Conhecimento - Abas
    "panorama": {"icon": "ri-bar-chart-box-line", "color": "#2563EB"},
    "legislacao": {"icon": "ri-scales-3-line", "color": "#2563EB"},
    "glossario": {"icon": "ri-book-2-line", "color": "#2563EB"},
    "linguagem": {"icon": "ri-chat-3-line", "color": "#2563EB"},
    "biblioteca": {"icon": "ri-library-line", "color": "#2563EB"},
    "manual": {"icon": "ri-book-mark-line", "color": "#2563EB"},
    
    # Ações e Estados
    "fluxo": {"icon": "ri-flow-chart", "color": "#2563EB"},
    "filosofia": {"icon": "ri-heart-line", "color": "#2563EB"},
    "justica": {"icon": "ri-scales-line", "color": "#2563EB"},
    "buscar": {"icon": "ri-search-line", "color": "#64748B"},
    "preferir": {"icon": "ri-checkbox-circle-line", "color": "#16A34A"},
    "evitar": {"icon": "ri-close-circle-line", "color": "#DC2626"},
    "legislacao_doc": {"icon": "ri-government-line", "color": "#2563EB"},
    "pedagogia": {"icon": "ri-brain-line", "color": "#2563EB"},
    "livro": {"icon": "ri-book-line", "color": "#2563EB"},
    
    # Hub de Inclusão
    "adaptar_prova": {"icon": "ri-file-edit-line", "color": "#06B6D4"},
    "adaptar_atividade": {"icon": "ri-scissors-cut-line", "color": "#06B6D4"},
    "criar_zero": {"icon": "ri-magic-line", "color": "#06B6D4"},
    "estudio_visual": {"icon": "ri-image-edit-line", "color": "#06B6D4"},
    "roteiro": {"icon": "ri-file-list-3-line", "color": "#06B6D4"},
    "papo_mestre": {"icon": "ri-chat-smile-2-line", "color": "#06B6D4"},
    "dinamica": {"icon": "ri-group-line", "color": "#06B6D4"},
    "plano_aula": {"icon": "ri-calendar-todo-line", "color": "#06B6D4"},
    
    # Educação Infantil
    "experiencia": {"icon": "ri-lightbulb-line", "color": "#06B6D4"},
    "rotina": {"icon": "ri-time-line", "color": "#06B6D4"},
    "brincar": {"icon": "ri-gamepad-line", "color": "#06B6D4"},
    
    # Ações Comuns
    "salvar": {"icon": "ri-save-line", "color": "#2563EB"},
    "editar": {"icon": "ri-edit-line", "color": "#2563EB"},
    "deletar": {"icon": "ri-delete-bin-line", "color": "#DC2626"},
    "adicionar": {"icon": "ri-add-circle-line", "color": "#16A34A"},
    "validar": {"icon": "ri-checkbox-circle-line", "color": "#16A34A"},
    "cancelar": {"icon": "ri-close-circle-line", "color": "#DC2626"},
    "download": {"icon": "ri-download-line", "color": "#2563EB"},
    "upload": {"icon": "ri-upload-line", "color": "#2563EB"},
    "visualizar": {"icon": "ri-eye-line", "color": "#2563EB"},
    "configurar": {"icon": "ri-settings-3-line", "color": "#64748B"},
    "info": {"icon": "ri-information-line", "color": "#2563EB"},
    "aviso": {"icon": "ri-alert-line", "color": "#F59E0B"},
    "erro": {"icon": "ri-error-warning-line", "color": "#DC2626"},
    "sucesso": {"icon": "ri-check-line", "color": "#16A34A"},
}

def get_icon(key: str, size: int = 20, color: str = None) -> str:
    """
    Retorna HTML do ícone RemixIcon com cor personalizada.
    
    Args:
        key: Chave do ícone na biblioteca
        size: Tamanho em pixels (padrão 20)
        color: Cor personalizada (sobrescreve a cor padrão)
    
    Returns:
        String HTML com o ícone
    """
    icon_data = ICON_LIBRARY.get(key.lower(), {"icon": "ri-question-line", "color": "#64748B"})
    icon_class = icon_data["icon"]
    icon_color = color or icon_data["color"]
    
    return f'<i class="{icon_class}" style="font-size: {size}px; color: {icon_color}; vertical-align: middle;"></i>'

def icon_title(text: str, icon_key: str, size: int = 24, color: str = None) -> str:
    """
    Cria um título com ícone integrado.
    
    Args:
        text: Texto do título
        icon_key: Chave do ícone na biblioteca
        size: Tamanho do ícone
        color: Cor personalizada
    
    Returns:
        String HTML formatada
    """
    icon_html = get_icon(icon_key, size, color)
    return f'{icon_html} <span style="vertical-align: middle;">{text}</span>'

# =============================================================================
# 1) ESTADO E CONFIGURAÇÃO INICIAL
# =============================================================================
APP_VERSION = "omni_utils v2.5 (Layout colado: menu + hero bem perto)"

def get_setting(name: str, default: str = "") -> str:
    """
    Getter multi-plataforma:
    - Render/containers: usa os.environ
    - Streamlit Cloud: usa st.secrets
    Importante: em ambientes sem secrets.toml (ex.: Render), acessar st.secrets pode levantar
    StreamlitSecretNotFoundError, então fazemos try/except.
    """
    v = os.environ.get(name)
    if v is not None and str(v).strip() != "":
        return str(v).strip()
    try:
        v2 = st.secrets.get(name, default)
        return str(v2).strip() if v2 is not None else default
    except Exception:
        return default

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
  button[data-testid="collapsedControl"] {{ display:none !important; }}

  /* 🔥 CONTEÚDO: começa logo abaixo de topbar+navbar, com gap mínimo */
  /* Nota: padding-top será sobrescrito por forcar_layout_hub() nas páginas */
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

  /* NAVBAR WRAPPER */
  .omni-navbar {{
    position: relative !important;
    height: var(--navbar-h) !important;
    background: transparent !important;
    z-index: 999998 !important;
    display:flex !important;
    align-items:center !important;
    justify-content:center !important;
    pointer-events: none;
    padding: 0px 0 !important; /* SEM espaço entre topbar e navbar */
    margin-bottom: 0px !important;
    margin-top: 0px !important;
  }}
  
  /* Remove espaçamento após navbar */
  .omni-navbar + *,
  .omni-navbar ~ * {{
    margin-top: 0px !important;
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
  
  /* Remove espaçamento após navbar no Streamlit */
  .omni-navbar .stMarkdownContainer,
  .omni-navbar + .element-container,
  .omni-navbar ~ .element-container {{
    margin-top: 0px !important;
    margin-bottom: 0px !important;
    padding-top: 0px !important;
    padding-bottom: 0px !important;
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
    background: linear-gradient(135deg, #2563EB 0%, #0EA5E9 100%) !important;
    border: none !important;
  }}
  .stButton > button[kind="primary"]:hover,
  .stDownloadButton > button[kind="primary"]:hover {{
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 16px rgba(37, 99, 235, 0.3) !important;
    background: linear-gradient(135deg, #0EA5E9 0%, #2563EB 100%) !important;
  }}

  /* Secondary */
  .stButton > button[kind="secondary"],
  .stDownloadButton > button[kind="secondary"] {{
    background: #ffffff !important;
    color: #2563EB !important;
    border: 1px solid #2563EB !important;
  }}
  .stButton > button[kind="secondary"]:hover,
  .stDownloadButton > button[kind="secondary"]:hover {{
    background: rgba(37, 99, 235, 0.06) !important;
    border-color: #0EA5E9 !important;
    color: #0EA5E9 !important;
  }}

  .stButton, .stDownloadButton {{
    margin: 0.15rem 0 !important;
  }}

  /* =========================
     TABS (compactas)
     ========================= */
  .stTabs [data-baseweb="tab-list"] {{
    gap: 6px !important;
    background: transparent !important;
    padding: 3px 3px !important;
    border-bottom: none !important; /* Remove linha embaixo */
    flex-wrap: wrap !important;
    margin-top: 8px !important;
    justify-content: center !important; /* Centraliza as abas */
  }}
  .stTabs [data-baseweb="tab"] {{
    height: 38px !important;
    padding: 0 18px !important;
    border-radius: 20px !important; /* Pílulas arredondadas */
    font-size: 0.75rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.5px !important;
    color: #64748B !important;
    border: 1px solid #E2E8F0 !important;
    background: #FFFFFF !important;
    position: relative !important;
    text-transform: uppercase !important;
  }}
  .stTabs [aria-selected="true"] {{
    color: {accent} !important;
    background-color: rgba(13,148,136,0.1) !important;
    border: 1px solid {accent} !important;
  }}
  /* Traço embaixo removido - não fica bonito */
  .stTabs [aria-selected="true"]::after {{
    display: none !important;
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

def render_omnisfera_header(active_tab: str = "Início"):
    """
    Versão Render 2026: Header fixo e compacto com botões de navegação inteligentes.
    Usa st.button + st.switch_page (100% Render-safe, sem HTML/JS injection).
    """
    ensure_state()
    
    HEADER_HEIGHT = 65
    
    # Injeta CSS de Layout
    st.markdown(f"""
        <style>
            /* Remove header padrão do Streamlit */
            [data-testid="stHeader"] {{ display:none !important; }}
            
            /* Ajusta padding-top do conteúdo */
            .main .block-container {{
                padding-top: {HEADER_HEIGHT + 10}px !important;
                max-width: 95% !important;
            }}
            
            /* Header Container Fixo */
            .omni-nav-bar {{
                position: fixed !important;
                top: 0 !important;
                left: 0 !important;
                right: 0 !important;
                height: {HEADER_HEIGHT}px !important;
                background: #FFFFFF !important;
                border-bottom: 1px solid #E2E8F0 !important;
                display: flex !important;
                align-items: center !important;
                justify-content: space-between !important;
                padding: 0 30px !important;
                z-index: 1000 !important;
                box-shadow: 0 2px 10px rgba(0,0,0,0.03) !important;
            }}

            .nav-group {{
                display: flex !important;
                align-items: center !important;
                gap: 10px !important;
            }}
            
            /* Estilização dos botões Streamlit como Pills */
            .omni-nav-bar button[data-testid="baseButton-secondary"],
            .omni-nav-bar button[data-testid="baseButton-primary"] {{
                padding: 6px 14px !important;
                border-radius: 20px !important;
                font-size: 12px !important;
                font-weight: 600 !important;
                border: 1px solid #E2E8F0 !important;
                transition: all 0.2s ease !important;
                height: auto !important;
                min-height: 32px !important;
            }}
            
            .omni-nav-bar button[data-testid="baseButton-secondary"] {{
                background: rgba(255,255,255,0.9) !important;
                color: #64748B !important;
            }}
            
            .omni-nav-bar button[data-testid="baseButton-secondary"]:hover {{
                background: #F1F5F9 !important;
                color: #1E293B !important;
                border-color: #CBD5E1 !important;
                transform: translateY(-1px) !important;
                box-shadow: 0 2px 6px rgba(0,0,0,0.08) !important;
            }}

            .omni-nav-bar button[data-testid="baseButton-primary"] {{
                background: #EFF6FF !important;
                color: #2563EB !important;
                border: 1px solid #BFDBFE !important;
                font-weight: 800 !important;
                box-shadow: 0 2px 8px rgba(37,99,235,0.15) !important;
            }}
            
            .omni-nav-bar button[data-testid="baseButton-primary"]:hover {{
                background: #DBEAFE !important;
                border-color: #93C5FD !important;
                transform: translateY(-1px) !important;
                box-shadow: 0 4px 12px rgba(37,99,235,0.2) !important;
            }}
            
            /* Avatar do usuário */
            .omni-avatar {{
                width: 36px !important;
                height: 36px !important;
                border-radius: 50% !important;
                background: linear-gradient(135deg, #3B82F6, #6366F1) !important;
                color: white !important;
                display: flex !important;
                align-items: center !important;
                justify-content: center !important;
                font-weight: 800 !important;
                font-size: 13px !important;
                box-shadow: 0 2px 4px rgba(59, 130, 246, 0.25) !important;
            }}
        </style>
    """, unsafe_allow_html=True)

    # Imagens Base64
    icone_b64 = get_base64_image("omni_icone.png") or ""
    texto_b64 = get_base64_image("omni_texto.png") or ""
    
    # Configuração dos botões (mesmos ícones dos cards)
    nav_items = [
        {"key": "Início", "label": "🏠 Início", "page": "pages/0_Home.py" if os.path.exists("pages/0_Home.py") else "Home.py"},
        {"key": "Estudantes", "label": "👥 Estudantes", "page": "pages/Alunos.py"},
        {"key": "Estratégias & PEI", "label": "📘 PEI", "page": "pages/1_PEI.py"},
        {"key": "Plano de Ação (AEE)", "label": "🧩 PAE", "page": "pages/2_PAE.py"},
        {"key": "Hub de Recursos", "label": "🚀 Hub", "page": "pages/3_Hub_Inclusao.py"},
        {"key": "Diário de Bordo", "label": "📝 Diário", "page": "pages/4_Diario_de_Bordo.py"},
        {"key": "Evolução & Dados", "label": "📊 Dados", "page": "pages/5_Monitoramento_Avaliacao.py"},
    ]

    # Renderização do Header
    st.markdown('<div class="omni-nav-bar">', unsafe_allow_html=True)
    
    cols = st.columns([1.5, 7, 1.5])
    
    with cols[0]:
        if icone_b64:
            st.markdown(f'''<div class="nav-group">
                <img src="data:image/png;base64,{icone_b64}" style="height:35px; object-fit:contain;">
                {f'<img src="data:image/png;base64,{texto_b64}" style="height:18px; margin-left:8px;">' if texto_b64 else '<span style="font-weight:800; font-size:18px; color:#1E293B; margin-left:8px;">OMNI</span>'}
            </div>''', unsafe_allow_html=True)
        else:
            st.markdown('<div class="nav-group"><span style="font-weight:800; font-size:18px; color:#1E293B;">OMNI</span></div>', unsafe_allow_html=True)

    with cols[1]:
        # Botões de navegação usando st.button (Render-safe)
        c_nav = st.columns(len(nav_items))
        for i, item in enumerate(nav_items):
            with c_nav[i]:
                is_active = item["key"] == active_tab
                btn_type = "primary" if is_active else "secondary"
                if st.button(item["label"], key=f"nav_{item['key']}", use_container_width=True, type=btn_type):
                    st.switch_page(item["page"])

    with cols[2]:
        user_name = st.session_state.get("usuario_nome", "Visitante") or "Visitante"
        user_initials = _get_initials(user_name)
        st.markdown(f'<div class="omni-avatar" title="{user_name}">{user_initials}</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

def render_navbar(active_tab: str = "Início"):
    """
    Navbar removido - agora integrado na topbar via render_omnisfera_header().
    Mantido para compatibilidade (não faz nada).
    """
    pass

# =============================================================================
# 3) SUPABASE & UTILS (LÓGICA PRESERVADA)
# =============================================================================
def _sb_url() -> str:
    url = str(get_setting("SUPABASE_URL", "")).strip()
    if not url:
        raise RuntimeError("SUPABASE_URL não encontrado nos secrets.")
    return url.rstrip("/")

def _sb_key() -> str:
    key = str(get_setting("SUPABASE_SERVICE_KEY", "")).strip()
    if not key:
        key = str(get_setting("SUPABASE_ANON_KEY", "")).strip()
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
    padding-top: 0.1rem !important;
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
    Injeta as classes de cores dos hero cards (paleta vibrante que dialoga com vermelho do Streamlit).
    Cada página deve usar sua cor específica no hero card.
    Nova paleta: azuis mais vivos que complementam o vermelho dos seletores do Streamlit.
    """
    st.markdown(
        """
<style>
/* ===============================
   CORES DOS CARDS DE MÓDULO (PALETA VIBRANTE - AZUIS QUE DIALOGAM COM VERMELHO)
================================ */
/* Estudantes - Azul Índigo Vibrante */
.c-indigo { background: #2563EB !important; }
.bg-indigo-soft { 
    background: #DBEAFE !important; 
    color: #1E40AF !important;
}

/* PEI - Azul Céu Vibrante */
.c-blue { background: #0EA5E9 !important; }
.bg-blue-soft { 
    background: #E0F2FE !important;
    color: #0284C7 !important;
}

/* PAEE - Roxo Vibrante */
.c-purple { background: #A855F7 !important; }
.bg-purple-soft { 
    background: #F3E8FF !important;
    color: #9333EA !important;
}

/* Hub - Verde Água Vibrante */
.c-teal { background: #06B6D4 !important; }
.bg-teal-soft { 
    background: #CFFAFE !important;
    color: #0891B2 !important;
}

/* Diário - Rosa Vibrante */
.c-rose { background: #F43F5E !important; }
.bg-rose-soft { 
    background: #FFE4E6 !important;
    color: #E11D48 !important;
}

/* Monitoramento - Azul Oceano Vibrante */
.c-sky { background: #0C4A6E !important; }
.bg-sky-soft { 
    background: #BAE6FD !important;
    color: #075985 !important;
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
    Usa azul vibrante (#2563EB) que dialoga com o vermelho dos seletores do Streamlit.
    """
    st.markdown(
        """
<style>
:root {
    --ui-primary: #1E3A8A;        /* blue-900 - azul marinho que dialoga com vermelho */
    --ui-primary-dark: #1E40AF;   /* blue-800 - mais escuro */
    --ui-primary-light: #2563EB;  /* blue-600 - mais claro */
    --ui-primary-soft: #DBEAFE;   /* blue-100 - fundo suave */
    --ui-primary-border: #93C5FD; /* blue-300 - bordas */
    
    /* Mantém variáveis neutras para compatibilidade */
    --ui-neutral: #1E3A8A;        /* usa azul marinho */
    --ui-neutral-dark: #1E40AF;   
    --ui-neutral-light: #2563EB;  
    --ui-neutral-soft: #DBEAFE;   
    --ui-neutral-border: #93C5FD; 
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
    justify-content: flex-start !important;  /* pílulas alinhadas à esquerda */
    align-items: center !important;
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
    border: 1px solid var(--ui-primary-border) !important;
    color: var(--ui-primary) !important;
    font-weight: 700 !important;
    font-size: 0.75rem !important;
    padding: 0 18px !important;
    box-shadow: 0 1px 2px rgba(30,58,138,0.1) !important;
    text-transform: uppercase !important;
    letter-spacing: 0.5px !important;
    transition: all 0.2s ease !important;
}

.stTabs [data-baseweb="tab"]:hover:not([aria-selected="true"]) { 
    border-color: var(--ui-primary-light) !important; 
    color: var(--ui-primary-dark) !important; 
    background-color: var(--ui-primary-soft) !important; 
}

.stTabs [aria-selected="true"] {
    background-color: var(--ui-primary-soft) !important; 
    color: var(--ui-primary-dark) !important;
    border: 1px solid var(--ui-primary) !important; 
    font-weight: 800 !important;
    box-shadow: 0 2px 4px rgba(30,58,138,0.2) !important;
}

/* ===============================
   TABS - CORES ESPECÍFICAS POR PÁGINA (via classe no body)
================================ */
/* Estudantes - Índigo */
.page-indigo .stTabs [aria-selected="true"] {
    background-color: #DBEAFE !important;
    color: #1E40AF !important;
    border: 1px solid #2563EB !important;
    box-shadow: 0 2px 4px rgba(30,58,138,0.2) !important;
}

/* PEI - Azul Céu */
.page-blue .stTabs [aria-selected="true"] {
    background-color: #E0F2FE !important;
    color: #0284C7 !important;
    border: 1px solid #0EA5E9 !important;
    box-shadow: 0 2px 4px rgba(14,165,233,0.2) !important;
}

/* PAEE - Roxo */
.page-purple .stTabs [aria-selected="true"] {
    background-color: #F3E8FF !important;
    color: #9333EA !important;
    border: 1px solid #A855F7 !important;
    box-shadow: 0 2px 4px rgba(168,85,247,0.2) !important;
}

/* Hub - Verde Água */
.page-teal .stTabs [aria-selected="true"] {
    background-color: #CFFAFE !important;
    color: #0891B2 !important;
    border: 1px solid #06B6D4 !important;
    box-shadow: 0 2px 4px rgba(6,182,212,0.2) !important;
}

/* Diário - Rosa */
.page-rose .stTabs [aria-selected="true"] {
    background-color: #FFE4E6 !important;
    color: #E11D48 !important;
    border: 1px solid #F43F5E !important;
    box-shadow: 0 2px 4px rgba(244,63,94,0.2) !important;
}

/* Monitoramento - Azul Oceano */
.page-sky .stTabs [aria-selected="true"] {
    background-color: #BAE6FD !important;
    color: #075985 !important;
    border: 1px solid #0C4A6E !important;
    box-shadow: 0 2px 4px rgba(12,74,110,0.2) !important;
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
    background: linear-gradient(135deg, #2563EB 0%, #0EA5E9 100%) !important;
    border: none !important;
    color: #ffffff !important;
}

.stButton > button[kind="primary"]:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 10px 22px rgba(37, 99, 235, 0.3) !important;
    background: linear-gradient(135deg, #0EA5E9 0%, #2563EB 100%) !important;
}

.stButton > button[kind="secondary"] {
    background: #ffffff !important;
    color: #2563EB !important;
    border: 1px solid #2563EB !important;
}

.stButton > button[kind="secondary"]:hover {
    background: rgba(37, 99, 235, 0.06) !important;
    border-color: #0EA5E9 !important;
    color: #0EA5E9 !important;
}

/* ===============================
   SELECTS / DROPDOWNS
================================ */
div[data-baseweb="select"] > div {
    border-radius: 8px !important;
    border-color: var(--ui-primary-border) !important;
}

div[data-baseweb="select"] > div:focus-within {
    border-color: var(--ui-primary) !important;
    box-shadow: 0 0 0 3px rgba(30,58,138,0.18) !important;
}

/* ===============================
   MULTISELECT
================================ */
div[data-baseweb="select"][aria-multiselectable="true"] > div {
    border-radius: 8px !important;
    border-color: var(--ui-primary-border) !important;
}

div[data-baseweb="select"][aria-multiselectable="true"] > div:focus-within {
    border-color: var(--ui-primary) !important;
    box-shadow: 0 0 0 3px rgba(30,58,138,0.18) !important;
}

/* ===============================
   SLIDER
================================ */
.stSlider {
    border-radius: 8px !important;
}

/* Track do slider */
.stSlider > div > div[data-baseweb="slider"] > div[data-baseweb="slider-track"] {
    background-color: var(--ui-primary-border) !important;
}

/* Fill do slider (parte preenchida) */
.stSlider > div > div[data-baseweb="slider"] > div[data-baseweb="slider-track"] > div[data-baseweb="slider-fill"] {
    background: linear-gradient(135deg, var(--ui-primary), var(--ui-primary-dark)) !important;
}

/* Thumb do slider (bolinha) */
.stSlider > div > div[data-baseweb="slider"] > div[data-baseweb="slider-thumb"] {
    background-color: var(--ui-primary) !important;
    border-color: var(--ui-primary) !important;
}

.stSlider > div > div[data-baseweb="slider"] > div[data-baseweb="slider-thumb"]:hover {
    background-color: var(--ui-primary-dark) !important;
    border-color: var(--ui-primary-dark) !important;
}

/* Fallback para estrutura alternativa do slider */
.stSlider div[data-baseweb="slider-thumb"] {
    background-color: var(--ui-primary) !important;
    border-color: var(--ui-primary) !important;
}

.stSlider div[data-baseweb="slider-fill"] {
    background: linear-gradient(135deg, var(--ui-primary), var(--ui-primary-dark)) !important;
}

/* ===============================
   CHECKBOX
================================ */
div[role="checkbox"] {
    border-radius: 4px !important;
    border-color: var(--ui-primary-border) !important;
}

div[role="checkbox"][aria-checked="true"] {
    background-color: var(--ui-primary) !important;
    border-color: var(--ui-primary) !important;
}

div[role="checkbox"]:hover {
    border-color: var(--ui-primary) !important;
}

div[role="checkbox"][aria-checked="true"]:hover {
    background-color: var(--ui-primary-dark) !important;
    border-color: var(--ui-primary-dark) !important;
}

/* ===============================
   RADIO
================================ */
div[role="radio"] {
    border-color: var(--ui-primary-border) !important;
}

div[role="radio"][aria-checked="true"] {
    background-color: var(--ui-primary) !important;
    border-color: var(--ui-primary) !important;
}

div[role="radio"]:hover {
    border-color: var(--ui-primary) !important;
}

div[role="radio"][aria-checked="true"]:hover {
    background-color: var(--ui-primary-dark) !important;
    border-color: var(--ui-primary-dark) !important;
}

/* ===============================
   INPUTS / TEXTAREAS
================================ */
.stTextInput input,
.stTextArea textarea {
    border-radius: 8px !important;
    border-color: var(--ui-primary-border) !important;
}

.stTextInput input:focus,
.stTextArea textarea:focus {
    border-color: var(--ui-primary) !important;
    box-shadow: 0 0 0 3px rgba(30,58,138,0.18) !important;
}

/* ===============================
   MULTISELECT TAGS / CHIPS
================================ */
div[data-baseweb="tag"] {
    background: var(--ui-primary-soft) !important;
    border: 1px solid var(--ui-primary-border) !important;
    border-radius: 6px !important;
}

div[data-baseweb="tag"] span {
    color: var(--ui-primary-dark) !important;
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
    border-color: var(--ui-primary-border) !important;
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
    
/* ===============================
   SOBRESCREVER VERMELHO DO STREAMLIT
================================ */
/* Tenta sobrescrever cores vermelhas padrão do Streamlit */
div[data-baseweb="select"] svg[fill="#FF0000"],
div[data-baseweb="select"] svg[fill="red"],
div[data-baseweb="select"] svg[fill="rgb(255, 0, 0)"] {
    fill: var(--ui-primary) !important;
}

/* Inputs com foco vermelho */
input:focus,
textarea:focus,
select:focus {
    border-color: var(--ui-primary) !important;
    outline-color: var(--ui-primary) !important;
}
}
</style>
        """,
        unsafe_allow_html=True,
    )

# =============================================================================
# 4.5) RODAPÉ COM ASSINATURA
# =============================================================================
def render_footer_assinatura():
    """Renderiza rodapé com assinatura em todas as páginas"""
    st.markdown("""
    <div style="
        text-align: center;
        padding: 24px 0;
        margin-top: 40px;
        border-top: 1px solid #E2E8F0;
        color: #94A3B8;
        font-size: 0.75rem;
        font-weight: 500;
    ">
        Criado e desenvolvido por <strong style="color: #64748B;">Rodrigo A. Queiroz</strong>
    </div>
    """, unsafe_allow_html=True)

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
