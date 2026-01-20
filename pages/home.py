from ui_nav import boot_ui, ensure_auth_state

ensure_auth_state()
boot_ui()

if not st.session_state.autenticado:
    st.query_params["go"] = "login"
    st.stop()

user = st.session_state.user or {}
email = user.get("email", "—")

# --- Estilo (mantém clean / neutro) ---
st.markdown("""
<style>
.home-header{
  display:flex; align-items:flex-end; justify-content:space-between;
  gap:16px; margin: 8px 0 10px 0;
}
.home-header .t{
  font-size: 20px; font-weight: 900; letter-spacing: -0.2px;
  color: rgba(0,0,0,0.78);
}
.home-header .s{
  margin-top: 4px;
  color: rgba(0,0,0,0.50);
  font-size: 13px;
}
.kpi-row{
  display:grid;
  grid-template-columns: repeat(4, minmax(0,1fr));
  gap:12px;
  margin: 12px 0 14px 0;
}
.kpi{
  border-radius: 18px;
  padding: 14px;
  border: 1px solid rgba(0,0,0,0.08);
  background: rgba(255,255,255,0.70);
  backdrop-filter: blur(10px);
}
.kpi .label{ font-size: 12px; color: rgba(0,0,0,0.50); }
.kpi .value{ font-size: 22px; font-weight: 900; margin-top: 6px; color: rgba(0,0,0,0.78); }

.cards{
  display:grid;
  grid-template-columns: repeat(3, minmax(0,1fr));
  gap:12px;
  margin-top: 10px;
}
.card{
  border-radius: 22px;
  padding: 16px;
  border: 1px solid rgba(0,0,0,0.08);
  background: rgba(255,255,255,0.72);
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
  background: rgba(0,0,0,0.03);
}
.badge i{
  font-size: 18px;
  color: rgba(0,0,0,0.70);
}
.card h3{ margin: 0; font-size: 16px; font-weight: 900; color: rgba(0,0,0,0.78); }
.card p{ margin: 8px 0 12px 0; font-size: 13px; color: rgba(0,0,0,0.56); line-height: 1.35; }
.card a{ text-decoration:none; font-weight: 900; font-size: 13px; color: rgba(0,0,0,0.70); }
.small{ margin-top: 8px; color: rgba(0,0,0,0.42); font-size: 12px; }

@media (max-width: 1000px){
  .kpi-row{ grid-template-columns: repeat(2, minmax(0,1fr)); }
  .cards{ grid-template-columns: repeat(1, minmax(0,1fr)); }
}
</style>
""", unsafe_allow_html=True)

# --- Header minimal ---
st.markdown(f"""
<div class="home-header">
  <div>
    <div class="t">Central</div>
    <div class="s">Logado como <b>{email}</b> · Acesso rápido aos módulos.</div>
  </div>
</div>
""", unsafe_allow_html=True)

# --- Logout simples (sem switch_page pra não dar exceção) ---
if st.button("Sair"):
    st.session_state.autenticado = False
    st.session_state.user = None
    st.query_params["go"] = "login"
    st.stop()

# --- KPIs (placeholder por enquanto) ---
st.markdown("""
<div class="kpi-row">
  <div class="kpi"><div class="label">Alunos na nuvem</div><div class="value">—</div></div>
  <div class="kpi"><div class="label">PEIs ativos</div><div class="value">—</div></div>
  <div class="kpi"><div class="label">Evidências</div><div class="value">—</div></div>
  <div class="kpi"><div class="label">Atualizações hoje</div><div class="value">—</div></div>
</div>
""", unsafe_allow_html=True)

# --- Cards com ícones Flaticon (sem emoji) ---
def card(title, desc, icon_class, go, link_label="Abrir"):
    return f"""
<div class="card">
  <div class="top">
    <div class="badge"><i class="{icon_class}"></i></div>
    <a href="?go={go}" target="_self">{link_label} →</a>
  </div>
  <h3>{title}</h3>
  <p>{desc}</p>
  <div class="small">Atalho: ?go={go}</div>
</div>
"""

st.markdown(f"""
<div class="cards">
  {card("Alunos", "Gerencie alunos salvos, cadastros e sincronização com Supabase.", "fi fi-sr-users", "alunos")}
  {card("PEI 360°", "Monte e acompanhe o Plano Educacional Individual com evidências e rubricas.", "fi fi-sr-document-signed", "pei")}
  {card("PAE", "Plano de Apoio Educacional e estratégias com foco no acompanhamento.", "fi fi-ss-bullseye-arrow", "pae")}
  {card("Hub de Inclusão", "Recursos, adaptações e trilhas por necessidade.", "fi fi-sr-book-open-cover", "hub")}
  {card("Diário", "Registro longitudinal (em breve).", "fi fi-br-notebook", "diario", "Em breve")}
  {card("Dados", "Dashboards e KPIs (em preferred).", "fi fi-br-chart-histogram", "dados", "Em breve")}
</div>
""", unsafe_allow_html=True)
