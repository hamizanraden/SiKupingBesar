"""Alur data -> rating -> simulasi. Murni Python, TIDAK mengimpor Streamlit."""
from dataclasses import dataclass
import difflib
import re
import unicodedata
import numpy as np
import pandas as pd
from .ratings import fit_ratings
from .simulate import simulate_season

REQUIRED = ["date", "home", "away", "home_goals", "away_goals", "competition"]
UCL = "UCL"

@dataclass(frozen=True)
class Params:
    n_sim: int = 10000
    seed: int = 42
    home_adv: float | None = None      # None = estimasi dari data
    half_life: float = 8.0             # minggu
    domestic_weight: float = 0.5

def _norm_name(name):
    """Bentuk kanonik nama tim: tanpa aksen, tanda baca, dan beda huruf besar/kecil."""
    s = unicodedata.normalize("NFKD", str(name)).encode("ascii", "ignore").decode()
    return " ".join(re.sub(r"[^a-z0-9]+", " ", s.lower()).split())

def _sample(items, limit=5):
    items = list(items)
    head = ", ".join(map(str, items[:limit]))
    return head + (f", dan {len(items) - limit} lainnya" if len(items) > limit else "")

def _clean_text(df, col):
    if df[col].isna().any():
        raise ValueError(f"Kolom '{col}' punya {int(df[col].isna().sum())} baris kosong.")
    df[col] = df[col].astype(str).str.strip()
    blank = df[col] == ""
    if blank.any():
        raise ValueError(f"Kolom '{col}' punya {int(blank.sum())} baris kosong.")

def _clean_goals(df, col):
    raw = df[col]
    num = pd.to_numeric(raw, errors="coerce")
    # Teks kosong dianggap "belum dimainkan"; teks lain yang bukan angka adalah error.
    bad = raw.notna() & (raw.astype(str).str.strip() != "") & num.isna()
    if bad.any():
        raise ValueError(f"Kolom '{col}' berisi nilai bukan angka pada baris {_sample(np.flatnonzero(bad) + 2, 3)}.")
    neg = num < 0
    if neg.any():
        raise ValueError(f"Kolom '{col}' berisi gol negatif pada baris {_sample(np.flatnonzero(neg) + 2, 3)}.")
    frac = num.notna() & (num % 1 != 0)
    if frac.any():
        raise ValueError(f"Kolom '{col}' berisi gol bukan bilangan bulat pada baris {_sample(np.flatnonzero(frac) + 2, 3)}.")
    return num

def validate(df):
    """Validasi + bersihkan dataset. Melempar ValueError dengan pesan yang bisa ditampilkan ke pengguna."""
    miss = [c for c in REQUIRED if c not in df.columns]
    if miss:
        raise ValueError(f"Kolom wajib tidak ditemukan: {', '.join(miss)}")
    if df.empty:
        raise ValueError("Dataset kosong.")

    df = df.copy()
    for col in ("home", "away", "competition"):
        _clean_text(df, col)
    df["competition"] = df["competition"].str.upper().replace({"UCL": UCL})

    parsed = pd.to_datetime(df["date"], errors="coerce")
    bad_date = parsed.isna()
    if bad_date.any():
        raise ValueError(f"Tanggal tidak valid pada baris {_sample(np.flatnonzero(bad_date) + 2)}.")
    df["date"] = parsed

    df["home_goals"] = _clean_goals(df, "home_goals")
    df["away_goals"] = _clean_goals(df, "away_goals")

    same = df["home"].str.casefold() == df["away"].str.casefold()
    if same.any():
        raise ValueError(f"Tim tidak boleh melawan dirinya sendiri pada baris {_sample(np.flatnonzero(same) + 2)}.")

    half = df["home_goals"].isna() != df["away_goals"].isna()
    if half.any():
        raise ValueError(
            f"Skor harus diisi kedua sisi atau dikosongkan kedua sisi; baris {_sample(np.flatnonzero(half) + 2)} hanya punya satu gol."
        )

    dup = df.duplicated(subset=["date", "home", "away", "competition"], keep=False)
    if dup.any():
        raise ValueError(f"Ada {int(dup.sum())} baris laga duplikat (tim & tanggal sama). Hapus duplikatnya dulu.")

    if df["home_goals"].notna().sum() == 0:
        raise ValueError("Belum ada satu pun laga yang sudah dimainkan (semua gol kosong).")

    ucl = df[df["competition"] == UCL]
    teams = set(ucl["home"]) | set(ucl["away"])
    if len(teams) != 36:
        raise ValueError(f"Format UCL butuh 36 tim pada competition='UCL', ditemukan {len(teams)}.")

    # Nama yang hanya beda huruf besar/kecil atau tanda baca akan terpecah jadi dua tim.
    by_norm = {}
    for t in sorted(set(df["home"]) | set(df["away"])):
        by_norm.setdefault(_norm_name(t), []).append(t)
    clashes = {k: v for k, v in by_norm.items() if len(v) > 1}
    if clashes:
        detail = "; ".join(f"{', '.join(v)}" for v in clashes.values())
        raise ValueError(f"Nama tim tidak konsisten (hanya beda kapitalisasi/tanda baca): {detail}. Samakan penulisannya.")

    played = df[df["home_goals"].notna()]
    domestic_teams = set(played[played["competition"] != UCL]["home"]) | set(played[played["competition"] != UCL]["away"])
    no_domestic = sorted(teams - domestic_teams)
    if no_domestic:
        raise ValueError(
            f"{len(no_domestic)} tim UCL tidak punya laga liga domestik yang sudah dimainkan: {_sample(no_domestic)}. "
            "Lengkapi dataset atau samakan nama timnya."
        )

    return df

def suspicious_names(df, cutoff=0.9):
    """Pasangan nama tim yang sangat mirip (kemungkinan salah ketik/alias). Hanya peringatan, bukan error."""
    teams = sorted(set(df["home"]) | set(df["away"]))
    out = []
    for i, a in enumerate(teams):
        for b in teams[i + 1:]:
            na, nb = _norm_name(a), _norm_name(b)
            if na != nb and difflib.SequenceMatcher(None, na, nb).ratio() >= cutoff:
                out.append((a, b))
    return out

def load_matches(src):
    df = pd.read_csv(src)
    return validate(df)

def data_date(matches):
    return matches.dropna(subset=["home_goals", "away_goals"])["date"].max()

def run(matches, p: Params):
    r = fit_ratings(matches, half_life_weeks=p.half_life,
                    domestic_weight=p.domestic_weight, home_adv=p.home_adv)
    return r, simulate_season(r, matches, p.n_sim, p.seed, home_adv=p.home_adv)
