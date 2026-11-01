"""Alat statistik: interval kepercayaan, konvergensi, Chi-square Poisson, Brier score, head-to-head."""
import math
import numpy as np, pandas as pd
from scipy import stats as sps

def wilson_ci(k, n, z=1.96):
    p = k/n; den = 1+z*z/n
    c = (p+z*z/(2*n))/den; h = z*math.sqrt(p*(1-p)/n + z*z/(4*n*n))/den
    return max(0.0, c-h), min(1.0, c+h)

def convergence(champions, team_idx, points=60):
    n = len(champions); hit = (champions == team_idx).cumsum()
    ks = np.unique(np.geomspace(50, n, points).astype(int))
    rows = []
    for k in ks:
        lo, hi = wilson_ci(int(hit[k-1]), int(k))
        rows.append((k, hit[k-1]/k, lo, hi))
    return pd.DataFrame(rows, columns=["n", "p", "lo", "hi"])

def poisson_matrix(lh, la, max_goals=12):
    k = np.arange(max_goals+1)
    pm = lambda lam: np.exp(-lam)*lam**k/np.array([math.factorial(i) for i in k])
    return np.outer(pm(lh), pm(la))

def match_probs(lh, la, max_goals=12):
    m = poisson_matrix(lh, la, max_goals)
    return float(np.tril(m, -1).sum()), float(np.trace(m)), float(np.triu(m, 1).sum()), m  # menang H, seri, menang A

def chi_square_poisson(goals, max_k=5):
    """Uji kecocokan: apakah gol per tim per laga ~ Poisson? Kelas terakhir = max_k atau lebih."""
    g = np.asarray(goals, int); n = len(g); lam = g.mean()
    obs = np.array([(g == k).sum() for k in range(max_k)] + [(g >= max_k).sum()], float)
    pk = np.array([sps.poisson.pmf(k, lam) for k in range(max_k)]); exp = np.append(pk, 1-pk.sum())*n
    while len(exp) > 2 and exp[-1] < 5:
        obs[-2] += obs[-1]; exp[-2] += exp[-1]; obs, exp = obs[:-1], exp[:-1]
    chi2 = float(((obs-exp)**2/exp).sum()); dof = len(obs)-2
    return dict(lam=float(lam), chi2=chi2, dof=dof, p_value=float(sps.chi2.sf(chi2, dof)), obs=obs, exp=exp)

def brier_1x2(matches, r):
    """Brier score 1X2 (in-sample) untuk laga UCL yang sudah dimainkan. Makin kecil makin baik; acuan acak = 0,667."""
    p = matches[(matches.competition == "UCL")].dropna(subset=["home_goals", "away_goals"])
    s = []
    for x in p.itertuples():
        w, d, l, _ = match_probs(*r.lam(x.home, x.away))
        o = (1, 0, 0) if x.home_goals > x.away_goals else (0, 1, 0) if x.home_goals == x.away_goals else (0, 0, 1)
        s.append((w-o[0])**2 + (d-o[1])**2 + (l-o[2])**2)
    return float(np.mean(s)), len(s)
