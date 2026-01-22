# pages/0_Home.py
import streamlit as st
from datetime import date
import base64
import os
import time

# ==============================================================================
# 1) CONFIG
# ==============================================================================
APP_VERSION = "v135.2 (Home Premium Grid)"

try:
    IS_TEST_ENV = st.secrets.get("ENV") == "TESTE"
except Exception:
    IS_TEST_ENV = False

st.set_page_config(
    page_title="Omnisfera",
    page_icon="omni_icone.png" if os.path.exists("omni_icone.png") else "🌐",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ==============================================================================
# 2) GATE (PROTEÇÃO) — HOME NÃO AUTENTICA
# ==============================================================================
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
            <div style="font-weight:900; font-size:1.1rem; margin-bottom:6px; color:#0f172a;">
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
        if st.button("🔑 Ir para Login", use_container_width=True, type="primary"):
            st.session_state.autenticado = False
            st.session_state.workspace_id = None
            st.session_state.workspace_name = None
            st.rerun()
    st.stop()

if not st.session_state.get("autenticado", False):
    acesso_bloqueado("Sessão expirada ou não iniciada.")

if not st.session_state.get("workspace_id"):
    acesso_bloqueado("Nenhum workspace vinculado ao seu acesso.")

# ==============================================================================
# 3) STATE (compat)
# ==============================================================================
if "dados" not in st.session_state:
    st.session_state.dados = {
        "nome": "",
        "nasc": date(2015, 1, 1),
        "serie": None,
        "turma": "",
        "diagnostico": "",
        "student_id": None,
    }

if "usuario_nome" not in st.session_state:
    st.session_state.usuario_nome = "Usuário"
if "usuario_cargo" not in st.session_state:
    st.session_state.usuario_cargo = ""

def get_base64_image(path: str) -> str:
    if path and os.path.exists(path):
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return ""

def escola_vinculada() -> str:
    v = st.session_state.get("workspace_name")
    if isinstance(v, str) and v.strip():
        return v.strip()
    wsid = st.session_state.get("workspace_id", "")
    if isinstance(wsid, str) and wsid:
        return f"Workspace {wsid[:8]}…"
    return "Workspace"

# ==============================================================================
# 4) CSS — “excelência” (grid real + botão overlay sem sobras)
# ==============================================================================
st.markdown(
    """
<style>
/* Fonts + Icons */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@500;600;700;800;900&family=Nunito:wght@400;600;700;800;900&display=swap');
@import url("https://cdn.jsdelivr.net/npm/remixicon@3.5.0/fonts/remixicon.css");

:root{
  --bg: #F7FAFC;
  --text:#0f172a;
  --muted:#64748B;
  --border:#E2E8F0;
  --card:#ffffff;
  --shadow: 0 18px 44px rgba(15,23,42,.08);

  --blue:#0F52BA;
  --deep:#062B61;
  --teal:#38B2AC;
  --purple:#805AD5;
  --indigo:#4F46E5;

  --r18: 18px;
  --r20: 20px;
}

/* Base */
html, body, [class*="css"]{
  font-family:'Nunito', sans-serif;
  background: var(--bg);
  color: var(--text);
}

/* Streamlit cleanup */
[data-testid="stSidebarNav"] { display:none !important; }
[data-testid="stHeader"] { visibility:hidden !important; height:0px !important; }
.block-container { padding-top: 120px !important; padding-bottom: 3rem !important; max-width: 1200px; }

/* Anim */
@keyframes spin { to { transform: rotate(360deg); } }

/* TOPBAR */
.header-container{
  position: fixed; top:0; left:0; width:100%; height:86px;
  background: rgba(255,255,255,0.78);
  backdrop-filter: blur(14px);
  border-bottom: 1px solid rgba(226,232,240,0.85);
  z-index: 99999;
  display:flex; align-items:center; justify-content:space-between;
  padding: 0 28px;
  box-shadow: 0 10px 30px rgba(15,82,186,0.06);
}
.header-left{ display:flex; align-items:center; gap:14px; }
.logo-spin{ width:54px; height:54px; animation: spin 18s linear infinite; }
.logo-text{ height:38px; width:auto; }
.header-div{ width:1px; height:34px; background: rgba(203,213,224,0.9); margin: 0 6px; }
.header-slogan{ font-weight:900; color:#64748B; letter-spacing:.2px; }

.header-badge{
  background: rgba(255,255,255,0.86);
  border: 1px solid rgba(226,232,240,0.9);
  border-radius: 14px;
  padding: 10px 12px;
  text-align:right;
  box-shadow: 0 10px 20px rgba(15,82,186,0.07);
  max-width: 520px;
}
.badge-top{
  font-family: Inter, sans-serif;
  font-weight: 900;
  font-size: .62rem;
  letter-spacing: 1.4px;
  text-transform: uppercase;
  color: #0f172a;
  opacity: .9;
}
.badge-val{
  font-weight: 900;
  font-size: .86rem;
  color:#1f2937;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* HERO */
.hero-shell{
  background:
    radial-gradient(900px 240px at 15% 10%, rgba(15,82,186,0.22), transparent 65%),
    radial-gradient(900px 240px at 85% 0%, rgba(56,178,172,0.18), transparent 60%),
    radial-gradient(circle at top right, #0F52BA, #062B61);
  border-radius: 22px;
  border: 1px solid rgba(255,255,255,0.14);
  box-shadow: 0 18px 50px rgba(15,82,186,0.24);
  padding: 22px 24px;
  color: white;
  display:flex;
  justify-content: space-between;
  align-items: center;
  gap: 14px;
  margin-bottom: 26px;
}
.hero-title{
  font-family: Inter, sans-serif;
  font-weight: 900;
  font-size: 1.55rem;
  margin: 0;
}
.hero-sub{
  margin-top: 6px;
  font-weight: 900;
  color: rgba(255,255,255,0.86);
}
.hero-chips{ display:flex; gap:8px; flex-wrap:wrap; margin-top: 12px; }
.chip{
  background: rgba(255,255,255,0.12);
  border: 1px solid rgba(255,255,255,0.14);
  padding: 6px 10px;
  border-radius: 999px;
  font-weight: 900;
  font-size: 0.76rem;
  color: rgba(255,255,255,0.92);
}
.hero-right{
  min-width: 220px;
  display:flex;
  justify-content:flex-end;
}
.hero-mini{
  background: rgba(255,255,255,0.10);
  border: 1px solid rgba(255,255,255,0.14);
  border-radius: 18px;
  padding: 10px 12px;
  text-align:right;
}
.hero-mini .t{ font-weight: 900; }
.hero-mini .s{ margin-top:3px; font-weight:900; color: rgba(255,255,255,0.86); font-size: .80rem; }

/* SECTION TITLE */
.section-title{
  display:flex; align-items:center; gap:10px;
  font-family: Inter, sans-serif;
  font-weight: 900;
  font-size: 1.15rem;
  margin: 6px 0 14px;
  color: #0f172a;
}

/* CARD PREMIUM (compacto, 3 por linha) */
.module-card{
  position: relative;
  background: rgba(255,255,255,0.94);
  border-radius: 20px;
  border: 1px solid rgba(226,232,240,0.95);
  box-shadow: 0 10px 22px rgba(15,82,186,0.07);
  padding: 16px 16px;
  min-height: 152px;
  overflow:hidden;
  transition: transform .14s ease, box-shadow .14s ease, border-color .14s ease;
}
.module-card:before{
  content:"";
  position:absolute;
  inset:-70px -70px auto auto;
  width: 180px;
  height: 180px;
  border-radius: 999px;
  background: rgba(15,82,186,0.06);
}
.module-card:hover{
  transform: translateY(-2px);
  box-shadow: 0 16px 38px rgba(15,82,186,0.12);
  border-color: rgba(49,130,206,0.35);
}
.mc-top{ display:flex; align-items:flex-start; gap:12px; }
.mc-ic{
  width: 46px; height:46px;
  border-radius: 16px;
  display:flex; align-items:center; justify-content:center;
  border: 1px solid rgba(15,82,186,0.10);
}
.mc-ic i{ font-size: 22px; line-height:1; }
.mc-title{
  font-family: Inter, sans-serif;
  font-weight: 900;
  font-size: 1.02rem;
  margin:0;
  color:#0f172a;
}
.mc-desc{
  margin-top:6px;
  font-weight: 800;
  font-size: .86rem;
  color: var(--muted);
  line-height: 1.25rem;
  display:-webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow:hidden;
}
.mc-tags{ display:flex; gap:6px; margin-top:10px; overflow:hidden; }
.tag{
  background: rgba(226,232,240,0.55);
  border: 1px solid rgba(226,232,240,0.9);
  color: #1f2937;
  padding: 4px 9px;
  border-radius: 999px;
  font-weight: 900;
  font-size: .70rem;
  white-space: nowrap;
}
.mc-cta{
  margin-top: 10px;
  font-weight: 900;
  color: #0F52BA;
  font-size: .80rem;
  display:flex; align-items:center; gap:6px;
}

/* Themes */
.t-indigo{ background: rgba(79,70,229,0.10); color: #4F46E5; border-color: rgba(79,70,229,0.14) !important; }
.t-blue  { background: rgba(15,82,186,0.10); color: #0F52BA; border-color: rgba(15,82,186,0.14) !important; }
.t-purple{ background: rgba(128,90,213,0.10); color: #805AD5; border-color: rgba(128,90,213,0.14) !important; }
.t-teal  { background: rgba(56,178,172,0.10); color: #319795; border-color: rgba(56,178,172,0.14) !important; }
.t-gray  { background: rgba(148,163,184,0.15); color: #64748B; border-color: rgba(148,163,184,0.22) !important; }

/* ---- CLICK OVERLAY (sem “open”, sem sobras) ----
   Estratégia: marcamos o bloco com um span .mk-<key>.
   Depois usamos :has() para tornar o bloco relativo e posicionar o botão absoluto.
*/
.block-rel { position: relative !important; }

/* O botão do Streamlit (container) vira overlay, sem ocupar layout */
div[data-testid="stVerticalBlock"]:has(.mk-card) { position: relative; }
div[data-testid="stVerticalBlock"]:has(.mk-card) div[data-testid="stButton"] { position: absolute; inset: 0; margin: 0; }
div[data-testid="stVerticalBlock"]:has(.mk-card) div[data-testid="stButton"] button{
  position:absolute; inset:0;
  width:100%; height:100%;
  opacity:0 !important;
  border:0 !important;
  padding:0 !important;
  background: transparent !important;
  cursor: pointer;
}
div[data-testid="stVerticalBlock"]:has(.mk-card) div[data-testid="stButton"] button:focus { outline: none !important; }

/* Sidebar (leve) */
section[data-testid="stSidebar"]{
  background: rgba(255,255,255,0.86) !important;
  border-right: 1px solid rgba(226,232,240,0.9);
}
</style>
""",
    unsafe_allow_html=True,
)

# ==============================================================================
# 5) TOPBAR
# ==============================================================================
icone_b64 = get_base64_image("omni_icone.png")
texto_b64 = get_base64_image("omni_texto.png")
esc = escola_vinculada()

logo_html = f'<img src="data:image/png;base64,{icone_b64}" class="logo-spin">' if icone_b64 else "🌐"
nome_html = f'<img src="data:image/png;base64,{texto_b64}" class="logo-text">' if texto_b64 else "<div style='font-family:Inter,sans-serif;font-weight:900;color:#0F52BA;font-size:1.15rem;'>OMNISFERA</div>"

st.markdown(
    f"""
<div class="header-container">
  <div class="header-left">
    {logo_html}
    {nome_html}
    <div class="header-div"></div>
    <div class="header-slogan">Inteligência Pedagógica</div>
  </div>
  <div class="header-badge">
    <div class="badge-top">OMNISFERA {APP_VERSION}</div>
    <div class="badge-val">🏫 {esc}</div>
  </div>
</div>
""",
    unsafe_allow_html=True,
)

# ==============================================================================
# 6) SIDEBAR (mesmos destinos)
# ==============================================================================
with st.sidebar:
    st.markdown("### 🧭 Navegação")

    if st.button("👥 Estudantes", use_container_width=True):
        st.switch_page("pages/0_Alunos.py")

    c1, c2 = st.columns(2)
    with c1:
        if st.button("📘 PEI", use_container_width=True):
            st.switch_page("pages/1_PEI.py")
    with c2:
        if st.button("🧩 PAEE", use_container_width=True):
            st.switch_page("pages/2_PAE.py")

    if st.button("🚀 Hub", use_container_width=True):
        st.switch_page("pages/3_Hub_Inclusao.py")

    st.markdown("---")
    st.markdown(f"**👤 {st.session_state.get('usuario_nome', 'Usuário')}**")
    st.caption(st.session_state.get("usuario_cargo", ""))
    st.caption(f"🏫 {esc}")

    st.markdown("---")
    if st.button("Sair", use_container_width=True):
        st.session_state.autenticado = False
        st.session_state.workspace_id = None
        st.session_state.workspace_name = None
        st.rerun()

# ==============================================================================
# 7) HERO
# ==============================================================================
primeiro_nome = (st.session_state.get("usuario_nome") or "Visitante").split()[0]
chips = ["BNCC + DUA", "PEI / PAEE", "Rubricas", "Inclusão"]
chips_html = "".join([f"<span class='chip'>{c}</span>" for c in chips])

st.markdown(
    f"""
<div class="hero-shell">
  <div>
    <div class="hero-title">Olá, {primeiro_nome}!</div>
    <div class="hero-sub">Seja bem-vindo ao seu painel de controle da inclusão.</div>
    <div class="hero-chips">{chips_html}</div>
  </div>
  <div class="hero-right">
    <div class="hero-mini">
      <div class="t">Acesso rápido</div>
      <div class="s">Seus módulos em 1 clique</div>
    </div>
  </div>
</div>
""",
    unsafe_allow_html=True,
)

# ==============================================================================
# 8) MÓDULOS — grid 3 por linha (premium)
# ==============================================================================
st.markdown("<div class='section-title'>🚀
