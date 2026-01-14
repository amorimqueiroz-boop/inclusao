import streamlit as st
from datetime import date
from openai import OpenAI
import base64
import os
import time

# --- 1. CONFIGURAÇÃO INICIAL (ADAPTADA PARA TESTE) ---
st.set_page_config(
    page_title="[TESTE] Omnisfera", # Alterado para identificar na aba
    page_icon="🛠️", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==============================================================================
# ### BLOCO VISUAL INTELIGENTE: HEADER OMNISFERA (TEXT ONLY) ###
# ==============================================================================
import os
import streamlit as st

# 1. Detecção Automática de Ambiente (Via st.secrets)
try:
    IS_TEST_ENV = st.secrets.get("ENV") == "TESTE"
except:
    IS_TEST_ENV = False

# 2. Definição Dinâmica de Cores e Texto
if IS_TEST_ENV:
    # Ambiente de Teste: Amarelo
    card_bg = "rgba(255, 220, 50, 0.95)" 
    card_border = "rgba(200, 160, 0, 0.5)"
    display_text = "OMNISFERA | TESTE"
else:
    # Ambiente Oficial: Branco Gelo (Vidro)
    card_bg = "rgba(255, 255, 255, 0.85)"
    card_border = "rgba(255, 255, 255, 0.6)"
    display_text = "OMNISFERA 360º"

# 3. Renderização do CSS Global e Header Flutuante
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    
    /* -------------------------------------------- */

    /* CARD FLUTUANTE (TEXTO CHIQUE) */
    .omni-badge {{
        position: fixed;
        top: 15px; 
        right: 15px;
        
        /* COR DINÂMICA */
        background: {card_bg};
        border: 1px solid {card_border};
        
        backdrop-filter: blur(8px);
        -webkit-backdrop-filter: blur(8px);
        
        /* Layout */
        padding: 6px 25px;
        min-width: 220px;          /* Largura suficiente para cobrir os botões */
        border-radius: 12px;       /* Bordas levemente arredondadas (mais elegante que pílula total) */
        
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        z-index: 999990;
        
        display: flex;
        align-items: center;
        justify-content: center;
        pointer-events: none;
    }}

    /* Tipografia Discreta e Elegante */
    .omni-text {{
        font-family: 'Inter', sans-serif;
        font-weight: 700;          /* Negrito na medida */
        font-size: 0.75rem;        /* Tamanho discreto */
        color: #2D3748;            /* Cinza Chumbo */
        letter-spacing: 2px;       /* Espaçamento "Chique" */
        text-transform: uppercase;
    }}

</style>

<div class="omni-badge">
    <span class="omni-text">{display_text}</span>
</div>
""", unsafe_allow_html=True)
# ==============================================================================
# ### FIM BLOCO VISUAL INTELIGENTE ###
# ==============================================================================


# ==============================================================================
# 🔐 SEGURANÇA, LOGIN E UTILITÁRIOS
# ==============================================================================
def get_base64_image(image_path):
    if not os.path.exists(image_path): return ""
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

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
                border: 1px solid #E2E8F0;
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
                font-family: 'Nunito', sans-serif;
                font-size: 0.9rem;
                color: #4A5568;
                font-style: italic;
                line-height: 1.5;
                margin-bottom: 30px;
                padding: 0 15px;
            }

            .stTextInput input {
                border-radius: 8px !important;
                border: 1px solid #CBD5E0 !important;
                padding: 10px !important;
                background-color: #F8FAFC !important;
            }

            .termo-box { 
                background-color: #F8FAFC; 
                padding: 15px; 
                border-radius: 8px; 
                height: 120px; 
                overflow-y: scroll; 
                font-size: 0.75rem; 
                border: 1px solid #E2E8F0; 
                margin-bottom: 20px; 
                text-align: left; 
                color: #4A5568;
                line-height: 1.4;
            }
            
            div[data-testid="column"] .stButton button {
                width: 100%;
                background-color: #0F52BA !important;
                color: white !important;
                border-radius: 8px !important;
                font-weight: 700 !important;
                height: 50px !important;
                border: none !important;
            }
            div[data-testid="column"] .stButton button:hover {
                background-color: #0A3D8F !important;
            }
            
            /* Destaque visual para modo teste */
            .teste-warning {
                color: #D69E2E; font-size: 0.8rem; font-weight: bold; margin-bottom: 10px;
            }
        </style>
    """, unsafe_allow_html=True)

    if "autenticado" not in st.session_state:
        st.session_state["autenticado"] = False

    if not st.session_state["autenticado"]:
        c_vazio1, c_login, c_vazio2 = st.columns([1, 2, 1])
        
        with c_login:
            st.markdown("<div class='login-container'>", unsafe_allow_html=True)
            
            # 1. LOGO
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
                st.markdown("<h1 style='color:#0F52BA; margin-top:0;'>🌐 OMNISFERA</h1>", unsafe_allow_html=True)

            # 2. MANIFESTO
            st.markdown("""
            <div class="manifesto-login">
                "A Omnisfera é um ecossistema vivo onde a <strong>Neurociência</strong> encontra a <strong>Pedagogia</strong>. 
                Conectamos dados, empatia e estratégia para que a inclusão deixe de ser um desafio e se torne a nossa linguagem universal."
            </div>
            """, unsafe_allow_html=True)
            
            # --- CAMPOS DE ENTRADA (CONDICIONAIS) ---
            
            nome_user = ""
            cargo_user = ""
            senha = ""
            concordo = False

            if IS_TEST_ENV:
                # --- MODO TESTE (SEM CAMPOS OBRIGATÓRIOS VISUAIS) ---
                st.markdown("<div class='teste-warning'>🛠️ MODO TESTE ATIVADO: Acesso Rápido Liberado</div>", unsafe_allow_html=True)
                # Campos opcionais para quem quiser preencher, mas não obrigatórios
                with st.expander("📝 Preencher dados (Opcional)"):
                    nome_user = st.text_input("nome_fake", placeholder="Nome (Opcional)", label_visibility="collapsed")
                    st.markdown("<div style='height:5px'></div>", unsafe_allow_html=True)
                    cargo_user = st.text_input("cargo_fake", placeholder="Cargo (Opcional)", label_visibility="collapsed")
                
                btn_texto = "🚀 ENTRAR (TESTE)"
                
            else:
                # --- MODO PÚBLICO (TUDO OBRIGATÓRIO) ---
                st.markdown("<div style='text-align:left; font-weight:bold; color:#2D3748; font-size:0.9rem; margin-bottom:5px;'>👋 Sua Identidade</div>", unsafe_allow_html=True)
                nome_user = st.text_input("nome_real", placeholder="Como gostaria de ser chamado?", label_visibility="collapsed")
                st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
                cargo_user = st.text_input("cargo_real", placeholder="Seu Cargo (Ex: Professor, Coord...)", label_visibility="collapsed")
                
                st.markdown("---")

                st.markdown("<div style='text-align:left; font-weight:bold; color:#2D3748; font-size:0.9rem; margin-bottom:5px;'>🛡️ Termos de Uso (Beta)</div>", unsafe_allow_html=True)
                st.markdown("""
                <div class="termo-box">
                    <strong>ACORDO DE CONFIDENCIALIDADE E PROPRIEDADE INTELECTUAL</strong><br><br>
                    1. <strong>Licença de Uso:</strong> Este software ("Omnisfera") encontra-se em estágio de desenvolvimento (BETA). O acesso é concedido em caráter pessoal, intransferível e temporário.<br><br>
                    2. <strong>Propriedade Intelectual:</strong> Todo o código fonte, algoritmos de IA, prompts, design de interface e metodologia pedagógica são de propriedade exclusiva de <strong>Rodrigo A. Queiroz</strong>. É estritamente vedada a cópia, engenharia reversa, print screen para divulgação pública ou comercialização de qualquer parte desta solução.<br><br>
                    3. <strong>Dados e Feedback:</strong> Ao utilizar o sistema, o usuário concorda que seus dados de navegação e feedbacks inseridos poderão ser utilizados para aprimoramento da plataforma.<br><br>
                    4. <strong>LGPD:</strong> O usuário compromete-se a não inserir dados reais sensíveis de alunos que violem a LGPD, utilizando dados fictícios para testes.
                </div>
                """, unsafe_allow_html=True)
                
                concordo = st.checkbox("Li, compreendi e concordo com os termos.")
                st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
                
                senha = st.text_input("senha_real", type="password", placeholder="Senha de Acesso", label_visibility="collapsed")
                btn_texto = "🔒 ACESSAR OMNISFERA"

            st.markdown("<div style='height:15px'></div>", unsafe_allow_html=True)
            
            # --- LÓGICA DO BOTÃO ---
            if st.button(btn_texto):
                if IS_TEST_ENV:
                    # Lógica Teste: Entra direto, usa valores padrão se vazio
                    st.session_state["autenticado"] = True
                    st.session_state["usuario_nome"] = nome_user if nome_user else "Visitante Teste"
                    st.session_state["usuario_cargo"] = cargo_user if cargo_user else "Desenvolvedor"
                    st.rerun()
                else:
                    # Lógica Pública: Validação Rigorosa
                    # Senha dinâmica baseada na data
                    hoje = date.today()
                    senha_mestra = "PEI_START_2026" if hoje <= date(2026, 1, 19) else "OMNI_PRO"

                    if not concordo:
                        st.warning("⚠️ Você precisa aceitar os termos de uso.")
                    elif not nome_user or not cargo_user:
                        st.warning("⚠️ Preencha Nome e Cargo para prosseguir.")
                    elif senha != senha_mestra:
                        st.error("🚫 Senha incorreta.")
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
# 🧠 GERAÇÃO DE CONTEÚDO (IA)
# ==============================================================================
# Personalização da mensagem
nome_display = st.session_state.get("usuario_nome", "Educador(a)").split()[0]
mensagem_banner = f"Olá, {nome_display}! Na Omnisfera, unimos ciência e afeto para revelar o potencial de cada estudante."

if 'OPENAI_API_KEY' in st.secrets:
    try:
        if 'banner_msg' not in st.session_state:
            client = OpenAI(api_key=st.secrets['OPENAI_API_KEY'])
            prompt_banner = f"""
            Crie uma frase de boas-vindas calorosa para {nome_display}, unindo o conceito de neurociência/inclusão com o potencial do aluno. Máximo 25 palavras.
            """
            res = client.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "user", "content": prompt_banner}])
            st.session_state['banner_msg'] = res.choices[0].message.content
        mensagem_banner = st.session_state['banner_msg']
    except: pass

# Curiosidade Final
noticia_insight = "A neuroplasticidade permite que o cérebro crie novos caminhos de aprendizado durante toda a vida."
if 'OPENAI_API_KEY' in st.secrets:
    try:
        if 'home_insight_end' not in st.session_state:
            client = OpenAI(api_key=st.secrets['OPENAI_API_KEY'])
            res = client.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "user", "content": "Uma curiosidade científica curta e inspiradora sobre aprendizagem e cérebro."}])
            st.session_state['home_insight_end'] = res.choices[0].message.content
        noticia_insight = st.session_state['home_insight_end']
    except: pass

# ==============================================================================
# 🏠 HOME - DASHBOARD OMNISFERA (V25 - CLEANEST LOGIN)
# ==============================================================================

# --- SIDEBAR (FEEDBACK & USER) ---
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
            # Lógica de salvar feedback poderia entrar aqui
            st.toast("Feedback enviado! Obrigado por colaborar.", icon="✅")
            time.sleep(1)
        else:
            st.warning("Escreva uma mensagem.")

st.markdown("""<style>


# --- CONTEÚDO PRINCIPAL ---
st.markdown(f"""
<div class="dash-hero">
    <div class="hero-text-block">
        <div class="hero-title">Olá, {nome_display}!</div>
        <div class="hero-subtitle">"{mensagem_banner}"</div>
    </div>
    <i class="ri-heart-pulse-fill hero-bg-icon"></i>
</div>
""", unsafe_allow_html=True)

# FERRAMENTAS
st.markdown("<div class='section-title'><i class='ri-cursor-fill'></i> Acesso Rápido</div>", unsafe_allow_html=True)

logo_pei = get_base64_image("360.png")
logo_paee = get_base64_image("pae.png") # Nome do arquivo mantido para não quebrar
logo_hub = get_base64_image("hub.png")

col1, col2, col3 = st.columns(3)

# PEI
with col1:
    icon_pei = f'<img src="data:image/png;base64,{logo_pei}" class="card-logo-img">' if logo_pei else '<i class="ri-book-read-line" style="font-size:4rem; color:#3182CE;"></i>'
    st.markdown(f"""
    <div class="tool-card border-blue">
        <div class="card-logo-box">{icon_pei}</div>
        <div class="tool-desc-short">Avaliação, anamnese e geração do plano oficial do aluno.</div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("➜ Acessar PEI", key="btn_pei", use_container_width=True):
        st.switch_page("pages/1_PEI.py")

# PAEE
with col2:
    icon_paee = f'<img src="data:image/png;base64,{logo_paee}" class="card-logo-img">' if logo_paee else '<i class="ri-puzzle-line" style="font-size:4rem; color:#805AD5;"></i>'
    st.markdown(f"""
    <div class="tool-card border-purple">
        <div class="card-logo-box">{icon_paee}</div>
        <div class="tool-desc-short">Inteligência da Sala de Recursos e Tecnologias Assistivas.</div>
    </div>
    """, unsafe_allow_html=True)
    # Botão atualizado para PAEE
    if st.button("➜ Acessar PAEE", key="btn_paee", use_container_width=True):
        st.switch_page("pages/2_PAE.py")

# HUB
with col3:
    icon_hub = f'<img src="data:image/png;base64,{logo_hub}" class="card-logo-img">' if logo_hub else '<i class="ri-rocket-line" style="font-size:4rem; color:#38B2AC;"></i>'
    st.markdown(f"""
    <div class="tool-card border-teal">
        <div class="card-logo-box">{icon_hub}</div>
        <div class="tool-desc-short">Adaptação automática de provas e criação de roteiros.</div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("➜ Acessar Hub", key="btn_hub", use_container_width=True):
        st.switch_page("pages/3_Hub_Inclusao.py")

# RODAPÉ
st.markdown("<div style='margin-top:40px;'></div>", unsafe_allow_html=True)
st.markdown("<div class='section-title'><i class='ri-book-mark-fill'></i> Base de Conhecimento</div>", unsafe_allow_html=True)

st.markdown("""
<div class="home-grid">
    <a href="#" class="rich-card">
        <div class="rich-card-top" style="background-color: #3182CE;"></div>
        <div class="rc-icon" style="background-color:#EBF8FF; color:#3182CE;"><i class="ri-question-answer-line"></i></div>
        <div class="rc-title">PEI vs PAEE</div>
        <div class="rc-desc">Diferenças fundamentais.</div>
    </a>
    <a href="https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2015/lei/l13146.htm" target="_blank" class="rich-card">
        <div class="rich-card-top" style="background-color: #D69E2E;"></div>
        <div class="rc-icon" style="background-color:#FFFFF0; color:#D69E2E;"><i class="ri-scales-3-line"></i></div>
        <div class="rc-title">Legislação</div>
        <div class="rc-desc">LBI e Decretos.</div>
    </a>
    <a href="https://institutoneurosaber.com.br/" target="_blank" class="rich-card">
        <div class="rich-card-top" style="background-color: #D53F8C;"></div>
        <div class="rc-icon" style="background-color:#FFF5F7; color:#D53F8C;"><i class="ri-brain-line"></i></div>
        <div class="rc-title">Neurociência</div>
        <div class="rc-desc">Desenvolvimento atípico.</div>
    </a>
    <a href="http://basenacionalcomum.mec.gov.br/" target="_blank" class="rich-card">
        <div class="rich-card-top" style="background-color: #38A169;"></div>
        <div class="rc-icon" style="background-color:#F0FFF4; color:#38A169;"><i class="ri-compass-3-line"></i></div>
        <div class="rc-title">BNCC</div>
        <div class="rc-desc">Currículo oficial.</div>
    </a>
</div>
""", unsafe_allow_html=True)

st.markdown(f"""
<div class="insight-card-end">
    <div class="insight-icon-end"><i class="ri-lightbulb-flash-line"></i></div>
    <div>
        <div style="font-weight: 700; font-size: 0.9rem; color: #D69E2E;">Insight do Dia (IA):</div>
        <p style="margin:2px 0 0 0; font-size:0.95rem; opacity:0.9; color:#4A5568; font-style: italic;">"{noticia_insight}"</p>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("<div style='text-align: center; color: #A0AEC0; font-size: 0.8rem; margin-top: 40px;'>Omnisfera © 2026 - Todos os direitos reservados.</div>", unsafe_allow_html=True)
