import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# ==============================================================================
# 1. SETUP & CSS (Gamified UI - Clean & Modern)
# ==============================================================================
st.set_page_config(page_title="Omnisfera | Codex", page_icon="🧩", layout="wide")

st.markdown("""
<style>
    /* Estilo "Glassmorphism" para os Cards */
    .game-card {
        background: rgba(255, 255, 255, 0.9);
        border: 1px solid #E2E8F0;
        border-radius: 16px;
        padding: 24px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        margin-bottom: 20px;
        transition: all 0.3s ease;
    }
    .game-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 15px rgba(0, 0, 0, 0.1);
        border-color: #0F52BA;
    }

    /* Tipografia de Interface de Jogo */
    h1, h2, h3 { font-family: 'Nunito', sans-serif; }
    .level-title { 
        color: #0F52BA; 
        font-weight: 800; 
        text-transform: uppercase; 
        letter-spacing: 1.5px;
        font-size: 0.9rem;
    }
    
    /* Badges de Atributos */
    .badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: bold;
        margin-right: 5px;
    }
    .badge-blue { background-color: #E3F2FD; color: #1565C0; }
    .badge-red { background-color: #FFEBEE; color: #C62828; }
    .badge-purple { background-color: #F3E5F5; color: #7B1FA2; }

</style>
""", unsafe_allow_html=True)

# ==============================================================================
# 2. HEADER: A MISSÃO
# ==============================================================================
c1, c2 = st.columns([3, 1])
with c1:
    st.markdown('<p class="level-title">Omnisfera Knowledge Base</p>', unsafe_allow_html=True)
    st.title("🗺️ Codex da Inclusão")
    st.markdown("**Design Thinking Aplicado:** O foco sai da *deficiência* e vai para a *interação* entre o sujeito e o ambiente.")

with c2:
    # Barra de Progresso "Level do Educador"
    st.caption("Nível de Acessibilidade da Escola")
    st.progress(65)

# Navegação Gamificada
tab_avatar, tab_inventory, tab_rules, tab_party = st.tabs([
    "👤 O Aluno (Avatar)", 
    "🎒 Inventário (Estratégias)", 
    "📜 Regras do Jogo (Legal)",
    "🛡️ Sua Party (Equipe)"
])

# ==============================================================================
# 3. ABA AVATAR: EMPATIA & RADAR CHART
# ==============================================================================
with tab_avatar:
    st.markdown("### 1. Mapa de Potencialidades (Design Thinking: Empatia)")
    st.markdown("Esqueça o laudo médico por um minuto. Quem é esse jogador? Onde ele brilha?")
    
    col_chart, col_desc = st.columns([1, 1])
    
    with col_chart:
        # GRÁFICO DE RADAR (RPG STYLE)
        # Isso muda a visão de "Deficit" para "Perfil Multidimensional"
        categories = ['Comunicação', 'Socialização', 'Vida Diária', 'Motor', 'Cognitivo', 'Artístico']
        
        # Exemplo de Perfil (Isso viria do Banco de Dados no futuro)
        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(
            r=[3, 2, 4, 3, 5, 5],
            theta=categories,
            fill='toself',
            name='Perfil do Aluno',
            line_color='#0F52BA'
        ))
        
        fig.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 5])),
            showlegend=False,
            height=300,
            margin=dict(l=40, r=40, t=20, b=20)
        )
        st.plotly_chart(fig, use_container_width=True)

    with col_desc:
        st.markdown("""
        <div class="game-card">
            <h4>🧠 Perfil: Hiperfoco Criativo</h4>
            <p>Este aluno possui <strong>Altas Habilidades</strong> em reconhecimento de padrões visuais, mas enfrenta barreiras em <strong>Socialização</strong>.</p>
            <hr>
            <p><span class="badge badge-purple">Superpoder</span> Memória Fotográfica</p>
            <p><span class="badge badge-red">Vulnerabilidade</span> Ruído Alto (Sensorial)</p>
            <p><span class="badge badge-blue">Interesse</span> Minecraft & Lego</p>
            <br>
            <small><em>"A deficiência não está na pessoa, mas na falta de recursos do ambiente." (LBI - Lei 13.146)</em></small>
        </div>
        """, unsafe_allow_html=True)

# ==============================================================================
# 4. ABA INVENTÁRIO: ESTRATÉGIAS COMO EQUIPAMENTOS
# ==============================================================================
with tab_inventory:
    st.markdown("### 2. Inventário de Recursos (Ideação)")
    st.markdown("Como Level Designer, quais ferramentas você oferece para o jogador superar a fase?")

    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown("""
        <div class="game-card" style="border-top: 4px solid #FF4B4B;">
            <h4>⏱️ O Timer Visual</h4>
            <p><strong>Tipo:</strong> Item de Apoio (Tempo)</p>
            <p><strong>Efeito:</strong> Reduz ansiedade em 40%.</p>
            <p><strong>Uso:</strong> Marcar o fim de uma tarefa.</p>
            <small><em>Para: TDAH e TEA.</em></small>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown("""
        <div class="game-card" style="border-top: 4px solid #0F52BA;">
            <h4>📝 Pauta Ampliada</h4>
            <p><strong>Tipo:</strong> Modificador de Ambiente</p>
            <p><strong>Efeito:</strong> Aumenta precisão motora.</p>
            <p><strong>Uso:</strong> Caderno com linhas espaçadas.</p>
            <small><em>Para: Baixa Visão e Disgrafia.</em></small>
        </div>
        """, unsafe_allow_html=True)

    with c3:
        st.markdown("""
        <div class="game-card" style="border-top: 4px solid #00CC96;">
            <h4>🎧 Fone Cancelador</h4>
            <p><strong>Tipo:</strong> Escudo Sensorial</p>
            <p><strong>Efeito:</strong> Bloqueia ruído de fundo.</p>
            <p><strong>Uso:</strong> Momentos de leitura e prova.</p>
            <small><em>Para: Hipersensibilidade Auditiva.</em></small>
        </div>
        """, unsafe_allow_html=True)
    
    with st.expander("🛠️ Ver Kit Completo de Adaptações Curriculares"):
        st.markdown("""
        * **Adaptação de Objetivo:** Mudar "o quê" se ensina (ex: focar na oralidade em vez da escrita).
        * **Adaptação Temporal:** Mudar "quanto tempo" se tem (flexibilidade nas provas).
        * **Adaptação Avaliativa:** Mudar "como" se prova o saber (portfólio, vídeo, projeto).
        """)

# ==============================================================================
# 5. ABA REGRAS: O SISTEMA (LEIS)
# ==============================================================================
with tab_rules:
    st.markdown("### 3. As Regras do Mundo (Fundamentos Legais)")
    st.markdown("Nenhum jogo funciona sem regras claras. A legislação é o nosso 'Rulebook'.")

    # Accordion com Estilo Limpo
    with st.expander("📜 A Constituição (Regra Mãe)", expanded=True):
        st.info("**Art. 205:** A educação é direito de todos. Não existe 'aluno inelegível' para a escola regular.")
    
    with st.expander("⚖️ LBI - Lei Brasileira de Inclusão (O Balanceamento)"):
        st.write("""
        Define que a deficiência é o resultado da interação entre impedimentos do corpo e **barreiras** do mundo. 
        Se removemos a barreira, a deficiência deixa de ser um fator limitante para a participação.
        """)
        
    with st.expander("📘 PEI vs. PAEE (Documentação de Quest)"):
        st.markdown("""
        **PEI (Plano Educacional Individualizado):** O mapa da sala de aula. Responsabilidade do Regente.
        **PAEE (Plano de AEE):** O mapa da Sala de Recursos. Foca em ferramentas e autonomia.
        """)

# ==============================================================================
# 6. ABA PARTY: GESTÃO DE EQUIPE
# ==============================================================================
with tab_party:
    st.markdown("### 4. Sua Party (Equipe Multidisciplinar)")
    st.markdown("Sozinho você não termina essa Raid. Defina os papéis para evitar 'fogo amigo'.")

    col_team1, col_team2 = st.columns(2)

    with col_team1:
        st.markdown("""
        <div class="game-card" style="background-color: #F0F7FF;">
            <h3 style="color: #0F52BA;">🛡️ Tank/Support (AP)</h3>
            <p><strong>Apoio Pedagógico / Escolar</strong></p>
            <ul style="font-size: 0.9rem;">
                <li><strong>Missão:</strong> Garantir acesso ao currículo.</li>
                <li><strong>Skill:</strong> Organização, higiene, locomoção.</li>
                <li><strong>Vínculo:</strong> Contratado da Escola.</li>
            </ul>
            <small><em>"O AP é os braços e pernas extras, mas a cabeça da aula é do professor."</em></small>
        </div>
        """, unsafe_allow_html=True)

    with col_team2:
        st.markdown("""
        <div class="game-card" style="background-color: #FFF5F5;">
            <h3 style="color: #FF4B4B;">⚕️ Healer (AT)</h3>
            <p><strong>Acompanhante Terapêutico</strong></p>
            <ul style="font-size: 0.9rem;">
                <li><strong>Missão:</strong> Saúde e Comportamento.</li>
                <li><strong>Skill:</strong> Manejo de crises, regulação emocional.</li>
                <li><strong>Vínculo:</strong> Externo (Saúde/Família).</li>
            </ul>
             <small><em>"Foca na clínica, não no pedagógico."</em></small>
        </div>
        """, unsafe_allow_html=True)
    
    st.success("💡 **Dica de Guilda:** O **Professor Regente** é o Líder da Party. Ele não pode terceirizar o ensino do aluno para o AP ou AT. A responsabilidade pedagógica é dele!")

# Footer
st.markdown("---")
st.caption("Omnisfera Level Design • Design Thinking for Education • Baseado na LBI e Diretrizes de Acessibilidade")
