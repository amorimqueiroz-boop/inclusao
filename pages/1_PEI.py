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
# 12. ABA ESTUDANTE
# ==============================================================================
  
with tab1:
    st.markdown("### <i class='ri-user-smile-line'></i> Dossiê do Estudante", unsafe_allow_html=True)

    # Garantias (caso algo não tenha entrado no default_state)
    st.session_state.dados.setdefault("matricula", "")
    st.session_state.dados.setdefault("meds_extraidas_tmp", [])
    st.session_state.dados.setdefault("status_meds_extraidas", "idle")

    # =========================
    # Funções de apoio da aba
    # =========================
    def detectar_segmento(serie_str: str) -> str:
        """Retorna: EI | EFI | EFII | EM"""
        if not serie_str:
            return "INDEFINIDO"
        s = serie_str.lower()
        if "infantil" in s:
            return "EI"
        if "1º ano" in s or "2º ano" in s or "3º ano" in s or "4º ano" in s or "5º ano" in s:
            return "EFI"
        if "6º ano" in s or "7º ano" in s or "8º ano" in s or "9º ano" in s:
            return "EFII"
        if "série" in s or "médio" in s or "eja" in s:
            return "EM"
        return "INDEFINIDO"

    def get_segmento_info_visual_v2(serie: str):
        seg = detectar_segmento(serie)
        if seg == "EI":
            return "Educação Infantil", "#4299e1", "Foco: Campos de Experiência (BNCC) e rotina estruturante."
        if seg == "EFI":
            return "Ensino Fundamental — Anos Iniciais", "#48bb78", "Foco: alfabetização, numeracia e consolidação de habilidades basais."
        if seg == "EFII":
            return "Ensino Fundamental — Anos Finais", "#ed8936", "Foco: autonomia, funções executivas, organização e aprofundamento conceitual."
        if seg == "EM":
            return "Ensino Médio / EJA", "#9f7aea", "Foco: projeto de vida, áreas do conhecimento e estratégias de estudo."
        return "Selecione a Série/Ano", "#718096", "Aguardando seleção..."

    def _normalizar_med(m: dict):
        return {
            "nome": (m.get("nome") or "").strip(),
            "posologia": (m.get("posologia") or "").strip(),
            "escola": bool(m.get("escola", False)),
        }

    def _ja_existe_med(lista, nome):
        nome_norm = (nome or "").strip().lower()
        if not nome_norm:
            return True
        return any((x.get("nome") or "").strip().lower() == nome_norm for x in (lista or []))

    # =========================
    # Identificação
    # =========================
    c1, c2, c3, c4, c5 = st.columns([3, 2, 2, 1, 2])

    st.session_state.dados["nome"] = c1.text_input("Nome Completo", st.session_state.dados.get("nome", ""))
    st.session_state.dados["nasc"] = c2.date_input("Nascimento", value=st.session_state.dados.get("nasc", date(2015, 1, 1)))

    # Série/Ano
    try:
        serie_idx = LISTA_SERIES.index(st.session_state.dados.get("serie")) if st.session_state.dados.get("serie") in LISTA_SERIES else 0
    except:
        serie_idx = 0

    st.session_state.dados["serie"] = c3.selectbox("Série/Ano", LISTA_SERIES, index=serie_idx, placeholder="Selecione...")

    # Segmento guiado (badge + descrição)
    if st.session_state.dados.get("serie"):
        seg_nome, seg_cor, seg_desc = get_segmento_info_visual_v2(st.session_state.dados["serie"])
        c3.markdown(
            f"<div class='segmento-badge' style='background-color:{seg_cor}'>{seg_nome}</div>",
            unsafe_allow_html=True
        )
        st.caption(seg_desc)

    st.session_state.dados["turma"] = c4.text_input("Turma", st.session_state.dados.get("turma", ""))

    # Matrícula / RA
    st.session_state.dados["matricula"] = c5.text_input("Matrícula / RA", st.session_state.dados.get("matricula", ""), placeholder="Ex: 2026-001234")

    st.divider()

    # =========================
    # Histórico & Família
    # =========================
    st.markdown("##### Histórico & Contexto Familiar")
    c_hist, c_fam = st.columns(2)
    st.session_state.dados["historico"] = c_hist.text_area("Histórico Escolar", st.session_state.dados.get("historico", ""))
    st.session_state.dados["familia"] = c_fam.text_area("Dinâmica Familiar", st.session_state.dados.get("familia", ""))

    default_familia_valido = [x for x in st.session_state.dados.get("composicao_familiar_tags", []) if x in LISTA_FAMILIA]
    st.session_state.dados["composicao_familiar_tags"] = st.multiselect(
        "Quem convive com o aluno?",
        LISTA_FAMILIA,
        default=default_familia_valido,
        help="Incluímos Mãe 1 / Mãe 2 e Pai 1 / Pai 2 para famílias diversas."
    )

    st.divider()

    # =========================
    # Laudo PDF + Extração IA
    # =========================
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
            else:
                st.warning("Não consegui extrair texto do PDF (pode estar escaneado/imagem).")

    with col_action:
        st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
        cbtn1, cbtn2, cbtn3 = st.columns([1, 2, 1])
        with cbtn2:
            extrair = st.button(
                "✨ Extrair Dados do Laudo",
                type="primary",
                use_container_width=True,
                disabled=(not st.session_state.get("pdf_text")),
                key="btn_extrair_laudo_tab1",
            )

        if extrair:
            with st.spinner("Analisando laudo..."):
                dados_extraidos, erro = extrair_dados_pdf_ia(api_key, st.session_state.pdf_text)

            if dados_extraidos:
                # 1) Diagnóstico: preencher o campo existente
                diag = (dados_extraidos.get("diagnostico") or "").strip()
                if diag:
                    st.session_state.dados["diagnostico"] = diag

                # 2) Medicações: preparar revisão (não inserir direto)
                meds = dados_extraidos.get("medicamentos") or []
                meds_norm = []
                for med in meds:
                    m = _normalizar_med(med)
                    if m["nome"]:
                        meds_norm.append(m)

                st.session_state.dados["meds_extraidas_tmp"] = meds_norm
                st.session_state.dados["status_meds_extraidas"] = "review" if meds_norm else "idle"

                st.success("Dados extraídos ✅ (revise as medicações abaixo)")
                st.rerun()
            else:
                st.error(f"Erro: {erro}")

    # Revisão das meds extraídas (antes de inserir na lista oficial)
    if st.session_state.dados.get("status_meds_extraidas") == "review":
        meds_tmp = st.session_state.dados.get("meds_extraidas_tmp", [])

        with st.container(border=True):
            st.markdown("**💊 Medicações encontradas no laudo (confirme antes de adicionar)**")

            if not meds_tmp:
                st.info("Nenhuma medicação identificada.")
                st.session_state.dados["status_meds_extraidas"] = "idle"
            else:
                for i, m in enumerate(meds_tmp):
                    cc1, cc2, cc3 = st.columns([3, 2, 1.5])
                    m["nome"] = cc1.text_input("Nome", value=m.get("nome", ""), key=f"tmp_med_nome_{i}")
                    m["posologia"] = cc2.text_input("Posologia", value=m.get("posologia", ""), key=f"tmp_med_pos_{i}")
                    m["escola"] = cc3.checkbox("Na escola?", value=bool(m.get("escola", False)), key=f"tmp_med_esc_{i}")

                a1, a2, a3 = st.columns([2, 2, 2])

                if a1.button("✅ Adicionar ao PEI", type="primary", use_container_width=True, key="btn_add_meds_tmp"):
                    # inserir no campo existente: lista_medicamentos (sem duplicar por nome)
                    lista_atual = st.session_state.dados.get("lista_medicamentos", [])
                    for m in meds_tmp:
                        m = _normalizar_med(m)
                        if m["nome"] and not _ja_existe_med(lista_atual, m["nome"]):
                            lista_atual.append(m)

                    st.session_state.dados["lista_medicamentos"] = lista_atual
                    st.session_state.dados["meds_extraidas_tmp"] = []
                    st.session_state.dados["status_meds_extraidas"] = "idle"
                    st.success("Medicações adicionadas ✅")
                    st.rerun()

                if a2.button("🧹 Limpar lista extraída", use_container_width=True, key="btn_clear_meds_tmp"):
                    st.session_state.dados["meds_extraidas_tmp"] = []
                    st.session_state.dados["status_meds_extraidas"] = "idle"
                    st.rerun()

                if a3.button("↩️ Voltar sem adicionar", use_container_width=True, key="btn_back_meds_tmp"):
                    st.session_state.dados["status_meds_extraidas"] = "idle"
                    st.rerun()

    st.divider()

    # =========================
    # Contexto Clínico + Medicação (campo EXISTENTE)
    # =========================
    st.markdown("##### Contexto Clínico")
    st.session_state.dados["diagnostico"] = st.text_input("Diagnóstico", st.session_state.dados.get("diagnostico", ""))

    with st.container(border=True):
        usa_med = st.toggle(
            "💊 O aluno faz uso contínuo de medicação?",
            value=len(st.session_state.dados.get("lista_medicamentos", [])) > 0,
            key="toggle_usa_med_tab1"
        )

        if usa_med:
            cmed1, cmed2, cmed3 = st.columns([3, 2, 2])
            nm = cmed1.text_input("Nome", key="nm_med_manual")
            pos = cmed2.text_input("Posologia", key="pos_med_manual")
            admin_escola = cmed3.checkbox("Na escola?", key="adm_esc_manual")

            if st.button("Adicionar", key="btn_add_med_manual"):
                if nm.strip():
                    # não duplicar por nome
                    if not _ja_existe_med(st.session_state.dados.get("lista_medicamentos", []), nm):
                        st.session_state.dados["lista_medicamentos"].append(
                            {"nome": nm.strip(), "posologia": pos.strip(), "escola": admin_escola}
                        )
                    st.rerun()

        if st.session_state.dados.get("lista_medicamentos"):
            st.write("---")
            for i, m in enumerate(st.session_state.dados["lista_medicamentos"]):
                tag = " [NA ESCOLA]" if m.get("escola") else ""
                c_txt, c_btn = st.columns([5, 1])
                c_txt.info(f"💊 **{m.get('nome','')}** ({m.get('posologia','')}){tag}")
                if c_btn.button("Excluir", key=f"del_med_{i}"):
                    st.session_state.dados["lista_medicamentos"].pop(i)
                    st.rerun()
# ==============================================================================
# 13. ABA EVIDÊNCIAS (COMPLETA)
# ==============================================================================
with tab2:
    st.markdown("### <i class='ri-search-eye-line'></i> Coleta de Evidências", unsafe_allow_html=True)

    atual = st.session_state.dados.get("nivel_alfabetizacao")
    idx = LISTA_ALFABETIZACAO.index(atual) if atual in LISTA_ALFABETIZACAO else 0
    st.session_state.dados["nivel_alfabetizacao"] = st.selectbox("Hipótese de Escrita", LISTA_ALFABETIZACAO, index=idx)

    st.divider()
    c1, c2, c3 = st.columns(3)

    def _tog(label):
        st.session_state.dados["checklist_evidencias"][label] = st.toggle(
            label,
            value=st.session_state.dados["checklist_evidencias"].get(label, False),
        )

    with c1:
        st.markdown("**Pedagógico**")
        for q in [
            "Estagnação na aprendizagem",
            "Lacuna em pré-requisitos",
            "Dificuldade de generalização",
            "Dificuldade de abstração",
        ]:
            _tog(q)

    with c2:
        st.markdown("**Cognitivo**")
        for q in [
            "Oscilação de foco",
            "Fadiga mental rápida",
            "Dificuldade de iniciar tarefas",
            "Esquecimento recorrente",
        ]:
            _tog(q)

    with c3:
        st.markdown("**Comportamental**")
        for q in [
            "Dependência de mediação (1:1)",
            "Baixa tolerância à frustração",
            "Desorganização de materiais",
            "Recusa de tarefas",
        ]:
            _tog(q)

    st.divider()
    st.markdown("##### Observações rápidas")
    st.session_state.dados["orientacoes_especialistas"] = st.text_area(
        "Registre observações de professores e especialistas (se houver)",
        st.session_state.dados.get("orientacoes_especialistas", ""),
        height=120,
    )

# ==============================================================================
# 14. ABA REDE DE APOIO (COMPLETA)
# ==============================================================================
with tab3:
    st.markdown("### <i class='ri-team-line'></i> Rede de Apoio", unsafe_allow_html=True)

    # Garantias (caso algo não tenha entrado no default_state)
    st.session_state.dados.setdefault("rede_apoio", [])
    st.session_state.dados.setdefault("orientacoes_especialistas", "")
    st.session_state.dados.setdefault("orientacoes_por_profissional", {})

    st.caption("Selecione os profissionais envolvidos e registre as orientações específicas de cada um.")

    # 1) Seleção da rede
    selecionados = st.multiselect(
        "Profissionais:",
        LISTA_PROFISSIONAIS,
        default=[p for p in st.session_state.dados.get("rede_apoio", []) if p in LISTA_PROFISSIONAIS],
        help="Ao selecionar um profissional, um campo de observação individual aparece abaixo."
    )
    st.session_state.dados["rede_apoio"] = selecionados

    # 2) Limpeza automática de chaves que não existem mais
    # (se o usuário desmarcar um profissional, removemos o texto dele do dicionário)
    orient_map = st.session_state.dados.get("orientacoes_por_profissional", {})
    orient_map = {k: v for k, v in orient_map.items() if k in selecionados}
    st.session_state.dados["orientacoes_por_profissional"] = orient_map

    st.divider()

    # 3) Campo geral (opcional) — mantém compatibilidade com o legado
    with st.expander("🗒️ Anotações gerais (opcional)", expanded=False):
        st.session_state.dados["orientacoes_especialistas"] = st.text_area(
            "Orientações clínicas gerais / resumo",
            st.session_state.dados.get("orientacoes_especialistas", ""),
            placeholder="Use para observações gerais da equipe (ex.: acordos com a família, encaminhamentos, alinhamentos).",
            height=140,
            key="txt_orientacoes_gerais_rede"
        )

    # 4) Campos individuais por profissional
    st.markdown("#### 📌 Orientações por profissional")
    if not selecionados:
        st.info("Selecione ao menos um profissional para habilitar os campos de observação.")
    else:
        # Layout em cards (2 colunas)
        cols = st.columns(2)
        for i, prof in enumerate(selecionados):
            alvo = cols[i % 2]
            with alvo:
                icon = get_pro_icon(prof) if "get_pro_icon" in globals() else "👤"
                with st.container(border=True):
                    st.markdown(f"**{icon} {prof}**")

                    st.session_state.dados["orientacoes_por_profissional"].setdefault(prof, "")

                    st.session_state.dados["orientacoes_por_profissional"][prof] = st.text_area(
                        "Observações / orientações",
                        value=st.session_state.dados["orientacoes_por_profissional"].get(prof, ""),
                        placeholder="Ex.: recomendações de intervenção, frequência, sinais de alerta, ajustes para sala de aula...",
                        height=140,
                        key=f"txt_orient_{prof}"
                    )

                    c1, c2 = st.columns([1, 1])
                    if c1.button("🧹 Limpar", use_container_width=True, key=f"btn_limpar_{prof}"):
                        st.session_state.dados["orientacoes_por_profissional"][prof] = ""
                        st.rerun()

                    if c2.button("🗑️ Remover profissional", use_container_width=True, key=f"btn_remove_{prof}"):
                        # remove do multiselect
                        st.session_state.dados["rede_apoio"] = [x for x in st.session_state.dados["rede_apoio"] if x != prof]
                        # remove do dicionário
                        st.session_state.dados["orientacoes_por_profissional"].pop(prof, None)
                        st.rerun()

    st.divider()

    # 5) Resumo visual rápido
    if selecionados:
        resumo = []
        for p in selecionados:
            txt = (st.session_state.dados["orientacoes_por_profissional"].get(p) or "").strip()
            resumo.append(f"- **{p}**: {'✅ preenchido' if txt else '⚠️ vazio'}")
        st.markdown("##### ✅ Checklist de preenchimento")
        st.markdown("\n".join(resumo))


# ==============================================================================
# 15. ABA MAPEAMENTO (3 colunas | hiperfoco + potências + barreiras + nível de apoio + observações)
# ==============================================================================
with tab4:
    st.markdown("### <i class='ri-radar-line'></i> Mapeamento", unsafe_allow_html=True)
    st.caption("Mapeie forças, hiperfocos e barreiras. Para cada barreira selecionada, indique a intensidade de apoio necessária.")

    # -------------------------
    # Garantias de estado
    # -------------------------
    st.session_state.dados.setdefault("hiperfoco", "")
    st.session_state.dados.setdefault("potencias", [])
    st.session_state.dados.setdefault("barreiras_selecionadas", {k: [] for k in LISTAS_BARREIRAS.keys()})
    st.session_state.dados.setdefault("niveis_suporte", {})          # chave: f"{dominio}_{barreira}" -> valor
    st.session_state.dados.setdefault("observacoes_barreiras", {})   # texto livre por domínio

    # -------------------------
    # 1) POTENCIALIDADES + HIPERFOCO
    # -------------------------
    with st.container(border=True):
        st.markdown("#### 🌟 Potencialidades e Hiperfoco")
        c1, c2 = st.columns(2)

        st.session_state.dados["hiperfoco"] = c1.text_input(
            "Hiperfoco (se houver)",
            st.session_state.dados.get("hiperfoco", ""),
            placeholder="Ex.: Dinossauros, Minecraft, Mapas, Carros, Desenho..."
        )

        pot_validas = [p for p in st.session_state.dados.get("potencias", []) if p in LISTA_POTENCIAS]
        st.session_state.dados["potencias"] = c2.multiselect(
            "Potencialidades / Pontos fortes",
            LISTA_POTENCIAS,
            default=pot_validas
        )

    st.divider()

    st.markdown("#### 🧩 Barreiras e nível de apoio")
    st.caption("Selecione as barreiras observadas e defina o nível de apoio para a rotina escolar (não é DUA).")

    # -------------------------
    # 2) Renderização por domínio
    # -------------------------
    def render_dominio(dominio: str, opcoes: list[str]):
        with st.container(border=True):
            st.markdown(f"**{dominio}**")

            # multiselect
            salvas = [b for b in st.session_state.dados["barreiras_selecionadas"].get(dominio, []) if b in opcoes]
            selecionadas = st.multiselect(
                "Selecione as barreiras",
                opcoes,
                default=salvas,
                key=f"ms_{dominio}",
                label_visibility="collapsed"
            )
            st.session_state.dados["barreiras_selecionadas"][dominio] = selecionadas

            # sliders por barreira (bem visível: nome + barra na mesma linha)
            if selecionadas:
                st.markdown("---")
                st.markdown("**Nível de apoio por barreira**")
                st.caption("Escala: Autônomo (faz sozinho) → Monitorado → Substancial → Muito Substancial (suporte intenso/contínuo).")

                for b in selecionadas:
                    chave = f"{dominio}_{b}"
                    st.session_state.dados["niveis_suporte"].setdefault(chave, "Monitorado")

                    colA, colB = st.columns([2.2, 2.8], vertical_alignment="center")
                    with colA:
                        st.markdown(f"✅ **{b}**")
                    with colB:
                        st.session_state.dados["niveis_suporte"][chave] = st.select_slider(
                            "Nível de apoio",
                            options=["Autônomo", "Monitorado", "Substancial", "Muito Substancial"],
                            value=st.session_state.dados["niveis_suporte"].get(chave, "Monitorado"),
                            key=f"sl_{dominio}_{b}",
                            label_visibility="collapsed",
                            help=(
                                "Autônomo: realiza sem mediação | "
                                "Monitorado: precisa de checagens | "
                                "Substancial: precisa de mediação frequente | "
                                "Muito Substancial: precisa de suporte intenso/contínuo"
                            )
                        )

            # observação por domínio (mantido)
            st.session_state.dados["observacoes_barreiras"].setdefault(dominio, "")
            st.session_state.dados["observacoes_barreiras"][dominio] = st.text_area(
                "Observações (opcional)",
                value=st.session_state.dados["observacoes_barreiras"].get(dominio, ""),
                placeholder="Ex.: quando ocorre, gatilhos, o que ajuda, o que piora, estratégias que já funcionam...",
                height=90,
                key=f"obs_{dominio}"
            )

    # -------------------------
    # 3) 3 colunas (distribuição como era antes)
    # -------------------------
    c_bar1, c_bar2, c_bar3 = st.columns(3)

    with c_bar1:
        render_dominio("Funções Cognitivas", LISTAS_BARREIRAS.get("Funções Cognitivas", []))
        render_dominio("Sensorial e Motor", LISTAS_BARREIRAS.get("Sensorial e Motor", []))

    with c_bar2:
        render_dominio("Comunicação e Linguagem", LISTAS_BARREIRAS.get("Comunicação e Linguagem", []))
        render_dominio("Acadêmico", LISTAS_BARREIRAS.get("Acadêmico", []))

    with c_bar3:
        render_dominio("Socioemocional", LISTAS_BARREIRAS.get("Socioemocional", []))

    # -------------------------
    # 4) Limpeza automática (remove níveis de suporte de barreiras desmarcadas)
    # -------------------------
    chaves_validas = set()
    for dom, itens in st.session_state.dados["barreiras_selecionadas"].items():
        for b in itens:
            chaves_validas.add(f"{dom}_{b}")

    niveis = st.session_state.dados.get("niveis_suporte", {})
    st.session_state.dados["niveis_suporte"] = {k: v for k, v in niveis.items() if k in chaves_validas}

    st.divider()

    # -------------------------
    # 5) Resumo
    # -------------------------
    st.markdown("#### 📌 Resumo do Mapeamento")

    r1, r2 = st.columns(2)

    with r1:
        hf = (st.session_state.dados.get("hiperfoco") or "").strip()
        if hf:
            st.success(f"🎯 **Hiperfoco:** {hf}")
        else:
            st.info("🎯 **Hiperfoco:** não informado")

        pots = st.session_state.dados.get("potencias", [])
        if pots:
            st.success(f"🌟 **Potencialidades:** {', '.join(pots)}")
        else:
            st.info("🌟 **Potencialidades:** não selecionadas")

    with r2:
        selecionadas = {dom: vals for dom, vals in st.session_state.dados["barreiras_selecionadas"].items() if vals}
        total_bar = sum(len(v) for v in selecionadas.values())

        if total_bar == 0:
            st.info("🧩 **Barreiras:** nenhuma selecionada")
        else:
            st.warning(f"🧩 **Barreiras selecionadas:** {total_bar}")
            for dom, vals in selecionadas.items():
                st.markdown(f"**{dom}:**")
                for b in vals:
                    chave = f"{dom}_{b}"
                    nivel = st.session_state.dados["niveis_suporte"].get(chave, "Monitorado")
                    st.markdown(f"- {b} → **{nivel}**")


# ==============================================================================
# 16. ABA PLANO DE AÇÃO (COMPLETA)
# ==============================================================================
with tab5:
    st.markdown("### <i class='ri-tools-line'></i> Plano de Ação", unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown("#### 1) Acesso (DUA)")
        st.session_state.dados["estrategias_acesso"] = st.multiselect(
            "Recursos de acesso",
            [
                "Tempo Estendido",
                "Apoio Leitura/Escrita",
                "Material Ampliado",
                "Tecnologia Assistiva",
                "Sala Silenciosa",
                "Mobiliário Adaptado",
                "Pistas Visuais",
                "Rotina Estruturada",
            ],
            default=st.session_state.dados.get("estrategias_acesso", []),
        )
        st.session_state.dados["outros_acesso"] = st.text_input(
            "Personalizado (Acesso)",
            st.session_state.dados.get("outros_acesso", ""),
            placeholder="Ex: Prova em local separado, fonte 18, papel pautado ampliado…",
        )

    with c2:
        st.markdown("#### 2) Ensino (Metodologias)")
        st.session_state.dados["estrategias_ensino"] = st.multiselect(
            "Estratégias de ensino",
            [
                "Fragmentação de Tarefas",
                "Instrução Explícita",
                "Modelagem",
                "Mapas Mentais",
                "Andaimagem (Scaffolding)",
                "Ensino Híbrido",
                "Organizadores Gráficos",
                "Prática Guiada",
            ],
            default=st.session_state.dados.get("estrategias_ensino", []),
        )
        st.session_state.dados["outros_ensino"] = st.text_input(
            "Personalizado (Ensino)",
            st.session_state.dados.get("outros_ensino", ""),
            placeholder="Ex: Sequência didática com apoio de imagens + exemplo resolvido…",
        )

    with c3:
        st.markdown("#### 3) Avaliação (Formato)")
        st.session_state.dados["estrategias_avaliacao"] = st.multiselect(
            "Estratégias de avaliação",
            [
                "Prova Adaptada",
                "Prova Oral",
                "Consulta Permitida",
                "Portfólio",
                "Autoavaliação",
                "Parecer Descritivo",
                "Questões Menores por Bloco",
                "Avaliação Prática (Demonstração)",
            ],
            default=st.session_state.dados.get("estrategias_avaliacao", []),
        )
        st.caption("Dica: combine formato + acesso (tempo/ambiente) para reduzir barreiras.")

    st.divider()
    st.info("✅ O plano de ação alimenta a Consultoria IA com contexto prático (o que você já pretende fazer).")


# ==============================================================================
# 17. ABA MONITORAMENTO (COMPLETA)
# ==============================================================================
with tab6:
    st.markdown("### <i class='ri-loop-right-line'></i> Monitoramento", unsafe_allow_html=True)

    st.session_state.dados["monitoramento_data"] = st.date_input(
        "Data da Próxima Revisão",
        value=st.session_state.dados.get("monitoramento_data", date.today()),
    )

    st.divider()
    st.warning("⚠️ Preencher esta aba principalmente na REVISÃO do PEI (ciclo de acompanhamento).")

    with st.container(border=True):
        c2, c3 = st.columns(2)
        with c2:
            atual = st.session_state.dados.get("status_meta", "Não Iniciado")
            st.session_state.dados["status_meta"] = st.selectbox(
                "Status da Meta",
                ["Não Iniciado", "Em Andamento", "Parcialmente Atingido", "Atingido", "Superado"],
                index=(["Não Iniciado", "Em Andamento", "Parcialmente Atingido", "Atingido", "Superado"].index(atual) if atual in ["Não Iniciado", "Em Andamento", "Parcialmente Atingido", "Atingido", "Superado"] else 0),
            )
        with c3:
            atualp = st.session_state.dados.get("parecer_geral", "Manter Estratégias")
            st.session_state.dados["parecer_geral"] = st.selectbox(
                "Parecer Geral",
                [
                    "Manter Estratégias",
                    "Aumentar Suporte",
                    "Reduzir Suporte (Autonomia)",
                    "Alterar Metodologia",
                    "Encaminhar para Especialista",
                ],
                index=(
                    [
                        "Manter Estratégias",
                        "Aumentar Suporte",
                        "Reduzir Suporte (Autonomia)",
                        "Alterar Metodologia",
                        "Encaminhar para Especialista",
                    ].index(atualp)
                    if atualp in [
                        "Manter Estratégias",
                        "Aumentar Suporte",
                        "Reduzir Suporte (Autonomia)",
                        "Alterar Metodologia",
                        "Encaminhar para Especialista",
                    ]
                    else 0
                ),
            )

        st.session_state.dados["proximos_passos_select"] = st.multiselect(
            "Ações Futuras",
            [
                "Reunião com Família",
                "Encaminhamento Clínico",
                "Adaptação de Material",
                "Mudança de Lugar em Sala",
                "Novo PEI",
                "Observação em Sala",
            ],
            default=st.session_state.dados.get("proximos_passos_select", []),
        )


# ==============================================================================
# 18. ABA CONSULTORIA IA (COMPLETA: gerar + revisar + aprovar + ajustar)
# ==============================================================================
with tab7:
    st.markdown("### <i class='ri-robot-2-line'></i> Consultoria Pedagógica", unsafe_allow_html=True)

    if not st.session_state.dados.get("serie"):
        st.warning("⚠️ Selecione a Série/Ano na aba **Estudante** para ativar o modo especialista.")
        st.stop()

    # estado default
    st.session_state.dados.setdefault("status_validacao_pei", "rascunho")
    st.session_state.dados.setdefault("feedback_ajuste", "")

    seg_nome, seg_cor, seg_desc = get_segmento_info_visual(st.session_state.dados.get("serie"))
    st.markdown(
        f"<div style='background-color:#F7FAFC; border-left:5px solid {seg_cor}; padding:14px; border-radius:8px; margin-bottom:16px;'>"
        f"<b style='color:{seg_cor};'>ℹ️ Modo Especialista: {seg_nome}</b><br>"
        f"<span style='color:#4A5568;'>{seg_desc}</span></div>",
        unsafe_allow_html=True,
    )



    # 1) Se ainda não tem texto, ou voltou para rascunho: botões de geração
    if (not st.session_state.dados.get("ia_sugestao")) or (st.session_state.dados.get("status_validacao_pei") == "rascunho"):
        col_btn, col_info = st.columns([1, 2])

        with col_btn:
            if st.button("✨ Gerar Estratégia Técnica", type="primary", use_container_width=True):
                res, err = consultar_gpt_pedagogico(
                    api_key,
                    st.session_state.dados,
                    st.session_state.get("pdf_text", ""),
                    modo_pratico=False,
                )
                if res:
                    st.session_state.dados["ia_sugestao"] = res
                    st.session_state.dados["status_validacao_pei"] = "revisao"
                    st.rerun()
                else:
                    st.error(err or "Erro ao gerar.")

            st.write("")
            if st.button("🧰 Gerar Guia Prático (Sala de Aula)", use_container_width=True):
                res, err = consultar_gpt_pedagogico(
                    api_key,
                    st.session_state.dados,
                    st.session_state.get("pdf_text", ""),
                    modo_pratico=True,
                )
                if res:
                    st.session_state.dados["ia_sugestao"] = res
                    st.session_state.dados["status_validacao_pei"] = "revisao"
                    st.rerun()
                else:
                    st.error(err or "Erro ao gerar.")

        with col_info:
            n_bar = sum(len(v) for v in (st.session_state.dados.get("barreiras_selecionadas") or {}).values())
            st.info(
                "Quanto mais completo o **Mapeamento** (barreiras + nível de suporte + hiperfoco) "
                "e o **Plano de Ação**, melhor a precisão.\n\n"
                f"📌 Barreiras mapeadas agora: **{n_bar}**"
            )

    # 2) Revisão / Aprovado: mostrar e permitir aprovar/ajustar
    elif st.session_state.dados.get("status_validacao_pei") in ["revisao", "aprovado"]:
        n_barreiras = sum(len(v) for v in (st.session_state.dados.get("barreiras_selecionadas") or {}).values())
        diag_show = st.session_state.dados.get("diagnostico") or "em observação"

        with st.expander("🧠 Como a IA construiu este relatório (transparência)"):
            exemplo_barreira = "geral"
            try:
                for area, lst in (st.session_state.dados.get("barreiras_selecionadas") or {}).items():
                    if lst:
                        exemplo_barreira = lst[0]
                        break
            except Exception:
                pass

            st.markdown(
                f"**1. Input do estudante:** Série **{st.session_state.dados.get('serie','-')}**, diagnóstico **{diag_show}**.\n\n"
                f"**2. Barreiras ativas:** detectei **{n_barreiras}** barreiras e cruzei isso com BNCC + DUA.\n\n"
                f"**3. Ponto crítico exemplo:** priorizei adaptações para reduzir impacto de **{exemplo_barreira}**."
            )

        with st.expander("🛡️ Calibragem e segurança pedagógica"):
            st.markdown(
                "- **Farmacologia:** não sugere dose/medicação; apenas sinaliza pontos de atenção.\n"
                "- **Dados sensíveis:** evite inserir PII desnecessária.\n"
                "- **Normativa:** sugestões buscam aderência à LBI/DUA e adaptações razoáveis."
            )

        st.markdown("#### 📝 Revisão do Plano")
        texto_visual = re.sub(r"\[.*?\]", "", st.session_state.dados.get("ia_sugestao", ""))
        st.markdown(texto_visual)

        st.divider()
        st.markdown("**⚠️ Responsabilidade do Educador:** a IA pode errar. Valide e ajuste antes de aplicar.")

        if st.session_state.dados.get("status_validacao_pei") == "revisao":
            c_ok, c_ajuste = st.columns(2)
            if c_ok.button("✅ Aprovar Plano", type="primary", use_container_width=True):
                st.session_state.dados["status_validacao_pei"] = "aprovado"
                st.success("Plano aprovado ✅")
                st.rerun()
            if c_ajuste.button("❌ Solicitar Ajuste", use_container_width=True):
                st.session_state.dados["status_validacao_pei"] = "ajustando"
                st.rerun()

        elif st.session_state.dados.get("status_validacao_pei") == "aprovado":
            st.success("Plano Validado ✅")
            novo_texto = st.text_area(
                "Edição Final Manual (opcional)",
                value=st.session_state.dados.get("ia_sugestao", ""),
                height=320,
            )
            st.session_state.dados["ia_sugestao"] = novo_texto

            c1, c2 = st.columns(2)
            with c1:
                if st.button("🔁 Regerar do Zero", use_container_width=True):
                    st.session_state.dados["ia_sugestao"] = ""
                    st.session_state.dados["status_validacao_pei"] = "rascunho"
                    st.rerun()
            with c2:
                if st.button("🧹 Voltar para Revisão", use_container_width=True):
                    st.session_state.dados["status_validacao_pei"] = "revisao"
                    st.rerun()

    # 3) Ajustando: caixa de feedback + regerar
    elif st.session_state.dados.get("status_validacao_pei") == "ajustando":
        st.warning("Descreva o ajuste desejado:")
        feedback = st.text_area("Seu feedback:", placeholder="Ex: Foque mais na alfabetização…")
        if st.button("Regerar com Ajustes", type="primary", use_container_width=True):
            res, err = consultar_gpt_pedagogico(
                api_key,
                st.session_state.dados,
                st.session_state.get("pdf_text", ""),
                modo_pratico=False,
                feedback_usuario=feedback,
            )
            if res:
                st.session_state.dados["ia_sugestao"] = res
                st.session_state.dados["status_validacao_pei"] = "revisao"
                st.rerun()
            else:
                st.error(err or "Erro ao regerar.")

        if st.button("Cancelar", use_container_width=True):
            st.session_state.dados["status_validacao_pei"] = "revisao"
            st.rerun()


# ==============================================================================
# 19. ABA DASHBOARD & DOCS (Dashboard + Metas + Exportações + Sincronização 'rico')
# ==============================================================================
with tab8:
    st.markdown("### <i class='ri-file-pdf-line'></i> Dashboard e Exportação", unsafe_allow_html=True)

    # --------------------------------------------------------------------------
    # 0) GARANTIR CSS DO DASH
    # --------------------------------------------------------------------------
    def _ensure_dashboard_css():
        css = """
        <style>
            .dash-hero { background: linear-gradient(135deg, #0F52BA 0%, #062B61 100%); border-radius: 16px; padding: 25px; color: white; margin-bottom: 20px; display: flex; justify-content: space-between; align-items: center; box-shadow: 0 4px 12px rgba(15, 82, 186, 0.15); }
            .apple-avatar { width: 60px; height: 60px; border-radius: 50%; background: rgba(255,255,255,0.15); border: 2px solid rgba(255,255,255,0.4); color: white; font-weight: 800; font-size: 1.6rem; display: flex; align-items: center; justify-content: center; }
            .metric-card { background: white; border-radius: 16px; padding: 15px; border: 1px solid #E2E8F0; display: flex; flex-direction: column; align-items: center; justify-content: center; height: 140px; box-shadow: 0 2px 5px rgba(0,0,0,0.02); }
            .css-donut { --p: 0; --fill: #e5e7eb; width: 80px; height: 80px; border-radius: 50%; background: conic-gradient(var(--fill) var(--p), #F3F4F6 0); position: relative; display: flex; align-items: center; justify-content: center; margin-bottom: 10px; }
            .css-donut:after { content: ""; position: absolute; width: 60px; height: 60px; border-radius: 50%; background: white; }
            .d-val { position: relative; z-index: 10; font-weight: 800; font-size: 1.2rem; color: #2D3748; }
            .d-lbl { font-size: 0.75rem; font-weight: 700; color: #718096; text-transform: uppercase; letter-spacing: 0.5px; text-align:center; }
            .comp-icon-box { width: 50px; height: 50px; border-radius: 50%; background: rgba(255,255,255,0.2); display: flex; align-items: center; justify-content: center; margin-bottom: 10px; }
            .soft-card { border-radius: 12px; padding: 20px; min-height: 220px; height: 100%; display: flex; flex-direction: column; box-shadow: 0 2px 5px rgba(0,0,0,0.02); border: 1px solid rgba(0,0,0,0.05); border-left: 5px solid; position: relative; overflow: hidden; }
            .sc-orange { background-color: #FFF5F5; border-left-color: #DD6B20; }
            .sc-blue { background-color: #EBF8FF; border-left-color: #3182CE; }
            .sc-yellow { background-color: #FFFFF0; border-left-color: #D69E2E; }
            .sc-cyan { background-color: #E6FFFA; border-left-color: #0BC5EA; }
            .sc-green { background-color: #F0FFF4; border-left-color: #38A169; }
            .sc-head { display: flex; align-items: center; gap: 8px; font-weight: 800; font-size: 0.95rem; margin-bottom: 15px; color: #2D3748; }
            .sc-body { font-size: 0.85rem; color: #4A5568; line-height: 1.5; flex-grow: 1; }
            .bg-icon { position: absolute; bottom: -10px; right: -10px; font-size: 5rem; opacity: 0.08; pointer-events: none; }
            .meta-row { display: flex; align-items: center; gap: 10px; margin-bottom: 8px; font-size: 0.85rem; border-bottom: 1px solid rgba(0,0,0,0.05); padding-bottom: 5px; }
            .dna-bar-container { margin-bottom: 15px; }
            .dna-bar-flex { display: flex; justify-content: space-between; font-size: 0.8rem; margin-bottom: 3px; font-weight: 600; color: #4A5568; }
            .dna-bar-bg { width: 100%; height: 8px; background-color: #E2E8F0; border-radius: 4px; overflow: hidden; }
            .dna-bar-fill { height: 100%; border-radius: 4px; transition: width 1s ease; }
            .rede-chip { display: inline-flex; align-items: center; gap: 5px; background: white; padding: 5px 12px; border-radius: 20px; font-size: 0.85rem; font-weight: 600; color: #2D3748; box-shadow: 0 1px 2px rgba(0,0,0,0.05); border: 1px solid #E2E8F0; margin: 0 5px 5px 0; }
            .pulse-alert { animation: pulse 2s infinite; color: #E53E3E; font-weight: bold; }
            @keyframes pulse { 0% { opacity: 1; } 50% { opacity: 0.5; } 100% { opacity: 1; } }
        </style>
        """
        st.markdown(css, unsafe_allow_html=True)

    _ensure_dashboard_css()

    # --------------------------------------------------------------------------
    # 1) HELPERS (fallbacks)
    # --------------------------------------------------------------------------
    d = st.session_state.dados

    def _safe(fn_name, default=None):
        return globals().get(fn_name, default)

    calcular_idade_fn = _safe("calcular_idade", lambda x: "")
    get_hiperfoco_emoji_fn = _safe("get_hiperfoco_emoji", lambda x: "🚀")
    calcular_complexidade_pei_fn = _safe("calcular_complexidade_pei", lambda _d: ("ATENÇÃO", "#FFFFF0", "#D69E2E"))
    extrair_metas_estruturadas_fn = _safe("extrair_metas_estruturadas", lambda _t: {"Curto": "Definir...", "Medio": "Definir...", "Longo": "Definir..."})
    inferir_componentes_impactados_fn = _safe("inferir_componentes_impactados", lambda _d: [])
    get_pro_icon_fn = _safe("get_pro_icon", lambda _p: "👨‍⚕️")

    # --------------------------------------------------------------------------
    # 2) GUARD
    # --------------------------------------------------------------------------
    if not d.get("nome"):
        st.info("Preencha o estudante na aba **Estudante** para visualizar o dashboard.")
        st.stop()

    # --------------------------------------------------------------------------
    # 3) HERO
    # --------------------------------------------------------------------------
    init_avatar = d.get("nome", "?")[0].upper() if d.get("nome") else "?"
    idade_str = calcular_idade_fn(d.get("nasc"))
    serie_txt = d.get("serie") or "-"
    turma_txt = d.get("turma") or "-"
    matricula_txt = d.get("matricula") or d.get("ra") or "-"
    student_id = st.session_state.get("selected_student_id")
    vinculo_txt = "Vinculado ao Supabase ✅" if student_id else "Rascunho (não sincronizado)"

    st.markdown(
        f"""
        <div class="dash-hero">
            <div style="display:flex; align-items:center; gap:20px;">
                <div class="apple-avatar">{init_avatar}</div>
                <div style="color:white;">
                    <h1 style="margin:0; line-height:1.1;">{d.get("nome","")}</h1>
                    <p style="margin:6px 0 0 0; opacity:.9;">
                        {serie_txt} • Turma {turma_txt} • Matrícula/RA: {matricula_txt}
                    </p>
                    <p style="margin:6px 0 0 0; opacity:.8; font-size:.85rem;">{vinculo_txt}</p>
                </div>
            </div>
            <div style="text-align:right;">
                <div style="font-size:0.8rem; opacity:.85;">IDADE</div>
                <div style="font-size:1.2rem; font-weight:800;">{idade_str}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # --------------------------------------------------------------------------
    # 4) KPIs
    # --------------------------------------------------------------------------
    c_kpi1, c_kpi2, c_kpi3, c_kpi4 = st.columns(4)

    with c_kpi1:
        n_pot = len(d.get("potencias", []) or [])
        color_p = "#38A169" if n_pot > 0 else "#CBD5E0"
        st.markdown(
            f"""<div class="metric-card">
                <div class="css-donut" style="--p: {min(n_pot*10,100)}%; --fill: {color_p};">
                    <div class="d-val">{n_pot}</div>
                </div>
                <div class="d-lbl">Potencialidades</div>
            </div>""",
            unsafe_allow_html=True
        )

    with c_kpi2:
        barreiras = d.get("barreiras_selecionadas", {}) or {}
        n_bar = sum(len(v) for v in barreiras.values()) if isinstance(barreiras, dict) else 0
        color_b = "#E53E3E" if n_bar > 5 else "#DD6B20"
        st.markdown(
            f"""<div class="metric-card">
                <div class="css-donut" style="--p: {min(n_bar*5,100)}%; --fill: {color_b};">
                    <div class="d-val">{n_bar}</div>
                </div>
                <div class="d-lbl">Barreiras</div>
            </div>""",
            unsafe_allow_html=True
        )

    with c_kpi3:
        hf = d.get("hiperfoco") or "-"
        hf_emoji = get_hiperfoco_emoji_fn(hf)
        st.markdown(
            f"""<div class="metric-card">
                <div style="font-size:2.5rem;">{hf_emoji}</div>
                <div style="font-weight:800; font-size:1.1rem; color:#2D3748; margin:10px 0;">{hf}</div>
                <div class="d-lbl">Hiperfoco</div>
            </div>""",
            unsafe_allow_html=True
        )

    with c_kpi4:
        txt_comp, bg_c, txt_c = calcular_complexidade_pei_fn(d)
        st.markdown(
            f"""<div class="metric-card" style="background-color:{bg_c}; border-color:{txt_c};">
                <div class="comp-icon-box">
                    <i class="ri-error-warning-line" style="color:{txt_c}; font-size: 2rem;"></i>
                </div>
                <div style="font-weight:800; font-size:1.1rem; color:{txt_c}; margin:5px 0;">{txt_comp}</div>
                <div class="d-lbl" style="color:{txt_c};">Nível de Atenção (Execução)</div>
            </div>""",
            unsafe_allow_html=True
        )

    # --------------------------------------------------------------------------
    # 5) CARDS PRINCIPAIS (2 colunas)
    # --------------------------------------------------------------------------
    st.write("")
    c_r1, c_r2 = st.columns(2)

    with c_r1:
        lista_meds = d.get("lista_medicamentos", []) or []
        if len(lista_meds) > 0:
            nomes_meds = ", ".join([m.get("nome","").strip() for m in lista_meds if m.get("nome")])
            alerta_escola = any(bool(m.get("escola")) for m in lista_meds)

            icon_alerta = '<i class="ri-alarm-warning-fill pulse-alert" style="font-size:1.2rem; margin-left:10px;"></i>' if alerta_escola else ""
            msg_escola = '<div style="margin-top:5px; color:#C53030; font-weight:bold; font-size:0.8rem;">🚨 ATENÇÃO: ADMINISTRAÇÃO NA ESCOLA NECESSÁRIA</div>' if alerta_escola else ""

            st.markdown(
                f"""<div class="soft-card sc-orange">
                    <div class="sc-head"><i class="ri-medicine-bottle-fill" style="color:#DD6B20;"></i> Atenção Farmacológica {icon_alerta}</div>
                    <div class="sc-body"><b>Uso Contínuo:</b> {nomes_meds if nomes_meds else "Medicação cadastrada."} {msg_escola}</div>
                    <div class="bg-icon">💊</div>
                </div>""",
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                """<div class="soft-card sc-green">
                    <div class="sc-head"><i class="ri-checkbox-circle-fill" style="color:#38A169;"></i> Medicação</div>
                    <div class="sc-body">Nenhuma medicação informada.</div>
                    <div class="bg-icon">✅</div>
                </div>""",
                unsafe_allow_html=True
            )

        st.write("")

        metas = extrair_metas_estruturadas_fn(d.get("ia_sugestao", ""))
        html_metas = (
            f"""<div class="meta-row"><span style="font-size:1.2rem;">🏁</span> <b>Curto:</b> {metas.get('Curto','Definir...')}</div>
                <div class="meta-row"><span style="font-size:1.2rem;">🧗</span> <b>Médio:</b> {metas.get('Medio','Definir...')}</div>
                <div class="meta-row"><span style="font-size:1.2rem;">🏔️</span> <b>Longo:</b> {metas.get('Longo','Definir...')}</div>"""
        )
        st.markdown(
            f"""<div class="soft-card sc-yellow">
                <div class="sc-head"><i class="ri-flag-2-fill" style="color:#D69E2E;"></i> Cronograma de Metas</div>
                <div class="sc-body">{html_metas}</div>
                <div class="bg-icon">🏁</div>
            </div>""",
            unsafe_allow_html=True
        )

    with c_r2:
        comps_inferidos = inferir_componentes_impactados_fn(d) or []
        if comps_inferidos:
            html_comps = "".join([f'<span class="rede-chip" style="border-color:#FC8181; color:#C53030;">{c}</span> ' for c in comps_inferidos])
            st.markdown(
                f"""<div class="soft-card sc-orange" style="border-left-color: #FC8181; background-color: #FFF5F5;">
                    <div class="sc-head"><i class="ri-radar-fill" style="color:#C53030;"></i> Radar Curricular (Automático)</div>
                    <div class="sc-body" style="margin-bottom:10px;">Componentes que exigem maior flexibilização (baseado nas barreiras):</div>
                    <div>{html_comps}</div>
                    <div class="bg-icon">🎯</div>
                </div>""",
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                """<div class="soft-card sc-blue">
                    <div class="sc-head"><i class="ri-radar-line" style="color:#3182CE;"></i> Radar Curricular</div>
                    <div class="sc-body">Nenhum componente específico marcado como crítico.</div>
                    <div class="bg-icon">🎯</div>
                </div>""",
                unsafe_allow_html=True
            )

        st.write("")

        rede = d.get("rede_apoio", []) or []
        rede_html = "".join([f'<span class="rede-chip">{get_pro_icon_fn(p)} {p}</span> ' for p in rede]) if rede else "<span style='opacity:0.6;'>Sem rede.</span>"
        st.markdown(
            f"""<div class="soft-card sc-cyan">
                <div class="sc-head"><i class="ri-team-fill" style="color:#0BC5EA;"></i> Rede de Apoio</div>
                <div class="sc-body">{rede_html}</div>
                <div class="bg-icon">🤝</div>
            </div>""",
            unsafe_allow_html=True
        )

    # --------------------------------------------------------------------------
    # 6) DNA de Suporte
    # --------------------------------------------------------------------------
    st.write("")
    st.markdown("##### 🧬 DNA de Suporte")
    dna_c1, dna_c2 = st.columns(2)

    LISTAS_BARREIRAS_LOCAL = globals().get("LISTAS_BARREIRAS", {}) or {}
    areas = list(LISTAS_BARREIRAS_LOCAL.keys()) if isinstance(LISTAS_BARREIRAS_LOCAL, dict) else []

    for i, area in enumerate(areas):
        qtd = len((d.get("barreiras_selecionadas", {}) or {}).get(area, []) or [])
        val = min(qtd * 20, 100)
        target = dna_c1 if i < 3 else dna_c2

        color = "#3182CE"
        if val > 40: color = "#DD6B20"
        if val > 70: color = "#E53E3E"

        target.markdown(
            f"""<div class="dna-bar-container">
                <div class="dna-bar-flex"><span>{area}</span><span>{qtd} barreiras</span></div>
                <div class="dna-bar-bg"><div class="dna-bar-fill" style="width:{val}%; background:{color};"></div></div>
            </div>""",
            unsafe_allow_html=True
        )

    # --------------------------------------------------------------------------
    # 7) EXPORTAÇÃO + SINCRONIZAÇÃO (BLOCO COMPLETO CORRIGIDO)
    # --------------------------------------------------------------------------
    st.divider()
    st.markdown("#### 📤 Exportação e Sincronização")

    # Verifica se existe conteúdo gerado pela IA
    if not d.get("ia_sugestao"):
        st.info("Gere o Plano na aba **Consultoria IA** para liberar PDF, Word e Sincronização.")
        # Se estiver dentro de uma função use return, se for script corrido:
        # st.stop() 
    else:
        # ======================================================================
        # 👇 A CORREÇÃO ESTÁ NESTA LINHA ABAIXO. ELA PRECISA EXISTIR AQUI 👇
        # ======================================================================
        col_docs, col_backup, col_sys = st.columns(3) 

        # ---------------- COLUNA 1: DOCS ----------------
        with col_docs:
            st.caption("📄 Documentos")

            pdf_bytes = None
            try:
                # Tenta gerar PDF com texto extraído se houver
                texto_pdf = st.session_state.get("pdf_text", "")
                pdf_bytes = gerar_pdf_final(d, len(texto_pdf) > 0)
            except TypeError:
                try:
                    pdf_bytes = gerar_pdf_final(d)
                except Exception as e:
                    st.error(f"Erro ao gerar PDF: {e}")

            if pdf_bytes:
                st.download_button(
                    "Baixar PDF Oficial",
                    pdf_bytes,
                    f"PEI_{d.get('nome','Aluno')}.pdf",
                    "application/pdf",
                    use_container_width=True
                )

            try:
                docx = gerar_docx_final(d)
                st.download_button(
                    "Baixar Word Editável",
                    docx,
                    f"PEI_{d.get('nome','Aluno')}.docx",
                    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    use_container_width=True
                )
            except Exception as e:
                st.warning("Word indisponível no momento.")

        # ---------------- COLUNA 2: BACKUP LOCAL ----------------
        with col_backup:
            st.caption("💾 Backup (JSON)")
            st.markdown(
                "<div style='font-size:.8rem; color:#64748B; margin-bottom:8px;'>"
                "Salva um arquivo no seu computador para garantir que nada se perca."
                "</div>",
                unsafe_allow_html=True
            )
            st.download_button(
                "Salvar Arquivo .JSON",
                json.dumps(d, default=str, ensure_ascii=False),
                f"PEI_{d.get('nome','Aluno')}.json",
                "application/json",
                use_container_width=True
            )

        # ---------------- COLUNA 3: NUVEM (SUPABASE COMPLETO) ----------------
        with col_sys:
            st.caption("🌐 Nuvem (Supabase)")
            st.markdown(
                "<div style='font-size:.8rem; color:#64748B; margin-bottom:8px;'>"
                "Salva cadastro + conteúdo completo (JSON) na nuvem."
                "</div>",
                unsafe_allow_html=True
            )

            # Helper interno de verificação
            def _cloud_ready_check():
                try:
                    url = str(st.secrets.get("SUPABASE_URL", "")).strip()
                    key = str(st.secrets.get("SUPABASE_SERVICE_KEY", "") or st.secrets.get("SUPABASE_ANON_KEY", "")).strip()
                    return bool(url and key)
                except:
                    return False

            if st.button("🔗 Sincronizar Tudo", type="primary", use_container_width=True, key="btn_sync_final_fix"):
                if not _cloud_ready_check():
                    st.error("⚠️ Configure os Secrets do Supabase.")
                else:
                    try:
                        with st.spinner("Sincronizando dados..."):
                            # 1. Tratar datas
                            nasc_iso = d.get("nasc").isoformat() if hasattr(d.get("nasc"), "isoformat") else None
                            
                            # 2. Dados Básicos
                            student_payload = {
                                "name": d.get("nome"),
                                "birth_date": nasc_iso,
                                "grade": d.get("serie"),
                                "class_group": d.get("turma") or None,
                                "diagnosis": d.get("diagnostico") or None,
                                "workspace_id": st.session_state.get("workspace_id"),
                            }
                            
                            # 3. Identificar ou Criar
                            sid = st.session_state.get("selected_student_id")
                            
                            if not sid:
                                created = db_create_student(student_payload)
                                if created and isinstance(created, dict):
                                    sid = created.get("id")
                                    st.session_state["selected_student_id"] = sid
                            else:
                                db_update_student(sid, student_payload)

                            # 4. SALVAR CONTEÚDO COMPLETO
                            if sid:
                                # Certifique-se de ter colado a função 'db_update_pei_content' lá em cima nas funções!
                                db_update_pei_content(sid, d)
                                
                                st.session_state["ultimo_backup_json"] = json.dumps(d, default=str, ensure_ascii=False)
                                st.session_state["sync_sucesso"] = True
                                
                                st.toast("Salvo na nuvem com sucesso!", icon="☁️")
                                st.rerun()
                            else:
                                st.error("Erro: ID do aluno não encontrado.")

                    except Exception as e:
                        st.error(f"Erro na sincronização: {e}")

            # Feedback e Download Pós-Sync
            if st.session_state.get("sync_sucesso"):
                st.success("✅ Tudo salvo!")
                timestamp = datetime.now().strftime("%d-%m_%Hh%M")
                nome_clean = (d.get('nome') or 'Aluno').replace(' ', '_')
                
                st.download_button(
                    label="📂 BAIXAR CÓPIA AGORA",
                    data=st.session_state["ultimo_backup_json"],
                    file_name=f"PEI_{nome_clean}_{timestamp}.json",
                    mime="application/json",
                    type="secondary",
                    use_container_width=True,
                    key="btn_post_sync_download_fix"
                )

# ==============================================================================
# ABA — JORNADA GAMIFICADA (BLOCO COMPLETO)
# ==============================================================================

with tab_9:
    

    nome_aluno = st.session_state.dados.get("nome") or "Estudante"
    serie = st.session_state.dados.get("serie") or ""
    hiperfoco = st.session_state.dados.get("hiperfoco") or ""
    potencias = st.session_state.dados.get("potencias") or []
    pei_ok = bool(st.session_state.dados.get("ia_sugestao"))

    # Header visual
    seg_nome, seg_cor, seg_desc = ("Selecione a Série", "#CBD5E0", "Defina a série na aba Estudante.")
    if serie:
        seg_nome, seg_cor, seg_desc = get_segmento_info_visual(serie)

    st.markdown(
        f"""
        <div style="
            background: linear-gradient(90deg, {seg_cor} 0%, #111827 140%);
            padding: 22px 26px; border-radius: 18px; color: white; margin-bottom: 18px;
            box-shadow: 0 8px 18px rgba(0,0,0,0.06);
        ">
            <div style="display:flex; align-items:center; justify-content:space-between; gap:16px;">
                <div>
                    <div style="font-size:0.9rem; opacity:0.9; font-weight:700; letter-spacing:0.3px;">🎮 JORNADA GAMIFICADA</div>
                    <div style="font-size:1.6rem; font-weight:900; margin-top:4px;">Missão do(a) {nome_aluno}</div>
                    <div style="opacity:0.92; margin-top:6px; font-weight:600;">{seg_nome} • {serie}</div>
                </div>
                <div style="text-align:right;">
                    <div style="font-size:0.75rem; opacity:0.85; font-weight:700;">Modo</div>
                    <div style="font-size:1.05rem; font-weight:900;">{("Pronto" if pei_ok else "Aguardando PEI")}</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.info(
        "ℹ️ Esta aba cria um material **para o estudante**: uma versão gamificada do plano, "
        "para imprimir, entregar à família ou usar como combinado de sala."
    )

    # Pré-requisitos
    if not serie:
        st.warning("⚠️ Selecione a **Série/Ano** na aba **Estudante** para liberar a Jornada.")
        st.stop()

    if not st.session_state.dados.get("nome"):
        st.warning("⚠️ Preencha o **nome do estudante** na aba **Estudante** para liberar a Jornada.")
        st.stop()

    if not pei_ok:
        st.warning("⚠️ Gere o PEI Técnico na aba **Consultoria IA** antes de criar a Jornada.")
        st.stop()

    # Contexto compacto
    with st.container(border=True):
        cA, cB, cC = st.columns([2, 2, 2])
        with cA:
            st.markdown("##### 🚀 Hiperfoco")
            st.write(hiperfoco if hiperfoco else "—")
        with cB:
            st.markdown("##### 🌟 Potencialidades")
            if potencias:
                st.write(", ".join(potencias))
            else:
                st.write("—")
        with cC:
            st.markdown("##### 🧭 Guia do Segmento")
            st.caption(seg_desc)

    st.divider()

    # Estado de validação
    st.session_state.dados.setdefault("status_validacao_game", "rascunho")
    st.session_state.dados.setdefault("feedback_ajuste_game", "")
    st.session_state.dados.setdefault("ia_mapa_texto", "")

    status_game = st.session_state.dados.get("status_validacao_game", "rascunho")

    # Ações principais (centralizadas)
    colL, colM, colR = st.columns([1, 2, 1])
    with colM:
        st.markdown("### 🧩 Gerar / Revisar Missão")

    # -------------------------
    # 1) RASCUNHO — gerar
    # -------------------------
    if status_game == "rascunho":
        st.markdown(
            """
            **Como funciona**
            - A IA usa **hiperfoco + potências** para criar uma história motivadora.
            - O texto evita dados sensíveis e foca em **apoio, autonomia e rotina**.
            """
        )

        col1, col2 = st.columns([2, 1])
        with col1:
            st.caption("Você pode pedir um estilo específico (opcional).")
            estilo = st.text_input(
                "Preferência de estilo (opcional)",
                placeholder="Ex: super-heróis, exploração espacial, futebol, fantasia medieval...",
                key="gm_estilo"
            )
        with col2:
            st.write("")
            st.write("")
            gerar_btn = st.button("🎮 Criar Roteiro Gamificado", type="primary", use_container_width=True)

        if gerar_btn:
            with st.spinner("Game Master criando a missão..."):
                # feedback opcional entra como ajuste de estilo
                fb = (f"Estilo desejado: {estilo}." if estilo else "").strip()
                texto_game, err = gerar_roteiro_gamificado(api_key, st.session_state.dados, st.session_state.dados["ia_sugestao"], fb)

                if texto_game:
                    st.session_state.dados["ia_mapa_texto"] = texto_game.replace("[MAPA_TEXTO_GAMIFICADO]", "").strip()
                    st.session_state.dados["status_validacao_game"] = "revisao"
                    st.rerun()
                else:
                    st.error(err or "Erro desconhecido ao gerar a missão.")

    # -------------------------
    # 2) REVISÃO — aprovar/refazer
    # -------------------------
    elif status_game == "revisao":
        st.success("✅ Missão gerada! Revise abaixo e aprove/solicite ajustes.")

        with st.container(border=True):
            st.markdown("#### 📜 Missão (prévia)")
            st.markdown(st.session_state.dados.get("ia_mapa_texto", ""))

        st.divider()
        c_ok, c_aj = st.columns(2)
        with c_ok:
            if st.button("✅ Aprovar Missão", type="primary", use_container_width=True):
                st.session_state.dados["status_validacao_game"] = "aprovado"
                st.rerun()
        with c_aj:
            if st.button("✏️ Solicitar Ajustes", use_container_width=True):
                st.session_state.dados["status_validacao_game"] = "ajustando"
                st.rerun()

    # -------------------------
    # 3) AJUSTANDO — feedback e regerar
    # -------------------------
    elif status_game == "ajustando":
        st.warning("🛠️ Descreva o que você quer mudar e regenere a missão.")

        fb_game = st.text_area(
            "O que ajustar na missão?",
            value=st.session_state.dados.get("feedback_ajuste_game", ""),
            placeholder="Ex: deixe mais curto, use linguagem mais infantil, traga recompensas, troque o tema para futebol...",
            height=140
        )
        st.session_state.dados["feedback_ajuste_game"] = fb_game

        c1, c2 = st.columns([2, 1])
        with c1:
            if st.button("🔁 Regerar com Ajustes", type="primary", use_container_width=True):
                with st.spinner("Reescrevendo missão..."):
                    texto_game, err = gerar_roteiro_gamificado(
                        api_key,
                        st.session_state.dados,
                        st.session_state.dados["ia_sugestao"],
                        feedback_game=fb_game
                    )
                    if texto_game:
                        st.session_state.dados["ia_mapa_texto"] = texto_game.replace("[MAPA_TEXTO_GAMIFICADO]", "").strip()
                        st.session_state.dados["status_validacao_game"] = "revisao"
                        st.rerun()
                    else:
                        st.error(err or "Erro desconhecido ao regerar a missão.")
        with c2:
            if st.button("↩️ Voltar", use_container_width=True):
                st.session_state.dados["status_validacao_game"] = "revisao"
                st.rerun()

    # -------------------------
    # 4) APROVADO — exportar PDF e editar fino
    # -------------------------
    elif status_game == "aprovado":
        st.success("🏁 Missão aprovada! Agora você pode imprimir e entregar.")

        colA, colB = st.columns([2, 1])
        with colA:
            with st.container(border=True):
                st.markdown("#### 📜 Missão Final (editável)")
                novo_texto = st.text_area(
                    "Edição final manual (opcional)",
                    value=st.session_state.dados.get("ia_mapa_texto", ""),
                    height=320
                )
                st.session_state.dados["ia_mapa_texto"] = novo_texto

        with colB:
            with st.container(border=True):
                st.markdown("#### 📥 Exportação")
                pdf_mapa = gerar_pdf_tabuleiro_simples(st.session_state.dados["ia_mapa_texto"])
                st.download_button(
                    "📄 Baixar Missão em PDF",
                    pdf_mapa,
                    file_name=f"Missao_{nome_aluno}.pdf",
                    mime="application/pdf",
                    type="primary",
                    use_container_width=True
                )
                st.caption("Dica: imprima e cole no caderno / agenda do aluno.")
                st.write("---")
                if st.button("🆕 Criar Nova Missão", use_container_width=True):
                    st.session_state.dados["status_validacao_game"] = "rascunho"
                    st.session_state.dados["feedback_ajuste_game"] = ""
                    st.session_state.dados["ia_mapa_texto"] = ""
                    st.rerun()

    else:
        # fallback seguro
        st.session_state.dados["status_validacao_game"] = "rascunho"
        st.rerun()
