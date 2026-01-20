# ui_nav.py
from __future__ import annotations

import base64
from pathlib import Path
import streamlit as st

TOPBAR_HEIGHT = 56
TOPBAR_PADDING = 14


def ensure_auth_state():
    if "autenticado" not in st.session_state:
        st.session_state.autenticado = False
    if "user" not in st.session_state:
        st.session_state.user = None
    if "go" not in st.session_state:
        st.session_state.go = "home"


def _root() -> Path:
    return Path(__file__).resolve().parent


def _img_data_uri(filename: str) -> str | None:
    p = _root() / filename
    if not p.exists():
        return None
    try:
        b64 = base64.b64encode(p.read_bytes()).decode("utf-8")
        return f"data:image/png;base64,{b64}"
    except Exception:
        return None


def inject_icons_cdn():
    st.markdown(
        """
<link rel="stylesheet" href="https://cdn-uicons.flaticon.com/3.0.0/uicons-solid-rounded/css/uicons-solid-rounded.css">
<link rel="stylesheet" href="https://cdn-uicons.flaticon.com/3.0.0/uicons-bold-rounded/css/uicons-bold-rounded.css">
<link rel="stylesheet" href="https://cdn-uicons.flaticon.com/3.0.0/uicons-solid-straight/css/uicons-solid-straight.css">
        """,
        unsafe_allow_html=True,
    )


def inject_shell_css():
    st.markdown(
        f"""
<style>
/* remove UI nativa */
[data-testid="stHeader"], header,
footer, #MainMenu,
[data-testid="stToolbar"],
[data-testid="stDecoration"] {{
  display: none !important;
}}

/* empurra conteúdo */
.main .block-container {{
  padding-top: {TOPBAR_HEIGHT + TOPBAR_PADDING}px !important;
}}

/* topbar light glass */
.omni-topbar {{
  position: fixed;
  top: 0; left: 0; right: 0;
  height: {TOPBAR_HEIGHT}px;
  z-index: 999999;

  display:flex;
  align-items:center;
  justify-content:space-between;

  padding: 0 14px;
  background: rgba(255,255,255,0.82);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border-bottom: 1px solid rgba(0,0,0,0.08);
  box-shadow: 0 10px 30px rgba(0,0,0,0.06);
}}

/* brand */
.omni-brand {{
  display:flex;
  align-items:center;
  gap:10px;
  user-select:none;
}}
.omni-logo-wrap {{
  width: 36px; height: 36px; border-radius: 14px;
  display:flex; align-items:center; justify-content:center;
  background: rgba(0,0,0,0.03);
  border: 1px solid rgba(0,0,0,0.08);
}}
.omni-logo {{ width: 22px; height: 22px; object-fit: contain; }}
.omni-wordmark-img {{ height: 16px; width: auto; object-fit: contain; opacity: 0.92; }}
.omni-wordmark-fallback {{ font-weight: 900; letter-spacing: .2px; color: rgba(0,0,0,0.82); font-size: 14px; }}

/* nav buttons (vamos estilizar st.button via CSS) */
.omni-nav {{
  display:flex;
  align-items:center;
  gap:10px;
}}

/* container onde ficam os botões do streamlit */
.omni-btn-row [data-testid="stHorizontalBlock"] {{
  gap: 10px !important;
}}
/* estiliza todos botões dentro do nav */
.omni-btn-row button {{
  width: 36px !important;
  height: 36px !important;
  padding: 0 !important;
  border-radius: 12px !important;

  background: rgba(0,0,0,0.03) !important;
  border: 1px solid rgba(0,0,0,0.08) !important;

  transition: transform .12s ease, background .12s ease, border-color .12s ease !important;
}}
.omni-btn-row button:hover {{
  transform: translateY(-1px) !important;
  background: rgba(0,0,0,0.05) !important;
  border-color: rgba(0,0,0,0.12) !important;
}}
/* estado ativo (vamos aplicar com uma classe no wrapper via markdown) */
.omni-btn-row .is-active button {{
  background: rgba(0,0,0,0.06) !important;
  border-color: rgba(0,0,0,0.16) !important;
}}
/* ícone dentro do botão */
.omni-btn-row button p {{
  margin: 0 !important;
  font-size: 18px !important;
  line-height: 1 !important;
  color: rgba(0,0,0,0.70) !important;
}}
</style>
        """,
        unsafe_allow_html=True,
    )


def ROUTES():
    return [
        ("home", "Home", "fi fi-br-home"),
        ("alunos", "Alunos", "fi fi-sr-users"),
        ("pei", "PEI 360°", "fi fi-sr-document-signed"),
        ("pae", "PAE", "fi fi-ss-bullseye-arrow"),
        ("hub", "Hub", "fi fi-sr-book-open-cover"),
        ("diario", "Diário", "fi fi-br-notebook"),
        ("dados", "Dados", "fi fi-br-chart-histogram"),
    ]


def set_go(go: str):
    st.session_state.go = go


def boot_ui():
    ensure_auth_state()
    inject_icons_cdn()
    inject_shell_css()

    # só desenha topbar quando autenticado
    if not st.session_state.autenticado:
        return

    logo_uri = _img_data_uri("omni_icone.png")
    text_uri = _img_data_uri("omni_texto.png")

    logo_html = f"<img class='omni-logo' src='{logo_uri}'/>" if logo_uri else "🌿"
    wordmark_html = f"<img class='omni-wordmark-img' src='{text_uri}'/>" if text_uri else "<span class='omni-wordmark-fallback'>Omnisfera</span>"

    # Topbar (HTML) + Row de botões (Streamlit) abaixo, mas visualmente “dentro” pela fixed bar
    st.markdown(
        f"""
<div class="omni-topbar">
  <div class="omni-brand">
    <div class="omni-logo-wrap">{logo_html}</div>
    <div>{wordmark_html}</div>
  </div>
  <div class="omni-nav"></div>
</div>
        """,
        unsafe_allow_html=True,
    )

    # Botões do nav: ficam no topo, mas a topbar já está fixed; isso só “alinha” as ações.
    # Truque: usamos um container no topo da página, mas a topbar é fixed, então o usuário só vê ela.
    with st.container():
        st.markdown('<div class="omni-btn-row">', unsafe_allow_html=True)

        cols = st.columns(len(ROUTES()), gap="small")
        for i, (go, label, icon_class) in enumerate(ROUTES()):
            is_active = (st.session_state.go == go)
            # wrapper para CSS do ativo
            if is_active:
                st.markdown('<div class="is-active">', unsafe_allow_html=True)

            with cols[i]:
                # botão com ícone (texto)
                if st.button(" ", key=f"nav_{go}", help=label):
                    set_go(go)
                    st.rerun()

                # injeta o ícone dentro do botão via markdown overlay (simples e estável)
                st.markdown(
                    f"""
<script>
const btn = window.parent.document.querySelector('button[kind="secondary"][data-testid="baseButton-secondary"][aria-describedby="nav_{go}-tooltip"]') 
</script>
                    """,
                    unsafe_allow_html=True,
                )

                # fallback: ícone “visível” como label (sem depender de script)
                st.markdown(
                    f"<div style='margin-top:-40px; text-align:center; pointer-events:none;'><i class='{icon_class}' style='font-size:18px;color:rgba(0,0,0,0.70)'></i></div>",
                    unsafe_allow_html=True,
                )

            if is_active:
                st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)
