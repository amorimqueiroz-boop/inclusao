# Home.py
import streamlit as st
from datetime import date
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
        if v in ("login","home","estudantes","pei","paee","hub","diario","mon"):
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
APP_VERSION = "v116.0"

def get_base64_image(image_path: str) -> str:
    if not os.path.exists(image_path):
        return ""
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode()

def go(view_name: str):
    st.session_state.view = view_name
    st.rerun()

# -------------------------
# CSS HOME (inspirado no antigo)
# -------------------------
st.markdown("""
<link href="https://cdn.jsdelivr.net/npm/remixicon@4.1.0/fonts/remixicon.css" rel="stylesheet">
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Nunito:wght@400;600;700;800;900&display=swap');

html, body, [class*="css"]{
  font-family:'Nunito', sans-serif;
  background:#F7FAFC;
  color:#2D3748;
}
header[data-testid="stHeader"]{display:none !important;}
[data-testid="stSidebar"]{display:none !important;}
[data-testid="stSidebarNav"]{display:none !important;}

/* HOME usa header fixo próprio */
.block-container{
  padding-top: 120px !important;
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
.portal-subtitle{
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

/* HERO */
.dash-hero{
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
  font-weight: 800;
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
.hero-bg-icon{
  position:absolute;
  right: 22px;
  font-size: 6rem;
  opacity: 0.07;
  top: 6px;
  transform: rotate(-10deg);
}

/* SECTION TITLE */
.section-title{
  font-family:'Inter', sans-serif;
  font-weight: 800;
  font-size: 1.05rem;
  color:#1A202C;
  margin: 22px 0 12px 0;
  display:flex;
  align-items:center;
  gap: 8px;
}

/* CARDS (6) */
.tools-grid{
  display:grid;
  grid-template-columns: repeat(12, 1fr);
  gap: 12px;
}
.tool-card{
  grid-column: span 4;
  background:white;
  border-radius: 16px;
  padding: 16px;
  border: 1px solid #E2E8F0;
  box-shadow: 0 2px 6px rgba(0,0,0,0.02);
  animation: fadeInUp .55s ease;
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
  font-size: 1.4rem;
}
.tool-title{
  font-weight: 900;
  color:#1A202C;
  margin:0;
  font-size: 0.95rem;
  letter-spacing: .1px;
}
.tool-desc{
  margin-top: 8px;
  color:#718096;
  font-size: 0.8rem;
  font-weight: 600;
  line-height: 1.25;
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
.bento-title{ font-weight: 800; font-size: 0.86rem; color:#1A202C; margin-bottom: 2px; }
.bento-desc{ font-size: 0.75rem; color:#718096; font-weight:600; line-height:1.2; }

/* INSIGHT */
.insight-card{
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
  font-weight: 600;
}

.footer-sign{
  text-align:center;
  color:#CBD5E0;
  font-size: 0.72rem;
  margin-top: 34px;
}
@media (max-width: 900px){
  .tool-card{grid-column: span 12;}
  .block-container{padding-top: 110px !important;}
}
</style>
""", unsafe_allow_html=True)

# -------------------------
# LOGIN VIEW (mantém sua estrutura nova; aqui está simples)
# -------------------------
view = st.session_state.view
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
            # ✅ aqui você pluga o Supabase depois
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
    # HEADER FIXO com logo (como antigo)
    icone_b64 = get_base64_image("omni_icone.png")
    texto_b64 = get_base64_image("omni_texto.png")

    if icone_b64 and texto_b64:
        header_html = f"""
<div class="portal-header">
  <img src="data:image/png;base64,{icone_b64}" class="portal-logo-spin" alt="Omnisfera"/>
  <img src="data:image/png;base64,{texto_b64}" class="portal-logo-text" alt="Omnisfera"/>
  <div class="portal-subtitle">Ecossistema de Inteligência Pedagógica e Inclusiva</div>
</div>
"""
    else:
        header_html = """
<div class="portal-header">
  <div style="font-size:32px">🌐</div>
  <div style="font-weight:900; letter-spacing:.6px;">OMNISFERA</div>
  <div class="portal-subtitle">Ecossistema de Inteligência Pedagógica e Inclusiva</div>
</div>
"""
    st.markdown(header_html, unsafe_allow_html=True)

    nome_display = st.session_state.get("usuario_nome", "Educador").split()[0]

    # HERO
    mensagem_banner = "Unindo ciência, dados e empatia para transformar a educação."
    st.markdown(f"""
<div class="dash-hero">
  <div>
    <div class="hero-title">Olá, {nome_display}!</div>
    <div class="hero-subtitle">"{mensagem_banner}"</div>
  </div>
  <i class="ri-heart-pulse-fill hero-bg-icon"></i>
</div>
""", unsafe_allow_html=True)

    # MANIFESTO (do seu texto antigo)
    st.markdown("<div class='section-title'><i class='ri-flag-2-fill'></i> Manifesto Omnisfera</div>", unsafe_allow_html=True)
    st.info(
        "“A Omnisfera foi desenvolvida com muito cuidado e carinho com o objetivo de auxiliar as escolas na tarefa de incluir. "
        "Ela tem o potencial para revolucionar o cenário da inclusão no Brasil.”"
    )

    # 6 CARDS (SPA)
    st.markdown("<div class='section-title'><i class='ri-cursor-fill'></i> Acesso Rápido</div>", unsafe_allow_html=True)
    st.markdown('<div class="tools-grid">', unsafe_allow_html=True)

    def tool_card(title, desc, emoji, bg, view_target, btn_label):
        st.markdown(f"""
<div class="tool-card">
  <div class="tool-top">
    <div>
      <div class="tool-title">{title}</div>
      <div class="tool-desc">{desc}</div>
    </div>
    <div class="tool-ico" style="background:{bg};">{emoji}</div>
  </div>
</div>
""", unsafe_allow_html=True)
        st.markdown('<div class="tool-btn">', unsafe_allow_html=True)
        if st.button(btn_label, use_container_width=True, key=f"go_{view_target}"):
            go(view_target)
        st.markdown("</div>", unsafe_allow_html=True)

    tool_card("👥 Estudantes", "Cadastro, histórico, evidências e vinculações.", "👥", "rgba(37,99,235,0.12)", "estudantes", "Abrir Estudantes")
    tool_card("🧩 Estratégias & PEI", "Barreiras, suporte, estratégias e rubricas.", "🧩", "rgba(59,130,246,0.12)", "pei", "Abrir PEI")
    tool_card("📍 Plano de Ação (PAEE)", "Metas SMART, ações, responsáveis e cronograma.", "📍", "rgba(34,197,94,0.12)", "paee", "Abrir PAEE")
    tool_card("💡 Hub de Recursos", "Adaptações, TA, atividades e modelos.", "💡", "rgba(245,158,11,0.14)", "hub", "Abrir Hub")
    tool_card("🧭 Diário de Bordo", "Registros de contexto, hipóteses e decisões pedagógicas.", "🧭", "rgba(249,115,22,0.14)", "diario", "Abrir Diário")
    tool_card("📈 Avaliação & Acompanhamento", "Indicadores, evidências e progresso longitudinal.", "📈", "rgba(168,85,247,0.14)", "mon", "Abrir Avaliação")

    st.markdown("</div>", unsafe_allow_html=True)

    # INCLUSÃO EM 60s
    st.markdown("<div class='section-title'><i class='ri-timer-flash-fill'></i> Inclusão em 60 segundos</div>", unsafe_allow_html=True)
    st.markdown("""
- **Incluir** não é “adaptar o aluno”: é **reduzir barreiras** para participação e aprendizagem.
- **Barreiras** (LBI): comunicacionais, metodológicas, atitudinais e tecnológicas/instrumentais.
- **DUA**: múltiplos caminhos de **engajamento**, **representação** e **ação/expressão**.
- **PEI**: organiza necessidades, objetivos, estratégias, apoios e evidências.
- **PAEE**: transforma estratégia em **ações**, rotina, responsáveis e cronograma.
- **Monitoramento**: rubricas + evidências + revisão periódica = progresso real (com rastreabilidade).
""")

    # FLUXO OMNISFERA (PEI → PAEE → MON)
    st.markdown("<div class='section-title'><i class='ri-route-fill'></i> Fluxo Omnisfera</div>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        st.success("**1) PEI**\n\nMapeie barreiras, defina níveis de suporte e registre estratégias.\n\n✅ Saída: Plano pedagógico claro.")
    with c2:
        st.warning("**2) PAEE**\n\nConverta em ações: metas SMART, rotina, responsabilidades e recursos.\n\n✅ Saída: Execução na escola.")
    with c3:
        st.info("**3) Monitoramento**\n\nColete evidências e avalie por rubricas.\n\n✅ Saída: Evolução longitudinal.")

    # DUA NA PRÁTICA (tabela)
    st.markdown("<div class='section-title'><i class='ri-layout-4-fill'></i> DUA na prática</div>", unsafe_allow_html=True)
    st.markdown("""
| Princípio | O que garantir | Exemplos rápidos |
|---|---|---|
| **Engajamento** | motivação e vínculo | escolhas, metas curtas, hiperfoco, gamificação |
| **Representação** | diferentes formas de apresentar | áudio, visual, concreto, exemplo guiado, texto simplificado |
| **Ação/Expressão** | diferentes formas de responder | oral, desenho, teclado, CAA, checklist, prova adaptada |
""")

    # BARREIRAS (LBI) com exemplos
    st.markdown("<div class='section-title'><i class='ri-shield-star-fill'></i> Barreiras mais comuns (LBI) e como agir</div>", unsafe_allow_html=True)
    with st.expander("🗣️ Comunicacionais", expanded=False):
        st.write("Sinais: aluno não compreende instruções, não consegue se expressar, ruído na interação.")
        st.write("Ações: instruções em passos, visual de rotina, CAA/apoios visuais, checagem de compreensão.")
    with st.expander("📚 Metodológicas", expanded=False):
        st.write("Sinais: tarefa exige um caminho único, tempo rígido, avaliação única.")
        st.write("Ações: flexibilizar produto, reduzir carga, scaffolding, rubricas, tempo extra, modelos.")
    with st.expander("🤝 Atitudinais", expanded=False):
        st.write("Sinais: expectativas baixas, rótulos, isolamento, ‘não dá conta’.")
        st.write("Ações: linguagem inclusiva, altas expectativas realistas, pares tutores, cultura de pertencimento.")
    with st.expander("🛠️ Tecnológicas/Instrumentais", expanded=False):
        st.write("Sinais: falta de recurso, ferramenta inadequada, acessibilidade digital inexistente.")
        st.write("Ações: TA baixa/média/alta, acessibilidade em materiais, alternativa offline, recursos de leitura.")

    # CHECKLIST
    st.markdown("<div class='section-title'><i class='ri-checkbox-circle-fill'></i> Checklist rápido do professor</div>", unsafe_allow_html=True)
    st.markdown("""
- Eu sei **qual é a barreira** (não apenas o diagnóstico)?
- A tarefa permite **mais de um caminho** para concluir?
- Eu defini **o mínimo essencial** (o que realmente preciso avaliar)?
- A sala tem **apoios visuais/rotina** para reduzir ansiedade?
- O estudante tem **uma forma alternativa** de responder?
- Eu registrei **evidência** (foto, rubrica, observação objetiva)?
""")

    # CONHECIMENTO (bento expandido)
    st.markdown("<div class='section-title'><i class='ri-book-mark-fill'></i> Conhecimento</div>", unsafe_allow_html=True)
    st.markdown("""
<div class="bento-grid">
  <a href="#" class="bento-item">
    <div class="bento-icon" style="background:#EBF8FF; color:#3182CE;"><i class="ri-question-answer-line"></i></div>
    <div class="bento-title">PEI vs PAEE</div>
    <div class="bento-desc">Diferenças e quando usar.</div>
  </a>
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
    <div class="bento-icon" style="background:#FFF5F7; color:#D53F8C;"><i class="ri-brain-line"></i></div>
    <div class="bento-title">Neurodesenvolvimento</div>
    <div class="bento-desc">Sinais, apoios e escola.</div>
  </a>
  <a href="#" class="bento-item">
    <div class="bento-icon" style="background:#EEF2FF; color:#4F46E5;"><i class="ri-settings-3-line"></i></div>
    <div class="bento-title">Rubricas</div>
    <div class="bento-desc">Avaliar com clareza.</div>
  </a>
  <a href="#" class="bento-item">
    <div class="bento-icon" style="background:#FDF2F8; color:#DB2777;"><i class="ri-tools-fill"></i></div>
    <div class="bento-title">Tecnologia Assistiva</div>
    <div class="bento-desc">Baixa, média e alta.</div>
  </a>
</div>
""", unsafe_allow_html=True)

    # INSIGHT (com conteúdo real — depois ligamos IA)
    insight = "A aprendizagem acontece quando o cérebro se emociona. Crie vínculos antes de cobrar conteúdos."
    st.markdown(f"""
<div class="insight-card">
  <div class="insight-ico"><i class="ri-lightbulb-flash-line"></i></div>
  <div>
    <div class="insight-kicker">Insight do Dia</div>
    <div class="insight-text">"{insight}"</div>
  </div>
</div>
""", unsafe_allow_html=True)

    st.markdown("<div class='footer-sign'>Omnisfera — Criada por Rodrigo A. Queiroz • PEI360 • PAEE360 • HUB de Inclusão</div>", unsafe_allow_html=True)

# -------------------------
# OTHER VIEWS (placeholders)
# -------------------------
elif view == "estudantes":
    st.markdown("## Estudantes (placeholder)")
elif view == "pei":
    st.markdown("## Estratégias & PEI (placeholder)")
elif view == "paee":
    st.markdown("## Plano de Ação (PAEE) (placeholder)")
elif view == "hub":
    st.markdown("## Hub de Recursos (placeholder)")
elif view == "diario":
    st.markdown("## Diário de Bordo (placeholder)")
elif view == "mon":
    st.markdown("## Avaliação & Acompanhamento (placeholder)")
else:
    st.warning(f"View desconhecida: {view}")
