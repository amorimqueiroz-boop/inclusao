import os
import base64
import json
import requests
import streamlit as st
from streamlit_option_menu import option_menu

# =============================================================================
# 1. ESTADO E CONFIGURAÇÃO INICIAL
# =============================================================================
def ensure_state():
    if "autenticado" not in st.session_state:
        st.session_state.autenticado = False
    if "user" not in st.session_state:
        st.session_state.user = None
    if "workspace_id" not in st.session_state:
        st.session_state.workspace_id = None
    if "view" not in st.session_state:
        st.session_state.view = "login"

# =============================================================================
# 2. UI COMPONENTS (HEADER & NAVBAR) - AJUSTE PIXEL PERFECT
# =============================================================================

def get_base64_image(path: str) -> str | None:
    if not os.path.exists(path):
        return None
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

def render_omnisfera_header():
    """
    Renderiza o Topbar fixo (60px) e remove margens excessivas do corpo da página.
    """
    def _get_initials(nome: str) -> str:
        if not nome: return "U"
        parts = nome.strip().split()
        return f"{parts[0][0]}{parts[-1][0]}".upper() if len(parts) >= 2 else parts[0][:2].upper()

    def _get_ws_short(max_len: int = 20) -> str:
        ws = st.session_state.get("workspace_name", "") or "Workspace"
        return (ws[:max_len] + "...") if len(ws) > max_len else ws

    # CSS GLOBAL DE LAYOUT
    st.markdown("""
    <link href="https://cdn.jsdelivr.net/npm/remixicon@3.5.0/fonts/remixicon.css" rel="stylesheet">
    <style>
        /* 1. AJUSTE CRÍTICO DE POSIÇÃO */
        /* Empurra o conteúdo apenas o suficiente para não ficar escondido atrás da barra */
        div[data-testid="stAppViewContainer"] > div:first-child {
            padding-top: 70px !important; /* 60px da barra + 10px de respiro */
        }
        
        /* Remove o header nativo completamente */
        .stApp > header { display: none !important; }
        
        /* Esconde elementos padrão do Streamlit */
        [data-testid="stSidebarNav"], footer, section[data-testid="stSidebar"], button[data-testid="collapsedControl"] {
            display: none !important;
        }
        
        /* 2. BARRA SUPERIOR (HEADER) */
        .omni-topbar {
            position: fixed !important;
            top: 0 !important; left: 0 !important; right: 0 !important;
            height: 60px !important; /* Altura ideal */
            background: #ffffff !important;
            border-bottom: 1px solid #E2E8F0 !important;
            z-index: 999999 !important;
            display: flex !important; align-items: center !important; justify-content: space-between !important;
            padding: 0 24px !important;
            box-shadow: 0 1px 3px rgba(0,0,0,0.03) !important;
        }
        
        .omni-brand { display: flex !important; align-items: center !important; gap: 12px !important; }
        
        /* Logo e Texto */
        .omni-logo { height: 34px !important; width: 34px !important; animation: spin-logo 60s linear infinite; }
        .omni-title-img { height: 20px !important; margin-left: 6px !important; }
        
        .omni-user-info { display: flex !important; align-items: center !important; gap: 12px !important; }
        
        /* Badge do Workspace */
        .omni-workspace {
            background: #F8FAFC !important; border: 1px solid #E2E8F0 !important;
            padding: 5px 12px !important; border-radius: 8px !important;
            font-size: 12px !important; font-weight: 600 !important; color: #475569 !important;
            max-width: 180px !important; overflow: hidden !important; white-space: nowrap !important; text-overflow: ellipsis !important;
        }
        
        /* Avatar */
        .omni-avatar {
            width: 32px !important; height: 32px !important;
            border-radius: 50% !important;
            background: linear-gradient(135deg, #3B82F6, #2563EB) !important; /* Azul Omnisfera */
            color: white !important;
            display: flex !important; align-items: center !important; justify-content: center !important;
            font-weight: 700 !important; font-size: 12px !important;
            box-shadow: 0 2px 4px rgba(37, 99, 235, 0.2) !important;
        }
        
        @keyframes spin-logo { 100% { transform: rotate(360deg); } }

        /* 3. LAYOUT DO CONTEÚDO PRINCIPAL */
        .block-container {
            padding-top: 0px !important; /* O padding é controlado pelo stAppViewContainer acima */
            padding-bottom: 30px !important;
            max-width: 100% !important; /* Ocupa largura total */
        }
        .main .block-container {
            padding-left: 2rem !important;
            padding-right: 2rem !important;
        }
    </style>
    """, unsafe_allow_html=True)

    icone = get_base64_image("omni_icone.png")
    texto = get_base64_image("omni_texto.png")
    ws_name = _get_ws_short()
    user_name = st.session_state.get("usuario_nome", "Visitante")
    
    img_logo = f'<img src="data:image/png;base64,{icone}" class="omni-logo">' if icone else '<span style="font-size:24px;">🌐</span>'
    img_text = f'<img src="data:image/png;base64,{texto}" class="omni-title-img">' if texto else '<span style="font-weight:800;color:#1E293B;font-size:18px;">OMNISFERA</span>'

    st.markdown(f"""
        <div class="omni-topbar">
            <div class="omni-brand">{img_logo}{img_text}</div>
            <div class="omni-user-info">
                <div class="omni-workspace" title="{ws_name}">{ws_name}</div>
                <div class="omni-avatar">{_get_initials(user_name)}</div>
            </div>
        </div>
    """, unsafe_allow_html=True)


def render_navbar(active_tab: str = "Início"):
    """
    Renderiza o menu centralizado usando Colunas do Streamlit para garantir alinhamento.
    """
    opcoes = ["Início", "Estudantes", "Estratégias & PEI", "Plano de Ação (AEE)", "Hub de Recursos", "Diário de Bordo", "Evolução & Dados"]
    icones = ["house", "people", "book", "puzzle", "rocket", "journal", "bar-chart"]

    try: default_idx = opcoes.index(active_tab)
    except ValueError: default_idx = 0

    # CSS para limpar margens do container do menu
    st.markdown("""
    <style>
    .stHorizontalBlock { margin-top: 0px !important; padding-top: 0px !important; }
    /* Ajuste fino para colar o menu logo abaixo do header */
    div[data-testid="column"] { padding-top: 0px !important; }
    </style>
    """, unsafe_allow_html=True)

    # USANDO COLUNAS PARA CENTRALIZAR
    # [Espaço Vazio] [MENU (Largo)] [Espaço Vazio]
    # Isso garante que o menu fique no meio da tela, independente da resolução
    c_left, c_menu, c_right = st.columns([1, 12, 1]) 
    
    with c_menu:
        selected = option_menu(
            menu_title=None, 
            options=opcoes,
            icons=icones,
            default_index=default_idx,
            orientation="horizontal",
            styles={
                "container": {
                    "padding": "0!important", 
                    "background-color": "white",
                    "border": "1px solid #E2E8F0",
                    "border-radius": "12px",
                    "margin": "0px",
                    "box-shadow": "0 2px 5px rgba(0,0,0,0.02)"
                },
                "icon": { "color": "#64748B", "font-size": "14px" }, 
                "nav-link": {
                    "font-size": "11px", 
                    "text-align": "center", 
                    "margin": "0px",
                    "padding": "10px 14px", /* Padding lateral um pouco maior para espaçar */
                    "--hover-color": "#F1F5F9",
                    "color": "#475569",
                    "white-space": "nowrap",
                    "border-radius": "8px",
                    "font-weight": "500"
                },
                "nav-link-selected": {
                    "background-color": "#0284C7", /* Azul Sky 600 */
                    "color": "white",
                    "font-weight": "700",
                    "border": "none",
                    "box-shadow": "0 2px 4px rgba(2, 132, 199, 0.25)"
                },
            }
        )
    
    # Lógica de Navegação
    if selected != active_tab:
        if selected == "Início":
            target = "pages/0_Home.py" if os.path.exists("pages/0_Home.py") else "0_Home.py"
            if not os.path.exists(target): target = "Home.py"
            st.switch_page(target)
        elif selected == "Estudantes": st.switch_page("pages/Alunos.py") 
        elif selected == "Estratégias & PEI": st.switch_page("pages/1_PEI.py")
        elif selected == "Plano de Ação (AEE)": st.switch_page("pages/2_PAE.py")
        elif selected == "Hub de Recursos": st.switch_page("pages/3_Hub_Inclusao.py")
        elif selected == "Diário de Bordo": st.switch_page("pages/4_Diario_de_Bordo.py")
        elif selected == "Evolução & Dados": st.switch_page("pages/5_Monitoramento_Avaliacao.py")

# =============================================================================
# 3. UI HELPERS (LOGIN/GERAL)
# =============================================================================
def inject_base_css():
    st.markdown("""<style>.login-box { background: white; border-radius: 24px; padding: 40px; box-shadow: 0 10px 30px rgba(0,0,0,0.05); text-align: center; border: 1px solid #E2E8F0; max-width: 650px; margin: 0 auto; margin-top: 30px; }</style>""", unsafe_allow_html=True)

# =============================================================================
# 4. SUPABASE / BANCO DE DADOS (REST)
# =============================================================================
def _sb_url() -> str:
    url = st.secrets.get("SUPABASE_URL", "").strip()
    if not url: raise RuntimeError("SUPABASE_URL não encontrado nos secrets.")
    return url.rstrip("/")

def _sb_key() -> str:
    key = st.secrets.get("SUPABASE_SERVICE_KEY", "").strip()
    if not key: key = st.secrets.get("SUPABASE_ANON_KEY", "").strip()
    if not key: raise RuntimeError("SUPABASE_SERVICE_KEY/ANON_KEY não encontrado nos secrets.")
    return key

def _headers() -> dict:
    key = _sb_key()
    return {"apikey": key, "Authorization": f"Bearer {key}", "Content-Type": "application/json"}

def supabase_rpc(fn_name: str, payload: dict):
    url = f"{_sb_url()}/rest/v1/rpc/{fn_name}"
    r = requests.post(url, headers=_headers(), json=payload, timeout=20)
    if r.status_code >= 400: raise RuntimeError(f"RPC {fn_name} falhou: {r.status_code} {r.text}")
    return r.json()

def supabase_insert(table: str, row: dict):
    url = f"{_sb_url()}/rest/v1/{table}"
    h = _headers()
    h["Prefer"] = "return=representation"
    r = requests.post(url, headers=h, json=row, timeout=20)
    if r.status_code >= 400: raise RuntimeError(f"Insert em {table} falhou: {r.status_code} {r.text}")
    return r.json()

def supabase_upsert(table: str, row: dict, on_conflict: str):
    url = f"{_sb_url()}/rest/v1/{table}?on_conflict={on_conflict}"
    h = _headers()
    h["Prefer"] = "resolution=merge-duplicates,return=representation"
    r = requests.post(url, headers=h, json=row, timeout=20)
    if r.status_code >= 400: raise RuntimeError(f"Upsert em {table} falhou: {r.status_code} {r.text}")
    data = r.json()
    if isinstance(data, list) and len(data) > 0: return data[0]
    return data if isinstance(data, dict) else None

def supabase_workspace_from_pin(pin: str) -> str | None:
    pin = (pin or "").strip()
    if not pin: return None
    for payload in ({"pin": pin}, {"p_pin": pin}, {"pincode": pin}):
        try:
            data = supabase_rpc("workspace_from_pin", payload)
            if isinstance(data, dict) and data.get("workspace_id"): return data["workspace_id"]
            if isinstance(data, list) and len(data) > 0:
                first = data[0]
                if isinstance(first, dict) and first.get("workspace_id"): return first["workspace_id"]
        except Exception: continue
    return None

def supabase_log_access(workspace_id: str, nome: str, cargo: str, event: str, app_version: str = ""):
    ua = st.context.headers.get("User-Agent", "") if hasattr(st, "context") else ""
    row = {
        "workspace_id": workspace_id, "nome": (nome or "").strip(), "cargo": (cargo or "").strip(),
        "event": (event or "").strip(), "user_agent": ua[:500], "app_version": (app_version or "").strip(),
    }
    return supabase_insert("access_logs", row)

def _cloud_ready(debug: bool = False):
    details = {}
    try: supabase_url = str(st.secrets.get("SUPABASE_URL", "")).strip()
    except: supabase_url = ""
    try: service_key = str(st.secrets.get("SUPABASE_SERVICE_KEY", "")).strip()
    except: service_key = ""
    has_key = bool(service_key) or bool(st.secrets.get("SUPABASE_ANON_KEY", ""))
    ws_id = st.session_state.get("workspace_id")
    auth = st.session_state.get("autenticado", False)
    details["has_supabase_url"] = bool(supabase_url)
    details["has_supabase_key"] = has_key
    details["has_workspace_id"] = bool(ws_id)
    details["autenticado"] = bool(auth)
    ok = all(details.values())
    if debug: details["missing"] = [k for k, v in details.items() if v is False]
    return ok, details

def supa_save_pei(student_id: str, dados: dict, pdf_text: str = ""):
    if not student_id: raise RuntimeError("student_id vazio.")
    ws_id = st.session_state.get("workspace_id")
    if not ws_id: raise RuntimeError("workspace_id não encontrado.")
    row = {
        "student_id": student_id, "workspace_id": ws_id,
        "pei_json": dados if isinstance(dados, dict) else {},
        "pdf_text": pdf_text or "",
    }
    return supabase_upsert("peis", row, on_conflict="student_id")
