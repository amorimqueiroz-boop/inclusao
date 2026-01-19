import streamlit as st
from datetime import date

from _client import get_supabase_user

# ==============================================================================
# 0) CONFIG
# ==============================================================================
st.set_page_config(
    page_title="Omnisfera | Alunos",
    page_icon="👥",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ==============================================================================
# 1) GUARDAS (LOGIN + SUPABASE)
# ==============================================================================
def _require_app_login():
    if "autenticado" not in st.session_state or not st.session_state["autenticado"]:
        st.error("🔒 Acesso Negado. Faça login na Home.")
        st.stop()

def _require_supabase_session():
    if "supabase_jwt" not in st.session_state or not st.session_state["supabase_jwt"]:
        st.warning("⚠️ Para gerenciar alunos, é necessário login Supabase (JWT). Volte na Home e faça o login Supabase.")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("🏠 Voltar Home", use_container_width=True, type="primary"):
                st.switch_page("Home.py")
        with c2:
            if st.button("🔄 Recarregar", use_container_width=True):
                st.rerun()
        st.stop()

    if "supabase_user_id" not in st.session_state or not st.session_state["supabase_user_id"]:
        st.warning("⚠️ ID do usuário Supabase não encontrado. Volte na Home e faça o login Supabase novamente.")
        if st.button("🏠 Voltar Home", use_container_width=True, type="primary"):
            st.switch_page("Home.py")
        st.stop()

def sb():
    return get_supabase_user(st.session_state["supabase_jwt"])

_require_app_login()
_require_supabase_session()

OWNER_ID = st.session_state["supabase_user_id"]

# ==============================================================================
# 2) DB HELPERS (students)
# ==============================================================================
def db_list_students(search: str | None = None):
    q = (
        sb()
        .table("students")
        .select("id, owner_id, name, birth_date, grade, class_group, diagnosis, created_at, updated_at")
        .eq("owner_id", OWNER_ID)
        .order("name", desc=False)
    )
    if search:
        # ilike no supabase: %texto%
        q = q.ilike("name", f"%{search}%")
    res = q.execute()
    return res.data or []

def db_create_student(payload: dict):
    res = sb().table("students").insert(payload).execute()
    return (res.data or [None])[0]

def db_update_student(student_id: str, payload: dict):
    sb().table("students").update(payload).eq("id", student_id).execute()

def db_delete_student(student_id: str):
    sb().table("students").delete().eq("id", student_id).execute()

def _set_selected_student(row: dict):
    st.session_state["selected_student_id"] = row["id"]
    st.session_state["selected_student_name"] = row.get("name") or ""
    # campos extras úteis (opcional)
    st.session_state["selected_student_grade"] = row.get("grade")
    st.session_state["selected_student_class_group"] = row.get("class_group")
    st.session_state["selected_student_birth_date"] = row.get("birth_date")
    st.session_state["selected_student_diagnosis"] = row.get("diagnosis")

# ==============================================================================
# 3) UI
# ==============================================================================
st.title("👥 Alunos")
st.caption("Crie, selecione e gerencie estudantes. A seleção aqui é usada no PEI, PAEE e HUB.")

# Top actions
top_c1, top_c2, top_c3, top_c4 = st.columns([2, 2, 2, 2])
with top_c1:
    if st.button("📘 Ir para PEI", use_container_width=True, type="primary"):
        st.switch_page("pages/1_PEI.py")
with top_c2:
    if st.button("🧩 Ir para PAEE", use_container_width=True):
        st.switch_page("pages/2_PAE.py")
with top_c3:
    if st.button("🚀 Ir para HUB", use_container_width=True):
        st.switch_page("pages/3_Hub_Inclusao.py")
with top_c4:
    if st.button("🏠 Home", use_container_width=True):
        st.switch_page("Home.py")

st.divider()

# Search + list
left, right = st.columns([1.2, 1])

with left:
    st.subheader("📚 Lista de alunos")
    search = st.text_input("Buscar por nome", placeholder="Ex: Ana, João, Miguel...")
    rows = db_list_students(search.strip() if search else None)

    if not rows:
        st.info("Nenhum aluno encontrado. Crie um aluno no painel ao lado.")
    else:
        # Mostra cards simples
        for r in rows:
            with st.container(border=True):
                c1, c2, c3 = st.columns([3, 2, 2])

                # resumo
                idade = ""
                if r.get("birth_date"):
                    try:
                        born = date.fromisoformat(str(r["birth_date"])[:10])
                        today = date.today()
                        yrs = today.year - born.year - ((today.month, today.day) < (born.month, born.day))
                        idade = f"{yrs} anos"
                    except:
                        idade = ""

                c1.markdown(f"**{r.get('name','(sem nome)')}**")
                c1.caption(f"Série: {r.get('grade') or '-'} | Turma: {r.get('class_group') or '-'}")
                if r.get("diagnosis"):
                    c1.caption(f"Diagnóstico: {r.get('diagnosis')}")
                if idade:
                    c1.caption(f"Idade: {idade}")

                # selecionar
                if c2.button("✅ Selecionar", key=f"sel_{r['id']}", use_container_width=True, type="primary"):
                    _set_selected_student(r)
                    st.success(f"Aluno selecionado: {r.get('name')}")
                    st.rerun()

                # ações rápidas
                if c3.button("⚙️ Editar", key=f"edit_{r['id']}", use_container_width=True):
                    st.session_state["edit_student_id"] = r["id"]
                    st.rerun()

# Create / edit panel
with right:
    st.subheader("➕ Criar / Editar aluno")

    edit_id = st.session_state.get("edit_student_id")

    # Se tem edit_id, carrega o registro para editar
    current = None
    if edit_id:
        all_rows = db_list_students()  # pequeno, ok
        current = next((x for x in all_rows if x["id"] == edit_id), None)

    with st.container(border=True):
        if current:
            st.markdown("### ✏️ Editando")
        else:
            st.markdown("### ✨ Novo aluno")

        nome = st.text_input("Nome", value=(current.get("name") if current else ""), placeholder="Nome do estudante")
        birth = None
        if current and current.get("birth_date"):
            try:
                birth = date.fromisoformat(str(current["birth_date"])[:10])
            except:
                birth = None

        nasc = st.date_input("Nascimento", value=birth or date(2015, 1, 1))
        grade = st.text_input("Série/Ano", value=(current.get("grade") if current else ""), placeholder="Ex: 7º Ano")
        turma = st.text_input("Turma", value=(current.get("class_group") if current else ""), placeholder="Ex: A")
        diag = st.text_input("Diagnóstico", value=(current.get("diagnosis") if current else ""), placeholder="Opcional")

        st.markdown("---")

        btn_c1, btn_c2 = st.columns(2)

        if current:
            with btn_c1:
                if st.button("💾 Salvar alterações", use_container_width=True, type="primary"):
                    if not nome.strip():
                        st.warning("Informe o nome.")
                    else:
                        db_update_student(
                            current["id"],
                            {
                                "name": nome.strip(),
                                "birth_date": nasc.isoformat(),
                                "grade": grade.strip() if grade else None,
                                "class_group": turma.strip() if turma else None,
                                "diagnosis": diag.strip() if diag else None,
                            },
                        )
                        st.success("Aluno atualizado ✅")
                        st.session_state["edit_student_id"] = None
                        st.rerun()

            with btn_c2:
                if st.button("🗑️ Excluir", use_container_width=True):
                    db_delete_student(current["id"])
                    st.warning("Aluno excluído.")
                    # se era o selecionado, limpa
                    if st.session_state.get("selected_student_id") == current["id"]:
                        st.session_state["selected_student_id"] = None
                        st.session_state["selected_student_name"] = None
                    st.session_state["edit_student_id"] = None
                    st.rerun()

            st.markdown("---")
            if st.button("❌ Cancelar edição", use_container_width=True):
                st.session_state["edit_student_id"] = None
                st.rerun()

        else:
            if st.button("➕ Criar aluno", use_container_width=True, type="primary"):
                if not nome.strip():
                    st.warning("Informe o nome.")
                else:
                    created = db_create_student(
                        {
                            "owner_id": OWNER_ID,
                            "name": nome.strip(),
                            "birth_date": nasc.isoformat(),
                            "grade": grade.strip() if grade else None,
                            "class_group": turma.strip() if turma else None,
                            "diagnosis": diag.strip() if diag else None,
                        }
                    )
                    if created:
                        _set_selected_student(created)
                        st.success("Aluno criado e selecionado ✅")
                        st.rerun()
                    else:
                        st.error("Não foi possível criar. Verifique RLS/policies do Supabase.")
