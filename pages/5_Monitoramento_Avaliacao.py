import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import graphviz

# ==============================================================================
# 1. SETUP & CSS (VISUAL PREMIUM - GLASSMORPHISM)
# ==============================================================================
st.set_page_config(page_title="Central de Conhecimento | Omnisfera", page_icon="🧠", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;800&display=swap');
    
    /* Tipografia Global */
    html, body, [class*="css"] { font-family: 'Nunito', sans-serif; }
    
    /* Cards com Efeito de Vidro (Glassmorphism) */
    .glass-card {
        background: rgba(255, 255, 255, 0.95);
        border: 1px solid rgba(255, 255, 255, 0.5);
        border-radius: 20px;
        padding: 30px;
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.07);
        backdrop-filter: blur(4px);
        margin-bottom: 25px;
        transition: transform 0.3s ease;
    }
    .glass-card:hover { transform: translateY(-5px); border-color: #0F52BA; }
    
    /* Hero Section (Degradê Suave) */
    .hero-box {
        background: linear-gradient(120deg, #fdfbfb 0%, #ebedee 100%);
        padding: 40px; border-radius: 20px; text-align: center;
        margin-bottom: 30px; border-bottom: 4px solid #0F52BA;
    }
    
    /* Glossário: Cards de Erro e Acerto */
    .term-wrong {
        background-color: #FFF5F5; border-left: 5px solid #E53E3E;
        padding: 15px; border-radius: 8px; margin-bottom: 10px; opacity: 0.8;
    }
    .term-right {
        background-color: #F0FFF4; border-left: 5px solid #48BB78;
        padding: 15px; border-radius: 8px; margin-bottom: 10px;
    }
    .arrow-icon { font-size: 1.5rem; color: #A0AEC0; align-self: center; }

    /* Estilo das Abas */
    .stTabs [data-baseweb="tab-list"] { justify-content: center; gap: 20px; border-bottom: 1px solid #E2E8F0; }
    .stTabs [data-baseweb="tab"] { font-size: 1rem; font-weight: 700; color: #718096; }
    .stTabs [aria-selected="true"] { color: #0F52BA !important; border-bottom: 3px solid #0F52BA !important; }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# 2. HERO SECTION: MANIFESTO VISUAL
# ==============================================================================
st.markdown("""
<div class="hero-box">
    <h1 style="color: #2D3748; font-size: 3rem; margin-bottom: 10px;">A Arte de "Outrar-se"</h1>
    <p style="font-size: 1.2rem; color: #4A5568; max-width: 800px; margin: 0 auto; line-height: 1.6;">
        <em>"Sentir o mundo do outro como se fosse o seu próprio mundo... numa relação empática sem se envolver, no entanto, com os sentimentos da pessoa."</em><br>
        — Bernardo Soares (Fernando Pessoa)
    </p>
</div>
""", unsafe_allow_html=True)

# Navegação
tab_universo, tab_glossario, tab_legal, tab_toolkit, tab_equipe = st.tabs([
    "🌌 O Universo do Aluno", 
    "📖 Glossário Anticapacitista", 
    "⚖️ Ecossistema Legal", 
    "🛠️ Toolkit Prático",
    "🤝 Equipe & Papéis"
])

# ==============================================================================
# 3. ABA 1: O UNIVERSO DO ALUNO (VISUAL SPECTACLE)
# ==============================================================================
with tab_universo:
    c1, c2 = st.columns([2, 1])
    
    with c1:
        st.markdown("### 🔭 Mapeamento Multidimensional")
        st.caption("Visualização Holística das Potencialidades (Sunburst Chart)")
        
        # DADOS PARA O GRÁFICO SUNBURST (Hierarquia Visual Rica)
        data = dict(
            character=["Aluno", "Aluno", "Aluno", "Intelectual", "Intelectual", "Social", "Social", "Motor", "Motor", "Sensorial", "Sensorial"],
            parent=["", "", "", "Aluno", "Aluno", "Aluno", "Aluno", "Aluno", "Aluno", "Aluno", "Aluno"],
            label=["Aluno", "Foco", "Interesse", "Lógico", "Linguístico", "Pares", "Adultos", "Fino", "Grosso", "Visual", "Auditivo"],
            value=[10, 5, 5, 8, 3, 2, 4, 3, 5, 9, 2], # Valores simulados de um perfil TEA típico
            color=["#F7FAFC", "#F7FAFC", "#F7FAFC", "#0F52BA", "#90CDF4", "#E53E3E", "#FEB2B2", "#ED8936", "#FBD38D", "#805AD5", "#D6BCFA"] 
        )
        
        fig = go.Figure(go.Sunburst(
            labels=["<b>O ALUNO</b>", "Cognitivo", "Social", "Motor", "Sensorial", 
                    "Lógica", "Leitura", "Pares", "Adultos", "Escrita", "Esportes", "Visual", "Auditivo"],
            parents=["", "<b>O ALUNO</b>", "<b>O ALUNO</b>", "<b>O ALUNO</b>", "<b>O ALUNO</b>",
                     "Cognitivo", "Cognitivo", "Social", "Social", "Motor", "Motor", "Sensorial", "Sensorial"],
            values=[0, 30, 20, 20, 30, 25, 5, 5, 15, 5, 15, 28, 2],
            branchvalues="total",
            marker=dict(colors=px.colors.qualitative.Prism),
            hovertemplate='<b>%{label}</b><br>Potencial: %{value}%<extra></extra>'
        ))
        
        fig.update_layout(
            margin=dict(t=0, l=0, r=0, b=0),
            height=450,
            paper_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        st.markdown("""
        <div class="glass-card" style="border-left: 5px solid #805AD5;">
            <h3 style="color: #2D3748;">🧠 Como ler este Universo?</h3>
            <p>Este gráfico rompe com a visão linear de "nota". Ele mostra o aluno como um sistema complexo.</p>
            <hr>
            <p><strong>Exemplo Visualizado:</strong></p>
            <ul>
                <li>🟣 <strong>Sensorial (Grande):</strong> Aluno aprende vendo (Memória Fotográfica).</li>
                <li>🔴 <strong>Social (Pequeno):</strong> Dificuldade com pares, prefere adultos.</li>
                <li>🔵 <strong>Cognitivo (Médio):</strong> Ótimo em lógica, dificuldade em leitura.</li>
            </ul>
            <br>
            <div style="background:#E9D8FD; color:#553C9A; padding:10px; border-radius:8px; font-weight:bold; text-align:center;">
                Estratégia: Use o Roxo (Visual) para alavancar o Vermelho (Social).
            </div>
        </div>
        """, unsafe_allow_html=True)

# ==============================================================================
# 4. ABA 2: GLOSSÁRIO ANTICAPACITISTA (NOVA)
# ==============================================================================
with tab_glossario:
    st.header("📖 Dicionário da Inclusão")
    st.markdown("As palavras constroem realidades. Abaixo, um guia para eliminar o **Capacitismo** do vocabulário escolar.")

    # Filtro de Busca
    busca = st.text_input("🔍 Pesquisar termo...", placeholder="Digite uma palavra...")

    # Dados do Glossário (Baseado nos seus PDFs)
    termos = [
        {"errado": "Portador de deficiência", "certo": "Pessoa com deficiência (PcD)", "desc": "A deficiência não é algo que se 'porta' ou traz consigo como um objeto. Ela é parte da pessoa."},
        {"errado": "Aluno de inclusão", "certo": "Aluno com deficiência / Público-alvo da Ed. Especial", "desc": "Todos os alunos são 'de inclusão'. Rotular o aluno cria estigma."},
        {"errado": "Surdo-mudo", "certo": "Surdo", "desc": "A maioria dos surdos tem aparelho fonador intacto. Eles não falam porque não ouvem, mas podem aprender a falar."},
        {"errado": "Atrasado / Lento", "certo": "Deficiência Intelectual / Ritmo próprio", "desc": "Termos pejorativos que ignoram o funcionamento cognitivo diverso."},
        {"errado": "Fingir de cego / João sem braço", "certo": "Desentendido / Preguiçoso", "desc": "Metáforas que usam a deficiência como sinônimo de falha de caráter (Capacitismo Recreativo)."},
        {"errado": "Doente Mental", "certo": "Transtorno Mental / Psicossocial", "desc": "Deficiência não é doença. Doença tem cura, deficiência é uma condição de vida."},
        {"errado": "Normal", "certo": "Típico / Sem deficiência", "desc": "Usar 'normal' implica que a pessoa com deficiência é 'anormal'."}
    ]

    c_esq, c_dir = st.columns(2)
    
    with c_esq:
        st.subheader("🚫 Termos a Abolir")
        st.caption("Expressões carregadas de preconceito ou imprecisão técnica.")
    with c_dir:
        st.subheader("✅ Termos Corretos")
        st.caption("Linguagem baseada na LBI e no Modelo Social da Deficiência.")

    for item in termos:
        if busca.lower() in item['errado'].lower() or busca.lower() in item['certo'].lower():
            col_w, col_seta, col_r = st.columns([1, 0.2, 1])
            
            with col_w:
                st.markdown(f"""
                <div class="term-wrong">
                    <div style="font-weight:bold; color:#C53030;">❌ {item['errado']}</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col_seta:
                st.markdown("<div style='text-align:center; margin-top:15px; font-size:1.5rem; color:#CBD5E0;'>➔</div>", unsafe_allow_html=True)
                
            with col_r:
                st.markdown(f"""
                <div class="term-right">
                    <div style="font-weight:bold; color:#276749;">✅ {item['certo']}</div>
                    <div style="font-size:0.85rem; margin-top:5px; color:#4A5568;">💡 {item['desc']}</div>
                </div>
                """, unsafe_allow_html=True)

    st.markdown("---")
    
    # Glossário Técnico (Conceitos)
    st.subheader("📚 Glossário Técnico (Siglas e Conceitos)")
    
    col_g1, col_g2, col_g3 = st.columns(3)
    with col_g1:
        st.info("**PEI (Plano Ed. Individualizado):** Documento do Professor Regente para adaptação curricular em sala.")
    with col_g2:
        st.info("**PAEE (Plano de AEE):** Documento do Professor Especialista para eliminação de barreiras na Sala de Recursos.")
    with col_g3:
        st.info("**Desenho Universal:** Planejar a aula pensando em TODOS, para evitar adaptações excessivas depois.")

# ==============================================================================
# 5. ABA 3: ECOSSISTEMA LEGAL (COM OS NOVOS DECRETOS)
# ==============================================================================
with tab_legal:
    st.header("Estrutura Legal")
    
    # Mapa Mental com Graphviz (Estilo Dark/Tech)
    st.subheader("🕸️ O Sistema de Proteção")
    
    mapa = graphviz.Digraph()
    mapa.attr(rankdir='LR', bgcolor='transparent')
    mapa.attr('node', shape='note', style='filled', fontname='Nunito', penwidth='0')
    
    mapa.node('CONST', 'Constituição\n(1988)', fillcolor='#2D3748', fontcolor='white')
    mapa.node('LBI', 'LBI (2015)\nLei Maior', fillcolor='#0F52BA', fontcolor='white')
    mapa.node('DECRETOS', 'Decretos 2025\n(Financiamento)', fillcolor='#FF4B4B', fontcolor='white')
    mapa.node('ESCOLA', 'A Escola\n(Prática)', fillcolor='#E2E8F0', fontcolor='#333')
    
    mapa.edge('CONST', 'LBI')
    mapa.edge('LBI', 'DECRETOS')
    mapa.edge('LBI', 'ESCOLA', label=' Criminaliza Recusa')
    mapa.edge('DECRETOS', 'ESCOLA', label=' Garante Verba')
    
    st.graphviz_chart(mapa)
    
    st.divider()
    
    # Timeline
    st.subheader("⏳ Evolução Histórica (Atualizada 2025)")
    timeline_data = [
        {"Ano": 1988, "Marco": "Constituição Federal", "Era": "Direito", "Desc": "Educação para todos."},
        {"Ano": 2008, "Marco": "PNEEPEI", "Era": "Política", "Desc": "Foco na escola comum."},
        {"Ano": 2015, "Marco": "LBI (Lei 13.146)", "Era": "Garantia", "Desc": "Crime de discriminação."},
        {"Ano": 2025, "Marco": "Decretos 12.686/773", "Era": "Financiamento", "Desc": "Duplo fundo e combate à recusa."}
    ]
    df_time = pd.DataFrame(timeline_data)
    
    fig_time = px.scatter(df_time, x="Ano", y=[1]*len(df_time), color="Era", size=[40]*4, hover_name="Marco", hover_data=["Desc"])
    fig_time.update_layout(height=200, yaxis=dict(visible=False), xaxis=dict(visible=True), plot_bgcolor="white")
    st.plotly_chart(fig_time, use_container_width=True)

# ==============================================================================
# 6. ABA 4: TOOLKIT (ESTRATÉGIAS)
# ==============================================================================
with tab_toolkit:
    st.header("Caixa de Ferramentas Pedagógicas")
    
    c1, c2, c3 = st.columns(3)
    
    with c1:
        st.markdown("""
        <div class="glass-card" style="border-top: 5px solid #E53E3E;">
            <h4>⏱️ Tempo</h4>
            <p>Adapte a duração, não a capacidade.</p>
            <ul>
                <li>Tempo estendido (1.5x)</li>
                <li>Pausas ativas</li>
                <li>Relógio visual</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown("""
        <div class="glass-card" style="border-top: 5px solid #3182CE;">
            <h4>📝 Material</h4>
            <p>Adapte a forma, não o conteúdo.</p>
            <ul>
                <li>Fonte Arial 14+</li>
                <li>Contraste visual</li>
                <li>Textos fatiados</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    with c3:
        st.markdown("""
        <div class="glass-card" style="border-top: 5px solid #38B2AC;">
            <h4>🗣️ Resposta</h4>
            <p>Adapte a saída, não a exigência.</p>
            <ul>
                <li>Prova Oral</li>
                <li>Uso de Tablet</li>
                <li>Escriba</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

# ==============================================================================
# 7. ABA 5: EQUIPE E PAPÉIS
# ==============================================================================
with tab_equipe:
    st.header("Quem faz o quê?")
    st.info("A confusão entre AT e AP é a maior causa de conflitos na escola. Use este guia.")
    
    c_at, c_ap = st.columns(2)
    
    with c_at:
        st.markdown("""
        <div class="glass-card" style="background:#FFF5F5;">
            <h3 style="color:#C53030;">🏥 AT (Saúde)</h3>
            <p><strong>Acompanhante Terapêutico</strong></p>
            <p>Profissional clínico (externo). Foco no comportamento e saúde mental.</p>
        </div>
        """, unsafe_allow_html=True)
        
    with c_ap:
        st.markdown("""
        <div class="glass-card" style="background:#EBF8FF;">
            <h3 style="color:#2B6CB0;">🏫 AP (Educação)</h3>
            <p><strong>Apoio Pedagógico</strong></p>
            <p>Profissional escolar. Foco na higiene, alimentação e acesso ao material.</p>
        </div>
        """, unsafe_allow_html=True)

# Rodapé
st.markdown("---")
st.caption("Central de Conhecimento Omnisfera • Atualizada com Decretos 2025 • Design Thinking Methodology")
