import streamlit as st
from datetime import date
from openai import OpenAI
import base64
import os
import time

# --- 1. CONFIGURAÇÃO INICIAL ---
st.set_page_config(
    page_title="Omnisfera | Ecossistema Inclusivo", 
    page_icon="🌐", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==============================================================================
# 🔐 SEGURANÇA & UTILITÁRIOS
# ==============================================================================
def get_base64_image(image_path):
    if not os.path.exists(image_path): return ""
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

def sistema_seguranca():
    # CSS: Limpa o topo e ajusta visual do Login
    st.markdown("""
        <style>
            [data-testid="stHeader"] {visibility: hidden !important; height: 0px !important;}
            footer {visibility: hidden !important;}
            
            .login-container { 
                background-color: white; 
                padding: 40px; 
                border-radius: 15px; 
                box-shadow: 0 10px 25px rgba(0,0,0,0.1); 
                text-align: center; 
                border: 1px solid #E2E8F0;
            }
            .termo-box { 
                background-color: #F7FAFC; 
                padding: 15px; 
                border-radius: 8px; 
                height: 180px; 
                overflow-y: scroll; 
                font-size: 0.75rem; 
                border: 1px solid #CBD5E0; 
                margin-bottom: 20px; 
                text-align: left;
                color: #4A5568;
                line-height: 1.5;
            }
            .termo-title {
                font-weight: bold;
                color: #2D3748;
                margin-bottom: 5px;
                font-size: 0.8rem;
            }
        </style>
    """, unsafe_allow_html=True)

    if "autenticado" not in st.session_state:
        st.session_state["autenticado"] = False

    if not st.session_state["autenticado"]:
        c1, c2, c3 = st.columns([1, 2, 1])
        with c2:
            st.markdown("<div class='login-container'>", unsafe_allow_html=True)
            
            # LOGO DO LOGIN (VOLTOU A OMNISFERA.PNG)
            try: 
                st.image("ominisfera.png", width=280)
            except: 
                st.markdown("## 🌐 OMNISFERA")
            
            st.markdown("### Portal de Acesso")
            st.markdown("---")
            
            # TERMO JURÍDICO MELHORADO
            st.markdown("##### 🛡️ Termos de Uso e Confidencialidade")
            termo_html = """
            <div class="termo-box">
                <div class="termo-title">1. PROPRIEDADE INTELECTUAL</div>
                Todo o conteúdo, algoritmos, prompts de IA e metodologia pedagógica contidos nesta plataforma ("Omnisfera") são de propriedade exclusiva de <strong>Rodrigo A. Queiroz</strong>. É estritamente proibida a cópia, reprodução, engenharia reversa ou distribuição não autorizada.<br><br>
                <div class="termo-title">2. SIGILO E DADOS</div>
                O usuário compromete-se a manter sigilo absoluto sobre as metodologias aqui apresentadas. Dados de alunos inseridos para teste devem ser fictícios ou anonimizados, em conformidade com a LGPD.<br><br>
                <div class="termo-title">3. LICENÇA DE USO</div>
                O acesso é concedido em caráter pessoal, intransferível e temporário para fins de validação pedagógica e técnica. O uso indevido acarretará no bloqueio imediato do acesso.<br><br>
                <div class="termo-title">4. ACEITE</div>
                Ao prosseguir, você declara estar ciente e de acordo com todas as cláusulas acima.
            </div>
            """
            st.markdown(termo_html, unsafe_allow_html=True)
            
            concordo = st.checkbox("Li, compreendi e aceito os termos de uso.")
            st.write("")
            senha = st.text_input("Chave de Acesso:", type="password")
            
            if st.button("🚀 ACESSAR ECOSSISTEMA", type="primary", use_container_width=True):
                hoje = date.today()
                senha_correta = "PEI_START_2026" if hoje <= date(2026, 1, 19) else "OMNI_PRO"
                
                if not concordo:
                    st.warning("⚠️ É necessário aceitar os termos para continuar.")
                elif senha == senha_correta:
                    st.session_state["autenticado"] = True
                    st.rerun()
                else:
                    st.error("🚫 Credenciais inválidas.")
            
            st.markdown("</div>", unsafe_allow_html=True)
        return False
    return True

# EXECUTA O LOGIN
if not sistema_seguranca(): st.stop()

# ==============================================================================
# 🏠 HOME - DASHBOARD (CORRIGIDA E POLIDA)
# ==============================================================================

# CSS GERAL
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Nunito:wght@300;400;600;700;800&display=swap');
    html, body, [class*="css"] { font-family: 'Nunito', sans-serif; color: #2D3748; }
    
    /* 1. TOPO COLADO */
    .block-container { 
        padding-top: 1rem !important; 
        padding-bottom: 2rem !important; 
        margin-top: 0rem !important;
    }

    /* --- LOGO GIGANTE ANIMADA --- */
    @keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
    
    .logo-container {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 15px; 
        margin-bottom: 0px; /* Colado no banner */
        padding-top: 0px;
    }
    .logo-icon-spin {
        height: 140px; 
        width: auto;
        animation: spin 30s linear infinite;
        filter: drop-shadow(0 4px 8px rgba(0,0,0,0.1));
    }
    .logo-text-static {
        height: 90px; 
        width: auto;
    }

    /* --- ANIMAÇÃO TEXTO (FADE) --- */
    @keyframes textFade1 {
        0%, 45% { opacity: 1; transform: translateY(0); }
        50%, 100% { opacity: 0; transform: translateY(-10px); }
    }
    @keyframes textFade2 {
        0%, 45% { opacity: 0; transform: translateY(10px); }
        50%, 100% { opacity: 1; transform: translateY(0); }
    }

    /* --- HERO BANNER (SLIM & CORRIGIDO) --- */
    .dash-hero { 
        background: linear-gradient(135deg, #0F52BA 0%, #062B61 100%); 
        border-radius: 12px;
        margin-bottom: 30px; 
        box-shadow: 0 4px 10px rgba(15, 82, 186, 0.2);
        color: white;
        position: relative;
        overflow: hidden;
        height: 80px; /* Altura fixa fina */
        display: flex;
        align-items: center;
        justify-content: center;
    }
    
    .hero-content-wrapper {
        position: relative;
        width: 100%;
        height: 100%;
        display: flex;
        align-items: center;
        justify-content: center;
    }

    .hero-text-block {
        position: absolute;
        width: 100%;
        text-align: center;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
    }
    
    /* Ciclo de Animação */
    .state-1 { animation: textFade1 50s infinite; }
    .state-2 { animation: textFade2 50s infinite; }

    .hero-title {
        color: white; 
        font-family: 'Nunito', sans-serif;
        font-weight: 700; 
        font-size: 1.5rem; 
        margin: 0; 
        line-height: 1.1;
        letter-spacing: 0.5px;
    }
    .hero-subtitle {
        color: rgba(255,255,255,0.9);
        font-size: 0.85rem;
        margin-top: 2px; 
        font-weight: 300; 
        font-style: italic;
    }
    
    .hero-bg-icon {
        position: absolute; 
        right: 20px; 
        font-size: 3rem;
        opacity: 0.1; 
        color: white; 
        transform: rotate(-10deg);
        top: 15px;
    }

    /* --- INSIGHT CARD --- */
    .insight-card {
        background-color: #FFFFF0;
        border-radius: 12px;
        padding: 15px 20px;
        color: #2D3748;
        display: flex; align-items: center; gap: 15px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        border: 1px solid #F6E05E; 
        margin-bottom: 30px;
        margin-top: 10px;
    }
    .insight-icon { font-size: 1.4rem; color: #D69E2E; }

    /* --- BOTÕES E CARDS --- */
    .tool-card { background: white; border-radius: 12px; padding: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.04); border: 1px solid #E2E8F0; height: 100%; display: flex; flex-direction: column; justify-content: space-between; transition: all 0.2s; }
    .tool-card:hover { transform: translateY(-3px); border-color: #3182CE; box-shadow: 0 8px 16px rgba(0,0,0,0.08); }
    .tool-title { font-size: 1.2rem; font-weight: 800; color: #2D3748; margin-bottom: 5px; }
    .tool-desc { font-size: 0.85rem; color: #718096; margin-bottom: 15px; line-height: 1.4; }
    .border-blue { border-top: 4px solid #3182CE; } .border-purple { border-top: 4px solid #805AD5; } .border-teal { border-top: 4px solid #38B2AC; }
    
    .home-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; }
    .rich-card { background: white; border-radius: 12px; padding: 15px; border: 1px solid #E2E8F0; box-shadow: 0 2px 4px rgba(0,0,0,0.02); transition: all 0.2s; text-decoration: none; color: inherit; display: flex; flex-direction: column; align-items: center; text-align: center; position: relative; overflow: hidden; height: 100%; }
    .rich-card:hover { transform: translateY(-3px); box-shadow: 0 5px 10px rgba(0,0,0,0.05); }
    .rich-card-top { width: 100%; height: 3px; position: absolute; top: 0; left: 0; }
    .rc-icon { width: 40px; height: 40px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 1.3rem; margin-bottom: 10px; }
    .rc-title { font-weight: 700; font-size: 0.95rem; color: #2D3748; margin-bottom: 4px; }
    .rc-desc { font-size: 0.75rem; color: #718096; line-height: 1.3; }
</style>
<link href="https://cdn.jsdelivr.net/npm/remixicon@4.1.0/fonts/remixicon.css" rel="stylesheet">
""", unsafe_allow_html=True)

# FRASE DO DIA (IA)
noticia = "A neurociência na escola revela como o aprendizado é moldado pelo cérebro, otimizando o ensino para cada aluno."
if 'OPENAI_API_KEY' in st.secrets:
    try:
        if 'home_insight' not in st.session_state:
            client = OpenAI(api_key=st.secrets['OPENAI_API_KEY'])
            res = client.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "user", "content": "Curiosidade curtíssima sobre neurociência na educação."}])
            st.session_state['home_insight'] = res.choices[0].message.content
        noticia = st.session_state['home_insight']
    except: pass

# --- 1. CABEÇALHO LOGO GIGANTE ANIMADA ---
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
    # Fallback se as imagens não existirem
    st.markdown("<h1 style='text-align: center; color: #0F52BA; font-size: 3rem; margin-bottom:10px;'>🌐 OMNISFERA</h1>", unsafe_allow_html=True)


# --- 2. HERO BANNER "VIVO" (CORRIGIDO PARA EXIBIR HTML) ---
st.markdown(f"""
<div class="dash-hero">
    <div class="hero-content-wrapper">
        <div class="hero-text-block state-1">
            <div class="hero-title">Olá, Educador(a)!</div>
            <div class="hero-subtitle">"Cada criança é única; seu potencial, ilimitado!"</div>
        </div>
        
        <div class="hero-text-block state-2">
            <div class="hero-title">O Ecossistema Omnisfera</div>
            <div class="hero-subtitle">Unindo neurociência, legislação e estratégia pedagógica.</div>
        </div>
    </div>
    <i class="ri-global-line hero-bg-icon"></i>
</div>
""", unsafe_allow_html=True)

# --- 3. FERRAMENTAS DE ACESSO ---
st.markdown("### 🎯 Acesso Rápido")
col1, col2, col3 = st.columns(3)

# PEI
with col1:
    st.markdown("""
    <div class="tool-card border-blue">
        <div>
            <div class="tool-title"><i class="ri-book-read-line" style="color:#3182CE; margin-right:5px;"></i> PEI 360º</div>
            <div class="tool-desc">
                <strong>Plano de Ensino Individualizado</strong><br>
                A porta de entrada. Anamnese e plano oficial.
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Acessar PEI ➡️", key="btn_pei", use_container_width=True):
        st.switch_page("pages/1_PEI.py")

# PAE
with col2:
    st.markdown("""
    <div class="tool-card border-purple">
        <div>
            <div class="tool-title"><i class="ri-puzzle-line" style="color:#805AD5; margin-right:5px;"></i> PAE</div>
            <div class="tool-desc">
                <strong>Plano de AEE</strong><br>
                Focado na Sala de Recursos. Identifique barreiras e tecnologias assistivas.
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Acessar PAE ➡️", key="btn_pae", use_container_width=True):
        st.switch_page("pages/2_PAE.py")

# HUB
with col3:
    st.markdown("""
    <div class="tool-card border-teal">
        <div>
            <div class="tool-title"><i class="ri-rocket-line" style="color:#38B2AC; margin-right:5px;"></i> Hub</div>
            <div class="tool-desc">
                <strong>Adaptação & Criação</strong><br>
                Adapte provas e crie atividades em segundos.
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Acessar Hub ➡️", key="btn_hub", type="primary", use_container_width=True):
        st.switch_page("pages/3_Hub_Inclusao.py")

# --- 4. INSIGHT DO DIA ---
st.markdown(f"""
<div class="insight-card">
    <div class="insight-icon"><i class="ri-lightbulb-flash-line"></i></div>
    <div>
        <div style="font-weight: 700; font-size: 0.9rem; color: #D69E2E;">Curiosidade do Dia (IA):</div>
        <p style="margin:2px 0 0 0; font-size:0.9rem; opacity:0.9; color:#4A5568; font-style: italic;">"{noticia}"</p>
    </div>
</div>
""", unsafe_allow_html=True)

# --- 5. RECURSOS EDUCATIVOS (RODAPÉ) ---
st.markdown("### 📚 Base de Conhecimento")
st.markdown("""
<div class="home-grid">
    <a href="#" class="rich-card">
        <div class="rich-card-top" style="background-color: #3182CE;"></div>
        <div class="rc-icon" style="background-color:#EBF8FF; color:#3182CE;"><i class="ri-question-answer-line"></i></div>
        <div class="rc-title">PEI vs PAE</div>
        <div class="rc-desc">Diferenças fundamentais.</div>
    </a>
    <a href="https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2015/lei/l13146.htm" target="_blank" class="rich-card">
        <div class="rich-card-top" style="background-color: #D69E2E;"></div>
        <div class="rc-icon" style="background-color:#FFFFF0; color:#D69E2E;"><i class="ri-scales-3-line"></i></div>
        <div class="rc-title">Legislação</div>
        <div class="rc-desc">LBI e Decretos (2025).</div>
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

st.markdown("---")
st.markdown("<div style='text-align: center; color: #A0AEC0; font-size: 0.8rem;'>Omnisfera © 2026 - Todos os direitos reservados.</div>", unsafe_allow_html=True)
