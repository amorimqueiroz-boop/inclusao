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
import base64

# --- 1. CONFIGURAÇÃO ---
st.set_page_config(page_title="Adaptador 360º | V12.0", page_icon="🧩", layout="wide")

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
    
    .stTabs [data-baseweb="tab-list"] { gap: 8px; flex-wrap: wrap; }
    .stTabs [data-baseweb="tab"] { border-radius: 4px; padding: 8px 16px; background-color: white; border: 1px solid #E2E8F0; font-size: 0.9rem; }
    .stTabs [aria-selected="true"] { background-color: #3182CE !important; color: white !important; }

    div[data-testid="column"] .stButton button[kind="primary"] { border-radius: 12px !important; height: 50px; width: 100%; background-color: #FF6B6B !important; color: white !important; font-weight: 800 !important; }
    div[data-testid="column"] .stButton button[kind="secondary"] { border-radius: 12px !important; height: 50px; width: 100%; background-color: white !important; color: #718096 !important; border: 2px solid #CBD5E0 !important; }
    </style>
""", unsafe_allow_html=True)

# --- 4. FUNÇÕES AUXILIARES (ARQUIVO/IMAGEM) ---
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

def sanitizar_imagem(image_bytes):
    try:
        img = Image.open(BytesIO(image_bytes)).convert("RGB")
        out = BytesIO()
        img.save(out, format="JPEG", quality=90)
        return out.getvalue()
    except: return None

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
    partes = re.split(r'(\[\[IMG.*?\d+\]\])', texto_ia, flags=re.IGNORECASE)
    
    for parte in partes:
        tag_match = re.search(r'(\d+)', parte)
        is_tag = "IMG" in parte.upper() and "[[" in parte
        if is_tag and tag_match:
            num = int(tag_match.group(1))
            img_bytes = mapa_imgs.get(num)
            if not img_bytes and len(mapa_imgs) == 1: img_bytes = list(mapa_imgs.values())[0]
            if img_bytes:
                try:
                    doc.add_picture(BytesIO(img_bytes), width=Inches(4.5))
                    doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
                    doc.add_paragraph("") 
                except: pass
        elif parte.strip():
            clean = parte.strip()
            if not (clean.startswith("[[IMG") and clean.endswith("]]")):
                doc.add_paragraph(clean)
    buffer = BytesIO(); doc.save(buffer); buffer.seek(0)
    return buffer

# --- 5. INTELIGÊNCIA ARTIFICIAL (TODAS AS FUNÇÕES) ---
def gerar_dalle_prompt(api_key, prompt_text):
    client = OpenAI(api_key=api_key)
    try:
        resp = client.images.generate(model="dall-e-3", prompt=prompt_text + " Educational style, clear lines, white background, no text.", size="1024x1024", quality="standard", n=1)
        return resp.data[0].url
    except: return None

def adaptar_conteudo_docx(api_key, aluno, texto, materia, tema, tipo_atv, remover_resp, questoes_mapeadas, temperatura=0.4):
    client = OpenAI(api_key=api_key)
    lista_q = ", ".join([str(n) for n in questoes_mapeadas])
    prompt = f"""
    ESPECIALISTA DUA.
    REGRA DE IMAGEM: O professor indicou imagens nas questões: {lista_q}.
    Para ESTAS questões, a estrutura é: 1. Texto da Questão -> 2. [[IMG_número]] -> 3. Alternativas.
    SAÍDA: [RACIONAL] ---DIVISOR--- [ATIVIDADE]
    PERFIL: Hiperfoco: {aluno.get('hiperfoco', 'Geral')} (Use em 30% das questões). PEI: {aluno.get('ia_sugestao', '')[:1000]}
    CONTEXTO: {materia} | {tema}. {"REMOVA GABARITO." if remover_resp else ""}
    TEXTO: {texto}
    """
    try:
        resp = client.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "user", "content": prompt}], temperature=temperatura)
        parts = resp.choices[0].message.content.split("---DIVISOR---")
        return (parts[0].strip(), parts[1].strip()) if len(parts)>1 else ("Adaptado.", resp.choices[0].message.content)
    except Exception as e: return str(e), ""

def adaptar_conteudo_imagem(api_key, aluno, imagem_bytes, materia, tema, tipo_atv, remover_resp, temperatura=0.4):
    client = OpenAI(api_key=api_key)
    b64 = base64.b64encode(imagem_bytes).decode('utf-8')
    prompt = f"""
    ATUAR COMO: Especialista em Acessibilidade.
    TAREFA: Descrever e adaptar material didático para aluno com necessidades específicas.
    1. Identifique o texto da imagem.
    2. Adapte considerando o PEI.
    3. Use a tag [[IMG_1]] após o enunciado principal.
    PERFIL: Hiperfoco: {aluno.get('hiperfoco')}. PEI: {aluno.get('ia_sugestao', '')[:1000]}
    SAÍDA: [RACIONAL] ---DIVISOR--- [ATIVIDADE]
    """
    try:
        resp = client.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "user", "content": [{"type": "text", "text": prompt}, {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}}]}], temperature=temperatura)
        parts = resp.choices[0].message.content.split("---DIVISOR---")
        return (parts[0].strip(), parts[1].strip()) if len(parts)>1 else ("Adaptado.", resp.choices[0].message.content)
    except Exception as e: return str(e), ""

def criar_profissional(api_key, aluno, materia, objeto, qtd, tipo_q):
    client = OpenAI(api_key=api_key)
    prompt = f"""
    PROFESSOR ELABORADOR DE ITENS (SÊNIOR).
    Crie atividade de {materia} ({objeto}) para {aluno.get('serie')}.
    QTD: {qtd} ({tipo_q}).
    REQUISITOS:
    1. Contexto Rico (textos base, situações-problema).
    2. Hiperfoco ({aluno.get('hiperfoco')}): Use em 30% das questões com profundidade (lógica/lore), não superficial.
    3. Rigor BNCC.
    4. Imagens: Sugira com [[GEN_IMG: descrição]].
    SAÍDA: [RACIONAL] ---DIVISOR--- [ATIVIDADE]
    """
    try:
        resp = client.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "user", "content": prompt}], temperature=0.6)
        parts = resp.choices[0].message.content.split("---DIVISOR---")
        return (parts[0].strip(), parts[1].strip()) if len(parts)>1 else ("Criado.", resp.choices[0].message.content)
    except Exception as e: return str(e), ""

def sugerir_imagem_pei(api_key, aluno):
    client = OpenAI(api_key=api_key)
    prompt = f"Sugira um recurso visual (imagem) para regulação/foco: {aluno.get('ia_sugestao','')[:500]}. Responda apenas o prompt em inglês."
    try:
        resp = client.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "user", "content": prompt}], temperature=0.7)
        return resp.choices[0].message.content
    except: return "Educational illustration"

# --- NOVAS FUNÇÕES V12 ---

def gerar_roteiro_aula(api_key, aluno, assunto):
    client = OpenAI(api_key=api_key)
    prompt = f"""
    CRIE UM ROTEIRO DE AULA INCLUSIVO.
    Assunto: {assunto}. Aluno: {aluno['nome']}. PEI: {aluno.get('ia_sugestao','')[:800]}.
    1. Como introduzir o tema considerando as barreiras do aluno?
    2. Quais estratégias do PEI usar durante a explicação?
    3. Como verificar a aprendizagem sem gerar ansiedade?
    """
    try:
        resp = client.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "user", "content": prompt}], temperature=0.7)
        return resp.choices[0].message.content
    except Exception as e: return str(e)

def gerar_quebra_gelo_profundo(api_key, aluno, assunto, tema_extra=""):
    client = OpenAI(api_key=api_key)
    tema = tema_extra if tema_extra else aluno.get('hiperfoco', 'Geral')
    prompt = f"""
    VOCÊ É UM ESPECIALISTA NO TEMA: {tema}.
    O aluno {aluno['nome']} também é especialista nisso. NÃO SEJA RASO.
    Objetivo: Criar pontes entre {tema} e {assunto}.
    
    Gere 3 Tópicos de Conversa (Quebra-Gelo):
    1. Uma analogia técnica/complexa entre uma mecânica/lore de {tema} e o conceito de {assunto}.
    2. Uma curiosidade obscura de {tema} que se relaciona com a aula.
    3. Uma pergunta desafio ("E se...") misturando os dois mundos.
    """
    try:
        resp = client.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "user", "content": prompt}], temperature=0.8)
        return resp.choices[0].message.content
    except Exception as e: return str(e)

def gerar_dinamica_inclusiva(api_key, aluno, assunto):
    client = OpenAI(api_key=api_key)
    prompt = f"""
    CRIE UMA DINÂMICA DE GRUPO PARA A TURMA TODA SOBRE: {assunto}.
    
    DESAFIO CRÍTICO DE INCLUSÃO:
    A turma tem o aluno {aluno['nome']} (Diagnóstico/PEI: {aluno.get('ia_sugestao','')[:800]}).
    Alunos atípicos muitas vezes não gostam de dinâmicas tradicionais barulhentas ou de toque.
    
    A DINÂMICA DEVE:
    1. Ser engajadora para a turma neurotípica.
    2. Permitir que o aluno {aluno['nome']} participe ATIVAMENTE, mas dentro de sua zona de conforto (sem gatilhos sensoriais ou sociais forçados).
    3. Usar, se possível, uma função especial para ele baseada em seus pontos fortes (descritos no PEI).
    
    SAÍDA: Nome da Dinâmica, Materiais, Passo a Passo e "O Pulo do Gato da Inclusão".
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
    if st.button("🗑️ Nova Sessão"):
        for k in list(st.session_state.keys()):
            if k not in ['banco_estudantes', 'OPENAI_API_KEY']: del st.session_state[k]
        st.rerun()

st.markdown("""<div class="header-clean"><div style="font-size:3rem;">🧩</div><div><p style="margin:0;color:#004E92;font-size:1.5rem;font-weight:800;">Adaptador V12.0: Suíte Completa</p></div></div>""", unsafe_allow_html=True)

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

# 7 ABAS DE PODER
tabs = st.tabs([
    "📄 Adaptar Prova", 
    "✂️ Adaptar Atividade", 
    "✨ Criar do Zero", 
    "🎨 Estúdio Visual", 
    "📝 Roteiro de Aula", 
    "🗣️ Papo de Mestre", 
    "🤝 Dinâmica Inclusiva"
])

# 1. ADAPTAR PROVA (WORD)
with tabs[0]:
    c1, c2, c3 = st.columns(3)
    materia_d = c1.selectbox("Matéria", ["Matemática", "Português", "Ciências", "História", "Geografia", "Artes", "Ed. Física", "Inglês"], key="dm")
    tema_d = c2.text_input("Tema", placeholder="Ex: Frações", key="dt")
    tipo_d = c3.selectbox("Tipo", ["Prova", "Tarefa"], key="dtp")
    arquivo_d = st.file_uploader("Upload DOCX", type=["docx"], key="fd")
    
    if 'docx_imgs' not in st.session_state: st.session_state.docx_imgs = []
    if 'docx_txt' not in st.session_state: st.session_state.docx_txt = None
    
    if arquivo_d and arquivo_d.file_id != st.session_state.get('last_d'):
        st.session_state.last_d = arquivo_d.file_id
        txt, imgs = extrair_dados_docx(arquivo_d)
        st.session_state.docx_txt = txt; st.session_state.docx_imgs = imgs
        st.success(f"{len(imgs)} imagens.")

    map_d = {}; qs_d = []
    if st.session_state.docx_imgs:
        st.write("### Mapeamento")
        cols = st.columns(3)
        for i, img in enumerate(st.session_state.docx_imgs):
            with cols[i % 3]:
                st.image(img, width=80)
                q = st.number_input(f"Questão:", 0, 50, key=f"dq_{i}")
                if q > 0: map_d[int(q)] = img; qs_d.append(int(q))

    c_go, c_redo = st.columns([3, 1])
    if c_go.button("🚀 ADAPTAR PROVA", type="primary", key="btn_d"):
        if not st.session_state.docx_txt: st.warning("Envie arquivo."); st.stop()
        with st.spinner("Adaptando..."):
            rac, txt = adaptar_conteudo_docx(api_key, aluno, st.session_state.docx_txt, materia_d, tema_d, tipo_d, True, qs_d)
            st.session_state['res_docx'] = {'rac': rac, 'txt': txt, 'map': map_d}
            st.rerun()

    if 'res_docx' in st.session_state:
        res = st.session_state['res_docx']
        if c_redo.button("🔄 Refazer", key="redo_d"):
            with st.spinner("Refazendo..."):
                rac, txt = adaptar_conteudo_docx(api_key, aluno, st.session_state.docx_txt, materia_d, tema_d, tipo_d, True, qs_d, temperatura=0.8)
                st.session_state['res_docx'] = {'rac': rac, 'txt': txt, 'map': map_d}
                st.rerun()
        with st.expander("🧠 Racional"): st.info(res['rac'])
        with st.container(border=True):
            partes = re.split(r'(\[\[IMG.*?\d+\]\])', res['txt'], flags=re.IGNORECASE)
            for p in partes:
                tag = re.search(r'(\d+)', p)
                if "IMG" in p.upper() and tag:
                    i = int(tag.group(1))
                    im = res['map'].get(i)
                    if im: st.image(im, width=300)
                elif p.strip(): st.markdown(p.strip())
        docx = construir_docx_final(res['txt'], aluno, materia_d, res['map'], None, tipo_d)
        st.download_button("📥 BAIXAR DOCX", docx, "Prova.docx", "primary")

# 2. ADAPTAR ATIVIDADE (PRINT)
with tabs[1]:
    c1, c2, c3 = st.columns(3)
    discip = ["Matemática", "Português", "Ciências", "História", "Geografia", "Artes", "Ed. Física", "Inglês", "Filosofia", "Sociologia", "Física", "Química", "Biologia"]
    materia_i = c1.selectbox("Matéria", discip, key="im")
    tema_i = c2.text_input("Tema", key="it")
    tipo_i = c3.selectbox("Tipo", ["Atividade", "Tarefa"], key="itp")
    arquivo_i = st.file_uploader("Upload Imagem", type=["png","jpg","jpeg"], key="fi")
    
    if 'img_raw' not in st.session_state: st.session_state.img_raw = None
    if arquivo_i and arquivo_i.file_id != st.session_state.get('last_i'):
        st.session_state.last_i = arquivo_i.file_id
        st.session_state.img_raw = sanitizar_imagem(arquivo_i.getvalue())

    cropped_res = None
    if st.session_state.img_raw:
        st.markdown("### ✂️ Recorte")
        img_pil = Image.open(BytesIO(st.session_state.img_raw))
        img_pil.thumbnail((800, 800))
        cropped_res = st_cropper(img_pil, realtime_update=True, box_color='#FF0000', aspect_ratio=None, key="crop_i")
        if cropped_res: st.image(cropped_res, width=200, caption="Prévia")

    c_go_i, c_redo_i = st.columns([3, 1])
    if c_go_i.button("🚀 ADAPTAR RECORTE", type="primary", key="btn_i"):
        if not cropped_res: st.warning("Recorte inválido."); st.stop()
        with st.spinner("Lendo e Adaptando..."):
            buf_c = BytesIO()
            cropped_res.convert('RGB').save(buf_c, format="JPEG", quality=90)
            img_bytes = buf_c.getvalue()
            rac, txt = adaptar_conteudo_imagem(api_key, aluno, img_bytes, materia_i, tema_i, tipo_i, True)
            st.session_state['res_img'] = {'rac': rac, 'txt': txt, 'map': {1: img_bytes}}
            st.rerun()

    if 'res_img' in st.session_state:
        res = st.session_state['res_img']
        if c_redo_i.button("🔄 Refazer", key="redo_i"):
             with st.spinner("Refazendo..."):
                img_bytes = res['map'][1]
                rac, txt = adaptar_conteudo_imagem(api_key, aluno, img_bytes, materia_i, tema_i, tipo_i, True, temperatura=0.9)
                st.session_state['res_img']['rac'] = rac
                st.session_state['res_img']['txt'] = txt
                st.rerun()
        with st.expander("🧠 Racional"): st.info(res['rac'])
        with st.container(border=True):
            partes = re.split(r'(\[\[IMG.*?\]\])', res['txt'], flags=re.IGNORECASE)
            for p in partes:
                if "IMG" in p.upper():
                    im = res['map'].get(1)
                    if im: st.image(im, width=300)
                elif p.strip(): st.markdown(p.strip())
        docx = construir_docx_final(res['txt'], aluno, materia_i, res['map'], None, tipo_i)
        st.download_button("📥 BAIXAR DOCX", docx, "Atividade.docx", "primary")

# 3. CRIAR DO ZERO
with tabs[2]:
    cc1, cc2 = st.columns(2)
    mat_c = cc1.selectbox("Componente", discip, key="cm")
    obj_c = cc2.text_input("Assunto", key="co")
    
    cc3, cc4 = st.columns(2)
    qtd_c = cc3.slider("Qtd", 1, 10, 5, key="cq")
    tipo_quest = cc4.selectbox("Tipo", ["Objetiva", "Discursiva", "Mista"], key="ctq")
    
    c_go_c, c_redo_c = st.columns([3, 1])
    if c_go_c.button("✨ CRIAR ATIVIDADE", type="primary", key="btn_c"):
        with st.spinner("Criando..."):
            rac, txt = criar_profissional(api_key, aluno, mat_c, obj_c, qtd_c, tipo_quest)
            novo_map = {}; count = 0
            tags = re.findall(r'\[\[GEN_IMG: (.*?)\]\]', txt)
            for p in tags:
                count += 1
                url = gerar_dalle_prompt(api_key, p)
                if url:
                    io = baixar_imagem_url(url)
                    if io: novo_map[count] = io.getvalue()
            txt_fin = txt
            for i in range(1, count + 1): 
                txt_fin = re.sub(r'\[\[GEN_IMG: .*?\]\]', f"[[IMG_G{i}]]", txt_fin, count=1)
            st.session_state['res_create'] = {'rac': rac, 'txt': txt_fin, 'map': novo_map}
            st.rerun()

    if 'res_create' in st.session_state:
        res = st.session_state['res_create']
        if c_redo_c.button("🔄 Refazer", key="redo_c"):
             with st.spinner("Reescrevendo..."):
                rac, txt = criar_profissional(api_key, aluno, mat_c, obj_c, qtd_c, tipo_quest, temperatura=0.9)
                st.session_state['res_create']['rac'] = rac
                st.session_state['res_create']['txt'] = txt
                st.rerun()
        with st.expander("🧠 Racional"): st.info(res['rac'])
        with st.container(border=True):
            partes = re.split(r'(\[\[IMG_G\d+\]\])', res['txt'])
            for p in partes:
                tag = re.search(r'\[\[IMG_G(\d+)\]\]', p)
                if tag:
                    i = int(tag.group(1))
                    im = res['map'].get(i)
                    if im: st.image(im, width=300)
                elif p.strip(): st.markdown(p.strip())
        docx = construir_docx_final(res['txt'], aluno, mat_c, {}, None, "Criada")
        st.download_button("📥 BAIXAR DOCX", docx, "Criada.docx", "primary")

# 4. ESTÚDIO VISUAL
with tabs[3]:
    if st.button("✨ MÁGICA DO PEI (Gerar Auto)", type="primary"):
        with st.spinner("Desenhando..."):
            desc_auto = sugerir_imagem_pei(api_key, aluno)
            url = gerar_dalle_prompt(api_key, desc_auto)
            if url: st.image(url, caption=f"Sugestão: {desc_auto}")
    st.markdown("---")
    desc = st.text_area("Descrição Manual:", key="vd")
    if st.button("🎨 Gerar"):
        url = gerar_dalle_prompt(api_key, f"{desc} style {aluno.get('hiperfoco')}")
        if url: st.image(url)

# 5. ROTEIRO DE AULA (ANTIGO CONTEXTUALIZAR)
with tabs[4]:
    st.info("Planejamento da Explicação.")
    ass = st.text_input("O que você vai ensinar?", key="rot_ass")
    if st.button("📝 CRIAR ROTEIRO", type="primary"):
        with st.spinner("Planejando..."):
            st.markdown(gerar_roteiro_aula(api_key, aluno, ass))

# 6. PAPO DE MESTRE (QUEBRA-GELO PROFUNDO)
with tabs[5]:
    st.info(f"Conectando com o universo: {aluno.get('hiperfoco')}")
    c1, c2 = st.columns(2)
    ass_q = c1.text_input("Assunto da Aula:", key="qg_ass")
    tema_q = c2.text_input("Tema (Hiperfoco):", value=aluno.get('hiperfoco'), key="qg_tema")
    
    if st.button("🗣️ GERAR CONVERSA", type="primary"):
        with st.spinner("Consultando a Lore..."):
            st.markdown(gerar_quebra_gelo_profundo(api_key, aluno, ass_q, tema_q))

# 7. DINÂMICA INCLUSIVA
with tabs[6]:
    st.info("Atividade em Grupo Segura.")
    ass_d = st.text_input("Tema da Dinâmica:", key="din_ass")
    if st.button("🤝 CRIAR PROPOSTA", type="primary"):
        with st.spinner("Adaptando regras sociais..."):
            st.markdown(gerar_dinamica_inclusiva(api_key, aluno, ass_d))
