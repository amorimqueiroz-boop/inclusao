import streamlit as st
from datetime import date
import time

# --- 1. CONFIGURAÇÃO INICIAL (Primeira linha obrigatória) ---
st.set_page_config(
    page_title="Omnisfera | Ecossistema Inclusivo", 
    page_icon="🌐", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==============================================================================
# 🔐 MÓDULO DE SEGURANÇA OMNISFERA (Blindagem)
# ==============================================================================
def sistema_seguranca():
    # CSS: Limpa o topo e ajusta visual do Login
    st.markdown("""
        <style>
            [data-testid="stHeader"] {visibility: hidden !important; height: 0px !important;}
            footer {visibility: hidden !important;}
            
            /* Card de Login */
            .login-container {
                background-color: white;
                padding: 40px;
                border-radius: 15px;
                box-shadow: 0 4px 15px rgba(0,0,0,0.1);
                text-align: center;
            }
            .termo-box {
                background-color: #f8f9fa; 
                padding: 15px; 
                border-radius: 8px; 
                height: 150px; 
                overflow-y: scroll; 
                font-size: 0.85rem;
                border: 1px solid #e9ecef;
                margin-bottom: 15px;
                text-align: left;
            }
        </style>
    """, unsafe_allow_html=True)

    if "autenticado" not in st.session_state:
        st.session_state["autenticado"] = False

    # TELA DE LOGIN (Se não autenticado)
    if not st.session_state["autenticado"]:
        # Centraliza o login forçando margens
        c_vazio_esq, c_login, c_vazio_dir = st.columns([1, 2, 1])
        
        with c_login:
            st.markdown("<div class='login-container'>", unsafe_allow_html=True)
            try:
                st.image("ominisfera.png", width=300) # Seu logo aqui
            except:
                st.markdown("# 🌐 OMNISFERA")
            
            st.markdown("### Acesso Restrito ao Ecossistema")
            st.markdown("---")
            
            # Termo
            st.markdown("##### 🛡️ Termo de Confidencialidade")
            termo_html = """
            <div class="termo-box">
                <strong>AMBIENTE PROTEGIDO</strong><br>
                Ao acessar, você concorda que:<br>
                1. <strong>Propriedade:</strong> A lógica e prompts são de Rodrigo A. Queiroz.<br>
                2. <strong>Sigilo:</strong> Metodologias confidenciais.<br>
                3. <strong>Proibições:</strong> Proibido cópia, engenharia reversa ou compartilhamento de acesso.<br>
                4. <strong>Legal:</strong> Sujeito às penas da Lei nº 9.610/98.
            </div>
            """
            st.markdown(termo_html, unsafe_allow_html=True)
            concordo = st.checkbox("Li e aceito os termos de uso.")
            
            st.write("")
            senha = st.text_input("Chave de Acesso:", type="password")
            
            if st.button("🚀 ENTRAR NO SISTEMA", type="primary", use_container_width=True):
                hoje = date.today()
                senha_correta = "PEI_START_2026" if hoje <= date(2026, 1, 19) else "OMNI_PRO"
                
                if not concordo:
                    st.warning("⚠️ Aceite os termos para continuar.")
                elif senha == senha_correta:
                    st.session_state["autenticado"] = True
                    st.rerun()
                else:
                    st.error("🚫 Chave inválida.")
            
            st.markdown("</div>", unsafe_allow_html=True)
        
        return False

    # Se autenticado, libera o app
    return True

# --- EXECUTA A SEGURANÇA ---
if not sistema_seguranca():
    st.stop()

# ==============================================================================
# 🏠 HOME - DASHBOARD OMNISFERA (Aparece após login)
# ==============================================================================

# CSS Específico da Home (Cards Bonitos)
st.markdown("""
<style>
    .card {
        background-color: white;
        border-radius: 15px;
        padding: 25px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        border: 1px solid #E2E8F0;
        transition: transform 0.2s, box-shadow 0.2s;
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    .card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 15px rgba(0,0,0,0.1);
        border-color: #3182CE;
    }
    .card-title {
        font-size: 1.5rem;
        font-weight: 800;
        color: #2D3748;
        margin-bottom: 10px;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .card-desc {
        font-size: 0.95rem;
        color: #718096;
        margin-bottom: 20px;
        line-height: 1.5;
    }
    .card-number {
        font-size: 3rem;
        font-weight: 900;
        color: #E2E8F0;
        position: absolute;
        top: 20px;
        right: 30px;
        opacity: 0.3;
    }
    /* Cores dos Cards */
    .border-blue { border-top: 5px solid #3182CE; }
    .border-purple { border-top: 5px solid #805AD5; }
    .border-teal { border-top: 5px solid #38B2AC; }
</style>
""", unsafe_allow_html=True)

# Cabeçalho da Home
c_head1, c_head2 = st.columns([1, 5])
with c_head1:
    try:
        st.image("ominisfera.png", width=120)
    except:
        st.write("🌐")
with c_head2:
    st.markdown("# OMNISFERA")
    st.markdown("### O Ecossistema de Gestão da Inclusão")

st.markdown("---")

# DASHBOARD - TRÊS PILARES
col1, col2, col3 = st.columns(3)

# --- PILAR 1: PEI (A Base) ---
with col1:
    st.markdown("""
    <div class="card border-blue">
        <div class="card-number">1</div>
        <div class="card-title">📘 PEI 360º</div>
        <div class="card-desc">
            <strong>Plano de Ensino Individualizado</strong><br><br>
            A porta de entrada. Realize a anamnese, avalie o perfil do aluno e gere o documento oficial que guia todo o processo inclusivo na sala de aula regular.
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.info("💡 *Dica: Comece cadastrando o aluno aqui.*")
    # Futuro: st.page_link("pages/1_PEI.py", label="Acessar PEI", icon="📘")

# --- PILAR 2: PAE (O Especialista) ---
with col2:
    st.markdown("""
    <div class="card border-purple">
        <div class="card-number">2</div>
        <div class="card-title">🧩 PAE</div>
        <div class="card-desc">
            <strong>Plano de AEE</strong><br><br>
            Focado na Sala de Recursos. Identifique barreiras específicas, selecione tecnologias assistivas e trabalhe a autonomia e funções executivas.
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.warning("🚧 *Em desenvolvimento...*")
    # Futuro: st.page_link("pages/2_PAE.py", label="Acessar PAE", icon="🧩")

# --- PILAR 3: HUB DE INCLUSÃO (A Ação) ---
with col3:
    st.markdown("""
    <div class="card border-teal">
        <div class="card-number">3</div>
        <div class="card-title">🚀 Hub de Inclusão</div>
        <div class="card-desc">
            <strong>Adaptação & Criação</strong><br><br>
            A ferramenta prática para o dia a dia. Adapte provas (Word/Print), crie atividades do zero, gere recursos visuais e roteiros de aula.
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Botão que leva para o arquivo que já temos pronto
    if st.button("Acessar Hub de Inclusão ➡️", type="primary", use_container_width=True):
        st.switch_page("pages/1_Adaptador_Atividades.py")

st.markdown("---")
st.markdown("<div style='text-align: center; color: #A0AEC0; font-size: 0.8rem;'>Omnisfera © 2026 - Todos os direitos reservados.</div>", unsafe_allow_html=True)
