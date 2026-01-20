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
# HEADER
# -----------------------------------------------------------------------------
st.title("Home — Omnisfera")

user = st.session_state.user or {}
st.caption(f"Logado como: {user.get('email', '—')}")

# -----------------------------------------------------------------------------
# LOGOUT
# -----------------------------------------------------------------------------
if st.button("Sair"):
    st.session_state.autenticado = False
    st.session_state.user = None
    st.query_params["go"] = "login"
    st.stop()

# -----------------------------------------------------------------------------
# CONTEÚDO DA HOME (EXEMPLO SEGURO)
# -----------------------------------------------------------------------------
# Verificação segura de ícone (NÃO quebra se não existir)
ICON_PATH = "omni_icone.png"

if os.path.exists(ICON_PATH):
    st.image(ICON_PATH, width=80)
else:
    st.markdown("🌿")

st.info(
    "Agora é aqui que vamos resgatar sua Home rica com cards, métricas "
    "e navegação elegante — com a base finalmente estável."
)
