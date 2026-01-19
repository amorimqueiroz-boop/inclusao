# ==========================================
# pages/1_PEI.py — OMNISFERA (PEI)
# PARTE 1/4 — BOOT + SIDEBAR + TABS
# ==========================================

import os
import sys
import json
from datetime import date

import streamlit as st

# ------------------------------------------------------------
# FIX CRÍTICO: permitir import de módulos na raiz do projeto
# (resolve ModuleNotFoundError ao rodar dentro de /pages)
# ------------------------------------------------------------
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# ------------------------------------------------------------
# IMPORTS DO PROJETO (precisam existir na raiz do repo)
# ------------------------------------------------------------
from omni_pei_legacy_features import (
    ensure_session_state,
    aplicar_estilo_visual,
    render_brand_badge,
    render_progresso,
    limpar_formulario,
    ler_pdf,
    extrair_dados_pdf_ia,
    consultar_gpt_pedagogico,
    gerar_roteiro_gamificado,
    gerar_pdf_final,
    gerar_docx_final,
    gerar_pdf_tabuleiro_simples,
    calcular_idade,
    LISTA_SERIES,
    LISTA_ALFABETIZACAO,
    LISTAS_BARREIRAS,
    LISTA_POTENCIAS,
    LISTA_PROFISSIONAIS,
    LISTA_FAMILIA,
    get_segmento_info_visual,
    get_hiperfoco_emoji,
    extrair_metas_estruturadas,
    inferir_componentes_impactados,
    get_pro_icon,
    calcular_complexidade_pei,
)

from omni_pei_db import (
    sync_student_and_open_pei,
    supa_save_pei,
    supa_sync_student_from_dados,
    supa_load_latest_pei,
    salvar_aluno_integrado,
)

# ------------------------------------------------------------
# STREAMLIT CONFIG
# ------------------------------------------------------------
st.set_page_config(
    page_title="Omnisfera · PEI",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ------------------------------------------------------------
# BOOT SEGURO (ordem correta)
# ------------------------------------------------------------
ensure_session_state()
aplicar_estilo_visual()
st.session_state["omni_logo_src"] = render_brand_badge()

# ------------------------------------------------------------
# OPENAI KEY (secrets ou input)
# ------------------------------------------------------------
if "OPENAI_API_KEY" in st.secrets:
    api_key = st.secrets["OPENAI_API_KEY"]
else:
    api_key = ""

# ------------------------------------------------------------
# SIDEBAR
# ------------------------------------------------------------
with st.sidebar:
    st.markdown("### 👤 Sessão")
    st.caption(f"Usuário: **{st.session_state.get('usuario_nome','')}**")

    st.divider()

    # OpenAI
    st.markdown("### 🤖 OpenAI")
    if "OPENAI_API_KEY" in st.secrets:
        st.success("✅ OpenAI OK (secrets)")
    else:
        api_key = st.text_input("Chave OpenAI", type="password", value=api_key)

    st.info("⚠️ IA gera sugestões. Revise antes de aplicar.")

    st.divider()

    # Backup local
    st.markdown("### 📂 Backup Local (.json)")
    uploaded_json = st.file_uploader(
        "Carregar backup do PEI",
        type="json",
        label_visibility="collapsed",
    )
    if uploaded_json:
        try:
            d = json.load(uploaded_json)

            # datas
            for k in ["nasc", "monitoramento_data"]:
                if k in d and isinstance(d[k], str):
                    try:
                        d[k] = date.fromisoformat(d[k])
                    except Exception:
                        pass

            st.session_state.dados.update(d)
            st.success("Backup carregado ✅")
            st.rerun()
        except Exception as e:
            st.error(f"Erro no arquivo: {e}")

    st.divider()

    # Supabase
    st.markdown("### 💾 Supabase")

    pei_mode = st.session_state.get("pei_mode", "rascunho")
    student_id = st.session_state.get("selected_student_id")

    if pei_mode == "rascunho":
        st.caption("Modo atual: **Rascunho** (nada salvo no banco)")
        if st.button("🔗 Sincronizar (criar aluno)", type="primary", use_container_width=True):
            try:
                ok, msg = sync_student_and_open_pei()
                if ok:
                    st.success(msg or "Sincronizado ✅")
                    st.rerun()
                else:
                    st.error(msg or "Falha ao sincronizar.")
            except Exception as e:
                st.error(f"Erro ao sincronizar: {e}")
    else:
        st.caption("Modo atual: **Vinculado ao Supabase** ✅")
        c1, c2 = st.columns(2)

        with c1:
            if st.button("💾 Salvar", type="primary", use_container_width=True):
                try:
                    with st.spinner("Salvando..."):
                        supa_save_pei(
                            student_id,
                            st.session_state.dados,
                            st.session_state.get("pdf_text", ""),
                        )
                        supa_sync_student_from_dados(student_id, st.session_state.dados)
                    st.success("Salvo no Supabase ✅")
                except Exception as e:
                    st.error(f"Erro ao salvar: {e}")

        with c2:
            if st.button("🔄 Recarregar", use_container_width=True):
                try:
                    with st.spinner("Recarregando..."):
                        row = supa_load_latest_pei(student_id)

                    if row and row.get("payload"):
                        payload = row["payload"]

                        for k in ["nasc", "monitoramento_data"]:
                            if payload.get(k) and isinstance(payload.get(k), str):
                                try:
                                    payload[k] = date.fromisoformat(payload[k])
                                except Exception:
                                    pass

                        st.session_state.dados.update(payload)
                        st.session_state.pdf_text = row.get("pdf_text") or ""
                        st.success("Recarregado ✅")
                        st.rerun()
                    else:
                        st.info("Ainda não existe PEI salvo para este aluno.")
                except Exception as e:
                    st.error(f"Erro ao recarregar: {e}")

    st.divider()

    if st.button("📄 Novo / Limpar (Rascunho)", use_container_width=True):
        limpar_formulario()
        st.session_state["pei_mode"] = "rascunho"
        st.session_state["selected_student_id"] = None
        st.session_state["selected_student_name"] = None
        st.toast("Formulário limpo! Use à vontade sem salvar.", icon="✨")
        st.rerun()

# ------------------------------------------------------------
# HEADER
# ------------------------------------------------------------
st.markdown(
    f"""
    <div class="header-unified">
        <img src="{st.session_state.get("omni_logo_src")}" style="height: 110px;">
        <div class="header-subtitle">Planejamento Educacional Inclusivo Inteligente</div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ------------------------------------------------------------
# TABS
# ------------------------------------------------------------
abas = [
    "INÍCIO",
    "ESTUDANTE",
    "EVIDÊNCIAS",
    "REDE DE APOIO",
    "MAPEAMENTO",
    "PLANO DE AÇÃO",
    "MONITORAMENTO",
    "CONSULTORIA IA",
    "DASHBOARD & DOCS",
    "JORNADA GAMIFICADA",
]
tab0, tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9 = st.tabs(abas)

# ==========================================
# PARTE 2/4 — TAB 0, TAB 1, TAB 2
# ==========================================

# ------------------------------------------------------------------
# TAB 0 — INÍCIO
# ------------------------------------------------------------------
with tab0:
    render_progresso()
    st.markdown("### 🏛️ Central de Fundamentos e Legislação")

    c1, c2 = st.columns(2)

    with c1:
        st.markdown(
            """
            <div class="rich-box">
                <div class="rb-title">📘 O que é o PEI?</div>
                <div class="rb-text">
                    O <b>Plano de Ensino Individualizado (PEI)</b> é o documento pedagógico que organiza
                    adaptações razoáveis, equidade e acompanhamento para estudantes PAEE.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c2:
        st.markdown(
            """
            <div class="rich-box">
                <div class="rb-title">⚖️ Base Legal</div>
                <div class="rb-text">
                    Sustentado na <b>LBI (Lei 13.146/2015)</b>, LDB e princípios do <b>DUA</b>.
                    Objetivo: reduzir barreiras e garantir acesso/participação/aprendizagem.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown(
        """
        <div class="rich-box" style="background-color:#EBF8FF; border-color:#3182CE;">
            <div class="rb-title" style="color:#2B6CB0;">🧭 Como usar?</div>
            <div class="rb-text">
                Fluxo sugerido:
                <ol>
                    <li><b>Estudante</b>: dados, histórico, diagnóstico.</li>
                    <li><b>Evidências</b>: sinais pedagógicos/cognitivos/comportamentais.</li>
                    <li><b>Mapeamento</b>: barreiras + nível de suporte + potências.</li>
                    <li><b>Consultoria IA</b>: gerar e revisar o plano técnico.</li>
                    <li><b>Dashboard & Docs</b>: exportar e salvar versões.</li>
                </ol>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ------------------------------------------------------------------
# TAB 1 — ESTUDANTE
# ------------------------------------------------------------------
with tab1:
    render_progresso()
    st.markdown("### 👤 Dossiê do Estudante")

    c1, c2, c3, c4 = st.columns([3, 2, 2, 1])

    st.session_state.dados["nome"] = c1.text_input(
        "Nome completo",
        st.session_state.dados.get("nome", ""),
    )

    st.session_state.dados["nasc"] = c2.date_input(
        "Nascimento",
        value=st.session_state.dados.get("nasc", date(2015, 1, 1)),
    )

    serie_atual = st.session_state.dados.get("serie")
    idx = LISTA_SERIES.index(serie_atual) if serie_atual in LISTA_SERIES else 0
    st.session_state.dados["serie"] = c3.selectbox("Série/Ano", LISTA_SERIES, index=idx)

    if st.session_state.dados.get("serie"):
        nome_seg, cor_seg, desc_seg = get_segmento_info_visual(st.session_state.dados["serie"])
        c3.markdown(
            f"<div class='segmento-badge' style='background-color:{cor_seg}'>{nome_seg}</div>",
            unsafe_allow_html=True,
        )

    st.session_state.dados["turma"] = c4.text_input(
        "Turma",
        st.session_state.dados.get("turma", ""),
    )

    st.divider()
    st.markdown("#### Histórico & Contexto Familiar")

    c_hist, c_fam = st.columns(2)
    st.session_state.dados["historico"] = c_hist.text_area(
        "Histórico escolar",
        st.session_state.dados.get("historico", ""),
    )
    st.session_state.dados["familia"] = c_fam.text_area(
        "Dinâmica familiar",
        st.session_state.dados.get("familia", ""),
    )

    # multiselect seguro (remove itens inválidos)
    default_fam = [
        x for x in (st.session_state.dados.get("composicao_familiar_tags") or [])
        if x in LISTA_FAMILIA
    ]
    st.session_state.dados["composicao_familiar_tags"] = st.multiselect(
        "Quem convive com o aluno?",
        LISTA_FAMILIA,
        default=default_fam,
    )

    st.divider()

    # PDF
    st.markdown("#### 📎 Upload de Laudo (PDF)")
    col_pdf, col_btn = st.columns([3, 1])

    with col_pdf:
        up = st.file_uploader("Envie o PDF", type="pdf", label_visibility="collapsed")
        if up:
            st.session_state.pdf_text = ler_pdf(up)

    with col_btn:
        st.write("")
        st.write("")
        if st.button(
            "✨ Extrair dados do laudo",
            type="primary",
            use_container_width=True,
            disabled=not bool(st.session_state.get("pdf_text")),
        ):
            if not api_key:
                st.error("Configure a chave OpenAI na sidebar.")
            else:
                with st.spinner("Analisando laudo..."):
                    dados_extraidos, erro = extrair_dados_pdf_ia(api_key, st.session_state.pdf_text)

                if dados_extraidos:
                    if dados_extraidos.get("diagnostico"):
                        st.session_state.dados["diagnostico"] = dados_extraidos["diagnostico"]

                    if dados_extraidos.get("medicamentos"):
                        for med in dados_extraidos["medicamentos"]:
                            st.session_state.dados["lista_medicamentos"].append(
                                {
                                    "nome": med.get("nome", ""),
                                    "posologia": med.get("posologia", ""),
                                    "escola": False,
                                }
                            )
                    st.success("Dados extraídos ✅")
                    st.rerun()
                else:
                    st.error(f"Erro: {erro}")

    st.divider()
    st.markdown("#### 🏥 Contexto Clínico")

    st.session_state.dados["diagnostico"] = st.text_input(
        "Diagnóstico",
        st.session_state.dados.get("diagnostico", ""),
    )

    with st.container(border=True):
        usa_med = st.toggle(
            "💊 O aluno faz uso contínuo de medicação?",
            value=len(st.session_state.dados.get("lista_medicamentos", [])) > 0,
        )

        if usa_med:
            mc1, mc2, mc3 = st.columns([3, 2, 2])
            nm = mc1.text_input("Nome", key="nm_med")
            pos = mc2.text_input("Posologia", key="pos_med")
            admin_escola = mc3.checkbox("Na escola?", key="adm_esc")

            if st.button("Adicionar", use_container_width=True):
                if (nm or "").strip():
                    st.session_state.dados["lista_medicamentos"].append(
                        {"nome": nm.strip(), "posologia": (pos or "").strip(), "escola": admin_escola}
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

# ------------------------------------------------------------------
# TAB 2 — EVIDÊNCIAS
# ------------------------------------------------------------------
with tab2:
    render_progresso()
    st.markdown("### 🔎 Coleta de Evidências")

    atual = st.session_state.dados.get("nivel_alfabetizacao")
    idx = LISTA_ALFABETIZACAO.index(atual) if atual in LISTA_ALFABETIZACAO else 0

    st.session_state.dados["nivel_alfabetizacao"] = st.selectbox(
        "Hipótese de Escrita",
        LISTA_ALFABETIZACAO,
        index=idx,
    )

    st.divider()
    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown("**Pedagógico**")
        for q in [
            "Estagnação na aprendizagem",
            "Dificuldade de generalização",
            "Dificuldade de abstração",
            "Lacuna em pré-requisitos",
        ]:
            st.session_state.dados["checklist_evidencias"][q] = st.toggle(
                q, value=st.session_state.dados["checklist_evidencias"].get(q, False)
            )

    with c2:
        st.markdown("**Cognitivo**")
        for q in [
            "Oscilação de foco",
            "Fadiga mental rápida",
            "Dificuldade de iniciar tarefas",
            "Esquecimento recorrente",
        ]:
            st.session_state.dados["checklist_evidencias"][q] = st.toggle(
                q, value=st.session_state.dados["checklist_evidencias"].get(q, False)
            )

    with c3:
        st.markdown("**Comportamental**")
        for q in [
            "Dependência de mediação (1:1)",
            "Baixa tolerância à frustração",
            "Desorganização de materiais",
            "Recusa de tarefas",
        ]:
            st.session_state.dados["checklist_evidencias"][q] = st.toggle(
                q, value=st.session_state.dados["checklist_evidencias"].get(q, False)
            )
