"""Simulasi Monte Carlo satu musim UCL (format 36 tim: league phase -> playoff -> knockout)."""
from dataclasses import dataclass
import numpy as np, pandas as pd
from .ratings import Ratings
from .stats import wilson_ci

@dataclass
class SimResult:
    table: pd.DataFrame
    champions: np.ndarray   # (n_sim,) indeks tim juara per simulasi
    teams: list
    n_sim: int

class _Engine:
    def __init__(s, mu, H, A, D, rng):
        s.mu, s.H, s.A, s.D, s.rng = mu, H, A, D, rng
    def goals(s, home, away, hfa=True):
        h = s.H if hfa else 1.0
        return (s.rng.poisson(s.mu*h*s.A[home]*s.D[away]),
                s.rng.poisson(s.mu*s.A[away]*s.D[home]))
    def two_leg(s, hi, lo):
        """hi = unggulan (leg 2 kandang). Imbang agregat -> 50:50 (perpanjangan/penalti)."""
        g1_lo, g1_hi = s.goals(lo, hi)
        g2_hi, g2_lo = s.goals(hi, lo)
        a_hi, a_lo = g1_hi+g2_hi, g1_lo+g2_lo
        win = (a_hi > a_lo) | ((a_hi == a_lo) & (s.rng.random(len(hi)) < .5))
        return np.where(win, hi, lo)
    def final(s, x, y):
        gx, gy = s.goals(x, y, hfa=False)
        win = (gx > gy) | ((gx == gy) & (s.rng.random(len(x)) < .5))
        return np.where(win, x, y)

def simulate_season(r: Ratings, matches, n_sim=10000, seed=42, home_adv=None):
    ucl = matches[matches.competition == "UCL"]
    teams = sorted(set(ucl.home) | set(ucl.away)); T = len(teams)
    if T != 36:
        raise ValueError(f"Format UCL 2024+ butuh 36 tim, ditemukan {T}.")
    loc = {t: i for i, t in enumerate(teams)}
    H = r.H if home_adv is None else home_adv
    ridx = np.array([r.index[t] for t in teams])
    A, D = r.a[ridx], r.d[ridx]
    rng = np.random.default_rng(seed); n = n_sim
    done = ucl.dropna(subset=["home_goals", "away_goals"])
    todo = ucl[ucl.home_goals.isna() | ucl.away_goals.isna()]
    pts = np.zeros((n, T)); gf = np.zeros((n, T)); gc = np.zeros((n, T))
    def add(h, a, gh, ga):
        pts[:, h] += 3*(gh > ga) + (gh == ga); pts[:, a] += 3*(ga > gh) + (gh == ga)
        gf[:, h] += gh; gc[:, h] += ga; gf[:, a] += ga; gc[:, a] += gh
    for row in done.itertuples():
        add(loc[row.home], loc[row.away], row.home_goals, row.away_goals)
    for row in todo.itertuples():
        h, a = loc[row.home], loc[row.away]
        add(h, a, rng.poisson(r.mu*H*A[h]*D[a], n), rng.poisson(r.mu*A[a]*D[h], n))
    key = pts*1e4 + (gf-gc)*1e2 + gf + rng.random((n, T))   # poin > selisih gol > gol > acak
    order = np.argsort(-key, axis=1); pos = np.argsort(order, axis=1)
    eng = _Engine(r.mu, H, A, D, rng)
    rows = np.arange(n)
    # playoff: peringkat 9-16 (unggulan) vs 24-17
    po = [eng.two_leg(order[:, 8+j], order[:, 23-j]) for j in range(8)]
    # R16: peringkat k vs pemenang playoff (1<-16v17, 2<-15v18, ..., 8<-9v24)
    r16 = [eng.two_leg(order[:, k], po[7-k]) for k in range(8)]
    def seeded(x, y):
        better = pos[rows, x] < pos[rows, y]
        return eng.two_leg(np.where(better, x, y), np.where(better, y, x))
    qf = [seeded(r16[i], r16[j]) for i, j in [(0, 7), (3, 4), (2, 5), (1, 6)]]
    sf = [seeded(qf[0], qf[1]), seeded(qf[2], qf[3])]
    champ = eng.final(sf[0], sf[1])
    cnt = lambda *arrs: np.bincount(np.concatenate([np.ravel(a) for a in arrs]), minlength=T)/n
    df = pd.DataFrame({
        "Tim": teams, "Rata-rata poin": pts.mean(0), "Rata-rata posisi": pos.mean(0)+1,
        "Top 8": cnt(order[:, :8]), "Top 24": cnt(order[:, :24]),
        "R16": cnt(order[:, :8], *po), "QF": cnt(*r16), "SF": cnt(*qf),
        "Final": cnt(*sf), "Juara": cnt(champ)})
    ci = [wilson_ci(int(round(p*n)), n) for p in df["Juara"]]
    df["CI95 bawah"] = [c[0] for c in ci]; df["CI95 atas"] = [c[1] for c in ci]
    return SimResult(df.sort_values("Juara", ascending=False).reset_index(drop=True), champ, teams, n_sim)
