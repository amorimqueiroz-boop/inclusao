# streamlit_app.py
import os
import base64
import streamlit as st
from datetime import datetime
from supabase import create_client

APP_TITLE = "Omnisfera"

# =============================================================================
# Supabase
# =============================================================================
@st.cache_resource(show_spinner=False)
def get_supabase():
    url = st.secrets.get("SUPABASE_URL", None) if hasattr(st, "secrets") else None
    key = st.secrets.get("SUPABASE_ANON_KEY", None) if hasattr(st, "secrets") else None
    url = url or os.getenv("SUPABASE_URL")
    key = key or os.getenv("SUPABASE_ANON_KEY")
    if not url or not key:
        raise RuntimeError("SUPABASE_URL / SUPABASE_ANON_KEY não configurados.")
    return create_client(url, key)

def workspace_from_pin(pin: str):
    sb = get_supabase()
    res = sb.rpc("workspace_from_pin", {"p_pin": pin}).execute()
    data = getattr(res, "data", None)
    error = getattr(res, "error", None)
    if error:
        raise RuntimeError(str(error))
    if not data:
        return None
    if isinstance(data, list):
        return data[0] if data else None
    if isinstance(data, dict):
        return data
    return None

# =============================================================================
# Estado
# =============================================================================
def ensure_state():
    st.session_state.setdefault("pin_validado", False)
    st.session_state.setdefault("workspace_id", None)
    st.session_state.setdefault("workspace_name", None)
    st.session_state.setdefault("workspace_pin", "")
    st.session_state.setdefault("workspace_validado_em", None)

def reset_session():
    for k in ["pin_validado", "workspace_id", "workspace_name", "workspace_pin", "workspace_validado_em"]:
        if k in st.session_state:
            del st.session_state[k]

# =============================================================================
# Logo (base64)
# =============================================================================
def logo_src():
    # procura arquivos típicos do seu projeto
    candidates = [
        "omni_icone.png",
        "logo.png",
        "iconeaba.png",
        "omni.png",
        "ominisfera.png",
        "assets/omni_icone.png",
        "assets/logo.png",
        "assets/iconeaba.png",
        "assets/omni.png",
        "assets/ominisfera.png",
    ]
    for f in candidates:
        if os.path.exists(f):
            with open(f, "rb") as img:
                b64 = base64.b64encode(img.read()).decode()
            return f"data:image/png;base64,{b64}"
    return None

# =============================================================================
# CSS
# =============================================================================
def inject_css():
    st.markdown(
        """
        <style>
          :root{
            --bg: #fbfbfc;
            --card: rgba(255,255,255,.9);
            --border: rgba(10,10,10,.08);
            --muted: rgba(10,10,10,.55);
            --shadow: 0 12px 30px rgba(20,20,20,.06);
            --radius: 18px;
          }
          .block-container{max-width: 1180px; padding-top: 22px;}
          body{background: var(--bg);}

          /* Header hero */
          .hero{
            border: 1px solid var(--border);
            border-radius: 26px;
            background: linear-gradient(180deg, rgba(255,255,255,.92), rgba(255,255,255,.78));
            box-shadow: var(--shadow);
            padding: 18px 18px 18px 18px;
            margin-bottom: 18px;
          }
          .hero-top{
            display:flex; align-items:center; justify-content:space-between; gap:18px;
          }
          .hero-left{display:flex; align-items:center; gap:14px;}
          .badge{
            display:inline-flex; align-items:center; gap:8px;
            padding: 6px 10px;
            border-radius: 999px;
            border: 1px solid var(--border);
            background: rgba(255,255,255,.75);
            font-size: 13px;
            color: var(--muted);
            width: fit-content;
          }
          .title{
            font-size: 52px;
            font-weight: 850;
            letter-spacing: -1.4px;
            margin: 0;
            line-height: 1.03;
          }
          .subtitle{
            margin-top: 8px;
            font-size: 16px;
            color: var(--muted);
          }
          .meta{
            display:flex; align-items:flex-start; gap:24px; flex-wrap:wrap;
          }
          .meta .k{font-size:12px; color: var(--muted); margin-bottom:6px;}
          .meta .v{
            font-size: 16px;
            font-weight: 650;
            background: rgba(10,10,10,.03);
            border: 1px solid var(--border);
            border-radius: 14px;
            padding: 10px 12px;
          }

          /* Spinning logo */
          .omni-spin{
            width: 46px; height: 46px;
            border-radius: 14px;
            border: 1px solid var(--border);
            background: rgba(255,255,255,.9);
            display:flex; align-items:center; justify-content:center;
            box-shadow: 0 10px 22px rgba(20,20,20,.06);
            overflow:hidden;
          }
          .omni-spin img{
            width: 30px; height: 30px;
            animation: spin 6s linear infinite;
            transform-origin: 50% 50%;
          }
          @keyframes spin{
            from{transform: rotate(0deg);}
            to{transform: rotate(360deg);}
          }

          /* Cards */
          .grid{
            display:grid;
            grid-template-columns: 1.1fr 1.1fr .9fr;
            gap: 14px;
            margin-top: 14px;
          }
          .card{
            border: 1px solid var(--border);
            border-radius: var(--radius);
            background: var(--card);
            box-shadow: 0 10px 26px rgba(20,20,20,.05);
            padding: 16px 16px 14px 16px;
            min-height: 120px;
          }
          .card .t{font-size: 13px; color: var(--muted); margin-bottom: 6px;}
          .card .h{font-size: 18px; font-weight: 780; margin: 0 0 8px 0;}
          .card .p{font-size: 14px; color: var(--muted); margin: 0;}
          .ok-pill{
            display:inline-flex;
            padding: 8px 10px;
            border-radius: 14px;
            border: 1px solid rgba(0,128,0,.18);
            background: rgba(0,255,0,.08);
            font-weight: 700;
            margin-top: 6px;
          }

          /* section title */
          .section-title{
            margin-top: 22px;
            font-size: 26px;
            font-weight: 820;
            letter-spacing: -.6px;
          }
          .bullets{
            margin-top: 8px;
            color: var(--muted);
            font-size: 15px;
            line-height: 1.5;
          }

          /* Mobile */
          @media (max-width: 980px){
            .grid{grid-template-columns: 1fr; }
            .title{font-size: 42px;}
          }
        </style>
        """,
        unsafe_allow_html=True,
    )

# =============================================================================
# UI blocks
# =============================================================================
def render_login():
    st.markdown("<div class='hero'>", unsafe_allow_html=True)
    st.markdown("<div class='badge'>Ambiente por PIN</div>", unsafe_allow_html=True)

    # header with spinning logo
    logo = logo_src()
    if logo:
        logo_html = f"<div class='omni-spin'><img src='{logo}'/></div>"
    else:
        # fallback simples se não achar imagem
        logo_html = "<div class='omni-spin'><div style='font-weight:900;'>🌿</div></div>"

    st.markdown(
        f"""
        <div class='hero-top'>
          <div class='hero-left'>
            {logo_html}
            <div>
              <h1 class='title'>{APP_TITLE}</h1>
              <div class='subtitle'>Digite o PIN da escola para acessar o ambiente.</div>
            </div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)

    with st.container():
        pin = st.text_input(
            "PIN da escola",
            value=st.session_state.workspace_pin or "",
            placeholder="Ex.: 3D6C-9718",
        ).strip()

        c1, c2 = st.columns([1, 1])
        validar = c1.button("Validar e entrar", use_container_width=True)
        limpar = c2.button("Limpar", use_container_width=True)

        if limpar:
            st.session_state.workspace_pin = ""
            st.rerun()

        if validar:
            st.session_state.workspace_pin = pin
            if not pin:
                st.error("Digite um PIN.")
                st.stop()

            with st.spinner("Validando PIN..."):
                try:
                    ws = workspace_from_pin(pin)
                except Exception as e:
                    st.error(f"Erro ao validar PIN: {e}")
                    st.stop()

            if not ws:
                st.error("PIN inválido ou não encontrado.")
                st.stop()

            st.session_state.pin_validado = True
            st.session_state.workspace_id = ws.get("id")
            st.session_state.workspace_name = ws.get("name") or "Workspace"
            st.session_state.workspace_validado_em = datetime.now().strftime("%d/%m/%Y %H:%M")

            st.rerun()

def render_home():
    # HERO
    ws_name = st.session_state.workspace_name or "Workspace"
    ws_id = st.session_state.workspace_id or "-"
    validado_em = st.session_state.workspace_validado_em or "-"

    st.markdown("<div class='hero'>", unsafe_allow_html=True)
    st.markdown("<div class='badge'>Ambiente liberado via PIN</div>", unsafe_allow_html=True)

    logo = logo_src()
    if logo:
        logo_html = f"<div class='omni-spin'><img src='{logo}'/></div>"
    else:
        logo_html = "<div class='omni-spin'><div style='font-weight:900;'>🌿</div></div>"

    st.markdown(
        f"""
        <div class='hero-top'>
          <div class='hero-left'>
            {logo_html}
            <div>
              <h1 class='title'>{ws_name}</h1>
              <div class='subtitle'>Ambiente liberado via PIN • {validado_em}</div>
            </div>
          </div>
          <div class='meta'>
            <div>
              <div class='k'>Workspace ID</div>
              <div class='v'>{ws_id}</div>
            </div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # CARDS
    st.markdown(
        """
        <div class="grid">
          <div class="card">
            <div class="t">Atalho</div>
            <div class="h">Cadastrar aluno</div>
            <div class="p">Abra a aba Alunos para criar e gerenciar estudantes.</div>
          </div>
          <div class="card">
            <div class="t">Atalho</div>
            <div class="h">Abrir PEI</div>
            <div class="p">Monte o plano individual e vincule ao aluno.</div>
          </div>
          <div class="card">
            <div class="t">Status</div>
            <div class="h">Supabase</div>
            <div class="p">Conectividade do backend e RPC por PIN.</div>
            <div class="ok-pill">Conectado ✅</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)

    # Buttons (por enquanto sem navegação)
    b1, b2, b3 = st.columns([1, 1, 1])
    b1.button("Ir para Alunos", use_container_width=True, disabled=True)
    b2.button("Ir para PEI", use_container_width=True, disabled=True)
    if b3.button("Sair / Trocar PIN", use_container_width=True):
        reset_session()
        st.rerun()

    # Próximos passos (igual à ideia antiga)
    st.markdown("<div class='section-title'>Próximos passos</div>", unsafe_allow_html=True)
    st.markdown(
        """
        <div class="bullets">
          <ul>
            <li>Confirmar que todas as páginas usam <code>st.session_state.workspace_id</code> para filtrar dados.</li>
            <li>Garantir tabelas (students, peis, pae etc.) com coluna <code>workspace_id</code>.</li>
            <li>Configurar políticas/RLS e permissões para leitura/escrita por workspace.</li>
          </ul>
        </div>
        """,
        unsafe_allow_html=True,
    )

# =============================================================================
# Main
# =============================================================================
def main():
    st.set_page_config(
        page_title="Omnisfera • Início",
        page_icon="🌿",
        layout="wide",
        initial_sidebar_state="collapsed",
    )

    ensure_state()
    inject_css()

    # Sem redirects, sem switch_page: apenas decide o que renderiza.
    if not st.session_state.pin_validado or not st.session_state.workspace_id:
        render_login()
    else:
        render_home()

if __name__ == "__main__":
    main()
