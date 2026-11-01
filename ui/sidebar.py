"""Panel parameter (kiri). Dipanggil sekali di app.py, hasilnya dibagi ke semua halaman."""
import io
from pathlib import Path
import streamlit as st
from core import pipeline
from core.pipeline import Params
from ui.state import Ctx, cached_run, set_ctx

DATA = Path(__file__).resolve().parent.parent / "data"

def render():
    sb = st.sidebar
    sb.header("Data & parameter")
    up = sb.file_uploader("Dataset laga (CSV)", type="csv")
    sb.caption("Kolom: date, home, away, home_goals, away_goals, competition (isi 'UCL' untuk laga UCL)")
    if up is not None: src, synthetic = io.BytesIO(up.getvalue()), False
    elif (DATA/"matches.csv").exists(): src, synthetic = DATA/"matches.csv", False
    else: src, synthetic = DATA/"sample_matches.csv", True
    try:
        matches = pipeline.load_matches(src)
    except (ValueError, FileNotFoundError) as e:
        sb.error(str(e)); st.stop()
    if synthetic:
        sb.warning("Memakai data SINTETIS (data/sample_matches.csv). Ganti dengan datasetmu.")
    n_sim = sb.select_slider("Jumlah simulasi", [1000, 5000, 10000, 50000, 100000], 10000)
    auto_h = sb.checkbox("Home advantage dari data", True)
    h = None if auto_h else sb.slider("Home advantage", 1.0, 1.6, 1.25, .01)
    hl = sb.slider("Bobot form: half-life (minggu)", 2, 26, 8)
    dw = sb.slider("Bobot laga liga domestik", 0.1, 1.0, 0.5, .05)
    seed = sb.number_input("Seed", 0, 99999, 42)
    p = Params(n_sim=int(n_sim), seed=int(seed), home_adv=h, half_life=float(hl), domestic_weight=float(dw))
    r, res = cached_run(matches, p)
    dd = pipeline.data_date(matches)
    sb.caption(f"Data per {dd:%d %b %Y}")
    set_ctx(Ctx(matches, r, res, p, synthetic, dd))
