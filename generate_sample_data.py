"""Membuat data SINTETIS (bukan data asli) untuk mencoba aplikasi dan menjalankan tes.
Hasil: data/sample_matches.csv"""
import numpy as np, pandas as pd

def make(seed=1):
    rng = np.random.default_rng(seed)
    N, LEAGUES = 36, 6
    teams = [f"Klub {i+1:02d}" for i in range(N)]
    att = rng.lognormal(0, .25, N); dfn = rng.lognormal(0, .25, N)
    MU, H = 1.35, 1.25
    rows = []
    def play(i, j, date, comp, played=True):
        gh = rng.poisson(MU*H*att[i]*dfn[j]); ga = rng.poisson(MU*att[j]*dfn[i])
        rows.append(dict(date=date, home=teams[i], away=teams[j],
                         home_goals=gh if played else np.nan,
                         away_goals=ga if played else np.nan, competition=comp))
    base = pd.Timestamp("2026-08-15")
    for L in range(LEAGUES):
        ids = range(L*6, L*6+6)
        for i in ids:
            for j in ids:
                if i != j:
                    play(i, j, base + pd.Timedelta(days=int(rng.integers(0, 78))), f"Liga {L+1}")
    played_dates = {1: ["2026-09-16", "2026-10-21"], 2: ["2026-09-30", "2026-10-28"]}
    for i in range(N):
        for k in (1, 2, 3, 4):
            j = (i + k) % N
            if k <= 2:
                play(i, j, pd.Timestamp(played_dates[k][i % 2]), "UCL", True)
            else:
                play(i, j, pd.Timestamp("2026-11-25") + pd.Timedelta(days=7*(k-3)), "UCL", False)
    return pd.DataFrame(rows).sort_values("date").reset_index(drop=True)

if __name__ == "__main__":
    df = make()
    df.to_csv("data/sample_matches.csv", index=False)
    print(len(df), "baris -> data/sample_matches.csv")
