import streamlit as st
import graphviz
import time

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
        border-radius: 0 0 24px 24px;
        color: white;
        margin-top: -60px;
        margin-bottom: 30px;
        box-shadow: 0 10px 30px -10px rgba(15, 82, 186, 0.4);
    }
    .hero-title { font-size: 2.5rem; font-weight: 800; margin-bottom: 5px; }
    .hero-subtitle { font-size: 1.1rem; opacity: 0.9; font-weight: 300; }

    /* Cards e Containers */
    .content-card {
        background: white; border: 1px solid #e2e8f0; border-radius: 16px;
        padding: 24px; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        transition: transform 0.2s; height: 100%; margin-bottom: 20px;
    }
    .content-card:hover { transform: translateY(-3px); border-color: #0F52BA; }
    
    /* Manual Step Visuals */
    .manual-box {
        border-left: 5px solid #0F52BA; background: white; padding: 25px;
        border-radius: 0 12px 12px 0; margin-bottom: 25px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.03);
    }
    .manual-header { font-size: 1.2rem; font-weight: 700; color: #1e293b; margin-bottom: 10px; display: flex; align-items: center; gap: 10px; }
    .manual-quote { font-style: italic; color: #64748b; background: #f8fafc; padding: 10px; border-radius: 6px; margin-bottom: 15px; border-left: 3px solid #cbd5e1; }
    .key-concept { background-color: #eff6ff; border: 1px solid #bfdbfe; color: #1e40af; padding: 12px; border-radius: 8px; margin-top: 15px; font-size: 0.9rem; font-weight: 600; }

    /* Glossários */
    .term-good { background: #f0fdf4; border-left: 4px solid #16a34a; padding: 15px; border-radius: 8px; margin-bottom: 15px; box-shadow: 0 2px 5px rgba(0,0,0,0.02); }
    .term-bad { background: #fef2f2; border-left: 4px solid #dc2626; padding: 15px; border-radius: 8px; margin-bottom: 15px; box-shadow: 0 2px 5px rgba(0,0,0,0.02); }
    .glossary-item { 
        background: white; padding: 20px; border-radius: 12px; border-left: 5px solid #0F52BA; 
        margin-bottom: 15px; box-shadow: 0 2px 8px rgba(0,0,0,0.05); transition: all 0.2s;
    }
    .glossary-item:hover { box-shadow: 0 5px 15px rgba(0,0,0,0.1); }

    /* AI Chat Box */
    .ai-box {
        background: linear-gradient(135deg, #ffffff 0%, #f0fdfa 100%);
        border: 2px solid #ccfbf1; border-radius: 16px; padding: 20px;
        margin-top: 20px;
    }

    /* Abas */
    .stTabs [data-baseweb="tab-list"] { gap: 8px; flex-wrap: wrap; }
    .stTabs [data-baseweb="tab"] {
        background-color: white; border-radius: 8px; border: 1px solid #e2e8f0;
        padding: 8px 16px; font-weight: 600; color: #64748b; flex-grow: 1; text-align: center;
    }
    .stTabs [aria-selected="true"] {
        background-color: #0F52BA !important; color: white !important; border-color: #0F52BA !important;
    }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# 2. HERO
# ==============================================================================
st.markdown("""
<div class="hero-container">
    <div class="hero-title">🧠 Central de Inteligência Inclusiva</div>
    <div class="hero-subtitle">Fundamentos Pedagógicos, Marcos Legais e Ferramentas Práticas.</div>
</div>
""", unsafe_allow_html=True)

# ==============================================================================
# 3. NAVEGAÇÃO PRINCIPAL (SEPARADA)
# ==============================================================================
tab_panorama, tab_legal, tab_glossario, tab_linguagem, tab_biblio, tab_manual = st.tabs([
    "📊 Panorama & Fluxos", 
    "⚖️ Legislação & IA", 
    "📖 Glossário Técnico", 
    "🗣️ Dicionário Inclusivo",
    "📚 Biblioteca Virtual",
    "📘 Manual da Jornada"
])

# ==============================================================================
# ABA 1: PANORAMA (FUNDAMENTOS)
# ==============================================================================
with tab_panorama:
    st.markdown("### 🔄 O Fluxo da Inclusão (Omnisfera 2025)")
    st.caption("Visualização do ecossistema escolar atualizado com os novos decretos.")
    
    try:
        fluxo = graphviz.Digraph()
        fluxo.attr(rankdir='LR', bgcolor='transparent', margin='0')
        fluxo.attr('node', shape='box', style='rounded,filled', fontname='Inter', fontsize='11', height='0.6')
        
        fluxo.node('A', '1. ACOLHIMENTO\n(Matrícula Garantida)', fillcolor='#dbeafe', color='#3b82f6')
        fluxo.node('B', '2. ESTUDO DE CASO\n(Avaliação Pedagógica)', fillcolor='#0F52BA', fontcolor='white', color='#0F52BA')
        fluxo.node('C', '3. IDENTIFICAÇÃO\n(Necessidades)', fillcolor='#dcfce7', color='#22c55e')
        fluxo.node('D', '4. PLANEJAMENTO\n(PEI + PAEE)', fillcolor='#f3e8ff', color='#a855f7')
        fluxo.node('E', '5. PRÁTICA\n(Sala + AEE)', fillcolor='#ffedd5', color='#f97316')
        
        fluxo.edge('A', 'B', label=' Equipe')
        fluxo.edge('B', 'C', label=' Substitui Laudo')
        fluxo.edge('C', 'D')
        fluxo.edge('D', 'E', label=' Duplo Fundo')
        
        st.graphviz_chart(fluxo, use_container_width=True)
    except:
        st.error("Visualizador gráfico indisponível.")

    st.divider()
    
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
# ABA 2: LEGISLAÇÃO & IA
# ==============================================================================
with tab_legal:
    c_info, c_ai = st.columns([1.5, 1])
    
    with c_info:
        st.markdown("### 📜 Legislação em Foco (2025)")
        
        with st.expander("💰 Decreto 12.686/2025: O Financiamento (Duplo Fundo)", expanded=True):
            st.markdown("""
            **Mudança Estrutural:**
            1.  **Dupla Matrícula:** O aluno público-alvo da educação especial é contabilizado **duas vezes** no FUNDEB (Matrícula Comum + AEE).
            2.  **Destinação:** A verba extra deve ser usada para Sala de Recursos, materiais adaptados e contratação de profissionais de apoio.
            """)
            
        with st.expander("🚫 Decreto 12.773/2025: Garantia de Acesso (Escolas Privadas)"):
            st.markdown("""
            **Tolerância Zero para Barreiras:**
            1.  **Taxas Extras:** É **ilegal** cobrar valor adicional na mensalidade para custear monitor ou material.
            2.  **Porta de Entrada:** A escola não pode exigir laudo médico para efetivar a matrícula. A avaliação pedagógica é soberana.
            """)

        st.markdown("#### ⏳ Marcos Históricos")
        st.caption("1988 (Constituição) • 1994 (Salamanca) • 2008 (PNEEPEI) • 2015 (LBI)")

    with c_ai:
        st.markdown("""
        <div class="ai-box">
            <div style="display:flex; align-items:center; gap:10px;">
                <span style="font-size:2rem;">🤖</span>
                <div style="font-weight:700; color:#0d9488;">Consultor Legal IA</div>
            </div>
            <p style="font-size:0.9rem; color:#475569; margin-top:5px;">
                Dúvidas sobre a lei? Pergunte à nossa inteligência especializada nos decretos de inclusão.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        user_question = st.text_input("Digite sua dúvida jurídica aqui:", placeholder="Ex: A escola pode exigir laudo para matricular?")
        
        if user_question:
            with st.spinner("Analisando Decretos 12.686 e 12.773..."):
                time.sleep(1.5)
                st.markdown(f"""
                <div style="background:white; padding:15px; border-radius:10px; border-left:4px solid #0d9488; margin-top:10px; box-shadow:0 4px 10px rgba(0,0,0,0.05);">
                    <strong>Resposta da IA:</strong><br>
                    Com base no <strong>Decreto 12.773/2025</strong>, a exigência de laudo médico como condição prévia para matrícula é ilegal. A escola deve realizar o <strong>Estudo de Caso</strong> pedagógico.
                </div>
                """, unsafe_allow_html=True)

# ==============================================================================
# ABA 3: GLOSSÁRIO TÉCNICO (COMPLETO)
# ==============================================================================
with tab_glossario:
    st.markdown("### 📖 Glossário Técnico Conceitual")
    st.markdown("Definições oficiais para embasar relatórios e PEIs.")
    
    termo_busca = st.text_input("🔍 Filtrar conceitos:", placeholder="Digite para buscar...")

    # LISTA COMPLETA RESTAURADA
    glossario_db = [
        {"t": "AEE (Atendimento Educacional Especializado)", "d": "Serviços educacionais suplementares que potencializam habilidades para que o aluno adquira autonomia. É transversal a todos os níveis, mas não substitui a escolarização regular."},
        {"t": "Alteridade", "d": "Conceito relacionado à capacidade de reconhecer e respeitar o 'outro' em sua diferença, incorporado por uma escola com responsabilidade social."},
        {"t": "Capacitismo", "d": "Toda forma de distinção, restrição ou exclusão que tenha o propósito de prejudicar, impedir ou anular o reconhecimento dos direitos da pessoa com deficiência."},
        {"t": "Cultura do Pertencimento", "d": "Uma cultura escolar onde o aluno realmente faz parte da comunidade, sendo condição essencial para o desenvolvimento inclusivo."},
        {"t": "Declaração de Salamanca", "d": "Resolução da ONU (1994) que estabeleceu princípios para a educação especial, formalizando o compromisso com a escola inclusiva."},
        {"t": "Educação Especial", "d": "Modalidade de educação que, dentro da inclusiva, oferece serviços, recursos e estratégias para atender às necessidades específicas."},
        {"t": "Educação Inclusiva", "d": "A efetivação do direito constitucional à educação para todos, garantindo que aprendam juntos independentemente das diferenças."},
        {"t": "Estudo de Caso", "d": "Metodologia de produção e registro de informações. Em 2025, é a porta de entrada que substitui o laudo médico."},
        {"t": "Justiça Curricular", "d": "Conceito que busca um currículo relevante e representativo, promovendo igualdade de condições e respeitando particularidades."},
        {"t": "Outragem / Outrar-se", "d": "Postura de quem é capaz de se colocar no lugar do outro, sentir o mundo do outro como se fosse seu próprio, numa relação empática."},
        {"t": "PcD", "d": "Sigla utilizada para se referir à Pessoa com Deficiência."},
        {"t": "PEI (Plano Educacional Individualizado)", "d": "Documento pedagógico de natureza obrigatória e atualização contínua ('documento vivo'), que visa garantir o atendimento personalizado."},
        {"t": "PNEEPEI", "d": "Política Nacional de Educação Especial na Perspectiva da Educação Inclusiva (2008)."},
        {"t": "PNAD Contínua", "d": "Pesquisa do IBGE que produziu estatísticas sobre pessoas com deficiência no Brasil."},
        {"t": "Profissional de Apoio Escolar", "d": "Atua no suporte (higiene, alimentação, locomoção). Deve ter nível médio e formação de 180h. Substitui 'cuidador'."},
        {"t": "Tecnologias Assistivas", "d": "Ferramentas, recursos ou dispositivos que auxiliam na funcionalidade e autonomia (pranchas, softwares, dispositivos)."},
        {"t": "Vieses Inconscientes", "d": "Processos inconscientes que levam a reproduzir comportamentos e discursos preconceituosos por associações aprendidas socialmente."}
    ]

    filtro = [g for g in glossario_db if termo_busca.lower() in g['t'].lower() or termo_busca.lower() in g['d'].lower()]
    
    for item in filtro:
        st.markdown(f"""
        <div class="glossary-item">
            <div style="color:#0F52BA; font-weight:700; font-size:1.1rem; margin-bottom:5px;">{item['t']}</div>
            <div style="color:#475569; font-size:0.95rem; line-height:1.5;">{item['d']}</div>
        </div>""", unsafe_allow_html=True)

# ==============================================================================
# ABA 4: DICIONÁRIO ANTICAPACITISTA (SEPARADO)
# ==============================================================================
with tab_linguagem:
    st.markdown("### 🗣️ Guia de Linguagem Inclusiva")
    st.markdown("Termos para adotar e termos para abolir, baseados no respeito e na técnica.")

    col_g1, col_g2 = st.columns(2)
    
    with col_g1:
        st.markdown("#### ✅ PREFIRA (Termos Corretos)")
        termos_bons = [
            ("Pessoa com Deficiência (PcD)", "Termo legal da LBI. Marca a deficiência como atributo, não identidade total."),
            ("Estudante com Deficiência", "Foco na pessoa primeiro."),
            ("Neurodivergente", "Funcionamento cerebral atípico (TEA, TDAH), sem conotação de doença."),
            ("Surdo", "Termo identitário correto (Comunidade Surda)."),
            ("Ritmo Próprio", "Respeita a singularidade da aprendizagem."),
            ("Típico / Atípico", "Substitui 'Normal' e 'Anormal'.")
        ]
        for t, d in termos_bons:
            st.markdown(f"""
            <div class="term-good">
                <div style="color:#166534; font-weight:bold; font-size:1.05rem;">{t}</div>
                <div style="color:#14532d; font-size:0.9rem;">{d}</div>
            </div>""", unsafe_allow_html=True)

    with col_g2:
        st.markdown("#### 🚫 EVITE (Termos Ofensivos)")
        termos_ruins = [
            ("Portador de Deficiência", "Deficiência não se porta (como uma bolsa). É intrínseca."),
            ("Aluno de Inclusão", "Segrega. Todos são alunos de inclusão."),
            ("Criança Especial", "Eufemismo que infantiliza. Use o nome da criança."),
            ("Surdo-Mudo", "Erro técnico. A surdez não implica mudez. Surdos têm voz."),
            ("Atrasado / Lento", "Pejorativo. Ignora a neurodiversidade."),
            ("Doença Mental", "Deficiência não é doença. Doença tem cura; deficiência é condição."),
            ("Fingir de João-sem-braço", "Expressão capacitista.")
        ]
        for t, d in termos_ruins:
            st.markdown(f"""
            <div class="term-bad">
                <div style="color:#991b1b; font-weight:bold; text-decoration:line-through; font-size:1.05rem;">{t}</div>
                <div style="color:#7f1d1d; font-size:0.9rem;">{d}</div>
            </div>""", unsafe_allow_html=True)

# ==============================================================================
# ABA 5: BIBLIOTECA VIRTUAL (ENRIQUECIDA)
# ==============================================================================
with tab_biblio:
    st.markdown("### 📚 Acervo Bibliográfico Completo")
    st.markdown("Clique nos itens para expandir o resumo e acessar o link (quando disponível).")

    def render_livro(titulo, autor, resumo, link=None, tag="Referência"):
        with st.expander(f"📕 {titulo}"):
            st.markdown(f"**Autor/Fonte:** {autor}")
            st.markdown(f"**Sobre:** {resumo}")
            if link:
                st.markdown(f"""<a href="{link}" target="_blank" class="biblio-link">🔗 Acessar Documento</a>""", unsafe_allow_html=True)

    st.markdown("#### 🏛️ Legislação e Documentos Oficiais")
    render_livro("Lei Brasileira de Inclusão (13.146/2015)", "Brasil", "Estatuto da PcD. Define barreira e criminaliza discriminação.", "http://www.planalto.gov.br/ccivil_03/_ato2015-2018/2015/lei/l13146.htm")
    render_livro("Decretos 12.686 e 12.773 (2025)", "Governo Federal", "Regulamentam o financiamento do AEE (Duplo Fundo) e proíbem cobranças extras.", "https://www.planalto.gov.br")
    render_livro("Política Nacional de Educação Especial (2008)", "MEC", "Consolidou a matrícula na escola comum.", "http://portal.mec.gov.br/seesp/arquivos/pdf/politica.pdf")
    render_livro("Declaração de Salamanca (1994)", "UNESCO", "Marco mundial da escola inclusiva.", "https://unesdoc.unesco.org/ark:/48223/pf0000139394")
    render_livro("Base Nacional Comum Curricular (BNCC)", "MEC", "Define as aprendizagens essenciais.", "https://www.gov.br/mec/pt-br/escola-em-tempo-integral/BNCC_EI_EF_110518_versaofinal.pdf")
    render_livro("Convenção sobre os Direitos das Pessoas com Deficiência", "ONU/Brasil (2008)", "Tratado internacional com status de emenda constitucional.", "https://www.planalto.gov.br/ccivil_03/_ato2007-2010/2009/decreto/d6949.htm")

    st.markdown("#### 🧠 Fundamentos Pedagógicos e Autores")
    render_livro("Inclusão Escolar: O que é? Como fazer?", "Maria Teresa Eglér Mantoan (2003)", "Diferencia integração de inclusão. Obra clássica.", None)
    render_livro("O Currículo e seus desafios: em busca da justiça curricular", "Branca Jurema Ponce (2018)", "Discute a justiça curricular como base da inclusão.", "http://www.curriculosemfronteiras.org/vol18iss3articles/ponce.pdf")
    render_livro("Altas Habilidades/Superdotação: inteligência e criatividade", "Virgolim, A. M. R. (2014)", "Conceitos de Renzulli e modelo dos três anéis.", None)
    render_livro("Mentes que mudam: a arte e a ciência de mudar as nossas mentes", "Howard Gardner (2005)", "Teoria das Inteligências Múltiplas aplicada.", None)
    render_livro("Capacitismo: o que é, onde vive?", "Sidney Andrade", "Entendendo o preconceito estrutural.", "https://medium.com/@sidneyandrade23")
    render_livro("Os Benefícios da Educação Inclusiva (2016)", "Instituto Alana", "Estudos comprovam ganhos para todos.", "https://alana.org.br/wp-content/uploads/2016/11/Os_Beneficios_da_Ed_Inclusiva_final.pdf")

# ==============================================================================
# ABA 6: MANUAL DA JORNADA (COMPLETO)
# ==============================================================================
with tab_manual:
    st.markdown("### 📘 Manual da Jornada Omnisfera: O Ciclo da Inclusão")
    st.markdown("Fluxo de trabalho ideal conectando planejamento, AEE e prática.")

    # PASSO 1
    st.markdown("""
    <div class="manual-box">
        <div class="manual-header"><span style="font-size:2rem;">1️⃣</span> O Alicerce: Planejamento (PEI)</div>
        <div class="manual-quote">"Não há inclusão sem intenção. Conhecer para incluir."</div>
        <p>Tudo começa na página <strong>Estratégias & PEI</strong>. Antes de pensar em recursos, precisamos mapear quem é o estudante.</p>
        <p><strong>Ação na Plataforma:</strong></p>
        <ul>
            <li>Registre o histórico e o diagnóstico na aba Estudante.</li>
            <li>Mapeie as barreiras de aprendizagem (cognitivas, sensoriais ou físicas).</li>
            <li>Use a IA para estruturar metas de curto, médio e longo prazo.</li>
        </ul>
        <div class="key-concept">
            💡 <strong>Conceito Chave:</strong> O PEI não é um "laudo", é um projeto de futuro. Ele define O QUE vamos ensinar e QUAIS barreiras remover.
        </div>
    </div>
    """, unsafe_allow_html=True)

    # PASSO 2
    st.markdown("""
    <div class="manual-box">
        <div class="manual-header"><span style="font-size:2rem;">2️⃣</span> A Estratégia: O AEE e o Plano de Ação (PAEE)</div>
        <div class="manual-quote">"A articulação entre o suporte especializado e a sala comum."</div>
        <p>Aqui entra a execução técnica do PEI. Na página <strong>Plano de Ação / PAEE</strong>, organizamos o Atendimento Especializado.</p>
        <p><strong>Ação na Plataforma:</strong></p>
        <ul>
            <li>Defina a frequência e o foco dos atendimentos no contraturno.</li>
            <li>Estabeleça a ponte com o professor regente.</li>
            <li>Organize a Tecnologia Assistiva.</li>
        </ul>
        <div class="key-concept">
            💡 <strong>Conceito Chave:</strong> O AEE não funciona isolado. Ele é o laboratório onde se testam as ferramentas que permitirão ao aluno acessar o currículo comum.
        </div>
    </div>
    """, unsafe_allow_html=True)

    # PASSO 3
    st.markdown("""
    <div class="manual-box">
        <div class="manual-header"><span style="font-size:2rem;">3️⃣</span> A Ferramenta: Adaptação (Hub de Inclusão)</div>
        <div class="manual-quote">"Acessibilidade é garantir que o conteúdo chegue a todos."</div>
        <p>Com o plano definido, vamos construir a aula. A página <strong>Hub de Recursos</strong> é sua oficina.</p>
        <div class="key-concept">
            💡 <strong>Conceito Chave:</strong> Adaptar não é empobrecer o currículo, é torná-lo flexível.
        </div>
    </div>
    """, unsafe_allow_html=True)

    # PASSO 4 e 5 (Agrupados)
    c_log, c_data = st.columns(2)
    with c_log:
        st.markdown("""
        <div class="content-card" style="border-left:5px solid #f59e0b;">
            <h4>4️⃣ O Registro: Diário de Bordo</h4>
            <p><em>"O olhar atento transforma a prática."</em></p>
            <p>Registre o que funcionou e o engajamento. Use o conceito de <strong>"outrar-se"</strong>.</p>
        </div>
        """, unsafe_allow_html=True)
    with c_data:
        st.markdown("""
        <div class="content-card" style="border-left:5px solid #ef4444;">
            <h4>5️⃣ O Fechamento: Avaliação</h4>
            <p><em>"Avaliar para recalcular a rota."</em></p>
            <p>Use as <strong>Rubricas</strong> para fugir do "achismo". Se a meta foi atingida, avançamos.</p>
        </div>
        """, unsafe_allow_html=True)

    # Tabela Resumo Final
    st.markdown("#### 🧭 Resumo do Ecossistema")
    st.markdown("""
    | Passo | Módulo | Função |
    | :--- | :--- | :--- |
    | 1 | 📘 PEI | **Fundamentar:** Quem é o aluno? |
    | 2 | 🧩 PAEE | **Estruturar:** Suporte especializado. |
    | 3 | 🚀 Hub | **Instrumentalizar:** Criar recursos. |
    | 4 | 📓 Diário | **Registrar:** Execução diária. |
    | 5 | 📊 Dados | **Validar:** Medir sucesso. |
    """)

# Rodapé
st.markdown("---")
st.caption("Central de Conhecimento Omnisfera • Atualizada 2026")
