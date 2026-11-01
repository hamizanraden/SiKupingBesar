"""Warna dan CSS tambahan. Tema dasar ada di .streamlit/config.toml."""
import streamlit as st

GOLD, GOLD_DARK, INK, CREAM = "#FFB800", "#B37A00", "#1A1400", "#FFFBEF"
SCALE = [CREAM, GOLD, GOLD_DARK]          # skala warna heatmap Plotly

_CSS = f"""
<style>
.block-container {{ padding-top: 2rem; max-width: 1280px; }}
h1, h2, h3 {{ color: {INK}; letter-spacing: -0.01em; }}
[data-testid="stMetric"] {{ background:#fff; border:1px solid #F0E6C8; border-radius:18px; padding:16px 20px; }}
.stButton > button, .stDownloadButton > button {{ border-radius:999px; background:{GOLD}; color:{INK}; border:0; font-weight:600; }}
[data-testid="stDataFrame"] {{ border-radius:16px; overflow:hidden; }}
</style>
"""

def inject_css():
    st.markdown(_CSS, unsafe_allow_html=True)
