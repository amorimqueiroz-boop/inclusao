# Home.py
import streamlit as st
import base64, os

st.set_page_config(page_title="Omnisfera", page_icon="🧩", layout="wide")

# -------------------------
# INIT SESSION
# -------------------------
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False
if "view" not in st.session_state:
    st.session_state.view = "login" if not st.session_state.autenticado else "home"

# lê view da URL (se existir)
try:
    if "view" in st.query_params:
        v = st.query_params["view"]
        if v in ("login","home","estudantes","pei","paee","hub","diario","mon","logout"):
            st.session_state.view = v
except Exception:
    pass

# força login se não autenticado
if not st.session_state.autenticado:
    st.session_state.view = "login"

# -------------------------
# NAV (só aparece fora de home/login)
# -------------------------
try:
    from ui_nav import render_topbar_nav
    render_topbar_nav(hide_on_views=("home","login"))
except Exception as e:
    st.error("Erro ao carregar ui_nav")
    st.exception(e)
    st.stop()

# -------------------------
# UTIL
# -------------------------
def get_base64_image(image_path: str) -> str:
    if not os.path.exists(image_path):
        return ""
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode()

def go(view_name: str):
    st.session_state.view = view_name
    st.rerun()

# -------------------------
# CSS (INJEÇÃO CERTA: <style> ... </style> + unsafe_allow_html=True)
# -------------------------
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800;900&family=Nunito:wght@400;600;700;800;900&display=swap');

html, body, [class*="css"]{
  font-family:'Nunito', sans-serif;
  background:#F7FAFC;
  color:#2D3748;
}

/* escondendo o header padrão do Streamlit */
header[data-testid="stHeader"]{display:none !important;}
[data-testid="stSidebar"]{display:none !important;}
[data-testid="stSidebarNav"]{display:none !important;}

/* espaço para o header do portal */
.block-container{
  padding-top: 120px !important;
  padding-left: 2rem !important;
  padding-right: 2rem !important;
  padding-bottom: 2rem !important;
}

@keyframes spin{from{transform:rotate(0deg);}to{transform:rotate(360deg);}}
@keyframes fadeInUp{from{opacity:0; transform:translateY(10px);}to{opacity:1; transform:translateY(0);}}

/* HEADER FIXO DO PORTAL */
.portal-header{
  position: fixed;
  top: 0; left: 0; right: 0;
  height: 90px;
  z-index: 99999;
  display:flex;
  align-items:center;
  gap: 16px;
  padding: 8px 28px;
  background: rgba(247,250,252,0.88);
  -webkit-backdrop-filter: blur(12px);
  backdrop-filter: blur(12px);
  border-bottom: 1px solid rgba(255,255,255,0.55);
  box-shadow: 0 4px 15px rgba(0,0,0,0.03);
}
.portal-logo-spin{
  height: 72px;
  width:auto;
  animation: spin 45s linear infinite;
  filter: drop-shadow(0 2px 4px rgba(0,0,0,0.10));
}
.portal-logo-text{
  height: 42px;
  width:auto;
}
.portal-subtitle{
  font-family:'Inter', sans-serif;
  font-weight: 700;
  font-size: 0.98rem;
  color: #718096;
  border-left: 2px solid #CBD5E0;
  padding-left: 14px;
  height: 40px;
  display:flex;
  align-items:center;
  letter-spacing: -0.3px;
}

/* HERO */
.hero{
  background: radial-gradient(circle at top right, #0F52BA, #062B61);
  border-radius: 16px;
  box-shadow: 0 10px 25px -5px rgba(15, 82, 186, 0.30);
  color: white;
  position: relative;
  overflow: hidden;
  padding: 26px 34px;
  display:flex;
  align-items:center;
  justify-content: space-between;
  border: 1px solid rgba(255,255,255,0.12);
  min-height: 105px;
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
  opacity: 0.92;
  font-weight: 400;
  margin-top: 6px;
}
.hero-bg{
  position:absolute;
  right: 22px;
  font-size: 6rem;
  opacity: 0.07;
  top: 6px;
  transform: rotate(-10deg);
}

.section-title{
  font-family:'Inter', sans-serif;
  font-weight: 900;
  font-size: 1.05rem;
  color:#1A202C;
  margin: 22px 0 12px 0;
  display:flex;
  align-items:center;
  gap: 8px;
}

/* CARDS 6 */
.tool-card{
  background:white;
  border-radius: 16px;
  padding: 16px;
  border: 1px solid #E2E8F0;
  box-shadow: 0 2px 6px rgba(0,0,0,0.02);
  animation: fadeInUp .55s ease;
  height: 100%;
}
.tool-top{
  display:flex;
  align-items:center;
  justify-content: space-between;
  gap: 10px;
}
.tool-ico{
  width: 44px;
  height: 44px;
  border-radius: 14px;
  display:flex;
  align-items:center;
  justify-content:center;
  font-size: 1.35rem;
}
.tool-title{
  font-family:'Inter', sans-serif;
  font-weight: 900;
  color:#1A202C;
  margin:0;
  font-size: 0.95rem;
}
.tool-desc{
  margin-top: 8px;
  color:#718096;
  font-size: 0.8rem;
  font-weight: 700;
  line-height: 1.25;
}
.tool-line{
  height: 4px;
  border-radius: 999px;
  margin-top: 12px;
  opacity: .95;
}
.tool-btn button{
  width:100%;
  height: 44px;
  border-radius: 12px !important;
  font-weight: 900 !important;
}

/* BENTO */
.bento-grid{
  display:grid;
  grid-template-columns: repeat(auto-fit, minmax(190px, 1fr));
  gap: 12px;
  margin-bottom: 12px;
}
.bento-item{
  background:white;
  border-radius: 14px;
  padding: 15px;
  border: 1px solid #E2E8F0;
  box-shadow: 0 2px 4px rgba(0,0,0,0.01);
  text-decoration:none;
  color: inherit;
  display:flex;
  flex-direction: column;
  align-items:center;
  text-align:center;
  transition: transform .16s ease;
}
.bento-item:hover{ transform: translateY(-2px); border-color:#CBD5E0; }
.bento-icon{
  width: 36px; height: 36px;
  border-radius: 10px;
  display:flex;
  align-items:center;
  justify-content:center;
  font-size: 1.1rem;
  margin-bottom: 8px;
}
.bento-title{ font-family:'Inter', sans-serif; font-weight: 900; font-size: 0.86rem; color:#1A202C; margin-bottom: 2px; }
.bento-desc{ font-size: 0.75rem; color:#718096; font-weight:700; line-height:1.2; }

/* INSIGHT */
.insight{
  background: linear-gradient(135deg, #FFFBEB 0%, #FFFFFF 100%);
  border-radius: 14px;
  padding: 15px 18px;
  display:flex;
  gap: 14px;
  border: 1px solid rgba(214,158,46,0.20);
  box-shadow: 0 5px 15px rgba(214,158,46,0.08);
}
.insight-ico{
  width: 46px; height: 46px;
  border-radius: 999px;
  display:flex;
  align-items:center;
  justify-content:center;
  font-size: 1.4rem;
  color:#D69E2E;
  background: rgba(214,158,46,0.12);
}
.insight-kicker{
  font-family:'Inter', sans-serif;
  font-weight: 900;
  font-size: 0.78rem;
  color:#D69E2E;
  letter-spacing: .5px;
  text-transform: uppercase;
}
.insight-text{
  margin-top: 2px;
  color:#4A5568;
  font-style: italic;
  font-weight: 700;
}

.footer-sign{
  text-align:center;
  color:#CBD5E0;
  font-size: 0.72rem;
  margin-top: 34px;
}

@media (max-width: 900px){
  .block-container{padding-top: 110px !important;}
}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

# -------------------------
# VIEW
# -------------------------
view = st.session_state.view

# -------------------------
# LOGIN
# -------------------------
if view == "login":
    st.markdown("## Acesso — Omnisfera")

    with st.container(border=True):
        st.markdown("### Termo de Confidencialidade")
        st.caption("Ao acessar, você declara ciência de que as informações são confidenciais e de uso pedagógico.")
        aceitou = st.checkbox("Li e concordo com o Termo de Confidencialidade.", value=False)

        c1, c2 = st.columns(2)
        with c1:
            nome = st.text_input("Nome")
        with c2:
            cargo = st.text_input("Cargo")

        usuario = st.text_input("Usuário (Email)")
        senha = st.text_input("Senha", type="password")

        disabled = not (aceitou and nome.strip() and cargo.strip() and usuario.strip() and senha.strip())
        if st.button("Entrar", type="primary", use_container_width=True, disabled=disabled):
            st.session_state.autenticado = True
            st.session_state.usuario_nome = nome.strip()
            st.session_state.usuario_cargo = cargo.strip()
            st.session_state.usuario_email = usuario.strip()
            st.session_state.view = "home"
            st.rerun()

    st.stop()

# -------------------------
# HOME PORTAL
# -------------------------
if view == "home":
    icone_b64 = get_base64_image("omni_icone.png")
    texto_b64 = get_base64_image("omni_texto.png")

    if icone_b64 and texto_b64:
        st.markdown(f"""
        <div class="portal-header">
          <img src="data:image/png;base64,{icone_b64}" class="portal-logo-spin" alt="Omnisfera">
          <img src="data:image/png;base64,{texto_b64}" class="portal-logo-text" alt="Omnisfera">
          <div class="portal-subtitle">Ecossistema de Inteligência Pedagógica e Inclusiva</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="portal-header">
          <div style="width:72px;height:72px;border-radius:18px;background:#0F52BA;"></div>
          <div style="font-family:Inter;font-weight:900;font-size:1.2rem;color:#111827;">OMNISFERA</div>
          <div class="portal-subtitle">Ecossistema de Inteligência Pedagógica e Inclusiva</div>
        </div>
        """, unsafe_allow_html=True)

    nome_display = st.session_state.get("usuario_nome", "Educador").split()[0]
    mensagem_banner = "Unindo ciência, dados e empatia para transformar a educação."

    st.markdown(f"""
    <div class="hero">
      <div>
        <div class="hero-title">Olá, {nome_display}!</div>
        <div class="hero-subtitle">"{mensagem_banner}"</div>
      </div>
      <i class="ri-heart-pulse-fill hero-bg"></i>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div class='section-title'><i class='ri-flag-2-fill'></i> Manifesto Omnisfera</div>", unsafe_allow_html=True)
    st.info("“A Omnisfera foi desenvolvida com muito cuidado e carinho com o objetivo de auxiliar as escolas na tarefa de incluir. Ela tem o potencial para revolucionar o cenário da inclusão no Brasil.”")

    st.markdown("<div class='section-title'><i class='ri-cursor-fill'></i> Acesso Rápido</div>", unsafe_allow_html=True)

    def card(title, desc, icon, color, key, target):
        st.markdown(f"""
        <div class="tool-card">
          <div class="tool-top">
            <div style="display:flex; align-items:center; gap:10px;">
              <div class="tool-ico" style="background:{color}20; color:{color};">
                <i class="{icon}"></i>
              </div>
              <div class="tool-title">{title}</div>
            </div>
          </div>
          <div class="tool-desc">{desc}</div>
          <div class="tool-line" style="background:{color};"></div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown('<div class="tool-btn">', unsafe_allow_html=True)
        if st.button("Acessar", key=key, use_container_width=True):
            go(target)
        st.markdown("</div>", unsafe_allow_html=True)

    a,b,c = st.columns(3)
    with a: card("Estudantes","Cadastro, histórico, evidências e rede de apoio.","ri-group-line","#2563EB","go_est","estudantes")
    with b: card("Estratégias & PEI","Barreiras, suportes, estratégias e rubricas.","ri-puzzle-2-line","#3B82F6","go_pei","pei")
    with c: card("Plano de Ação (PAEE)","Metas SMART, ações, responsáveis e cronograma.","ri-map-pin-2-line","#22C55E","go_paee","paee")

    d,e,f = st.columns(3)
    with d: card("Hub de Recursos","Modelos, TA, adaptações e atividades.","ri-lightbulb-flash-fill","#F59E0B","go_hub","hub")
    with e: card("Diário de Bordo","Registros de contexto, hipóteses e decisões.","ri-compass-3-fill","#F97316","go_diario","diario")
    with f: card("Avaliação & Acompanhamento","Evidências, rubricas e evolução longitudinal.","ri-line-chart-fill","#A855F7","go_mon","mon")

    st.markdown("<div class='section-title'><i class='ri-timer-flash-fill'></i> Inclusão em 60 segundos</div>", unsafe_allow_html=True)
    st.markdown("""
- **Incluir** não é “adaptar o aluno”: é **reduzir barreiras** para participação e aprendizagem.
- **Barreiras** (LBI): comunicacionais, metodológicas, atitudinais e tecnológicas/instrumentais.
- **DUA**: múltiplos caminhos de **engajamento**, **representação** e **ação/expressão**.
- **PEI**: organiza necessidades, objetivos, estratégias, apoios e evidências.
- **PAEE**: transforma estratégia em **rotina de ações**.
- **Monitoramento**: rubricas + evidências + revisão periódica = progresso real.
""")

    st.markdown("<div class='section-title'><i class='ri-book-mark-fill'></i> Conhecimento</div>", unsafe_allow_html=True)
    st.markdown("""
    <div class="bento-grid">
        <a href="https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2015/lei/l13146.htm" target="_blank" class="bento-item">
            <div class="bento-icon" style="background:#FFFFF0; color:#D69E2E;"><i class="ri-scales-3-line"></i></div>
            <div class="bento-title">Lei Brasileira de Inclusão</div>
            <div class="bento-desc">Marco legal e princípios.</div>
        </a>
        <a href="http://basenacionalcomum.mec.gov.br/" target="_blank" class="bento-item">
            <div class="bento-icon" style="background:#F0FFF4; color:#38A169;"><i class="ri-compass-3-line"></i></div>
            <div class="bento-title">BNCC</div>
            <div class="bento-desc">Currículo oficial.</div>
        </a>
        <a href="#" class="bento-item">
            <div class="bento-icon" style="background:#EBF8FF; color:#3182CE;"><i class="ri-question-answer-line"></i></div>
            <div class="bento-title">PEI vs PAEE</div>
            <div class="bento-desc">Diferenças e quando usar.</div>
        </a>
        <a href="#" class="bento-item">
            <div class="bento-icon" style="background:#FFF5F7; color:#D53F8C;"><i class="ri-brain-line"></i></div>
            <div class="bento-title">Neurodesenvolvimento</div>
            <div class="bento-desc">Sinais e apoios na escola.</div>
        </a>
    </div>
    """, unsafe_allow_html=True)

    insight = "A aprendizagem acontece quando o cérebro se emociona. Crie vínculos antes de cobrar conteúdos."
    st.markdown(f"""
    <div class="insight">
      <div class="insight-ico"><i class="ri-lightbulb-flash-line"></i></div>
      <div>
        <div class="insight-kicker">Insight do Dia</div>
        <div class="insight-text">"{insight}"</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div class='footer-sign'>Omnisfera — Criada por Rodrigo A. Queiroz • PEI360 • PAEE360 • HUB de Inclusão</div>", unsafe_allow_html=True)

elif view == "logout":
    st.session_state.autenticado = False
    st.session_state.view = "login"
    st.rerun()
else:
    st.markdown(f"## {view} (placeholder)")
