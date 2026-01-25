# pages/Alunos.py
import streamlit as st
import requests
from datetime import datetime
import base64
import os

# ==============================================================================
# CONFIG
# ==============================================================================
st.set_page_config(
    page_title="Omnisfera • Estudantes",
    page_icon="👥",
    layout="wide",
    initial_sidebar_state="expanded",
)

APP_VERSION = "v2.0 - Gestão de Estudantes"

# ==============================================================================
# Helpers essenciais (faltava isso aqui)
# ==============================================================================
def get_base64_image(image_path: str) -> str:
    """Lê imagem local e retorna base64 (string vazia se não existir)."""
    if not os.path.exists(image_path):
        return ""
    try:
        with open(image_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except Exception:
        return ""

# ==============================================================================
# 🔷 DESIGN SYSTEM (mantive seu bloco, mas acrescentei CSS da Topbar + padding)
# ==============================================================================
def _ui_home_block():
    st.markdown(
        """
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
@import url("https://cdn.jsdelivr.net/npm/remixicon@3.5.0/fonts/remixicon.css");

/* ===== RESET & BASE ===== */
html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    color: #1E293B !important;
    background-color: #F8FAFC !important;
}

/* ===== TOPBAR (faltava no seu arquivo) ===== */
.topbar {
    position: fixed; top: 0; left: 0; right: 0; height: 74px;
    background: rgba(255, 255, 255, 0.98) !important;
    border-bottom: 1px solid #E2E8F0;
    z-index: 9999;
    display: flex; align-items: center; justify-content: space-between;
    padding: 0 1.25rem;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
}

.brand-box { display: flex; align-items: center; gap: 10px; }

.brand-logo { height: 46px !important; width: auto !important; animation: spin 45s linear infinite; }
.brand-img-text { height: 30px !important; width: auto; margin-left: 8px; }

.user-badge {
    background: #F1F5F9;
    border: 1px solid #E2E8F0;
    padding: 6px 14px;
    border-radius: 999px;
    font-size: 0.75rem;
    font-weight: 800;
    color: #64748B;
}

/* AVATAR (iniciais) — usado pela topbar completa */
.apple-avatar {
    width: 36px;
    height: 36px;
    border-radius: 999px;
    background: linear-gradient(135deg, #2563EB, #1E40AF);
    color: white;
    font-weight: 800;
    font-size: 0.75rem;
    display: flex;
    align-items: center;
    justify-content: center;
}

@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }

/* ===== CONTAINER =====
   Ajuste: agora o conteúdo desce o suficiente para não ficar embaixo da Topbar + Menu rápido */
.block-container {
    padding-top: 120px !important; /* era 3.5rem; aqui resolve topbar + quick access */
    padding-bottom: 3rem !important;
    max-width: 95% !important;
    padding-left: 1rem !important;
    padding-right: 1rem !important;
}

/* ===== CARD HERO (ESTILO EXATO DA HOME) ===== */
.mod-card-wrapper {
    display: flex;
    flex-direction: column;
    margin-bottom: 20px;
    border-radius: 16px;
    overflow: hidden;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.02);
}

.mod-card-rect {
    background: white;
    border-radius: 16px 16px 0 0;
    padding: 0;
    border: 1px solid #E2E8F0;
    border-bottom: none;
    display: flex;
    flex-direction: row;
    align-items: center;
    height: 130px;
    width: 100%;
    position: relative;
    overflow: hidden;
    transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
}

.mod-card-rect:hover {
    transform: translateY(-4px);
    box-shadow: 0 12px 24px rgba(0, 0, 0, 0.08);
    border-color: #CBD5E1;
}

.mod-bar { width: 6px; height: 100%; flex-shrink: 0; }

.mod-icon-area {
    width: 90px;
    height: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.8rem;
    flex-shrink: 0;
    background: #FAFAFA;
    border-right: 1px solid #F1F5F9;
    transition: all 0.3s ease;
}

.mod-card-rect:hover .mod-icon-area {
    background: white;
    transform: scale(1.05);
}

.mod-content {
    flex-grow: 1;
    padding: 0 24px;
    display: flex;
    flex-direction: column;
    justify-content: center;
}

.mod-title {
    font-weight: 800;
    font-size: 1.1rem;
    color: #1E293B;
    margin-bottom: 6px;
    letter-spacing: -0.3px;
    transition: color 0.2s;
}

.mod-card-rect:hover .mod-title { color: #4F46E5; }

.mod-desc {
    font-size: 0.8rem;
    color: #64748B;
    line-height: 1.4;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
}

/* CORES DOS CARDS - MESMA DA HOME */
.c-sky { background: #0284C7 !important; }
.bg-sky-soft { background: #F0F9FF !important; color: #0284C7 !important; }

/* ===== STUDENT TABLE ===== */
.student-table {
    background: white;
    border-radius: 16px;
    border: 1px solid #E2E8F0;
    overflow: hidden;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.02);
    margin-top: 24px;
}

.student-header {
    display: grid;
    grid-template-columns: 3.2fr 1.1fr 1.1fr 2.6fr 1.1fr;
    background: #F8FAFC;
    padding: 18px 24px;
    border-bottom: 2px solid #E2E8F0;
    font-weight: 800;
    color: #475569;
    font-size: 0.85rem;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.student-row {
    display: grid;
    grid-template-columns: 3.2fr 1.1fr 1.1fr 2.6fr 1.1fr;
    padding: 20px 24px;
    border-bottom: 1px solid #F1F5F9;
    align-items: center;
    transition: all 0.2s ease;
    background: white;
}

.student-row:hover { background: #F8FAFC; transform: translateX(4px); }

.student-name { font-weight: 700; color: #1E293B; font-size: 0.95rem; }
.student-meta { font-size: 0.85rem; color: #64748B; font-weight: 500; }

.badge-grade {
    background: #F0F9FF;
    color: #0369A1;
    padding: 4px 10px;
    border-radius: 20px;
    font-size: 0.8rem;
    font-weight: 700;
    border: 1px solid #BAE6FD;
    display: inline-block;
    text-align: center;
}

.badge-class {
    background: #F0FDF4;
    color: #15803D;
    padding: 4px 10px;
    border-radius: 20px;
    font-size: 0.8rem;
    font-weight: 700;
    border: 1px solid #BBF7D0;
    display: inline-block;
    text-align: center;
}

.empty-state {
    text-align: center;
    padding: 80px 40px;
    background: white;
    border-radius: 16px;
    border: 1px dashed #E2E8F0;
    margin-top: 24px;
}

.empty-icon { font-size: 3rem; color: #CBD5E1; margin-bottom: 16px; }
.empty-title { font-weight: 800; color: #64748B; margin-bottom: 8px; }
.empty-desc { color: #94A3B8; font-size: 0.9rem; max-width: 400px; margin: 0 auto; }

/* ===== BANNER DE CONFIRMAÇÃO ===== */
.delete-confirm-banner {
    background: #FEF3C7;
    border: 1px solid #FDE68A;
    border-radius: 8px;
    padding: 8px 12px;
    margin-top: 4px;
    font-size: 0.8rem;
    color: #92400E;
    display: flex;
    align-items: center;
    gap: 8px;
}
</style>
        """,
        unsafe_allow_html=True,
    )

_ui_home_block()

# ==============================================================================
# BLOCO A — TOPBAR COMPLETA (Logo + Workspace + Usuário + Avatar)
# ==============================================================================
def get_user_initials(nome: str) -> str:
    if not nome:
        return "U"
    parts = nome.strip().split()
    if len(parts) >= 2:
        return f"{parts[0][0]}{parts[-1][0]}".upper()
    return parts[0][:2].upper()

def get_user_first_name() -> str:
    return (st.session_state.get("usuario_nome", "Visitante").strip().split() or ["Visitante"])[0]

def get_workspace_short(max_len: int = 20) -> str:
    ws = st.session_state.get("workspace_name", "") or ""
    return (ws[:max_len] + "...") if len(ws) > max_len else ws

def render_topbar():
    icone_b64 = get_base64_image("omni_icone.png")
    texto_b64 = get_base64_image("omni_texto.png")

    img_logo = f'<img src="data:image/png;base64,{icone_b64}" class="brand-logo">' if icone_b64 else "🌐"
    img_text = f'<img src="data:image/png;base64,{texto_b64}" class="brand-img-text">' if texto_b64 else "<span style='font-weight:800;color:#2B3674;'>OMNISFERA</span>"

    user_full = st.session_state.get("usuario_nome", "Visitante")
    user_first = get_user_first_name()
    initials = get_user_initials(user_full)
    ws_name = get_workspace_short()

    st.markdown(
        f"""
        <div class="topbar">
            <div class="brand-box">
                {img_logo}
                {img_text}
            </div>

            <div class="brand-box" style="gap:10px;">
                <div class="user-badge">{ws_name}</div>
                <div class="user-badge">{user_first}</div>
                <div class="apple-avatar">{initials}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

# ==============================================================================
# BLOCO B — MENU DE ACESSO RÁPIDO
# ==============================================================================
def render_quick_access_bar():
    st.markdown("""
    <style>
        .qa-btn button {
            font-weight: 800 !important;
            border-radius: 6px !important;
            padding: 4px 0 !important;
            font-size: 0.7rem !important;
            text-transform: uppercase !important;
            box-shadow: none !important;
            min-height: 32px !important;
            border-width: 1px !important;
        }

        div[data-testid="column"]:nth-of-type(1) .qa-btn button { border-color:#64748B !important; color:#64748B !important; background:white !important;}
        div[data-testid="column"]:nth-of-type(2) .qa-btn button { border-color:#4F46E5 !important; color:#4F46E5 !important; background:white !important;}
        div[data-testid="column"]:nth-of-type(3) .qa-btn button { border-color:#2563EB !important; color:#2563EB !important; background:white !important;}
        div[data-testid="column"]:nth-of-type(4) .qa-btn button { border-color:#7C3AED !important; color:#7C3AED !important; background:white !important;}
        div[data-testid="column"]:nth-of-type(5) .qa-btn button { border-color:#0D9488 !important; color:#0D9488 !important; background:white !important;}
        div[data-testid="column"]:nth-of-type(6) .qa-btn button { border-color:#E11D48 !important; color:#E11D48 !important; background:white !important;}
        div[data-testid="column"]:nth-of-type(7) .qa-btn button { border-color:#0284C7 !important; color:#0284C7 !important; background:white !important;}
    </style>
    """, unsafe_allow_html=True)

    c1, c2, c3, c4, c5, c6, c7 = st.columns(7, gap="small")

    def _wrap_button(label: str, on_click):
        st.markdown('<div class="qa-btn">', unsafe_allow_html=True)
        st.button(label, use_container_width=True, on_click=on_click)
        st.markdown('</div>', unsafe_allow_html=True)

    with c1: _wrap_button("INÍCIO", lambda: st.switch_page("pages/0_Home.py"))
    with c2: _wrap_button("ESTUDANTES", lambda: st.rerun())
    with c3: _wrap_button("PEI", lambda: st.switch_page("pages/1_PEI.py"))
    with c4: _wrap_button("AEE", lambda: st.switch_page("pages/2_PAE.py"))
    with c5: _wrap_button("RECURSOS", lambda: st.switch_page("pages/3_Hub_Inclusao.py"))
    with c6: _wrap_button("DIÁRIO", lambda: st.switch_page("pages/4_Diario_de_Bordo.py"))
    with c7: _wrap_button("DADOS", lambda: st.switch_page("pages/5_Monitoramento_Avaliacao.py"))

# ==============================================================================
# 🔒 VERIFICAÇÃO DE ACESSO (mantive sua lógica)
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
USUARIO_NOME = st.session_state.get("usuario_nome", "Visitante").split()[0]

# ==============================================================================
# ✅ CHAMADAS (isso faltava!)
# ==============================================================================
render_topbar()
render_quick_access_bar()

# ==============================================================================
# SIDEBAR PERSONALIZADA (mantive)
# ==============================================================================
with st.sidebar:
    st.markdown("### 🧭 Navegação")

    if st.button("🏠 Home", key="nav_home", use_container_width=True,
                 help="Voltar para a página inicial"):
        st.switch_page("pages/0_Home.py")

    col1, col2 = st.columns(2)
    with col1:
        st.button("👥 Estudantes", key="nav_estudantes", use_container_width=True, disabled=True)
    with col2:
        if st.button("📘 PEI", key="nav_pei", use_container_width=True):
            st.switch_page("pages/1_PEI.py")

    if st.button("🧩 Plano de Ação", key="nav_paee", use_container_width=True):
        st.switch_page("pages/2_PAE.py")

    if st.button("🚀 Hub IA", key="nav_hub", use_container_width=True):
        st.switch_page("pages/3_Hub_Inclusao.py")

    if st.button("📝 Diário", key="nav_diario", use_container_width=True):
        st.switch_page("pages/4_Diario_de_Bordo.py")

    if st.button("📊 Dashboard", key="nav_dashboard", use_container_width=True):
        st.switch_page("pages/5_Monitoramento_Avaliacao.py")

    st.markdown("---")
    st.markdown("### 👤 Sessão")
    st.caption(f"**Usuário:** {st.session_state.get('usuario_nome', 'Visitante')}")
    st.caption(f"**Workspace:** {WORKSPACE_NAME}")

    st.markdown("---")
    st.markdown("### 🔧 Ações")
    if st.button("🔄 Sincronizar Dados", key="sync_sidebar", use_container_width=True,
                 help="Atualizar todos os dados do workspace"):
        st.session_state["force_refresh"] = True
        st.rerun()

    st.markdown("---")
    st.markdown(f"**Versão:** {APP_VERSION}")

    if st.button("🚪 Sair", key="btn_sair", use_container_width=True):
        for k in ["autenticado", "workspace_id", "workspace_name", "usuario_nome", "usuario_cargo"]:
            st.session_state.pop(k, None)
        st.switch_page("streamlit_app.py")

# ==============================================================================
# CARD HERO
# ==============================================================================
hora = datetime.now().hour
saudacao = "Bom dia" if 5 <= hora < 12 else "Boa tarde" if 12 <= hora < 18 else "Boa noite"

st.markdown(
    f"""
    <div class="mod-card-wrapper">
        <div class="mod-card-rect">
            <div class="mod-bar c-sky"></div>
            <div class="mod-icon-area bg-sky-soft">
                <i class="ri-group-fill"></i>
            </div>
            <div class="mod-content">
                <div class="mod-title">Gestão de Estudantes</div>
                <div class="mod-desc">
                    {saudacao}, <strong>{USUARIO_NOME}</strong>! Aqui você gerencia todos os estudantes do workspace
                    <strong>{WORKSPACE_NAME}</strong>. Visualize, busque e administre os dados dos alunos vinculados aos PEIs.
                </div>
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ==============================================================================
# CONTROLES SUPERIORES
# ==============================================================================
col1, col2 = st.columns([3, 1], gap="medium")

with col1:
    q = st.text_input(
        "Buscar por nome",
        placeholder="Digite o nome do estudante...",
        label_visibility="collapsed",
        key="search_students"
    )

with col2:
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    if st.button("**🔄 Atualizar Lista**", key="btn_refresh", use_container_width=True):
        st.session_state["force_refresh"] = True
        st.rerun()

force_refresh = st.session_state.pop("force_refresh", False) or st.session_state.pop("students_dirty", False)

# ==============================================================================
# SUPABASE REST
# ==============================================================================
def _sb_url() -> str:
    url = str(st.secrets.get("SUPABASE_URL", "")).strip()
    if not url:
        raise RuntimeError("SUPABASE_URL não encontrado nos secrets.")
    return url.rstrip("/")

def _sb_key() -> str:
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
# CARREGAMENTO DOS DADOS
# ==============================================================================
if force_refresh:
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

if q and q.strip():
    qq = q.strip().lower()
    alunos = [a for a in alunos if (a.get("name") or "").lower().find(qq) >= 0]

# ==============================================================================
# RENDERIZAÇÃO
# ==============================================================================
if not alunos:
    st.markdown(
        """
        <div class="empty-state">
            <div class="empty-icon"><i class="ri-user-search-line"></i></div>
            <div class="empty-title">Nenhum estudante encontrado</div>
            <div class="empty-desc">
                Este workspace ainda não possui estudantes cadastrados.
                Crie um PEI para começar a adicionar alunos.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.stop()

st.markdown(
    """
    <div class="student-table">
        <div class="student-header">
            <div>Nome</div>
            <div>Série</div>
            <div>Turma</div>
            <div>Diagnóstico</div>
            <div>Ações</div>
        </div>
    """,
    unsafe_allow_html=True,
)

st.caption(f"**{len(alunos)}** estudante(s) encontrado(s)")

for a in alunos:
    sid = a.get("id")
    nome = a.get("name") or "—"
    serie = a.get("grade") or "—"
    turma = a.get("class_group") or "—"
    diag = a.get("diagnosis") or "—"

    confirm_key = f"confirm_del_{sid}"
    if confirm_key not in st.session_state:
        st.session_state[confirm_key] = False

    st.markdown(
        f"""
        <div class="student-row">
            <div class="student-name">{nome}</div>
            <div><span class="badge-grade">{serie}</span></div>
            <div><span class="badge-class">{turma}</span></div>
            <div class="student-meta">{diag}</div>
            <div>
        """,
        unsafe_allow_html=True,
    )

    if not st.session_state[confirm_key]:
        colx, _ = st.columns([1, 5])
        with colx:
            if st.button("🗑️", key=f"del_{sid}", help="Apagar estudante", use_container_width=True):
                st.session_state[confirm_key] = True
                st.rerun()
    else:
        st.markdown(
            f"""
            <div class="delete-confirm-banner">
                <i class="ri-alert-fill"></i>
                <div>Confirmar exclusão de <strong>{nome}</strong>?</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        c1, c2 = st.columns(2)
        with c1:
            if st.button("✅ Sim", key=f"yes_{sid}", use_container_width=True, type="primary"):
                try:
                    delete_student_rest(sid, WORKSPACE_ID)
                    list_students_rest.clear()
                    st.session_state[confirm_key] = False
                    st.toast(f"✅ Estudante '{nome}' removido com sucesso!", icon="🗑️")
                    st.rerun()
                except Exception as e:
                    st.session_state[confirm_key] = False
                    st.error(f"Erro ao apagar: {e}")

        with c2:
            if st.button("❌ Não", key=f"no_{sid}", use_container_width=True):
                st.session_state[confirm_key] = False
                st.rerun()

    st.markdown("</div></div>", unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)

# ==============================================================================
# RODAPÉ
# ==============================================================================
st.markdown(
    f"""
    <div style='
        text-align: center;
        color: #64748B;
        font-size: 0.75rem;
        padding: 20px;
        border-top: 1px solid #E2E8F0;
        margin-top: 40px;
    '>
        <strong>Omnisfera {APP_VERSION}</strong> • Gestão de Estudantes •
        Workspace: {WORKSPACE_NAME[:30]} •
        {datetime.now().strftime("%d/%m/%Y %H:%M")}
    </div>
    """,
    unsafe_allow_html=True,
)
