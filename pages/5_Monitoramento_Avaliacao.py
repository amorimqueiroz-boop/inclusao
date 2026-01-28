import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import graphviz

# ==============================================================================
# 1. SETUP & CSS (VISUAL PREMIUM - GLASSMORPHISM & CLEAN DESIGN)
# ==============================================================================
st.set_page_config(page_title="Central de Conhecimento | Omnisfera", page_icon="🧠", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800&display=swap');
    
    /* Tipografia Global */
    html, body, [class*="css"] { font-family: 'Nunito', sans-serif; color: #2D3748; }
    
    /* Fundo Geral */
    .stApp { background-color: #F8FAFC; }

    /* Cards com Efeito de Vidro (Glassmorphism) */
    .glass-card {
        background: rgba(255, 255, 255, 0.95);
        border: 1px solid rgba(255, 255, 255, 0.6);
        border-radius: 16px;
        padding: 24px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.03);
        margin-bottom: 20px;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .glass-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 10px 25px rgba(15, 82, 186, 0.1);
        border-color: #0F52BA;
    }
    
    /* Hero Section */
    .hero-box {
        background: linear-gradient(135deg, #ffffff 0%, #f1f5f9 100%);
        padding: 40px; border-radius: 20px; text-align: center;
        margin-bottom: 30px; border-bottom: 4px solid #0F52BA;
        box-shadow: 0 10px 30px -10px rgba(0,0,0,0.1);
    }
    
    /* Glossário: Cards de Erro e Acerto */
    .term-wrong {
        background-color: #FFF5F5; border-left: 4px solid #E53E3E;
        padding: 15px; border-radius: 8px; margin-bottom: 8px; opacity: 0.9;
    }
    .term-right {
        background-color: #F0FFF4; border-left: 4px solid #48BB78;
        padding: 15px; border-radius: 8px; margin-bottom: 8px;
    }
    
    /* Bibliografia e Quiz */
    .biblio-box {
        border-left: 4px solid #805AD5; background: white;
        padding: 20px; margin-bottom: 15px; border-radius: 0 12px 12px 0;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }
    .quiz-question { font-weight: 700; color: #2D3748; margin-bottom: 5px; }
    
    /* Abas Personalizadas */
    .stTabs [data-baseweb="tab-list"] { justify-content: center; gap: 20px; border-bottom: 1px solid #E2E8F0; padding-bottom: 10px; }
    .stTabs [data-baseweb="tab"] { font-size: 1rem; font-weight: 700; color: #718096; background-color: transparent; border: none; }
    .stTabs [aria-selected="true"] { color: #0F52BA !important; border-bottom: 3px solid #0F52BA !important; }
    
    /* Títulos */
    h1, h2, h3 { color: #1A202C; font-weight: 800; }
    .highlight { color: #0F52BA; }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# 2. HERO SECTION: MANIFESTO
# ==============================================================================
st.markdown("""
<div class="hero-box">
    <h1 style="font-size: 2.5rem; margin-bottom: 10px;">A Arte de <span class="highlight">'Outrar-se'</span></h1>
    <p style="font-size: 1.1rem; color: #4A5568; max-width: 800px; margin: 0 auto; line-height: 1.6;">
        <em>"Sentir o mundo do outro como se fosse o seu próprio mundo... numa relação empática sem se envolver, no entanto, com os sentimentos da pessoa."</em><br>
        — Bernardo Soares (Fernando Pessoa)
    </p>
</div>
""", unsafe_allow_html=True)

# ==============================================================================
# 3. NAVEGAÇÃO PRINCIPAL
# ==============================================================================
tab_universo, tab_glossario, tab_legal, tab_estudos, tab_equipe = st.tabs([
    "🌌 O Universo do Aluno", 
    "📖 Dicionário Anticapacitista", 
    "⚖️ Ecossistema Legal", 
    "🎓 Centro de Estudos", 
    "🤝 Equipe & Papéis"
])

# ==============================================================================
# ABA 1: O UNIVERSO DO ALUNO (SUNBURST CHART)
# ==============================================================================
with tab_universo:
    c1, c2 = st.columns([1.8, 1])
    
    with c1:
        st.markdown("### 🔭 Mapeamento Multidimensional")
        st.caption("O aluno não é uma nota. Ele é um sistema complexo de inteligências.")
        
        # Dados Hierárquicos (Sunburst)
        fig = go.Figure(go.Sunburst(
            labels=["<b>O ALUNO</b>", "Cognitivo", "Social", "Motor", "Sensorial", 
                    "Lógica", "Leitura", "Pares", "Adultos", "Fino", "Grosso", "Visual", "Auditivo"],
            parents=["", "<b>O ALUNO</b>", "<b>O ALUNO</b>", "<b>O ALUNO</b>", "<b>O ALUNO</b>",
                     "Cognitivo", "Cognitivo", "Social", "Social", "Motor", "Motor", "Sensorial", "Sensorial"],
            values=[0, 30, 20, 20, 30, 25, 5, 5, 15, 5, 15, 28, 2],
            branchvalues="total",
            marker=dict(colors=px.colors.qualitative.Prism),
            hovertemplate='<b>%{label}</b><br>Potencial: %{value}%<extra></extra>'
        ))
        
        fig.update_layout(margin=dict(t=0, l=0, r=0, b=0), height=450, paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        st.markdown("""
        <div class="glass-card" style="border-left: 5px solid #805AD5;">
            <h3 style="color: #553C9A;">🧠 Leitura do Gráfico</h3>
            <p>Este gráfico rompe com a visão linear. Ele mostra onde estão as <strong>ilhas de competência</strong>.</p>
            <hr>
            <p><strong>Exemplo Visualizado (Perfil TEA):</strong></p>
            <ul>
                <li>🟣 <strong>Sensorial (Grande):</strong> Memória visual fotográfica.</li>
                <li>🔵 <strong>Cognitivo (Médio):</strong> Alta lógica, baixa leitura.</li>
                <li>🔴 <strong>Social (Pequeno):</strong> Dificuldade com pares.</li>
            </ul>
            <br>
            <div style="background:#F3E8FF; color:#553C9A; padding:10px; border-radius:8px; font-weight:bold; text-align:center; font-size:0.9rem;">
                Insight: Use o Roxo (Visual) para ensinar o Vermelho (Social).
            </div>
        </div>
        """, unsafe_allow_html=True)

# ==============================================================================
# ABA 2: GLOSSÁRIO ANTICAPACITISTA
# ==============================================================================
with tab_glossario:
    st.header("📖 As Palavras Constroem Realidades")
    st.markdown("Um guia prático para eliminar o **Capacitismo** (preconceito contra PcD) do vocabulário escolar.")

    termo_busca = st.text_input("🔍 Pesquisar expressão...", placeholder="Ex: Portador, Surdo-mudo, Normal...")

    # Banco de Termos (Baseado nos seus PDFs)
    termos = [
        {"errado": "Portador de deficiência", "certo": "Pessoa com deficiência (PcD)", "desc": "Deficiência não é algo que se 'porta' como uma bolsa. É parte da condição humana."},
        {"errado": "Aluno de inclusão", "certo": "Aluno com deficiência / Público da Ed. Especial", "desc": "Todos os alunos são de inclusão. O termo correto foca no direito, não no estigma."},
        {"errado": "Surdo-mudo", "certo": "Surdo", "desc": "A maioria dos surdos tem o aparelho fonador intacto. Eles não falam porque não ouvem."},
        {"errado": "Atrasado / Lento", "certo": "Deficiência Intelectual / Ritmo próprio", "desc": "Termos pejorativos que ignoram a neurodiversidade e os tempos de aprendizagem."},
        {"errado": "Fingir de cego / João sem braço", "certo": "Desentendido / Preguiçoso", "desc": "Metáforas que associam deficiência a falha de caráter (Capacitismo Recreativo)."},
        {"errado": "Doença Mental", "certo": "Transtorno Mental / Psicossocial", "desc": "Deficiência não é doença. Doença tem cura; deficiência é uma condição de vida."},
        {"errado": "Criança Normal", "certo": "Criança Típica / Sem deficiência", "desc": "Usar 'normal' implica que a pessoa com deficiência é 'anormal'."}
    ]

    # Renderização Lado a Lado
    col_dict, col_info = st.columns([2, 1])
    
    with col_dict:
        filtro = [t for t in termos if termo_busca.lower() in t['errado'].lower() or termo_busca.lower() in t['certo'].lower()]
        
        for item in filtro:
            c_w, c_arrow, c_r = st.columns([1, 0.1, 1])
            with c_w:
                st.markdown(f"<div class='term-wrong'>❌ <strong>{item['errado']}</strong></div>", unsafe_allow_html=True)
            with c_arrow:
                st.markdown("<div style='text-align:center; padding-top:10px; color:#CBD5E0;'>➔</div>", unsafe_allow_html=True)
            with c_r:
                st.markdown(f"""
                <div class='term-right'>
                    ✅ <strong>{item['certo']}</strong>
                    <div style='font-size:0.85rem; margin-top:4px; color:#4A5568;'>{item['desc']}</div>
                </div>""", unsafe_allow_html=True)

    with col_info:
        st.info("**Nota Técnica:** O capacitismo pode ser físico (barreiras arquitetônicas) ou atitudinal (dúvida da capacidade). Combata os dois.")

# ==============================================================================
# ABA 3: ECOSSISTEMA LEGAL (TIMELINE & GRAPHVIZ)
# ==============================================================================
with tab_legal:
    st.header("Ecossistema Legal & Marcos 2025")
    
    # 1. Mapa Mental (O Sistema)
    st.subheader("🕸️ A Rede de Proteção")
    mapa = graphviz.Digraph()
    mapa.attr(rankdir='LR', bgcolor='transparent')
    mapa.attr('node', shape='box', style='rounded,filled', fontname='Nunito', margin='0.2')
    
    mapa.node('CONST', 'Constituição (1988)', fillcolor='#2D3748', fontcolor='white')
    mapa.node('LBI', 'LBI (Lei 13.146)', fillcolor='#0F52BA', fontcolor='white')
    mapa.node('DEC', 'Decretos 2025\n(12.686 / 12.773)', fillcolor='#FF4B4B', fontcolor='white')
    mapa.node('ESC', 'Escola\n(Gestão)', fillcolor='#E2E8F0')
    
    mapa.edge('CONST', 'LBI')
    mapa.edge('LBI', 'DEC')
    mapa.edge('LBI', 'ESC', label=' Criminaliza Recusa')
    mapa.edge('DEC', 'ESC', label=' Garante Financiamento')
    
    st.graphviz_chart(mapa)
    
    st.divider()
    
    # 2. Timeline Interativa
    st.subheader("⏳ Linha do Tempo Evolutiva")
    timeline_data = [
        {"Ano": 1988, "Marco": "Constituição Federal", "Era": "Fundação", "Desc": "Educação como direito de todos (Art. 205)."},
        {"Ano": 1994, "Marco": "Declaração de Salamanca", "Era": "Fundação", "Desc": "Compromisso global com a escola comum."},
        {"Ano": 2008, "Marco": "PNEEPEI", "Era": "Estruturação", "Desc": "Política Nacional: Fim da segregação."},
        {"Ano": 2015, "Marco": "LBI (Estatuto)", "Era": "Garantia", "Desc": "Conceito de barreira e crime de discriminação."},
        {"Ano": 2025, "Marco": "Decretos 12.686/773", "Era": "Atualização", "Desc": "Duplo fundo para AEE e regras contra recusa de matrícula."}
    ]
    df_time = pd.DataFrame(timeline_data)
    
    fig_time = px.scatter(df_time, x="Ano", y=[1]*len(df_time), color="Era", size=[40]*len(df_time), 
                          hover_name="Marco", hover_data=["Desc"],
                          color_discrete_map={"Fundação": "#CBD5E0", "Estruturação": "#90CDF4", "Garantia": "#0F52BA", "Atualização": "#FF4B4B"})
    
    fig_time.update_layout(height=220, yaxis=dict(visible=False), xaxis=dict(visible=True, title=""), plot_bgcolor="white")
    st.plotly_chart(fig_time, use_container_width=True)

# ==============================================================================
# ABA 4: CENTRO DE ESTUDOS (RESTAURO COMPLETO)
# ==============================================================================
with tab_estudos:
    st.header("🎓 Centro de Estudos e Capacitação")
    st.markdown("Material aprofundado para formação continuada da equipe.")

    sub_quiz, sub_resumos = st.tabs(["🧠 Quiz de Autoavaliação", "📚 Bibliografia Comentada"])

    # --- QUIZ INTERATIVO ---
    with sub_quiz:
        st.subheader("Teste seus conhecimentos")
        st.caption("Responda mentalmente e clique para conferir o gabarito oficial.")
        
        questions = [
            ("O que é o conceito de 'outragem'?", "É a postura de 'outrar-se': sentir o mundo do outro mantendo a empatia, mas com distanciamento profissional para não confundir procedimentos."),
            ("Qual a função do 'Estudo de Caso' em 2025?", "Substitui o laudo médico como porta de entrada. É uma avaliação pedagógica para identificar necessidades e definir apoios."),
            ("O que define 'Capacitismo' na LBI?", "Qualquer distinção, restrição ou exclusão que prejudique direitos da PcD. Manifesta-se em barreiras físicas e atitudinais."),
            ("Dados da PNAD 2022 sobre educação?", "Gap alarmante: 19,5% de analfabetismo em PcD (vs 4,1% geral). Apenas 25,6% concluem o Ensino Médio."),
            ("Qual a diferença entre PEI e PAEE?", "PEI: Plano para a sala de aula (currículo). PAEE: Plano para a sala de recursos (barreiras e autonomia).")
        ]
        
        for i, (q, a) in enumerate(questions):
            with st.expander(f"Questão {i+1}: {q}"):
                st.markdown(f"**Resposta:** {a}")

    # --- BIBLIOGRAFIA E RESUMOS ---
    with sub_resumos:
        st.subheader("Acervo Bibliográfico")
        
        livros = [
            {"titulo": "Inclusão Escolar: O que é? Como fazer?", "autor": "Maria Teresa Eglér Mantoan", "tag": "Filosofia", "resumo": "Obra que quebra o paradigma da 'integração' (aluno se adapta) para 'inclusão' (escola muda). Defende que não existe aluno ineducável."},
            {"titulo": "Declaração de Salamanca (1994)", "autor": "UNESCO", "tag": "Marco Legal", "resumo": "Estabelece que escolas regulares com orientação inclusiva são o meio mais eficaz de combater atitudes discriminatórias."},
            {"titulo": "Lei Brasileira de Inclusão (13.146/2015)", "autor": "Brasil", "tag": "Legislação", "resumo": "Define 'Barreira' como qualquer entrave à participação. Criminaliza a recusa de matrícula e cobra acessibilidade."},
            {"titulo": "Os Benefícios da Educação Inclusiva", "autor": "Instituto Alana", "tag": "Evidências", "resumo": "Estudos provam que alunos sem deficiência também aprendem mais em ambientes inclusivos (ganho em empatia e resolução de problemas)."}
        ]
        
        for l in livros:
            cor = "#48BB78" if l['tag'] == "Filosofia" else ("#0F52BA" if l['tag'] == "Legislação" else "#ED8936")
            st.markdown(f"""
            <div class="biblio-box">
                <div style="display:flex; justify-content:space-between;">
                    <span style="font-weight:bold; font-size:1.1rem; color:#2D3748;">{l['titulo']}</span>
                    <span style="background:{cor}; color:white; padding:2px 10px; border-radius:12px; font-size:0.75rem;">{l['tag']}</span>
                </div>
                <div style="color:#718096; font-size:0.9rem; font-style:italic; margin-bottom:8px;">{l['autor']}</div>
                <p style="margin:0; font-size:0.95rem;">{l['resumo']}</p>
            </div>
            """, unsafe_allow_html=True)

# ==============================================================================
# ABA 5: EQUIPE E PAPÉIS
# ==============================================================================
with tab_equipe:
    st.header("Definição de Papéis")
    st.info("A clareza entre quem cuida da **Saúde** e quem cuida da **Educação** evita conflitos.")
    
    c_at, c_ap = st.columns(2)
    with c_at:
        st.markdown("""
        <div class="glass-card" style="background-color:#FFF5F5; border-left:5px solid #E53E3E;">
            <h3 style="color:#C53030;">🏥 AT (Saúde)</h3>
            <p><strong>Acompanhante Terapêutico</strong></p>
            <p>Foco clínico e comportamental (manejo de crises). Vínculo geralmente externo (Família/Plano).</p>
        </div>""", unsafe_allow_html=True)
        
    with c_ap:
        st.markdown("""
        <div class="glass-card" style="background-color:#EBF8FF; border-left:5px solid #3182CE;">
            <h3 style="color:#2B6CB0;">🏫 AP (Educação)</h3>
            <p><strong>Profissional de Apoio</strong></p>
            <p>Foco no acesso ao currículo, higiene e alimentação. Vínculo com a Escola/Secretaria.</p>
        </div>""", unsafe_allow_html=True)

# Rodapé
st.markdown("---")
st.caption("Omnisfera Knowledge Base • Atualizado com Decretos 2025 • Design Thinking Methodology")
