import numpy as np, pandas as pd, pytest
from generate_sample_data import make
from core.pipeline import Params, run, suspicious_names, validate
from core.stats import convergence, match_probs, wilson_ci
from ui.components import html

@pytest.fixture(scope="module")
def data(): return make(1)

def test_totals(data):
    _, res = run(data, Params(n_sim=4000, seed=7)); t = res.table
    assert t["Juara"].sum() == pytest.approx(1.0)
    assert t["Top 8"].sum() == pytest.approx(8.0)
    assert t["Top 24"].sum() == pytest.approx(24.0)
    assert t["R16"].sum() == pytest.approx(16.0) and t["Final"].sum() == pytest.approx(2.0)

def test_reproducible(data):
    a = run(data, Params(n_sim=2000, seed=3))[1].table; b = run(data, Params(n_sim=2000, seed=3))[1].table
    assert a.equals(b)

def test_h2h_sums_to_one(data):
    r, _ = run(data, Params(n_sim=500))
    w, d, l, m = match_probs(*r.lam("Klub 01", "Klub 02"))
    assert w+d+l == pytest.approx(1.0, abs=1e-4)

def test_ci_contains_p():
    lo, hi = wilson_ci(200, 1000); assert lo < 0.2 < hi

def test_validate_needs_36_teams(data):
    with pytest.raises(ValueError): validate(data[~data.home.isin(["Klub 01"]) & ~data.away.isin(["Klub 01"])])

def test_templates_render():
    out = html("prob_pills.html", home="A", away="B", w=.4, d=.3, l=.3, lh=1.5, la=1.1)
    assert "40.0%" in out and "tailwindcss" in out

def test_validate_accepts_and_cleans(data):
    original = data.copy()
    out = validate(data)
    assert len(out) == len(data)
    assert str(out["date"].dtype).startswith("datetime")
    assert data.equals(original)                     # input tidak diubah

def test_validate_rejects_partial_score(data):
    bad = data.copy()
    i = bad.index[bad.competition == "UCL"][0]
    bad.loc[i, "away_goals"] = np.nan
    with pytest.raises(ValueError, match="kedua sisi"): validate(bad)

def test_validate_rejects_negative_goal(data):
    bad = data.copy()
    i = bad.index[bad.competition == "UCL"][0]
    bad.loc[i, "home_goals"] = -1
    with pytest.raises(ValueError, match="negatif"): validate(bad)

def test_validate_rejects_duplicate_match(data):
    bad = pd.concat([data, data.iloc[[0]]], ignore_index=True)
    with pytest.raises(ValueError, match="duplikat"): validate(bad)

def test_validate_rejects_team_without_domestic_matches(data):
    bad = data[data.competition == "UCL"].copy()
    with pytest.raises(ValueError, match="liga domestik"): validate(bad)

def test_validate_rejects_inconsistent_team_name(data):
    bad = data.copy()
    extra = bad.iloc[[0]].copy()
    extra["home"] = extra["home"].str.lower()
    extra["competition"] = "Liga 9"
    extra["date"] = pd.Timestamp("2026-08-20")
    bad = pd.concat([bad, extra], ignore_index=True)
    with pytest.raises(ValueError, match="tidak konsisten"): validate(bad)

def test_suspicious_names_flags_typo():
    df = pd.DataFrame({"home": ["Manchester City", "Arsenal"],
                       "away": ["Manchester Cty", "Chelsea"]})
    assert ("Manchester City", "Manchester Cty") in suspicious_names(df)

def test_manual_home_advantage_is_used(data):
    r, _ = run(data, Params(n_sim=500, seed=1, home_adv=1.0))
    assert r.H == 1.0

def test_convergence_band_narrows(data):
    _, res = run(data, Params(n_sim=3000, seed=5))
    cv = convergence(res.champions, 0)
    assert (cv.hi - cv.lo).iloc[-1] < (cv.hi - cv.lo).iloc[0]

