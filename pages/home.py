import streamlit as st
from ui_nav import boot_ui, ensure_auth_state

# -----------------------------------------------------------------------------
# BOOT / AUTH
# -----------------------------------------------------------------------------
ensure_auth_state()
boot_ui()

if not st.session_state.autenticado:
    st.stop()

# -----------------------------------------------------------------------------
# HOME — OMNISFERA
# -----------------------------------------------------------------------------
st.markdown(
    """
    <style>
    .home-wrap {
        max-width: 1200px;
        margin: 0 auto;
    }

    .home-title {
        font-size: 22px;
        font-weight: 800;
        margin-bottom: 4px;
        color: rgba(0,0,0,0.78);
    }

    .home-sub {
        font-size: 13px;
        color: rgba(0,0,0,0.55);
        margin-bottom: 18px;
    }

    .kpis {
        display: grid;
        grid-template-columns: repeat(4, minmax(0, 1fr));
        gap: 14px;
        margin-bottom: 20px;
    }

    .kpi {
        padding: 14px 16px;
        border-radius: 18px;
        background: rgba(255,255,255,0.75);
        border: 1px solid rgba(0,0,0,0.08);
        backdrop-filter: blur(8px);
    }

    .kpi-label {
        font-size: 12px;
        color: rgba(0,0,0,0.55);
    }

    .kpi-value {
        font-size: 22px;
        font-weight: 800;
        margin-top: 6px;
        color: rgba(0,0,0,0.8);
    }

    .cards {
        display: grid;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: 16px;
    }

    .card {
        padding: 18px;
        border-radius: 22px;
        background: rgba(255,255,255,0.78);
        border: 1px solid rgba(0,0,0,0.08);
        backdrop-filter: blur(8px);
        transition: transform .12s ease, box-shadow .12s ease;
    }

    .card:hover {
        transform: translateY(-2px);
        box-shadow: 0 12px 30px rgba(0,0,0,0.10);
    }

    .card-icon {
        width: 42px;
        height: 42px;
        border-radius: 14px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 20px;
        background: rgba(0,0,0,0.04);
        border: 1px solid rgba(0,0,0,0.08);
        margin-bottom: 10px;
    }

    .card-title {
        font-size: 16px;
        font-weight: 800;
        margin-bottom: 6px;
        color: rgba(0,0,0,0.8);
    }

    .card-desc {
        font-size: 13px;
        color: rgba(0,0,0,0.55);
        line-height: 1.4;
        margin-bottom: 14px;
    }

    @media (max-width: 1000px) {
        .kpis { grid-template-columns: repeat(2, 1fr); }
        .cards { grid-template-columns: 1fr; }
    }
    </style>
    """,
    unsafe_allow_html=True
)

user_email = st.session_state.user.get("email", "—") if st.session_state.user else "—"

st.markdown(
    f"""
    <div class="home-wrap">
        <div class="home-title">Central</div>
        <div class="home-sub">
            Logado como <b>{user_email}</b> · Acesso rápido aos módulos do Omnisfera
        </div>

        <div class="kpis">
            <div class="kpi">
                <div class="kpi-label">Alunos na nuvem</div>
                <div class="kpi-value">—</div>
            </div>
            <div class="kpi">
                <div class="kpi-label">PEIs ativos</div>
                <div class="kpi-value">—</div>
            </div>
            <div class="kpi">
                <div class="kpi-label">Evidências</div>
                <div class="kpi-value">—</div>
            </div>
            <div class="kpi">
                <div class="kpi-label">Atualizações hoje</div>
                <div class="kpi-value">—</div>
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# -----------------------------------------------------------------------------
# CARDS DE ACESSO RÁPIDO (NAVEGAÇÃO VIA PAGE_LINK)
# -----------------------------------------------------------------------------
c1, c2, c3 = st.columns(3)

with c1:
    st.markdown(
        """
        <div class="card">
            <div class="card-icon">👥</div>
            <div class="card-title">Alunos</div>
            <div class="card-desc">
                Gerencie alunos salvos, cadastros e sincronização com a nuvem.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
    st.page_link("pages/0_Alunos.py", label="Abrir Alunos →")

with c2:
    st.markdown(
        """
        <div class="card">
            <div class="card-icon">🧠</div>
            <div class="card-title">PEI 360°</div>
            <div class="card-desc">
                Monte e acompanhe o Plano Educacional Individual com evidências e rubricas.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
    st.page_link("pages/1_PEI.py", label="Abrir PEI →")

with c3:
    st.markdown(
        """
        <div class="card">
            <div class="card-icon">🎯</div>
            <div class="card-title">PAE</div>
            <div class="card-desc">
                Plano de Apoio Educacional e estratégias com foco no acompanhamento.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
    st.page_link("pages/2_PAE.py", label="Abrir PAE →")

# -----------------------------------------------------------------------------
# LOGOUT
# -----------------------------------------------------------------------------
st.divider()

if st.button("Sair"):
    st.session_state.autenticado = False
    st.session_state.user = None
    st.experimental_rerun()
