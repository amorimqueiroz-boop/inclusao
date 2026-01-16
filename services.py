import requests
import streamlit as st

# --- CONFIGURAÇÃO ---
# https://sheetdb.io/api/v1/jr7on4w9yqczn)
SHEET_DB_URL = "COLE_SEU_LINK_SHEETDB_AQUI"

def enviar_checkin(dados):
    """Envia o check-in para a aba Logs_Checkin"""
    url = f"{SHEET_DB_URL}?sheet=Logs_Checkin"
    headers = {"Content-Type": "application/json"}
    
    # Prepara o pacote de dados
    payload = {"data": [dados]}
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 201:
            return True
        else:
            st.error(f"Erro no envio: {response.text}")
            return False
    except Exception as e:
        st.error(f"Erro de conexão: {e}")
        return False

def buscar_metas():
    """Busca as metas da aba Metas_PEI"""
    url = f"{SHEET_DB_URL}?sheet=Metas_PEI"
    try:
        response = requests.get(url)
        return response.json()
    except:
        return []
