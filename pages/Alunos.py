# pages/Alunos.py
import streamlit as st
import requests
from datetime import datetime
import base64
import os

# ==============================================================================
# CONFIG
# ==============================================================================
st.set_page_config(page_title="Omnisfera • Estudantes", page_icon="👥", layout="wide")

# ==============================================================================
# 🔷 DESIGN SYSTEM COM NAVBAR FLUTUANTE SUPERIOR
# ==============================================================================
def _ui_home_block():
    # Carrega a imagem da logo para base64
    def get_base64_image(image_path: str) -> str:
        """Carrega imagem e converte para base64"""
        if not os.path.exists(image_path):
            return ""
        try:
            with open(image_path, "rb") as f:
                return base64.b64encode(f.read()).decode()
        except Exception:
            return ""

    icone_b64 = get_base64_image("omni_icone.png")
    
    st.markdown(
        f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
@import url("https://cdn.jsdelivr.net/npm/remixicon@3.5.0/fonts/remixicon.css");

/* ===== RESET & BASE ===== */
html, body, [class*="css"] {{
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    color: #1E293B !important;
    background-color: #F8FAFC !important;
}}

/* ===== NAVBAR FLUTUANTE SUPERIOR (PÍLULA) ===== */
.floating-navbar {{
    position: fixed;
    top: 20px;
    left: 50%;
    transform: translateX(-50%);
    width: 90%;
    max-width: 1200px;
    background: rgba(255, 255, 255, 0.95) !important;
    backdrop-filter: blur(12px) !important;
    -webkit-backdrop-filter: blur(12px) !important;
    border: 1px solid #E2E8F0;
    border-radius: 99px;
    z-index: 9999;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 12px 24px;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.08);
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}}

.floating-navbar:hover {{
    box-shadow: 0 12px 48px rgba(0, 0, 0, 0.12);
    border-color: #CBD5E1;
    transform: translateX(-50%) translateY(-2px);
}}

.nav-brand {{
    display: flex;
    align-items: center;
    gap: 12px;
    font-weight: 800;
    font-size: 1.2rem;
    color: #2B3674;
    text-decoration: none;
}}

.nav-logo {{
    width: 32px;
    height: 32px;
    animation: spin 45s linear infinite;
    filter: brightness(1.1);
    transition: all 0.3s ease;
}}

.floating-navbar:hover .nav-logo {{
    animation-duration: 20s;
    filter: brightness(1.2);
}}

@keyframes spin {{
    0% {{ transform: rotate(0deg); }}
    100% {{ transform: rotate(360deg); }}
}}

.nav-menu {{
    display: flex;
    gap: 2px;
    background: #F1F5F9;
    border-radius: 99px;
    padding: 4px;
}}

.nav-item {{
    padding: 10px 20px;
    border-radius: 99px;
    font-size: 0.8rem;
    font-weight: 700;
    color: #64748B;
    text-decoration: none;
    transition: all 0.2s ease;
    border: none;
    background: transparent;
    cursor: pointer;
    white-space: nowrap;
}}

.nav-item:hover {{
    background: white;
    color: #4F46E5;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}}

.nav-item.active {{
    background: white;
    color: #4F46E5;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}}

.nav-actions {{
    display: flex;
    align-items: center;
    gap: 16px;
}}

.nav-action-btn {{
    background: #F1F5F9;
    border: 1px solid #E2E8F0;
    border-radius: 99px;
    padding: 8px 16px;
    font-size: 0.75rem;
    font-weight: 700;
    color: #475569;
    text-decoration: none;
    transition: all 0.2s ease;
    white-space: nowrap;
}}

.nav-action-btn:hover {{
    background: white;
    color: #4F46E5;
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}}

.nav-user {{
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 0.8rem;
    font-weight: 700;
    color: #334155;
}}

.user-avatar {{
    width: 32px;
    height: 32px;
    border-radius: 50%;
    background: linear-gradient(135deg, #4F46E5, #7C3AED);
    color: white;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 800;
    font-size: 0.8rem;
}}

/* ===== CONTAINER COM NAVBAR ===== */
.block-container {{
    padding-top: 100px !important;
    padding-bottom: 3rem !important;
    max-width: 95% !important;
    padding-left: 1rem !important;
    padding-right: 1rem !important;
}}

/* ===== SIDEBAR VISÍVEL ===== */
[data-testid="stHeader"],
[data-testid="stToolbar"],
footer {{
    display: none !important;
}}

/* ===== CARD HERO (ESTILO EXATO DA HOME) ===== */
.mod-card-wrapper {{
    display: flex;
    flex-direction: column;
    margin-bottom: 20px;
    border-radius: 16px;
    overflow: hidden;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.02);
}}

.mod-card-rect {{
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
}}

.mod-card-rect:hover {{
    transform: translateY(-4px);
    box-shadow: 0 12px 24px rgba(0, 0, 0, 0.08);
    border-color: #CBD5E1;
}}

.mod-bar {{
    width: 6px;
    height: 100%;
    flex-shrink: 0;
}}

.mod-icon-area {{
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
}}

.mod-card-rect:hover .mod-icon-area {{
    background: white;
    transform: scale(1.05);
}}

.mod-content {{
    flex-grow: 1;
    padding: 0 24px;
    display: flex;
    flex-direction: column;
    justify-content: center;
}}

.mod-title {{
    font-weight: 800;
    font-size: 1.1rem;
    color: #1E293B;
    margin-bottom: 6px;
    letter-spacing: -0.3px;
    transition: color 0.2s;
}}

.mod-card-rect:hover .mod-title {{
    color: #4F46E5;
}}

.mod-desc {{
    font-size: 0.8rem;
    color: #64748B;
    line-height: 1.4;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
}}

/* CORES DOS CARDS - MESMA DA HOME */
.c-sky {{ background: #0284C7 !important; }}
.bg-sky-soft {{ 
    background: #F0F9FF !important;
    color: #0284C7 !important;
}}

/* ===== STUDENT TABLE (MELHORADA) ===== */
.student-table {{
    background: white;
    border-radius: 16px;
    border: 1px solid #E2E8F0;
    overflow: hidden;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.02);
    margin-top: 24px;
}}

.student-header {{
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
}}

.student-row {{
    display: grid;
    grid-template-columns: 3.2fr 1.1fr 1.1fr 2.6fr 1.1fr;
    padding: 20px 24px;
    border-bottom: 1px solid #F1F5F9;
    align-items: center;
    transition: all 0.2s ease;
    background: white;
}}

.student-row:hover {{
    background: #F8FAFC;
    transform: translateX(4px);
}}

.student-name {{
    font-weight: 700;
    color: #1E293B;
    font-size: 0.95rem;
}}

.student-meta {{
    font-size: 0.85rem;
    color: #64748B;
    font-weight: 500;
}}

/* ===== BADGES ===== */
.badge-grade {{
    background: #F0F9FF;
    color: #0369A1;
    padding: 4px 10px;
    border-radius: 20px;
    font-size: 0.8rem;
    font-weight: 700;
    border: 1px solid #BAE6FD;
    display: inline-block;
    text-align: center;
}}

.badge-class {{
    background: #F0FDF4;
    color: #15803D;
    padding: 4px 10px;
    border-radius: 20px;
    font-size: 0.8rem;
    font-weight: 700;
    border: 1px solid #BBF7D0;
    display: inline-block;
    text-align: center;
}}

/* ===== ACTION BUTTONS (MELHORADO) ===== */
.action-btn-small {{
    width: 36px;
    height: 36px;
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    transition: all 0.2s ease;
    border: 1px solid transparent;
    font-size: 0.9rem;
    background: white;
    color: #475569;
    border: 1px solid #E2E8F0;
}}

.action-btn-small:hover {{
    transform: translateY(-2px);
    box-shadow: 0 6px 12px rgba(0, 0, 0, 0.08);
}}

.action-delete {{
    background: #FEF2F2;
    color: #DC2626;
    border-color: #FECACA;
}}

.action-delete:hover {{
    background: #FEE2E2;
}}

.action-confirm {{
    background: #DCFCE7;
    color: #16A34A;
    border-color: #BBF7D0;
}}

.action-cancel {{
    background: #FEF3C7;
    color: #D97706;
    border-color: #FDE68A;
}}

/* ===== EMPTY STATE ===== */
.empty-state {{
    text-align: center;
    padding: 80px 40px;
    background: white;
    border-radius: 16px;
    border: 1px dashed #E2E8F0;
    margin-top: 24px;
}}

.empty-icon {{
    font-size: 3rem;
    color: #CBD5E1;
    margin-bottom: 16px;
}}

.empty-title {{
    font-weight: 800;
    color: #64748B;
    margin-bottom: 8px;
}}

.empty-desc {{
    color: #94A3B8;
    font-size: 0.9rem;
    max-width: 400px;
    margin: 0 auto;
}}

/* ===== STREAMLIT OVERRIDES ===== */
.stButton > button {{
    border-radius: 12px !important;
    border: 1px solid #E2E8F0 !important;
    background: white !important;
    color: #475569 !important;
    font-weight: 800 !important;
    font-size: 0.85rem !important;
    padding: 10px 20px !important;
    transition: all 0.2s ease !important;
}}

.stButton > button:hover {{
    background: #F8FAFC !important;
    color: #4F46E5 !important;
    border-color: #CBD5E1 !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 12px rgba(0, 0, 0, 0.08) !important;
}}

.stTextInput > div > div > input {{
    border-radius: 12px !important;
    border: 1px solid #E2E8F0 !important;
    padding: 12px 16px !important;
    font-size: 0.9rem !important;
}}

.stTextInput > div > div > input:focus {{
    border-color: #4F46E5 !important;
    box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.1) !important;
}}

/* ===== RESPONSIVIDADE ===== */
@media (max-width: 1024px) {{
    .floating-navbar {{
        flex-direction: column;
        gap: 12px;
        border-radius: 20px;
        padding: 16px;
        top: 10px;
    }}
    .nav-menu {{
        flex-wrap: wrap;
        justify-content: center;
    }}
    .nav-actions {{
        flex-wrap: wrap;
        justify-content: center;
    }}
    .student-header, .student-row {{ grid-template-columns: 2.5fr 1fr 1fr 2fr 1fr; }}
    .mod-card-rect {{ height: 120px; }}
    .mod-icon-area {{ width: 80px; }}
}}

@media (max-width: 768px) {{
    .floating-navbar {{
        width: 95%;
        padding: 12px;
    }}
    .nav-brand span {{
        display: none;
    }}
    .nav-item {{
        padding: 8px 12px;
        font-size: 0.7rem;
    }}
    .nav-action-btn {{
        padding: 6px 12px;
        font-size: 0.7rem;
    }}
    .student-header, .student-row {{ grid-template-columns: 1fr; gap: 12px; }}
    .student-header {{ display: none; }}
    .mod-card-rect {{ 
        height: 110px;
        flex-direction: column;
        height: auto;
        padding: 16px;
    }}
    .mod-bar {{ width: 100%; height: 6px; }}
    .mod-icon-area {{ 
        width: 100%; 
        height: 60px; 
        border-right: none;
        border-bottom: 1px solid #F1F5F9;
    }}
    .mod-content {{ padding: 16px 0 0 0; }}
}}

/* ===== BANNER DE CONFIRMAÇÃO DE EXCLUSÃO ===== */
.delete-confirm-banner {{
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
}}
</style>

<!-- NAVBAR FLUTUANTE SUPERIOR -->
<div class="floating-navbar">
    <div class="nav-brand">
        {f'<img src="data:image/png;base64,{icone_b64}" class="nav-logo" alt="Omnisfera Logo">' if icone_b64 else '🌐'}
        <span>OMNISFERA</span>
    </div>
    
    <div class="nav-menu">
        <button class="nav-item active" onclick="window.location.href='/Alunos'">ESTUDANTES</button>
        <button class="nav-item" onclick="window.location.href='/1_PEI'">PEI</button>
        <button class="nav-item" onclick="window.location.href='/2_PAE'">PLANO DE AÇÃO</button>
        <button class="nav-item" onclick="window.location.href='/4_Diario_de_Bordo'">DIÁRIO</button>
        <button class="nav-item" onclick="window.location.href='/5_Monitoramento_Avaliacao'">DASHBOARD</button>
        <button class="nav-item" onclick="window.location.href='/3_Hub_Inclusao'">HUB IA</button>
    </div>
    
    <div class="nav-actions">
        <a href="#" class="nav-action-btn">WORKSPACE</a>
        <a href="#" class="nav-action-btn">AJUDA</a>
        <div class="nav-user">
            <div class="user-avatar" id="userAvatar">U</div>
        </div>
    </div>
</div>

<script>
// Função para definir as iniciais do usuário no avatar
function setUserInitials() {{
    const userName = "{st.session_state.get('usuario_nome', 'Visitante')}";
    if (!userName) return;
    
    const parts = userName.split(' ');
    let initials = 'U';
    if (parts.length >= 2) {{
        initials = (parts[0][0] + parts[parts.length - 1][0]).toUpperCase();
    }} else if (userName.length >= 2) {{
        initials = userName.substring(0, 2).toUpperCase();
    }} else {{
        initials = userName[0].toUpperCase();
    }}
    
    document.getElementById('userAvatar').textContent = initials;
}}

// Executar quando a página carregar
document.addEventListener('DOMContentLoaded', setUserInitials);
</script>
        """,
        unsafe_allow_html=True,
    )


_ui_home_block()

# ==============================================================================
# 🔒 VERIFICAÇÃO DE ACESSO
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
# CARD HERO (ESTILO EXATO DA HOME COM HOVER)
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
    if st.button("🔄 Atualizar Lista", use_container_width=True, type="secondary"):
        list_students_rest.clear()
        st.rerun()

# 🔥 Refresh automático se veio do PEI
if st.session_state.pop("students_dirty", False):
    try:
        list_students_rest.clear()
    except Exception:
        pass

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
with st.spinner("Carregando estudantes..."):
    try:
        alunos = list_students_rest(WORKSPACE_ID)
    except Exception as e:
        st.error(f"Erro ao carregar do Supabase: {e}")
        st.stop()

# Filtro
if q and q.strip():
    qq = q.strip().lower()
    alunos = [a for a in alunos if (a.get("name") or "").lower().find(qq) >= 0]

# ==============================================================================
# RENDERIZAÇÃO DOS ESTUDANTES
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

# Header da tabela
st.markdown(
    f"""
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

# Contador
st.caption(f"**{len(alunos)}** estudante(s) encontrado(s)")

# Linhas dos estudantes
for a in alunos:
    sid = a.get("id")
    nome = a.get("name") or "—"
    serie = a.get("grade") or "—"
    turma = a.get("class_group") or "—"
    diag = a.get("diagnosis") or "—"
    
    confirm_key = f"confirm_del_{sid}"
    if confirm_key not in st.session_state:
        st.session_state[confirm_key] = False
    
    # Renderiza a linha
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
    
    # Controles de ação com hover antigo preservado
    if not st.session_state[confirm_key]:
        col1, _ = st.columns([1, 5])
        with col1:
            if st.button("🗑️", key=f"del_{sid}", help="Apagar estudante", use_container_width=True):
                st.session_state[confirm_key] = True
                st.rerun()
    else:
        # Modal de confirmação inline
        st.markdown(f"""
        <div class="delete-confirm-banner">
            <i class="ri-alert-fill"></i>
            <div>Confirmar exclusão de <strong>{nome}</strong>?</div>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
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
        
        with col2:
            if st.button("❌ Não", key=f"no_{sid}", use_container_width=True):
                st.session_state[confirm_key] = False
                st.rerun()
    
    st.markdown("</div></div>", unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)  # Fecha student-table

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
        <strong>Omnisfera v2.0</strong> • Gestão de Estudantes • 
        Workspace: {WORKSPACE_NAME[:30]} • 
        {datetime.now().strftime("%d/%m/%Y %H:%M")}
    </div>
    """,
    unsafe_allow_html=True,
)
