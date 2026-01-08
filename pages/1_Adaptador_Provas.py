import streamlit as st
from openai import OpenAI
from io import BytesIO
from docx import Document
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from PIL import Image
from streamlit_cropper import st_cropper
import re
import requests
import json

# --- 1. CONFIGURAÇÃO ---
st.set_page_config(page_title="Adaptador 360º | V9.1", page_icon="🧩", layout="wide")

# --- 2. BANCO DE DADOS ---
ARQUIVO_DB = "banco_alunos.json"

def carregar_banco():
    if os.path.exists(ARQUIVO_DB):
        try:
            with open(ARQUIVO_DB, "r", encoding="utf-8") as f:
                return json.load(f)
        except: return []
    return []

if 'banco_estudantes' not in st.session_state or not st.session_state.banco_estudantes:
    st.session_state.banco_estudantes = carregar_banco()

# --- 3. ESTILO VISUAL ---
st.markdown("""
    <style>
    html, body, [class*="css"] { font-family: 'Nunito', sans-serif; color: #2D3748; }
    .header-clean { background: white; padding: 25px; border-radius: 16px; border: 1px solid #EDF2F7; margin-bottom: 20px; display: flex; gap: 20px; align-items: center; }
    .student-header { background-color: #EBF8FF; border: 1px solid #BEE3F8; border-radius: 12px; padding: 15px 25px; margin-bottom: 25px; display: flex; justify-content: space-between; align-items: center; }
    .student-label { font-size: 0.85rem; color: #718096; font-weight: 700; text-transform: uppercase; }
    .student-value { font-size: 1.1rem; color: #2C5282; font-weight: 800; }
    .crop-instruction { background: #EBF8FF; border-left: 4px solid #3182CE; padding: 15px; color: #2C5282; border-radius: 4px; margin-bottom: 10px; }
    
    /* Abas */
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] { border-radius: 4px; padding: 10px 20px; background-color: white; border: 1px solid #E2E8F0; }
    .stTabs [aria-selected="true"] { background-color: #3182CE !important; color: white !important; }

    div[data-testid="column"] .stButton button[kind="primary"] { border-radius: 12px !important; height: 50px; width: 100%; background-color: #FF6B6B !important; color: white !important; font-weight: 800 !important; }
    div[data-testid="column"] .stButton button[kind="secondary"] { border-radius: 12px !important; height: 50px; width: 100%; background-color: white !important; color: #718096 !important; border: 2px solid #CBD5E0 !important; }
    </style>
""", unsafe_allow_html=True)

# --- 4. FUNÇÕES DE ARQUIVO ---
def extrair_dados_docx(uploaded_file):
    uploaded_file.seek(0); imagens = []; texto = ""
    try:
        doc = Document(uploaded_file)
        texto = "\n".join([p.text for p in doc.paragraphs if p.text.strip() != ""])
        for rel in doc.part.rels.values():
            if "image" in rel.target_ref:
                img_data = rel.target_part.blob
                if len(img_data) > 1024: imagens.append(img_data)
    except: pass
    return texto, imagens

def baixar_imagem_url(url):
    try:
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200: return BytesIO(resp.content)
    except: pass
    return None

def construir_docx_final(texto_ia, aluno, materia, mapa_imgs, img_dalle_url, tipo_atv):
    doc = Document(); style = doc.styles['Normal']; style.font.name = 'Arial'; style.font.size = Pt(12)
    doc.add_heading(f'{tipo_atv.upper()} ADAPTADA - {materia.upper()}', 0).alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_paragraph(f"Estudante: {aluno['nome']}").alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_paragraph("_"*50)

    if img_dalle_url:
        img_io = baixar_imagem_url(img_dalle_url)
        if img_io:
            doc.add_heading('Apoio Visual', level=3)
            doc.add_picture(img_io, width=Inches(4.5))
            doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
            doc.add_paragraph("")

    doc.add_heading('Atividades', level=2)
    
    # Processa tags [[IMG_1]]
    partes = re.split(r'(\[\[IMG_\d+\]\])', texto_ia)
    
    for parte in partes:
        tag_match = re.search(r'\[\[IMG_(\d+)\]\]', parte)
        if tag_match:
            num = int(tag_match.group(1))
            # Busca imagem no mapa (pelo numero da questao ou indice sequencial)
            img_bytes = mapa_imgs.get(num)
            # Se for imagem única (recorte), usa ela independente do número
            if not img_bytes and len(mapa_imgs) == 1:
                img_bytes = list(mapa_imgs.values())[0]

            if img_bytes:
                try:
                    doc.add_picture(BytesIO(img_bytes), width=Inches(4.5))
                    doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
                    doc.add_paragraph("") 
                except: pass
        elif parte.strip():
            doc.add_paragraph(parte.strip())
            
    buffer = BytesIO(); doc.save(buffer); buffer.seek(0)
    return buffer

# --- 5. INTELIGÊNCIA ARTIFICIAL ---
def gerar_dalle_prompt(api_key, prompt_text):
    client = OpenAI(api_key=api_key)
    try:
        resp = client.images.generate(model="dall-e-3", prompt=prompt_text + " Educational style, clear, autism-friendly, white background, no text.", size="1024x1024", quality="standard", n=1)
        return resp.data[0].url
    except: return None

# MÓDULO ADAPTAR (ESTRATÉGIA SANDUÍCHE)
def adaptar_conteudo(api_key, aluno, conteudo, tipo, materia, tema, tipo_atv, remover_resp, questoes_mapeadas):
    client = OpenAI(api_key=api_key)
    
    lista_q = ", ".join([str(n) for n in questoes_mapeadas])
    
    prompt = f"""
    ADAPTADOR DE ATIVIDADE ESCOLAR.
    
    REGRA CRÍTICA DE IMAGENS (ESTRATÉGIA SANDUÍCHE):
    O professor indicou que existem imagens para as questões: {lista_q}.
    Ao escrever essas questões, você DEVE seguir esta ordem estrita:
    
    1. Número e Enunciado da Questão.
    2. A tag [[IMG_número]] (EXATAMENTE AQUI, NO MEIO).
    3. As Alternativas (A, B, C...) ou linhas de resposta.
    
    ERRADO: Enunciado -> Alternativas -> [[IMG_1]] (NÃO FAÇA ISSO!)
    CERTO: Enunciado -> [[IMG_1]] -> Alternativas.
    
    ESTRUTURA DE SAÍDA:
    [RACIONAL] (Breve explicação)
    ---DIVISOR---
    [ATIVIDADE] (Conteúdo pronto para o aluno)
    
    PEI DO ALUNO: {aluno.get('ia_sugestao', '')[:1500]}
    {"REMOVA TODAS AS RESPOSTAS." if remover_resp else ""}
    CONTEXTO: {materia} | {tema}
    CONTEÚDO ORIGINAL:
    """
    
    msgs = [{"role": "user", "content": []}]
    if tipo == "imagem":
        b64 = base64.b64encode(conteudo).decode('utf-8')
        msgs[0]["content"].append({"type": "text", "text": prompt})
        msgs[0]["content"].append({"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}})
    else:
        msgs[0]["content"].append({"type": "text", "text": prompt + "\n" + str(conteudo)})

    try:
        resp = client.chat.completions.create(model="gpt-4o-mini", messages=msgs, temperature=0.3)
        parts = resp.choices[0].message.content.split("---DIVISOR---")
        return (parts[0].strip(), parts[1].strip()) if len(parts)>1 else ("Adaptado.", resp.choices[0].message.content)
    except Exception as e: return str(e), ""

# MÓDULO CRIAR (OPÇÃO DUPLA)
def criar_duas_opcoes(api_key, aluno, materia, objeto, qtd, tipo_q):
    client = OpenAI(api_key=api_key)
    hiperfoco = aluno.get('hiperfoco', 'Geral')
    
    prompt = f"""
    CRIE DUAS VERSÕES DE UMA ATIVIDADE DE {materia} ({objeto}) PARA {aluno.get('serie')}.
    QTD: {qtd} questões ({tipo_q}).
    PEI: {aluno.get('ia_sugestao', '')[:1000]}
    
    --- OPÇÃO A: LÚDICA (Imersão Total) ---
    Use o hiperfoco ({hiperfoco}) como narrativa principal. O aluno é o protagonista nesse mundo.
    
    --- OPÇÃO B: ESTRUTURADA (Foco Conteúdo) ---
    Use o hiperfoco apenas como contexto leve, priorizando a estrutura acadêmica clara.
    
    REGRAS PARA AMBAS:
    1. A cada 5 questões, coloque uma tag [[GEN_IMG: descrição]] onde couber uma imagem.
    
    SAÍDA:
    [RACIONAL]
    ---SPLIT_A---
    [CONTEUDO_A]
    ---SPLIT_B---
    [CONTEUDO_B]
    """
    
    try:
        resp = client.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "user", "content": prompt}], temperature=0.7)
        full = resp.choices[0].message.content
        try:
            racional = full.split("---SPLIT_A---")[0].replace("[RACIONAL]", "").strip()
            rest = full.split("---SPLIT_A---")[1]
            opt_a = rest.split("---SPLIT_B---")[0].strip()
            opt_b = rest.split("---SPLIT_B---")[1].strip()
            return racional, opt_a, opt_b
        except: return "Erro formato.", full, full
    except Exception as e: return str(e), "", ""

# MÓDULO CONTEXTUALIZAR (O RETORNO)
def gerar_contextualizacao(api_key, aluno, assunto, tema_extra=""):
    client = OpenAI(api_key=api_key)
    tema = tema_extra if tema_extra else aluno.get('hiperfoco', 'Geral')
    
    prompt = f"""
    VOCÊ É UM CONSULTOR DE INCLUSÃO.
    Objetivo: Ajudar o professor a explicar '{assunto}' para o aluno {aluno['nome']} (Série: {aluno.get('serie')}).
    Hiperfoco/Interesse: {tema}.
    PEI: {aluno.get('ia_sugestao', '')[:800]}
    
    GERE UM GUIA RÁPIDO:
    1. 🧊 **Quebra-Gelo:** Uma pergunta ou curiosidade sobre {tema} que ligue ao assunto.
    2. 🔗 **Analogia de Ouro:** Como explicar o conceito difícil usando a lógica de {tema}?
    3. 🧠 **Dica Sensorial:** Uma estratégia baseada no PEI para manter o foco durante essa explicação.
    """
    try:
        resp = client.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "user", "content": prompt}], temperature=0.7)
        return resp.choices[0].message.content
    except Exception as e: return str(e)

# --- 6. INTERFACE ---
with st.sidebar:
    if 'OPENAI_API_KEY' in st.secrets: api_key = st.secrets['OPENAI_API_KEY']; st.success("✅ Conectado")
    else: api_key = st.text_input("Chave OpenAI:", type="password")
    
    st.markdown("---")
    if st.button("🗑️ Nova Sessão (Limpar Tudo)"):
        for k in list(st.session_state.keys()):
            if k not in ['banco_estudantes', 'OPENAI_API_KEY']: del st.session_state[k]
        st.rerun()

st.markdown("""<div class="header-clean"><div style="font-size:3rem;">🧩</div><div><p style="margin:0;color:#004E92;font-size:1.5rem;font-weight:800;">Adaptador V9.1: Hub Completo</p></div></div>""", unsafe_allow_html=True)

if not st.session_state.banco_estudantes:
    st.warning("⚠️ Cadastre um aluno no PEI 360º primeiro.")
    st.stop()

lista = [a['nome'] for a in st.session_state.banco_estudantes]
nome_aluno = st.selectbox("📂 Selecione o Estudante:", lista)
aluno = next(a for a in st.session_state.banco_estudantes if a['nome'] == nome_aluno)

st.markdown(f"""
    <div class="student-header">
        <div class="student-info-item"><div class="student-label">Nome</div><div class="student-value">{aluno.get('nome')}</div></div>
        <div class="student-info-item"><div class="student-label">Série</div><div class="student-value">{aluno.get('serie', '-')}</div></div>
        <div class="student-info-item"><div class="student-label">Hiperfoco</div><div class="student-value">{aluno.get('hiperfoco', '-')}</div></div>
    </div>
""", unsafe_allow_html=True)

# 4 ABAS RESTAURADAS
tab_adapt, tab_create, tab_visual, tab_ctx = st.tabs(["📂 Adaptar Arquivo", "✨ Criar (Opções A/B)", "🎨 Estúdio Visual", "💡 Contextualizador"])

# 1. ADAPTAR
with tab_adapt:
    c1, c2, c3 = st.columns(3)
    materia = c1.selectbox("Matéria", ["Matemática", "Português", "Ciências", "História", "Geografia"], key="am")
    tema = c2.text_input("Tema Original", placeholder="Ex: Frações", key="at")
    tipo_atv = c3.selectbox("Tipo", ["Prova", "Tarefa", "Atividade"], key="atip")

    arquivo = st.file_uploader("Arquivo (FOTO ou DOCX)", type=["png","jpg","jpeg","docx"], key="af")
    
    if 'adapt_imgs' not in st.session_state: st.session_state.adapt_imgs = []
    if 'adapt_txt' not in st.session_state: st.session_state.adapt_txt = None
    if 'adapt_type' not in st.session_state: st.session_state.adapt_type = None

    if arquivo:
        if arquivo.file_id != st.session_state.get('a_last_id'):
            st.session_state.a_last_id = arquivo.file_id
            st.session_state.adapt_imgs = []
            if "image" in arquivo.type:
                st.session_state.adapt_type = "imagem"
                st.markdown("<div class='crop-instruction'>✂️ <b>TESOURA DIGITAL:</b> Recorte e confirme.</div>", unsafe_allow_html=True)
                img = Image.open(arquivo).convert("RGB")
                buf = BytesIO(); img.save(buf, format="JPEG"); st.session_state.adapt_txt = buf.getvalue()
                img.thumbnail((1000, 1000))
                cropped = st_cropper(img, realtime_update=False, box_color='#FF0000', aspect_ratio=None, key="crop1")
                if st.button("✂️ CONFIRMAR RECORTE", key="cut_btn"):
                    buf_c = BytesIO(); cropped.save(buf_c, format="JPEG")
                    st.session_state.adapt_imgs = [buf_c.getvalue()]
                    st.rerun()
            elif "word" in arquivo.type:
                st.session_state.adapt_type = "docx"
                txt, imgs = extrair_dados_docx(arquivo)
                st.session_state.adapt_txt = txt
                st.session_state.adapt_imgs = imgs
                st.success(f"DOCX: {len(imgs)} imagens encontradas.")

    adapt_map = {}
    adapt_qs = []
    if st.session_state.adapt_imgs:
        if st.session_state.adapt_type == "docx":
            st.info("Mapeamento: Digite o número da questão para cada imagem (0 para ignorar).")
            cols = st.columns(3)
            for i, img in enumerate(st.session_state.adapt_imgs):
                with cols[i % 3]:
                    st.image(img, width=80)
                    q = st.number_input(f"Q:", 0, 50, key=f"qmap_{i}")
                    if q > 0: adapt_map[int(q)] = img; adapt_qs.append(int(q))
        else:
            adapt_map[1] = st.session_state.adapt_imgs[0]

    if st.button("🚀 GERAR ADAPTAÇÃO", type="primary", key="btn_adapt"):
        with st.spinner("Adaptando com regra 'sanduíche' de imagens..."):
            rac, txt = adaptar_conteudo(api_key, aluno, st.session_state.adapt_txt, st.session_state.adapt_type, materia, tema, tipo_atv, True, adapt_qs)
            st.session_state['res_adapt'] = {'rac': rac, 'txt': txt, 'map': adapt_map}
            st.rerun()

    if 'res_adapt' in st.session_state:
        res = st.session_state['res_adapt']
        st.markdown("---")
        with st.expander("🧠 Ver Racional Pedagógico", expanded=False): st.info(res['rac'])
        st.subheader("👁️ Resultado Final")
        with st.container(border=True):
            partes = re.split(r'(\[\[IMG_\d+\]\])', res['txt'])
            for p in partes:
                tag = re.search(r'\[\[IMG_(\d+)\]\]', p)
                if tag:
                    i = int(tag.group(1))
                    im = res['map'].get(i)
                    if not im and len(res['map']) == 1: im = list(res['map'].values())[0]
                    if im: st.image(im, width=300)
                elif p.strip(): st.markdown(p.strip())
        
        docx = construir_docx_final(res['txt'], aluno, materia, res['map'], None, tipo_atv)
        st.download_button("📥 BAIXAR DOCX", docx, "Atividade_Adaptada.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document", type="primary", use_container_width=True)

# 2. CRIAR DO ZERO
with tab_create:
    cc1, cc2 = st.columns(2)
    mat_c = cc1.selectbox("Componente", ["Matemática", "Português", "Ciências", "História", "Geografia"], key="cm")
    obj_c = cc2.text_input("Objeto de Conhecimento", placeholder="Ex: Sistema Solar", key="co")
    cc3, cc4 = st.columns(2)
    qtd_c = cc3.slider("Quantidade", 1, 10, 5, key="cq")
    tipo_c = cc4.selectbox("Formato", ["Múltipla Escolha", "Discursiva", "Mista"], key="ct")
    
    if st.button("✨ CRIAR (GERAR OPÇÕES)", type="primary", key="btn_create"):
        with st.spinner(f"Criando opções A e B..."):
            rac, opt_a, opt_b = criar_duas_opcoes(api_key, aluno, mat_c, obj_c, qtd_c, tipo_c)
            st.session_state['create_opts'] = {'rac': rac, 'A': opt_a, 'B': opt_b}
            st.rerun()

    if 'create_opts' in st.session_state:
        opts = st.session_state['create_opts']
        with st.expander("🧠 Racional Pedagógico", expanded=False): st.info(opts['rac'])
        st.write("### Escolha a versão:")
        tab_a, tab_b = st.tabs(["🅰️ Opção A (Lúdica)", "🅱️ Opção B (Estruturada)"])
        
        with tab_a:
            st.markdown(opts['A'])
            if st.button("✅ ESCOLHER A", key="sel_a"):
                st.session_state['final_create'] = opts['A']; st.rerun()
        with tab_b:
            st.markdown(opts['B'])
            if st.button("✅ ESCOLHER B", key="sel_b"):
                st.session_state['final_create'] = opts['B']; st.rerun()

    if 'final_create' in st.session_state:
        txt_base = st.session_state['final_create']
        st.markdown("---")
        
        if 'create_map' not in st.session_state:
            novo_map = {}; count = 0
            tags = re.findall(r'\[\[GEN_IMG: (.*?)\]\]', txt_base)
            with st.spinner(f"Gerando {len(tags)} imagens..."):
                for p in tags:
                    count += 1
                    url = gerar_dalle_prompt(api_key, p)
                    if url:
                        io = baixar_imagem_url(url)
                        if io: novo_map[count] = io.getvalue()
            
            txt_fin = txt_base
            for i in range(1, count + 1): 
                txt_fin = re.sub(r'\[\[GEN_IMG: .*?\]\]', f"[[IMG_{i}]]", txt_fin, count=1)
            
            st.session_state['create_map'] = novo_map
            st.session_state['create_txt_final'] = txt_fin
            st.rerun()

        with st.container(border=True):
            partes = re.split(r'(\[\[IMG_\d+\]\])', st.session_state['create_txt_final'])
            for p in partes:
                tag = re.search(r'\[\[IMG_(\d+)\]\]', p)
                if tag:
                    idx = int(tag.group(1))
                    im = st.session_state['create_map'].get(idx)
                    if im: st.image(im, width=300)
                elif p.strip(): st.markdown(p.strip())

        docx = construir_docx_final(st.session_state['create_txt_final'], aluno, mat_c, st.session_state['create_map'], None, "Atividade Criada")
        st.download_button("📥 BAIXAR DOCX FINAL", docx, "Atividade_Criada.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document", type="primary", use_container_width=True)

# 3. VISUAL
with tab_visual:
    st.info("Estúdio Visual: Crie recursos de apoio.")
    desc = st.text_area("Descrição:", placeholder="Ex: Rotina visual...", key="vd")
    if st.button("🎨 GERAR", type="primary", key="v_btn"):
        with st.spinner("Desenhando..."):
            url = gerar_dalle_prompt(api_key, f"{desc} with {aluno.get('hiperfoco')} theme")
            if url: st.image(url)

# 4. CONTEXTO
with tab_ctx:
    st.info("Quebra-Gelo Pedagógico.")
    ass = st.text_input("Assunto:", key="cx_ass")
    t_extra = st.text_input("Tema (Opcional):", placeholder="Ex: Minecraft", key="cx_tema")
    if st.button("💡 EXPLICAR", type="primary", key="cx_btn"):
        with st.spinner("Pensando..."):
            st.markdown(gerar_contextualizacao(api_key, aluno, ass, t_extra))
