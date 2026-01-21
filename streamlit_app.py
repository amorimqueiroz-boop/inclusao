# streamlit_app.py
# Omnisfera — Tela de Início (PIN) + Supabase RPC + Logo girando
# - Sem sidebar
# - Evita loops de navegação
# - Esconde “menu de baixo” (chrome do Streamlit) por padrão
#   (Só NÃO esconde quando ENV="TESTE" no secrets)

import os
import time
import base64
from datetime import datetime

import streamlit as st
from supabase import create_client


# =============================================================================
# 0) CONFIG
# =============================================================================
st.set_page_config(
    page_title="Omnisfera",
    page_icon="🍃",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# =============================================================================
# 1) ENV + HIDE STREAMLIT CHROME (menu/toolbar/footer)
# =============================================================================
def _get_env_flag() -> str:
    # prioridade: secrets > env var
    try:
        v = st.secrets.get("ENV", None)
        if v:
            return str(v).strip().upper()
    except Exception:
        pass
    return str(os.getenv("ENV", "")).strip().upper()


def maybe_hide_streamlit_chrome():
    env_flag = _get_env_flag()

    # Em TESTE, não esconde (pra depurar)
    if env_flag == "TESTE":
        return

    # Em PROD (ou sem ENV), esconde o chrome
    st.markdown(
        """
        <style>
          #MainMenu {visibility: hidden;}
          header {visibility: hidden;}
          footer {visibility: hidden;}

          /* remove espaço do header */
          .block-container { padding-top: 1.2rem; }

          /* tenta esconder toolbar (varia por versão) */
          [data-testid="stToolbar"] {visibility: hidden;}
          [data-testid="stDecoration"] {visibility: hidden;}
          [data-testid="stStatusWidget"] {visibility: hidden;}

          /* também oculta possíveis botões do canto superior */
          [data-testid="stAppDeployButton"] {display:none;}
        </style>
        """,
        unsafe_allow_html=True,
    )


maybe_hide_streamlit_chrome()


# =============================================================================
# 2) CSS + LOGO GIRANDO
# =============================================================================
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
            --bg:#ffffff;
            --muted:#6b7280;
            --text:#111827;
            --card:#ffffff;
            --border:rgba(17,24,39,.08);
            --shadow: 0 10px 30px rgba(17,24,39,.06);
            --green:#16a34a;
            --red:#ef4444;
          }

          .omni-wrap{
            max-width: 980px;
            margin: 0 auto;
            padding: 24px 18px 64px;
          }

          .top-chip{
            display:inline-flex;
            align-items:center;
            gap:8px;
            border:1px solid var(--border);
            padding: 6px 10px;
            border-radius: 999px;
            font-size: 13px;
            color: var(--muted);
            background: rgba(17,24,39,.02);
          }

          .hero{
            margin-top: 18px;
            display:flex;
            align-items:flex-start;
            justify-content: space-between;
            gap: 28px;
          }

          .brand{
            display:flex;
            align-items:center;
            gap:14px;
          }

          .logoSpin{
            width:56px;height:56px;
            border-radius:16px;
            display:inline-flex;
            align-items:center;
            justify-content:center;
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

          @keyframes spin{
            0%{transform: rotate(0deg);}
            100%{transform: rotate(360deg);}
          }

          .title{
            font-size: 58px;
            line-height: 1.02;
            letter-spacing: -0.04em;
            margin: 0;
            color: var(--text);
          }

          .subtitle{
            margin-top: 10px;
            color: var(--muted);
            font-size: 16px;
          }

          .card{
            margin-top: 18px;
            background: var(--card);
            border:1px solid var(--border);
            box-shadow: var(--shadow);
            border-radius: 18px;
            padding: 18px;
          }

          .grid2{
            display:grid;
            grid-template-columns: 1.2fr 1fr;
            gap: 18px;
          }

          .fieldlabel{
            font-size: 13px;
            color: var(--muted);
            margin-bottom: 6px;
          }

          .pill-ok{
            display:flex;
            align-items:center;
            gap:10px;
            padding: 12px 14px;
            border-radius: 12px;
            border: 1px solid rgba(22,163,74,.18);
            background: rgba(22,163,74,.08);
            color: #166534;
            font-weight: 600;
          }

          .pill-bad{
            display:flex;
            align-items:center;
            gap:10px;
            padding: 12px 14px;
            border-radius: 12px;
            border: 1px solid rgba(239,68,68,.22);
            background: rgba(239,68,68,.08);
            color: #991b1b;
            font-weight: 600;
          }

          .mono{
            font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
          }

          .thinhr{
            margin: 16px 0;
            height:1px;
            background: rgba(17,24,39,.08);
            border:0;
          }
        </style>
        """,
        unsafe_allow_html=True,
    )


inject_css()


# =============================================================================
# 3) SUPABASE CLIENT + RPC
# =============================================================================
@st.cache_resource(show_spinner=False)
def get_supabase():
    # prefer secrets, fallback env
    url = None
    key = None
    try:
        url = st.secrets.get("SUPABASE_URL", None)
        key = st.secrets.get("SUPABASE_ANON_KEY", None)
    except Exception:
        pass
    url = url or os.getenv("SUPABASE_URL")
    key = key or os.getenv("SUPABASE_ANON_KEY")

    if not url or not key:
        raise RuntimeError(
            "SUPABASE_URL / SUPABASE_ANON_KEY não encontrados. "
            "Configure no Secrets (Streamlit Cloud) ou como variáveis de ambiente."
        )
    return create_client(url, key)


def workspace_from_pin(pin: str) -> dict | None:
    """
    Espera um RPC public.workspace_from_pin(p_pin text)
    que retorna (id uuid, name text)
    """
    sb = get_supabase()
    res = sb.rpc("workspace_from_pin", {"p_pin": pin}).execute()
    data = res.data
    if not data:
        return None
    # Pode vir como lista (padrão do PostgREST)
    if isinstance(data, list):
        return data[0] if len(data) else None
    if isinstance(data, dict):
        return data
    return None


# =============================================================================
# 4) STATE (sem loops)
# =============================================================================
def ensure_state():
    if "session_ok" not in st.session_state:
        st.session_state.session_ok = False

    if "workspace_id" not in st.session_state:
        st.session_state.workspace_id = None
    if "workspace_name" not in st.session_state:
        st.session_state.workspace_name = None

    if "pin_debug" not in st.session_state:
        st.session_state.pin_debug = None

    if "connected" not in st.session_state:
        st.session_state.connected = False

    if "last_auth_ts" not in st.session_state:
        st.session_state.last_auth_ts = None


def clear_session():
    st.session_state.session_ok = False
    st.session_state.workspace_id = None
    st.session_state.workspace_name = None
    st.session_state.pin_debug = None
    st.session_state.connected = False
    st.session_state.last_auth_ts = None


ensure_state()


# =============================================================================
# 5) UI HELPERS
# =============================================================================
def render_header():
    logo_b64 = _b64_logo_from_file()

    if logo_b64:
        logo_html = f"<img src='data:image/png;base64,{logo_b64}'/>"
    else:
        # fallback: ícone simples (sem arquivo)
        logo_html = "<div style='width:34px;height:34px;border-radius:10px;background:rgba(22,163,74,.25);'></div>"

    st.markdown(
        f"""
        <div class="omni-wrap">
          <div class="top-chip">Sessão ativa</div>

          <div class="hero">
            <div>
              <div class="brand">
                <div class="logoSpin">{logo_html}</div>
                <div>
                  <h1 class="title">Omnisfera</h1>
                  <div class="subtitle">Ambiente por PIN (workspace). Conexão Supabase via RPC.</div>
                </div>
              </div>
            </div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_login():
    st.markdown('<div class="omni-wrap">', unsafe_allow_html=True)

    st.markdown(
        """
        <div class="card">
          <div style="font-weight:700; font-size:16px; margin-bottom:6px;">Validar PIN</div>
          <div style="color:var(--muted); font-size:14px;">
            Digite o PIN do workspace (ex.: <span class="mono">ABCD-1234</span>).
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    c1, c2 = st.columns([2, 1], gap="large")
    with c1:
        pin = st.text_input(
            "PIN do Workspace",
            value="",
            placeholder="Ex.: 3D6C-9718",
            label_visibility="collapsed",
        )
        st.caption("Dica: você pode colar o PIN com ou sem hífen; nós normalizamos.")

    with c2:
        do = st.button("Validar e entrar", use_container_width=True)

    # Normaliza: remove espaços e força maiúsculo; mantém hífen se existir
    pin_norm = (pin or "").strip().upper().replace(" ", "")
    if len(pin_norm) == 8 and "-" not in pin_norm:
        pin_norm = pin_norm[:4] + "-" + pin_norm[4:]

    if do:
        if not pin_norm or len(pin_norm) < 6:
            st.error("Digite um PIN válido.")
        else:
            with st.spinner("Validando PIN..."):
                try:
                    ws = workspace_from_pin(pin_norm)
                except Exception as e:
                    st.error("Falha ao consultar o Supabase. Verifique URL/KEY e o RPC.")
                    st.caption(str(e))
                    ws = None

            if not ws:
                st.error("PIN não encontrado ou inválido.")
            else:
                st.session_state.session_ok = True
                st.session_state.workspace_id = ws.get("id")
                st.session_state.workspace_name = ws.get("name")
                st.session_state.pin_debug = pin_norm
                st.session_state.connected = True
                st.session_state.last_auth_ts = datetime.now().strftime("%d/%m/%Y %H:%M")
                st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)


def render_status_card():
    st.markdown('<div class="omni-wrap">', unsafe_allow_html=True)

    ok = st.session_state.connected and st.session_state.workspace_id

    # linha “Conectado”
    if ok:
        st.markdown('<div class="pill-ok">Conectado ✅</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="pill-bad">Desconectado ❌</div>', unsafe_allow_html=True)

    st.markdown("<hr class='thinhr'/>", unsafe_allow_html=True)

    # infos
    ws_name = st.session_state.workspace_name or "—"
    ws_id = st.session_state.workspace_id or "—"
    pin = st.session_state.pin_debug or "—"
    ts = st.session_state.last_auth_ts or "—"

    st.markdown(
        f"""
        <div class="card">
          <div class="grid2">
            <div>
              <div class="fieldlabel">Workspace</div>
              <div style="font-size:18px; font-weight:700;">{ws_name}</div>
              <div style="margin-top:6px; color:var(--muted); font-size:13px;">Ambiente liberado via PIN · {ts}</div>
            </div>
            <div>
              <div class="fieldlabel">Workspace ID</div>
              <div class="mono" style="font-size:14px; padding:12px 14px; border:1px solid var(--border); border-radius:14px; background:rgba(17,24,39,.02);">
                {ws_id}
              </div>
              <div class="fieldlabel" style="margin-top:12px;">PIN usado (somente para depuração)</div>
              <div class="mono" style="font-size:14px; padding:12px 14px; border:1px solid var(--border); border-radius:14px; background:rgba(17,24,39,.02); display:inline-block;">
                {pin}
              </div>
            </div>
          </div>

          <div style="margin-top:14px; display:flex; justify-content:flex-end; gap:10px;">
        </div>
        """,
        unsafe_allow_html=True,
    )

    colA, colB = st.columns([1, 1], gap="large")
    with colA:
        if st.button("Atualizar estado", use_container_width=True):
            # só revalida se tiver pin
            if st.session_state.pin_debug:
                with st.spinner("Revalidando..."):
                    ws = workspace_from_pin(st.session_state.pin_debug)
                if ws:
                    st.session_state.workspace_id = ws.get("id")
                    st.session_state.workspace_name = ws.get("name")
                    st.session_state.connected = True
                    st.session_state.last_auth_ts = datetime.now().strftime("%d/%m/%Y %H:%M")
                    st.toast("Estado atualizado.")
                    st.rerun()
                else:
                    st.session_state.connected = False
                    st.warning("Não foi possível revalidar o PIN. Volte e valide novamente.")
            else:
                st.warning("Sem PIN na sessão.")
    with colB:
        if st.button("Sair / Trocar PIN", use_container_width=True):
            clear_session()
            st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)


# =============================================================================
# 6) MAIN
# =============================================================================
def main():
    render_header()

    # Se não tem sessão, fica só na tela de início/login.
    if not st.session_state.session_ok or not st.session_state.workspace_id:
        # Se estava “meio logado” mas perdeu o workspace_id, limpa sem loop
        if st.session_state.session_ok and not st.session_state.workspace_id:
            clear_session()
        render_login()
        return

    # Sessão ok (PIN validado)
    render_status_card()


if __name__ == "__main__":
    main()
