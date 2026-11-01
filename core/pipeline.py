"""Alur data -> rating -> simulasi. Murni Python, TIDAK mengimpor Streamlit."""
from dataclasses import dataclass
import pandas as pd
from .ratings import fit_ratings
from .simulate import simulate_season

REQUIRED = ["date", "home", "away", "home_goals", "away_goals", "competition"]

@dataclass(frozen=True)
class Params:
    n_sim: int = 10000
    seed: int = 42
    home_adv: float | None = None      # None = estimasi dari data
    half_life: float = 8.0             # minggu
    domestic_weight: float = 0.5

def validate(df):
    miss = [c for c in REQUIRED if c not in df.columns]
    if miss:
        raise ValueError(f"Kolom wajib tidak ditemukan: {', '.join(miss)}")
    ucl = df[df.competition == "UCL"]
    teams = set(ucl.home) | set(ucl.away)
    if len(teams) != 36:
        raise ValueError(f"Format UCL butuh 36 tim pada competition='UCL', ditemukan {len(teams)}.")
    return df

def load_matches(src):
    df = pd.read_csv(src)
    df = validate(df)
    df["date"] = pd.to_datetime(df["date"])
    return df

def data_date(matches):
    return matches.dropna(subset=["home_goals", "away_goals"])["date"].max()

def run(matches, p: Params):
    r = fit_ratings(matches, half_life_weeks=p.half_life,
                    domestic_weight=p.domestic_weight, home_adv=p.home_adv)
    return r, simulate_season(r, matches, p.n_sim, p.seed, home_adv=p.home_adv)
