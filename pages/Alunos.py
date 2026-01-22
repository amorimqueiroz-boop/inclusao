# pages/Alunos.py
import streamlit as st
from datetime import datetime

from supabase_client import get_supabase

# ==============================================================================
# CONFIG
# ==============================================================================
st.set_page_config(page_title="Omnisfera • Estudantes", page_icon="👥", layout="wide")


# ==============================================================================
# GATE (SEM LOGIN AQUI) — só redireciona para o começo do app
# ==============================================================================
def acesso_bloqueado(msg: str):
    st.markdown(
        f"""
        <div style="
            max-width:520px;
            margin: 110px auto 18px auto;
            padding: 26px;
            background: white;
            border-radius: 18px;
            border: 1px solid #E2E8F0;
            box-shadow: 0 20px 40px rgba(15,82,186,0.10);
            text-align: center;
        ">
            <div style="font-size:2.1rem; margin-bottom:10px;">🔐</div>
            <div style="font-weight:900; font-size:1.1rem; margin-bottom:6px; color:#0f172a;">
                Acesso restrito
            </div>
            <div style="color:#4A5568; font-weight:700; font-size:0.95rem; margin-bottom:10px;">
                {msg}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        if st.button("🔑 Voltar para o Login", use_container_width=True, type="primary"):
            # limpa sessão essencial
            for k in ["autenticado", "workspace_id", "workspace_name", "usuario_nome", "usuario_cargo"]:
                st.session_state.pop(k, None)

            # tenta voltar para o início (onde o router chama login_view)
            try:
                st.switch_page("streamlit_app.py")
            except Exception:
                # fallback super confiável: raiz do app
                st.markdown(
                    """
                    <div style="text-align:center; margin-top:10px;">
                      <a href="/" target="_self"
                         style="display:inline-block; padding:10px 14px; border-radius:12px;
                                background:#0F52BA; color:white; font-weight:900; text-decoration:none;">
                        Clique aqui para voltar ao Login
                      </a>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                st.stop()
    st.stop()


if not st.session_state.get("autenticado", False):
    acesso_bloqueado("Sessão expirada ou não iniciada.")

if not st.session_state.get("workspace_id"):
    acesso_bloqueado("Nenhum workspace vinculado ao seu acesso (PIN).")


WORKSPACE_ID = st.session_state.get("workspace_id")
WORKSPACE_NAME = st.session_state.get("workspace_name") or f"{str(WORKSPACE_ID)[:8]}…"


# ==============================================================================
# DATA
# ==============================================================================
@st.cache_data(ttl=20, show_spinner=False)
def list_students(workspace_id: str):
    sb = get_supabase()
    res = (
        sb.table("students")
        .select("id, name, birth_date, grade, class_group, diagnosis, created_at")
        .eq("workspace_id", workspace_id)
        .order("created_at", desc=True)
        .execute()
    )
    return res.data or []


def delete_student(student_id: str):
    sb = get_supabase()
    sb.table("students").delete().eq("id", student_id).execute()


def _fmt_date(s):
    if not s:
        return "—"
    # pode vir como "YYYY-MM-DD" ou ISO
    try:
        if isinstance(s, str) and "T" in s:
            return s.split("T")[0]
        if isinstance(s, str):
            return s[:10]
    except Exception:
        pass
    return "—"


# ==============================================================================
# UI
# ==============================================================================
st.title("👥 Estudantes")
st.caption(f"Gestão do workspace (PIN) — **{WORKSPACE_NAME}**")
st.write("Aqui você apenas visualiza os estudantes criados no PEI deste workspace e pode apagar quando necessário.")

top_l, top_r = st.columns([3, 1])
with top_l:
    q = st.text_input("Buscar por nome", placeholder="Digite para filtrar…", label_visibility="visible")
with top_r:
    st.markdown("#### Ações")
    if st.button("🔄 Atualizar", use_container_width=True):
        list_students.clear()
        st.rerun()

with st.spinner("Carregando estudantes..."):
    alunos = list_students(WORKSPACE_ID)

# filtro
if q and q.strip():
    qq = q.strip().lower()
    alunos = [a for a in alunos if (a.get("name") or "").lower().find(qq) >= 0]

st.divider()

if not alunos:
    st.info("Nenhum estudante encontrado neste workspace ainda. Crie um PEI para começar.")
    st.stop()

st.caption(f"**{len(alunos)}** estudante(s) exibido(s).")

# Cabeçalho
h = st.columns([3.2, 1.1, 1.1, 2.6, 1.1])
h[0].markdown("**Nome**")
h[1].markdown("**Série**")
h[2].markdown("**Turma**")
h[3].markdown("**Diagnóstico**")
h[4].markdown("**Ações**")
st.divider()

for a in alunos:
    sid = a.get("id")
    nome = a.get("name") or "—"
    serie = a.get("grade") or "—"
    turma = a.get("class_group") or "—"
    diag = a.get("diagnosis") or "—"

    row = st.columns([3.2, 1.1, 1.1, 2.6, 1.1])
    row[0].markdown(f"**{nome}**")
    row[1].write(serie)
    row[2].write(turma)
    row[3].write(diag)

    confirm_key = f"confirm_del_{sid}"
    if confirm_key not in st.session_state:
        st.session_state[confirm_key] = False

    with row[4]:
        if not st.session_state[confirm_key]:
            if st.button("🗑️", key=f"del_{sid}", use_container_width=True, help="Apagar estudante"):
                st.session_state[confirm_key] = True
                st.rerun()
        else:
            st.warning("Confirmar?")
            c1, c2 = st.columns(2)
            with c1:
                if st.button("✅", key=f"yes_{sid}", use_container_width=True):
                    try:
                        delete_student(sid)
                        list_students.clear()
                        st.session_state[confirm_key] = False
                        st.toast(f"Removido: {nome}", icon="🗑️")
                        st.rerun()
                    except Exception as e:
                        st.session_state[confirm_key] = False
                        st.error(f"Erro ao apagar: {e}")
            with c2:
                if st.button("↩️", key=f"no_{sid}", use_container_width=True):
                    st.session_state[confirm_key] = False
                    st.rerun()

    st.markdown("<hr style='margin:8px 0; border:none; border-top:1px solid #EEF2F7;'>", unsafe_allow_html=True)
