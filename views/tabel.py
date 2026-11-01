import streamlit as st
from ui.state import get_ctx

ctx = get_ctx(); tb = ctx.res.table; p = ctx.params

st.subheader("Probabilitas lengkap 36 tim")
st.caption(
    f"Data per {ctx.data_date:%d %b %Y} · {p.n_sim:,} simulasi · seed {p.seed} · "
    "klik judul kolom untuk mengurutkan."
)

stages = ["Top 8", "Top 24", "R16", "QF", "SF", "Final", "Juara"]
ci = ["CI95 bawah", "CI95 atas"]
show = tb.copy()
show[stages + ci] = show[stages + ci] * 100
show = show.rename(columns={"CI95 bawah": "CI95 juara bawah", "CI95 atas": "CI95 juara atas"})

pct = {c: st.column_config.NumberColumn(format="%.1f%%")
       for c in stages + ["CI95 juara bawah", "CI95 juara atas"]}
pct["Rata-rata poin"] = st.column_config.NumberColumn(format="%.2f")
pct["Rata-rata posisi"] = st.column_config.NumberColumn(format="%.1f")

st.dataframe(show, hide_index=True, width="stretch", height=660, column_config=pct)
st.download_button("Unduh CSV", tb.to_csv(index=False), "hasil_simulasi.csv", mime="text/csv")
st.caption(
    "CI95 juara = interval kepercayaan Wilson 95% untuk peluang juara. "
    "Semua angka adalah peluang hasil simulasi, bukan jaminan."
)
