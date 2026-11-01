"""Warna dan CSS global. Tema dasar ada di .streamlit/config.toml."""
import streamlit as st

GOLD, GOLD_DARK, INK, CREAM = "#FFB800", "#B37A00", "#1A1400", "#FFFBEF"
SCALE = [CREAM, GOLD, GOLD_DARK]          # skala warna heatmap Plotly

_CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700&display=swap');
.stApp {{ font-family: Outfit, sans-serif; background: {CREAM}; }}

/* tanpa sidebar dan tanpa header bawaan: menu ada di navbar */
[data-testid="stSidebar"], [data-testid="stSidebarCollapsedControl"],
[data-testid="stHeader"], [data-testid="stToolbar"] {{ display: none !important; }}
html, body, .stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"] {{ overflow-x: hidden; }}
[data-testid="stMainBlockContainer"], .block-container {{
    max-width: 1400px; padding: 0 32px 3rem 32px !important; }}

h1, h2, h3 {{ color: {INK}; letter-spacing: -0.01em; font-weight: 600; }}
[data-testid="stMetric"] {{ background:#fff; border:1px solid #F0E6C8; border-radius:18px; padding:16px 20px; }}
[data-testid="stVerticalBlockBorderWrapper"] {{ background:#fff; border:1px solid #F0E6C8 !important; border-radius:24px; }}
.stButton > button, .stDownloadButton > button {{ border-radius:999px; background:{GOLD}; color:{INK}; border:0; font-weight:600; }}
[data-testid="stDataFrame"] {{ border-radius:16px; overflow:hidden; }}
</style>
"""

def inject_css():
    st.markdown(_CSS, unsafe_allow_html=True)
