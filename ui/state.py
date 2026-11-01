"""Penghubung Streamlit <-> core: cache dan konteks yang dibagi ke semua halaman."""
from dataclasses import dataclass
import streamlit as st
from core import pipeline
from core.pipeline import Params

@st.cache_data(show_spinner="Menjalankan simulasi...")
def cached_run(matches, p: Params):
    return pipeline.run(matches, p)

@dataclass
class Ctx:
    matches: object
    ratings: object
    res: object
    params: Params
    synthetic: bool
    data_date: object

def set_ctx(c: Ctx): st.session_state["ctx"] = c
def get_ctx() -> Ctx:
    if "ctx" not in st.session_state:
        from ui import sidebar
        sidebar.render()
    return st.session_state["ctx"]
