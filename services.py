import requests
import streamlit as st
import pandas as pd

# --- CONFIGURAÇÃO ---
# ⚠️ SUBSTITUA O LINK ABAIXO PELO SEU LINK DO SHEETDB
SHEET_DB_URL = "https://sheetdb.io/api/v1/d8098eian87x9"

def enviar_checkin(dados):
    """Envia o check-in para a aba Logs_Checkin"""
    url = f"{SHEET_DB_URL}?sheet=Logs_Checkin"
    headers = {"Content-Type": "application/json"}
    payload = {"data": [dados]}
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        return response.status_code == 201
    except Exception as e:
        st.error(f"Erro de conexão: {e}")
        return False

@st.cache_data(ttl=60) # Guarda os dados por 60s para não ficar lento
def buscar_logs():
    """Busca todo o histórico de check-ins para gerar os gráficos"""
    url = f"{SHEET_DB_URL}?sheet=Logs_Checkin"
    try:
        response = requests.get(url)
        data = response.json()
        if isinstance(data, list):
            return pd.DataFrame(data)
        return pd.DataFrame()
    except:
        return pd.DataFrame()

def salvar_pei_db(dados):
    """Salva os dados do PEI na aba 'Metas_PEI' do Google Sheets"""
    # Garante que está apontando para a aba correta
    url = f"{SHEET_DB_URL}?sheet=Metas_PEI"
    headers = {"Content-Type": "application/json"}
    
    # Empacota os dados no formato esperado pela API
    payload = {"data": [dados]}
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        return response.status_code == 201
    except Exception as e:
        st.error(f"Erro ao conectar com o banco de dados: {e}")
        return False
