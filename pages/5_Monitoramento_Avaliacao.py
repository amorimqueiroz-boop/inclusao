import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import graphviz

# ==============================================================================
# 1. ESTILIZAÇÃO CUSTOMIZADA (CSS PREMIUM)
# ==============================================================================
st.markdown("""
<style>
    /* Cards Flutuantes */
    .stCard {
        background-color: white;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        border-left: 5px solid #FF4B4B;
        margin-bottom: 20px;
    }
    .stCardBlue {
        background-color: #F0F7FF;
        padding: 20px;
        border-radius: 12px;
        border-left: 5px solid #0F52BA;
        color: #0F52BA;
    }
    
    /* Títulos e Métricas */
    h3 { color: #FF4B4B !important; }
    div[data-testid="stMetricValue"] { color: #0F52BA !important; }
    
    /* Abas */
    .stTabs [data-baseweb="tab-highlight"] { background-color: #FF4B4B; }
</style>
""", unsafe_allow_html=True)

st.title("📚 Guia de Práticas e Fundamentos")
st.markdown("Base de conhecimento visual para suporte à gestão e prática da educação inclusiva.")

# Abas
tab1, tab2, tab3, tab4 = st.tabs([
    "🏛️ Fundamentos & Legal", 
    "📊 Gestão & Dados", 
    "🧠 Prática Pedagógica",
    "🤝 Equipe & Papéis"
])

# ==============================================================================
# ABA 1: FUNDAMENTOS & TIMELINE INTERATIVA
# ==============================================================================
with tab1:
    st.header("Filosofia e Legislação")
    
    # Bloco Conceitual (Cards Lado a Lado)
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("""
        <div class="stCardBlue">
            <h4>💡 O Conceito de 'Outrar-se'</h4>
            <p><em>"Sentir o mundo do outro como se fosse o seu... numa relação empática sem se envolver com os sentimentos da pessoa."</em></p>
            <small>— Fernando Pessoa (Bernardo Soares)</small>
            <br><br>
            <strong>Aplicação:</strong> Empatia Técnica. Interpretar a necessidade sem perder a postura profissional.
        </div>
        """, unsafe_allow_html=True)
    
    with c2:
        st.markdown("""
        <div class="stCard" style="border-left-color: #FF4B4B;">
            <h4>🚫 Inimigo: Capacitismo</h4>
            <p>Preconceito que pressupõe a deficiência como uma 'falta' ou 'diminuição'.</p>
            <ul>
                <li><strong>Físico:</strong> Falta de rampas, banheiros.</li>
                <li><strong>Simbólico:</strong> Metáforas ("fingir de cego") e viés inconsciente.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    st.divider()
    st.subheader("📜 Evolução dos Marcos Legais")
    
    # CRIAÇÃO DA TIMELINE COM PLOTLY (Visual Gráfico)
    timeline_data = [
        dict(Ano="1988", Marco="Constituição Federal", Desc="Direito de todos"),
        dict(Ano="1994", Marco="Declaração de Salamanca", Desc="Compromisso Global"),
        dict(Ano="1996", Marco="LDB (Lei 9.394)", Desc="Obrig. Educação Especial"),
        dict(Ano="2008", Marco="PNEEPEI", Desc="Política Nacional na Escola Comum"),
        dict(Ano="2015", Marco="LBI (Lei 13.146)", Desc="Lei Brasileira de Inclusão")
    ]
    df_time = pd.DataFrame(timeline_data)
    
    fig_time = px.scatter(df_time, x="Ano", y=[1]*len(df_time), text="Marco", 
                          hover_data=["Desc"], size=[30]*5, color="Marco")
    
    fig_time.update_traces(textposition='top center', marker=dict(symbol="circle", line=dict(width=2, color='DarkSlateGrey')))
    fig_time.update_layout(
        showlegend=False, 
        height=250, 
        yaxis=dict(visible=False),
        xaxis=dict(type='category'),
        margin=dict(l=20, r=20, t=20, b=20),
        plot_bgcolor="white"
    )
    st.plotly_chart(fig_time, use_container_width=True)
    
    with st.expander("Ver detalhes da legislação"):
        st.table(df_time[['Ano', 'Marco', 'Desc']])

# ==============================================================================
# ABA 2: GESTÃO & DADOS (Gráficos do IBGE citados no PDF)
# ==============================================================================
with tab2:
    st.header("Gestão Estratégica Baseada em Dados")
    st.caption("Dados extraídos do Cenário Brasileiro (IBGE) citados no material de referência.")

    # KPI Cards
    k1, k2, k3 = st.columns(3)
    k1.metric("População PcD (Brasil)", "18.6 Mi", "8.9% da População")
    k2.metric("Gap Analfabetismo", "19.5%", "vs 4.1% Geral")
    k3.metric("Gap Trabalho Informal", "57.3%", "Maior Precarização")

    st.markdown("---")

    g1, g2 = st.columns([1, 1.5])
    
    with g1:
        st.subheader("🎓 Escolaridade")
        # Gráfico de Rosca comparando Ensino Médio
        labels = ['PcD', 'População Geral']
        values = [25.6, 55] # Dados do PDF (Ensino Médio Completo)
        
        fig_educ = go.Figure(data=[go.Pie(labels=labels, values=values, hole=.6, marker_colors=['#FF4B4B', '#0F52BA'])])
        fig_educ.update_layout(title_text="Conclusão Ensino Médio (%)", height=300, margin=dict(t=30, b=0, l=0, r=0))
        st.plotly_chart(fig_educ, use_container_width=True)
        st.caption("*Apenas 25,6% das PcD concluem o Ensino Médio (IBGE).")

    with g2:
        st.subheader("📋 Checklist do PGEI")
        st.markdown("Passo a passo para o **Plano Geral de Educação Inclusiva**:")
        
        # Barra de Progresso Visual (Steps)
        steps = ["1. Censo Escolar", "2. Mapear Perfis", "3. Recursos Físicos", "4. Dimensionar Equipe"]
        current = st.selectbox("Status da sua escola:", steps)
        
        if current == steps[0]: prog = 25
        elif current == steps[1]: prog = 50
        elif current == steps[2]: prog = 75
        else: prog = 100
        
        st.progress(prog)
        st.info(f"**Próxima Ação:** {current} - Garanta que estes dados estejam no sistema Omnisfera.")

# ==============================================================================
# ABA 3: PRÁTICA PEDAGÓGICA (Fluxogramas e Toolkit)
# ==============================================================================
with tab3:
    st.header("Toolkit Pedagógico")
    
    # 1. Fluxograma do PEI (Graphviz)
    st.subheader("🔄 O Fluxo da Justiça Curricular")
    
    graph = graphviz.Digraph()
    graph.attr(rankdir='LR', bgcolor='transparent')
    graph.attr('node', shape='box', style='filled', fillcolor='white', color='#0F52BA', fontname='Nunito')
    
    graph.node('A', '1. COLETA\n(Laudos + Família)')
    graph.node('B', '2. FILTRO\n(Equipe Multidisciplinar)')
    graph.node('C', '3. AÇÃO\n(Adaptação Curricular)')
    graph.node('D', 'ALUNO\n(Aprendizado Real)')
    
    graph.edge('A', 'B', label=' Sigilo')
    graph.edge('B', 'C', label=' Tradução Pedagógica')
    graph.edge('C', 'D', label=' Inclusão')
    
    st.graphviz_chart(graph)
    
    st.divider()
    
    # 2. Grid de Estratégias (Cards Coloridos)
    st.subheader("🧠 Estratégias Neurocompatíveis (TDAH/Dislexia)")
    
    row1 = st.columns(4)
    strategies = [
        ("⏱️ Tempo", "Flexibilidade em provas e tarefas.", "⏳"),
        ("🗣️ Consignas", "Instruções curtas e diretas.", "📢"),
        ("📝 Avaliação", "Oral, projetos, múltipla escolha.", "✅"),
        ("💡 Ambiente", "Longe de janelas/portas.", "🪑")
    ]
    
    for col, (title, desc, icon) in zip(row1, strategies):
        col.markdown(f"""
        <div style="background:#f9f9f9; padding:15px; border-radius:10px; text-align:center; height:180px; border-top: 4px solid #FF4B4B;">
            <div style="font-size:30px;">{icon}</div>
            <div style="font-weight:bold; color:#333;">{title}</div>
            <div style="font-size:12px; color:#666; margin-top:10px;">{desc}</div>
        </div>
        """, unsafe_allow_html=True)

# ==============================================================================
# ABA 4: EQUIPE (Comparativo Visual)
# ==============================================================================
with tab4:
    st.header("Definição de Papéis")
    st.warning("⚠️ Confusão comum: A escola contrata AT achando que é AP, ou vice-versa.")

    col_at, col_ap = st.columns(2)
    
    # Card AT
    with col_at:
        st.markdown("""
        <div style="background-color: #FFF5F5; border: 1px solid #FF4B4B; border-radius: 10px; padding: 20px;">
            <h3 style="color:#FF4B4B; text-align:center;">AT</h3>
            <p style="text-align:center; font-weight:bold;">Atendente Terapêutico</p>
            <hr>
            <ul style="list-style-type: none; padding: 0;">
                <li>🏥 <strong>Foco:</strong> Clínico / Saúde</li>
                <li>🔗 <strong>Vínculo:</strong> Família ou Estado</li>
                <li>🎯 <strong>Missão:</strong> Manejo de comportamento e crises.</li>
                <li>❌ <strong>Não faz:</strong> Adaptação de lição.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    # Card AP
    with col_ap:
        st.markdown("""
        <div style="background-color: #F0F7FF; border: 1px solid #0F52BA; border-radius: 10px; padding: 20px;">
            <h3 style="color:#0F52BA; text-align:center;">AP</h3>
            <p style="text-align:center; font-weight:bold;">Atendente Pedagógico</p>
            <hr>
            <ul style="list-style-type: none; padding: 0;">
                <li>🏫 <strong>Foco:</strong> Escolar / Pedagógico</li>
                <li>🔗 <strong>Vínculo:</strong> Escola</li>
                <li>🎯 <strong>Missão:</strong> Acesso ao currículo e rotina.</li>
                <li>✅ <strong>Faz:</strong> Auxílio na lancheira, materiais, interação.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.info("💡 **Dica do Diretor:** O Psicólogo Escolar **não faz clínica** (terapia) dentro da escola. Ele faz mediação institucional e suporte à equipe.")

# Rodapé
st.markdown("<br><br><div style='text-align:center; color:gray; font-size:0.8em;'>Omnisfera Learning Systems • Baseado na obra 'Inclusão Escolar: Gestão e Prática'</div>", unsafe_allow_html=True)
