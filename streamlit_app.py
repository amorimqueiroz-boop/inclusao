import streamlit as st
from datetime import datetime

# ajuste o import conforme seu projeto
from _client import get_supabase

st.set_page_config(
    page_title="Omnisfera • Início",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ----------------------------
# helpers
# ----------------------------
def clear_workspace():
    for k in ["workspace_id", "workspace_name", "workspace_at"]:
        st.session_state.pop(k, None)

def has_workspace():
    return bool(st.session_state.get("workspace_id")) and bool(st.session_state.get("workspace_name"))

def validate_pin(pin: str):
    """
    Chama RPC workspace_from_pin(p_pin text) -> retorna tabela(id uuid, name text)
    """
    sb = get_supabase()
    # no supabase-py, o retorno costuma vir em res.data
    res = sb.rpc("workspace_from_pin", {"p_pin": pin}).execute()
    data = getattr(res, "data", None) or []
    return data


# ----------------------------
# UI - Header
# ----------------------------
st.markdown(
    """
    <div style="padding: 6px 0 18px 0;">
      <div style="font-size: 44px; font-weight: 800; letter-spacing: -0.02em;">Omnisfera</div>
      <div style="font-size: 16px; color: #6b7280; margin-top: 6px;">
        Digite o PIN da escola para acessar o ambiente.
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ----------------------------
# Status atual (sem redirecionar!)
# ----------------------------
c1, c2, c3 = st.columns([2, 2, 2])
with c1:
    st.markdown("**Status**")
    st.write("Workspace definido:" , has_workspace())

with c2:
    st.markdown("**Workspace**")
    st.write(st.session_state.get("workspace_name", "—"))

with c3:
    st.markdown("**Workspace ID**")
    st.code(st.session_state.get("workspace_id", "—") or "—")


st.divider()

# ----------------------------
# Form PIN
# ----------------------------
with st.container():
    st.markdown("### Acesso por PIN")

    pin = st.text_input(
        "PIN da escola",
        value=st.session_state.get("last_pin", "DEMO-2026"),
        placeholder="ex.: DEMO-2026",
    )

    b1, b2, b3 = st.columns([1, 1, 3])
    with b1:
        validar = st.button("✅ Validar PIN", use_container_width=True)
    with b2:
        limpar = st.button("🧹 Limpar sessão", use_container_width=True)
    with b3:
        st.caption("Dica: nesta fase NÃO vamos navegar para páginas — só validar e manter sessão estável.")

    if limpar:
        clear_workspace()
        st.session_state.pop("last_pin", None)
        st.success("Sessão limpa. Agora valide o PIN novamente.")

    if validar:
        pin_norm = (pin or "").strip()
        st.session_state["last_pin"] = pin_norm

        if not pin_norm:
            st.warning("Digite um PIN.")
        else:
            try:
                rows = validate_pin(pin_norm)

                if not rows:
                    clear_workspace()
                    st.error("PIN inválido (nenhum workspace encontrado).")
                else:
                    ws = rows[0]
                    # ws pode vir como dict: {"id": "...", "name": "..."}
                    ws_id = ws.get("id") if isinstance(ws, dict) else None
                    ws_name = ws.get("name") if isinstance(ws, dict) else None

                    if not ws_id or not ws_name:
                        clear_workspace()
                        st.error("RPC retornou dados inesperados. Confira o retorno da função no Supabase.")
                        st.write("Retorno bruto:", rows)
                    else:
                        st.session_state["workspace_id"] = ws_id
                        st.session_state["workspace_name"] = ws_name
                        st.session_state["workspace_at"] = datetime.now().strftime("%d/%m/%Y %H:%M")
                        st.success(f"✅ Ambiente liberado: {ws_name}")

            except Exception as e:
                clear_workspace()
                st.error("Erro ao validar PIN (RPC).")
                st.write("Detalhe técnico:")
                st.exception(e)

st.divider()

# ----------------------------
# Debug (opcional)
# ----------------------------
with st.expander("🔎 Debug da sessão"):
    st.json(
        {
            "workspace_id": st.session_state.get("workspace_id"),
            "workspace_name": st.session_state.get("workspace_name"),
            "workspace_at": st.session_state.get("workspace_at"),
            "last_pin": st.session_state.get("last_pin"),
        }
    )
