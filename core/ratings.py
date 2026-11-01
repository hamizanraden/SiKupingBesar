"""Estimasi kekuatan serang/bertahan tiap tim dengan model Poisson.
lambda_home = mu * H * attack[home] * defense[away]
lambda_away = mu * attack[away] * defense[home]
(defense lebih besar = pertahanan lebih lemah)."""
from dataclasses import dataclass
import numpy as np, pandas as pd

@dataclass
class Ratings:
    index: dict
    a: np.ndarray
    d: np.ndarray
    mu: float
    H: float

    def lam(self, home, away, H=None):
        H = self.H if H is None else H
        i, j = self.index[home], self.index[away]
        return self.mu*H*self.a[i]*self.d[j], self.mu*self.a[j]*self.d[i]

def fit_ratings(matches, as_of=None, half_life_weeks=8.0, domestic_weight=0.5,
                home_adv=None, prior=2.0, iters=60):
    teams = sorted(set(matches.home) | set(matches.away))
    index = {t: i for i, t in enumerate(teams)}
    n = len(teams)
    p = matches.dropna(subset=["home_goals", "away_goals"]).copy()
    p["date"] = pd.to_datetime(p["date"])
    as_of = pd.to_datetime(as_of) if as_of is not None else p["date"].max()
    p = p[p["date"] <= as_of]
    age = (as_of - p["date"]).dt.days.to_numpy() / 7.0
    w = 0.5 ** (age / half_life_weeks) if half_life_weeks else np.ones(len(p))
    w = w * np.where(p["competition"].to_numpy() == "UCL", 1.0, domestic_weight)
    hi = p["home"].map(index).to_numpy(); ai = p["away"].map(index).to_numpy()
    gh = p["home_goals"].to_numpy(float); ga = p["away_goals"].to_numpy(float)
    a = np.ones(n); d = np.ones(n); mu = (gh.sum()+ga.sum()) / (2*len(p))
    H = 1.2 if home_adv is None else home_adv
    bc = lambda idx, v: np.bincount(idx, weights=v, minlength=n)
    for _ in range(iters):
        a = (bc(hi, w*gh)+bc(ai, w*ga)+prior) / (bc(hi, w*mu*d[ai]*H)+bc(ai, w*mu*d[hi])+prior)
        d = (bc(ai, w*gh)+bc(hi, w*ga)+prior) / (bc(ai, w*mu*a[hi]*H)+bc(hi, w*mu*a[ai])+prior)
        a /= np.exp(np.log(a).mean()); d /= np.exp(np.log(d).mean())
        base = a[hi]*d[ai]*H + a[ai]*d[hi]
        mu = (w*(gh+ga)).sum() / (w*base).sum()
        if home_adv is None:
            H = float(np.clip((w*gh).sum() / (w*mu*a[hi]*d[ai]).sum(), 1.0, 1.6))
    return Ratings(index, a, d, float(mu), float(H))
