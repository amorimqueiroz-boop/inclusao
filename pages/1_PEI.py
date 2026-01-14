import streamlit as st
from datetime import date
from io import BytesIO
from docx import Document
from docx.shared import Pt
from openai import OpenAI
from pypdf import PdfReader
from fpdf import FPDF
import base64
import json
import os
import re
import glob
import random
import requests

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
# ### BLOCO VISUAL E UTILITÁRIOS ###
# ==============================================================================
# 1. Detecção Automática de Ambiente
try:
    IS_TEST_ENV = st.secrets.get("ENV") == "TESTE"
except:
    IS_TEST_ENV = False

# 2. Função para carregar a logo em Base64
def get_logo_base64():
    caminhos = ["omni_icone.png", "logo.png", "iconeaba.png"]
    for c in caminhos:
        if os.path.exists(c):
            with open(c, "rb") as f:
                return f"data:image/png;base64,{base64.b64encode(f.read()).decode()}"
    return "https://cdn-icons-png.flaticon.com/512/1183/1183672.png"

src_logo_giratoria = get_logo_base64()

# 3. Definição Dinâmica de Cores
if IS_TEST_ENV:
    card_bg = "rgba(255, 220, 50, 0.95)" 
    card_border = "rgba(200, 160, 0, 0.5)"
else:
    card_bg = "rgba(255, 255, 255, 0.85)"
    card_border = "rgba(255, 255, 255, 0.6)"

# 4. Verificação de Acesso
def verificar_acesso():
    if "autenticado" not in st.session_state or not st.session_state["autenticado"]:
        st.error("🔒 Acesso Negado. Por favor, faça login na Página Inicial.")
        st.stop()

verificar_acesso()

# ==============================================================================
# 2. LÓGICA DO BANCO DE DADOS
# ==============================================================================
ARQUIVO_DB_CENTRAL = "banco_alunos.json"
PASTA_BANCO = "banco_alunos_backup"

if not os.path.exists(PASTA_BANCO): os.makedirs(PASTA_BANCO)

def carregar_banco():
    if os.path.exists(ARQUIVO_DB_CENTRAL):
        try:
            with open(ARQUIVO_DB_CENTRAL, "r", encoding="utf-8") as f:
                return json.load(f)
        except: return []
    return []

if 'banco_estudantes' not in st.session_state or not st.session_state.banco_estudantes:
    st.session_state.banco_estudantes = carregar_banco()

def salvar_aluno_integrado(dados):
    if not dados['nome']: return False, "Nome é obrigatório."
    
    # Backup Local
    nome_arq = re.sub(r'[^a-zA-Z0-9]', '_', dados['nome'].lower()) + ".json"
    try:
        with open(os.path.join(PASTA_BANCO, nome_arq), 'w', encoding='utf-8') as f:
            json.dump(dados, f, default=str, ensure_ascii=False, indent=4)
    except Exception as e: return False, f"Erro backup: {str(e)}"

    # Integração Omnisfera
    st.session_state.banco_estudantes = [a for a in st.session_state.banco_estudantes if a['nome'] != dados['nome']]
    novo_registro = {
        "nome": dados['nome'],
        "serie": dados.get('serie', ''),
        "hiperfoco": dados.get('hiperfoco', ''),
        "ia_sugestao": dados.get('ia_sugestao', ''),
        "diagnostico": dados.get('diagnostico', ''),
        "responsavel": st.session_state.get("usuario_nome", "Desconhecido"),
        "data_criacao": str(date.today())
    }
    st.session_state.banco_estudantes.append(novo_registro)
    
    try:
        with open(ARQUIVO_DB_CENTRAL, "w", encoding="utf-8") as f:
            json.dump(st.session_state.banco_estudantes, f, default=str, ensure_ascii=False, indent=4)
        return True, f"Aluno {dados['nome']} integrado à Omnisfera!"
    except Exception as e:
        return False, f"Erro integração: {str(e)}"

# ==============================================================================
# 3. LISTAS E GERENCIAMENTO DE ESTADO
# ==============================================================================
LISTA_SERIES = [
    "Educação Infantil (Creche)", "Educação Infantil (Pré-Escola)", 
    "1º Ano (Fund. I)", "2º Ano (Fund. I)", "3º Ano (Fund. I)", "4º Ano (Fund. I)", "5º Ano (Fund. I)", 
    "6º Ano (Fund. II)", "7º Ano (Fund. II)", "8º Ano (Fund. II)", "9º Ano (Fund. II)", 
    "1ª Série (EM)", "2ª Série (EM)", "3ª Série (EM)", "EJA (Educação de Jovens e Adultos)"
]
LISTA_ALFABETIZACAO = ["Não se aplica (EI)", "Pré-Silábico", "Silábico", "Silábico-Alfabético", "Alfabético", "Ortográfico"]
LISTAS_BARREIRAS = {
    "Funções Cognitivas": ["Atenção", "Memória", "Flexibilidade"],
    "Comunicação": ["Fala", "Compreensão", "Pragmática"],
    "Socioemocional": ["Regulação", "Interação", "Autoestima"],
    "Sensorial/Motor": ["Coordenação", "Hipersensibilidade", "Planejamento Motor"],
    "Acadêmico": ["Leitura", "Escrita", "Raciocínio"]
}
LISTA_POTENCIAS = ["Memória Visual", "Musicalidade", "Tecnologia", "Hiperfoco", "Liderança", "Esportes", "Artes", "Oralidade", "Criatividade", "Empatia"]
LISTA_PROFISSIONAIS = ["Psicólogo", "Fonoaudiólogo", "Terapeuta Ocupacional", "Neuropediatra", "Psicopedagogo", "Prof. Apoio"]
LISTA_FAMILIA = ["Mãe", "Pai", "Avós", "Irmãos", "Tios", "Tutor"]

default_state = {
    'nome': '', 'nasc': date(2015, 1, 1), 'serie': None, 'turma': '', 'diagnostico': '', 
    'lista_medicamentos': [], 'composicao_familiar_tags': [], 'historico': '', 'familia': '', 
    'hiperfoco': '', 'potencias': [], 'rede_apoio': [], 'orientacoes_especialistas': '',
    'checklist_evidencias': {}, 'nivel_alfabetizacao': 'Não se aplica (EI)',
    'barreiras_selecionadas': {k: [] for k in LISTAS_BARREIRAS.keys()},
    'niveis_suporte': {}, 'estrategias_acesso': [], 'estrategias_ensino': [], 'estrategias_avaliacao': [], 
    'ia_sugestao': '', 'ia_mapa_texto': '', 'outros_acesso': '', 'outros_ensino': '', 
    'monitoramento_data': date.today(), 'status_meta': 'Não Iniciado', 'parecer_geral': 'Manter Estratégias', 'proximos_passos_select': []
}

if 'dados' not in st.session_state: st.session_state.dados = default_state
else:
    for key, val in default_state.items():
        if key not in st.session_state.dados: st.session_state.dados[key] = val

if 'pdf_text' not in st.session_state: st.session_state.pdf_text = ""

# ==============================================================================
# 4. FUNÇÕES UTILITÁRIAS
# ==============================================================================
def calcular_idade(data_nasc):
    if not data_nasc: return ""
    hoje = date.today()
    idade = hoje.year - data_nasc.year - ((hoje.month, hoje.day) < (data_nasc.month, data_nasc.day))
    return f"{idade} anos"

def get_hiperfoco_emoji(texto):
    if not texto: return "🚀"
    t = texto.lower()
    if "jogo" in t: return "🎮"
    if "dino" in t: return "🦖"
    return "🚀"

def detecting_nivel_ensino(serie_str): # Mantendo nome antigo para compatibilidade
    return detectar_nivel_ensino(serie_str)

def detectar_nivel_ensino(serie_str):
    if not serie_str: return "INDEFINIDO"
    s = serie_str.lower()
    if "infantil" in s: return "EI"
    if "1º" in s or "2º" in s or "3º" in s or "4º" in s or "5º" in s: return "FI"
    if "6º" in s or "7º" in s or "8º" in s or "9º" in s: return "FII"
    if "série" in s or "médio" in s or "eja" in s: return "EM"
    return "INDEFINIDO"

def get_segmento_info_visual(serie):
    nivel = detectar_nivel_ensino(serie)
    if nivel == "EI": return "Educação Infantil", "#4299e1", "Foco: Campos de Experiência e Desenvolvimento Integral."
    elif nivel == "FI": return "Anos Iniciais", "#48bb78", "Foco: Alfabetização e Habilidades."
    elif nivel == "FII": return "Anos Finais", "#ed8936", "Foco: Autonomia e Identidade."
    elif nivel == "EM": return "Ensino Médio", "#9f7aea", "Foco: Projeto de Vida."
    return "Selecione a Série", "grey", "..."

def calcular_complexidade_pei(dados):
    n_bar = sum(len(v) for v in dados['barreiras_selecionadas'].values())
    saldo = n_bar - (3 if dados['rede_apoio'] else 0)
    if saldo <= 2: return "FLUIDA", "#F0FFF4", "#276749"
    if saldo <= 7: return "ATENÇÃO", "#FFFFF0", "#D69E2E"
    return "CRÍTICA", "#FFF5F5", "#C53030"

def finding_logo():
    caminhos = ["omni_icone.png", "logo.png"]
    for c in caminhos:
        if os.path.exists(c): return c
    return None

def get_base64_image(path):
    if path and os.path.exists(path):
        with open(path, "rb") as f: return base64.b64encode(f.read()).decode()
    return ""

def ler_pdf(uploaded):
    try:
        reader = PdfReader(uploaded); text = ""
        for p in reader.pages[:5]: text += p.extract_text() + "\n"
        return text
    except: return ""

def extrair_tag_ia(texto, tag):
    match = re.search(fr'\[{tag}\](.*?)(\[|$)', texto, re.DOTALL)
    return match.group(1).strip() if match else ""

def extrair_metas_estruturadas(texto):
    raw = extrair_tag_ia(texto, "METAS_SMART")
    if not raw: return None
    metas = {"Curto": "...", "Medio": "...", "Longo": "..."}
    for l in raw.split('\n'):
        if "Curto" in l: metas["Curto"] = l.split(":")[-1].strip()
        elif "Médio" in l: metas["Medio"] = l.split(":")[-1].strip()
        elif "Longo" in l: metas["Longo"] = l.split(":")[-1].strip()
    return metas

def calcular_progresso():
    return 100 if st.session_state.dados['ia_sugestao'] else 20

# ----------------- ATUALIZAÇÃO DA BARRA DE PROGRESSO COM LOGO -----------------
def render_progresso():
    p = calcular_progresso()
    # Substituindo emoji pela logo giratória
    icon_html = f'<img src="{src_logo_giratoria}" class="prog-logo-spin">'
    
    bar_color = "linear-gradient(90deg, #FF6B6B 0%, #FF8E53 100%)"
    if p >= 100: bar_color = "linear-gradient(90deg, #00C6FF 0%, #0072FF 100%)"
    
    st.markdown(f"""
    <div class="prog-container">
        <div class="prog-track">
            <div class="prog-fill" style="width: {p}%; background: {bar_color};"></div>
        </div>
        <div class="prog-icon" style="left: {p}%;">{icon_html}</div>
    </div>
    """, unsafe_allow_html=True)

# ==============================================================================
# 5. ESTILO VISUAL
# ==============================================================================
def aplicar_estilo_visual():
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800&display=swap');
        html, body, [class*="css"] { font-family: 'Nunito', sans-serif; color: #2D3748; background-color: #F7FAFC; }
        .block-container { padding-top: 1.5rem !important; padding-bottom: 5rem !important; }
        
        /* HEADER UNIFICADO */
        .header-unified { background-color: white; padding: 20px 40px; border-radius: 16px; border: 1px solid #E2E8F0; box-shadow: 0 2px 10px rgba(0,0,0,0.02); margin-bottom: 20px; display: flex; align-items: center; gap: 20px; }
        .header-subtitle { font-size: 1.2rem; color: #718096; font-weight: 600; border-left: 2px solid #E2E8F0; padding-left: 20px; line-height: 1.2; }

        /* ABAS EM PÍLULA (COM SCROLL CORRIGIDO) */
        div[data-baseweb="tab-border"], div[data-baseweb="tab-highlight"] { display: none !important; }
        .stTabs [data-baseweb="tab-list"] { 
            gap: 8px; display: flex; flex-wrap: nowrap; overflow-x: auto; white-space: nowrap; 
            padding: 10px 5px; -ms-overflow-style: none; scrollbar-width: auto; /* Scroll visível se necessário */
        }
        .stTabs [data-baseweb="tab-list"]::-webkit-scrollbar { height: 4px; } /* Scroll fino */
        .stTabs [data-baseweb="tab-list"]::-webkit-scrollbar-thumb { background: #CBD5E0; border-radius: 4px; }
        
        .stTabs [data-baseweb="tab"] { 
            height: 38px; border-radius: 20px !important; background-color: #FFFFFF; border: 1px solid #E2E8F0; 
            color: #718096; font-weight: 700; font-size: 0.8rem; padding: 0 20px; transition: all 0.2s ease; 
            box-shadow: 0 1px 2px rgba(0,0,0,0.03); flex-shrink: 0; text-transform: uppercase; letter-spacing: 0.5px; 
        }
        .stTabs [data-baseweb="tab"]:hover { border-color: #CBD5E0; background-color: #EDF2F7; }
        .stTabs [aria-selected="true"] { 
            background-color: transparent !important; color: #3182CE !important; border: 1px solid #3182CE !important; 
            box-shadow: 0 0 12px rgba(49, 130, 206, 0.4); 
        }
        .stTabs [data-baseweb="tab"]:last-of-type[aria-selected="true"] {
            color: #D69E2E !important; border-color: #D69E2E !important;
        }

        /* BARRA DE PROGRESSO COM LOGO */
        .prog-container { width: 100%; position: relative; margin: 0 0 35px 0; }
        .prog-track { width: 100%; height: 3px; background-color: #E2E8F0; border-radius: 1.5px; }
        .prog-fill { height: 100%; border-radius: 1.5px; transition: width 1s ease; box-shadow: 0 1px 4px rgba(0,0,0,0.1); }
        .prog-icon { position: absolute; top: -16px; transition: left 1s ease; transform: translateX(-50%); z-index: 10; }
        .prog-logo-spin { height: 35px; width: 35px; animation: spin 10s linear infinite; filter: drop-shadow(0 2px 4px rgba(0,0,0,0.15)); }

        /* CARDS GERAIS */
        .soft-card { border-radius: 12px; padding: 20px; display: flex; flex-direction: column; position: relative; overflow: hidden; border: 1px solid rgba(0,0,0,0.05); border-left: 5px solid; }
        .sc-blue { background-color: #EBF8FF; border-left-color: #3182CE; }
        .sc-yellow { background-color: #FFFFF0; border-left-color: #D69E2E; }
        .sc-head { display: flex; align-items: center; gap: 8px; font-weight: 800; font-size: 1rem; margin-bottom: 10px; color: #2D3748; }
        .bg-icon { position: absolute; bottom: -10px; right: 10px; font-size: 6rem; opacity: 0.08; pointer-events: none; }
        
        .omni-badge {
            position: fixed; top: 15px; right: 15px; background: rgba(255,255,255,0.85); border: 1px solid rgba(255,255,255,0.6);
            backdrop-filter: blur(8px); padding: 4px 30px; border-radius: 20px; z-index: 9999; display: flex; align-items: center; gap: 10px;
        }
        .omni-text { font-family: 'Nunito'; font-weight: 800; font-size: 0.9rem; color: #2D3748; letter-spacing: 1px; }
        .omni-logo-spin { height: 26px; animation: spin 10s linear infinite; }
        @keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }

        /* INPUTS & BUTTONS */
        .stTextInput input, .stTextArea textarea, .stSelectbox div[data-baseweb="select"] { border-radius: 8px !important; border-color: #E2E8F0 !important; }
        div[data-testid="column"] .stButton button { border-radius: 8px !important; font-weight: 700; height: 45px; background-color: #0F52BA; color: white; border: none; }
        div[data-testid="column"] .stButton button:hover { background-color: #0A3D8F; }
    </style>
    <link href="https://cdn.jsdelivr.net/npm/remixicon@4.1.0/fonts/remixicon.css" rel="stylesheet">
    """, unsafe_allow_html=True)

aplicar_estilo_visual()

# ==============================================================================
# 6. FUNÇÕES IA
# ==============================================================================
def extrair_dados_pdf_ia(api_key, texto_pdf):
    if not api_key: return None, "Configure a Chave API."
    try:
        client = OpenAI(api_key=api_key)
        prompt = f"Extraia do texto em JSON: {{'diagnostico': '...', 'medicamentos': [{{'nome':'...','posologia':'...'}}]}}. Texto: {texto_pdf[:3000]}"
        res = client.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "user", "content": prompt}], response_format={"type": "json_object"})
        return json.loads(res.choices[0].message.content), None
    except Exception as e: return None, str(e)

def consultar_gpt_pedagogico(api_key, dados, contexto_pdf="", modo_pratico=False):
    if not api_key: return None, "Configure a API."
    try:
        client = OpenAI(api_key=api_key)
        prompt = f"Gere um PEI para {dados['nome']}, Hiperfoco: {dados['hiperfoco']}. Use estrutura técnica com Metas SMART e Bloom."
        res = client.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "user", "content": prompt}])
        return res.choices[0].message.content, None
    except Exception as e: return None, str(e)

def gerar_roteiro_gamificado(api_key, dados, pei_tecnico):
    if not api_key: return None, "Configure API."
    try:
        client = OpenAI(api_key=api_key)
        prompt = f"Gere roteiro gamificado para {dados['nome']} baseado no hiperfoco {dados['hiperfoco']}."
        res = client.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "user", "content": prompt}])
        return res.choices[0].message.content, None
    except Exception as e: return None, str(e)

# ==============================================================================
# 8. INTERFACE UI (PRINCIPAL)
# ==============================================================================
with st.sidebar:
    try: st.image("ominisfera.png", width=120)
    except: pass
    if 'OPENAI_API_KEY' in st.secrets: api_key = st.secrets['OPENAI_API_KEY']; st.success("✅ OpenAI OK")
    else: api_key = st.text_input("Chave OpenAI:", type="password")
    st.info("⚠️ Conteúdo gerado por IA. Revise.")
    
    st.markdown("### 📂 Backup")
    uploaded_json = st.file_uploader("Arquivo .json", type="json")
    if uploaded_json:
        try: 
            d = json.load(uploaded_json)
            if 'nasc' in d: d['nasc'] = date.fromisoformat(d['nasc'])
            if d.get('monitoramento_data'): d['monitoramento_data'] = date.fromisoformat(d['monitoramento_data'])
            st.session_state.dados.update(d); st.success("Carregado!")
        except: st.error("Erro.")
    
    st.markdown("---")
    if st.button("🌐 INTEGRAR NA OMNISFERA", use_container_width=True, type="primary"):
        ok, msg = salvar_aluno_integrado(st.session_state.dados)
        if ok: st.success(msg); st.balloons()
        else: st.error(msg)
    st.markdown("---")

# HEADER
logo_path = "omni_icone.png" if os.path.exists("omni_icone.png") else None
img_html = f'<img src="data:image/png;base64,{get_base64_image(logo_path)}" style="height: 110px;">' if logo_path else ""

st.markdown(f"""
<div class="header-unified">
    {img_html}
    <div class="header-subtitle">Ecossistema de Inteligência Pedagógica e Inclusiva</div>
</div>""", unsafe_allow_html=True)

# NAVEGAÇÃO
abas = ["INÍCIO", "ESTUDANTE", "EVIDÊNCIAS", "REDE DE APOIO", "MAPEAMENTO", "PLANO DE AÇÃO", "MONITORAMENTO", "CONSULTORIA IA", "DASHBOARD & DOCS", "JORNADA GAMIFICADA"]
tabs = st.tabs(abas)

# ABA 0: INÍCIO (ATUALIZADA)
with tabs[0]:
    st.markdown("### 🏛️ Central de Fundamentos e Legislação")

    # Bloco 1: O PEI (Azul) - Ícone Atualizado
    st.markdown("""
    <div class="soft-card sc-blue" style="min-height: auto; margin-bottom: 20px;">
        <div class="sc-head"><i class="ri-article-line" style="color:#3182CE;"></i> O que é o PEI? (Definição Técnica)</div>
        <div class="sc-body" style="font-size: 0.95rem; line-height: 1.6;">
            O <b>Plano de Ensino Individualizado (PEI)</b> é o instrumento norteador da inclusão escolar. Ele não é apenas um documento burocrático, mas um mapa vivo que descreve as potencialidades, as barreiras e, principalmente, as <b>estratégias de eliminação de barreiras</b> para garantir o acesso ao currículo. O PEI baseia-se no Desenho Universal para a Aprendizagem (DUA) e deve ser revisado periodicamente. Ele garante que a escola não apenas "receba" o aluno, mas planeje ativamente sua permanência e sucesso.
        </div>
        <div class="bg-icon"><i class="ri-book-read-line"></i></div>
    </div>
    """, unsafe_allow_html=True)

    # Bloco 2: Legislação (Amarelo) - Ícone Atualizado
    st.markdown("""
    <div class="soft-card sc-yellow" style="min-height: auto;">
        <div class="sc-head"><i class="ri-balance-line" style="color:#D69E2E;"></i> Marco Legal & Atualizações (2025)</div>
        <div class="sc-body" style="font-size: 0.95rem; line-height: 1.6;">
            A fundamentação legal do PDI/PEI baseia-se na <b>LDB (Lei 9.394/96)</b> e na Lei Brasileira de Inclusão, garantindo o direito à adaptação curricular e ao AEE.
            <br><br>
            <div style="background: rgba(255,255,255,0.6); padding: 15px; border-radius: 8px; border: 1px solid #E2E8F0;">
                <strong style="color:#C05621;">📢 ATUALIZAÇÕES RECENTES (DEZEMBRO/2025)</strong>
                <ul style="margin-top: 10px;">
                     <li><b><a href="https://www2.camara.leg.br/legin/fed/decret/2025/decreto-12686-20-outubro-2025-798166-publicacaooriginal-176779-pe.html" target="_blank" style="text-decoration:none; color:#C05621;">Decreto nº 12.686 (20/10/2025)</a></b>: Estabelece novas diretrizes para o financiamento do AEE e a estruturação das salas de recursos multifuncionais.</li>
                     <li style="margin-top:8px;"><b><a href="https://www2.camara.leg.br/legin/fed/decret/2025/decreto-12773-8-dezembro-2025-798454-publicacaooriginal-177304-pe.html" target="_blank" style="text-decoration:none; color:#C05621;">Decreto nº 12.773 (08/12/2025)</a></b>: Regula a obrigatoriedade do PDI em transições escolares e a formação continuada de professores.</li>
                </ul>
            </div>
            <div style="margin-top: 10px; font-size: 0.85rem;">
                🔗 <a href="https://www.planalto.gov.br/ccivil_03/leis/l9394.htm" target="_blank" style="color:#718096; text-decoration:none;">Consultar LDB na íntegra</a>
            </div>
        </div>
        <div class="bg-icon"><i class="ri-government-line"></i></div>
    </div>
    """, unsafe_allow_html=True)

with tabs[1]: # ESTUDANTE
    render_progresso()
    st.markdown("### <i class='ri-user-smile-line'></i> Dossiê do Estudante", unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns([3, 2, 2, 1])
    st.session_state.dados['nome'] = c1.text_input("Nome Completo", st.session_state.dados['nome'])
    st.session_state.dados['nasc'] = c2.date_input("Nascimento", value=st.session_state.dados.get('nasc', date(2015, 1, 1)))
    st.session_state.dados['serie'] = c3.selectbox("Série/Ano", LISTA_SERIES, index=0)
    st.session_state.dados['turma'] = c4.text_input("Turma", st.session_state.dados['turma'])
    
    st.markdown("##### Histórico & Contexto")
    c_hist, c_fam = st.columns(2)
    st.session_state.dados['historico'] = c_hist.text_area("Histórico Escolar", st.session_state.dados['historico'])
    st.session_state.dados['familia'] = c_fam.text_area("Dinâmica Familiar", st.session_state.dados['familia'])
    st.session_state.dados['composicao_familiar_tags'] = st.multiselect("Quem convive?", LISTA_FAMILIA, default=st.session_state.dados['composicao_familiar_tags'])
    
    st.divider()
    col_pdf, col_btn_ia = st.columns([2, 1])
    with col_pdf:
        st.markdown("**📎 Upload de Laudo (PDF)**")
        up = st.file_uploader("Arquivo", type="pdf", label_visibility="collapsed")
        if up: st.session_state.pdf_text = ler_pdf(up)
    with col_btn_ia:
        st.write(""); st.write("")
        if st.button("✨ Extrair Dados", type="primary", use_container_width=True, disabled=(not st.session_state.pdf_text)):
             with st.spinner("Lendo..."):
                 d, e = extrair_dados_pdf_ia(api_key, st.session_state.pdf_text)
                 if d:
                     st.session_state.dados['diagnostico'] = d.get('diagnostico', '')
                     st.success("Dados extraídos!")
                     st.rerun()

    st.markdown("##### Contexto Clínico")
    st.session_state.dados['diagnostico'] = st.text_input("Diagnóstico", st.session_state.dados['diagnostico'])
    
    with st.container(border=True):
        if st.toggle("💊 O aluno usa medicação?", value=len(st.session_state.dados['lista_medicamentos'])>0):
            c1, c2, c3 = st.columns([3, 2, 2])
            nm = c1.text_input("Nome", key="nm_med")
            pos = c2.text_input("Posologia", key="pos_med")
            esc = c3.checkbox("Na escola?", key="adm_esc")
            if st.button("Adicionar Medicação"):
                st.session_state.dados['lista_medicamentos'].append({"nome": nm, "posologia": pos, "escola": esc})
                st.rerun()
        if st.session_state.dados['lista_medicamentos']:
            for i, m in enumerate(st.session_state.dados['lista_medicamentos']):
                st.info(f"💊 {m['nome']} ({m['posologia']})")

with tabs[2]: # EVIDÊNCIAS
    render_progresso()
    st.markdown("### <i class='ri-search-eye-line'></i> Evidências", unsafe_allow_html=True)
    st.session_state.dados['nivel_alfabetizacao'] = st.selectbox("Nível de Alfabetização", LISTA_ALFABETIZACAO)
    st.divider()
    c1, c2, c3 = st.columns(3)
    with c1: 
        st.markdown("**Pedagógico**")
        st.session_state.dados['checklist_evidencias']['Estagnação'] = st.toggle("Estagnação")
    with c2: 
        st.markdown("**Cognitivo**")
        st.session_state.dados['checklist_evidencias']['Foco'] = st.toggle("Oscilação de Foco")

with tabs[3]: # REDE
    render_progresso()
    st.markdown("### <i class='ri-team-line'></i> Rede de Apoio", unsafe_allow_html=True)
    st.session_state.dados['rede_apoio'] = st.multiselect("Profissionais:", LISTA_PROFISSIONAIS, default=st.session_state.dados['rede_apoio'])
    st.session_state.dados['orientacoes_especialistas'] = st.text_area("Orientações Clínicas", st.session_state.dados['orientacoes_especialistas'])

with tabs[4]: # MAPEAMENTO
    render_progresso()
    st.markdown("### <i class='ri-radar-line'></i> Mapeamento", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    st.session_state.dados['hiperfoco'] = c1.text_input("Hiperfoco", st.session_state.dados['hiperfoco'])
    st.session_state.dados['potencias'] = c2.multiselect("Potencialidades", LISTA_POTENCIAS, default=st.session_state.dados.get('potencias',[]))
    st.divider()
    st.markdown("#### Barreiras")
    c1, c2 = st.columns(2)
    with c1:
        sel = st.multiselect("Cognitivas", LISTAS_BARREIRAS["Funções Cognitivas"])
        st.session_state.dados['barreiras_selecionadas']["Funções Cognitivas"] = sel

with tabs[5]: # PLANO
    render_progresso()
    st.markdown("### <i class='ri-tools-line'></i> Plano de Ação", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1: st.session_state.dados['estrategias_acesso'] = st.multiselect("Estratégias Acesso", ["Tempo Estendido", "Material Ampliado"])

# ABA 6: MONITORAMENTO (ATUALIZADA COM SEPARAÇÃO)
with tabs[6]: 
    render_progresso()
    st.markdown("### <i class='ri-loop-right-line'></i> Monitoramento e Metas", unsafe_allow_html=True)
    
    # Seção 1: Data de Revisão
    st.markdown("#### 📅 Próxima Revisão")
    st.session_state.dados['monitoramento_data'] = st.date_input("Agendar para:", value=st.session_state.dados.get('monitoramento_data', date.today()))
    
    st.divider()
    
    # Seção 2: Área de Revisão (Com Aviso)
    st.markdown("""
    <div style="background-color: #FFF5F5; border-left: 5px solid #E53E3E; padding: 15px; border-radius: 5px; margin-bottom: 20px;">
        <strong style="color: #C53030;">⚠️ ÁREA DE REVISÃO DO PEI</strong><br>
        <span style="font-size: 0.9rem; color: #742A2A;">
        Preencha os campos abaixo <b>apenas no momento da reavaliação</b> do plano para registrar a evolução do estudante.
        </span>
    </div>
    """, unsafe_allow_html=True)
    
    c1, c2 = st.columns(2)
    with c1: 
        st.session_state.dados['status_meta'] = st.selectbox("Status da Meta", ["Não Iniciado", "Em Andamento", "Atingido"], index=0)
    with c2: 
        st.session_state.dados['parecer_geral'] = st.selectbox("Parecer Geral", ["Manter Estratégias", "Alterar Metodologia"], index=0)
    
    st.write("")
    st.session_state.dados['proximos_passos_select'] = st.multiselect("Ações Futuras (Pós-Revisão)", ["Reunião com Família", "Encaminhamento Clínico", "Novo PEI"])

with tabs[7]: # CONSULTORIA IA
    render_progresso()
    st.markdown("### <i class='ri-robot-2-line'></i> Consultoria IA", unsafe_allow_html=True)
    if st.button("✨ Gerar PEI Técnico", type="primary"):
        res, _ = consultar_gpt_pedagogico(api_key, st.session_state.dados)
        st.session_state.dados['ia_sugestao'] = res
    if st.session_state.dados['ia_sugestao']:
        st.markdown(st.session_state.dados['ia_sugestao'])

# ABA 8: DASHBOARD & DOCS (ATUALIZADA)
with tabs[8]: 
    render_progresso()
    st.markdown("### <i class='ri-file-pdf-line'></i> Dashboard e Exportação", unsafe_allow_html=True)
    
    # ... código do dashboard (KPIs) ...
    # Exemplo do Card de Atenção renomeado
    txt_comp, bg_c, txt_c = calcular_complexidade_pei(st.session_state.dados)
    st.markdown(f"""<div class="metric-card" style="background-color:{bg_c}; border-color:{txt_c};"><div class="comp-icon-box"><i class="ri-error-warning-line" style="color:{txt_c}; font-size: 2rem;"></i></div><div style="font-weight:800; font-size:1.1rem; color:{txt_c}; margin:5px 0;">{txt_comp}</div><div class="d-lbl" style="color:{txt_c};">Nível de Atenção (Execução)</div></div>""", unsafe_allow_html=True)

    st.divider()
    
    # Botão de JSON com explicação
    st.markdown("**💾 Backup do Estudante**")
    st.caption("ℹ️ **Dica:** Crie uma pasta 'Alunos_PEI' no seu computador e salve este arquivo lá para manter o histórico organizado.")
    
    json_dados = json.dumps(st.session_state.dados, default=str)
    st.download_button("📥 Baixar Arquivo .json", json_dados, f"PEI_{st.session_state.dados['nome']}.json", "application/json")

with tab_mapa:
    st.markdown("### Jornada Gamificada")
    if st.button("🎮 Gerar Mapa", type="primary"):
        res, _ = gerar_roteiro_gamificado(api_key, st.session_state.dados, "")
        st.session_state.dados['ia_mapa_texto'] = res
    if st.session_state.dados['ia_mapa_texto']:
        st.markdown(st.session_state.dados['ia_mapa_texto'])

# Footer final
st.markdown("<div class='footer-signature'>PEI 360º v116.0 Gold Edition - Desenvolvido por Rodrigo A. Queiroz</div>", unsafe_allow_html=True)
