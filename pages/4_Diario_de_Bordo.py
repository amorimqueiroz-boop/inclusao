import streamlit as st
from services import enviar_checkin
from datetime import datetime

st.set_page_config(page_title="Diário de Bordo", page_icon="📝", layout="wide")

st.title("📝 Diário de Bordo & Check-in")

# --- IDENTIFICAÇÃO (Simples) ---
with st.sidebar:
    st.header("Quem é você?")
    # Tenta lembrar o nome se já digitou antes
    if "usuario_nome" not in st.session_state:
        st.session_state["usuario_nome"] = ""
    
    nome_input = st.text_input("Seu Nome:", value=st.session_state["usuario_nome"])
    
    if nome_input:
        st.session_state["usuario_nome"] = nome_input
        st.success(f"Logado como: {nome_input}")
    else:
        st.warning("Digite seu nome para liberar o salvamento.")

# --- ÁREA PRINCIPAL ---
col_esq, col_dir = st.columns([1, 1])

with col_esq:
    st.subheader("📍 Registro Rápido")
    
    # Exemplo de atividades (depois puxamos do banco)
    atividade = st.selectbox("Qual atividade foi aplicada?", 
        ["História: Feudalismo (Adaptada)", 
         "Matemática: Frações (Visual)", 
         "Português: Interpretação (Áudio)"])
    
    status = st.radio("Resultado:", ["🟢 Sucesso", "🟡 Com Ajuda", "🔴 Dificuldade"])
    obs = st.text_area("Observação:")
    
    if st.button("Salvar Check-in", type="primary"):
        if not st.session_state["usuario_nome"]:
            st.error("Precisa se identificar na barra lateral!")
        else:
            # Prepara os dados
            dados = {
                "id": str(datetime.now().timestamp()),
                "data_hora": datetime.now().strftime("%d/%m/%Y %H:%M"),
                "autor_nome": st.session_state["usuario_nome"],
                "atividade_resumo": atividade,
                "resultado": status,
                "observacao": obs
            }
            # Envia
            if enviar_checkin(dados):
                st.success("✅ Salvo no Google Sheets!")
                st.balloons()

with col_dir:
    st.info("Aqui ficará o histórico de correções de rota.")
