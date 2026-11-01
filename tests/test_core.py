import numpy as np, pytest
from generate_sample_data import make
from core.pipeline import Params, run, validate
from core.stats import match_probs, wilson_ci
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
