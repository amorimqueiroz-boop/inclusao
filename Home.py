import streamlit as st
from datetime import date
from openai import OpenAI
import base64
import os
import time

# --- 1. CONFIGURAÇÃO INICIAL ---
st.set_page_config(
    page_title="[TESTE] Omnisfera",  # Mudei o título da aba também
    page_icon="🛠️", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==============================================================================
# 🛠️ VISUAL DE AMBIENTE DE TESTES (Faixa de Alerta)
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
</style>
<div class="test-environment-bar"></div>
<div class="test-badge">🛠️ AMBIENTE DE TESTES</div>
""", unsafe_allow_html=True)


# ==============================================================================
# 🛠️ UTILITÁRIOS (IMAGENS)
# ==============================================================================
def get_base64_image(image_path):
    if not os.path.exists(image_path): return ""
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

# Carregamos a imagem da logo para usar no Loader e no Canto
img_logo_b64 = get_base64_image("omni_icone.png")
if not img_logo_b64:
    # Fallback caso a imagem não exista (icone genérico de internet)
    src_logo = "https://cdn-icons-png.flaticon.com/512/1183/1183672.png"
else:
    src_logo = f"data:image/png;base64,{img_logo_b64}"

# ==============================================================================
# ✨ LOADER E LOGO GIRATÓRIA (CSS + JS)
# ==============================================================================
st.markdown(f"""
<style>
    /* DEFINIÇÃO DA ANIMAÇÃO DE ROTAÇÃO */
    @keyframes girar-suave {{
        from {{ transform: rotate(0deg); }}
        to {{ transform: rotate(360deg); }}
    }}

    /* 1. TELA DE LOADING */
    #loader-overlay {{
        position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
        background: #F7FAFC; z-index: 999999;
        display: flex; flex-direction: column; justify-content: center; align-items: center;
        transition: opacity 0.5s ease;
    }}
    
    /* 2. LOGO NO CANTO (BRANDING PERSISTENTE) */
    .brand-corner {{
        position: fixed; bottom: 20px; right: 20px;
        width: 50px; height: 50px; z-index: 999998;
        cursor: pointer; opacity: 0.6; transition: all 0.3s ease;
        filter: grayscale(100%);
    }}
    .brand-corner:hover {{
        opacity: 1; transform: scale(1.15);
        filter: grayscale(0%);
    }}
    .brand-corner img {{
        width: 100%; height: 100%; object-fit: contain;
    }}
    .brand-corner:hover img {{
        animation: girar-suave 2.5s linear infinite;
    }}
</style>

<div id="loader-overlay">
    <div style="width: 90px; height: 90px; animation: girar-suave 1.2s linear infinite;">
        <img src="{src_logo}" style="width:100%; height:100%; object-fit:contain;">
    </div>
    <p style="margin-top:20px; font-family:'Nunito', sans-serif; color:#4A5568; font-weight:600; letter-spacing:1px;">CARREGANDO TESTE...</p>
</div>

<div class="brand-corner" title="Omnisfera Teste">
    <img src="{src_logo}">
</div>

<script>
    window.addEventListener('load', function() {{
        setTimeout(function() {{
            var loader = document.getElementById('loader-overlay');
            if (loader) {{
                loader.style.opacity = '0'; 
                setTimeout(function() {{ loader.style.display = 'none'; }}, 500); 
            }}
        }}, 1000); // Carregamento mais rápido no teste (1s)
    }});
    
    setTimeout(function() {{
        var loader = document.getElementById('loader-overlay');
        if (loader) {{
            loader.style.opacity = '0';
            setTimeout(function() {{ loader.style.display = 'none'; }}, 500);
        }}
    }}, 2000);
</script>
""", unsafe_allow_html=True)


# ==============================================================================
# 🔐 SEGURANÇA (MODO TESTE: SEM SENHA)
# ==============================================================================

def sistema_seguranca():
    # CSS Específico para a Tela de Login
    st.markdown("""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&family=Nunito:wght@400;600;700&display=swap');
            
            [data-testid="stHeader"] {visibility: hidden !important; height: 0px !important;}
            footer {visibility: hidden !important;}
            
            .block-container {
                padding-top: 1rem !important;
                margin-top: 0rem !important;
            }
            
            .login-container { 
                background-color: white; 
                padding: 5px 40px 40px 40px; 
                border-radius: 20px; 
                box-shadow: 0 10px 30px rgba(0,0,0,0.08); 
                text-align: center; 
                border: 2px dashed #FF9800; /* Borda laranja para indicar teste */
                max-width: 550px;
                margin: 0 auto;
                margin-top: 20px;
            }

            @keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
            .login-logo-spin {
                height: 110px; width: auto;
                animation: spin 45s linear infinite; 
                filter: drop-shadow(0 4px 8px rgba(0,0,0,0.1));
            }
            .login-logo-static { height: 75px; width: auto; margin-left: 10px; }
            
            .logo-wrapper { 
                display: flex; justify-content: center; align-items: center; 
                margin-bottom: 20px; 
                margin-top: 10px;
            }

            .manifesto-login {
                font-family: 'Nunito', sans-serif; font-size: 0.9rem; color: #4A5568;
                font-style: italic; line-height: 1.5; margin-bottom: 30px; padding: 0 15px;
            }

            .stTextInput input {
                border-radius: 8px !important; border: 1px solid #CBD5E0 !important;
                padding: 10px !important; background-color: #F8FAFC !important;
            }

            .termo-box { 
                background-color: #FFF3E0; /* Fundo levemente laranja */
                padding: 15px; border-radius: 8px; 
                height: 120px; overflow-y: scroll; font-size: 0.75rem; 
                border: 1px solid #FFCC80; margin-bottom: 20px; text-align: left; 
                color: #E65100; line-height: 1.4;
            }
            
            div[data-testid="column"] .stButton button {
                width: 100%; background-color: #FF9800 !important; /* Botão Laranja */
                color: white !important;
                border-radius: 8px !important; font-weight: 700 !important; height: 50px !important; border: none !important;
            }
            div[data-testid="column"] .stButton button:hover { background-color: #F57C00 !important; }
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
                st.markdown(f"""
                <div class="logo-wrapper">
                    <img src="data:image/png;base64,{icone_b64}" class="login-logo-spin">
                    <img src="data:image/png;base64,{texto_b64}" class="login-logo-static">
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("<h1 style='color:#E65100; margin-top:0;'>🛠️ OMNISFERA TEST</h1>", unsafe_allow_html=True)

            st.markdown("""
            <div class="manifesto-login">
                "Ambiente destinado a testes e validação de novas funcionalidades.
                Dados inseridos aqui <strong>não são salvos</strong> permanentemente."
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("<div style='text-align:left; font-weight:bold; color:#2D3748; font-size:0.9rem; margin-bottom:5px;'>👋 Identidade de Teste</div>", unsafe_allow_html=True)
            nome_user = st.text_input("nome_fake", value="Usuário Teste", placeholder="Seu nome", label_visibility="collapsed")
            st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
            cargo_user = st.text_input("cargo_fake", value="Desenvolvedor", placeholder="Seu cargo", label_visibility="collapsed")
            
            st.markdown("---")

            st.markdown("<div style='text-align:left; font-weight:bold; color:#E65100; font-size:0.9rem; margin-bottom:5px;'>⚠️ Termos de Teste</div>", unsafe_allow_html=True)
            st.markdown("""
            <div class="termo-box">
                <strong>AMBIENTE DE DESENVOLVIMENTO (SANDBOX)</strong><br><br>
                1. Este ambiente é instável e pode sofrer alterações a qualquer momento.<br>
                2. Não insira dados reais de alunos (LGPD). Use apenas dados fictícios.<br>
                3. A autenticação por senha está DESABILITADA para facilitar os testes.
            </div>
            """, unsafe_allow_html=True)
            
            concordo = st.checkbox("Estou ciente que é um ambiente de teste.", value=True)
            st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
            
            # Campo de senha visual, mas inútil
            senha = st.text_input("senha_fake", type="password", placeholder="Senha (Opcional no Teste)", label_visibility="collapsed")
            st.caption("🔓 Modo Teste: Senha liberada")
            
            st.markdown("<div style='height:15px'></div>", unsafe_allow_html=True)
            
            if st.button("🚀 ENTRAR NO MODO TESTE"):
                if not concordo:
                    st.warning("⚠️ Confirme os termos de teste.")
                elif not nome_user or not cargo_user:
                    st.warning("⚠️ Preencha Nome e Cargo (apenas para exibição).")
                else:
                    # LOGICA MÁGICA: Não checa a senha!
                    st.session_state["autenticado"] = True
                    st.session_state["usuario_nome"] = nome_user
                    st.session_state["usuario_cargo"] = cargo_user
                    st.rerun()
            
            st.markdown("</div>", unsafe_allow_html=True)
        return False
    return True

if not sistema_seguranca(): st.stop()

# ==============================================================================
# 🧠 GERAÇÃO DE CONTEÚDO (IA)
# ==============================================================================
nome_display = st.session_state.get("usuario_nome", "Dev").split()[0]
mensagem_banner = f"Olá, {nome_display}! Bem-vindo ao Laboratório da Omnisfera. Teste com segurança."

# ==============================================================================
# 🏠 HOME - DASHBOARD OMNISFERA (MODO TESTE)
# ==============================================================================

with st.sidebar:
    if "usuario_nome" in st.session_state:
        st.markdown(f"**🛠️ {st.session_state['usuario_nome']}**")
        st.caption(f"{st.session_state['usuario_cargo']}")
        st.markdown("---")

    st.markdown("### 📢 Reportar Bugs")
    st.info("Você está no ambiente de testes. Se algo quebrar, avise!")
    
    tipo_feedback = st.selectbox("Tipo:", ["Bug / Erro", "Melhoria"], label_visibility="collapsed")
    texto_feedback = st.text_area("O que aconteceu?", height=100, label_visibility="collapsed", placeholder="Descreva o erro...")
    
    if st.button("Registrar Bug", use_container_width=True):
        st.toast("Bug registrado! (Simulação)", icon="🪲")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&family=Nunito:wght@400;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Nunito', sans-serif; color: #2D3748; background-color: #FFF8E1; } /* Fundo levemente amarelado */
    
    .logo-container {
        display: flex; align-items: center; justify-content: center;
        gap: 20px; 
        position: fixed; top: 12px; left: 0; width: 100%; /* Ajuste por causa da faixa de teste */
        background-color: #FFF8E1; z-index: 999; 
        padding-top: 15px; padding-bottom: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
    }

    .block-container { 
        padding-top: 180px !important; 
        padding-bottom: 3rem !important; 
        margin-top: 0rem !important;
    }

    @keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
    .logo-icon-spin {
        height: 120px; width: auto;
        animation: spin 45s linear infinite; 
        filter: drop-shadow(0 4px 8px rgba(0,0,0,0.1));
    }
    .logo-text-static { height: 80px; width: auto; }

    .dash-hero { 
        background: linear-gradient(135deg, #FF9800 0%, #E65100 100%); /* Laranja para diferenciar */
        border-radius: 16px; margin-bottom: 40px; 
        box-shadow: 0 10px 25px rgba(230, 81, 0, 0.25);
        color: white; position: relative; overflow: hidden;
        padding: 50px 60px;
        display: flex; align-items: center; justify-content: flex-start;
    }
    .hero-text-block { z-index: 2; text-align: left; max-width: 90%; }
    .hero-title {
        color: white; font-family: 'Inter', sans-serif; font-weight: 700; 
        font-size: 2.2rem; margin: 0; line-height: 1.1; letter-spacing: -0.5px;
        margin-bottom: 15px;
    }
    .hero-subtitle {
        color: rgba(255,255,255,0.95); font-family: 'Inter', sans-serif;
        font-size: 1.15rem; font-weight: 400; line-height: 1.5; font-style: italic;
    }
    .hero-bg-icon {
        position: absolute; right: 40px; font-size: 6rem;
        opacity: 0.1; color: white; transform: rotate(-15deg); top: 30px;
    }

    .tool-card { 
        background: white; border-radius: 20px; padding: 25px; 
        box-shadow: 0 4px 10px rgba(0,0,0,0.03); border: 1px solid #E2E8F0; 
        height: 100%; display: flex; flex-direction: column; justify-content: space-between; 
        transition: all 0.3s ease; text-align: center;
    }
    .tool-card:hover { transform: translateY(-8px); border-color: #FF9800; box-shadow: 0 15px 30px rgba(0,0,0,0.1); }
    
    .card-logo-box { height: 110px; display: flex; align-items: center; justify-content: center; margin-bottom: 10px; }
    .card-logo-img { max-height: 95px; width: auto; object-fit: contain; filter: drop-shadow(0 4px 6px rgba(0,0,0,0.05)); }
    .tool-desc-short { font-size: 0.9rem; color: #4A5568; font-weight: 500; margin-bottom: 15px; min-height: 45px; display: flex; align-items: center; justify-content: center; line-height: 1.3; }
    
    div[data-testid="column"] .stButton button {
        width: 100%; border-radius: 12px; border: 1px solid #E2E8F0;
        background-color: #F8F9FA; color: #2D3748; font-family: 'Inter', sans-serif; font-weight: 700; 
        font-size: 1rem; padding: 12px 0; transition: all 0.2s;
    }
    div[data-testid="column"] .stButton button:hover { background-color: #FF9800; color: white; border-color: #FF9800; }
    
    .border-blue { border-bottom: 6px solid #FF9800; } 
    .border-purple { border-bottom: 6px solid #FF9800; } 
    .border-teal { border-bottom: 6px solid #FF9800; }

    .section-title { font-family: 'Inter', sans-serif; font-weight: 700; font-size: 1.4rem; color: #2D3748; margin-bottom: 20px; display: flex; align-items: center; gap: 10px; }
    .section-title i { color: #FF9800; }

</style>
<link href="https://cdn.jsdelivr.net/npm/remixicon@4.1.0/fonts/remixicon.css" rel="stylesheet">
""", unsafe_allow_html=True)

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
    st.markdown("<div class='logo-container'><h1 style='color: #FF9800; margin:0;'>🛠️ OMNISFERA TEST</h1></div>", unsafe_allow_html=True)

st.markdown(f"""
<div class="dash-hero">
    <div class="hero-text-block">
        <div class="hero-title">Olá, {nome_display}!</div>
        <div class="hero-subtitle">"{mensagem_banner}"</div>
    </div>
    <i class="ri-flask-fill hero-bg-icon"></i>
</div>
""", unsafe_allow_html=True)

st.markdown("<div class='section-title'><i class='ri-test-tube-fill'></i> Ferramentas em Teste</div>", unsafe_allow_html=True)

logo_pei = get_base64_image("360.png")
logo_paee = get_base64_image("pae.png") 
logo_hub = get_base64_image("hub.png")

col1, col2, col3 = st.columns(3)

with col1:
    icon_pei = f'<img src="data:image/png;base64,{logo_pei}" class="card-logo-img">' if logo_pei else '<i class="ri-book-read-line" style="font-size:4rem; color:#FF9800;"></i>'
    st.markdown(f"""
    <div class="tool-card border-blue">
        <div class="card-logo-box">{icon_pei}</div>
        <div class="tool-desc-short">Avaliação, anamnese e geração do plano oficial do aluno.</div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("➜ Testar PEI", key="btn_pei", use_container_width=True):
        st.switch_page("pages/1_PEI.py")

with col2:
    icon_paee = f'<img src="data:image/png;base64,{logo_paee}" class="card-logo-img">' if logo_paee else '<i class="ri-puzzle-line" style="font-size:4rem; color:#FF9800;"></i>'
    st.markdown(f"""
    <div class="tool-card border-purple">
        <div class="card-logo-box">{icon_paee}</div>
        <div class="tool-desc-short">Inteligência da Sala de Recursos e Tecnologias Assistivas.</div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("➜ Testar PAEE", key="btn_paee", use_container_width=True):
        st.switch_page("pages/2_PAE.py")

with col3:
    icon_hub = f'<img src="data:image/png;base64,{logo_hub}" class="card-logo-img">' if logo_hub else '<i class="ri-rocket-line" style="font-size:4rem; color:#FF9800;"></i>'
    st.markdown(f"""
    <div class="tool-card border-teal">
        <div class="card-logo-box">{icon_hub}</div>
        <div class="tool-desc-short">Adaptação automática de provas e criação de roteiros.</div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("➜ Testar Hub", key="btn_hub", use_container_width=True):
        st.switch_page("pages/3_Hub_Inclusao.py")

st.markdown("<div style='text-align: center; color: #E65100; font-size: 0.8rem; margin-top: 40px;'>🛠️ Você está rodando uma versão de desenvolvimento (Branch: feature-logo).</div>", unsafe_allow_html=True)
