import streamlit as st
from openai import OpenAI
from io import BytesIO
from docx import Document
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from pypdf import PdfReader
from fpdf import FPDF
import base64
import os
import re
import requests
import zipfile

# --- 1. CONFIGURAÇÃO ---
st.set_page_config(page_title="Adaptador V4.6", page_icon="🧩", layout="wide")

if 'banco_estudantes' not in st.session_state:
    st.session_state.banco_estudantes = []

# --- 2. ESTILO VISUAL (CLEAN) ---
st.markdown("""
    <style>
    html, body, [class*="css"] { font-family: 'Nunito', sans-serif; color: #2D3748; }
    
    /* Cabeçalho */
    .header-clean {
        background-color: white; padding: 20px 30px; border-radius: 12px;
        border: 1px solid #E2E8F0; box-shadow: 0 2px 5px rgba(0,0,0,0.02);
        margin-bottom: 20px; display: flex; align-items: center; gap: 20px;
    }
    
    /* Editor de Texto */
    .stTextArea textarea {
        font-family: 'Consolas', 'Courier New', monospace !important;
        font-size: 14px !important;
        line-height: 1.6 !important;
        border: 2px solid #CBD5E0 !important;
        border-radius: 10px !important;
    }
    
    /* Área de Preview (Simulando Papel) */
    .preview-paper {
        background-color: white;
        padding: 30px;
        border: 1px solid #E2E8F0;
        border-radius: 4px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        min-height: 600px;
    }
    
    .img-placeholder {
        background-color: #EDF2F7; border: 2px dashed #A0AEC0; 
        color: #4A5568; padding: 20px; text-align: center; border-radius: 8px; margin: 10px 0;
    }

    div[data-testid="column"] .stButton button {
        border-radius: 10px !important; font-weight: 700 !important; height: 45px !important; width: 100%;
    }
    </style>
""", unsafe_allow_html=True)

# --- 3. FUNÇÕES DE ARQUIVO ---
def extrair_dados_docx(uploaded_file):
    uploaded_file.seek(0)
    texto = ""
    imagens = []
    try:
        doc = Document(uploaded_file)
        texto = "\n".join([p.text for p in doc.paragraphs if p.text.strip() != ""])
        
        uploaded_file.seek(0)
        with zipfile.ZipFile(uploaded_file) as z:
            all_files = z.namelist()
            # Filtra e ordena imagens
            media_files = [f for f in all_files if f.startswith('word/media/') and f.endswith(('.png', '.jpg', '.jpeg'))]
            media_files.sort(key=lambda f: int(re.search(r'\d+', f).group()) if re.search(r'\d+', f) else 0)
            
            for media in media_files:
                imagens.append(z.read(media))
    except: pass
    return texto, imagens

def ler_arquivo_generico(uploaded_file):
    if uploaded_file is None: return None, None, [], None
    texto, imgs, img_unica, tipo = "", [], None, "indefinido"
    
    try:
        if uploaded_file.type == "application/pdf":
            reader = PdfReader(uploaded_file)
            for page in reader.pages: texto += page.extract_text() + "\n"
            tipo = "pdf"
        elif "word" in uploaded_file.type:
            texto, imgs = extrair_dados_docx(uploaded_file)
            tipo = "docx"
        elif "image" in uploaded_file.type:
            img_unica = uploaded_file.getvalue()
            texto = base64.b64encode(img_unica).decode('utf-8')
            tipo = "imagem"
    except: pass
    return texto, tipo, imgs, img_unica

def baixar_imagem_url(url):
    try:
        resp = requests.get(url)
        if resp.status_code == 200: return BytesIO(resp.content)
    except: pass
    return None

# --- 4. CONSTRUTOR DE DOCX ---
def construir_docx_final(texto_editado, aluno, materia, lista_imgs, img_dalle_url, img_unica):
    doc = Document()
    style = doc.styles['Normal']; style.font.name = 'Arial'; style.font.size = Pt(12)
    
    # Cabeçalho
    head = doc.add_heading(f'ATIVIDADE ADAPTADA - {materia.upper()}', 0)
    head.alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_paragraph(f"Estudante: {aluno}")
    doc.add_paragraph("_"*50)

    # 1. Apoio Visual (DALL-E)
    if img_dalle_url:
        img_io = baixar_imagem_url(img_dalle_url)
        if img_io:
            try:
                doc.add_picture(img_io, width=Inches(4.0))
                doc.add_paragraph("")
            except: pass

    # 2. Montagem Inteligente
    # Divide o texto pelas tags [[IMG_X]]
    partes = re.split(r'(\[\[IMG_\d+\]\]|\[\[IMG_ORIGINAL\]\])', texto_editado)
    
    for parte in partes:
        tag_match = re.match(r'\[\[IMG_(\d+)\]\]', parte)
        
        # Inserção da Imagem do Word
        if tag_match:
            try:
                idx = int(tag_match.group(1)) - 1
                if 0 <= idx < len(lista_imgs):
                    doc.add_picture(BytesIO(lista_imgs[idx]), width=Inches(4.5))
                    doc.add_paragraph("")
            except: pass
            
        # Inserção da Imagem Única (Upload de Foto)
        elif parte == "[[IMG_ORIGINAL]]" and img_unica:
            try:
                doc.add_picture(BytesIO(img_unica), width=Inches(5.0))
                doc.add_paragraph("")
            except: pass
            
        # Texto
        else:
            if parte.strip():
                doc.add_paragraph(parte.strip())

    buffer = BytesIO(); doc.save(buffer); buffer.seek(0)
    return buffer

# --- 5. INTELIGÊNCIA ---
def gerar_dalle(api_key, tema, aluno_dados):
    client = OpenAI(api_key=api_key)
    hiperfoco = aluno_dados.get('hiperfoco', '')
    prompt = f"Educational illustration about '{tema}'. Simple, clear, white background. {hiperfoco if hiperfoco else ''} No text."
    try:
        resp = client.images.generate(model="dall-e-3", prompt=prompt, size="1024x1024", quality="standard", n=1)
        return resp.data[0].url, None
    except Exception as e: return None, str(e)

def adaptar_ia(api_key, aluno, conteudo, tipo, materia, tema, qtd_imagens):
    if not api_key: return None, None, "Sem chave."
    client = OpenAI(api_key=api_key)
    
    instrucao_imgs = ""
    if qtd_imagens > 0:
        instrucao_imgs = f"""
        O documento tem {qtd_imagens} imagens (Imagem 1 a {qtd_imagens}).
        IMPORTANTE: Ao adaptar, você deve inserir a tag [[IMG_1]], [[IMG_2]], etc. EXATAMENTE no meio da questão onde a imagem deve aparecer.
        Não deixe as imagens para o final. Integre-as ao texto.
        """
    elif tipo == "imagem":
        instrucao_imgs = "Insira a tag [[IMG_ORIGINAL]] antes das questões."

    prompt_sys = "Você é um Especialista em Adaptação. Gere: 1. Racional (curto), 2. Atividade Adaptada (com tags de imagem no lugar certo)."
    prompt_user = f"ALUNO: {aluno['nome']} | DIAG: {aluno.get('diagnostico')}\nMATÉRIA: {materia} | TEMA: {tema}\n{instrucao_imgs}\nCONTEÚDO:\n"
    
    msgs = [{"role": "system", "content": prompt_sys}, {"role": "user", "content": []}]
    
    if tipo == "imagem":
        msgs[1]["content"].append({"type": "text", "text": prompt_user})
        msgs[1]["content"].append({"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{conteudo}"}})
    else:
        msgs[1]["content"].append({"type": "text", "text": prompt_user + conteudo})

    try:
        resp = client.chat.completions.create(model="gpt-4o-mini", messages=msgs, temperature=0.5)
        txt = resp.choices[0].message.content
        # Tenta separar Racional da Atividade (se a IA usar o divisor padrão ou não)
        if "---" in txt:
            parts = txt.split("---") # Pega a última parte como atividade
            return parts[0], parts[-1], None
        return "Racional integrado.", txt, None
    except Exception as e: return None, None, str(e)

# --- 6. INTERFACE ---
with st.sidebar:
    st.markdown("### Configuração")
    api_key = st.secrets.get('OPENAI_API_KEY', st.text_input("Chave OpenAI:", type="password"))
    if api_key: st.success("✅ Conectado")
    st.markdown("---")
    usar_dalle = st.toggle("🎨 Gerar Imagem IA", value=True)
    if st.button("🗑️ Limpar Tudo"): 
        for k in list(st.session_state.keys()):
            if k.startswith('res_'): del st.session_state[k]
        st.rerun()

st.markdown("""
    <div class="header-clean">
        <div style="font-size: 2.5rem;">🧩</div>
        <div>
            <p style="margin: 0; color: #004E92; font-size: 1.4rem; font-weight: 800;">Adaptador V4.6: Live Preview</p>
            <p style="margin: 0; color: #718096;">Edite o texto e veja as imagens se encaixarem em tempo real.</p>
        </div>
    </div>
""", unsafe_allow_html=True)

if not st.session_state.banco_estudantes:
    st.warning("⚠️ Crie um aluno no PEI 360º primeiro.")
    st.stop()

# Seleção
lista = [a['nome'] for a in st.session_state.banco_estudantes]
aluno = next(a for a in st.session_state.banco_estudantes if a['nome'] == st.selectbox("📂 Estudante:", lista, index=len(lista)-1))

c1, c2 = st.columns(2)
with c1:
    materia = st.selectbox("Matéria:", ["Matemática", "Português", "Ciências", "História", "Geografia"])
    tema = st.text_input("Tema:", placeholder="Ex: Frações")
with c2:
    arquivo = st.file_uploader("Arquivo (Word/PDF/Foto)", type=["docx","pdf","png","jpg"])
    texto_orig, tipo_arq, lista_imgs, img_unica = ler_arquivo_generico(arquivo)
    if tipo_arq == "docx": st.success(f"DOCX: {len(lista_imgs)} imagens encontradas.")
    elif tipo_arq: st.success("Arquivo carregado.")

if st.button("✨ GERAR ATIVIDADE", type="primary"):
    if not materia or not tema or not texto_orig: st.warning("Preencha tudo.")
    else:
        with st.spinner("Adaptando e diagramando..."):
            qtd = len(lista_imgs) if tipo_arq == "docx" else 0
            racional, atividade, err = adaptar_ia(api_key, aluno, texto_orig, tipo_arq, materia, tema, qtd)
            
            img_dalle = None
            if usar_dalle: img_dalle, _ = gerar_dalle(api_key, tema, aluno)
            
            if not err:
                st.session_state['res_racional'] = racional
                st.session_state['res_atv_editavel'] = atividade # Editável
                st.session_state['res_dalle'] = img_dalle
                st.session_state['res_imgs_orig'] = lista_imgs
                st.session_state['res_img_unica'] = img_unica
                st.rerun()

# --- ÁREA DE TRABALHO (EDITOR + PREVIEW) ---
if 'res_atv_editavel' in st.session_state:
    st.markdown("---")
    
    col_edit, col_view = st.columns([1, 1])
    
    # 1. EDITOR (Esquerda)
    with col_edit:
        st.subheader("✏️ Editor")
        st.caption("Mova as tags [[IMG_1]], [[IMG_2]] para posicionar as imagens.")
        
        novo_texto = st.text_area(
            "Texto da Atividade:", 
            value=st.session_state['res_atv_editavel'], 
            height=600,
            label_visibility="collapsed"
        )
        st.session_state['res_atv_editavel'] = novo_texto # Atualiza estado

    # 2. PREVIEW (Direita)
    with col_view:
        st.subheader("👁️ Resultado Final")
        st.caption("Como sairá no arquivo Word.")
        
        with st.container(border=True):
            # Imagem DALL-E
            if st.session_state.get('res_dalle'):
                st.image(st.session_state['res_dalle'], use_column_width=True)
            
            # Renderização do Texto + Imagens
            txt_atual = st.session_state['res_atv_editavel']
            partes = re.split(r'(\[\[IMG_\d+\]\]|\[\[IMG_ORIGINAL\]\])', txt_atual)
            
            for parte in partes:
                tag_match = re.match(r'\[\[IMG_(\d+)\]\]', parte)
                
                if tag_match:
                    idx = int(tag_match.group(1)) - 1
                    imgs = st.session_state.get('res_imgs_orig', [])
                    if 0 <= idx < len(imgs):
                        st.image(imgs[idx], use_column_width=True)
                    else:
                        st.markdown(f"🚫 *Imagem {idx+1} não existe*")
                        
                elif parte == "[[IMG_ORIGINAL]]" and st.session_state.get('res_img_unica'):
                    st.image(st.session_state['res_img_unica'], use_column_width=True)
                    
                else:
                    if parte.strip(): st.markdown(parte)

    # DOWNLOAD
    st.markdown("---")
    docx = construir_docx_final(
        st.session_state['res_atv_editavel'], 
        aluno['nome'], 
        materia, 
        st.session_state.get('res_imgs_orig', []), 
        st.session_state.get('res_dalle'),
        st.session_state.get('res_img_unica')
    )
    st.download_button("📥 BAIXAR ATIVIDADE (WORD)", docx, "atividade.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document", type="primary", use_container_width=True)
