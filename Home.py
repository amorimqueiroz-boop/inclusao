import streamlit as st
from datetime import date
from openai import OpenAI
import base64
import os
import time

from _client import supabase_login  # <- agora existe no _client.py
from ui_nav import render_omnisfera_nav
render_omnisfera_nav()

view = st.session_state.get("view", "home")

if view == "home":
    render_home()
elif view == "pei":
    render_pei()
elif view == "paee":
    render_paee()
elif view == "hub":
    render_hub()
elif view == "diario":
    render_diario()
elif view == "mon":
    render_monitoramento()


# ==============================================================================
# 1. CONFIGURAÇÃO INICIAL E AMBIENTE
# ==============================================================================
APP_VERSION = "v116.0"

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
# 2. UTILITÁRIOS
# ==============================================================================
def get_base64_image(image_path):
    if not os.path.exists(image_path):
        return ""
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
# 3. CSS GLOBAL
# ==============================================================================
css_estatico = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Nunito:wght@400;600;700&display=swap');
    html { scroll-behavior: smooth; }
    html, body, [class*="css"] {
        font-family: 'Nunito', sans-serif;
        color: #2D3748;
        background-color: #F7FAFC;
    }

    @keyframes fadeInUp { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
    @keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }

    .hover-spring { transition: transform 0.3s cubic-bezier(0.34, 1.56, 0.64, 1), box-shadow 0.3s ease; }
    .hover-spring:hover { transform: translateY(-3px) scale(1.01); box-shadow: 0 10px 20px rgba(0,0,0,0.06) !important; z-index: 10; }

    .block-container {
        padding-top: 130px !important;
        padding-bottom: 2rem !important;
        margin-top: 0rem !important;
        animation: fadeInUp 0.6s cubic-bezier(0.2, 0.8, 0.2, 1);
    }

    .logo-container {
        display: flex; align-items: center; justify-content: flex-start;
        gap: 15px;
        position: fixed;
        top: 0; left: 0; width: 100%; height: 90px;
        background-color: rgba(247, 250, 252, 0.85);
        backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px);
        border-bottom: 1px solid rgba(255, 255, 255, 0.5);
        z-index: 9999;
        box-shadow: 0 4px 15px rgba(0,0,0,0.03);
        padding-left: 40px;
        padding-top: 5px;
    }
    .header-subtitle-text {
        font-family: 'Nunito', sans-serif; font-weight: 600; font-size: 1rem;
        color: #718096; border-left: 2px solid #CBD5E0; padding-left: 15px;
        height: 40px; display: flex; align-items: center; letter-spacing: -0.3px;
    }
    .logo-icon-spin { height: 75px; width: auto; animation: spin 45s linear infinite; filter: drop-shadow(0 2px 4px rgba(0,0,0,0.1)); }
    .logo-text-static { height: 45px; width: auto; }

    .login-container {
        background-color: white; padding: 30px;
        border-radius: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.06);
        text-align: center; border: 1px solid #E2E8F0;
        max-width: 720px; margin: 0 auto; margin-top: 40px;
        animation: fadeInUp 0.8s ease-out;
    }

    .login-logo-spin { height: 80px; width: auto; animation: spin 45s linear infinite; margin-bottom: 5px; }
    .login-logo-static { height: 50px; width: auto; margin-left: 8px; }
    .logo-wrapper { display: flex; justify-content: center; align-items: center; margin-bottom: 15px; }

    .manifesto-login {
        font-size: 0.9rem; color: #64748B; font-style: italic; line-height: 1.6;
        margin-bottom: 18px; text-align: center; padding: 0 10px;
    }

    .termo-box {
        background-color: #F8FAFC; padding: 12px; border-radius: 10px;
        height: 90px; overflow-y: scroll; font-size: 0.7rem;
        border: 1px solid #CBD5E0; margin-bottom: 15px;
        text-align: justify; color: #4A5568; line-height: 1.3;
    }

    [data-testid="stHeader"] { visibility: hidden !important; height: 0px !important; }
    [data-testid="stToolbar"] { visibility: hidden !important; display: none !important; }
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
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# 4. LOGIN OMNISFERA + LOGIN SUPABASE (NA HOME)
# ==============================================================================
def _ensure_session_defaults():
    st.session_state.setdefault("autenticado", False)
    st.session_state.setdefault("usuario_nome", "")
    st.session_state.setdefault("usuario_cargo", "")

    # Supabase auth state
    st.session_state.setdefault("supabase_jwt", "")
    st.session_state.setdefault("supabase_user_id", "")

_ensure_session_defaults()

def _render_header_fixed():
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

_render_header_fixed()

# Badge canto direito
st.markdown(f"""<div class="omni-badge hover-spring"><span class="omni-text">{display_text}</span></div>""", unsafe_allow_html=True)

def sistema_seguranca_e_supabase():
    """
    1) Login do App (nome/cargo/termos/senha)
    2) Login do Supabase (email/senha) -> salva JWT + user_id
    """
    if st.session_state["autenticado"] and st.session_state["supabase_jwt"] and st.session_state["supabase_user_id"]:
        return True  # tudo OK

    # esconde sidebar durante login
    st.markdown("""
    <style>
        section[data-testid="stSidebar"] { display: none !important; }
        [data-testid="stSidebarCollapsedControl"] { display: none !important; }
    </style>
    """, unsafe_allow_html=True)

    c1, c_login, c2 = st.columns([1, 2, 1])
    with c_login:
        st.markdown("<div class='login-container'>", unsafe_allow_html=True)

        # logos
        icone_b64_login = get_base64_image("omni_icone.png")
        texto_b64_login = get_base64_image("omni_texto.png")
        if icone_b64_login and texto_b64_login:
            st.markdown(f"""
            <div class="logo-wrapper">
                <img src="data:image/png;base64,{icone_b64_login}" class="login-logo-spin">
                <img src="data:image/png;base64,{texto_b64_login}" class="login-logo-static">
            </div>""", unsafe_allow_html=True)

        st.markdown("""<div class="manifesto-login">"A Omnisfera foi desenvolvida com muito cuidado e carinho com o objetivo de auxiliar as escolas na tarefa de incluir."</div>""", unsafe_allow_html=True)

        # -----------------------
        # LOGIN DO APP
        # -----------------------
        st.subheader("🔐 Acesso Omnisfera")
        nome_user = st.text_input("Seu Nome", value=st.session_state.get("usuario_nome",""), placeholder="Seu Nome")
        cargo_user = st.text_input("Seu Cargo", value=st.session_state.get("usuario_cargo",""), placeholder="Seu Cargo")

        st.markdown("""
        <div class="termo-box">
            <strong>ACORDO DE CONFIDENCIALIDADE E USO DE DADOS (Versão Beta)</strong><br><br>
            1. Natureza do Software: sistema em fase beta.<br>
            2. LGPD: proibido inserir dados reais sensíveis de estudantes em ambiente não autorizado.<br>
            3. Propriedade Intelectual: vedada reprodução/comercialização sem autorização.<br>
            4. Responsabilidade: IA deve ser revisada por humano antes de aplicar.<br>
            Ao prosseguir, você declara estar ciente e de acordo.
        </div>
        """, unsafe_allow_html=True)
        concordo = st.checkbox("Li, compreendi e concordo com os termos.")

        senha = st.text_input("Senha de Acesso", type="password")

        colA, colB = st.columns(2)
        with colA:
            if st.button("ACESSAR OMNISFERA", use_container_width=True, type="primary"):
                hoje = date.today()
                senha_mestra = "PEI_START_2026" if hoje <= date(2026, 1, 19) else "OMNI_PRO"

                if not concordo:
                    st.warning("Aceite os termos.")
                    st.stop()
                if not nome_user.strip() or not cargo_user.strip():
                    st.warning("Preencha nome e cargo.")
                    st.stop()
                if senha != senha_mestra:
                    st.error("Senha incorreta.")
                    st.stop()

                st.session_state["autenticado"] = True
                st.session_state["usuario_nome"] = nome_user.strip()
                st.session_state["usuario_cargo"] = cargo_user.strip()
                st.success("Login Omnisfera OK ✅")
                st.rerun()

        with colB:
            if st.button("Sair / Reset", use_container_width=True):
                for k in ["autenticado","usuario_nome","usuario_cargo","supabase_jwt","supabase_user_id","selected_student_id","selected_student_name"]:
                    if k in st.session_state:
                        st.session_state[k] = "" if "jwt" in k or "user_id" in k else False
                st.rerun()

        st.divider()

        # -----------------------
        # LOGIN DO SUPABASE (só aparece depois do login Omnisfera)
        # -----------------------
        st.subheader("🔒 Login Supabase (obrigatório para salvar/carregar)")
        if not st.session_state["autenticado"]:
            st.info("Faça o login Omnisfera acima para liberar o login Supabase.")
            st.markdown("</div>", unsafe_allow_html=True)
            return False

        # pré-preenche com demo se quiser
        demo_email = st.secrets.get("DEMO_EMAIL", "")
        demo_pass = st.secrets.get("DEMO_PASSWORD", "")

        email_sb = st.text_input("Email (Supabase)", value=demo_email, placeholder="email@dominio.com")
        senha_sb = st.text_input("Senha (Supabase)", type="password", value=demo_pass)

        col1, col2 = st.columns(2)

        with col1:
            if st.button("🔐 Entrar (Supabase)", use_container_width=True):
                jwt, user_id, err = supabase_login(email_sb.strip(), senha_sb)
                if err:
                    st.error(f"Falha no login Supabase: {err}")
                else:
                    st.session_state["supabase_jwt"] = jwt
                    st.session_state["supabase_user_id"] = user_id
                    st.success("Supabase OK ✅")
                    st.rerun()

        with col2:
            if st.button("🚀 Entrar em modo demonstração", use_container_width=True):
                # modo demo: só funciona se DEMO_EMAIL/DEMO_PASSWORD estiverem nos secrets
                if not demo_email or not demo_pass:
                    st.warning("Defina DEMO_EMAIL e DEMO_PASSWORD em st.secrets para usar o modo demo.")
                else:
                    jwt, user_id, err = supabase_login(demo_email, demo_pass)
                    if err:
                        st.error(f"Falha no modo demo: {err}")
                    else:
                        st.session_state["supabase_jwt"] = jwt
                        st.session_state["supabase_user_id"] = user_id
                        st.success("Demo Supabase OK ✅")
                        st.rerun()

        if st.session_state["supabase_jwt"] and st.session_state["supabase_user_id"]:
            st.success("Supabase conectado. Você já pode usar PEI/Alunos ✅")

        st.markdown("</div>", unsafe_allow_html=True)
        return False

# trava até fazer os 2 logins
if not sistema_seguranca_e_supabase():
    st.stop()

# ==============================================================================
# 5. CONTEÚDO DA HOME (SÓ DEPOIS DOS LOGINS)
# ==============================================================================
nome_display = (st.session_state.get("usuario_nome", "Educador").split()[0]) if st.session_state.get("usuario_nome") else "Educador"

mensagem_banner = "Unindo ciência, dados e empatia para transformar a educação."
if 'OPENAI_API_KEY' in st.secrets:
    try:
        if 'banner_msg' not in st.session_state:
            client = OpenAI(api_key=st.secrets['OPENAI_API_KEY'])
            res = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": "Crie uma frase curta e inspiradora sobre inclusão escolar. Máximo 20 palavras."}]
            )
            st.session_state['banner_msg'] = res.choices[0].message.content
        mensagem_banner = st.session_state['banner_msg']
    except:
        pass

# Sidebar normal (após login)
with st.sidebar:
    st.markdown(f"**👤 {st.session_state['usuario_nome']}**")
    st.caption(f"{st.session_state['usuario_cargo']}")
    st.markdown("---")
    st.markdown("✅ Supabase conectado")
    st.caption(f"user_id: {st.session_state.get('supabase_user_id','')[:8]}...")

# HERO
st.markdown(f"""
<div class="dash-hero hover-spring" style="background: radial-gradient(circle at top right, #0F52BA, #062B61);
    border-radius: 16px; margin-bottom: 20px; margin-top: 10px;
    box-shadow: 0 10px 25px -5px rgba(15, 82, 186, 0.3);
    color: white; position: relative; overflow: hidden;
    padding: 25px 35px; display: flex; align-items: center; justify-content: flex-start;">
    <div>
        <div style="font-family:Inter; font-weight:700; font-size:1.5rem; margin:0;">Olá, {nome_display}!</div>
        <div style="font-family:Inter; font-size:0.9rem; opacity:0.9; font-weight:400;">"{mensagem_banner}"</div>
    </div>
    <i class="ri-heart-pulse-fill hero-bg-icon" style="position:absolute; right:20px; font-size:6rem; opacity:0.08; top:5px; transform: rotate(-10deg);"></i>
</div>
""", unsafe_allow_html=True)

# Acesso rápido (mantive seus botões principais)
st.markdown("### ⚡ Acesso Rápido")
c1, c2, c3 = st.columns(3)

with c1:
    if st.button("📘 PEI", use_container_width=True, type="primary"):
        st.switch_page("pages/1_PEI.py")
with c2:
    if st.button("🧩 PAEE", use_container_width=True):
        st.switch_page("pages/2_PAE.py")
with c3:
    if st.button("🚀 HUB", use_container_width=True):
        st.switch_page("pages/3_Hub_Inclusao.py")

st.markdown("<div style='text-align: center; color: #CBD5E0; font-size: 0.7rem; margin-top: 40px;'>Omnisfera desenvolvida e CRIADA por RODRIGO A. QUEIROZ</div>", unsafe_allow_html=True)
