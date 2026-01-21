import streamlit as st
from supabase_client import supabase

st.set_page_config(page_title="Omnisfera", page_icon="🌿", layout="centered")

# -----------------------------
# Estado
# -----------------------------
if "workspace" not in st.session_state:
    st.session_state.workspace = None

# -----------------------------
# Supabase RPC
# -----------------------------
def workspace_from_pin(pin: str):
    pin = (pin or "").strip()
    if not pin:
        return None

    try:
        res = supabase.schema("public").rpc(
            "workspace_from_pin",
            {"p_pin": pin}
        ).execute()

        if res.data and len(res.data) == 1:
            return res.data[0]
        return None

    except Exception as e:
        st.error("Falha ao validar PIN no Supabase. Abra Manage app → Logs para ver o detalhe.")
        st.caption(f"Detalhe técnico: {type(e).__name__}")
        return None


# -----------------------------
# UI (leve + elegante)
# -----------------------------
st.markdown(
    """
<style>
.block-container { padding-top: 4.5rem; max-width: 520px; }
.omni-card{
  border: 1px solid rgba(15, 23, 42, .10);
  border-radius: 18px;
  padding: 22px 22px 18px;
  background: rgba(255,255,255,.85);
  box-shadow: 0 10px 30px rgba(15, 23, 42, .08);
}
.omni-title{ font-size: 34px; font-weight: 800; letter-spacing:-0.02em; margin: 0 0 6px; }
.omni-sub{ color: rgba(15, 23, 42, .65); margin: 0 0 18px; }
.omni-badge{
  display:inline-block; padding:6px 10px; border-radius:999px;
  font-size:12px; border:1px solid rgba(15,23,42,.12);
  color: rgba(15,23,42,.65);
}
</style>
""",
    unsafe_allow_html=True,
)

# -----------------------------
# Se já tem workspace, mostra e permite trocar
# -----------------------------
if st.session_state.workspace:
    st.markdown("<div class='omni-card'>", unsafe_allow_html=True)
    st.markdown("<div class='omni-badge'>Workspace ativo</div>", unsafe_allow_html=True)
    st.markdown(
        f"<div class='omni-title'>{st.session_state.workspace['name']}</div>",
        unsafe_allow_html=True,
    )
    st.caption(f"workspace_id: {st.session_state.workspace['id']}")
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("Entrar no sistema", use_container_width=True, type="primary"):
            st.switch_page("pages/home.py")  # Home real do app
    with col2:
        if st.button("Trocar PIN", use_container_width=True):
            st.session_state.workspace = None
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# -----------------------------
# Tela de PIN
# -----------------------------
st.markdown("<div class='omni-card'>", unsafe_allow_html=True)
st.markdown("<div class='omni-badge'>Acesso por PIN</div>", unsafe_allow_html=True)
st.markdown("<div class='omni-title'>Omnisfera</div>", unsafe_allow_html=True)
st.markdown("<p class='omni-sub'>Digite o PIN da escola para acessar o ambiente.</p>", unsafe_allow_html=True)

with st.form("pin_form", clear_on_submit=False):
    pin = st.text_input("PIN da escola", placeholder="Ex: DEMO-2026")
    entrar = st.form_submit_button("Validar e entrar", type="primary")

    if entrar:
        ws = workspace_from_pin(pin)
        if ws:
            st.session_state.workspace = {"id": ws["id"], "name": ws["name"]}
            st.success(f"✅ Escola validada: {ws['name']}")
            st.rerun()
        else:
            st.error("PIN inválido. Verifique e tente novamente.")

st.markdown("</div>", unsafe_allow_html=True)
