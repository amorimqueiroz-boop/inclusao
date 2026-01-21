# streamlit_app.py
# Omnisfera — Login por PIN + Supabase (sem auth do Supabase) + Sidebar simples
#
# ✅ Requisitos no Supabase (resumo):
# 1) Ter uma tabela workspaces (id uuid, name text, pin_hash text)
# 2) Ter as funções RPC:
#    - public.create_workspace(p_name text, p_pin text) returns uuid
#    - public.workspace_from_pin(p_pin text) returns table(id uuid, name text)
#
# ⚠️ Importante sobre o pgcrypto no Supabase:
# Em muitos projetos Supabase, as funções do pgcrypto ficam no schema "extensions".
# Então sua function deve usar extensions.crypt e extensions.gen_salt (e não crypt puro).
#
# Exemplo (SQL) — cole TUDO DE UMA VEZ no SQL Editor:
# ----------------------------------------------------
# create extension if not exists pgcrypto with schema extensions;
#
# create table if not exists public.workspaces (
#   id uuid primary key default gen_random_uuid(),
#   name text not null,
#   pin_hash text not null,
#   created_at timestamptz not null default now()
# );
#
# create or replace function public.create_workspace(p_name text, p_pin text)
# returns uuid
# language plpgsql
# security definer
# set search_path = public, extensions
# as $$
# declare
#   v_id uuid;
# begin
#   insert into public.workspaces(name, pin_hash)
#   values (p_name, extensions.crypt(p_pin, extensions.gen_salt('bf')))
#   returning id into v_id;
#   return v_id;
# end;
# $$;
#
# create or replace function public.workspace_from_pin(p_pin text)
# returns table (id uuid, name text)
# language sql
# security definer
# set search_path = public, extensions
# as $$
#   select w.id, w.name
#   from public.workspaces w
#   where w.pin_hash = extensions.crypt(p_pin, w.pin_hash)
#   limit 1;
# $$;
#
# grant execute on function public.create_workspace(text, text) to anon, authenticated;
# grant execute on function public.workspace_from_pin(text) to anon, authenticated;
# ----------------------------------------------------

import streamlit as st
from datetime import datetime
from typing import Optional, Dict, Any

# Supabase python client
from supabase import create_client
from postgrest.exceptions import APIError

# -----------------------------------------------------------------------------
# CONFIG
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Omnisfera",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -----------------------------------------------------------------------------
# SUPABASE CLIENT
# -----------------------------------------------------------------------------
@st.cache_resource
def get_supabase():
    """
    Usa APENAS anon key (public).
    No Streamlit Cloud, configure em Secrets:
      SUPABASE_URL
      SUPABASE_ANON_KEY
    """
    url = st.secrets.get("SUPABASE_URL")
    key = st.secrets.get("SUPABASE_ANON_KEY")
    if not url or not key:
        return None
    return create_client(url, key)

supabase = get_supabase()

def supabase_ok() -> bool:
    return supabase is not None

# -----------------------------------------------------------------------------
# SESSION STATE
# -----------------------------------------------------------------------------
def ensure_state():
    if "workspace_id" not in st.session_state:
        st.session_state.workspace_id = None
    if "workspace_name" not in st.session_state:
        st.session_state.workspace_name = None
    if "autenticado" not in st.session_state:
        st.session_state.autenticado = False

ensure_state()

# -----------------------------------------------------------------------------
# RPC HELPERS
# -----------------------------------------------------------------------------
def rpc_workspace_from_pin(pin: str) -> Optional[Dict[str, Any]]:
    """
    Chama RPC public.workspace_from_pin(p_pin text)
    Retorna {"id": ..., "name": ...} ou None
    """
    if not supabase_ok():
        st.error("Supabase não configurado. Verifique Secrets (SUPABASE_URL / SUPABASE_ANON_KEY).")
        return None

    try:
        res = supabase.rpc("workspace_from_pin", {"p_pin": pin}).execute()
        data = res.data
        # Dependendo do client, pode vir dict ou lista
        if isinstance(data, list) and len(data) > 0:
            return data[0]
        if isinstance(data, dict) and data.get("id"):
            return data
        return None
    except APIError as e:
        # Streamlit Cloud pode redigir detalhes; ainda assim exibimos algo útil
        st.error("Erro ao validar PIN via RPC (workspace_from_pin).")
        st.caption("Dica: confira se a função existe, se tem GRANT para anon, e se usa extensions.crypt.")
        st.exception(e)
        return None
    except Exception as e:
        st.error("Erro inesperado ao acessar Supabase.")
        st.exception(e)
        return None

# -----------------------------------------------------------------------------
# UI HELPERS (CSS)
# -----------------------------------------------------------------------------
def inject_css():
    st.markdown(
        """
<style>
/* Layout clean */
.block-container { padding-top: 2.0rem; padding-bottom: 3rem; max-width: 1100px; }

/* Card */
.card {
  background: rgba(255,255,255,0.85);
  border: 1px solid rgba(0,0,0,0.06);
  border-radius: 18px;
  padding: 18px 18px;
  box-shadow: 0 10px 30px rgba(0,0,0,0.06);
}

/* Hero title */
.h1 {
  font-size: 54px;
  font-weight: 900;
  letter-spacing: -0.03em;
  margin: 0;
  line-height: 1.0;
}
.sub {
  color: rgba(0,0,0,0.60);
  font-size: 18px;
  margin-top: 10px;
}

/* Muted label */
.muted { color: rgba(0,0,0,0.55); font-size: 13px; }

/* Button */
div.stButton > button {
  border-radius: 14px;
  padding: 12px 16px;
  font-weight: 800;
}
</style>
        """,
        unsafe_allow_html=True,
    )

inject_css()

# -----------------------------------------------------------------------------
# LOGIN (PIN)
# -----------------------------------------------------------------------------
def render_pin_login():
    st.markdown(
        """
<div style="height:14px"></div>
<div class="card" style="padding:26px 26px;">
  <div class="muted" style="margin-bottom:12px;">Acesso por PIN</div>
  <div class="h1">Omnisfera</div>
  <div class="sub">Digite o PIN da escola para acessar o ambiente.</div>
</div>
<div style="height:18px"></div>
        """,
        unsafe_allow_html=True,
    )

    colL, colC, colR = st.columns([1, 2, 1])
    with colC:
        with st.form("pin_form", clear_on_submit=False):
            pin = st.text_input("PIN da escola", placeholder="Ex.: DEMO-2026")
            entrar = st.form_submit_button("Validar e entrar")
            if entrar:
                pin = (pin or "").strip()
                if len(pin) < 3:
                    st.error("Digite um PIN válido.")
                    return

                ws = rpc_workspace_from_pin(pin)
                if ws:
                    st.session_state.workspace_id = ws["id"]
                    st.session_state.workspace_name = ws.get("name") or "Workspace"
                    st.session_state.autenticado = True
                    st.rerun()
                else:
                    st.error("PIN inválido ou workspace não encontrado.")

    st.caption("Se estiver em desenvolvimento, valide primeiro se o Supabase está conectado.")
    st.write("Supabase conectado:", supabase_ok())

# -----------------------------------------------------------------------------
# APP SHELL (SIDEBAR)
# -----------------------------------------------------------------------------
def render_sidebar_nav():
    with st.sidebar:
        st.markdown("## 🌿 Omnisfera")
        st.caption("Ambiente por PIN")

        if st.session_state.workspace_name:
            st.markdown(
                f"""
<div class="card" style="padding:12px 14px;">
  <div class="muted">Escola</div>
  <div style="font-size:18px; font-weight:900; margin-top:2px;">
    {st.session_state.workspace_name}
  </div>
  <div class="muted" style="margin-top:6px;">
    {datetime.now().strftime('%d/%m/%Y %H:%M')}
  </div>
</div>
                """,
                unsafe_allow_html=True,
            )

        st.divider()

        # Menu (ajuste conforme suas páginas existentes)
        choice = st.radio(
            "Navegação",
            options=[
                "Início",
                "Alunos",
                "PEI",
                "PAE",
                "Hub Inclusão",
                "Diário de Bordo",
                "Monitoramento & Avaliação",
            ],
            index=0,
            label_visibility="collapsed",
        )

        st.divider()

        col1, col2 = st.columns(2)
        with col1:
            if st.button("Sair"):
                st.session_state.workspace_id = None
                st.session_state.workspace_name = None
                st.session_state.autenticado = False
                st.rerun()
        with col2:
            st.write("")  # espaçador

    return choice

# -----------------------------------------------------------------------------
# ROUTING PARA MULTIPAGE (st.switch_page)
# -----------------------------------------------------------------------------
def go_to(choice: str):
    """
    Mapeie para suas páginas reais.
    Seu repositório (print) sugere:
      pages/0_Alunos.py
      pages/1_PEI.py
      pages/2_PAE.py
      pages/3_Hub_Inclusao.py
      pages/4_Diario_de_Bordo.py
      pages/5_Monitoramento_Avaliacao.py
      pages/home.py (se existir) OU uma home interna aqui
    """
    mapping = {
        "Início": None,  # renderiza home aqui
        "Alunos": "pages/0_Alunos.py",
        "PEI": "pages/1_PEI.py",
        "PAE": "pages/2_PAE.py",
        "Hub Inclusão": "pages/3_Hub_Inclusao.py",
        "Diário de Bordo": "pages/4_Diario_de_Bordo.py",
        "Monitoramento & Avaliação": "pages/5_Monitoramento_Avaliacao.py",
    }
    target = mapping.get(choice)
    if target:
        try:
            st.switch_page(target)
        except Exception:
            st.warning(f"Não consegui abrir {target}. Confirme o nome/arquivo em /pages.")
    # Se for Início, não faz nada (fica no streamlit_app.py)

# -----------------------------------------------------------------------------
# HOME (quando autenticado)
# -----------------------------------------------------------------------------
def render_home_authenticated():
    st.markdown(
        f"""
<div class="card">
  <div style="display:flex; justify-content:space-between; align-items:center; gap:16px;">
    <div>
      <div class="muted">Escola</div>
      <div style="font-size:28px; font-weight:900; letter-spacing:-0.02em;">
        {st.session_state.workspace_name}
      </div>
      <div class="muted" style="margin-top:6px;">
        Ambiente liberado via PIN • {datetime.now().strftime('%d/%m/%Y %H:%M')}
      </div>
    </div>
    <div style="text-align:right;">
      <div class="muted">Workspace ID</div>
      <div style="font-family: ui-monospace, SFMono-Regular, Menlo, monospace; font-size:13px;">
        {st.session_state.workspace_id}
      </div>
    </div>
  </div>
</div>
<div style="height:14px"></div>
        """,
        unsafe_allow_html=True,
    )

    # Cards rápidos
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(
            """
<div class="card">
  <div class="muted">Atalho</div>
  <div style="font-size:18px; font-weight:900; margin-top:2px;">Cadastrar aluno</div>
  <div class="muted" style="margin-top:8px;">Abra a aba Alunos para criar e gerenciar estudantes.</div>
</div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("Ir para Alunos"):
            go_to("Alunos")

    with c2:
        st.markdown(
            """
<div class="card">
  <div class="muted">Atalho</div>
  <div style="font-size:18px; font-weight:900; margin-top:2px;">Abrir PEI</div>
  <div class="muted" style="margin-top:8px;">Monte o plano individual e vincule ao aluno.</div>
</div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("Ir para PEI"):
            go_to("PEI")

    with c3:
        st.markdown(
            """
<div class="card">
  <div class="muted">Status</div>
  <div style="font-size:18px; font-weight:900; margin-top:2px;">Supabase</div>
  <div class="muted" style="margin-top:8px;">Conectividade do backend e RPC por PIN.</div>
</div>
            """,
            unsafe_allow_html=True,
        )
        st.write("Conectado:", supabase_ok())

    st.divider()
    st.subheader("Próximos passos")
    st.write(
        "- Confirmar que todas as páginas em `/pages` usam `st.session_state.workspace_id` para filtrar dados.\n"
        "- Criar tabelas (students, peis, pae etc.) com coluna `workspace_id`.\n"
        "- Criar políticas/RPCs para inserir/ler por workspace."
    )

# -----------------------------------------------------------------------------
# MAIN
# -----------------------------------------------------------------------------
if not st.session_state.autenticado:
    render_pin_login()
else:
    choice = render_sidebar_nav()

    # Se escolher algo diferente de Início, tenta abrir a page correspondente
    if choice != "Início":
        go_to(choice)
        st.stop()

    # Início
    render_home_authenticated()
