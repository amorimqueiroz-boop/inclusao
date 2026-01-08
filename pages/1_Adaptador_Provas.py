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
st.set_page_config(page_title="Adaptador 360º | V7.2", page_icon="🧩", layout="wide")

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
    .action-bar { background: #F7FAFC; padding: 20px; border-radius: 16px; border: 1px solid #E2E8F0; margin: 20px 0; }
    .crop-instruction { background: #EBF8FF; border-left: 4px solid #3182CE; padding: 15px; color: #2C5282; border-radius: 4px; margin-bottom: 10px; }
    .racional-box { background-color: #F0FFF4; border-left: 4px solid #48BB78; padding: 15px; border-radius: 4px; margin-bottom: 20px; color: #2F855A; font-size: 0.95rem; }
    
    /* Abas Superiores */
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] { border-radius: 4px; padding: 10px 20px; background-color: white; border: 1px solid #E2E8F0; }
    .stTabs [aria-selected="true"] { background-color: #3182CE !important; color: white !important; }

    div[data-testid="column"] .stButton button[kind="primary"] { border-radius: 12px !important; height: 50px; width: 100%; background-color: #FF6B6B !important; color: white !important; font-weight: 800 !important; }
    div[data-testid="column"] .stButton button[kind="secondary"] { border-radius: 12px !important; height: 50px; width: 100%; background-color: white !important; color: #718096 !important; border: 2px solid #CBD5E0 !important; }
    </style>
""", unsafe_allow_html=True)

# --- 4. FUNÇÕES DE ARQUIVO ---
def extrair_dados_docx(uploaded_file):
    """Extrai texto e imagens na ordem visual (XML), com filtro leve."""
    uploaded_file.seek(0)
    imagens = []
    texto = ""
    try:
        doc = Document(uploaded_file)
        texto = "\n".join([p.text for p in doc.paragraphs if p.text.strip() != ""])
        
        # Varre XML para pegar imagens na ordem correta
        for rel in doc.part.rels.values():
            if "image" in rel.target_ref:
                img_data = rel.target_part.blob
                # Filtro reduzido para 1KB (pega quase tudo, evita sumir imagens pequenas)
                if len(img_data) > 1024: 
                    imagens.append(img_data)
    except Exception as e:
        st.error(f"Erro leitura DOCX: {e}")
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
    
    # Processa tags de imagem [[IMG_Qx]]
    partes = re.split(r'(\[\[IMG_Q\d+\]\])', texto_ia)
    
    for parte in partes:
        tag_match = re.match(r'\[\[IMG_Q(\d+)\]\]', parte)
        
        if tag_match:
            num_q = int(tag_match.group(1))
            # Se for modo CROP (lista com 1 item), usa índice 0 para a imagem única
            if len(mapa_imgs) == 1 and 0 in mapa_imgs:
                 try:
                    doc.add_picture(BytesIO(mapa_imgs[0]), width=Inches(5.0))
                    doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
                    doc.add_paragraph("")
                 except: pass
            
            # Se for modo DOCX (mapa real), usa o número da questão
            elif num_q in mapa_imgs:
                try:
                    doc.add_picture(BytesIO(mapa_imgs[num_q]), width=Inches(5.0))
                    doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
                    doc.add_paragraph("") 
                except: pass
        elif parte.strip():
            clean = parte.replace("Utilize a tag", "").strip()
            if clean: doc.add_paragraph(clean)
            
    buffer = BytesIO(); doc.save(buffer); buffer.seek(0)
    return buffer

# --- 5. IA (ADAPTAÇÃO E CRIAÇÃO) ---
def gerar_dalle(api_key, tema, aluno):
    client = OpenAI(api_key=api_key)
    prompt = f"Educational illustration about '{tema}'. Simple, clear, white background. {aluno.get('hiperfoco','')} style. No text."
    try:
        resp = client.images.generate(model="dall-e-3", prompt=prompt, size="1024x1024", quality="standard", n=1)
        return resp.data[0].url, None
    except Exception as e: return None, str(e)

# MÓDULO 1: ADAPTAR EXISTENTE
def adaptar_conteudo(api_key, aluno, conteudo, tipo, materia, tema, tipo_atv, remover_resp, questoes_mapeadas):
    client = OpenAI(api_key=api_key)
    
    # Instrução de Imagem (Separada por Tipo)
    if tipo == "docx":
        lista_q = ", ".join([str(n) for n in questoes_mapeadas])
        instrucao_imgs = f"""
        DIAGRAMAÇÃO OBRIGATÓRIA (DOCX):
        Existem imagens para as questões: {lista_q}.
        Se a Questão X tiver imagem, insira a tag [[IMG_QX]] LOGO APÓS o enunciado, antes das alternativas.
        Exemplo: "Questão 5: ... (texto) ... [[IMG_Q5]] ... a) ..."
        """
    else:
        instrucao_imgs = "Use a tag [[IMG_Q1]] para inserir a imagem recortada logo após o enunciado principal."

    instrucao_prof = "REMOVA TODAS AS RESPOSTAS (azul/rosa)." if remover_resp else ""
    hiperfoco = f"Adapte usando o HIPERFOCO: {aluno.get('hiperfoco', 'livre')}."
    pei_contexto = f"DIRETRIZES PEI:\n{aluno.get('ia_sugestao', '')[:1500]}"

    prompt = f"""
    Especialista em DUA. [RACIONAL PEDAGÓGICO curto + ---DIVISOR---].
    {instrucao_prof} {instrucao_imgs} {hiperfoco} {pei_contexto}
    CONTEXTO: {materia} | {tema} | {tipo_atv}
    CONTEÚDO:
    """
    
    msgs = [{"role": "user", "content": []}]
    if tipo == "imagem":
        b64 = base64.b64encode(conteudo).decode('utf-8')
        msgs[0]["content"].append({"type": "text", "text": prompt})
        msgs[0]["content"].append({"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}})
    else:
        msgs[0]["content"].append({"type": "text", "text": prompt + "\n" + str(conteudo)})

    try:
        resp = client.chat.completions.create(model="gpt-4o-mini", messages=msgs, temperature=0.4, max_tokens=4000)
        parts = resp.choices[0].message.content.split("---DIVISOR---")
        return (parts[0].strip(), parts[1].strip(), None) if len(parts)>1 else ("Adaptado.", resp.choices[0].message.content, None)
    except Exception as e: return None, None, str(e)

# MÓDULO 2: CRIAR DO ZERO (NOVO!)
def criar_do_zero(api_key, aluno, materia, objeto, qtd, tipo_q):
    client = OpenAI(api_key=api_key)
    
    prompt = f"""
    CRIE UMA ATIVIDADE DO ZERO PARA ESTE ALUNO:
    Aluno: {aluno['nome']} | Diagnóstico: {aluno.get('diagnostico')}
    Hiperfoco: {aluno.get('hiperfoco', 'Geral')} (USE ISSO PARA CONTEXTUALIZAR TUDO!)
    
    CONFIGURAÇÃO:
    - Componente: {materia}
    - Objeto de Conhecimento: {objeto}
    - Quantidade: {qtd} questões
    - Tipo: {tipo_q}
    
    DIRETRIZES:
    1. Inicie com um [RACIONAL PEDAGÓGICO] curto explicando como o hiperfoco foi usado.
    2. Use ---DIVISOR---.
    3. Crie as questões. Se usar o hiperfoco (ex: Minecraft), use nomes, itens e lógicas desse universo.
    4. Linguagem acessível e direta.
    """
    
    try:
        resp = client.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "user", "content": prompt}], temperature=0.7)
        parts = resp.choices[0].message.content.split("---DIVISOR---")
        return (parts[0].strip(), parts[1].strip(), None) if len(parts)>1 else ("Criado.", resp.choices[0].message.content, None)
    except Exception as e: return None, None, str(e)

# --- 6. INTERFACE ---
with st.sidebar:
    if 'OPENAI_API_KEY' in st.secrets: api_key = st.secrets['OPENAI_API_KEY']; st.success("✅ Conectado")
    else: api_key = st.text_input("Chave OpenAI:", type="password")
    st.markdown("---")
    if st.button("🗑️ Limpar Tudo"):
        for k in list(st.session_state.keys()):
            if k.startswith('res_') or k.startswith('imgs_'): del st.session_state[k]
        st.rerun()

st.markdown("""<div class="header-clean"><div style="font-size:3rem;">🧩</div><div><p style="margin:0;color:#004E92;font-size:1.5rem;font-weight:800;">Adaptador V7.2: Criação & Adaptação</p></div></div>""", unsafe_allow_html=True)

if not st.session_state.banco_estudantes:
    st.warning("⚠️ Cadastre um aluno no PEI 360º primeiro.")
    st.stop()

# SELETOR DE ALUNO
lista = [a['nome'] for a in st.session_state.banco_estudantes]
nome_aluno = st.selectbox("📂 Estudante:", lista)
aluno = next(a for a in st.session_state.banco_estudantes if a['nome'] == nome_aluno)

# --- ABAS PRINCIPAIS ---
tab_adapt, tab_criar = st.tabs(["📂 Adaptar Arquivo Existente", "✨ Criar do Zero"])

# ABA 1: ADAPTAR
with tab_adapt:
    c1, c2, c3 = st.columns(3)
    materia = c1.selectbox("Matéria", ["Matemática", "Português", "Ciências", "História", "Geografia"], key="m1")
    tema = c2.text_input("Tema Original", placeholder="Ex: Frações", key="t1")
    tipo_atv = c3.selectbox("Tipo", ["Prova", "Tarefa", "Atividade"], key="tp1")

    arquivo = st.file_uploader("Arquivo (FOTO ou DOCX)", type=["png","jpg","jpeg","docx"])
    
    # Estado Local
    if 'imgs_extraidas' not in st.session_state: st.session_state.imgs_extraidas = []
    if 'tipo_arq' not in st.session_state: st.session_state.tipo_arq = None
    if 'txt_orig' not in st.session_state: st.session_state.txt_orig = None

    if arquivo:
        if arquivo.file_id != st.session_state.get('last_id'):
            st.session_state.last_id = arquivo.file_id
            st.session_state.imgs_extraidas = []
            
            if "image" in arquivo.type:
                st.session_state.tipo_arq = "imagem"
                st.markdown("<div class='crop-instruction'>✂️ <b>TESOURA DIGITAL:</b> Recorte a figura. O texto será lido da imagem completa.</div>", unsafe_allow_html=True)
                img = Image.open(arquivo).convert("RGB")
                buf = BytesIO(); img.save(buf, format="JPEG"); st.session_state.txt_orig = buf.getvalue()
                
                img.thumbnail((1000, 1000))
                cropped = st_cropper(img, realtime_update=True, box_color='#FF0000', aspect_ratio=None)
                buf_c = BytesIO(); cropped.save(buf_c, format="JPEG")
                st.session_state.imgs_extraidas = [buf_c.getvalue()]
            
            elif "word" in arquivo.type:
                st.session_state.tipo_arq = "docx"
                txt, imgs = extrair_dados_docx(arquivo)
                st.session_state.txt_orig = txt
                st.session_state.imgs_extraidas = imgs
                st.success(f"DOCX: {len(imgs)} imagens encontradas.")

    # Mapeamento Condicional (SÓ PARA DOCX)
    mapa_imgs = {}
    questoes_ativas = []
    
    if st.session_state.imgs_extraidas and st.session_state.tipo_arq == "docx":
        st.subheader("🖼️ Mapear Imagens (DOCX)")
        cols = st.columns(3)
        for i, img in enumerate(st.session_state.imgs_extraidas):
            with cols[i % 3]:
                st.image(img, width=100)
                q = st.number_input(f"Questão:", 0, 50, key=f"q_{i}")
                if q > 0:
                    mapa_imgs[q] = img
                    questoes_ativas.append(q)
    
    # Se for IMAGEM, o mapa é simples (índice 0)
    elif st.session_state.imgs_extraidas and st.session_state.tipo_arq == "imagem":
        mapa_imgs[0] = st.session_state.imgs_extraidas[0] # Chave 0 para imagem única

    # Botões Adaptar
    c_opt, c_act = st.columns([1, 1])
    with c_opt:
        modo_prof = st.checkbox("Remover Respostas", value=True) if st.session_state.tipo_arq == "imagem" else False
        usar_dalle = st.toggle("Capa IA", value=True, key="d1")
    
    with c_act:
        if st.button("🚀 GERAR ADAPTAÇÃO", type="primary"):
            if not materia or not tema: st.warning("Preencha os dados.")
            else:
                with st.spinner("Processando..."):
                    rac, txt, err = adaptar_conteudo(
                        api_key, aluno, st.session_state.txt_orig, st.session_state.tipo_arq,
                        materia, tema, tipo_atv, modo_prof, questoes_ativas
                    )
                    img_d = gerar_dalle(api_key, tema, aluno)[0] if usar_dalle else None
                    
                    st.session_state['res_racional'] = rac
                    st.session_state['res_texto'] = txt
                    st.session_state['res_mapa'] = mapa_imgs
                    st.session_state['res_dalle'] = img_d
                    st.rerun()

# ABA 2: CRIAR DO ZERO
with tab_criar:
    st.info(f"O sistema usará o hiperfoco **{aluno.get('hiperfoco', 'Geral')}** para criar questões engajadoras.")
    
    cc1, cc2 = st.columns(2)
    mat_c = cc1.selectbox("Componente Curricular", ["Matemática", "Língua Portuguesa", "Ciências", "História", "Geografia"], key="mc")
    obj_c = cc2.text_input("Objeto de Conhecimento (Conteúdo)", placeholder="Ex: Sistema Solar", key="oc")
    
    cc3, cc4 = st.columns(2)
    qtd_c = cc3.slider("Quantidade de Questões", 1, 10, 5)
    tipo_c = cc4.selectbox("Formato", ["Múltipla Escolha", "Discursiva", "Mista (Objetiva + Aberta)"])
    
    if st.button("✨ CRIAR PROVA DO ZERO", type="primary"):
        if not obj_c: st.warning("Informe o conteúdo.")
        else:
            with st.spinner(f"Criando questões sobre {obj_c} com tema {aluno.get('hiperfoco')}..."):
                rac, txt, err = criar_do_zero(api_key, aluno, mat_c, obj_c, qtd_c, tipo_c)
                img_d = gerar_dalle(api_key, obj_c, aluno)[0]
                
                st.session_state['res_racional'] = rac
                st.session_state['res_texto'] = txt
                st.session_state['res_mapa'] = {} # Sem imagens anexas na criação
                st.session_state['res_dalle'] = img_d
                st.rerun()

# --- RESULTADOS GERAIS ---
if 'res_texto' in st.session_state:
    st.markdown("---")
    if st.session_state.get('res_racional'):
        st.markdown(f"<div class='racional-box'><b>🧠 Racional Pedagógico:</b><br>{st.session_state['res_racional']}</div>", unsafe_allow_html=True)

    with st.container(border=True):
        if st.session_state.get('res_dalle'): st.image(st.session_state['res_dalle'], width=200, caption="Capa Sensorial")
        
        txt = st.session_state['res_texto']
        partes = re.split(r'(\[\[IMG_Q\d+\]\])', txt)
        mapa = st.session_state.get('res_mapa', {})
        
        for parte in partes:
            tag = re.match(r'\[\[IMG_Q(\d+)\]\]', parte)
            if tag:
                q = int(tag.group(1))
                # Tenta achar no mapa (para DOCX) ou usa a única imagem (para CROP)
                img_show = mapa.get(q) if q in mapa else (mapa.get(0) if 0 in mapa else None)
                
                if img_show: st.image(img_show, width=300)
            else:
                clean = parte.replace("Utilize a tag", "").strip()
                if clean: st.markdown(clean)

    docx = construir_docx_final(
        st.session_state['res_texto'], aluno, 
        st.session_state.get('tipo_atv', 'Atividade'), 
        st.session_state.get('res_mapa', {}), 
        st.session_state.get('res_dalle'), 
        'Atividade'
    )
    st.download_button("📥 BAIXAR DOCX", docx, f"Atividade_{aluno['nome']}.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document", type="primary", use_container_width=True)
