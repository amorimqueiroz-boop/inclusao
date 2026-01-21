import streamlit as st

def require_workspace():
    """
    Guard padrão: impede abrir qualquer página sem workspace válido.
    E oferece retorno ao Início.
    """
    ws_id = st.session_state.get("workspace_id")
    ws_name = st.session_state.get("workspace_name")

    if not ws_id or not ws_name:
        st.error("Workspace não definido. Volte ao Início e valide o PIN novamente.")

        c1, c2 = st.columns([1, 1])
        with c1:
            if st.button("⬅️ Voltar ao Início"):
                # tenta mandar o usuário para o início
                try:
                    st.switch_page("streamlit_app.py")
                except Exception:
                    # fallback (caso switch_page falhe)
                    st.session_state["__go_home__"] = True
                    st.rerun()

        with c2:
            if st.button("🧹 Limpar sessão"):
                for k in ["workspace_id", "workspace_name", "workspace_at"]:
                    st.session_state.pop(k, None)
                try:
                    st.switch_page("streamlit_app.py")
                except Exception:
                    st.session_state["__go_home__"] = True
                    st.rerun()

        st.stop()

    return ws_id, ws_name


def clear_workspace():
    for k in ["workspace_id", "workspace_name", "workspace_at"]:
        st.session_state.pop(k, None)
