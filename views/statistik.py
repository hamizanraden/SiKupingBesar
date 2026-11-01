import numpy as np, pandas as pd, plotly.graph_objects as go
import streamlit as st
from core.stats import brier_1x2, chi_square_poisson, convergence
from ui.state import get_ctx

ctx = get_ctx(); res = ctx.res; tb = res.table

st.subheader("Konvergensi (Law of Large Numbers)")
pick = st.selectbox("Tim", tb.Tim.tolist())
cv = convergence(res.champions, res.teams.index(pick))
f = go.Figure()
f.add_trace(go.Scatter(x=cv.n, y=cv.hi*100, line=dict(width=0), showlegend=False, hoverinfo="skip"))
f.add_trace(go.Scatter(x=cv.n, y=cv.lo*100, fill="tonexty", fillcolor="rgba(255,184,0,.3)",
                       line=dict(width=0), name="CI 95%"))
f.add_trace(go.Scatter(x=cv.n, y=cv.p*100, line=dict(color="#B37A00", width=3), name="Peluang juara"))
f.update_layout(xaxis_type="log", xaxis_title="Jumlah simulasi", yaxis_title="%", height=380,
                legend=dict(orientation="h", yanchor="bottom", y=1.02))
st.plotly_chart(f, width="stretch")
st.caption(
    f"Peluang juara {pick} setelah N simulasi pertama. Pita CI Wilson 95% menyempit seiring N bertambah: "
    "inilah Law of Large Numbers — dugaan makin stabil ketika jumlah percobaan diperbesar."
)

st.subheader("Validasi model")
m = ctx.matches
u = m[m.competition == "UCL"].dropna(subset=["home_goals", "away_goals"])
if u.empty:
    st.info("Belum ada laga UCL yang sudah dimainkan, jadi uji Chi-square dan Brier score belum bisa dihitung.")
    st.stop()
cs = chi_square_poisson(np.concatenate([u.home_goals, u.away_goals]))

st.markdown("**Uji Chi-square kecocokan Poisson**")
st.markdown(
    "H₀: gol per tim per laga berdistribusi Poisson.  \n"
    "H₁: gol per tim per laga tidak berdistribusi Poisson.  \n"
    "Tolak H₀ bila p-value < 0,05."
)
c1, c2, c3 = st.columns(3)
c1.metric("Statistik χ²", f"{cs['chi2']:.2f}")
c2.metric("Derajat bebas", cs["dof"])
c3.metric("p-value", f"{cs['p_value']:.3f}")

if cs["p_value"] >= 0.05:
    st.success("p ≥ 0,05 → tidak cukup bukti untuk menolak H₀. Asumsi Poisson masih wajar untuk data ini.")
else:
    st.warning("p < 0,05 → H₀ ditolak. Asumsi Poisson kurang cocok; hasil simulasi perlu dibaca lebih hati-hati.")

labels = [str(i) for i in range(len(cs["obs"]) - 1)] + [f"≥{len(cs['obs']) - 1}"]
tab = pd.DataFrame({
    "Gol per tim per laga": labels,
    "Observasi": cs["obs"].astype(int),
    "Ekspektasi Poisson": cs["exp"].round(2),
})
st.dataframe(tab, hide_index=True, width="stretch")
st.caption(
    f"n = {len(u) * 2:,} tim-laga UCL, rata-rata {cs['lam']:.2f} gol. Uji ini memakai gol kandang dan tandang "
    "digabung; independensi gol kedua tim tidak diuji di sini."
)

st.markdown("**Brier score 1X2**")
bs, nb = brier_1x2(m, ctx.ratings)
c1, c2 = st.columns(2)
c1.metric("Brier score (in-sample)", f"{bs:.3f}", f"{bs - 2/3:+.3f} vs tebak acak", delta_color="inverse")
c2.metric("Acuan tebak seragam", "0,667", "selalu 1/3 – 1/3 – 1/3", delta_color="off")
st.caption(
    f"Dihitung dari {nb} laga UCL yang sudah dimainkan. Makin kecil makin baik. Skor ini in-sample "
    "(laga yang sama dipakai untuk mengestimasi rating), jadi cenderung optimistis."
)
