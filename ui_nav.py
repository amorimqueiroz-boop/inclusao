import streamlit as st
import base64
import os

# =========================
# CONFIGURAÇÃO DE ROTAS
# =========================
PAGES = {
    "home":   "home_portal.py",
    "alunos": "pages/0_Alunos.py",
    "pei":    "pages/1_PEI.py",
    "paee":   "pages/2_PAE.py",
    "hub":    "pages/3_Hub_Inclusao.py",
}

COLORS = {
    "home": "#111827", "alunos": "#2563EB", "pei": "#3B82F6",
    "paee": "#10B981", "hub": "#F59E0B", "sair": "#EF4444"
}

ICONS = {
    "home": "fi fi-sr-home", "alunos": "fi fi-sr-users", "pei": "fi fi-sr-puzzle-alt",
    "paee": "fi fi-sr-route", "hub": "fi fi-sr-lightbulb-on", "sair": "fi fi-sr-exit"
}

# =========================
# FUNÇÕES AUXILIARES
# =========================
def _b64(path: str) -> str:
    if not os.path.exists(path): return ""
    with open(path, "rb") as f: return base64.b64encode(f.read()).decode()

def _check_navigation():
    """Verifica se há um pedido de troca de página via Query Params"""
    try:
        qp = st.query_params
        if "go" in qp:
            page_key = qp["go"]
            # Limpa o param para não ficar em loop
            st.query_params.clear()
            if page_key in PAGES:
                st.switch_page(PAGES[page_key])
    except Exception:
        pass

# =========================
# O ESTILO "NUCLEAR" (CSS)
# =========================
def _inject_css():
    st.markdown("""
        <link rel="stylesheet" href="https://cdn-uicons.flaticon.com/3.0.0/uicons-solid-rounded/css/uicons-solid-rounded.css">
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap" rel="stylesheet">
        
        <style>
            /* 1. Ocultar completamente o Header e Toolbar nativos do Streamlit */
            header[data-testid="stHeader"] {
                display: none !important;
                visibility: hidden !important;
                height: 0 !important;
            }
            [data-testid="stToolbar"] {
                display: none !important;
            }
            
            /* 2. Remover a Sidebar nativa visualmente (caso o config falhe) */
            [data-testid="stSidebar"] {
                display: none !important;
            }

            /* 3. Ajustar o layout principal para colar no topo e dar espaço ao menu */
            .block-container {
                padding-top: 7rem !important; /* Espaço para o menu não cobrir o título */
                padding-bottom: 2rem !important;
                max-width: 95% !important;
            }

            /* 4. Estilo do Menu Personalizado (OmniBar) */
            .omni-topbar {
                position: fixed;
                top: 0; left: 0; right: 0;
                height: 64px;
                background: white;
                border-bottom: 1px solid #E2E8F0;
                display: flex; align-items: center; justify-content: space-between;
                padding: 0 24px;
                z-index: 999999; /* Fica acima de tudo */
                box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
                font-family: 'Inter', sans-serif;
            }

            .omni-logo-area { display: flex; align-items: center; gap: 12px; }
            .omni-logo-img { height: 32px; width: 32px; border-radius: 50%; object-fit: cover; }
            .omni-app-title { font-weight: 800; font-size: 14px; color: #0F172A; letter-spacing: 0.05em; }

            .omni-nav-items { display: flex; gap: 8px; align-items: center; }
            
            /* Botões de Navegação */
            .omni-nav-btn {
                text-decoration: none;
                width: 42px; height: 42px;
                display: flex; align-items: center; justify-content: center;
                border-radius: 10px;
                color: #64748B;
                transition: all 0.2s ease;
                position: relative;
            }
            .omni-nav-btn:hover { background-color: #F1F5F9; color: #0F172A; transform: translateY(-1px); }
            .omni-nav-btn.active { background-color: #EFF6FF; color: #2563EB; }
            .omni-nav-btn i { font-size: 20px; }

            /* Tooltip Customizado */
            .omni-nav-btn::after {
                content: attr(data-title);
                position: absolute;
                bottom: -32px; left: 50%; transform: translateX(-50%);
                background: #1E293B; color: white;
                padding: 4px 8px; border-radius: 6px;
                font-size: 11px; font-weight: 600;
                white-space: nowrap; opacity: 0; pointer-events: none;
                transition: opacity 0.2s;
            }
            .omni-nav-btn:hover::after { opacity: 1; }
            
            .omni-divider { width: 1px; height: 24px; background: #E2E8F0; margin: 0 8px; }

        </style>
    """, unsafe_allow_html=True)

# =========================
# RENDER PRINCIPAL
# =========================
def render_topbar_nav(active_page: str):
    # 1. Checa se precisa navegar antes de desenhar
    _check_navigation()
    
    # 2. Injeta o CSS que mata o menu antigo
    _inject_css()

    # 3. Prepara Logo
    logo_b64 = _b64("omni_icone.png")
    logo_src = f"data:image/png;base64,{logo_b64}" if logo_b64 else ""
    logo_html = f'<img src="{logo_src}" class="omni-logo-img">' if logo_b64 else '<div style="width:32px;height:32px;background:#ddd;border-radius:50%"></div>'

    # 4. Monta os Links HTML
    nav_html = ""
    for key, label in [("home","Home"), ("alunos","Alunos"), ("pei","PEI"), ("paee","PAE"), ("hub","Hub")]:
        is_active = "active" if key == active_page else ""
        icon = ICONS.get(key, "fi fi-sr-circle")
        # O truque: href="?go=key" força o reload e o _check_navigation pega
        nav_html += f"""
        <a href="?go={key}" class="omni-nav-btn {is_active}" data-title="{label}">
            <i class="{icon}"></i>
        </a>
        """

    # 5. Renderiza a Barra Fixa
    st.markdown(f"""
        <div class="omni-topbar">
            <div class="omni-logo-area">
                {logo_html}
                <span class="omni-app-title">OMNISFERA</span>
            </div>
            <div class="omni-nav-items">
                {nav_html}
                <div class="omni-divider"></div>
                <a href="?go=home" class="omni-nav-btn" data-title="Sair" style="color: #EF4444;">
                    <i class="fi fi-sr-exit"></i>
                </a>
            </div>
        </div>
    """, unsafe_allow_html=True)
