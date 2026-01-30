# supabase_client.py
import os
from typing import Optional
import streamlit as st

# 🔒 Nome da função RPC
RPC_NAME = "workspace_from_pin"


def _get_secret(name: str) -> Optional[str]:
    """Lê env var (Render) e fallback para secrets (Streamlit Cloud)."""
    v = os.environ.get(name)
    if v:
        return str(v).strip()
    try:
        v = st.secrets.get(name)
        if v:
            return str(v).strip()
    except Exception:
        pass
    return None


@st.cache_resource(show_spinner=False)
def _create_supabase_client():
    """
    Cria UM cliente Supabase (cacheado para o app inteiro).
    Não depende de session_state.
    """
    try:
        from supabase import create_client  # type: ignore
    except Exception as e:
        raise RuntimeError(
            "Pacote 'supabase' não encontrado.\n"
            "➡️ requirements.txt precisa ter: supabase==2.*\n"
            f"Detalhe: {e}"
        )

    url = _get_secret("SUPABASE_URL")
    key = _get_secret("SUPABASE_ANON_KEY")

    if not url or not key:
        raise RuntimeError(
            "SUPABASE_URL / SUPABASE_ANON_KEY não encontrados.\n"
            "➡️ Configure em Settings → Secrets do Streamlit Cloud."
        )

    return create_client(url, key)


def get_sb():
    """
    ✅ Função padrão do projeto: garante sb na session_state.
    Retorna o client.
    """
    if "sb" in st.session_state and st.session_state["sb"] is not None:
        return st.session_state["sb"]

    sb = _create_supabase_client()
    st.session_state["sb"] = sb
    return sb


# Compatibilidade com seu código antigo
def get_supabase():
    """Alias para manter compatibilidade com versões anteriores."""
    return get_sb()


def rpc_workspace_from_pin(pin: str) -> Optional[dict]:
    """
    Chama a função:
    public.workspace_from_pin(p_pin text)
    Retorna: { id, name } ou None
    """
    sb = get_sb()

    res = sb.rpc(RPC_NAME, {"p_pin": pin}).execute()
    data = res.data

    if not data:
        return None
    if isinstance(data, list):
        return data[0] if data else None
    if isinstance(data, dict):
        return data
    return None
