# streamlit_app.py
import os
import streamlit as st
from supabase import create_client

# =============================================================================
# Omnisfera — Tela Inicial (PIN) — versão mínima e estável (sem loops)
# =============================================================================

APP_TITLE = "Omnisfera"

# -------------------------------
# Helpers: Supabase client
# -------------------------------
@st.cache_resource(show_spinner=False)
def get_supabase():
    url = st.secrets.get("SUPABASE_URL", None) if hasattr(st, "secrets") else None
    key = st.secrets.get("SUPABASE_ANON_KEY", None) if hasattr(st, "secrets") else None

    # fallback local (opcional)
    url = url or os.getenv("SUPABASE_URL")
    key = key or os.getenv("SUPABASE_ANON_KEY")

    if not url or not key:
        raise RuntimeError("SUPABASE_URL / SUPABASE_ANON_KEY não configurados.")
    return create_client(url, key)

def workspace_from_pin(pin: str):
    """
    Chama a RPC public.workspace_from_pin(p_pin text)
    e espera retorno com colunas: id, name
    """
    sb = get_supabase()
    res = sb.rpc("workspace_from_pin", {"p_pin": pin}).execute()

    # supabase-py retorna .data (list/dict) e .error em versões diferentes;
    # vamos ser defensivos:
    data = getattr(res, "data", None)
    error = getattr(res, "error", None)

    if error:
        # Erro PostgREST / permissões / etc.
        raise RuntimeError(str(error))

    if not data:
        return None

    # normal: data pode ser lista com 1 item ou dict
    if isinstance(data, list):
        return data[0] if data else None
    if isinstance(data, dict):
        return data
    return None

# -------------------------------
# Estado mínimo
# -------------------------------
def ensure_state():
    if "pin_validado" not in st.session_state:
        st.session_state.pin_validado = False
    if "workspace_id" not in st.session_state:
        st.session_state.workspace_id = None
    if "workspace_name" not in st.session_state:
        st.session_state.workspace_name = None
    if "workspace_pin" not in st.session_state:
        st.session_state.workspace_pin = ""

def reset_session():
    for k in ["pin_validado", "workspace_id", "workspace_name", "workspace_pin"]:
        if k in st.session_state:
            del st.session_state[k]

# -------------------------------
# UI
# -------------------------------
def inject_css():
    st.markdown(
        """
        <style>
          .omni-wrap {max-width: 880px; margin: 0 auto; padding-top: 10px;}
          .omni-hero {padding: 14px 6px 18px 6px;}
          .omni-title {font-size: 56px; font-weight: 800; line-height: 1; margin: 10px 0 4px 0;}
          .omni-sub {font-size: 18px; opacity: .7; margin-bottom: 22px;}
          .card {border: 1px solid rgba(0,0,0,.08); border-radius: 16px; padding: 18px 18px 14px 18px; background: rgba(255,255,255,.7);}
          .row {display:flex; gap:14px; flex-wrap:wrap;}
          .pill {display:inline-block; padding: 6px 10px; border-radius: 999px; border:1px solid rgba(0,0,0,.10); background: rgba(255,255,255,.65); font-size: 14px;}
          .ok {padding: 10px 12px; border-radius: 12px; border: 1px solid rgba(0,128,0,.25); background: rgba(0,255,0,.08);}
          .bad {padding: 10px 12px; border-radius: 12px; border: 1px solid rgba(255,0,0,.18); background: rgba(255,0,0,.06);}
          .muted {opacity: .65;}
          .spacer {height: 14px;}
        </style>
        """,
        unsafe_allow_html=True,
    )

def render_login():
    st.markdown("<div class='omni-hero'>", unsafe_allow_html=True)
    st.markdown("<div class='pill'>Acesso por PIN</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='omni-title'>{APP_TITLE}</div>", unsafe_allow_html=True)
    st.markdown("<div class='omni-sub'>Digite o PIN da escola para acessar o ambiente.</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='card'>", unsafe_allow_html=True)

    pin = st.text_input(
        "PIN da escola",
        value=st.session_state.workspace_pin or "",
        placeholder="Ex.: DEMO-2026",
    ).strip()

    c1, c2 = st.columns([1, 1])
    with c1:
        validar = st.button("Validar e entrar", use_container_width=True)
    with c2:
        limpar = st.button("Limpar", use_container_width=True)

    if limpar:
        st.session_state.workspace_pin = ""
        st.rerun()

    if validar:
        st.session_state.workspace_pin = pin

        if not pin:
            st.markdown("<div class='bad'>Digite um PIN.</div>", unsafe_allow_html=True)
        else:
            with st.spinner("Validando PIN..."):
                try:
                    ws = workspace_from_pin(pin)
                except Exception as e:
                    st.markdown(
                        f"<div class='bad'><b>Erro ao validar PIN</b><br><span class='muted'>{str(e)}</span></div>",
                        unsafe_allow_html=True,
                    )
                    ws = None

            if not ws:
                st.markdown("<div class='bad'>PIN inválido ou não encontrado.</div>", unsafe_allow_html=True)
            else:
                # salva estado mínimo
                st.session_state.pin_validado = True
                st.session_state.workspace_id = ws.get("id")
                st.session_state.workspace_name = ws.get("name") or "Workspace"

                st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

def render_session_panel():
    st.markdown("<div class='omni-hero'>", unsafe_allow_html=True)
    st.markdown("<div class='pill'>Sessão ativa</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='omni-title'>{APP_TITLE}</div>", unsafe_allow_html=True)
    st.markdown("<div class='omni-sub'>PIN validado com sucesso. (Por enquanto, esta tela só confirma o estado.)</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("<div class='ok'><b>Conectado ✅</b></div>", unsafe_allow_html=True)
    st.markdown("<div class='spacer'></div>", unsafe_allow_html=True)

    r1 = st.columns([2, 3])
    with r1[0]:
        st.caption("Workspace")
        st.write(st.session_state.workspace_name)
    with r1[1]:
        st.caption("Workspace ID")
        st.code(str(st.session_state.workspace_id))

    st.markdown("<div class='spacer'></div>", unsafe_allow_html=True)

    colA, colB = st.columns([2, 1])
    with colA:
        st.caption("PIN usado (somente para depuração)")
        st.code(st.session_state.workspace_pin or "")
    with colB:
        if st.button("Sair / Trocar PIN", use_container_width=True):
            reset_session()
            st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

# -------------------------------
# Main
# -------------------------------
def main():
    st.set_page_config(
        page_title="Omnisfera • PIN",
        page_icon="🌿",
        layout="centered",
        initial_sidebar_state="collapsed",
    )

    ensure_state()
    inject_css()

    # Importante: SEM switch_page, SEM redirect.
    if not st.session_state.pin_validado or not st.session_state.workspace_id:
        render_login()
    else:
        render_session_panel()

if __name__ == "__main__":
    main()
