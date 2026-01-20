import streamlit as st
import base64, os

def _b64_img(*paths):
    for p in paths:
        if p and os.path.exists(p):
            with open(p, "rb") as f:
                return "data:image/png;base64," + base64.b64encode(f.read()).decode()
    return None

def render_home_portal():
    logo_spin = _b64_img("omni_icone.png","logo.png","iconeaba.png","omni.png","ominisfera.png") \
                or "https://cdn-icons-png.flaticon.com/512/1183/1183672.png"
    wordmark = _b64_img("omnisfera_wordmark.png","omnisfera_nome.png")

    st.markdown("""
<style>
/* HOME PORTAL LAYOUT */
.portal-wrap{max-width:1200px;margin:0 auto;}
.portal-hero{
  background: linear-gradient(180deg, rgba(255,255,255,0.95), rgba(255,255,255,0.80));
  border: 1px solid rgba(229,231,235,0.9);
  box-shadow: 0 10px 30px rgba(15,23,42,0.06);
  border-radius: 22px;
  padding: 26px 26px;
  display:flex;
  align-items:center;
  justify-content:space-between;
  gap: 18px;
}
.hero-left{display:flex;align-items:center;gap:16px;}
@keyframes spin{from{transform:rotate(0deg);}to{transform:rotate(360deg);}}
.hero-logo{
  width:62px;height:62px;
  border-radius:999px;
  animation: spin 10s linear infinite;
  box-shadow: 0 10px 30px rgba(15,23,42,0.10);
}
.hero-title{
  font-family: system-ui, -apple-system, Segoe UI, Roboto, Arial;
  font-weight: 950;
  letter-spacing: .8px;
  text-transform: uppercase;
  font-size: 16px;
  color:#111827;
  margin:0;
}
.hero-sub{
  margin-top:6px;
  color: rgba(17,24,39,0.70);
  font-weight: 600;
}
.hero-badges{
  display:flex; gap:10px; flex-wrap:wrap; justify-content:flex-end;
}
.badge{
  padding: 8px 12px;
  border-radius: 999px;
  border: 1px solid rgba(229,231,235,0.9);
  background: rgba(255,255,255,0.78);
  font-weight: 800;
  letter-spacing: .4px;
  color: rgba(17,24,39,0.72);
  font-size: 12px;
}
.grid{
  display:grid;
  grid-template-columns: repeat(12, 1fr);
  gap: 14px;
  margin-top: 16px;
}
.card{
  border-radius: 20px;
  border: 1px solid rgba(229,231,235,0.9);
  background: rgba(255,255,255,0.92);
  box-shadow: 0 10px 26px rgba(15,23,42,0.05);
  padding: 18px 18px;
  transition: transform .12s ease, filter .12s ease;
}
.card:hover{transform: translateY(-2px); filter: brightness(1.01);}
.card h3{margin:0 0 6px 0;font-size: 15px;letter-spacing:.2px;color:#111827;}
.card p{margin:0;color: rgba(17,24,39,0.68); font-weight: 600; font-size: 13px; line-height: 1.35;}
.card .meta{margin-top:10px;color: rgba(17,24,39,0.50); font-weight:700; font-size:12px;}
/* tamanhos */
.span-6{grid-column: span 6;}
.span-4{grid-column: span 4;}
.span-8{grid-column: span 8;}
.span-12{grid-column: span 12;}
/* CTA button */
.portal-btn button{
  width:100%;
  height: 48px;
  border-radius: 14px !important;
  font-weight: 900 !important;
}
.section-title{
  margin-top: 18px;
  font-weight: 950;
  letter-spacing: .3px;
  color:#111827;
}
.small-note{color: rgba(17,24,39,0.60); font-weight:600;}
</style>
""", unsafe_allow_html=True)

    st.markdown('<div class="portal-wrap">', unsafe_allow_html=True)

    # HERO
    wm_html = f"<img src='{wordmark}' style='height:20px; width:auto; object-fit:contain;' />" if wordmark else "OMNISFERA"
    st.markdown(f"""
<div class="portal-hero">
  <div class="hero-left">
    <img src="{logo_spin}" class="hero-logo" alt="Omnisfera" />
    <div>
      <div class="hero-title">{wm_html}</div>
      <div class="hero-sub">Inclusão com evidências • PEI • PAEE • Monitoramento • DUA</div>
    </div>
  </div>
  <div class="hero-badges">
    <div class="badge">LBI</div>
    <div class="badge">DUA</div>
    <div class="badge">BNCC</div>
    <div class="badge">PAEE</div>
    <div class="badge">PEI</div>
  </div>
</div>
""", unsafe_allow_html=True)

    # MENU EM CARDS (sem topbar minimal)
    st.markdown("### Acesso rápido", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown("""
<div class="card">
  <h3>👥 Estudantes</h3>
  <p>Cadastro, histórico, evidências e trilhas.</p>
  <div class="meta">Comece por aqui para vincular PEI/PAEE</div>
</div>
""", unsafe_allow_html=True)
        if st.button("Abrir Estudantes", use_container_width=True, key="go_estudantes"):
            st.session_state.view = "estudantes"
            st.rerun()

    with c2:
        st.markdown("""
<div class="card">
  <h3>🧩 Estratégias & PEI</h3>
  <p>Barreiras, níveis de suporte, estratégias e rubricas.</p>
  <div class="meta">Documento vivo do estudante</div>
</div>
""", unsafe_allow_html=True)
        if st.button("Abrir PEI", use_container_width=True, key="go_pei"):
            st.session_state.view = "pei"
            st.rerun()

    with c3:
        st.markdown("""
<div class="card">
  <h3>📍 Plano de Ação (PAEE)</h3>
  <p>Metas SMART, ações, responsabilidades e cronograma.</p>
  <div class="meta">Da estratégia para a prática</div>
</div>
""", unsafe_allow_html=True)
        if st.button("Abrir PAEE", use_container_width=True, key="go_paee"):
            st.session_state.view = "paee"
            st.rerun()

    c4, c5, c6 = st.columns(3)
    with c4:
        st.markdown("""
<div class="card">
  <h3>💡 Hub de Recursos</h3>
  <p>Banco curado: adaptações, TA, atividades e modelos.</p>
  <div class="meta">Rápido para aplicar em sala</div>
</div>
""", unsafe_allow_html=True)
        if st.button("Abrir Hub", use_container_width=True, key="go_hub"):
            st.session_state.view = "hub"
            st.rerun()

    with c5:
        st.markdown("""
<div class="card">
  <h3>🧭 Diário de Bordo</h3>
  <p>Registros breves, contexto, hipóteses e decisões.</p>
  <div class="meta">Ainda vamos construir</div>
</div>
""", unsafe_allow_html=True)
        if st.button("Abrir Diário", use_container_width=True, key="go_diario"):
            st.session_state.view = "diario"
            st.rerun()

    with c6:
        st.markdown("""
<div class="card">
  <h3>📈 Evolução & Acompanhamento</h3>
  <p>Indicadores, rubricas, evidências e progresso.</p>
  <div class="meta">Acompanhamento longitudinal</div>
</div>
""", unsafe_allow_html=True)
        if st.button("Abrir Monitoramento", use_container_width=True, key="go_mon"):
            st.session_state.view = "mon"
            st.rerun()

    # CONTEÚDO DE INCLUSÃO (estrutura pronta pra você colar)
    st.markdown("<div class='section-title'>Inclusão em 60 segundos</div>", unsafe_allow_html=True)
    st.markdown("""
- **Barreiras** (LBI): não é “o aluno”, é o que impede participação.
- **DUA**: múltiplas formas de **engajamento**, **representação** e **ação/expressão**.
- **PEI**: plano pedagógico individual que organiza necessidades, estratégias e evidências.
- **PAEE**: transforma o PEI em ações/rotina e responsabilidades (na escola e rede de apoio).
- **Evidência + Rubrica**: acompanhamento contínuo do progresso (não só “relato”).
""")

    st.markdown("<div class='section-title'>Biblioteca de referência</div>", unsafe_allow_html=True)
    st.caption("Cole aqui suas informações e vamos transformar em uma base navegável (cards, tags e busca).")

    with st.expander("📘 Marco legal e diretrizes (LBI, Política Nacional, etc.)", expanded=False):
        st.info("Cole aqui seus textos. Depois eu organizo em tópicos, resumos e ‘o que isso muda na prática’.")

    with st.expander("🧠 DUA na prática (exemplos rápidos por área)", expanded=False):
        st.info("Cole exemplos e eu devolvo em ‘receitas rápidas’ com sugestões para diferentes níveis de suporte.")

    with st.expander("🧩 PEI/PAEE (modelos e orientações)", expanded=False):
        st.info("Cole sua estrutura, e eu organizo em um guia operacional dentro do Omnisfera.")

    with st.expander("🛠️ Tecnologia Assistiva (baixa/média/alta)", expanded=False):
        st.info("Cole recursos/links e eu transformo em um hub com filtros (objetivo, barreira, contexto).")

    st.markdown("</div>", unsafe_allow_html=True)  # portal-wrap
