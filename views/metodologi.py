import streamlit as st

st.markdown("### Model gol per laga")
st.latex(r"G_{home}\sim Poisson(\lambda_h),\quad \lambda_h=\mu\cdot H\cdot a_{home}\cdot d_{away}")
st.latex(r"G_{away}\sim Poisson(\lambda_a),\quad \lambda_a=\mu\cdot a_{away}\cdot d_{home}")
st.markdown("""
- **a** (serang) dan **d** (kelemahan bertahan) diestimasi dari laga liga domestik dan UCL dengan iterasi *maximum likelihood* Poisson, dengan *shrinkage* ke 1 agar stabil.
- **Bobot form**: tiap laga berbobot 0,5^(umur/half-life); laga liga dikali bobot domestik. Laga UCL menghubungkan kekuatan antarliga.
- **Monte Carlo**: sisa laga league phase disimulasikan N kali. Urutan klasemen: poin, selisih gol, gol, acak. Peringkat 1-8 ke R16, 9-24 ke playoff.
- **Knockout**: dua leg, agregat imbang diselesaikan 50:50; final satu laga netral.
- **Interval kepercayaan**: Wilson 95% untuk proporsi.
- **Keterbatasan**: gol independen, kekuatan tim tetap selama musim, tanpa data pemain atau cedera, bracket knockout disederhanakan (ubah di `core/simulate.py`), Brier score masih in-sample.
""")
