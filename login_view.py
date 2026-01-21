# login_view.py
import os
import base64
from datetime import datetime
import streamlit as st

from supabase_client import rpc_workspace_from_pin, RPC_NAME


def _get_env_flag() -> str:
    try:
        v = st.secrets.get("ENV", None)
        if v:
            return str(v).strip().upper()
    except Exception:
        pass
    return str(os.getenv("ENV", "")).strip().upper()


def maybe_hide_streamlit_chrome():
    if _get_env_flag() == "TESTE":
        return
    st.markdown(
        """
        <style>
          #MainMenu {visibility: hidden;}
          header {visibility: hidden;}
          footer {visibility: hidden;}
          [data-testid="stToolbar"] {visibility: hidden;}
          [data-testid="stDecoration"] {visibility: hidden;}
          [data-testid="stStatusWidget"] {visibility: hidden;}
          [data-testid="stAppDeployButton"] {display:none;}
          .block-container { padding-top: 1.2rem; }
        </style>
        """,
        unsafe_allow_html=True,
    )


def _b64_logo_from_file() -> str | None:
    for f in ["omni_icone.png", "logo.png", "iconeaba.png", "omni.png", "omnisfera.png"]:
        if os.path.exists(f):
            with open(f, "rb") as img:
                return base64.b64encode(img.read()).decode("utf-8")
    return None


def inject_css():
    st.markdown(
        """
        <style>
          :root{
            --muted:#6b7280;
            --text:#111827;
            --border:rgba(17,24,39,.08);
            --shadow: 0 10px 30px rgba(17,24,39,.06);
          }
          .omni-wrap{ max-width: 980px; margin: 0 auto; padding: 24px 18px 64px; }
          .top-chip{
            display:inline-flex; align-items:center; gap:8px;
            border:1px solid var(--border);
            padding: 6px 10px; border-radius: 999px;
            font-size: 13px; color: var(--muted);
            background: rgba(17,24,39,.02);
          }
          .brand{ display:flex; align-items:center; gap:14px; margin-top: 18px; }
          .logoSpin{
            width:56px;height:56px; border-radius:16px;
            display:inline-flex; align-items:center; justify-content:center;
            background: rgba(22,163,74,.08);
            border:1px solid rgba(22,163,74,.18);
            box-shadow: 0 8px 22px rgba(17,24,39,.06);
            overflow:hidden;
          }
          .logoSpin img{
            width:34px;height:34px;
            animation: spin 6.5s linear infinite;
            transform-origin:center;
          }
          @keyframes spin{ 0%{transform: rotate(0deg);} 100%{transform: rotate(360deg);} }
          .title{ font-size: 58px; line-height: 1.02; letter-spacing: -0.04em; margin: 0; color: var(--text); }
          .subtitle{ margin-top: 10px; color: var(--muted); font-size: 16px; }

          .card{
            margin-top: 18px;
            background: #fff;
            border:1px solid var(--border);
            box-shadow: var(--shadow);
            border-radius: 18px;
            padding: 18px;
          }
          .mono{
            font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
          }
          .hint{ color: var(--muted); font-size: 13px; }
        </style>
        """,
        unsafe_allow_html=True,
    )


def ensure_auth_state():
    # ✅ estado oficial do app
    if "autenticado" not in st.session_state:
        st.session_state.autenticado = False

    if "workspace_id" not in st.session_state:
        st.session_state.workspace_id = None
    if "workspace_name" not in st.session_state:
        st.session_state.workspace_name = None

    # opcionais
    if "pin_debug" not in st.session_state:
        st.session_state.pin_debug = None
    if "connected" not in st.session_state:
        st.session_state.connected = False
    if "last_auth_ts" not in st.session_state:
        st.session_state.last_auth_ts = None
    if "rpc_used" not in st.session_state:
        st.session_state.rpc_used = RPC_NAME

    if "usuario_nome" not in st.session_state:
        st.session_state.usuario_nome = "Visitante"
    if "usuario_cargo" not in st.session_state:
        st.session_state.usuario_cargo = ""


def clear_session():
    st.session_state.autenticado = False
    st.session_state.workspace_id = None
    st.session_state.workspace_name = None
    st.session_state.pin_debug = None
    st.session_state.connected = False
    st.session_state.last_auth_ts = None
    st.session_state.rpc_used = RPC_NAME


def render_login():
    maybe_hide_streamlit_chrome()
    inject_css()
    ensure_auth_state()

    logo_b64 = _b64_logo_from_file()
    logo_html = f"<img src='data:image/png;base64,{logo_b64}'/>" if logo_b64 else ""

    st.markdown(
        f"""
        <div class="omni-wrap">
          <div class="top-chip">Ambiente por PIN</div>
          <div class="brand">
            <div class="logoSpin">{logo_html}</div>
            <div>
              <h1 class="title">Omnisfera</h1>
              <div class="subtitle">Valide o PIN para entrar no workspace.</div>
            </div>
          </div>

          <div class="card">
            <div style="font-weight:700; font-size:16px; margin-bottom:6px;">Validar PIN</div>
            <div class="hint">Função (RPC) usada: <span class="mono">{RPC_NAME}(p_pin text)</span></div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="omni-wrap">', unsafe_allow_html=True)
    c1, c2 = st.columns([2, 1], gap="large")

    with c1:
        pin = st.text_input(
            "PIN do Workspace",
            value="",
            placeholder="Ex.: 3D6C-9718",
            label_visibility="collapsed",
        )
        st.caption("Pode colar com ou sem hífen; o app normaliza.")

    with c2:
        do = st.button("Validar e entrar", use_container_width=True)

    pin_norm = (pin or "").strip().upper().replace(" ", "")
    if len(pin_norm) == 8 and "-" not in pin_norm:
        pin_norm = pin_norm[:4] + "-" + pin_norm[4:]

    if do:
        if not pin_norm or len(pin_norm) < 6:
            st.error("Digite um PIN válido.")
        else:
            with st.spinner("Validando PIN..."):
                ws = rpc_workspace_from_pin(pin_norm)

            if not ws:
                st.error("PIN não encontrado ou inválido.")
            else:
                st.session_state.autenticado = True
                st.session_state.workspace_id = ws.get("id")
                st.session_state.workspace_name = ws.get("name")

                st.session_state.pin_debug = pin_norm
                st.session_state.connected = True
                st.session_state.last_auth_ts = datetime.now().strftime("%d/%m/%Y %H:%M")
                st.session_state.rpc_used = RPC_NAME

                st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

    if st.session_state.autenticado and st.session_state.workspace_id:
        st.markdown('<div class="omni-wrap">', unsafe_allow_html=True)
        if st.button("Sair / Trocar PIN", use_container_width=True):
            clear_session()
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
