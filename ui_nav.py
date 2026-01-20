# ui_nav.py
import streamlit as st
import os, base64

def render_omnisfera_nav():

    ROUTES = {
        "home":   "Home.py",
        "pei":    "pages/1_PEI.py",
        "paee":   "pages/2_PAE.py",
        "hub":    "pages/3_Hub_Inclusao.py",
        "diario": "pages/4_Diario_de_Bordo.py",
        "mon":    "pages/5_Monitoramento_Avaliacao.py",
    }

    # Navegação
    qp = st.query_params
    if "go" in qp:
        dest = qp["go"]
        if dest in ROUTES:
            st.query_params.clear()
            st.switch_page(ROUTES[dest])

    # Logo
    def logo():
        for f in ["omni_icone.png", "logo.png", "ominisfera.png"]:
            if os.path.exists(f):
                with open(f, "rb") as img:
                    return f"data:image/png;base64,{base64.b64encode(img.read()).decode()}"
        return "https://cdn-icons-png.flaticon.com/512/1183/1183672.png"

    src = logo()

    st.markdown(f"""
    <style>
    .omni-pill {{
      position: fixed;
      top: 14px;
      right: 14px;
      z-index: 99999;
      display: flex;
      align-items: center;
      gap: 10px;
      padding: 8px 12px;
      border-radius: 999px;
      background: rgba(255,255,255,.85);
      backdrop-filter: blur(10px);
      box-shadow: 0 10px 30px rgba(0,0,0,.12);
    }}
    .omni-logo {{
      width: 26px;
      height: 26px;
      animation: spin 10s linear infinite;
    }}
    @keyframes spin {{
      from {{ transform: rotate(0deg); }}
      to {{ transform: rotate(360deg); }}
    }}
    .omni-btn {{
      width: 32px;
      height: 32px;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      text-decoration: none;
      background: white;
      border: 1px solid #e5e7eb;
      font-size: 14px;
      font-weight: 800;
    }}
    </style>

    <div class="omni-pill">
      <img src="{src}" class="omni-logo">
      <a class="omni-btn" href="?go=home">🏠</a>
      <a class="omni-btn" href="?go=pei">🧩</a>
      <a class="omni-btn" href="?go=paee">📍</a>
      <a class="omni-btn" href="?go=hub">💡</a>
      <a class="omni-btn" href="?go=diario">🧭</a>
      <a class="omni-btn" href="?go=mon">📈</a>
    </div>
    """, unsafe_allow_html=True)
