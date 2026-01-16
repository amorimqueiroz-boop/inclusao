import streamlit as st
import asyncio
from httpx_oauth.clients.google import GoogleOAuth2

def check_login():
    """Verifica se o usuário está logado via Google"""
    
    # 1. Tenta pegar as chaves do Cofre (Secrets)
    try:
        client_id = st.secrets["google_auth"]["client_id"]
        client_secret = st.secrets["google_auth"]["client_secret"]
        redirect_url = st.secrets["google_auth"]["redirect_url"]
    except:
        st.error("⚠️ Erro: As chaves do Google não foram encontradas no Secrets.")
        st.stop()

    client = GoogleOAuth2(client_id, client_secret)

    # 2. Se já tem email na memória, libera o acesso
    if "email_usuario" in st.session_state:
        return st.session_state["email_usuario"]

    # 3. Se o Google está devolvendo o usuário (Redirecionamento)
    code = st.query_params.get("code")
    
    if code:
        try:
            # Troca o código pelo Token e pelo Email
            token = asyncio.run(client.get_access_token(code, redirect_url))
            user_id, email = asyncio.run(client.get_id_email(token["access_token"]))
            
            # Salva e recarrega a página limpa
            st.session_state["email_usuario"] = email
            st.query_params.clear()
            st.rerun()
        except Exception as e:
            st.error(f"Erro no login: {e}")
            st.stop()

    # 4. Se não está logado: Mostra o Botão de Entrar
    else:
        # Gera o link oficial de login
        authorization_url = asyncio.run(client.get_authorization_url(
            redirect_url,
            scope=["email", "profile"],
            extras_params={"access_type": "offline"},
        ))
        
        st.title("🔒 Acesso Restrito")
        st.markdown(f'''
            <div style="text-align: center; margin-top: 50px;">
                <h3>Bem-vindo à Ominisfera</h3>
                <p>Faça login com sua conta Google para continuar.</p>
                <br>
                <a href="{authorization_url}" target="_self">
                    <button style="
                        background-color: #4285F4; color: white; padding: 12px 24px; 
                        border: none; border-radius: 4px; font-size: 16px; cursor: pointer;
                        font-family: sans-serif; font-weight: bold;">
                        G Entrar com Google
                    </button>
                </a>
            </div>
        ''', unsafe_allow_html=True)
        st.stop() # Trava o código aqui até logar

