import streamlit as st
from ui_nav import boot_ui, ensure_auth_state

# -----------------------------------------------------------------------------
# PAGE CONFIG
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Omnisfera",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# -----------------------------------------------------------------------------
# STATE
# -----------------------------------------------------------------------------
ensure_auth_state()
boot_ui()


# -----------------------------------------------------------------------------
# STYLES (HOME)
# -----------------------------------------------------------------------------
def _home_css():
    st.markdown(
        """
<style>
/* Container padrão mais elegante */
.omni-wrap{
  max-width: 1180px;
  margin: 0 auto;
}

/* Header da Home */
.omni-hero{
  display:flex;
  align-items:flex-end;
  justify-content:space-between;
  gap:16px;
  margin-top: 8px;
  margin-bottom: 14px;
}

.omni-title{
  font-size: 34px;
  line-height: 1.05;
  font-weight: 900;
  letter-spacing: -0.02em;
  color: rgba(0,0,0,0.78);
}

.omni-sub{
  margin-top: 8px;
  font-size: 13px;
  color: rgba(0,0,0,0.56);
  max-width: 72ch;
}

/* KPI row */
.omni-kpis{
  display:grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 12px;
  margin: 14px 0 18px 0;
}

.omni-kpi{
  padding: 14px 16px;
  border-radius: 18px;
  background: rgba(255,255,255,0.78);
  border: 1px solid rgba(0,0,0,0.08);
  backdrop-filter: blur(10px);
}

.omni-kpi-label{
  font-size: 12px;
  color: rgba(0,0,0,0.52);
}

.omni-kpi-value{
  margin-top: 6px;
  font-size: 22px;
  font-weight: 900;
  color: rgba(0,0,0,0.78);
}

/* Cards */
.omni-grid{
  display:grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 14px;
}

.omni-card{
  padding: 18px 18px 14px 18px;
  border-radius: 22px;
  background: rgba(255,255,255,0.82);
  border: 1px solid rgba(0,0,0,0.08);
  backdrop-filter: blur(10px);
  transition: transform .12s ease, box-shadow .12s ease, background .12s ease;
}

.omni-card:hover{
  transform: translateY(-2px);
  box-shadow: 0 14px 34px rgba(0,0,0,0.10);
  background: rgba(255,255,255,0.88);
}

.omni-badge{
  width: 44px;
  height: 44px;
  border-radius: 16px;
  display:flex;
  align-items:center;
  justify-content:center;
  font-size: 20px;
  background: rgba(0,0,0,0.04);
  border: 1px solid rgba(0,0,0,0.08);
  margin-bottom: 10px;
}

.omni-card-title{
  font-size: 16px;
  font-weight: 900;
  color: rgba(0,0,0,0.78);
  margin-bottom: 6px;
}

.omni-card-desc{
  font-size: 13px;
  line-height: 1.45;
  color: rgba(0,0,0,0.56);
  margin-bottom: 12px;
}

.omni-hint{
  font-size: 12px;
  color: rgba(0,0,0,0.45);
  margin-top: 6px;
}

/* Botão link (page_link) com cara de CTA minimalista */
.omni-cta [data-testid="stPageLink"] a{
  width: 100% !important;
  display:flex !important;
  align-items:center !important;
  justify-content:space-between !important;

  padding: 10px 12px !important;
  border-radius: 14px !important;

  background: rgba(0,0,0,0.03) !important;
  border: 1px solid rgba(0,0,0,0.08) !important;

  text-decoration: none !important;
  font-weight: 700 !important;
}

.omni-cta [data-testid="stPageLink"] a:hover{
  background: rgba(0,0,0,0.05) !important;
}

/* Responsivo */
@media (max-width: 1100px){
  .omni-kpis{ grid-template-columns: repeat(2, 1fr); }
  .omni-grid{ grid-template-columns: 1fr; }
  .omni-title{ font-size: 30px; }
}
</style>
        """,
        unsafe_allow_html=True,
    )


# -----------------------------------------------------------------------------
# LOGIN
# -----------------------------------------------------------------------------
def render_login():
    _home_css()
    st.markdown("<div class='omni-wrap'>", unsafe_allow_html=True)

    st.markdown(
        """
        <div class="omni-hero">
          <div>
            <div class="omni-title">Acesse o Omnisfera</div>
            <div class="omni-sub">Entre para continuar. Seu estado e progresso ficam preservados durante a navegação.</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.form("login", clear_on_submit=False):
        email = st.text_input("E-mail", placeholder="demo@omnisfera.net")
        senha = st.text_input("Senha", type="password", placeholder="••••••••")
        ok = st.form_submit_button("Entrar")

    if ok:
        if email.strip() and senha.strip():
            # Login simples (placeholder). Depois liga no Supabase Auth.
            st.session_state.autenticado = True
            st.session_state.user = {"email": email.strip()}
            st.rerun()
        else:
            st.error("Preencha e-mail e senha.")

    st.markdown("</div>", unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# HOME (RICA)
# -----------------------------------------------------------------------------
def render_home():
    _home_css()
    st.markdown("<div class='omni-wrap'>", unsafe_allow_html=True)

    user_email = "—"
    if isinstance(st.session_state.get("user"), dict):
        user_email = st.session_state["user"].get("email", "—")

    st.markdown(
        f"""
        <div class="omni-hero">
          <div>
            <div class="omni-title">Central</div>
            <div class="omni-sub">
              Logado como <b>{user_email}</b>. Acesso rápido aos módulos e visão geral do dia.
            </div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # KPIs (por enquanto placeholders — depois conectamos ao Supabase)
    st.markdown(
        """
        <div class="omni-kpis">
          <div class="omni-kpi">
            <div class="omni-kpi-label">Alunos na nuvem</div>
            <div class="omni-kpi-value">—</div>
          </div>
          <div class="omni-kpi">
            <div class="omni-kpi-label">PEIs ativos</div>
            <div class="omni-kpi-value">—</div>
          </div>
          <div class="omni-kpi">
            <div class="omni-kpi-label">Evidências</div>
            <div class="omni-kpi-value">—</div>
          </div>
          <div class="omni-kpi">
            <div class="omni-kpi-label">Atualizações hoje</div>
            <div class="omni-kpi-value">—</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<div class='omni-hint'>Dica: use os ícones do menu superior ou os cards abaixo.</div>", unsafe_allow_html=True)
    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

    # Cards
    c1, c2, c3 = st.columns(3, gap="large")

    with c1:
        st.markdown(
            """
            <div class="omni-card">
              <div class="omni-badge">👥</div>
              <div class="omni-card-title">Alunos</div>
              <div class="omni-card-desc">
                Gerencie alunos salvos, cadastros e sincronização com a nuvem.
              </div>
              <div class="omni-cta"></div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.page_link("pages/0_Alunos.py", label="Abrir Alunos →")

    with c2:
        st.markdown(
            """
            <div class="omni-card">
              <div class="omni-badge">🧠</div>
              <div class="omni-card-title">PEI 360°</div>
              <div class="omni-card-desc">
                Monte e acompanhe o Plano Educacional Individual com evidências e rubricas.
              </div>
              <div class="omni-cta"></div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.page_link("pages/1_PEI.py", label="Abrir PEI →")

    with c3:
        st.markdown(
            """
            <div class="omni-card">
              <div class="omni-badge">🎯</div>
              <div class="omni-card-title">PAE</div>
              <div class="omni-card-desc">
                Plano de Apoio Educacional e estratégias com foco no acompanhamento.
              </div>
              <div class="omni-cta"></div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.page_link("pages/2_PAE.py", label="Abrir PAE →")

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

    c4, c5, c6 = st.columns(3, gap="large")

    with c4:
        st.markdown(
            """
            <div class="omni-card">
              <div class="omni-badge">📚</div>
              <div class="omni-card-title">Hub de Inclusão</div>
              <div class="omni-card-desc">
                Recursos, orientações, modelos e boas práticas para inclusão.
              </div>
              <div class="omni-cta"></div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.page_link("pages/3_Hub_Inclusao.py", label="Abrir Hub →")

    with c5:
        st.markdown(
            """
            <div class="omni-card">
              <div class="omni-badge">📝</div>
              <div class="omni-card-title">Diário de Bordo</div>
              <div class="omni-card-desc">
                Registros, observações e linha do tempo de intervenções.
              </div>
              <div class="omni-cta"></div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.page_link("pages/4_Diario_de_Bordo.py", label="Abrir Diário →")

    with c6:
        st.markdown(
            """
            <div class="omni-card">
              <div class="omni-badge">📈</div>
              <div class="omni-card-title">Monitoramento</div>
              <div class="omni-card-desc">
                Acompanhamento, avaliação e indicadores de evolução.
              </div>
              <div class="omni-cta"></div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.page_link("pages/5_Monitoramento_Avaliacao.py", label="Abrir Monitoramento →")

    st.divider()

    # Logout
    left, right = st.columns([1, 4])
    with left:
        if st.button("Sair"):
            st.session_state.autenticado = False
            st.session_state.user = None
            st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# ROUTING
# -----------------------------------------------------------------------------
if not st.session_state.autenticado:
    render_login()
else:
    render_home()
