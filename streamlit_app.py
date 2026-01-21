import streamlit as st
from supabase_client import supabase

st.write("Supabase conectado:", supabase is not None)
