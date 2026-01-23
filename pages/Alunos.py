# pages/Alunos.py
import streamlit as st
import requests
import base64
import os
from datetime import datetime

# ==============================================================================
# CONFIG
# ==============================================================================
st.set_page_config(page_title="Omnisfera • Estudantes", page_icon="👥", layout="wide")

# ==============================================================================
# VISUAL (mesmo padrão da Home v2.0)
# ==============================================================================
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
@import url("https://cdn.jsdelivr.net/npm/remixicon@3.5.0/fonts/remixicon.css");

html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    color: #1E293B !important;
    background-color: #F8FAFC !important;
}

/* --- OCULTAR CHROME NATIVO DO STREAMLIT --- */
[data-testid="stSidebarNav"],
[data-testid="stHeader"],
[data-testid="stToolbar"],
[data-testid="collapsedControl"],
footer {
    display: none !important;
}

/* Ajustar padding para compensar a topbar fixa */
.block-container {
    padding-top: 100px !important;
    padding-bottom: 4rem !important;
    max-width: 95% !important;
    padding-left: 1rem !important;
    padding-right: 1rem !important;
}

/* --- TOPBAR (HOME v2.0) --- */
.topbar {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    height: 80px;
    background: rgba(255, 255, 255, 0.95) !important;
    backdrop-filter: blur(12px) !important;
    -webkit-backdrop-filter: blur(12px) !important;
    border-bottom: 1px solid #E2E8F0;
    z-index: 9999;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 2.5rem;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.brand-box {
    display: flex;
    align-items: center;
    gap: 12px;
}

.brand-logo {
    height: 55px !important;
    width: auto !important;
    animation: spin 45s linear infinite;
    filter: brightness(1.1);
}

.brand-img-text {
    height: 35px !important;
    width: auto;
    margin-left: 10px;
}

.user-badge {
    background: #F1F5F9;
    border: 1px solid #E2E8F0;
    padding: 6px 14px;
    border-radius: 99px;
    font-size: 0.8rem;
    font-weight: 700;
    color: #64748B;
    letter-spacing: 0.5px;
}

/* --- PADRÃO "RECURSOS EXTERNOS" (para cabeçalho) --- */
.res-card {
    background: white;
    border-radius: 14px;
    padding: 20px;
    border: 1px solid #E2E8F0;
    display: flex;
    align-items: center;
    gap: 16px;
    transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
    height: 100%;
    min-height: 96px;
}

.res-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 12px 24px rgba(0, 0, 0, 0.08);
    border-color: transparent;
}

.res-icon {
    width: 48px;
    height: 48px;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.4rem;
    flex-shrink: 0;
    transition: all 0.3s ease;
}

.res-card:hover .res-icon {
    transform: scale(1.06) rotate(3deg);
}

.res-info {
    display: flex;
    flex-direction: column;
    flex-grow: 1;
}

.res-name {
    font-weight: 800;
    color: #1E293B;
    font-size: 1.05rem;
    margin-bottom: 2px;
    transition: color 0.2s;
}

.res-card:hover .res-name {
    color: #4F46E5;
}

.res-meta {
    font-size: 0.85rem;
    font-weight: 600;
    color: #64748B;
    opacity: 0.9;
}

/* Temas (rc-*) */
.rc-sky {
    background: #F0F9FF !important;
    color: #0284C7 !important;
    border-color: #BAE6FD !important;
}
.rc-sky .res-icon { background: #F0F9FF !important; border: 1px solid #BAE6FD !important; }

.rc-green {
    background: #F0FDF4 !important;
    color: #16A34A !important;
    border-color: #BBF7D0 !important;
}
.rc-green .res-icon { background: #F0FDF4 !important; border: 1px solid #BBF7D0 !important; }

.rc-rose {
    background: #FFF1F2 !important;
    color: #E11D48 !important;
    border-color: #FECDD3 !important;
}
.rc-rose .res-icon { background: #FFF1F2 !important; border: 1px solid #FECDD3 !important; }

.rc-orange {
    background: #FFF7ED !important;
    color: #EA580C !important;
    border-color: #FDBA74 !important;
}
.rc-orange .res-icon { background: #FFF7ED !important; border: 1px solid #FDBA74 !important; }

/* botão */
.stButton > button {
    border-radius: 14px !important;
    border: 1px solid #E2E8F0 !important;
    background: white !important;
    color: #334155 !important;
    font-weight: 800 !important;
    letter-spacing: 0.3px !important;
    transition: all 0.2s ease !important;
}
.stButton > button:hover {
    background: #F8FAFC !important;
    color: #4F46E5 !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 10px 18px rgba(0,0,0,0.08) !important;
}

/* animação logo */
@keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}

/* responsividade */
@media (max-width: 640px) {
    .brand-img-text { display: none; }
    .user-badge { display: none; }
    .topbar { padding: 0 1rem; }
}
</style>
""",
    unsafe_allow_html=True,
)

# ==============================================================================
# FUNÇÕES VISUAIS (reaproveitadas da Home)
# ==============================================================================
def _get_base64_image(image_path: str) -> str:
    if not os.path.exists(image_path):
        return ""
    try:
        with open(image_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except Exception:
        return ""


def _escola_vinculada() -> str:
    workspace_name = st.session_state.get("workspace_name", "")
    workspace_id = st.session_state.get("workspace_id", "")
    if workspace_name:
        return workspace_name[:20] + "..." if len(workspace_name) > 20 else workspace_name
    if workspace_id:
        return f"ID: {str(workspace_id)[:8]}..."
    return "Sem Escola"


def _get_user_initials(nome: str) -> str:
    if not nome:
        return "U"
    parts = nome.split()
    if len(parts) >= 2:
        return f"{parts[0][0]}{parts[-1][0]}".upper()
    return nome[:2].upper() if len(nome) >= 2 else nome[0].upper()


def render_topbar():
    icone_b64 = _get_base64_image("omni_icone.png")
    texto_b64 = _get_base64_image("omni_texto.png")
    workspace = _escola_vinculada()
    nome_user_full = st.session_state.get("usuario_nome", "Visitante")
    nome_user = (nome_user_full.split()[0] if nome_user_full else "Visitante")
    initials = _get_user_initials(nome_user_full)

    img_logo = (
        f'<img src="data:image/png;base64,{icone_b64}" class="brand-logo" alt="Omnisfera Logo">'
        if icone_b64 else "🌐"
    )
    img_text = (
        f'<img src="data:image/png;base64,{texto_b64}" class="brand-img-text" alt="Omnisfera">'
        if texto_b64 else "<span style='font-weight:900; font-size:1.1rem; color:#2B3674;'>OMNISFERA</span>"
    )

    st.markdown(
        f"""
        <div class="topbar">
            <div class="brand-box">
                {img_logo}
                {img_text}
            </div>
            <div class="brand-box" style="gap: 16px;">
                <div class="user-badge">{workspace}</div>
                <div style="
                    display: flex;
                    align-items: center;
                    gap: 12px;
                    font-weight: 800;
                    color: #334155;
                ">
                    <div style="
                        width: 40px;
                        height: 40px;
                        border-radius: 50%;
                        background: linear-gradient(135deg, #4F46E5, #7C3AED);
                        color: white;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        font-weight: 900;
                        font-size: 0.9rem;
                    ">{initials}</div>
                    <div>{nome_user}</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_page_header_estudantes(workspace_name: str):
    # Cabeçalho no padrão dos “Recursos Externos” (card grande)
    st.markdown(
        f"""
        <div class="res-card rc-sky" style="
            margin-bottom: 18px;
            padding: 26px;
            align-items: flex-start;
        ">
            <div class="res-icon rc-sky" style="
                width: 64px;
                height: 64px;
                font-size: 2rem;
            ">
                <i class="ri-group-fill"></i>
            </div>
            <div class="res-info">
                <div class="res-name" style="font-size:1.45rem;">
                    Estudantes
                </div>
                <div class="res-meta" style="font-size:0.92rem; margin-top:4px; max-width:820px;">
                    Gestão do workspace (PIN) — <strong>{workspace_name}</strong>. Aqui você visualiza os estudantes criados no PEI
                    deste workspace e pode apagar quando necessário.
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ==============================================================================
# GATE (SEM LOGIN AQUI) — só redireciona para o começo do app
# ==============================================================================
def acesso_bloqueado(msg: str):
    st.markdown(
        f"""
        <div style="
            max-width:520px;
            margin: 110px auto 18px auto;
            padding: 26px;
            background: white;
            border-radius: 18px;
            border: 1px solid #E2E8F0;
            box-shadow: 0 20px 40px rgba(15,82,186,0.10);
            text-align: center;
        ">
            <div style="font-size:2.1rem; margin-bottom:10px;">🔐</div>
            <div style="font-weight:900; font-size:1.1rem; margin-bottom:6px; color:#0f172a;">
                Acesso restrito
            </div>
            <div style="color:#4A5568; font-weight:700; font-size:0.95rem; margin-bottom:10px;">
                {msg}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        if st.button("🔑 Voltar para o Login", use_container_width=True, type="primary"):
            for k in ["autenticado", "workspace_id", "workspace_name", "usuario_nome", "usuario_cargo"]:
                st.session_state.pop(k, None)

            try:
                st.switch_page("streamlit_app.py")
            except Exception:
                st.markdown(
                    """
                    <div style="text-align:center; margin-top:10px;">
                      <a href="/" target="_self"
                         style="display:inline-block; padding:10px 14px; border-radius:12px;
                                background:#0F52BA; color:white; font-weight:900; text-decoration:none;">
                        Clique aqui para voltar ao Login
                      </a>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                st.stop()
    st.stop()


if not st.session_state.get("autenticado", False):
    acesso_bloqueado("Sessão expirada ou não iniciada.")

if not st.session_state.get("workspace_id"):
    acesso_bloqueado("Nenhum workspace vinculado ao seu acesso (PIN).")


WORKSPACE_ID = st.session_state.get("workspace_id")
WORKSPACE_NAME = st.session_state.get("workspace_name") or f"{str(WORKSPACE_ID)[:8]}…"

# ==============================================================================
# SUPABASE REST (mesmo padrão do PEI)
# ==============================================================================
def _sb_url() -> str:
    url = str(st.secrets.get("SUPABASE_URL", "")).strip()
    if not url:
        raise RuntimeError("SUPABASE_URL não encontrado nos secrets.")
    return url.rstrip("/")


def _sb_key() -> str:
    # Preferência: SERVICE_KEY (server-side), fallback: ANON_KEY
    key = str(st.secrets.get("SUPABASE_SERVICE_KEY", "")).strip()
    if not key:
        key = str(st.secrets.get("SUPABASE_ANON_KEY", "")).strip()
    if not key:
        raise RuntimeError("SUPABASE_SERVICE_KEY/ANON_KEY não encontrado nos secrets.")
    return key


def _headers() -> dict:
    key = _sb_key()
    return {
        "apikey": key,
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
    }


def _http_error(prefix: str, r: requests.Response):
    raise RuntimeError(f"{prefix}: {r.status_code} {r.text}")


@st.cache_data(ttl=10, show_spinner=False)
def list_students_rest(workspace_id: str):
    base = (
        f"{_sb_url()}/rest/v1/students"
        f"?select=id,name,birth_date,grade,class_group,diagnosis,created_at"
        f"&workspace_id=eq.{workspace_id}"
        f"&order=created_at.desc"
    )
    r = requests.get(base, headers=_headers(), timeout=20)
    if r.status_code >= 400:
        _http_error("List students falhou", r)
    data = r.json()
    return data if isinstance(data, list) else []


def delete_student_rest(student_id: str, workspace_id: str):
    url = f"{_sb_url()}/rest/v1/students?id=eq.{student_id}&workspace_id=eq.{workspace_id}"
    h = _headers()
    h["Prefer"] = "return=representation"
    r = requests.delete(url, headers=h, timeout=20)
    if r.status_code >= 400:
        _http_error("Delete em students falhou", r)
    return r.json()

# ==============================================================================
# UI
# ==============================================================================

# Topbar fixa (mesmo padrão da Home)
render_topbar()

# Cabeçalho da página no padrão “Recursos Externos”
render_page_header_estudantes(WORKSPACE_NAME)

top_l, top_r = st.columns([3, 1])
with top_l:
    q = st.text_input("Buscar por nome", placeholder="Digite para filtrar…", label_visibility="visible")
with top_r:
    st.markdown("#### Ações")
    if st.button("🔄 Atualizar", use_container_width=True):
        list_students_rest.clear()
        st.rerun()

# 🔥 Se você veio de uma sincronização no PEI, forçamos refresh imediato
if st.session_state.pop("students_dirty", False):
    try:
        list_students_rest.clear()
    except Exception:
        pass

with st.spinner("Carregando estudantes..."):
    try:
        alunos = list_students_rest(WORKSPACE_ID)
    except Exception as e:
        st.error(f"Erro ao carregar do Supabase: {e}")
        st.stop()

# filtro
if q and q.strip():
    qq = q.strip().lower()
    alunos = [a for a in alunos if (a.get("name") or "").lower().find(qq) >= 0]

st.divider()

if not alunos:
    st.info("Nenhum estudante encontrado neste workspace ainda. Crie um PEI para começar.")
    st.stop()

st.caption(f"**{len(alunos)}** estudante(s) exibido(s).")

# Cabeçalho
h = st.columns([3.2, 1.1, 1.1, 2.6, 1.1])
h[0].markdown("**Nome**")
h[1].markdown("**Série**")
h[2].markdown("**Turma**")
h[3].markdown("**Diagnóstico**")
h[4].markdown("**Ações**")
st.divider()

for a in alunos:
    sid = a.get("id")
    nome = a.get("name") or "—"
    serie = a.get("grade") or "—"
    turma = a.get("class_group") or "—"
    diag = a.get("diagnosis") or "—"

    row = st.columns([3.2, 1.1, 1.1, 2.6, 1.1])
    row[0].markdown(f"**{nome}**")
    row[1].write(serie)
    row[2].write(turma)
    row[3].write(diag)

    confirm_key = f"confirm_del_{sid}"
    if confirm_key not in st.session_state:
        st.session_state[confirm_key] = False

    with row[4]:
        if not st.session_state[confirm_key]:
            if st.button("🗑️", key=f"del_{sid}", use_container_width=True, help="Apagar estudante"):
                st.session_state[confirm_key] = True
                st.rerun()
        else:
            st.warning("Confirmar?")
            c1, c2 = st.columns(2)
            with c1:
                if st.button("✅", key=f"yes_{sid}", use_container_width=True):
                    try:
                        delete_student_rest(sid, WORKSPACE_ID)
                        list_students_rest.clear()
                        st.session_state[confirm_key] = False
                        st.toast(f"Removido: {nome}", icon="🗑️")
                        st.rerun()
                    except Exception as e:
                        st.session_state[confirm_key] = False
                        st.error(f"Erro ao apagar: {e}")
            with c2:
                if st.button("↩️", key=f"no_{sid}", use_container_width=True):
                    st.session_state[confirm_key] = False
                    st.rerun()

    st.markdown("<hr style='margin:8px 0; border:none; border-top:1px solid #EEF2F7;'>", unsafe_allow_html=True)

# Rodapé discreto (opcional, não interfere em nada)
st.markdown(
    f"""
    <div style='
        text-align: center;
        color: #64748B;
        font-size: 0.72rem;
        padding: 18px 10px;
        border-top: 1px solid #E2E8F0;
        margin-top: 30px;
        opacity: 0.9;
    '>
        <strong>Omnisfera</strong> • Estudantes • {datetime.now().strftime("%d/%m/%Y %H:%M")}
    </div>
    """,
    unsafe_allow_html=True,
)
