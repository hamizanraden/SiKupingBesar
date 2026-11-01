import numpy as np, plotly.graph_objects as go
import streamlit as st
from core.stats import convergence, chi_square_poisson, brier_1x2
from ui.state import get_ctx

ctx = get_ctx(); res = ctx.res; tb = res.table
st.subheader("Konvergensi (Law of Large Numbers)")
pick = st.selectbox("Tim", tb.Tim.tolist())
cv = convergence(res.champions, res.teams.index(pick))
f = go.Figure()
f.add_trace(go.Scatter(x=cv.n, y=cv.hi*100, line=dict(width=0), showlegend=False))
f.add_trace(go.Scatter(x=cv.n, y=cv.lo*100, fill="tonexty", fillcolor="rgba(255,184,0,.3)", line=dict(width=0), name="CI 95%"))
f.add_trace(go.Scatter(x=cv.n, y=cv.p*100, line=dict(color="#B37A00", width=3), name="Peluang juara"))
f.update_layout(xaxis_type="log", xaxis_title="Jumlah simulasi", yaxis_title="%", height=380)
st.plotly_chart(f, use_container_width=True)

st.subheader("Validasi model")
m = ctx.matches; u = m[m.competition == "UCL"].dropna(subset=["home_goals"])
cs = chi_square_poisson(np.concatenate([u.home_goals, u.away_goals]))
c1, c2 = st.columns(2)
c1.metric("Chi-square gol ~ Poisson", f"χ²={cs['chi2']:.2f}, dof={cs['dof']}", f"p-value {cs['p_value']:.3f}", delta_color="off")
c1.caption("H₀: gol per tim per laga berdistribusi Poisson. p > 0,05 berarti tidak ada bukti untuk menolak H₀.")
bs, nb = brier_1x2(m, ctx.ratings)
c2.metric("Brier score 1X2 (in-sample)", f"{bs:.3f}", f"n={nb} laga · acuan acak 0,667", delta_color="off")
