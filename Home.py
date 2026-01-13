import streamlit as st
from datetime import date
from openai import OpenAI
import base64
import os
import time

# --- 1. CONFIGURAÇÃO INICIAL (ADAPTADA PARA TESTE) ---
st.set_page_config(
    page_title="[TESTE] Omnisfera", 
    page_icon="🛠️", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==============================================================================
# ### INICIO BLOCO TESTE: VISUAL DE ALERTA ###
# ==============================================================================
st.markdown("""
<style>
    /* Faixa de aviso no topo */
    .test-environment-bar {
        position: fixed; top: 0; left: 0; width: 100%; height: 12px;
        background: repeating-linear-gradient(45deg, #FFC107, #FFC107 10px, #FF9800 10px, #FF9800 20px);
        z-index: 9999999;
    }
    /* Selo de Teste */
    .test-badge {
        position: fixed; top: 20px; right: 20px; 
        background-color: #FF9800; color: white;
        padding: 5px 12px; border-radius: 8px;
        font-weight: 800; font-size: 0.8rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.2);
        z-index: 9999999; pointer-events: none;
    }
    .login-container { border: 2px dashed #FF9800 !important; }
</style>
<div class="test-environment-bar"></div>
<div class="test-badge">🛠️ AMBIENTE DE TESTES</div>
""", unsafe_allow_html=True)
# ==============================================================================
# ### FIM BLOCO TESTE ###
# ==============================================================================


# ==============================================================================
# 🔐 SEGURANÇA, LOGIN E UTILITÁRIOS
# ==============================================================================
def get_base64_image(image_path):
    if not os.path.exists(image_path): return ""
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

def sistema_seguranca():
    st.markdown("""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&family=Nunito:wght@400;600;700&display=swap');
            [data-testid="stHeader"] {visibility: hidden !important; height: 0px !important;}
            footer {visibility: hidden !important;}
            .block-container { padding-top: 1rem !important; margin-top: 0rem !important; }
            .login-container { 
                background-color: white; padding: 5px 40px 40px 40px; border-radius: 20px; 
                box-shadow: 0 10px 30px rgba(0,0,0,0.08); text-align: center; 
                border: 1px solid #E2E8F0; max-width: 550px; margin: 0 auto; margin-top: 20px; 
            }
            @keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
            .login-logo-spin { height: 110px; width: auto; animation: spin 45s linear infinite; filter: drop-shadow(0 4px 8px rgba(0,0,0,0.1)); }
            .login-logo-static { height: 75px; width: auto; margin-left: 10px; }
            .logo-wrapper { display: flex; justify-content: center; align-items: center; margin-bottom: 20px; margin-top: 10px; }
            .manifesto-login { font-family: 'Nunito', sans-serif; font-size: 0.9rem; color: #4A5568; font-style: italic; line-height: 1.5; margin-bottom: 30px; padding: 0 15px; }
            .stTextInput input { border-radius: 8px !important; border: 1px solid #CBD5E0 !important; padding: 10px !important; background-color: #F8FAFC !important; }
            .termo-box { background-color: #F8FAFC; padding: 15px; border-radius: 8px; height: 120px; overflow-y: scroll; font-size: 0.75rem; border: 1px solid #E2E8F0; margin-bottom: 20px; text-align: left; color: #4A5568; line-height: 1.4; }
            div[data-testid="column"] .stButton button { width: 100%; background-color: #0F52BA !important; color: white !important; border-radius: 8px !important; font-weight: 700 !important; height: 50px !important; border: none !important; }
            div[data-testid="column"] .stButton button:hover { background-color: #0A3D8F !important; }
        </style>
    """, unsafe_allow_html=True)

    if "autenticado" not in st.session_state:
        st.session_state["autenticado"] = False

    if not st.session_state["autenticado"]:
        c_vazio1, c_login, c_vazio2 = st.columns([1, 2, 1])
        with c_login:
            st.markdown("<div class='login-container'>", unsafe_allow_html=True)
            icone_b64 = get_base64_image("omni_icone.png")
            texto_b64 = get_base64_image("omni_texto.png")
            if icone_b64 and texto_b64:
                st.markdown(f"""<div class="logo-wrapper"><img src="data:image/png;base64,{icone_b64}" class="login-logo-spin"><img src="data:image/png;base64,{texto_b64}" class="login-logo-static"></div>""", unsafe_allow_html=True)
            else:
                st.markdown("<h1 style='color:#0F52BA; margin-top:0;'>🌐 OMNISFERA</h1>", unsafe_allow_html=True)

            st.markdown("""<div class="manifesto-login">"A Omnisfera é um ecossistema vivo onde a <strong>Neurociência</strong> encontra a <strong>Pedagogia</strong>. Conectamos dados, empatia e estratégia para que a inclusão deixe de ser um desafio e se torne a nossa linguagem universal."</div>""", unsafe_allow_html=True)
            
            st.markdown("<div style='text-align:left; font-weight:bold; color:#2D3748; font-size:0.9rem; margin-bottom:5px;'>👋 Sua Identidade (Para melhoria contínua)</div>", unsafe_allow_html=True)
            nome_user = st.text_input("nome_fake", placeholder="Como gostaria de ser chamado?", label_visibility="collapsed")
            st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
            cargo_user = st.text_input("cargo_fake", placeholder="Seu Cargo (Ex: Professor, Coord...)", label_visibility="collapsed")
            st.markdown("---")

            st.markdown("<div style='text-align:left; font-weight:bold; color:#2D3748; font-size:0.9rem; margin-bottom:5px;'>🛡️ Termos de Uso (Beta)</div>", unsafe_allow_html=True)
            st.markdown("""<div class="termo-box"><strong>ACORDO DE CONFIDENCIALIDADE...</strong><br>O usuário compromete-se a não inserir dados reais...</div>""", unsafe_allow_html=True)
            
            concordo = st.checkbox("Li, compreendi e concordo com os termos.")
            st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
            
            # --- ### INICIO BLOCO TESTE: SENHA OPCIONAL ### ---
            senha = st.text_input("senha_fake", type="password", placeholder="Senha (Opcional no Teste)", label_visibility="collapsed")
            st.caption("🔓 Ambiente de Teste: Senha liberada")
            # --- ### FIM BLOCO TESTE ### ---

            st.markdown("<div style='height:15px'></div>", unsafe_allow_html=True)
            
            # --- ### INICIO BLOCO TESTE: BOTÃO ### ---
            if st.button("🚀 ACESSAR (MODO TESTE)"):
                if not concordo:
                    st.warning("⚠️ Aceite os termos para continuar.")
                elif not nome_user or not cargo_user:
                    st.warning("⚠️ Preencha Nome e Cargo para prosseguir.")
                else: 
                    st.session_state["autenticado"] = True
                    st.session_state["usuario_nome"] = nome_user
                    st.session_state["usuario_cargo"] = cargo_user
                    st.rerun()
            # --- ### FIM BLOCO TESTE ### ---
            
            st.markdown("</div>", unsafe_allow_html=True)
        return False
    return True

if not sistema_seguranca(): st.stop()

# ==============================================================================
# 🧠 GERAÇÃO DE CONTEÚDO (IA) - CORREÇÃO DE NOME DUPLICADO
# ==============================================================================
nome_display = st.session_state.get("usuario_nome", "Educador(a)").split()[0]
# Frase padrão caso a IA falhe
mensagem_banner = "Na Omnisfera, unimos ciência e afeto para revelar o potencial de cada estudante."

if 'OPENAI_API_KEY' in st.secrets:
    try:
        if 'banner_msg' not in st.session_state:
            client = OpenAI(api_key=st.secrets['OPENAI_API_KEY'])
            # MUDANÇA AQUI: Instrução explícita para NÃO repetir o nome
            prompt_banner = f"""
            O usuário se chama {nome_display}.
            Crie uma frase curta e inspiradora sobre inclusão e neurociência para o dashboard dele.
            REGRA IMPORTANTE: NÃO repita o nome dele na frase. Escreva apenas a mensagem.
            Máximo 20 palavras.
            """
            res = client.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "user", "content": prompt_banner}])
            st.session_state['banner_msg'] = res.choices[0].message.content
        mensagem_banner = st.session_state['banner_msg']
    except: pass

# ==============================================================================
# 🏠 HOME - DASHBOARD OMNISFERA
# ==============================================================================
with st.sidebar:
    if "usuario_nome" in st.session_state:
        st.markdown(f"**👤 {st.session_state['usuario_nome']}**")
        st.caption(f"{st.session_state['usuario_cargo']}")
        st.markdown("---")
    st.markdown("### 📢 Central de Feedback")
    st.info("Ambiente de Testes")

# CSS e Layout (Mantidos iguais, omitidos para brevidade se já tiver)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&family=Nunito:wght@400;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Nunito', sans-serif; color: #2D3748; background-color: #F7FAFC; }
    .dash-hero { background: linear-gradient(135deg, #0F52BA 0%, #062B61 100%); border-radius: 16px; margin-bottom: 40px; padding: 50px 60px; display: flex; align-items: center; color: white; position: relative; overflow: hidden; }
    .hero-title { font-family: 'Inter', sans-serif; font-weight: 700; font-size: 2.2rem; margin: 0; margin-bottom: 10px; }
    .hero-subtitle { font-family: 'Inter', sans-serif; font-size: 1.15rem; font-style: italic; opacity: 0.9; }
    .tool-card { background: white; border-radius: 20px; padding: 25px; border: 1px solid #E2E8F0; text-align: center; height: 100%; transition: 0.3s; }
    .tool-card:hover { transform: translateY(-5px); border-color: #3182CE; }
    .section-title { font-size: 1.4rem; font-weight: 700; margin-bottom: 20px; color: #2D3748; }
</style>
""", unsafe_allow_html=True)

# HERO SECTION CORRIGIDA
st.markdown(f"""
<div class="dash-hero">
    <div style="z-index: 2;">
        <div class="hero-title">Olá, {nome_display}!</div>
        <div class="hero-subtitle">"{mensagem_banner}"</div>
    </div>
</div>
""", unsafe_allow_html=True)

# FERRAMENTAS
st.markdown("<div style='margin-top:40px;'></div>", unsafe_allow_html=True)
st.markdown("<div class='section-title'>Acesso Rápido</div>", unsafe_allow_html=True)

c1, c2, c3 = st.columns(3)
with c1:
    st.markdown("""<div class="tool-card"><h4>PEI 360</h4><p>Avaliação e Plano</p></div>""", unsafe_allow_html=True)
    if st.button("➜ Acessar PEI", use_container_width=True): st.switch_page("pages/1_PEI.py")
with c2:
    st.markdown("""<div class="tool-card"><h4>PAEE & T.A.</h4><p>Sala de Recursos</p></div>""", unsafe_allow_html=True)
    if st.button("➜ Acessar PAEE", use_container_width=True): st.switch_page("pages/2_PAE.py")
with c3:
    st.markdown("""<div class="tool-card"><h4>Hub Inclusão</h4><p>Adaptação de Provas</p></div>""", unsafe_allow_html=True)
    if st.button("➜ Acessar Hub", use_container_width=True): st.switch_page("pages/3_Hub_Inclusao.py")

st.markdown("<div style='text-align: center; color: #A0AEC0; font-size: 0.8rem; margin-top: 50px;'>Omnisfera © 2026 - Versão Beta</div>", unsafe_allow_html=True)
