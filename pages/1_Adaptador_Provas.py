import streamlit as st
from openai import OpenAI
import os

# --- CONFIGURAÇÃO ---
st.set_page_config(page_title="Adaptador de Avaliações", page_icon="📝", layout="wide")

# --- ESTILO VISUAL BLINDADO ---
css_adaptador = """
    <link href="https://cdn.jsdelivr.net/npm/remixicon@4.1.0/fonts/remixicon.css" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800&display=swap" rel="stylesheet">
    <style>
    html, body, [class*="css"] { font-family: 'Nunito', sans-serif; color: #2D3748; }
    :root { --brand-primary: #004E92; --brand-coral: #FF6B6B; }
    
    .stTextInput input, .stTextArea textarea, .stSelectbox div[data-baseweb="select"] {
        border-radius: 12px !important; border: 1px solid #CBD5E0 !important;
    }
    .stButton > button {
        background-color: var(--brand-primary) !important; color: white !important;
        border-radius: 12px !important; height: 3.5em !important; font-weight: 700 !important;
        width: 100%;
    }
    .stButton > button:hover { transform: scale(1.02); }
    
    .result-card {
        background: #FFFFFF; padding: 25px; border-radius: 16px;
        border: 1px solid #E2E8F0; border-left: 6px solid var(--brand-coral);
        box-shadow: 0 4px 10px rgba(0,0,0,0.05);
    }
    .instruction-box {
        background: #E3F2FD; padding: 15px; border-radius: 10px; color: #004E92; font-size: 0.9rem; margin-bottom: 20px;
    }
    </style>
"""
st.markdown(css_adaptador, unsafe_allow_html=True)

# --- CABEÇALHO ---
st.markdown("""
<div style="display:flex; align-items:center; gap:15px; margin-bottom:20px; padding-bottom:20px; border-bottom:1px solid #E2E8F0;">
    <div style="background:#E3F2FD; width:50px; height:50px; border-radius:12px; display:flex; align-items:center; justify-content:center;">
        <i class="ri-pencil-ruler-2-line" style="font-size:24px; color:#004E92;"></i>
    </div>
    <div>
        <h1 style="margin:0; color:#004E92; font-size:1.8rem;">Adaptador de Avaliações</h1>
        <p style="margin:0; color:#718096;">Transforme questões complexas em formatos acessíveis.</p>
    </div>
</div>
""", unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Configuração IA")
    if 'DEEPSEEK_API_KEY' in st.secrets:
        api_key = st.secrets['DEEPSEEK_API_KEY']
        st.success("✅ Chave Segura Ativa")
    else:
        api_key = st.text_input("Chave API DeepSeek:", type="password")
    
    st.markdown("---")
    st.markdown("""
    **Como funciona?**
    1. Defina o perfil do aluno (ex: TDAH).
    2. Cole a questão original difícil.
    3. Escolha o formato adaptado desejado.
    4. A IA reescreve mantendo o conteúdo, mas mudando a forma.
    """)

# --- INTERFACE ---
c1, c2 = st.columns([1, 1])

with c1:
    st.markdown("### 1. Dados de Entrada")
    
    perfil = st.text_area("Perfil do Aluno (Resumo):", 
        placeholder="Ex: João tem TDAH, leitura lenta e se beneficia de textos curtos com palavras-chave em negrito.",
        height=100)
    
    tipo_adaptacao = st.selectbox("Formato de Saída Desejado:", [
        "Múltipla Escolha (Simplificada - 3 opções)",
        "Ligue as Colunas (Associação)",
        "Verdadeiro ou Falso",
        "Texto Lacunado (Preencher espaços)",
        "Passo a Passo (Fragmentação)",
        "Apoio Visual (Descrição de Imagem Sugerida)"
    ])
    
    questao_original = st.text_area("Questão Original (Cole aqui):", 
        placeholder="Ex: Explique as consequências da Revolução Industrial...",
        height=150)
    
    if st.button("✨ Adaptar Questão Agora"):
        if not api_key:
            st.error("Insira a Chave API na barra lateral.")
        elif not perfil or not questao_original:
            st.warning("Preencha o perfil e a questão.")
        else:
            with st.spinner("A IA está reestruturando a questão pedagogicamente..."):
                try:
                    client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")
                    
                    prompt_sistema = """
                    Você é um Especialista em Adaptação Curricular e Desenho Universal para Aprendizagem (DUA).
                    Sua missão é reescrever questões de prova para torná-las acessíveis para alunos neurodivergentes.
                    NUNCA dê a resposta da questão. Apenas reformule o enunciado e as opções.
                    """
                    
                    prompt_user = f"""
                    PERFIL DO ALUNO: {perfil}
                    FORMATO DESEJADO: {tipo_adaptacao}
                    
                    QUESTÃO ORIGINAL PARA ADAPTAR:
                    "{questao_original}"
                    
                    AÇÃO:
                    1. Reescreva o enunciado de forma direta e simples.
                    2. Use **negrito** nas palavras-chave.
                    3. Crie a estrutura da questão no formato solicitado ({tipo_adaptacao}).
                    4. Adicione uma breve "Nota ao Professor" explicando o que foi adaptado e porquê.
                    """
                    
                    response = client.chat.completions.create(
                        model="deepseek-chat",
                        messages=[{"role": "system", "content": prompt_sistema}, {"role": "user", "content": prompt_user}],
                        temperature=0.3
                    )
                    st.session_state['resultado_adaptacao'] = response.choices[0].message.content
                except Exception as e:
                    st.error(f"Erro: {e}")

with c2:
    st.markdown("### 2. Questão Adaptada")
    
    if 'resultado_adaptacao' in st.session_state:
        st.markdown(f"""
        <div class="result-card">
            {st.session_state['resultado_adaptacao']}
        </div>
        """, unsafe_allow_html=True)
        
        st.download_button("📥 Baixar Adaptação (.txt)", st.session_state['resultado_adaptacao'], "questao_adaptada.txt")
    else:
        st.info("O resultado aparecerá aqui após o processamento.")
        st.markdown("""
        <div class="instruction-box">
            <b>Dica de Ouro:</b><br>
            Para alunos com Autismo, evite metáforas ou perguntas com "duplo sentido". 
            Para TDAH, fragmente questões longas em etapas A, B e C.
        </div>
        """, unsafe_allow_html=True)
