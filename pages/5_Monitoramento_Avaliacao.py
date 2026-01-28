import streamlit as st
import graphviz

# ==============================================================================
# 1. SETUP & CSS (VISUAL "CLEAN PRO")
# ==============================================================================
st.set_page_config(page_title="Central de Conhecimento", page_icon="🧠", layout="wide")

st.markdown("""
<style>
    /* Importação de Fontes */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; color: #1e293b; }
    .stApp { background-color: #f8fafc; }

    /* Cards Executivos */
    .exec-card {
        background: white;
        border-radius: 12px;
        padding: 25px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        border-left: 5px solid #0F52BA;
        height: 100%;
        transition: transform 0.2s;
    }
    .exec-card:hover { transform: translateY(-3px); box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1); }
    .card-title { font-size: 1.1rem; font-weight: 800; color: #0f172a; margin-bottom: 10px; text-transform: uppercase; letter-spacing: 0.5px; }
    .card-body { font-size: 0.95rem; color: #475569; line-height: 1.6; }

    /* Bibliografia Estilo "Fichamento" */
    .biblio-item {
        background: white; border: 1px solid #e2e8f0; border-radius: 8px;
        padding: 20px; margin-bottom: 15px; border-left: 4px solid #64748b;
    }
    
    /* Manual - Steps */
    .step-box {
        background: #f1f5f9; padding: 15px; border-radius: 8px; margin-bottom: 10px;
        border-left: 4px solid #0F52BA;
    }

    /* Glossário */
    .term-bad { color: #dc2626; font-weight: bold; text-decoration: line-through; }
    .term-good { color: #16a34a; font-weight: bold; }

    /* Abas */
    .stTabs [data-baseweb="tab-list"] { gap: 20px; border-bottom: 2px solid #e2e8f0; }
    .stTabs [aria-selected="true"] { color: #0F52BA !important; border-bottom-color: #0F52BA !important; }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# 2. HEADER
# ==============================================================================
st.title("🧠 Central de Inteligência Inclusiva")
st.markdown("""
**Base de Conhecimento Omnisfera:** Fundamentos teóricos, diretrizes legais e manual operacional.
<br>
""", unsafe_allow_html=True)

# ==============================================================================
# 3. NAVEGAÇÃO
# ==============================================================================
tab_panorama, tab_legal, tab_biblio, tab_glossario, tab_manual = st.tabs([
    "📊 Panorama & Fundamentos", 
    "⚖️ Ecossistema Legal", 
    "📚 Biblioteca de Referência",
    "📖 Glossário Técnico",
    "⚙️ Manual da Omnisfera"
])

# ==============================================================================
# ABA 1: PANORAMA (RESUMO EXECUTIVO)
# ==============================================================================
with tab_panorama:
    st.markdown("### Os 3 Pilares da Educação Inclusiva")
    st.markdown("Síntese dos fundamentos baseados na metodologia Ritmos/COC e Legislação 2025.")
    
    c1, c2, c3 = st.columns(3)
    
    with c1:
        st.markdown("""
        <div class="exec-card" style="border-left-color: #0F52BA;">
            <div class="card-title">1. Filosofia ("Outrar-se")</div>
            <div class="card-body">
                A inclusão começa na postura ética.
                <br><br>
                <ul>
                    <li><strong>Conceito:</strong> Capacidade de sentir o mundo do outro sem perder o distanciamento profissional.</li>
                    <li><strong>Meta:</strong> Superar o "capacitismo" (preconceito) e a visão médica da deficiência.</li>
                    <li><strong>Lema:</strong> "Temos direito à diferença quando a igualdade nos descaracteriza."</li>
                </ul>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown("""
        <div class="exec-card" style="border-left-color: #e11d48;">
            <div class="card-title">2. Gestão & Justiça</div>
            <div class="card-body">
                A inclusão se sustenta na estratégia.
                <br><br>
                <ul>
                    <li><strong>Justiça Curricular:</strong> Adaptar o currículo para que todos aprendam, não apenas "passem".</li>
                    <li><strong>PEI vs. PAEE:</strong> Clareza entre o papel da sala de aula (PEI) e da sala de recursos (PAEE).</li>
                    <li><strong>Liderança:</strong> O gestor garante os recursos e a cultura escolar.</li>
                </ul>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with c3:
        st.markdown("""
        <div class="exec-card" style="border-left-color: #059669;">
            <div class="card-title">3. Prática Pedagógica</div>
            <div class="card-body">
                A inclusão acontece na sala de aula.
                <br><br>
                <ul>
                    <li><strong>Desenho Universal:</strong> Planejar para todos, reduzindo a necessidade de adaptações.</li>
                    <li><strong>Flexibilização:</strong> Ajustar tempo, material e avaliação (não o conteúdo essencial).</li>
                    <li><strong>Equipe:</strong> O Professor Regente lidera; AT e AP dão suporte.</li>
                </ul>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.divider()
    
    st.markdown("### 🔄 O Fluxo da Inclusão (Omnisfera)")
    st.caption("Como transformamos dados em permanência e sucesso escolar.")
    
    # Diagrama de Processo (Visualização Limpa com Try-Except para evitar erros de ambiente)
    try:
        fluxo = graphviz.Digraph()
        fluxo.attr(rankdir='LR', bgcolor='transparent', margin='0.1')
        fluxo.attr('node', shape='box', style='rounded,filled', fontname='Inter', fontsize='10')
        
        fluxo.node('A', '1. Acolhimento\n(Matrícula Sem Barreira)', fillcolor='#cbd5e1')
        fluxo.node('B', '2. Estudo de Caso\n(Olhar Pedagógico)', fillcolor='#bfdbfe')
        fluxo.node('C', '3. PEI / PAEE\n(Planejamento)', fillcolor='#0F52BA', fontcolor='white')
        fluxo.node('D', '4. Prática\n(Sala de Aula + AEE)', fillcolor='#86efac')
        fluxo.node('E', '5. Reavaliação\n(Processo Vivo)', fillcolor='#fcd34d')
        
        fluxo.edge('A', 'B')
        fluxo.edge('B', 'C')
        fluxo.edge('C', 'D')
        fluxo.edge('D', 'E')
        fluxo.edge('E', 'C', label=' Ajustes')
        
        st.graphviz_chart(fluxo, use_container_width=True)
    except Exception as e:
        st.error(f"Erro ao renderizar gráfico: {e}")

# ==============================================================================
# ABA 2: LEGAL (ECOSSISTEMA)
# ==============================================================================
with tab_legal:
    st.header("⚖️ Ecossistema Legal")
    
    c_law1, c_law2 = st.columns([1, 2])
    
    with c_law1:
        st.info("""
        **Decreto 12.686 (2025)**
        
        Reestrutura o financiamento do AEE (Duplo Fundo). Garante que a escola receba verba extra para cada aluno público-alvo da educação especial matriculado.
        """)
        
        st.warning("""
        **Decreto 12.773 (2025)**
        
        Endurece regras contra a recusa de matrícula. Torna explícito que escolas privadas não podem cobrar taxas extras por acessibilidade ou mediador.
        """)

    with c_law2:
        st.markdown("#### Timeline dos Avanços")
        # Timeline simplificada em Markdown para carregar rápido e sem erros
        st.markdown("""
        * **1988 - Constituição:** Educação é direito de todos (Art. 205).
        * **2008 - PNEEPEI:** Política Nacional que foca na escola comum.
        * **2015 - LBI (Lei 13.146):** Estatuto da Pessoa com Deficiência. Crime de discriminação.
        * **2024 - PNEE:** Política Nacional de Equidade (foco em interseccionalidade).
        * **2025 - Novos Decretos:** Foco em financiamento e garantia de matrícula.
        """)

# ==============================================================================
# ABA 3: BIBLIOTECA (REFERÊNCIA)
# ==============================================================================
with tab_biblio:
    st.header("📚 Referências Essenciais")
    st.markdown("Resumos executivos das obras que fundamentam a prática da Omnisfera.")

    obras = [
        {
            "titulo": "Inclusão Escolar: O que é? Por quê? Como fazer?",
            "autor": "Maria Teresa Eglér Mantoan",
            "tipo": "Filosofia",
            "resumo": "Obra seminal que diferencia 'integração' (aluno se adapta) de 'inclusão' (escola muda). Defende que não existe aluno ineducável e que a diferenciação enriquece a todos."
        },
        {
            "titulo": "Declaração de Salamanca (1994)",
            "autor": "UNESCO",
            "tipo": "Marco Legal",
            "resumo": "Estabelece que as escolas regulares com orientação inclusiva são os meios mais eficazes de combater atitudes discriminatórias e construir uma sociedade inclusiva."
        },
        {
            "titulo": "Lei Brasileira de Inclusão (2015)",
            "autor": "Legislação Federal",
            "tipo": "Direito",
            "resumo": "Define deficiência não como doença, mas como interação com barreiras. Criminaliza a discriminação e obriga a eliminação de barreiras (urbanísticas, comunicacionais, atitudinais)."
        },
        {
            "titulo": "Os Benefícios da Educação Inclusiva",
            "autor": "Instituto Alana / Harvard",
            "tipo": "Evidência",
            "resumo": "Estudos comprovam que alunos sem deficiência em salas inclusivas desenvolvem melhores habilidades socioemocionais e não têm prejuízo acadêmico."
        }
    ]

    for obra in obras:
        cor_tag = "#0F52BA" if obra['tipo'] == "Filosofia" else ("#e11d48" if obra['tipo'] == "Direito" else "#059669")
        st.markdown(f"""
        <div class="biblio-item">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <span style="font-weight:800; font-size:1.1rem; color:#1e293b;">{obra['titulo']}</span>
                <span style="background:{cor_tag}; color:white; padding:4px 10px; border-radius:12px; font-size:0.75rem; font-weight:bold;">{obra['tipo']}</span>
            </div>
            <div style="color:#64748b; font-style:italic; font-size:0.9rem; margin-bottom:10px;">{obra['autor']}</div>
            <div style="color:#334155; line-height:1.5;">{obra['resumo']}</div>
        </div>
        """, unsafe_allow_html=True)

# ==============================================================================
# ABA 4: GLOSSÁRIO (VISUAL)
# ==============================================================================
with tab_glossario:
    st.header("📖 Dicionário Anticapacitista")
    st.markdown("A linguagem cria cultura. Use este guia para alinhar a comunicação da escola.")

    col_g1, col_g2 = st.columns(2)
    
    with col_g1:
        st.subheader("🚫 Abolir (Termos Ofensivos)")
        st.markdown("""
        * <span class="term-bad">Portador de Deficiência</span> → Deficiência não se porta, se tem.
        * <span class="term-bad">Criança Especial</span> → Todos são especiais. Use o nome ou PcD.
        * <span class="term-bad">Aluno de Inclusão</span> → Estigmatiza. Use "Estudante com deficiência".
        * <span class="term-bad">Surdo-mudo</span> → Incorreto. Surdos têm voz, só não ouvem.
        * <span class="term-bad">Atrasado / Lento</span> → Desrespeitoso. Use "Ritmo próprio".
        """, unsafe_allow_html=True)

    with col_g2:
        st.subheader("✅ Adotar (Termos Técnicos)")
        st.markdown("""
        * <span class="term-good">Pessoa com Deficiência (PcD)</span> → Termo legal correto (LBI).
        * <span class="term-good">Barreira</span> → O que impede a participação (Física ou Atitudinal).
        * <span class="term-good">Estudo de Caso</span> → Avaliação pedagógica que precede o PEI.
        * <span class="term-good">Neurodivergente</span> → Cérebro que funciona de forma atípica (TEA, TDAH).
        * <span class="term-good">Público-Alvo da Ed. Especial (PAEE)</span> → Termo técnico oficial.
        """, unsafe_allow_html=True)

# ==============================================================================
# ABA 5: MANUAL DA OMNISFERA
# ==============================================================================
with tab_manual:
    st.header("⚙️ Manual de Uso do Sistema")
    st.markdown("Guia rápido para o educador navegar nos módulos da plataforma.")

    # Accordions passo a passo
    with st.expander("1️⃣ Módulo PEI 360º (O Coração do Sistema)", expanded=True):
        st.markdown("""
        Este é o módulo principal para o Professor Regente.
        1.  **Aba Estudante:** Preencha os dados básicos e o Hiperfoco (essencial para a IA).
        2.  **Abas Acadêmico/Social/Motor:** Use as rubricas (sliders) para mapear o nível atual.
        3.  **Aba Consultoria IA:** Clique em "Gerar Análise". A IA lerá os dados e criará o PEI Técnico.
        4.  **Aba Jornada:** Cria uma missão gamificada para o aluno baseada no PEI.
        """)

    with st.expander("2️⃣ Módulo PAEE & Recursos"):
        st.markdown("""
        Focado na Sala de Recursos e Especialistas.
        1.  **Diagnóstico de Barreiras:** Identifique o que impede o acesso (físico ou comunicação).
        2.  **Plano de Habilidades:** Defina metas específicas para o AEE (ex: uso de tesoura, Libras).
        3.  **Carta de Articulação:** Gere um documento automático para alinhar com o professor da sala.
        """)

    with st.expander("3️⃣ Módulo Monitoramento"):
        st.markdown("""
        Para acompanhamento bimestral ou semestral.
        1.  Selecione o aluno.
        2.  Compare as metas do PEI com o Diário de Bordo.
        3.  Gere o relatório de evolução para a família.
        """)

# Rodapé
st.markdown("---")
st.caption("Central de Conhecimento Omnisfera • Atualizado 2026")
