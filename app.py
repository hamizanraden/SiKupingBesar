"""Pintu masuk: streamlit run app.py"""
import streamlit as st
from ui import navbar, state, theme

st.set_page_config(page_title="SiKupingBesar", layout="wide", initial_sidebar_state="collapsed")
theme.inject_css()

pages = [
    st.Page("views/dashboard.py", title="Dashboard", default=True),
    st.Page("views/tabel.py", title="Tabel"),
    st.Page("views/simulator.py", title="Simulator"),
    st.Page("views/head_to_head.py", title="Head-to-Head"),
    st.Page("views/statistik.py", title="Statistik"),
    st.Page("views/metodologi.py", title="Metodologi"),
]
nav = st.navigation(pages, position="hidden")   # menu bawaan disembunyikan
navbar.render(pages, nav)                       # diganti navbar buatan sendiri
state.build_ctx()                               # data + simulasi, dibagi ke semua halaman
nav.run()
