import streamlit as st
from datetime import date
import base64
import os
import time
import json
import gspread
from google.oauth2.service_account import Credentials

# ==============================================================================
# 1. CONFIGURAÇÃO INICIAL E AMBIENTE
# ==============================================================================
APP_VERSION = "v128.0 (Leitura Blindada)"

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
        scope = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]
        credentials = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scope)
        client = gspread.authorize(credentials)
        return client
    except Exception as e:
        return None

def carregar_banco_nuvem():
    client = conectar_gsheets()
    if not client: 
        st.error("❌ Erro de conexão com o Google.")
        return []
    
    try:
        sheet = client.open("Omnisfera_Dados")
        worksheet = sheet.get_worksheet(0)
        all_rows = worksheet.get_all_values()
        
        if len(all_rows) < 2: return []
            
        lista_processada = []
        for row in all_rows[1:]:
            try:
                if not row or not row[0]: continue
                json_str = row[5] if len(row) > 5 else ""
                
                if json_str and len(json_str) > 10:
                    try:
                        dados_completos = json.loads(json_str)
                        lista_processada.append(dados_completos)
                    except:
                        basic_data = default_state.copy()
                        basic_data['nome'] = row[0]
                        basic_data['serie'] = row[1] if len(row) > 1 else ""
                        basic_data['diagnostico'] = row[2] if len(row) > 2 else ""
                        lista_processada.append(basic_data)
                else:
                    basic_data = default_state.copy()
                    basic_data['nome'] = row[0]
                    basic_data['serie'] = row[1] if len(row) > 1 else ""
                    basic_data['diagnostico'] = row[2] if len(row) > 2 else ""
                    lista_processada.append(basic_data)
            except Exception as e:
                continue
                
        return lista_processada
    except Exception as e:
        st.error(f"⚠️ Erro ao ler planilha: {str(e)}")
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
# 3. CSS GLOBAL E BARRA SUPERIOR
# ==============================================================================
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Nunito:wght@400;600;700&display=swap');
    
    html, body, [class*="css"] {{ font-family: 'Nunito', sans-serif; color: #2D3748; background-color: #F7FAFC; }}
    
    /* AJUSTE PARA O CONTEÚDO NÃO FICAR ATRÁS DA BARRA */
    .block-container {{ padding-top: 110px !important; padding-bottom: 2rem !important; }}
    
    /* BARRA SUPERIOR FIXA */
    .header-container {{
        position: fixed; top: 0; left: 0; width: 100%; height: 80px;
        background-color: rgba(255, 255, 255, 0.90);
        backdrop-filter: blur(10px);
        border-bottom: 1px solid rgba(226, 232, 240, 0.8);
        z-index: 99999;
        display: flex; align-items: center; justify-content: space-between;
        padding: 0 30px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.03);
    }}
    
    .header-left {{ display: flex; align-items: center; gap: 20px; }}
    
    /* LOGO GIRATÓRIA */
    .header-logo-spin {{
        height: 50px; width: 50px;
        animation: spin 20s linear infinite;
    }}
    
    .header-logo-text {{ height: 35px; width: auto; }}
    
    .header-divider {{
        height: 35px; width: 1px; background-color: #CBD5E0;
        margin: 0 15px;
    }}
    
    .header-slogan {{
        font-family: 'Nunito', sans-serif;
        font-weight: 600; font-size: 0.95rem; color: #718096;
        letter-spacing: 0.5px;
    }}

    /* Badge Flutuante (Versão Barra) */
    .header-badge {{
        background: {card_bg}; border: 1px solid {card_border};
        padding: 6px 16px; border-radius: 20px;
        font-family: 'Inter', sans-serif; font-weight: 800; font-size: 0.7rem;
        color: #2D3748; letter-spacing: 1px; text-transform: uppercase;
    }}
    
    /* Animação de Rotação */
    @keyframes spin {{ 100% {{ transform: rotate(360deg); }} }}

    /* Outros Estilos */
    .login-container {{ background: white; padding: 30px; border-radius: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.06); text-align: center; border: 1px solid #E2E8F0; max-width: 480px; margin: 40px auto; }}
    .dash-hero {{ background: radial-gradient(circle at top right, #0F52BA, #062B61); border-radius: 16px; margin: 20px 0 20px 0; box-shadow: 0 10px 25px -5px rgba(15, 82, 186, 0.3); color: white; padding: 25px 35px; display: flex; align-items: center; border: 1px solid rgba(255,255,255,0.1); min-height: 100px; }}
    .hero-title {{ font-family: 'Inter', sans-serif; font-weight: 700; font-size: 1.5rem; margin: 0; margin-bottom: 5px; }}
    
    .nav-btn-card {{ background: white; border-radius: 16px; padding: 15px; border: 1px solid #E2E8F0; box-shadow: 0 2px 5px rgba(0,0,0,0.02); text-align: center; display: flex; flex-direction: column; align-items: center; justify-content: center; height: 130px; position: relative; }}
    .nav-icon {{ height: 45px; width: auto; object-fit: contain; margin-bottom: 10px; }}
    .nav-desc {{ font-size: 0.75rem; color: #718096; font-weight: 500; }}
    
    /* Correção visual Streamlit */
    [data-testid="stHeader"] {{ visibility: hidden !important; height: 0px !important; }}
    footer {{ visibility: {footer_visibility} !important; }}
    
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
        if img_icone: st.markdown(f"<img src='data:image/png;base64,{img_icone}' style='height:80px; animation: spin 20s linear infinite;'>", unsafe_allow_html=True)
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
# 5. RENDERIZAÇÃO DA BARRA SUPERIOR (HEADER)
# ==============================================================================
icone_b64 = get_base64_image("omni_icone.png")
texto_b64 = get_base64_image("omni_texto.png")

logo_img = f'<img src="data:image/png;base64,{icone_b64}" class="header-logo-spin">' if icone_b64 else "🌐"
text_img = f'<img src="data:image/png;base64,{texto_b64}" class="header-logo-text">' if texto_b64 else "<span style='font-weight:800; color:#2C5282; font-size:1.2rem;'>OMNISFERA</span>"

st.markdown(f"""
<div class="header-container">
    <div class="header-left">
        {logo_img}
        {text_img}
        <div class="header-divider"></div>
        <div class="header-slogan">Ecossistema de Inteligência Pedagógica</div>
    </div>
    <div class="header-badge">{display_text}</div>
</div>
""", unsafe_allow_html=True)

# ==============================================================================
# 6. CONTEÚDO DA HOME (DASHBOARD)
# ==============================================================================

# Sidebar
with st.sidebar:
    st.markdown(f"**👤 {st.session_state.get('usuario_nome', '')}**")
    st.caption(st.session_state.get('usuario_cargo', ''))
    st.markdown("---")
    if st.button("Sair"): st.session_state["autenticado"] = False; st.rerun()

# Hero Section
st.markdown(f"""<div class="dash-hero"><div class="hero-title">Olá, {st.session_state.get('usuario_nome', '').split()[0]}!</div></div>""", unsafe_allow_html=True)

# Ferramentas (Cards)
st.markdown("### 🚀 Acesso Rápido")
c1, c2, c3 = st.columns(3)

def render_card_func(col, img, desc, key, path, border, icon):
    with col:
        img_html = f'<img src="data:image/png;base64,{img}" class="nav-icon">' if img else f'<i class="{icon}" style="font-size:3rem;"></i>'
        st.markdown(f"""<div class="nav-btn-card {border}">{img_html}<div class="nav-desc">{desc}</div></div>""", unsafe_allow_html=True)
        # Botão invisível sobre o card para clique
        st.markdown(f"""
        <style>
        div[data-testid="stVerticalBlock"] > div:has(div.nav-btn-card) {{ position: relative; }}
        </style>
        """, unsafe_allow_html=True)
        
        if st.button("Acessar", key=key, use_container_width=True):
             if st.session_state.dados['nome']: st.switch_page(path)
             else: st.toast("⚠️ Selecione um aluno abaixo primeiro!", icon="👇"); time.sleep(1)

render_card_func(c1, get_base64_image("360.png"), "Plano de Ensino (PEI)", "btn_pei", "pages/1_PEI.py", "b-blue", "ri-book-read-line")
render_card_func(c2, get_base64_image("pae.png"), "Sala de Recursos (PAEE)", "btn_paee", "pages/2_PAE.py", "b-purple", "ri-puzzle-line")
render_card_func(c3, get_base64_image("hub.png"), "Hub de Inclusão", "btn_hub", "pages/3_Hub_Inclusao.py", "b-teal", "ri-rocket-line")

# --- LISTA DE ALUNOS (BANCO DE DADOS) ---
st.markdown("---")
st.markdown("### 🗄️ Banco de Estudantes (Nuvem)")

if st.session_state.dados['nome']:
    st.success(f"✅ Aluno Ativo: **{st.session_state.dados['nome']}**")
else:
    st.info("👇 Selecione um aluno para começar ou vá ao PEI para criar um novo.")

# Se o banco estiver vazio, tenta recarregar
if not st.session_state.banco_estudantes:
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
    st.warning("Nenhum aluno encontrado ou erro de conexão. (Verifique se a 'Google Drive API' está ativa).")

# Footer
st.markdown("<div style='text-align: center; color: #CBD5E0; font-size: 0.7rem; margin-top: 40px;'>Omnisfera desenvolvida por RODRIGO A. QUEIROZ</div>", unsafe_allow_html=True)
