# login_view.py
import streamlit as st
from datetime import datetime

from omni_utils import (
    get_base64_image,
    supabase_workspace_from_pin,
    supabase_log_access,
    ensure_state,
    inject_base_css,
)

APP_VERSION = "v1.0"


def render_login():
    ensure_state()
    inject_base_css()

    # Se já estiver autenticado, manda pra home
    if st.session_state.get("autenticado") and st.session_state.get("workspace_id"):
        st.session_state.view = "home"
        st.rerun()

    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        st.markdown("<div class='login-box'>", unsafe_allow_html=True)

        # Logo
        img_login = get_base64_image("omni_icone.png")
        if img_login:
            st.markdown(
                f"<img src='data:image/png;base64,{img_login}' class='login-logo'>",
                unsafe_allow_html=True,
            )
        else:
            st.markdown("<h2 style='color:#0F52BA;'>OMNISFERA</h2>", unsafe_allow_html=True)

        st.markdown(
            "<div class='login-manifesto'>"
            "\"A Omnisfera foi desenvolvida com muito cuidado e carinho com o objetivo de auxiliar as escolas na tarefa de incluir.\""
            "</div>",
            unsafe_allow_html=True,
        )

        with st.expander("📄 Ler Termos de Uso e Confidencialidade"):
            st.markdown(
                """
<div class="termo-box">
<strong>1. Confidencialidade:</strong> Não inserir dados reais sensíveis (documentos, laudos identificáveis).<br>
<strong>2. Natureza Beta:</strong> O sistema está em evolução constante.<br>
<strong>3. Responsabilidade:</strong> Sugestões de IA são apoio pedagógico e devem ser validadas por profissional humano.<br>
<strong>4. Registro de uso:</strong> Acesso e eventos essenciais (ex.: login, navegação de módulos) podem ser registrados para auditoria interna.
</div>
                """,
                unsafe_allow_html=True,
            )

        concordo = st.checkbox("Li e concordo com os termos.")

        st.markdown("### 🔐 Acesso por PIN")
        pin = st.text_input("PIN (fornecido por Rodrigo)", placeholder="Ex.: 482913", max_chars=32)

        st.markdown("### 👤 Identificação")
        nome = st.text_input("Seu nome", placeholder="Ex.: Ana Paula")
        cargo = st.text_input("Seu cargo", placeholder="Ex.: Coordenação Pedagógica")

        col_a, col_b = st.columns([3, 1])
        with col_b:
            entrar = st.button("ENTRAR")

        if entrar:
            if not concordo:
                st.warning("⚠️ Aceite os termos para continuar.")
                st.stop()

            if not pin or not nome or not cargo:
                st.warning("⚠️ Preencha PIN, nome e cargo.")
                st.stop()

            # 1) Resolve workspace_id via RPC do Supabase (workspace_from_pin)
            ws = supabase_workspace_from_pin(pin)

            if not ws:
                st.error("PIN inválido ou workspace não encontrado.")
                st.stop()

            # 2) Salva sessão
            st.session_state.autenticado = True
            st.session_state.workspace_id = ws
            st.session_state.user = {"nome": nome.strip(), "cargo": cargo.strip()}
            st.session_state.view = "home"

            # 3) Log interno de acesso (para você)
            try:
                supabase_log_access(
                    workspace_id=ws,
                    nome=st.session_state.user["nome"],
                    cargo=st.session_state.user["cargo"],
                    event="login_ok",
                    app_version=APP_VERSION,
                )
            except Exception:
                # Não derruba o login se o log falhar (mas você vê no console)
                pass

            st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

    # trava aqui se não autenticou
    st.stop()
