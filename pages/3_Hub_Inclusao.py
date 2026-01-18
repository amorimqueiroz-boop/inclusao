import streamlit as st
import os
import requests
import json
import re
import base64
from datetime import date, datetime
from io import BytesIO
from PIL import Image
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Pt, Inches
from pypdf import PdfReader
from fpdf import FPDF
from openai import OpenAI
from streamlit_cropper import st_cropper

st.set_page_config(page_title="Omnisfera | Hub", page_icon="🚀", layout="wide")
SHEET_DB_URL = "https://sheetdb.io/api/v1/d8098eian87x9"

def carregar_banco_alunos_nuvem():
    try:
        response = requests.get(f"{SHEET_DB_URL}?sheet=Banco_Alunos")
        data = response.json()
        if isinstance(data, list):
            lista_processada = []
            for item in data:
                if 'dados_completos' in item:
                    try:
                        lista_processada.append(json.loads(item['dados_completos']))
                    except: pass
            return lista_processada
        return []
    except: return []

def salvar_log_producao(aluno, componente, tema, tipo, detalhes):
    if not componente or componente.strip() == "": componente = "Educação Infantil (Campos de Exp.)"
    payload = {
        "data_hora": datetime.now().strftime("%d/%m/%Y %H:%M"), "aluno_nome": aluno,
        "componente": componente, "tema": tema, "tipo_atividade": tipo, "detalhes": detalhes
    }
    try: requests.post(f"{SHEET_DB_URL}?sheet=Logs_Producao", json={"data": [payload]}, headers={"Content-Type": "application/json"}); return True
    except: return False

try: IS_TEST_ENV = st.secrets.get("ENV") == "TESTE"
except: IS_TEST_ENV = False

def get_base64_image(image_path):
    if os.path.exists(image_path):
        with open(image_path, "rb") as f: return base64.b64encode(f.read()).decode()
    return ""

src_logo = f"data:image/png;base64,{get_base64_image('omni_icone.png')}"
card_bg = "rgba(255, 220, 50, 0.95)" if IS_TEST_ENV else "rgba(255, 255, 255, 0.85)"
card_border = "rgba(200, 160, 0, 0.5)" if IS_TEST_ENV else "rgba(255, 255, 255, 0.6)"

st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800&display=swap');
    html, body, [class*="css"] {{ font-family: 'Nunito', sans-serif; color: #2D3748; }}
    .omni-badge {{ position: fixed; top: 15px; right: 15px; background: {card_bg}; border: 1px solid {card_border}; backdrop-filter: blur(8px); padding: 4px 30px; min-width: 260px; border-radius: 20px; box-shadow: 0 4px 15px rgba(0,0,0,0.08); z-index: 999990; display: flex; align-items: center; gap: 10px; pointer-events: none; }}
    .omni-text {{ font-family: 'Nunito'; font-weight: 800; font-size: 0.9rem; color: #2D3748; letter-spacing: 1px; }}
    .omni-logo-spin {{ height: 26px; width: 26px; animation: spin-slow 10s linear infinite; }}
    @keyframes spin-slow {{ from {{ transform: rotate(0deg); }} to {{ transform: rotate(360deg); }} }}
    .header-hub {{ background: white; padding: 20px 30px; border-radius: 12px; border-left: 6px solid #3182CE; box-shadow: 0 2px 4px rgba(0,0,0,0.05); margin-bottom: 20px; display: flex; align-items: center; gap: 25px; }}
    .student-header {{ background-color: #EBF8FF; border: 1px solid #BEE3F8; border-radius: 12px; padding: 15px 25px; margin-bottom: 25px; display: flex; justify-content: space-between; align-items: center; }}
    .student-label {{ font-size: 0.85rem; color: #718096; font-weight: 700; text-transform: uppercase; }}
    .student-value {{ font-size: 1.1rem; color: #2C5282; font-weight: 800; }}
    .analise-box {{ background-color: #F0FFF4; border: 1px solid #C6F6D5; border-radius: 8px; padding: 20px; margin-bottom: 20px; color: #22543D; }}
    .validado-box {{ background-color: #C6F6D5; color: #22543D; padding: 15px; border-radius: 8px; text-align: center; font-weight: bold; margin-top: 15px; border: 1px solid #276749; }}
    .pedagogia-box {{ background-color: #F7FAFC; border-left: 4px solid #3182CE; padding: 15px; border-radius: 0 8px 8px 0; margin-bottom: 20px; font-size: 0.9rem; color: #4A5568; }}
    .pedagogia-title {{ color: #2C5282; font-weight: 700; margin-bottom: 5px; }}
    div[data-testid="column"] .stButton button[kind="primary"] {{ border-radius: 10px !important; height: 50px; width: 100%; background-color: #3182CE !important; color: white !important; font-weight: 800 !important; border: none; }}
    div[data-testid="column"] .stButton button[kind="primary"]:hover {{ background-color: #2B6CB0 !important; }}
</style>
<div class="omni-badge"><img src="{src_logo}" class="omni-logo-spin"><span class="omni-text">OMNISFERA</span></div>
""", unsafe_allow_html=True)

def verificar_acesso():
    if "autenticado" not in st.session_state or not st.session_state["autenticado"]:
        st.error("🔒 Acesso Negado."); st.stop()
verificar_acesso()

# --- SIDEBAR ---
with st.sidebar:
    if 'OPENAI_API_KEY' in st.secrets: api_key = st.secrets['OPENAI_API_KEY']; st.success("✅ OpenAI OK")
    else: api_key = st.text_input("Chave OpenAI:", type="password")
    if 'UNSPLASH_ACCESS_KEY' in st.secrets: unsplash_key = st.secrets['UNSPLASH_ACCESS_KEY']
    else: unsplash_key = st.text_input("Chave Unsplash:", type="password")
    st.markdown("---")
    if st.button("🔄 Atualizar Lista de Alunos"): st.session_state.banco_estudantes = carregar_banco_alunos_nuvem()
    
    if not st.session_state.get('banco_estudantes'):
        # Tenta carregar se estiver vazio na primeira execução
        st.session_state.banco_estudantes = carregar_banco_alunos_nuvem()

    if not st.session_state.banco_estudantes:
        st.warning("Sem alunos. Sincronize no módulo PEI.")
        st.stop()
    else:
        lista = [a['nome'] for a in st.session_state.banco_estudantes]
        nome_aluno = st.selectbox("📂 Selecione o Estudante:", lista)
        aluno = next(a for a in st.session_state.banco_estudantes if a['nome'] == nome_aluno)
    st.markdown("---")
    if st.button("🏠 Home"): st.switch_page("Home.py")

# --- HEADER HUB ---
img_hub_html = f'<img src="data:image/png;base64,{get_base64_image("hub.png")}" width="220">' 
st.markdown(f"""<div class="header-hub"><div>{img_hub_html}</div><div style="flex-grow: 1; text-align: center;"><p style="color:#2C5282; font-size: 1.3rem; font-weight: 700;">Adaptação de Materiais & Criação</p></div></div>""", unsafe_allow_html=True)

st.markdown(f"""<div class="student-header"><div class="student-info-item"><div class="student-label">Nome</div><div class="student-value">{aluno.get('nome')}</div></div><div class="student-info-item"><div class="student-label">Série</div><div class="student-value">{aluno.get('serie', '-')}</div></div><div class="student-info-item"><div class="student-label">Hiperfoco</div><div class="student-value">{aluno.get('hiperfoco', '-')}</div></div></div>""", unsafe_allow_html=True)

# --- FUNÇÕES UTILITÁRIAS E IA ---
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
        img = Image.open(BytesIO(image_bytes)).convert("RGB"); out = BytesIO(); img.save(out, format="JPEG", quality=90); return out.getvalue()
    except: return None

def buscar_imagem_unsplash(query, access_key):
    if not access_key: return None
    try:
        resp = requests.get(f"https://api.unsplash.com/search/photos?query={query}&per_page=1&client_id={access_key}&lang=pt", timeout=5)
        data = resp.json()
        if data.get('results'): return data['results'][0]['urls']['regular']
    except: pass
    return None

def criar_pdf_generico(texto):
    pdf = FPDF(); pdf.add_page(); pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, texto.encode('latin-1', 'replace').decode('latin-1'))
    return pdf.output(dest='S').encode('latin-1')

def construir_docx_final(texto_ia, aluno, materia, mapa_imgs, tipo_atv):
    doc = Document(); doc.add_heading(f'{tipo_atv.upper()} ADAPTADA - {materia.upper()}', 0).alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_paragraph(f"Estudante: {aluno['nome']}").alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_paragraph("_"*50)
    for linha in texto_ia.split('\n'):
        if re.search(r'\[\[IMG.*?\d+\]\]', linha):
            num = int(re.search(r'(\d+)', linha).group(1))
            if mapa_imgs.get(num):
                try: doc.add_paragraph().add_run().add_picture(BytesIO(mapa_imgs[num]), width=Inches(4.5))
                except: pass
        elif linha.strip(): doc.add_paragraph(linha.strip())
    buffer = BytesIO(); doc.save(buffer); buffer.seek(0); return buffer

def criar_docx_simples(texto, titulo):
    doc = Document(); doc.add_heading(titulo, 0)
    for p in texto.split('\n'):
        if p.strip(): doc.add_paragraph(p.strip())
    buffer = BytesIO(); doc.save(buffer); buffer.seek(0); return buffer

def gerar_imagem_inteligente(api_key, prompt, unsplash_key=None, prioridade="IA"):
    client = OpenAI(api_key=api_key)
    if prioridade == "BANCO" and unsplash_key:
        url = buscar_imagem_unsplash(prompt, unsplash_key)
        if url: return url
    try:
        resp = client.images.generate(model="dall-e-3", prompt=f"Educational illustration, no text. {prompt}", size="1024x1024", n=1)
        return resp.data[0].url
    except: return None

def gerar_pictograma_caa(api_key, conceito):
    try:
        client = OpenAI(api_key=api_key)
        resp = client.images.generate(model="dall-e-3", prompt=f"AAC Symbol for '{conceito}'. Flat vector icon, white background, black outline. NO TEXT.", size="1024x1024", n=1)
        return resp.data[0].url
    except: return None

def adaptar_conteudo_docx(api_key, aluno, texto, materia, tema, tipo_atv, questoes_mapeadas, modo_profundo=False):
    client = OpenAI(api_key=api_key)
    prompt = f"Especialista em DUA. Adapte para: {aluno.get('ia_sugestao','')[:800]}. Hiperfoco: {aluno.get('hiperfoco')}. Imagens nas questões {questoes_mapeadas}. SAÍDA: [ANÁLISE PEDAGÓGICA]... ---DIVISOR--- [ATIVIDADE]... Texto: {texto}"
    try:
        resp = client.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "user", "content": prompt}], temperature=0.7)
        parts = resp.choices[0].message.content.split("---DIVISOR---")
        return parts[0].replace("[ANÁLISE PEDAGÓGICA]", "").strip(), parts[1].replace("[ATIVIDADE]", "").strip()
    except: return "Erro", ""

def adaptar_conteudo_imagem(api_key, aluno, img_bytes, materia, tema, tipo):
    client = OpenAI(api_key=api_key); b64 = base64.b64encode(img_bytes).decode('utf-8')
    prompt = f"Transcreva e adapte DUA. Aluno: {aluno.get('ia_sugestao','')[:500]}. Hiperfoco: {aluno.get('hiperfoco')}. SAÍDA: [ANÁLISE PEDAGÓGICA]... ---DIVISOR--- [ATIVIDADE]..."
    try:
        resp = client.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "user", "content": [{"type": "text", "text": prompt}, {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}}]}])
        parts = resp.choices[0].message.content.split("---DIVISOR---")
        return parts[0].replace("[ANÁLISE PEDAGÓGICA]", "").strip(), parts[1].replace("[ATIVIDADE]", "").strip()
    except: return "Erro", ""

def criar_profissional(api_key, aluno, mat, obj, qtd, tipo, imgs, verbos=None):
    client = OpenAI(api_key=api_key)
    prompt = f"Crie atividade {mat}-{obj}. Qtd: {qtd}. Tipo: {tipo}. Imagens: {imgs}. Bloom: {verbos}. Hiperfoco: {aluno.get('hiperfoco')}. SAÍDA: [ANÁLISE PEDAGÓGICA]... ---DIVISOR--- [ATIVIDADE]..."
    try:
        resp = client.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "user", "content": prompt}], temperature=0.7)
        parts = resp.choices[0].message.content.split("---DIVISOR---")
        return parts[0].replace("[ANÁLISE PEDAGÓGICA]", "").strip(), parts[1].replace("[ATIVIDADE]", "").strip()
    except: return "Erro", ""

def gerar_experiencia_ei_bncc(api_key, aluno, campo, obj, feedback=""):
    client = OpenAI(api_key=api_key)
    prompt = f"Crie experiência lúdica EI (BNCC). Campo: {campo}. Obj: {obj}. Aluno: {aluno['nome']}, Hiperfoco: {aluno.get('hiperfoco')}. {feedback}"
    try:
        return client.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "user", "content": prompt}]).choices[0].message.content
    except: return "Erro"

def gerar_generico_ia(api_key, prompt):
    try:
        return OpenAI(api_key=api_key).chat.completions.create(model="gpt-4o-mini", messages=[{"role": "user", "content": prompt}]).choices[0].message.content
    except: return "Erro"

# --- LÓGICA DAS ABAS ---
serie_aluno = aluno.get('serie', '').lower()
is_ei = "infantil" in serie_aluno or "creche" in serie_aluno or "pré" in serie_aluno

if 'res_scene_url' not in st.session_state: st.session_state.res_scene_url = None
if 'valid_scene' not in st.session_state: st.session_state.valid_scene = False
if 'res_caa_url' not in st.session_state: st.session_state.res_caa_url = None
if 'valid_caa' not in st.session_state: st.session_state.valid_caa = False

if is_ei:
    tabs = st.tabs(["🧸 Criar Experiência", "🎨 Estúdio Visual", "📝 Rotina", "🤝 Inclusão"])
    
    with tabs[0]: # Experiência
        st.markdown("<div class='pedagogia-box'>Pedagogia do Brincar (BNCC)</div>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        campo = c1.selectbox("Campo de Exp.", ["O eu, o outro e o nós", "Corpo, gestos e movimentos", "Traços, sons, cores e formas", "Escuta, fala, pensamento", "Espaços, tempos, quantidades"])
        obj = c2.text_input("Objetivo:", placeholder="Ex: Cores")
        if 'res_ei' not in st.session_state: st.session_state.res_ei = None
        if st.button("✨ GERAR", type="primary"):
            st.session_state.res_ei = gerar_experiencia_ei_bncc(api_key, aluno, campo, obj)
            st.session_state.valid_ei = False
        if st.session_state.res_ei:
            st.markdown(st.session_state.res_ei)
            if not st.session_state.get('valid_ei'):
                if st.button("✅ Validar Experiência"):
                    st.session_state.valid_ei = True
                    salvar_log_producao(aluno['nome'], "Educação Infantil", campo, "Experiência Lúdica", f"Obj: {obj}")
                    st.success("Registrado!"); st.rerun()
            else: st.success("Validado!")

    with tabs[1]: # Visual EI
        c_sc, c_caa = st.columns(2)
        with c_sc:
            desc = st.text_area("Cena:", key="vdm_ei")
            if st.button("🎨 Gerar Cena", key="btn_c_ei"):
                st.session_state.res_scene_url = gerar_imagem_inteligente(api_key, desc, prioridade="IA")
                st.session_state.valid_scene = False
            if st.session_state.res_scene_url:
                st.image(st.session_state.res_scene_url)
                if not st.session_state.valid_scene:
                    if st.button("✅ Validar Cena", key="val_c_ei"):
                        st.session_state.valid_scene = True
                        salvar_log_producao(aluno['nome'], "Recurso Visual", "Cena", "Ilustração", desc)
                        st.success("Registrado!"); st.rerun()

    with tabs[2]: # Rotina EI
        rotina = st.text_area("Rotina Atual:", height=150)
        if st.button("📝 Adaptar Rotina"):
            st.session_state.res_rot = gerar_generico_ia(api_key, f"Adapte rotina EI para {aluno['nome']}: {rotina}")
            st.session_state.valid_rot = False
        if st.session_state.get('res_rot'):
            st.markdown(st.session_state.res_rot)
            if not st.session_state.get('valid_rot'):
                if st.button("✅ Validar Rotina"):
                    st.session_state.valid_rot = True
                    salvar_log_producao(aluno['nome'], "Educação Infantil", "Rotina", "Adaptação", "Rotina Visual")
                    st.success("Registrado!"); st.rerun()

    with tabs[3]: # Inclusão
        tema = st.text_input("Tema da brincadeira:")
        if st.button("🤝 Gerar Dinâmica"):
            st.session_state.res_din = gerar_generico_ia(api_key, f"Dinâmica inclusiva EI para {aluno['nome']}. Tema: {tema}")
            st.session_state.valid_din = False
        if st.session_state.get('res_din'):
            st.markdown(st.session_state.res_din)
            if not st.session_state.get('valid_din'):
                if st.button("✅ Validar Dinâmica"):
                    st.session_state.valid_din = True
                    salvar_log_producao(aluno['nome'], "Educação Infantil", tema, "Dinâmica", "Socialização")
                    st.success("Registrado!"); st.rerun()

else:
    # === MODO FUNDAMENTAL/MÉDIO ===
    tabs = st.tabs(["📄 Adaptar Prova", "✂️ Adaptar Atividade", "✨ Criar do Zero", "🎨 Estúdio Visual", "📝 Roteiros"])
    
    with tabs[0]: # DOCX
        c1, c2, c3 = st.columns(3)
        mat_d = c1.selectbox("Matéria", ["Matemática", "Português", "Ciências", "História", "Geografia"], key="md")
        tema_d = c2.text_input("Tema", key="td")
        tipo_d = c3.selectbox("Tipo", ["Prova", "Tarefa"], key="tpd")
        arq_d = st.file_uploader("DOCX", type=["docx"], key="fd")
        if arq_d and arq_d.file_id != st.session_state.get('last_d'):
            st.session_state.last_d = arq_d.file_id
            st.session_state.docx_txt, st.session_state.docx_imgs = extrair_dados_docx(arq_d)
        
        map_d = {}; qs_d = []
        if st.session_state.get('docx_imgs'):
            cols = st.columns(3)
            for i, img in enumerate(st.session_state.docx_imgs):
                with cols[i%3]:
                    st.image(img, width=80)
                    q = st.number_input(f"Q#", 0, 50, key=f"q_{i}")
                    if q > 0: map_d[int(q)] = img; qs_d.append(int(q))
        
        if st.button("🚀 ADAPTAR", type="primary", key="bd"):
            if st.session_state.get('docx_txt'):
                rac, txt = adaptar_conteudo_docx(api_key, aluno, st.session_state.docx_txt, mat_d, tema_d, tipo_d, qs_d)
                st.session_state['res_docx'] = {'rac': rac, 'txt': txt, 'map': map_d, 'valid': False}
                st.rerun()
        
        if 'res_docx' in st.session_state:
            res = st.session_state['res_docx']
            st.markdown(f"<div class='analise-box'>{res['rac']}</div>", unsafe_allow_html=True)
            if not res['valid']:
                if st.button("✅ Validar Adaptação", key="vd"):
                    st.session_state['res_docx']['valid'] = True
                    salvar_log_producao(aluno['nome'], mat_d, tema_d, f"Adaptação {tipo_d}", "DOCX")
                    st.success("Registrado!"); st.rerun()
            else:
                docx = construir_docx_final(res['txt'], aluno, mat_d, res['map'], tipo_d)
                st.download_button("📥 Baixar DOCX", docx, "Adaptada.docx", "primary")

    with tabs[1]: # OCR/Imagem
        c1, c2, c3 = st.columns(3)
        mat_i = c1.selectbox("Matéria", ["Matemática", "Português", "Ciências"], key="mi")
        tema_i = c2.text_input("Tema", key="ti")
        tipo_i = c3.selectbox("Tipo", ["Atividade", "Tarefa"], key="tpi")
        arq_i = st.file_uploader("Foto", type=["png","jpg"], key="fi")
        if arq_i:
            img = Image.open(arq_i); st.session_state.img_raw = sanitizar_imagem(arq_i.getvalue())
            st_cropper(img, realtime_update=True, box_color='#FF0000', key="crop")
            
        if st.button("🚀 ADAPTAR FOTO", type="primary", key="bi"):
            if st.session_state.get('img_raw'):
                rac, txt = adaptar_conteudo_imagem(api_key, aluno, st.session_state.img_raw, mat_i, tema_i, tipo_i)
                st.session_state['res_img'] = {'rac': rac, 'txt': txt, 'valid': False}
                st.rerun()
        
        if 'res_img' in st.session_state:
            res = st.session_state['res_img']
            st.markdown(f"<div class='analise-box'>{res['rac']}</div>", unsafe_allow_html=True)
            if not res['valid']:
                if st.button("✅ Validar", key="vi"):
                    st.session_state['res_img']['valid'] = True
                    salvar_log_producao(aluno['nome'], mat_i, tema_i, f"Adaptação Imagem ({tipo_i})", "OCR")
                    st.success("Registrado!"); st.rerun()
            else:
                st.download_button("📥 Baixar DOCX", criar_docx_simples(res['txt'], "Atividade"), "Atividade.docx")

    with tabs[2]: # Criar Zero
        c1, c2 = st.columns(2); mat_c = c1.selectbox("Matéria", ["Matemática", "Português"], key="mc"); obj_c = c2.text_input("Assunto", key="oc")
        if st.button("✨ CRIAR", type="primary", key="bc"):
            rac, txt = criar_profissional(api_key, aluno, mat_c, obj_c, 5, "Objetiva", 0)
            st.session_state['res_create'] = {'rac': rac, 'txt': txt, 'valid': False}
            st.rerun()
        
        if 'res_create' in st.session_state:
            res = st.session_state['res_create']
            st.markdown(f"<div class='analise-box'>{res['rac']}</div>", unsafe_allow_html=True)
            if not res['valid']:
                if st.button("✅ Validar Criação", key="vc"):
                    st.session_state['res_create']['valid'] = True
                    salvar_log_producao(aluno['nome'], mat_c, obj_c, "Criação Inédita", "IA")
                    st.success("Registrado!"); st.rerun()
            else:
                st.download_button("📥 Baixar DOCX", criar_docx_simples(res['txt'], "Atividade"), "Criada.docx")

    with tabs[3]: # Visual Fundamental
        desc = st.text_area("Imagem:"); palavra = st.text_input("Símbolo CAA:")
        if st.button("Gerar Imagem"): st.image(gerar_imagem_inteligente(api_key, desc))
        if st.button("Gerar Símbolo"): st.image(gerar_pictograma_caa(api_key, palavra))

    with tabs[4]: # Roteiros
        tema_rot = st.text_input("Tema da Aula:"); mat_rot = st.selectbox("Matéria", ["Matemática", "Português"], key="mr")
        if st.button("Gerar Roteiro"):
            res = gerar_generico_ia(api_key, f"Roteiro de aula {mat_rot} - {tema_rot} para {aluno['nome']}")
            st.markdown(res)
