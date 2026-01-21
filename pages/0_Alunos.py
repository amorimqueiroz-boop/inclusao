import streamlit as st
from datetime import date

# Ajuste o import conforme seu projeto:
# - se o seu _client.py tem get_supabase(), ótimo.
# - se tiver outro nome, me diga que eu adapto.
from _client import get_supabase


st.set_page_config(page_title="Omnisfera • Alunos", layout="wide")


# -----------------------------
# Helpers
# -----------------------------
def _require_workspace():
    ws_id = st.session_state.get("workspace_id")
    ws_name = st.session_state.get("workspace_name")

    if not ws_id:
        st.error("Workspace não definido. Volte ao Início e valide o PIN novamente.")
        st.stop()

    return ws_id, ws_name


def _fetch_students(sb, workspace_id: str):
    res = (
        sb.table("students")
        .select("id, name, birth_date, grade, class_group, diagnosis, created_at, updated_at")
        .eq("workspace_id", workspace_id)
        .order("name", desc=False)
        .execute()
    )
    return res.data or []


def _insert_student(sb, workspace_id: str, payload: dict):
    payload = {k: v for k, v in payload.items() if v is not None}
    payload["workspace_id"] = workspace_id
    res = sb.table("students").insert(payload).execute()
    return res.data


def _update_student(sb, student_id: str, workspace_id: str, payload: dict):
    payload = {k: v for k, v in payload.items() if v is not None}
    res = (
        sb.table("students")
        .update(payload)
        .eq("id", student_id)
        .eq("workspace_id", workspace_id)  # proteção extra no app
        .execute()
    )
    return res.data


def _delete_student(sb, student_id: str, workspace_id: str):
    res = (
        sb.table("students")
        .delete()
        .eq("id", student_id)
        .eq("workspace_id", workspace_id)  # proteção extra no app
        .execute()
    )
    return res.data


# -----------------------------
# UI
# -----------------------------
st.title("Alunos")

workspace_id, workspace_name = _require_workspace()
sb = get_supabase()

with st.container():
    cols = st.columns([2, 2, 2, 2])
    with cols[0]:
        st.caption("Workspace")
        st.write(workspace_name or "—")
    with cols[1]:
        st.caption("Workspace ID")
        st.code(workspace_id)
    with cols[2]:
        st.caption("Supabase")
        # ping simples
        ok = sb is not None
        st.success("Conectado" if ok else "Desconectado")
    with cols[3]:
        if st.button("🔄 Atualizar lista", use_container_width=True):
            st.rerun()

st.divider()

# Carrega lista
students = _fetch_students(sb, workspace_id)

left, right = st.columns([1.05, 1.35], gap="large")

# -----------------------------
# Left: lista + seleção
# -----------------------------
with left:
    st.subheader("Lista de alunos")

    if not students:
        st.info("Nenhum aluno cadastrado ainda.")
        selected_id = None
    else:
        options = {f"{s['name']}": s["id"] for s in students}
        selected_label = st.selectbox(
            "Selecione um aluno para editar",
            options=list(options.keys()),
            index=0,
        )
        selected_id = options.get(selected_label)

    st.caption(f"Total: {len(students)}")

    # tabela simples
    if students:
        table_rows = []
        for s in students:
            table_rows.append({
                "Nome": s.get("name"),
                "Nascimento": s.get("birth_date"),
                "Série": s.get("grade"),
                "Turma": s.get("class_group"),
                "Diagnóstico": s.get("diagnosis"),
            })
        st.dataframe(table_rows, use_container_width=True, hide_index=True)

# -----------------------------
# Right: criar/editar
# -----------------------------
with right:
    st.subheader("Cadastrar / Editar")

    # encontra o aluno selecionado
    current = None
    if selected_id:
        current = next((s for s in students if s["id"] == selected_id), None)

    tab_new, tab_edit = st.tabs(["➕ Novo aluno", "✏️ Editar aluno"])

    with tab_new:
        with st.form("form_new", clear_on_submit=True):
            name = st.text_input("Nome do aluno *")
            birth_date = st.date_input("Data de nascimento", value=None)
            grade = st.text_input("Série/Ano")
            class_group = st.text_input("Turma")
            diagnosis = st.text_area("Diagnóstico / Observações (resumo)", height=120)

            submitted = st.form_submit_button("Salvar aluno", use_container_width=True)
            if submitted:
                if not name.strip():
                    st.error("Preencha o nome do aluno.")
                    st.stop()

                payload = {
                    "name": name.strip(),
                    "birth_date": birth_date if isinstance(birth_date, date) else None,
                    "grade": grade.strip() if grade else None,
                    "class_group": class_group.strip() if class_group else None,
                    "diagnosis": diagnosis.strip() if diagnosis else None,
                }

                try:
                    _insert_student(sb, workspace_id, payload)
                    st.success("Aluno cadastrado com sucesso.")
                    st.rerun()
                except Exception as e:
                    st.error("Falha ao cadastrar aluno.")
                    st.exception(e)

    with tab_edit:
        if not current:
            st.info("Selecione um aluno na lista para editar.")
        else:
            with st.form("form_edit"):
                name = st.text_input("Nome do aluno *", value=current.get("name") or "")
                bd = current.get("birth_date")
                birth_date = st.date_input("Data de nascimento", value=bd)
                grade = st.text_input("Série/Ano", value=current.get("grade") or "")
                class_group = st.text_input("Turma", value=current.get("class_group") or "")
                diagnosis = st.text_area("Diagnóstico / Observações (resumo)", value=current.get("diagnosis") or "", height=120)

                c1, c2 = st.columns([1, 1])
                with c1:
                    save = st.form_submit_button("Salvar alterações", use_container_width=True)
                with c2:
                    delete = st.form_submit_button("Excluir aluno", use_container_width=True)

                if save:
                    if not name.strip():
                        st.error("Preencha o nome do aluno.")
                        st.stop()

                    payload = {
                        "name": name.strip(),
                        "birth_date": birth_date if isinstance(birth_date, date) else None,
                        "grade": grade.strip() if grade else None,
                        "class_group": class_group.strip() if class_group else None,
                        "diagnosis": diagnosis.strip() if diagnosis else None,
                        "updated_at": "now()",  # se seu Supabase aceitar; senão, remova
                    }

                    try:
                        # Se "now()" não funcionar via postgrest, remova updated_at do payload.
                        _update_student(sb, current["id"], workspace_id, payload)
                        st.success("Aluno atualizado.")
                        st.rerun()
                    except Exception as e:
                        # fallback sem updated_at
                        try:
                            payload.pop("updated_at", None)
                            _update_student(sb, current["id"], workspace_id, payload)
                            st.success("Aluno atualizado.")
                            st.rerun()
                        except Exception as e2:
                            st.error("Falha ao atualizar.")
                            st.exception(e2)

                if delete:
                    try:
                        _delete_student(sb, current["id"], workspace_id)
                        st.success("Aluno excluído.")
                        st.rerun()
                    except Exception as e:
                        st.error("Falha ao excluir.")
                        st.exception(e)
