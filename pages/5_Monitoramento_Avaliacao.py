import streamlit as st
import graphviz
import time

# ==============================================================================
# 1. SETUP & DESIGN SYSTEM
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
        background: linear-gradient(135deg, #0F52BA 0%, #2563eb 100%);
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
    .term-good { background: #f0fdf4; border-left: 4px solid #16a34a; padding: 12px; border-radius: 6px; margin-bottom: 10px; }
    .term-bad { background: #fef2f2; border-left: 4px solid #dc2626; padding: 12px; border-radius: 6px; margin-bottom: 10px; }
    .glossary-item { background: white; padding: 15px; border-radius: 8px; border-left: 4px solid #94a3b8; margin-bottom: 10px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }

    /* AI Chat Box */
    .ai-box {
        background: linear-gradient(135deg, #ffffff 0%, #f0fdfa 100%);
        border: 2px solid #ccfbf1; border-radius: 16px; padding: 20px;
        margin-top: 20px;
    }

    /* Abas */
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] {
        background-color: white; border-radius: 8px; border: 1px solid #e2e8f0;
        padding: 8px 16px; font-weight: 600; color: #64748b;
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
    <div class="hero-subtitle">Conectando Fundamentos, Legislação Viva e Prática Pedagógica.</div>
</div>
""", unsafe_allow_html=True)

# ==============================================================================
# 3. NAVEGAÇÃO PRINCIPAL
# ==============================================================================
tab_panorama, tab_legal, tab_glossario, tab_biblio, tab_manual = st.tabs([
    "📊 Panorama & Fluxos", 
    "⚖️ Legislação & IA Jurídica", 
    "📖 Dicionários Técnicos",
    "📚 Biblioteca Virtual",
    "📘 Manual da Jornada"
])

# ==============================================================================
# ABA 1: PANORAMA (FUNDAMENTOS)
# ==============================================================================
with tab_panorama:
    st.markdown("### 🔄 O Fluxo da Inclusão (Omnisfera 2025)")
    st.caption("Visualização do ecossistema escolar atualizado com os novos decretos.")
    
    # Diagrama de Processo
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
# ABA 2: LEGISLAÇÃO & IA (O DIFERENCIAL)
# ==============================================================================
with tab_legal:
    c_info, c_ai = st.columns([1.5, 1])
    
    with c_info:
        st.markdown("### 📜 Legislação em Foco (2025)")
        st.markdown("Análise detalhada dos impactos dos novos Decretos Federais.")
        
        with st.expander("💰 Decreto 12.686/2025: O Financiamento (Duplo Fundo)", expanded=True):
            st.markdown("""
            **Mudança Estrutural:**
            Este decreto altera a contabilidade do FUNDEB. Antes, havia dúvidas sobre o repasse.
            
            1.  **Dupla Matrícula:** O aluno público-alvo da educação especial é contabilizado **duas vezes**:
                * Uma vez pela matrícula na classe comum.
                * Uma segunda vez pela matrícula no AEE (Atendimento Educacional Especializado).
            2.  **Destinação:** A verba extra deve ser usada para Sala de Recursos, materiais adaptados e contratação de profissionais de apoio.
            """)
            
        with st.expander("🚫 Decreto 12.773/2025: Garantia de Acesso (Escolas Privadas)"):
            st.markdown("""
            **Tolerância Zero para Barreiras:**
            Este decreto fecha o cerco contra a recusa de matrícula.
            
            1.  **Taxas Extras:** É **ilegal** cobrar valor adicional na mensalidade para custear monitor, mediador ou material adaptado. O custo deve ser diluído na planilha geral da escola (Princípio da Solidariedade).
            2.  **Porta de Entrada:** A escola não pode exigir laudo médico para efetivar a matrícula. A avaliação pedagógica (Estudo de Caso) é soberana para iniciar o atendimento.
            """)

        st.markdown("#### ⏳ Marcos Históricos")
        st.caption("1988 (Constituição) • 1994 (Salamanca) • 2008 (PNEEPEI) • 2015 (LBI)")

    # --- AQUI ENTRA A IA JURÍDICA ---
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
        
        # Interface de Chat Simulada (Pronta para conectar no seu Backend)
        user_question = st.text_input("Digite sua dúvida jurídica aqui:", placeholder="Ex: A escola pode exigir laudo para matricular?")
        
        if user_question:
            with st.spinner("Analisando Decretos 12.686 e 12.773..."):
                time.sleep(1.5) # Simulação de processamento
                
                # Resposta Simulada (Aqui você conectaria sua função da OpenAI)
                st.markdown(f"""
                <div style="background:white; padding:15px; border-radius:10px; border-left:4px solid #0d9488; margin-top:10px; box-shadow:0 4px 10px rgba(0,0,0,0.05);">
                    <strong>Resposta da IA:</strong><br>
                    Com base no <strong>Decreto 12.773/2025</strong>, a exigência de laudo médico como condição prévia para matrícula é considerada uma barreira ilegal. 
                    <br><br>
                    A escola deve realizar o <strong>Acolhimento</strong> e iniciar um <strong>Estudo de Caso</strong> pedagógico. O laudo é um documento complementar de saúde, mas não pode impedir o acesso à educação.
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="margin-top:20px; font-size:0.85rem; color:#94a3b8;">
                Try asking:<br>
                <em>- "Como funciona o duplo fundo?"</em><br>
                <em>- "Quem paga o profissional de apoio?"</em>
            </div>
            """, unsafe_allow_html=True)

# ==============================================================================
# ABA 3: DICIONÁRIOS (TÉCNICO + LINGUAGEM)
# ==============================================================================
with tab_glossario:
    st.markdown("### 📖 Dicionários da Inclusão")
    
    sub_tab1, sub_tab2 = st.tabs(["🗣️ Guia Anticapacitista", "📚 Glossário Técnico A-Z"])
    
    with sub_tab1:
        st.markdown("#### O poder da linguagem")
        st.caption("Termos para adotar e termos para abolir.")
        
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**✅ PREFIRA (Termos Corretos)**")
            termos_bons = [
                ("Pessoa com Deficiência (PcD)", "Termo legal da LBI. Marca a deficiência como atributo, não identidade total."),
                ("Neurodivergente", "Funcionamento cerebral atípico (TEA, TDAH), sem conotação de doença."),
                ("Estudante Público-Alvo", "Foca no direito ao serviço, não no estigma.")
            ]
            for t, d in termos_bons:
                st.markdown(f"<div class='term-good'><strong>{t}</strong><br><small>{d}</small></div>", unsafe_allow_html=True)
        
        with c2:
            st.markdown("**🚫 EVITE (Termos Ofensivos)**")
            termos_ruins = [
                ("Portador de Deficiência", "Deficiência não se porta. É intrínseca."),
                ("Aluno de Inclusão", "Segrega. Todos são alunos."),
                ("Criança Especial", "Infantiliza. Use o nome da criança."),
                ("Surdo-Mudo", "Erro técnico. Surdos têm voz.")
            ]
            for t, d in termos_ruins:
                st.markdown(f"<div class='term-bad'><strong style='text-decoration:line-through;'>{t}</strong><br><small>{d}</small></div>", unsafe_allow_html=True)

    with sub_tab2:
        st.markdown("#### Conceitos Técnicos")
        busca = st.text_input("🔎 Filtrar glossário:", placeholder="Ex: Justiça Curricular...")
        
        # Glossário Completo
        glossario = [
            {"t": "AEE", "d": "Atendimento Educacional Especializado. Suplementar/Complementar, não substitutivo."},
            {"t": "Alteridade", "d": "Reconhecer o 'outro' como legítimo em sua diferença."},
            {"t": "Capacitismo", "d": "Preconceito que pressupõe a incapacidade da PcD."},
            {"t": "Cultura do Pertencimento", "d": "Ambiente onde o aluno é parte ativa da comunidade."},
            {"t": "Estudo de Caso", "d": "Metodologia pedagógica que substitui o laudo como porta de entrada (2025)."},
            {"t": "Justiça Curricular", "d": "Currículo que representa todos os grupos e adapta meios para equidade."},
            {"t": "Outragem", "d": "Empatia técnica. Sentir o mundo do outro mantendo a postura profissional."},
            {"t": "PEI", "d": "Plano Educacional Individualizado. Documento vivo de adaptação curricular."},
            {"t": "Tecnologia Assistiva", "d": "Recursos que ampliam a funcionalidade (pranchas, softwares)."},
            {"t": "Vieses Inconscientes", "d": "Associações automáticas que reproduzem preconceitos."}
        ]
        
        filtro = [g for g in glossario if busca.lower() in g['t'].lower() or busca.lower() in g['d'].lower()]
        
        for item in filtro:
            st.markdown(f"""
            <div class="glossary-item">
                <div style="color:#0F52BA; font-weight:700;">{item['t']}</div>
                <div style="color:#475569; font-size:0.9rem;">{item['d']}</div>
            </div>""", unsafe_allow_html=True)

# ==============================================================================
# ABA 4: BIBLIOTECA
# ==============================================================================
with tab_biblio:
    st.markdown("### 📚 Biblioteca Virtual")
    st.markdown("Referências expandidas (Clique para ver detalhes).")

    def render_livro(titulo, autor, resumo, link=None):
        with st.expander(f"📕 {titulo}"):
            st.markdown(f"**Autor:** {autor}")
            st.markdown(f"**Resumo:** {resumo}")
            if link: st.markdown(f"[🔗 Acessar Documento]({link})")

    render_livro("Lei Brasileira de Inclusão (13.146/2015)", "Brasil", "Estatuto da PcD. Define barreira e criminaliza discriminação.", "http://www.planalto.gov.br")
    render_livro("Os Benefícios da Educação Inclusiva (2016)", "Instituto Alana", "Estudos comprovam ganhos para todos os alunos.", "https://alana.org.br")
    render_livro("Declaração de Salamanca (1994)", "UNESCO", "Marco mundial da escola inclusiva.", "https://unesdoc.unesco.org")
    render_livro("Inclusão Escolar: O que é? Como fazer?", "Mantoan (2003)", "Diferencia integração de inclusão.", None)
    render_livro("Capacitismo: o que é, onde vive?", "Sidney Andrade", "Entendendo o preconceito estrutural.", None)

# ==============================================================================
# ABA 5: MANUAL DA JORNADA (TEXTO DO USUÁRIO)
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
            <li>Mapeie as barreiras de aprendizagem.</li>
            <li>Use a IA para estruturar metas.</li>
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
        <p>Aqui entra a execução técnica. Na página <strong>Plano de Ação / PAEE</strong>, organizamos o Atendimento Especializado.</p>
        <p><strong>Ação na Plataforma:</strong></p>
        <ul>
            <li>Defina a frequência e o foco dos atendimentos.</li>
            <li>Estabeleça a ponte com o professor regente.</li>
            <li>Organize a Tecnologia Assistiva.</li>
        </ul>
        <div class="key-concept">
            💡 <strong>Conceito Chave:</strong> O AEE é o laboratório onde se testam as ferramentas que permitirão ao aluno acessar o currículo comum.
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

    # PASSO 4 e 5 (Agrupados visualmente)
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
