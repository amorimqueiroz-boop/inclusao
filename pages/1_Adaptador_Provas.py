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
st.set_page_config(page_title="Adaptador 360º | Final", page_icon="🧩", layout="wide")

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
    div[data-testid="column"] .stButton button[kind="primary"] { border-radius: 12px !important; height: 50px; width: 100%; background-color: #FF6B6B !important; color: white !important; font-weight: 800 !important; }
    div[data-testid="column"] .stButton button[kind="secondary"] { border-radius: 12px !important; height: 50px; width: 100%; background-color: white !important; color: #718096 !important; border: 2px solid #CBD5E0 !important; }
    </style>
""", unsafe_allow_html=True)

# --- 4. FUNÇÕES DE ARQUIVO ---
def extrair_dados_docx(uploaded_file):
    uploaded_file.seek(0); texto = ""; imagens = []
    try:
        doc = Document(uploaded_file); texto = "\n".join([p.text for p in doc.paragraphs if p.text.strip() != ""])
        uploaded_file.seek(0)
        with zipfile.ZipFile(uploaded_file) as z:
            media_files = [f for f in z.namelist() if f.startswith('word/media/') and f.endswith(('.png','.jpg','.jpeg'))]
            media_files.sort(key=lambda f: int(re.search(r'image(\d+)', f).group(1)) if re.search(r'image(\d+)', f) else 0)
            for m in media_files: imagens.append(z.read(m))
    except: pass
    return texto, imagens

def baixar_imagem_url(url):
    try:
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200: return BytesIO(resp.content)
    except: pass
    return None

def construir_docx_final(texto_ia, aluno, materia, lista_imgs, img_dalle_url, tipo_atv):
    doc = Document(); style = doc.styles['Normal']; style.font.name = 'Arial'; style.font.size = Pt(12)
    doc.add_heading(f'{tipo_atv.upper()} ADAPTADA - {materia.upper()}', 0).alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_paragraph(f"Estudante: {aluno['nome']}").alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_paragraph("_"*50)

    if img_dalle_url:
        img_io = baixar_imagem_url(img_dalle_url)
        if img_io:
            doc.add_heading('Contexto Visual', level=3)
            doc.add_picture(img_io, width=Inches(4.5)); doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
            doc.add_paragraph("")

    doc.add_heading('Questões', level=2)
    partes = re.split(r'(\[\[IMG_\d+\]\])', texto_ia)
    for parte in partes:
        if "[[IMG_" in parte:
            try:
                idx = 0 
                if 0 <= idx < len(lista_imgs):
                    doc.add_picture(BytesIO(lista_imgs[idx]), width=Inches(5.5))
                    doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
                    doc.add_paragraph("")
            except: pass
        elif parte.strip():
            clean_text = parte.replace("Utilize a tag", "").strip()
            if clean_text: doc.add_paragraph(clean_text)
            
    buffer = BytesIO(); doc.save(buffer); buffer.seek(0)
    return buffer

# --- 5. IA (LÓGICA HÍBRIDA + POSICIONAMENTO) ---
def gerar_dalle(api_key, tema, aluno):
    client = OpenAI(api_key=api_key)
    prompt = f"Educational illustration about '{tema}'. Simple, clear, white background. {aluno.get('hiperfoco','')} style. No text."
    try:
        resp = client.images.generate(model="dall-e-3", prompt=prompt, size="1024x1024", quality="standard", n=1)
        return resp.data[0].url, None
    except Exception as e: return None, str(e)

def adaptar_hibrido(api_key, aluno, conteudo_visual_completo, tipo, materia, tema, tipo_atv, remover_respostas):
    client = OpenAI(api_key=api_key)
    
    # --- PROMPT REFINADO PARA POSICIONAMENTO ---
    instrucao_imgs = """
    A imagem original contém um mapa/figura. Eu já recortei essa figura.
    
    REGRA CRÍTICA DE POSICIONAMENTO:
    Você deve inserir a tag [[IMG_1]] ANTES das perguntas começarem.
    
    Ordem Correta:
    1. Título ou Enunciado (Ex: "Observe a imagem:")
    2. [[IMG_1]] (Aqui entra a imagem)
    3. Perguntas (a, b, c...)
    
    NUNCA coloque a tag [[IMG_1]] no final do texto. Ela é o suporte visual da questão.
    """
    
    instrucao_prof = "REMOVA TODAS AS RESPOSTAS (azul/rosa/itálico). Mantenha apenas perguntas." if remover_respostas else ""
    
    diretrizes_pei = ""
    if 'ia_sugestao' in aluno:
        diretrizes_pei = f"\nDIRETRIZES DO PEI:\n{aluno['ia_sugestao'][:2000]}..."

    prompt_sys = f"Você é um Especialista em Adaptação. {instrucao_prof}. {instrucao_imgs}. {diretrizes_pei}"
    prompt_user = f"CONTEXTO: {materia} | {tema} | {tipo_atv}\nCONTEÚDO PARA ADAPTAR:"
    
    msgs = [{"role": "system", "content": prompt_sys}, {"role": "user", "content": []}]
    
    if tipo == "imagem":
        b64 = base64.b64encode(conteudo_visual_completo).decode('utf-8')
        msgs[1]["content"].append({"type": "text", "text": prompt_user})
        msgs[1]["content"].append({"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}})
    else:
        msgs[1]["content"].append({"type": "text", "text": prompt_user + str(conteudo_visual_completo)})

    try:
        resp = client.chat.completions.create(model="gpt-4o-mini", messages=msgs, temperature=0.3, max_tokens=4000)
        return resp.choices[0].message.content, None
    except Exception as e: return None, str(e)

# --- 6. INTERFACE ---
with st.sidebar:
    if 'OPENAI_API_KEY' in st.secrets: api_key = st.secrets['OPENAI_API_KEY']; st.success("✅ Conectado")
    else: api_key = st.text_input("Chave OpenAI:", type="password")
    st.markdown("---")
    st.info("✂️ Recorte a imagem para limpar. O texto original será lido automaticamente.")

st.markdown("""<div class="header-clean"><div style="font-size:3rem;">🧩</div><div><p style="margin:0;color:#004E92;font-size:1.5rem;font-weight:800;">Adaptador V6.6: Final</p></div></div>""", unsafe_allow_html=True)

if not st.session_state.banco_estudantes:
    st.warning("⚠️ Nenhum aluno no banco. Vá em 'PEI 360º' e salve um aluno primeiro.")
    st.stop()

lista = [a['nome'] for a in st.session_state.banco_estudantes]
nome_aluno = st.selectbox("📂 Selecione o Estudante:", lista)
aluno = next(a for a in st.session_state.banco_estudantes if a['nome'] == nome_aluno)

with st.expander(f"ℹ️ Perfil de {aluno['nome']}"):
    st.write(f"**Hiperfoco:** {aluno.get('hiperfoco', 'Não informado')}")
    st.write(f"**Diagnóstico:** {aluno.get('diagnostico', 'Não informado')}")

c1, c2, c3 = st.columns(3)
materia = c1.selectbox("Matéria", ["Matemática", "Português", "Ciências", "História", "Geografia", "Inglês", "Artes"])
tema = c2.text_input("Tema", placeholder="Ex: Frações")
tipo_atv = c3.selectbox("Tipo de Atividade", [
    "Prova / Avaliação", 
    "Tarefa de Casa", 
    "Atividade de Sala", 
    "Trabalho em Grupo", 
    "Atividade Lúdica",
    "Resumo / Esquema"
])

# UPLOAD
arquivo = st.file_uploader("Arquivo (FOTO ou DOCX)", type=["png","jpg","jpeg","docx"])

img_original_bytes = None 
lista_recortes_final = [] 
tipo_arq = None

if arquivo:
    if "image" in arquivo.type:
        tipo_arq = "imagem"
        st.markdown("<div class='crop-instruction'>✂️ <b>TESOURA DIGITAL:</b> Recorte APENAS a figura/mapa. O sistema lerá o texto da página inteira automaticamente.</div>", unsafe_allow_html=True)
        
        img_pil = Image.open(arquivo)
        
        # Converte para RGB (blindagem contra erro OSError)
        if img_pil.mode in ("RGBA", "P"): img_pil = img_pil.convert("RGB")
            
        # Salva original para IA
        buf_full = BytesIO(); img_pil.save(buf_full, format="JPEG"); 
        img_original_bytes = buf_full.getvalue()
        
        # Recorte
        img_pil.thumbnail((1200, 1200)) 
        cropped_img = st_cropper(img_pil, realtime_update=True, box_color='#FF0000', aspect_ratio=None)
        st.caption("Recorte Final:")
        st.image(cropped_img, width=250)
        
        buf_crop = BytesIO(); cropped_img.save(buf_crop, format="JPEG"); 
        lista_recortes_final = [buf_crop.getvalue()]
        
    elif "word" in arquivo.type:
        tipo_arq = "docx"
        txt, imgs = extrair_dados_docx(arquivo)
        img_original_bytes = txt 
        lista_recortes_final = imgs
        st.success("DOCX carregado.")

st.markdown("<div class='action-bar'>", unsafe_allow_html=True)
c_opt, c_act = st.columns([1, 1])
with c_opt:
    modo_prof = st.checkbox("🕵️ Modo Professor (Remover Respostas)", value=True)
    usar_dalle = st.toggle("🎨 Gerar Capa IA", value=True)
with c_act:
    c_gerar, c_limpar = st.columns([2, 1])
    btn_gerar = c_gerar.button("✨ GERAR ATIVIDADE", type="primary", use_container_width=True)
    if c_limpar.button("🗑️ Nova", type="secondary", use_container_width=True):
        st.session_state.pop('res_texto', None); st.rerun()
st.markdown("</div>", unsafe_allow_html=True)

if btn_gerar:
    if not materia or not tema or not arquivo: st.warning("Preencha tudo.")
    else:
        with st.spinner("IA diagramando a atividade..."):
            # Envia a IMAGEM ORIGINAL para leitura, mas usa o RECORTE no final
            texto_adaptado, err = adaptar_hibrido(api_key, aluno, img_original_bytes, tipo_arq, materia, tema, tipo_atv, modo_prof)
            
            img_dalle = None
            if usar_dalle and not err: img_dalle, _ = gerar_dalle(api_key, tema, aluno)
            
            if not err:
                st.session_state['res_texto'] = texto_adaptado
                st.session_state['res_imgs'] = lista_recortes_final
                st.session_state['res_dalle'] = img_dalle
                st.rerun()
            else: st.error(f"Erro: {err}")

if 'res_texto' in st.session_state:
    st.markdown("---")
    st.subheader("👁️ Resultado Final")
    with st.container(border=True):
        if st.session_state.get('res_dalle'): st.image(st.session_state['res_dalle'], width=200, caption="Capa IA")
        txt = st.session_state['res_texto']
        partes = re.split(r'(\[\[IMG_\d+\]\])', txt)
        for parte in partes:
            if "[[IMG_" in parte:
                if st.session_state['res_imgs']: st.image(st.session_state['res_imgs'][0], width=300, caption="Seu Recorte")
            else:
                if parte.strip(): st.markdown(parte)

    docx = construir_docx_final(st.session_state['res_texto'], aluno, materia, st.session_state['res_imgs'], st.session_state.get('res_dalle'), tipo_atv)
    st.download_button("📥 BAIXAR WORD", docx, f"Atividade_{aluno['nome']}.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document", type="primary", use_container_width=True)
