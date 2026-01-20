import streamlit as st
from ui_nav import render_topbar_nav

# -------------------------------------------------
# HOME.PY AGORA É O "APP.PY"
# -------------------------------------------------

# Desenha o menu
# (ele mesmo decide se aparece ou não)
view = render_topbar_nav(hide_on_views=("home",))

# -------------------------
# HOME (SEM MENU)
# -------------------------
if view == "home":
    st.title("Home — Omnisfera")
    st.write("Home limpa, sem menu.")

    st.markdown("### Acessar módulos:")
    st.markdown("- [Plano de Ação (PAEE)](?view=paee)")
    st.markdown("- [Estratégias & PEI](?view=pei)")
    st.markdown("- [Alunos](?view=alunos)")

# -------------------------
# PAEE
# -------------------------
elif view == "paee":
    st.title("PAEE — teste mínimo")
    st.success("Menu funcionando sem caixinhas ✅")
    st.write("Aqui entra o conteúdo real do PAEE.")

# -------------------------
# PEI
# -------------------------
elif view == "pei":
    st.title("PEI — teste mínimo")
    st.write("Conteúdo do PEI aqui.")

# -------------------------
# ALUNOS
# -------------------------
elif view == "alunos":
    st.title("Alunos — teste mínimo")
    st.write("Conteúdo de alunos aqui.")

# -------------------------
# FALLBACK
# -------------------------
else:
    st.title(f"Tela: {view}")
    st.write("Tela ainda não implementada.")
