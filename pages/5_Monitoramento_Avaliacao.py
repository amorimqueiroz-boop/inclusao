import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import graphviz

# ==============================================================================
# 1. CONFIGURAÇÃO VISUAL & CSS (Design System Omnisfera)
# ==============================================================================
st.set_page_config(page_title="Guia de Práticas | Omnisfera", page_icon="📚", layout="wide")

st.markdown("""
<style>
    /* Cards e Containers */
    .stCard {
        background-color: white;
        padding: 24px;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        border: 1px solid #E2E8F0;
        margin-bottom: 20px;
        transition: transform 0.2s;
    }
    .stCard:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0,0,0,0.12); }
    
    .card-red { border-left: 5px solid #FF4B4B; }
    .card-blue { border-left: 5px solid #0F52BA; }
    .card-green { border-left: 5px solid #00CC96; }
    .card-purple { border-left: 5px solid #8856F5; }

    /* Tipografia */
    h1, h2, h3 { font-family: 'Nunito', sans-serif; }
    h3 { color: #2D3748 !important; font-weight: 700; }
    .highlight { color: #FF4B4B; font-weight: bold; }
    
    /* Abas Personalizadas */
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] {
        background-color: #F7FAFC;
        border-radius: 8px 8px 0 0;
        padding: 10px 20px;
        border: none;
    }
    .stTabs [aria-selected="true"] {
        background-color: #FFFFFF !important;
        border-top: 3px solid #FF4B4B !important;
        color: #FF4B4B !important;
        font-weight: bold;
    }
    
    /* Métricas */
    div[data-testid="stMetric"] { background-color: #F8FAFC; padding: 15px; border-radius: 10px; }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# 2. HEADER E INTRODUÇÃO
# ==============================================================================
c1, c2 = st.columns([3, 1])
with c1:
    st.title("📚 Central de Conhecimento Inclusivo")
    st.markdown("Base estratégica para gestão do **PEI**, **PAEE** e fundamentação legal.")

# Navegação Principal
tab_fundamentos, tab_paee, tab_pratica, tab_equipe = st.tabs([
    "🏛️ Fundamentos & Legal", 
    "📝 PEI vs PAEE (Gestão)", 
    "🧠 Práticas (BNCC & Socioemocional)",
    "🤝 Papéis & Equipe"
])

# ==============================================================================
# 3. ABA FUNDAMENTOS: TIMELINE & CONCEITOS
# ==============================================================================
with tab_fundamentos:
    st.header("Filosofia e Marcos Legais")
    st.markdown("Os pilares que sustentam a educação inclusiva no Brasil.")

    # Bloco 1: Conceitos Chave
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        <div class="stCard card-blue">
            <h3>💡 O Princípio de 'Outrar-se'</h3>
            <p style="font-style: italic; color: #555;">
                "Sentir o mundo do outro como se fosse o seu... numa relação empática sem se perder nos sentimentos alheios."
            </p>
            <hr>
            <p><strong>Aplicação Prática:</strong> Empatia Técnica. O educador deve acolher a diferença sem perder a postura profissional de mediador do conhecimento.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="stCard card-red">
            <h3>🚫 O Inimigo: Capacitismo</h3>
            <p>Concepção que reduz a pessoa à sua deficiência, pressupondo incapacidade.</p>
            <hr>
            <ul>
                <li><strong>Capacitismo Físico:</strong> Barreiras arquitetônicas.</li>
                <li><strong>Capacitismo Atitudinal:</strong> "Ele é um anjo", "Apesar da deficiência...", infantilização.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    st.divider()

    # Bloco 2: Linha do Tempo Interativa
    st.subheader("📜 Evolução Histórica (Brasil)")
    
    timeline_data = [
        dict(Ano="1988", Marco="Constituição Federal", Desc="Art. 205: Educação como direito de todos e dever do Estado."),
        dict(Ano="1996", Marco="LDB (Lei 9.394)", Desc="Capítulo V: Define a Educação Especial como modalidade transversal."),
        dict(Ano="2008", Marco="Política Nacional (PNEEPEI)", Desc="Ruptura com o modelo segregacionista. Foco na escola comum."),
        dict(Ano="2015", Marco="LBI (Lei 13.146)", Desc="Estatuto da Pessoa com Deficiência. Crime de discriminação e recusa de matrícula."),
        dict(Ano="2020", Marco="Decreto 10.502 (Suspenso)", Desc="Tentativa de retorno de classes especiais (polêmica jurídica).")
    ]
    df_time = pd.DataFrame(timeline_data)
    
    fig_time = px.scatter(df_time, x="Ano", y=[1]*len(df_time), text="Marco", 
                          hover_data=["Desc"], size=[40]*5, color="Marco",
                          color_discrete_sequence=px.colors.qualitative.Set2)
    
    fig_time.update_traces(textposition='top center', marker=dict(line=dict(width=2, color='DarkSlateGrey')))
    fig_time.update_layout(
        showlegend=False, height=220, yaxis=dict(visible=False, range=[0.5, 2]),
        xaxis=dict(type='category', title=""), margin=dict(l=20, r=20, t=10, b=20),
        plot_bgcolor="white"
    )
    st.plotly_chart(fig_time, use_container_width=True)
    
    with st.expander("📖 Ver Detalhes Legislativos"):
        st.table(df_time[['Ano', 'Marco', 'Desc']])

# ==============================================================================
# 4. ABA GESTÃO: PEI VS PAEE
# ==============================================================================
with tab_paee:
    st.header("Gestão Estratégica: PEI x PAEE")
    st.markdown("A distinção crucial para a organização da escola inclusiva.")

    # Comparativo Lado a Lado
    c_pei, c_paee = st.columns(2)
    
    with c_pei:
        st.markdown("""
        <div class="stCard card-purple">
            <h3 style="color: #8856F5 !important;">📘 PEI (Plano Educacional Individualizado)</h3>
            <p><strong>Foco:</strong> O ALUNO na SALA DE AULA.</p>
            <ul>
                <li><strong>Responsável:</strong> Professor Regente (com apoio).</li>
                <li><strong>O que é:</strong> Adaptação curricular, objetivos de aprendizagem, metodologia de ensino.</li>
                <li><strong>Exemplo:</strong> "João vai aprender soma com material dourado enquanto a turma faz exercícios no caderno."</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
    with c_paee:
        st.markdown("""
        <div class="stCard card-green">
            <h3 style="color: #00CC96 !important;">🧩 PAEE (Plano de AEE)</h3>
            <p><strong>Foco:</strong> O RECURSO e a BARREIRA.</p>
            <ul>
                <li><strong>Responsável:</strong> Professor do AEE (Sala de Recursos).</li>
                <li><strong>O que é:</strong> Eliminação de barreiras, produção de materiais, ensino de Libras/Braille.</li>
                <li><strong>Exemplo:</strong> "Ensinar João a usar a prancha de comunicação para que ele possa responder ao Professor Regente."</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    
    # Wizard de Construção do PAEE
    st.subheader("🛠️ Construtor de PAEE (Passo a Passo)")
    st.caption("Fluxo baseado no Decreto 7.611/2011 e Nota Técnica MEC/SEESP.")

    steps = ["1. Estudo de Caso", "2. Plano de AEE", "3. Atendimento", "4. Avaliação"]
    active_step = st.radio("Etapa do Processo:", steps, horizontal=True, label_visibility="collapsed")
    
    if active_step == "1. Estudo de Caso":
        st.info("Investigação inicial para identificar as barreiras.")
        st.checkbox("Entrevista com a Família (Anamnese)")
        st.checkbox("Observação em Sala de Aula (Vínculo e Interação)")
        st.checkbox("Análise de Laudos Clínicos (Saúde)")
        
    elif active_step == "2. Plano de AEE":
        st.info("Documento formal que organiza o serviço.")
        c1, c2 = st.columns(2)
        c1.text_input("Objetivos Específicos (ex: Autonomia no banheiro)")
        c1.selectbox("Frequência de Atendimento", ["1x Semana", "2x Semana", "Diário"])
        c2.multiselect("Recursos Necessários", ["Engrossadores", "Libras", "Pranchas", "Software", "Mobiliário"])
        
    elif active_step == "3. Atendimento":
        st.warning("Execução das atividades na Sala de Recursos ou em classe.")
        st.markdown("* **Foco:** Não é reforço escolar! É ensino de habilidades para autonomia.")
        st.markdown("* **Articulação:** O Prof. AEE deve conversar com o Regente semanalmente.")
        
    elif active_step == "4. Avaliação":
        st.success("Revisão periódica do plano.")
        st.slider("Eficácia das Estratégias Atuais", 0, 10, 5)
        st.text_area("Justificativa para Reestruturação do Plano")

# ==============================================================================
# 5. ABA PRÁTICA: BNCC & SOCIOEMOCIONAL
# ==============================================================================
with tab_pratica:
    st.header("Toolkit Pedagógico (Baseado na BNCC)")
    
    # Diagrama de Fluxo (Graphviz)
    st.subheader("🔄 Fluxo da Adaptação Curricular")
    
    fluxo = graphviz.Digraph()
    fluxo.attr(rankdir='LR', bgcolor='transparent')
    fluxo.attr('node', shape='box', style='rounded,filled', fillcolor='#F0F2F6', color='#0F52BA', fontname='Nunito')
    
    fluxo.node('BNCC', 'Objetivo da Turma\n(BNCC)', fillcolor='#E2E8F0')
    fluxo.node('BAR', 'Identificar Barreira\n(Acesso)')
    fluxo.node('EST', 'Estratégia\n(Flexibilização)')
    fluxo.node('ALUNO', 'Aprendizagem\n(Equidade)', fillcolor='#D4EDDA')
    
    fluxo.edge('BNCC', 'BAR')
    fluxo.edge('BAR', 'EST', label=' Desenho Universal')
    fluxo.edge('EST', 'ALUNO')
    
    st.graphviz_chart(fluxo)
    
    st.divider()
    
    # Estratégias Práticas
    st.subheader("🧠 Estratégias Neurocompatíveis (TDAH, TEA, Dislexia)")
    
    col_s1, col_s2, col_s3 = st.columns(3)
    
    with col_s1:
        st.markdown("**1. Gestão do Tempo**")
        st.success("Permitir tempo estendido em provas. Uso de relógios visuais (Timer).")
        
    with col_s2:
        st.markdown("**2. Instruções (Consignas)**")
        st.info("Fatiar tarefas complexas em passos menores. Uso de pistas visuais junto com a fala.")
        
    with col_s3:
        st.markdown("**3. Ambiente Físico**")
        st.warning("Reduzir estímulos visuais na parede frontal. Aluno sentado longe de portas/janelas.")

    # Seção Sócioemocional
    st.markdown("---")
    with st.expander("❤️ Competências Socioemocionais e Habilidades de Vida", expanded=True):
        st.markdown("""
        A inclusão não é apenas cognitiva, é afetiva. O currículo deve prever o desenvolvimento integral:
        * **Autoconhecimento:** O aluno reconhecer suas próprias emoções e limites.
        * **Consciência Social:** A turma entender e respeitar a neurodiversidade (combate ao bullying).
        * **Tomada de Decisão Responsável:** Autonomia para escolher materiais e parceiros.
        """)

# ==============================================================================
# 6. ABA EQUIPE: PAPÉIS CLAROS
# ==============================================================================
with tab_equipe:
    st.header("Definição de Papéis e Responsabilidades")
    st.warning("⚠️ Conflito Comum: A escola contrata AT achando que é AP, ou vice-versa.")

    col_at, col_ap = st.columns(2)
    
    # Card AT
    with col_at:
        st.markdown("""
        <div class="stCard" style="background-color: #FFF5F5; border-color: #FF4B4B;">
            <h3 style="color:#FF4B4B;">🏥 AT (Acompanhante Terapêutico)</h3>
            <p><strong>Natureza:</strong> Clínica / Saúde</p>
            <hr>
            <ul>
                <li><strong>Vínculo:</strong> Geralmente externo (Família/Plano/SUS).</li>
                <li><strong>Função:</strong> Manejo de comportamento, crises agressivas, suporte emocional.</li>
                <li><strong>Não faz:</strong> Não ensina conteúdo pedagógico.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    # Card AP
    with col_ap:
        st.markdown("""
        <div class="stCard" style="background-color: #F0F7FF; border-color: #0F52BA;">
            <h3 style="color:#0F52BA;">🏫 AP (Apoio Pedagógico/Escolar)</h3>
            <p><strong>Natureza:</strong> Escolar / Pedagógica</p>
            <hr>
            <ul>
                <li><strong>Vínculo:</strong> Escola / Secretaria de Educação.</li>
                <li><strong>Função:</strong> Acesso ao currículo, higiene, alimentação, locomoção.</li>
                <li><strong>Faz:</strong> Auxilia na organização do material e rotina.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.info("💡 **Dica para Gestão:** O Psicólogo Escolar **não faz clínica** (terapia) dentro da escola. Ele atua na mediação institucional, formação docente e acolhimento das famílias.")

# Rodapé
st.markdown("<br><div style='text-align:center; color:#A0AEC0; font-size:0.8em;'>Omnisfera • Baseado nas Diretrizes da BNCC e Legislação Vigente</div>", unsafe_allow_html=True)
