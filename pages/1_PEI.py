# pages/1_PEI.py
import streamlit as st
from datetime import date, datetime
import json
import os

import omni_utils as ou
from pei_functions import *

# ✅ set_page_config UMA VEZ SÓ, SEMPRE no topo
st.set_page_config(
    page_title="Omnisfera | PEI",
    page_icon="📘",
    layout="wide",
    initial_sidebar_state="collapsed",
)

APP_VERSION = "v150.0 (SaaS Design)"

# ✅ UI lockdown (não quebra se faltar)
try:
    from ui_lockdown import hide_streamlit_chrome_if_needed, hide_default_sidebar_nav
    hide_streamlit_chrome_if_needed()
    hide_default_sidebar_nav()
except Exception:
    pass

# ==============================================================================
# CSS E ESTILOS
# ==============================================================================
def forcar_layout_hub():
    st.markdown("""
        <style>
            /* 1. Remove o cabeçalho padrão do Streamlit e a linha colorida */
            header[data-testid="stHeader"] {
                visibility: hidden !important;
                height: 0px !important;
            }

            /* 2. Puxa todo o conteúdo para cima (O SEGREDO ESTÁ AQUI) */
            .block-container {
                padding-top: 1rem !important;
                padding-bottom: 1rem !important;
                margin-top: 0px !important;
            }

            /* 3. Remove padding extra se houver container de navegação */
            div[data-testid="stVerticalBlock"] > div:first-child {
                padding-top: 0px !important;
            }
            
            /* 4. Esconde o menu hambúrguer e rodapé */
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
        </style>
    """, unsafe_allow_html=True)

# Tema PEI
PEI_ACCENT = "#4A6FA5"
PEI_ACCENT_DARK = "#3A5A8C"
PEI_ACCENT_SOFT = "#EEF2F7"

def inject_pei_css():
    st.markdown(f"""
    <style>
    :root {{
      --acc: {PEI_ACCENT};
      --accDark: {PEI_ACCENT_DARK};
      --accSoft: {PEI_ACCENT_SOFT};
    }}
    
    /* BOTÕES */
    .stButton > button[kind="primary"] {{
      background: linear-gradient(135deg, var(--acc), var(--accDark)) !important;
      border: none !important;
      color: #ffffff !important;
      font-weight: 700 !important;
      border-radius: 10px !important;
      transition: all .18s ease !important;
    }}
    .stButton > button[kind="primary"]:hover {{
      transform: translateY(-1px) !important;
      box-shadow: 0 10px 22px rgba(15,23,42,.25) !important;
    }}
    
    /* TABS — SEM UNDERLINE */
    .stTabs [aria-selected="true"] {{
      color: var(--accDark) !important;
      font-weight: 700 !important;
      background-color: transparent !important;
    }}
    
    .stTabs [aria-selected="true"]::after {{
      display: none !important;
    }}
    
    /* PROGRESS BAR */
    .progress-container {{
        margin: 10px 0 20px 0;
        padding: 0;
    }}
    
    .segmento-badge {{
        display: inline-block;
        padding: 4px 12px;
        border-radius: 12px;
        color: white;
        font-size: 0.8rem;
        font-weight: bold;
        margin-top: 5px;
    }}
    </style>
    """, unsafe_allow_html=True)

# ==============================================================================
# INICIALIZAÇÃO
# ==============================================================================
def init_session_state():
    """Inicializa o estado da sessão"""
    default_state = {
        "nome": "",
        "nasc": date(2015, 1, 1),
        "serie": None,
        "turma": "",
        "diagnostico": "",
        "lista_medicamentos": [],
        "composicao_familiar_tags": [],
        "historico": "",
        "familia": "",
        "hiperfoco": "",
        "potencias": [],
        "rede_apoio": [],
        "orientacoes_especialistas": "",
        "orientacoes_por_profissional": {},
        "checklist_evidencias": {},
        "nivel_alfabetizacao": "Não se aplica (Educação Infantil)",
        "barreiras_selecionadas": {k: [] for k in LISTAS_BARREIRAS.keys()},
        "niveis_suporte": {},
        "observacoes_barreiras": {},
        "estrategias_acesso": [],
        "estrategias_ensino": [],
        "estrategias_avaliacao": [],
        "ia_sugestao": "",
        "ia_mapa_texto": "",
        "outros_acesso": "",
        "outros_ensino": "",
        "monitoramento_data": date.today(),
        "status_meta": "Não Iniciado",
        "parecer_geral": "Manter Estratégias",
        "proximos_passos_select": [],
        "status_validacao_pei": "rascunho",
        "feedback_ajuste": "",
        "status_validacao_game": "rascunho",
        "feedback_ajuste_game": "",
        "matricula": "",
        "meds_extraidas_tmp": [],
        "status_meds_extraidas": "idle",
    }
    
    if "dados" not in st.session_state:
        st.session_state.dados = default_state
    else:
        for k, v in default_state.items():
            if k not in st.session_state.dados:
                st.session_state.dados[k] = v
    
    st.session_state.setdefault("pdf_text", "")
    st.session_state.setdefault("selected_student_id", None)
    st.session_state.setdefault("selected_student_name", "")

# ==============================================================================
# FUNÇÕES DE RENDERIZAÇÃO
# ==============================================================================
def render_header():
    """Renderiza o cabeçalho e navbar"""
    ou.render_omnisfera_header()
    ou.render_navbar(active_tab="Estratégias & PEI")
    ou.inject_compact_app_css()

def render_hero_card():
    """Renderiza o card hero"""
    hora = datetime.now().hour
    saudacao = "Bom dia" if 5 <= hora < 12 else "Boa tarde" if 12 <= hora < 18 else "Boa noite"
    USUARIO_NOME = st.session_state.get("usuario_nome", "Visitante").split()[0]
    WORKSPACE_NAME = st.session_state.get("workspace_name", "Workspace")
    
    st.markdown(f"""
    <div class="mod-card-wrapper">
        <div class="mod-card-rect">
            <div class="mod-bar c-blue"></div>
            <div class="mod-icon-area bg-blue-soft">
                <i class="ri-book-open-fill"></i>
            </div>
            <div class="mod-content">
                <div class="mod-title">Plano Educacional Individualizado (PEI)</div>
                <div class="mod-desc">
                    {saudacao}, <strong>{USUARIO_NOME}</strong>! Crie e gerencie Planos Educacionais Individualizados 
                    para estudantes do workspace <strong>{WORKSPACE_NAME}</strong>. 
                    Desenvolva estratégias personalizadas e acompanhe o progresso de cada aluno.
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_progress_bar():
    """Renderiza a barra de progresso"""
    def calcular_progresso() -> int:
        try:
            dados = st.session_state.get("dados", {}) or {}
            campos = ["nome", "nasc", "turma", "ano"]
            total = len(campos)
            ok = sum(1 for c in campos if dados.get(c))
            return int(round((ok / total) * 100)) if total else 0
        except Exception:
            return 0
    
    p = max(0, min(100, int(calcular_progresso())))
    
    st.markdown(f"""
    <div class="progress-container">
        <div style="width:100%; height:8px; background:#E2E8F0; border-radius:4px; position:relative; margin:10px 0 20px 0;">
            <div style="height:8px; width:{p}%; background:linear-gradient(90deg, var(--acc), var(--accDark)); border-radius:4px;"></div>
            <div style="position:absolute; top:-5px; left:{p}%; transform:translateX(-50%); font-size:0.8rem; font-weight:bold; color:var(--accDark);">
                {p}%
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ==============================================================================
# ABA INÍCIO
# ==============================================================================
def render_aba_inicio():
    """Renderiza a aba Início"""
    st.markdown("### 🏛️ Central de Fundamentos e Gestão")
    st.caption("Aqui você gerencia alunos (backup local e nuvem/Supabase) e acessa fundamentos do PEI.")
    
    col_left, col_right = st.columns([1.15, 0.85])
    
    with col_left:
        with st.container(border=True):
            st.markdown("#### 📚 Fundamentos do PEI")
            st.markdown("""
            - O **PEI** organiza o planejamento individualizado com foco em **barreiras** e **apoios**.
            - A lógica é **equidade**: ajustar **acesso, ensino e avaliação**, sem baixar expectativas.
            - Base: **LBI (Lei 13.146/2015)**, LDB e diretrizes de Educação Especial na Perspectiva Inclusiva.
            """)
        
        with st.container(border=True):
            st.markdown("#### 🧭 Como usar a Omnisfera")
            st.markdown("""
            1) **Estudante**: identificação + contexto + laudo (opcional)  
            2) **Evidências**: o que foi observado e como aparece na rotina  
            3) **Mapeamento**: barreiras + nível de apoio + potências  
            4) **Plano de Ação**: acesso/ensino/avaliação  
            5) **Consultoria IA**: gerar o documento técnico (validação do educador)  
            6) **Dashboard**: KPIs + exportações + sincronização  
            """)
    
    with col_right:
        st.markdown("#### 👤 Gestão de Alunos")
        
        # Status vínculo
        student_id = st.session_state.get("selected_student_id")
        if student_id:
            st.success("✅ Aluno vinculado ao Supabase (nuvem)")
            st.caption(f"student_id: {str(student_id)[:8]}...")
        else:
            st.warning("📝 Modo rascunho (sem vínculo na nuvem)")
        
        # Backup Local
        with st.container(border=True):
            st.markdown("##### 1) Carregar Backup Local (.JSON)")
            st.caption("✅ Não comunica com Supabase. Envie o arquivo e clique em **Carregar no formulário**.")
            
            up_json = st.file_uploader(
                "Envie um arquivo .json",
                type="json",
                key="inicio_uploader_json",
            )
            
            if up_json is not None:
                try:
                    payload = json.load(up_json)
                    # Aplicar dados
                    if st.button("📥 Carregar no formulário", type="primary", use_container_width=True):
                        st.session_state.dados.update(payload)
                        st.session_state["selected_student_id"] = None
                        st.success("Backup aplicado ao formulário ✅")
                        st.rerun()
                except Exception as e:
                    st.error(f"Erro ao ler JSON: {e}")

# ==============================================================================
# ABA ESTUDANTE
# ==============================================================================
def render_aba_estudante():
    """Renderiza a aba Estudante"""
    st.markdown("### <i class='ri-user-smile-line'></i> Dossiê do Estudante", unsafe_allow_html=True)
    
    d = st.session_state.dados
    
    # Identificação
    c1, c2, c3, c4, c5 = st.columns([3, 2, 2, 1, 2])
    
    d["nome"] = c1.text_input("Nome Completo", d.get("nome", ""))
    d["nasc"] = c2.date_input("Nascimento", value=d.get("nasc", date(2015, 1, 1)))
    
    # Série/Ano
    try:
        serie_idx = LISTA_SERIES.index(d.get("serie")) if d.get("serie") in LISTA_SERIES else 0
    except:
        serie_idx = 0
    
    d["serie"] = c3.selectbox("Série/Ano", LISTA_SERIES, index=serie_idx, placeholder="Selecione...")
    
    # Segmento guiado
    if d.get("serie"):
        seg_nome, seg_cor, seg_desc = get_segmento_info_visual(d["serie"])
        c3.markdown(
            f"<div class='segmento-badge' style='background-color:{seg_cor}'>{seg_nome}</div>",
            unsafe_allow_html=True
        )
        st.caption(seg_desc)
    
    d["turma"] = c4.text_input("Turma", d.get("turma", ""))
    d["matricula"] = c5.text_input("Matrícula / RA", d.get("matricula", ""), placeholder="Ex: 2026-001234")
    
    st.divider()
    
    # Histórico & Família
    st.markdown("##### Histórico & Contexto Familiar")
    c_hist, c_fam = st.columns(2)
    d["historico"] = c_hist.text_area("Histórico Escolar", d.get("historico", ""))
    d["familia"] = c_fam.text_area("Dinâmica Familiar", d.get("familia", ""))
    
    default_familia_valido = [x for x in d.get("composicao_familiar_tags", []) if x in LISTA_FAMILIA]
    d["composicao_familiar_tags"] = st.multiselect(
        "Quem convive com o aluno?",
        LISTA_FAMILIA,
        default=default_familia_valido,
        help="Incluímos Mãe 1 / Mãe 2 e Pai 1 / Pai 2 para famílias diversas."
    )
    
    st.divider()
    
    # Laudo PDF
    st.markdown("##### 📎 Laudo (PDF) + Extração Inteligente")
    
    col_pdf, col_action = st.columns([2, 1], vertical_alignment="center")
    
    with col_pdf:
        up = st.file_uploader(
            "Arraste o arquivo aqui",
            type="pdf",
            label_visibility="collapsed",
            key="pei_laudo_pdf_uploader_tab1",
        )
        if up:
            st.session_state.pdf_text = ler_pdf(up)
            if st.session_state.pdf_text:
                st.success("PDF lido ✅ (usando até 6 páginas)")
    
    with col_action:
        st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
        if st.button("✨ Extrair Dados do Laudo", type="primary", use_container_width=True,
                    disabled=(not st.session_state.get("pdf_text"))):
            with st.spinner("Analisando laudo..."):
                dados_extraidos, erro = extrair_dados_pdf_ia(st.secrets.get("OPENAI_API_KEY", ""), 
                                                           st.session_state.pdf_text)
            
            if dados_extraidos:
                diag = (dados_extraidos.get("diagnostico") or "").strip()
                if diag:
                    d["diagnostico"] = diag
                    st.success("Diagnóstico extraído ✅")
                st.rerun()
            else:
                st.error(f"Erro: {erro}")
    
    st.divider()
    
    # Contexto Clínico
    st.markdown("##### Contexto Clínico")
    d["diagnostico"] = st.text_input("Diagnóstico", d.get("diagnostico", ""))

# ==============================================================================
# ABA EVIDÊNCIAS
# ==============================================================================
def render_aba_evidencias():
    """Renderiza a aba Evidências"""
    st.markdown("### <i class='ri-search-eye-line'></i> Coleta de Evidências", unsafe_allow_html=True)
    
    d = st.session_state.dados
    atual = d.get("nivel_alfabetizacao")
    idx = LISTA_ALFABETIZACAO.index(atual) if atual in LISTA_ALFABETIZACAO else 0
    d["nivel_alfabetizacao"] = st.selectbox("Hipótese de Escrita", LISTA_ALFABETIZACAO, index=idx)
    
    st.divider()
    c1, c2, c3 = st.columns(3)
    
    def _tog(label):
        d["checklist_evidencias"][label] = st.toggle(
            label,
            value=d["checklist_evidencias"].get(label, False),
        )
    
    with c1:
        st.markdown("**Pedagógico**")
        for q in ["Estagnação na aprendizagem", "Lacuna em pré-requisitos", 
                 "Dificuldade de generalização", "Dificuldade de abstração"]:
            _tog(q)
    
    with c2:
        st.markdown("**Cognitivo**")
        for q in ["Oscilação de foco", "Fadiga mental rápida", 
                 "Dificuldade de iniciar tarefas", "Esquecimento recorrente"]:
            _tog(q)
    
    with c3:
        st.markdown("**Comportamental**")
        for q in ["Dependência de mediação (1:1)", "Baixa tolerância à frustração", 
                 "Desorganização de materiais", "Recusa de tarefas"]:
            _tog(q)
    
    st.divider()
    st.markdown("##### Observações rápidas")
    d["orientacoes_especialistas"] = st.text_area(
        "Registre observações de professores e especialistas (se houver)",
        d.get("orientacoes_especialistas", ""),
        height=120,
    )

# ==============================================================================
# FUNÇÃO PRINCIPAL
# ==============================================================================
def main():
    # Configuração inicial
    forcar_layout_hub()
    inject_pei_css()
    
    # Verificar login
    if "autenticado" not in st.session_state or not st.session_state["autenticado"]:
        st.error("🔒 Acesso Negado. Faça login na Página Inicial.")
        st.stop()
    
    # Inicializar estado
    init_session_state()
    
    # Renderizar cabeçalho
    render_header()
    
    # Renderizar card hero
    render_hero_card()
    
    # Definir abas (BARRA DE PROGRESSO VAI AQUI DEPOIS DAS ABAS)
    abas = ["INÍCIO", "ESTUDANTE", "EVIDÊNCIAS", "REDE DE APOIO", "MAPEAMENTO",
            "PLANO DE AÇÃO", "MONITORAMENTO", "CONSULTORIA IA", "DASHBOARD & DOCS", "JORNADA GAMIFICADA"]
    
    # Criar tabs
    tabs = st.tabs(abas)
    
    # BARRA DE PROGRESSO - AGORA ABAIXO DAS ABAS
    render_progress_bar()
    
    # Renderizar cada aba
    with tabs[0]:
        render_aba_inicio()
    
    with tabs[1]:
        render_aba_estudante()
    
    with tabs[2]:
        render_aba_evidencias()
    
    # Nota: As outras abas precisarão ser refatoradas seguindo o mesmo padrão
    # Para manter o código gerenciável, recomendo criar uma função para cada aba

if __name__ == "__main__":
    main()
