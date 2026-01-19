# _client.py
from __future__ import annotations

import streamlit as st
from supabase import create_client, Client


def _get_supabase_url() -> str:
    url = st.secrets.get("SUPABASE_URL", "")
    if not url:
        raise ValueError("SUPABASE_URL não está definido em st.secrets.")
    return url


def _get_supabase_anon_key() -> str:
    key = st.secrets.get("SUPABASE_ANON_KEY", "")
    if not key:
        raise ValueError("SUPABASE_ANON_KEY não está definido em st.secrets.")
    return key


def get_supabase_admin() -> Client:
    """Client sem JWT (anon)."""
    return create_client(_get_supabase_url(), _get_supabase_anon_key())


def get_supabase_user(jwt: str) -> Client:
    """
    Client com JWT (para RLS).
    Evita sb.auth.set_auth(jwt) porque quebra em versões diferentes.
    """
    if not jwt:
        raise ValueError("JWT vazio em get_supabase_user(jwt).")

    sb = create_client(_get_supabase_url(), _get_supabase_anon_key())

    # jeito mais compatível (postgrest.auth)
    try:
        sb.postgrest.auth(jwt)
        return sb
    except Exception:
        pass

    # fallback: headers
    try:
        sb.postgrest.session.headers.update({"Authorization": f"Bearer {jwt}"})
        return sb
    except Exception:
        pass

    # fallback: options.headers
    try:
        sb.options.headers.update({"Authorization": f"Bearer {jwt}"})
        return sb
    except Exception:
        pass

    raise RuntimeError(
        "Não consegui aplicar o JWT no supabase client. Verifique a versão do pacote supabase."
    )


def supabase_login(email: str, password: str):
    """
    Faz login no Supabase Auth e retorna:
    (jwt, user_id, error_msg)
    """
    try:
        sb = get_supabase_admin()
        res = sb.auth.sign_in_with_password({"email": email, "password": password})

        # tenta pegar token e user de forma robusta
        jwt = None
        user_id = None

        # res.session / res.user em versões comuns
        if hasattr(res, "session") and res.session:
            jwt = getattr(res.session, "access_token", None) or getattr(res.session, "access_token", None)
        if hasattr(res, "user") and res.user:
            user_id = getattr(res.user, "id", None)

        # alguns retornam dict-like
        if jwt is None and isinstance(res, dict):
            jwt = (res.get("session") or {}).get("access_token")
            user_id = (res.get("user") or {}).get("id")

        if not jwt:
            return None, None, "Login falhou: não recebi access_token."
        if not user_id:
            return jwt, None, "Login OK, mas não consegui obter user_id."

        return jwt, user_id, None

    except Exception as e:
        return None, None, str(e)
