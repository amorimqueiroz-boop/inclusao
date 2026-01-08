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
st.set_page_config(page_title="Adaptador 360º | V8.0 Hub", page_icon="🧩", layout="wide")

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
    
    /* Abas */
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] { border-radius: 6px; padding: 12px 24px; background-color: white; border: 1px solid #E2E8F0; font-weight: 600; }
    .stTabs [aria-selected="true"] { background-color: #3182CE !important; color: white !important; border-color: #3182CE !important; }

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
    partes = re.split(r'(\[\[IMG_[Q|G]\w+\]\])', texto_ia)
    for parte in partes:
        tag_match = re.match(r'\[\[IMG_(Q|G)(\w+)\]\]', parte)
        if tag_match:
            tipo, id_img = tag_match.groups()
            img_bytes = None
            if tipo == "Q": # Original
                try:
                    num = int(id_img)
                    img_bytes = mapa_imgs.get(num, mapa_imgs.get(0))
                except: pass
            elif tipo == "G": # Gerada
                img_bytes = mapa_imgs.get(f"G{id_img}")

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

# --- 5. INTELIGÊNCIA ARTIFICIAL (TODOS OS MÓDULOS) ---

# GERAÇÃO DE IMAGEM (DALL-E)
def gerar_dalle_prompt(api_key, prompt_text):
    client = OpenAI(api_key=api_key)
    try:
        resp = client.images.generate(model="dall-e-3", prompt=prompt_text + " Educational style, clear, autism-friendly, white background, no text.", size="1024x1024", quality="standard", n=1)
        return resp.data[0].url
    except: return None

# INSTRUÇÃO DE HIPERFOCO (REGRA 30%)
def get_hiperfoco_instruction(aluno):
    return f"""
    REGRA DOS 30% (Hiperfoco: {aluno.get('hiperfoco', 'Geral')}):
    - Use o tema do hiperfoco em APENAS 30% das questões.
    - O restante deve ser neutro/cotidiano.
    - O objetivo é engajar sem saturar.
    """

# MÓDULO 1: ADAPTAR
def adaptar_conteudo(api_key, aluno, conteudo, tipo, materia, tema, tipo_atv, remover_resp, questoes_mapeadas, temperatura=0.4):
    client = OpenAI(api_key=api_key)
    if tipo == "docx":
        lista_q = ", ".join([str(n) for n in questoes_mapeadas])
        instrucao_imgs = f"DOCX: Existem imagens para as questões {lista_q}. Insira [[IMG_QX]] LOGO APÓS o enunciado da questão X."
    else:
        instrucao_imgs = "FOTO: Use [[IMG_Q1]] para a imagem recortada logo após o enunciado."

    prompt = f"""
    Especialista em BNCC. [RACIONAL PEDAGÓGICO curto + ---DIVISOR---].
    {"REMOVA TODAS AS RESPOSTAS." if remover_resp else ""} {instrucao_imgs} 
    {get_hiperfoco_instruction(aluno)}
    PEI: {aluno.get('ia_sugestao', '')[:1500]}
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
        resp = client.chat.completions.create(model="gpt-4o-mini", messages=msgs, temperature=temperatura, max_tokens=4000)
        parts = resp.choices[0].message.content.split("---DIVISOR---")
        return (parts[0].strip(), parts[1].strip(), None) if len(parts)>1 else ("Adaptado.", resp.choices[0].message.content, None)
    except Exception as e: return None, None, str(e)

# MÓDULO 2: CRIAR
def criar_do_zero(api_key, aluno, materia, objeto, qtd, tipo_q, temperatura=0.7):
    client = OpenAI(api_key=api_key)
    prompt = f"""
    CRIE UMA ATIVIDADE DE {materia} ({objeto}) PARA {aluno.get('serie')}.
    PEI: {aluno.get('ia_sugestao', '')[:1500]}
    {get_hiperfoco_instruction(aluno)}
    
    REGRAS:
    1. RIGOR BNCC. Use hiperfoco apenas como contexto.
    2. A cada 5 questões, 1 deve ter imagem gerada: [[GEN_IMG: descrição]].
    3. QUANTIDADE: {qtd} questões ({tipo_q}).
    
    SAÍDA: [RACIONAL] ---DIVISOR--- [ATIVIDADE]
    """
    try:
        resp = client.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "user", "content": prompt}], temperature=temperatura)
        parts = resp.choices[0].message.content.split("---DIVISOR---")
        return (parts[0].strip(), parts[1].strip(), None) if len(parts)>1 else ("Criado.", resp.choices[0].message.content, None)
    except Exception as e: return None, None, str(e)

# MÓDULO 4: CONTEXTUALIZAR
def gerar_contextualizacao(api_key, aluno, assunto, tema_extra=""):
    client = OpenAI(api_key=api_key)
    tema_foco = tema_extra if tema_extra else aluno.get('hiperfoco', 'Interesses Gerais')
    
    prompt = f"""
    Você é um Consultor Pedagógico de Inclusão.
    O professor precisa explicar "{assunto}" para o aluno {aluno['nome']}.
    O Hiperfoco/Interesse do aluno é: {tema_foco}.
    
    GERE UM GUIA CURTO COM:
    1. **Analogia Principal:** Como explicar {assunto} usando a lógica de {tema_foco}?
    2. **Quebra-Gelo:** Uma pergunta ou curiosidade para iniciar a conversa e captar a atenção.
    3. **Dica Sensorial/Comportamental:** Baseada no PEI abaixo.
    
    PEI: {aluno.get('ia_sugestao', '')[:1000]}
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
    if st.button("🗑️ Limpar Tudo"):
        for k in list(st.session_state.keys()):
            if k.startswith('res_') or k.startswith('imgs_'): del st.session_state[k]
        st.rerun()

st.markdown("""<div class="header-clean"><div style="font-size:3rem;">🧩</div><div><p style="margin:0;color:#004E92;font-size:1.5rem;font-weight:800;">Adaptador V8.0: Hub de Inclusão</p></div></div>""", unsafe_allow_html=True)

if not st.session_state.banco_estudantes:
    st.warning("⚠️ Cadastre um aluno no PEI 360º primeiro.")
    st.stop()

lista = [a['nome'] for a in st.session_state.banco_estudantes]
nome_aluno = st.selectbox("📂 Estudante:", lista)
aluno = next(a for a in st.session_state.banco_estudantes if a['nome'] == nome_aluno)

# --- ABAS DO HUB ---
tab1, tab2, tab3, tab4 = st.tabs(["📂 Adaptar Atividade", "✨ Criar Atividade", "🎨 Estúdio Visual", "💡 Contextualizador"])

# 1. ADAPTAR
with tab1:
    c1, c2, c3 = st.columns(3)
    materia = c1.selectbox("Matéria", ["Matemática", "Português", "Ciências", "História", "Geografia"], key="m1")
    tema = c2.text_input("Tema Original", placeholder="Ex: Frações", key="t1")
    tipo_atv = c3.selectbox("Tipo", ["Prova", "Tarefa", "Atividade"], key="tp1")

    arquivo = st.file_uploader("Arquivo (FOTO ou DOCX)", type=["png","jpg","jpeg","docx"])
    
    if 'imgs_extraidas' not in st.session_state: st.session_state.imgs_extraidas = []
    if 'tipo_arq' not in st.session_state: st.session_state.tipo_arq = None
    if 'txt_orig' not in st.session_state: st.session_state.txt_orig = None

    if arquivo:
        if arquivo.file_id != st.session_state.get('last_id'):
            st.session_state.last_id = arquivo.file_id
            st.session_state.imgs_extraidas = []
            
            if "image" in arquivo.type:
                st.session_state.tipo_arq = "imagem"
                st.markdown("<div class='crop-instruction'>✂️ <b>TESOURA DIGITAL:</b> Recorte a figura.</div>", unsafe_allow_html=True)
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
                st.success(f"DOCX: {len(imgs)} imagens.")

    mapa_imgs = {}
    questoes_ativas = []
    if st.session_state.imgs_extraidas and st.session_state.tipo_arq == "docx":
        st.subheader("🖼️ Mapear Imagens")
        cols = st.columns(3)
        for i, img in enumerate(st.session_state.imgs_extraidas):
            with cols[i % 3]:
                st.image(img, width=100)
                q = st.number_input(f"Questão:", 0, 50, key=f"q_{i}")
                if q > 0: mapa_imgs[q] = img; questoes_ativas.append(q)
    elif st.session_state.imgs_extraidas and st.session_state.tipo_arq == "imagem":
        mapa_imgs[0] = st.session_state.imgs_extraidas[0]

    c_opt, c_act = st.columns([1, 1])
    with c_opt:
        modo_prof = st.checkbox("Remover Respostas", value=True) if st.session_state.tipo_arq == "imagem" else False
        usar_dalle = st.toggle("Capa IA", value=True, key="d1")
    
    with c_act:
        if st.button("🚀 ADAPTAR AGORA", type="primary"):
            st.session_state.fluxo_atual = 'adaptar'
            with st.spinner("Adaptando..."):
                rac, txt, err = adaptar_conteudo(api_key, aluno, st.session_state.txt_orig, st.session_state.tipo_arq, materia, tema, tipo_atv, modo_prof, questoes_ativas)
                img_d = gerar_dalle_prompt(api_key, f"{tema} in {aluno.get('hiperfoco')} style") if usar_dalle else None
                st.session_state['res_racional'] = rac; st.session_state['res_texto'] = txt; st.session_state['res_mapa'] = mapa_imgs; st.session_state['res_dalle'] = img_d
                st.rerun()

# 2. CRIAR
with tab2:
    cc1, cc2 = st.columns(2)
    mat_c = cc1.selectbox("Componente", ["Matemática", "Português", "Ciências", "História", "Geografia"], key="mc")
    obj_c = cc2.text_input("Objeto de Conhecimento", placeholder="Ex: Sistema Solar", key="oc")
    cc3, cc4 = st.columns(2)
    qtd_c = cc3.slider("Quantidade", 1, 10, 5)
    tipo_c = cc4.selectbox("Formato", ["Múltipla Escolha", "Discursiva", "Mista"])
    
    if st.button("✨ CRIAR ATIVIDADE", type="primary"):
        st.session_state.fluxo_atual = 'criar'
        with st.spinner(f"Criando..."):
            rac, txt, err = criar_do_zero(api_key, aluno, mat_c, obj_c, qtd_c, tipo_c)
            novo_mapa = {}; count_imgs = 0
            tags_geracao = re.findall(r'\[\[GEN_IMG: (.*?)\]\]', txt)
            for prompt_img in tags_geracao:
                count_imgs += 1
                url_img = gerar_dalle_prompt(api_key, prompt_img)
                if url_img:
                    img_io = baixar_imagem_url(url_img)
                    if img_io: novo_mapa[f"G{count_imgs}"] = img_io.getvalue()
            
            txt_final = txt
            for i in range(count_imgs): txt_final = re.sub(r'\[\[GEN_IMG: .*?\]\]', f"[[IMG_G{i+1}]]", txt_final, count=1)
            st.session_state['res_racional'] = rac; st.session_state['res_texto'] = txt_final; st.session_state['res_mapa'] = novo_mapa; st.session_state['res_dalle'] = None
            st.rerun()

# 3. ESTÚDIO VISUAL
with tab3:
    st.info("Crie recursos visuais específicos (capas, pranchas, rotinas) usando o hiperfoco.")
    desc_visual = st.text_area("Descreva o que você precisa:", placeholder=f"Ex: Uma rotina matinal com personagens de {aluno.get('hiperfoco')}")
    if st.button("🎨 GERAR IMAGEM SENSORIAL", type="primary"):
        with st.spinner("Desenhando..."):
            url = gerar_dalle_prompt(api_key, f"{desc_visual}. {aluno.get('hiperfoco')} style.")
            if url: st.image(url, caption="Imagem Gerada")
            else: st.error("Erro ao gerar.")

# 4. CONTEXTUALIZADOR
with tab4:
    st.info("Ferramenta para 'Quebra-Gelo' e Explicação.")
    c_assunto, c_tema = st.columns(2)
    assunto_ctx = c_assunto.text_input("Assunto da Aula:", placeholder="Ex: Fotossíntese")
    tema_ctx = c_tema.text_input("Tema de Conexão:", value=aluno.get('hiperfoco', ''), placeholder="Deixe vazio para usar o Hiperfoco")
    
    if st.button("💡 GERAR EXPLICAÇÃO", type="primary"):
        with st.spinner("Criando ponte pedagógica..."):
            res_ctx = gerar_contextualizacao(api_key, aluno, assunto_ctx, tema_ctx)
            st.markdown(f"<div style='background:white; padding:20px; border-radius:10px; border:1px solid #ddd;'>{res_ctx}</div>", unsafe_allow_html=True)

# --- RESULTADOS COM VALIDAÇÃO ---
if 'res_texto' in st.session_state:
    st.markdown("---")
    if st.session_state.get('res_racional'):
        st.markdown(f"<div class='racional-box'><b>🧠 Resumo:</b><br>{st.session_state['res_racional']}</div>", unsafe_allow_html=True)

    c_edit, c_view = st.columns([1, 1])
    with c_edit:
        st.subheader("✏️ Validar Texto")
        texto_validado = st.text_area("Editor:", value=st.session_state['res_texto'], height=600)
        st.session_state['res_texto'] = texto_validado
        if st.button("🔄 Refazer (Não gostei)"):
            if st.session_state.get('fluxo_atual') == 'criar':
                rac, txt, err = criar_do_zero(api_key, aluno, mat_c, obj_c, qtd_c, tipo_c, temperatura=0.9)
            else:
                rac, txt, err = adaptar_conteudo(api_key, aluno, st.session_state.get('txt_orig'), st.session_state.get('tipo_arq'), materia, tema, tipo_atv, modo_prof, questoes_ativas, temperatura=0.9)
            st.session_state['res_racional'] = rac; st.session_state['res_texto'] = txt; st.rerun()

    with c_view:
        st.subheader("👁️ Visualização")
        with st.container(border=True):
            if st.session_state.get('res_dalle'): st.image(st.session_state['res_dalle'], width=200)
            partes = re.split(r'(\[\[IMG_[Q|G]\w+\]\])', texto_validado)
            mapa = st.session_state.get('res_mapa', {})
            for parte in partes:
                tag = re.match(r'\[\[IMG_(Q|G)(\w+)\]\]', parte)
                if tag:
                    tipo, id_i = tag.groups()
                    img_show = None
                    if tipo == "Q": 
                        num = int(id_i); img_show = mapa.get(num, mapa.get(0))
                    elif tipo == "G": img_show = mapa.get(f"G{id_i}")
                    if img_show: st.image(img_show, width=300)
                else:
                    if parte.strip(): st.markdown(parte.strip())

    docx = construir_docx_final(st.session_state['res_texto'], aluno, st.session_state.get('tipo_atv', 'Atividade'), st.session_state.get('res_mapa', {}), st.session_state.get('res_dalle'), 'Atividade')
    st.download_button("📥 BAIXAR DOCX", docx, f"Atividade_{aluno['nome']}.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document", type="primary", use_container_width=True)
