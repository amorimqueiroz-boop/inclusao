import streamlit as st
from datetime import date
from openai import OpenAI
import base64
import os
import time

# ==============================================================================
# 1. CONFIGURAÇÃO INICIAL E AMBIENTE
# ==============================================================================
APP_VERSION = "v116.0"

# Detecção de Ambiente
try:
    IS_TEST_ENV = st.secrets.get("ENV") == "TESTE"
except:
    IS_TEST_ENV = False

# Configurações da Página
titulo_pag = "[TESTE] Omnisfera" if IS_TEST_ENV else "Omnisfera | Ecossistema"

# Lógica para usar a logo como ícone da aba
icone_pag = "omni_icone.png" if os.path.exists("omni_icone.png") else "🌐"

st.set_page_config(
    page_title=titulo_pag,
    page_icon=icone_pag,
    layout="wide",
    initial_sidebar_state="expanded" 
)

# ==============================================================================
# 2. UTILITÁRIOS E CORES
# ==============================================================================
def get_base64_image(image_path):
    if not os.path.exists(image_path): return ""
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

# Definição de Cores
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
# 3. CSS BLINDADO (SEM F-STRING NO BLOCO GRANDE)
# ==============================================================================
# Este bloco não usa f""" para evitar o erro de SyntaxError com as chaves do CSS
css_estatico = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Nunito:wght@400;600;700&display=swap');
    
    html { scroll-behavior: smooth; }
    html, body, [class*="css"] { 
        font-family: 'Nunito', sans-serif; 
        color: #2D3748; 
        background-color: #F7FAFC;
    }

    /* Animações */
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    @keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }

    .hover-spring { transition: transform 0.4s cubic-bezier(0.34, 1.56, 0.64, 1), box-shadow 0.3s ease; }
    .hover-spring:hover { transform: translateY(-5px) scale(1.01); box-shadow: 0 15px 30px rgba(0,0,0,0.08) !important; z-index: 10; }

    /* Ajuste de Padding do Container Principal */
    .block-container { 
        padding-top: 130px !important; 
        padding-bottom: 2rem !important; 
        margin-top: 0rem !important;
        animation: fadeInUp 0.8s cubic-bezier(0.2, 0.8, 0.2, 1);
    }

    /* --- HEADER (FIXED - VOLTAMOS AO PADRÃO FIXO) --- */
    .logo-container {
        display: flex; align-items: center; justify-content: flex-start; 
        gap: 20px; 
        position: fixed; /* Fixa no topo */
        top: 0; left: 0; width: 100%; height: 110px;
        background-color: rgba(247, 250, 252, 0.9); /* Fundo vidro */
        backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px);
        border-bottom: 1px solid rgba(255, 255, 255, 0.6);
        z-index: 9998; 
        box-shadow: 0 4px 20px rgba(0,0,0,0.03);
        padding-left: 40px;
        padding-top: 5px;
    }
    .header-subtitle-text {
        font-family: 'Nunito', sans-serif; font-weight: 600; font-size: 1.15rem;
        color: #718096; border-left: 2px solid #CBD5E0; padding-left: 20px;
        height: 50px; display: flex; align-items: center; letter-spacing: -0.3px;
    }
    /* AUMENTADO DE 70PX PARA 95PX */
    .logo-icon-spin { height: 95px; width: auto; animation: spin 45s linear infinite; filter: drop-shadow(0 4px 8px rgba(0,0,0,0.1)); }
    .logo-text-static { height: 50px; width: auto; }

    /* Login Styles */
    .login-container { 
        background-color: white; padding: 40px 40px 50px 40px; 
        border-radius: 24px; box-shadow: 0 20px 50px rgba(0,0,0,0.08); 
        text-align: center; border: 1px solid #E2E8F0; 
        max-width: 500px; margin: 0 auto; margin-top: 60px;
        animation: fadeInUp 0.8s ease-out;
    }
    .login-logo-spin { height: 100px; width: auto; animation: spin 45s linear infinite; margin-bottom: 10px; }
    .login-logo-static { height: 60px; width: auto; margin-left: 10px; }
    .logo-wrapper { display: flex; justify-content: center; align-items: center; margin-bottom: 25px; }
    .manifesto-login { font-family: 'Nunito', sans-serif; font-size: 0.95rem; color: #64748B; font-style: italic; line-height: 1.6; margin-bottom: 30px; }
    
    /* Inputs */
    .stTextInput input { border-radius: 12px !important; border: 1px solid #E2E8F0 !important; padding: 12px !important; background-color: #F8FAFC !important; }
    .stTextInput input:focus { border-color: #3182CE !important; box-shadow: 0 0 0 3px rgba(49, 130, 206, 0.1); }
    
    /* --- BENTO GRID & CARDS --- */
    
    .dash-hero { 
        background: radial-gradient(circle at top right, #0F52BA, #062B61); 
        border-radius: 20px; 
        margin-bottom: 25px; 
        margin-top: 10px;
        box-shadow: 0 20px 40px -10px rgba(15, 82, 186, 0.4);
        color: white; position: relative; overflow: hidden; 
        padding: 35px 45px; 
        display: flex; align-items: center; justify-content: flex-start;
        border: 1px solid rgba(255,255,255,0.1);
    }
    .hero-title { 
        font-family: 'Inter', sans-serif; 
        font-weight: 700; font-size: 1.7rem; 
        margin: 0; line-height: 1.2; margin-bottom: 6px; 
    }
    .hero-subtitle { 
        font-family: 'Inter', sans-serif; 
        font-size: 0.95rem; opacity: 0.9; font-weight: 400; 
    }
    .hero-bg-icon { position: absolute; right: 30px; font-size: 8rem; opacity: 0.05; top: 10px; transform: rotate(-10deg); }

    /* CARDS ACESSO RÁPIDO */
    .nav-btn-card {
        background-color: white; border-radius: 16px; padding: 15px;
        border: 1px solid #E2E8F0; box-shadow: 0 2px 5px rgba(0,0,0,0.02);
        text-align: center; transition: all 0.2s ease; cursor: pointer;
        display: flex; flex-direction: column; align-items: center; justify-content: center;
        height: 140px; position: relative; overflow: hidden;
        text-decoration: none !important;
    }
    .nav-btn-card:hover { transform: translateY(-3px); box-shadow: 0 8px 15px rgba(0,0,0,0.08); border-color: #CBD5E0; }
    .nav-icon { height: 50px; width: auto; object-fit: contain; margin-bottom: 10px; }
    .nav-desc { font-size: 0.75rem; color: #718096; line-height: 1.3; font-weight: 600; }
    
    .b-blue { border-bottom: 4px solid #3182CE; } 
    .b-purple { border-bottom: 4px solid #805AD5; } 
    .b-teal { border-bottom: 4px solid #38B2AC; }

    /* Esconde botões streamlit */
    .stButton button { display: none !important; }

    /* BENTO GRID COMPACTADO */
    .bento-grid { 
        display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); 
        gap: 15px; margin-bottom: 30px; 
    }
    .bento-item { 
        background: white; border-radius: 16px; padding: 20px; border: 1px solid #E2E8F0; 
        box-shadow: 0 4px 6px rgba(0,0,0,0.01); text-decoration: none; color: inherit; 
        display: flex; flex-direction: column; align-items: center; text-align: center; 
        position: relative; overflow: hidden; height: 100%; transition: transform 0.2s;
    }
    .bento-item:hover { transform: translateY(-2px); border-color: #CBD5E0; }
    .bento-icon { 
        width: 45px; height: 45px; border-radius: 14px; display: flex; align-items: center; justify-content: center; 
        font-size: 1.4rem; margin-bottom: 12px; transition: transform 0.3s ease;
    }
    .bento-item:hover .bento-icon { transform: scale(1.1) rotate(5deg); }
    .bento-title { font-weight: 700; font-size: 0.95rem; color: #1A202C; margin-bottom: 4px; }
    .bento-desc { font-size: 0.8rem; color: #718096; line-height: 1.3; }

    /* Insight Card */
    .insight-card-end { 
        background: linear-gradient(135deg, #FFFBEB 0%, #FFFFFF 100%); 
        border-radius: 16px; padding: 25px; 
        color: #2D3748; display: flex; align-items: center; gap: 20px; 
        box-shadow: 0 10px 25px rgba(214, 158, 46, 0.1); 
        border: 1px solid rgba(214, 158, 46, 0.2); margin-bottom: 20px; 
    }
    .insight-icon-end { 
        font-size: 1.8rem; color: #D69E2E; background: rgba(214, 158, 46, 0.1); 
        width: 60px; height: 60px; border-radius: 50%; display: flex; align-items: center; justify-content: center;
    }
    .section-title { 
        font-family: 'Inter', sans-serif; font-weight: 700; font-size: 1.3rem; 
        color: #1A202C; margin-bottom: 20px; display: flex; align-items: center; gap: 10px; margin-top: 30px; 
    }

    /* Ocultar elementos padrão */
    [data-testid="stHeader"] { visibility: hidden !important; height: 0px !important; }
    [data-testid="stToolbar"] { visibility: hidden !important; display: none !important; }
</style>
<link href="https://cdn.jsdelivr.net/npm/remixicon@4.1.0/fonts/remixicon.css" rel="stylesheet">
"""
st.markdown(css_estatico, unsafe_allow_html=True)

# CSS DINÂMICO (Cores variáveis)
st.markdown(f"""
<style>
    .omni-badge {{
        position: fixed; top: 20px; right: 20px;
        background: {card_bg}; border: 1px solid {card_border};
        backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px);
        padding: 6px 20px; min-width: 180px; border-radius: 14px;
        box-shadow: 0 8px 20px rgba(0,0,0,0.06); z-index: 999990;
        display: flex; align-items: center; justify-content: center;
        pointer-events: none; transition: transform 0.3s ease;
    }}
    .omni-text {{
        font-family: 'Inter', sans-serif; font-weight: 800; font-size: 0.65rem;
        color: #2D3748; letter-spacing: 2px; text-transform: uppercase;
    }}
    footer {{ visibility: {footer_visibility} !important; }}
    
    /* Botão de Login */
    .login-btn-area button {{
        width: 100%; border-radius: 12px !important; border: none !important;
        font-family: 'Inter', sans-serif; font-weight: 700 !important; font-size: 0.9rem !important;
        padding: 12px 0; transition: all 0.3s ease;
        background-color: #0F52BA !important; color: white !important;
        display: block !important; 
        height: 50px !important;
    }}
    .login-btn-area button:hover {{ 
        background-color: #3182CE !important; color: white !important; 
        box-shadow: 0 8px 15px rgba(49, 130, 206, 0.25); transform: translateY(-2px);
    }}
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# 4. SISTEMA DE SEGURANÇA E LOGIN
# ==============================================================================
def sistema_seguranca():
    if "autenticado" not in st.session_state:
        st.session_state["autenticado"] = False

    if not st.session_state["autenticado"]:
        
        st.markdown("""
        <style>
            section[data-testid="stSidebar"] { display: none !important; }
            [data-testid="stSidebarCollapsedControl"] { display: none !important; }
        </style>
        """, unsafe_allow_html=True)

        btn_text = "🚀 ENTRAR (TESTE)" if IS_TEST_ENV else "🔒 ACESSAR OMNISFERA"
        
        c1, c_login, c2 = st.columns([1, 2, 1])
        
        with c_login:
            st.markdown("<div class='login-container'>", unsafe_allow_html=True)
            
            icone_b64_login = get_base64_image("omni_icone.png")
            texto_b64_login = get_base64_image("omni_texto.png")
            
            # LOGO LOGIN - APENAS LOGO E TEXTO CENTRALIZADOS
            if icone_b64_login and texto_b64_login:
                st.markdown(f"""
                <div class="logo-wrapper">
                    <img src="data:image/png;base64,{icone_b64_login}" class="login-logo-spin">
                    <img src="data:image/png;base64,{texto_b64_login}" class="login-logo-static">
                </div>""", unsafe_allow_html=True)
            else:
                st.markdown(f"<h2 style='color:#0F52BA; margin:0; margin-bottom:10px;'>OMNISFERA</h2>", unsafe_allow_html=True)

            st.markdown("""<div class="manifesto-login">"A Omnisfera foi desenvolvida com muito cuidado e carinho com o objetivo de auxiliar as escolas na tarefa de incluir. Ela tem o potencial para revolucionar o cenário da inclusão no Brasil."</div>""", unsafe_allow_html=True)
            
            if IS_TEST_ENV:
                with st.expander("📝 Dados (Opcional)"):
                    nome_user = st.text_input("nome_fake", placeholder="Nome", label_visibility="collapsed")
                    cargo_user = st.text_input("cargo_fake", placeholder="Cargo", label_visibility="collapsed")
            else:
                st.markdown("<div style='text-align:left; font-weight:700; color:#475569; font-size:0.85rem; margin-bottom:5px;'>Identificação</div>", unsafe_allow_html=True)
                nome_user = st.text_input("nome_real", placeholder="Seu Nome", label_visibility="collapsed")
                st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
                cargo_user = st.text_input("cargo_real", placeholder="Seu Cargo", label_visibility="collapsed")
                st.markdown("---")
                
                # --- TERMO DE CONFIDENCIALIDADE ---
                st.markdown("<div style='text-align:left; font-weight:700; color:#475569; font-size:0.8rem; margin-bottom:5px;'>Termos de Uso</div>", unsafe_allow_html=True)
                st.markdown("""
                <div style="background-color: #F8FAFC; padding: 12px; border-radius: 10px; height: 100px; overflow-y: scroll; font-size: 0.75rem; border: 1px solid #CBD5E0; margin-bottom: 15px; text-align: justify; color: #4A5568; line-height: 1.4;">
                    <strong>ACORDO DE CONFIDENCIALIDADE E USO DE DADOS (Versão Beta)</strong><br><br>
                    1. <strong>Natureza do Software:</strong> O usuário reconhece que o sistema "Omnisfera" encontra-se em fase de testes (BETA) e pode conter instabilidades.<br>
                    2. <strong>Proteção de Dados (LGPD):</strong> É estritamente proibida a inserção de dados reais sensíveis de estudantes (nomes completos, endereços, documentos) que permitam a identificação direta, salvo em ambientes controlados e autorizados pela instituição de ensino.<br>
                    3. <strong>Propriedade Intelectual:</strong> Todo o código, design e inteligência gerada são de propriedade exclusiva dos desenvolvedores. É vedada a cópia, reprodução ou comercialização sem autorização.<br>
                    4. <strong>Responsabilidade:</strong> O uso das sugestões pedagógicas geradas pela IA é de responsabilidade do educador, devendo sempre passar por crivo humano antes da aplicação.<br>
                    Ao prosseguir, você declara estar ciente e de acordo com estes termos.
                </div>
                """, unsafe_allow_html=True)
                
                concordo = st.checkbox("Li, compreendi e concordo com os termos.")
                
                st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
                senha = st.text_input("senha_real", type="password", placeholder="Senha de Acesso", label_visibility="collapsed")

            st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
            
            # Botão
            st.markdown('<div class="login-btn-area">', unsafe_allow_html=True)
            if st.button(btn_text):
                if IS_TEST_ENV:
                    st.session_state["autenticado"] = True
                    st.session_state["usuario_nome"] = nome_user if nome_user else "Visitante Teste"
                    st.session_state["usuario_cargo"] = cargo_user if cargo_user else "Dev"
                    st.rerun()
                else:
                    hoje = date.today()
                    senha_mestra = "PEI_START_2026" if hoje <= date(2026, 1, 19) else "OMNI_PRO"
                    if not concordo: st.warning("Aceite os termos.")
                    elif not nome_user or not cargo_user: st.warning("Preencha seus dados.")
                    elif senha != senha_mestra: st.error("Senha incorreta.")
                    else:
                        st.session_state["autenticado"] = True
                        st.session_state["usuario_nome"] = nome_user
                        st.session_state["usuario_cargo"] = cargo_user
                        st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown("</div>", unsafe_allow_html=True)
        return False
    return True

if not sistema_seguranca(): st.stop()

# ==============================================================================
# 5. CONTEÚDO DA HOME (SÓ CARREGA APÓS LOGIN)
# ==============================================================================

# CARD OMNISFERA (Canto Direito)
st.markdown(f"""<div class="omni-badge hover-spring"><span class="omni-text">{display_text}</span></div>""", unsafe_allow_html=True)

# HEADER LOGO (FIXO COM GLASSMORPHISM)
icone_b64 = get_base64_image("omni_icone.png")
texto_b64 = get_base64_image("omni_texto.png")

if icone_b64 and texto_b64:
    st.markdown(f"""
    <div class="logo-container">
        <img src="data:image/png;base64,{icone_b64}" class="logo-icon-spin">
        <img src="data:image/png;base64,{texto_b64}" class="logo-text-static">
        <div class="header-subtitle-text">Ecossistema de Inteligência Pedagógica e Inclusiva</div>
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown("<div class='logo-container'><h1 style='color: #0F52BA; margin:0;'>🌐 OMNISFERA</h1><div class='header-subtitle-text'>Ecossistema de Inteligência Pedagógica e Inclusiva</div></div>", unsafe_allow_html=True)

nome_display = st.session_state.get("usuario_nome", "Educador").split()[0]

# Banner Message
mensagem_banner = "Unindo ciência, dados e empatia para transformar a educação."
if 'OPENAI_API_KEY' in st.secrets:
    try:
        if 'banner_msg' not in st.session_state:
            client = OpenAI(api_key=st.secrets['OPENAI_API_KEY'])
            # Prompt alterado para NÃO usar nomes na frase
            res = client.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "user", "content": f"Crie uma frase curta e inspiradora sobre inclusão escolar. Não use nomes. Máximo 20 palavras."}])
            st.session_state['banner_msg'] = res.choices[0].message.content
        mensagem_banner = st.session_state['banner_msg']
    except: pass

# --- SIDEBAR (SÓ AGORA) ---
with st.sidebar:
    if "usuario_nome" in st.session_state:
        st.markdown(f"**👤 {st.session_state['usuario_nome']}**")
        st.caption(f"{st.session_state['usuario_cargo']}")
        st.markdown("---")

    st.markdown("### 📢 Central de Feedback")
    tipo = st.selectbox("Tipo:", ["Sugestão", "Erro", "Elogio"])
    msg = st.text_area("Mensagem:", height=80)
    # Habilita botão na sidebar
    st.markdown("<style>section[data-testid='stSidebar'] .stButton button { display: block !important; }</style>", unsafe_allow_html=True)
    if st.button("Enviar"):
        if msg: st.toast("Enviado!", icon="✅"); time.sleep(1)

# --- HERO SECTION ---
st.markdown(f"""
<div class="dash-hero hover-spring">
    <div class="hero-text-block">
        <div class="hero-title">Olá, {nome_display}!</div>
        <div class="hero-subtitle">"{mensagem_banner}"</div>
    </div>
    <i class="ri-heart-pulse-fill hero-bg-icon"></i>
</div>
""", unsafe_allow_html=True)

# FERRAMENTAS COMO BOTÕES GRANDES (SEM TÍTULO, SÓ LOGO)
st.markdown("<div class='section-title'><i class='ri-cursor-fill'></i> Acesso Rápido</div>", unsafe_allow_html=True)

logo_pei = get_base64_image("360.png")
logo_paee = get_base64_image("pae.png")
logo_hub = get_base64_image("hub.png")

c1, c2, c3 = st.columns(3)

def card_botao(coluna, img_b64, desc, chave_btn, page_path, cor_borda_class, fallback_icon):
    with coluna:
        # Renderiza o Card Visual (Sem Título)
        img_html = f'<img src="data:image/png;base64,{img_b64}" class="nav-icon">' if img_b64 else f'<i class="{fallback_icon}" style="font-size:3rem; margin-bottom:10px;"></i>'
        
        st.markdown(f"""
        <div class="nav-btn-card {cor_borda_class}">
            {img_html}
            <div class="nav-desc">{desc}</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Botão invisível esticado sobre o card para capturar o clique
        if st.button(f"Acessar {desc[:5]}", key=chave_btn, use_container_width=True):
            st.switch_page(page_path)

# Card 1: PEI
card_botao(c1, logo_pei, "Plano de Ensino Individualizado Oficial.", "btn_pei", "pages/1_PEI.py", "b-blue", "ri-book-read-line")

# Card 2: PAEE
card_botao(c2, logo_paee, "Sala de Recursos e Tecnologias Assistivas.", "btn_paee", "pages/2_PAE.py", "b-purple", "ri-puzzle-line")

# Card 3: HUB
card_botao(c3, logo_hub, "Adaptação de provas e roteiros.", "btn_hub", "pages/3_Hub_Inclusao.py", "b-teal", "ri-rocket-line")

# BENTO GRID (BASE DE CONHECIMENTO)
st.markdown("<div class='section-title'><i class='ri-book-mark-fill'></i> Conhecimento</div>", unsafe_allow_html=True)

st.markdown("""
<div class="bento-grid">
    <a href="#" class="bento-item">
        <div class="bento-icon" style="background:#EBF8FF; color:#3182CE;"><i class="ri-question-answer-line"></i></div>
        <div class="bento-title">PEI vs PAEE</div>
        <div class="bento-desc">Diferenças fundamentais.</div>
    </a>
    <a href="https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2015/lei/l13146.htm" target="_blank" class="bento-item">
        <div class="bento-icon" style="background:#FFFFF0; color:#D69E2E;"><i class="ri-scales-3-line"></i></div>
        <div class="bento-title">Legislação</div>
        <div class="bento-desc">LBI e Decretos.</div>
    </a>
    <a href="https://institutoneurosaber.com.br/" target="_blank" class="bento-item">
        <div class="bento-icon" style="background:#FFF5F7; color:#D53F8C;"><i class="ri-brain-line"></i></div>
        <div class="bento-title">Neurociência</div>
        <div class="bento-desc">Desenvolvimento atípico.</div>
    </a>
    <a href="http://basenacionalcomum.mec.gov.br/" target="_blank" class="bento-item">
        <div class="bento-icon" style="background:#F0FFF4; color:#38A169;"><i class="ri-compass-3-line"></i></div>
        <div class="bento-title">BNCC</div>
        <div class="bento-desc">Currículo oficial.</div>
    </a>
</div>
""", unsafe_allow_html=True)

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

st.markdown(f"""
<div class="insight-card-end hover-spring">
    <div class="insight-icon-end"><i class="ri-lightbulb-flash-line"></i></div>
    <div>
        <div style="font-weight: 800; font-size: 0.8rem; color: #D69E2E; letter-spacing: 0.5px; text-transform: uppercase;">Insight do Dia</div>
        <p style="margin:2px 0 0 0; font-size:0.9rem; opacity:0.9; color:#4A5568; font-style: italic;">"{noticia_insight}"</p>
    </div>
</div>
""", unsafe_allow_html=True)

# ASSINATURA FINAL ATUALIZADA
st.markdown("<div style='text-align: center; color: #CBD5E0; font-size: 0.7rem; margin-top: 40px;'>Omnisfera desenvolvida e CRIADA por RODRIGO A. QUEIROZ; assim como PEI360, PAEE360 & HUB de Inclusão</div>", unsafe_allow_html=True)
