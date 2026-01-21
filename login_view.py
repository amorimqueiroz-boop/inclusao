import streamlit as st
from _client import supabase_login

def render_login():
    """Renderiza a tela de login."""
    
    # CSS específico do Login para centralizar
    st.markdown("""
    <style>
        .login-container {
            max-width: 400px;
            margin: 50px auto;
            padding: 30px;
            background: white;
            border-radius: 12px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.08);
            border: 1px solid #E2E8F0;
            text-align: center;
        }
        .login-title {
            font-family: 'Nunito', sans-serif;
            font-size: 26px;
            font-weight: 800;
            color: #1F2937;
            margin-bottom: 8px;
        }
        .login-sub {
            color: #6B7280;
            font-size: 14px;
            margin-bottom: 24px;
        }
        /* Botão full width */
        div[data-testid="stForm"] button {
            width: 100%;
            border-radius: 8px;
            font-weight: bold;
        }
    </style>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
        <div class="login-container">
            <div class="login-title">Omnisfera</div>
            <div class="login-sub">Acesso Seguro</div>
        </div>
        """, unsafe_allow_html=True)

        with st.form("login_form"):
            email = st.text_input("E-mail", placeholder="seu@email.com")
            senha = st.text_input("Senha", type="password", placeholder="••••••••")
            
            submitted = st.form_submit_button("Entrar", type="primary")

            if submitted:
                if not email or not senha:
                    st.warning("Preencha todos os campos.")
                else:
                    with st.spinner("Autenticando..."):
                        jwt, uid, err = supabase_login(email.strip(), senha.strip())
                        
                        if jwt and uid:
                            st.session_state.autenticado = True
                            st.session_state.user = {"email": email.strip()}
                            st.session_state["supabase_jwt"] = jwt
                            st.session_state["supabase_user_id"] = uid
                            st.rerun()
                        else:
                            st.error(f"Erro: {err}")
