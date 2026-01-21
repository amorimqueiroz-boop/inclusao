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
# 1) Ambiente (Secrets) e esconder menu inferior
# ------------------------------------------------------------
def get_env() -> str:
    try:
        v = st.secrets.get("ENV", None)
        if v:
            return str(v).strip().upper()
    except Exception:
        pass
    return (os.getenv("ENV") or "").strip().upper()

ENV = get_env()

def apply_hide_streamlit_chrome():
    """
    Se ENV != TESTE => esconde menu/footer/header (evita acesso a secrets).
    """
    if ENV == "TESTE":
        return
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

apply_hide_streamlit_chrome()


# ------------------------------------------------------------
# 2) Estado (tudo aqui — nada em imports)
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

    # Termo de uso
    if "aceitou_termos" not in st.session_state:
        st.session_state.aceitou_termos = False

ensure_state()


# ------------------------------------------------------------
# 3) Assets / CSS / Helpers
# ------------------------------------------------------------
def logo_base64(paths=("omni_icone.png", "logo.png", "iconeaba.png", "omni.png", "omnisfera.png")):
    for p in paths:
        if os.path.exists(p):
            with open(p, "rb") as f:
                return base64.b64encode(f.read()).decode("utf-8")
    return None

LOGO64 = logo_base64()


def inject_css():
    spin_css = ""
    if LOGO64:
        spin_css = """
        .omni-spin{
          width:56px;height:56px;border-radius:18px;
          display:flex;align-items:center;justify-content:center;
          background:#f3f5f7;
          box-shadow:0 8px 24px rgba(0,0,0,.08);
        }
        .omni-spin img{
          width:34px;height:34px;
          animation: omniRotate 3.6s linear infinite;
          transform-origin: 50% 50%;
        }
        @keyframes omniRotate{from{transform:rotate(0)}to{transform:rotate(360deg)}}
        """

    st.markdown(
        f"""
        <style>
          :root {{
            --bg:#fff; --card:#fff; --muted:#6b7280; --text:#111827;
            --border:rgba(17,24,39,.08);
            --shadow2:0 8px 24px rgba(0,0,0,.06);
            --green:#16a34a; --red:#ef4444;
          }}
          .block-container {{ padding-top:2.2rem; padding-bottom:2.2rem; max-width:1100px; }}
          .wrap {{ display:flex; flex-direction:column; gap:22px; }}

          .badge {{
            display:inline-flex; align-items:center; gap:8px;
            padding:6px 12px; border-radius:999px;
            background:rgba(17,24,39,.04);
            color:var(--muted); font-size:13px;
          }}

          .hero {{ display:flex; align-items:center; gap:16px; }}
          h1.title {{ margin:0; font-size:54px; line-height:1.0; letter-spacing:-1.2px; color:var(--text); }}
          .subtitle {{ color:var(--muted); font-size:16px; margin-top:6px; }}

          .card {{
            background:var(--card);
            border:1px solid var(--border);
            border-radius:18px;
            box-shadow:var(--shadow2);
            padding:18px;
          }}
          .card h3{{ margin:0 0 4px 0; font-size:18px; color:var(--text); }}
          .small{{ color:var(--muted); font-size:13px; }}

          .chip {{
            display:inline-flex; align-items:center; gap:8px;
            padding:6px 10px;
            border-radius:999px;
            border:1px solid var(--border);
            background:rgba(17,24,39,.02);
            color:var(--text);
            font-size:12.5px;
          }}
          .mono {{ font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace; }}

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

          details.terms {{
            border:1px solid var(--border);
            border-radius:14px;
            padding:10px 12px;
            background:rgba(17,24,39,.02);
          }}
          details.terms > summary {{
            cursor:pointer;
            color:var(--text);
            font-weight:600;
          }}
          details.terms p, details.terms li {{
            color:var(--muted);
            font-size:13px;
            line-height:1.35;
          }}

          @media (max-width: 960px) {{
            h1.title {{ font-size: 40px; }}
          }}

          {spin_css}
        </style>
        """,
        unsafe_allow_html=True,
    )

inject_css()


def normalize_pin(raw: str) -> str:
    if not raw:
        return ""
    s = str(raw).strip().upper()
    s = s.replace(" ", "").replace("_", "-")
    s = "".join([c for c in s if c.isalnum() or c == "-"])
    if "-" not in s and len(s) == 8:
        s = f"{s[:4]}-{s[4:]}"
    return s


def logout():
    st.session_state.autenticado = False
    st.session_state.workspace_id = None
    st.session_state.workspace_name = None
    st.session_state.pin_ok_at = None
    st.session_state.pin = ""
    st.session_state.aceitou_termos = False
    st.rerun()


# ------------------------------------------------------------
# 4) Termo de uso (fica aqui, centralizado)
# ------------------------------------------------------------
def render_termo_de_uso():
    st.markdown(
        """
        <details class="terms">
          <summary>Termo de uso e privacidade (resumo)</summary>
          <div style="height:8px"></div>
          <p><b>Uso de teste/validação:</b> este ambiente é destinado a validação do PIN e acesso ao workspace.</p>
          <p><b>Dados sensíveis:</b> evite inserir informações sensíveis/identificáveis de estudantes em ambientes de teste.</p>
          <p><b>Responsabilidade:</b> o usuário responsável pelo workspace deve garantir consentimento e conformidade (LGPD/LBI).</p>
          <p><b>Segurança:</b> o menu nativo do Streamlit é ocultado em produção para reduzir risco de acesso indevido.</p>
          <p class="small">Você poderá ajustar o texto completo depois (este é um placeholder controlado).</p>
        </details>
        """,
        unsafe_allow_html=True,
    )


# ------------------------------------------------------------
# 5) UI — LOGIN (tela de início)
# ------------------------------------------------------------
def render_login_page():
    st.markdown("<div class='wrap'>", unsafe_allow_html=True)

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
          <h1 class="title">Omnisfera</h1>
          <div class="subtitle">Valide o PIN para vincular um workspace via Supabase RPC.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)

    # Chip fixo com NOME DA FUNÇÃO (para seu controle visual)
    st.markdown(
        f"""
        <div class="chip">
          <span>RPC:</span>
          <span class="mono">{RPC_NAME}(p_pin text)</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Card principal
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("<h3>Validar PIN</h3>", unsafe_allow_html=True)
    st.markdown(
        f"<div class='small'>Função (RPC) usada: <span class='mono'>{RPC_NAME}(p_pin text)</span></div>",
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

    # Termos + checkbox (obrigatório)
    render_termo_de_uso()
    st.session_state.aceitou_termos = st.checkbox(
        "Li e aceito os termos de uso",
        value=st.session_state.aceitou_termos,
    )

    # Ação
    if clicked:
        if not st.session_state.aceitou_termos:
            st.markdown("<div class='err'>Você precisa aceitar os termos para continuar.</div>", unsafe_allow_html=True)
            st.stop()

        pin_norm = normalize_pin(pin_in)
        st.session_state.pin = pin_norm

        if not pin_norm:
            st.markdown("<div class='err'>Informe um PIN válido.</div>", unsafe_allow_html=True)
            st.stop()

        with st.spinner("Validando PIN no Supabase..."):
            ws = rpc_workspace_from_pin(pin_norm)

        if not ws or not ws.get("id"):
            st.markdown("<div class='err'>PIN não encontrado ou inválido.</div>", unsafe_allow_html=True)
            st.stop()

        # ✅ sucesso
        st.session_state.autenticado = True
        st.session_state.workspace_id = ws["id"]
        st.session_state.workspace_name = ws.get("name") or "Workspace"
        st.session_state.pin_ok_at = time.strftime("%d/%m/%Y %H:%M")
        st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)


# ------------------------------------------------------------
# 6) UI — HOME mínima (só confirma estado)
# ------------------------------------------------------------
def render_home_page():
    st.markdown("<div class='wrap'>", unsafe_allow_html=True)

    st.markdown("<div class='badge'>Sessão ativa</div>", unsafe_allow_html=True)

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
          <h1 class="title">Omnisfera</h1>
          <div class="subtitle">PIN validado e vinculado a um workspace via Supabase RPC.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("<div class='ok'>Conectado ✅</div>", unsafe_allow_html=True)
    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

    a, b = st.columns(2)
    with a:
        st.caption("Workspace")
        st.write(st.session_state.workspace_name or "—")
    with b:
        st.caption("Workspace ID")
        st.code(str(st.session_state.workspace_id), language=None)

    st.caption("PIN usado (somente para depuração)")
    st.code(st.session_state.pin or "—", language=None)

    st.markdown("</div>", unsafe_allow_html=True)

    if st.button("Sair / Trocar PIN"):
        logout()

    st.markdown("</div>", unsafe_allow_html=True)


# ------------------------------------------------------------
# 7) Router local (sem pages)
# ------------------------------------------------------------
if st.session_state.autenticado and st.session_state.workspace_id:
    render_home_page()
else:
    render_login_page()
