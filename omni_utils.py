# omni_utils.py
import os
import base64
import requests
import streamlit as st
from streamlit_option_menu import option_menu

# =============================================================================
# 1) ESTADO E CONFIGURAÇÃO INICIAL
# =============================================================================
APP_VERSION = "omni_utils v2.4 (Layout Estável: Topbar+Navbar sem CSS global perigoso)"

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

def inject_layout_css(topbar_h: int = 56, navbar_h: int = 52, content_gap: int = 14):
    """
    CSS base do layout:
    - Topbar fixa
    - Espaço exato para navbar + conteúdo
    - NÃO mexe em inputs globalmente
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

  /* Container principal: espaço calculado para topbar+navbar */
  .main .block-container {{
    padding-top: calc(var(--topbar-h) + var(--navbar-h) + var(--content-gap)) !important;
    padding-bottom: 2rem !important;
    padding-left: 2rem !important;
    padding-right: 2rem !important;
    max-width: 100% !important;
    font-family: 'Inter', sans-serif !important;
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

  /* NAVBAR WRAPPER (fixa logo abaixo da topbar) */
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
    pointer-events: none; /* libera clique só dentro do menu */
  }}
  .omni-navbar-inner {{
    width: min(1200px, calc(100% - 48px));
    pointer-events: auto;
  }}

  /* Deixa o option_menu sem espaçamento fantasma do Streamlit */
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

def render_omnisfera_header():
    """
    Topbar fixa (apenas render).
    O espaço do conteúdo é controlado por inject_layout_css().
    """
    ensure_state()

    TOPBAR_H = 56
    NAVBAR_H = 52
    inject_layout_css(topbar_h=TOPBAR_H, navbar_h=NAVBAR_H, content_gap=14)

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

    # wrapper fixo
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

    # roteamento (preservado)
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
# 4) CSS DO LOGIN (ESCOPADO) — NÃO AFETA O APP TODO
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
