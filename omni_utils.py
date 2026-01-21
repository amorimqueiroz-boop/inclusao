# omni_utils.py
import os
import base64
import streamlit as st
import requests


# =============================================================================
# ESTADO
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
# UI HELPERS
# =============================================================================
def get_base64_image(path: str) -> str | None:
    if not os.path.exists(path):
        return None
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def inject_base_css():
    st.markdown(
        """
<style>
/* Layout geral */
.block-container { padding-top: 2rem !important; padding-bottom: 3rem !important; max-width: 1200px; }

/* LOGIN */
.login-box {
  background: white; border-radius: 24px; padding: 40px;
  box-shadow: 0 10px 30px rgba(0,0,0,0.05);
  text-align: center; border: 1px solid #E2E8F0;
  max-width: 650px; margin: 0 auto; margin-top: 30px;
}
.login-logo { height: 80px; margin-bottom: 16px; }
.login-manifesto { font-style: italic; color: #718096; margin-bottom: 22px; font-size: 0.95rem; }
.stTextInput input { border-radius: 10px !important; border: 1px solid #E2E8F0 !important; height: 46px !important; }
.termo-box {
  background-color: #F8FAFC; padding: 15px; border-radius: 10px;
  height: 130px; overflow-y: auto; font-size: 0.80rem;
  border: 1px solid #E2E8F0; margin-bottom: 14px;
  text-align: justify; color: #4A5568;
}

/* HOME */
.header-lite{
  display:flex; justify-content:space-between; align-items:center;
  border: 1px solid #E2E8F0; background: rgba(255,255,255,0.85);
  border-radius: 16px; padding: 18px 20px; margin-bottom: 18px;
}
.h-title{ font-size: 1.35rem; font-weight: 900; color:#1A202C; }
.h-sub{ font-size: .95rem; font-weight: 600; color:#718096; margin-top: 2px; }
.h-badge{
  border: 1px solid #E2E8F0; background:#F7FAFC; color:#4A5568;
  border-radius: 999px; padding: 6px 12px; font-weight: 900; font-size: .75rem;
  letter-spacing: .08em;
}
</style>
        """,
        unsafe_allow_html=True,
    )


# =============================================================================
# SUPABASE (sem depender de supabase-py; usa REST)
# =============================================================================
def _sb_url() -> str:
    url = st.secrets.get("SUPABASE_URL", "").strip()
    if not url:
        raise RuntimeError("SUPABASE_URL não encontrado nos secrets.")
    return url.rstrip("/")


def _sb_key() -> str:
    # Preferência: SERVICE_KEY (server-side), fallback: ANON_KEY
    key = st.secrets.get("SUPABASE_SERVICE_KEY", "").strip()
    if not key:
        key = st.secrets.get("SUPABASE_ANON_KEY", "").strip()
    if not key:
        raise RuntimeError("SUPABASE_SERVICE_KEY/ANON_KEY não encontrado nos secrets.")
    return key


def _headers() -> dict:
    key = _sb_key()
    return {
        "apikey": key,
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
    }


def supabase_rpc(fn_name: str, payload: dict):
    url = f"{_sb_url()}/rest/v1/rpc/{fn_name}"
    r = requests.post(url, headers=_headers(), json=payload, timeout=20)
    if r.status_code >= 400:
        raise RuntimeError(f"RPC {fn_name} falhou: {r.status_code} {r.text}")
    return r.json()


def supabase_insert(table: str, row: dict):
    url = f"{_sb_url()}/rest/v1/{table}"
    h = _headers()
    h["Prefer"] = "return=representation"
    r = requests.post(url, headers=h, json=row, timeout=20)
    if r.status_code >= 400:
        raise RuntimeError(f"Insert em {table} falhou: {r.status_code} {r.text}")
    return r.json()


# =============================================================================
# WORKSPACE (PIN)
# =============================================================================
def supabase_workspace_from_pin(pin: str) -> str | None:
    """
    Espera existir no Supabase a RPC: workspace_from_pin(pin)
    ou workspace_from_pin(p_pin).
    Retorna workspace_id (uuid).
    """
    pin = (pin or "").strip()
    if not pin:
        return None

    # Tentativas para compatibilidade com nomes de parâmetro
    for payload in ({"pin": pin}, {"p_pin": pin}, {"pincode": pin}):
        try:
            data = supabase_rpc("workspace_from_pin", payload)
            # data pode vir como {"workspace_id": "..."} OU como lista [{"workspace_id": "..."}]
            if isinstance(data, dict) and data.get("workspace_id"):
                return data["workspace_id"]
            if isinstance(data, list) and len(data) > 0:
                first = data[0]
                if isinstance(first, dict) and first.get("workspace_id"):
                    return first["workspace_id"]
        except Exception:
            continue

    return None


# =============================================================================
# LOGS INTERNOS (para você)
# =============================================================================
def supabase_log_access(
    workspace_id: str,
    nome: str,
    cargo: str,
    event: str,
    app_version: str = "",
):
    """
    Requer tabela no Supabase: access_logs
    Campos sugeridos:
      - id (uuid default gen_random_uuid())
      - created_at (timestamptz default now())
      - workspace_id (uuid)
      - nome (text)
      - cargo (text)
      - event (text)
      - user_agent (text)
      - app_version (text)
    """
    ua = st.context.headers.get("User-Agent", "") if hasattr(st, "context") else ""
    row = {
        "workspace_id": workspace_id,
        "nome": (nome or "").strip(),
        "cargo": (cargo or "").strip(),
        "event": (event or "").strip(),
        "user_agent": ua[:500],
        "app_version": (app_version or "").strip(),
    }
    return supabase_insert("access_logs", row)
