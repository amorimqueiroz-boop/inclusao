from datetime import date
import streamlit as st
import time

from ui_shell import inject_global_css, render_topbar

APP_VERSION = "v128.0 (Leitura Blindada)"
IS_TEST_ENV = (st.secrets.get("ENV") == "TESTE") if "ENV" in st.secrets else False

# --- estado base (mantém seu default_state do jeito que já está) ---
# if 'dados' not in st.session_state: st.session_state.dados = default_state.copy()

# --- Supabase client: use o que já existe na carcaça ---
# Exemplo (AJUSTE para sua forma atual de criar client):
# from supabase import create_client
# sb = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_ANON_KEY"])
sb = st.session_state.get("sb")  # se a carcaça já guarda o client aqui
workspace_id = st.session_state.get("workspace_id")

inject_global_css(APP_VERSION, IS_TEST_ENV)
render_topbar()

# Sidebar (pode manter)
with st.sidebar:
    st.markdown(f"**👤 {st.session_state.get('usuario_nome', '')}**")
    st.caption(st.session_state.get('usuario_cargo', ''))
    st.markdown("---")
    if st.button("Sair"):
        st.session_state["autenticado"] = False
        st.rerun()

# Hero
primeiro_nome = (st.session_state.get("usuario_nome","").split()[0] if st.session_state.get("usuario_nome") else "")
st.markdown(
    f"""<div class="dash-hero"><div class="hero-title">Olá, {primeiro_nome}!</div></div>""",
    unsafe_allow_html=True,
)

# Cards
st.markdown("### 🚀 Acesso Rápido")
c1, c2, c3 = st.columns(3)

def render_card(col, img_b64, desc, key, path, border, icon_html=""):
    with col:
        img_html = f'<img src="data:image/png;base64,{img_b64}" class="nav-icon">' if img_b64 else icon_html
        st.markdown(
            f"""<div class="nav-btn-card {border}">{img_html}<div class="nav-desc">{desc}</div></div>""",
            unsafe_allow_html=True,
        )
        if st.button("Acessar", key=key, use_container_width=True):
            if st.session_state.dados.get("nome"):
                st.switch_page(path)
            else:
                st.toast("⚠️ Selecione um aluno abaixo primeiro!", icon="👇")
                time.sleep(0.3)

# se você quiser manter as imagens 360/pae/hub:
import base64, os
def get_b64(path):
    if not os.path.exists(path): return ""
    with open(path,"rb") as f: return base64.b64encode(f.read()).decode()

render_card(c1, get_b64("360.png"), "Plano de Ensino (PEI)", "btn_pei", "pages/1_PEI.py", "b-blue")
render_card(c2, get_b64("pae.png"), "Sala de Recursos (PAEE)", "btn_paee", "pages/2_PAE.py", "b-purple")
render_card(c3, get_b64("hub.png"), "Hub de Inclusão", "btn_hub", "pages/3_Hub_Inclusao.py", "b-teal")

# --- Banco Supabase ---
st.markdown("---")
st.markdown("### 🗄️ Banco de Estudantes (Supabase)")

if st.session_state.dados.get("nome"):
    st.success(f"✅ Aluno Ativo: **{st.session_state.dados['nome']}**")
else:
    st.info("👇 Selecione um aluno para começar ou vá ao PEI para criar um novo.")

def supa_list_students():
    if not sb or not workspace_id:
        return []
    # Ajuste as colunas conforme sua tabela real
    res = sb.table("students").select("id,name,birth_date,grade,class_group,diagnosis,workspace_id").eq("workspace_id", workspace_id).order("created_at", desc=True).execute()
    return res.data or []

def supa_delete_student(student_id: str):
    if not sb or not workspace_id:
        return False, "Sem conexão/workspace."
    sb.table("students").delete().eq("id", student_id).eq("workspace_id", workspace_id).execute()
    return True, "Removido."

def load_student_to_session(row: dict):
    # mapeia Supabase -> seu st.session_state.dados
    st.session_state.dados["nome"] = row.get("name","")
    # birth_date pode vir str 'YYYY-MM-DD'
    bd = row.get("birth_date")
    if isinstance(bd, str):
        try: st.session_state.dados["nasc"] = date.fromisoformat(bd)
        except: pass
    st.session_state.dados["serie"] = row.get("grade")
    st.session_state.dados["turma"] = row.get("class_group","")
    st.session_state.dados["diagnostico"] = row.get("diagnosis","")
    # importante: guardar id ativo para as páginas usarem
    st.session_state.dados["student_id"] = row.get("id")

# cache leve em session_state pra não bater no banco toda hora
if "supa_students" not in st.session_state:
    st.session_state.supa_students = supa_list_students()

if st.button("🔄 Recarregar lista", use_container_width=False):
    st.session_state.supa_students = supa_list_students()
    st.rerun()

students = st.session_state.supa_students or []
if not students:
    st.warning("Nenhum aluno encontrado neste workspace.")
else:
    for i, row in enumerate(students):
        with st.container():
            c_info, c_act = st.columns([4, 1])

            with c_info:
                st.markdown(f"**{row.get('name','(sem nome)')}** | {row.get('grade','-')}")
                st.caption(f"Diagnóstico: {row.get('diagnosis','---')}")

            with c_act:
                if st.button("📂 Carregar", key=f"supa_load_{i}", use_container_width=True):
                    load_student_to_session(row)
                    st.toast(f"Carregado: {row.get('name','')}", icon="✅")
                    time.sleep(0.2)
                    st.rerun()

                if st.button("🗑️", key=f"supa_del_{i}", type="secondary", use_container_width=True):
                    ok, msg = supa_delete_student(row.get("id"))
                    if ok:
                        st.success(msg)
                        st.session_state.supa_students = supa_list_students()
                        st.rerun()
                    else:
                        st.error(msg)

            st.markdown("<hr style='margin:5px 0;'>", unsafe_allow_html=True)

st.markdown(
    "<div style='text-align:center; color:#CBD5E0; font-size:0.7rem; margin-top:40px;'>Omnisfera desenvolvida por RODRIGO A. QUEIROZ</div>",
    unsafe_allow_html=True
)
