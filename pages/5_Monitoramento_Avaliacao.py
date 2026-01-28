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
    
    /* Estilos Específicos do Manual */
    .manual-step {
        border-left: 5px solid #0F52BA; background: white; padding: 20px;
        border-radius: 8px; margin-bottom: 20px; box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }
    .manual-title { font-size: 1.2rem; font-weight: 700; color: #1e293b; margin-bottom: 5px; }
    .manual-quote { font-style: italic; color: #64748b; font-size: 0.9rem; margin-bottom: 15px; border-bottom: 1px solid #f1f5f9; padding-bottom: 10px;}
    .key-concept {
        background-color: #eff6ff; border-radius: 6px; padding: 10px;
        font-size: 0.9rem; color: #1e40af; margin-top: 15px; border: 1px solid #dbeafe;
    }

    /* Estilo do Glossário */
    .glossary-term { color: #0F52BA; font-weight: 700; font-size: 1.1rem; margin-bottom: 5px; }
    .glossary-def { color: #475569; line-height: 1.6; font-size: 0.95rem; text-align: justify; }
    .glossary-box {
        background: white; padding: 20px; border-radius: 10px;
        border-left: 4px solid #0F52BA; margin-bottom: 15px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        transition: all 0.2s;
    }
    .glossary-box:hover { box-shadow: 0 4px 12px rgba(0,0,0,0.1); }

    /* Estilo do Dicionário Anticapacitista */
    .term-bad { color: #dc2626; font-weight: bold; text-decoration: line-through; }
    .term-good { color: #16a34a; font-weight: bold; }
    .term-box-good { background: #f0fdf4; border-left: 4px solid #16a34a; padding: 15px; border-radius: 6px; margin-bottom: 10px; }
    .term-box-bad { background: #fef2f2; border-left: 4px solid #dc2626; padding: 15px; border-radius: 6px; margin-bottom: 10px; }

    /* Estilo da Biblioteca */
    .biblio-link {
        text-decoration: none; color: white; background-color: #0F52BA;
        padding: 6px 12px; border-radius: 6px; font-size: 0.8rem; display: inline-block;
        margin-top: 10px; transition: background 0.3s;
    }
    .biblio-link:hover { background-color: #0b3d91; color: white; }
    
    /* Timeline Tags */
    .time-tag {
        background: #e2e8f0; padding: 2px 8px; border-radius: 4px; font-size: 0.8rem; font-weight: bold; color: #475569;
    }
    
    /* Abas Customizadas */
    .stTabs [data-baseweb="tab-list"] { gap: 10px; padding: 10px 0; overflow-x: auto; }
    .stTabs [data-baseweb="tab"] {
        background-color: white; border-radius: 8px; border: 1px solid #e2e8f0;
        padding: 8px 16px; font-weight: 600; color: #64748b; white-space: nowrap;
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
    <div class="hero-subtitle">Fundamentos Pedagógicos, Marcos Legais e Ferramentas Práticas para a Educação Inclusiva.</div>
</div>
""", unsafe_allow_html=True)

# ==============================================================================
# 3. NAVEGAÇÃO
# ==============================================================================
tab_panorama, tab_legal, tab_glossario, tab_linguagem, tab_biblio, tab_manual = st.tabs([
    "📊 Panorama & Fluxos", 
    "⚖️ Legislação & Marcos", 
    "📖 Glossário Técnico",
    "🗣️ Linguagem Inclusiva",
    "📚 Biblioteca Virtual",
    "📘 Manual da Jornada"
])

# ==============================================================================
# ABA 1: PANORAMA & FLUXOS
# ==============================================================================
with tab_panorama:
    st.markdown("### 🔄 O Fluxo da Inclusão (Omnisfera 2025)")
    st.caption("Visualização do processo de entrada e permanência, atualizado com a substituição do laudo médico pelo Estudo de Caso.")
    
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
# ABA 2: LEGISLAÇÃO (COMPLETA + DESTAQUE 2025)
# ==============================================================================
with tab_legal:
    st.markdown("### ⚖️ Ecossistema Legal")
    st.markdown("Da Constituição de 88 aos Decretos de 2025: a evolução do direito.")

    # 1. Timeline Histórica (Para contexto)
    with st.expander("⏳ Linha do Tempo Histórica (Clique para ver)", expanded=False):
        st.markdown("""
        * <span class="time-tag">1988</span> **Constituição Federal:** Educação como direito de todos (Art. 205).
        * <span class="time-tag">1994</span> **Declaração de Salamanca:** Marco mundial contra a segregação.
        * <span class="time-tag">1996</span> **LDB (Lei 9.394):** Educação Especial como modalidade transversal.
        * <span class="time-tag">2008</span> **PNEEPEI:** Política Nacional que focou na escola comum.
        * <span class="time-tag">2015</span> **LBI (Lei 13.146):** Estatuto da Pessoa com Deficiência. Crime de discriminação.
        """, unsafe_allow_html=True)

    st.divider()

    # 2. Destaque 2025 (O Novo)
    st.markdown("#### 🔥 Atualizações Críticas (2025)")
    
    c1, c2 = st.columns(2)
    
    with c1:
        st.markdown("""
        <div class="content-card" style="border-left: 5px solid #22c55e;">
            <div style="display:flex; align-items:center; gap:10px; margin-bottom:10px;">
                <span style="font-size:1.5rem;">💰</span>
                <span style="font-weight:700; font-size:1.1rem;">Decreto 12.686/2025</span>
            </div>
            <p><strong>Financiamento (Duplo Fundo)</strong></p>
            <p style="font-size:0.9rem; color:#475569;">
                Garante que o aluno da Educação Especial conte <strong>duas vezes</strong> no repasse de verbas do FUNDEB:
                uma pela matrícula na classe comum e outra pelo atendimento no AEE.
            </p>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown("""
        <div class="content-card" style="border-left: 5px solid #ef4444;">
            <div style="display:flex; align-items:center; gap:10px; margin-bottom:10px;">
                <span style="font-size:1.5rem;">🚫</span>
                <span style="font-weight:700; font-size:1.1rem;">Decreto 12.773/2025</span>
            </div>
            <p><strong>Matrícula & Acesso</strong></p>
            <p style="font-size:0.9rem; color:#475569;">
                Criminaliza a recusa de matrícula e proíbe explicitamente a cobrança de <strong>taxas extras</strong> 
                em escolas privadas para acessibilidade, mediadores ou materiais adaptados.
            </p>
        </div>
        """, unsafe_allow_html=True)

# ==============================================================================
# ABA 3: GLOSSÁRIO TÉCNICO (INDEPENDENTE)
# ==============================================================================
with tab_glossario:
    st.markdown("### 📖 Glossário Técnico Conceitual")
    st.markdown("Definições oficiais para embasar relatórios, PEIs e reuniões pedagógicas.")
    
    termo_busca = st.text_input("🔍 Buscar conceito:", placeholder="Ex: Justiça Curricular, Alteridade...")

    # Banco de Dados Completo (Baseado no seu texto)
    glossario_db = [
        {"t": "AEE (Atendimento Educacional Especializado)", "d": "Serviços educacionais suplementares que potencializam habilidades para que o aluno adquira autonomia. É transversal a todos os níveis, etapas e modalidades de ensino, mas não substitui a escolarização regular."},
        {"t": "Alteridade", "d": "Conceito relacionado à capacidade de reconhecer e respeitar o 'outro' em sua diferença, incorporado por uma escola com responsabilidade social."},
        {"t": "Capacitismo", "d": "Toda forma de distinção, restrição ou exclusão, por ação ou omissão, que tenha o propósito de prejudicar, impedir ou anular o reconhecimento ou o exercício dos direitos e das liberdades fundamentais de pessoa com deficiência."},
        {"t": "Cultura do Pertencimento", "d": "Uma cultura escolar onde o(a) aluno(a) realmente faz parte da comunidade, sendo uma das condições essenciais para o desenvolvimento do público-alvo da educação inclusiva."},
        {"t": "Declaração de Salamanca", "d": "Resolução da ONU (1994) que estabeleceu princípios, políticas e práticas para a educação especial, formalizando o compromisso dos países com a construção de um sistema educacional inclusivo."},
        {"t": "Educação Inclusiva", "d": "A efetivação do direito constitucional à educação para todos, garantindo que todos aprendam juntos nos mesmos ambientes, independentemente de suas diferenças e dificuldades. Engloba a educação especial e a regular."},
        {"t": "Estudo de Caso", "d": "Metodologia de produção, sistematização e registro de informações e estratégias relativas ao AEE. Configura-se, na nova legislação de 2025, como a etapa inicial (porta de entrada) para a identificação do estudante público da educação especial."},
        {"t": "Justiça Curricular", "d": "Conceito que busca estabelecer a inclusão de todos com suas diferenças por meio de um currículo relevante, representativo e capaz de promover igualdade de condições para todos os estudantes, levando em conta suas particularidades e contexto."},
        {"t": "Outragem / Outrar-se", "d": "Postura de quem é capaz de se colocar no lugar do outro, sentir o mundo do outro como se fosse seu próprio, para compreendê-lo numa relação empática e acolhedora."},
        {"t": "PcD (Pessoa com Deficiência)", "d": "Sigla utilizada para se referir à pessoa com deficiência."},
        {"t": "PEI (Plano Educacional Individualizado)", "d": "Documento pedagógico, de natureza obrigatória e atualização contínua ('documento vivo'), que visa garantir a inclusão de alunos com necessidades específicas, proporcionando um atendimento personalizado e adaptado."},
        {"t": "PNEEPEI", "d": "Sigla para a Política Nacional de Educação Especial na Perspectiva da Educação Inclusiva, instituída em 2008 pelo MEC com o objetivo de articular políticas e promover a formação de professores para a inclusão escolar."},
        {"t": "PNAD Contínua", "d": "Sigla para a Pesquisa Nacional por Amostra de Domicílios Contínua, realizada pelo IBGE, que em 2022 produziu pela primeira vez estatísticas sobre pessoas com deficiência."},
        {"t": "Profissional de Apoio Escolar", "d": "Profissional que atua no suporte a alunos da educação especial. Conforme a legislação de 2025, deve ter no mínimo nível médio e formação continuada de 180 horas. O termo substitui nomenclaturas como 'cuidador' ou 'monitor'."},
        {"t": "Tecnologias Assistivas", "d": "Ferramentas, recursos ou dispositivos que auxiliam na funcionalidade de pessoas com deficiência, promovendo autonomia e inclusão, como pranchas de comunicação, softwares adaptados e outros dispositivos digitais."},
        {"t": "Vieses Inconscientes / Implícitos", "d": "Processos inconscientes, estudados pela neurociência e psicologia, que levam um indivíduo a reproduzir comportamentos e discursos preconceituosos por associações aprendidas socialmente, atribuindo defeitos a todos de um mesmo grupo."}
    ]

    # Lógica de Filtro
    termos_filtrados = [item for item in glossario_db if termo_busca.lower() in item['t'].lower() or termo_busca.lower() in item['d'].lower()]

    if not termos_filtrados:
        st.warning("Nenhum termo encontrado com essa busca.")
    
    # Renderização Limpa
    for item in termos_filtrados:
        st.markdown(f"""
        <div class="glossary-box">
            <div class="glossary-term">{item['t']}</div>
            <div class="glossary-def">{item['d']}</div>
        </div>
        """, unsafe_allow_html=True)

# ==============================================================================
# ABA 4: LINGUAGEM INCLUSIVA (ANTICAPACITISMO)
# ==============================================================================
with tab_linguagem:
    st.markdown("### 🗣️ Guia de Linguagem Anticapacitista")
    st.markdown("A linguagem cria cultura. Guia visual para alinhar a comunicação da escola.")

    col_g1, col_g2 = st.columns(2)
    
    with col_g1:
        st.markdown("#### ✅ Termos Corretos (Adotar)")
        st.markdown("Focam na pessoa e no direito.")
        termos_bons = [
            ("Pessoa com Deficiência (PcD)", "Termo legal (LBI). Marca que a deficiência é um atributo, não a pessoa inteira."),
            ("Estudante com deficiência", "O foco está no estudante, não no laudo."),
            ("Neurodivergente", "Pessoas com funcionamento cerebral atípico (TEA, TDAH, Dislexia), sem conotação de doença."),
            ("Surdo", "Termo identitário correto (assumido pela Comunidade Surda).")
        ]
        for t, d in termos_bons:
            st.markdown(f"""
            <div class="term-box-good">
                <strong>{t}</strong><br>
                <small style="color:#334155;">{d}</small>
            </div>
            """, unsafe_allow_html=True)

    with col_g2:
        st.markdown("#### 🚫 Termos a Abolir (Evitar)")
        st.markdown("Carregam estigma, piedade ou erro técnico.")
        termos_ruins = [
            ("Portador de Deficiência", "Ninguém 'porta' deficiência como se fosse um objeto. Ela é intrínseca."),
            ("Aluno de Inclusão", "Estigmatizante e segregador. Todos os alunos são de inclusão."),
            ("Criança Especial", "Eufemismo que infantiliza. Use o nome da criança."),
            ("Surdo-Mudo", "Incorreto. A surdez não implica mudez. Surdos têm voz."),
            ("Doença Mental", "Deficiência não é doença. Doença tem cura/tratamento; deficiência é condição.")
        ]
        for t, d in termos_ruins:
            st.markdown(f"""
            <div class="term-box-bad">
                <strong style="text-decoration: line-through;">{t}</strong><br>
                <small style="color:#334155;">{d}</small>
            </div>
            """, unsafe_allow_html=True)

# ==============================================================================
# ABA 5: BIBLIOTECA VIRTUAL
# ==============================================================================
with tab_biblio:
    st.markdown("### 📚 Biblioteca Virtual")
    st.markdown("Referências essenciais e documentos oficiais. Clique para ver detalhes.")

    def render_livro(titulo, autor, resumo, link=None):
        with st.expander(f"📕 {titulo}"):
            st.markdown(f"**Autor/Fonte:** {autor}")
            st.markdown(f"**Resumo:** {resumo}")
            if link:
                st.markdown(f"""<a href="{link}" target="_blank" class="biblio-link">🔗 Acessar Documento Oficial</a>""", unsafe_allow_html=True)
            else:
                st.caption("Material disponível no acervo físico ou referência interna.")

    # --- Lista Curada (Baseada no seu texto extenso) ---
    
    st.markdown("#### 🏛️ Legislação e Documentos Oficiais")
    
    render_livro(
        "Lei Brasileira de Inclusão (Lei 13.146/2015)",
        "Brasil (Governo Federal)",
        "Estatuto da Pessoa com Deficiência. Define o conceito biopsicossocial de deficiência e criminaliza a discriminação.",
        "http://www.planalto.gov.br/ccivil_03/_ato2015-2018/2015/lei/l13146.htm"
    )
    
    render_livro(
        "Decretos 12.686 e 12.773 (2025)",
        "Governo Federal",
        "Regulamentam o financiamento do AEE (Duplo Fundo) e proíbem cobranças extras em escolas privadas.",
        "https://www.planalto.gov.br"
    )

    render_livro(
        "Política Nacional de Educação Especial (2008)",
        "MEC / SEESP",
        "Documento que consolidou a matrícula na escola comum e rompeu com o modelo segregacionista.",
        "http://portal.mec.gov.br/seesp/arquivos/pdf/politica.pdf"
    )

    st.markdown("#### 🧠 Fundamentos Pedagógicos")

    render_livro(
        "Os Benefícios da Educação Inclusiva (2016)",
        "Instituto Alana / ABT Associates",
        "Revisão de 89 estudos comprovando que a inclusão beneficia alunos com e sem deficiência.",
        "https://alana.org.br/wp-content/uploads/2016/11/Os_Beneficios_da_Ed_Inclusiva_final.pdf"
    )

    render_livro(
        "Inclusão Escolar: O que é? Por quê? Como fazer?",
        "Maria Teresa Eglér Mantoan (2003)",
        "Obra clássica sobre a diferenciação pedagógica e o fim da escola que seleciona alunos.",
        None
    )

    render_livro(
        "Capacitismo: o que é, onde vive?",
        "Sidney Andrade",
        "Artigo essencial para entender a estrutura do preconceito contra PcD na sociedade.",
        "https://medium.com/@sidneyandrade23"
    )

    render_livro(
        "Declaração de Salamanca (1994)",
        "UNESCO",
        "Compromisso mundial com a escola para todos e combate a atitudes discriminatórias.",
        "https://unesdoc.unesco.org/ark:/48223/pf0000139394"
    )

# ==============================================================================
# ABA 6: MANUAL DA JORNADA (NOVO E COMPLETO)
# ==============================================================================
with tab_manual:
    st.markdown("### 📘 Manual da Jornada Omnisfera: O Ciclo da Inclusão")
    st.markdown("Fluxo de trabalho ideal conectando planejamento, AEE e prática em sala.")

    # Passo 1: PEI
    st.markdown("""
    <div class="manual-step" style="border-left-color: #3b82f6;">
        <div class="manual-title">1. O Alicerce: Planejamento (PEI)</div>
        <div class="manual-quote">"Não há inclusão sem intenção. Conhecer para incluir."</div>
        <p>Tudo começa na página <strong>Estratégias & PEI</strong>. Antes de pensar em recursos, precisamos mapear quem é o estudante.</p>
        <p><strong>Ação na Plataforma:</strong></p>
        <ul>
            <li>Registre o histórico e o diagnóstico na aba Estudante.</li>
            <li>Mapeie as barreiras de aprendizagem (cognitivas, sensoriais ou físicas).</li>
            <li>Use a IA para estruturar metas de curto, médio e longo prazo.</li>
        </ul>
        <div class="key-concept">
            💡 <strong>Conceito Chave:</strong> O PEI não é um "laudo", é um projeto de futuro. Ele define o que vamos ensinar e quais barreiras precisamos remover.
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Passo 2: PAEE
    st.markdown("""
    <div class="manual-step" style="border-left-color: #8b5cf6;">
        <div class="manual-title">2. A Estratégia: O AEE e o Plano de Ação (PAEE)</div>
        <div class="manual-quote">"A articulação entre o suporte especializado e a sala comum."</div>
        <p>Aqui entra a execução técnica do PEI. Na página <strong>Plano de Ação / PAEE</strong>, organizamos o Atendimento Educacional Especializado.</p>
        <p><strong>Ação na Plataforma:</strong></p>
        <ul>
            <li>Defina a frequência e o foco dos atendimentos no contraturno.</li>
            <li>Estabeleça a ponte com o professor regente: quais estratégias do AEE serão levadas para a sala de aula?</li>
            <li>Organize os recursos de Tecnologia Assistiva necessários.</li>
        </ul>
        <div class="key-concept">
            💡 <strong>Conceito Chave:</strong> O AEE não funciona isolado. Ele é o laboratório onde se testam as ferramentas que permitirão ao aluno acessar o currículo comum.
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Passo 3: Hub
    st.markdown("""
    <div class="manual-step" style="border-left-color: #10b981;">
        <div class="manual-title">3. A Ferramenta: Adaptação (Hub de Inclusão)</div>
        <div class="manual-quote">"Acessibilidade é garantir que o conteúdo chegue a todos."</div>
        <p>Com o plano (PEI) e a estratégia (AEE) definidos, vamos construir a aula. A página <strong>Hub de Recursos</strong> é sua "oficina pedagógica".</p>
        <p><strong>Ação na Plataforma:</strong></p>
        <ul>
            <li>Busque ou gere atividades adaptadas ao nível de desenvolvimento do aluno.</li>
            <li>Crie pranchas de comunicação alternativa ou textos simplificados.</li>
            <li>Acesse modelos validados por especialistas.</li>
        </ul>
        <div class="key-concept">
            💡 <strong>Conceito Chave:</strong> Adaptar não é empobrecer o currículo, é torná-lo flexível. O gestor e o educador devem equilibrar o currículo prescrito com a necessidade de personalização.
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Passo 4: Diário
    st.markdown("""
    <div class="manual-step" style="border-left-color: #f59e0b;">
        <div class="manual-title">4. O Registro: Diário de Bordo</div>
        <div class="manual-quote">"O olhar atento transforma a prática."</div>
        <p>A inclusão acontece nos detalhes do dia a dia. A página <strong>Diário de Bordo</strong> captura a realidade da execução.</p>
        <p><strong>Ação na Plataforma:</strong></p>
        <ul>
            <li>Documente o que funcionou e o que falhou nas atividades adaptadas.</li>
            <li>Registre a frequência e o engajamento do aluno.</li>
            <li>Use o conceito de "outrar-se" para interpretar as reações do aluno.</li>
        </ul>
        <div class="key-concept">
            💡 <strong>Conceito Chave:</strong> Sem registro, não há memória pedagógica. O Diário é a prova de que a inclusão está acontecendo.
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Passo 5: Avaliação
    st.markdown("""
    <div class="manual-step" style="border-left-color: #ef4444;">
        <div class="manual-title">5. O Fechamento: Avaliação (Evolução & Dados)</div>
        <div class="manual-quote">"Avaliar para recalcular a rota, não para rotular."</div>
        <p>Por fim, consolidamos tudo na página <strong>Avaliação e Monitoramento</strong>.</p>
        <p><strong>Ação na Plataforma:</strong></p>
        <ul>
            <li>Use as Rubricas de Avaliação para medir o avanço nas competências do PEI.</li>
            <li>Visualize gráficos de evolução.</li>
            <li>Decida: a meta foi atingida? Se sim, avançamos. Se não, voltamos ao Passo 2 (AEE) para ajustar a estratégia.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

    # Tabela Resumo
    st.markdown("#### 🧭 Resumo do Ecossistema")
    st.markdown("""
    | Passo | Módulo | Função |
    | :--- | :--- | :--- |
    | 1 | 📘 PEI | **Fundamentar:** Quem é o aluno e o que ele precisa? |
    | 2 | 🧩 PAEE (AEE) | **Estruturar:** Como o suporte especializado vai atuar? |
    | 3 | 🚀 Hub | **Instrumentalizar:** Criar os recursos para a aula. |
    | 4 | 📓 Diário | **Registrar:** Acompanhar a execução diária. |
    | 5 | 📊 Dados | **Validar:** Medir o sucesso e evoluir o plano. |
    """)

# Rodapé
st.markdown("---")
st.caption("Central de Conhecimento Omnisfera • Atualizado com Decretos 2025")
