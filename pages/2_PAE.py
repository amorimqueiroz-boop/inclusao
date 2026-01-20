import streamlit as st

def render_topbar_nav():
    st.markdown("""
    <style>
      .omni-topbar{position:fixed;top:0;left:0;right:0;height:56px;z-index:999999;
      background:#fff;border-bottom:1px solid #eee;display:flex;align-items:center;justify-content:space-between;padding:0 16px;}
      .omni-topbar a{text-decoration:none;margin-left:12px;font-size:20px;color:#444;}
      .block-container{padding-top:74px !important;}
    </style>
    <div class="omni-topbar">
      <div style="font-weight:900;letter-spacing:.6px">OMNISFERA</div>
      <div>
        <a href="?view=home" target="_self">🏠</a>
        <a href="?view=pei" target="_self">🧩</a>
        <a href="?view=paee" target="_self">📍</a>
        <a href="?view=hub" target="_self">💡</a>
      </div>
    </div>
    """, unsafe_allow_html=True)
