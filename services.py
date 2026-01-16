iimport requests
import streamlit as st
import pandas as pd

# --- CONFIGURAÇÃO ---
# https://sheetdb.io/api/v1/jr7on4w9yqczn)
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

@st.cache_data(ttl=60) # Guarda os dados por 60 segundos para não travar
def buscar_logs():
    """Busca todo o histórico de check-ins"""
    url = f"{SHEET_DB_URL}?sheet=Logs_Checkin"
    try:
        response = requests.get(url)
        data = response.json()
        # Transforma em Tabela Inteligente (DataFrame)
        if data:
            df = pd.DataFrame(data)
            return df
        return pd.DataFrame()
    except:
        return pd.DataFrame()






