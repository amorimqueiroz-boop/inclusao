import streamlit as st
from datetime import date
from openai import OpenAI
import base64
import os
import time

# ==============================================================================
# 1. DETECÇÃO AUTOMÁTICA DE AMBIENTE
# ==============================================================================
# O sistema verifica se existe um segredo configurado no painel do Streamlit
# Se você configurar ENV = "TESTE" nos secrets, ele ativa o modo teste.
# Se não tiver nada configurado (Produção), ele assume modo seguro.
try:
    IS_TEST_ENV = st.secrets.get("ENV") == "TESTE"
except:
    IS_TEST_ENV = False

# ==============================================================================
# 2. CONFIGURAÇÃO INICIAL
# ==============================================================================
titulo_pag = "[TESTE] Omnisfera" if IS_TEST_ENV else "Omnisfera | Ecossistema"
icone_pag = "🛠️" if IS_TEST_ENV else "🌐"

st.set_page_config(
    page_title=titulo_pag,
    page_icon=icone_pag,
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==============================================================================
# 3. UTILITÁRIOS (IMAGENS)
# ==============================================================================
def get_base64_image(image_path):
    if not os.path.exists(image_path): return ""
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

# Carrega imagens para uso no CSS
b64_icone = get_base64_image("omni_icone.png")
b64_texto = get_base64_image("omni_texto.png")

# Define fonte da imagem (fallback se não existir arquivo)
src_logo = f"data:image/png;base64,{b64_icone}" if b64_icone else "https://cdn-icons-png.flaticon.com/512/1183/1183672.png"

# ==============================================================================
# 4. ESTILO GLOBAL & HEADER "GLASSMORPHISM"
# ==============================================================================
# Se for teste, injeta a faixa amarela. Se não, string vazia.
css_faixa_teste = """
    .test-stripe {
        position: fixed; top: 0; left: 0; width: 100%; height: 8px;
        background: repeating-linear-gradient(45deg, #FFC107, #FFC107 10px, #FF9800 10px, #FF9800 20px);
        z-index: 99999999; pointer-events: none;
    }
""" if IS_TEST_ENV else ""

html_faixa_teste = '<div class="test-stripe"></div>' if IS_TEST_ENV else ""

st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&family=Nunito:wght@400;600;700&display=swap');
    
    /* Esconde o Header padrão do Streamlit (Aquele com Deploy/Share) */
    header[data-testid="stHeader"] {{
        visibility: hidden;
    }}
    
    /* Esconde Rodapé */
    footer {{visibility: hidden !important;}}

    /* Ajuste do topo para o conteúdo não ficar escondido atrás da nossa barra */
    .block-container {{
        padding-top: 120px !important;
    }}

    /* --- FAIXA DE TESTE (AMARELA) --- */
    {css_faixa_teste}

    /* --- BARRA DE VIDRO (GLASS HEADER) --- */
    .glass-header {{
        position: fixed;
        top: 0; left: 0; width: 100%;
        height: 80px;
        background: rgba(255, 255, 255, 0.85); /* Branco Transparente */
        backdrop-filter: blur(12px); /* Desfoque do fundo */
        -webkit-backdrop-filter: blur(12px);
        border-bottom: 1px solid rgba(255, 255, 255, 0.3);
        box-shadow: 0 4px 20px rgba(0,0,0,0.04);
        z-index: 999990; /* Acima de tudo, mas abaixo da faixa de teste */
        display: flex;
        align-items: center;
        justify-content: center; /* Centraliza tudo */
        padding: 0 20px;
        transition: all 0.3s ease;
    }}

    /* Container interno para alinhar logo e texto */
    .header-content {{
        display: flex; align-items: center; gap: 15px;
    }}

    /* Animação da Logo */
    @keyframes spin-slow {{ from {{ transform: rotate(0deg); }} to {{ transform: rotate(360deg); }} }}
    
    .header-logo {{
        height: 45px; width: auto;
        animation: spin-slow 20s linear infinite; /* Girando suavemente */
    }}

    .header-title {{
        font-family: 'Inter', sans-serif;
        font-weight: 800;
        font-size: 1.4rem;
        background: linear-gradient(90deg, #0F52BA 0%, #3182CE 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        letter-spacing: 1px;
    }}
    
    .badge-beta {{
        background-color: #EBF8FF; color: #3182CE;
        padding: 2px 8px; border-radius: 10px;
        font-size: 0.6rem; font-weight: 700;
        margin-left: 5px; vertical-align: middle;
        border: 1px solid #BEE3F8;
    }}

</style>

{html_faixa_teste}

<div class="glass-header">
    <div class="header-content">
        <img src="{src_logo}" class="header-logo">
        <div class="header-title">OMNISFERA <span class="badge-beta">BETA</span></div>
    </div>
</div>
""", unsafe_allow_html=True)


# ==============================================================================
# 5. SISTEMA DE LOGIN (INTELIGENTE)
# ==============================================================================
def sistema_seguranca():
    # Estilização específica do container de Login
    st.markdown("""
        <style>
            .login-container { 
                background-color: white; 
                padding: 40px; 
                border-radius: 20px; 
                box-shadow: 0 10px 40px rgba(0,0,0,0.08); 
                text-align: center; 
                border: 1px solid #F7FAFC;
                max-width: 500px;
                margin: 0 auto;
                margin-top: 40px;
            }
            /* Se for teste, borda laranja */
            .border-test { border: 2px dashed #FF9800 !important; }
            
            .stTextInput input {
                border-radius: 10px !important; padding: 12px !important;
                border: 1px solid #E2E8F0 !important;
            }
            .stButton button {
                width: 100%; border-radius: 10px !important; height: 50px !important;
                font-weight: 700 !important;
            }
        </style>
    """, unsafe_allow_html=True)

    if "autenticado" not in st.session_state:
        st.session_state["autenticado"] = False

    if not st.session_state["autenticado"]:
        # Layout centralizado
        c_vazio1, c_login, c_vazio2 = st.columns([1, 1.5, 1])
        
        with c_login:
            # Adiciona classe de borda se for teste
            cls_extra = "border-test" if IS_TEST_ENV else ""
            st.markdown(f"<div class='login-container {cls_extra}'>", unsafe_allow_html=True)
            
            # Cabeçalho do Card
            if IS_TEST_ENV:
                st.markdown("<h2 style='color:#E65100; margin:0;'>🛠️ MODO TESTE</h2>", unsafe_allow_html=True)
                st.caption("Acesso liberado para desenvolvedores")
            else:
                st.markdown("<h3>Bem-vindo de volta!</h3>", unsafe_allow_html=True)
                st.caption("Acesse sua conta para continuar")

            st.markdown("---")
            
            # Campos
            nome_user = st.text_input("Seu Nome", placeholder="Como quer ser chamado?", label_visibility="collapsed")
            st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
            cargo_user = st.text_input("Seu Cargo", placeholder="Ex: Professor, Coordenação", label_visibility="collapsed")
            
            # Senha (Condicional)
            if IS_TEST_ENV:
                st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
                # Senha visual apenas, não validada
                st.text_input("Senha", placeholder="Sem senha no modo teste 🔓", disabled=True, label_visibility="collapsed")
            else:
                st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
                senha = st.text_input("Senha", type="password", placeholder="Digite sua senha de acesso", label_visibility="collapsed")

            st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
            
            # Botão de Ação
            texto_btn = "🚀 ENTRAR (TESTE)" if IS_TEST_ENV else "🔒 ACESSAR OMNISFERA"
            tipo_btn = "secondary" if IS_TEST_ENV else "primary" # Laranja (warning) vs Azul (primary)
            
            if st.button(texto_btn, type=tipo_btn):
                if not nome_user or not cargo_user:
                    st.warning("⚠️ Preencha seu Nome e Cargo.")
                else:
                    if IS_TEST_ENV:
                        # Login liberado
                        st.session_state["autenticado"] = True
                        st.session_state["usuario_nome"] = nome_user
                        st.session_state["usuario_cargo"] = cargo_user
                        st.rerun()
                    else:
                        # Validação de Produção
                        hoje = date.today()
                        senha_mestra = "PEI_START_2026" if hoje <= date(2026, 1, 19) else "OMNI_PRO"
                        if senha == senha_mestra:
                            st.session_state["autenticado"] = True
                            st.session_state["usuario_nome"] = nome_user
                            st.session_state["usuario_cargo"] = cargo_user
                            st.rerun()
                        else:
                            st.error("🚫 Senha incorreta.")

            st.markdown("</div>", unsafe_allow_html=True)
            
            if IS_TEST_ENV:
                st.markdown("<div style='text-align:center; margin-top:10px; color:#E65100; font-size:0.8rem;'>⚠️ Dados inseridos aqui são voláteis.</div>", unsafe_allow_html=True)

        return False
    return True

if not sistema_seguranca(): st.stop()

# ==============================================================================
# 6. CONTEÚDO DA HOME (DASHBOARD)
# ==============================================================================
# Daqui para baixo, o código segue normal, pois o usuário já está logado.
# O Header de Vidro continua fixo lá em cima.

nome_display = st.session_state.get("usuario_nome", "Educador").split()[0]

# Prompt IA para mensagem (Opcional, se tiver chave)
mensagem_banner = "Unindo ciência, dados e empatia para transformar a educação."
if 'OPENAI_API_KEY' in st.secrets:
    try:
        if 'banner_msg' not in st.session_state:
            client = OpenAI(api_key=st.secrets['OPENAI_API_KEY'])
            prompt_banner = f"Crie uma frase curta e inspiradora para {nome_display} sobre inclusão escolar. Máx 20 palavras. NÃO repita o nome."
            res = client.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "user", "content": prompt_banner}])
            st.session_state['banner_msg'] = res.choices[0].message.content
        mensagem_banner = st.session_state['banner_msg']
    except: pass

# --- SIDEBAR (USER INFO) ---
with st.sidebar:
    st.markdown(f"**👤 {st.session_state['usuario_nome']}**")
    st.caption(f"{st.session_state['usuario_cargo']}")
    st.markdown("---")
    st.info("💡 Dica: Use o menu superior para navegar entre PEI, PAEE e Hub.")

# --- HERO SECTION ---
st.markdown(f"""
<div style="background: linear-gradient(135deg, #0F52BA 0%, #062B61 100%); border-radius: 16px; padding: 40px 50px; color: white; margin-bottom: 40px; position: relative; overflow: hidden; box-shadow: 0 10px 30px rgba(15, 82, 186, 0.3);">
    <div style="position: relative; z-index: 2;">
        <h1 style="font-family: 'Inter', sans-serif; font-weight: 700; margin-bottom: 10px;">Olá, {nome_display}!</h1>
        <p style="font-size: 1.1rem; opacity: 0.9; max-width: 600px;">"{mensagem_banner}"</p>
    </div>
    <div style="position: absolute; right: -20px; top: -20px; opacity: 0.1; font-size: 10rem;">🌐</div>
</div>
""", unsafe_allow_html=True)

# --- GRID DE FERRAMENTAS ---
st.markdown("### 🚀 Acesso Rápido")

col1, col2, col3 = st.columns(3)

# Função auxiliar para cards
def card_ferramenta(col, titulo, desc, icone, link, cor_borda):
    with col:
        st.markdown(f"""
        <div style="background: white; border-radius: 15px; padding: 25px; height: 100%; border: 1px solid #E2E8F0; border-bottom: 5px solid {cor_borda}; box-shadow: 0 4px 6px rgba(0,0,0,0.02); transition: transform 0.2s;">
            <div style="font-size: 2.5rem; margin-bottom: 15px;">{icone}</div>
            <h3 style="margin: 0 0 10px 0; font-size: 1.2rem; color: #2D3748;">{titulo}</h3>
            <p style="color: #718096; font-size: 0.9rem; margin-bottom: 20px;">{desc}</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button(f"Acessar {titulo}", key=f"btn_{titulo}", use_container_width=True):
            st.switch_page(link)

card_ferramenta(col1, "PEI 360º", "Avaliação, anamnese e plano educacional oficial.", "📘", "pages/1_PEI.py", "#3182CE")
card_ferramenta(col2, "PAEE & T.A.", "Sala de recursos e eliminação de barreiras.", "🧩", "pages/2_PAE.py", "#805AD5")
card_ferramenta(col3, "Hub Inclusão", "Adaptação de provas e criação de materiais.", "🚀", "pages/3_Hub_Inclusao.py", "#38B2AC")

# --- RODAPÉ ---
st.markdown("<div style='margin-top: 50px; text-align: center; color: #CBD5E0; font-size: 0.8rem;'>Omnisfera © 2026</div>", unsafe_allow_html=True)
