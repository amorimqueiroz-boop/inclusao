import streamlit as st
from datetime import date
from openai import OpenAI
import base64
import os
import time
import json
import gspread
from google.oauth2.service_account import Credentials

# ==============================================================================
# 1. CONFIGURAÇÃO INICIAL E AMBIENTE
# ==============================================================================
APP_VERSION = "v126.0 (Student Grid)"

try:
    IS_TEST_ENV = st.secrets.get("ENV") == "TESTE"
except:
    IS_TEST_ENV = False

titulo_pag = "[TESTE] Omnisfera" if IS_TEST_ENV else "Omnisfera | Ecossistema"
icone_pag = "omni_icone.png" if os.path.exists("omni_icone.png") else "🌐"

st.set_page_config(
    page_title=titulo_pag,
    page_icon=icone_pag,
    layout="wide",
    initial_sidebar_state="expanded" 
)

# ==============================================================================
# 1.1. LÓGICA DE BANCO DE DADOS
# ==============================================================================
default_state = {
    'nome': '', 'nasc': date(2015, 1, 1), 'serie': None, 'turma': '', 'diagnostico': '', 
    'lista_medicamentos': [], 'composicao_familiar_tags': [], 'historico': '', 'familia': '', 
    'hiperfoco': '', 'potencias': [], 'rede_apoio': [], 'orientacoes_especialistas': '',
    'checklist_evidencias': {}, 
    'nivel_alfabetizacao': 'Não se aplica (Educação Infantil)',
    'barreiras_selecionadas': {}, 'niveis_suporte': {}, 
    'estrategias_acesso': [], 'estrategias_ensino': [], 'estrategias_avaliacao': [], 
    'ia_sugestao': '', 'checklist_hub': {}
}

if 'dados' not in st.session_state: st.session_state.dados = default_state.copy()

@st.cache_resource
def conectar_gsheets():
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        credentials = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scope)
        client = gspread.authorize(credentials)
        return client
    except: return None

def carregar_banco_nuvem():
    try:
        client = conectar_gsheets()
        if not client: return []
        sheet = client.open("Omnisfera_Dados").sheet1 
        records = sheet.get_all_records()
        lista_processada = []
        for reg in records:
            try:
                if 'Dados_Completos' in reg and reg['Dados_Completos']:
                    dados_completos = json.loads(reg['Dados_Completos'])
                    lista_processada.append(dados_completos)
                else:
                    lista_processada.append(reg)
            except: continue
        return lista_processada
    except: return []

def excluir_aluno_nuvem(nome_aluno):
    try:
        client = conectar_gsheets()
        sheet = client.open("Omnisfera_Dados").sheet1
        try:
            cell = sheet.find(nome_aluno)
            if cell:
                sheet.delete_rows(cell.row)
                # Atualiza o cache local
                st.session_state.banco_estudantes = [a for a in st.session_state.banco_estudantes if a['nome'] != nome_aluno]
                return True, f"Aluno {nome_aluno} removido."
            else:
                return False, "Aluno não encontrado."
        except gspread.exceptions.CellNotFound:
             return False, "Aluno não encontrado."
    except Exception as e:
        return False, f"Erro ao excluir: {str(e)}"

if 'banco_estudantes' not in st.session_state:
    st.session_state.banco_estudantes = carregar_banco_nuvem()

# ==============================================================================
# 2. UTILITÁRIOS E CORES
# ==============================================================================
def get_base64_image(image_path):
    if not os.path.exists(image_path): return ""
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

if IS_TEST_ENV:
    card_bg = "rgba(255, 220, 50, 0.95)" 
    card_border = "rgba(200, 160, 0, 0.5)"
    display_text = "OMNISFERA | TESTE"
    footer_visibility = "visible" 
else:
    card_bg = "rgba(255, 255, 255, 0.85)"
    card_border = "rgba(255, 255, 255, 0.6)"
    display_text = f"OMNISFERA {APP_VERSION}"
    footer_visibility = "hidden"

# ==============================================================================
# 3. CSS GLOBAL
# ==============================================================================
css_estatico = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Nunito:wght@400;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Nunito', sans-serif; color: #2D3748; background-color: #F7FAFC; }
    @keyframes fadeInUp { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
    @keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
    .hover-spring { transition: transform 0.3s cubic-bezier(0.34, 1.56, 0.64, 1), box-shadow 0.3s ease; }
    .hover-spring:hover { transform: translateY(-3px) scale(1.01); box-shadow: 0 10px 20px rgba(0,0,0,0.06) !important; z-index: 10; }
    .block-container { padding-top: 130px !important; padding-bottom: 2rem !important; margin-top: 0rem !important; animation: fadeInUp 0.6s cubic-bezier(0.2, 0.8, 0.2, 1); }
    .logo-container { display: flex; align-items: center; justify-content: flex-start; gap: 15px; position: fixed; top: 0; left: 0; width: 100%; height: 90px; background-color: rgba(247, 250, 252, 0.85); backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px); border-bottom: 1px solid rgba(255, 255, 255, 0.5); z-index: 9999; box-shadow: 0 4px 15px rgba(0,0,0,0.03); padding-left: 40px; padding-top: 5px; }
    .header-subtitle-text { font-family: 'Nunito', sans-serif; font-weight: 600; font-size: 1rem; color: #718096; border-left: 2px solid #CBD5E0; padding-left: 15px; height: 40px; display: flex; align-items: center; letter-spacing: -0.3px; }
    .logo-icon-spin { height: 75px; width: auto; animation: spin 45s linear infinite; filter: drop-shadow(0 2px 4px rgba(0,0,0,0.1)); }
    .logo-text-static { height: 45px; width: auto; }
    .login-container { background-color: white; padding: 30px; border-radius: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.06); text-align: center; border: 1px solid #E2E8F0; max-width: 480px; margin: 0 auto; margin-top: 40px; animation: fadeInUp 0.8s ease-out; }
    .login-logo-spin { height: 80px; width: auto; animation: spin 45s linear infinite; margin-bottom: 5px; }
    .login-logo-static { height: 50px; width: auto; margin-left: 8px; }
    .logo-wrapper { display: flex; justify-content: center; align-items: center; margin-bottom: 20px; }
    .manifesto-login { font-family: 'Nunito', sans-serif; font-size: 0.9rem; color: #64748B; font-style: italic; line-height: 1.6; margin-bottom: 30px; text-align: center; padding: 0 10px; }
    .termo-box { background-color: #F8FAFC; padding: 12px; border-radius: 10px; height: 90px; overflow-y: scroll; font-size: 0.7rem; border: 1px solid #CBD5E0; margin-bottom: 15px; text-align: justify; color: #4A5568; line-height: 1.3; }
    .stTextInput input { border-radius: 10px !important; border: 1px solid #E2E8F0 !important; padding: 10px !important; background-color: #F8FAFC !important; font-size: 0.9rem !important;}
    .dash-hero { background: radial-gradient(circle at top right, #0F52BA, #062B61); border-radius: 16px; margin-bottom: 20px; margin-top: 10px; box-shadow: 0 10px 25px -5px rgba(15, 82, 186, 0.3); color: white; position: relative; overflow: hidden; padding: 25px 35px; display: flex; align-items: center; justify-content: flex-start; border: 1px solid rgba(255,255,255,0.1); min-height: 100px; }
    .hero-title { font-family: 'Inter', sans-serif; font-weight: 700; font-size: 1.5rem; margin: 0; line-height: 1.1; margin-bottom: 5px; }
    .hero-subtitle { font-family: 'Inter', sans-serif; font-size: 0.9rem; opacity: 0.9; font-weight: 400; }
    .hero-bg-icon { position: absolute; right: 20px; font-size: 6rem; opacity: 0.05; top: 5px; transform: rotate(-10deg); }
    .nav-btn-card { background-color: white; border-radius: 16px; padding: 15px; border: 1px solid #E2E8F0; box-shadow: 0 2px 5px rgba(0,0,0,0.02); text-align: center; transition: all 0.2s ease; display: flex; flex-direction: column; align-items: center; justify-content: center; height: 130px; position: relative; overflow: hidden; pointer-events: none; }
    .nav-icon { height: 45px; width: auto; object-fit: contain; margin-bottom: 10px; }
    .nav-desc { font-size: 0.75rem; color: #718096; line-height: 1.3; font-weight: 500; }
    .b-blue { border-bottom: 4px solid #3182CE; }
    .b-purple { border-bottom: 4px solid #805AD5; }
    .b-teal { border-bottom: 4px solid #38B2AC; }
    .card-overlay-btn button { position: absolute; top: -140px; left: 0; width: 100%; height: 140px; opacity: 0.01; z-index: 10; cursor: pointer; }
    .card-overlay-btn button:hover { background-color: transparent !important; border: none !important; }
    .bento-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 12px; margin-bottom: 20px; }
    .bento-item { background: white; border-radius: 14px; padding: 15px; border: 1px solid #E2E8F0; box-shadow: 0 2px 4px rgba(0,0,0,0.01); text-decoration: none; color: inherit; display: flex; flex-direction: column; align-items: center; text-align: center; position: relative; overflow: hidden; height: 100%; transition: transform 0.2s; }
    .bento-item:hover { transform: translateY(-2px); border-color: #CBD5E0; }
    .bento-icon { width: 35px; height: 35px; border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 1.2rem; margin-bottom: 8px; }
    .bento-title { font-weight: 700; font-size: 0.85rem; color: #1A202C; margin-bottom: 2px; }
    .bento-desc { font-size: 0.75rem; color: #718096; line-height: 1.2; }
    .insight-card-end { background: linear-gradient(135deg, #FFFBEB 0%, #FFFFFF 100%); border-radius: 14px; padding: 15px 20px; color: #2D3748; display: flex; align-items: center; gap: 15px; box-shadow: 0 5px 15px rgba(214, 158, 46, 0.08); border: 1px solid rgba(214, 158, 46, 0.2); margin-bottom: 15px; }
    .insight-icon-end { font-size: 1.5rem; color: #D69E2E; background: rgba(214, 158, 46, 0.1); width: 45px; height: 45px; border-radius: 50%; display: flex; align-items: center; justify-content: center;}
    .section-title { font-family: 'Inter', sans-serif; font-weight: 700; font-size: 1.1rem; color: #1A202C; margin-bottom: 15px; display: flex; align-items: center; gap: 8px; margin-top: 25px; }
    [data-testid="stHeader"] { visibility: hidden !important; height: 0px !important; }
    [data-testid="stToolbar"] { visibility: hidden !important; display: none !important; }
    
    /* CSS DO BANCO DE DADOS (LISTA) */
    .student-row { background-color: white; border-radius: 10px; border: 1px solid #E2E8F0; padding: 15px; margin-bottom: 10px; display: flex; align-items: center; justify-content: space-between; transition: all 0.2s; }
    .student-row:hover { border-color: #3182CE; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }
    .st-name { font-weight: 700; color: #2D3748; font-size: 1rem; }
    .st-meta { font-size: 0.8rem; color: #718096; }
</style>
<link href="https://cdn.jsdelivr.net/npm/remixicon@4.1.0/fonts/remixicon.css" rel="stylesheet">
"""
st.markdown(css_estatico, unsafe_allow_html=True)

# CSS DINÂMICO
st.markdown(f"""
<style>
    .omni-badge {{
        position: fixed; top: 15px; right: 15px;
        background: {card_bg}; border: 1px solid {card_border};
        backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px);
        padding: 5px 15px; min-width: 150px; border-radius: 12px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.06); z-index: 999990;
        display: flex; align-items: center; justify-content: center;
        pointer-events: none; transition: transform 0.3s ease;
    }}
    .omni-text {{
        font-family: 'Inter', sans-serif; font-weight: 800; font-size: 0.6rem;
        color: #2D3748; letter-spacing: 1.5px; text-transform: uppercase;
    }}
    footer {{ visibility: {footer_visibility} !important; }}
    .login-btn-area button {{ width: 100%; border-radius: 10px !important; border: none !important; font-family: 'Inter', sans-serif; font-weight: 700 !important; font-size: 0.9rem !important; padding: 8px 0; transition: all 0.3s ease; height: 40px !important; background-color: #0F52BA !important; color: white !important; display: block !important; }}
    .login-btn-area button:hover {{ box-shadow: 0 4px 12px rgba(15, 82, 186, 0.3); transform: translateY(-1px); }}
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# 4. SISTEMA DE SEGURANÇA E LOGIN
# ==============================================================================
def sistema_seguranca():
    if "autenticado" not in st.session_state:
        st.session_state["autenticado"] = False

    if not st.session_state["autenticado"]:
        st.markdown("""<style>section[data-testid="stSidebar"] { display: none !important; } [data-testid="stSidebarCollapsedControl"] { display: none !important; } .stButton button { display: block !important; }</style>""", unsafe_allow_html=True)
        btn_text = "🚀 ENTRAR (TESTE)" if IS_TEST_ENV else "ACESSAR OMNISFERA"
        c1, c_login, c2 = st.columns([1, 2, 1])
        with c_login:
            st.markdown("<div class='login-container'>", unsafe_allow_html=True)
            icone_b64_login = get_base64_image("omni_icone.png")
            texto_b64_login = get_base64_image("omni_texto.png")
            if icone_b64_login and texto_b64_login:
                st.markdown(f"""<div class="logo-wrapper"><img src="data:image/png;base64,{icone_b64_login}" class="login-logo-spin"><img src="data:image/png;base64,{texto_b64_login}" class="login-logo-static"></div>""", unsafe_allow_html=True)
            else:
                st.markdown(f"<h2 style='color:#0F52BA; margin:0; margin-bottom:10px;'>OMNISFERA</h2>", unsafe_allow_html=True)
            st.markdown("""<div class="manifesto-login">"A Omnisfera foi desenvolvida com muito cuidado e carinho com o objetivo de auxiliar as escolas na tarefa de incluir. Ela tem o potencial para revolucionar o cenário da inclusão no Brasil."</div>""", unsafe_allow_html=True)
            
            if IS_TEST_ENV:
                st.info("🔧 MODO DE TESTE: Identificação simplificada.")
                st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
            else:
                st.markdown("<div style='text-align:left; font-weight:700; color:#475569; font-size:0.85rem; margin-bottom:5px;'>Identificação</div>", unsafe_allow_html=True)
                nome_user = st.text_input("nome_real", placeholder="Seu Nome", label_visibility="collapsed")
                st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
                cargo_user = st.text_input("cargo_real", placeholder="Seu Cargo", label_visibility="collapsed")
                st.markdown("---")
                st.markdown("<div style='text-align:left; font-weight:700; color:#475569; font-size:0.8rem; margin-bottom:5px;'>Termos de Uso</div>", unsafe_allow_html=True)
                st.markdown("""<div class="termo-box"><strong>ACORDO DE CONFIDENCIALIDADE E USO DE DADOS (Versão Beta)</strong><br><br>1. <strong>Natureza do Software:</strong> O usuário reconhece que o sistema "Omnisfera" encontra-se em fase de testes (BETA) e pode conter instabilidades.<br>2. <strong>Proteção de Dados (LGPD):</strong> É estritamente proibida a inserção de dados reais sensíveis de estudantes (nomes completos, endereços, documentos) que permitam a identificação direta, salvo em ambientes controlados e autorizados pela instituição de ensino.<br>3. <strong>Propriedade Intelectual:</strong> Todo o código, design e inteligência gerada são de propriedade exclusiva dos desenvolvedores. É vedada a cópia, reprodução ou comercialização sem autorização.<br>4. <strong>Responsabilidade:</strong> O uso das sugestões pedagógicas geradas pela IA é de responsabilidade do educador, devendo sempre passar por crivo humano antes da aplicação.<br>Ao prosseguir, você declara estar ciente e de acordo com estes termos.</div>""", unsafe_allow_html=True)
                concordo = st.checkbox("Li, compreendi e concordo com os termos.")
                st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

            st.markdown("""<style>.login-btn-fix button { margin-top: 28px !important; }</style>""", unsafe_allow_html=True)
            c_senha, c_btn = st.columns([2, 1])
            with c_senha:
                if not IS_TEST_ENV: senha = st.text_input("senha_real", type="password", placeholder="Senha de Acesso")
                else: st.markdown("")
            with c_btn:
                st.markdown('<div class="login-btn-area login-btn-fix">', unsafe_allow_html=True)
                login_click = st.button(btn_text, key="btn_login")
                st.markdown('</div>', unsafe_allow_html=True)
            st.markdown("<div style='height:15px'></div>", unsafe_allow_html=True)
            
            if 'login_click' in locals() and login_click:
                if IS_TEST_ENV:
                    st.session_state["autenticado"] = True; st.session_state["usuario_nome"] = "Visitante Teste"; st.session_state["usuario_cargo"] = "Desenvolvedor"; st.rerun()
                else:
                    hoje = date.today()
                    senha_mestra = "PEI_START_2026" if hoje <= date(2026, 1, 19) else "OMNI_PRO"
                    if not concordo: st.warning("Aceite os termos.")
                    elif not nome_user or not cargo_user: st.warning("Preencha seus dados.")
                    elif senha != senha_mestra: st.error("Senha incorreta.")
                    else:
                        st.session_state["autenticado"] = True; st.session_state["usuario_nome"] = nome_user; st.session_state["usuario_cargo"] = cargo_user; st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)
        return False
    return True

if not sistema_seguranca(): st.stop()

# ==============================================================================
# 5. CONTEÚDO DA HOME (SÓ CARREGA APÓS LOGIN)
# ==============================================================================

# CARD OMNISFERA
st.markdown(f"""<div class="omni-badge hover-spring"><span class="omni-text">{display_text}</span></div>""", unsafe_allow_html=True)

# HEADER LOGO
icone_b64 = get_base64_image("omni_icone.png")
texto_b64 = get_base64_image("omni_texto.png")
if icone_b64 and texto_b64:
    st.markdown(f"""<div class="logo-container"><img src="data:image/png;base64,{icone_b64}" class="logo-icon-spin"><img src="data:image/png;base64,{texto_b64}" class="logo-text-static"><div class="header-subtitle-text">Ecossistema de Inteligência Pedagógica e Inclusiva</div></div>""", unsafe_allow_html=True)
else:
    st.markdown("<div class='logo-container'><h1 style='color: #0F52BA; margin:0;'>🌐 OMNISFERA</h1><div class='header-subtitle-text'>Ecossistema de Inteligência Pedagógica e Inclusiva</div></div>", unsafe_allow_html=True)

nome_display = st.session_state.get("usuario_nome", "Educador").split()[0]

# Banner Message
mensagem_banner = "Unindo ciência, dados e empatia para transformar a educação."
if 'OPENAI_API_KEY' in st.secrets:
    try:
        if 'banner_msg' not in st.session_state:
            client = OpenAI(api_key=st.secrets['OPENAI_API_KEY'])
            res = client.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "user", "content": f"Crie uma frase curta e inspiradora sobre inclusão escolar. Não use nomes. Máximo 20 palavras."}])
            st.session_state['banner_msg'] = res.choices[0].message.content
        mensagem_banner = st.session_state['banner_msg']
    except: pass

# --- SIDEBAR LIMPA ---
with st.sidebar:
    if "usuario_nome" in st.session_state:
        st.markdown(f"**👤 {st.session_state['usuario_nome']}**")
        st.caption(f"{st.session_state['usuario_cargo']}")
        st.markdown("---")

    st.markdown("### 📢 Central de Feedback")
    tipo = st.selectbox("Tipo:", ["Sugestão", "Erro", "Elogio"])
    msg = st.text_area("Mensagem:", height=80)
    st.markdown("<style>section[data-testid='stSidebar'] .stButton button { display: block !important; }</style>", unsafe_allow_html=True)
    if st.button("Enviar"):
        if msg: st.toast("Enviado!", icon="✅"); time.sleep(1)

# --- HERO SECTION ---
st.markdown(f"""<div class="dash-hero hover-spring"><div class="hero-text-block"><div class="hero-title">Olá, {nome_display}!</div><div class="hero-subtitle">"{mensagem_banner}"</div></div><i class="ri-heart-pulse-fill hero-bg-icon"></i></div>""", unsafe_allow_html=True)

# FERRAMENTAS COMO CARDS CLICÁVEIS (COM OVERLAY BUTTON)
st.markdown("<div class='section-title'><i class='ri-cursor-fill'></i> Acesso Rápido</div>", unsafe_allow_html=True)

logo_pei = get_base64_image("360.png")
logo_paee = get_base64_image("pae.png")
logo_hub = get_base64_image("hub.png")

c1, c2, c3 = st.columns(3)

def card_botao(coluna, img_b64, desc, chave_btn, page_path, cor_borda_class, fallback_icon):
    with coluna:
        img_html = f'<img src="data:image/png;base64,{img_b64}" class="nav-icon">' if img_b64 else f'<i class="{fallback_icon}" style="font-size:3rem; margin-bottom:10px;"></i>'
        st.markdown(f"""<div class="nav-btn-card {cor_borda_class}">{img_html}<div class="nav-desc">{desc}</div></div>""", unsafe_allow_html=True)
        st.markdown('<div class="card-overlay-btn">', unsafe_allow_html=True)
        if st.button("Acessar", key=chave_btn, use_container_width=True):
            if st.session_state.dados['nome']:
                st.switch_page(page_path)
            else:
                st.toast("⚠️ Selecione um aluno no Banco de Estudantes abaixo!", icon="👇")
                time.sleep(1) 
        st.markdown('</div>', unsafe_allow_html=True)

# Card 1: PEI
card_botao(c1, logo_pei, "Plano de Ensino Individualizado Oficial.", "btn_pei", "pages/1_PEI.py", "b-blue", "ri-book-read-line")
# Card 2: PAEE
card_botao(c2, logo_paee, "Sala de Recursos e Tecnologias Assistivas.", "btn_paee", "pages/2_PAE.py", "b-purple", "ri-puzzle-line")
# Card 3: HUB
card_botao(c3, logo_hub, "Adaptação de provas e roteiros.", "btn_hub", "pages/3_Hub_Inclusao.py", "b-teal", "ri-rocket-line")

# BENTO GRID (BASE DE CONHECIMENTO)
st.markdown("<div class='section-title'><i class='ri-book-mark-fill'></i> Conhecimento</div>", unsafe_allow_html=True)
st.markdown("""<div class="bento-grid"><a href="#" class="bento-item"><div class="bento-icon" style="background:#EBF8FF; color:#3182CE;"><i class="ri-question-answer-line"></i></div><div class="bento-title">PEI vs PAEE</div><div class="bento-desc">Diferenças fundamentais.</div></a><a href="https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2015/lei/l13146.htm" target="_blank" class="bento-item"><div class="bento-icon" style="background:#FFFFF0; color:#D69E2E;"><i class="ri-scales-3-line"></i></div><div class="bento-title">Legislação</div><div class="bento-desc">LBI e Decretos.</div></a><a href="https://institutoneurosaber.com.br/" target="_blank" class="bento-item"><div class="bento-icon" style="background:#FFF5F7; color:#D53F8C;"><i class="ri-brain-line"></i></div><div class="bento-title">Neurociência</div><div class="bento-desc">Desenvolvimento atípico.</div></a><a href="http://basenacionalcomum.mec.gov.br/" target="_blank" class="bento-item"><div class="bento-icon" style="background:#F0FFF4; color:#38A169;"><i class="ri-compass-3-line"></i></div><div class="bento-title">BNCC</div><div class="bento-desc">Currículo oficial.</div></a></div>""", unsafe_allow_html=True)

# INSIGHT DO DIA
noticia_insight = "A aprendizagem acontece quando o cérebro se emociona. Crie vínculos antes de cobrar conteúdos."
if 'OPENAI_API_KEY' in st.secrets:
    try:
        if 'insight_dia' not in st.session_state:
            client = OpenAI(api_key=st.secrets['OPENAI_API_KEY'])
            res = client.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "user", "content": "Dica de 1 frase curta sobre neurociência."}])
            st.session_state['insight_dia'] = res.choices[0].message.content
        noticia_insight = st.session_state['insight_dia']
    except: pass

st.markdown(f"""<div class="insight-card-end hover-spring"><div class="insight-icon-end"><i class="ri-lightbulb-flash-line"></i></div><div><div style="font-weight: 800; font-size: 0.8rem; color: #D69E2E; letter-spacing: 0.5px; text-transform: uppercase;">Insight do Dia</div><p style="margin:2px 0 0 0; font-size:0.9rem; opacity:0.9; color:#4A5568; font-style: italic;">"{noticia_insight}"</p></div></div>""", unsafe_allow_html=True)

# --- LISTA DE ALUNOS NA PARTE INFERIOR (FORA DA SIDEBAR) ---
st.markdown("---")
st.markdown("<div class='section-title'><i class='ri-folder-user-line'></i> Banco de Estudantes (Nuvem)</div>", unsafe_allow_html=True)

# Mostra quem está carregado no momento
if st.session_state.dados['nome']:
    st.info(f"✅ Aluno carregado atualmente: **{st.session_state.dados['nome']}**")
else:
    st.warning("⚠️ Nenhum aluno carregado. Selecione abaixo para começar.")

if st.session_state.banco_estudantes:
    for i, aluno in enumerate(st.session_state.banco_estudantes):
        if not aluno.get('nome'): continue
        
        # Cria um card visual para cada aluno
        with st.container():
            c_info, c_actions = st.columns([3, 1])
            with c_info:
                st.markdown(f"**{aluno['nome']}** | <span style='color:grey'>{aluno.get('serie', '-')}</span>", unsafe_allow_html=True)
                st.caption(f"Diagnóstico: {aluno.get('diagnostico', 'Não informado')}")
            
            with c_actions:
                col_btn1, col_btn2 = st.columns(2)
                if col_btn1.button("📂 Carregar", key=f"load_{i}", use_container_width=True):
                    # Recupera as datas
                    if 'nasc' in aluno and isinstance(aluno['nasc'], str):
                         try: aluno['nasc'] = date.fromisoformat(aluno['nasc'])
                         except: pass
                    if 'monitoramento_data' in aluno and isinstance(aluno['monitoramento_data'], str):
                         try: aluno['monitoramento_data'] = date.fromisoformat(aluno['monitoramento_data'])
                         except: pass
                    
                    st.session_state.dados.update(aluno)
                    st.toast(f"Carregado: {aluno['nome']}", icon="✅")
                    time.sleep(0.5)
                    st.rerun()
                
                if col_btn2.button("🗑️", key=f"del_{i}", type="secondary", use_container_width=True, help="Excluir permanentemente"):
                    ok, msg = excluir_aluno_nuvem(aluno['nome'])
                    if ok: 
                        st.toast(msg, icon="🗑️")
                        # Recarrega a lista do banco
                        st.session_state.banco_estudantes = carregar_banco_nuvem()
                        st.rerun()
                    else: st.error(msg)
            st.divider()
else:
    st.info("O banco de dados está vazio. Vá em 'Acesso Rápido > PEI' para criar o primeiro aluno.")

# ASSINATURA FINAL
st.markdown("<div style='text-align: center; color: #CBD5E0; font-size: 0.7rem; margin-top: 40px;'>Omnisfera desenvolvida e CRIADA por RODRIGO A. QUEIROZ; assim como PEI360, PAEE360 & HUB de Inclusão</div>", unsafe_allow_html=True)
