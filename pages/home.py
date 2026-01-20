import streamlit as st
import os
from ui_nav import boot_ui, ensure_auth_state

# -----------------------------------------------------------------------------
# BOOT
# -----------------------------------------------------------------------------
ensure_auth_state()
boot_ui(do_route=False)

# -----------------------------------------------------------------------------
# BLOQUEIO SEM LOGIN
# -----------------------------------------------------------------------------
if not st.session_state.autenticado:
    st.query_params["go"] = "login"
    st.stop()

# -----------------------------------------------------------------------------
# ESTILO (cards + grid)
# -----------------------------------------------------------------------------
st.markdown("""
<style>
.home-hero{
  display:flex;
  align-items:flex-end;
  justify-content:space-between;
  gap:16px;
  margin: 4px 0 18px 0;
}
.home-title{
  font-size: 44px;
  font-weight: 850;
  letter-spacing: -0.8px;
  margin: 0;
}
.home-sub{
  margin-top: 6px;
  color: rgba(0,0,0,0.60);
  font-size: 14px;
}
.home-actions{
  display:flex;
  gap:10px;
  align-items:center;
}

.kpi-row{
  display:grid;
  grid-template-columns: repeat(4, minmax(0,1fr));
  gap:12px;
  margin: 10px 0 14px 0;
}
.kpi{
  border-radius: 18px;
  padding: 14px 14px;
  border: 1px solid rgba(0,0,0,0.08);
  background: rgba(255,255,255,0.55);
  backdrop-filter: blur(10px);
}
.kpi .label{ font-size: 12px; color: rgba(0,0,0,0.55); }
.kpi .value{ font-size: 22px; font-weight: 800; margin-top: 6px; }

.cards{
  display:grid;
  grid-template-columns: repeat(3, minmax(0,1fr));
  gap:12px;
  margin-top: 10px;
}
.card{
  border-radius: 22px;
  padding: 16px 16px;
  border: 1px solid rgba(0,0,0,0.08);
  background: rgba(255,255,255,0.62);
  backdrop-filter: blur(10px);
  transition: transform .12s ease, box-shadow .12s ease;
}
.card:hover{
  transform: translateY(-2px);
  box-shadow: 0 12px 34px rgba(0,0,0,0.10);
}
.card .top{
  display:flex; align-items:center; justify-content:space-between;
  gap:10px; margin-bottom: 10px;
}
.badge{
  width: 40px; height: 40px; border-radius: 14px;
  display:flex; align-items:center; justify-content:center;
  border: 1px solid rgba(0,0,0,0.10);
  background: rgba(255,255,255,0.70);
  font-size: 18px;
}
.card h3{ margin: 0; font-size: 16px; font-weight: 850; }
.card p{ margin: 8px 0 12px 0; font-size: 13px; color: rgba(0,0,0,0.60); line-height: 1.35; }
.card a{
  text-decoration:none;
  font-weight: 800;
  font-size: 13px;
}
.small{
  margin-top: 8px;
  color: rgba(0,0,0,0.48);
  font-size: 12px;
}
@media (max-width: 1000px){
  .kpi-row{ grid-template-columns: repeat(2, minmax(0,1fr)); }
  .cards{ grid-template-columns: repeat(1, minmax(0,1fr)); }
}
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# HEADER
# -----------------------------------------------------------------------------
user = st.session_state.user or {}
email = user.get("email", "—")

st.markdown(f"""
<div class="home-hero">
  <div>
    <div class="home-title">Home — Omnisfera</div>
    <div class="home-sub">Logado como: <b>{email}</b> · Acesso rápido aos módulos e visão geral do dia.</div>
  </div>
  <div class="home-actions"></div>
</div>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# AÇÕES (logout + “voltar pro login” sem switch_page)
# -----------------------------------------------------------------------------
colA, colB = st.columns([1, 5])
with colA:
    if st.button("Sair"):
        st.session_state.autenticado = False
        st.session_state.user = None
        st.query_params["go"] = "login"
        st.stop()

with colB:
    st.caption("Dica: use o menu superior para navegação rápida. Os cards abaixo também navegam via `?go=`.")

# -----------------------------------------------------------------------------
# KPIs (placeholders — depois ligamos no Supabase)
# -----------------------------------------------------------------------------
st.markdown("""
<div class="kpi-row">
  <div class="kpi"><div class="label">Alunos na nuvem</div><div class="value">—</div></div>
  <div class="kpi"><div class="label">PEIs ativos</div><div class="value">—</div></div>
  <div class="kpi"><div class="label">Evidências</div><div class="value">—</div></div>
  <div class="kpi"><div class="label">Atualizações hoje</div><div class="value">—</div></div>
</div>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# LOGO/Ícone (opcional)
# -----------------------------------------------------------------------------
ICON_PATH = "omni_icone.png"
if os.path.exists(ICON_PATH):
    st.image(ICON_PATH, width=72)

# -----------------------------------------------------------------------------
# CARDS DE NAVEGAÇÃO (já funcionam com o seu router ?go=)
# -----------------------------------------------------------------------------
def card(title, desc, emoji, go, link_label="Abrir"):
    return f"""
<div class="card">
  <div class="top">
    <div class="badge">{emoji}</div>
    <a href="?go={go}">{link_label} →</a>
  </div>
  <h3>{title}</h3>
  <p>{desc}</p>
  <div class="small">Atalho: ?go={go}</div>
</div>
"""

st.markdown(f"""
<div class="cards">
  {card("Alunos", "Gerencie alunos salvos, cadastros e sincronização com Supabase.", "👥", "alunos")}
  {card("PEI 360°", "Monte e acompanhe o Plano Educacional Individual com evidências e rubricas.", "🧠", "pei")}
  {card("PAE", "Plano de Apoio Educacional e estratégias com foco no acompanhamento.", "🎯", "pae")}
  {card("Hub de Inclusão", "Banco de recursos, adaptações, trilhas e materiais por necessidade.", "📚", "hub")}
  {card("Diário", "Registro longitudinal (em breve).", "📝", "diario", "Em breve")}
  {card("Dados", "Dashboards e KPIs (em breve).", "📈", "dados", "Em breve")}
</div>
""", unsafe_allow_html=True)

st.markdown("---")
st.caption("Próximo passo: ligar KPIs e a lista de alunos do Supabase diretamente aqui na Home.")
