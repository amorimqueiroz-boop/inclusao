import streamlit as st
from datetime import date
import base64
import os
import time

# Supabase
from supabase import create_client

# --- ESCONDE O MENU PADRÃO (Pages / streamlit_app / etc.) ---
st.markdown("""
<style>
/* Esconde o menu de páginas padrão do Streamlit */
[data-testid="stSidebarNav"] { display: none !important; }
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    # Seu bloco atual de usuário/sair pode ficar, mas antes coloca o NAV custom
    st.markdown("### 🧭 Navegação")

    # HOME (aqui na home só dá rerun pra “voltar pro topo”)
    if st.button("🏠 Home", use_container_width=True):
        st.rerun()

    col1, col2 = st.columns(2)
    with col1:
        if st.button("📘 PEI", use_container_width=True):
            st.switch_page("pages/1_PEI.py")
    with col2:
        if st.button("🧩 PAEE", use_container_width=True):
            st.switch_page("pages/2_PAE.py")

    if st.button("🚀 Hub", use_container_width=True):
        st.switch_page("pages/3_Hub_Inclusao.py")

    st.markdown("---")

    # (depois disso, mantém seu bloco atual)
    st.markdown(f"**👤 {st.session_state.get('usuario_nome', '')}**")
    st.caption(st.session_state.get("usuario_cargo", ""))
    if st.button("Sair", use_container_width=True):
        st.session_state["autenticado"] = False
        st.rerun()


# ==============================================================================
# 1. CONFIGURAÇÃO INICIAL E AMBIENTE
# ==============================================================================
APP_VERSION = "v128.0 (Leitura Blindada)"

try:
    IS_TEST_ENV = st.secrets.get("ENV") == "TESTE"
except Exception:
    IS_TEST_ENV = False

titulo_pag = "[TESTE] Omnisfera" if IS_TEST_ENV else "Omnisfera | Ecossistema"
icone_pag = "omni_icone.png" if os.path.exists("omni_icone.png") else "🌐"

st.set_page_config(
    page_title=titulo_pag,
    page_icon=icone_pag,
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==============================================================================
# 1.1. ESTADO BASE (ALUNO) — mantém compatível com suas páginas
# ==============================================================================
default_state = {
    "nome": "",
    "nasc": date(2015, 1, 1),
    "serie": None,
    "turma": "",
    "diagnostico": "",
    "lista_medicamentos": [],
    "composicao_familiar_tags": [],
    "historico": "",
    "familia": "",
    "hiperfoco": "",
    "potencias": [],
    "rede_apoio": [],
    "orientacoes_especialistas": "",
    "checklist_evidencias": {},
    "nivel_alfabetizacao": "Não se aplica (Educação Infantil)",
    "barreiras_selecionadas": {},
    "niveis_suporte": {},
    "estrategias_acesso": [],
    "estrategias_ensino": [],
    "estrategias_avaliacao": [],
    "ia_sugestao": "",
    "checklist_hub": {},
    # útil para navegação/CRUD
    "student_id": None,
}

if "dados" not in st.session_state:
    st.session_state.dados = default_state.copy()

# ==============================================================================
# 1.2. SUPABASE (somente) — client + helpers
# ==============================================================================
@st.cache_resource
def get_sb():
    url = st.secrets.get("SUPABASE_URL", "")
    key = st.secrets.get("SUPABASE_ANON_KEY", "")
    if not url or not key:
        return None
    return create_client(url, key)

sb = get_sb()

def get_workspace_id():
    """
    Se você já usa PIN/RPC no streamlit_app.py, normalmente workspace_id está no session_state.
    Aqui só lemos, sem criar guard/redirect pra não dar loop.
    """
    return st.session_state.get("workspace_id")  # <- ajuste se o seu nome for outro

def sb_list_students():
    if not sb:
        return []
    ws = get_workspace_id()
    q = sb.table("students").select("id,name,birth_date,grade,class_group,diagnosis,created_at")
    if ws:
        q = q.eq("workspace_id", ws)
    res = q.order("created_at", desc=True).execute()
    return res.data or []

def sb_delete_student(student_id: str):
    if not sb:
        return False, "Supabase não configurado."
    ws = get_workspace_id()
    q = sb.table("students").delete().eq("id", student_id)
    if ws:
        q = q.eq("workspace_id", ws)
    q.execute()
    return True, "Aluno removido."

def load_student_to_session(row: dict):
    st.session_state.dados["student_id"] = row.get("id")
    st.session_state.dados["nome"] = row.get("name", "") or ""
    st.session_state.dados["serie"] = row.get("grade", None)
    st.session_state.dados["turma"] = row.get("class_group", "") or ""
    st.session_state.dados["diagnostico"] = row.get("diagnosis", "") or ""

    bd = row.get("birth_date")
    if isinstance(bd, str):
        try:
            st.session_state.dados["nasc"] = date.fromisoformat(bd)
        except Exception:
            pass

# cache leve em session_state para UX (sem bater no banco a cada rerun)
if "banco_estudantes" not in st.session_state:
    st.session_state.banco_estudantes = sb_list_students() if sb else []

# ==============================================================================
# 2. UTILITÁRIOS (imagens base64)
# ==============================================================================
def get_base64_image(image_path: str) -> str:
    if not os.path.exists(image_path):
        return ""
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

# ==============================================================================
# 3. SISTEMA DE SEGURANÇA (mantém seu gate)
# ==============================================================================
if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False

if not st.session_state["autenticado"]:
    st.markdown(
        """<style>section[data-testid="stSidebar"] { display: none !important; }</style>""",
        unsafe_allow_html=True,
    )
    c1, c_login, c2 = st.columns([1, 2, 1])
    with c_login:
        st.markdown(
            """
            <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&family=Nunito:wght@400;600;700&display=swap');
            html, body, [class*="css"] { font-family: 'Nunito', sans-serif; background:#F7FAFC; }
            .login-container {
                background: white; padding: 30px; border-radius: 20px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.06);
                text-align: center; border: 1px solid #E2E8F0;
                max-width: 480px; margin: 40px auto;
            }
            @keyframes spin { from { transform: rotate(0deg);} to { transform: rotate(360deg);} }
            </style>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("<div class='login-container'>", unsafe_allow_html=True)
        img_icone = get_base64_image("omni_icone.png")
        if img_icone:
            st.markdown(
                f"<img src='data:image/png;base64,{img_icone}' style='height:80px; animation: spin 45s linear infinite;'>",
                unsafe_allow_html=True,
            )
        st.markdown("<h2 style='color:#0F52BA; margin:10px 0;'>OMNISFERA</h2>", unsafe_allow_html=True)

        if IS_TEST_ENV:
            if st.button("🚀 ENTRAR (MODO TESTE)", use_container_width=True):
                st.session_state["autenticado"] = True
                st.session_state["usuario_nome"] = "Visitante Teste"
                st.rerun()
        else:
            nome = st.text_input("Nome", placeholder="Seu Nome")
            cargo = st.text_input("Cargo", placeholder="Seu Cargo")
            senha = st.text_input("Senha", type="password", placeholder="Senha de Acesso")

            if st.button("ACESSAR", use_container_width=True):
                hoje = date.today()
                senha_mestra = "PEI_START_2026" if hoje <= date(2026, 1, 19) else "OMNI_PRO"

                if senha == senha_mestra and nome:
                    st.session_state["autenticado"] = True
                    st.session_state["usuario_nome"] = nome
                    st.session_state["usuario_cargo"] = cargo
                    st.rerun()
                else:
                    st.error("Dados incorretos.")

        st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# ==============================================================================
# 4. TOPBAR OMNISFERA (SÓ HOME) — logo girando + badge + CSS seguro
# ==============================================================================
if IS_TEST_ENV:
    card_bg, card_border, display_text, footer_visibility = (
        "rgba(255, 220, 50, 0.95)",
        "rgba(200, 160, 0, 0.5)",
        "OMNISFERA | TESTE",
        "visible",
    )
else:
    card_bg, card_border, display_text, footer_visibility = (
        "rgba(255, 255, 255, 0.85)",
        "rgba(255, 255, 255, 0.6)",
        f"OMNISFERA {APP_VERSION}",
        "hidden",
    )

st.markdown(
    f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Nunito:wght@400;600;700&display=swap');

html, body, [class*="css"] {{
  font-family: 'Nunito', sans-serif;
  color: #2D3748;
  background-color: #F7FAFC;
}}

.block-container {{
  padding-top: 130px !important;
  padding-bottom: 2rem !important;
}}

.logo-container {{
  display: flex;
  align-items: center;
  justify-content: flex-start;
  gap: 15px;

  position: fixed;
  top: 0; left: 0;
  width: 100%;
  height: 90px;

  background-color: rgba(247, 250, 252, 0.85);
  backdrop-filter: blur(12px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.5);

  z-index: 99999;
  box-shadow: 0 4px 15px rgba(0,0,0,0.03);
  padding-left: 40px;
  padding-top: 5px;
}}

.header-subtitle-text {{
  font-family: 'Nunito', sans-serif;
  font-weight: 600;
  font-size: 1rem;
  color: #718096;

  border-left: 2px solid #CBD5E0;
  padding-left: 15px;

  height: 40px;
  display: flex;
  align-items: center;
}}

.logo-icon-spin {{
  height: 75px;
  width: auto;
  animation: spin 45s linear infinite;
}}
.logo-text-static {{
  height: 45px;
  width: auto;
}}

.omni-badge {{
  position: fixed;
  top: 15px;
  right: 15px;

  background: {card_bg};
  border: 1px solid {card_border};
  backdrop-filter: blur(12px);

  padding: 5px 15px;
  min-width: 150px;
  border-radius: 12px;

  box-shadow: 0 4px 10px rgba(0,0,0,0.06);
  z-index: 999990;

  display: flex;
  align-items: center;
  justify-content: center;
  pointer-events: none;
}}

.omni-text {{
  font-family: 'Inter', sans-serif;
  font-weight: 800;
  font-size: 0.6rem;
  color: #2D3748;
  letter-spacing: 1.5px;
  text-transform: uppercase;
}}

@keyframes spin {{
  from {{ transform: rotate(0deg); }}
  to {{ transform: rotate(360deg); }}
}}

/* Home visual */
.dash-hero {{
  background: radial-gradient(circle at top right, #0F52BA, #062B61);
  border-radius: 16px;
  margin: 10px 0 20px 0;
  box-shadow: 0 10px 25px -5px rgba(15, 82, 186, 0.3);
  color: white;
  padding: 25px 35px;
  display: flex;
  align-items: center;
  border: 1px solid rgba(255,255,255,0.1);
  min-height: 100px;
}}
.hero-title {{
  font-family: 'Inter', sans-serif;
  font-weight: 700;
  font-size: 1.5rem;
  margin: 0;
}}

.nav-btn-card {{
  background: white;
  border-radius: 16px;
  padding: 15px;
  border: 1px solid #E2E8F0;
  box-shadow: 0 2px 5px rgba(0,0,0,0.02);
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 130px;
  position: relative;
}}
.nav-icon {{ height: 45px; width: auto; object-fit: contain; margin-bottom: 10px; }}
.nav-desc {{ font-size: 0.75rem; color: #718096; font-weight: 500; }}

.b-blue {{ border-bottom: 4px solid #3182CE; }}
.b-purple {{ border-bottom: 4px solid #805AD5; }}
.b-teal {{ border-bottom: 4px solid #38B2AC; }}

[data-testid="stHeader"] {{
  visibility: hidden !important;
  height: 0px !important;
}}
footer {{
  visibility: {footer_visibility} !important;
}}
</style>
""",
    unsafe_allow_html=True,
)

icone_b64 = get_base64_image("omni_icone.png")
texto_b64 = get_base64_image("omni_texto.png")

logo_icon_html = (
    f'<img src="data:image/png;base64,{icone_b64}" class="logo-icon-spin">'
    if icone_b64
    else '<div style="width:75px;height:75px;border-radius:20px;display:flex;align-items:center;justify-content:center;background:white;border:1px solid #E2E8F0;">🌐</div>'
)
logo_text_html = (
    f'<img src="data:image/png;base64,{texto_b64}" class="logo-text-static">'
    if texto_b64
    else '<div style="font-family:Inter,sans-serif;font-weight:800;font-size:1.2rem;color:#0F52BA;">OMNISFERA</div>'
)

st.markdown(
    f"""
<div class="logo-container">
  {logo_icon_html}
  {logo_text_html}
  <div class="header-subtitle-text">Ecossistema de Inteligência Pedagógica</div>
</div>
<div class="omni-badge"><span class="omni-text">{display_text}</span></div>
""",
    unsafe_allow_html=True,
)

# ==============================================================================
# 5. HOME (conteúdo)
# ==============================================================================

# Sidebar
with st.sidebar:
    st.markdown(f"**👤 {st.session_state.get('usuario_nome', '')}**")
    st.caption(st.session_state.get("usuario_cargo", ""))
    st.markdown("---")
    if st.button("Sair"):
        st.session_state["autenticado"] = False
        st.rerun()

# Hero
primeiro_nome = ""
try:
    primeiro_nome = st.session_state.get("usuario_nome", "").split()[0]
except Exception:
    primeiro_nome = ""

st.markdown(
    f"""<div class="dash-hero"><div class="hero-title">Olá, {primeiro_nome}!</div></div>""",
    unsafe_allow_html=True,
)

# Ferramentas (Cards)
st.markdown("### 🚀 Acesso Rápido")
c1, c2, c3 = st.columns(3)

def render_card_func(col, img_b64, desc, key, path, border):
    with col:
        img_html = (
            f'<img src="data:image/png;base64,{img_b64}" class="nav-icon">'
            if img_b64
            else '<div style="font-size:2.2rem; line-height:1;">🌐</div>'
        )
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

render_card_func(c1, get_base64_image("360.png"), "Plano de Ensino (PEI)", "btn_pei", "pages/1_PEI.py", "b-blue")
render_card_func(c2, get_base64_image("pae.png"), "Sala de Recursos (PAEE)", "btn_paee", "pages/2_PAE.py", "b-purple")
render_card_func(c3, get_base64_image("hub.png"), "Hub de Inclusão", "btn_hub", "pages/3_Hub_Inclusao.py", "b-teal")

# --- LISTA DE ALUNOS (SUPABASE) ---
st.markdown("---")
st.markdown("### 🗄️ Banco de Estudantes (Supabase)")

if st.session_state.dados.get("nome"):
    st.success(f"✅ Aluno Ativo: **{st.session_state.dados['nome']}**")
else:
    st.info("👇 Selecione um aluno para começar ou vá ao PEI para criar um novo.")

if not sb:
    st.error("❌ Supabase não configurado. Verifique SUPABASE_URL e SUPABASE_ANON_KEY em st.secrets.")
else:
    colA, colB = st.columns([1, 3])
    with colA:
        if st.button("🔄 Recarregar lista", use_container_width=True):
            st.session_state.banco_estudantes = sb_list_students()
            st.rerun()
    with colB:
        ws = get_workspace_id()
        if ws:
            st.caption(f"Workspace ativo: {ws}")
        else:
            st.caption("Workspace_id não encontrado no session_state. Listando sem filtro de workspace.")

    alunos = st.session_state.banco_estudantes or []
    if not alunos:
        st.warning("Nenhum aluno encontrado.")
    else:
        for i, aluno in enumerate(alunos):
            nome = aluno.get("name", "")
            if not nome:
                continue

            with st.container():
                c_info, c_act = st.columns([4, 1])

                with c_info:
                    st.markdown(f"**{nome}** | {aluno.get('grade', '-')}")
                    st.caption(f"Diagnóstico: {aluno.get('diagnosis', '---')}")

                with c_act:
                    if st.button("📂 Carregar", key=f"load_{i}", use_container_width=True):
                        load_student_to_session(aluno)
                        st.toast(f"Carregado: {nome}", icon="✅")
                        time.sleep(0.2)
                        st.rerun()

                    if st.button("🗑️", key=f"del_{i}", type="secondary", use_container_width=True):
                        ok, msg = sb_delete_student(aluno.get("id"))
                        if ok:
                            st.success(msg)
                            st.session_state.banco_estudantes = sb_list_students()
                            st.rerun()
                        else:
                            st.error(msg)

                st.markdown("<hr style='margin:5px 0;'>", unsafe_allow_html=True)

# Footer
st.markdown(
    "<div style='text-align: center; color: #CBD5E0; font-size: 0.7rem; margin-top: 40px;'>Omnisfera desenvolvida por RODRIGO A. QUEIROZ</div>",
    unsafe_allow_html=True,
)
