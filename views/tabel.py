import streamlit as st
from ui.state import get_ctx

tb = get_ctx().res.table
stages = ["Top 8", "Top 24", "R16", "QF", "SF", "Final", "Juara"]
st.subheader("Probabilitas lengkap 36 tim")
show = tb.copy(); show[stages] = show[stages]*100
st.dataframe(show.drop(columns=["CI95 bawah", "CI95 atas"]), hide_index=True, use_container_width=True,
             column_config={c: st.column_config.NumberColumn(format="%.1f%%") for c in stages})
st.download_button("Unduh CSV", tb.to_csv(index=False), "hasil_simulasi.csv")
