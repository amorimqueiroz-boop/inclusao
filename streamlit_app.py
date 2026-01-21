# streamlit_app.py
import os
import time
import base64
import streamlit as st

from supabase_client import rpc_workspace_from_pin, RPC_NAME


# ------------------------------------------------------------
# 0) Config
# ------------------------------------------------------------
st.set_page_config(
    page_title="Omnisfera",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ------------------------------------------------------------
# 1) Guard de ambiente (SECRETS)
# - Se ENV != "TESTE" => esconde menus do Streamlit (protege secrets)
# ------------------------------------------------------------
def _get_env():
    try:
        v = st.secrets.get("ENV", None)
        if v:
            return str(v).strip().upper()
    except Exception:
        pass
    return (os.getenv("ENV") or "").strip().upper()

ENV = _get_env()

def hide_streamlit_chrome_if_needed():
    if ENV == "TESTE":
        return  # em teste, não escondemos
    st.markdown(
        """
        <style>
          #MainMenu {visibility: hidden;}
          footer {visibility: hidden;}
          header {visibility: hidden;}
        </style>
        """,
        unsafe_allow_html=True,
    )

hide_streamlit_chrome_if_needed()


# ------------------------------------------------------------
# 2) Estado de sessão (NÃO pode ficar em imports externos)
# ------------------------------------------------------------
def ensure_state():
    if "autenticado" not in st.session_state:
        st.session_state.autenticado = False
    if "workspace_id" not in st.session_state:
        st.session_state.workspace_id = None
    if "workspace_name" not in st.session_state:
        st.session_state.workspace_name = None
    if "pin" not in st.session_state:
        st.session_state.pin = ""
    if "pin_ok_at" not in st.session_state:
        st.session_state.pin_ok_at = None

ensure_state()


# ------------------------------------------------------------
# 3) Helpers UI
# ------------------------------------------------------------
def _logo_base64(paths=("omni_icone.png", "logo.png", "iconeaba.png", "omni.png", "omnisfera.png")):
    for p in paths:
        if os.path.exists(p):
            with open(p, "rb") as f:
                return base64.b64encode(f.read()).decode("utf-8")
    return None

LOGO64 = _logo_base64()

def css_global():
    spin_css = ""
    if LOGO64:
        spin_css = f"""
        .omni-spin {{
            width: 56px; height: 56px;
            border-radius: 18px;
            display:flex; align-items:center; justify-content:center;
            background: #f3f5f7;
            box-shadow: 0 8px 24px rgba(0,0,0,.08);
        }}
        .omni-spin img {{
            width: 34px; height: 34px;
            animation: omniRotate 3.6s linear infinite;
            transform-origin: 50% 50%;
        }}
        @keyframes omniRotate {{
            from {{ transform: rotate(0deg); }}
            to   {{ transform: rotate(360deg); }}
        }}
        """
    st.markdown(
        f"""
        <style>
          :root {{
            --bg: #ffffff;
            --card: #ffffff;
            --muted: #6b7280;
            --text: #111827;
            --border: rgba(17,24,39,.08);
            --shadow: 0 18px 44px rgba(0,0,0,.08);
            --shadow2: 0 8px 24px rgba(0,0,0,.06);
            --green: #16a34a;
            --red: #ef4444;
          }}

          .block-container {{
            padding-top: 2.2rem;
            padding-bottom: 2.2rem;
            max-width: 1100px;
          }}

          .omni-wrap {{
            display:flex; flex-direction:column;
            gap: 22px;
          }}

          .hero {{
            display:flex; align-items:center; gap: 16px;
          }}

          .badge {{
            display:inline-flex;
            align-items:center;
            gap:8px;
            padding: 6px 12px;
            border-radius: 999px;
            background: rgba(17,24,39,.04);
            color: var(--muted);
            font-size: 13px;
          }}

          h1.omni-title {{
            margin:0;
            font-size: 54px;
            line-height: 1.0;
            letter-spacing: -1.2px;
            color: var(--text);
          }}

          .subtitle {{
            color: var(--muted);
            font-size: 16px;
            margin-top: 6px;
          }}

          .card {{
            background: var(--card);
            border: 1px solid var(--border);
            border-radius: 18px;
            box-shadow: var(--shadow2);
            padding: 18px 18px;
          }}

          .card h3 {{
            margin: 0 0 4px 0;
            font-size: 18px;
            color: var(--text);
          }}

          .small {{
            color: var(--muted);
            font-size: 13px;
          }}

          .ok {{
            background: rgba(22,163,74,.10);
            border: 1px solid rgba(22,163,74,.22);
            color: var(--green);
            border-radius: 14px;
            padding: 12px 14px;
            font-weight: 600;
          }}

          .err {{
            background: rgba(239,68,68,.10);
            border: 1px solid rgba(239,68,68,.20);
            color: var(--red);
            border-radius: 14px;
            padding: 12px 14px;
            font-weight: 600;
          }}

          .grid3 {{
            display:grid;
            grid-template-columns: 1fr 1fr 1fr;
            gap: 14px;
          }}

          @media (max-width: 960px) {{
            .grid3 {{ grid-template-columns: 1fr; }}
            h1.omni-title {{ font-size: 40px; }}
          }}

          {spin_css}
        </style>
        """,
        unsafe_allow_html=True,
    )

css_global()


def normalize_pin(raw: str) -> str:
    if not raw:
        return ""
    s = str(raw).strip().upper()
    s = s.replace(" ", "").replace("_", "-")
    # remove caracteres estranhos
    s = "".join([c for c in s if c.isalnum() or c == "-"])
    # se veio sem hífen e tem 8 chars, formata AAAA-BBBB
    if "-" not in s and len(s) == 8:
        s = f"{s[:4]}-{s[4:]}"
    return s


def do_logout():
    st.session_state.autenticado = False
    st.session_state.workspace_id = None
    st.session_state.workspace_name = None
    st.session_state.pin_ok_at = None
    st.session_state.pin = ""
    st.rerun()


# ------------------------------------------------------------
# 4) UI — LOGIN
# ------------------------------------------------------------
def render_login():
    st.markdown("<div class='omni-wrap'>", unsafe_allow_html=True)

    st.markdown("<div class='badge'>Sessão / PIN</div>", unsafe_allow_html=True)

    # HERO
    st.markdown("<div class='hero'>", unsafe_allow_html=True)
    if LOGO64:
        st.markdown(
            f"""
            <div class="omni-spin">
              <img src="data:image/png;base64,{LOGO64}" />
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown("<div class='badge'>🌿</div>", unsafe_allow_html=True)

    st.markdown(
        """
        <div>
          <h1 class="omni-title">Omnisfera</h1>
          <div class="subtitle">Valide o PIN para vincular um workspace via Supabase RPC.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)

    # CARD PIN
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("<h3>Validar PIN</h3>", unsafe_allow_html=True)
    st.markdown(
        f"<div class='small'>Função (RPC) usada: <code>{RPC_NAME}(p_pin text)</code></div>",
        unsafe_allow_html=True,
    )

    c1, c2 = st.columns([4, 1])
    with c1:
        pin_in = st.text_input(
            "PIN",
            value=st.session_state.pin,
            placeholder="Ex.: 3D6C-9718",
            label_visibility="collapsed",
        )
        st.caption("Pode colar com ou sem hífen; o app normaliza.")
    with c2:
        clicked = st.button("Validar e entrar", use_container_width=True)

    st.markdown("</div>", unsafe_allow_html=True)  # end card

    # Feedback + ação
    if clicked:
        pin_norm = normalize_pin(pin_in)
        st.session_state.pin = pin_norm

        if not pin_norm:
            st.markdown("<div class='err'>Informe um PIN válido.</div>", unsafe_allow_html=True)
            st.stop()

        with st.spinner("Validando PIN no Supabase..."):
            try:
                ws = rpc_workspace_from_pin(pin_norm)
            except Exception as e:
                st.markdown(
                    "<div class='err'>Falha ao consultar o Supabase. Verifique Secrets e RPC.</div>",
                    unsafe_allow_html=True,
                )
                st.exception(e)
                st.stop()

        if not ws or not ws.get("id"):
            st.markdown("<div class='err'>PIN não encontrado ou inválido.</div>", unsafe_allow_html=True)
            st.stop()

        # ✅ sucesso: grava estado e RE-RENDERIZA outra tela (sem loop)
        st.session_state.autenticado = True
        st.session_state.workspace_id = ws["id"]
        st.session_state.workspace_name = ws.get("name") or "Workspace"
        st.session_state.pin_ok_at = time.strftime("%d/%m/%Y %H:%M")
        st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)  # end wrap


# ------------------------------------------------------------
# 5) UI — HOME (depois do PIN)
# ------------------------------------------------------------
def render_home():
    st.markdown("<div class='omni-wrap'>", unsafe_allow_html=True)

    st.markdown("<div class='badge'>Sessão ativa</div>", unsafe_allow_html=True)

    # HERO
    st.markdown("<div class='hero'>", unsafe_allow_html=True)
    if LOGO64:
        st.markdown(
            f"""
            <div class="omni-spin">
              <img src="data:image/png;base64,{LOGO64}" />
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown("<div class='badge'>🌿</div>", unsafe_allow_html=True)

    st.markdown(
        f"""
        <div>
          <h1 class="omni-title">Omnisfera</h1>
          <div class="subtitle">PIN validado e vinculado a um workspace via Supabase RPC.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)

    # STATUS
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("<div class='ok'>Conectado ✅</div>", unsafe_allow_html=True)
    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

    g1, g2 = st.columns([1, 1])
    with g1:
        st.caption("Workspace")
        st.write(st.session_state.workspace_name or "—")
    with g2:
        st.caption("Workspace ID")
        st.code(str(st.session_state.workspace_id), language=None)

    st.caption("PIN usado (somente para depuração)")
    st.code(st.session_state.pin or "—", language=None)

    st.markdown("</div>", unsafe_allow_html=True)

    # Ações (por enquanto)
    st.markdown("<div class='grid3'>", unsafe_allow_html=True)
    st.markdown(
        """
        <div class='card'>
          <h3>Atalho</h3>
          <div class='small'>Cadastrar aluno (em seguida vamos reconstruir).</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        """
        <div class='card'>
          <h3>Atalho</h3>
          <div class='small'>Abrir PEI (depois de arrumar a página Alunos).</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        """
        <div class='card'>
          <h3>Status</h3>
          <div class='small'>Conectividade do backend e RPC por PIN.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)

    # Sair
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    if st.button("Sair / Trocar PIN"):
        do_logout()

    st.markdown("</div>", unsafe_allow_html=True)


# ------------------------------------------------------------
# 6) Roteamento local (sem pages, sem loop)
# ------------------------------------------------------------
if st.session_state.autenticado and st.session_state.workspace_id:
    render_home()
else:
    render_login()
