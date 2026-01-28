import streamlit as st
import graphviz

# ==============================================================================
# 1. SETUP & DESIGN SYSTEM (VISUAL "PREMIUM GLASS")
# ==============================================================================
st.set_page_config(page_title="Central de Conhecimento", page_icon="🧠", layout="wide")

st.markdown("""
<style>
    /* Fontes e Base */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
    
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; color: #1e293b; }
    .stApp { background-color: #f8fafc; }

    /* Hero Section Gradient */
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

    /* Cards de Conteúdo (Glass Effect) */
    .content-card {
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 16px;
        padding: 24px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        transition: transform 0.2s, box-shadow 0.2s;
        height: 100%;
    }
    .content-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 12px 20px -3px rgba(0, 0, 0, 0.1);
        border-color: #0F52BA;
    }
    
    /* Títulos e Destaques */
    .card-header {
        display: flex; align-items: center; gap: 10px; margin-bottom: 15px;
        border-bottom: 1px solid #f1f5f9; padding-bottom: 10px;
    }
    .card-icon { font-size: 1.5rem; background: #eff6ff; padding: 8px; border-radius: 8px; }
    .card-title { font-weight: 700; color: #0f172a; font-size: 1.1rem; }
    
    /* Tags e Pílulas */
    .tag {
        display: inline-block; padding: 4px 10px; border-radius: 20px;
        font-size: 0.75rem; font-weight: 600; text-transform: uppercase;
        margin-right: 5px;
    }
    .tag-blue { background: #dbeafe; color: #1e40af; }
    .tag-green { background: #dcfce7; color: #166534; }
    .tag-red { background: #fee2e2; color: #991b1b; }
    
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
    <div class="hero-subtitle">Base de conhecimento atualizada: Decretos 2025, Fundamentos Pedagógicos e Manual Operacional.</div>
</div>
""", unsafe_allow_html=True)

# ==============================================================================
# 3. NAVEGAÇÃO ESTRUTURADA
# ==============================================================================
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Fundamentos & Processos", 
    "⚖️ Legislação 2025", 
    "📚 Biblioteca Essencial",
    "📖 Dicionário Técnico",
    "⚙️ Manual do Sistema"
])

# ==============================================================================
# ABA 1: PANORAMA & FLUXOS (Conceitos Chave)
# ==============================================================================
with tab1:
    c_intro, c_flow = st.columns([1, 1.5])
    
    with c_intro:
        st.markdown("### 🏛️ Os Pilares da Prática")
        st.markdown("Conceitos extraídos dos Módulos Ritmos e Diretrizes Nacionais.")
        
        st.markdown("""
        <div class="content-card">
            <div class="card-header">
                <span class="card-icon">🤝</span>
                <span class="card-title">1. Filosofia: "Outrar-se"</span>
            </div>
            <p style="font-size:0.95rem; color:#475569;">
                Conceito central de <em>Fernando Pessoa/Bernardo Soares</em>. É a capacidade de sentir o mundo do outro mantendo o 
                distanciamento profissional. É ter empatia sem confundir papéis. <br>
                <strong>Meta:</strong> Superar o capacitismo (visão da falta).
            </p>
        </div>
        <br>
        <div class="content-card">
            <div class="card-header">
                <span class="card-icon">⚖️</span>
                <span class="card-title">2. Justiça Curricular</span>
            </div>
            <p style="font-size:0.95rem; color:#475569;">
                O currículo não pode ser uma barreira. Justiça curricular é adaptar o ensino para que todos tenham 
                <strong>acesso ao conhecimento</strong>, não apenas presença física. <br>
                <strong>Ferramenta:</strong> O PEI é a materialização dessa justiça.
            </p>
        </div>
        """, unsafe_allow_html=True)

    with c_flow:
        st.markdown("### 🔄 O Novo Fluxo de Entrada (2025)")
        st.caption("Mudança Crítica: O Laudo Médico não é mais a única porta de entrada. O foco é pedagógico.")
        
        # Diagrama Graphviz Otimizado e Bonito
        try:
            fluxo = graphviz.Digraph()
            fluxo.attr(rankdir='LR', bgcolor='transparent', margin='0')
            fluxo.attr('node', shape='box', style='rounded,filled', fontname='Inter', fontsize='11', height='0.6')
            
            # Nós
            fluxo.node('A', '1. Acolhimento\n(Matrícula Garantida)', fillcolor='#dbeafe', color='#3b82f6')
            fluxo.node('B', '2. ESTUDO DE CASO\n(Avaliação Pedagógica)', fillcolor='#0F52BA', fontcolor='white', color='#0F52BA')
            fluxo.node('C', '3. Identificação\n(Público-Alvo)', fillcolor='#dcfce7', color='#22c55e')
            fluxo.node('D', '4. Planejamento\n(PEI + PAEE)', fillcolor='#f3e8ff', color='#a855f7')
            fluxo.node('E', '5. AEE\n(Duplo Fundo)', fillcolor='#ffedd5', color='#f97316')
            
            # Arestas
            fluxo.edge('A', 'B', label=' Equipe Escolar')
            fluxo.edge('B', 'C', label=' Substitui Laudo')
            fluxo.edge('C', 'D')
            fluxo.edge('D', 'E', label=' Financiamento')
            
            st.graphviz_chart(fluxo, use_container_width=True)
            
            st.info("""
            **💡 Nota Técnica:** O **Estudo de Caso** é agora a ferramenta oficial para identificar necessidades. 
            A escola não pode esperar o laudo médico para começar a agir (Decreto 12.773).
            """)
        except Exception:
            st.error("Visualizador de gráficos indisponível.")

# ==============================================================================
# ABA 2: LEGISLAÇÃO (Atualizada 2025)
# ==============================================================================
with tab2:
    st.markdown("### 📜 O Novo Marco Regulatório (2025)")
    st.markdown("Os Decretos 12.686 e 12.773 trouxeram mudanças estruturais no financiamento e na matrícula.")

    c1, c2 = st.columns(2)
    
    with c1:
        st.markdown("""
        <div class="content-card" style="border-left: 5px solid #22c55e;">
            <div class="card-header">
                <span class="card-icon">💰</span>
                <span class="card-title">Decreto 12.686/2025: Financiamento</span>
            </div>
            <p><strong>O que mudou:</strong> Estrutura o "Duplo Fundo" para o FUNDEB.</p>
            <ul>
                <li>O aluno da Educação Especial conta <strong>duas vezes</strong> no repasse de verbas: uma pela matrícula comum e outra pelo AEE.</li>
                <li>Garante recursos para Salas Multifuncionais e contratação de profissionais de apoio.</li>
            </ul>
            <span class="tag tag-green">Vitória Histórica</span>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown("""
        <div class="content-card" style="border-left: 5px solid #ef4444;">
            <div class="card-header">
                <span class="card-icon">🚫</span>
                <span class="card-title">Decreto 12.773/2025: Matrícula</span>
            </div>
            <p><strong>O que mudou:</strong> Criminaliza barreiras na matrícula.</p>
            <ul>
                <li>Proíbe explicitamente a cobrança de <strong>taxas extras</strong> em escolas privadas (para mediadores ou materiais).</li>
                <li>A recusa de matrícula ou a imposição de condições (ex: "só se tiver laudo") é infração grave.</li>
            </ul>
            <span class="tag tag-red">Proteção Legal</span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("#### ⏳ Linha do Tempo Resumida")
    st.markdown("""
    * **1988 (Constituição):** Educação como direito de TODOS.
    * **2008 (PNEEPEI):** Fim da segregação. Foco na Escola Comum.
    * **2015 (LBI - Lei 13.146):** Deficiência = Impedimento + Barreira. Estatuto da PcD.
    * **2025 (Novos Decretos):** Garantia de verba e tolerância zero com a exclusão.
    """)

# ==============================================================================
# ABA 3: BIBLIOTECA (Fichamentos)
# ==============================================================================
with tab3:
    st.markdown("### 📚 Acervo Bibliográfico Omnisfera")
    st.caption("Resumos executivos das obras fundamentais carregadas no sistema.")

    refs = [
        {
            "titulo": "Inclusão Escolar: O que é? Por quê? Como fazer?",
            "autor": "Maria Teresa Eglér Mantoan",
            "tag": "Filosofia",
            "texto": "Obra seminal. Mantoan defende que não existe 'aluno ineducável'. A escola que se adapta ao aluno (Inclusão) é diferente da escola que pede para o aluno se adaptar (Integração). A diferenciação enriquece a todos."
        },
        {
            "titulo": "Declaração de Salamanca (1994)",
            "autor": "UNESCO",
            "tag": "Marco Mundial",
            "texto": "Estabeleceu que escolas regulares com orientação inclusiva são os 'meios mais eficazes' de combater atitudes discriminatórias. Onde tudo começou globalmente."
        },
        {
            "titulo": "Os Benefícios da Educação Inclusiva",
            "autor": "Instituto Alana / Harvard",
            "tag": "Evidências",
            "texto": "Estudos comprovam: Alunos típicos (sem deficiência) em salas inclusivas desenvolvem mais empatia, liderança e resolução de problemas. A inclusão não 'atrasa' a turma, ela a qualifica."
        },
        {
            "titulo": "Cadernos de Educação Especial",
            "autor": "MEC / SEESP",
            "tag": "Prática",
            "texto": "Define as atribuições do AEE: Prover recursos de acessibilidade (Libras, Braille, Tecnologia Assistiva) para eliminar barreiras, não para substituir o ensino da sala comum."
        }
    ]

    col_a, col_b = st.columns(2)
    
    for i, ref in enumerate(refs):
        # Alterna colunas
        with (col_a if i % 2 == 0 else col_b):
            cor = "#0F52BA" if ref['tag'] == "Filosofia" else "#64748b"
            st.markdown(f"""
            <div class="content-card" style="border-top: 4px solid {cor}; margin-bottom: 20px;">
                <div style="font-weight: 700; color: #1e293b; font-size: 1.05rem;">{ref['titulo']}</div>
                <div style="font-size: 0.85rem; color: #64748b; margin-bottom: 10px;">{ref['autor']} • <span style="color:{cor};">{ref['tag']}</span></div>
                <p style="font-size: 0.95rem; color: #334155; line-height: 1.5;">{ref['texto']}</p>
            </div>
            """, unsafe_allow_html=True)

# ==============================================================================
# ABA 4: DICIONÁRIO TÉCNICO (Visual)
# ==============================================================================
with tab4:
    st.markdown("### 📖 Dicionário Anticapacitista")
    st.markdown("Alinhamento conceitual para a equipe escolar. **A linguagem cria cultura.**")

    c1, c2 = st.columns(2)
    
    with c1:
        st.markdown("#### ✅ Termos Corretos")
        termos_bons = [
            ("Pessoa com Deficiência (PcD)", "Termo legal (LBI). Marca que a deficiência é um atributo, não a pessoa inteira."),
            ("Barreira", "Qualquer entrave (físico ou atitudinal) que limite a participação. A deficiência é a interação com a barreira."),
            ("Estudo de Caso", "Metodologia pedagógica de avaliação que substitui a exigência de laudo médico inicial."),
            ("Neurodivergente", "Pessoas com funcionamento cerebral atípico (TEA, TDAH, Dislexia), sem conotação de doença.")
        ]
        for t, d in termos_bons:
            st.markdown(f"""
            <div style="background:#f0fdf4; border-left:4px solid #16a34a; padding:12px; margin-bottom:10px; border-radius:4px;">
                <strong style="color:#166534;">{t}</strong><br>
                <small style="color:#334155;">{d}</small>
            </div>
            """, unsafe_allow_html=True)

    with c2:
        st.markdown("#### 🚫 Termos a Abolir")
        termos_ruins = [
            ("Portador de Deficiência", "Ninguém 'porta' deficiência como se fosse um objeto. Ela é intrínseca."),
            ("Aluno de Inclusão", "Estigmatizante. Todos os alunos são de inclusão. Use 'Público-alvo da Ed. Especial'."),
            ("Criança Especial", "Eufemismo que infantiliza. Use o nome da criança ou 'estudante com deficiência'."),
            ("Surdo-Mudo", "Incorreto. A surdez não implica mudez. Surdos têm voz."),
            ("Doença Mental", "Deficiência não é doença. Doença tem cura/tratamento; deficiência é condição.")
        ]
        for t, d in termos_ruins:
            st.markdown(f"""
            <div style="background:#fef2f2; border-left:4px solid #dc2626; padding:12px; margin-bottom:10px; border-radius:4px;">
                <strong style="color:#991b1b; text-decoration: line-through;">{t}</strong><br>
                <small style="color:#334155;">{d}</small>
            </div>
            """, unsafe_allow_html=True)

# ==============================================================================
# ABA 5: MANUAL DA OMNISFERA (NOVO)
# ==============================================================================
with tab5:
    st.markdown("### ⚙️ Manual de Navegação")
    st.info("Guia rápido para o Professor Regente e a Equipe Técnica utilizarem a plataforma.")

    step1, step2, step3 = st.columns(3)
    
    with step1:
        st.markdown("""
        <div class="content-card" style="background:#f8fafc;">
            <h4>1️⃣ Módulo PEI 360º</h4>
            <p><strong>Para quem:</strong> Professor Regente.</p>
            <ol style="font-size:0.9rem; padding-left:15px;">
                <li>Cadastre os dados básicos na aba <strong>Estudante</strong>.</li>
                <li>Preencha o <strong>Hiperfoco</strong> (Vital para a IA!).</li>
                <li>Use os sliders nas abas Acadêmico/Social para mapear o nível.</li>
                <li>Vá em <strong>Consultoria IA</strong> e gere o PEI Técnico.</li>
            </ol>
        </div>
        """, unsafe_allow_html=True)

    with step2:
        st.markdown("""
        <div class="content-card" style="background:#f8fafc;">
            <h4>2️⃣ Módulo PAEE</h4>
            <p><strong>Para quem:</strong> Sala de Recursos (AEE).</p>
            <ol style="font-size:0.9rem; padding-left:15px;">
                <li>Foque na aba <strong>Diagnóstico de Barreiras</strong>.</li>
                <li>Defina metas de <strong>Habilidades</strong> (não conteúdo).</li>
                <li>Gere a <strong>Carta de Articulação</strong> para alinhar com o professor da sala.</li>
            </ol>
        </div>
        """, unsafe_allow_html=True)

    with step3:
        st.markdown("""
        <div class="content-card" style="background:#f8fafc;">
            <h4>3️⃣ Monitoramento</h4>
            <p><strong>Para quem:</strong> Coordenação.</p>
            <ol style="font-size:0.9rem; padding-left:15px;">
                <li>Acesse bimestralmente.</li>
                <li>Compare as metas do PEI com o Diário de Bordo.</li>
                <li>Gere o gráfico de evolução para mostrar à família.</li>
            </ol>
        </div>
        """, unsafe_allow_html=True)
    
    st.divider()
    st.caption("Dúvidas? Consulte a Coordenação Pedagógica ou a Base Legal na Aba 2.")
