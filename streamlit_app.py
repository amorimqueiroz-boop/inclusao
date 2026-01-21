import streamlit as st
from ui_nav import boot_ui, ensure_auth_state, nav_href

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
# BOOT UI
# -----------------------------------------------------------------------------
ensure_auth_state()
boot_ui()
# DEBUG (pode remover depois)
try:
    qp = dict(st.query_params)
except Exception:
    qp = {}
st.caption(f"DEBUG → autenticado={st.session_state.get('autenticado')} | go={qp.get('go')} | user={type(st.session_state.get('user')).__name__}")



# -----------------------------------------------------------------------------
# STYLES (HOME)
# -----------------------------------------------------------------------------
def _home_css():
    st.markdown(
        """
<style>
.omni-wrap{ max-width: 1180px; margin: 0 auto; }

.omni-hero{
  display:flex; align-items:flex-end; justify-content:space-between;
  gap:16px; margin-top: 10px; margin-bottom: 14px;
}
.omni-title{
  font-size: 34px; line-height: 1.05; font-weight: 900;
  letter-spacing: -0.02em; color: rgba(0,0,0,0.78);
}
.omni-sub{
  margin-top: 8px; font-size: 13px; color: rgba(0,0,0,0.56);
  max-width: 72ch;
}

.omni-kpis{
  display:grid; grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 12px; margin: 14px 0 18px 0;
}
.omni-kpi{
  padding: 14px 16px; border-radius: 18px;
  background: rgba(255,255,255,0.78);
  border: 1px solid rgba(0,0,0,0.08);
  backdrop-filter: blur(10px);
}
.omni-kpi-label{ font-size: 12px; color: rgba(0,0,0,0.52); }
.omni-kpi-value{ margin-top: 6px; font-size: 22px; font-weight: 900; color: rgba(0,0,0,0.78); }

.omni-hint{ font-size: 12px; color: rgba(0,0,0,0.45); margin-top: 6px; }

.omni-grid{
  display:grid; grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 14px;
}

.omni-card{
  padding: 18px 18px 14px 18px; border-radius: 22px;
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
  width: 44px; height: 44px; border-radius: 16px;
  display:flex; align-items:center; justify-content:center;
  background: rgba(0,0,0,0.04);
  border: 1px solid rgba(0,0,0,0.08);
  margin-bottom: 10px;
}
.omni-badge i{ font-size: 18px; line-height: 1; }

.omni-card-title{ font-size: 16px; font-weight: 900; color: rgba(0,0,0,0.78); margin-bottom: 6px; }
.omni-card-desc{ font-size: 13px; line-height: 1.45; color: rgba(0,0,0,0.56); margin-bottom: 12px; }

.omni-cta{
  display:inline-flex; align-items:center; justify-content:space-between;
  width: 100%;
  padding: 10px 12px;
  border-radius: 14px;
  background: rgba(0,0,0,0.03);
  border: 1px solid rgba(0,0,0,0.08);
  text-decoration:none;
  font-weight: 800;
  color: rgba(0,0,0,0.72);
}
.omni-cta:hover{
  background: rgba(0,0,0,0.05);
}

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
# LOGIN (placeholder)
# -----------------------------------------------------------------------------
def render_login():
    _home_css()
    st.markdown("<div class='omni-wrap'>", unsafe_allow_html=True)

    st.markdown(
        """
        <div class="omni-hero">
          <div>
            <div class="omni-title">Acesse o Omnisfera</div>
            <div class="omni-sub">Entre para continuar.</div>
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
            st.session_state.autenticado = True
            st.session_state.user = {"email": email.strip()}
            st.rerun()
        else:
            st.error("Preencha e-mail e senha.")

    st.markdown("</div>", unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# HOME
# -----------------------------------------------------------------------------
def _card(title: str, desc: str, go_key: str, ico_class: str, color: str, cta: str):
    return f"""
<div class="omni-card">
  <div class="omni-badge"><i class="{ico_class}" style="color:{color}"></i></div>
  <div class="omni-card-title">{title}</div>
  <div class="omni-card-desc">{desc}</div>
  <a class="omni-cta" href="{nav_href(go_key)}">
    {cta} <span>→</span>
  </a>
</div>
"""


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

    # Grid 3x2 (cards)
    c1, c2, c3 = st.columns(3, gap="large")
    with c1:
        st.markdown(
            _card(
                "Alunos",
                "Gerencie alunos salvos, cadastros e sincronização com a nuvem.",
                "alunos",
                "fi fi-br-users",
                "#2563EB",
                "Abrir Alunos",
            ),
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown(
            _card(
                "PEI 360°",
                "Monte e acompanhe o Plano Educacional Individual com evidências e rubricas.",
                "pei",
                "fi fi-br-brain",
                "#7C3AED",
                "Abrir PEI",
            ),
            unsafe_allow_html=True,
        )
    with c3:
        st.markdown(
            _card(
                "PAE",
                "Plano de Apoio Educacional e estratégias com foco no acompanhamento.",
                "pae",
                "fi fi-br-bullseye",
                "#F97316",
                "Abrir PAE",
            ),
            unsafe_allow_html=True,
        )

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

    c4, c5, c6 = st.columns(3, gap="large")
    with c4:
        st.markdown(
            _card(
                "Hub de Inclusão",
                "Recursos, orientações, modelos e boas práticas para inclusão.",
                "hub",
                "fi fi-br-book-open-cover",
                "#16A34A",
                "Abrir Hub",
            ),
            unsafe_allow_html=True,
        )
    with c5:
        st.markdown(
            _card(
                "Diário de Bordo",
                "Registros, observações e linha do tempo de intervenções.",
                "diario",
                "fi fi-br-notebook",
                "#0EA5E9",
                "Abrir Diário",
            ),
            unsafe_allow_html=True,
        )
    with c6:
        st.markdown(
            _card(
                "Monitoramento",
                "Acompanhamento, avaliação e indicadores de evolução.",
                "dados",
                "fi fi-br-chart-histogram",
                "#111827",
                "Abrir Monitoramento",
            ),
            unsafe_allow_html=True,
        )

    st.divider()

    left, right = st.columns([1, 5])
    with left:
        if st.button("Sair"):
            st.session_state.autenticado = False
            st.session_state.user = None
            st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# ROUTING
# -----------------------------------------------------------------------------
if not st.session_state.get("autenticado"):
    render_login()
else:
    render_home()
