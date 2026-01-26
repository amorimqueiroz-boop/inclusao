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
# 2. UI COMPONENTS (HEADER & NAVBAR) - CORRIGIDO E SIMPLIFICADO
# =============================================================================

def get_base64_image(path: str) -> str | None:
    if not os.path.exists(path):
        return None
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

def render_omnisfera_header():
    """
    Renderiza o Topbar com CSS simplificado e que funciona
    """
    def _get_initials(nome: str) -> str:
        if not nome: return "U"
        parts = nome.strip().split()
        return f"{parts[0][0]}{parts[-1][0]}".upper() if len(parts) >= 2 else parts[0][:2].upper()

    def _get_ws_short(max_len: int = 20) -> str:
        ws = st.session_state.get("workspace_name", "") or "Workspace"
        return (ws[:max_len] + "...") if len(ws) > max_len else ws

    # CSS simplificado e mais agressivo
    st.markdown("""
    <link href="https://cdn.jsdelivr.net/npm/remixicon@3.5.0/fonts/remixicon.css" rel="stylesheet">
    <style>
        /* CSS MAIS AGUESSIVO - prioridade máxima */
        div[data-testid="stAppViewContainer"] > div:first-child {
            padding-top: 70px !important;
        }
        
        .stApp > header {
            display: none !important;
        }
        
        [data-testid="stSidebarNav"],
        footer,
        section[data-testid="stSidebar"],
        button[data-testid="collapsedControl"] {
            display: none !important;
        }
        
        /* TOPBAR FIXA SIMPLES */
        .omni-topbar {
            position: fixed !important;
            top: 0 !important;
            left: 0 !important;
            right: 0 !important;
            height: 50px !important;
            background: white !important;
            border-bottom: 1px solid #E2E8F0 !important;
            z-index: 999999 !important;
            display: flex !important;
            align-items: center !important;
            justify-content: space-between !important;
            padding: 0 20px !important;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05) !important;
        }
        
        .omni-brand {
            display: flex !important;
            align-items: center !important;
            gap: 10px !important;
        }
        
        .omni-logo {
            height: 28px !important;
            width: 28px !important;
        }
        
        .omni-user-info {
            display: flex !important;
            align-items: center !important;
            gap: 10px !important;
        }
        
        .omni-workspace {
            background: #F1F5F9 !important;
            border: 1px solid #E2E8F0 !important;
            padding: 4px 12px !important;
            border-radius: 10px !important;
            font-size: 12px !important;
            font-weight: 600 !important;
            color: #64748B !important;
            max-width: 150px !important;
            overflow: hidden !important;
            text-overflow: ellipsis !important;
            white-space: nowrap !important;
        }
        
        .omni-avatar {
            width: 28px !important;
            height: 28px !important;
            border-radius: 50% !important;
            background: linear-gradient(135deg, #4F46E5, #7C3AED) !important;
            color: white !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            font-weight: 700 !important;
            font-size: 11px !important;
        }
        
        /* CORREÇÃO DO LAYOUT PRINCIPAL */
        .block-container {
            padding-top: 20px !important;
            padding-bottom: 20px !important;
            max-width: 100% !important;
        }
        
        /* REMOVER MARGENS E PADDINGS EXCESSIVOS */
        .main .block-container {
            padding-left: 1rem !important;
            padding-right: 1rem !important;
        }
    </style>
    """, unsafe_allow_html=True)

    icone = get_base64_image("omni_icone.png")
    texto = get_base64_image("omni_texto.png")
    ws_name = _get_ws_short()
    user_name = st.session_state.get("usuario_nome", "Visitante")
    
    # Usar fallback se as imagens não existirem
    img_logo = f'<img src="data:image/png;base64,{icone}" class="omni-logo">' if icone else '<div class="omni-logo">🌐</div>'
    img_text = f'<img src="data:image/png;base64,{texto}" style="height: 16px; margin-left: 5px;">' if texto else '<span style="font-weight:800;color:#2B3674;font-size:14px;">OMNISFERA</span>'

    st.markdown(f"""
        <div class="omni-topbar">
            <div class="omni-brand">
                {img_logo}
                {img_text}
            </div>
            <div class="omni-user-info">
                <div class="omni-workspace" title="{ws_name}">{ws_name}</div>
                <div class="omni-avatar">{_get_initials(user_name)}</div>
            </div>
        </div>
    """, unsafe_allow_html=True)


def render_navbar(active_tab: str = "Início"):
    """
    Renderiza o menu horizontal - versão simplificada
    """
    opcoes = ["Início", "Estudantes", "Estratégias & PEI", "Plano de Ação (AEE)", "Hub de Recursos", "Diário de Bordo", "Evolução & Dados"]
    icones = ["house", "people", "book", "puzzle", "rocket", "journal", "bar-chart"]

    try: 
        default_idx = opcoes.index(active_tab)
    except ValueError: 
        default_idx = 0

    # CSS específico para o navbar
    st.markdown("""
    <style>
    /* CONTAINER DO NAVBAR */
    .stHorizontalBlock {
        margin-top: 10px !important;
        margin-bottom: 20px !important;
    }
    
    /* REMOVER EFEITOS DO STREAMLIT */
    div[data-testid="stHorizontalBlock"] {
        background: none !important;
        border: none !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # Usar container para melhor controle
    with st.container():
        # Adicionar um pouco de espaço acima do menu
        st.markdown('<div style="height: 10px;"></div>', unsafe_allow_html=True)
        
        selected = option_menu(
            menu_title=None, 
            options=opcoes,
            icons=icones,
            default_index=default_idx,
            orientation="horizontal",
            styles={
                "container": {
                    "padding": "0!important", 
                    "background-color": "#ffffff",
                    "border": "1px solid #E2E8F0",
                    "border-radius": "10px",
                    "margin": "0px",
                    "box-shadow": "0 1px 3px rgba(0,0,0,0.05)"
                },
                "icon": {
                    "color": "#64748B", 
                    "font-size": "14px"
                }, 
                "nav-link": {
                    "font-size": "11px", 
                    "text-align": "center", 
                    "margin": "0px",
                    "padding": "10px 12px",
                    "--hover-color": "#F1F5F9",
                    "color": "#475569",
                    "white-space": "nowrap",
                    "border-radius": "8px"
                },
                "nav-link-selected": {
                    "background-color": "#0284C7",
                    "color": "white",
                    "font-weight": "600",
                    "border": "none"
                },
            }
        )
    
    # Redirecionamento
    if selected != active_tab:
        if selected == "Início":
            target = "pages/0_Home.py" if os.path.exists("pages/0_Home.py") else "0_Home.py"
            if not os.path.exists(target): target = "Home.py"
            st.switch_page(target)
        elif selected == "Estudantes": 
            st.switch_page("pages/Alunos.py") 
        elif selected == "Estratégias & PEI": 
            st.switch_page("pages/1_PEI.py")
        elif selected == "Plano de Ação (AEE)": 
            st.switch_page("pages/2_PAE.py")
        elif selected == "Hub de Recursos": 
            st.switch_page("pages/3_Hub_Inclusao.py")
        elif selected == "Diário de Bordo": 
            st.switch_page("pages/4_Diario_de_Bordo.py")
        elif selected == "Evolução & Dados": 
            st.switch_page("pages/5_Monitoramento_Avaliacao.py")

# =============================================================================
# 3. UI HELPERS (LEGADO / LOGIN) - MANTIDO IGUAL
# =============================================================================
def inject_base_css():
    """
    CSS básico para a tela de Login e Home sem Header.
    """
    st.markdown(
        """
<style>
/* LOGIN e GERAIS */
.login-box {
  background: white; 
  border-radius: 24px; 
  padding: 40px;
  box-shadow: 0 10px 30px rgba(0,0,0,0.05);
  text-align: center; 
  border: 1px solid #E2E8F0;
  max-width: 650px; 
  margin: 0 auto; 
  margin-top: 30px;
}

.login-logo { 
  height: 80px; 
  margin-bottom: 16px; 
}

.login-manifesto { 
  font-style: italic; 
  color: #718096; 
  margin-bottom: 22px; 
  font-size: 0.95rem; 
}

.stTextInput input { 
  border-radius: 10px !important; 
  border: 1px solid #E2E8F0 !important; 
  height: 46px !important; 
}

.termo-box {
  background-color: #F8FAFC; 
  padding: 15px; 
  border-radius: 10px;
  height: 130px; 
  overflow-y: auto; 
  font-size: 0.80rem;
  border: 1px solid #E2E8F0; 
  margin-bottom: 14px;
  text-align: justify; 
  color: #4A5568;
}

/* HOME COMPONENTS */
.header-lite {
  display:flex; 
  justify-content:space-between; 
  align-items:center;
  border: 1px solid #E2E8F0; 
  background: rgba(255,255,255,0.85);
  border-radius: 16px; 
  padding: 18px 20px; 
  margin-bottom: 18px;
}

.h-title { 
  font-size: 1.35rem; 
  font-weight: 900; 
  color:#1A202C; 
}

.h-sub { 
  font-size: .95rem; 
  font-weight: 600; 
  color:#718096; 
  margin-top: 2px; 
}

.h-badge {
  border: 1px solid #E2E8F0; 
  background:#F7FAFC; 
  color:#4A5568;
  border-radius: 999px; 
  padding: 6px 12px; 
  font-weight: 900; 
  font-size: .75rem;
  letter-spacing: .08em;
}
</style>
        """,
        unsafe_allow_html=True,
    )

# =============================================================================
# RESTANTE DO CÓDIGO (MANTIDO IGUAL)
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
