import streamlit as st
from openai import OpenAI
from io import BytesIO
from docx import Document
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from pypdf import PdfReader
from PIL import Image
from streamlit_cropper import st_cropper # A NOVA FERRAMENTA
import base64
import os
import re
import requests
import zipfile

# --- 1. CONFIGURAÇÃO ---
st.set_page_config(page_title="Adaptador 360º V6.0", page_icon="🧩", layout="wide")

if 'banco_estudantes' not in st.session_state:
    st.session_state.banco_estudantes = []

# --- 2. ESTILO VISUAL ---
st.markdown("""
    <style>
    html, body, [class*="css"] { font-family: 'Nunito', sans-serif; color: #2D3748; }
    
    .header-clean {
        background-color: white; padding: 25px 40px; border-radius: 16px;
        border: 1px solid #EDF2F7; box-shadow: 0 4px 12px rgba(0,0,0,0.04);
        margin-bottom: 25px; display: flex; align-items: center; gap: 20px;
    }
    
    .action-bar {
        background-color: #F7FAFC; padding: 20px; border-radius: 16px;
        border: 1px solid #E2E8F0; margin-top: 20px; margin-bottom: 20px;
    }
    
    .crop-instruction {
        background-color: #EBF8FF; border-left: 4px solid #3182CE; padding: 15px;
        color: #2C5282; margin-bottom: 15px; border-radius: 4px;
    }

    div[data-testid="column"] .stButton button[kind="primary"] {
        border-radius: 12px !important; font-weight: 800 !important; height: 55px !important; width: 100%;
        background-color: #FF6B6B !important; border: none !important; color: white !important;
        font-size: 1.1rem !important; transition: 0.3s;
    }
    
    div[data-testid="column"] .stButton button[kind="secondary"] {
        border-radius: 12px !important; height: 55px !important; width: 100%;
        border: 2px solid #CBD5E0 !important; color: #718096 !important; background-color: white !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- 3. FUNÇÕES DE ARQUIVO ---
def otimizar_imagem_para_ia(image_bytes):
    try:
        img = Image.open(BytesIO(image_bytes))
        if img.mode in ("RGBA", "P"): img = img.convert("RGB")
        max_dim = 1024
        if max(img.size) > max_dim:
            ratio = max_dim / max(img.size)
            new_size = (int(img.width * ratio), int(img.height * ratio))
            img = img.resize(new_size, Image.Resampling.LANCZOS)
        buffer = BytesIO()
        img.save(buffer, format="JPEG", quality=85)
        return buffer.getvalue()
    except: return image_bytes

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
            media_files = [f for f in all_files if f.startswith('word/media/') and f.endswith(('.png', '.jpg', '.jpeg'))]
            media_files.sort(key=lambda f: int(re.search(r'image(\d+)', f).group(1)) if re.search(r'image(\d+)', f) else 0)
            for media in media_files:
                imagens.append(z.read(media))
    except: pass
    return texto, imagens

def baixar_imagem_url(url):
    try:
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200: return BytesIO(resp.content)
    except: pass
    return None

# --- 4. CONSTRUTOR DE DOCX ---
def construir_docx_final(texto_ia, aluno, materia, lista_imgs, img_dalle_url, tipo_atv):
    doc = Document()
    style = doc.styles['Normal']; style.font.name = 'Arial'; style.font.size = Pt(12)
    
    head = doc.add_heading(f'{tipo_atv.upper()} ADAPTADA - {materia.upper()}', 0)
    head.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p = doc.add_paragraph(f"Estudante: {aluno}")
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_paragraph("_"*50)

    # 1. Apoio Visual (DALL-E)
    if img_dalle_url:
        img_io = baixar_imagem_url(img_dalle_url)
        if img_io:
            try:
                doc.add_heading('Contexto Visual', level=3)
                doc.add_picture(img_io, width=Inches(4.5))
                doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
                doc.add_paragraph("")
            except: pass

    # 2. Atividade
    doc.add_heading('Questões', level=2)
    partes = re.split(r'(\[\[IMG_\d+\]\])', texto_ia)
    imagens_usadas = set()

    for parte in partes:
        tag_match = re.match(r'\[\[IMG_(\d+)\]\]', parte)
        if tag_match:
            try:
                idx_ia = int(tag_match.group(1)) - 1
                if len(lista_imgs) == 1: idx_ia = 0
                
                if 0 <= idx_ia < len(lista_imgs):
                    # INSERE A IMAGEM RECORTADA AQUI
                    doc.add_picture(BytesIO(lista_imgs[idx_ia]), width=Inches(5.5))
                    doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
                    doc.add_paragraph("") 
                    imagens_usadas.add(idx_ia)
            except: pass
        else:
            if parte.strip():
                texto_limpo = re.sub(r'\n{3,}', '\n\n', parte.strip())
                doc.add_paragraph(texto_limpo)

    # 3. Anexos
    sobras = [i for i in range(len(lista_imgs)) if i not in imagens_usadas]
    if sobras and len(lista_imgs) > 1:
        doc.add_page_break()
        doc.add_heading("Anexos Visuais", level=2)
        for idx in sobras:
            try:
                doc.add_picture(BytesIO(lista_imgs[idx]), width=Inches(4.0))
                doc.add_paragraph("")
            except: pass

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

def adaptar_atividade_v6(api_key, aluno, conteudo, tipo, materia, tema, tipo_atv, total_imagens, remover_respostas):
    if not api_key: return None, "Sem chave."
    client = OpenAI(api_key=api_key)
    
    instrucao_imgs = ""
    if total_imagens > 0 or tipo == "imagem":
        instrucao_imgs = "Insira a tag [[IMG_1]] EXATAMENTE onde a imagem/mapa deve aparecer no texto."

    instrucao_professor = ""
    if remover_respostas:
        instrucao_professor = """
        🚨 MODO LIVRO DO PROFESSOR:
        1. A imagem original contém respostas/gabarito. IGNORE-AS.
        2. Reescreva a atividade APENAS com as perguntas.
        3. Substitua respostas por linhas "__________".
        """

    prompt_sys = f"Você é um Especialista em Adaptação. {instrucao_professor}"
    prompt_user = f"ALUNO: {aluno['nome']} | DIAG: {aluno.get('diagnostico')}\nCONTEXTO: {materia} | {tema}\n{instrucao_imgs}\nCONTEÚDO:"
    
    msgs = [{"role": "system", "content": prompt_sys}, {"role": "user", "content": []}]
    
    if tipo == "imagem":
        # Envia a imagem (já recortada se for o caso)
        base64_image = base64.b64encode(conteudo[0]).decode('utf-8')
        msgs[1]["content"].append({"type": "text", "text": prompt_user})
        msgs[1]["content"].append({"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}})
    else:
        msgs[1]["content"].append({"type": "text", "text": prompt_user})

    try:
        resp = client.chat.completions.create(model="gpt-4o-mini", messages=msgs, temperature=0.3, max_tokens=4000)
        return resp.choices[0].message.content, None
    except Exception as e: return None, str(e)

# --- 6. INTERFACE ---
with st.sidebar:
    st.markdown("### Configuração")
    if 'OPENAI_API_KEY' in st.secrets:
        api_key = st.secrets['OPENAI_API_KEY']
        st.success("✅ OpenAI Ativa")
    else:
        api_key = st.text_input("Chave OpenAI:", type="password")
    
    st.markdown("---")
    st.info("✂️ **Nova Ferramenta:** Use o recorte para isolar mapas e figuras do texto original.")

st.markdown("""
    <div class="header-clean">
        <div style="font-size: 3rem;">🧩</div>
        <div>
            <p style="margin: 0; color: #004E92; font-size: 1.5rem; font-weight: 800;">Adaptador V6.0: Tesoura Digital</p>
            <p style="margin: 0; color: #718096;">Recorte apenas o que importa (Mapas, Gráficos) e elimine o texto poluído.</p>
        </div>
    </div>
""", unsafe_allow_html=True)

if not st.session_state.banco_estudantes:
    st.warning("⚠️ Crie um aluno no PEI 360º primeiro.")
    st.stop()

# --- SELEÇÃO ---
lista = [a['nome'] for a in st.session_state.banco_estudantes]
aluno = next(a for a in st.session_state.banco_estudantes if a['nome'] == st.selectbox("📂 Estudante:", lista, index=len(lista)-1))

c1, c2, c3 = st.columns([1, 1, 1])
with c1:
    materia = st.selectbox("Matéria:", ["Matemática", "Português", "Ciências", "História", "Geografia", "Inglês", "Artes"])
with c2:
    tema = st.text_input("Tema:", placeholder="Ex: Frações")
with c3:
    tipo_atv = st.selectbox("Tipo de Atividade:", ["Prova / Avaliação", "Tarefa de Casa", "Atividade de Sala", "Trabalho em Grupo"])

# --- UPLOAD & RECORTE ---
uploaded_file = st.file_uploader("Arquivo (FOTO ou DOCX)", type=["png","jpg","jpeg","docx"])

img_para_processar = None
tipo_arquivo = None
lista_imagens_finais = []

if uploaded_file:
    # SE FOR IMAGEM, ABRE O RECORTADOR
    if uploaded_file.type in ["image/png", "image/jpeg", "image/jpg"]:
        tipo_arquivo = "imagem"
        img_original = Image.open(uploaded_file)
        
        st.markdown("<div class='crop-instruction'>✂️ <b>TESOURA DIGITAL:</b> Arraste o retângulo na imagem abaixo para selecionar APENAS a figura/mapa que você quer na prova.</div>", unsafe_allow_html=True)
        
        # O Recortador Mágico
        cropped_img = st_cropper(img_original, realtime_update=True, box_color='#FF0000', aspect_ratio=None)
        
        st.caption("Prévia do Recorte:")
        st.image(cropped_img, width=200)
        
        # Converte o recorte para bytes para enviar pra IA e pro Word
        buf = BytesIO()
        cropped_img.save(buf, format="JPEG")
        img_bytes = buf.getvalue()
        
        # Salva na lista
        lista_imagens_finais = [img_bytes]
        
    # SE FOR DOCX, SEGUE O FLUXO NORMAL
    elif "word" in uploaded_file.type:
        tipo_arquivo = "docx"
        texto_docx, lista_imagens_finais = extrair_dados_docx(uploaded_file)
        if lista_imagens_finais:
            st.success(f"DOCX: {len(lista_imagens_finais)} imagens encontradas.")

# --- BARRA DE AÇÃO ---
st.markdown("<div class='action-bar'>", unsafe_allow_html=True)
c_prof, c_img = st.columns(2)
with c_prof:
    modo_professor = st.checkbox("🕵️ Modo Livro do Professor (Remover Respostas)", value=True)
with c_img:
    usar_dalle = st.toggle("🎨 Criar Capa Visual (IA)", value=True)

st.markdown("---")
col_gerar, col_reset = st.columns([3, 1])

with col_gerar:
    btn_gerar = st.button("✨ GERAR ATIVIDADE", type="primary", use_container_width=True)

with col_reset:
    if st.button("🗑️ Nova Atividade", type="secondary", use_container_width=True):
        st.session_state.pop('res_texto', None)
        st.rerun()
st.markdown("</div>", unsafe_allow_html=True)

# --- LÓGICA ---
if btn_gerar:
    if not materia or not tema or not uploaded_file: st.warning("Preencha tudo.")
    else:
        try:
            with st.spinner("Processando recorte e adaptando..."):
                qtd = len(lista_imagens_finais)
                
                # Se for imagem, mandamos o RECORTE para a IA, não a original gigante
                conteudo_envio = lista_imagens_finais if tipo_arquivo == "imagem" else texto_docx
                
                texto_adaptado, err = adaptar_atividade_v6(
                    api_key, 
                    aluno, 
                    conteudo_envio, 
                    tipo_arquivo, 
                    materia, 
                    tema, 
                    tipo_atv, 
                    qtd, 
                    modo_professor
                )
                
                img_dalle = None
                if usar_dalle and not err:
                    img_dalle, _ = gerar_dalle(api_key, tema, aluno)
                
                if not err:
                    st.session_state['res_texto'] = texto_adaptado
                    st.session_state['res_imgs'] = lista_imagens_finais
                    st.session_state['res_dalle'] = img_dalle
                    st.session_state['tipo_selecionado'] = tipo_atv
                    st.rerun()
                else:
                    st.error(f"Erro na IA: {err}")
        except Exception as e:
            st.error(f"Erro: {e}")

# --- RESULTADOS ---
if 'res_texto' in st.session_state:
    st.markdown("---")
    st.subheader("👁️ Resultado Final")
    
    with st.container(border=True):
        if st.session_state.get('res_dalle'):
            st.image(st.session_state['res_dalle'], width=250, caption="Capa Visual")
        
        txt = st.session_state['res_texto']
        partes = re.split(r'(\[\[IMG_\d+\]\])', txt)
        for parte in partes:
            if "[[IMG_" in parte:
                try:
                    idx = 0 if len(st.session_state['res_imgs']) == 1 else int(re.search(r'\d+', parte).group()) - 1
                    imgs = st.session_state['res_imgs']
                    if 0 <= idx < len(imgs): 
                        st.image(imgs[idx], width=400, caption="Imagem Recortada (Limpa)")
                except: pass
            else:
                if parte.strip(): st.markdown(parte)

    docx = construir_docx_final(
        st.session_state['res_texto'], 
        aluno['nome'], 
        materia, 
        st.session_state['res_imgs'], 
        st.session_state.get('res_dalle'),
        st.session_state.get('tipo_selecionado', 'Atividade')
    )
    
    st.download_button(
        label="📥 BAIXAR ATIVIDADE (WORD)",
        data=docx,
        file_name=f"Atividade_{aluno['nome']}.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        type="primary",
        use_container_width=True
    )
