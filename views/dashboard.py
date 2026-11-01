import numpy as np, plotly.express as px, plotly.graph_objects as go
import streamlit as st
from core.stats import match_probs
from ui import components as C, theme
from ui.state import get_ctx

ctx = get_ctx(); tb = ctx.res.table; p = ctx.params; r = ctx.ratings
u = ctx.matches[ctx.matches.competition == "UCL"]
sisa = int((u.home_goals.isna() | u.away_goals.isna()).sum())
lead = tb.iloc[0]
h_used = r.H if p.home_adv is None else p.home_adv

# --- Sekilas simulasi (kartu ringkas yang dihitung dari hasil) ---
C.render("glance.html", height=185, tiles=[
    dict(label="Favorit juara", value=f"{lead['Juara']*100:.1f}%", sub=lead["Tim"]),
    dict(label="Peluang Top 8 di atas 50%", value=f"{int((tb['Top 8'] > .5).sum())} tim", sub="lolos langsung ke R16"),
    dict(label="Jumlah simulasi", value=f"{p.n_sim:,}", sub=f"seed {p.seed}"),
    dict(label="Home advantage", value=f"{h_used:.2f}×", sub="dari data" if p.home_adv is None else "diatur manual"),
    dict(label="Laga UCL tersisa", value=str(sisa), sub=f"data per {ctx.data_date:%d %b %Y}"),
])

main, side = st.columns([2.1, 1], gap="large")

with main:
    top3 = [dict(name=x["Tim"], pct=x["Juara"]*100, lo=x["CI95 bawah"]*100, hi=x["CI95 atas"]*100)
            for x in tb.head(3).to_dict("records")]
    C.render("hero.html", height=340, teams=top3, eyebrow=f"MUSIM UCL · {p.n_sim:,} SIMULASI",
             title="Siapa juara Liga Champions musim ini?",
             subtitle="Prediksi berbasis simulasi Monte Carlo dengan gol tiap laga mengikuti distribusi Poisson.")
    top = tb.head(10).iloc[::-1]
    fig = go.Figure(go.Bar(x=top["Juara"]*100, y=top["Tim"], orientation="h", marker_color=theme.GOLD,
                           error_x=dict(type="data", symmetric=False, array=(top["CI95 atas"]-top["Juara"])*100,
                                        arrayminus=(top["Juara"]-top["CI95 bawah"])*100)))
    fig.update_layout(title="Peluang juara (%) dengan CI 95%", height=430, margin=dict(l=0, r=0, t=40, b=0),
                      paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig, width="stretch")
    st.subheader("Peluang mencapai tiap babak")
    stages = ["Top 8", "Top 24", "R16", "QF", "SF", "Final", "Juara"]
    hm = tb.head(12).set_index("Tim")[stages]*100
    st.plotly_chart(px.imshow(hm, text_auto=".0f", aspect="auto", color_continuous_scale=theme.SCALE)
                    .update_layout(height=450, margin=dict(l=0, r=0, t=10, b=0)), width="stretch")

with side:
    a, b = tb.iloc[0]["Tim"], tb.iloc[1]["Tim"]
    w, d, l, m = match_probs(*r.lam(a, b, h_used))
    i, j = np.unravel_index(m.argmax(), m.shape)
    C.render("side_panel.html", height=1010,
             rows=tb.sort_values("Rata-rata posisi").head(5).to_dict("records"),
             h2h=dict(home=a, away=b, w=w, d=d, l=l, score=f"{i}-{j}", score_p=float(m[i, j])),
             settings=[("Jumlah simulasi", f"{p.n_sim:,}"),
                       ("Home advantage", f"{h_used:.2f}×" + (" (data)" if p.home_adv is None else "")),
                       ("Half-life form", f"{p.half_life:g} minggu"),
                       ("Bobot liga domestik", f"{p.domestic_weight:.2f}"),
                       ("Seed", str(p.seed))])
    st.page_link("views/simulator.py", label="Ubah pengaturan simulasi")
