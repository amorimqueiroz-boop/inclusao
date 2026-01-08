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
st.set_page_config(page_title="Adaptador 360º V4.9", page_icon="🧩", layout="wide")

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
    
    div[data-testid="column"] .stButton button {
        border-radius: 12px !important; font-weight: 800 !important; height: 50px !important; width: 100%;
    }
    
    /* Botão de Limpeza com cor diferente */
    div[data-testid="column"]:nth-of-type(3) .stButton button {
        background-color: white !important;
        color: #E53E3E !important;
        border: 1px solid #E53E3E !important;
    }
    div[data-testid="column"]:nth-of-type(3) .stButton button:hover {
        background-color: #FFF5F5 !important;
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
            media_files = [f for f in all_files if f.startswith('word/media/') and f.endswith(('.png', '.jpg', '.jpeg'))]
            media_files.sort(key=lambda f: int(re.search(r'image(\d+)', f).group(1)) if re.search(r'image(\d+)', f) else 0)
            for media in media_files:
                imagens.append(z.read(media))
    except: pass
    return texto, imagens

def ler_arquivo(uploaded_file):
    if uploaded_file is None: return None, None, []
    texto, imgs, tipo = "", [], "indefinido"
    try:
        if uploaded_file.type == "application/pdf":
            reader = PdfReader(uploaded_file)
            for page in reader.pages: texto += page.extract_text() + "\n"
            tipo = "pdf"
        elif "word" in uploaded_file.type:
            texto, imgs = extrair_dados_docx(uploaded_file)
            tipo = "docx"
        elif "image" in uploaded_file.type:
            imgs = [uploaded_file.getvalue()]
            texto = "Conteúdo visual (foto)."
            tipo = "imagem"
    except: pass
    return texto, tipo, imgs

def baixar_imagem_url(url):
    try:
        resp = requests.get(url)
        if resp.status_code == 200: return BytesIO(resp.content)
    except: pass
    return None

# --- 4. CONSTRUTOR DE DOCX ---
def construir_docx_final(texto_ia, aluno, materia, lista_imgs, img_dalle_url, tipo_atv):
    doc = Document()
    style = doc.styles['Normal']; style.font.name = 'Arial'; style.font.size = Pt(12)
    
    # Cabeçalho
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
                if 0 <= idx_ia < len(lista_imgs):
                    doc.add_picture(BytesIO(lista_imgs[idx_ia]), width=Inches(5.0))
                    doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
                    doc.add_paragraph("") 
                    imagens_usadas.add(idx_ia)
                else:
                    doc.add_paragraph(f"[Imagem {idx_ia+1} não encontrada]")
            except: pass
        else:
            if parte.strip():
                texto_limpo = re.sub(r'\n{3,}', '\n\n', parte.strip())
                doc.add_paragraph(texto_limpo)

    # 3. Anexos
    sobras = [i for i in range(len(lista_imgs)) if i not in imagens_usadas]
    if sobras:
        doc.add_page_break()
        doc.add_heading("Anexos Visuais", level=2)
        for idx in sobras:
            try:
                doc.add_paragraph(f"Figura {idx+1}:")
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

def adaptar_atividade_v49(api_key, aluno, conteudo, tipo, materia, tema, tipo_atv, total_imagens):
    if not api_key: return None, "Sem chave."
    client = OpenAI(api_key=api_key)
    
    instrucao_imgs = ""
    if total_imagens > 0:
        instrucao_imgs = f"""
        O arquivo original tem {total_imagens} imagens sequenciais (Imagem 1, Imagem 2...).
        REGRA DE OURO: Ao encontrar uma questão que usa imagem, insira a tag [[IMG_1]] (para a primeira), [[IMG_2]] (para a segunda) EXATAMENTE onde a imagem deve aparecer no texto.
        """
    elif tipo == "imagem":
        instrucao_imgs = "O conteúdo é uma foto. Use [[IMG_1]] no início."

    prompt_sys = f"Você é um Especialista em Adaptação de {tipo_atv}. Gere a atividade adaptada com linguagem adequada."
    
    prompt_user = f"""
    ALUNO: {aluno['nome']} | DIAG: {aluno.get('diagnostico')}
    CONTEXTO: {materia} | {tema} | TIPO: {tipo_atv}
    
    {instrucao_imgs}
    
    CONTEÚDO PARA ADAPTAR:
    {conteudo}
    """
    
    msgs = [{"role": "system", "content": prompt_sys}, {"role": "user", "content": []}]
    
    if tipo == "imagem":
        msgs[1]["content"].append({"type": "text", "text": prompt_user})
        msgs[1]["content"].append({"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64.b64encode(conteudo[0]).decode('utf-8')}"}})
    else:
        msgs[1]["content"].append({"type": "text", "text": prompt_user})

    try:
        resp = client.chat.completions.create(model="gpt-4o-mini", messages=msgs, temperature=0.4)
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
    st.info("💡 **Dica:** Para provas com imagens, use sempre arquivo **DOCX**.")

st.markdown("""
    <div class="header-clean">
        <div style="font-size: 3rem;">🧩</div>
        <div>
            <p style="margin: 0; color: #004E92; font-size: 1.5rem; font-weight: 800;">Adaptador V4.9: Painel de Controle</p>
            <p style="margin: 0; color: #718096;">Fluxo otimizado com controles integrados.</p>
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
    # BOTÃO RESTAURADO E REPOSICIONADO
    tipo_atv = st.selectbox("Tipo de Atividade:", ["Prova / Avaliação", "Tarefa de Casa", "Atividade de Sala", "Trabalho em Grupo", "Atividade Lúdica"])

arquivo = st.file_uploader("Arquivo Original (DOCX, PDF, FOTO)", type=["docx","pdf","png","jpg"])
texto_orig, tipo_arq, lista_imgs = ler_arquivo(arquivo)

if tipo_arq == "docx": st.success(f"📎 DOCX lido com {len(lista_imgs)} imagens.")
elif tipo_arq: st.success("📎 Arquivo carregado.")

# --- BARRA DE AÇÃO (CENTRALIZADA) ---
st.markdown("<div class='action-bar'>", unsafe_allow_html=True)
col_toggle, col_btn, col_clean = st.columns([1, 2, 1])

with col_toggle:
    # CHAVE PARA GERAR IMAGEM (DENTRO DA PÁGINA)
    st.write("") # Espaçamento
    usar_dalle = st.toggle("🎨 Criar Capa Visual (IA)", value=True, help="Usa DALL-E 3 para gerar uma imagem de contexto.")

with col_btn:
    btn_gerar = st.button("✨ ADAPTAR ATIVIDADE", type="primary")

with col_clean:
    # BOTÃO DE LIMPEZA
    if st.button("🗑️ Nova Atividade"):
        st.session_state.pop('res_texto', None)
        st.rerun()
st.markdown("</div>", unsafe_allow_html=True)

# --- LÓGICA ---
if btn_gerar:
    if not materia or not tema or not texto_orig: st.warning("Preencha todos os campos acima.")
    else:
        with st.spinner(f"Adaptando {tipo_atv} para {aluno['nome']}..."):
            qtd = len(lista_imgs)
            texto_adaptado, err = adaptar_atividade_v49(api_key, aluno, texto_orig if tipo_arq!="imagem" else lista_imgs, tipo_arq, materia, tema, tipo_atv, qtd)
            
            img_dalle = None
            if usar_dalle and not err:
                img_dalle, _ = gerar_dalle(api_key, tema, aluno)
            
            if not err:
                st.session_state['res_texto'] = texto_adaptado
                st.session_state['res_imgs'] = lista_imgs
                st.session_state['res_dalle'] = img_dalle
                st.session_state['tipo_selecionado'] = tipo_atv # Salva para o título do Word
                st.rerun()

# --- RESULTADOS ---
if 'res_texto' in st.session_state:
    st.markdown("---")
    
    # Preview Visual
    st.subheader(f"👁️ Resultado: {st.session_state.get('tipo_selecionado', 'Atividade')}")
    with st.container(border=True):
        if st.session_state.get('res_dalle'):
            st.image(st.session_state['res_dalle'], width=250, caption="Capa Visual")
        
        # Renderização Inteligente
        txt = st.session_state['res_texto']
        partes = re.split(r'(\[\[IMG_\d+\]\])', txt)
        for parte in partes:
            if "[[IMG_" in parte:
                try:
                    idx = int(re.search(r'\d+', parte).group()) - 1
                    imgs = st.session_state['res_imgs']
                    if 0 <= idx < len(imgs): st.image(imgs[idx], width=300)
                except: pass
            else:
                if parte.strip(): st.markdown(parte)

    # Download
    docx = construir_docx_final(
        st.session_state['res_texto'], 
        aluno['nome'], 
        materia, 
        st.session_state['res_imgs'], 
        st.session_state.get('res_dalle'),
        st.session_state.get('tipo_selecionado', 'Atividade')
    )
    
    st.download_button(
        label="📥 BAIXAR ARQUIVO WORD PRONTO",
        data=docx,
        file_name=f"Atividade_{aluno['nome']}.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        type="primary",
        use_container_width=True
    )
