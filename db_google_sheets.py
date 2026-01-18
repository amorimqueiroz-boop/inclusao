# db_google_sheets.py
import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
import json
from datetime import datetime, date
import time

# ==============================================================================
# 1. CONEXÃO ÚNICA COM GOOGLE SHEETS
# ==============================================================================
@st.cache_resource
def conectar_gsheets():
    """Conecta ao Google Sheets uma única vez"""
    try:
        scope = ["https://spreadsheets.google.com/feeds", 
                "https://www.googleapis.com/auth/drive"]
        credentials = Credentials.from_service_account_info(
            st.secrets["gcp_service_account"], 
            scopes=scope
        )
        client = gspread.authorize(credentials)
        return client
    except Exception as e:
        st.error(f"Erro de conexão: {str(e)}")
        return None

# ==============================================================================
# 2. FUNÇÕES PARA ALUNOS (REPLACES services.py)
# ==============================================================================
def carregar_alunos_usuario(usuario_atual=None):
    """Carrega apenas alunos do usuário atual"""
    if not usuario_atual:
        usuario_atual = st.session_state.get("usuario_nome", "")
    
    try:
        client = conectar_gsheets()
        if not client:
            return []
            
        sheet = client.open("Omnisfera_Dados").sheet1 
        records = sheet.get_all_records()
        lista_processada = []
        
        for reg in records:
            try:
                # Filtra por responsável OU se for Admin mostra todos
                if usuario_atual == "Admin" or (reg.get('Responsável') == usuario_atual):
                    if 'Dados_Completos' in reg and reg['Dados_Completos']:
                        try:
                            dados_completos = json.loads(reg['Dados_Completos'])
                            lista_processada.append(dados_completos)
                        except:
                            lista_processada.append(reg)
                    else:
                        lista_processada.append(reg)
            except:
                continue
        return lista_processada
    except Exception as e:
        st.warning(f"Não foi possível carregar dados: {e}")
        return []

def salvar_aluno_completo(dados):
    """Salva aluno com todos os dados (substitui salvar_aluno_integrado)"""
    if not dados.get('nome'):
        return False, "Nome é obrigatório."
    
    try:
        client = conectar_gsheets()
        if not client:
            return False, "Erro de conexão"
        
        sheet = client.open("Omnisfera_Dados").sheet1
        
        # Prepara o JSON completo
        dados_json_str = json.dumps(dados, default=str, ensure_ascii=False)
        
        # Linha para salvar
        linha_dados = [
            dados['nome'],
            dados.get('serie', ''),
            dados.get('diagnostico', ''),
            str(date.today()),
            dados.get('responsavel', st.session_state.get("usuario_nome", "Admin")),
            dados_json_str
        ]
        
        # Verifica se já existe
        try:
            cell = sheet.find(dados['nome'])
        except:
            cell = None
            
        if cell:
            # Atualiza
            range_name = f"A{cell.row}:F{cell.row}" 
            sheet.update(range_name=range_name, values=[linha_dados])
            msg = "Atualizado!"
        else:
            # Novo
            sheet.append_row(linha_dados)
            msg = "Cadastrado!"
            
        return True, msg
        
    except Exception as e:
        return False, f"Erro: {str(e)}"

def excluir_aluno_por_nome(nome_aluno):
    """Remove aluno permanentemente"""
    try:
        client = conectar_gsheets()
        if not client:
            return False, "Erro de conexão"
        
        sheet = client.open("Omnisfera_Dados").sheet1
        
        try:
            cell = sheet.find(nome_aluno)
            if cell:
                sheet.delete_rows(cell.row)
                return True, f"Aluno {nome_aluno} removido."
            else:
                return False, "Aluno não encontrado."
        except gspread.exceptions.CellNotFound:
            return False, "Aluno não encontrado."
    except Exception as e:
        return False, f"Erro: {str(e)}"

# ==============================================================================
# 3. FUNÇÕES PARA METAS PEI
# ==============================================================================
def salvar_metas_pei(dados_metas):
    """Salva metas do PEI na aba específica"""
    try:
        client = conectar_gsheets()
        if not client:
            return False
        
        # Tenta abrir aba Metas_PEI ou cria se não existir
        try:
            planilha = client.open("Omnisfera_Dados")
            try:
                sheet = planilha.worksheet("Metas_PEI")
            except:
                sheet = planilha.add_worksheet("Metas_PEI", rows=1000, cols=10)
                sheet.append_row([
                    "ID", "Aluno", "Meta_Curto", "Meta_Medio", "Meta_Longo",
                    "Status", "Data_Criacao", "Responsavel", "Série", "Diagnostico"
                ])
        
        except Exception as e:
            st.error(f"Erro na aba Metas_PEI: {e}")
            return False
        
        # Prepara dados
        linha = [
            f"{dados_metas.get('aluno_nome')}_{datetime.now().timestamp()}",
            dados_metas.get('aluno_nome', ''),
            dados_metas.get('meta_curto', ''),
            dados_metas.get('meta_medio', ''),
            dados_metas.get('meta_longo', ''),
            dados_metas.get('status', 'Ativo'),
            str(date.today()),
            st.session_state.get("usuario_nome", ""),
            dados_metas.get('serie', ''),
            dados_metas.get('diagnostico', '')
        ]
        
        sheet.append_row(linha)
        return True
        
    except Exception as e:
        st.error(f"Erro ao salvar metas: {e}")
        return False

def buscar_metas_por_aluno(nome_aluno):
    """Busca metas de um aluno específico"""
    try:
        client = conectar_gsheets()
        if not client:
            return []
        
        try:
            sheet = client.open("Omnisfera_Dados").worksheet("Metas_PEI")
            records = sheet.get_all_records()
            
            # Filtra pelo aluno
            metas_aluno = []
            for reg in records:
                if reg.get('Aluno', '').strip() == nome_aluno.strip():
                    metas_aluno.append(reg)
            
            return metas_aluno
            
        except:
            return []
            
    except:
        return []

# ==============================================================================
# 4. FUNÇÕES PARA DIÁRIO DE BORDO (REPLACES 4_Diario_de_Bordo.py)
# ==============================================================================
def salvar_registro_diario(dados_registro):
    """Salva um registro no diário de bordo"""
    try:
        client = conectar_gsheets()
        if not client:
            return False
        
        # Garante que a aba existe
        try:
            planilha = client.open("Omnisfera_Dados")
            try:
                sheet = planilha.worksheet("Diario_Bordo")
            except:
                sheet = planilha.add_worksheet("Diario_Bordo", rows=1000, cols=12)
                sheet.append_row([
                    "ID", "Data_Hora", "Professor", "Aluno", "Turma", 
                    "Meta_PEI", "Estrategia_Base", "Atividade_Hub", 
                    "Avaliacao_Suporte", "Observacao", "Status_Integracao", "Componente"
                ])
        
        except Exception as e:
            st.error(f"Erro na aba Diario_Bordo: {e}")
            return False
        
        # Prepara linha
        linha = [
            f"{datetime.now().timestamp()}",
            datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            dados_registro.get('professor', st.session_state.get("usuario_nome", "")),
            dados_registro.get('aluno', ''),
            dados_registro.get('turma', ''),
            dados_registro.get('meta_pei', ''),
            dados_registro.get('estrategia_base', ''),
            dados_registro.get('atividade_hub', ''),
            dados_registro.get('avaliacao', ''),
            dados_registro.get('observacao', ''),
            "Integrado",
            dados_registro.get('componente', '')
        ]
        
        sheet.append_row(linha)
        return True
        
    except Exception as e:
        st.error(f"Erro ao salvar registro: {e}")
        return False

def carregar_diario_completo():
    """Carrega todo o diário para análise"""
    try:
        client = conectar_gsheets()
        if not client:
            return pd.DataFrame()
        
        try:
            sheet = client.open("Omnisfera_Dados").worksheet("Diario_Bordo")
            records = sheet.get_all_records()
            return pd.DataFrame(records)
        except:
            return pd.DataFrame()
            
    except:
        return pd.DataFrame()

# ==============================================================================
# 5. FUNÇÕES PARA HUB DE INCLUSÃO (VALIDAÇÃO)
# ==============================================================================
def salvar_validacao_hub(nome_aluno, tipo_atividade, componente, tema):
    """Salva validação do Hub no histórico"""
    try:
        client = conectar_gsheets()
        if not client:
            return False
        
        # Tenta abrir aba Historico_Hub ou cria
        try:
            planilha = client.open("Omnisfera_Dados")
            try:
                sheet = planilha.worksheet("Historico_Hub")
            except:
                sheet = planilha.add_worksheet("Historico_Hub", rows=1000, cols=8)
                sheet.append_row([
                    "ID", "Data_Hora", "Aluno", "Tipo_Atividade", 
                    "Componente", "Tema", "Responsavel", "Status"
                ])
        
        except Exception as e:
            st.error(f"Erro na aba Historico_Hub: {e}")
            return False
        
        # Prepara linha
        linha = [
            f"{datetime.now().timestamp()}",
            datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            nome_aluno,
            tipo_atividade,
            componente if componente else "Educação Infantil",
            tema,
            st.session_state.get("usuario_nome", ""),
            "Validado"
        ]
        
        sheet.append_row(linha)
        return True
        
    except Exception as e:
        st.error(f"Erro ao salvar validação: {e}")
        return False

def buscar_historico_hub_aluno(nome_aluno):
    """Busca histórico de validações de um aluno"""
    try:
        client = conectar_gsheets()
        if not client:
            return []
        
        try:
            sheet = client.open("Omnisfera_Dados").worksheet("Historico_Hub")
            records = sheet.get_all_records()
            
            # Filtra pelo aluno
            historico = []
            for reg in records:
                if reg.get('Aluno', '').strip() == nome_aluno.strip():
                    historico.append(reg)
            
            return historico
            
        except:
            return []
            
    except:
        return []

# ==============================================================================
# 6. FUNÇÃO DE INICIALIZAÇÃO (VERIFICA/CREA ABAS)
# ==============================================================================
def inicializar_planilha():
    """Verifica se todas as abas existem, cria se necessário"""
    try:
        client = conectar_gsheets()
        if not client:
            return False
        
        planilha = client.open("Omnisfera_Dados")
        
        # Lista de abas necessárias
        abas_necessarias = [
            ("Metas_PEI", [
                "ID", "Aluno", "Meta_Curto", "Meta_Medio", "Meta_Longo",
                "Status", "Data_Criacao", "Responsavel", "Série", "Diagnostico"
            ]),
            ("Diario_Bordo", [
                "ID", "Data_Hora", "Professor", "Aluno", "Turma", 
                "Meta_PEI", "Estrategia_Base", "Atividade_Hub", 
                "Avaliacao_Suporte", "Observacao", "Status_Integracao", "Componente"
            ]),
            ("Historico_Hub", [
                "ID", "Data_Hora", "Aluno", "Tipo_Atividade", 
                "Componente", "Tema", "Responsavel", "Status"
            ])
        ]
        
        for nome_aba, cabecalhos in abas_necessarias:
            try:
                planilha.worksheet(nome_aba)
            except:
                nova_aba = planilha.add_worksheet(nome_aba, rows=1000, cols=len(cabecalhos))
                nova_aba.append_row(cabecalhos)
                time.sleep(1)  # Evita rate limit
        
        return True
        
    except Exception as e:
        st.error(f"Erro ao inicializar planilha: {e}")
        return False
