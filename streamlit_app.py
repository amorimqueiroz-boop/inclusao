import streamlit as st
from datetime import date
import base64
import os
import time

# ==============================================================================
# 0) CONFIGURAÇÃO
# ==============================================================================
APP_VERSION = "v134.1 (Home High Design • sem login aqui)"
titulo_pag = "Omnisfera | Ecossistema"
icone_pag = "omni_icone.png" if os.path.exists("omni_icone.png") else "🌐"

st.set_page_config(
    page_title=titulo_pag,
    page_icon=icone_pag,
    layout="wide",
    initial_sidebar_state="expanded",
)


# ==============================================================================
# GATE DE ACESSO — HOME NÃO AUTENTICA
# Apenas respeita quem já liberou o acesso (PIN / Supabase)
# ==============================================================================

LOGIN_PAGE = "login_pin.py"  # <<< AJUSTE AQUI se o nome do arquivo for outro

def acesso_bloqueado(msg: str):
    st.markdown(
        f"""
        <div style="
            max-width:520px;
            margin: 120px auto;
            padding: 28px;
            background: white;
            border-radius: 18px;
            border: 1px solid #E2E8F0;
            box-shadow: 0 20px 40px rgba(15,82,186,0.12);
            text-align: center;
        ">
            <div style="font-size:2.2rem; margin-bottom:10px;">🔐</div>
            <div style="font-weight:900; font-size:1.1rem; margin-bottom:6px;">
                Acesso restrito
            </div>
            <div style="color:#4A5568; font-weight:700; font-size:0.95rem; margin-bottom:18px;">
                {msg}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🔑 Voltar para a tela de login", use_container_width=True):
            st.switch_page(LOGIN_PAGE)

    st.stop()


# 1) Não autenticado
if not st.session_state.get("autenticado", False):
    acesso_bloqueado("Faça login para acessar o Omnisfera.")

# 2) Sem escola / workspace
if not st.session_state.get("workspace_id"):
    acesso_bloqueado("Nenhuma escola vinculada ao seu acesso.")


# ==============================================================================
# 2) STATE BASE (compat)
# ==============================================================================
if "workspace_name" not in st.session_state:
    st.session_state["workspace_name"] = ""

if "usuario_nome" not in st.session_state:
    st.session_state["usuario_nome"] = "Visitante"

if "usuario_cargo" not in st.session_state:
    st.session_state["usuario_cargo"] = ""

default_state = {"nome": "", "nasc": date(2015, 1, 1), "serie": None, "turma": "", "diagnostico": "", "student_id": None}
if "dados" not in st.session_state:
    st.session_state.dados = default_state.copy()

# ==============================================================================
# 3) HELPERS
# ==============================================================================
def get_base64_image(image_path: str) -> str:
    if not image_path or not os.path.exists(image_path):
        return ""
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

def escola_vinculada() -> str:
    # principal (definido no login PIN)
    v = st.session_state.get("workspace_name")
    if isinstance(v, str) and v.strip():
        return v.strip()

    # fallback
    for k in ["escola_nome", "escola", "school_name", "workspace_label", "workspace_display"]:
        vv = st.session_state.get(k)
        if isinstance(vv, str) and vv.strip():
            return vv.strip()

    wsid = st.session_state.get("workspace_id")
    if isinstance(wsid, str) and wsid.strip():
        return f"Workspace {wsid[:8]}…"

    return ""

# ==============================================================================
# 4) CSS BASE + VISUAL HOME (GRID REAL 3 POR LINHA)
# ==============================================================================
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&family=Nunito:wght@400;600;700;800&display=swap');

html, body, [class*="css"] { font-family: 'Nunito', sans-serif; color:#1A202C; background:#F7FAFC; }

[data-testid="stSidebarNav"] { display: none !important; }
[data-testid="stHeader"] { visibility: hidden !important; height: 0px !important; }

.block-container { padding-top: 128px !important; padding-bottom: 2rem !important; }

@keyframes spin { from { transform: rotate(0deg);} to { transform: rotate(360deg);} }

/* Flaticon UIcons */
@import url('https://cdn-uicons.flaticon.com/3.0.0/uicons-solid-rounded/css/uicons-solid-rounded.css');
@import url('https://cdn-uicons.flaticon.com/3.0.0/uicons-solid-straight/css/uicons-solid-straight.css');
@import url('https://cdn-uicons.flaticon.com/3.0.0/uicons-bold-rounded/css/uicons-bold-rounded.css');

/* TOPBAR */
.header-container {
  position: fixed; top: 0; left: 0; width: 100%; height: 88px;
  background: rgba(255,255,255,0.78);
  backdrop-filter: blur(14px);
  border-bottom: 1px solid rgba(226,232,240,0.85);
  z-index: 99999;
  display: flex; align-items: center; justify-content: space-between;
  padding: 0 28px;
  box-shadow: 0 10px 30px rgba(15,82,186,0.06);
}
.header-left { display: flex; align-items: center; gap: 16px; }
.header-logo-spin { height: 54px; width: 54px; animation: spin 18s linear infinite; }
.header-logo-text { height: 38px; width: auto; }
.header-divider { height: 36px; width: 1px; background: rgba(203,213,224,0.9); margin: 0 6px; }
.header-slogan { font-weight: 900; color: #718096; letter-spacing: .2px; }
.header-badge {
  background: rgba(255,255,255,0.85);
  border: 1px solid rgba(255,255,255,0.6);
  border-radius: 14px;
  padding: 8px 12px;
  display: flex;
  flex-direction: column;
  gap: 2px;
  align-items: flex-end;
  box-shadow: 0 10px 20px rgba(15,82,186,0.07);
}
.badge-top {
  font-family: Inter, sans-serif;
  font-weight: 900;
  font-size: 0.62rem;
  letter-spacing: 1.4px;
  text-transform: uppercase;
  color: #1A202C;
}
.badge-school {
  font-weight: 900;
  font-size: 0.80rem;
  color: #2D3748;
  opacity: .92;
  max-width: 420px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* HERO */
.hero-shell {
  background:
    radial-gradient(900px 240px at 15% 10%, rgba(15,82,186,0.22), transparent 65%),
    radial-gradient(900px 240px at 85% 0%, rgba(56,178,172,0.18), transparent 60%),
    radial-gradient(circle at top right, #0F52BA, #062B61);
  border-radius: 22px;
  border: 1px solid rgba(255,255,255,0.14);
  box-shadow: 0 18px 50px rgba(15,82,186,0.24);
  padding: 22px 24px;
  color: white;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 14px;
}
.hero-title {
  font-family: Inter, sans-serif;
  font-weight: 900;
  font-size: 1.45rem;
  margin: 0;
}
.hero-sub {
  margin-top: 6px;
  font-weight: 900;
  color: rgba(255,255,255,0.86);
}
.hero-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 12px;
}
.chip {
  background: rgba(255,255,255,0.12);
  border: 1px solid rgba(255,255,255,0.14);
  padding: 6px 10px;
  border-radius: 999px;
  font-weight: 900;
  font-size: 0.76rem;
  color: rgba(255,255,255,0.92);
}
.hero-right { min-width: 220px; display: flex; justify-content: flex-end; }
.hero-pulse {
  background: rgba(255,255,255,0.10);
  border: 1px solid rgba(255,255,255,0.14);
  border-radius: 18px;
  padding: 10px 12px;
  text-align: right;
}
.hero-mini { font-weight: 900; letter-spacing: .3px; }
.hero-mini-sub { margin-top: 3px; font-weight: 900; color: rgba(255,255,255,0.86); font-size: .80rem; }

/* CARD compacto */
.home-card {
  position: relative;
  background: rgba(255,255,255,0.92);
  border-radius: 20px;
  border: 1px solid rgba(226,232,240,0.95);
  box-shadow: 0 10px 22px rgba(15,82,186,0.07);
  padding: 14px 14px;
  display: flex;
  align-items: flex-start;
  gap: 12px;
  min-height: 104px;
  transition: transform .14s ease, box-shadow .14s ease, border-color .14s ease;
  overflow: hidden;
}
.home-card:before {
  content: "";
  position: absolute;
  inset: -60px -60px auto auto;
  width: 130px;
  height: 130px;
  border-radius: 999px;
  background: rgba(15,82,186,0.07);
}
.home-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 16px 38px rgba(15,82,186,0.12);
  border-color: rgba(49,130,206,0.35);
}
.home-ic {
  width: 44px; height: 44px;
  border-radius: 15px;
  display: flex; align-items: center; justify-content: center;
  background: rgba(15,82,186,0.08);
  border: 1px solid rgba(15,82,186,0.12);
  margin-top: 1px;
}
.home-ic i { font-size: 21px; color: #0F52BA; line-height: 1; }
.home-txt { display:flex; flex-direction:column; gap:5px; min-width: 0; }
.home-title {
  font-family: Inter, sans-serif;
  font-weight: 900;
  font-size: 0.98rem;
  color: #1A202C;
  margin: 0;
}
.home-sub {
  font-size: 0.80rem;
  color: #718096;
  margin: 0;
  font-weight: 900;
  line-height: 1.22rem;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.home-tags {
  display:flex;
  flex-wrap: nowrap;
  gap: 6px;
  margin-top: 2px;
  overflow: hidden;
}
.tag {
  background: rgba(226,232,240,0.55);
  border: 1px solid rgba(226,232,240,0.9);
  color: #2D3748;
  padding: 3px 8px;
  border-radius: 999px;
  font-weight: 900;
  font-size: 0.66rem;
  letter-spacing: .2px;
  white-space: nowrap;
}
.home-cta {
  margin-top: 0px;
  font-weight: 900;
  color: #0F52BA;
  font-size: 0.76rem;
}

.b-slate { border-bottom: 4px solid #4A5568; }
.b-blue  { border-bottom: 4px solid #3182CE; }
.b-purple{ border-bottom: 4px solid #805AD5; }
.b-teal  { border-bottom: 4px solid #38B2AC; }

/* Botão invisível SEM “open” aparecendo e sem ocupar espaço */
.ghost-btn [data-testid="stButton"] > button {
  height: 1px !important;
  min-height: 1px !important;
  padding: 0 !important;
  opacity: 0 !important;
  border: 0 !important;
  margin: 0 !important;
}
</style>
""",
    unsafe_allow_html=True,
)

# ==============================================================================
# 5) TOPBAR
# ==============================================================================
esc = escola_vinculada()
icone_b64 = get_base64_image("omni_icone.png")
texto_b64 = get_base64_image("omni_texto.png")

logo_icon_html = (
    f'<img src="data:image/png;base64,{icone_b64}" class="header-logo-spin">'
    if icone_b64
    else '<div style="width:54px;height:54px;border-radius:18px;display:flex;align-items:center;justify-content:center;background:white;border:1px solid #E2E8F0;">🌐</div>'
)
logo_text_html = (
    f'<img src="data:image/png;base64,{texto_b64}" class="header-logo-text">'
    if texto_b64
    else '<div style="font-family:Inter,sans-serif;font-weight:900;font-size:1.15rem;color:#0F52BA;">OMNISFERA</div>'
)

st.markdown(
    f"""
<div class="header-container">
  <div class="header-left">
    {logo_icon_html}
    {logo_text_html}
    <div class="header-divider"></div>
    <div class="header-slogan">Ecossistema de Inteligência Pedagógica</div>
  </div>
  <div class="header-badge">
    <div class="badge-top">OMNISFERA {APP_VERSION}</div>
    {"<div class='badge-school'>🏫 "+esc+"</div>" if esc else ""}
  </div>
</div>
""",
    unsafe_allow_html=True,
)

# ==============================================================================
# 6) SIDEBAR (aponta para os mesmos destinos)
# ==============================================================================
with st.sidebar:
    st.markdown("### 🧭 Navegação")

    if st.button("👥 Estudantes", use_container_width=True):
        st.switch_page("pages/0_Alunos.py")

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
    if esc:
        st.caption("🏫 Escola vinculada")
        st.markdown(f"**{esc}**")

    st.markdown("---")
    st.markdown(f"**👤 {st.session_state.get('usuario_nome', '')}**")
    st.caption(st.session_state.get("usuario_cargo", ""))

    if st.button("Sair", use_container_width=True):
        # O arquivo de login deve cuidar da autenticação, mas deixamos um logout simples
        st.session_state["autenticado"] = False
        st.session_state["workspace_id"] = None
        st.session_state["workspace_name"] = ""
        st.rerun()

# ==============================================================================
# 7) HOME (conteúdo) — cards 3 por linha (compactos)
# ==============================================================================
primeiro_nome = (st.session_state.get("usuario_nome") or "Visitante").split()[0]

chips = ["BNCC + DUA", "PEI / PAEE", "Rubricas", "Inclusão"]
chips_html = "".join([f"<span class='chip'>{c}</span>" for c in chips])

st.markdown(
    f"""
<div class="hero-shell">
  <div>
    <div class="hero-title">Olá, {primeiro_nome}!</div>
    <div class="hero-sub">{("🏫 " + esc) if esc else "Bem-vindo(a) ao Omnisfera."}</div>
    <div class="hero-chips">{chips_html}</div>
  </div>
  <div class="hero-right">
    <div class="hero-pulse">
      <div class="hero-mini">Acesso rápido</div>
      <div class="hero-mini-sub">Seus módulos em 1 clique</div>
    </div>
  </div>
</div>
""",
    unsafe_allow_html=True,
)

st.markdown("### 🚀 Módulos")

def go(dest: str):
    if dest == "ALUNOS":
        st.switch_page("pages/0_Alunos.py")
    elif dest == "PEI":
        st.switch_page("pages/1_PEI.py")
    elif dest == "PAEE":
        st.switch_page("pages/2_PAE.py")
    elif dest == "HUB":
        st.switch_page("pages/3_Hub_Inclusao.py")
    elif dest == "DIARIO":
        st.toast("🛠️ Diário de Bordo — em breve neste build.", icon="✨")
    elif dest == "DADOS":
        st.toast("🛠️ Evolução & Dados — em breve neste build.", icon="✨")
    time.sleep(0.10)

cards = [
    ("Estudantes", "Gestão, seleção e histórico do aluno.", "fi fi-br-users", "ALUNOS", "b-slate", ["Cadastro", "Turmas"], "Abrir →"),
    ("Estratégias & PEI", "Plano Educacional Individualizado com rubricas.", "fi fi-sr-book-open-cover", "PEI", "b-blue", ["PEI 360°", "DUA"], "Abrir →"),
    ("Plano de Ação / PAEE", "Intervenções e sala de recursos.", "fi fi-ss-puzzle", "PAEE", "b-purple", ["AEE", "Ações"], "Abrir →"),
    ("Hub de Recursos", "Modelos, adaptações e ferramentas.", "fi fi-sr-rocket", "HUB", "b-teal", ["Materiais", "Provas"], "Abrir →"),
    ("Diário de Bordo", "Registro contínuo e evidências.", "fi fi-br-notebook", "DIARIO", "b-slate", ["Notas", "Evidências"], "Em breve →"),
    ("Evolução & Dados", "Indicadores e visão longitudinal.", "fi fi-br-chart-histogram", "DADOS", "b-slate", ["KPIs", "Radar"], "Em breve →"),
]

for r in range(0, len(cards), 3):
    row = cards[r:r+3]
    cols = st.columns(3)
    for i, item in enumerate(row):
        title, sub, icon_class, dest, border, tags, cta = item
        tags = (tags or [])[:2]
        tags_html = "".join([f"<span class='tag'>{t}</span>" for t in tags])

        with cols[i]:
            st.markdown(
                f"""
<div class="home-card {border}">
  <div class="home-ic"><i class="{icon_class}"></i></div>
  <div class="home-txt">
    <div class="home-title">{title}</div>
    <div class="home-sub">{sub}</div>
    <div class="home-tags">{tags_html}</div>
    <div class="home-cta">{cta}</div>
  </div>
</div>
""",
                unsafe_allow_html=True,
            )
            st.markdown("<div class='ghost-btn'>", unsafe_allow_html=True)
            if st.button("open", key=f"card_{r+i}", use_container_width=True):
                go(dest)
            st.markdown("</div>", unsafe_allow_html=True)

# ==============================================================================
# 8) FOOTER
# ==============================================================================
st.markdown(
    "<div style='text-align: center; color: #A0AEC0; font-weight:900; font-size: 0.72rem; margin-top: 44px;'>Omnisfera desenvolvida por RODRIGO A. QUEIROZ</div>",
    unsafe_allow_html=True,
)
