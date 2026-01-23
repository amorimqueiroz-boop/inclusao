# pages/1_PEI.py
import streamlit as st
from datetime import date
from io import BytesIO
from docx import Document
from openai import OpenAI
from pypdf import PdfReader
from fpdf import FPDF
import requests
import base64
import json
import os
import time
import re
from datetime import date, datetime


# ✅ 1) set_page_config (UMA VEZ SÓ e sempre no topo)
st.set_page_config(
    page_title="Omnisfera | PEI",
    page_icon="📘",
    layout="wide",
    initial_sidebar_state="expanded",
)

APP_VERSION = "v150.0 (SaaS Design)"

# ✅ 2) UI lockdown (não quebra se faltar arquivo)
try:
    from ui_lockdown import hide_streamlit_chrome_if_needed, hide_default_sidebar_nav
    hide_streamlit_chrome_if_needed()
    hide_default_sidebar_nav()
except Exception:
    pass

# ✅ 3) Flag de ambiente (opcional)
try:
    IS_TEST_ENV = st.secrets.get("ENV") == "TESTE"
except Exception:
    IS_TEST_ENV = False

# ✅ 4) Gate mínimo: autenticado + workspace_id
if not st.session_state.get("autenticado"):
    st.error("🔒 Acesso negado. Faça login na Página Inicial.")
    st.stop()

ws_id = st.session_state.get("workspace_id")
if not ws_id:
    st.error("Workspace não definido. Volte ao Início e valide o PIN.")
    if st.button("Voltar para Login", key="pei_btn_voltar_login", use_container_width=True):
        for k in ["autenticado", "workspace_id", "workspace_name", "usuario_nome", "usuario_cargo", "supabase_jwt", "supabase_user_id"]:
            st.session_state.pop(k, None)
        st.switch_page("streamlit_app.py")
    st.stop()

# ✅ 5) Supabase (opcional: não bloqueia PEI se der ruim)
sb = None
try:
    from _client import get_supabase
    sb = get_supabase()  # <-- cliente (não é função)
except Exception:
    sb = None

# Guardas legadas (não travam)
def verificar_login_supabase():
    st.session_state.setdefault("supabase_jwt", "")
    st.session_state.setdefault("supabase_user_id", "")

verificar_login_supabase()
OWNER_ID = st.session_state.get("supabase_user_id", "")

# ✅ Sidebar UNIFICADA (navegação + sessão + salvar/carregar + sync)
with st.sidebar:
    st.markdown("### 🧭 Navegação")
    if st.button("🏠 Home", key="pei_nav_home", use_container_width=True):
        st.switch_page("streamlit_app.py")  # se sua home for pages/0_Home.py, troque aqui

    col1, col2 = st.columns(2)
    with col1:
        st.button("📘 PEI", key="pei_nav_pei", use_container_width=True, disabled=True)
    with col2:
        if st.button("🧩 PAEE", key="pei_nav_paee", use_container_width=True):
            st.switch_page("pages/2_PAE.py")

    if st.button("🚀 Hub", key="pei_nav_hub", use_container_width=True):
        st.switch_page("pages/3_Hub_Inclusao.py")

    st.markdown("---")
    st.markdown("### 👤 Sessão")
    st.caption(f"Usuário: **{st.session_state.get('usuario_nome','')}**")
    st.caption(f"Workspace: **{st.session_state.get('workspace_name','')}**")

    st.markdown("---")
    st.markdown("### 🔑 OpenAI")
    if 'OPENAI_API_KEY' in st.secrets:
        api_key = st.secrets['OPENAI_API_KEY']
        st.success("✅ OpenAI OK")
    else:
        api_key = st.text_input("Chave OpenAI:", type="password", key="pei_openai_key")

    st.markdown("---")
    st.markdown("### 🧾 Status do Aluno (Supabase)")
    st.session_state.setdefault("selected_student_id", None)
    st.session_state.setdefault("selected_student_name", "")

    student_id = st.session_state.get("selected_student_id")
    if student_id:
        st.success("✅ Vinculado ao Supabase")
        st.caption(f"student_id: {student_id[:8]}...")
    else:
        st.warning("📝 Rascunho (ainda não salvo no Supabase)")

    # Aviso se supabase não estiver pronto
    if sb is None:
        st.info("Supabase não inicializado (sb=None). O PEI funciona em rascunho, mas não salva/carrega.")

    st.markdown("---")

# ==============================================================================
# 1. GUARDAS (LOGIN + SUPABASE)
# ==============================================================================
def verificar_login_app():
    if "autenticado" not in st.session_state or not st.session_state["autenticado"]:
        st.error("🔒 Acesso Negado. Faça login na Página Inicial.")
        st.stop()

def verificar_login_supabase():
    # Supabase é necessário para SALVAR/CARREGAR, mas o PEI pode abrir como rascunho.
    # Então aqui só garantimos chaves mínimas (não bloqueia).
    if "supabase_jwt" not in st.session_state:
        st.session_state["supabase_jwt"] = ""
    if "supabase_user_id" not in st.session_state:
        st.session_state["supabase_user_id"] = ""

verificar_login_app()
verificar_login_supabase()


# =============================================================================
# 2. SUPABASE (CRUD students) — REST (compatível com omni_utils.py)
#    Remove dependência de: sb / OWNER_ID / supabase-py
# =============================================================================

def _rest_ready(debug: bool = False):
    """
    Checa se a nuvem está pronta para operar via REST:
    - autenticado
    - workspace_id presente
    - SUPABASE_URL e alguma KEY (SERVICE ou ANON) presentes
    """
    details = {}
    details["autenticado"] = bool(st.session_state.get("autenticado", False))
    details["has_workspace_id"] = bool(st.session_state.get("workspace_id"))

    try:
        details["has_supabase_url"] = bool(str(st.secrets.get("SUPABASE_URL", "")).strip())
    except Exception:
        details["has_supabase_url"] = False

    try:
        service = str(st.secrets.get("SUPABASE_SERVICE_KEY", "")).strip()
        anon = str(st.secrets.get("SUPABASE_ANON_KEY", "")).strip()
        details["has_supabase_key"] = bool(service or anon)
    except Exception:
        details["has_supabase_key"] = False

    ok = all(details.values())
    if debug:
        details["missing"] = [k for k, v in details.items() if not v]
    return ok, details


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


def _http_error(prefix: str, r):
    raise RuntimeError(f"{prefix}: {r.status_code} {r.text}")


def db_create_student(payload: dict):
    """
    Cria aluno em public.students usando REST.
    - injeta workspace_id automaticamente
    - retorna o registro criado
    """
    ok, details = _rest_ready(debug=True)
    if not ok:
        raise RuntimeError(f"Supabase não está pronto (REST). Missing: {details.get('missing')}")

    ws_id = st.session_state.get("workspace_id")
    row = dict(payload or {})
    row["workspace_id"] = ws_id

    url = f"{_sb_url()}/rest/v1/students"
    h = _headers()
    h["Prefer"] = "return=representation"

    r = requests.post(url, headers=h, json=row, timeout=20)
    if r.status_code >= 400:
        _http_error("Insert em students falhou", r)

    data = r.json()
    if isinstance(data, list) and len(data) > 0:
        return data[0]
    if isinstance(data, dict):
        return data
    return None


def db_update_student(student_id: str, payload: dict):
    """
    Atualiza aluno em public.students (por id) via REST
    - garante workspace_id no filtro
    """
    ok, details = _rest_ready(debug=True)
    if not ok:
        raise RuntimeError(f"Supabase não está pronto (REST). Missing: {details.get('missing')}")

    ws_id = st.session_state.get("workspace_id")
    row = dict(payload or {})

    url = f"{_sb_url()}/rest/v1/students?id=eq.{student_id}&workspace_id=eq.{ws_id}"
    h = _headers()
    h["Prefer"] = "return=representation"

    r = requests.patch(url, headers=h, json=row, timeout=20)
    if r.status_code >= 400:
        _http_error("Update em students falhou", r)

    data = r.json()
    if isinstance(data, list) and len(data) > 0:
        return data[0]
    if isinstance(data, dict):
        return data
    return None


def db_delete_student(student_id: str):
    """
    Deleta aluno em public.students (por id) via REST
    - garante workspace_id no filtro
    """
    ok, details = _rest_ready(debug=True)
    if not ok:
        raise RuntimeError(f"Supabase não está pronto (REST). Missing: {details.get('missing')}")

    ws_id = st.session_state.get("workspace_id")

    url = f"{_sb_url()}/rest/v1/students?id=eq.{student_id}&workspace_id=eq.{ws_id}"
    h = _headers()
    h["Prefer"] = "return=representation"

    r = requests.delete(url, headers=h, timeout=20)
    if r.status_code >= 400:
        _http_error("Delete em students falhou", r)

    return r.json()


def db_list_students(search: str | None = None):
    """
    Lista alunos do workspace atual.
    Se search vier preenchido, filtra por nome (ilike).
    """
    ok, _ = _rest_ready(debug=False)
    if not ok:
        return []

    ws_id = st.session_state.get("workspace_id")
    base = f"{_sb_url()}/rest/v1/students?select=*&workspace_id=eq.{ws_id}&order=created_at.desc"

    if search:
        s = str(search).strip()
        if s:
            base += f"&name=ilike.*{s}*"

    r = requests.get(base, headers=_headers(), timeout=20)
    if r.status_code >= 400:
        _http_error("List students falhou", r)

    data = r.json()
    return data if isinstance(data, list) else []

# ==============================================================================
# 3. BLOCO VISUAL (badge / logo)
# ==============================================================================
def get_logo_base64():
    caminhos = ["omni_icone.png", "logo.png", "iconeaba.png", "omni.png", "ominisfera.png"]
    for c in caminhos:
        if os.path.exists(c):
            with open(c, "rb") as f:
                return f"data:image/png;base64,{base64.b64encode(f.read()).decode()}"
    # fallback
    return "https://cdn-icons-png.flaticon.com/512/1183/1183672.png"

src_logo_giratoria = get_logo_base64()

if IS_TEST_ENV:
    card_bg = "rgba(255, 220, 50, 0.95)"
    card_border = "rgba(200, 160, 0, 0.5)"
else:
    card_bg = "rgba(255, 255, 255, 0.85)"
    card_border = "rgba(255, 255, 255, 0.6)"

st.markdown(f"""
<style>
    .omni-badge {{
        position: fixed; top: 15px; right: 15px;
        background: {card_bg}; border: 1px solid {card_border};
        backdrop-filter: blur(8px); -webkit-backdrop-filter: blur(8px);
        padding: 4px 30px; min-width: 260px; justify-content: center;
        border-radius: 20px; box-shadow: 0 4px 15px rgba(0,0,0,0.08);
        z-index: 999990; display: flex; align-items: center; gap: 10px;
        pointer-events: none;
    }}
    .omni-text {{
        font-family: 'Nunito', sans-serif; font-weight: 800; font-size: 0.9rem;
        color: #2D3748; letter-spacing: 1px; text-transform: uppercase;
    }}
    @keyframes spin-slow {{ from {{ transform: rotate(0deg); }} to {{ transform: rotate(360deg); }} }}
    .omni-logo-spin {{ height: 26px; width: 26px; animation: spin-slow 10s linear infinite; }}
</style>
<div class="omni-badge">
    <img src="{src_logo_giratoria}" class="omni-logo-spin">
    <span class="omni-text">OMNISFERA</span>
</div>
""", unsafe_allow_html=True)


# ==============================================================================
# 4. LISTAS DE DADOS
# ==============================================================================
LISTA_SERIES = [
    "Educação Infantil (Creche)", "Educação Infantil (Pré-Escola)",
    "1º Ano (Fund. I)", "2º Ano (Fund. I)", "3º Ano (Fund. I)", "4º Ano (Fund. I)", "5º Ano (Fund. I)",
    "6º Ano (Fund. II)", "7º Ano (Fund. II)", "8º Ano (Fund. II)", "9º Ano (Fund. II)",
    "1ª Série (EM)", "2ª Série (EM)", "3ª Série (EM)", "EJA (Educação de Jovens e Adultos)"
]

LISTA_ALFABETIZACAO = [
    "Não se aplica (Educação Infantil)",
    "Pré-Silábico (Garatuja/Desenho sem letras)",
    "Pré-Silábico (Letras aleatórias sem valor sonoro)",
    "Silábico (Sem valor sonoro convencional)",
    "Silábico (Com valor sonoro vogais/consoantes)",
    "Silábico-Alfabético (Transição)",
    "Alfabético (Escrita fonética, com erros ortográficos)",
    "Ortográfico (Escrita convencional consolidada)"
]

LISTAS_BARREIRAS = {
    "Funções Cognitivas": ["Atenção Sustentada/Focada", "Memória de Trabalho (Operacional)", "Flexibilidade Mental", "Planejamento e Organização", "Velocidade de Processamento", "Abstração e Generalização"],
    "Comunicação e Linguagem": ["Linguagem Expressiva (Fala)", "Linguagem Receptiva (Compreensão)", "Pragmática (Uso social da língua)", "Processamento Auditivo", "Intenção Comunicativa"],
    "Socioemocional": ["Regulação Emocional (Autocontrole)", "Tolerância à Frustração", "Interação Social com Pares", "Autoestima e Autoimagem", "Reconhecimento de Emoções"],
    "Sensorial e Motor": ["Praxias Globais (Coordenação Grossa)", "Praxias Finas (Coordenação Fina)", "Hipersensibilidade Sensorial", "Hipossensibilidade (Busca Sensorial)", "Planejamento Motor"],
    "Acadêmico": ["Decodificação Leitora", "Compreensão Textual", "Raciocínio Lógico-Matemático", "Grafomotricidade (Escrita manual)", "Produção Textual"]
}

LISTA_POTENCIAS = ["Memória Visual", "Musicalidade/Ritmo", "Interesse em Tecnologia", "Hiperfoco Construtivo", "Liderança Natural", "Habilidades Cinestésicas (Esportes)", "Expressão Artística (Desenho)", "Cálculo Mental Rápido", "Oralidade/Vocabulário", "Criatividade/Imaginação", "Empatia/Cuidado com o outro", "Resolução de Problemas", "Curiosidade Investigativa"]

LISTA_PROFISSIONAIS = ["Psicólogo Clínico", "Neuropsicólogo", "Fonoaudiólogo", "Terapeuta Ocupacional", "Neuropediatra", "Psiquiatra Infantil", "Psicopedagogo Clínico", "Professor de Apoio (Mediador)", "Acompanhante Terapêutico (AT)", "Musicoterapeuta", "Equoterapeuta", "Oftalmologista"]

LISTA_FAMILIA = ["Mãe", "Mãe 2", "Pai", "Pai 2", "Madrasta", "Padrasto", "Avó Materna", "Avó Paterna", "Avô Materno", "Avô Paterno", "Irmãos", "Tios", "Primos", "Tutor Legal", "Abrigo Institucional"]


# ==============================================================================
# 5. ESTADO DEFAULT (RASCUNHO)
# ==============================================================================
default_state = {
    "nome": "",
    "nasc": date(2015, 1, 1),
    "serie": None,
    "turma": "",
    "diagnostico": "",
    "lista_medicamentos": [],
    "composicao_familiar_tags": [],
    "historico": "",
    "familia": "",
    "hiperfoco": "",
    "potencias": [],
    "rede_apoio": [],
    "orientacoes_especialistas": "",
    "orientacoes_por_profissional": {},
    "checklist_evidencias": {},
    "nivel_alfabetizacao": "Não se aplica (Educação Infantil)",
    "barreiras_selecionadas": {k: [] for k in LISTAS_BARREIRAS.keys()},
    "niveis_suporte": {},
    "observacoes_barreiras": {},
    "estrategias_acesso": [],
    "estrategias_ensino": [],
    "estrategias_avaliacao": [],
    "ia_sugestao": "",
    "ia_mapa_texto": "",
    "outros_acesso": "",
    "outros_ensino": "",
    "monitoramento_data": date.today(),
    "status_meta": "Não Iniciado",
    "parecer_geral": "Manter Estratégias",
    "proximos_passos_select": [],
    "status_validacao_pei": "rascunho",
    "feedback_ajuste": "",
    "status_validacao_game": "rascunho",
    "feedback_ajuste_game": "",
    "matricula": "",
    "meds_extraidas_tmp": [],
    "status_meds_extraidas": "idle",
}

if "dados" not in st.session_state:
    st.session_state.dados = default_state
else:
    for k, v in default_state.items():
        if k not in st.session_state.dados:
            st.session_state.dados[k] = v

st.session_state.setdefault("pdf_text", "")

# vínculo supabase
st.session_state.setdefault("selected_student_id", None)
st.session_state.setdefault("selected_student_name", "")


# ==============================================================================
# 6. SIDEBAR (Renderização segura)
# ==============================================================================

def render_sidebar():
    """
    Renderiza a sidebar da Omnisfera.
    Este bloco é isolado e seguro contra IndentationError.
    """

    # CSS e JS podem estar vazios sem quebrar o app
    sidebar_css = ""
    sidebar_js = ""

    # Injetar CSS (se existir)
    if sidebar_css:
        st.markdown(sidebar_css, unsafe_allow_html=True)

    # Injetar JS (se existir)
    if sidebar_js:
        st.markdown(sidebar_js, unsafe_allow_html=True)

    # Sidebar visual
    with st.sidebar:
        # Container principal
        st.markdown("<div class='sidebar-content'>", unsafe_allow_html=True)

        # Logo
        st.markdown("<div class='sidebar-logo-container'>", unsafe_allow_html=True)

        if os.path.exists("omnisfera.png"):
            st.image("omnisfera.png", use_container_width=True)
        elif os.path.exists("omni_texto.png"):
            st.image("omni_texto.png", use_container_width=True)
        else:
            st.markdown(
                """
                <div style="text-align:center; padding:16px 0;">
                    <div style="
                        font-size:1.8rem;
                        font-weight:800;
                        background:linear-gradient(135deg,#4F46E5,#7C3AED);
                        -webkit-background-clip:text;
                        -webkit-text-fill-color:transparent;
                    ">
                        OMNISFERA
                    </div>
                    <div style="font-size:.9rem; color:#64748B;">
                        Educação Inclusiva Inteligente
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

        st.markdown("</div>", unsafe_allow_html=True)

        # Separador
        st.divider()

        # Informações de sessão (opcional)
        usuario = st.session_state.get("usuario_nome")
        workspace = st.session_state.get("workspace_name")

        if usuario:
            st.caption(f"👤 {usuario}")
        if workspace:
            st.caption(f"🏫 {workspace}")

        # Rodapé
        st.markdown(
            """
            <div style="margin-top:40px; font-size:.75rem; color:#94A3B8; text-align:center;">
                Omnisfera © 2026<br>
                Educação como direito de todos
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown("</div>", unsafe_allow_html=True)

# ==============================================================================
# 7. UTILITÁRIOS
# ==============================================================================
def calcular_progresso():
    if st.session_state.dados.get('ia_sugestao'):
        return 100
    pontos = 0
    total = 7
    d = st.session_state.dados
    if d.get('nome'):
        pontos += 1
    if d.get('serie'):
        pontos += 1
    if d.get('nivel_alfabetizacao') and d.get('nivel_alfabetizacao') != 'Não se aplica (Educação Infantil)':
        pontos += 1
    if any(d.get('checklist_evidencias', {}).values()):
        pontos += 1
    if d.get('hiperfoco'):
        pontos += 1
    if any(d.get('barreiras_selecionadas', {}).values()):
        pontos += 1
    if d.get('estrategias_ensino'):
        pontos += 1
    return int((pontos / total) * 90)

def finding_logo():
    possiveis = ["360.png", "360.jpg", "logo.png", "logo.jpg", "iconeaba.png"]
    for nome in possiveis:
        if os.path.exists(nome):
            return nome
    return None

def get_base64_image(image_path):
    if not image_path or not os.path.exists(image_path):
        return ""
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

def ler_pdf(arquivo):
    try:
        reader = PdfReader(arquivo)
        texto = ""
        for i, page in enumerate(reader.pages):
            if i >= 6:
                break
            texto += (page.extract_text() or "") + "\n"
        return texto
    except:
        return ""

def render_progresso():
    p = calcular_progresso()
    icon_html = f'<img src="{src_logo_giratoria}" class="omni-logo-spin" style="width: 25px; height: 25px;">'
    bar_color = "linear-gradient(90deg, #FF6B6B 0%, #FF8E53 100%)"
    if p >= 100:
        bar_color = "linear-gradient(90deg, #00C6FF 0%, #0072FF 100%)"
    st.markdown(
        f"""<div style="width:100%; margin: 0 0 20px 0;">
              <div style="width:100%; height:3px; background:#E2E8F0; border-radius:2px; position:relative;">
                <div style="height:3px; width:{p}%; background:{bar_color}; border-radius:2px;"></div>
                <div style="position:absolute; top:-14px; left:{p}%; transform:translateX(-50%);">{icon_html}</div>
              </div>
            </div>""",
        unsafe_allow_html=True
    )
# ==============================================================================
# 7B. UTILITÁRIOS AVANÇADOS (idade, segmento, metas, radar, etc.)
# ==============================================================================

def calcular_idade(data_nasc):
    if not data_nasc:
        return ""
    hoje = date.today()
    idade = hoje.year - data_nasc.year - ((hoje.month, hoje.day) < (data_nasc.month, data_nasc.day))
    return f"{idade} anos"

def detectar_nivel_ensino(serie_str: str | None):
    if not serie_str:
        return "INDEFINIDO"
    s = serie_str.lower()
    if "infantil" in s:
        return "EI"
    if "1º ano" in s or "2º ano" in s or "3º ano" in s or "4º ano" in s or "5º ano" in s:
        return "FI"
    if "6º ano" in s or "7º ano" in s or "8º ano" in s or "9º ano" in s:
        return "FII"
    if "série" in s or "médio" in s or "eja" in s:
        return "EM"
    return "INDEFINIDO"

def get_segmento_info_visual(serie: str | None):
    nivel = detectar_nivel_ensino(serie or "")
    if nivel == "EI":
        return "Educação Infantil", "#4299e1", "Foco: Campos de Experiência (BNCC)."
    if nivel == "FI":
        return "Anos Iniciais (Fund. I)", "#48bb78", "Foco: Alfabetização e BNCC."
    if nivel == "FII":
        return "Anos Finais (Fund. II)", "#ed8936", "Foco: Autonomia e Identidade."
    if nivel == "EM":
        return "Ensino Médio / EJA", "#9f7aea", "Foco: Projeto de Vida."
    return "Selecione a Série", "grey", "Aguardando seleção..."

def get_hiperfoco_emoji(texto: str | None):
    if not texto:
        return "🚀"
    t = texto.lower()
    if "jogo" in t or "game" in t or "minecraft" in t or "roblox" in t:
        return "🎮"
    if "dino" in t:
        return "🦖"
    if "fute" in t or "bola" in t:
        return "⚽"
    if "desenho" in t or "arte" in t:
        return "🎨"
    if "músic" in t or "music" in t:
        return "🎵"
    if "anim" in t or "gato" in t or "cachorro" in t:
        return "🐾"
    if "carro" in t:
        return "🏎️"
    if "espaço" in t or "espaco" in t:
        return "🪐"
    return "🚀"

def calcular_complexidade_pei(dados: dict):
    n_bar = sum(len(v) for v in (dados.get("barreiras_selecionadas") or {}).values())
    n_suporte_alto = sum(
        1 for v in (dados.get("niveis_suporte") or {}).values()
        if v in ["Substancial", "Muito Substancial"]
    )
    recursos = 0
    if dados.get("rede_apoio"):
        recursos += 3
    if dados.get("lista_medicamentos"):
        recursos += 2
    saldo = (n_bar + n_suporte_alto) - recursos
    if saldo <= 2:
        return "FLUIDA", "#F0FFF4", "#276749"
    if saldo <= 7:
        return "ATENÇÃO", "#FFFFF0", "#D69E2E"
    return "CRÍTICA", "#FFF5F5", "#C53030"

def extrair_tag_ia(texto: str, tag: str):
    if not texto:
        return ""
    padrao = fr"\[{tag}\](.*?)(\[|$)"
    match = re.search(padrao, texto, re.DOTALL)
    return match.group(1).strip() if match else ""

def extrair_metas_estruturadas(texto: str):
    bloco = extrair_tag_ia(texto or "", "METAS_SMART")
    metas = {"Curto": "Definir...", "Medio": "Definir...", "Longo": "Definir..."}
    if bloco:
        linhas = bloco.split("\n")
        for l in linhas:
            l_clean = re.sub(r"^[\-\*]+", "", l).strip()
            if not l_clean:
                continue
            if "Curto" in l or "2 meses" in l:
                metas["Curto"] = l_clean.split(":")[-1].strip()
            elif "Médio" in l or "Semestre" in l or "Medio" in l:
                metas["Medio"] = l_clean.split(":")[-1].strip()
            elif "Longo" in l or "Ano" in l:
                metas["Longo"] = l_clean.split(":")[-1].strip()
    return metas

def get_pro_icon(nome_profissional: str | None):
    p = (nome_profissional or "").lower()
    if "psic" in p:
        return "🧠"
    if "fono" in p:
        return "🗣️"
    if "terapeuta" in p or "equo" in p or "musico" in p:
        return "🧩"
    if "neuro" in p or "psiq" in p or "medico" in p:
        return "🩺"
    return "👨‍⚕️"

def inferir_componentes_impactados(dados: dict):
    barreiras = dados.get("barreiras_selecionadas", {}) or {}
    serie = (dados.get("serie") or "")
    nivel = detectar_nivel_ensino(serie)
    impactados = set()

    # Leitura
    if barreiras.get("Acadêmico") and any("Leitora" in b for b in barreiras["Acadêmico"]):
        impactados.add("Língua Portuguesa")
        impactados.add("História/Sociologia/Filosofia" if nivel == "EM" else "História/Geografia")

    # Matemática
    if barreiras.get("Acadêmico") and any("Matemático" in b for b in barreiras["Acadêmico"]):
        impactados.add("Matemática")
        if nivel == "EM":
            impactados.add("Física/Química")
        elif nivel == "FII":
            impactados.add("Ciências")

    # Cognitivas (transversal)
    if barreiras.get("Funções Cognitivas"):
        impactados.add("Transversal (Todas as áreas)")

    # Motor fino
    if barreiras.get("Sensorial e Motor") and any("Fina" in b for b in barreiras["Sensorial e Motor"]):
        impactados.add("Arte")
        impactados.add("Geometria")

    if not impactados and dados.get("diagnostico"):
        return ["Análise Geral (Baseada no Diagnóstico)"]

    return list(impactados) if impactados else ["Nenhum componente específico detectado automaticamente"]


# ==============================================================================
# 7C. PDF / DOCX (Exportação)
# ==============================================================================

def limpar_texto_pdf(texto: str):
    if not texto:
        return ""
    t = texto.replace("**", "").replace("__", "").replace("#", "").replace("•", "-")
    t = t.replace("“", '"').replace("”", '"').replace("‘", "'").replace("’", "'")
    t = t.replace("–", "-").replace("—", "-")
    return t.encode("latin-1", "replace").decode("latin-1")

class PDF_Classic(FPDF):
    def header(self):
        self.set_fill_color(248, 248, 248)
        self.rect(0, 0, 210, 40, "F")
        logo = finding_logo()
        x_offset = 40 if logo else 12
        if logo:
            self.image(logo, 10, 8, 25)
        self.set_xy(x_offset, 12)
        self.set_font("Arial", "B", 14)
        self.set_text_color(50, 50, 50)
        self.cell(0, 8, "PEI - PLANO DE ENSINO INDIVIDUALIZADO", 0, 1, "L")
        self.set_xy(x_offset, 19)
        self.set_font("Arial", "", 9)
        self.set_text_color(100, 100, 100)
        self.cell(0, 5, "Documento de Planejamento e Flexibilização Curricular", 0, 1, "L")
        self.ln(15)

    def footer(self):
        self.set_y(-15)
        self.set_font("Arial", "I", 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, f"Página {self.page_no()} | Gerado via Omnisfera", 0, 0, "C")

    def section_title(self, label):
        self.ln(6)
        self.set_fill_color(230, 230, 230)
        self.rect(10, self.get_y(), 190, 8, "F")
        self.set_font("ZapfDingbats", "", 10)
        self.set_text_color(80, 80, 80)
        self.set_xy(12, self.get_y() + 1)
        self.cell(5, 6, "o", 0, 0)
        self.set_font("Arial", "B", 11)
        self.set_text_color(50, 50, 50)
        self.cell(0, 6, label.upper(), 0, 1, "L")
        self.ln(4)

    def add_flat_icon_item(self, texto, bullet_type="check"):
        self.set_font("ZapfDingbats", "", 10)
        self.set_text_color(80, 80, 80)
        char = "3" if bullet_type == "check" else "l"
        self.cell(6, 5, char, 0, 0)
        self.set_font("Arial", "", 10)
        self.set_text_color(0)
        self.multi_cell(0, 5, texto)
        self.ln(1)

class PDF_Simple_Text(FPDF):
    def header(self):
        self.set_font("Arial", "B", 16)
        self.set_text_color(50)
        self.cell(0, 10, "ROTEIRO DE MISSÃO", 0, 1, "C")
        self.set_draw_color(150)
        self.line(10, 25, 200, 25)
        self.ln(10)

def gerar_pdf_final(dados: dict):
    pdf = PDF_Classic()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=20)

    pdf.section_title("Identificação e Contexto")
    pdf.set_font("Arial", "B", 10)
    pdf.cell(35, 6, "Estudante:", 0, 0)
    pdf.set_font("Arial", "", 10)
    pdf.cell(0, 6, dados.get("nome", ""), 0, 1)

    pdf.set_font("Arial", "B", 10)
    pdf.cell(35, 6, "Série/Turma:", 0, 0)
    pdf.set_font("Arial", "", 10)
    pdf.cell(0, 6, f"{dados.get('serie','')} - {dados.get('turma','')}", 0, 1)

    pdf.set_font("Arial", "B", 10)
    pdf.cell(35, 6, "Diagnóstico:", 0, 0)
    pdf.set_font("Arial", "", 10)
    pdf.multi_cell(0, 6, dados.get("diagnostico", ""))
    pdf.ln(2)

    if any((dados.get("barreiras_selecionadas") or {}).values()):
        pdf.section_title("Plano de Suporte (Barreiras x Nível)")
        for area, itens in (dados.get("barreiras_selecionadas") or {}).items():
            if itens:
                pdf.set_font("Arial", "B", 10)
                pdf.cell(0, 8, limpar_texto_pdf(area), 0, 1)
                for item in itens:
                    nivel = (dados.get("niveis_suporte") or {}).get(f"{area}_{item}", "Monitorado")
                    pdf.add_flat_icon_item(limpar_texto_pdf(f"{item} (Nível: {nivel})"), "check")

    if dados.get("ia_sugestao"):
        pdf.add_page()
        pdf.section_title("Planejamento Pedagógico Detalhado")
        texto_limpo = limpar_texto_pdf(dados["ia_sugestao"])
        texto_limpo = re.sub(r"\[.*?\]", "", texto_limpo)

        for linha in texto_limpo.split("\n"):
            l = linha.strip()
            if not l:
                continue
            if l.startswith("###") or l.startswith("##"):
                pdf.ln(5)
                pdf.set_font("Arial", "B", 12)
                pdf.set_text_color(0, 51, 102)
                pdf.cell(0, 8, l.replace("#", "").strip(), 0, 1, "L")
                pdf.set_font("Arial", "", 10)
                pdf.set_text_color(0, 0, 0)
            elif l.startswith("-") or l.startswith("*"):
                pdf.add_flat_icon_item(l.replace("-", "").replace("*", "").strip(), "dot")
            else:
                pdf.multi_cell(0, 6, l)

    return pdf.output(dest="S").encode("latin-1", "replace")

def gerar_pdf_tabuleiro_simples(texto: str):
    pdf = PDF_Simple_Text()
    pdf.add_page()
    pdf.set_font("Arial", size=11)
    for linha in limpar_texto_pdf(texto).split("\n"):
        l = linha.strip()
        if not l:
            continue
        if l.isupper() or "**" in linha:
            pdf.ln(4)
            pdf.set_font("Arial", "B", 11)
            pdf.set_fill_color(240, 240, 240)
            pdf.cell(0, 8, l.replace("**", ""), 0, 1, "L", fill=True)
            pdf.set_font("Arial", "", 11)
        else:
            pdf.multi_cell(0, 6, l)
    return pdf.output(dest="S").encode("latin-1", "ignore")

def gerar_docx_final(dados: dict):
    doc = Document()
    doc.add_heading("PEI - " + (dados.get("nome") or "Sem Nome"), 0)
    if dados.get("ia_sugestao"):
        doc.add_paragraph(re.sub(r"\[.*?\]", "", dados["ia_sugestao"]))
    b = BytesIO()
    doc.save(b)
    b.seek(0)
    return b


# ==============================================================================
# 7D. IA (Extração PDF + Consultoria + Gamificação)
# ==============================================================================

def extrair_dados_pdf_ia(api_key: str, texto_pdf: str):
    if not api_key:
        return None, "Configure a Chave API OpenAI."
    try:
        client = OpenAI(api_key=api_key)
        prompt = (
            "Analise este laudo médico/escolar. Extraia: 1) Diagnóstico; 2) Medicamentos. "
            'Responda em JSON no formato: { "diagnostico": "...", "medicamentos": [ {"nome": "...", "posologia": "..."} ] }. '
            f"Texto: {texto_pdf[:4000]}"
        )
        res = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
        )
        return json.loads(res.choices[0].message.content), None
    except Exception as e:
        return None, str(e)

def consultar_gpt_pedagogico(api_key: str, dados: dict, contexto_pdf: str = "", modo_pratico: bool = False, feedback_usuario: str = ""):
    if not api_key:
        return None, "⚠️ Configure a Chave API OpenAI."
    try:
        client = OpenAI(api_key=api_key)

        evid = "\n".join([f"- {k.replace('?', '')}" for k, v in (dados.get("checklist_evidencias") or {}).items() if v])
        meds_info = "\n".join(
            [f"- {m.get('nome','')} ({m.get('posologia','')})." for m in (dados.get("lista_medicamentos") or [])]
        ) if dados.get("lista_medicamentos") else "Nenhuma medicação informada."

        hiperfoco_txt = f"HIPERFOCO DO ALUNO: {dados.get('hiperfoco','')}" if dados.get("hiperfoco") else "Hiperfoco: Não identificado."
        serie = dados.get("serie") or ""
        nivel_ensino = detectar_nivel_ensino(serie)
        alfabetizacao = dados.get("nivel_alfabetizacao", "Não Avaliado")

        prompt_identidade = f"""
[PERFIL_NARRATIVO]
Inicie com "👤 QUEM É O ESTUDANTE?". Crie um parágrafo humanizado. {hiperfoco_txt}.
Use o hiperfoco para conectar com a aprendizagem.
[/PERFIL_NARRATIVO]
""".strip()

        prompt_diagnostico = """
### 1. 🏥 DIAGNÓSTICO E IMPACTO (FUNDAMENTAL):
- Cite o Diagnóstico (e o CID se disponível).
- Descreva os impactos diretos na aprendizagem.
- Liste cuidados/pontos de atenção.
""".strip()

        prompt_literacia = ""
        if "Alfabético" not in alfabetizacao and alfabetizacao != "Não se aplica (Educação Infantil)":
            prompt_literacia = f"""[ATENÇÃO CRÍTICA: ALFABETIZAÇÃO] Fase: {alfabetizacao}. Inclua 2 ações de consciência fonológica.[/ATENÇÃO CRÍTICA]"""

        prompt_hub = """
### 6. 🧩 CHECKLIST DE ADAPTAÇÃO E ACESSIBILIDADE:
**A. Mediação (Triângulo de Ouro):**
1) Instruções passo a passo
2) Fragmentação de tarefas
3) Scaffolding

**B. Acessibilidade:**
4) Inferências/figuras de linguagem
5) Descrição de imagens (alt text)
6) Adaptação visual (fonte/espaçamento)
7) Adequação de desafio
""".strip()

        prompt_componentes = ""
        if nivel_ensino != "EI":
            prompt_componentes = f"""
### 4. ⚠️ COMPONENTES CURRICULARES DE ATENÇÃO:
Com base no diagnóstico ({dados.get('diagnostico','')}) e nas barreiras citadas, identifique componentes que exigirão maior flexibilização.
- Liste componentes
- Para cada um, explique o motivo técnico
""".strip()

        prompt_metas = """
[METAS_SMART]
- Meta de Curto Prazo (2 meses): [Descreva a meta]
- Meta de Médio Prazo (1 semestre): [Descreva a meta]
- Meta de Longo Prazo (1 ano): [Descreva a meta]
[/METAS_SMART]
""".strip()

        if nivel_ensino == "EI":
            perfil_ia = "Especialista em EDUCAÇÃO INFANTIL e BNCC."
            estrutura_req = f"""
{prompt_identidade}
{prompt_diagnostico}

### 2. 🌟 AVALIAÇÃO DE REPERTÓRIO:
[CAMPOS_EXPERIENCIA_PRIORITARIOS] Destaque 2 ou 3 Campos BNCC. [/CAMPOS_EXPERIENCIA_PRIORITARIOS]

### 3. 🚀 ESTRATÉGIAS DE INTERVENÇÃO:
(Estratégias de acolhimento, rotina e adaptação sensorial).

{prompt_metas}

### 5. ⚠️ PONTOS DE ATENÇÃO FARMACOLÓGICA:
[ANALISE_FARMA] Se houver medicação, cite efeitos colaterais para atenção pedagógica. [/ANALISE_FARMA]

{prompt_hub}
""".strip()
        else:
            perfil_ia = "Especialista em Inclusão Escolar e BNCC."
            instrucao_bncc = "[MAPEAMENTO_BNCC] Separe por Componente Curricular. Inclua código alfanumérico (ex: EF01LP02). [/MAPEAMENTO_BNCC]"
            instrucao_bloom = "[TAXONOMIA_BLOOM] Explique a categoria cognitiva escolhida. [/TAXONOMIA_BLOOM]"
            estrutura_req = f"""
{prompt_identidade}
{prompt_diagnostico}

### 2. 🌟 AVALIAÇÃO DE REPERTÓRIO:
- Defasagens (anos anteriores)
- Foco do ano atual
{instrucao_bncc}
{instrucao_bloom}

### 3. 🚀 ESTRATÉGIAS DE INTERVENÇÃO:
(Adaptações curriculares e de acesso).
{prompt_literacia}

{prompt_componentes}

{prompt_metas}

### 5. ⚠️ PONTOS DE ATENÇÃO FARMACOLÓGICA:
[ANALISE_FARMA] Se houver medicação, cite efeitos colaterais para atenção pedagógica. [/ANALISE_FARMA]

{prompt_hub}
""".strip()

        prompt_feedback = f"AJUSTE SOLICITADO: {feedback_usuario}" if feedback_usuario else ""
        prompt_formatacao = "IMPORTANTE: Use Markdown simples. Use títulos H3 (###). Evite tabelas."

        prompt_sys = f"""{perfil_ia}
MISSÃO: Criar PEI Técnico Oficial.
ESTRUTURA OBRIGATÓRIA:
{estrutura_req}

{prompt_feedback}
{prompt_formatacao}
""".strip()

        if modo_pratico:
            prompt_sys = f"""{perfil_ia}
GUIA PRÁTICO PARA SALA DE AULA.
{prompt_feedback}

{prompt_hub}
""".strip()

        prompt_user = (
            f"ALUNO: {dados.get('nome','')} | SÉRIE: {serie} | HISTÓRICO: {dados.get('historico','')} | "
            f"DIAGNÓSTICO: {dados.get('diagnostico','')} | MEDS: {meds_info} | "
            f"EVIDÊNCIAS: {evid} | LAUDO: {(contexto_pdf or '')[:3000]}"
        )

        res = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "system", "content": prompt_sys}, {"role": "user", "content": prompt_user}],
        )
        return res.choices[0].message.content, None

    except Exception as e:
        return None, str(e)

def gerar_roteiro_gamificado(api_key: str, dados: dict, pei_tecnico: str, feedback_game: str = ""):
    if not api_key:
        return None, "Configure a chave OpenAI."
    try:
        client = OpenAI(api_key=api_key)
        serie = dados.get("serie") or ""
        nivel_ensino = detectar_nivel_ensino(serie)
        hiperfoco = dados.get("hiperfoco") or "brincadeiras"
        nome_curto = (dados.get("nome","").split() or ["Estudante"])[0]

        contexto_seguro = (
            f"ALUNO: {nome_curto} | HIPERFOCO: {hiperfoco} | "
            f"PONTOS FORTES: {', '.join(dados.get('potencias',[]))}"
        )

        prompt_feedback = f"AJUSTE: {feedback_game}" if feedback_game else ""

        if nivel_ensino == "EI":
            prompt_sys = "Crie uma história visual (4-5 anos) com emojis. Estrutura: começo, desafio, ajuda, conquista, rotina."
        elif nivel_ensino == "FI":
            prompt_sys = "Crie um quadro de missões RPG (6-10 anos). Estrutura: mapa, missões, recompensas, superpoder."
        else:
            prompt_sys = "Crie uma ficha RPG (adolescente). Estrutura: quest, skills, buffs, checklists e metas."

        full_sys = f"{prompt_sys}\n{prompt_feedback}"
        res = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "system", "content": full_sys}, {"role": "user", "content": contexto_seguro}],
        )
        return res.choices[0].message.content, None
    except Exception as e:
        return None, str(e)


# ==============================================================================
# 7E. AÇÕES AUXILIARES (Reset)
# ==============================================================================
def limpar_formulario():
    # recria um "rascunho limpo" preservando a estrutura do dicionário
    st.session_state.dados = {
        'nome': '',
        'nasc': date(2015, 1, 1),
        'serie': None,
        'turma': '',
        'diagnostico': '',
        'lista_medicamentos': [],
        'composicao_familiar_tags': [],
        'historico': '',
        'familia': '',
        'hiperfoco': '',
        'potencias': [],
        'rede_apoio': [],
        'orientacoes_especialistas': '',
        'checklist_evidencias': {},
        'nivel_alfabetizacao': 'Não se aplica (Educação Infantil)',
        'barreiras_selecionadas': {k: [] for k in LISTAS_BARREIRAS.keys()},
        'niveis_suporte': {},
        'estrategias_acesso': [],
        'estrategias_ensino': [],
        'estrategias_avaliacao': [],
        'ia_sugestao': '',
        'ia_mapa_texto': '',
        'outros_acesso': '',
        'outros_ensino': '',
        'monitoramento_data': date.today(),
        'status_meta': 'Não Iniciado',
        'parecer_geral': 'Manter Estratégias',
        'proximos_passos_select': [],
        'status_validacao_pei': 'rascunho',
        'feedback_ajuste': '',
        'status_validacao_game': 'rascunho',
        'feedback_ajuste_game': ''
    }
    st.session_state.pdf_text = ""


# ==============================================================================
# 8. ESTILO VISUAL
# ==============================================================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800&display=swap');
    html, body, [class*="css"] { font-family: 'Nunito', sans-serif; color: #2D3748; background-color: #F7FAFC; }
    .block-container { padding-top: 1.5rem !important; padding-bottom: 5rem !important; }
    div[data-baseweb="tab-border"], div[data-baseweb="tab-highlight"] { display: none !important; }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px; display: flex; flex-wrap: wrap !important;
        white-space: normal !important; overflow-x: visible !important;
        padding: 10px 5px; width: 100%;
    }
    .stTabs [data-baseweb="tab"] {
        height: 38px; border-radius: 20px !important;
        background-color: #FFFFFF; border: 1px solid #E2E8F0;
        color: #718096; font-weight: 700; font-size: 0.8rem;
        padding: 0 20px; box-shadow: 0 1px 2px rgba(0,0,0,0.03);
        text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 5px;
    }
    .stTabs [data-baseweb="tab"]:hover { border-color: #CBD5E0; color: #4A5568; background-color: #EDF2F7; }
    .stTabs [aria-selected="true"] {
        background-color: transparent !important; color: #3182CE !important;
        border: 1px solid #3182CE !important; font-weight: 800;
        box-shadow: 0 0 12px rgba(49, 130, 206, 0.4), inset 0 0 5px rgba(49, 130, 206, 0.1) !important;
    }
    .header-unified { background-color: white; padding: 20px 40px; border-radius: 16px; border: 1px solid #E2E8F0; box-shadow: 0 2px 10px rgba(0,0,0,0.02); margin-bottom: 20px; display: flex; align-items: center; gap: 20px; }
    .header-subtitle { font-size: 1.2rem; color: #718096; font-weight: 600; border-left: 2px solid #E2E8F0; padding-left: 20px; line-height: 1.2; }
    .stTextInput input, .stTextArea textarea, .stSelectbox div[data-baseweb="select"], .stMultiSelect div[data-baseweb="select"] { border-radius: 8px !important; border-color: #E2E8F0 !important; }
    div[data-testid="column"] .stButton button { border-radius: 8px !important; font-weight: 700 !important; height: 45px !important; background-color: #0F52BA !important; color: white !important; border: none !important; }
    div[data-testid="column"] .stButton button:hover { background-color: #0A3D8F !important; }
    .footer-signature { text-align:center; opacity:0.55; font-size:0.75rem; padding:30px 0 10px 0; }
</style>
<link href="https://cdn.jsdelivr.net/npm/remixicon@4.1.0/fonts/remixicon.css" rel="stylesheet">
""", unsafe_allow_html=True)


# ==============================================================================
# 9. SIDEBAR — Sessão + OpenAI + Sincronização + Salvar/Carregar
#    (sem duplicar navegação / sem loops / com guard supabase)
# ==============================================================================

# CSS da sidebar (o mesmo código acima)
sidebar_css = """
<style>
... todo o CSS da sidebar aqui ...
</style>
"""

# JavaScript da sidebar
sidebar_js = """
<script>
... todo o JavaScript da sidebar aqui ...
</script>
"""

def render_sidebar():
    """Função principal para renderizar a sidebar em qualquer página"""
    
    # Injetar CSS
    st.markdown(sidebar_css, unsafe_allow_html=True)
    
    with st.sidebar:
        # Container principal
        st.markdown('<div class="sidebar-content">', unsafe_allow_html=True)
        
        # 1. Logo centralizada
        st.markdown('<div class="sidebar-logo-container">', unsafe_allow_html=True)
        
        if os.path.exists("omnisfera.png"):
            st.image("omnisfera.png", use_column_width=True)
        elif os.path.exists("omni_texto.png"):
            st.image("omni_texto.png", use_column_width=True)
        else:
            st.markdown("""
            <div style="text-align: center; width: 100%;">
                <div style="
                    font-size: 2rem; 
                    font-weight: 800; 
                    background: linear-gradient(135deg, #4F46E5 0%, #7C3AED 100%); 
                    -webkit-background-clip: text; 
                    -webkit-text-fill-color: transparent;
                    margin-bottom: 10px;
                ">
                    OMNISFERA
                </div>
                <div style="font-size: 0.9rem; color: #64748B;">
                    Plataforma de Inclusão
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # 2. Informações do usuário
        if st.session_state.get("autenticado"):
            nome_user = st.session_state.get('usuario_nome', 'Visitante')
            workspace = st.session_state.get("workspace_name") or st.session_state.get("workspace_id", "ESCOLA")[:8]
            
            iniciais = "".join([n[0].upper() for n in nome_user.split()[:2]])
            
            st.markdown(f'''
            <div class="user-info-container">
                <div class="user-avatar">{iniciais}</div>
                <div class="user-name">{nome_user.split()[0]}</div>
                <div class="user-workspace">{workspace}</div>
            </div>
            ''', unsafe_allow_html=True)
        
        # 3. Menu de navegação
        st.markdown("""
        <div class="sidebar-nav-section">
            <div class="sidebar-nav-title">
                <i class="ri-compass-3-line"></i> MENU PRINCIPAL
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Botões de navegação
        nav_items = [
            {"label": "👥 Alunos", "page": "pages/Alunos.py", "icon": "ri-team-line", "class": "sidebar-btn-alunos"},
            {"label": "📘 PEI 360°", "page": "pages/1_PEI.py", "icon": "ri-book-open-line", "class": "sidebar-btn-pei"},
            {"label": "🧩 PAEE & T.A.", "page": "pages/2_PAE.py", "icon": "ri-puzzle-line", "class": "sidebar-btn-paee"},
            {"label": "🚀 Hub de Inclusão", "page": "pages/3_Hub_Inclusao.py", "icon": "ri-rocket-line", "class": "sidebar-btn-hub"},
            {"label": "📓 Diário de Bordo", "page": "pages/4_Diario_de_Bordo.py", "icon": "ri-notebook-line", "class": "sidebar-btn-diario"},
            {"label": "📊 Monitoramento", "page": "pages/5_Monitoramento_Avaliacao.py", "icon": "ri-bar-chart-line", "class": "sidebar-btn-dados"},
        ]
        
        for item in nav_items:
            button_html = f'''
            <div class="sidebar-nav-button {item['class']}" data-page="{item['page']}">
                <i class="{item['icon']}"></i>
                <span>{item['label']}</span>
            </div>
            '''
            st.markdown(button_html, unsafe_allow_html=True)
        
        # Espaçador
        st.markdown('<div class="sidebar-spacer"></div>', unsafe_allow_html=True)
        
        # Botão de sair
        st.markdown('<div class="sidebar-logout-container">', unsafe_allow_html=True)
        
        if st.button("🚪 Sair do Sistema", 
                    use_container_width=True,
                    type="secondary",
                    key="sidebar_logout"):
            st.session_state.autenticado = False
            st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Versão
        st.markdown(f"""
        <div style="
            text-align: center; 
            color: #94A3B8; 
            font-size: 0.7rem;
            margin-top: 20px;
            padding: 10px;
        ">
            Omnisfera v2.1 • {datetime.now().strftime("%d/%m/%Y")}
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # JavaScript
        st.markdown(sidebar_js, unsafe_allow_html=True)
        
# ==============================================================================
# 10. HEADER + ABAS
# ==============================================================================
logo_path = finding_logo()
b64_logo = get_base64_image(logo_path)
mime = "image/png"
img_html = f'<img src="data:{mime};base64,{b64_logo}" style="height: 110px;">' if logo_path else ""

st.markdown(
    f"""<div class="header-unified">{img_html}<div class="header-subtitle">Planejamento Educacional Inclusivo Inteligente</div></div>""",
    unsafe_allow_html=True
)

abas = [
    "INÍCIO", "ESTUDANTE", "EVIDÊNCIAS", "REDE DE APOIO", "MAPEAMENTO",
    "PLANO DE AÇÃO", "MONITORAMENTO", "CONSULTORIA IA", "DASHBOARD & DOCS", "JORNADA GAMIFICADA"
]
tab0, tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab_mapa = st.tabs(abas)


# ==============================================================================
# 11. ABA INÍCIO — CENTRAL (Gestão de Alunos + Backups)
# ==============================================================================
with tab0:
    st.markdown("### 🏛️ Central de Fundamentos e Gestão")
    st.caption("Aqui você gerencia alunos (backup local e nuvem/Supabase) e acessa fundamentos do PEI.")

    # -------------------------
    # Helpers locais (somente UI)
    # -------------------------
    def _coerce_dates_in_payload(d: dict):
        """Converte campos de data salvos como string de volta para date (sem depender de Supabase)."""
        if not isinstance(d, dict):
            return d
        for k in ["nasc", "monitoramento_data"]:
            try:
                if k in d and isinstance(d[k], str) and d[k]:
                    d[k] = date.fromisoformat(d[k])
            except Exception:
                pass
        return d

    def _cloud_ready():
        """
        Nuvem só deve aparecer quando:
        - sb (cliente supabase) está OK
        - OWNER_ID e ws_id existem
        Observação: se seu projeto usa JWT/user_id, isso normalmente já chega pela Home/Login.
        """
        try:
            return (sb is not None) and bool(OWNER_ID) and bool(ws_id)
        except Exception:
            return False

    # -------------------------
    # LAYOUT 2 COLUNAS
    # -------------------------
    col_left, col_right = st.columns([1.15, 0.85])

    # =========================
    # ESQUERDA: Fundamentos
    # =========================
    with col_left:
        with st.container(border=True):
            st.markdown("#### 📚 Fundamentos do PEI")
            st.markdown(
                """
- O **PEI** organiza o planejamento individualizado com foco em **barreiras** e **apoios**.
- A lógica é **equidade**: ajustar **acesso, ensino e avaliação**, sem baixar expectativas.
- Base: **LBI (Lei 13.146/2015)**, LDB e diretrizes de Educação Especial na Perspectiva Inclusiva.
                """
            )

        with st.container(border=True):
            st.markdown("#### 🧭 Como usar a Omnisfera")
            st.markdown(
                """
1) **Estudante**: identificação + contexto + laudo (opcional)  
2) **Evidências**: o que foi observado e como aparece na rotina  
3) **Mapeamento**: barreiras + nível de apoio + potências  
4) **Plano de Ação**: acesso/ensino/avaliação  
5) **Consultoria IA**: gerar o documento técnico (validação do educador)  
6) **Dashboard**: KPIs + exportações + sincronização  
                """
            )

    # =========================
    # DIREITA: Gestão de alunos
    # =========================
    with col_right:
        st.markdown("#### 👤 Gestão de Alunos")

        # Status vínculo
        student_id = st.session_state.get("selected_student_id")
        if student_id:
            st.success("✅ Aluno vinculado ao Supabase (nuvem)")
            st.caption(f"student_id: {student_id[:8]}...")
        else:
            st.warning("📝 Modo rascunho (sem vínculo na nuvem)")

        # ------------------------------------------------------------------
        # (1) BACKUP LOCAL: upload JSON NÃO aplica sozinho (evita loop)
        # ------------------------------------------------------------------
        with st.container(border=True):
            st.markdown("##### 1) Carregar Backup Local (.JSON)")
            st.caption("✅ Não comunica com Supabase. Envie o arquivo e clique em **Carregar no formulário**.")

            # estados do fluxo local (cache em memória)
            if "local_json_pending" not in st.session_state:
                st.session_state["local_json_pending"] = None
            if "local_json_name" not in st.session_state:
                st.session_state["local_json_name"] = ""

            up_json = st.file_uploader(
                "Envie um arquivo .json",
                type="json",
                key="inicio_uploader_json",
            )

            # 1) Ao enviar: só guardar em memória (não aplicar)
            if up_json is not None:
                try:
                    payload = json.load(up_json)
                    payload = _coerce_dates_in_payload(payload)

                    st.session_state["local_json_pending"] = payload
                    st.session_state["local_json_name"] = getattr(up_json, "name", "") or "backup.json"

                    st.success(f"Arquivo pronto ✅ ({st.session_state['local_json_name']})")
                    st.caption("Agora clique no botão abaixo para aplicar os dados no formulário.")
                except Exception as e:
                    st.session_state["local_json_pending"] = None
                    st.session_state["local_json_name"] = ""
                    st.error(f"Erro ao ler JSON: {e}")

            pending = st.session_state.get("local_json_pending")

            # 2) Prévia (opcional)
            if isinstance(pending, dict) and pending:
                with st.expander("👀 Prévia do backup", expanded=False):
                    st.write({
                        "nome": pending.get("nome"),
                        "serie": pending.get("serie"),
                        "turma": pending.get("turma"),
                        "diagnostico": pending.get("diagnostico"),
                        "tem_ia_sugestao": bool(pending.get("ia_sugestao")),
                    })

            # 3) Botões
            b1, b2 = st.columns(2)

            with b1:
                if st.button(
                    "📥 Carregar no formulário",
                    type="primary",
                    use_container_width=True,
                    disabled=not isinstance(pending, dict),
                    key="inicio_btn_aplicar_json_local",
                ):
                    # aplica no estado do formulário
                    if "dados" in st.session_state and isinstance(st.session_state.dados, dict):
                        st.session_state.dados.update(pending)
                    else:
                        st.session_state.dados = pending

                    # JSON local NÃO cria vínculo com nuvem
                    st.session_state["selected_student_id"] = None
                    st.session_state["selected_student_name"] = ""

                    # limpa pendência pra não reaplicar
                    st.session_state["local_json_pending"] = None
                    st.session_state["local_json_name"] = ""

                    st.success("Backup aplicado ao formulário ✅")
                    st.toast("Dados aplicados.", icon="✅")
                    st.rerun()

            with b2:
                if st.button(
                    "🧹 Limpar pendência",
                    use_container_width=True,
                    key="inicio_btn_limpar_json_local",
                ):
                    st.session_state["local_json_pending"] = None
                    st.session_state["local_json_name"] = ""
                    st.rerun()

        # ------------------------------------------------------------------
        # (2) (Opcional) OUTROS CONTROLES LOCAIS AQUI
        # ------------------------------------------------------------------

        # ------------------------------------------------------------------
        # (3) SINCRONIZAR: criar aluno na nuvem (somente quando você quiser)
        # ------------------------------------------------------------------
        with st.container(border=True):
            st.markdown("##### 🔗 Sincronizar aluno (criar e vincular na nuvem)")
            st.caption("Cria o aluno na tabela **students** e libera salvar/carregar PEI na nuvem.")

            if not _cloud_ready():
                st.info("Nuvem indisponível: faça login e valide workspace.")
            else:
                if st.session_state.get("selected_student_id"):
                    st.success("Este aluno já está sincronizado ✅")
                else:
                    btn_sync = st.button(
                        "🔗 Sincronizar agora",
                        type="primary",
                        use_container_width=True,
                        key="inicio_btn_sync_nuvem",
                    )
                    if btn_sync:
                        if not st.session_state.dados.get("nome"):
                            st.warning("Preencha o NOME do estudante na aba Estudante antes de sincronizar.")
                        elif not st.session_state.dados.get("serie"):
                            st.warning("Selecione a SÉRIE/Ano na aba Estudante antes de sincronizar.")
                        else:
                            try:
                                created = db_create_student({
                                    "name": st.session_state.dados.get("nome"),
                                    "birth_date": (
                                        st.session_state.dados.get("nasc").isoformat()
                                        if hasattr(st.session_state.dados.get("nasc"), "isoformat")
                                        else None
                                    ),
                                    "grade": st.session_state.dados.get("serie"),
                                    "class_group": st.session_state.dados.get("turma") or None,
                                    "diagnosis": st.session_state.dados.get("diagnostico") or None,
                                })
                                if created and created.get("id"):
                                    st.session_state["selected_student_id"] = created["id"]
                                    st.session_state["selected_student_name"] = created.get("name") or ""
                                    st.success("Sincronizado ✅ Agora você pode salvar/carregar PEI na nuvem.")
                                    st.rerun()
                                else:
                                    st.error("Falha ao criar aluno. Verifique RLS/policies no Supabase.")
                            except Exception as e:
                                st.error(f"Erro ao sincronizar: {e}")
# ==============================================================================
# 12. ABA ESTUDANTE
# ==============================================================================
  
with tab1:
    render_progresso()
    st.markdown("### <i class='ri-user-smile-line'></i> Dossiê do Estudante", unsafe_allow_html=True)

    # Garantias (caso algo não tenha entrado no default_state)
    st.session_state.dados.setdefault("matricula", "")
    st.session_state.dados.setdefault("meds_extraidas_tmp", [])
    st.session_state.dados.setdefault("status_meds_extraidas", "idle")

    # =========================
    # Funções de apoio da aba
    # =========================
    def detectar_segmento(serie_str: str) -> str:
        """Retorna: EI | EFI | EFII | EM"""
        if not serie_str:
            return "INDEFINIDO"
        s = serie_str.lower()
        if "infantil" in s:
            return "EI"
        if "1º ano" in s or "2º ano" in s or "3º ano" in s or "4º ano" in s or "5º ano" in s:
            return "EFI"
        if "6º ano" in s or "7º ano" in s or "8º ano" in s or "9º ano" in s:
            return "EFII"
        if "série" in s or "médio" in s or "eja" in s:
            return "EM"
        return "INDEFINIDO"

    def get_segmento_info_visual_v2(serie: str):
        seg = detectar_segmento(serie)
        if seg == "EI":
            return "Educação Infantil", "#4299e1", "Foco: Campos de Experiência (BNCC) e rotina estruturante."
        if seg == "EFI":
            return "Ensino Fundamental — Anos Iniciais", "#48bb78", "Foco: alfabetização, numeracia e consolidação de habilidades basais."
        if seg == "EFII":
            return "Ensino Fundamental — Anos Finais", "#ed8936", "Foco: autonomia, funções executivas, organização e aprofundamento conceitual."
        if seg == "EM":
            return "Ensino Médio / EJA", "#9f7aea", "Foco: projeto de vida, áreas do conhecimento e estratégias de estudo."
        return "Selecione a Série/Ano", "#718096", "Aguardando seleção..."

    def _normalizar_med(m: dict):
        return {
            "nome": (m.get("nome") or "").strip(),
            "posologia": (m.get("posologia") or "").strip(),
            "escola": bool(m.get("escola", False)),
        }

    def _ja_existe_med(lista, nome):
        nome_norm = (nome or "").strip().lower()
        if not nome_norm:
            return True
        return any((x.get("nome") or "").strip().lower() == nome_norm for x in (lista or []))

    # =========================
    # Identificação
    # =========================
    c1, c2, c3, c4, c5 = st.columns([3, 2, 2, 1, 2])

    st.session_state.dados["nome"] = c1.text_input("Nome Completo", st.session_state.dados.get("nome", ""))
    st.session_state.dados["nasc"] = c2.date_input("Nascimento", value=st.session_state.dados.get("nasc", date(2015, 1, 1)))

    # Série/Ano
    try:
        serie_idx = LISTA_SERIES.index(st.session_state.dados.get("serie")) if st.session_state.dados.get("serie") in LISTA_SERIES else 0
    except:
        serie_idx = 0

    st.session_state.dados["serie"] = c3.selectbox("Série/Ano", LISTA_SERIES, index=serie_idx, placeholder="Selecione...")

    # Segmento guiado (badge + descrição)
    if st.session_state.dados.get("serie"):
        seg_nome, seg_cor, seg_desc = get_segmento_info_visual_v2(st.session_state.dados["serie"])
        c3.markdown(
            f"<div class='segmento-badge' style='background-color:{seg_cor}'>{seg_nome}</div>",
            unsafe_allow_html=True
        )
        st.caption(seg_desc)

    st.session_state.dados["turma"] = c4.text_input("Turma", st.session_state.dados.get("turma", ""))

    # Matrícula / RA
    st.session_state.dados["matricula"] = c5.text_input("Matrícula / RA", st.session_state.dados.get("matricula", ""), placeholder="Ex: 2026-001234")

    st.divider()

    # =========================
    # Histórico & Família
    # =========================
    st.markdown("##### Histórico & Contexto Familiar")
    c_hist, c_fam = st.columns(2)
    st.session_state.dados["historico"] = c_hist.text_area("Histórico Escolar", st.session_state.dados.get("historico", ""))
    st.session_state.dados["familia"] = c_fam.text_area("Dinâmica Familiar", st.session_state.dados.get("familia", ""))

    default_familia_valido = [x for x in st.session_state.dados.get("composicao_familiar_tags", []) if x in LISTA_FAMILIA]
    st.session_state.dados["composicao_familiar_tags"] = st.multiselect(
        "Quem convive com o aluno?",
        LISTA_FAMILIA,
        default=default_familia_valido,
        help="Incluímos Mãe 1 / Mãe 2 e Pai 1 / Pai 2 para famílias diversas."
    )

    st.divider()

    # =========================
    # Laudo PDF + Extração IA
    # =========================
    st.markdown("##### 📎 Laudo (PDF) + Extração Inteligente")

    col_pdf, col_action = st.columns([2, 1], vertical_alignment="center")

    with col_pdf:
        up = st.file_uploader(
            "Arraste o arquivo aqui",
            type="pdf",
            label_visibility="collapsed",
            key="pei_laudo_pdf_uploader_tab1",
        )
        if up:
            st.session_state.pdf_text = ler_pdf(up)
            if st.session_state.pdf_text:
                st.success("PDF lido ✅ (usando até 6 páginas)")
            else:
                st.warning("Não consegui extrair texto do PDF (pode estar escaneado/imagem).")

    with col_action:
        st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
        cbtn1, cbtn2, cbtn3 = st.columns([1, 2, 1])
        with cbtn2:
            extrair = st.button(
                "✨ Extrair Dados do Laudo",
                type="primary",
                use_container_width=True,
                disabled=(not st.session_state.get("pdf_text")),
                key="btn_extrair_laudo_tab1",
            )

        if extrair:
            with st.spinner("Analisando laudo..."):
                dados_extraidos, erro = extrair_dados_pdf_ia(api_key, st.session_state.pdf_text)

            if dados_extraidos:
                # 1) Diagnóstico: preencher o campo existente
                diag = (dados_extraidos.get("diagnostico") or "").strip()
                if diag:
                    st.session_state.dados["diagnostico"] = diag

                # 2) Medicações: preparar revisão (não inserir direto)
                meds = dados_extraidos.get("medicamentos") or []
                meds_norm = []
                for med in meds:
                    m = _normalizar_med(med)
                    if m["nome"]:
                        meds_norm.append(m)

                st.session_state.dados["meds_extraidas_tmp"] = meds_norm
                st.session_state.dados["status_meds_extraidas"] = "review" if meds_norm else "idle"

                st.success("Dados extraídos ✅ (revise as medicações abaixo)")
                st.rerun()
            else:
                st.error(f"Erro: {erro}")

    # Revisão das meds extraídas (antes de inserir na lista oficial)
    if st.session_state.dados.get("status_meds_extraidas") == "review":
        meds_tmp = st.session_state.dados.get("meds_extraidas_tmp", [])

        with st.container(border=True):
            st.markdown("**💊 Medicações encontradas no laudo (confirme antes de adicionar)**")

            if not meds_tmp:
                st.info("Nenhuma medicação identificada.")
                st.session_state.dados["status_meds_extraidas"] = "idle"
            else:
                for i, m in enumerate(meds_tmp):
                    cc1, cc2, cc3 = st.columns([3, 2, 1.5])
                    m["nome"] = cc1.text_input("Nome", value=m.get("nome", ""), key=f"tmp_med_nome_{i}")
                    m["posologia"] = cc2.text_input("Posologia", value=m.get("posologia", ""), key=f"tmp_med_pos_{i}")
                    m["escola"] = cc3.checkbox("Na escola?", value=bool(m.get("escola", False)), key=f"tmp_med_esc_{i}")

                a1, a2, a3 = st.columns([2, 2, 2])

                if a1.button("✅ Adicionar ao PEI", type="primary", use_container_width=True, key="btn_add_meds_tmp"):
                    # inserir no campo existente: lista_medicamentos (sem duplicar por nome)
                    lista_atual = st.session_state.dados.get("lista_medicamentos", [])
                    for m in meds_tmp:
                        m = _normalizar_med(m)
                        if m["nome"] and not _ja_existe_med(lista_atual, m["nome"]):
                            lista_atual.append(m)

                    st.session_state.dados["lista_medicamentos"] = lista_atual
                    st.session_state.dados["meds_extraidas_tmp"] = []
                    st.session_state.dados["status_meds_extraidas"] = "idle"
                    st.success("Medicações adicionadas ✅")
                    st.rerun()

                if a2.button("🧹 Limpar lista extraída", use_container_width=True, key="btn_clear_meds_tmp"):
                    st.session_state.dados["meds_extraidas_tmp"] = []
                    st.session_state.dados["status_meds_extraidas"] = "idle"
                    st.rerun()

                if a3.button("↩️ Voltar sem adicionar", use_container_width=True, key="btn_back_meds_tmp"):
                    st.session_state.dados["status_meds_extraidas"] = "idle"
                    st.rerun()

    st.divider()

    # =========================
    # Contexto Clínico + Medicação (campo EXISTENTE)
    # =========================
    st.markdown("##### Contexto Clínico")
    st.session_state.dados["diagnostico"] = st.text_input("Diagnóstico", st.session_state.dados.get("diagnostico", ""))

    with st.container(border=True):
        usa_med = st.toggle(
            "💊 O aluno faz uso contínuo de medicação?",
            value=len(st.session_state.dados.get("lista_medicamentos", [])) > 0,
            key="toggle_usa_med_tab1"
        )

        if usa_med:
            cmed1, cmed2, cmed3 = st.columns([3, 2, 2])
            nm = cmed1.text_input("Nome", key="nm_med_manual")
            pos = cmed2.text_input("Posologia", key="pos_med_manual")
            admin_escola = cmed3.checkbox("Na escola?", key="adm_esc_manual")

            if st.button("Adicionar", key="btn_add_med_manual"):
                if nm.strip():
                    # não duplicar por nome
                    if not _ja_existe_med(st.session_state.dados.get("lista_medicamentos", []), nm):
                        st.session_state.dados["lista_medicamentos"].append(
                            {"nome": nm.strip(), "posologia": pos.strip(), "escola": admin_escola}
                        )
                    st.rerun()

        if st.session_state.dados.get("lista_medicamentos"):
            st.write("---")
            for i, m in enumerate(st.session_state.dados["lista_medicamentos"]):
                tag = " [NA ESCOLA]" if m.get("escola") else ""
                c_txt, c_btn = st.columns([5, 1])
                c_txt.info(f"💊 **{m.get('nome','')}** ({m.get('posologia','')}){tag}")
                if c_btn.button("Excluir", key=f"del_med_{i}"):
                    st.session_state.dados["lista_medicamentos"].pop(i)
                    st.rerun()


# ==============================================================================
# 13. ABA EVIDÊNCIAS (COMPLETA)
# ==============================================================================
with tab2:
    render_progresso()
    st.markdown("### <i class='ri-search-eye-line'></i> Coleta de Evidências", unsafe_allow_html=True)

    atual = st.session_state.dados.get("nivel_alfabetizacao")
    idx = LISTA_ALFABETIZACAO.index(atual) if atual in LISTA_ALFABETIZACAO else 0
    st.session_state.dados["nivel_alfabetizacao"] = st.selectbox("Hipótese de Escrita", LISTA_ALFABETIZACAO, index=idx)

    st.divider()
    c1, c2, c3 = st.columns(3)

    def _tog(label):
        st.session_state.dados["checklist_evidencias"][label] = st.toggle(
            label,
            value=st.session_state.dados["checklist_evidencias"].get(label, False),
        )

    with c1:
        st.markdown("**Pedagógico**")
        for q in [
            "Estagnação na aprendizagem",
            "Lacuna em pré-requisitos",
            "Dificuldade de generalização",
            "Dificuldade de abstração",
        ]:
            _tog(q)

    with c2:
        st.markdown("**Cognitivo**")
        for q in [
            "Oscilação de foco",
            "Fadiga mental rápida",
            "Dificuldade de iniciar tarefas",
            "Esquecimento recorrente",
        ]:
            _tog(q)

    with c3:
        st.markdown("**Comportamental**")
        for q in [
            "Dependência de mediação (1:1)",
            "Baixa tolerância à frustração",
            "Desorganização de materiais",
            "Recusa de tarefas",
        ]:
            _tog(q)

    st.divider()
    st.markdown("##### Observações rápidas")
    st.session_state.dados["orientacoes_especialistas"] = st.text_area(
        "Registre observações de professores e especialistas (se houver)",
        st.session_state.dados.get("orientacoes_especialistas", ""),
        height=120,
    )

# ==============================================================================
# 14. ABA REDE DE APOIO (COMPLETA)
# ==============================================================================
with tab3:
    render_progresso()
    st.markdown("### <i class='ri-team-line'></i> Rede de Apoio", unsafe_allow_html=True)

    # Garantias (caso algo não tenha entrado no default_state)
    st.session_state.dados.setdefault("rede_apoio", [])
    st.session_state.dados.setdefault("orientacoes_especialistas", "")
    st.session_state.dados.setdefault("orientacoes_por_profissional", {})

    st.caption("Selecione os profissionais envolvidos e registre as orientações específicas de cada um.")

    # 1) Seleção da rede
    selecionados = st.multiselect(
        "Profissionais:",
        LISTA_PROFISSIONAIS,
        default=[p for p in st.session_state.dados.get("rede_apoio", []) if p in LISTA_PROFISSIONAIS],
        help="Ao selecionar um profissional, um campo de observação individual aparece abaixo."
    )
    st.session_state.dados["rede_apoio"] = selecionados

    # 2) Limpeza automática de chaves que não existem mais
    # (se o usuário desmarcar um profissional, removemos o texto dele do dicionário)
    orient_map = st.session_state.dados.get("orientacoes_por_profissional", {})
    orient_map = {k: v for k, v in orient_map.items() if k in selecionados}
    st.session_state.dados["orientacoes_por_profissional"] = orient_map

    st.divider()

    # 3) Campo geral (opcional) — mantém compatibilidade com o legado
    with st.expander("🗒️ Anotações gerais (opcional)", expanded=False):
        st.session_state.dados["orientacoes_especialistas"] = st.text_area(
            "Orientações clínicas gerais / resumo",
            st.session_state.dados.get("orientacoes_especialistas", ""),
            placeholder="Use para observações gerais da equipe (ex.: acordos com a família, encaminhamentos, alinhamentos).",
            height=140,
            key="txt_orientacoes_gerais_rede"
        )

    # 4) Campos individuais por profissional
    st.markdown("#### 📌 Orientações por profissional")
    if not selecionados:
        st.info("Selecione ao menos um profissional para habilitar os campos de observação.")
    else:
        # Layout em cards (2 colunas)
        cols = st.columns(2)
        for i, prof in enumerate(selecionados):
            alvo = cols[i % 2]
            with alvo:
                icon = get_pro_icon(prof) if "get_pro_icon" in globals() else "👤"
                with st.container(border=True):
                    st.markdown(f"**{icon} {prof}**")

                    st.session_state.dados["orientacoes_por_profissional"].setdefault(prof, "")

                    st.session_state.dados["orientacoes_por_profissional"][prof] = st.text_area(
                        "Observações / orientações",
                        value=st.session_state.dados["orientacoes_por_profissional"].get(prof, ""),
                        placeholder="Ex.: recomendações de intervenção, frequência, sinais de alerta, ajustes para sala de aula...",
                        height=140,
                        key=f"txt_orient_{prof}"
                    )

                    c1, c2 = st.columns([1, 1])
                    if c1.button("🧹 Limpar", use_container_width=True, key=f"btn_limpar_{prof}"):
                        st.session_state.dados["orientacoes_por_profissional"][prof] = ""
                        st.rerun()

                    if c2.button("🗑️ Remover profissional", use_container_width=True, key=f"btn_remove_{prof}"):
                        # remove do multiselect
                        st.session_state.dados["rede_apoio"] = [x for x in st.session_state.dados["rede_apoio"] if x != prof]
                        # remove do dicionário
                        st.session_state.dados["orientacoes_por_profissional"].pop(prof, None)
                        st.rerun()

    st.divider()

    # 5) Resumo visual rápido
    if selecionados:
        resumo = []
        for p in selecionados:
            txt = (st.session_state.dados["orientacoes_por_profissional"].get(p) or "").strip()
            resumo.append(f"- **{p}**: {'✅ preenchido' if txt else '⚠️ vazio'}")
        st.markdown("##### ✅ Checklist de preenchimento")
        st.markdown("\n".join(resumo))


# ==============================================================================
# 15. ABA MAPEAMENTO (3 colunas | hiperfoco + potências + barreiras + nível de apoio + observações)
# ==============================================================================
with tab4:
    render_progresso()
    st.markdown("### <i class='ri-radar-line'></i> Mapeamento", unsafe_allow_html=True)
    st.caption("Mapeie forças, hiperfocos e barreiras. Para cada barreira selecionada, indique a intensidade de apoio necessária.")

    # -------------------------
    # Garantias de estado
    # -------------------------
    st.session_state.dados.setdefault("hiperfoco", "")
    st.session_state.dados.setdefault("potencias", [])
    st.session_state.dados.setdefault("barreiras_selecionadas", {k: [] for k in LISTAS_BARREIRAS.keys()})
    st.session_state.dados.setdefault("niveis_suporte", {})          # chave: f"{dominio}_{barreira}" -> valor
    st.session_state.dados.setdefault("observacoes_barreiras", {})   # texto livre por domínio

    # -------------------------
    # 1) POTENCIALIDADES + HIPERFOCO
    # -------------------------
    with st.container(border=True):
        st.markdown("#### 🌟 Potencialidades e Hiperfoco")
        c1, c2 = st.columns(2)

        st.session_state.dados["hiperfoco"] = c1.text_input(
            "Hiperfoco (se houver)",
            st.session_state.dados.get("hiperfoco", ""),
            placeholder="Ex.: Dinossauros, Minecraft, Mapas, Carros, Desenho..."
        )

        pot_validas = [p for p in st.session_state.dados.get("potencias", []) if p in LISTA_POTENCIAS]
        st.session_state.dados["potencias"] = c2.multiselect(
            "Potencialidades / Pontos fortes",
            LISTA_POTENCIAS,
            default=pot_validas
        )

    st.divider()

    st.markdown("#### 🧩 Barreiras e nível de apoio")
    st.caption("Selecione as barreiras observadas e defina o nível de apoio para a rotina escolar (não é DUA).")

    # -------------------------
    # 2) Renderização por domínio
    # -------------------------
    def render_dominio(dominio: str, opcoes: list[str]):
        with st.container(border=True):
            st.markdown(f"**{dominio}**")

            # multiselect
            salvas = [b for b in st.session_state.dados["barreiras_selecionadas"].get(dominio, []) if b in opcoes]
            selecionadas = st.multiselect(
                "Selecione as barreiras",
                opcoes,
                default=salvas,
                key=f"ms_{dominio}",
                label_visibility="collapsed"
            )
            st.session_state.dados["barreiras_selecionadas"][dominio] = selecionadas

            # sliders por barreira (bem visível: nome + barra na mesma linha)
            if selecionadas:
                st.markdown("---")
                st.markdown("**Nível de apoio por barreira**")
                st.caption("Escala: Autônomo (faz sozinho) → Monitorado → Substancial → Muito Substancial (suporte intenso/contínuo).")

                for b in selecionadas:
                    chave = f"{dominio}_{b}"
                    st.session_state.dados["niveis_suporte"].setdefault(chave, "Monitorado")

                    colA, colB = st.columns([2.2, 2.8], vertical_alignment="center")
                    with colA:
                        st.markdown(f"✅ **{b}**")
                    with colB:
                        st.session_state.dados["niveis_suporte"][chave] = st.select_slider(
                            "Nível de apoio",
                            options=["Autônomo", "Monitorado", "Substancial", "Muito Substancial"],
                            value=st.session_state.dados["niveis_suporte"].get(chave, "Monitorado"),
                            key=f"sl_{dominio}_{b}",
                            label_visibility="collapsed",
                            help=(
                                "Autônomo: realiza sem mediação | "
                                "Monitorado: precisa de checagens | "
                                "Substancial: precisa de mediação frequente | "
                                "Muito Substancial: precisa de suporte intenso/contínuo"
                            )
                        )

            # observação por domínio (mantido)
            st.session_state.dados["observacoes_barreiras"].setdefault(dominio, "")
            st.session_state.dados["observacoes_barreiras"][dominio] = st.text_area(
                "Observações (opcional)",
                value=st.session_state.dados["observacoes_barreiras"].get(dominio, ""),
                placeholder="Ex.: quando ocorre, gatilhos, o que ajuda, o que piora, estratégias que já funcionam...",
                height=90,
                key=f"obs_{dominio}"
            )

    # -------------------------
    # 3) 3 colunas (distribuição como era antes)
    # -------------------------
    c_bar1, c_bar2, c_bar3 = st.columns(3)

    with c_bar1:
        render_dominio("Funções Cognitivas", LISTAS_BARREIRAS.get("Funções Cognitivas", []))
        render_dominio("Sensorial e Motor", LISTAS_BARREIRAS.get("Sensorial e Motor", []))

    with c_bar2:
        render_dominio("Comunicação e Linguagem", LISTAS_BARREIRAS.get("Comunicação e Linguagem", []))
        render_dominio("Acadêmico", LISTAS_BARREIRAS.get("Acadêmico", []))

    with c_bar3:
        render_dominio("Socioemocional", LISTAS_BARREIRAS.get("Socioemocional", []))

    # -------------------------
    # 4) Limpeza automática (remove níveis de suporte de barreiras desmarcadas)
    # -------------------------
    chaves_validas = set()
    for dom, itens in st.session_state.dados["barreiras_selecionadas"].items():
        for b in itens:
            chaves_validas.add(f"{dom}_{b}")

    niveis = st.session_state.dados.get("niveis_suporte", {})
    st.session_state.dados["niveis_suporte"] = {k: v for k, v in niveis.items() if k in chaves_validas}

    st.divider()

    # -------------------------
    # 5) Resumo
    # -------------------------
    st.markdown("#### 📌 Resumo do Mapeamento")

    r1, r2 = st.columns(2)

    with r1:
        hf = (st.session_state.dados.get("hiperfoco") or "").strip()
        if hf:
            st.success(f"🎯 **Hiperfoco:** {hf}")
        else:
            st.info("🎯 **Hiperfoco:** não informado")

        pots = st.session_state.dados.get("potencias", [])
        if pots:
            st.success(f"🌟 **Potencialidades:** {', '.join(pots)}")
        else:
            st.info("🌟 **Potencialidades:** não selecionadas")

    with r2:
        selecionadas = {dom: vals for dom, vals in st.session_state.dados["barreiras_selecionadas"].items() if vals}
        total_bar = sum(len(v) for v in selecionadas.values())

        if total_bar == 0:
            st.info("🧩 **Barreiras:** nenhuma selecionada")
        else:
            st.warning(f"🧩 **Barreiras selecionadas:** {total_bar}")
            for dom, vals in selecionadas.items():
                st.markdown(f"**{dom}:**")
                for b in vals:
                    chave = f"{dom}_{b}"
                    nivel = st.session_state.dados["niveis_suporte"].get(chave, "Monitorado")
                    st.markdown(f"- {b} → **{nivel}**")


# ==============================================================================
# 16. ABA PLANO DE AÇÃO (COMPLETA)
# ==============================================================================
with tab5:
    render_progresso()
    st.markdown("### <i class='ri-tools-line'></i> Plano de Ação", unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown("#### 1) Acesso (DUA)")
        st.session_state.dados["estrategias_acesso"] = st.multiselect(
            "Recursos de acesso",
            [
                "Tempo Estendido",
                "Apoio Leitura/Escrita",
                "Material Ampliado",
                "Tecnologia Assistiva",
                "Sala Silenciosa",
                "Mobiliário Adaptado",
                "Pistas Visuais",
                "Rotina Estruturada",
            ],
            default=st.session_state.dados.get("estrategias_acesso", []),
        )
        st.session_state.dados["outros_acesso"] = st.text_input(
            "Personalizado (Acesso)",
            st.session_state.dados.get("outros_acesso", ""),
            placeholder="Ex: Prova em local separado, fonte 18, papel pautado ampliado…",
        )

    with c2:
        st.markdown("#### 2) Ensino (Metodologias)")
        st.session_state.dados["estrategias_ensino"] = st.multiselect(
            "Estratégias de ensino",
            [
                "Fragmentação de Tarefas",
                "Instrução Explícita",
                "Modelagem",
                "Mapas Mentais",
                "Andaimagem (Scaffolding)",
                "Ensino Híbrido",
                "Organizadores Gráficos",
                "Prática Guiada",
            ],
            default=st.session_state.dados.get("estrategias_ensino", []),
        )
        st.session_state.dados["outros_ensino"] = st.text_input(
            "Personalizado (Ensino)",
            st.session_state.dados.get("outros_ensino", ""),
            placeholder="Ex: Sequência didática com apoio de imagens + exemplo resolvido…",
        )

    with c3:
        st.markdown("#### 3) Avaliação (Formato)")
        st.session_state.dados["estrategias_avaliacao"] = st.multiselect(
            "Estratégias de avaliação",
            [
                "Prova Adaptada",
                "Prova Oral",
                "Consulta Permitida",
                "Portfólio",
                "Autoavaliação",
                "Parecer Descritivo",
                "Questões Menores por Bloco",
                "Avaliação Prática (Demonstração)",
            ],
            default=st.session_state.dados.get("estrategias_avaliacao", []),
        )
        st.caption("Dica: combine formato + acesso (tempo/ambiente) para reduzir barreiras.")

    st.divider()
    st.info("✅ O plano de ação alimenta a Consultoria IA com contexto prático (o que você já pretende fazer).")


# ==============================================================================
# 17. ABA MONITORAMENTO (COMPLETA)
# ==============================================================================
with tab6:
    render_progresso()
    st.markdown("### <i class='ri-loop-right-line'></i> Monitoramento", unsafe_allow_html=True)

    st.session_state.dados["monitoramento_data"] = st.date_input(
        "Data da Próxima Revisão",
        value=st.session_state.dados.get("monitoramento_data", date.today()),
    )

    st.divider()
    st.warning("⚠️ Preencher esta aba principalmente na REVISÃO do PEI (ciclo de acompanhamento).")

    with st.container(border=True):
        c2, c3 = st.columns(2)
        with c2:
            atual = st.session_state.dados.get("status_meta", "Não Iniciado")
            st.session_state.dados["status_meta"] = st.selectbox(
                "Status da Meta",
                ["Não Iniciado", "Em Andamento", "Parcialmente Atingido", "Atingido", "Superado"],
                index=(["Não Iniciado", "Em Andamento", "Parcialmente Atingido", "Atingido", "Superado"].index(atual) if atual in ["Não Iniciado", "Em Andamento", "Parcialmente Atingido", "Atingido", "Superado"] else 0),
            )
        with c3:
            atualp = st.session_state.dados.get("parecer_geral", "Manter Estratégias")
            st.session_state.dados["parecer_geral"] = st.selectbox(
                "Parecer Geral",
                [
                    "Manter Estratégias",
                    "Aumentar Suporte",
                    "Reduzir Suporte (Autonomia)",
                    "Alterar Metodologia",
                    "Encaminhar para Especialista",
                ],
                index=(
                    [
                        "Manter Estratégias",
                        "Aumentar Suporte",
                        "Reduzir Suporte (Autonomia)",
                        "Alterar Metodologia",
                        "Encaminhar para Especialista",
                    ].index(atualp)
                    if atualp in [
                        "Manter Estratégias",
                        "Aumentar Suporte",
                        "Reduzir Suporte (Autonomia)",
                        "Alterar Metodologia",
                        "Encaminhar para Especialista",
                    ]
                    else 0
                ),
            )

        st.session_state.dados["proximos_passos_select"] = st.multiselect(
            "Ações Futuras",
            [
                "Reunião com Família",
                "Encaminhamento Clínico",
                "Adaptação de Material",
                "Mudança de Lugar em Sala",
                "Novo PEI",
                "Observação em Sala",
            ],
            default=st.session_state.dados.get("proximos_passos_select", []),
        )


# ==============================================================================
# 18. ABA CONSULTORIA IA (COMPLETA: gerar + revisar + aprovar + ajustar)
# ==============================================================================
with tab7:
    render_progresso()
    st.markdown("### <i class='ri-robot-2-line'></i> Consultoria Pedagógica", unsafe_allow_html=True)

    if not st.session_state.dados.get("serie"):
        st.warning("⚠️ Selecione a Série/Ano na aba **Estudante** para ativar o modo especialista.")
        st.stop()

    # estado default
    st.session_state.dados.setdefault("status_validacao_pei", "rascunho")
    st.session_state.dados.setdefault("feedback_ajuste", "")

    seg_nome, seg_cor, seg_desc = get_segmento_info_visual(st.session_state.dados.get("serie"))
    st.markdown(
        f"<div style='background-color:#F7FAFC; border-left:5px solid {seg_cor}; padding:14px; border-radius:8px; margin-bottom:16px;'>"
        f"<b style='color:{seg_cor};'>ℹ️ Modo Especialista: {seg_nome}</b><br>"
        f"<span style='color:#4A5568;'>{seg_desc}</span></div>",
        unsafe_allow_html=True,
    )

    if not api_key:
        st.error("⚠️ Configure a chave OpenAI na sidebar para gerar o PEI por IA.")
        st.stop()

    # 1) Se ainda não tem texto, ou voltou para rascunho: botões de geração
    if (not st.session_state.dados.get("ia_sugestao")) or (st.session_state.dados.get("status_validacao_pei") == "rascunho"):
        col_btn, col_info = st.columns([1, 2])

        with col_btn:
            if st.button("✨ Gerar Estratégia Técnica", type="primary", use_container_width=True):
                res, err = consultar_gpt_pedagogico(
                    api_key,
                    st.session_state.dados,
                    st.session_state.get("pdf_text", ""),
                    modo_pratico=False,
                )
                if res:
                    st.session_state.dados["ia_sugestao"] = res
                    st.session_state.dados["status_validacao_pei"] = "revisao"
                    st.rerun()
                else:
                    st.error(err or "Erro ao gerar.")

            st.write("")
            if st.button("🧰 Gerar Guia Prático (Sala de Aula)", use_container_width=True):
                res, err = consultar_gpt_pedagogico(
                    api_key,
                    st.session_state.dados,
                    st.session_state.get("pdf_text", ""),
                    modo_pratico=True,
                )
                if res:
                    st.session_state.dados["ia_sugestao"] = res
                    st.session_state.dados["status_validacao_pei"] = "revisao"
                    st.rerun()
                else:
                    st.error(err or "Erro ao gerar.")

        with col_info:
            n_bar = sum(len(v) for v in (st.session_state.dados.get("barreiras_selecionadas") or {}).values())
            st.info(
                "Quanto mais completo o **Mapeamento** (barreiras + nível de suporte + hiperfoco) "
                "e o **Plano de Ação**, melhor a precisão.\n\n"
                f"📌 Barreiras mapeadas agora: **{n_bar}**"
            )

    # 2) Revisão / Aprovado: mostrar e permitir aprovar/ajustar
    elif st.session_state.dados.get("status_validacao_pei") in ["revisao", "aprovado"]:
        n_barreiras = sum(len(v) for v in (st.session_state.dados.get("barreiras_selecionadas") or {}).values())
        diag_show = st.session_state.dados.get("diagnostico") or "em observação"

        with st.expander("🧠 Como a IA construiu este relatório (transparência)"):
            exemplo_barreira = "geral"
            try:
                for area, lst in (st.session_state.dados.get("barreiras_selecionadas") or {}).items():
                    if lst:
                        exemplo_barreira = lst[0]
                        break
            except Exception:
                pass

            st.markdown(
                f"**1. Input do estudante:** Série **{st.session_state.dados.get('serie','-')}**, diagnóstico **{diag_show}**.\n\n"
                f"**2. Barreiras ativas:** detectei **{n_barreiras}** barreiras e cruzei isso com BNCC + DUA.\n\n"
                f"**3. Ponto crítico exemplo:** priorizei adaptações para reduzir impacto de **{exemplo_barreira}**."
            )

        with st.expander("🛡️ Calibragem e segurança pedagógica"):
            st.markdown(
                "- **Farmacologia:** não sugere dose/medicação; apenas sinaliza pontos de atenção.\n"
                "- **Dados sensíveis:** evite inserir PII desnecessária.\n"
                "- **Normativa:** sugestões buscam aderência à LBI/DUA e adaptações razoáveis."
            )

        st.markdown("#### 📝 Revisão do Plano")
        texto_visual = re.sub(r"\[.*?\]", "", st.session_state.dados.get("ia_sugestao", ""))
        st.markdown(texto_visual)

        st.divider()
        st.markdown("**⚠️ Responsabilidade do Educador:** a IA pode errar. Valide e ajuste antes de aplicar.")

        if st.session_state.dados.get("status_validacao_pei") == "revisao":
            c_ok, c_ajuste = st.columns(2)
            if c_ok.button("✅ Aprovar Plano", type="primary", use_container_width=True):
                st.session_state.dados["status_validacao_pei"] = "aprovado"
                st.success("Plano aprovado ✅")
                st.rerun()
            if c_ajuste.button("❌ Solicitar Ajuste", use_container_width=True):
                st.session_state.dados["status_validacao_pei"] = "ajustando"
                st.rerun()

        elif st.session_state.dados.get("status_validacao_pei") == "aprovado":
            st.success("Plano Validado ✅")
            novo_texto = st.text_area(
                "Edição Final Manual (opcional)",
                value=st.session_state.dados.get("ia_sugestao", ""),
                height=320,
            )
            st.session_state.dados["ia_sugestao"] = novo_texto

            c1, c2 = st.columns(2)
            with c1:
                if st.button("🔁 Regerar do Zero", use_container_width=True):
                    st.session_state.dados["ia_sugestao"] = ""
                    st.session_state.dados["status_validacao_pei"] = "rascunho"
                    st.rerun()
            with c2:
                if st.button("🧹 Voltar para Revisão", use_container_width=True):
                    st.session_state.dados["status_validacao_pei"] = "revisao"
                    st.rerun()

    # 3) Ajustando: caixa de feedback + regerar
    elif st.session_state.dados.get("status_validacao_pei") == "ajustando":
        st.warning("Descreva o ajuste desejado:")
        feedback = st.text_area("Seu feedback:", placeholder="Ex: Foque mais na alfabetização…")
        if st.button("Regerar com Ajustes", type="primary", use_container_width=True):
            res, err = consultar_gpt_pedagogico(
                api_key,
                st.session_state.dados,
                st.session_state.get("pdf_text", ""),
                modo_pratico=False,
                feedback_usuario=feedback,
            )
            if res:
                st.session_state.dados["ia_sugestao"] = res
                st.session_state.dados["status_validacao_pei"] = "revisao"
                st.rerun()
            else:
                st.error(err or "Erro ao regerar.")

        if st.button("Cancelar", use_container_width=True):
            st.session_state.dados["status_validacao_pei"] = "revisao"
            st.rerun()


# ==============================================================================
# 19. ABA DASHBOARD & DOCS (Dashboard + Metas + Exportações + Sincronização)
# ==============================================================================
with tab8:
    render_progresso()
    st.markdown("### <i class='ri-file-pdf-line'></i> Dashboard e Exportação", unsafe_allow_html=True)

    # --------------------------------------------------------------------------
    # 0) CSS DO DASH
    # --------------------------------------------------------------------------
    def _ensure_dashboard_css():
        css = """
        <style>
            .dash-hero { background: linear-gradient(135deg, #0F52BA 0%, #062B61 100%); border-radius: 16px; padding: 25px; color: white; margin-bottom: 20px; display: flex; justify-content: space-between; align-items: center; }
            .apple-avatar { width: 60px; height: 60px; border-radius: 50%; background: rgba(255,255,255,.15); border: 2px solid rgba(255,255,255,.4); display:flex; align-items:center; justify-content:center; font-size:1.6rem; font-weight:800; }
            .metric-card { background:white; border-radius:16px; padding:15px; border:1px solid #E2E8F0; height:140px; display:flex; flex-direction:column; align-items:center; justify-content:center; }
            .soft-card { border-radius:12px; padding:20px; border-left:5px solid; background:#FFF; }
        </style>
        """
        st.markdown(css, unsafe_allow_html=True)

    _ensure_dashboard_css()

    # --------------------------------------------------------------------------
    # 1) HELPERS
    # --------------------------------------------------------------------------
    d = st.session_state.dados

    def _safe(fn, default):
        return globals().get(fn, default)

    calcular_idade_fn = _safe("calcular_idade", lambda x: "")
    extrair_metas_fn = _safe(
        "extrair_metas_estruturadas",
        lambda t: {"Curto": "—", "Medio": "—", "Longo": "—"}
    )

    # ✅ Converte qualquer coisa "não serializável" (date/datetime etc.) em JSON-safe
    def _json_safe(obj):
        from datetime import date, datetime

        if obj is None:
            return None

        # date/datetime → ISO
        if isinstance(obj, (date, datetime)):
            return obj.isoformat()

        # dict → recursivo
        if isinstance(obj, dict):
            return {str(k): _json_safe(v) for k, v in obj.items()}

        # list/tuple → recursivo
        if isinstance(obj, (list, tuple)):
            return [_json_safe(x) for x in obj]

        # tipos simples ok
        if isinstance(obj, (str, int, float, bool)):
            return obj

        # fallback seguro (ex.: objetos)
        return str(obj)

    # --------------------------------------------------------------------------
    # 2) GUARD
    # --------------------------------------------------------------------------
    if not d.get("nome"):
        st.info("Preencha o estudante na aba **Estudante**.")
        st.stop()

    # --------------------------------------------------------------------------
    # 3) HERO
    # --------------------------------------------------------------------------
    init_avatar = d["nome"][0].upper()
    idade = calcular_idade_fn(d.get("nasc"))
    student_id = st.session_state.get("selected_student_id")

    st.markdown(
        f"""
        <div class="dash-hero">
            <div style="display:flex; gap:16px; align-items:center;">
                <div class="apple-avatar">{init_avatar}</div>
                <div>
                    <h2 style="margin:0;">{d.get("nome")}</h2>
                    <div style="opacity:.85; font-size:.9rem;">
                        {d.get("serie","-")} • {d.get("turma","-")}
                    </div>
                    <div style="font-size:.8rem; opacity:.7;">
                        {"Vinculado ao Supabase" if student_id else "Rascunho local"}
                    </div>
                </div>
            </div>
            <div style="text-align:right;">
                <div style="font-size:.75rem;">IDADE</div>
                <div style="font-size:1.2rem; font-weight:800;">{idade}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # --------------------------------------------------------------------------
    # 4) KPIs (simples)
    # --------------------------------------------------------------------------
    c1, c2, c3 = st.columns(3)

    with c1:
        st.metric("Potencialidades", len(d.get("potencias", []) or []))
    with c2:
        st.metric(
            "Barreiras",
            sum(len(v) for v in (d.get("barreiras_selecionadas", {}) or {}).values())
        )
    with c3:
        st.metric("Rede de Apoio", len(d.get("rede_apoio", []) or []))

    # --------------------------------------------------------------------------
    # 5) METAS
    # --------------------------------------------------------------------------
    metas = extrair_metas_fn(d.get("ia_sugestao", ""))
    st.markdown(
        f"""
        <div class="soft-card" style="border-left-color:#D69E2E;">
            <b>🏁 Metas</b><br><br>
            <b>Curto:</b> {metas.get("Curto")}<br>
            <b>Médio:</b> {metas.get("Medio")}<br>
            <b>Longo:</b> {metas.get("Longo")}
        </div>
        """,
        unsafe_allow_html=True
    )

    # --------------------------------------------------------------------------
    # 6) EXPORTAÇÃO + SINCRONIZAÇÃO
    # --------------------------------------------------------------------------
    st.divider()
    st.markdown("#### 📤 Exportação e Sincronização")

    if not d.get("ia_sugestao"):
        st.info("Gere o Plano na aba **Consultoria IA** para liberar exportações.")
        st.stop()

    col_docs, col_backup, col_sys = st.columns(3)

    # ---------------- DOCS ----------------
    with col_docs:
        st.caption("📄 Documentos")

        try:
            pdf = gerar_pdf_final(d)
            st.download_button(
                "Baixar PDF",
                pdf,
                f"PEI_{d.get('nome')}.pdf",
                "application/pdf",
                use_container_width=True
            )
        except Exception as e:
            st.error(f"Erro PDF: {e}")

        try:
            docx = gerar_docx_final(d)
            st.download_button(
                "Baixar Word",
                docx,
                f"PEI_{d.get('nome')}.docx",
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                use_container_width=True
            )
        except Exception as e:
            st.error(f"Erro Word: {e}")

    # ---------------- BACKUP ----------------
    with col_backup:
        st.caption("💾 Backup (JSON)")
        st.download_button(
            "Salvar JSON",
            json.dumps(_json_safe(d), ensure_ascii=False),  # ✅ também fica mais robusto
            f"PEI_{d.get('nome')}.json",
            "application/json",
            use_container_width=True
        )

    # ---------------- CLOUD ----------------
    with col_sys:
        st.caption("🌐 Omnisfera")

        st.markdown(
            "<div style='font-size:.85rem; color:#4A5568; margin-bottom:8px;'>"
            "Vincula o aluno e salva o PEI na nuvem (Supabase)."
            "</div>",
            unsafe_allow_html=True
        )

        def _cloud_ready(debug: bool = False):
            details = {}
            auth = bool(st.session_state.get("autenticado", False))
            ws_id = st.session_state.get("workspace_id")

            try:
                has_url = bool(str(st.secrets.get("SUPABASE_URL", "")).strip())
            except Exception:
                has_url = False

            try:
                has_key = bool(
                    str(st.secrets.get("SUPABASE_SERVICE_KEY", "")).strip()
                    or str(st.secrets.get("SUPABASE_ANON_KEY", "")).strip()
                )
            except Exception:
                has_key = False

            details["autenticado"] = auth
            details["has_workspace_id"] = bool(ws_id)
            details["has_supabase_url"] = has_url
            details["has_supabase_key"] = has_key

            ok = all(details.values())
            if debug:
                details["missing"] = [k for k, v in details.items() if not v]
            return ok, details

        if st.button(
            "🔗 Sincronizar (Omnisfera)",
            type="primary",
            use_container_width=True,
            key="btn_sync_omnisfera_tab8"
        ):
            ok, details = _cloud_ready(debug=True)
            if not ok:
                st.error("Nuvem indisponível: verifique login/workspace/secrets do Supabase.")
                st.json(details)
                st.stop()

            try:
                from omni_utils import supa_save_pei

                sid = st.session_state.get("selected_student_id")

                # 1) cria aluno no Supabase se ainda não tiver
                if not sid:
                    nasc = d.get("nasc")
                    birth_iso = nasc.isoformat() if hasattr(nasc, "isoformat") else None

                    created = db_create_student({
                        "name": d.get("nome"),
                        "birth_date": birth_iso,
                        "grade": d.get("serie"),
                        "class_group": d.get("turma") or None,
                        "diagnosis": d.get("diagnostico") or None,
                    })

                    sid = (created or {}).get("id") if isinstance(created, dict) else None
                    if not sid:
                        raise RuntimeError("Falha ao criar aluno no Supabase. Verifique tabela/policies/RLS.")

                    st.session_state["selected_student_id"] = sid

                # 2) ✅ salva PEI com dados JSON-safe
                dados_cloud = _json_safe(d)
                supa_save_pei(sid, dados_cloud, st.session_state.get("pdf_text", ""))

                st.success("✅ Sincronizado: aluno vinculado + PEI salvo na nuvem.")
                st.rerun()

            except Exception as e:
                st.error(f"Erro ao salvar na nuvem: {e}")


# ==============================================================================
# ABA — JORNADA GAMIFICADA (BLOCO COMPLETO)
# ==============================================================================

with tab_mapa:
    render_progresso()

    nome_aluno = st.session_state.dados.get("nome") or "Estudante"
    serie = st.session_state.dados.get("serie") or ""
    hiperfoco = st.session_state.dados.get("hiperfoco") or ""
    potencias = st.session_state.dados.get("potencias") or []
    pei_ok = bool(st.session_state.dados.get("ia_sugestao"))

    # Header visual
    seg_nome, seg_cor, seg_desc = ("Selecione a Série", "#CBD5E0", "Defina a série na aba Estudante.")
    if serie:
        seg_nome, seg_cor, seg_desc = get_segmento_info_visual(serie)

    st.markdown(
        f"""
        <div style="
            background: linear-gradient(90deg, {seg_cor} 0%, #111827 140%);
            padding: 22px 26px; border-radius: 18px; color: white; margin-bottom: 18px;
            box-shadow: 0 8px 18px rgba(0,0,0,0.06);
        ">
            <div style="display:flex; align-items:center; justify-content:space-between; gap:16px;">
                <div>
                    <div style="font-size:0.9rem; opacity:0.9; font-weight:700; letter-spacing:0.3px;">🎮 JORNADA GAMIFICADA</div>
                    <div style="font-size:1.6rem; font-weight:900; margin-top:4px;">Missão do(a) {nome_aluno}</div>
                    <div style="opacity:0.92; margin-top:6px; font-weight:600;">{seg_nome} • {serie}</div>
                </div>
                <div style="text-align:right;">
                    <div style="font-size:0.75rem; opacity:0.85; font-weight:700;">Modo</div>
                    <div style="font-size:1.05rem; font-weight:900;">{("Pronto" if pei_ok else "Aguardando PEI")}</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.info(
        "ℹ️ Esta aba cria um material **para o estudante**: uma versão gamificada do plano, "
        "para imprimir, entregar à família ou usar como combinado de sala."
    )

    # Pré-requisitos
    if not serie:
        st.warning("⚠️ Selecione a **Série/Ano** na aba **Estudante** para liberar a Jornada.")
        st.stop()

    if not st.session_state.dados.get("nome"):
        st.warning("⚠️ Preencha o **nome do estudante** na aba **Estudante** para liberar a Jornada.")
        st.stop()

    if not pei_ok:
        st.warning("⚠️ Gere o PEI Técnico na aba **Consultoria IA** antes de criar a Jornada.")
        st.stop()

    # Contexto compacto
    with st.container(border=True):
        cA, cB, cC = st.columns([2, 2, 2])
        with cA:
            st.markdown("##### 🚀 Hiperfoco")
            st.write(hiperfoco if hiperfoco else "—")
        with cB:
            st.markdown("##### 🌟 Potencialidades")
            if potencias:
                st.write(", ".join(potencias))
            else:
                st.write("—")
        with cC:
            st.markdown("##### 🧭 Guia do Segmento")
            st.caption(seg_desc)

    st.divider()

    # Estado de validação
    st.session_state.dados.setdefault("status_validacao_game", "rascunho")
    st.session_state.dados.setdefault("feedback_ajuste_game", "")
    st.session_state.dados.setdefault("ia_mapa_texto", "")

    status_game = st.session_state.dados.get("status_validacao_game", "rascunho")

    # Ações principais (centralizadas)
    colL, colM, colR = st.columns([1, 2, 1])
    with colM:
        st.markdown("### 🧩 Gerar / Revisar Missão")

    # -------------------------
    # 1) RASCUNHO — gerar
    # -------------------------
    if status_game == "rascunho":
        st.markdown(
            """
            **Como funciona**
            - A IA usa **hiperfoco + potências** para criar uma história motivadora.
            - O texto evita dados sensíveis e foca em **apoio, autonomia e rotina**.
            """
        )

        col1, col2 = st.columns([2, 1])
        with col1:
            st.caption("Você pode pedir um estilo específico (opcional).")
            estilo = st.text_input(
                "Preferência de estilo (opcional)",
                placeholder="Ex: super-heróis, exploração espacial, futebol, fantasia medieval...",
                key="gm_estilo"
            )
        with col2:
            st.write("")
            st.write("")
            gerar_btn = st.button("🎮 Criar Roteiro Gamificado", type="primary", use_container_width=True)

        if gerar_btn:
            with st.spinner("Game Master criando a missão..."):
                # feedback opcional entra como ajuste de estilo
                fb = (f"Estilo desejado: {estilo}." if estilo else "").strip()
                texto_game, err = gerar_roteiro_gamificado(api_key, st.session_state.dados, st.session_state.dados["ia_sugestao"], fb)

                if texto_game:
                    st.session_state.dados["ia_mapa_texto"] = texto_game.replace("[MAPA_TEXTO_GAMIFICADO]", "").strip()
                    st.session_state.dados["status_validacao_game"] = "revisao"
                    st.rerun()
                else:
                    st.error(err or "Erro desconhecido ao gerar a missão.")

    # -------------------------
    # 2) REVISÃO — aprovar/refazer
    # -------------------------
    elif status_game == "revisao":
        st.success("✅ Missão gerada! Revise abaixo e aprove/solicite ajustes.")

        with st.container(border=True):
            st.markdown("#### 📜 Missão (prévia)")
            st.markdown(st.session_state.dados.get("ia_mapa_texto", ""))

        st.divider()
        c_ok, c_aj = st.columns(2)
        with c_ok:
            if st.button("✅ Aprovar Missão", type="primary", use_container_width=True):
                st.session_state.dados["status_validacao_game"] = "aprovado"
                st.rerun()
        with c_aj:
            if st.button("✏️ Solicitar Ajustes", use_container_width=True):
                st.session_state.dados["status_validacao_game"] = "ajustando"
                st.rerun()

    # -------------------------
    # 3) AJUSTANDO — feedback e regerar
    # -------------------------
    elif status_game == "ajustando":
        st.warning("🛠️ Descreva o que você quer mudar e regenere a missão.")

        fb_game = st.text_area(
            "O que ajustar na missão?",
            value=st.session_state.dados.get("feedback_ajuste_game", ""),
            placeholder="Ex: deixe mais curto, use linguagem mais infantil, traga recompensas, troque o tema para futebol...",
            height=140
        )
        st.session_state.dados["feedback_ajuste_game"] = fb_game

        c1, c2 = st.columns([2, 1])
        with c1:
            if st.button("🔁 Regerar com Ajustes", type="primary", use_container_width=True):
                with st.spinner("Reescrevendo missão..."):
                    texto_game, err = gerar_roteiro_gamificado(
                        api_key,
                        st.session_state.dados,
                        st.session_state.dados["ia_sugestao"],
                        feedback_game=fb_game
                    )
                    if texto_game:
                        st.session_state.dados["ia_mapa_texto"] = texto_game.replace("[MAPA_TEXTO_GAMIFICADO]", "").strip()
                        st.session_state.dados["status_validacao_game"] = "revisao"
                        st.rerun()
                    else:
                        st.error(err or "Erro desconhecido ao regerar a missão.")
        with c2:
            if st.button("↩️ Voltar", use_container_width=True):
                st.session_state.dados["status_validacao_game"] = "revisao"
                st.rerun()

    # -------------------------
    # 4) APROVADO — exportar PDF e editar fino
    # -------------------------
    elif status_game == "aprovado":
        st.success("🏁 Missão aprovada! Agora você pode imprimir e entregar.")

        colA, colB = st.columns([2, 1])
        with colA:
            with st.container(border=True):
                st.markdown("#### 📜 Missão Final (editável)")
                novo_texto = st.text_area(
                    "Edição final manual (opcional)",
                    value=st.session_state.dados.get("ia_mapa_texto", ""),
                    height=320
                )
                st.session_state.dados["ia_mapa_texto"] = novo_texto

        with colB:
            with st.container(border=True):
                st.markdown("#### 📥 Exportação")
                pdf_mapa = gerar_pdf_tabuleiro_simples(st.session_state.dados["ia_mapa_texto"])
                st.download_button(
                    "📄 Baixar Missão em PDF",
                    pdf_mapa,
                    file_name=f"Missao_{nome_aluno}.pdf",
                    mime="application/pdf",
                    type="primary",
                    use_container_width=True
                )
                st.caption("Dica: imprima e cole no caderno / agenda do aluno.")
                st.write("---")
                if st.button("🆕 Criar Nova Missão", use_container_width=True):
                    st.session_state.dados["status_validacao_game"] = "rascunho"
                    st.session_state.dados["feedback_ajuste_game"] = ""
                    st.session_state.dados["ia_mapa_texto"] = ""
                    st.rerun()

    else:
        # fallback seguro
        st.session_state.dados["status_validacao_game"] = "rascunho"
        st.rerun()
