import streamlit as st
import time
from supabase_client import validar_acesso_pin

def render_login():
    # Layout limpo e centralizado
    st.markdown("""
    <style>
        .login-container {
            max-width: 400px;
            margin: 0 auto;
            padding: 40px;
            background-color: white;
            border-radius: 16px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.05);
            border: 1px solid #E2E8F0;
            text-align: center;
        }
        .app-title {
            font-family: 'Nunito', sans-serif;
            font-weight: 800;
            font-size: 1.8rem;
            color: #1F2937;
            margin-bottom: 5px;
        }
        .app-subtitle {
            color: #6B7280;
            font-size: 0.9rem;
            margin-bottom: 30px;
        }
        /* Ajuste inputs */
        div[data-testid="stTextInput"] label { font-size: 0.85rem; color: #4B5563; }
        div[data-testid="stForm"] button { width: 100%; border-radius: 8px; font-weight: bold; margin-top: 10px; }
    </style>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
        <div class="login-container">
            <div class="app-title">Omnisfera</div>
            <div class="app-subtitle">Ambiente Educacional Seguro</div>
        </div>
        """, unsafe_allow_html=True)

        with st.form("login_form"):
            st.markdown("##### Identificação")
            nome = st.text_input("Seu Nome", placeholder="Ex: Rodrigo Queiroz")
            funcao = st.text_input("Sua Função", placeholder="Ex: Professor, Coordenação")
            
            st.markdown("##### Acesso")
            pin = st.text_input("PIN do Workspace", type="password", placeholder="****")
            
            submitted = st.form_submit_button("ACESSAR SISTEMA", type="primary")

            if submitted:
                if not nome or not funcao or not pin:
                    st.warning("⚠️ Todos os campos são obrigatórios para o registro de acesso.")
                else:
                    with st.spinner("Validando credenciais..."):
                        # Chama a função atualizada do client
                        sucesso, dados_ws, erro = validar_acesso_pin(pin.strip(), nome.strip(), funcao.strip())
                        
                        if sucesso:
                            # Configura a sessão
                            st.session_state.autenticado = True
                            st.session_state.user = {"nome": nome, "cargo": funcao}
                            st.session_state.workspace_id = dados_ws["owner_id"]
                            st.session_state.workspace_name = dados_ws["workspace_name"]
                            
                            st.success(f"Bem-vindo(a), {nome}!")
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error(f"Acesso negado: {erro}")
