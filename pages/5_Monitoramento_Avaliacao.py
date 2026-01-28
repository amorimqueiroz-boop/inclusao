import streamlit as st
import graphviz

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
        background: linear-gradient(135deg, #0F52BA 0%, #60a5fa 100%);
        padding: 2.5rem; border-radius: 0 0 24px 24px; color: white;
        margin-top: -60px; margin-bottom: 30px;
        box-shadow: 0 10px 25px -5px rgba(15, 82, 186, 0.3);
    }
    .hero-title { font-size: 2.5rem; font-weight: 800; }
    .hero-subtitle { font-size: 1.1rem; opacity: 0.95; font-weight: 300; }

    /* Cards Glassmorphism */
    .glass-card {
        background: white; border: 1px solid #e2e8f0; border-radius: 16px;
        padding: 24px; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        transition: transform 0.2s; height: 100%;
    }
    .glass-card:hover { transform: translateY(-3px); border-color: #0F52BA; box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1); }

    /* Estilo do Dicionário (O Retorno!) */
    .term-box-good {
        background: #f0fdf4; border-left: 5px solid #16a34a; padding: 15px;
        border-radius: 8px; margin-bottom: 10px;
    }
    .term-box-bad {
        background: #fef2f2; border-left: 5px solid #dc2626; padding: 15px;
        border-radius: 8px; margin-bottom: 10px; opacity: 0.9;
    }
    .glossary-item {
        background: white; border-bottom: 1px solid #f1f5f9; padding: 15px;
        transition: background 0.2s;
    }
    .glossary-item:hover { background: #f8fafc; }
    
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
# 2. HERO HEADER
# ==============================================================================
st.markdown("""
<div class="hero-container">
    <div class="hero-title">🧠 Central de Inteligência Inclusiva</div>
    <div class="hero-subtitle">Fundamentos Pedagógicos, Marcos Legais e Ferramentas Práticas.</div>
</div>
""", unsafe_allow_html=True)

# ==============================================================================
# 3. NAVEGAÇÃO
# ==============================================================================
tab_mapa, tab_dict, tab_legal, tab_biblio, tab_manual = st.tabs([
    "🌌 Mapa Mental (Panorama)", 
    "📖 Dicionário & Glossário", 
    "⚖️ Legislação 2025", 
    "📚 Biblioteca Virtual",
    "⚙️ Manual do Sistema"
])

# ==============================================================================
# ABA 1: MAPA MENTAL (ESTILO NOTEBOOK LM)
# ==============================================================================
with tab_mapa:
    st.markdown("### 🌐 Ecossistema da Inclusão")
    st.caption("Visão sistêmica: Como os conceitos se conectam para sustentar o aluno.")
    
    # Mapa Mental com Layout Radial (Tentativa de replicar o visual "aranha")
    try:
        mapa = graphviz.Digraph(engine='dot') # 'dot' é mais estável, mas configurado para parecer radial
        mapa.attr(bgcolor='transparent')
        mapa.attr(rankdir='TB') # Top to Bottom
        mapa.attr('node', shape='ellipse', style='filled', fontname='Inter', fontsize='10', margin='0.2')
        mapa.attr('edge', color='#94a3b8', arrowsize='0.7')

        # Nó Central
        mapa.node('CENTRO', 'ESCOLA\nINCLUSIVA', shape='doublecircle', fillcolor='#0F52BA', fontcolor='white', fontsize='14', width='1.5')

        # Nível 1 (Os Pilares)
        mapa.node('FIL', 'FILOSOFIA\n(Outrar-se)', fillcolor='#dbeafe', color='#3b82f6')
        mapa.node('LEG', 'LEGISLAÇÃO\n(Direitos)', fillcolor='#fce7f3', color='#db2777')
        mapa.node('PRA', 'PRÁTICA\n(Pedagogia)', fillcolor='#dcfce7', color='#16a34a')
        mapa.node('GES', 'GESTÃO\n(Processos)', fillcolor='#ffedd5', color='#ea580c')

        # Conexões Centro -> Pilares
        mapa.edge('CENTRO', 'FIL')
        mapa.edge('CENTRO', 'LEG')
        mapa.edge('CENTRO', 'PRA')
        mapa.edge('CENTRO', 'GES')

        # Nível 2 (Conceitos Chave)
        # Filosofia
        mapa.node('ALT', 'Alteridade', shape='box', fillcolor='white')
        mapa.node('PER', 'Pertencimento', shape='box', fillcolor='white')
        mapa.edge('FIL', 'ALT')
        mapa.edge('FIL', 'PER')

        # Legislação
        mapa.node('LBI', 'LBI (2015)', shape='box', fillcolor='white')
        mapa.node('DEC', 'Decretos\n2025', shape='box', fillcolor='white')
        mapa.edge('LEG', 'LBI')
        mapa.edge('LEG', 'DEC')

        # Prática
        mapa.node('PEI', 'PEI\n(Sala Aula)', shape='box', fillcolor='white')
        mapa.node('AEE', 'AEE\n(Recursos)', shape='box', fillcolor='white')
        mapa.edge('PRA', 'PEI')
        mapa.edge('PRA', 'AEE')

        # Gestão
        mapa.node('EST', 'Estudo de\nCaso', shape='box', fillcolor='white')
        mapa.node('FIN', 'Duplo\nFundo', shape='box', fillcolor='white')
        mapa.edge('GES', 'EST')
        mapa.edge('GES', 'FIN')

        st.graphviz_chart(mapa, use_container_width=True)
    except:
        st.error("Erro ao renderizar o mapa. Verifique se o Graphviz está instalado.")

    st.markdown("---")
    
    # Resumo dos Pilares (Abaixo do Mapa)
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.info("**Filosofia:** Postura de 'outrar-se'. Empatia técnica e acolhimento da diferença.")
    with c2:
        st.error("**Legislação:** Garantia de matrícula e financiamento (Novos Decretos 2025).")
    with c3:
        st.success("**Prática:** Justiça Curricular. O PEI adapta o meio, não o aluno.")
    with c4:
        st.warning("**Gestão:** Estudo de Caso como porta de entrada e monitoramento contínuo.")

# ==============================================================================
# ABA 2: DICIONÁRIO E GLOSSÁRIO (COMPLETO)
# ==============================================================================
with tab_dict:
    st.markdown("### 📖 Dicionário da Inclusão")
    st.markdown("Esta aba une o **alinhamento de linguagem** (o que falar) com o **glossário técnico** (conceitos).")

    # Sub-abas internas para organizar
    sub_guia, sub_glossario = st.tabs(["🗣️ Guia de Linguagem (Anticapacitismo)", "📚 Glossário Técnico A-Z"])

    # --- 1. GUIA ANTICAPACITISTA (O que você gostou!) ---
    with sub_guia:
        st.markdown("#### Como combater o Capacitismo no dia a dia")
        st.caption("Substitua expressões estigmatizantes por termos técnicos e respeitosos.")

        col_ruim, col_seta, col_bom = st.columns([1, 0.2, 1])
        
        with col_ruim:
            st.markdown("<div style='text-align:center; font-weight:bold; color:#dc2626; margin-bottom:10px;'>❌ EVITE (Termos Ofensivos)</div>", unsafe_allow_html=True)
            termos_ruins = [
                ("Portador de Deficiência", "Deficiência não é um objeto que se porta."),
                ("Aluno de Inclusão", "Rotula e segrega. Todos são alunos."),
                ("Criança Especial", "Eufemismo que infantiliza."),
                ("Surdo-Mudo", "Erro técnico. Surdos têm voz."),
                ("Atrasado / Lento", "Desrespeita o ritmo neurodivergente.")
            ]
            for t, d in termos_ruins:
                st.markdown(f"""
                <div class="term-box-bad">
                    <strong style="text-decoration:line-through;">{t}</strong><br>
                    <small>{d}</small>
                </div>""", unsafe_allow_html=True)

        with col_seta:
            st.markdown("<br><br><div style='text-align:center; font-size:2rem; color:#cbd5e1;'>➔</div>", unsafe_allow_html=True)

        with col_bom:
            st.markdown("<div style='text-align:center; font-weight:bold; color:#16a34a; margin-bottom:10px;'>✅ USE (Termos Corretos)</div>", unsafe_allow_html=True)
            termos_bons = [
                ("Pessoa com Deficiência (PcD)", "Termo da Lei Brasileira de Inclusão."),
                ("Estudante Público-Alvo da Ed. Especial", "Termo técnico correto."),
                ("Estudante com Deficiência", "Foco na pessoa, depois na condição."),
                ("Surdo", "Termo identitário correto."),
                ("Ritmo Próprio / DI", "Deficiência Intelectual ou Neurodivergência.")
            ]
            for t, d in termos_bons:
                st.markdown(f"""
                <div class="term-box-good">
                    <strong>{t}</strong><br>
                    <small>{d}</small>
                </div>""", unsafe_allow_html=True)

    # --- 2. GLOSSÁRIO TÉCNICO A-Z (Conteúdo Rico) ---
    with sub_glossario:
        st.markdown("#### Glossário Conceitual")
        termo_busca = st.text_input("🔎 Pesquisar no Glossário:", placeholder="Digite para filtrar...")

        glossario_db = [
            {"t": "AEE (Atendimento Educacional Especializado)", "d": "Serviços que identificam, elaboram e organizam recursos pedagógicos e de acessibilidade. Complementar ou suplementar à escolarização."},
            {"t": "Alteridade", "d": "Reconhecer o outro como um sujeito pleno e legítimo em sua diferença."},
            {"t": "Capacitismo", "d": "Preconceito contra pessoas com deficiência. A crença de que corpos 'típicos' são superiores ou 'normais'."},
            {"t": "Cultura do Pertencimento", "d": "Ambiente onde o aluno não é apenas 'aceito', mas é parte vital da comunidade escolar."},
            {"t": "Declaração de Salamanca (1994)", "d": "Marco mundial que firmou o compromisso com a Escola Inclusiva como meio de combater discriminação."},
            {"t": "Educação Inclusiva", "d": "Paradigma onde a escola se adapta para acolher a todos, sem exceção. Diferente da 'Integração', onde o aluno tinha que se adaptar."},
            {"t": "Estudo de Caso", "d": "Metodologia pedagógica que substitui o laudo médico como porta de entrada inicial, focando na funcionalidade do aluno."},
            {"t": "Justiça Curricular", "d": "Adaptação do currículo para que ele represente e sirva a todos os grupos, garantindo equidade de acesso ao saber."},
            {"t": "Outragem / Outrar-se", "d": "Neologismo baseado em Fernando Pessoa. A capacidade de empatia profunda mantendo a postura profissional."},
            {"t": "PcD", "d": "Pessoa com Deficiência."},
            {"t": "PEI (Plano Educacional Individualizado)", "d": "Documento vivo que planeja as adaptações curriculares necessárias para o aluno na sala regular."},
            {"t": "PNEEPEI (2008)", "d": "Política Nacional que consolidou a matrícula na rede regular de ensino."},
            {"t": "Profissional de Apoio", "d": "Antigo 'cuidador'. Foca em alimentação, higiene e locomoção. Não substitui o professor."},
            {"t": "Tecnologia Assistiva", "d": "Qualquer recurso ou serviço que amplie a habilidade funcional da PcD (ex: pranchas, softwares, engrossadores)."},
            {"t": "Vieses Inconscientes", "d": "Associações automáticas do cérebro que reproduzem estereótipos aprendidos socialmente."}
        ]

        # Filtragem
        glossario_final = [g for g in glossario_db if termo_busca.lower() in g['t'].lower() or termo_busca.lower() in g['d'].lower()]

        for item in glossario_final:
            st.markdown(f"""
            <div class="glossary-item">
                <div style="color:#0F52BA; font-weight:700; font-size:1.05rem;">{item['t']}</div>
                <div style="color:#475569; margin-top:5px;">{item['d']}</div>
            </div>
            """, unsafe_allow_html=True)

# ==============================================================================
# ABA 3: LEGISLAÇÃO (ATUALIZADA)
# ==============================================================================
with tab_legal:
    st.markdown("### ⚖️ Legislação Vigente (Atualização 2025)")
    
    col_leg1, col_leg2 = st.columns(2)
    with col_leg1:
        st.markdown("""
        <div class="glass-card" style="border-left: 5px solid #22c55e;">
            <h4>💰 Decreto 12.686/2025 (Financiamento)</h4>
            <p>Institui o <strong>Duplo Fundo</strong>. O aluno da educação especial conta duas vezes para o repasse de verbas (Matrícula Regular + AEE).</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col_leg2:
        st.markdown("""
        <div class="glass-card" style="border-left: 5px solid #ef4444;">
            <h4>🚫 Decreto 12.773/2025 (Matrícula)</h4>
            <p>Criminaliza a recusa de matrícula e proíbe a cobrança de taxas extras para acessibilidade ou mediador em escolas privadas.</p>
        </div>
        """, unsafe_allow_html=True)

# ==============================================================================
# ABA 4: BIBLIOTECA VIRTUAL (EXPANSIVA)
# ==============================================================================
with tab_biblio:
    st.markdown("### 📚 Biblioteca & Referências")
    st.markdown("Clique nos itens para expandir o resumo e acessar o link.")

    def livro(titulo, autor, resumo, link):
        with st.expander(f"📕 {titulo}"):
            st.markdown(f"**Autor:** {autor}")
            st.markdown(f"**Síntese:** {resumo}")
            if link:
                st.markdown(f"[🔗 Acessar Documento Oficial]({link})")
            else:
                st.caption("Documento interno / Link não disponível.")

    # Lista Completa (Do seu texto)
    livro("Decreto 12.686 e 12.773 (Nova Política 2025)", "Governo Federal", 
          "Atualizam o financiamento do AEE e as regras de matrícula, focando no combate à exclusão e garantia de recursos.", 
          "https://www.planalto.gov.br")
    
    livro("Lei Brasileira de Inclusão (LBI - 13.146/2015)", "Brasil", 
          "Estatuto da Pessoa com Deficiência. Define barreira e criminaliza a discriminação.", 
          "http://www.planalto.gov.br/ccivil_03/_ato2015-2018/2015/lei/l13146.htm")
    
    livro("Declaração de Salamanca (1994)", "UNESCO", 
          "Marco mundial que estabeleceu as escolas regulares como meio mais eficaz de combater atitudes discriminatórias.", 
          "https://unesdoc.unesco.org/ark:/48223/pf0000139394")
    
    livro("Os Benefícios da Educação Inclusiva (2016)", "Instituto Alana", 
          "Estudos comprovam benefícios acadêmicos e sociais para alunos com e sem deficiência em ambientes inclusivos.", 
          "https://alana.org.br/wp-content/uploads/2016/11/Os_Beneficios_da_Ed_Inclusiva_final.pdf")
    
    livro("Capacitismo: o que é, onde vive?", "Sidney Andrade", 
          "Artigo fundamental para entender a estrutura do preconceito contra PcD.", 
          "https://medium.com/@sidneyandrade23/capacitismo-o-que-%C3%A9-onde-vive-como-sereproduz-5f68c5fdf73e")
    
    livro("Inclusão Escolar: O que é? Como fazer?", "Maria Teresa Eglér Mantoan", 
          "A bíblia da inclusão escolar no Brasil. Diferencia integração de inclusão.", None)

    livro("Base Nacional Comum Curricular (BNCC)", "MEC", 
          "Documento normativo que define as aprendizagens essenciais, base para a adaptação curricular.", 
          "https://www.gov.br/mec/pt-br/escola-em-tempo-integral/BNCC_EI_EF_110518_versaofinal.pdf")

# ==============================================================================
# ABA 5: MANUAL (MANTIDO)
# ==============================================================================
with tab_manual:
    st.markdown("### ⚙️ Manual de Uso")
    col1, col2 = st.columns(2)
    with col1:
        st.info("**1. PEI 360º:** Para o Professor Regente cadastrar o aluno e gerar o plano.")
    with col2:
        st.info("**2. PAEE:** Para a Sala de Recursos gerenciar barreiras e habilidades.")

# Rodapé
st.markdown("---")
st.caption("Central de Conhecimento Omnisfera • Atualizado com Decretos 2025")
