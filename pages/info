import streamlit as st
import pandas as pd

# Configuração visual (Mantendo o padrão vermelho do Omnisfera)
st.markdown("""
<style>
    .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
        font-size: 1.1rem;
    }
    .stTabs [data-baseweb="tab-highlight"] {
        background-color: #FF4B4B;
    }
    h3 { color: #FF4B4B; }
</style>
""", unsafe_allow_html=True)

st.title("📚 Guia de Práticas e Fundamentos")
st.markdown("Base de conhecimento para suporte à gestão e prática da educação inclusiva.")

# Criação das Abas para organizar o conteúdo do PDF
tab1, tab2, tab3, tab4 = st.tabs([
    "🏛️ Fundamentos & Legal", 
    "🏫 Gestão Escolar", 
    "👩‍🏫 Prática Pedagógica",
    "🤝 Equipe & Papéis"
])

# --- ABA 1: FUNDAMENTOS E MARCOS LEGAIS ---
with tab1:
    st.header("Filosofia e Legislação")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### O Conceito de 'Outrar-se'")
        st.info("""
        *"Outrar-se é sentir o mundo do outro como se fosse o seu próprio mundo... 
        numa relação empática sem se envolver, no entanto, com os sentimentos da pessoa."*
        
        **Bernardo Soares (Fernando Pessoa)**
        """)
        st.markdown("**Aplicação:** A inclusão corre o risco de ser retórica vazia se não houver a 'outragem'. O educador deve ter proximidade para interpretar necessidades, mas distanciamento para atuar profissionalmente.")

    with col2:
        st.markdown("### 🚫 Inimigo Invisível: Capacitismo")
        st.warning("""
        **Definição:** Qualquer distinção, restrição ou exclusão que prejudique direitos da PcD, baseada na premissa de que a deficiência é uma 'falta'.
        """)
        st.markdown("""
        **Duas Frentes de Combate:**
        1.  **Físico:** Barreiras estruturais (rampas, banheiros).
        2.  **Simbólico:** Viés inconsciente e metáforas (ex: 'fingir de cego').
        """)

    st.divider()
    
    st.subheader("📜 Evolução dos Marcos Legais")
    timeline = [
        {"Ano": "1988", "Marco": "Constituição Federal", "Resumo": "Educação como direito de todos."},
        {"Ano": "1994", "Marco": "Declaração de Salamanca", "Resumo": "Compromisso global com o sistema inclusivo."},
        {"Ano": "1996", "Marco": "LDB (Lei 9.394)", "Resumo": "Obrigatoriedade da oferta de educação especial."},
        {"Ano": "2008", "Marco": "PNEEPEI", "Resumo": "Política Nacional focada na escola comum."},
        {"Ano": "2015", "Marco": "LBI (Lei 13.146)", "Resumo": "Lei Brasileira de Inclusão e definição de capacitismo."}
    ]
    st.table(pd.DataFrame(timeline))

# --- ABA 2: GESTÃO ESCOLAR ---
with tab2:
    st.header("Gestão e Estratégia")
    
    with st.expander("📌 PGEI – Plano Geral de Educação Inclusiva", expanded=True):
        st.write("Ferramenta estratégica que organiza as ações institucionais e rotina escolar.")
        st.markdown("""
        **Checklist de Elaboração:**
        1.  **Censo Escolar:** Total de alunos vs. PCD matriculados.
        2.  **Perfis:** Mapeamento de necessidades (TEA, Altas Habilidades, Física).
        3.  **Recursos:** Intérpretes, material adaptado, acessibilidade.
        4.  **Dimensionamento:** Cálculo da carga horária da equipe vs. demanda.
        """)
    
    with st.expander("🛠️ A Escola Necessária (Papel da Gestão)"):
        c1, c2, c3 = st.columns(3)
        c1.metric("Prioridade", "Adaptação Curricular", "Necessidades Reais")
        c2.metric("Investimento", "Espaço e Equipamentos", "Acessibilidade")
        c3.metric("Legalidade", "Respeito às Leis", "Sem recusas")
        st.markdown("**O Mandato do Diretor:** Liderança pelo exemplo (cultura anticapacitista) e comunicação transparente (PPP).")

# --- ABA 3: PRÁTICA PEDAGÓGICA ---
with tab3:
    st.header("Estratégias de Sala de Aula")
    
    st.markdown("### 🧠 Estratégias para Transtornos de Aprendizagem (TDAH, Dislexia)")
    
    cols = st.columns(4)
    cols[0].success("**1. Tempo:** Flexibilidade em tarefas e provas.")
    cols[1].success("**2. Avaliação:** Métodos diversificados (oral, projetos).")
    cols[2].success("**3. Consignas:** Instruções claras e diretas.")
    cols[3].success("**4. Feedback:** Contínuo e construtivo (erro = aprendizado).")
    
    cols2 = st.columns(3)
    cols2[0].info("**5. Ambiente:** Posição estratégica e iluminação.")
    cols2[1].info("**6. Materiais:** Pautas espaçadas, fontes adaptadas.")
    cols2[2].info("**7. Supervisão:** Tutoria e monitoramento.")

    st.divider()
    
    st.markdown("### 🔄 O Fluxo do PEI e Justiça Curricular")
    st.markdown("""
    > **Objetivo:** Personalização de metas sem reduzir a expectativa de aprendizado.
    
    * **Coleta:** Orientador recebe laudos e histórico.
    * **Filtro:** Equipe filtra dados confidenciais (Sigilo é vital).
    * **Ação:** Pedagógico traduz dados clínicos em adaptações práticas.
    """)

# --- ABA 4: EQUIPE E PAPÉIS (AT vs AP) ---
with tab4:
    st.header("Quem faz o quê?")
    
    st.markdown("### ⚔️ A Diferença Crucial: AT vs. AP")
    st.markdown("Muitas escolas confundem esses papéis. Use a tabela abaixo para orientação:")
    
    data_papeis = {
        "Característica": ["Foco", "Vínculo", "Função Principal", "Exemplo de atuação"],
        "AT (Atendente Terapêutico)": [
            "Clínico / Saúde", 
            "Família ou Estado (Externo)", 
            "Atendimento individual exclusivo",
            "Suporte em casos de autismo severo, manejo de crises."
        ],
        "AP (Atendente Pedagógico)": [
            "Escolar / Suporte", 
            "Escola", 
            "Apoio ao acesso ao currículo e rotina",
            "Auxílio em locomoção, higiene, organização e interação social."
        ]
    }
    df_papeis = pd.DataFrame(data_papeis)
    st.dataframe(df_papeis, use_container_width=True, hide_index=True)

    st.markdown("---")
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("**Coordenador Pedagógico**")
        st.caption("Responsável pela adaptação curricular (PEI) e suporte docente.")
    with col_b:
        st.markdown("**Psicólogo Escolar**")
        st.caption("Estudos de caso, supervisão e mediação. **Não faz clínica na escola.**")

# Rodapé com a fonte
st.markdown("---")
st.caption("Fonte: Material 'Inclusão Escolar: Gestão e Prática' - Baseado na obra de Leila Rentroia Iannone e Jurjo Torres Santomé.")
