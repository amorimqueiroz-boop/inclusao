# ARQUIVO: omni_utils.py
import streamlit as st
import os
import base64

# ==============================================================================
# 1. FUNÇÕES DE ARQUIVO E IMAGEM
# ==============================================================================
def get_base64_image(image_path):
    if not os.path.exists(image_path): return ""
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

def finding_logo():
    """Tenta encontrar a logo em caminhos comuns"""
    caminhos = ["omni_icone.png", "logo.png", "icone.png", "static/omni_icone.png"]
    for c in caminhos:
        if os.path.exists(c):
            return c
    return None

# ==============================================================================
# 2. O HEADER PADRONIZADO (A SOLUÇÃO QUE VOCÊ PEDIU)
# ==============================================================================
def renderizar_header_padrao(titulo, subtitulo, cor_destaque="#0F52BA"):
    """
    Renderiza o cabeçalho padrão (Logo 110px + Textos) em qualquer página.
    """
    
    # 1. Prepara a Logo
    logo_path = finding_logo()
    
    if logo_path:
        b64_logo = get_base64_image(logo_path)
        mime = "image/png"
        img_html = f'<img src="data:{mime};base64,{b64_logo}" style="height: 110px; filter: drop-shadow(0 4px 6px rgba(0,0,0,0.1));">'
    else:
        # Fallback se não tiver logo: usa um emoji ou ícone
        img_html = '<div style="font-size: 80px;">🌐</div>'

    # 2. CSS Local (Só para o header)
    st.markdown("""
    <style>
        .header-container {
            display: flex;
            align-items: center;
            gap: 25px; /* Separação entre logo e texto */
            background-color: white;
            padding: 30px;
            border-radius: 20px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.05);
            border: 1px solid #E2E8F0;
            margin-bottom: 30px;
        }
        .header-texts {
            display: flex;
            flex-direction: column;
        }
        .header-title {
            font-family: 'Nunito', sans-serif;
            font-weight: 800;
            font-size: 2.2rem;
            color: #2D3748;
            margin: 0;
            line-height: 1.1;
        }
        .header-subtitle {
            font-family: 'Inter', sans-serif;
            font-size: 1.1rem;
            color: #718096;
            margin-top: 5px;
            font-weight: 400;
        }
        
        /* Responsividade para celular */
        @media (max-width: 600px) {
            .header-container { flex-direction: column; text-align: center; }
        }
    </style>
    """, unsafe_allow_html=True)

    # 3. Renderiza o HTML
    st.markdown(f"""
    <div class="header-container" style="border-left: 8px solid {cor_destaque};">
        <div class="header-logo">
            {img_html}
        </div>
        <div class="header-texts">
            <div class="header-title">{titulo}</div>
            <div class="header-subtitle">{subtitulo}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ==============================================================================
# 3. CONTROLE DE ACESSO (SIMPLIFICADO)
# ==============================================================================
def verificar_acesso():
    # Se já logou, libera
    if st.session_state.get("autenticado", False):
        return True
    
    # Se não, mostra aviso básico (ou redireciona para Home)
    st.warning("🔒 Acesso restrito. Por favor, faça login na Home.")
    if st.button("Ir para Login"):
        st.switch_page("Home.py")
    return False
