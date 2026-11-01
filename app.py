"""Pintu masuk: streamlit run app.py"""
import streamlit as st
from ui import sidebar, theme

st.set_page_config(page_title="SiKupingBesar", layout="wide")
theme.inject_css()
sidebar.render()

pages = [
    st.Page("views/dashboard.py", title="Dashboard", default=True),
    st.Page("views/tabel.py", title="Tabel"),
    st.Page("views/head_to_head.py", title="Head-to-Head"),
    st.Page("views/statistik.py", title="Statistik"),
    st.Page("views/metodologi.py", title="Metodologi"),
]
try:
    nav = st.navigation(pages, position="top")
except TypeError:                     # Streamlit lama: navigasi di sidebar
    nav = st.navigation(pages)
nav.run()
