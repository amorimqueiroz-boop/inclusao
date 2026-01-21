# streamlit_app.py
import streamlit as st
from datetime import date
import base64
import os
import time

# ==============================================================================
# 0) CONFIGURAÇÃO DO APP
# ==============================================================================
APP_VERSION = "v133.0 (Home High Design • 6 cards ricos • Escola do PIN)"

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
    initial_sidebar_state="expanded",
)

# ==============================================================================
# 1) STATE (mínimo) + compat
# ==============================================================================
if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False
if "usuario_nome" not in st.session_state:
    st.session_state["usuario_nome"] = ""
if "usuario_cargo" not in st.session_state:
    st.session_state["usuario_cargo"] = ""

# Mantém dados para compatibilidade com páginas (Home não usa como gate)
default_state = {"nome": "", "nasc": date(2015, 1, 1), "serie": None, "turma": "", "diagnostico": "", "student_id": None}
if "dados" not in st.session_state:
    st.session_state.dados = default_state.copy()

# ==============================================================================
# 2) HELPERS
# ==============================================================================
def get_base64_image(image_path: str) -> str:
    if not image_path or not os.path.exists(image_path):
        return ""
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

def get_escola_vinculada() -> str:
    """
    Recupera o nome da escola vinculada ao PIN a partir do session_state.
    Ajuste fino: basta você salvar o nome em alguma dessas chaves ao autenticar via PIN.
    """
    keys_direct = [
        "escola", "escola_nome", "school_name",
        "workspace_name", "workspace_label", "workspace_display"
    ]
    for k in keys_direct:
        v = st.session_state.get(k)
        if isinstance(v, str) and v.strip():
            return v.strip()

    w = st.session_state.get("workspace")
    if isinstance(w, dict):
        for k in ["name", "school_name", "escola", "escola_nome", "label", "display_name"]:
            v = w.get(k)
            if isinstance(v, str) and v.strip():
                return v.strip()

    wsid = st.session_state.get("workspace_id")
    if isinstance(wsid, str) and wsid.strip():
        return f"Workspace {wsid[:8]}…"

    return ""

# ==============================================================================
# 3) CSS BASE (sempre)
# ==============================================================================
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Nunito:wght@400;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Nunito', sans-serif; color:#1A202C; background:#F7FAFC; }

[data-testid="stSidebarNav"] { display: none !important; }
[data-testid="stHeader"] { visibility: hidden !important; height: 0px !important; }

/* remove aquele “respiro” feio acima em alguns temas */
.block-container { padding-top: 128px !important; padding-bottom: 2rem !important; }
</style>
""",
    unsafe_allow_html=True,
)

# ==============================================================================
# 4) LOGIN (único) — sem sobreposição
# ==============================================================================
if not st.session_state["autenticado"]:
    st.markdown("""<style>section[data-testid="stSidebar"] { display:none !important; }</style>""", unsafe_allow_html=True)

    st.markdown(
        """
<style>
.login-shell { max-width: 520px; margin: 50px auto; }
.login-card {
  background: rgba(255,255,255,0.92);
  border: 1px solid rgba(226,232,240,0.9);
  border-radius: 22px;
  box-shadow: 0 18px 45px rgba(15,82,186,0.10);
  padding: 28px;
  text-align: center;
}
.login-title { font-family: Inter, sans-serif; font-weight: 900; letter-spacing: .6px; color:#0F52BA; margin: 12px 0 2px; }
.login-sub { color:#718096; font-weight:700; margin-bottom: 16px; }
@keyframes spin { from { transform: rotate(0deg);} to { transform: rotate(360deg);} }
</style>
""",
        unsafe_allow_html=True,
    )

    c1, c_login, c2 = st.columns([1, 2, 1])
    with c_login:
        st.markdown("<div class='login-shell'><div class='login-card'>", unsafe_allow_html=True)

        img_icone = get_base64_image("omni_icone.png")
        if img_icone:
            st.markdown(
                f"<img src='data:image/png;base64,{img_icone}' style='height:84px; animation: spin 45s linear infinite;'>",
                unsafe_allow_html=True,
            )

        st.markdown("<div class='login-title'>OMNISFERA</div>", unsafe_allow_html=True)
        st.markdown("<div class='login-sub'>Ecossistema de Inteligência Pedagógica</div>", unsafe_allow_html=True)

        if IS_TEST_ENV:
            if st.button("🚀 ENTRAR (MODO TESTE)", use_container_width=True):
                st.session_state["autenticado"] = True
                st.session_state["usuario_nome"] = "Visitante Teste"
                st.session_state["usuario_cargo"] = "Ambiente de Teste"
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

        st.markdown("</div></div>", unsafe_allow_html=True)

    st.stop()

# ==============================================================================
# 5) TOPBAR + HOME HIGH DESIGN
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

escola_vinculada = get_escola_vinculada()

st.markdown(
    f"""
<style>
/* Flaticon UIcons v3.0.0 */
@import url('https://cdn-uicons.flaticon.com/3.0.0/uicons-solid-rounded/css/uicons-solid-rounded.css');
@import url('https://cdn-uicons.flaticon.com/3.0.0/uicons-solid-straight/css/uicons-solid-straight.css');
@import url('https://cdn-uicons.flaticon.com/3.0.0/uicons-bold-rounded/css/uicons-bold-rounded.css');

/* TOPBAR */
.header-container {{
  position: fixed; top: 0; left: 0; width: 100%; height: 88px;
  background: rgba(255,255,255,0.78);
  backdrop-filter: blur(14px);
  border-bottom: 1px solid rgba(226,232,240,0.85);
  z-index: 99999;
  display: flex; align-items: center; justify-content: space-between;
  padding: 0 28px;
  box-shadow: 0 10px 30px rgba(15,82,186,0.06);
}}
.header-left {{ display: flex; align-items: center; gap: 16px; }}
.header-logo-spin {{ height: 54px; width: 54px; animation: spin 18s linear infinite; }}
.header-logo-text {{ height: 38px; width: auto; }}
.header-divider {{ height: 36px; width: 1px; background: rgba(203,213,224,0.9); margin: 0 6px; }}
.header-slogan {{ font-weight: 800; color: #718096; letter-spacing: .2px; }}
.header-badge {{
  background: {card_bg};
  border: 1px solid {card_border};
  border-radius: 14px;
  padding: 8px 12px;
  display: flex;
  flex-direction: column;
  gap: 2px;
  align-items: flex-end;
  box-shadow: 0 10px 20px rgba(15,82,186,0.07);
}}
.badge-top {{
  font-family: Inter, sans-serif;
  font-weight: 900;
  font-size: 0.62rem;
  letter-spacing: 1.4px;
  text-transform: uppercase;
  color: #1A202C;
}}
.badge-school {{
  font-weight: 800;
  font-size: 0.82rem;
  color: #2D3748;
  opacity: .92;
  max-width: 420px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}}
@keyframes spin {{ from {{ transform: rotate(0deg); }} to {{ transform: rotate(360deg); }} }}

/* HERO */
.hero-shell {{
  background:
    radial-gradient(900px 250px at 15% 10%, rgba(15,82,186,0.22), transparent 65%),
    radial-gradient(900px 250px at 85% 0%, rgba(56,178,172,0.18), transparent 60%),
    radial-gradient(circle at top right, #0F52BA, #062B61);
  border-radius: 22px;
  border: 1px solid rgba(255,255,255,0.14);
  box-shadow: 0 18px 50px rgba(15,82,186,0.24);
  padding: 26px 28px;
  color: white;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 18px;
}}
.hero-title {{
  font-family: Inter, sans-serif;
  font-weight: 900;
  font-size: 1.55rem;
  margin: 0;
}}
.hero-sub {{
  margin-top: 6px;
  font-weight: 800;
  color: rgba(255,255,255,0.86);
}}
.hero-chips {{
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 14px;
}}
.chip {{
  background: rgba(255,255,255,0.12);
  border: 1px solid rgba(255,255,255,0.14);
  padding: 7px 10px;
  border-radius: 999px;
  font-weight: 800;
  font-size: 0.78rem;
  color: rgba(255,255,255,0.92);
}}
.hero-right {{
  min-width: 230px;
  display: flex;
  justify-content: flex-end;
}}
.hero-pulse {{
  background: rgba(255,255,255,0.10);
  border: 1px solid rgba(255,255,255,0.14);
  border-radius: 18px;
  padding: 12px 14px;
  text-align: right;
}}
.hero-mini {{
  font-weight: 900;
  letter-spacing: .4px;
}}
.hero-mini-sub {{
  margin-top: 4px;
  font-weight: 800;
  color: rgba(255,255,255,0.86);
  font-size: .82rem;
}}

/* CARDS (6) — high design */
.home-grid {{
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 16px;
  margin-top: 10px;
}}
@media (max-width: 1100px) {{ .home-grid {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }} }}
@media (max-width: 700px)  {{ .home-grid {{ grid-template-columns: repeat(1, minmax(0, 1fr)); }} }}

.home-card {{
  position: relative;
  background: rgba(255,255,255,0.92);
  border-radius: 22px;
  border: 1px solid rgba(226,232,240,0.95);
  box-shadow: 0 12px 28px rgba(15,82,186,0.08);
  padding: 18px 18px;
  display: flex;
  align-items: flex-start;
  gap: 14px;
  min-height: 132px;
  transition: transform .14s ease, box-shadow .14s ease, border-color .14s ease;
  overflow: hidden;
}}
.home-card:before {{
  content: "";
  position: absolute;
  inset: -60px -60px auto auto;
  width: 140px;
  height: 140px;
  border-radius: 999px;
  background: rgba(15,82,186,0.08);
  filter: blur(0px);
}}
.home-card:hover {{
  transform: translateY(-2px);
  box-shadow: 0 18px 45px rgba(15,82,186,0.14);
  border-color: rgba(49,130,206,0.35);
}}
.home-ic {{
  width: 48px; height: 48px;
  border-radius: 16px;
  display: flex; align-items: center; justify-content: center;
  background: rgba(15,82,186,0.08);
  border: 1px solid rgba(15,82,186,0.12);
  margin-top: 2px;
}}
.home-ic i {{ font-size: 22px; color: #0F52BA; line-height: 1; }}

.home-txt {{ display:flex; flex-direction:column; gap:6px; }}
.home-title {{
  font-family: Inter, sans-serif;
  font-weight: 900;
  font-size: 1.02rem;
  color: #1A202C;
  margin: 0;
}}
.home-sub {{
  font-size: 0.82rem;
  color: #718096;
  margin: 0;
  font-weight: 800;
  line-height: 1.25rem;
}}
.home-tags {{
  display:flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-top: 4px;
}}
.tag {{
  background: rgba(226,232,240,0.55);
  border: 1px solid rgba(226,232,240,0.9);
  color: #2D3748;
  padding: 4px 8px;
  border-radius: 999px;
  font-weight: 900;
  font-size: 0.68rem;
  letter-spacing: .3px;
}}
.home-cta {{
  margin-top: 2px;
  font-weight: 900;
  color: #0F52BA;
  font-size: 0.78rem;
}}

/* botão invisível cobrindo o card */
.home-btn-wrap {{ position: relative; }}
.home-btn-wrap button {{
  position: absolute;
  inset: 0;
  opacity: 0.01;
  height: 100%;
  z-index: 10;
}}
.home-btn-wrap [data-testid="stButton"] {{ margin: 0; }}
.home-btn-wrap [data-testid="stButton"] > button {{ padding: 0 !important; }}
.home-btn-wrap [data-testid="stButton"] > button:focus {{ outline: none !important; box-shadow: none !important; }}

/* acentos por módulo */
.b-slate {{ border-bottom: 4px solid #4A5568; }}
.b-blue  {{ border-bottom: 4px solid #3182CE; }}
.b-purple{{ border-bottom: 4px solid #805AD5; }}
.b-teal  {{ border-bottom: 4px solid #38B2AC; }}

/* footer */
footer {{ visibility: {footer_visibility} !important; }}
</style>
""",
    unsafe_allow_html=True,
)

# TOPBAR render
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
    <div class="badge-top">{display_text}</div>
    {"<div class='badge-school'>🏫 "+escola_vinculada+"</div>" if escola_vinculada else ""}
  </div>
</div>
""",
    unsafe_allow_html=True,
)

# ==============================================================================
# 6) SIDEBAR (NAV + usuário) — destinos estáveis
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
    if escola_vinculada:
        st.caption("🏫 Escola vinculada")
        st.markdown(f"**{escola_vinculada}**")

    st.markdown("---")
    st.markdown(f"**👤 {st.session_state.get('usuario_nome', '')}**")
    st.caption(st.session_state.get("usuario_cargo", ""))

    if st.button("Sair", use_container_width=True):
        st.session_state["autenticado"] = False
        st.rerun()

# ==============================================================================
# 7) HOME (conteúdo)
# ==============================================================================
primeiro_nome = ""
try:
    primeiro_nome = (st.session_state.get("usuario_nome", "") or "").split()[0]
except Exception:
    primeiro_nome = ""

# HERO
chips = [
    "BNCC + DUA",
    "PEI / PAEE",
    "Rubricas",
    "Inclusão",
]
chips_html = "".join([f"<span class='chip'>{c}</span>" for c in chips])

st.markdown(
    f"""
<div class="hero-shell">
  <div>
    <div class="hero-title">Olá, {primeiro_nome}!</div>
    <div class="hero-sub">{("🏫 " + escola_vinculada) if escola_vinculada else "Bem-vindo(a) ao Omnisfera."}</div>
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

# ==============================================================================
# 7.1) HOME — 6 CARDS (ricos) — sem “Home”, com “Estudantes”
# ==============================================================================
st.markdown("### 🚀 Módulos")

def _handle(dest: str):
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
        time.sleep(0.2)
    elif dest == "DADOS":
        st.toast("🛠️ Evolução & Dados — em breve neste build.", icon="✨")
        time.sleep(0.2)
    else:
        st.toast("🛠️ Em breve.", icon="✨")
        time.sleep(0.2)

cards = [
    # title, subtitle, icon_class, dest, border, tags(list), cta
    ("Estudantes", "Gestão, seleção e histórico do aluno.", "fi fi-br-users", "ALUNOS", "b-slate",
     ["Cadastro", "Turmas", "Ativos"], "Abrir gestão →"),

    ("Estratégias & PEI", "Plano Educacional Individualizado com rubricas.", "fi fi-sr-book-open-cover", "PEI", "b-blue",
     ["PEI 360°", "DUA", "BNCC"], "Abrir PEI →"),

    ("Plano de Ação / PAEE", "Intervenções, sala de recursos e execução.", "fi fi-ss-puzzle", "PAEE", "b-purple",
     ["Rotinas", "AEE", "Ações"], "Abrir PAEE →"),

    ("Hub de Recursos", "Modelos, adaptações e ferramentas pedagógicas.", "fi fi-sr-rocket", "HUB", "b-teal",
     ["Materiais", "Provas", "Planos"], "Abrir Hub →"),

    ("Diário de Bordo", "Registro contínuo, evidências e acompanhamento.", "fi fi-br-notebook", "DIARIO", "b-slate",
     ["Observações", "Evidências", "Notas"], "Em breve →"),

    ("Evolução & Dados", "Indicadores, visão longitudinal e dashboards.", "fi fi-br-chart-histogram", "DADOS", "b-slate",
     ["KPIs", "Radar", "Progresso"], "Em breve →"),
]

st.markdown("<div class='home-grid'>", unsafe_allow_html=True)

for idx, (title, sub, icon_class, dest, border, tags, cta) in enumerate(cards):
    tags_html = "".join([f"<span class='tag'>{t}</span>" for t in (tags or [])])
    st.markdown(
        f"""
<div class="home-btn-wrap">
  <div class="home-card {border}">
    <div class="home-ic"><i class="{icon_class}"></i></div>
    <div class="home-txt">
      <div class="home-title">{title}</div>
      <div class="home-sub">{sub}</div>
      <div class="home-tags">{tags_html}</div>
      <div class="home-cta">{cta}</div>
    </div>
  </div>
</div>
""",
        unsafe_allow_html=True,
    )
    if st.button("open", key=f"home_card_{idx}", use_container_width=True):
        _handle(dest)

st.markdown("</div>", unsafe_allow_html=True)

# ==============================================================================
# 8) FOOTER
# ==============================================================================
st.markdown(
    "<div style='text-align: center; color: #A0AEC0; font-weight:800; font-size: 0.72rem; margin-top: 44px;'>Omnisfera desenvolvida por RODRIGO A. QUEIROZ</div>",
    unsafe_allow_html=True,
)
