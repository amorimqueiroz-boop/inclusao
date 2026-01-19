import streamlit as st
from datetime import date
from _client import get_supabase

st.set_page_config(page_title="Alunos | Omnisfera", page_icon="👥", layout="wide")

# ========= Segurança (mesma lógica do seu projeto) =========
if "autenticado" not in st.session_state or not st.session_state["autenticado"]:
    st.error("🔒 Acesso Negado. Faça login na Home.")
    st.stop()

sb = get_supabase()

st.title("👥 Alunos")
st.caption("Cadastre, visualize e selecione um aluno para abrir no PEI.")

st.session_state.setdefault("selected_student_id", None)
st.session_state.setdefault("selected_student_name", None)

# ========= Helpers Supabase =========
def db_list_students():
    res = sb.table("students").select("id,name,birth_date,grade,class_name,created_at").order("created_at", desc=True).execute()
    return res.data or []

def db_create_student(name: str, birth_date: date, grade: str, class_name: str):
    payload = {
        "name": name.strip(),
        "birth_date": birth_date.isoformat() if birth_date else None,
        "grade": grade or "",
        "class_name": class_name or "",
    }
    res = sb.table("students").insert(payload).execute()
    return (res.data or [None])[0]

def db_delete_student(student_id: str):
    sb.table("students").delete().eq("id", student_id).execute()

# ========= UI: cadastrar =========
with st.expander("➕ Cadastrar novo aluno", expanded=True):
    c1, c2, c3, c4 = st.columns([3, 2, 2, 1])
    with c1:
        nome = st.text_input("Nome do aluno", placeholder="Ex: Maria Silva")
    with c2:
        nasc = st.date_input("Nascimento", value=date(2015, 1, 1))
    with c3:
        serie = st.text_input("Série/Ano", placeholder="Ex: 2º Ano (Fund. I)")
    with c4:
        turma = st.text_input("Turma", placeholder="Ex: B")

    if st.button("Salvar aluno", type="primary", use_container_width=True):
        if not nome.strip():
            st.warning("Digite o nome do aluno.")
        else:
            novo = db_create_student(nome, nasc, serie, turma)
            st.toast("Aluno cadastrado!", icon="✅")
            # seleciona automaticamente
            if novo:
                st.session_state["selected_student_id"] = novo["id"]
                st.session_state["selected_student_name"] = novo["name"]
            st.rerun()

st.divider()

# ========= UI: listar e selecionar =========
st.markdown("### 📋 Alunos cadastrados")

students = db_list_students()

if not students:
    st.info("Nenhum aluno cadastrado ainda. Cadastre acima.")
else:
    # selectbox
    nomes = [s["name"] for s in students]
    default_idx = 0
    if st.session_state.get("selected_student_name") in nomes:
        default_idx = nomes.index(st.session_state["selected_student_name"])

    escolhido = st.selectbox("Selecionar aluno para trabalhar", nomes, index=default_idx)

    aluno = next((s for s in students if s["name"] == escolhido), None)
    if aluno:
        st.session_state["selected_student_id"] = aluno["id"]
        st.session_state["selected_student_name"] = aluno["name"]

    c_go, c_clear = st.columns([2, 1])
    with c_go:
        if st.button("➡️ Abrir PEI deste aluno", use_container_width=True, type="primary"):
            st.switch_page("pages/1_PEI.py")
    with c_clear:
        if st.button("Limpar seleção", use_container_width=True):
            st.session_state["selected_student_id"] = None
            st.session_state["selected_student_name"] = None
            st.rerun()

    st.write("")
    st.markdown("#### Detalhes")
    st.write(f"**Nome:** {aluno.get('name','-')}")
    st.write(f"**Nascimento:** {aluno.get('birth_date','-')}")
    st.write(f"**Série/Ano:** {aluno.get('grade','-')}")
    st.write(f"**Turma:** {aluno.get('class_name','-')}")

    st.write("")
    with st.expander("🗑️ Excluir aluno (cuidado)"):
        st.warning("Isso remove o aluno do banco. Os PEIs associados podem ficar órfãos se você não apagar também.")
        if st.button("Excluir este aluno", use_container_width=True):
            db_delete_student(aluno["id"])
            st.toast("Aluno excluído.", icon="🗑️")
            st.session_state["selected_student_id"] = None
            st.session_state["selected_student_name"] = None
            st.rerun()
