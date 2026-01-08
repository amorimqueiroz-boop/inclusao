import streamlit as st
from openai import OpenAI
from io import BytesIO
from docx import Document
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from pypdf import PdfReader
from fpdf import FPDF
from PIL import Image # Importante para otimização
import base64
import os
import re
import requests
import zipfile

# --- 1. CONFIGURAÇÃO ---
st.set_page_config(page_title="Adaptador 360º V5.2", page_icon="🧩", layout="wide")

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
    
    div[data-testid="column"] .stButton button[kind="primary"] {
        border-radius: 12px !important; font-weight: 800 !important; height: 55px !important; width: 100%;
        background-color: #FF6B6B !important; border: none !important;
        font-size: 1.1rem !important;
    }
    
    div[data-testid="column"] .stButton button[kind="secondary"] {
        border-radius: 12px !important; height: 55px !important; width: 100%;
        border: 2px solid #CBD5E0 !important; color: #718096 !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- 3. FUNÇÕES DE ARQUIVO E OTIMIZAÇÃO ---

def otimizar_imagem(image_bytes):
    """Reduz o tamanho da imagem para não travar a IA"""
    try:
        img = Image.open(BytesIO(image_bytes))
        # Converte para RGB se for PNG transparente
        if img.mode in ("RGBA", "P"): img = img.convert("RGB")
        
        # Redimensiona se for muito grande (max 1500px)
        max_size = 1500
        if max(img.size) > max_size:
            ratio = max_size / max(img.size)
            new_size = (int(img.width * ratio), int(img.height * ratio))
            img = img.resize(new_size, Image.Resampling.LANCZOS)
            
        buffer = BytesIO()
        img.save(buffer, format="JPEG", quality=85) # Comprime para JPEG
        return buffer.getvalue()
    except Exception as e:
        st.error(f"Erro ao otimizar imagem: {e}")
        return image_bytes # Retorna original se falhar

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
    except Exception as e: st.error(f"Erro ao ler DOCX: {e}")
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
            raw_bytes = uploaded_file.getvalue()
            # OTIMIZAÇÃO AQUI
            opt_bytes = otimizar_imagem(raw_bytes)
            imgs = [opt_bytes]
            texto = "Conteúdo visual (foto)."
            tipo = "imagem"
    except Exception as e: st.error(f"Erro no upload: {e}")
    return texto, tipo, imgs

def baixar_imagem_url(url):
    try:
        resp = requests.get(url, timeout=5)
        if resp.status_code == 200: return BytesIO(resp.content)
    except: pass
    return None

# --- 4. CONSTRUTOR DE DOCX ---
def construir_docx_final(texto_ia, aluno, materia, lista_imgs, img_dalle_url, tipo_atv):
    try:
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
                doc.add_heading('Contexto Visual', level=3)
                doc.add_picture(img_io, width=Inches(4.5))
                doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
                doc.add_paragraph("")

        # 2. Atividade
        doc.add_heading('Questões', level=2)
        partes = re.split(r'(\[\[IMG_\d+\]\])', texto_ia)
        imagens_usadas = set()

        for parte in partes:
            tag_match = re.match(r'\[\[IMG_(\d+)\]\]', parte)
            if tag_match:
                try:
                    # Para foto única (livro do professor), usamos sempre a índice 0
                    idx_ia = int(tag_match.group(1)) - 1
                    # Se só tem 1 imagem na lista, usamos ela independente do número que a IA chutou
                    if len(lista_imgs) == 1: idx_ia = 0
                    
                    if 0 <= idx_ia < len(lista_imgs):
                        doc.add_picture(BytesIO(lista_imgs[idx_ia]), width=Inches(5.5))
                        doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
                        doc.add_paragraph("") 
                        imagens_usadas.add(idx_ia)
                except: pass
            else:
                if parte.strip():
                    texto_limpo = re.sub(r'\n{3,}', '\n\n', parte.strip())
                    doc.add_paragraph(texto_limpo)

        # 3. Anexos (Segurança)
        sobras = [i for i in range(len(lista_imgs)) if i not in imagens_usadas]
        if sobras and len(lista_imgs) > 1: # Só mostra anexo se for mais de 1 imagem
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
    except Exception as e:
        st.error(f"Erro ao montar Word: {e}")
        return None

# --- 5. INTELIGÊNCIA ---
def gerar_dalle(api_key, tema, aluno_dados):
    client = OpenAI(api_key=api_key)
    hiperfoco = aluno_dados.get('hiperfoco', '')
    prompt = f"Educational illustration about '{tema}'. Simple, clear, white background. {hiperfoco if hiperfoco else ''} No text."
    try:
        resp = client.images.generate(model="dall-e-3", prompt=prompt, size="1024x1024", quality="standard", n=1)
        return resp.data[0].url, None
    except Exception as e: return None, f"Erro DALL-E: {e}"

def adaptar_atividade_v5(api_key, aluno, conteudo, tipo, materia, tema, tipo_atv, total_imagens, remover_respostas):
    if not api_key: return None, "Chave OpenAI não configurada."
    client = OpenAI(api_key=api_key)
    
    instrucao_imgs = ""
    if total_imagens > 0:
        instrucao_imgs = f"Insira a tag [[IMG_1]] onde a imagem deve aparecer."
    elif tipo == "imagem":
        instrucao_imgs = "Insira a tag [[IMG_1]] no início do texto."

    instrucao_professor = ""
    if remover_respostas:
        instrucao_professor = """
        🚨 MODO LIVRO DO PROFESSOR:
        1. A imagem contém RESPOSTAS em azul/rosa. IGNORE e REMOVA todas as respostas.
        2. Copie APENAS as perguntas e enunciados.
        3. Substitua as respostas por linhas (_______) ou espaços em branco.
        4. O aluno não pode ver o gabarito.
        """

    prompt_sys = f"Você é um Especialista em Adaptação. {instrucao_professor}"
    
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
        # Imagem já otimizada aqui
        msgs[1]["content"].append({"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64.b64encode(conteudo[0]).decode('utf-8')}"}})
    else:
        msgs[1]["content"].append({"type": "text", "text": prompt_user})

    try:
        # Aumentei o timeout para evitar cortes bruscos
        resp = client.chat.completions.create(model="gpt-4o-mini", messages=msgs, temperature=0.3, timeout=40)
        return resp.choices[0].message.content, None
    except Exception as e: return None, f"Erro IA: {str(e)}"

# --- 6. INTERFACE ---
with st.sidebar:
    st.markdown("### Configuração")
    if 'OPENAI_API_KEY' in st.secrets:
        api_key = st.secrets['OPENAI_API_KEY']
        st.success("✅ OpenAI Ativa")
    else:
        api_key = st.text_input("Chave OpenAI:", type="password")
    
    st.markdown("---")
    st.info("Para remover respostas em azul, ative o 'Modo Livro do Professor' abaixo.")

st.markdown("""
    <div class="header-clean">
        <div style="font-size: 3rem;">🧩</div>
        <div>
            <p style="margin: 0; color: #004E92; font-size: 1.5rem; font-weight: 800;">Adaptador V5.2: Otimizado</p>
            <p style="margin: 0; color: #718096;">Compressão automática de imagens para maior velocidade.</p>
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

arquivo = st.file_uploader("Arquivo Original (FOTO DO LIVRO, PDF ou DOCX)", type=["png","jpg","jpeg","pdf","docx"])
texto_orig, tipo_arq, lista_imgs = ler_arquivo(arquivo)

if tipo_arq: st.success(f"Arquivo carregado ({tipo_arq}).")

# --- BARRA DE AÇÃO ---
st.markdown("<div class='action-bar'>", unsafe_allow_html=True)
c_prof, c_img = st.columns(2)
with c_prof:
    modo_professor = st.checkbox("🕵️ Modo Livro do Professor (Remover Respostas)", value=False, help="Remove respostas em azul/rosa.")
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

# --- LÓGICA BLINDADA ---
if btn_gerar:
    if not materia or not tema or not texto_orig: 
        st.warning("Preencha todos os campos e faça o upload.")
    else:
        try:
            # Etapa 1: Processamento da IA
            with st.status("🤖 Inteligência Artificial trabalhando...", expanded=True) as status:
                st.write("Lendo imagens e removendo respostas...")
                qtd = len(lista_imgs)
                
                texto_adaptado, err = adaptar_atividade_v5(
                    api_key, 
                    aluno, 
                    texto_orig if tipo_arq!="imagem" else lista_imgs, 
                    tipo_arq, 
                    materia, 
                    tema, 
                    tipo_atv, 
                    qtd,
                    modo_professor
                )
                
                if err:
                    status.update(label="Erro na IA!", state="error")
                    st.error(err)
                    st.stop()
                
                img_dalle = None
                if usar_dalle:
                    st.write("Gerando capa visual...")
                    img_dalle, _ = gerar_dalle(api_key, tema, aluno)
                
                status.update(label="Processamento Concluído!", state="complete", expanded=False)

            # Etapa 2: Salvar Estado
            st.session_state['res_texto'] = texto_adaptado
            st.session_state['res_imgs'] = lista_imgs
            st.session_state['res_dalle'] = img_dalle
            st.session_state['tipo_selecionado'] = tipo_atv
            st.rerun()
            
        except Exception as e:
            st.error(f"Erro crítico no processamento: {str(e)}")

# --- RESULTADOS ---
if 'res_texto' in st.session_state:
    st.markdown("---")
    st.subheader("👁️ Resultado Final")
    
    with st.container(border=True):
        if st.session_state.get('res_dalle'):
            st.image(st.session_state['res_dalle'], width=250, caption="Capa Visual")
        
        txt = st.session_state['res_texto']
        # Renderização segura
        try:
            partes = re.split(r'(\[\[IMG_\d+\]\])', txt)
            for parte in partes:
                if "[[IMG_" in parte:
                    try:
                        # Se for foto única, mostra a primeira sempre
                        idx = 0 if len(st.session_state['res_imgs']) == 1 else int(re.search(r'\d+', parte).group()) - 1
                        imgs = st.session_state['res_imgs']
                        if 0 <= idx < len(imgs): 
                            st.image(imgs[idx], width=400, caption="Imagem Original")
                    except: pass
                else:
                    if parte.strip(): st.markdown(parte)
        except:
            st.write(txt) # Fallback se o regex falhar

    # Download
    docx = construir_docx_final(
        st.session_state['res_texto'], 
        aluno['nome'], 
        materia, 
        st.session_state['res_imgs'], 
        st.session_state.get('res_dalle'),
        st.session_state.get('tipo_selecionado', 'Atividade')
    )
    
    if docx:
        st.download_button(
            label="📥 BAIXAR ATIVIDADE (WORD)",
            data=docx,
            file_name=f"Atividade_{aluno['nome']}.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            type="primary",
            use_container_width=True
        )
    else:
        st.error("Erro ao gerar arquivo Word. Tente novamente.")
