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
LISTA_FAMILIA = ["Mãe", "Mãe 2", "Pai", "Pai 2", "Madrasta", "Padrasto", "Avó Materna", "Avó Paterna", "Avô Materno", "Avô Paterno", "Irmãos", "Tios", "Primos", "Tutor Legal", "Abrigo Institucional"]

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
st.session_state.dados.setdefault("meds_extraidas_tmp", [])
st.session_state.dados.setdefault("status_meds_extraidas", "idle")


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
# 12. ABA ESTUDANTE (REFEITA com recursos do legado)
# ==============================================================================
with tab1:
    render_progresso()
    st.markdown("### <i class='ri-user-smile-line'></i> Dossiê do Estudante", unsafe_allow_html=True)

    # --------- Identificação ----------
    c1, c2, c3, c4 = st.columns([3, 2, 2, 1])

    st.session_state.dados["nome"] = c1.text_input("Nome Completo", st.session_state.dados.get("nome", ""))

    st.session_state.dados["nasc"] = c2.date_input(
        "Nascimento",
        value=st.session_state.dados.get("nasc", date(2015, 1, 1)),
    )

    try:
        serie_idx = LISTA_SERIES.index(st.session_state.dados.get("serie")) if st.session_state.dados.get("serie") in LISTA_SERIES else 0
    except Exception:
        serie_idx = 0

    st.session_state.dados["serie"] = c3.selectbox(
        "Série/Ano",
        LISTA_SERIES,
        index=serie_idx,
        placeholder="Selecione...",
    )

    if st.session_state.dados.get("serie"):
        nome_seg, cor_seg, desc_seg = get_segmento_info_visual(st.session_state.dados["serie"])
        c3.markdown(
            f"<div class='segmento-badge' style='background-color:{cor_seg}'>{nome_seg}</div>",
            unsafe_allow_html=True,
        )
        c3.caption(desc_seg)

    st.session_state.dados["turma"] = c4.text_input("Turma", st.session_state.dados.get("turma", ""))

    st.divider()

    # --------- Histórico & família ----------
    st.markdown("##### Histórico & Contexto Familiar")
    c_hist, c_fam = st.columns(2)

    st.session_state.dados["historico"] = c_hist.text_area(
        "Histórico Escolar",
        st.session_state.dados.get("historico", ""),
        height=160,
        placeholder="Ex: defasagens, adaptações anteriores, evolução, observações da equipe…",
    )

    st.session_state.dados["familia"] = c_fam.text_area(
        "Dinâmica Familiar",
        st.session_state.dados.get("familia", ""),
        height=160,
        placeholder="Ex: rotina, responsáveis, acompanhamento, comunicação com a escola…",
    )

    default_familia_valido = [x for x in st.session_state.dados.get("composicao_familiar_tags", []) if x in LISTA_FAMILIA]
    st.session_state.dados["composicao_familiar_tags"] = st.multiselect(
        "Quem convive com o aluno?",
        LISTA_FAMILIA,
        default=default_familia_valido,
    )

    st.divider()

    # --------- Upload de laudo + extração IA ----------
   # --------- Upload de laudo + extração IA (layout melhor + revisão meds) ----------
st.session_state.dados.setdefault("meds_extraidas_tmp", [])
st.session_state.dados.setdefault("status_meds_extraidas", "idle")

st.markdown("##### 📎 Laudo (PDF) + Extração Inteligente")
col_pdf, col_action = st.columns([2, 1], vertical_alignment="center")

with col_pdf:
    up = st.file_uploader(
    "Arraste o arquivo aqui",
    type="pdf",
    label_visibility="collapsed",
    key="pei_laudo_pdf_uploader",
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
        )

    if extrair:
        with st.spinner("Analisando laudo..."):
            dados_extraidos, erro = extrair_dados_pdf_ia(api_key, st.session_state.pdf_text)

        if dados_extraidos:
            # Diagnóstico
            if dados_extraidos.get("diagnostico"):
                st.session_state.dados["diagnostico"] = dados_extraidos["diagnostico"]

            # Medicamentos -> vão para revisão antes de salvar
            meds = dados_extraidos.get("medicamentos") or []
            meds_norm = []
            for med in meds:
                meds_norm.append({
                    "nome": (med.get("nome") or "").strip(),
                    "posologia": (med.get("posologia") or "").strip(),
                    "escola": False,  # usuário decide na revisão
                })

            st.session_state.dados["meds_extraidas_tmp"] = meds_norm
            st.session_state.dados["status_meds_extraidas"] = "review" if meds_norm else "idle"

            st.success("Diagnóstico extraído ✅ (medicações: revisar abaixo)")
            st.rerun()
        else:
            st.error(f"Erro: {erro}")

# --------- Revisão das meds extraídas ----------
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
            if a1.button("✅ Adicionar ao PEI", type="primary", use_container_width=True):
                for m in meds_tmp:
                    if (m.get("nome") or "").strip():
                        st.session_state.dados["lista_medicamentos"].append({
                            "nome": (m.get("nome") or "").strip(),
                            "posologia": (m.get("posologia") or "").strip(),
                            "escola": bool(m.get("escola", False)),
                        })
                st.session_state.dados["meds_extraidas_tmp"] = []
                st.session_state.dados["status_meds_extraidas"] = "idle"
                st.success("Medicações adicionadas ✅")
                st.rerun()

            if a2.button("🧹 Limpar lista extraída", use_container_width=True):
                st.session_state.dados["meds_extraidas_tmp"] = []
                st.session_state.dados["status_meds_extraidas"] = "idle"
                st.rerun()

            if a3.button("↩️ Voltar sem adicionar", use_container_width=True):
                st.session_state.dados["status_meds_extraidas"] = "idle"
                st.rerun()

    with col_pdf:
        st.markdown("**📎 Upload de Laudo (PDF)**")
        up = st.file_uploader(
            "Arraste o arquivo aqui",
            type="pdf",
            label_visibility="collapsed",
        )
        if up:
            st.session_state.pdf_text = ler_pdf(up)
            if st.session_state.pdf_text:
                st.success("PDF lido ✅ (usando até 6 páginas)")
            else:
                st.warning("Não consegui extrair texto do PDF (pode estar escaneado/imagem).")

    with col_btn_ia:
        st.write("")
        st.write("")
        if st.button(
            "✨ Extrair Dados do Laudo",
            type="primary",
            use_container_width=True,
            disabled=(not st.session_state.get("pdf_text")),
        ):
            with st.spinner("Analisando laudo..."):
                dados_extraidos, erro = extrair_dados_pdf_ia(api_key, st.session_state.pdf_text)

            if dados_extraidos:
                # Diagnóstico
                if dados_extraidos.get("diagnostico"):
                    st.session_state.dados["diagnostico"] = dados_extraidos["diagnostico"]

                # Medicamentos
                meds = dados_extraidos.get("medicamentos") or []
                if meds:
                    for med in meds:
                        st.session_state.dados["lista_medicamentos"].append(
                            {
                                "nome": (med.get("nome") or "").strip(),
                                "posologia": (med.get("posologia") or "").strip(),
                                "escola": False,
                            }
                        )

                st.success("Dados extraídos ✅")
                st.rerun()
            else:
                st.error(f"Erro: {erro}")

    st.divider()

    # --------- Contexto clínico + medicação ----------
    st.markdown("##### Contexto Clínico")
    st.session_state.dados["diagnostico"] = st.text_input(
        "Diagnóstico",
        st.session_state.dados.get("diagnostico", ""),
        placeholder="Ex: TEA nível 1, TDAH, Dislexia… (se houver CID, cole também)",
    )

    with st.container(border=True):
        usa_med = st.toggle(
            "💊 O aluno faz uso contínuo de medicação?",
            value=len(st.session_state.dados.get("lista_medicamentos", [])) > 0,
        )

        if usa_med:
            c_m1, c_m2, c_m3 = st.columns([3, 2, 2])
            nm = c_m1.text_input("Nome", key="nm_med")
            pos = c_m2.text_input("Posologia", key="pos_med")
            admin_escola = c_m3.checkbox("Na escola?", key="adm_esc")

            if st.button("Adicionar", use_container_width=False):
                if not nm.strip():
                    st.warning("Informe o nome do medicamento.")
                else:
                    st.session_state.dados["lista_medicamentos"].append(
                        {"nome": nm.strip(), "posologia": pos.strip(), "escola": bool(admin_escola)}
                    )
                    st.rerun()

        # Lista e excluir
        meds_list = st.session_state.dados.get("lista_medicamentos", [])
        if meds_list:
            st.write("---")
            for i, m in enumerate(list(meds_list)):
                tag = " [NA ESCOLA]" if m.get("escola") else ""
                c_txt, c_btn = st.columns([5, 1])
                c_txt.info(f"💊 **{m.get('nome','')}** ({m.get('posologia','')}){tag}")
                if c_btn.button("Excluir", key=f"del_{i}"):
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

    default_prof = [x for x in (st.session_state.dados.get("rede_apoio") or []) if x in LISTA_PROFISSIONAIS]
    st.session_state.dados["rede_apoio"] = st.multiselect(
        "Profissionais envolvidos:",
        LISTA_PROFISSIONAIS,
        default=default_prof,
    )

    if st.session_state.dados["rede_apoio"]:
        st.markdown("##### Visão rápida")
        cols = st.columns(3)
        for i, p in enumerate(st.session_state.dados["rede_apoio"]):
            cols[i % 3].markdown(f"- {get_pro_icon(p)} **{p}**")

# ==============================================================================
# 15. ABA MAPEAMENTO (COMPLETA: hiperfoco + potências + barreiras + nível de suporte)
# ==============================================================================
with tab4:
    render_progresso()
    st.markdown("### <i class='ri-radar-line'></i> Mapeamento", unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    st.session_state.dados["hiperfoco"] = c1.text_input("Hiperfoco", st.session_state.dados.get("hiperfoco", ""))
    emoji = get_hiperfoco_emoji(st.session_state.dados.get("hiperfoco"))
    c1.caption(f"{emoji} Use o hiperfoco como alavanca de engajamento.")

    default_pot = [x for x in (st.session_state.dados.get("potencias") or []) if x in LISTA_POTENCIAS]
    st.session_state.dados["potencias"] = c2.multiselect("Potencialidades", LISTA_POTENCIAS, default=default_pot)

    st.divider()
    st.markdown("##### Barreiras (CIF) + Nível de Suporte")

    for area, itens in LISTAS_BARREIRAS.items():
        with st.container(border=True):
            st.markdown(f"**{area}**")

            selecionadas = st.multiselect(
                "Barreiras",
                itens,
                default=st.session_state.dados["barreiras_selecionadas"].get(area, []),
                key=f"bar_{area}",
            )
            st.session_state.dados["barreiras_selecionadas"][area] = selecionadas

            if selecionadas:
                st.caption("Defina o nível de suporte para cada barreira selecionada:")
            for b in selecionadas:
                st.session_state.dados["niveis_suporte"][f"{area}_{b}"] = st.select_slider(
                    f"Nível de suporte — {b}",
                    ["Autônomo", "Monitorado", "Substancial", "Muito Substancial"],
                    value=st.session_state.dados["niveis_suporte"].get(f"{area}_{b}", "Monitorado"),
                    key=f"sup_{area}_{b}",
                )

    st.divider()
    nivel, bg, cor = calcular_complexidade_pei(st.session_state.dados)
    st.markdown(
        f"<div style='background:{bg}; border:1px solid #E2E8F0; padding:14px; border-radius:14px;'>"
        f"<b>Complexidade do PEI:</b> <span style='color:{cor}; font-weight:900;'>{nivel}</span>"
        f"</div>",
        unsafe_allow_html=True,
    )


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
# 19. ABA DASHBOARD & DOCS (KPIs + Exportações)
# ==============================================================================
with tab8:
    render_progresso()
    st.markdown("### <i class='ri-file-pdf-line'></i> Dashboard e Exportação", unsafe_allow_html=True)

    dados = st.session_state.dados

    # ---------------- KPIs ----------------
    st.markdown("#### 📊 Indicadores do PEI")
    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Barreiras Ativas", sum(len(v) for v in dados.get("barreiras_selecionadas", {}).values()))
    c2.metric("Estratégias (Ensino)", len(dados.get("estrategias_ensino", [])))
    c3.metric("Rede de Apoio", len(dados.get("rede_apoio", [])))
    c4.metric("Potencialidades", len(dados.get("potencias", [])))

    st.divider()

    # ---------------- Metas SMART ----------------
    st.markdown("#### 🎯 Metas SMART (extraídas da IA)")
    metas = extrair_metas_estruturadas(dados.get("ia_sugestao", ""))

    mc1, mc2, mc3 = st.columns(3)
    mc1.info(f"**Curto Prazo**\n\n{metas.get('Curto')}")
    mc2.info(f"**Médio Prazo**\n\n{metas.get('Medio')}")
    mc3.info(f"**Longo Prazo**\n\n{metas.get('Longo')}")

    st.divider()

    # ---------------- Componentes Impactados ----------------
    st.markdown("#### 📚 Componentes Curriculares Impactados")
    comps = inferir_componentes_impactados(dados)
    for c in comps:
        st.markdown(f"- {c}")

    st.divider()

    # ---------------- Exportações ----------------
    st.markdown("#### 📤 Exportar Documentos")

    ec1, ec2, ec3 = st.columns(3)

    with ec1:
        if st.button("📄 Gerar PDF Oficial", use_container_width=True, type="primary"):
            if not dados.get("ia_sugestao"):
                st.warning("Gere o PEI na aba Consultoria IA antes.")
            else:
                pdf_bytes = gerar_pdf_final(dados)
                st.download_button(
                    "⬇️ Download PDF",
                    pdf_bytes,
                    file_name=f"PEI_{dados.get('nome','estudante')}.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                )

    with ec2:
        if st.button("📝 Gerar Word (.docx)", use_container_width=True):
            if not dados.get("ia_sugestao"):
                st.warning("Gere o PEI na aba Consultoria IA antes.")
            else:
                docx_io = gerar_docx_final(dados)
                st.download_button(
                    "⬇️ Download DOCX",
                    docx_io,
                    file_name=f"PEI_{dados.get('nome','estudante')}.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    use_container_width=True,
                )

    with ec3:
        st.download_button(
            "💾 Backup JSON",
            json.dumps(dados, ensure_ascii=False, indent=2, default=str),
            file_name=f"PEI_{dados.get('nome','estudante')}.json",
            mime="application/json",
            use_container_width=True,
        )

    st.divider()
    st.caption("⚠️ Os documentos exportados devem ser revisados e assinados pela equipe pedagógica.")


# ==============================================================================
# 20. ABA JORNADA GAMIFICADA (Roteiro + PDF)
# ==============================================================================
with tab_mapa:
    render_progresso()
    st.markdown("### <i class='ri-gamepad-line'></i> Jornada Gamificada", unsafe_allow_html=True)

    dados = st.session_state.dados
    st.session_state.dados.setdefault("status_validacao_game", "rascunho")
    st.session_state.dados.setdefault("feedback_ajuste_game", "")

    if not dados.get("ia_sugestao"):
        st.warning("⚠️ Gere primeiro o PEI Técnico na aba **Consultoria IA**.")
        st.stop()

    if not api_key:
        st.error("Configure a chave OpenAI na sidebar.")
        st.stop()

    # --------- Geração ----------
    if dados.get("status_validacao_game") == "rascunho":
        if st.button("🎮 Gerar Jornada Gamificada", type="primary", use_container_width=True):
            texto, err = gerar_roteiro_gamificado(
                api_key,
                dados,
                dados.get("ia_sugestao", ""),
            )
            if texto:
                st.session_state.dados["ia_mapa_texto"] = texto
                st.session_state.dados["status_validacao_game"] = "revisao"
                st.rerun()
            else:
                st.error(err or "Erro ao gerar jornada.")

    # --------- Revisão ----------
    elif dados.get("status_validacao_game") == "revisao":
        st.markdown("#### 🗺️ Roteiro Gerado")
        st.markdown(dados.get("ia_mapa_texto", ""))

        c1, c2 = st.columns(2)
        if c1.button("✅ Aprovar Jornada", type="primary", use_container_width=True):
            st.session_state.dados["status_validacao_game"] = "aprovado"
            st.rerun()
        if c2.button("❌ Solicitar Ajuste", use_container_width=True):
            st.session_state.dados["status_validacao_game"] = "ajustando"
            st.rerun()

    # --------- Ajuste ----------
    elif dados.get("status_validacao_game") == "ajustando":
        st.warning("Descreva o ajuste desejado:")
        fb = st.text_area("Feedback:", placeholder="Ex: mais visual, menos texto…")
        if st.button("Regerar Jornada", type="primary", use_container_width=True):
            texto, err = gerar_roteiro_gamificado(
                api_key,
                dados,
                dados.get("ia_sugestao", ""),
                feedback_game=fb,
            )
            if texto:
                st.session_state.dados["ia_mapa_texto"] = texto
                st.session_state.dados["status_validacao_game"] = "revisao"
                st.rerun()
            else:
                st.error(err or "Erro ao regerar.")

        if st.button("Cancelar", use_container_width=True):
            st.session_state.dados["status_validacao_game"] = "revisao"
            st.rerun()

    # --------- Aprovado ----------
    elif dados.get("status_validacao_game") == "aprovado":
        st.success("🎉 Jornada aprovada!")
        texto_edit = st.text_area(
            "Edição Final (opcional)",
            value=dados.get("ia_mapa_texto", ""),
            height=320,
        )
        st.session_state.dados["ia_mapa_texto"] = texto_edit

        pdf_game = gerar_pdf_tabuleiro_simples(texto_edit)
        st.download_button(
            "⬇️ Baixar Jornada (PDF)",
            pdf_game,
            file_name=f"Jornada_{dados.get('nome','estudante')}.pdf",
            mime="application/pdf",
            use_container_width=True,
        )

        if st.button("🔁 Refazer Jornada", use_container_width=True):
            st.session_state.dados["status_validacao_game"] = "rascunho"
            st.rerun()
