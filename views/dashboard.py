import plotly.express as px, plotly.graph_objects as go
import streamlit as st
from ui import components as C, theme
from ui.state import get_ctx

ctx = get_ctx(); tb = ctx.res.table; p = ctx.params
top3 = [dict(name=r["Tim"], pct=r["Juara"]*100, lo=r["CI95 bawah"]*100, hi=r["CI95 atas"]*100)
        for r in tb.head(3).to_dict("records")]
C.render("hero.html", height=330, teams=top3, eyebrow="PREDIKSI JUARA LIGA CHAMPIONS",
         title="Siapa juara musim ini?",
         subtitle=f"{p.n_sim:,} simulasi Monte Carlo, gol tiap laga ~ Poisson, data per {ctx.data_date:%d %b %Y}.")

c1, c2 = st.columns([1.2, 1])
top = tb.head(10).iloc[::-1]
fig = go.Figure(go.Bar(x=top["Juara"]*100, y=top["Tim"], orientation="h", marker_color=theme.GOLD,
                       error_x=dict(type="data", symmetric=False, array=(top["CI95 atas"]-top["Juara"])*100,
                                    arrayminus=(top["Juara"]-top["CI95 bawah"])*100)))
fig.update_layout(title="Peluang juara (%) dengan CI 95%", height=430, margin=dict(l=0, r=0, t=40, b=0),
                  paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
c1.plotly_chart(fig, use_container_width=True)
with c2:
    C.render("standings.html", height=520, title="Klasemen proyeksi",
             rows=tb.sort_values("Rata-rata posisi").head(8).to_dict("records"))

st.subheader("Peluang mencapai tiap babak")
stages = ["Top 8", "Top 24", "R16", "QF", "SF", "Final", "Juara"]
hm = tb.head(12).set_index("Tim")[stages]*100
st.plotly_chart(px.imshow(hm, text_auto=".0f", aspect="auto", color_continuous_scale=theme.SCALE)
                .update_layout(height=450, margin=dict(l=0, r=0, t=10, b=0)), use_container_width=True)
