import requests
import streamlit as st
import json
import pandas as pd
from datetime import date

# --- CONFIGURAÇÃO ---
# ⚠️ SUBSTITUA O LINK ABAIXO PELO SEU LINK DO SHEETDB
SHEET_DB_URL = "https://sheetdb.io/api/v1/d8098eian87x9"

# ==============================================================================
# 1. FUNÇÕES DO PEI (CADASTRO E METAS)
# ==============================================================================

def salvar_aluno_integrado(dados):
    """
    Salva o perfil completo do aluno na aba 'Banco_Alunos'.
    """
    url = f"{SHEET_DB_URL}?sheet=Banco_Alunos"
    headers = {"Content-Type": "application/json"}
    
    # Gera um ID único simples
    aluno_id = f"{dados.get('nome')}_{str(dados.get('nasc'))}".replace(" ", "_")
    
    pacote = {
        "id": aluno_id,
        "nome": dados.get('nome'),
        "serie": dados.get('serie'),
        "responsavel": st.session_state.get("usuario_nome", "Admin"),
        "data_criacao": str(date.today()),
        # Salva o JSON completo como texto para backup total
        "dados_completos": json.dumps(dados, default=str, ensure_ascii=False)
    }
    
    payload = {"data": [pacote]}
    
    try:
        # Primeiro tenta verificar se já existe para atualizar (PATCH) ou criar (POST)
        # Por simplicidade no SheetDB, vamos usar POST. Se precisar de update real, seria PUT/PATCH.
        # Aqui, vamos adicionar um novo registro sempre (histórico) ou você pode limpar antes.
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 201:
            return True, "Aluno integrado à Omnisfera com sucesso!"
        else:
            return False, f"Erro na API: {response.text}"
    except Exception as e:
        return False, f"Erro de conexão: {str(e)}"

def salvar_pei_db(dados_pacote):
    """Salva o Texto do PEI na aba 'Metas_PEI'"""
    url = f"{SHEET_DB_URL}?sheet=Metas_PEI"
    headers = {"Content-Type": "application/json"}
    
    payload = {"data": [dados_pacote]}
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        return response.status_code == 201
    except Exception as e:
        st.error(f"Erro ao conectar: {e}")
        return False

def buscar_alunos_banco():
    """Busca a lista de alunos para o selectbox da Sidebar"""
    url = f"{SHEET_DB_URL}?sheet=Banco_Alunos"
    try:
        response = requests.get(url)
        data = response.json()
        return data if isinstance(data, list) else []
    except:
        return []

def carregar_aluno_completo(nome_aluno):
    """Recupera o JSON completo de um aluno específico"""
    # Busca pelo nome exato
    url = f"{SHEET_DB_URL}/search?nome={nome_aluno}&sheet=Banco_Alunos"
    try:
        response = requests.get(url)
        data = response.json()
        if data and len(data) > 0:
            # Pega o registro mais recente (último da lista se houver duplicados)
            registro = data[-1]
            json_str = registro.get('dados_completos')
            return json.loads(json_str)
        return None
    except:
        return None

# ==============================================================================
# 2. FUNÇÕES DO DIÁRIO DE BORDO E MONITORAMENTO (CHECK-IN)
# ==============================================================================

def enviar_checkin(dados):
    """Envia o check-in diário para a aba 'Logs_Checkin'"""
    url = f"{SHEET_DB_URL}?sheet=Logs_Checkin"
    headers = {"Content-Type": "application/json"}
    payload = {"data": [dados]}
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        return response.status_code == 201
    except Exception as e:
        st.error(f"Erro de conexão: {e}")
        return False

@st.cache_data(ttl=60)
def buscar_logs():
    """Busca todo o histórico de check-ins para os gráficos"""
    url = f"{SHEET_DB_URL}?sheet=Logs_Checkin"
    try:
        response = requests.get(url)
        data = response.json()
        if isinstance(data, list):
            return pd.DataFrame(data)
        return pd.DataFrame()
    except:
        return pd.DataFrame()


def carregar_peis_do_banco():
    """Busca todos os PEIs salvos na aba Metas_PEI"""
    url = f"{SHEET_DB_URL}?sheet=Metas_PEI"
    try:
        response = requests.get(url)
        data = response.json()
        # Se vier vazio ou der erro, retorna lista vazia
        if isinstance(data, list):
            return data
        return []
    except Exception as e:
        st.error(f"Erro ao buscar PEIs: {e}")
        return []
