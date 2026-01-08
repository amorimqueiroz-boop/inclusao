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
st.set_page_config(page_title="Adaptador 360º V4.3", page_icon="🧩", layout="wide")

if 'banco_estudantes' not in st.session_state:
    st.session_state.banco_estudantes = []

# --- 2. ESTILO VISUAL ---
st.markdown("""
    <style>
    html, body, [class*="css"] { font-family: 'Nunito', sans-serif; color: #2D3748; }
    :root { --brand-blue: #004E92; --card-radius: 16px; }
    .header-clean {
        background-color: white; padding: 30px 40px; border-radius: var(--card-radius);
        border: 1px solid #EDF2F7; box-shadow: 0 4px 12px rgba(0,0,0,0.04);
        margin-bottom: 30px; display: flex; align-items: center; gap: 20px;
    }
    .unified-card {
        background-color: white; padding: 25px; border-radius: var(--card-radius);
        border: 1px solid #EDF2F7; box-shadow: 0 4px 6px rgba(0,0,0,0.03); margin-bottom: 20px;
    }
    .rationale-box {
        background-color: #F0F4FF; border-left: 4px solid #004E92; padding: 15px;
        border-radius: 8px; font-size: 0.9rem; color: #1A365D; margin-bottom: 20px;
    }
    div[data-testid="stFileUploader"] section { 
        background-color: #F7FAFC; border: 2px dashed #CBD5E0; border-radius: 16px; 
    }
    div[data-testid="column"] .stButton button {
        border-radius: 12px !important; font-weight: 800 !important; height: 50px !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- 3. FUNÇÕES DE ARQUIVO E MINERAÇÃO ---

def extrair_dados_docx(uploaded_file):
    """
    Lê o DOCX e retorna:
    1. Texto completo (string)
    2. Lista de bytes das imagens NA ORDEM CORRETA (image1, image2...)
    """
    uploaded_file.seek(0)
    texto = ""
    imagens = []
    
    try:
        # 1. Extrair Texto
        doc = Document(uploaded_file)
        texto = "\n".join([p.text for p in doc.paragraphs if p.text.strip() != ""])
        
        # 2. Extrair Imagens (Ordenadas)
        uploaded_file.seek(0)
        with zipfile.ZipFile(uploaded_file) as z:
            # Pega lista de arquivos, filtra media, e ORDENA (image1, image2, image10...)
            all_files = z.namelist()
            media_files = [f for f in all_files if f.startswith('word/media/') and f.endswith(('.png', '.jpg', '.jpeg'))]
            
            # Função para extrair o número do nome do arquivo para ordenar corretamente (image2 vem antes de image10)
            def get_number(filename):
                nums = re.findall(r'\d+', filename)
                return int(nums[-1]) if nums else 0
            
            media_files.sort(key=get_number)
            
            for media in media_files:
                imagens.append(z.read(media))
                
    except Exception as e:
        return f"Erro leitura: {e}", []
        
    return texto, imagens

def ler_arquivo_generico(uploaded_file):
    """Router de leitura para PDF, DOCX ou Imagem"""
    if uploaded_file is None: return None, None, [], None
    
    tipo = "indefinido"
    texto = ""
    imgs = []
    img_unica = None
    
    if uploaded_file.type == "application/pdf":
        try:
            reader = PdfReader(uploaded_file)
            for page in reader.pages: texto += page.extract_text() + "\n"
            tipo = "pdf"
        except: return "", "erro", [], None
        
    elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        texto, imgs = extrair_dados_docx(uploaded_file)
        tipo = "docx"
        
    elif uploaded_file.type in ["image/png", "image/jpeg", "image/jpg"]:
        img_bytes = uploaded_file.getvalue()
        # Para enviar pro GPT ler o conteúdo da imagem
        texto = base64.b64encode(img_bytes).decode('utf-8') 
        img_unica = img_bytes
        tipo = "imagem"
        
    return texto, tipo, imgs, img_unica

def baixar_imagem_url(url):
    try:
        resp = requests.get(url)
        if resp.status_code == 200: return BytesIO(resp.content)
    except: pass
    return None

# --- 4. CONSTRUTOR INTELIGENTE DE DOCX ---
def construir_docx_final(racional_texto, atividade_texto, aluno, materia, lista_imgs, img_dalle_url):
    doc = Document()
    style = doc.styles['Normal']; style.font.name = 'Arial'; style.font.size = Pt(12)
    
    # Cabeçalho
    head = doc.add_heading(f'ATIVIDADE ADAPTADA - {materia.upper()}', 0)
    head.alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_paragraph(f"Estudante: {aluno}")
    doc.add_paragraph("_"*50)

    # 1. Apoio Visual (DALL-E) no topo
    if img_dalle_url:
        doc.add_heading('Apoio Visual (Contexto)', level=2)
        img_io = baixar_imagem_url(img_dalle_url)
        if img_io:
            try:
                doc.add_picture(img_io, width=Inches(4.0))
                doc.add_paragraph("Figura de apoio ao tema.")
                doc.add_paragraph("")
            except: pass

    # 2. Atividade (Texto + Imagens Originais intercaladas)
    doc.add_heading('Atividade', level=2)
    
    # Aqui está o segredo: Dividimos o texto pelas tags [[IMG_X]]
    # Ex: ["Questão 1: Olhe o mapa.", "[[IMG_1]]", "Qual a capital?"]
    partes = re.split(r'(\[\[IMG_\d+\]\])', atividade_texto)
    
    for parte in partes:
        # Se for uma tag de imagem
        if "[[IMG_" in parte:
            try:
                # Extrai o número: [[IMG_1]] -> 1
                idx = int(re.findall(r'\d+', parte)[0]) - 1 # Array começa em 0
                
                if 0 <= idx < len(lista_imgs):
                    # Insere a imagem original
                    doc.add_picture(BytesIO(lista_imgs[idx]), width=Inches(4.5))
                    doc.add_paragraph("") # Espaço
            except:
                doc.add_paragraph(f"[Imagem original {idx+1} não encontrada]")
        
        # Se for texto normal
        else:
            # Limpa espaços excessivos e adiciona
            if parte.strip():
                doc.add_paragraph(parte.strip())

    buffer = BytesIO(); doc.save(buffer); buffer.seek(0)
    return buffer

# --- 5. INTELIGÊNCIA ---
def gerar_dalle(api_key, tema, aluno_dados):
    client = OpenAI(api_key=api_key)
    hiperfoco = aluno_dados.get('hiperfoco', '')
    contexto = f"Include elements of '{hiperfoco}' subtly." if hiperfoco else ""
    prompt = f"Educational illustration about '{tema}'. Simple, clear, white background. {contexto} No text."
    try:
        resp = client.images.generate(model="dall-e-3", prompt=prompt, size="1024x1024", quality="standard", n=1)
        return resp.data[0].url, None
    except Exception as e: return None, str(e)

def adaptar_v4_3(api_key, aluno, conteudo, tipo, materia, tema, qtd_imagens):
    if not api_key: return None, None, "Sem chave."
    client = OpenAI(api_key=api_key)
    
    # Instrução específica sobre as imagens
    instrucao_imagens = ""
    if qtd_imagens > 0:
        instrucao_imagens = f"""
        ATENÇÃO: O documento original possui {qtd_imagens} imagens/figuras.
        Ao adaptar o texto, você DEVE indicar onde cada imagem deve entrar usando EXATAMENTE a tag [[IMG_1]] para a primeira, [[IMG_2]] para a segunda, etc.
        Exemplo: "Observe o gráfico abaixo:\n[[IMG_1]]\nAgora responda..."
        Não deixe as imagens de fora se elas forem importantes para a questão.
        """

    prompt_sys = """
    Você é um Especialista em Adaptação Curricular e DUA.
    Retorne DOIS blocos separados por '---DIVISOR---':
    1. O Racional para o professor.
    2. A Atividade Adaptada para o aluno (com as tags de imagem inseridas).
    """
    
    prompt_user = f"""
    ALUNO: {aluno['nome']} | DIAG: {aluno.get('diagnostico')}
    MATÉRIA: {materia} | TEMA: {tema}
    
    {instrucao_imagens}
    
    CONTEÚDO ORIGINAL PARA ADAPTAR:
    """
    
    msgs = [{"role": "system", "content": prompt_sys}, {"role": "user", "content": []}]
    
    if tipo == "imagem":
        msgs[1]["content"].append({"type": "text", "text": prompt_user})
        msgs[1]["content"].append({"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{conteudo}"}})
    else:
        msgs[1]["content"].append({"type": "text", "text": f"{prompt_user}\n{conteudo}"})

    try:
        resp = client.chat.completions.create(model="gpt-4o-mini", messages=msgs, temperature=0.5)
        txt = resp.choices[0].message.content
        parts = txt.split("---DIVISOR---")
        if len(parts) == 2: return parts[0], parts[1], None
        return None, txt, "Erro formato."
    except Exception as e: return None, None, str(e)

# --- 6. INTERFACE ---
with st.sidebar:
    st.markdown("### ⚙️ Configuração")
    api_key = st.secrets.get('OPENAI_API_KEY', st.text_input("Chave OpenAI:", type="password"))
    if api_key: st.success("✅ Conectado")
    st.markdown("---")
    usar_dalle = st.toggle("🎨 Gerar Capa/Apoio (DALL-E)", value=True)
    st.markdown("---")
    if st.button("🗑️ Limpar"): st.session_state.pop('res_atv', None); st.rerun()

st.markdown("""
    <div class="header-clean">
        <div style="font-size: 3rem;">🧩</div>
        <div>
            <p style="margin: 0; color: #004E92; font-size: 1.5rem; font-weight: 800;">Adaptador V4.3: Montagem Inteligente</p>
            <p style="margin: 0; color: #718096;">As imagens originais são inseridas automaticamente dentro das questões.</p>
        </div>
    </div>
""", unsafe_allow_html=True)

if not st.session_state.banco_estudantes:
    st.warning("⚠️ Crie um aluno no PEI 360º primeiro.")
    st.stop()

# Seleção
lista = [a['nome'] for a in st.session_state.banco_estudantes]
aluno = next(a for a in st.session_state.banco_estudantes if a['nome'] == st.selectbox("📂 Estudante:", lista, index=len(lista)-1))

with st.expander(f"👤 Perfil: {aluno['nome']}", expanded=False):
    st.write(f"Diag: {aluno.get('diagnostico')}")

c1, c2 = st.columns(2)
with c1:
    materia = st.selectbox("Matéria:", ["Matemática", "Português", "Ciências", "História", "Geografia", "Inglês"])
    tema = st.text_input("Tema:", placeholder="Ex: Frações")
    tipo_atv = st.selectbox("Tipo:", ["Prova", "Tarefa", "Trabalho"])
with c2:
    arquivo = st.file_uploader("Original (Word com Imagens é ideal)", type=["docx","pdf","png","jpg"])
    
    # Processamento Inicial
    texto_orig, tipo_arq, lista_imgs, img_unica = ler_arquivo_generico(arquivo)
    
    if tipo_arq == "docx":
        st.success(f"DOCX lido. {len(lista_imgs)} imagens recuperadas.")
        if len(lista_imgs) > 0:
            with st.expander("Ver imagens encontradas"):
                cols = st.columns(min(len(lista_imgs), 4))
                for i, img in enumerate(lista_imgs):
                    if i < 4: cols[i].image(img, caption=f"Img {i+1}", width=100)
    elif tipo_arq: st.success(f"{tipo_arq} carregado.")

if st.button("✨ ADAPTAR E MONTAR", type="primary"):
    if not materia or not tema or not texto_orig: st.warning("Preencha tudo.")
    else:
        qtd_imgs = len(lista_imgs) if tipo_arq == "docx" else 0
        
        with st.spinner("IA reconstruindo a atividade..."):
            racional, atividade, err = adaptar_v4_3(api_key, aluno, texto_orig, tipo_arq, materia, tema, qtd_imgs)
        
        img_dalle = None
        if usar_dalle and not err:
            with st.spinner("Gerando apoio visual..."):
                img_dalle, _ = gerar_dalle(api_key, tema, aluno)
        
        if not err:
            st.session_state['res_racional'] = racional
            st.session_state['res_atv'] = atividade
            st.session_state['res_dalle'] = img_dalle
            st.session_state['res_imgs_orig'] = lista_imgs
            st.success("Documento montado com sucesso!")

# RESULTADOS
if 'res_atv' in st.session_state:
    st.markdown("---")
    with st.expander("🧠 Racional (Professor)", expanded=False):
        st.info(st.session_state['res_racional'])
    
    c1, c2 = st.columns([1, 2])
    with c1:
        if st.session_state.get('res_dalle'):
            st.image(st.session_state['res_dalle'], caption="Apoio Visual (IA)")
    with c2:
        st.markdown("### Visualização Prévia")
        st.caption("Nota: No arquivo Word baixado, as imagens originais estarão no meio do texto.")
        st.code(st.session_state['res_atv'], language="markdown")

    docx = construir_docx_final(
        st.session_state['res_atv'], 
        aluno['nome'], 
        materia, 
        st.session_state.get('res_imgs_orig', []), 
        st.session_state.get('res_dalle')
    )
    
    st.download_button("📥 BAIXAR PROVA PRONTA (WORD)", docx, "atividade_adaptada.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document", type="primary")
