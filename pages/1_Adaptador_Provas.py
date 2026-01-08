import streamlit as st
from openai import OpenAI
from io import BytesIO
from docx import Document
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from pypdf import PdfReader
from PIL import Image
from streamlit_cropper import st_cropper
import base64
import os
import re
import requests
import zipfile
import json

# --- 1. CONFIGURAÇÃO ---
st.set_page_config(page_title="Adaptador 360º | V8.2", page_icon="🧩", layout="wide")

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
    
    /* Card Aluno */
    .student-header { background-color: #EBF8FF; border: 1px solid #BEE3F8; border-radius: 12px; padding: 15px 25px; margin-bottom: 25px; display: flex; justify-content: space-between; align-items: center; }
    .student-label { font-size: 0.85rem; color: #718096; font-weight: 700; text-transform: uppercase; }
    .student-value { font-size: 1.1rem; color: #2C5282; font-weight: 800; }
    
    /* Botões */
    div[data-testid="column"] .stButton button[kind="primary"] { border-radius: 12px !important; height: 50px; width: 100%; background-color: #FF6B6B !important; color: white !important; font-weight: 800 !important; }
    div[data-testid="column"] .stButton button[kind="secondary"] { border-radius: 12px !important; height: 50px; width: 100%; background-color: white !important; color: #718096 !important; border: 2px solid #CBD5E0 !important; }
    
    /* Editor */
    .stTextArea textarea { border: 1px solid #CBD5E0; border-radius: 8px; font-family: monospace; font-size: 14px; }
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

def construir_docx_final(texto_ia, aluno, materia, mapa_imgs, tipo_atv):
    doc = Document(); style = doc.styles['Normal']; style.font.name = 'Arial'; style.font.size = Pt(12)
    doc.add_heading(f'{tipo_atv.upper()} ADAPTADA - {materia.upper()}', 0).alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_paragraph(f"Estudante: {aluno['nome']}").alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_paragraph("_"*50)

    doc.add_heading('Atividades', level=2)
    
    # Processa tags e insere imagens no fluxo
    partes = re.split(r'(\[\[IMG_[Q|G]\w+\]\])', texto_ia)
    
    for parte in partes:
        tag_match = re.match(r'\[\[IMG_(Q|G)(\w+)\]\]', parte)
        
        if tag_match:
            tipo, id_img = tag_match.groups()
            img_bytes = None
            
            # Recupera a imagem do mapa (Q=Original, G=Gerada)
            if tipo == "Q": 
                try: 
                    num = int(id_img)
                    img_bytes = mapa_imgs.get(num, mapa_imgs.get(0))
                except: pass
            elif tipo == "G":
                img_bytes = mapa_imgs.get(f"G{id_img}")

            if img_bytes:
                try:
                    doc.add_picture(BytesIO(img_bytes), width=Inches(4.5))
                    doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
                    doc.add_paragraph("") # Espaço após imagem
                except: pass
        
        elif parte.strip():
            # Remove restos de instruções da IA se houver
            clean_text = parte.replace("Utilize a tag", "").replace("Insira a imagem", "").strip()
            if clean_text: doc.add_paragraph(clean_text)
            
    buffer = BytesIO(); doc.save(buffer); buffer.seek(0)
    return buffer

# --- 5. INTELIGÊNCIA ARTIFICIAL ---

def gerar_dalle_prompt(api_key, prompt_text):
    """Gera uma imagem pedagógica clara"""
    client = OpenAI(api_key=api_key)
    try:
        # Prompt forçado para estilo limpo e escolar
        safe_prompt = f"Educational illustration showing: {prompt_text}. Clear lines, white background, textbook style, autism-friendly colors. No text labels."
        resp = client.images.generate(model="dall-e-3", prompt=safe_prompt, size="1024x1024", quality="standard", n=1)
        return resp.data[0].url
    except: return None

def get_hiperfoco_instruction(aluno):
    return f"""
    REGRA DE OURO (Hiperfoco: {aluno.get('hiperfoco', 'Geral')}):
    - Use o tema do hiperfoco em cerca de 30% das questões para engajar.
    - Nas outras questões, mantenha contextos neutros/escolares.
    - O objetivo é criar conexão sem infantilizar o aluno.
    """

# MÓDULO ADAPTAR
def adaptar_conteudo(api_key, aluno, conteudo, tipo, materia, tema, tipo_atv, remover_resp, questoes_mapeadas, temperatura=0.4):
    client = OpenAI(api_key=api_key)
    
    if tipo == "docx":
        lista_q = ", ".join([str(n) for n in questoes_mapeadas])
        instrucao_imgs = f"DOCX: Existem imagens originais para as questões {lista_q}. Insira a tag [[IMG_QX]] IMEDIATAMENTE após o enunciado da questão X."
    else:
        instrucao_imgs = "FOTO: Use a tag [[IMG_Q1]] para a imagem recortada. Coloque-a logo abaixo do enunciado principal."

    prompt = f"""
    Especialista em BNCC.
    OBJETIVO: Adaptar atividade escolar.
    
    ESTRUTURA DE SAÍDA OBRIGATÓRIA:
    [RACIONAL PEDAGÓGICO] (Explique brevemente as adaptações feitas)
    ---DIVISOR---
    [ATIVIDADE] (Apenas o conteúdo final para o aluno)
    
    DIRETRIZES:
    1. {"REMOVA TODAS AS RESPOSTAS/GABARITO." if remover_resp else ""}
    2. {instrucao_imgs}
    3. {get_hiperfoco_instruction(aluno)}
    4. PEI: {aluno.get('ia_sugestao', '')[:1000]}
    
    CONTEXTO: {materia} | {tema} | {tipo_atv}
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
        resp = client.chat.completions.create(model="gpt-4o-mini", messages=msgs, temperature=temperatura, max_tokens=4000)
        content = resp.choices[0].message.content
        if "---DIVISOR---" in content:
            parts = content.split("---DIVISOR---")
            return parts[0].strip(), parts[1].strip(), None
        return "Adaptação realizada.", content, None
    except Exception as e: return None, None, str(e)

# MÓDULO CRIAR (COM IMAGENS INTELIGENTES)
def criar_do_zero(api_key, aluno, materia, objeto, qtd, tipo_q, temperatura=0.7):
    client = OpenAI(api_key=api_key)
    
    prompt = f"""
    CRIE UMA ATIVIDADE DE {materia} ({objeto}) PARA {aluno.get('serie')}.
    
    ESTRUTURA DE SAÍDA:
    [RACIONAL PEDAGÓGICO]
    ---DIVISOR---
    [ATIVIDADE]
    
    REGRAS DE CRIAÇÃO:
    1. RIGOR BNCC: Questões adequadas à série.
    2. {get_hiperfoco_instruction(aluno)}
    3. IMAGENS (AUTOMÁTICO): A cada 4 ou 5 questões, escolha UMA que necessite de apoio visual (ex: mapa, gráfico, personagem fazendo ação).
       - Nessa questão, escreva a tag: [[GEN_IMG: descrição visual detalhada em inglês]].
       - Exemplo: "Questão 3: ... texto ... [[GEN_IMG: A pixel-art apple tree with 5 apples]]."
    4. QUANTIDADE: {qtd} questões ({tipo_q}).
    
    DADOS PEI: {aluno.get('ia_sugestao', '')[:1000]}
    """
    
    try:
        resp = client.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "user", "content": prompt}], temperature=temperatura)
        content = resp.choices[0].message.content
        if "---DIVISOR---" in content:
            parts = content.split("---DIVISOR---")
            return parts[0].strip(), parts[1].strip(), None
        return "Criação realizada.", content, None
    except Exception as e: return None, None, str(e)

def gerar_contextualizacao(api_key, aluno, assunto, tema_extra=""):
    client = OpenAI(api_key=api_key)
    tema = tema_extra if tema_extra else aluno.get('hiperfoco', 'Geral')
    prompt = f"Explique '{assunto}' para {aluno['nome']} usando a lógica de {tema}. PEI: {aluno.get('ia_sugestao','')[:500]}."
    try:
        resp = client.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "user", "content": prompt}], temperature=0.7)
        return resp.choices[0].message.content
    except Exception as e: return str(e)

# --- 6. INTERFACE ---
with st.sidebar:
    if 'OPENAI_API_KEY' in st.secrets: api_key = st.secrets['OPENAI_API_KEY']; st.success("✅ Conectado")
    else: api_key = st.text_input("Chave OpenAI:", type="password")
    st.markdown("---")
    if st.button("🗑️ Limpar Sessão"):
        for k in list(st.session_state.keys()):
            if k.startswith('res_') or k.startswith('imgs_') or k.startswith('adapt_'): del st.session_state[k]
        st.rerun()

st.markdown("""<div class="header-clean"><div style="font-size:3rem;">🧩</div><div><p style="margin:0;color:#004E92;font-size:1.5rem;font-weight:800;">Adaptador V8.2: Final Refined</p></div></div>""", unsafe_allow_html=True)

if not st.session_state.banco_estudantes:
    st.warning("⚠️ Cadastre um aluno no PEI 360º primeiro.")
    st.stop()

# CABEÇALHO ALUNO
lista = [a['nome'] for a in st.session_state.banco_estudantes]
nome_aluno = st.selectbox("📂 Selecione o Estudante:", lista)
aluno = next(a for a in st.session_state.banco_estudantes if a['nome'] == nome_aluno)

st.markdown(f"""
    <div class="student-header">
        <div class="student-info-item"><div class="student-label">Nome</div><div class="student-value">{aluno.get('nome')}</div></div>
        <div class="student-info-item"><div class="student-label">Idade</div><div class="student-value">{aluno.get('idade_calculada', '-')}</div></div>
        <div class="student-info-item"><div class="student-label">Série</div><div class="student-value">{aluno.get('serie', '-')}</div></div>
        <div class="student-info-item"><div class="student-label">Turma</div><div class="student-value">{aluno.get('turma', '-')}</div></div>
    </div>
""", unsafe_allow_html=True)

# ABAS
tab_adapt, tab_create, tab_visual, tab_ctx = st.tabs(["📂 Adaptar Arquivo", "✨ Criar Atividade", "🎨 Estúdio Visual", "💡 Contextualizador"])

# 1. ADAPTAR
with tab_adapt:
    c1, c2, c3 = st.columns(3)
    materia = c1.selectbox("Matéria", ["Matemática", "Português", "Ciências", "História", "Geografia"], key="m1")
    tema = c2.text_input("Tema", placeholder="Ex: Frações", key="t1")
    tipo_atv = c3.selectbox("Tipo", ["Prova", "Tarefa", "Atividade"], key="tp1")

    arquivo = st.file_uploader("Arquivo (FOTO ou DOCX)", type=["png","jpg","jpeg","docx"], key="f1")
    
    if 'adapt_imgs' not in st.session_state: st.session_state.adapt_imgs = []
    if 'adapt_txt' not in st.session_state: st.session_state.adapt_txt = None
    if 'adapt_type' not in st.session_state: st.session_state.adapt_type = None

    if arquivo:
        if arquivo.file_id != st.session_state.get('last_id_a'):
            st.session_state.last_id_a = arquivo.file_id
            st.session_state.adapt_imgs = []
            
            if "image" in arquivo.type:
                st.session_state.adapt_type = "imagem"
                st.markdown("<div class='crop-instruction'>✂️ <b>TESOURA DIGITAL:</b> Recorte a figura da questão.</div>", unsafe_allow_html=True)
                img = Image.open(arquivo).convert("RGB")
                buf = BytesIO(); img.save(buf, format="JPEG"); st.session_state.adapt_txt = buf.getvalue()
                img.thumbnail((1000, 1000))
                cropped = st_cropper(img, realtime_update=True, box_color='#FF0000', aspect_ratio=None)
                buf_c = BytesIO(); cropped.save(buf_c, format="JPEG")
                st.session_state.adapt_imgs = [buf_c.getvalue()]
            elif "word" in arquivo.type:
                st.session_state.adapt_type = "docx"
                txt, imgs = extrair_dados_docx(arquivo)
                st.session_state.adapt_txt = txt
                st.session_state.adapt_imgs = imgs
                st.success(f"DOCX: {len(imgs)} imagens encontradas.")

    adapt_map = {}
    questoes_ativas = []
    if st.session_state.adapt_imgs and st.session_state.adapt_type == "docx":
        st.subheader("🖼️ Mapear Imagens")
        cols = st.columns(3)
        for i, img in enumerate(st.session_state.adapt_imgs):
            with cols[i % 3]:
                st.image(img, width=100)
                q = st.number_input(f"Questão:", 0, 50, key=f"qa_{i}")
                if q > 0: adapt_map[q] = img; questoes_ativas.append(q)
    elif st.session_state.adapt_imgs and st.session_state.adapt_type == "imagem":
        adapt_map[0] = st.session_state.adapt_imgs[0]

    if st.button("🚀 ADAPTAR", type="primary"):
        st.session_state.fluxo = 'adaptar'
        with st.spinner("Processando..."):
            rac, txt, err = adaptar_conteudo(api_key, aluno, st.session_state.adapt_txt, st.session_state.adapt_type, materia, tema, tipo_atv, True, questoes_ativas)
            st.session_state['res_final'] = {'rac': rac, 'txt': txt, 'map': adapt_map}
            st.rerun()

# 2. CRIAR
with tab_create:
    c1, c2 = st.columns(2)
    mat_c = c1.selectbox("Componente", ["Matemática", "Português", "Ciências", "História", "Geografia"], key="cm")
    obj_c = c2.text_input("Objeto de Conhecimento", placeholder="Ex: Sistema Solar", key="co")
    c3, c4 = st.columns(2)
    qtd_c = c3.slider("Quantidade", 1, 10, 5, key="cq")
    tipo_c = c4.selectbox("Formato", ["Múltipla Escolha", "Discursiva", "Mista"], key="ct")
    
    if st.button("✨ CRIAR ATIVIDADE", type="primary"):
        st.session_state.fluxo = 'criar'
        with st.spinner("Criando questões e imagens..."):
            rac, txt, err = criar_do_zero(api_key, aluno, mat_c, obj_c, qtd_c, tipo_c)
            
            # Geração Automática de Imagens
            novo_mapa = {}; count = 0
            tags = re.findall(r'\[\[GEN_IMG: (.*?)\]\]', txt)
            for p in tags:
                count += 1
                url = gerar_dalle_prompt(api_key, p)
                if url:
                    io = baixar_imagem_url(url)
                    if io: novo_mapa[f"G{count}"] = io.getvalue()
            
            txt_final = txt
            for i in range(count): 
                txt_final = re.sub(r'\[\[GEN_IMG: .*?\]\]', f"[[IMG_G{i+1}]]", txt_final, count=1)
                
            st.session_state['res_final'] = {'rac': rac, 'txt': txt_final, 'map': novo_mapa}
            st.rerun()

# 3. VISUAL
with tab_visual:
    st.info("Estúdio Visual: Crie capas e recursos de apoio.")
    desc = st.text_area("Descrição:", placeholder="Ex: Rotina visual...", key="vd")
    if st.button("🎨 GERAR", type="primary"):
        with st.spinner("Desenhando..."):
            url = gerar_dalle_prompt(api_key, f"{desc} with {aluno.get('hiperfoco')} theme")
            if url: st.image(url)

# 4. CONTEXTO
with tab_ctx:
    st.info("Quebra-Gelo Pedagógico.")
    ass = st.text_input("Assunto:", key="cx")
    if st.button("💡 EXPLICAR", type="primary"):
        with st.spinner("Pensando..."):
            st.write(gerar_contextualizacao(api_key, aluno, ass))

# --- RESULTADOS UNIFICADOS ---
if 'res_final' in st.session_state:
    res = st.session_state['res_final']
    st.markdown("---")
    
    # Racional na Aba Expansível (Limpeza Visual)
    with st.expander("🧠 Racional Pedagógico (Por que adaptei assim?)", expanded=False):
        st.info(res['rac'])

    c_ed, c_vi = st.columns([1, 1])
    with c_ed:
        st.subheader("✏️ Editor")
        res['txt'] = st.text_area("Ajuste o texto se precisar:", value=res['txt'], height=600)
        
        if st.button("🔄 Refazer (Tentar Novamente)", type="secondary"):
            if st.session_state.get('fluxo') == 'criar':
                rac, txt, err = criar_do_zero(api_key, aluno, mat_c, obj_c, qtd_c, tipo_c, temperatura=0.9)
            else:
                rac, txt, err = adaptar_conteudo(api_key, aluno, st.session_state.get('adapt_txt'), st.session_state.get('adapt_type'), materia, tema, tipo_atv, True, questoes_ativas, temperatura=0.9)
            st.session_state['res_final']['rac'] = rac
            st.session_state['res_final']['txt'] = txt
            st.rerun()

    with c_view:
        st.subheader("👁️ Visualização")
        with st.container(border=True):
            partes = re.split(r'(\[\[IMG_[Q|G]\w+\]\])', res['txt'])
            for p in partes:
                tag = re.match(r'\[\[IMG_(Q|G)(\w+)\]\]', p)
                if tag:
                    t, i = tag.groups()
                    im = None
                    if t=="Q": im = res['map'].get(int(i), res['map'].get(0))
                    elif t=="G": im = res['map'].get(f"G{i}")
                    
                    if im: st.image(im, width=300)
                    else: st.warning(f"[Imagem {t}{i} não encontrada]")
                elif p.strip(): st.markdown(p.strip())

    docx = construir_docx_final(res['txt'], aluno, materia, res['map'], None, "Atividade")
    st.download_button("📥 BAIXAR DOCX", docx, "Atividade_Inclusiva.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document", type="primary", use_container_width=True)
