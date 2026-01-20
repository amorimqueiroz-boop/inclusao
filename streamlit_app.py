import streamlit as st
from ui_nav import boot_ui

boot_ui(do_route=True)
import importlib.util
import os

TARGET = "home_portal.py"

# falha de forma explícita se o arquivo sumir (mas sem poluir a tela)
if not os.path.exists(TARGET):
    raise FileNotFoundError(f"Arquivo não encontrado: {TARGET}")

spec = importlib.util.spec_from_file_location("home_module", TARGET)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
