import streamlit as st
from ui_nav import boot_ui, ensure_auth_state, nav_href
from login import render_login  # <--- Importamos do novo arquivo

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

# -----------------------------------------------------------------------------
# HOME DASHBOARD (Só aparece se logado)
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
    # CSS da Home (Cards, KPIs)
    st.markdown("""
    <style>
    .omni-wrap{ max-width: 1180px; margin: 0 auto; }
    .omni-hero{ display:flex; align-items:flex-end; justify-content:space-between; gap:16px; margin-top: 10px; margin-bottom: 14px; }
    .omni-title{ font-size: 34px; font-weight: 900; color: rgba(0,0,0,0.78); }
    .omni-sub{ margin-top: 8px; font-size: 13px; color: rgba(0,0,0,0.56); }
    .omni-card{ padding: 18px; border-radius: 22px; background: rgba(255,255,255,0.82); border: 1px solid rgba(0,0,0,0.08); transition: all .12s ease; }
    .omni-card:hover{ transform: translateY(-2px); box-shadow: 0 14px 34px rgba(0,0,0,0.10); }
    .omni-badge{ width: 44px; height: 44px; border-radius: 16px; display:flex; align-items:center; justify-content:center; background: rgba(0,0,0,0.04); margin-bottom: 10px; }
    .omni-badge i{ font-size: 18px; }
    .omni-card-title{ font-size: 16px; font-weight: 900; color: rgba(0,0,0,0.78); margin-bottom: 6px; }
    .omni-card-desc{ font-size: 13px; color: rgba(0,0,0,0.56); margin-bottom: 12px; }
    .omni-cta{ display:inline-flex; align-items:center; justify-content:space-between; width: 100%; padding: 10px 12px; border-radius: 14px; background: rgba(0,0,0,0.03); text-decoration:none; font-weight: 800; color: rgba(0,0,0,0.72); }
    .omni-cta:hover{ background: rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("<div class='omni-wrap'>", unsafe_allow_html=True)
    
    user_email = st.session_state["user"].get("email") if st.session_state["user"] else "Visitante"

    st.markdown(f"""
        <div class="omni-hero">
          <div>
            <div class="omni-title">Central</div>
            <div class="omni-sub">Logado como <b>{user_email}</b>.</div>
          </div>
        </div>
    """, unsafe_allow_html=True)

    # Grid de Cards
    c1, c2, c3 = st.columns(3, gap="large")
    with c1: st.markdown(_card("Alunos", "Gerencie cadastros e sincronização.", "alunos", "fi fi-br-users", "#2563EB", "Abrir"), unsafe_allow_html=True)
    with c2: st.markdown(_card("PEI 360°", "Monte e acompanhe o Plano Educacional.", "pei", "fi fi-br-brain", "#7C3AED", "Abrir"), unsafe_allow_html=True)
    with c3: st.markdown(_card("PAEE", "Plano de Apoio Educacional Especializado.", "paee", "fi fi-br-bullseye", "#F97316", "Abrir"), unsafe_allow_html=True)
    
    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
    
    c4, c5, c6 = st.columns(3, gap="large")
    with c4: st.markdown(_card("Hub de Inclusão", "Recursos e boas práticas.", "hub", "fi fi-br-book-open-cover", "#16A34A", "Abrir"), unsafe_allow_html=True)
    with c5: st.markdown(_card("Diário de Bordo", "Registros e observações diárias.", "diario", "fi fi-br-notebook", "#0EA5E9", "Abrir"), unsafe_allow_html=True)
    with c6: st.markdown(_card("Monitoramento", "Indicadores de evolução.", "dados", "fi fi-br-chart-histogram", "#111827", "Abrir"), unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# ROTEAMENTO PRINCIPAL
# -----------------------------------------------------------------------------
if not st.session_state.get("autenticado"):
    render_login()  # Chama a função do novo arquivo login.py
else:
    render_home()
