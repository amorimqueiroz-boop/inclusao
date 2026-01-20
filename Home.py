# Home.py — OMNISFERA (Portal + Login) | Cards Premium (suave) + Flaticon UIcons
import streamlit as st
import base64, os

APP_VERSION = "v116.3"

st.set_page_config(
    page_title="Omnisfera | Ecossistema",
    page_icon="🧩",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# 🔁 Ajuste se seu arquivo tiver outro nome:
ROUTES = {
    "estudantes": "pages/0_Alunos.py",   # página chama aluno, exibimos "Estudantes"
    "pei":        "pages/1_PEI.py",
    "paee":       "pages/2_PAE.py",
    "hub":        "pages/3_Hub_Inclusao.py",
    "diario":     "pages/4_Diario_de_Bordo.py",
    "mon":        "pages/5_Monitoramento_Avaliacao.py",
}

# -------------------------
# SESSION INIT
# -------------------------
def _init_session():
    if "autenticado" not in st.session_state:
        st.session_state.autenticado = False
    if "usuario_nome" not in st.session_state:
        st.session_state.usuario_nome = ""
    if "usuario_cargo" not in st.session_state:
        st.session_state.usuario_cargo = ""
    if "usuario_email" not in st.session_state:
        st.session_state.usuario_email = ""

_init_session()

# -------------------------
# UTILS
# -------------------------
def get_base64_image(path: str) -> str:
    if not os.path.exists(path):
        return ""
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

# -------------------------
# ICONS (padronizados p/ evitar sumir)
# -------------------------
# Padronizei para evitar "br" (brands), que falha mais.
# Você pediu IA fixo:
ICON_AI = "fi fi-ss-chip-brain"

ICONS = {
    "estudantes": "fi fi-ss-users-alt",
    "pei":        "fi fi-sr-puzzle-alt",
    "paee":       "fi fi-rr-track",          # rr ok se carregar
    "hub":        "fi fi-sr-lightbulb-on",
    "diario":     "fi fi-sr-compass",        # trocado (antes era br-compass-alt)
    "mon":        "fi fi-sr-chart-line-up",  # trocado (antes era br-analyse)
}

# -------------------------
# CSS
# -------------------------
st.markdown("""
<link rel="stylesheet" href="https://cdn-uicons.flaticon.com/uicons-solid-rounded/css/uicons-solid-rounded.css">
<link rel="stylesheet" href="https://cdn-uicons.flaticon.com/uicons-solid-straight/css/uicons-solid-straight.css">
<link rel="stylesheet" href="https://cdn-uicons.flaticon.com/uicons-regular-rounded/css/uicons-regular-rounded.css">

<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&family=Nunito:wght@400;600;700;800;900&display=swap');

:root{
  --bg: #F6F8FB;
  --ink: #0B1220;
  --muted: #5B677A;
  --line: rgba(15,23,42,0.10);
  --glass: rgba(255,255,255,0.86);

  /* tons mais elegantes (suaves) */
  --c-students: #2F6FED;
  --c-pei:      #3B82F6;
  --c-paee:     #22C55E;
  --c-hub:      #F59E0B;
  --c-diario:   #F97316;
  --c-mon:      #A855F7;

  --shadow-soft: 0 10px 26px rgba(2,6,23,0.08);
  --shadow-hover: 0 18px 44px rgba(2,6,23,0.12);
}

html, body, [class*="css"]{
  font-family:'Nunito', sans-serif;
  background: var(--bg);
  color: var(--ink);
}

header[data-testid="stHeader"]{display:none !important;}
[data-testid="stSidebar"], [data-testid="stSidebarNav"]{display:none !important;}

.block-container{
  padding-top: 112px !important;
  padding-left: 2rem !important;
  padding-right: 2rem !important;
  padding-bottom: 2rem !important;
}

@keyframes spin{from{transform:rotate(0deg);}to{transform:rotate(360deg);}}
@keyframes fadeInUp{from{opacity:0; transform:translateY(10px);}to{opacity:1; transform:translateY(0);}}

/* HEADER FIXO */
.portal-header{
  position: fixed;
  top: 0; left: 0; right: 0;
  height: 92px;
  z-index: 99999;
  display:flex;
  align-items:center;
  gap: 16px;
  padding: 10px 26px;
  background: var(--glass);
  -webkit-backdrop-filter: blur(14px);
  backdrop-filter: blur(14px);
  border-bottom: 1px solid var(--line);
  box-shadow: 0 6px 22px rgba(2,6,23,0.06);
}
.portal-logo-spin{
  height: 68px;
  width:auto;
  animation: spin 55s linear infinite;
  filter: drop-shadow(0 2px 6px rgba(2,6,23,0.15));
}
.portal-logo-text{ height: 38px; width:auto; }
.portal-subtitle{
  font-family: Inter, system-ui, -apple-system, Segoe UI, Roboto, Arial;
  font-weight: 650;
  font-size: 0.98rem;
  color: var(--muted);
  border-left: 2px solid rgba(148,163,184,0.45);
  padding-left: 14px;
  height: 40px;
  display:flex;
  align-items:center;
  letter-spacing: -0.2px;
}

/* HERO */
.dash-hero{
  background: radial-gradient(circle at top right, rgba(37,99,235,0.90), rgba(9,24,62,0.92));
  border-radius: 18px;
  box-shadow: var(--shadow-soft);
  color: white;
  position: relative;
  overflow: hidden;
  padding: 26px 34px;
  display:flex;
  align-items:center;
  justify-content: space-between;
  border: 1px solid rgba(255,255,255,0.12);
  min-height: 110px;
  animation: fadeInUp .55s ease;
}
.hero-title{
  font-family:'Inter', sans-serif;
  font-weight: 900;
  font-size: 1.55rem;
  margin:0;
  line-height:1.1;
}
.hero-subtitle{
  font-family:'Inter', sans-serif;
  font-size: 0.92rem;
  opacity: 0.90;
  font-weight: 450;
  margin-top: 7px;
}
.hero-bg-ic{
  position:absolute;
  right: 22px;
  font-size: 5.4rem;
  opacity: 0.10;
  top: 10px;
  transform: rotate(-10deg);
}

/* SECTION TITLE */
.section-title{
  font-family:'Inter', sans-serif;
  font-weight: 900;
  font-size: 1.05rem;
  color: var(--ink);
  margin: 22px 0 12px 0;
  display:flex;
  align-items:center;
  gap: 10px;
}

/* ===== CARD (BRANCO + FAIXA ELEGANTE) ===== */
.card-shell{
  position: relative;
  background: white;
  border-radius: 18px;
  border: 1px solid rgba(148,163,184,0.22);
  box-shadow: var(--shadow-soft);
  overflow: hidden;
  animation: fadeInUp .55s ease;
  transition: transform .20s ease, box-shadow .20s ease, border-color .20s ease;
}
.card-shell:hover{
  transform: translateY(-4px);
  box-shadow: var(--shadow-hover);
  border-color: rgba(148,163,184,0.35);
}

/* faixa de cor — fina e chique */
.card-accent{
  position:absolute;
  top:0; left:0; right:0;
  height: 6px;
  background: var(--accent);
}

/* conteúdo */
.card-body{
  padding: 16px 16px 10px 16px;
  display:flex;
  gap: 12px;
  align-items:flex-start;
}
.ico-chip{
  width: 44px;
  height: 44px;
  border-radius: 16px;
  display:flex;
  align-items:center;
  justify-content:center;
  background: var(--accent);
  box-shadow: 0 10px 22px rgba(2,6,23,0.10);
}
.ico-chip i{
  font-size: 1.25rem;
  color: white;
  line-height: 1;
  margin-top: 2px;
}
.card-title{
  font-family: Inter, system-ui, -apple-system, Segoe UI, Roboto, Arial;
  font-weight: 900;
  font-size: 0.98rem;
  color: var(--ink);
  margin: 0;
  padding: 0;
}
.card-desc{
  margin-top: 6px;
  color: rgba(91,103,122,0.92);
  font-size: 0.82rem;
  font-weight: 650;
  line-height: 1.25;
}
.card-brand{
  margin-left:auto;
  font-family: Inter, system-ui, -apple-system, Segoe UI, Roboto, Arial;
  font-weight: 900;
  font-size: 0.62rem;
  letter-spacing: .12em;
  color: rgba(2,6,23,0.35);
  text-transform: uppercase;
  margin-top: 2px;
}

/* botão integrado no card */
.card-bottom{
  padding: 10px 14px 14px 14px;
  border-top: 1px solid rgba(148,163,184,0.16);
  background: rgba(2,6,23,0.015);
}

/* Botão com visual integrado */
.card-bottom div[data-testid="stButton"] > button{
  width: 100%;
  height: 44px;
  border-radius: 14px !important;
  font-weight: 900 !important;
  border: 1px solid rgba(15,23,42,0.10) !important;
  background: rgba(255,255,255,0.92) !important;
  color: var(--ink) !important;
  transition: transform .12s ease, filter .12s ease;
}
.card-bottom div[data-testid="stButton"] > button:hover{
  filter: brightness(0.99);
  transform: translateY(-1px);
  border-color: rgba(15,23,42,0.14) !important;
}

/* LOGIN */
.login-shell{ max-width: 520px; margin: 0 auto; }
.login-card{
  background: white;
  border-radius: 18px;
  border: 1px solid rgba(148,163,184,0.25);
  box-shadow: 0 12px 34px rgba(2,6,23,0.08);
  padding: 22px 22px 18px 22px;
}
.termo-box{
  background: #F8FAFC;
  border: 1px solid rgba(148,163,184,0.45);
  border-radius: 12px;
  padding: 12px;
  font-size: 0.78rem;
  color: #334155;
  line-height: 1.35;
  max-height: 120px;
  overflow-y: auto;
}
.footer-sign{
  text-align:center;
  color: rgba(148,163,184,0.75);
  font-size: 0.72rem;
  margin-top: 34px;
}

@media (max-width: 950px){
  .block-container{ padding-top: 106px !important; }
  .portal-subtitle{ display:none; }
}
</style>
""", unsafe_allow_html=True)

# -------------------------
# HEADER FIXO (logo grande)
# -------------------------
icone_b64 = get_base64_image("omni_icone.png")
texto_b64 = get_base64_image("omni_texto.png")

if icone_b64 and texto_b64:
    st.markdown(f"""
    <div class="portal-header">
      <img src="data:image/png;base64,{icone_b64}" class="portal-logo-spin" alt="Omnisfera"/>
      <img src="data:image/png;base64,{texto_b64}" class="portal-logo-text" alt="Omnisfera"/>
      <div class="portal-subtitle">Ecossistema de Inteligência Pedagógica e Inclusiva</div>
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
    <div class="portal-header">
      <div style="font-size:2.1rem;">🌐</div>
      <div style="font-family:Inter,sans-serif;font-weight:900;color:#0F52BA;font-size:1.35rem;">OMNISFERA</div>
      <div class="portal-subtitle">Ecossistema de Inteligência Pedagógica e Inclusiva</div>
    </div>
    """, unsafe_allow_html=True)

# -------------------------
# LOGIN
# -------------------------
def try_supabase_login(email: str, password: str) -> bool:
    try:
        url = st.secrets.get("SUPABASE_URL", "")
        key = st.secrets.get("SUPABASE_ANON_KEY", "")
        if not url or not key:
            return False
        from supabase import create_client  # type: ignore
        supa = create_client(url, key)
        res = supa.auth.sign_in_with_password({"email": email, "password": password})
        return bool(res and getattr(res, "session", None))
    except Exception:
        return False

def demo_login(email: str, password: str) -> bool:
    return (email.strip().lower() == "demo@omnisfera.net") and (password == "OmniDemo@2026!")

def render_login():
    st.markdown("## Acesso — Omnisfera")
    st.caption("Entre com seu usuário e senha. Use dados reais somente em ambiente autorizado e seguro.")

    st.markdown('<div class="login-shell">', unsafe_allow_html=True)
    st.markdown('<div class="login-card">', unsafe_allow_html=True)

    st.markdown("### Termo de confidencialidade")
    st.markdown("""
    <div class="termo-box">
      <b>ACORDO DE CONFIDENCIALIDADE E USO DE DADOS (Versão Beta)</b><br><br>
      1) O usuário reconhece que o Omnisfera está em fase de testes (BETA).<br>
      2) É proibida a inserção de dados sensíveis de estudantes sem autorização institucional e controle adequado (LGPD).<br>
      3) As sugestões pedagógicas devem passar por validação humana antes de aplicação.<br>
      4) Ao prosseguir, você declara estar ciente e de acordo com estes termos.
    </div>
    """, unsafe_allow_html=True)

    aceitou = st.checkbox("Li, compreendi e concordo com o termo.", value=False)

    c1, c2 = st.columns(2)
    with c1:
        nome = st.text_input("Nome", placeholder="Seu nome")
    with c2:
        cargo = st.text_input("Cargo/Função", placeholder="Seu cargo/função")

    st.markdown("#### Credenciais")
    usuario = st.text_input("Usuário (Email)", placeholder="seu@email.com")
    senha = st.text_input("Senha", type="password", placeholder="")

    can = bool(aceitou and nome.strip() and cargo.strip() and usuario.strip() and senha.strip())

    if st.button("Entrar", type="primary", use_container_width=True, disabled=not can):
        ok = try_supabase_login(usuario.strip(), senha) or demo_login(usuario, senha)
        if not ok:
            st.error("Usuário ou senha inválidos.")
        else:
            st.session_state.autenticado = True
            st.session_state.usuario_nome = nome.strip()
            st.session_state.usuario_cargo = cargo.strip()
            st.session_state.usuario_email = usuario.strip()
            st.rerun()

    st.markdown("---")
    st.markdown("#### Manifesto Omnisfera")
    st.info(
        "“A Omnisfera foi desenvolvida com muito cuidado e carinho com o objetivo de auxiliar as escolas na tarefa de incluir. "
        "Ela tem o potencial para revolucionar o cenário da inclusão no Brasil.”"
    )

    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

if not st.session_state.autenticado:
    render_login()
    st.stop()

# -------------------------
# HOME (portal)
# -------------------------
nome_display = (st.session_state.usuario_nome or "Educador").split()[0]
mensagem_banner = "Unindo ciência, dados e empatia para transformar a educação."

st.markdown(f"""
<div class="dash-hero">
  <div>
    <div class="hero-title">Olá, {nome_display}!</div>
    <div class="hero-subtitle">"{mensagem_banner}"</div>
  </div>
  <div class="hero-bg-ic"><i class="{ICON_AI}"></i></div>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="section-title">
  <span style="opacity:.9;">Acesso Rápido</span>
</div>
""", unsafe_allow_html=True)

def portal_card(col, title, desc, icon_class, accent_css_var, btn_key, route_key):
    with col:
        st.markdown(f"""
        <div class="card-shell" style="--accent: var({accent_css_var});">
          <div class="card-accent"></div>

          <div class="card-body">
            <div class="ico-chip"><i class="{icon_class}"></i></div>

            <div style="flex:1;">
              <div class="card-title">{title}</div>
              <div class="card-desc">{desc}</div>
            </div>

            <div class="card-brand">OMNISFERA</div>
          </div>

          <div class="card-bottom">
        """, unsafe_allow_html=True)

        if st.button("Acessar", key=btn_key, use_container_width=True):
            path = ROUTES.get(route_key)
            if not path:
                st.error("Rota não configurada. Ajuste ROUTES no topo do arquivo.")
            else:
                st.switch_page(path)

        st.markdown("</div></div>", unsafe_allow_html=True)

c1, c2, c3 = st.columns(3)
portal_card(
    c1, "Estudantes",
    "Cadastro, histórico, evidências e rede de apoio.",
    ICONS["estudantes"], "--c-students",
    "go_estudantes", "estudantes",
)
portal_card(
    c2, "Estratégias & PEI",
    "Barreiras, suportes, estratégias e rubricas (PEI).",
    ICONS["pei"], "--c-pei",
    "go_pei", "pei",
)
portal_card(
    c3, "Plano de Ação (PAEE)",
    "Metas SMART, ações, responsáveis e cronograma.",
    ICONS["paee"], "--c-paee",
    "go_paee", "paee",
)

c4, c5, c6 = st.columns(3)
portal_card(
    c4, "Hub de Recursos",
    "Adaptações, TA, atividades e modelos.",
    ICONS["hub"], "--c-hub",
    "go_hub", "hub",
)
portal_card(
    c5, "Diário de Bordo",
    "Registros de contexto, hipóteses e decisões (em construção).",
    ICONS["diario"], "--c-diario",
    "go_diario", "diario",
)
portal_card(
    c6, "Evolução & Dados",
    "Indicadores, evidências e acompanhamento longitudinal.",
    ICONS["mon"], "--c-mon",
    "go_mon", "mon",
)

st.markdown("""
<div class="section-title">
  <i class="fi fi-ss-chip-brain"></i>
  Inclusão em 60 segundos
</div>
""", unsafe_allow_html=True)

st.markdown("""
- **Incluir** não é “adaptar o aluno”: é **reduzir barreiras** para participação e aprendizagem.
- **Barreiras** (LBI): comunicacionais, metodológicas, atitudinais e tecnológicas/instrumentais.
- **DUA**: múltiplos caminhos de **engajamento**, **representação** e **ação/expressão**.
- **PEI**: organiza necessidades, objetivos, estratégias, apoios e evidências.
- **PAEE**: transforma estratégia em **rotina de ações** (responsáveis + cronograma + recursos).
- **Monitoramento**: rubricas + evidências + revisão periódica = progresso real.
""")

# Rodapé (logado + sair)
st.markdown("---")
cL, cR = st.columns([2, 1])
with cL:
    st.caption(f"Logado como: **{st.session_state.usuario_email}**  •  {st.session_state.usuario_cargo}")
with cR:
    if st.button("Sair", use_container_width=True):
        st.session_state.autenticado = False
        st.session_state.usuario_nome = ""
        st.session_state.usuario_cargo = ""
        st.session_state.usuario_email = ""
        st.rerun()

st.markdown(
    "<div class='footer-sign'>Omnisfera — Criada por Rodrigo A. Queiroz • PEI360 • PAEE360 • HUB de Inclusão</div>",
    unsafe_allow_html=True,
)
