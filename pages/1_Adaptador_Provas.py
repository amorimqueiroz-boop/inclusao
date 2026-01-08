import streamlit as st
from openai import OpenAI
from io import BytesIO
from docx import Document
from docx.shared import Pt, Inches
from pypdf import PdfReader
from fpdf import FPDF
import base64
import os
import re
import requests

# --- 1. CONFIGURAÇÃO ---
st.set_page_config(page_title="Adaptador 360º V4", page_icon="🧩", layout="wide")

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

# --- 3. FUNÇÕES AUXILIARES ---
def ler_arquivo(uploaded_file):
    if uploaded_file is None: return None, None
    if uploaded_file.type == "application/pdf":
        try:
            reader = PdfReader(uploaded_file)
            texto = ""
            for page in reader.pages: texto += page.extract_text() + "\n"
            return texto, "pdf"
        except: return "", "erro"
    elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        try:
            doc = Document(uploaded_file)
            texto = "\n".join([p.text for p in doc.paragraphs])
            return texto, "docx"
        except: return "", "erro"
    elif uploaded_file.type in ["image/png", "image/jpeg", "image/jpg"]:
        return base64.b64encode(uploaded_file.read()).decode('utf-8'), "imagem"
    return None, None

# Funções de Download (Word/PDF) precisam ser atualizadas para suportar imagens no futuro
# Por enquanto, elas baixam apenas o texto adaptado.
def gerar_docx_atividade(conteudo, aluno, materia):
    doc = Document()
    style = doc.styles['Normal']; style.font.name = 'Arial'; style.font.size = Pt(12)
    doc.add_heading(f'ATIVIDADE ADAPTADA - {materia.upper()}', 0)
    doc.add_paragraph(f"Estudante: {aluno}")
    doc.add_paragraph("_"*50)
    doc.add_paragraph(conteudo)
    buffer = BytesIO(); doc.save(buffer); buffer.seek(0)
    return buffer

def gerar_pdf_atividade(conteudo, aluno, materia):
    pdf = FPDF(); pdf.add_page(); pdf.set_font("Arial", size=12)
    def txt(t): return str(t).encode('latin-1', 'replace').decode('latin-1')
    pdf.set_font("Arial", 'B', 14); pdf.cell(0, 10, txt(f"ATIVIDADE ADAPTADA - {materia.upper()}"), 0, 1, 'C')
    pdf.set_font("Arial", 'I', 10); pdf.cell(0, 10, txt(f"Estudante: {aluno}"), 0, 1, 'L')
    pdf.line(10, 30, 200, 30); pdf.ln(10)
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 7, txt(conteudo))
    return pdf.output(dest='S').encode('latin-1')

# --- 4. INTELIGÊNCIA (DALL-E 3 - GERAÇÃO DE IMAGEM) ---
def gerar_apoio_visual_dalle(api_key, tema, aluno_dados):
    client = OpenAI(api_key=api_key)
    
    hiperfoco = aluno_dados.get('hiperfoco', '')
    contexto_hiperfoco = f"Integrate elements related to '{hiperfoco}' to engage the student, but keep it subtle." if hiperfoco else ""

    # Prompt para o DALL-E (em inglês funciona melhor)
    prompt_dalle = f"""
    Create a clear, educational illustration for a school activity about "{tema}".
    Target audience: A student with special educational needs.
    Style: Clean line art, friendly colors, no distracting background elements, easy to understand.
    Content: A central visual representation of the concept "{tema}".
    {contexto_hiperfoco}
    Do NOT include any text or letters in the image.
    """
    
    try:
        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt_dalle,
            size="1024x1024",
            quality="standard",
            n=1,
        )
        image_url = response.data[0].url
        return image_url, None
    except Exception as e:
        return None, f"Erro DALL-E: {e}"

# --- 5. INTELIGÊNCIA (GPT-4o - ADAPTAÇÃO DE TEXTO + RACIONAL) ---
def adaptar_atividade_v4(api_key, aluno_dados, conteudo_orig, tipo_arquivo, materia, tema, tipo_atv):
    if not api_key: return None, None, "⚠️ Chave API faltando."
    
    client = OpenAI(api_key=api_key)
    
    diretrizes_pei = "Foco na redução de barreiras e clareza."
    if 'ia_sugestao' in aluno_dados and "DIRETRIZES" in aluno_dados['ia_sugestao']:
        try: match = re.search(r"DIRETRIZES.*?(?=\n\n|$)", aluno_dados['ia_sugestao'], re.DOTALL); diretrizes_pei = match.group(0) if match else diretrizes_pei
        except: pass

    prompt_sistema = """
    Você é um Especialista em DUA (Desenho Universal para Aprendizagem).
    Sua tarefa é dupla:
    1. Gerar um RACIONAL TÉCNICO para o professor, explicando as adaptações feitas.
    2. Gerar a ATIVIDADE FINAL para o aluno, pronta para uso.
    
    FORMATO DE SAÍDA OBRIGATÓRIO (Use exatamente este divisor):
    [RACIONAL PROFESSOR]
    ...seu texto explicativo aqui...
    ---DIVISOR---
    [ATIVIDADE ALUNO]
    ...a atividade adaptada aqui...
    """
    
    texto_usuario = f"""
    ESTUDANTE: {aluno_dados['nome']} | DIAGNÓSTICO: {aluno_dados.get('diagnostico')}
    DIRETRIZES DO PEI: {diretrizes_pei}
    CONTEXTO: {materia} | {tema} | {tipo_atv}
    
    INSTRUÇÕES:
    1. No Racional, explique quais barreiras foram consideradas e por que certas mudanças (simplificação, quebra de questões, mudança de layout) foram feitas.
    2. Na Atividade, aplique as adaptações mantendo o objetivo pedagógico da BNCC.
    """

    mensagens = [{"role": "system", "content": prompt_sistema}, {"role": "user", "content": []}]
    mensagens[1]["content"].append({"type": "text", "text": texto_usuario})

    if tipo_arquivo == "imagem":
        mensagens[1]["content"].append({"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{conteudo_orig}"}})
    else:
        mensagens[1]["content"].append({"type": "text", "text": f"\n--- CONTEÚDO ORIGINAL ---\n{conteudo_orig}"})

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=mensagens,
            temperature=0.5
        )
        texto_completo = response.choices[0].message.content
        
        # Separa o Racional da Atividade usando o divisor
        partes = texto_completo.split("---DIVISOR---")
        if len(partes) == 2:
            racional = partes[0].replace("[RACIONAL PROFESSOR]", "").strip()
            atividade = partes[1].replace("[ATIVIDADE ALUNO]", "").strip()
            return racional, atividade, None
        else:
            return None, texto_completo, "Erro de formatação da IA. Tente novamente."

    except Exception as e: return None, None, f"Erro OpenAI: {e}"

# --- 6. INTERFACE ---
with st.sidebar:
    st.markdown("### ⚙️ Configuração")
    api_key = st.secrets.get('OPENAI_API_KEY', st.text_input("Chave OpenAI:", type="password"))
    if api_key: st.success("✅ OpenAI Ativa")
    
    st.markdown("---")
    # NOVIDADE: Toggle para DALL-E
    usar_dalle = st.toggle("🎨 Gerar Apoio Visual (IA)", value=False, help="Ativa o DALL-E 3 para criar uma imagem de suporte personalizada para a atividade. (Custo adicional por imagem gerada).")
    
    st.markdown("---")
    if st.button("🗑️ Limpar Sessão"):
        for key in ['resultado_racional', 'resultado_atividade', 'resultado_imagem_dalle']:
            if key in st.session_state: del st.session_state[key]
        st.rerun()

st.markdown("""
    <div class="header-clean">
        <div style="font-size: 3rem;">🧩</div>
        <div>
            <p style="margin: 0; color: #004E92; font-size: 1.5rem; font-weight: 800;">Adaptador V4: Visual & Racional</p>
            <p style="margin: 0; color: #718096;">Adaptação com explicação técnica e geração de imagens de suporte.</p>
        </div>
    </div>
""", unsafe_allow_html=True)

if not st.session_state.banco_estudantes:
    st.warning("⚠️ Nenhum aluno encontrado. Crie o perfil no PEI 360º primeiro.")
    aluno_selecionado = None
else:
    lista_nomes = [a['nome'] for a in st.session_state.banco_estudantes]
    escolha = st.selectbox("📂 Selecione o Estudante:", lista_nomes, index=len(lista_nomes)-1)
    aluno_selecionado = next(a for a in st.session_state.banco_estudantes if a['nome'] == escolha)

if aluno_selecionado:
    with st.expander(f"👤 Perfil Ativo: {aluno_selecionado['nome']}", expanded=False):
        st.write(f"Diagnóstico: {aluno_selecionado.get('diagnostico')}")
        if 'ia_sugestao' in aluno_selecionado: st.info("Diretrizes do PEI carregadas.")

    c_conf, c_up = st.columns([1, 1])
    with c_conf:
        materia = st.selectbox("Componente:", ["Língua Portuguesa", "Matemática", "Ciências", "História", "Geografia", "Arte", "Inglês", "Ed. Física", "Biologia", "Física", "Química"])
        tema = st.text_input("Tema / Assunto:", placeholder="Ex: Fotossíntese")
        tipo_atv = st.selectbox("Tipo:", ["Tarefa", "Atividade de Sala", "Prova", "Trabalho"])
    with c_up:
        arquivo = st.file_uploader("Material Original (PDF, Docx, Foto)", type=["pdf", "docx", "png", "jpg", "jpeg"])
        conteudo_orig, tipo_arq = ler_arquivo(arquivo)
        if tipo_arq == "imagem": st.image(arquivo, width=150, caption="Original")
        elif tipo_arq: st.success(f"{tipo_arq.upper()} carregado.")
        elif not arquivo:
            conteudo_orig = st.text_area("Ou cole o texto:", height=100); tipo_arq = "texto"

    if st.button("✨ ADAPTAR (V4)", type="primary"):
        if not materia or not tema or not conteudo_orig: st.warning("Preencha os campos obrigatórios.")
        else:
            # 1. Adaptação de Texto + Racional
            with st.spinner("IA analisando barreiras e adaptando texto..."):
                racional, atividade, err = adaptar_atividade_v4(api_key, aluno_selecionado, conteudo_orig, tipo_arq, materia, tema, tipo_atv)
                if err: st.error(err)
                else:
                    st.session_state['resultado_racional'] = racional
                    st.session_state['resultado_atividade'] = atividade
            
            # 2. Geração de Imagem (DALL-E) se ativado
            if usar_dalle and not err:
                with st.spinner("DALL-E gerando apoio visual personalizado..."):
                    img_url, img_err = gerar_apoio_visual_dalle(api_key, tema, aluno_selecionado)
                    if img_err: st.warning(f"Não foi possível gerar a imagem: {img_err}")
                    else: st.session_state['resultado_imagem_dalle'] = img_url
            
            if not err: st.success("Processo concluído!")

    # --- ÁREA DE RESULTADOS V4 ---
    if 'resultado_atividade' in st.session_state:
        st.markdown("---")
        st.subheader("Resultado da Adaptação")

        # 1. Racional (Expansível para o professor)
        if 'resultado_racional' in st.session_state:
            with st.expander("🧠 Racional da Adaptação (Visão do Professor) - Clique para ver o que mudou", expanded=False):
                st.markdown(f"<div class='rationale-box'>{st.session_state['resultado_racional']}</div>", unsafe_allow_html=True)

        # 2. Área Visual (Imagem Original + Imagem Gerada)
        c_img_orig, c_img_ia = st.columns(2)
        with c_img_orig:
            if tipo_arq == "imagem" and arquivo:
                st.markdown("###### Material Original (Referência)")
                st.image(arquivo, use_column_width=True)
        with c_img_ia:
            if 'resultado_imagem_dalle' in st.session_state:
                st.markdown("###### Apoio Visual Gerado (IA)")
                st.image(st.session_state['resultado_imagem_dalle'], caption="Imagem gerada pelo DALL-E para este aluno.", use_column_width=True)

        # 3. Atividade Final (Texto Adaptado)
        st.markdown("###### Atividade para Impressão (Aluno)")
        st.markdown(f"<div class='unified-card'>{st.session_state['resultado_atividade']}</div>", unsafe_allow_html=True)

        # 4. Downloads (Ainda só texto por enquanto)
        cd1, cd2 = st.columns(2)
        docx = gerar_docx_atividade(st.session_state['resultado_atividade'], aluno_selecionado['nome'], materia)
        cd1.download_button("📥 Baixar Word (Texto)", docx, "atividade.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document")
        pdf = gerar_pdf_atividade(st.session_state['resultado_atividade'], aluno_selecionado['nome'], materia)
        cd2.download_button("📄 Baixar PDF (Texto)", pdf, "atividade.pdf", "application/pdf")
