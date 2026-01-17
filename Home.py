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
APP_VERSION = "v128.0 (API V4 Fix)"

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
# 1.1. LÓGICA DE BANCO DE DADOS (CORREÇÃO DOS SCOPES)
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
        # --- MUDANÇA CRÍTICA AQUI: SCOPES ATUALIZADOS ---
        scope = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]
        credentials = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scope)
        client = gspread.authorize(credentials)
        return client
    except Exception as e:
        st.error(f"Erro de Credenciais: {e}")
        return None

def carregar_banco_nuvem():
    client = conectar_gsheets()
    if not client: return []
    
    try:
        # Tenta abrir a planilha. Se falhar, mostra o erro REAL.
        sheet = client.open("Omnisfera_Dados")
        
        # Pega a primeira aba (mais seguro que 'Sheet1')
        worksheet = sheet.get_worksheet(0)
        
        records = worksheet.get_all_records()
        
        lista_processada = []
        for reg in records:
            try:
                # Tenta ler o JSON completo
                if 'Dados_Completos' in reg and reg['Dados_Completos']:
                    if isinstance(reg['Dados_Completos'], str) and len(reg['Dados_Completos']) > 10:
                        dados_completos = json.loads(reg['Dados_Completos'])
                        lista_processada.append(dados_completos)
                    else:
                        lista_processada.append(reg)
                else:
                    lista_processada.append(reg)
            except: 
                lista_processada.append(reg)
                continue
                
        return lista_processada

    except gspread.exceptions.SpreadsheetNotFound:
        st.error("❌ A planilha 'Omnisfera_Dados' não foi encontrada!")
        st.info("👉 Verifique se você compartilhou a planilha com o e-mail do robô (client_email no secrets).")
        return []
    except Exception as e:
        # Mostra o erro detalhado se não for 200
        st.error(f"⚠️ Erro ao acessar dados: {str(e)}")
        return []

def excluir_aluno_nuvem(nome_aluno):
    try:
        client = conectar_gsheets()
        sheet = client.open("Omnisfera_Dados")
        worksheet = sheet.get_worksheet(0)
        try:
            cell = worksheet.find(nome_aluno)
            if cell:
                worksheet.delete_rows(cell.row)
                st.session_state.banco_estudantes = [a for a in st.session_state.banco_estudantes if a['nome'] != nome_aluno]
                return True, f"Aluno {nome_aluno} removido."
            return False, "Aluno não encontrado."
        except: return False, "Aluno não encontrado."
    except Exception as e: return False, str(e)

# Tenta carregar na inicialização
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
    card_bg, card_border, display_text, footer_visibility = "rgba(255, 220, 50, 0.95)", "rgba(200, 160, 0, 0.5)", "OMNISFERA | TESTE", "visible"
else:
    card_bg, card_border, display_text, footer_visibility = "rgba(255, 255, 255, 0.85)", "rgba(255, 255, 255, 0.6)", f"OMNISFERA {APP_VERSION}", "hidden"

# ==============================================================================
# 3. CSS GLOBAL
# ==============================================================================
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Nunito:wght@400;600;700&display=swap');
    html, body, [class*="css"] {{ font-family: 'Nunito', sans-serif; color: #2D3748; background-color: #F7FAFC; }}
    .block-container {{ padding-top: 130px !important; padding-bottom: 2rem !important; }}
    .logo-container {{ display: flex; align-items: center; justify-content: flex-start; gap: 15px; position: fixed; top: 0; left: 0; width: 100%; height: 90px; background-color: rgba(247, 250, 252, 0.85); backdrop-filter: blur(12px); border-bottom: 1px solid rgba(255, 255, 255, 0.5); z-index: 9999; box-shadow: 0 4px 15px rgba(0,0,0,0.03); padding-left: 40px; padding-top: 5px; }}
    .header-subtitle-text {{ font-family: 'Nunito', sans-serif; font-weight: 600; font-size: 1rem; color: #718096; border-left: 2px solid #CBD5E0; padding-left: 15px; height: 40px; display: flex; align-items: center; }}
    .logo-icon-spin {{ height: 75px; width: auto; animation: spin 45s linear infinite; }}
    .logo-text-static {{ height: 45px; width: auto; }}
    .omni-badge {{ position: fixed; top: 15px; right: 15px; background: {card_bg}; border: 1px solid {card_border}; backdrop-filter: blur(12px); padding: 5px 15px; min-width: 150px; border-radius: 12px; box-shadow: 0 4px 10px rgba(0,0,0,0.06); z-index: 999990; display: flex; align-items: center; justify-content: center; pointer-events: none; }}
    .omni-text {{ font-family: 'Inter', sans-serif; font-weight: 800; font-size: 0.6rem; color: #2D3748; letter-spacing: 1.5px; text-transform: uppercase; }}
    
    /* Login & Hero */
    .login-container {{ background: white; padding: 30px; border-radius: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.06); text-align: center; border: 1px solid #E2E8F0; max-width: 480px; margin: 40px auto; }}
    .dash-hero {{ background: radial-gradient(circle at top right, #0F52BA, #062B61); border-radius: 16px; margin: 10px 0 20px 0; box-shadow: 0 10px 25px -5px rgba(15, 82, 186, 0.3); color: white; padding: 25px 35px; display: flex; align-items: center; border: 1px solid rgba(255,255,255,0.1); min-height: 100px; }}
    .hero-title {{ font-family: 'Inter', sans-serif; font-weight: 700; font-size: 1.5rem; margin: 0; margin-bottom: 5px; }}
    
    /* Cards Navegação */
    .nav-btn-card {{ background: white; border-radius: 16px; padding: 15px; border: 1px solid #E2E8F0; box-shadow: 0 2px 5px rgba(0,0,0,0.02); text-align: center; display: flex; flex-direction: column; align-items: center; justify-content: center; height: 130px; position: relative; }}
    .nav-icon {{ height: 45px; width: auto; object-fit: contain; margin-bottom: 10px; }}
    .nav-desc {{ font-size: 0.75rem; color: #718096; font-weight: 500; }}
    .card-overlay-btn button {{ position: absolute; top: -140px; left: 0; width: 100%; height: 140px; opacity: 0.01; z-index: 10; cursor: pointer; }}
    
    /* Banco de Dados Lista */
    .student-row {{ background-color: white; border-radius: 10px; border: 1px solid #E2E8F0; padding: 15px; margin-bottom: 10px; display: flex; align-items: center; justify-content: space-between; transition: all 0.2s; }}
    .student-row:hover {{ border-color: #3182CE; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }}
    
    /* Ocultar Streamlit padrao */
    [data-testid="stHeader"] {{ visibility: hidden !important; height: 0px !important; }}
    footer {{ visibility: {footer_visibility} !important; }}
    @keyframes spin {{ from {{ transform: rotate(0deg); }} to {{ transform: rotate(360deg); }} }}
    .b-blue {{ border-bottom: 4px solid #3182CE; }} .b-purple {{ border-bottom: 4px solid #805AD5; }} .b-teal {{ border-bottom: 4px solid #38B2AC; }}
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# 4. SISTEMA DE SEGURANÇA
# ==============================================================================
if "autenticado" not in st.session_state: st.session_state["autenticado"] = False

if not st.session_state["autenticado"]:
    st.markdown("""<style>section[data-testid="stSidebar"] { display: none !important; }</style>""", unsafe_allow_html=True)
    c1, c_login, c2 = st.columns([1, 2, 1])
    with c_login:
        st.markdown("<div class='login-container'>", unsafe_allow_html=True)
        img_icone = get_base64_image("omni_icone.png")
        if img_icone: st.markdown(f"<img src='data:image/png;base64,{img_icone}' style='height:80px; animation: spin 45s linear infinite;'>", unsafe_allow_html=True)
        st.markdown("<h2 style='color:#0F52BA; margin:10px 0;'>OMNISFERA</h2>", unsafe_allow_html=True)
        
        if IS_TEST_ENV:
            if st.button("🚀 ENTRAR (MODO TESTE)", use_container_width=True):
                st.session_state["autenticado"] = True; st.session_state["usuario_nome"] = "Visitante Teste"; st.rerun()
        else:
            nome = st.text_input("Nome", placeholder="Seu Nome")
            cargo = st.text_input("Cargo", placeholder="Seu Cargo")
            senha = st.text_input("Senha", type="password", placeholder="Senha de Acesso")
            if st.button("ACESSAR", use_container_width=True):
                hoje = date.today()
                senha_mestra = "PEI_START_2026" if hoje <= date(2026, 1, 19) else "OMNI_PRO"
                if senha == senha_mestra and nome:
                    st.session_state["autenticado"] = True; st.session_state["usuario_nome"] = nome; st.session_state["usuario_cargo"] = cargo; st.rerun()
                else: st.error("Dados incorretos.")
        st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# ==============================================================================
# 5. CONTEÚDO DA HOME
# ==============================================================================
# Header
icone_b64 = get_base64_image("omni_icone.png")
texto_b64 = get_base64_image("omni_texto.png")
header_html = f"""<div class="logo-container"><img src="data:image/png;base64,{icone_b64}" class="logo-icon-spin"><img src="data:image/png;base64,{texto_b64}" class="logo-text-static"><div class="header-subtitle-text">Ecossistema de Inteligência Pedagógica</div></div>""" if icone_b64 else ""
st.markdown(header_html, unsafe_allow_html=True)
st.markdown(f"""<div class="omni-badge"><span class="omni-text">{display_text}</span></div>""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown(f"**👤 {st.session_state.get('usuario_nome', '')}**")
    st.caption(st.session_state.get('usuario_cargo', ''))
    st.markdown("---")
    if st.button("Sair"): st.session_state["autenticado"] = False; st.rerun()

# Hero
st.markdown(f"""<div class="dash-hero"><div class="hero-title">Olá, {st.session_state.get('usuario_nome', '').split()[0]}!</div></div>""", unsafe_allow_html=True)

# Ferramentas
st.markdown("### 🚀 Acesso Rápido")
c1, c2, c3 = st.columns(3)
def render_card(col, img, desc, key, path, border, icon):
    with col:
        img_html = f'<img src="data:image/png;base64,{img}" class="nav-icon">' if img else f'<i class="{icon}" style="font-size:3rem;"></i>'
        st.markdown(f"""<div class="nav-btn-card {border}">{img_html}<div class="nav-desc">{desc}</div></div>""", unsafe_allow_html=True)
        st.markdown('<div class="card-overlay-btn">', unsafe_allow_html=True)
        if st.button("Acessar", key=key, use_container_width=True):
            if st.session_state.dados['nome']: st.switch_page(path)
            else: st.toast("⚠️ Selecione um aluno abaixo primeiro!", icon="👇"); time.sleep(1)
        st.markdown('</div>', unsafe_allow_html=True)

render_card(c1, get_base64_image("360.png"), "Plano de Ensino (PEI)", "btn_pei", "pages/1_PEI.py", "b-blue", "ri-book-read-line")
render_card(c2, get_base64_image("pae.png"), "Sala de Recursos (PAEE)", "btn_paee", "pages/2_PAE.py", "b-purple", "ri-puzzle-line")
render_card(c3, get_base64_image("hub.png"), "Hub de Inclusão", "btn_hub", "pages/3_Hub_Inclusao.py", "b-teal", "ri-rocket-line")

# --- LISTA DE ALUNOS (BANCO DE DADOS) ---
st.markdown("---")
st.markdown("### 🗄️ Banco de Estudantes (Nuvem)")

if st.session_state.dados['nome']:
    st.success(f"✅ Aluno Ativo: **{st.session_state.dados['nome']}**")
else:
    st.info("👇 Selecione um aluno para começar ou vá ao PEI para criar um novo.")

# Botão de Recarregar Manual
if st.button("🔄 Conectar/Recarregar Google Sheets"):
    st.session_state.banco_estudantes = carregar_banco_nuvem()
    st.rerun()

if st.session_state.banco_estudantes:
    for i, aluno in enumerate(st.session_state.banco_estudantes):
        if not aluno.get('nome'): continue
        
        with st.container():
            c_info, c_act = st.columns([4, 1])
            with c_info:
                st.markdown(f"**{aluno['nome']}** | {aluno.get('serie', '-')}")
                st.caption(f"Diagnóstico: {aluno.get('diagnostico', '---')}")
            with c_act:
                if st.button("📂 Carregar", key=f"load_{i}", use_container_width=True):
                    # Corrige datas
                    if 'nasc' in aluno and isinstance(aluno['nasc'], str):
                         try: aluno['nasc'] = date.fromisoformat(aluno['nasc'])
                         except: pass
                    st.session_state.dados.update(aluno)
                    st.toast(f"Carregado: {aluno['nome']}", icon="✅"); time.sleep(0.5); st.rerun()
                
                if st.button("🗑️", key=f"del_{i}", type="secondary", use_container_width=True):
                    ok, msg = excluir_aluno_nuvem(aluno['nome'])
                    if ok: st.success(msg); st.session_state.banco_estudantes = carregar_banco_nuvem(); st.rerun()
                    else: st.error(msg)
            st.markdown("<hr style='margin:5px 0;'>", unsafe_allow_html=True)
else:
    st.warning("Nenhum aluno encontrado. (Se aparecer 'Erro 200', a API Drive ainda não propagou).")

# Footer
st.markdown("<div style='text-align: center; color: #CBD5E0; font-size: 0.7rem; margin-top: 40px;'>Omnisfera desenvolvida por RODRIGO A. QUEIROZ</div>", unsafe_allow_html=True)
