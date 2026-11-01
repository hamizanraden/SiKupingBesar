"""Penghubung Streamlit <-> core: parameter, data, cache, dan konteks yang dibagi ke semua halaman."""
import io
from dataclasses import dataclass, field
from pathlib import Path
import streamlit as st
from core import pipeline
from core.pipeline import Params

DATA = Path(__file__).resolve().parent.parent / "data"

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
    name_warnings: list = field(default_factory=list)

def get_params() -> Params:
    return st.session_state.setdefault("params", Params())

def set_params(p: Params):
    st.session_state["params"] = p

def build_ctx() -> Ctx:
    """Muat data + jalankan simulasi (di-cache) dengan parameter tersimpan, lalu bagikan ke halaman."""
    matches, synthetic = None, False
    up = st.session_state.get("upload_bytes")
    if up:
        try:
            matches = pipeline.load_matches(io.BytesIO(up))
        except ValueError as e:
            st.error(f"Unggahan ditolak: {e}")
            st.session_state.pop("upload_bytes", None)
    if matches is None:
        path = DATA / "matches.csv"
        if not path.exists():
            path, synthetic = DATA / "sample_matches.csv", True
        try:
            matches = pipeline.load_matches(path)
        except (ValueError, FileNotFoundError) as e:
            st.error(str(e)); st.stop()
    p = get_params()
    r, res = cached_run(matches, p)
    ctx = Ctx(matches, r, res, p, synthetic, pipeline.data_date(matches), pipeline.suspicious_names(matches))
    st.session_state["ctx"] = ctx
    return ctx

def get_ctx() -> Ctx:
    return st.session_state.get("ctx") or build_ctx()
