import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import graphviz

# ==============================================================================
# 1. SETUP & DESIGN SYSTEM (Visual Premium)
# ==============================================================================
st.set_page_config(page_title="Central de Conhecimento | Omnisfera", page_icon="🧠", layout="wide")

st.markdown("""
<style>
    /* Cards de Informação (Efeito Glass/Clean) */
    .info-card {
        background-color: white;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 24px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        transition: transform 0.2s;
        height: 100%;
    }
    .info-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 15px rgba(0,0,0,0.1);
        border-color: #0F52BA;
    }
    
    /* Referências Bibliográficas (Estilo Livro) */
    .biblio-card {
        border-left: 4px solid #CBD5E0;
        background: #F8FAFC;
        padding: 15px;
        margin-bottom: 15px;
        border-radius: 0 8px 8px 0;
    }
    .biblio-title { font-weight: 700; color: #2D3748; font-size: 1.1rem; }
    .biblio-author { color: #718096; font-size: 0.9rem; font-style: italic; }
    
    /* Tags de Era na Timeline */
    .era-tag {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 20px;
        color: white;
        font-weight: bold;
        font-size: 0.8rem;
        margin-bottom: 10px;
    }

    /* Tipografia */
    h1, h2, h3, h4 { font-family: 'Nunito', sans-serif; color: #1A202C; }
    
    /* Abas */
    .stTabs [data-baseweb="tab-list"] { border-bottom: 1px solid #E2E8F0; gap: 20px; }
    .stTabs [data-baseweb="tab"] { font-weight: 700; color: #A0AEC0; border: none; }
    .stTabs [aria-selected="true"] { color: #0F52BA !important; border-bottom: 3px solid #0F52BA !important; }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# 2. HEADER: CONCEITO VISUAL
# ==============================================================================
c1, c2 = st.columns([3, 1])
with c1:
    st.title("🧠 Central de Inteligência Inclusiva")
    st.markdown("**Design System Educacional:** Conectando legislação, empatia e prática em um ecossistema vivo.")

# Navegação
tab_empatia, tab_legal, tab_pratica, tab_equipe, tab_biblio = st.tabs([
    "1. Empatia (O Aluno)", 
    "2. Ecossistema Legal (Timeline)", 
    "3. Toolkit (Estratégias)", 
    "4. Equipe (Papéis)",
    "5. Biblioteca (Referências)"
])

# ==============================================================================
# 3. ABA EMPATIA: RADAR CHART (MANTIDO E APERFEIÇOADO)
# ==============================================================================
with tab_empatia:
    st.header("Design Thinking: A Fase de Empatia")
    st.markdown("Para projetar soluções (PEI), precisamos primeiro mapear a experiência do usuário (Aluno).")
    
    col_graf, col_txt = st.columns([1.5, 1])
    
    with col_graf:
        # Radar Chart - Visualizando Múltiplas Inteligências
        categories = ['Lógico-Matemática', 'Linguística', 'Interpessoal (Social)', 'Intrapessoal (Emoção)', 'Corporal', 'Visual']
        
        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(
            r=[4, 3, 1, 2, 5, 5], 
            theta=categories,
            fill='toself',
            name='Perfil do Aluno',
            line_color='#0F52BA',
            fillcolor='rgba(15, 82, 186, 0.2)'
        ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(visible=True, range=[0, 5], gridcolor='#E2E8F0'),
                angularaxis=dict(gridcolor='#E2E8F0')
            ),
            showlegend=False,
            height=400,
            margin=dict(l=50, r=50, t=30, b=30),
            paper_bgcolor='rgba(0,0,0,0)',
        )
        st.plotly_chart(fig, use_container_width=True)

    with col_txt:
        st.markdown("""
        <div class="info-card" style="border-left: 5px solid #0F52BA;">
            <h4>🔍 Leitura do Mapa</h4>
            <p>Este gráfico representa um aluno com perfil visual e motor forte, mas com barreiras sociais (comum em TEA ou TDAH).</p>
            <br>
            <strong>Insight de Design:</strong>
            <p>Em vez de forçar a competência "Interpessoal" (o ponto fraco) através de trabalhos em grupo tradicionais, utilize a competência "Visual" (ponto forte) como ponte. Ex: O aluno desenha o projeto e o grupo apresenta.</p>
        </div>
        """, unsafe_allow_html=True)

# ==============================================================================
# 4. ABA LEGAL: TIMELINE 2.0 & ECOSSISTEMA
# ==============================================================================
with tab_legal:
    st.header("Ecossistema Legal & Marcos Históricos")
    
    # --- PARTE A: O ECOSSISTEMA (VISÃO SISTÊMICA) ---
    st.subheader("🕸️ A Teia da Inclusão (Ecossistema)")
    st.markdown("Como as partes se conectam para sustentar o aluno.")
    
    # Graphviz para criar um Mapa Mental Limpo
    sys_map = graphviz.Digraph()
    sys_map.attr(rankdir='LR', bgcolor='transparent')
    sys_map.attr('node', shape='box', style='rounded,filled', fontname='Nunito', margin='0.2')
    
    # Nós
    sys_map.node('LEI', '⚖️ Legislação\n(LBI/Decretos)', fillcolor='#2D3748', fontcolor='white')
    sys_map.node('ESC', '🏫 Escola\n(Gestão/PPP)', fillcolor='#E2E8F0', color='#CBD5E0')
    sys_map.node('PEI', '📘 PEI/PAEE\n(Instrumento)', fillcolor='#0F52BA', fontcolor='white')
    sys_map.node('ALUNO', '👶 Aluno\n(Centro)', fillcolor='#48BB78', fontcolor='white')
    sys_map.node('FAM', '🏠 Família\n(Parceria)', fillcolor='#F6E05E')
    
    # Conexões
    sys_map.edge('LEI', 'ESC', label=' Regula')
    sys_map.edge('ESC', 'PEI', label=' Produz')
    sys_map.edge('FAM', 'ESC', label=' Compartilha')
    sys_map.edge('PEI', 'ALUNO', label=' Garante Acesso')
    
    st.graphviz_chart(sys_map)
    
    st.divider()

    # --- PARTE B: TIMELINE 2.0 (COM DECRETOS 2025) ---
    st.subheader("⏳ Linha do Tempo Evolutiva")
    st.markdown("Acompanhe a mudança de paradigma: da Exclusão à Inclusão Total.")

    # Dados Enriquecidos
    data_timeline = [
        {"Ano": 1988, "Marco": "Constituição Federal", "Era": "Fundação", "Desc": "Educação como direito de TODOS (Art. 205)."},
        {"Ano": 1994, "Marco": "Declaração de Salamanca", "Era": "Fundação", "Desc": "Documento mundial que baseia a inclusão."},
        {"Ano": 1996, "Marco": "LDB (Lei 9.394)", "Era": "Estruturação", "Desc": "Cap. V: Educação Especial como modalidade transversal."},
        {"Ano": 2008, "Marco": "PNEEPEI", "Era": "Estruturação", "Desc": "Política Nacional: Foco na escola comum (fim da segregação)."},
        {"Ano": 2015, "Marco": "LBI (Lei 13.146)", "Era": "Consolidação", "Desc": "Crime de discriminação. Conceito de Barreira vs Deficiência."},
        {"Ano": 2024, "Marco": "Política Nac. Equidade", "Era": "Atualização", "Desc": "Foco em populações vulneráveis e interseccionalidade."},
        {"Ano": 2025, "Marco": "Novos Decretos (12.686/12.773)", "Era": "Atualização", "Desc": "Reforço do financiamento do AEE e combate à discriminação."}
    ]
    df_time = pd.DataFrame(data_timeline)
    
    # Gráfico Customizado
    fig_time = px.scatter(
        df_time, x="Ano", y=[1]*len(df_time), 
        color="Era", 
        hover_name="Marco", hover_data={"Ano":True, "Desc":True, "Era":False},
        size=[40]*len(df_time),
        color_discrete_map={"Fundação": "#CBD5E0", "Estruturação": "#90CDF4", "Consolidação": "#0F52BA", "Atualização": "#FF4B4B"}
    )
    
    # Labels e Layout
    for i, row in df_time.iterrows():
        fig_time.add_annotation(x=row['Ano'], y=1, text=str(row['Ano']), showarrow=False, yshift=25, font=dict(color="#555"))

    fig_time.update_traces(marker=dict(line=dict(width=2, color='DarkSlateGrey')))
    fig_time.update_layout(
        height=250, 
        yaxis=dict(visible=False, range=[0.8, 1.2]), 
        xaxis=dict(visible=False, range=[1985, 2027]),
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.1, xanchor="center", x=0.5),
        margin=dict(l=20, r=20, t=50, b=20),
        plot_bgcolor="white"
    )
    st.plotly_chart(fig_time, use_container_width=True)
    
    # Detalhamento dos Decretos 2025 (Novo Upload)
    with st.expander("🔥 Destaque: Decretos de 2025 (Atualização)", expanded=True):
        c_dec1, c_dec2 = st.columns(2)
        with c_dec1:
            st.info("**Decreto 12.686/2025**\n\nFoca na reestruturação do financiamento do AEE (Atendimento Educacional Especializado), garantindo duplo fundo para matrícula de estudantes da educação especial.")
        with c_dec2:
            st.error("**Decreto 12.773/2025**\n\nEstabelece diretrizes mais rígidas contra a recusa de matrícula e cobra das escolas privadas a garantia de acessibilidade sem cobrança extra.")

# ==============================================================================
# 5. ABA TOOLKIT: ESTRATÉGIAS (IDEAR)
# ==============================================================================
with tab_pratica:
    st.header("Toolkit de Adaptação Curricular")
    st.markdown("Ferramentas para a fase de **Ideação**. Como superar as barreiras identificadas?")

    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="info-card" style="border-top: 5px solid #E53E3E;">
            <h4>⏱️ Tempo & Espaço</h4>
            <p><strong>Barreira:</strong> Atenção/Ansiedade</p>
            <ul>
                <li>Uso de Timer Visual (Pomodoro).</li>
                <li>Localização do aluno na frente (foco).</li>
                <li>Provas com tempo estendido (fator 1.5x).</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
    with col2:
        st.markdown("""
        <div class="info-card" style="border-top: 5px solid #3182CE;">
            <h4>📝 Material & Suporte</h4>
            <p><strong>Barreira:</strong> Leitura/Sensorial</p>
            <ul>
                <li>Fonte Arial 14/16 (Dislexia).</li>
                <li>Papel fosco (evitar reflexo).</li>
                <li>Pauta ampliada para escrita.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
    with col3:
        st.markdown("""
        <div class="info-card" style="border-top: 5px solid #38B2AC;">
            <h4>🗣️ Resposta & Avaliação</h4>
            <p><strong>Barreira:</strong> Motora/Escrita</p>
            <ul>
                <li>Prova Oral ou ditada.</li>
                <li>Uso de Tablet/Computador.</li>
                <li>Avaliação por Portfólio/Projeto.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

# ==============================================================================
# 6. ABA EQUIPE: AT VS AP
# ==============================================================================
with tab_equipe:
    st.header("Definição de Papéis (Role Definition)")
    st.markdown("Evite o 'Fogo Amigo'. Cada profissional tem um escopo de atuação.")
    
    c_at, c_ap = st.columns(2)
    with c_at:
        st.markdown("""
        <div class="info-card" style="background-color: #FFF5F5; border-left: 5px solid #F56565;">
            <h3 style="color:#C53030;">🏥 AT (Saúde)</h3>
            <p><strong>Acompanhante Terapêutico</strong></p>
            <p>Foco clínico e comportamental. Atua no manejo de crises, regulação emocional e habilidades sociais.</p>
            <small>Vínculo: Externo (Família/Plano/SUS)</small>
        </div>
        """, unsafe_allow_html=True)
        
    with c_ap:
        st.markdown("""
        <div class="info-card" style="background-color: #EBF8FF; border-left: 5px solid #4299E1;">
            <h3 style="color:#2B6CB0;">🏫 AP (Educação)</h3>
            <p><strong>Apoio Pedagógico / Escolar</strong></p>
            <p>Foco no acesso ao currículo. Auxilia na locomoção, higiene, alimentação e organização dos materiais.</p>
            <small>Vínculo: Escola / Secretaria</small>
        </div>
        """, unsafe_allow_html=True)

# ==============================================================================
# 7. NOVA ABA: BIBLIOTECA (RESUMIDA)
# ==============================================================================
with tab_biblio:
    st.header("📚 Biblioteca de Referência")
    st.markdown("Base teórica que fundamenta a Omnisfera. Resumos executivos para consulta rápida.")
    
    # Dados Bibliográficos
    livros = [
        {
            "titulo": "Inclusão Escolar: O que é? Por quê? Como fazer?",
            "autor": "Maria Teresa Eglér Mantoan",
            "resumo": "Obra fundamental que quebra o paradigma da 'integração' (o aluno se adapta) para a 'inclusão' (a escola muda). Mantoan defende que não existe aluno ineducável.",
            "tag": "Filosofia"
        },
        {
            "titulo": "Declaração de Salamanca (1994)",
            "autor": "UNESCO",
            "resumo": "O documento marco mundial. Estabelece que escolas regulares com orientação inclusiva são os meios mais eficazes de combater atitudes discriminatórias.",
            "tag": "Legislação"
        },
        {
            "titulo": "Lei Brasileira de Inclusão (Estatuto da PcD)",
            "autor": "Lei 13.146/2015",
            "resumo": "Define 'Barreira' (qualquer entrave que limite a participação) e criminaliza a recusa de matrícula. Base jurídica para exigir adaptações.",
            "tag": "Legislação"
        },
        {
            "titulo": "Os Benefícios da Educação Inclusiva",
            "autor": "Instituto Alana / ABT Associates",
            "resumo": "Estudo baseado em evidências que prova: alunos sem deficiência também aprendem mais em ambientes inclusivos (melhora em empatia e resolução de problemas).",
            "tag": "Evidências"
        },
        {
            "titulo": "NotebookLM Insights (Omnisfera)",
            "autor": "Compilação IA",
            "resumo": "Mapeamento das novas diretrizes de 2025 (Decretos 12.686/12.773), focando no financiamento do AEE e na gestão do PAEE.",
            "tag": "Atualização 2025"
        }
    ]
    
    # Renderização em Grid
    for livro in livros:
        cor_tag = "#48BB78" if livro['tag'] == "Filosofia" else ("#4299E1" if livro['tag'] == "Legislação" else "#ED8936")
        
        st.markdown(f"""
        <div class="biblio-card">
            <div style="display:flex; justify-content:space-between;">
                <span class="biblio-title">{livro['titulo']}</span>
                <span style="background:{cor_tag}; color:white; padding:2px 8px; border-radius:10px; font-size:0.7rem;">{livro['tag']}</span>
            </div>
            <div class="biblio-author">{livro['autor']}</div>
            <p style="margin-top:10px; font-size:0.95rem;">{livro['resumo']}</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.download_button("📥 Baixar Lista Bibliográfica Completa (PDF)", data="Simulação de PDF...", file_name="Bibliografia_Omnisfera.pdf")

# Rodapé
st.markdown("---")
st.caption("Omnisfera Knowledge Base • Atualizado com Decretos 2025 • Design Thinking Methodology")
