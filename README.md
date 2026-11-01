# SiKupingBesar

Prediksi juara Liga Champions (format 36 tim) dengan simulasi Monte Carlo dan model gol Poisson.
Streamlit + Tailwind CSS (CDN) + Plotly. Hanya memakai dataset laga liga domestik dan UCL.

## Menjalankan
```bash
python -m venv .venv
.venv\Scripts\activate          # Windows  (macOS/Linux: source .venv/bin/activate)
pip install -r requirements.txt
python generate_sample_data.py  # membuat data SINTETIS untuk mencoba
streamlit run app.py
```

## Memakai datamu
Taruh `data/matches.csv` (atau unggah lewat halaman Simulator) dengan kolom:
`date, home, away, home_goals, away_goals, competition`. Laga UCL: `competition = UCL`;
laga belum dimainkan: gol dikosongkan. Harus ada tepat 36 tim UCL.
Sumber data: _isi tautan dan lisensi dataset di sini_.

Saat dimuat, dataset divalidasi: kolom wajib, tanggal valid, gol bulat dan tidak negatif,
tidak ada laga duplikat, skor diisi kedua sisi atau kosong kedua sisi, penulisan nama tim konsisten,
tepat 36 tim UCL, dan tiap tim UCL punya laga liga domestik yang sudah dimainkan.
Nama tim yang sangat mirip ditampilkan sebagai peringatan di halaman Simulator.

## Halaman
Dashboard · Tabel · Simulator · Head-to-Head · Statistik · Metodologi

Parameter (jumlah simulasi, seed, home advantage, half-life form, bobot liga domestik) dan unggahan
data ada di halaman **Simulator**; perubahan langsung dipakai semua halaman. Tampilan memakai navbar
pil sesuai `docs/mockup/ucl-simulator.html`.

## Struktur
- `app.py` pintu masuk dan navigasi (`st.navigation`)
- `views/` satu file satu halaman
- `ui/` navbar, tema, komponen, dan template Tailwind (`ui/templates/`)
- `core/` logika statistik tanpa Streamlit (rating, simulasi, statistik, pipeline)
- `tests/` uji untuk `core/` dan template · `docs/mockup/` acuan tampilan
- Logo klub (opsional): `assets/logos/<nama-tim>.png`, contoh `real-madrid.png`

## Tes
```bash
pip install -r requirements-dev.txt
pytest
```
