import streamlit as st
from datetime import date
from io import BytesIO
from docx import Document
from openai import OpenAI
from pypdf import PdfReader
from fpdf import FPDF
import base64
import json
import os
import re

from _client import get_supabase_user

# ==============================================================================
# 0. CONFIGURAÇÃO DE PÁGINA
# ==============================================================================
st.set_page_config(
    page_title="Omnisfera | PEI",
    page_icon="📘",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==============================================================================
# 1. GUARDAS (LOGIN + SUPABASE)
# ==============================================================================
def verificar_login_app():
    if "autenticado" not in st.session_state or not st.session_state["autenticado"]:
        st.error("🔒 Acesso Negado. Faça login na Página Inicial.")
        st.stop()

def verificar_login_supabase():
    # Supabase é necessário para SALVAR/CARREGAR, mas o PEI pode abrir como rascunho.
    # Então aqui só avisamos, não bloqueamos tudo.
    if "supabase_jwt" not in st.session_state or not st.session_state["supabase_jwt"]:
        st.session_state["supabase_jwt"] = ""
    if "supabase_user_id" not in st.session_state or not st.session_state["supabase_user_id"]:
        st.session_state["supabase_user_id"] = ""

verificar_login_app()
verificar_login_supabase()

def sb():
    return get_supabase_user(st.session_state["supabase_jwt"])

OWNER_ID = st.session_state.get("supabase_user_id", "")

# ==============================================================================
# 2. SUPABASE: STUDENTS (criar/atualizar/listar)
# ==============================================================================
def db_create_student(payload: dict):
    res = sb().table("students").insert(payload).execute()
    return (res.data or [None])[0]

def db_update_student(student_id: str, payload: dict):
    sb().table("students").update(payload).eq("id", student_id).eq("owner_id", OWNER_ID).execute()

def db_list_students(search: str | None = None):
    q = (
        sb()
        .table("students")
        .select("id, owner_id, name, birth_date, grade, class_group, diagnosis, created_at, updated_at")
        .eq("owner_id", OWNER_ID)
        .order("name", desc=False)
    )
    if search:
        q = q.ilike("name", f"%{search}%")
    res = q.execute()
    return res.data or []

def db_get_student(student_id: str):
    res = (
        sb()
        .table("students")
        .select("id, owner_id, name, birth_date, grade, class_group, diagnosis, created_at, updated_at")
        .eq("id", student_id)
        .eq("owner_id", OWNER_ID)
        .limit(1)
        .execute()
    )
    data = res.data or []
    return data[0] if data else None

# ==============================================================================
# 3. BLOCO VISUAL (badge / logo)
# ==============================================================================
try:
    IS_TEST_ENV = st.secrets.get("ENV") == "TESTE"
except:
    IS_TEST_ENV = False

def get_logo_base64():
    caminhos = ["omni_icone.png", "logo.png", "iconeaba.png"]
    for c in caminhos:
        if os.path.exists(c):
            with open(c, "rb") as f:
                return f"data:image/png;base64,{base64.b64encode(f.read()).decode()}"
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
LISTA_FAMILIA = ["Mãe", "Pai", "Madrasta", "Padrasto", "Avó Materna", "Avó Paterna", "Avô Materno", "Avô Paterno", "Irmãos", "Tios", "Primos", "Tutor Legal", "Abrigo Institucional"]

# ==============================================================================
# 5. ESTADO DEFAULT (RASCUNHO)
# ==============================================================================
default_state = {
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

if 'dados' not in st.session_state:
    st.session_state.dados = default_state
else:
    for k, v in default_state.items():
        if k not in st.session_state.dados:
            st.session_state.dados[k] = v

if 'pdf_text' not in st.session_state:
    st.session_state.pdf_text = ""

# Estado do vínculo com Supabase (só após sincronizar)
st.session_state.setdefault("selected_student_id", None)
st.session_state.setdefault("selected_student_name", "")

# ==============================================================================
# 6. SUPABASE: carregar/salvar PEI (pei_documents) - SÓ QUANDO VINCULADO
# ==============================================================================
def supa_load_latest_pei(student_id: str):
    res = (
        sb()
        .table("pei_documents")
        .select("*")
        .eq("student_id", student_id)
        .eq("owner_id", OWNER_ID)
        .order("updated_at", desc=True)
        .limit(1)
        .execute()
    )
    data = res.data or []
    return data[0] if data else None

def supa_save_pei(student_id: str, payload: dict, pdf_text: str):
    def _jsonify(x):
        return json.loads(json.dumps(x, default=str))

    safe_payload = _jsonify(payload)
    year = date.today().year

    existing = supa_load_latest_pei(student_id)
    if existing:
        sb().table("pei_documents").update({
            "payload": safe_payload,
            "pdf_text": (pdf_text or "")[:20000],
            "school_year": year,
            "status": payload.get("status_validacao_pei", "draft"),
        }).eq("id", existing["id"]).execute()
    else:
        sb().table("pei_documents").insert({
            "owner_id": OWNER_ID,
            "student_id": student_id,
            "school_year": year,
            "status": payload.get("status_validacao_pei", "draft"),
            "payload": safe_payload,
            "pdf_text": (pdf_text or "")[:20000],
        }).execute()

def supa_sync_student_from_dados(student_id: str, d: dict):
    db_update_student(student_id, {
        "name": d.get("nome"),
        "birth_date": d.get("nasc").isoformat() if hasattr(d.get("nasc"), "isoformat") else d.get("nasc"),
        "grade": d.get("serie"),
        "class_group": d.get("turma"),
        "diagnosis": d.get("diagnostico"),
    })

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
# 9. SIDEBAR (RASCUNHO -> SINCRONIZA)
# ==============================================================================
with st.sidebar:
    st.markdown("### 👤 Sessão")
    st.caption(f"Usuário: **{st.session_state.get('usuario_nome','')}**")

    st.markdown("---")
    st.markdown("### 🧾 Status do Aluno")
    student_id = st.session_state.get("selected_student_id")

    if student_id:
        st.success("✅ Vinculado ao Supabase")
        st.caption(f"student_id: {student_id[:8]}...")
    else:
        st.warning("📝 Rascunho (ainda não salvo no Supabase)")

    st.markdown("---")
    # OpenAI
    if 'OPENAI_API_KEY' in st.secrets:
        api_key = st.secrets['OPENAI_API_KEY']
        st.success("✅ OpenAI OK")
    else:
        api_key = st.text_input("Chave OpenAI:", type="password")

    st.markdown("---")
    st.markdown("### 🔗 Sincronização (Criar no Supabase)")
    if not st.session_state.get("supabase_jwt") or not st.session_state.get("supabase_user_id"):
        st.info("Faça login Supabase na Home para habilitar sincronização/salvar.")
    else:
        if not student_id:
            if st.button("🔗 Sincronizar agora (criar aluno)", use_container_width=True, type="primary"):
                # validações mínimas
                if not st.session_state.dados.get("nome"):
                    st.warning("Preencha o NOME do estudante na aba Estudante antes de sincronizar.")
                elif not st.session_state.dados.get("serie"):
                    st.warning("Selecione a SÉRIE/Ano na aba Estudante antes de sincronizar.")
                else:
                    created = db_create_student({
                        "owner_id": OWNER_ID,
                        "name": st.session_state.dados.get("nome"),
                        "birth_date": st.session_state.dados.get("nasc").isoformat(),
                        "grade": st.session_state.dados.get("serie"),
                        "class_group": st.session_state.dados.get("turma") or None,
                        "diagnosis": st.session_state.dados.get("diagnostico") or None
                    })
                    if created and created.get("id"):
                        st.session_state["selected_student_id"] = created["id"]
                        st.session_state["selected_student_name"] = created.get("name") or ""
                        st.success("Sincronizado ✅ Agora você pode salvar/carregar.")
                        st.rerun()
                    else:
                        st.error("Falha ao criar aluno. Verifique RLS/policies no Supabase.")
        else:
            st.caption("Aluno já sincronizado. Use Salvar/Carregar abaixo.")

    st.markdown("---")
    st.markdown("### 💾 Supabase (PEI)")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("💾 Salvar", use_container_width=True, type="primary", disabled=(not student_id)):
            with st.spinner("Salvando..."):
                supa_save_pei(student_id, st.session_state.dados, st.session_state.get("pdf_text", ""))
                supa_sync_student_from_dados(student_id, st.session_state.dados)
            st.success("Salvo no Supabase ✅")
    with c2:
        if st.button("🔄 Carregar", use_container_width=True, disabled=(not student_id)):
            with st.spinner("Carregando..."):
                row = supa_load_latest_pei(student_id)
            if row and row.get("payload"):
                payload = row["payload"]
                try:
                    if payload.get("nasc"):
                        payload["nasc"] = date.fromisoformat(payload["nasc"])
                except:
                    pass
                try:
                    if payload.get("monitoramento_data"):
                        payload["monitoramento_data"] = date.fromisoformat(payload["monitoramento_data"])
                except:
                    pass
                st.session_state.dados.update(payload)
                st.session_state.pdf_text = row.get("pdf_text") or ""
                st.success("Carregado ✅")
                st.rerun()
            else:
                st.info("Ainda não existe PEI salvo para este aluno.")

    st.markdown("---")
    st.markdown("### 🧭 Navegação")
    if st.button("🏠 Home", use_container_width=True):
        st.switch_page("Home.py")

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
# 11. ABA INÍCIO
# ==============================================================================
with tab0:
    st.markdown("### 🏛️ Central de Fundamentos e Legislação")
    if not st.session_state.get("selected_student_id"):
        st.warning("📝 Você está em modo rascunho. Preencha o aluno e clique em **Sincronizar** na sidebar para salvar no banco.")
    else:
        st.success("✅ Aluno sincronizado. Salvar/Carregar liberados.")

# ==============================================================================
# 12. ABA ESTUDANTE (AGORA É ONDE SE CRIA O ALUNO)
# ==============================================================================
with tab1:
    render_progresso()
    st.markdown("### <i class='ri-user-smile-line'></i> Dossiê do Estudante", unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns([3, 2, 2, 1])
    st.session_state.dados['nome'] = c1.text_input("Nome Completo", st.session_state.dados['nome'])
    st.session_state.dados['nasc'] = c2.date_input("Nascimento", value=st.session_state.dados.get('nasc', date(2015, 1, 1)))

    try:
        serie_idx = LISTA_SERIES.index(st.session_state.dados['serie']) if st.session_state.dados['serie'] in LISTA_SERIES else 0
    except:
        serie_idx = 0

    st.session_state.dados['serie'] = c3.selectbox("Série/Ano", LISTA_SERIES, index=serie_idx, placeholder="Selecione...")
    st.session_state.dados['turma'] = c4.text_input("Turma", st.session_state.dados['turma'])

    st.divider()
    st.markdown("##### Contexto Clínico")
    st.session_state.dados['diagnostico'] = st.text_input("Diagnóstico", st.session_state.dados['diagnostico'])

# ==============================================================================
# 13. ABA EVIDÊNCIAS
# ==============================================================================
with tab2:
    render_progresso()
    st.markdown("### <i class='ri-search-eye-line'></i> Coleta de Evidências", unsafe_allow_html=True)

    st.session_state.dados['nivel_alfabetizacao'] = st.selectbox(
        "Hipótese de Escrita",
        LISTA_ALFABETIZACAO,
        index=LISTA_ALFABETIZACAO.index(st.session_state.dados['nivel_alfabetizacao']) if st.session_state.dados['nivel_alfabetizacao'] in LISTA_ALFABETIZACAO else 0
    )

# ==============================================================================
# 14. ABA REDE DE APOIO
# ==============================================================================
with tab3:
    render_progresso()
    st.markdown("### <i class='ri-team-line'></i> Rede de Apoio", unsafe_allow_html=True)
    st.session_state.dados['rede_apoio'] = st.multiselect("Profissionais:", LISTA_PROFISSIONAIS, default=st.session_state.dados['rede_apoio'])

# ==============================================================================
# 15. ABA MAPEAMENTO
# ==============================================================================
with tab4:
    render_progresso()
    st.markdown("### <i class='ri-radar-line'></i> Mapeamento", unsafe_allow_html=True)

# ==============================================================================
# 16. ABA PLANO DE AÇÃO
# ==============================================================================
with tab5:
    render_progresso()
    st.markdown("### <i class='ri-tools-line'></i> Plano de Ação", unsafe_allow_html=True)

# ==============================================================================
# 17. ABA MONITORAMENTO
# ==============================================================================
with tab6:
    render_progresso()
    st.markdown("### <i class='ri-loop-right-line'></i> Monitoramento", unsafe_allow_html=True)

# ==============================================================================
# 18. ABA CONSULTORIA IA (mantida mínima)
# ==============================================================================
with tab7:
    render_progresso()
    st.markdown("### <i class='ri-robot-2-line'></i> Consultoria Pedagógica", unsafe_allow_html=True)
    st.info("Nesta versão compacta, a geração de IA será reativada no próximo ajuste (ponto 2).")

# ==============================================================================
# 19. ABA DASHBOARD & DOCS (mantida mínima)
# ==============================================================================
with tab8:
    render_progresso()
    st.markdown("### <i class='ri-file-pdf-line'></i> Dashboard e Exportação", unsafe_allow_html=True)
    st.info("Exportação completa será reativada no próximo ajuste (ponto 2).")

# ==============================================================================
# 20. FOOTER
# ==============================================================================
st.markdown(
    "<div class='footer-signature'>PEI 360º v116.0 Gold Edition - Desenvolvido por Rodrigo A. Queiroz</div>",
    unsafe_allow_html=True
)
