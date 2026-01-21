import streamlit as st
from _client import get_supabase

supabase = get_supabase()

st.title("Alunos")

st.write("Supabase conectado:", supabase is not None)

# workspace_id vem do login por PIN
workspace_id = st.session_state.get("workspace_id")

if not workspace_id:
    st.warning("Workspace não definido.")
    st.stop()

# Exemplo: listar alunos do workspace
res = (
    supabase
    .table("students")
    .select("*")
    .eq("workspace_id", workspace_id)
    .order("name")
    .execute()
)

if res.data:
    st.dataframe(res.data)
else:
    st.info("Nenhum aluno cadastrado.")
