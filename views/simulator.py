"""Halaman Simulator: unggah data dan atur parameter. Perubahan langsung dipakai semua halaman."""
import streamlit as st
from core.pipeline import Params
from ui.state import get_ctx, get_params, set_params

_KEYS = ["w_n_sim", "w_seed", "w_auto_h", "w_h", "w_hl", "w_dw"]

def _sync():
    s = st.session_state
    set_params(Params(n_sim=int(s["w_n_sim"]), seed=int(s["w_seed"]),
                      home_adv=None if s["w_auto_h"] else float(s["w_h"]),
                      half_life=float(s["w_hl"]), domestic_weight=float(s["w_dw"])))

def _upload():
    f = st.session_state["w_upload"]
    if f is None: st.session_state.pop("upload_bytes", None)
    else: st.session_state["upload_bytes"] = f.getvalue()

def _reset():
    for k in _KEYS: st.session_state.pop(k, None)
    set_params(Params())

p = get_params(); ctx = get_ctx()
st.title("Simulator")
st.caption("Atur data dan parameter model. Hasil di semua halaman ikut diperbarui otomatis.")

left, right = st.columns(2, gap="large")
with left, st.container(border=True):
    st.subheader("Data")
    st.file_uploader("Dataset laga (CSV)", type="csv", key="w_upload", on_change=_upload)
    st.caption("Kolom: date, home, away, home_goals, away_goals, competition (isi 'UCL' untuk laga UCL).")
    if ctx.synthetic:
        st.warning("Memakai data SINTETIS (data/sample_matches.csv). Ganti dengan datasetmu.")
    if ctx.name_warnings:
        pairs = "; ".join(f"“{a}” vs “{b}”" for a, b in ctx.name_warnings[:5])
        st.warning(f"Nama tim sangat mirip, cek lagi ejaannya: {pairs}.")
    m = ctx.matches
    st.metric("Laga dalam dataset", f"{len(m):,}", f"data per {ctx.data_date:%d %b %Y}", delta_color="off")

with right, st.container(border=True):
    st.subheader("Parameter model")
    st.select_slider("Jumlah simulasi", [1000, 5000, 10000, 50000, 100000], p.n_sim, key="w_n_sim", on_change=_sync)
    st.checkbox("Home advantage dari data", p.home_adv is None, key="w_auto_h", on_change=_sync)
    st.slider("Home advantage", 1.0, 1.6, float(1.25 if p.home_adv is None else p.home_adv), .01, key="w_h", on_change=_sync,
              disabled=st.session_state.get("w_auto_h", p.home_adv is None))
    st.slider("Bobot form: half-life (minggu)", 2, 26, int(p.half_life), key="w_hl", on_change=_sync,
              help="Makin kecil, laga lama makin cepat dianggap tidak relevan.")
    st.slider("Bobot laga liga domestik", 0.1, 1.0, float(p.domestic_weight), .05, key="w_dw", on_change=_sync,
              help="Bobot laga liga dibanding laga UCL (bobot 1,0).")
    st.number_input("Seed", 0, 99999, int(p.seed), key="w_seed", on_change=_sync)
    st.button("Kembalikan ke default", on_click=_reset)
