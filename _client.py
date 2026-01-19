import streamlit as st
from functools import lru_cache

# supabase-py v2+
from supabase import create_client

# Alguns ambientes têm ClientOptions; outros não.
try:
    from supabase import ClientOptions  # type: ignore
except Exception:
    ClientOptions = None


def _get_secret(key: str, default=None):
    try:
        return st.secrets.get(key, default)
    except Exception:
        return default


@lru_cache(maxsize=4)
def get_supabase_anon():
    """
    Cliente padrão (anon). Útil para leituras/escritas quando a tabela NÃO exige auth via RLS,
    ou quando você ainda não está passando JWT do usuário.
    """
    url = _get_secret("SUPABASE_URL")
    anon = _get_secret("SUPABASE_ANON_KEY")

    if not url or not anon:
        raise RuntimeError(
            "Supabase não configurado. Verifique em Secrets: SUPABASE_URL e SUPABASE_ANON_KEY"
        )

    return create_client(url, anon)


@lru_cache(maxsize=4)
def get_supabase_admin():
    """
    Cliente admin (SERVICE ROLE). Use só se você souber o que está fazendo.
    (Ideal para rotinas internas/ETL; cuidado com segurança).
    """
    url = _get_secret("SUPABASE_URL")
    service = _get_secret("SUPABASE_SERVICE_ROLE_KEY")

    if not url or not service:
        raise RuntimeError(
            "Supabase admin não configurado. Verifique em Secrets: SUPABASE_URL e SUPABASE_SERVICE_ROLE_KEY"
        )

    return create_client(url, service)


def get_supabase_user(jwt: str | None):
    """
    Cliente Supabase 'como usuário' (com JWT) para funcionar com RLS.

    - Se jwt vier vazio/None: cai automaticamente no cliente anon (não quebra o app).
    - Se jwt vier preenchido: tenta criar cliente com headers Authorization.
    """
    if not jwt:
        return get_supabase_anon()

    url = _get_secret("SUPABASE_URL")
    anon = _get_secret("SUPABASE_ANON_KEY")
    if not url or not anon:
        raise RuntimeError(
            "Supabase não configurado. Verifique em Secrets: SUPABASE_URL e SUPABASE_ANON_KEY"
        )

    # Tentativa 1 (supabase-py com ClientOptions)
    if ClientOptions is not None:
        opts = ClientOptions(
            headers={
                "Authorization": f"Bearer {jwt}",
            }
        )
        return create_client(url, anon, options=opts)

    # Tentativa 2 (fallback simples)
    # Alguns builds aceitam options como dict com headers.
    try:
        return create_client(
            url,
            anon,
            options={
                "headers": {"Authorization": f"Bearer {jwt}"},
            },
        )
    except Exception:
        # Se a lib for incompatível, ainda assim não derrubamos o app:
        return get_supabase_anon()
