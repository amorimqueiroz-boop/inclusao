import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import pandas as pd

@st.cache_resource
def conectar_gsheets():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    credentials = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scope)
    client = gspread.authorize(credentials)
    return client

def carregar_banco():
    """Busca os alunos na planilha 'Omnisfera_Dados' apenas do usuário atual"""
    usuario_atual = st.session_state.get("usuario_nome", "")
    try:
        client = conectar_gsheets()
        sheet = client.open("Omnisfera_Dados").sheet1 
        records = sheet.get_all_records()
        lista_processada = []
        
        for reg in records:
            try:
                # Verifica se o responsável é o usuário atual
                if 'Responsável' in reg and reg['Responsável'] == usuario_atual:
                    # Se salvamos o objeto completo na coluna 'Dados_Completos', recuperamos aqui
                    if 'Dados_Completos' in reg and reg['Dados_Completos']:
                        try:
                            dados_completos = json.loads(reg['Dados_Completos'])
                            lista_processada.append(dados_completos)
                        except:
                            lista_processada.append(reg)
                    else:
                        lista_processada.append(reg)
            except Exception as e:
                continue
        return lista_processada
    except Exception as e:
        st.warning(f"Não foi possível carregar dados do Google Sheets: {e}")
        return []

def salvar_aluno(dados):
    """Salva o aluno na planilha 'Omnisfera_Dados'"""
    if not dados['nome']: return False, "Nome é obrigatório."
    
    try:
        client = conectar_gsheets()
        sheet = client.open("Omnisfera_Dados").sheet1
        
        # Prepara o JSON completo para salvar na nuvem
        dados_json_str = json.dumps(dados, default=str, ensure_ascii=False)
        
        # Colunas: Nome, Série, Diagnóstico, Data, Responsável, Dados_Completos (JSON)
        linha_dados = [
            dados['nome'],
            dados.get('serie', ''),
            dados.get('diagnostico', ''),
            str(date.today()),
            dados.get('responsavel', st.session_state.get("usuario_nome", "Admin")),
            dados_json_str
        ]
        
        cell = None
        try:
            cell = sheet.find(dados['nome'])
        except:
            pass
            
        if cell:
            # Atualiza
            range_name = f"A{cell.row}:F{cell.row}" 
            sheet.update(range_name=range_name, values=[linha_dados])
            msg_nuvem = "Nuvem: Atualizado!"
        else:
            # Novo
            sheet.append_row(linha_dados)
            msg_nuvem = "Nuvem: Cadastrado!"
            
        return True, msg_nuvem
        
    except Exception as e:
        return False, f"Erro Nuvem: {str(e)}"

def excluir_aluno(nome_aluno):
    """Apaga o aluno da planilha"""
    try:
        client = conectar_gsheets()
        sheet = client.open("Omnisfera_Dados").sheet1
        try:
            cell = sheet.find(nome_aluno)
            if cell:
                sheet.delete_rows(cell.row)
                return True, f"Aluno {nome_aluno} removido permanentemente."
            else:
                return False, "Aluno não encontrado na planilha."
        except gspread.exceptions.CellNotFound:
             return False, "Aluno não encontrado."
    except Exception as e:
        return False, f"Erro ao excluir: {str(e)}"

def salvar_pei(dados):
    """Salva o PEI na aba 'Metas_PEI'"""
    # Implementar similarmente, ajustando a estrutura de dados
    pass

def buscar_logs():
    """Busca os logs do diário de bordo"""
    try:
        client = conectar_gsheets()
        sheet = client.open("Omnisfera_Dados").worksheet("Diario_Bordo")
        records = sheet.get_all_records()
        return pd.DataFrame(records)
    except Exception as e:
        st.error(f"Erro ao buscar logs: {e}")
        return pd.DataFrame()

def enviar_checkin(dados):
    """Envia um registro para o diário de bordo"""
    try:
        client = conectar_gsheets()
        sheet = client.open("Omnisfera_Dados").worksheet("Diario_Bordo")
        # Converter os valores para string para evitar erros
        linha = [str(dados[col]) for col in dados]
        sheet.append_row(linha)
        return True
    except Exception as e:
        st.error(f"Erro ao enviar check-in: {e}")
        return False


def carregar_peis():
    """Carrega os PEIs da aba 'Metas_PEI'"""
    try:
        client = conectar_gsheets()
        sheet = client.open("Omnisfera_Dados").worksheet("Metas_PEI")
        records = sheet.get_all_records()
        return pd.DataFrame(records)
    except Exception as e:
        st.error(f"Erro ao carregar PEIs: {e}")
        return pd.DataFrame()
