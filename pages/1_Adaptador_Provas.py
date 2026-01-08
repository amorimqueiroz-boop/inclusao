import streamlit as st
from openai import OpenAI
from io import BytesIO
from docx import Document
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from PIL import Image
from streamlit_cropper import st_cropper
import re
import requests
import json
import base64

# --- 1. CONFIGURAÇÃO ---
st.set_page_config(page_title="Adaptador 360º | V9.4", page_icon="🧩", layout="wide")

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
    .student-header { background-color: #EBF8FF; border: 1px solid #BEE3F8; border-radius: 12px; padding: 15px 25px; margin-bottom: 25px; display: flex; justify-content: space-between; align-items: center; }
    .student-label { font-size: 0.85rem; color: #718096; font-weight: 700; text-transform: uppercase; }
    .student-value { font-size: 1.1rem; color: #2C5282; font-weight: 800; }
    .crop-instruction { background: #EBF8FF; border-left: 4px solid #3182CE; padding: 15px; color: #2C5282; border-radius: 4px; margin-bottom: 10px; }
    
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] { border-radius: 4px; padding: 10px 20px; background-color: white; border: 1px solid #E2E8F0; }
    .stTabs [aria-selected="true"] { background-color: #3182CE !important; color: white !important; }

    div[data-testid="column"] .stButton button[kind="primary"] { border-radius: 12px !important; height: 50px; width: 100%; background-color: #FF6B6B !important; color: white !important; font-weight: 800 !important; }
    div[data-testid="column"] .stButton button[kind="secondary"] { border-radius: 12px !important; height: 50px; width: 100%; background-color: white !important; color: #718096 !important; border: 2px solid #CBD5E0 !important; }
    </style>
""", unsafe_allow_html=True)

# --- 4. FUNÇÕES DE ARQUIVO ---
def extrair_dados_docx(uploaded_file):
    uploaded_file.seek(0); imagens = []; texto = ""
    try:
        doc = Document(uploaded_file)
        texto = "\n".join([p.text for p in doc.paragraphs if p.text.strip() != ""])
        # Varre XML para pegar imagens na ordem correta
        for rel in doc.part.rels.values():
            if "image" in rel.target_ref:
                img_data = rel.target_part.blob
                # Filtro: ignora imagens muito pequenas (ícones)
                if len(img_data) > 2000: 
                    imagens.append(img_data)
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
    
    # Processa tags [[IMG_1]]
    partes = re.split(r'(\[\[IMG_\d+\]\])', texto_ia)
    
    for parte in partes:
        tag_match = re.search(r'\[\[IMG_(\d+)\]\]', parte)
        if tag_match:
            num = int(tag_match.group(1))
            # Busca imagem no mapa
            img_bytes = mapa_imgs.get(num)
            
            # Se não achar e for a única imagem (caso do recorte), usa ela
            if not img_bytes and len(mapa_imgs) == 1:
                img_bytes = list(mapa_imgs.values())[0]

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

# --- 5. INTELIGÊNCIA ARTIFICIAL ---
def gerar_dalle_prompt(api_key, prompt_text):
    client = OpenAI(api_key=api_key)
    try:
        resp = client.images.generate(model="dall-e-3", prompt=prompt_text + " Educational style, clear, autism-friendly, white background, no text.", size="1024x1024", quality="standard", n=1)
        return resp.data[0].url
    except: return None

def adaptar_conteudo(api_key, aluno, conteudo, tipo, materia, tema, tipo_atv, remover_resp, questoes_mapeadas):
    client = OpenAI(api_key=api_key)
    
    # Validação de Segurança
    if not conteudo: return "Erro: Conteúdo vazio.", ""

    lista_q = ", ".join([str(n) for n in questoes_mapeadas])
    
    prompt = f"""
    ADAPTADOR DE ATIVIDADE ESCOLAR.
    
    REGRA CRÍTICA DE IMAGENS (SANDUÍCHE):
    O professor indicou imagens para as questões: {lista_q}.
    ESTRUTURA OBRIGATÓRIA PARA CADA QUESTÃO COM IMAGEM:
    1. Texto do Enunciado.
    2. A tag [[IMG_número]] (COLADA ABAIXO DO ENUNCIADO).
    3. As Alternativas.
    
    NUNCA coloque a imagem no final. Ela é o meio do sanduíche.
    
    SAÍDA:
    [RACIONAL] (Resumo)
    ---DIVISOR---
    [ATIVIDADE] (Conteúdo limpo)
    
    PEI: {aluno.get('ia_sugestao', '')[:1000]}
    {"REMOVA RESPOSTAS." if remover_resp else ""}
    CONTEXTO: {materia} | {tema}
    CONTEÚDO ORIGINAL:
    """
    
    msgs = [{"role": "user", "content": []}]
    if tipo == "imagem":
        if isinstance(conteudo, bytes):
            b64 = base64.b64encode(conteudo).decode('utf-8')
            msgs[0]["content"].append({"type": "text", "text": prompt})
            msgs[0]["content"].append({"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}})
        else: return "Erro img", ""
    else:
        msgs[0]["content"].append({"type": "text", "text": prompt + "\n" + str(conteudo)})

    try:
        resp = client.chat.completions.create(model="gpt-4o-mini", messages=msgs, temperature=0.3)
        parts = resp.choices[0].message.content.split("---DIVISOR---")
        return (parts[0].strip(), parts[1].strip()) if len(parts)>1 else ("Adaptado.", resp.choices[0].message.content)
    except Exception as e: return str(e), ""

def criar_duas_opcoes(api_key, aluno, materia, objeto, qtd, tipo_q):
    client = OpenAI(api_key=api_key)
    hiperfoco = aluno.get('hiperfoco', 'Geral')
    
    prompt = f"""
    CRIE 2 VERSÕES DE ATIVIDADE ({materia} - {objeto}) PARA {aluno.get('serie')}.
    QTD: {qtd} questões ({tipo_q}).
    PEI: {aluno.get('ia_sugestao', '')[:1000]}
    
    --- OPÇÃO A: LÚDICA (Mergulho no {hiperfoco}) ---
    --- OPÇÃO B: ESTRUTURADA (Foco acadêmico) ---
    
    REGRAS:
    1. A cada 5 questões, coloque uma tag [[GEN_IMG: descrição]] onde couber imagem.
    
    SAÍDA:
    [RACIONAL]
    ---SPLIT_A---
    [CONTEUDO_A]
    ---SPLIT_B---
    [CONTEUDO_B]
    """
    try:
        resp = client.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "user", "content": prompt}], temperature=0.7)
        full = resp.choices[0].message.content
        try:
            racional = full.split("---SPLIT_A---")[0].replace("[RACIONAL]", "").strip()
            rest = full.split("---SPLIT_A---")[1]
            opt_a = rest.split("---SPLIT_B---")[0].strip()
            opt_b = rest.split("---SPLIT_B---")[1].strip()
            return racional, opt_a, opt_b
        except: return "Erro formato.", full, full
    except Exception as e: return str(e), "", ""

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
    if st.button("🗑️ Nova Sessão"):
        for k in list(st.session_state.keys()):
            if k not in ['banco_estudantes', 'OPENAI_API_KEY']: del st.session_state[k]
        st.rerun()

st.markdown("""<div class="header-clean"><div style="font-size:3rem;">🧩</div><div><p style="margin:0;color:#004E92;font-size:1.5rem;font-weight:800;">Adaptador V9.4: Recorte Sincronizado</p></div></div>""", unsafe_allow_html=True)

if not st.session_state.banco_estudantes:
    st.warning("⚠️ Cadastre um aluno no PEI 360º primeiro.")
    st.stop()

lista = [a['nome'] for a in st.session_state.banco_estudantes]
nome_aluno = st.selectbox("📂 Selecione o Estudante:", lista)
aluno = next(a for a in st.session_state.banco_estudantes if a['nome'] == nome_aluno)

st.markdown(f"""
    <div class="student-header">
        <div class="student-info-item"><div class="student-label">Nome</div><div class="student-value">{aluno.get('nome')}</div></div>
        <div class="student-info-item"><div class="student-label">Série</div><div class="student-value">{aluno.get('serie', '-')}</div></div>
        <div class="student-info-item"><div class="student-label">Hiperfoco</div><div class="student-value">{aluno.get('hiperfoco', '-')}</div></div>
    </div>
""", unsafe_allow_html=True)

tab_adapt, tab_create, tab_visual, tab_ctx = st.tabs(["📂 Adaptar Arquivo", "✨ Criar (Opções A/B)", "🎨 Estúdio Visual", "💡 Contextualizador"])

# 1. ADAPTAR
with tab_adapt:
    c1, c2, c3 = st.columns(3)
    materia = c1.selectbox("Matéria", ["Matemática", "Português", "Ciências", "História", "Geografia"], key="am")
    tema = c2.text_input("Tema Original", placeholder="Ex: Frações", key="at")
    tipo_atv = c3.selectbox("Tipo", ["Prova", "Tarefa", "Atividade"], key="atip")

    arquivo = st.file_uploader("Arquivo (FOTO ou DOCX)", type=["png","jpg","jpeg","docx"], key="af")
    
    # Variáveis de Estado
    if 'adapt_content' not in st.session_state: st.session_state.adapt_content = None 
    if 'adapt_type' not in st.session_state: st.session_state.adapt_type = None
    if 'adapt_imgs' not in st.session_state: st.session_state.adapt_imgs = []
    
    if arquivo:
        if arquivo.file_id != st.session_state.get('a_last_id'):
            st.session_state.a_last_id = arquivo.file_id
            st.session_state.adapt_imgs = []
            
            if "image" in arquivo.type:
                st.session_state.adapt_type = "imagem"
                # Carrega ORIGINAL para memória
                img = Image.open(arquivo).convert("RGB")
                buf = BytesIO(); img.save(buf, format="JPEG"); 
                st.session_state.adapt_content = buf.getvalue()
            
            elif "word" in arquivo.type:
                st.session_state.adapt_type = "docx"
                txt, imgs = extrair_dados_docx(arquivo)
                st.session_state.adapt_content = txt
                st.session_state.adapt_imgs = imgs
                st.success(f"DOCX: {len(imgs)} imagens encontradas.")

    # WIDGET DE RECORTE (Realtime = True, mas com Imagem Otimizada)
    cropped_pil_result = None
    if st.session_state.adapt_type == "imagem" and st.session_state.adapt_content:
        st.markdown("<div class='crop-instruction'>✂️ <b>TESOURA DIGITAL:</b> Ajuste a caixa vermelha. O que você vê é o que a IA vai ler.</div>", unsafe_allow_html=True)
        img_original = Image.open(BytesIO(st.session_state.adapt_content))
        # OTIMIZAÇÃO CRÍTICA: Reduz para 800px para o cropper fluir sem travar
        img_original.thumbnail((800, 800))
        
        # Realtime TRUE: Atualização visual imediata
        cropped_pil_result = st_cropper(img_original, realtime_update=True, box_color='#FF0000', aspect_ratio=None, key="cropper_v9")
        
        st.caption("Prévia do Recorte (Isto será enviado):")
        if cropped_pil_result:
            st.image(cropped_pil_result, width=200)

    # MAPEAMENTO (DOCX)
    adapt_map = {}
    adapt_qs = []
    if st.session_state.adapt_imgs and st.session_state.adapt_type == "docx":
        st.info("Mapeamento: Digite o número da questão para cada imagem (0 para ignorar).")
        cols = st.columns(3)
        for i, img in enumerate(st.session_state.adapt_imgs):
            with cols[i % 3]:
                st.image(img, width=80)
                q = st.number_input(f"Q:", 0, 50, key=f"qmap_{i}")
                if q > 0: adapt_map[int(q)] = img; adapt_qs.append(int(q))

    c_opt, c_act = st.columns([1, 1])
    with c_opt:
        modo_prof = st.checkbox("Remover Respostas", value=True, key="mprof") if st.session_state.adapt_type == "imagem" else False
    
    with c_act:
        if st.button("🚀 GERAR ADAPTAÇÃO", type="primary", key="btn_adapt"):
            
            # CAPTURA FINAL DO CONTEÚDO
            final_content = st.session_state.adapt_content
            
            if st.session_state.adapt_type == "imagem":
                if cropped_pil_result:
                    # Converte o resultado do cropper para bytes
                    buf_c = BytesIO()
                    cropped_pil_result.save(buf_c, format="JPEG")
                    final_content = buf_c.getvalue()
                    # Atualiza mapa para imagem única
                    adapt_map = {1: final_content}
                    adapt_qs = [1]
                else:
                    st.warning("Aguarde o carregamento do recorte...")
                    st.stop()

            if not final_content:
                st.warning("Conteúdo vazio.")
            else:
                with st.spinner("Adaptando..."):
                    rac, txt = adaptar_conteudo(api_key, aluno, final_content, st.session_state.adapt_type, materia, tema, tipo_atv, modo_prof, adapt_qs)
                    st.session_state['res_adapt'] = {'rac': rac, 'txt': txt, 'map': adapt_map}
                    st.rerun()

    if 'res_adapt' in st.session_state:
        res = st.session_state['res_adapt']
        st.markdown("---")
        with st.expander("🧠 Ver Racional Pedagógico", expanded=False): st.info(res['rac'])
        st.subheader("👁️ Resultado Final")
        with st.container(border=True):
            partes = re.split(r'(\[\[IMG_\d+\]\])', res['txt'])
            for p in partes:
                tag = re.search(r'\[\[IMG_(\d+)\]\]', p)
                if tag:
                    i = int(tag.group(1))
                    im = res['map'].get(i)
                    if not im and len(res['map']) == 1: im = list(res['map'].values())[0]
                    if im: st.image(im, width=300)
                elif p.strip(): st.markdown(p.strip())
        
        docx = construir_docx_final(res['txt'], aluno, materia, res['map'], None, tipo_atv)
        st.download_button("📥 BAIXAR DOCX", docx, "Atividade_Adaptada.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document", type="primary", use_container_width=True)

# 2. CRIAR
with tab_create:
    cc1, cc2 = st.columns(2)
    mat_c = cc1.selectbox("Componente", ["Matemática", "Português", "Ciências", "História", "Geografia"], key="cm")
    obj_c = cc2.text_input("Objeto de Conhecimento", placeholder="Ex: Sistema Solar", key="co")
    cc3, cc4 = st.columns(2)
    qtd_c = cc3.slider("Quantidade", 1, 10, 5, key="cq")
    tipo_c = cc4.selectbox("Formato", ["Múltipla Escolha", "Discursiva", "Mista"], key="ct")
    
    if st.button("✨ CRIAR (GERAR OPÇÕES)", type="primary", key="btn_create"):
        with st.spinner(f"Criando..."):
            rac, opt_a, opt_b = criar_duas_opcoes(api_key, aluno, mat_c, obj_c, qtd_c, tipo_c)
            st.session_state['create_opts'] = {'rac': rac, 'A': opt_a, 'B': opt_b}
            st.rerun()

    if 'create_opts' in st.session_state:
        opts = st.session_state['create_opts']
        with st.expander("🧠 Racional Pedagógico", expanded=False): st.info(opts['rac'])
        st.write("### Escolha a versão:")
        tab_a, tab_b = st.tabs(["🅰️ Opção A (Lúdica)", "🅱️ Opção B (Estruturada)"])
        
        with tab_a:
            st.markdown(opts['A'])
            if st.button("✅ ESCOLHER A", key="sel_a"):
                st.session_state['final_create'] = opts['A']; st.rerun()
        with tab_b:
            st.markdown(opts['B'])
            if st.button("✅ ESCOLHER B", key="sel_b"):
                st.session_state['final_create'] = opts['B']; st.rerun()

    if 'final_create' in st.session_state:
        txt_base = st.session_state['final_create']
        st.markdown("---")
        
        if 'create_map' not in st.session_state:
            novo_map = {}; count = 0
            tags = re.findall(r'\[\[GEN_IMG: (.*?)\]\]', txt_base)
            with st.spinner(f"Gerando {len(tags)} imagens..."):
                for p in tags:
                    count += 1
                    url = gerar_dalle_prompt(api_key, p)
                    if url:
                        io = baixar_imagem_url(url)
                        if io: novo_map[count] = io.getvalue()
            
            txt_fin = txt_base
            for i in range(1, count + 1): 
                txt_fin = re.sub(r'\[\[GEN_IMG: .*?\]\]', f"[[IMG_{i}]]", txt_fin, count=1)
            
            st.session_state['create_map'] = novo_map
            st.session_state['create_txt_final'] = txt_fin
            st.rerun()

        with st.container(border=True):
            partes = re.split(r'(\[\[IMG_\d+\]\])', st.session_state['create_txt_final'])
            for p in partes:
                tag = re.search(r'\[\[IMG_(\d+)\]\]', p)
                if tag:
                    idx = int(tag.group(1))
                    im = st.session_state['create_map'].get(idx)
                    if im: st.image(im, width=300)
                elif p.strip(): st.markdown(p.strip())

        docx = construir_docx_final(st.session_state['create_txt_final'], aluno, mat_c, st.session_state['create_map'], None, "Atividade Criada")
        st.download_button("📥 BAIXAR DOCX FINAL", docx, "Atividade_Criada.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document", type="primary", use_container_width=True)

# 3. VISUAL
with tab_visual:
    st.info("Estúdio Visual: Crie recursos de apoio.")
    desc = st.text_area("Descrição:", placeholder="Ex: Rotina visual...", key="vd")
    if st.button("🎨 GERAR", type="primary", key="v_btn"):
        with st.spinner("Desenhando..."):
            url = gerar_dalle_prompt(api_key, f"{desc} with {aluno.get('hiperfoco')} theme")
            if url: st.image(url)

# 4. CONTEXTO
with tab_ctx:
    st.info("Quebra-Gelo Pedagógico.")
    ass = st.text_input("Assunto:", key="cx_ass")
    t_extra = st.text_input("Tema (Opcional):", placeholder="Ex: Minecraft", key="cx_tema")
    if st.button("💡 EXPLICAR", type="primary", key="cx_btn"):
        with st.spinner("Pensando..."):
            st.markdown(gerar_contextualizacao(api_key, aluno, ass, t_extra))
