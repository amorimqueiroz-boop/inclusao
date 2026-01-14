import streamlit as st
import omni_utils as core
from openai import OpenAI

# 1. Configuração (Obrigatória ser a primeira linha)
st.set_page_config(page_title="Omnisfera", page_icon="🌐", layout="wide", initial_sidebar_state="expanded")

# 2. Invoca a Matriz (Aplica CSS, Header, e SIDEBAR)
core.aplicar_estilo_global()

# 3. Verifica Segurança
if not core.verificar_acesso():
    st.stop()

# --- CONTEÚDO DA HOME ---
nome = st.session_state["usuario_nome"].split()[0]

# Hero Simples e Bonito
st.markdown(f"""
<div style="background: linear-gradient(135deg, #0F52BA 0%, #062B61 100%); border-radius: 20px; padding: 50px; color: white; margin-bottom: 30px; margin-top: 20px; box-shadow: 0 10px 20px rgba(15, 82, 186, 0.2);">
    <h1 style="margin:0; font-family: 'Inter';">Olá, {nome}!</h1>
    <p style="opacity: 0.9; margin-top: 10px; font-size: 1.1rem;">"Unindo ciência e dados para transformar a educação."</p>
</div>
""", unsafe_allow_html=True)

# Cards de Acesso
st.markdown("### 🚀 Acesso Rápido")
c1, c2, c3 = st.columns(3)

def card(col, titulo, desc, icon, page):
    with col:
        st.markdown(f"""
        <div style="background: white; padding: 20px; border-radius: 15px; border: 1px solid #E2E8F0; height: 100%; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.02);">
            <div style="font-size: 2.5rem; margin-bottom: 10px;">{icon}</div>
            <h3 style="margin: 0; color: #2D3748; font-size: 1.2rem;">{titulo}</h3>
            <p style="color: #718096; font-size: 0.9rem;">{desc}</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button(f"Abrir {titulo}", key=titulo, use_container_width=True):
            st.switch_page(page)

card(c1, "PEI 360º", "Plano Educacional Individualizado.", "📘", "pages/1_PEI.py")
card(c2, "PAEE", "Atendimento Educacional Especializado.", "🧩", "pages/2_PAE.py")
card(c3, "Hub", "Adaptação de materiais e provas.", "🚀", "pages/3_Hub_Inclusao.py")

# Rodapé simples
st.markdown("<div style='text-align: center; color: #CBD5E0; font-size: 0.8rem; margin-top: 50px;'>Omnisfera © 2026</div>", unsafe_allow_html=True)

# ==============================================================================
# 1. CONFIGURAÇÃO INICIAL E AMBIENTE
# ==============================================================================
APP_VERSION = "v116.0"

# Detecção de Ambiente (Secrets)
try:
    IS_TEST_ENV = st.secrets.get("ENV") == "TESTE"
except:
    IS_TEST_ENV = False

# Configurações da Página
titulo_pag = "[TESTE] Omnisfera" if IS_TEST_ENV else "Omnisfera | Ecossistema"
icone_pag = "🛠️" if IS_TEST_ENV else "🌐"

st.set_page_config(
    page_title=titulo_pag,
    page_icon=icone_pag,
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==============================================================================
# 2. DEFINIÇÃO DE ESTILO E FLUIDEZ (CSS BENTO & MOTION)
# ==============================================================================

# Definição Dinâmica de Cores
if IS_TEST_ENV:
    # Teste: Amarelo e Rodapé Visível
    card_bg = "rgba(255, 220, 50, 0.95)" 
    card_border = "rgba(200, 160, 0, 0.5)"
    display_text = "OMNISFERA | TESTE"
    footer_visibility = "visible" 
else:
    # Produção: Branco Gelo e Rodapé Oculto
    card_bg = "rgba(255, 255, 255, 0.85)"
    card_border = "rgba(255, 255, 255, 0.6)"
    display_text = f"OMNISFERA {APP_VERSION}"
    footer_visibility = "hidden"

# CSS GLOBAL (BENTO UI + FRAMER MOTION FEEL)
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Nunito:wght@400;600;700&display=swap');
    
    /* --- 1. RESET E BASE --- */
    html {{ scroll-behavior: smooth; }}
    html, body, [class*="css"] {{ 
        font-family: 'Nunito', sans-serif; 
        color: #2D3748; 
        background-color: #F7FAFC; /* Fundo neutro suave */
    }}

    /* --- 2. ANIMAÇÕES TIPO FRAMER MOTION --- */
    /* Entrada suave (Fade Up) */
    @keyframes fadeInUp {{
        from {{ opacity: 0; transform: translateY(20px); }}
        to {{ opacity: 1; transform: translateY(0); }}
    }}
    
    /* Física de Mola para Hover (Bounce) */
    .hover-spring {{
        transition: transform 0.4s cubic-bezier(0.34, 1.56, 0.64, 1), box-shadow 0.3s ease;
    }}
    .hover-spring:hover {{
        transform: translateY(-8px) scale(1.01);
        box-shadow: 0 20px 40px rgba(0,0,0,0.08) !important;
        z-index: 10;
    }}

    /* Aplica animação de entrada no container principal */
    .block-container {{ 
        padding-top: 140px !important; 
        padding-bottom: 3rem !important; 
        margin-top: 0rem !important;
        animation: fadeInUp 0.8s cubic-bezier(0.2, 0.8, 0.2, 1);
    }}

    /* --- 3. HEADER DE VIDRO (GLASSMORPHISM) --- */
    .logo-container {{
        display: flex; align-items: center; justify-content: center;
        gap: 20px; 
        position: fixed; top: 0; left: 0; width: 100%; height: 100px;
        background-color: rgba(247, 250, 252, 0.8); 
        backdrop-filter: blur(16px) saturate(180%); 
        -webkit-backdrop-filter: blur(16px) saturate(180%);
        border-bottom: 1px solid rgba(255, 255, 255, 0.6);
        z-index: 9998; 
        box-shadow: 0 4px 30px rgba(0,0,0,0.03);
    }}

    /* LOGO GIRATÓRIA */
    @keyframes spin {{ from {{ transform: rotate(0deg); }} to {{ transform: rotate(360deg); }} }}
    .logo-icon-spin {{ height: 80px; width: auto; animation: spin 45s linear infinite; filter: drop-shadow(0 4px 8px rgba(0,0,0,0.1)); }}
    .logo-text-static {{ height: 50px; width: auto; }}

    /* --- 4. BADGE FLUTUANTE (STATUS) --- */
    .omni-badge {{
        position: fixed; top: 20px; right: 20px;
        background: {card_bg};
        border: 1px solid {card_border};
        backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px);
        padding: 8px 25px;
        min-width: 200px;
        border-radius: 16px;
        box-shadow: 0 8px 20px rgba(0,0,0,0.06);
        z-index: 999990;
        display: flex; align-items: center; justify-content: center;
        pointer-events: none;
        transition: transform 0.3s ease;
    }}
    .omni-text {{
        font-family: 'Inter', sans-serif; font-weight: 800; font-size: 0.7rem;
        color: #2D3748; letter-spacing: 2px; text-transform: uppercase;
    }}

    /* --- 5. COMPONENTES DE UI --- */
    
    /* Controles do Streamlit */
    footer {{ visibility: {footer_visibility} !important; }}
    header[data-testid="stHeader"] {{ background-color: transparent !important; z-index: 9999 !important; pointer-events: none; }}
    [data-testid="stToolbar"] {{ visibility: hidden !important; display: none !important; }}
    
    /* Botão Menu Lateral (Estilo iOS/Notion) */
    [data-testid="stSidebarCollapsedControl"] {{
        position: fixed !important; top: 110px !important; left: 20px !important; z-index: 1000000 !important;
        visibility: visible !important; display: flex !important;
        background-color: rgba(255,255,255,0.9) !important;
        backdrop-filter: blur(8px);
        border: 1px solid #E2E8F0 !important; border-radius: 12px !important;
        width: 40px !important; height: 40px !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05) !important;
        align-items: center !important; justify-content: center !important;
        color: #4A5568 !important; pointer-events: auto !important; 
        transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1) !important;
    }}
    [data-testid="stSidebarCollapsedControl"]:hover {{
        background-color: #3182CE !important; color: white !important; transform: scale(1.1); box-shadow: 0 8px 20px rgba(49, 130, 206, 0.3) !important;
    }}

    /* --- 6. LAYOUTS TIPO BENTO GRID --- */
    
    /* Hero Section */
    .dash-hero {{ 
        background: radial-gradient(circle at top right, #0F52BA, #062B61); 
        border-radius: 24px; margin-bottom: 40px; 
        box-shadow: 0 20px 40px -10px rgba(15, 82, 186, 0.4);
        color: white; position: relative; overflow: hidden;
        padding: 60px;
        display: flex; align-items: center; justify-content: flex-start;
        margin-top: 20px;
        border: 1px solid rgba(255,255,255,0.1);
    }}
    .hero-title {{ font-family: 'Inter', sans-serif; font-weight: 800; font-size: 2.4rem; margin: 0; line-height: 1.1; margin-bottom: 15px; letter-spacing: -1px; }}
    .hero-subtitle {{ font-family: 'Inter', sans-serif; font-size: 1.15rem; opacity: 0.9; font-weight: 400; max-width: 600px; }}
    .hero-bg-icon {{ position: absolute; right: 30px; font-size: 10rem; opacity: 0.05; top: 10px; transform: rotate(-10deg); pointer-events: none; }}

    /* Tool Cards (Bento Style) */
    .tool-card {{ 
        background: white; border-radius: 24px; padding: 30px 25px; 
        box-shadow: 0 2px 10px rgba(0,0,0,0.02); border: 1px solid #E2E8F0; 
        height: 100%; display: flex; flex-direction: column; justify-content: space-between; 
        text-align: center; position: relative; overflow: hidden;
    }}
    
    .card-logo-box {{ height: 90px; display: flex; align-items: center; justify-content: center; margin-bottom: 20px; }}
    .card-logo-img {{ max-height: 85px; width: auto; object-fit: contain; filter: drop-shadow(0 10px 15px rgba(0,0,0,0.1)); }}
    .tool-desc-short {{ font-size: 0.95rem; color: #718096; font-weight: 500; margin-bottom: 25px; min-height: 45px; line-height: 1.5; }}
    
    /* Botões dentro dos cards */
    div[data-testid="column"] .stButton button {{
        width: 100%; border-radius: 14px; border: none;
        background-color: #F1F5F9; color: #475569; font-family: 'Inter', sans-serif; font-weight: 700; 
        font-size: 0.95rem; padding: 14px 0; transition: all 0.3s ease;
        border: 1px solid transparent;
    }}
    div[data-testid="column"] .stButton button:hover {{ 
        background-color: #3182CE; color: white; box-shadow: 0 8px 15px rgba(49, 130, 206, 0.25); transform: translateY(-2px);
    }}
    
    /* Bordas inferiores coloridas */
    .border-blue {{ border-bottom: 6px solid #3182CE; }} 
    .border-purple {{ border-bottom: 6px solid #805AD5; }} 
    .border-teal {{ border-bottom: 6px solid #38B2AC; }}

    /* BENTO GRID (Links) */
    .bento-grid {{ 
        display: grid; 
        grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); 
        gap: 20px; margin-bottom: 40px; 
    }}
    
    .bento-item {{ 
        background: white; border-radius: 20px; padding: 25px; 
        border: 1px solid #E2E8F0; 
        box-shadow: 0 4px 6px rgba(0,0,0,0.01); 
        text-decoration: none; color: inherit; 
        display: flex; flex-direction: column; align-items: center; text-align: center; 
        position: relative; overflow: hidden; height: 100%; 
    }}
    
    .bento-icon {{ 
        width: 55px; height: 55px; border-radius: 18px; 
        display: flex; align-items: center; justify-content: center; 
        font-size: 1.6rem; margin-bottom: 15px; 
        transition: transform 0.3s ease;
    }}
    .bento-item:hover .bento-icon {{ transform: scale(1.1) rotate(5deg); }}
    
    .bento-title {{ font-weight: 800; font-size: 1.05rem; color: #1A202C; margin-bottom: 5px; }}
    .bento-desc {{ font-size: 0.85rem; color: #718096; line-height: 1.4; }}

    /* Insight Card */
    .insight-card-end {{ 
        background: linear-gradient(135deg, #FFFBEB 0%, #FFFFFF 100%); 
        border-radius: 20px; padding: 30px; 
        color: #2D3748; display: flex; align-items: center; gap: 30px; 
        box-shadow: 0 10px 25px rgba(214, 158, 46, 0.1); 
        border: 1px solid rgba(214, 158, 46, 0.2);
        margin-bottom: 30px; 
    }}
    .insight-icon-end {{ 
        font-size: 2.2rem; color: #D69E2E; background: rgba(214, 158, 46, 0.1); 
        width: 70px; height: 70px; border-radius: 50%; 
        display: flex; align-items: center; justify-content: center;
    }}

    .section-title {{ 
        font-family: 'Inter', sans-serif; font-weight: 800; font-size: 1.5rem; 
        color: #1A202C; margin-bottom: 30px; display: flex; align-items: center; gap: 12px; margin-top: 60px; 
    }}
</style>
<link href="https://cdn.jsdelivr.net/npm/remixicon@4.1.0/fonts/remixicon.css" rel="stylesheet">
""", unsafe_allow_html=True)

# ==============================================================================
# 3. UTILITÁRIOS (IMAGENS) E HEADER FIXO
# ==============================================================================
def get_base64_image(image_path):
    if not os.path.exists(image_path): return ""
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

# CARD OMNISFERA (Canto Direito)
st.markdown(f"""<div class="omni-badge hover-spring"><span class="omni-text">{display_text}</span></div>""", unsafe_allow_html=True)

# HEADER LOGO (Centro/Topo - VIDRO)
icone_b64 = get_base64_image("omni_icone.png")
texto_b64 = get_base64_image("omni_texto.png")

if icone_b64 and texto_b64:
    st.markdown(f"""
    <div class="logo-container">
        <img src="data:image/png;base64,{icone_b64}" class="logo-icon-spin">
        <img src="data:image/png;base64,{texto_b64}" class="logo-text-static">
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown("<div class='logo-container'><h1 style='color: #0F52BA; margin:0;'>🌐 OMNISFERA</h1></div>", unsafe_allow_html=True)

# ==============================================================================
# 4. SISTEMA DE SEGURANÇA E LOGIN
# ==============================================================================
def sistema_seguranca():
    # Definição de cores e textos para o Login
    if IS_TEST_ENV:
        border_color = "#FF9800"
        card_title = "🛠️ MODO TESTE"
        btn_text = "🚀 ENTRAR (TESTE)"
        btn_color = "#E65100"
    else:
        border_color = "#E2E8F0"
        card_title = "Bem-vindo de volta!"
        btn_text = "🔒 ACESSAR OMNISFERA"
        btn_color = "#0F52BA"

    st.markdown(f"""
        <style>
            /* Esconde header padrão na tela de login */
            [data-testid="stHeader"] {{visibility: hidden !important; height: 0px !important;}}
            
            .login-container {{ 
                background-color: white; 
                padding: 10px 40px 50px 40px; 
                border-radius: 24px; 
                box-shadow: 0 20px 50px rgba(0,0,0,0.08); 
                text-align: center; 
                border: 2px solid {border_color}; 
                max-width: 500px;
                margin: 0 auto;
                margin-top: 40px;
                animation: fadeInUp 0.8s ease-out;
            }}

            .login-logo-spin {{ height: 100px; width: auto; animation: spin 45s linear infinite; filter: drop-shadow(0 4px 8px rgba(0,0,0,0.1)); }}
            .login-logo-static {{ height: 60px; width: auto; margin-left: 10px; }}
            .logo-wrapper {{ display: flex; justify-content: center; align-items: center; margin-bottom: 20px; margin-top: 10px; }}
            
            .manifesto-login {{ font-family: 'Nunito', sans-serif; font-size: 0.95rem; color: #64748B; font-style: italic; line-height: 1.6; margin-bottom: 30px; padding: 0 10px; }}
            
            .stTextInput input {{ border-radius: 12px !important; border: 1px solid #E2E8F0 !important; padding: 12px !important; background-color: #F8FAFC !important; transition: all 0.3s; }}
            .stTextInput input:focus {{ border-color: #3182CE !important; box-shadow: 0 0 0 3px rgba(49, 130, 206, 0.1); }}
            
            .termo-box {{ background-color: #F8FAFC; padding: 20px; border-radius: 12px; height: 130px; overflow-y: scroll; font-size: 0.8rem; border: 1px solid #E2E8F0; margin-bottom: 25px; text-align: left; color: #4A5568; line-height: 1.5; }}
            
            div[data-testid="column"] .stButton button {{
                width: 100%; background-color: {btn_color} !important; color: white !important;
                border-radius: 14px !important; font-weight: 700 !important; height: 55px !important; border: none !important;
                font-size: 1rem !important; transition: all 0.2s;
            }}
            div[data-testid="column"] .stButton button:hover {{ transform: translateY(-2px); box-shadow: 0 10px 20px rgba(0,0,0,0.15); }}
            .teste-warning {{ color: #D69E2E; font-size: 0.85rem; font-weight: 700; margin-bottom: 15px; background: #FFFBEB; padding: 8px; border-radius: 8px; }}
        </style>
    """, unsafe_allow_html=True)

    if "autenticado" not in st.session_state:
        st.session_state["autenticado"] = False

    if not st.session_state["autenticado"]:
        c_vazio1, c_login, c_vazio2 = st.columns([1, 2, 1])
        
        with c_login:
            st.markdown("<div class='login-container'>", unsafe_allow_html=True)
            
            # LOGO LOGIN
            if icone_b64 and texto_b64:
                st.markdown(f"""<div class="logo-wrapper"><img src="data:image/png;base64,{icone_b64}" class="login-logo-spin"><img src="data:image/png;base64,{texto_b64}" class="login-logo-static"></div>""", unsafe_allow_html=True)
            else:
                st.markdown(f"<h2 style='color:#0F52BA; margin:0; margin-bottom:10px;'>{card_title}</h2>", unsafe_allow_html=True)

            # MANIFESTO
            st.markdown("""<div class="manifesto-login">"A Omnisfera é um ecossistema vivo onde a <strong>Neurociência</strong> encontra a <strong>Pedagogia</strong>."</div>""", unsafe_allow_html=True)
            
            # --- FORMULÁRIO CONDICIONAL ---
            nome_user = ""
            cargo_user = ""
            senha = ""
            concordo = False

            if IS_TEST_ENV:
                # MODO TESTE
                st.markdown("<div class='teste-warning'>🛠️ MODO TESTE ATIVADO</div>", unsafe_allow_html=True)
                with st.expander("📝 Preencher dados (Opcional)"):
                    nome_user = st.text_input("nome_fake", placeholder="Nome (Opcional)", label_visibility="collapsed")
                    st.markdown("<div style='height:5px'></div>", unsafe_allow_html=True)
                    cargo_user = st.text_input("cargo_fake", placeholder="Cargo (Opcional)", label_visibility="collapsed")
            else:
                # MODO PÚBLICO
                st.markdown("<div style='text-align:left; font-weight:700; color:#475569; font-size:0.9rem; margin-bottom:8px;'>👋 Identificação</div>", unsafe_allow_html=True)
                nome_user = st.text_input("nome_real", placeholder="Como gostaria de ser chamado?", label_visibility="collapsed")
                st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
                cargo_user = st.text_input("cargo_real", placeholder="Seu Cargo (Ex: Professor, Coord...)", label_visibility="collapsed")
                
                st.markdown("---")
                st.markdown("<div style='text-align:left; font-weight:700; color:#475569; font-size:0.9rem; margin-bottom:8px;'>🛡️ Termos de Uso (Beta)</div>", unsafe_allow_html=True)
                st.markdown("""<div class="termo-box"><strong>ACORDO DE CONFIDENCIALIDADE</strong><br><br>1. Software em desenvolvimento (BETA).<br>2. Proibida a comercialização.<br>3. Respeite a LGPD (use dados fictícios).</div>""", unsafe_allow_html=True)
                concordo = st.checkbox("Li, compreendi e concordo com os termos.")
                
                st.markdown("<div style='height:15px'></div>", unsafe_allow_html=True)
                senha = st.text_input("senha_real", type="password", placeholder="Senha de Acesso", label_visibility="collapsed")

            st.markdown("<div style='height:25px'></div>", unsafe_allow_html=True)
            
            # VALIDAÇÃO DO BOTÃO
            if st.button(btn_text):
                if IS_TEST_ENV:
                    st.session_state["autenticado"] = True
                    st.session_state["usuario_nome"] = nome_user if nome_user else "Visitante Teste"
                    st.session_state["usuario_cargo"] = cargo_user if cargo_user else "Dev"
                    st.rerun()
                else:
                    hoje = date.today()
                    senha_mestra = "PEI_START_2026" if hoje <= date(2026, 1, 19) else "OMNI_PRO"

                    if not concordo: st.warning("⚠️ Você precisa aceitar os termos de uso.")
                    elif not nome_user or not cargo_user: st.warning("⚠️ Preencha Nome e Cargo.")
                    elif senha != senha_mestra: st.error("🚫 Senha incorreta.")
                    else:
                        st.session_state["autenticado"] = True
                        st.session_state["usuario_nome"] = nome_user
                        st.session_state["usuario_cargo"] = cargo_user
                        st.rerun()
            
            st.markdown("</div>", unsafe_allow_html=True)
        return False
    return True

if not sistema_seguranca(): st.stop()

# ==============================================================================
# 5. CONTEÚDO DA HOME (DASHBOARD BENTO)
# ==============================================================================
nome_display = st.session_state.get("usuario_nome", "Educador").split()[0]

# Banner Message
mensagem_banner = "Unindo ciência, dados e empatia para transformar a educação."
if 'OPENAI_API_KEY' in st.secrets:
    try:
        if 'banner_msg' not in st.session_state:
            client = OpenAI(api_key=st.secrets['OPENAI_API_KEY'])
            prompt_banner = f"Crie uma frase curta e inspiradora para {nome_display} sobre inclusão escolar. Máx 20 palavras."
            res = client.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "user", "content": prompt_banner}])
            st.session_state['banner_msg'] = res.choices[0].message.content
        mensagem_banner = st.session_state['banner_msg']
    except: pass

# --- SIDEBAR ---
with st.sidebar:
    if "usuario_nome" in st.session_state:
        st.markdown(f"**👤 {st.session_state['usuario_nome']}**")
        st.caption(f"{st.session_state['usuario_cargo']}")
        st.markdown("---")

    st.markdown("### 📢 Central de Feedback")
    st.info("Encontrou um erro ou tem uma ideia? Conte para nós!")
    tipo_feedback = st.selectbox("Tipo:", ["Sugestão", "Reportar Erro", "Elogio"], label_visibility="collapsed")
    texto_feedback = st.text_area("Sua mensagem:", height=100, label_visibility="collapsed", placeholder="Digite aqui...")
    
    if st.button("Enviar Feedback", use_container_width=True):
        if texto_feedback:
            st.toast("Feedback enviado! Obrigado.", icon="✅")
            time.sleep(1)
        else:
            st.warning("Escreva uma mensagem.")

# --- HERO SECTION (MOTION) ---
st.markdown(f"""
<div class="dash-hero hover-spring">
    <div class="hero-text-block">
        <div class="hero-title">Olá, {nome_display}!</div>
        <div class="hero-subtitle">"{mensagem_banner}"</div>
    </div>
    <i class="ri-heart-pulse-fill hero-bg-icon"></i>
</div>
""", unsafe_allow_html=True)

# FERRAMENTAS (BENTO CARDS)
st.markdown("<div class='section-title'><i class='ri-cursor-fill'></i> Acesso Rápido</div>", unsafe_allow_html=True)

logo_pei = get_base64_image("360.png")
logo_paee = get_base64_image("pae.png")
logo_hub = get_base64_image("hub.png")

col1, col2, col3 = st.columns(3)

# PEI
with col1:
    icon_pei = f'<img src="data:image/png;base64,{logo_pei}" class="card-logo-img">' if logo_pei else '<i class="ri-book-read-line" style="font-size:4rem; color:#3182CE;"></i>'
    st.markdown(f"""<div class="tool-card border-blue hover-spring"><div class="card-logo-box">{icon_pei}</div><div class="tool-desc-short">Avaliação, anamnese e geração do plano oficial do aluno.</div></div>""", unsafe_allow_html=True)
    if st.button("➜ Acessar PEI", key="btn_pei", use_container_width=True): st.switch_page("pages/1_PEI.py")

# PAEE
with col2:
    icon_paee = f'<img src="data:image/png;base64,{logo_paee}" class="card-logo-img">' if logo_paee else '<i class="ri-puzzle-line" style="font-size:4rem; color:#805AD5;"></i>'
    st.markdown(f"""<div class="tool-card border-purple hover-spring"><div class="card-logo-box">{icon_paee}</div><div class="tool-desc-short">Inteligência da Sala de Recursos e Tecnologias Assistivas.</div></div>""", unsafe_allow_html=True)
    if st.button("➜ Acessar PAEE", key="btn_paee", use_container_width=True): st.switch_page("pages/2_PAE.py")

# HUB
with col3:
    icon_hub = f'<img src="data:image/png;base64,{logo_hub}" class="card-logo-img">' if logo_hub else '<i class="ri-rocket-line" style="font-size:4rem; color:#38B2AC;"></i>'
    st.markdown(f"""<div class="tool-card border-teal hover-spring"><div class="card-logo-box">{icon_hub}</div><div class="tool-desc-short">Adaptação automática de provas e criação de roteiros.</div></div>""", unsafe_allow_html=True)
    if st.button("➜ Acessar Hub", key="btn_hub", use_container_width=True): st.switch_page("pages/3_Hub_Inclusao.py")

# RODAPÉ E INSIGHT (BENTO GRID REAL)
st.markdown("<div style='margin-top:50px;'></div>", unsafe_allow_html=True)
st.markdown("<div class='section-title'><i class='ri-book-mark-fill'></i> Base de Conhecimento</div>", unsafe_allow_html=True)

st.markdown("""
<div class="bento-grid">
    <a href="#" class="bento-item hover-spring">
        <div class="bento-icon" style="background:#EBF8FF; color:#3182CE;"><i class="ri-question-answer-line"></i></div>
        <div class="bento-title">PEI vs PAEE</div>
        <div class="bento-desc">Diferenças fundamentais.</div>
    </a>
    <a href="https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2015/lei/l13146.htm" target="_blank" class="bento-item hover-spring">
        <div class="bento-icon" style="background:#FFFFF0; color:#D69E2E;"><i class="ri-scales-3-line"></i></div>
        <div class="bento-title">Legislação</div>
        <div class="bento-desc">LBI e Decretos.</div>
    </a>
    <a href="https://institutoneurosaber.com.br/" target="_blank" class="bento-item hover-spring">
        <div class="bento-icon" style="background:#FFF5F7; color:#D53F8C;"><i class="ri-brain-line"></i></div>
        <div class="bento-title">Neurociência</div>
        <div class="bento-desc">Desenvolvimento atípico.</div>
    </a>
    <a href="http://basenacionalcomum.mec.gov.br/" target="_blank" class="bento-item hover-spring">
        <div class="bento-icon" style="background:#F0FFF4; color:#38A169;"><i class="ri-compass-3-line"></i></div>
        <div class="bento-title">BNCC</div>
        <div class="bento-desc">Currículo oficial.</div>
    </a>
</div>
""", unsafe_allow_html=True)

# Insight do Dia
noticia_insight = "A aprendizagem acontece quando o cérebro se emociona. Crie vínculos antes de cobrar conteúdos."
if 'OPENAI_API_KEY' in st.secrets:
    try:
        if 'insight_dia' not in st.session_state:
            client = OpenAI(api_key=st.secrets['OPENAI_API_KEY'])
            res = client.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "user", "content": "Dica de 1 frase sobre neurociência para professores."}])
            st.session_state['insight_dia'] = res.choices[0].message.content
        noticia_insight = st.session_state['insight_dia']
    except: pass

st.markdown(f"""
<div class="insight-card-end hover-spring">
    <div class="insight-icon-end"><i class="ri-lightbulb-flash-line"></i></div>
    <div>
        <div style="font-weight: 800; font-size: 0.95rem; color: #D69E2E; letter-spacing: 0.5px; text-transform: uppercase;">Insight do Dia</div>
        <p style="margin:5px 0 0 0; font-size:1.05rem; opacity:0.9; color:#4A5568; font-style: italic; font-weight: 500;">"{noticia_insight}"</p>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("<div style='text-align: center; color: #CBD5E0; font-size: 0.8rem; margin-top: 60px; font-weight: 600;'>Omnisfera © 2026 - Tecnologia Assistiva & Inclusão</div>", unsafe_allow_html=True)
