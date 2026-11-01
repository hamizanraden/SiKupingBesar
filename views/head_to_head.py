import plotly.express as px
import streamlit as st
from core.stats import match_probs
from ui import components as C, theme
from ui.state import get_ctx

ctx = get_ctx(); ts = ctx.res.teams
a, b = st.columns(2)
A = a.selectbox("Tim kandang", ts, 0); B = b.selectbox("Tim tandang", ts, 1)
if A == B:
    st.warning("Pilih dua tim berbeda.")
else:
    lh, la = ctx.ratings.lam(A, B, ctx.ratings.H if ctx.params.home_adv is None else ctx.params.home_adv)
    w, d, l, m = match_probs(lh, la)
    C.render("prob_pills.html", height=230, home=A, away=B, w=w, d=d, l=l, lh=lh, la=la)
    st.subheader("Matriks skor")
    st.plotly_chart(px.imshow(m[:6, :6]*100, x=list(range(6)), y=list(range(6)), text_auto=".1f",
                    labels=dict(x=f"Gol {B}", y=f"Gol {A}", color="%"), color_continuous_scale=theme.SCALE)
                    .update_layout(height=450), width="stretch")
