# supabase_client.py
import os
import streamlit as st

# 🔒 Nome da função RPC
RPC_NAME = "workspace_from_pin"


def _get_secret(name: str) -> str | None:
    try:
        v = st.secrets.get(name)
        if v:
            return str(v).strip()
    except Exception:
        pass
    v = os.getenv(name)
    return str(v).strip() if v else None


@st.cache_resource(show_spinner=False)
def _create_supabase_client():
    """
    Cria um client Supabase (cacheado no app).
    NÃO depende de session_state.
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
    Garante que o client Supabase exista e fique acessível em:
    st.session_state["sb"]
    """
    try:
        sb = _create_supabase_client()
        st.session_state["sb"] = sb
        st.session_state.pop("sb_error", None)
        return sb
    except Exception as e:
        st.session_state["sb"] = None
        st.session_state["sb_error"] = str(e)
        raise


def rpc_workspace_from_pin(pin: str) -> dict | None:
    """
    Chama a função:
    public.workspace_from_pin(p_pin text)
    Retorna: { id, name } ou None
    """
    sb = _create_supabase_client()
    res = sb.rpc(RPC_NAME, {"p_pin": pin}).execute()

    data = res.data
    if not data:
        return None

    if isinstance(data, list):
        return data[0] if data else None

    if isinstance(data, dict):
        return data

    return None
