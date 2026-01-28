import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

# ==============================================================================
# 1. SETUP & DESIGN SYSTEM (Professional & Clean)
# ==============================================================================
st.set_page_config(page_title="Guia de Práticas | Omnisfera", page_icon="🧩", layout="wide")

st.markdown("""
<style>
    /* Design System: Cards de Informação */
    .info-card {
        background-color: white;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 24px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.04);
        margin-bottom: 20px;
        height: 100%;
    }
    .info-card h4 {
        color: #2D3748;
        font-weight: 700;
        margin-bottom: 12px;
        font-family: 'Nunito', sans-serif;
    }
    .info-card p, .info-card li {
        color: #4A5568;
        font-size: 0.95rem;
        line-height: 1.5;
    }
    
    /* Destaques Laterais (Color Coding) */
    .border-blue { border-left: 5px solid #0F52BA; }
    .border-red { border-left: 5px solid #FF4B4B; }
    .border-teal { border-left: 5px solid #00B8D9; }
    .border-purple { border-left: 5px solid #6554C0; }

    /* Tipografia de Títulos */
    h1, h2, h3 { font-family: 'Nunito', sans-serif; color: #1A202C; }
    
    /* Abas Minimalistas */
    .stTabs [data-baseweb="tab-list"] { border-bottom: 1px solid #E2E8F0; }
    .stTabs [data-baseweb="tab"] { font-weight: 600; color: #718096; }
    .stTabs [aria-selected="true"] { color: #0F52BA !important; border-bottom: 2px solid #0F52BA !important; }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# 2. CABEÇALHO: CONCEITO DE DESIGN THINKING
# ==============================================================================
c1, c2 = st.columns([3, 1])
with c1:
    st.title("📚 Central de Conhecimento")
    st.markdown("**Design Thinking na Inclusão:** Do entendimento do sujeito à prototipagem de soluções curriculares.")

# Navegação Estruturada
tab_empatia, tab_definicao, tab_ideacao, tab_equipe = st.tabs([
    "1. Empatizar (O Aluno)", 
    "2. Definir (Conceitos & Leis)", 
    "3. Idear (Estratégias)", 
    "4. Equipe (Papéis)"
])

# ==============================================================================
# 3. ABA EMPATIZAR: O SUJEITO ALÉM DO DIAGNÓSTICO
# ==============================================================================
with tab_empatia:
    st.header("Mapeamento de Potencialidades")
    st.markdown("A fase de **Empatia** exige visualizar o aluno de forma multidimensional, não apenas suas falhas.")
    
    col_grafico, col_insights = st.columns([1.2, 1])
    
    with col_grafico:
        # GRÁFICO DE RADAR: VISUALIZAÇÃO DE PERFIL
        # Mostra desníveis comuns em neurodivergência (ex: Alto Cognitivo, Baixo Social)
        categories = ['Lógico-Matemático', 'Linguística', 'Interpessoal', 'Intrapessoal', 'Corporal-Cinestésica', 'Visual-Espacial']
        
        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(
            r=[5, 3, 1, 2, 2, 5], # Exemplo: Aluno com perfil TEA (Alta lógica/visual, baixa social)
            theta=categories,
            fill='toself',
            name='Perfil Atual',
            line_color='#0F52BA',
            opacity=0.6
        ))
        
        fig.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 5])),
            showlegend=False,
            height=350,
            margin=dict(l=40, r=40, t=20, b=20),
            title="Radar de Habilidades (Exemplo)"
        )
        st.plotly_chart(fig, use_container_width=True)

    with col_insights:
        st.markdown("""
        <div class="info-card border-blue">
            <h4>🧠 Análise do Perfil (Exemplo)</h4>
            <p>O gráfico ao lado ilustra um perfil comum na escola inclusiva (ex: TEA ou Altas Habilidades):</p>
            <ul>
                <li><strong>Pontos de Força (Alavancas):</strong> Raciocínio Lógico e Visual. O aluno aprende vendo esquemas, não apenas ouvindo.</li>
                <li><strong>Pontos de Atenção (Barreiras):</strong> Inteligência Interpessoal. Trabalhos em grupo sem mediação geram ansiedade.</li>
            </ul>
            <hr style="margin: 15px 0;">
            <p><strong>Insight de Design:</strong> Não tente "consertar" o lado social forçando interação. Use o lado Visual (Força) para mediar a comunicação.</p>
        </div>
        """, unsafe_allow_html=True)

# ==============================================================================
# 4. ABA DEFINIR: CONCEITOS ESTRUTURANTES
# ==============================================================================
with tab_definicao:
    st.header("Definição do Problema e Escopo")
    st.markdown("Na fase de **Definição**, precisamos clareza sobre quais ferramentas usar e qual o respaldo legal.")

    # PEI vs PAEE (Lado a Lado)
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("""
        <div class="info-card border-purple">
            <h4>📘 PEI: Plano Educacional Individualizado</h4>
            <p><strong>Cenário:</strong> Sala de Aula Regular.</p>
            <p><strong>Responsável:</strong> Professor Regente.</p>
            <p><strong>O que define:</strong> As adaptações curriculares necessárias para o aluno acessar o conteúdo da turma (ex: prova adaptada, tempo estendido).</p>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown("""
        <div class="info-card border-teal">
            <h4>🧩 PAEE: Plano de AEE</h4>
            <p><strong>Cenário:</strong> Sala de Recursos Multifuncionais.</p>
            <p><strong>Responsável:</strong> Professor Especialista (AEE).</p>
            <p><strong>O que define:</strong> O treinamento de habilidades e uso de tecnologias assistivas para eliminar barreiras (ex: ensino de Libras, uso de prancha).</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    
    # Timeline Legal
    st.subheader("Fundamentação Legal (Rule of Law)")
    timeline_data = [
        dict(Ano="1988", Marco="Constituição", Desc="Art. 205: Educação como direito de todos."),
        dict(Ano="1996", Marco="LDB", Desc="Define a Ed. Especial como modalidade transversal."),
        dict(Ano="2008", Marco="PNEEPEI", Desc="Política Nacional: Foco na matrícula em escola comum."),
        dict(Ano="2015", Marco="LBI", Desc="Lei 13.146: Define 'Barreira' e criminaliza a discriminação.")
    ]
    df_time = pd.DataFrame(timeline_data)
    
    fig_time = px.scatter(df_time, x="Ano", y=[1]*len(df_time), text="Marco", 
                          hover_data=["Desc"], size=[30]*4, color="Marco")
    fig_time.update_layout(height=200, yaxis=dict(visible=False), xaxis=dict(type='category'), showlegend=False, margin=dict(t=20, b=20))
    st.plotly_chart(fig_time, use_container_width=True)

# ==============================================================================
# 5. ABA IDEAR: ESTRATÉGIAS DE INTERVENÇÃO
# ==============================================================================
with tab_ideacao:
    st.header("Ideação e Prototipagem de Soluções")
    st.markdown("Banco de estratégias validadas para superar barreiras comuns.")

    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="info-card border-red">
            <h4>⏱️ Adaptação Temporal</h4>
            <p>Para alunos com processamento lento ou TDAH.</p>
            <ul>
                <li>Aumento de tempo em provas (mínimo 1h).</li>
                <li>Fracionamento de tarefas longas (Pausas ativas).</li>
                <li>Uso de Timer Visual para gestão de ansiedade.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
    with col2:
        st.markdown("""
        <div class="info-card border-blue">
            <h4>📝 Adaptação de Material</h4>
            <p>Para baixa visão, dislexia ou disgrafia.</p>
            <ul>
                <li>Fonte Arial/Verdana, tamanho 14+.</li>
                <li>Espaçamento duplo entre linhas.</li>
                <li>Evitar "poluição visual" nas páginas de prova.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
    with col3:
        st.markdown("""
        <div class="info-card border-teal">
            <h4>🗣️ Adaptação de Resposta</h4>
            <p>Para dificuldades motoras ou de escrita.</p>
            <ul>
                <li>Prova Oral (com gravação).</li>
                <li>Uso de Escriba (Ledor/Transcritor).</li>
                <li>Uso de Tablet/Computador para digitação.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

# ==============================================================================
# 6. ABA EQUIPE: CLAREZA DE PAPÉIS
# ==============================================================================
with tab_equipe:
    st.header("Arquitetura da Equipe Multidisciplinar")
    st.markdown("Para que a inclusão funcione, cada ator deve atuar dentro do seu escopo técnico.")

    c_at, c_ap = st.columns(2)
    
    with c_at:
        st.markdown("""
        <div class="info-card" style="border-left: 5px solid #E53E3E; background-color: #FFF5F5;">
            <h3 style="color: #C53030;">AT (Acompanhante Terapêutico)</h3>
            <p><strong>Escopo:</strong> Saúde / Clínica.</p>
            <hr>
            <p>Profissional (geralmente Psicólogo ou Terapeuta Ocupacional) focado no manejo comportamental e habilidades sociais.</p>
            <p><strong>NÃO DEVE:</strong> Assumir a alfabetização ou adaptação de conteúdo pedagógico.</p>
        </div>
        """, unsafe_allow_html=True)
        
    with c_ap:
        st.markdown("""
        <div class="info-card" style="border-left: 5px solid #3182CE; background-color: #EBF8FF;">
            <h3 style="color: #2B6CB0;">AP (Apoio Pedagógico)</h3>
            <p><strong>Escopo:</strong> Escolar / Educação.</p>
            <hr>
            <p>Profissional de apoio (Cuidador ou Estagiário) focado no acesso: higiene, alimentação, locomoção e organização do material.</p>
            <p><strong>NÃO DEVE:</strong> Ser responsável solitário pelo planejamento da aula.</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.info("💡 **Conceito Chave:** A presença do AT ou AP não isenta o **Professor Regente** da responsabilidade sobre o aprendizado do aluno.")
