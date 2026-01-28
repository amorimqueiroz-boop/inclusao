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
        margin-bottom: 20px;
    }
    .content-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 12px 20px -3px rgba(0, 0, 0, 0.1);
        border-color: #0F52BA;
    }
    
    /* Destaques do Flowchart */
    .flow-container {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 20px;
        padding: 30px;
        margin-bottom: 40px;
        box-shadow: 0 10px 30px -10px rgba(0, 0, 0, 0.1);
        text-align: center;
    }

    /* Bibliografia Estilo "Estante" */
    .biblio-card {
        border-left: 5px solid #0F52BA;
        background: white;
        padding: 20px;
        border-radius: 0 12px 12px 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        margin-bottom: 15px;
    }
    .biblio-tag {
        font-size: 0.7rem; text-transform: uppercase; font-weight: bold; 
        padding: 3px 8px; border-radius: 10px; color: white;
    }

    /* Glossário */
    .term-bad { color: #dc2626; font-weight: bold; text-decoration: line-through; }
    .term-good { color: #16a34a; font-weight: bold; }

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
    "📊 Panorama & Fluxos", 
    "⚖️ Legislação 2025", 
    "📚 Biblioteca Completa",
    "📖 Dicionário Técnico",
    "⚙️ Manual do Sistema"
])

# ==============================================================================
# ABA 1: PANORAMA & FLUXOS (REORGANIZADO)
# ==============================================================================
with tab1:
    # --- PARTE 1: O FLUXO (EM DESTAQUE TOTAL) ---
    st.markdown("### 🔄 O Fluxo da Inclusão (Omnisfera 2025)")
    st.caption("O novo processo de entrada e permanência, atualizado com a substituição do laudo pelo Estudo de Caso.")
    
    st.markdown('<div class="flow-container">', unsafe_allow_html=True)
    
    try:
        fluxo = graphviz.Digraph()
        fluxo.attr(rankdir='LR', bgcolor='transparent', margin='0')
        fluxo.attr('node', shape='box', style='rounded,filled', fontname='Inter', fontsize='11', height='0.6')
        
        # Nós com cores estratégicas
        fluxo.node('A', '1. ACOLHIMENTO\n(Matrícula Garantida)', fillcolor='#dbeafe', color='#3b82f6')
        fluxo.node('B', '2. ESTUDO DE CASO\n(Avaliação Pedagógica)', fillcolor='#0F52BA', fontcolor='white', color='#0F52BA')
        fluxo.node('C', '3. IDENTIFICAÇÃO\n(Público-Alvo)', fillcolor='#dcfce7', color='#22c55e')
        fluxo.node('D', '4. PLANEJAMENTO\n(PEI + PAEE)', fillcolor='#f3e8ff', color='#a855f7')
        fluxo.node('E', '5. AEE\n(Sala de Recursos)', fillcolor='#ffedd5', color='#f97316')
        
        # Conexões
        fluxo.edge('A', 'B', label=' Equipe Escolar')
        fluxo.edge('B', 'C', label=' Substitui Laudo')
        fluxo.edge('C', 'D', label=' Adaptação')
        fluxo.edge('D', 'E', label=' Duplo Fundo')
        fluxo.edge('E', 'D', label=' Retroalimentação', style='dashed')
        
        st.graphviz_chart(fluxo, use_container_width=True)
    except:
        st.error("Visualizador gráfico indisponível no momento.")
        
    st.markdown('</div>', unsafe_allow_html=True)

    # --- PARTE 2: FUNDAMENTOS E PILARES (ABAIXO DO FLUXO) ---
    st.markdown("---")
    st.markdown("### 🏛️ Fundamentos da Prática")
    
    c_intro, c_conc = st.columns(2)
    
    with c_intro:
        st.markdown("""
        <div class="content-card" style="border-left: 5px solid #0F52BA;">
            <div class="card-header">
                <span class="card-icon">🤝</span>
                <span class="card-title">Filosofia: "Outrar-se"</span>
            </div>
            <p style="font-size:0.95rem; color:#475569;">
                Baseado em <em>Fernando Pessoa/Bernardo Soares</em>. É a capacidade de sentir o mundo do outro mantendo o 
                distanciamento profissional. <br><br>
                <em>"Temos direito à igualdade quando a diferença nos inferioriza, e direito à diferença quando a igualdade nos descaracteriza."</em> (Boaventura de Sousa Santos)
            </p>
        </div>
        """, unsafe_allow_html=True)

    with c_conc:
        st.markdown("""
        <div class="content-card" style="border-left: 5px solid #a855f7;">
            <div class="card-header">
                <span class="card-icon">⚖️</span>
                <span class="card-title">Justiça Curricular</span>
            </div>
            <p style="font-size:0.95rem; color:#475569;">
                Conceito de <em>Jurjo Torres Santomé</em>. O currículo não pode ser uma barreira. <br><br>
                O PEI é a ferramenta que materializa a justiça curricular, garantindo que o aluno tenha acesso ao conhecimento de forma adaptada, e não apenas socialize.
            </p>
        </div>
        """, unsafe_allow_html=True)

# ==============================================================================
# ABA 2: LEGISLAÇÃO (ATUALIZADA)
# ==============================================================================
with tab2:
    st.markdown("### 📜 O Novo Marco Regulatório (2025)")
    st.markdown("Impactos imediatos na gestão escolar com os novos decretos.")

    c1, c2 = st.columns(2)
    
    with c1:
        st.markdown("""
        <div class="content-card" style="border-left: 5px solid #22c55e;">
            <div class="card-header">
                <span class="card-icon">💰</span>
                <span class="card-title">Decreto 12.686/2025</span>
            </div>
            <p><strong>Foco: Financiamento (Duplo Fundo)</strong></p>
            <ul>
                <li>O aluno da Educação Especial conta <strong>duas vezes</strong> no repasse do FUNDEB (Matrícula + AEE).</li>
                <li>Garante recursos específicos para Salas Multifuncionais e profissionais de apoio.</li>
            </ul>
            <span class="tag tag-green">Gestão Financeira</span>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown("""
        <div class="content-card" style="border-left: 5px solid #ef4444;">
            <div class="card-header">
                <span class="card-icon">🚫</span>
                <span class="card-title">Decreto 12.773/2025</span>
            </div>
            <p><strong>Foco: Garantia de Matrícula</strong></p>
            <ul>
                <li>Proíbe cobrança de taxas extras em escolas privadas.</li>
                <li>Criminaliza a recusa de matrícula sob alegação de deficiência.</li>
                <li>Torna o "Estudo de Caso" o instrumento oficial de entrada.</li>
            </ul>
            <span class="tag tag-red">Proteção Legal</span>
        </div>
        """, unsafe_allow_html=True)

# ==============================================================================
# ABA 3: BIBLIOTECA COMPLETA (EXPANDIDA)
# ==============================================================================
with tab3:
    st.markdown("### 📚 Acervo Bibliográfico & Referências")
    st.markdown("Compilação de todas as obras, leis e artigos fundamentais da Omnisfera.")

    # Lista Expandida baseada nos uploads (NotebookLM, PDFs, Textos)
    bibliografia = [
        {
            "titulo": "Inclusão Escolar: O que é? Por quê? Como fazer?",
            "autor": "Maria Teresa Eglér Mantoan (2003)",
            "tipo": "Filosofia",
            "cor": "#0F52BA",
            "resumo": "Obra seminal. Diferencia 'integração' (o aluno muda para caber na escola) de 'inclusão' (a escola muda para acolher o aluno). Defende a escola comum para todos."
        },
        {
            "titulo": "Lei Brasileira de Inclusão (LBI)",
            "autor": "Lei Federal nº 13.146/2015",
            "tipo": "Legislação",
            "cor": "#e11d48",
            "resumo": "Estatuto da Pessoa com Deficiência. Define deficiência como interação entre impedimentos e barreiras. Criminaliza discriminação e define o direito ao Acompanhante."
        },
        {
            "titulo": "Declaração de Salamanca",
            "autor": "UNESCO (1994)",
            "tipo": "Marco Mundial",
            "cor": "#059669",
            "resumo": "Documento fundador da inclusão global. Estabelece que escolas regulares com orientação inclusiva são o meio mais eficaz de combater o preconceito."
        },
        {
            "titulo": "Os Benefícios da Educação Inclusiva",
            "autor": "Instituto Alana / ABT Associates (2016)",
            "tipo": "Evidência Científica",
            "cor": "#7c3aed",
            "resumo": "Revisão de 89 estudos que comprova: alunos sem deficiência em salas inclusivas desenvolvem melhores habilidades sociais e não têm prejuízo acadêmico."
        },
        {
            "titulo": "Política Nacional de Educação Especial (PNEEPEI)",
            "autor": "MEC (2008)",
            "tipo": "Política Pública",
            "cor": "#e11d48",
            "resumo": "Diretriz que rompeu com o modelo de escolas especiais segregadas, focando o financiamento público na escola comum."
        },
        {
            "titulo": "Currículo e Justiça Curricular",
            "autor": "Jurjo Torres Santomé (2013)",
            "tipo": "Pedagogia",
            "cor": "#0F52BA",
            "resumo": "Conceito de que um currículo justo deve representar todos os grupos sociais e culturais, evitando a exclusão pelo conteúdo."
        },
        {
            "titulo": "Convenção sobre os Direitos das Pessoas com Deficiência",
            "autor": "ONU (2006) / Brasil (2008)",
            "tipo": "Direitos Humanos",
            "cor": "#059669",
            "resumo": "Primeiro tratado de direitos humanos do século XXI, incorporado à Constituição Brasileira com status de Emenda Constitucional."
        },
        {
            "titulo": "Decretos da Nova Política (12.686 e 12.773)",
            "autor": "Governo Federal (2025)",
            "tipo": "Legislação Atual",
            "cor": "#e11d48",
            "resumo": "Atualização do PNEEPEI, focando na garantia de financiamento, profissional de apoio e proibição de barreiras na matrícula privada."
        }
    ]

    # Renderização em Grid (2 colunas)
    col_a, col_b = st.columns(2)
    
    for i, item in enumerate(bibliografia):
        # Distribui entre as colunas
        with (col_a if i % 2 == 0 else col_b):
            st.markdown(f"""
            <div class="biblio-card" style="border-left-color: {item['cor']};">
                <div style="display:flex; justify-content:space-between; align-items:start;">
                    <div style="font-weight:700; font-size:1.05rem; color:#1e293b;">{item['titulo']}</div>
                    <span class="biblio-tag" style="background-color:{item['cor']};">{item['tipo']}</span>
                </div>
                <div style="font-size:0.85rem; color:#64748b; margin:5px 0 10px 0; font-style:italic;">{item['autor']}</div>
                <div style="font-size:0.9rem; color:#334155; line-height:1.5;">{item['resumo']}</div>
            </div>
            """, unsafe_allow_html=True)

# ==============================================================================
# ABA 4: GLOSSÁRIO TÉCNICO
# ==============================================================================
with tab4:
    st.markdown("### 📖 Dicionário Anticapacitista")
    st.markdown("A linguagem cria cultura. Guia de alinhamento para a equipe.")

    c1, c2 = st.columns(2)
    
    with c1:
        st.markdown("#### ✅ Termos Corretos")
        termos_bons = [
            ("Pessoa com Deficiência (PcD)", "Termo legal (LBI). Marca que a deficiência é um atributo, não a pessoa inteira."),
            ("Barreira", "Qualquer entrave (físico ou atitudinal) que limite a participação."),
            ("Estudo de Caso", "Avaliação pedagógica que substitui a exigência de laudo médico inicial."),
            ("Neurodivergente", "Funcionamento cerebral atípico (TEA, TDAH), sem conotação de doença."),
            ("Cultura do Pertencimento", "Ambiente onde o aluno é parte ativa, não apenas 'visitante'.")
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
            ("Portador de Deficiência", "Ninguém 'porta' deficiência. Ela é intrínseca à condição."),
            ("Aluno de Inclusão", "Estigmatizante. Use 'Público-alvo da Ed. Especial'."),
            ("Criança Especial", "Eufemismo que infantiliza. Use o nome da criança."),
            ("Surdo-Mudo", "Incorreto. A surdez não implica mudez."),
            ("Atrasado / Lento", "Preconceituoso. Use 'Ritmo próprio de aprendizagem'.")
        ]
        for t, d in termos_ruins:
            st.markdown(f"""
            <div style="background:#fef2f2; border-left:4px solid #dc2626; padding:12px; margin-bottom:10px; border-radius:4px;">
                <strong style="color:#991b1b; text-decoration: line-through;">{t}</strong><br>
                <small style="color:#334155;">{d}</small>
            </div>
            """, unsafe_allow_html=True)

# ==============================================================================
# ABA 5: MANUAL DO SISTEMA
# ==============================================================================
with tab5:
    st.markdown("### ⚙️ Manual de Uso Omnisfera")
    st.info("Passo a passo para operacionalizar a inclusão na plataforma.")

    step1, step2, step3 = st.columns(3)
    
    with step1:
        st.markdown("""
        <div class="content-card" style="background:#f8fafc;">
            <h4>1️⃣ Módulo PEI 360º</h4>
            <p><strong>Para quem:</strong> Professor Regente.</p>
            <ol style="font-size:0.9rem; padding-left:15px;">
                <li>Cadastre os dados na aba <strong>Estudante</strong> (Hiperfoco é vital!).</li>
                <li>Mapeie habilidades nas abas Acadêmico/Social.</li>
                <li>Gere o PEI Técnico na <strong>Consultoria IA</strong>.</li>
                <li>Crie a missão na aba <strong>Jornada</strong>.</li>
            </ol>
        </div>
        """, unsafe_allow_html=True)

    with step2:
        st.markdown("""
        <div class="content-card" style="background:#f8fafc;">
            <h4>2️⃣ Módulo PAEE</h4>
            <p><strong>Para quem:</strong> Sala de Recursos (AEE).</p>
            <ol style="font-size:0.9rem; padding-left:15px;">
                <li>Foque no <strong>Diagnóstico de Barreiras</strong>.</li>
                <li>Defina metas de Habilidades (não conteúdo).</li>
                <li>Gere a <strong>Carta de Articulação</strong> para alinhar com a sala comum.</li>
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
                <li>Compare as metas do PEI com o Diário.</li>
                <li>Verifique se o PEI está sendo um "documento vivo".</li>
            </ol>
        </div>
        """, unsafe_allow_html=True)

# Rodapé
st.markdown("---")
st.caption("Central de Conhecimento Omnisfera • Baseada na Legislação Vigente 2026")
