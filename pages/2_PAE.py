import streamlit as st
import os
import json
import base64
from datetime import date
import pandas as pd
from openai import OpenAI
from ui_nav import render_omnisfera_nav

# ==============================================================================
# 1) CONFIG
# ==============================================================================
st.set_page_config(
    page_title="PAEE & T.A. | Omnisfera",
    page_icon="🧩",
    layout="wide",
    initial_sidebar_state="collapsed",  # sidebar não será usada
)

# ==============================================================================
# 2) MENU TOPBAR (NOVO)
# ==============================================================================
try:
    from ui_nav import render_topbar_nav
    render_topbar_nav(active="paee")  # <--- importante
except Exception as e:
    st.error("Erro ao carregar o menu (ui_nav.py).")
    st.exception(e)
    st.stop()

# ==============================================================================
# 3) SEGURANÇA
# ==============================================================================
def verificar_acesso():
    if not st.session_state.get("autenticado", False):
        st.error("🔒 Acesso negado. Faça login na Home.")
        st.stop()

verificar_acesso()

# ==============================================================================
# 4) HELPERS (IMAGENS)
# ==============================================================================
def _b64_file(path: str) -> str:
    if not os.path.exists(path):
        return ""
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

def img_tag(path: str, width_px: int) -> str:
    b64 = _b64_file(path)
    if not b64:
        return ""
    return f'<img src="data:image/png;base64,{b64}" width="{width_px}" style="object-fit:contain; display:block;">'

# ==============================================================================
# 5) CSS (AJUSTADO PARA TOPBAR + COERÊNCIA VISUAL)
#    - Não cria sidebar
#    - Não joga padding-top pequeno (topbar precisa respiro)
#    - Tabs e inputs mantém seu look
# ==============================================================================
try:
    IS_TEST_ENV = st.secrets.get("ENV") == "TESTE"
except Exception:
    IS_TEST_ENV = False

st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800&display=swap" rel="stylesheet">
<link rel="stylesheet" href="https://cdn-uicons.flaticon.com/uicons-solid-rounded/css/uicons-solid-rounded.css">

<style>
:root{
  --brand: #22A765;          /* PAEE (verde elegante) */
  --brand-hover: #1E8E57;
  --ink: #0F172A;
  --muted: #64748B;
  --bg: #F7FAFC;
  --card: #FFFFFF;
  --stroke: #E2E8F0;
  --radius: 16px;
}

html, body, [class*="css"]{
  font-family: 'Nunito', sans-serif;
  background: var(--bg);
  color: #2D3748;
}

/* Não usar sidebar */
[data-testid="stSidebar"], [data-testid="stSidebarNav"]{display:none !important;}
header[data-testid="stHeader"]{display:none !important;}
[data-testid="stToolbar"]{display:none !important;}

/* espaço para o menu topo (ui_nav já define, mas garantimos aqui também) */
.block-container{
  padding-top: 86px !important;
  padding-bottom: 5rem !important;
}

/* Tabs clean */
div[data-baseweb="tab-border"], div[data-baseweb="tab-highlight"]{display:none !important;}

.stTabs [data-baseweb="tab-list"]{
  gap: 8px;
  display:flex;
  flex-wrap: nowrap;
  overflow-x: auto;
  white-space: nowrap;
  padding: 10px 5px;
  scrollbar-width: none;
}
.stTabs [data-baseweb="tab-list"]::-webkit-scrollbar{display:none;}

.stTabs [data-baseweb="tab"]{
  height: 38px;
  border-radius: 999px !important;
  background: #FFFFFF;
  border: 1px solid var(--stroke);
  color: #64748B;
  font-weight: 800;
  font-size: 0.76rem;
  padding: 0 18px;
  transition: all .18s ease;
  box-shadow: 0 1px 2px rgba(0,0,0,0.03);
  flex-shrink: 0;
  text-transform: uppercase;
  letter-spacing: .08em;
}
.stTabs [data-baseweb="tab"]:hover{
  border-color: #CBD5E0;
  background: #F1F5F9;
  color: #334155;
}
.stTabs [aria-selected="true"]{
  background: rgba(34,167,101,0.08) !important;
  border-color: rgba(34,167,101,0.55) !important;
  color: var(--brand) !important;
  box-shadow: 0 0 10px rgba(34,167,101,0.18) !important;
}

/* Inputs */
.stTextInput input, .stTextArea textarea, .stSelectbox div[data-baseweb="select"], .stNumberInput input{
  border-radius: 12px !important;
  border-color: var(--stroke) !important;
  background: #FFFFFF !important;
}

/* Botões (colunas) */
div[data-testid="column"] .stButton button{
  border-radius: 12px !important;
  font-weight: 900 !important;
  text-transform: uppercase;
  height: 48px !important;
  background-color: var(--brand) !important;
  color: white !important;
  border: none !important;
  letter-spacing: .06em;
}
div[data-testid="column"] .stButton button:hover{
  background-color: var(--brand-hover) !important;
}

/* Caixa pedagógica */
.pedagogia-box{
  background: #F8FAFC;
  border: 1px solid var(--stroke);
  border-left: 4px solid var(--brand);
  padding: 18px 18px;
  border-radius: 14px;
  margin-bottom: 18px;
  color: #475569;
  font-size: 0.95rem;
}

/* Header do módulo (premium) */
.module-header{
  background: var(--card);
  border: 1px solid var(--stroke);
  border-radius: 18px;
  padding: 18px 18px;
  box-shadow: 0 10px 30px rgba(15,23,42,0.05);
  display:flex;
  align-items:center;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 16px;
  overflow:hidden;
  position: relative;
}
.module-left{
  display:flex;
  align-items:center;
  gap: 14px;
  min-width: 320px;
}
.module-tile{
  width: 54px;
  height: 54px;
  border-radius: 16px;
  background: var(--brand);
  display:flex;
  align-items:center;
  justify-content:center;
  box-shadow: 0 12px 26px rgba(34,167,101,0.25);
}
.module-tile i{
  color: #FFFFFF;
  font-size: 22px;
  line-height: 1;
}
.module-title{
  font-family: system-ui, -apple-system, Segoe UI, Roboto, Arial;
  font-weight: 950;
  font-size: 1.05rem;
  color: var(--ink);
  letter-spacing: .02em;
}
.module-sub{
  margin-top: 2px;
  color: var(--muted);
  font-weight: 700;
  font-size: 0.92rem;
}
.module-right{
  display:flex;
  align-items:center;
  gap: 12px;
}
.module-right .png{
  opacity: 0.92;
}
.module-watermark{
  position:absolute;
  right: -10px;
  top: -18px;
  font-size: 120px;
  opacity: 0.04;
  transform: rotate(-12deg);
  pointer-events:none;
}
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# 6) BANCO LOCAL (JSON)
# ==============================================================================
ARQUIVO_DB = "banco_alunos.json"

def carregar_banco():
    usuario_atual = st.session_state.get("usuario_nome", "")
    if os.path.exists(ARQUIVO_DB):
        try:
            with open(ARQUIVO_DB, "r", encoding="utf-8") as f:
                todos_alunos = json.load(f)
            return [aluno for aluno in todos_alunos if aluno.get("responsavel") == usuario_atual]
        except Exception:
            return []
    return []

if "banco_estudantes" not in st.session_state or not st.session_state.get("banco_estudantes"):
    st.session_state.banco_estudantes = carregar_banco()

# ==============================================================================
# 7) HEADER (COERENTE COM O NOVO SISTEMA)
# ==============================================================================
img_pae = img_tag("pae.png", 210)

st.markdown(f"""
<div class="module-header">
  <div class="module-watermark"><i class="fi fi-sr-route"></i></div>

  <div class="module-left">
    <div class="module-tile"><i class="fi fi-sr-route"></i></div>
    <div>
      <div class="module-title">Plano de Ação (PAEE) & Tecnologia Assistiva</div>
      <div class="module-sub">Sala de Recursos • Eliminação de Barreiras • Articulação com a sala regular</div>
    </div>
  </div>

  <div class="module-right">
    <div class="png">{img_pae}</div>
  </div>
</div>
""", unsafe_allow_html=True)

# ==============================================================================
# 8) GUARD: precisa ter estudante
# ==============================================================================
if not st.session_state.banco_estudantes:
    st.warning("⚠️ Nenhum estudante encontrado para o seu usuário. Cadastre no módulo PEI primeiro.")
    st.stop()

# ==============================================================================
# 9) SELEÇÃO DE ESTUDANTE
# ==============================================================================
lista_alunos = [a.get("nome", "") for a in st.session_state.banco_estudantes if a.get("nome")]
col_sel, col_info = st.columns([1, 2])
with col_sel:
    nome_aluno = st.selectbox("📂 Selecione o Estudante:", lista_alunos)

aluno = next(a for a in st.session_state.banco_estudantes if a.get("nome") == nome_aluno)

# Detector Educação Infantil
serie_aluno = (aluno.get("serie", "") or "").lower()
is_ei = ("infantil" in serie_aluno) or ("creche" in serie_aluno) or ("pré" in serie_aluno) or ("pre" in serie_aluno)

# Header do estudante (clean)
st.markdown(f"""
<div style="
  background:#FFFFFF;
  border:1px solid #E2E8F0;
  border-radius:16px;
  padding:18px 22px;
  margin-bottom:16px;
  display:flex;
  gap:18px;
  align-items:center;
  justify-content:space-between;
  box-shadow: 0 10px 30px rgba(15,23,42,0.04);
">
  <div style="flex:1;">
    <div style="font-size:.72rem; color:#64748B; font-weight:900; text-transform:uppercase; letter-spacing:.12em;">Nome</div>
    <div style="font-size:1.1rem; color:#0F172A; font-weight:950;">{aluno.get('nome','-')}</div>
  </div>

  <div style="flex:1;">
    <div style="font-size:.72rem; color:#64748B; font-weight:900; text-transform:uppercase; letter-spacing:.12em;">Série</div>
    <div style="font-size:1.1rem; color:#0F172A; font-weight:900;">{aluno.get('serie','-')}</div>
  </div>

  <div style="flex:1;">
    <div style="font-size:.72rem; color:#64748B; font-weight:900; text-transform:uppercase; letter-spacing:.12em;">Hiperfoco</div>
    <div style="font-size:1.1rem; color:#22A765; font-weight:950;">{aluno.get('hiperfoco','-')}</div>
  </div>
</div>
""", unsafe_allow_html=True)

if is_ei:
    st.info("🧸 **Modo Educação Infantil ativado:** foco em Campos de Experiência (BNCC) e participação no brincar.")

with st.expander("📄 Ver resumo do PEI (base para o PAEE)", expanded=False):
    st.info(aluno.get("ia_sugestao", "Nenhum dado de PEI processado ainda."))

# ==============================================================================
# 10) OPENAI KEY
# ==============================================================================
api_key = st.secrets.get("OPENAI_API_KEY", "")
if not api_key:
    st.warning("⚠️ Chave OpenAI não encontrada em Secrets. Configure para ativar IA.")
    # (você pode trocar por input se quiser, mas sem sidebar agora)

# ==============================================================================
# 11) FUNÇÕES IA
# ==============================================================================
def gerar_diagnostico_barreiras(api_key, aluno, obs_prof):
    client = OpenAI(api_key=api_key)
    prompt = f"""
ATUAR COMO: Especialista em AEE.
ALUNO: {aluno['nome']} | HIPERFOCO: {aluno.get('hiperfoco')}
RESUMO PEI: {aluno.get('ia_sugestao', '')[:1000]}
OBSERVAÇÃO ATUAL: {obs_prof}

CLASSIFIQUE AS BARREIRAS (Lei Brasileira de Inclusão):
1) Barreiras Comunicacionais
2) Barreiras Metodológicas
3) Barreiras Atitudinais
4) Barreiras Tecnológicas/Instrumentais
SAÍDA: Tabela Markdown.
"""
    try:
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
        )
        return resp.choices[0].message.content
    except Exception as e:
        return f"Erro: {str(e)}"

def gerar_projetos_ei_bncc(api_key, aluno, campo_exp):
    client = OpenAI(api_key=api_key)
    prompt = f"""
ATUAR COMO: Pedagogo Especialista em Educação Infantil e Inclusão.
ALUNO: {aluno['nome']} (Educação Infantil).
HIPERFOCO: {aluno.get('hiperfoco', 'Brincadeiras')}.
RESUMO DAS NECESSIDADES (PEI): {aluno.get('ia_sugestao', '')[:800]}

Crie 3 propostas de EXPERIÊNCIAS LÚDICAS focadas no Campo de Experiência: "{campo_exp}".

REGRAS:
1) Usar o hiperfoco para engajar
2) Reduzir barreiras de participação
3) Ser sensorial e concreta

SAÍDA (Markdown):
### 🧸 Experiência 1: [Nome]
* Objetivo:
* Como fazer:
* Adaptação:
(repetir 2 e 3)
"""
    try:
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
        )
        return resp.choices[0].message.content
    except Exception as e:
        return str(e)

def gerar_plano_habilidades(api_key, aluno, foco_treino):
    client = OpenAI(api_key=api_key)
    prompt = f"""
Crie um PLANO DE INTERVENÇÃO AEE (Sala de Recursos).
FOCO: {foco_treino}
ALUNO: {aluno['nome']} | HIPERFOCO: {aluno.get('hiperfoco')}
Gere 3 METAS SMART (com estratégia usando hiperfoco + recurso + frequência).
"""
    try:
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
        )
        return resp.choices[0].message.content
    except Exception as e:
        return str(e)

def sugerir_tecnologia_assistiva(api_key, aluno, dificuldade):
    client = OpenAI(api_key=api_key)
    prompt = f"""
Sugestão de TECNOLOGIA ASSISTIVA.
Aluno: {aluno['nome']}
Dificuldade: {dificuldade}

Sugira:
- Baixa tecnologia (DIY)
- Média tecnologia
- Alta tecnologia
Em tópicos curtos e práticos.
"""
    try:
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
        )
        return resp.choices[0].message.content
    except Exception as e:
        return str(e)

def gerar_documento_articulacao(api_key, aluno, frequencia, acoes):
    client = OpenAI(api_key=api_key)
    prompt = f"""
Escreva uma CARTA DE ARTICULAÇÃO (AEE -> SALA REGULAR).
Aluno: {aluno['nome']}
Frequência: {frequencia}
Ações no AEE: {acoes}

Inclua:
- objetivo
- 3 combinados práticos para o professor regente
- tom colaborativo
"""
    try:
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
        )
        return resp.choices[0].message.content
    except Exception as e:
        return str(e)

# ==============================================================================
# 12) ABAS (EI vs demais)
# ==============================================================================
if is_ei:
    tab_barreiras, tab_projetos, tab_rotina, tab_ponte = st.tabs([
        "🔍 Barreiras no Brincar",
        "🧸 Banco de Experiências",
        "🏠 Rotina & Adaptação",
        "🌉 Articulação",
    ])

    with tab_barreiras:
        st.markdown("<div class='pedagogia-box'><strong>Diagnóstico do brincar:</strong> barreira não é 'não escrever' — é não participar da interação.</div>", unsafe_allow_html=True)
        obs_aee = st.text_area("Observação do brincar:", placeholder="Ex: Isola-se no parquinho, não aceita texturas...", height=100)
        if st.button("Mapear Barreiras do Brincar", type="primary"):
            if not api_key:
                st.error("Configure a chave OpenAI no Secrets para usar IA.")
                st.stop()
            with st.spinner("Analisando..."):
                st.markdown(gerar_diagnostico_barreiras(api_key, aluno, obs_aee))

    with tab_projetos:
        st.markdown("<div class='pedagogia-box'><strong>Banco de experiências (BNCC):</strong> propostas lúdicas usando o hiperfoco como motor de engajamento.</div>", unsafe_allow_html=True)
        campo_bncc = st.selectbox("Campo de Experiência (BNCC):", [
            "O eu, o outro e o nós (Identidade e Interação)",
            "Corpo, gestos e movimentos (Motricidade)",
            "Traços, sons, cores e formas (Artes)",
            "Escuta, fala, pensamento e imaginação (Oralidade)",
            "Espaços, tempos, quantidades, relações e transformações (Cognição)",
        ])
        if st.button("✨ Gerar Atividades Lúdicas", type="primary"):
            if not api_key:
                st.error("Configure a chave OpenAI no Secrets para usar IA.")
                st.stop()
            with st.spinner("Criando experiências..."):
                st.markdown(gerar_projetos_ei_bncc(api_key, aluno, campo_bncc))

    with tab_rotina:
        st.markdown("<div class='pedagogia-box'><strong>Adaptação de rotina:</strong> recursos visuais e sensoriais para creche/pré-escola.</div>", unsafe_allow_html=True)
        dif_rotina = st.text_input("Dificuldade na rotina:", placeholder="Ex: Hora do soninho, Desfralde, Alimentação")
        if st.button("Sugerir Adaptação", type="primary"):
            if not api_key:
                st.error("Configure a chave OpenAI no Secrets para usar IA.")
                st.stop()
            with st.spinner("Buscando recursos..."):
                st.markdown(sugerir_tecnologia_assistiva(api_key, aluno, f"Rotina EI: {dif_rotina}"))

else:
    tab_barreiras, tab_plano, tab_tec, tab_ponte = st.tabs([
        "🔍 Mapear Barreiras",
        "🎯 Plano de Habilidades",
        "🛠️ Tec. Assistiva",
        "🌉 Cronograma & Articulação",
    ])

    with tab_barreiras:
        st.markdown("<div class='pedagogia-box'><strong>Diagnóstico de acessibilidade:</strong> identifique o que impede participação — não o rótulo.</div>", unsafe_allow_html=True)
        obs_aee = st.text_area("Observações iniciais do AEE (opcional):", placeholder="Ex: recusa escrita, evita leitura em voz alta...", height=100)
        if st.button("Analisar Barreiras via IA", type="primary"):
            if not api_key:
                st.error("Configure a chave OpenAI no Secrets para usar IA.")
                st.stop()
            with st.spinner("Analisando..."):
                st.markdown(gerar_diagnostico_barreiras(api_key, aluno, obs_aee))

    with tab_plano:
        st.markdown("<div class='pedagogia-box'><strong>Treino de habilidades:</strong> desenvolvimento cognitivo, motor e socioemocional com foco e rotina.</div>", unsafe_allow_html=True)
        foco = st.selectbox("Foco do atendimento:", ["Funções Executivas", "Autonomia", "Coordenação Motora", "Comunicação", "Habilidades Sociais"])
        if st.button("Gerar Plano", type="primary"):
            if not api_key:
                st.error("Configure a chave OpenAI no Secrets para usar IA.")
                st.stop()
            with st.spinner("Planejando..."):
                st.markdown(gerar_plano_habilidades(api_key, aluno, foco))

    with tab_tec:
        st.markdown("<div class='pedagogia-box'><strong>Tecnologia assistiva:</strong> recursos para autonomia e acesso curricular.</div>", unsafe_allow_html=True)
        dif_especifica = st.text_input("Dificuldade específica:", placeholder="Ex: não segura o lápis, não acompanha leitura, não copia do quadro")
        if st.button("Sugerir Recursos", type="primary"):
            if not api_key:
                st.error("Configure a chave OpenAI no Secrets para usar IA.")
                st.stop()
            with st.spinner("Buscando T.A..."):
                st.markdown(sugerir_tecnologia_assistiva(api_key, aluno, dif_especifica))

# Articulação (comum)
with tab_ponte:
    st.markdown("<div class='pedagogia-box'><strong>Ponte com a sala regular:</strong> documento prático de colaboração para o professor regente.</div>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    freq = c1.selectbox("Frequência:", ["1x/sem", "2x/sem", "3x/sem", "Diário"])
    turno = c2.selectbox("Turno:", ["Manhã", "Tarde"])
    acoes_resumo = st.text_area("Trabalho no AEE:", placeholder="Ex: CAA, rotina visual, treino de FE, comunicação social...", height=80)

    if st.button("Gerar Carta", type="primary"):
        if not api_key:
            st.error("Configure a chave OpenAI no Secrets para usar IA.")
            st.stop()
        with st.spinner("Escrevendo..."):
            carta = gerar_documento_articulacao(api_key, aluno, f"{freq} ({turno})", acoes_resumo)
            st.markdown("### 📄 Documento gerado")
            st.markdown(carta)
            st.download_button("📥 Baixar Carta", carta, "Carta_Articulacao.txt")
