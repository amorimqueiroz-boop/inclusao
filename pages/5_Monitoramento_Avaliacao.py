import streamlit as st
import graphviz

# ==============================================================================
# 1. SETUP & DESIGN SYSTEM (VISUAL PREMIUM)
# ==============================================================================
st.set_page_config(page_title="Central de Conhecimento", page_icon="🧠", layout="wide")

st.markdown("""
<style>
    /* Fontes e Base */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
    
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; color: #1e293b; }
    .stApp { background-color: #f8fafc; }

    /* Hero Section */
    .hero-container {
        background: linear-gradient(135deg, #0F52BA 0%, #3b82f6 100%);
        padding: 3rem 2rem;
        border-radius: 0 0 20px 20px;
        color: white;
        margin-top: -60px;
        margin-bottom: 30px;
        box-shadow: 0 10px 25px -5px rgba(15, 82, 186, 0.25);
    }
    .hero-title { font-size: 2.2rem; font-weight: 800; margin-bottom: 10px; }
    .hero-subtitle { font-size: 1.1rem; opacity: 0.9; font-weight: 300; }

    /* Cards de Conteúdo */
    .content-card {
        background: white; border: 1px solid #e2e8f0; border-radius: 16px;
        padding: 24px; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        transition: transform 0.2s; height: 100%; margin-bottom: 20px;
    }
    .content-card:hover { transform: translateY(-3px); border-color: #0F52BA; }
    
    /* Estilo do Glossário */
    .glossary-term {
        color: #0F52BA; font-weight: 700; font-size: 1.1rem; margin-bottom: 5px;
    }
    .glossary-def { color: #475569; line-height: 1.6; font-size: 0.95rem; }
    .glossary-box {
        background: white; padding: 20px; border-radius: 10px;
        border-left: 4px solid #0F52BA; margin-bottom: 15px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }

    /* Estilo da Biblioteca */
    .biblio-link {
        text-decoration: none; color: white; background-color: #0F52BA;
        padding: 8px 16px; border-radius: 6px; font-size: 0.85rem; display: inline-block;
        margin-top: 10px; transition: background 0.3s;
    }
    .biblio-link:hover { background-color: #0b3d91; color: white; }
    
    /* Abas Customizadas */
    .stTabs [data-baseweb="tab-list"] { gap: 10px; padding: 10px 0; }
    .stTabs [data-baseweb="tab"] {
        background-color: white; border-radius: 8px; border: 1px solid #e2e8f0;
        padding: 8px 20px; font-weight: 600; color: #64748b;
    }
    .stTabs [aria-selected="true"] {
        background-color: #0F52BA !important; color: white !important; border-color: #0F52BA !important;
    }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# 2. HERO HEADER
# ==============================================================================
st.markdown("""
<div class="hero-container">
    <div class="hero-title">🧠 Central de Inteligência Inclusiva</div>
    <div class="hero-subtitle">Fundamentos, Legislação, Glossário Técnico e Biblioteca Virtual.</div>
</div>
""", unsafe_allow_html=True)

# ==============================================================================
# 3. NAVEGAÇÃO
# ==============================================================================
tab_panorama, tab_glossario, tab_biblio, tab_manual = st.tabs([
    "📊 Panorama & Fluxos", 
    "📖 Glossário de Termos", 
    "📚 Biblioteca Virtual",
    "⚙️ Manual do Sistema"
])

# ==============================================================================
# ABA 1: PANORAMA & FLUXOS
# ==============================================================================
with tab_panorama:
    st.markdown("### 🔄 O Fluxo da Inclusão (Omnisfera 2025)")
    st.caption("Processo atualizado com a substituição do laudo médico pelo Estudo de Caso (Decretos 2025).")
    
    # Diagrama Graphviz
    try:
        fluxo = graphviz.Digraph()
        fluxo.attr(rankdir='LR', bgcolor='transparent', margin='0')
        fluxo.attr('node', shape='box', style='rounded,filled', fontname='Inter', fontsize='11', height='0.6')
        
        fluxo.node('A', '1. ACOLHIMENTO\n(Matrícula Garantida)', fillcolor='#dbeafe', color='#3b82f6')
        fluxo.node('B', '2. ESTUDO DE CASO\n(Avaliação Pedagógica)', fillcolor='#0F52BA', fontcolor='white', color='#0F52BA')
        fluxo.node('C', '3. PEI + PAEE\n(Planejamento)', fillcolor='#f3e8ff', color='#a855f7')
        fluxo.node('D', '4. AEE\n(Duplo Fundo)', fillcolor='#ffedd5', color='#f97316')
        
        fluxo.edge('A', 'B', label=' Equipe Escolar')
        fluxo.edge('B', 'C', label=' Substitui Laudo')
        fluxo.edge('C', 'D', label=' Financiamento')
        
        st.graphviz_chart(fluxo, use_container_width=True)
    except:
        st.error("Visualizador gráfico indisponível.")

    st.divider()
    
    # Cards de Fundamentos
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("""
        <div class="content-card">
            <h4>🤝 Filosofia: "Outrar-se"</h4>
            <p style="color:#64748b;">A capacidade de sentir o mundo do outro mantendo o distanciamento profissional. É ter empatia sem confundir papéis, superando o capacitismo.</p>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown("""
        <div class="content-card">
            <h4>⚖️ Justiça Curricular</h4>
            <p style="color:#64748b;">O currículo não pode ser uma barreira. O PEI materializa a justiça curricular, garantindo acesso ao conhecimento através da adaptação.</p>
        </div>
        """, unsafe_allow_html=True)

# ==============================================================================
# ABA 2: GLOSSÁRIO DE TERMOS (NOVO CONTEÚDO)
# ==============================================================================
with tab_glossario:
    st.markdown("### 📖 Glossário de Termos-Chave")
    st.markdown("Conceitos fundamentais para alinhar a linguagem da equipe escolar.")
    
    termo_busca = st.text_input("🔍 Pesquisar termo...", placeholder="Ex: Capacitismo, PEI, AEE...")

    # Dados do Glossário (Copiados do seu input)
    glossario_db = [
        {"t": "AEE (Atendimento Educacional Especializado)", "d": "Serviços educacionais suplementares que potencializam habilidades para que o aluno adquira autonomia. É transversal a todos os níveis, mas não substitui a escolarização regular."},
        {"t": "Alteridade", "d": "Conceito relacionado à capacidade de reconhecer e respeitar o 'outro' em sua diferença, incorporado por uma escola com responsabilidade social."},
        {"t": "Capacitismo", "d": "Toda forma de distinção, restrição ou exclusão que tenha o propósito de prejudicar o exercício dos direitos da pessoa com deficiência. Preconceito que pressupõe incapacidade."},
        {"t": "Cultura do Pertencimento", "d": "Uma cultura escolar onde o aluno realmente faz parte da comunidade, sendo condição essencial para o desenvolvimento do público-alvo da educação inclusiva."},
        {"t": "Declaração de Salamanca", "d": "Resolução da ONU (1994) que estabeleceu princípios para a educação especial, formalizando o compromisso com a escola inclusiva."},
        {"t": "Educação Inclusiva", "d": "Direito constitucional. Garante que todos aprendam juntos nos mesmos ambientes, independentemente de diferenças. Engloba a educação especial e a regular."},
        {"t": "Estudo de Caso", "d": "Metodologia de produção e registro de informações. Na legislação de 2025, é a etapa inicial (porta de entrada) que substitui o laudo médico para identificação de necessidades."},
        {"t": "Justiça Curricular", "d": "Conceito que busca um currículo relevante e representativo, capaz de promover igualdade de condições respeitando as particularidades."},
        {"t": "Outragem / Outrar-se", "d": "Postura de quem é capaz de se colocar no lugar do outro, sentir o mundo do outro como se fosse seu próprio, numa relação empática e acolhedora."},
        {"t": "PcD", "d": "Sigla utilizada para se referir à Pessoa com Deficiência (termo legal correto)."},
        {"t": "PEI (Plano Educacional Individualizado)", "d": "Documento pedagógico de natureza obrigatória e atualização contínua ('documento vivo'), que visa garantir o atendimento personalizado."},
        {"t": "PNAD Contínua", "d": "Pesquisa do IBGE que em 2022 produziu estatísticas inéditas: 18,6 milhões de brasileiros com deficiência e grandes disparidades na educação/trabalho."},
        {"t": "Profissional de Apoio Escolar", "d": "Atua no suporte (higiene, alimentação, locomoção). Conforme 2025, exige nível médio + 180h de formação. Substitui o termo 'cuidador'."},
        {"t": "Tecnologias Assistivas", "d": "Ferramentas e recursos que auxiliam na funcionalidade e autonomia, como pranchas de comunicação, softwares adaptados, etc."},
        {"t": "Vieses Inconscientes", "d": "Processos automáticos do cérebro que levam a reproduzir comportamentos preconceituosos por associações aprendidas socialmente."}
    ]

    # Filtragem e Renderização
    termos_filtrados = [item for item in glossario_db if termo_busca.lower() in item['t'].lower() or termo_busca.lower() in item['d'].lower()]

    if not termos_filtrados:
        st.warning("Nenhum termo encontrado.")
    
    for item in termos_filtrados:
        st.markdown(f"""
        <div class="glossary-box">
            <div class="glossary-term">{item['t']}</div>
            <div class="glossary-def">{item['d']}</div>
        </div>
        """, unsafe_allow_html=True)

# ==============================================================================
# ABA 3: BIBLIOTECA VIRTUAL (EXPANSIVA COM LINKS)
# ==============================================================================
with tab_biblio:
    st.markdown("### 📚 Biblioteca Virtual & Referências")
    st.markdown("Clique nos itens para expandir o resumo e acessar o documento original.")

    # Função auxiliar para gerar card de livro
    def render_book(titulo, autor, resumo, link=None, tag="Referência"):
        with st.expander(f"📖 {titulo}"):
            st.markdown(f"**Autor(es):** {autor}")
            st.markdown(f"**Sobre:** {resumo}")
            if link:
                st.markdown(f"""<a href="{link}" target="_blank" class="biblio-link">🔗 Acessar Documento Oficial</a>""", unsafe_allow_html=True)
            else:
                st.caption("Documento disponível no acervo físico ou restrito.")

    # --- LISTA CURADA (Baseada no seu upload) ---
    
    st.markdown("#### 🏛️ Legislação e Políticas Públicas")
    
    render_book(
        "Lei Brasileira de Inclusão (Lei 13.146/2015)",
        "Governo Federal (Brasil)",
        "O Estatuto da Pessoa com Deficiência. Define o conceito moderno de deficiência (impedimento + barreira), criminaliza a discriminação e garante o direito ao acompanhante e à acessibilidade.",
        "http://www.planalto.gov.br/ccivil_03/_ato2015-2018/2015/lei/l13146.htm"
    )
    
    render_book(
        "Decreto 12.686 e 12.773 (2025)",
        "Governo Federal (Nova Política)",
        "Atualizam o financiamento do AEE (Duplo Fundo) e endurecem regras contra recusa de matrícula em escolas privadas. Estabelecem o Estudo de Caso como padrão.",
        "https://www.planalto.gov.br" # Link genérico pois o decreto é muito recente
    )

    render_book(
        "Política Nacional de Educação Especial (PNEEPEI 2008)",
        "MEC / SEESP",
        "Documento histórico que rompeu com o modelo de escolas segregadas e consolidou a matrícula na escola comum.",
        "http://portal.mec.gov.br/seesp/arquivos/pdf/politica.pdf"
    )

    st.markdown("#### 🧠 Fundamentos e Evidências")

    render_book(
        "Os Benefícios da Educação Inclusiva (2016)",
        "Instituto Alana / ABT Associates",
        "Revisão sistemática de mais de 80 estudos que comprova: estudantes sem deficiência em salas inclusivas desenvolvem melhores habilidades socioemocionais e acadêmicas.",
        "https://alana.org.br/wp-content/uploads/2016/11/Os_Beneficios_da_Ed_Inclusiva_final.pdf"
    )

    render_book(
        "Declaração de Salamanca (1994)",
        "UNESCO",
        "Marco mundial. Estabelece que as escolas regulares com orientação inclusiva são os meios mais eficazes de combater atitudes discriminatórias.",
        "https://unesdoc.unesco.org/ark:/48223/pf0000139394"
    )

    st.markdown("#### 📘 Pedagogia e Prática")

    render_book(
        "Inclusão Escolar: O que é? Por quê? Como fazer?",
        "Maria Teresa Eglér Mantoan (2003)",
        "Obra clássica que diferencia 'Integração' de 'Inclusão' e oferece caminhos práticos para a diferenciação pedagógica.",
        None 
    )

    render_book(
        "Base Nacional Comum Curricular (BNCC)",
        "Ministério da Educação",
        "Documento normativo que define as aprendizagens essenciais. A inclusão na BNCC pressupõe que todos alcancem os objetivos, com as devidas adaptações.",
        "https://www.gov.br/mec/pt-br/escola-em-tempo-integral/BNCC_EI_EF_110518_versaofinal.pdf"
    )

    render_book(
        "Capacitismo: o que é, onde vive, como se reproduz?",
        "Sidney Andrade",
        "Artigo fundamental para entender o preconceito estrutural contra pessoas com deficiência.",
        "https://medium.com/@sidneyandrade23/capacitismo-o-que-%C3%A9-onde-vive-como-sereproduz-5f68c5fdf73e"
    )

# ==============================================================================
# ABA 4: MANUAL DO SISTEMA
# ==============================================================================
with tab_manual:
    st.markdown("### ⚙️ Manual de Uso Omnisfera")
    
    col_steps1, col_steps2 = st.columns(2)
    
    with col_steps1:
        st.info("**1. Módulo PEI 360º (Professor Regente)**")
        st.markdown("""
        1.  **Cadastro:** Preencha os dados e o Hiperfoco.
        2.  **Mapeamento:** Use os sliders nas abas Acadêmico/Social.
        3.  **IA:** Gere o PEI Técnico na aba Consultoria IA.
        4.  **Gamificação:** Crie a missão na aba Jornada.
        """)
        
    with col_steps2:
        st.info("**2. Módulo PAEE (Sala de Recursos)**")
        st.markdown("""
        1.  **Diagnóstico:** Identifique barreiras de acesso.
        2.  **Plano:** Defina metas de habilidades (ex: uso de tesoura).
        3.  **Articulação:** Gere a carta para o professor da sala.
        """)

# Rodapé
st.markdown("---")
st.caption("Central de Conhecimento Omnisfera • Baseada na Legislação Vigente 2026")
