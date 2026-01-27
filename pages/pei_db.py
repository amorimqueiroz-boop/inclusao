# pei_db.py
import streamlit as st
import requests
from datetime import datetime

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
        raise RuntimeError("SUPABASE_SERVICE_KEY/ANON_KEY não encontrado nos secrets.")
    return key

def _headers() -> dict:
    key = _sb_key()
    return {
        "apikey": key,
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
    }

def db_create_student(payload: dict):
    """Cria aluno em public.students usando REST"""
    ws_id = st.session_state.get("workspace_id")
    row = dict(payload or {})
    row["workspace_id"] = ws_id

    url = f"{_sb_url()}/rest/v1/students"
    h = _headers()
    h["Prefer"] = "return=representation"

    r = requests.post(url, headers=h, json=row, timeout=20)
    if r.status_code >= 400:
        raise RuntimeError(f"Insert em students falhou: {r.status_code} {r.text}")

    data = r.json()
    if isinstance(data, list) and len(data) > 0:
        return data[0]
    if isinstance(data, dict):
        return data
    return None

def db_update_student(student_id: str, payload: dict):
    """Atualiza aluno em public.students (por id) via REST"""
    ws_id = st.session_state.get("workspace_id")
    row = dict(payload or {})

    url = f"{_sb_url()}/rest/v1/students?id=eq.{student_id}&workspace_id=eq.{ws_id}"
    h = _headers()
    h["Prefer"] = "return=representation"

    r = requests.patch(url, headers=h, json=row, timeout=20)
    if r.status_code >= 400:
        raise RuntimeError(f"Update em students falhou: {r.status_code} {r.text}")

    data = r.json()
    if isinstance(data, list) and len(data) > 0:
        return data[0]
    if isinstance(data, dict):
        return data
    return None

def db_update_pei_content(student_id: str, pei_dict: dict):
    """Salva o JSON completo na coluna pei_data do Supabase"""
    import json
    
    url = f"{_sb_url()}/rest/v1/students?id=eq.{student_id}"
    headers = _headers()
    headers["Prefer"] = "return=representation"
    
    payload_json = json.loads(json.dumps(pei_dict, default=str))
    
    body = {
        "pei_data": payload_json,
        "updated_at": datetime.now().isoformat()
    }
    
    r = requests.patch(url, headers=headers, json=body, timeout=20)
    return r.json() if r.status_code < 400 else None
