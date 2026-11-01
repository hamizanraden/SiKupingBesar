import streamlit as st

st.subheader("Model gol per laga")
st.markdown(
    "Jumlah gol tiap tim dalam satu laga dimodelkan sebagai variabel acak Poisson:"
)
st.latex(r"P(G=g)=\frac{e^{-\lambda}\lambda^{g}}{g!},\qquad g=0,1,2,\dots")
st.markdown("Rata-rata gol (λ) tiap tim adalah hasil kali kekuatan serang, kelemahan bertahan lawan, dan faktor kandang:")
st.latex(r"\lambda_{home}=\mu\cdot H\cdot a_{home}\cdot d_{away}")
st.latex(r"\lambda_{away}=\mu\cdot a_{away}\cdot d_{home}")
st.markdown(
    "- **a** = kekuatan serang, **d** = kelemahan bertahan (nilai lebih besar berarti pertahanan lebih lemah).\n"
    "- **μ** = rata-rata gol dasar per tim per laga, **H** = home advantage (bisa diestimasi dari data atau diatur manual).\n"
    "- **a** dan **d** diestimasi dengan *maximum likelihood* Poisson secara iteratif, lalu di-*shrink* ke 1 "
    "(prior 2 gol semu) supaya tim dengan sedikit laga tidak menghasilkan rating ekstrem. Keduanya dinormalisasi "
    "agar rata-rata geometriknya 1."
)
st.markdown("**Bobot tiap laga.** Laga yang lebih lama diberi bobot lebih kecil, dan laga liga domestik diberi bobot terpisah:")
st.latex(r"w_i=0{,}5^{\,\text{umur}_i/\text{half-life}}\times w_{liga}")
st.markdown(
    "Laga UCL dipakai sebagai penghubung kekuatan antarliga. Half-life, bobot liga domestik, home advantage, "
    "jumlah simulasi, dan seed dapat diubah di halaman **Simulator**."
)

st.subheader("Simulasi Monte Carlo")
st.markdown(
    "1. Poin, gol, dan kebobolan dihitung dari laga UCL yang sudah dimainkan.\n"
    "2. Untuk tiap laga sisa, gol kandang dan tandang diambil dari Poisson(λ) sebanyak N kali (tervektorisasi dengan NumPy).\n"
    "3. Klasemen tiap simulasi diurutkan dengan aturan: **poin → selisih gol → jumlah gol → acak**.\n"
    "4. Peringkat 1–8 langsung ke 16 besar; peringkat 9–24 bermain playoff dua leg (9 v 24, 10 v 23, dst.).\n"
    "5. Babak gugur dua leg: tim unggulan menjadi tuan rumah leg kedua; agregat imbang diselesaikan 50:50 "
    "(mewakili perpanjangan waktu dan penalti). Final satu laga di tempat netral.\n"
    "6. Peluang tiap babak = jumlah simulasi yang berhasil ÷ N. Rata-rata poin dan posisi dihitung dari seluruh simulasi."
)
st.markdown("**Law of Large Numbers.** Proporsi hasil simulasi konvergen ke peluang sebenarnya ketika N membesar:")
st.latex(r"\hat p_N=\frac{1}{N}\sum_{i=1}^{N}\mathbf{1}\{\text{tim juara pada simulasi }i\}\;\xrightarrow[N\to\infty]{}\;p")
st.caption("Lihat halaman Statistik: pita interval kepercayaan menyempit seiring bertambahnya N.")

st.subheader("Interval kepercayaan 95% (Wilson)")
st.markdown("Peluang juara adalah estimasi proporsi, sehingga selalu ditampilkan bersama ketidakpastiannya. Interval Wilson dipakai karena tetap stabil untuk peluang yang sangat kecil atau mendekati 0/1:")
st.latex(r"\frac{\hat p+\frac{z^2}{2N}\pm z\sqrt{\frac{\hat p(1-\hat p)}{N}+\frac{z^2}{4N^2}}}{1+\frac{z^2}{N}},\qquad z=1{,}96")
st.markdown("Angka ini berarti: bila simulasi diulang dengan seed berbeda, sekitar 95% interval akan memuat peluang sebenarnya dari model.")

st.subheader("Uji hipotesis Chi-square")
st.markdown("Kecocokan model Poisson diuji dengan membandingkan frekuensi gol observasi dan ekspektasi:")
st.latex(r"\chi^2=\sum_{k}\frac{(O_k-E_k)^2}{E_k},\qquad E_k=n\,P(G=k;\hat\lambda)")
st.markdown(
    "Derajat bebas = jumlah kelas − 1 (untuk estimasi λ) − 1.  \n"
    "**H₀:** gol per tim per laga berdistribusi Poisson. **H₁:** tidak berdistribusi Poisson.  \n"
    "Keputusan diambil pada taraf 5%: tolak H₀ bila p-value < 0,05. Uji ini memakai gol kandang dan tandang "
    "digabung; independensi gol kedua tim tidak diuji."
)

st.subheader("Brier score 1X2")
st.markdown("Kualitas probabilitas menang/seri/kalah dievaluasi dengan Brier score (makin kecil makin baik):")
st.latex(r"BS=\frac{1}{M}\sum_{i=1}^{M}\sum_{j\in\{H,D,A\}}\left(p_{ij}-o_{ij}\right)^2")
st.markdown(
    "Tebakan seragam (1/3, 1/3, 1/3) menghasilkan BS = 0,667, jadi skor di bawah 0,667 lebih baik daripada menebak acak. "
    "Skor saat ini dihitung **in-sample** — laga UCL yang sama dipakai untuk mengestimasi rating — sehingga "
    "cenderung optimistis dan belum menjadi bukti performa di laga yang belum dimainkan."
)

st.subheader("Asumsi")
st.markdown(
    "- Gol kedua tim dalam satu laga saling independen dan berdistribusi Poisson.\n"
    "- Kekuatan tim tetap selama sisa musim; hanya bobot form yang membedakan relevansi laga lama.\n"
    "- Home advantage sama untuk semua tim (kecuali diatur manual).\n"
    "- Pertandingan yang belum dimainkan memiliki jadwal dan peserta yang sudah pasti.\n"
    "- Bracket babak gugur mengikuti format UCL 2024/25; perempat final ke atas memakai bracket standar."
)

st.subheader("Keterbatasan")
st.markdown(
    "- Tidak memperhitungkan cedera, skorsing, transfer, rotasi, motivasi, atau kondisi pemain.\n"
    "- Tidak ada form guide 5 laga terakhir, mode what-if, heatmap posisi akhir, atau histogram poin.\n"
    "- Kekuatan antarliga hanya dihubungkan oleh laga UCL; jumlah laga UCL yang sedikit membuat perbandingan antarliga kurang pasti.\n"
    "- Bracket knockout disederhanakan dan bisa berbeda sedikit dari aturan resmi UEFA.\n"
    "- Brier score masih in-sample; validasi walk-forward belum tersedia.\n"
    "- Semua angka adalah peluang, bukan jaminan hasil."
)

st.subheader("Data dan reproduksibilitas")
st.markdown(
    "Data hanya berasal dari file CSV laga liga domestik dan UCL: kolom `date, home, away, home_goals, away_goals, competition`. "
    "Laga yang belum dimainkan dikosongkan golnya. Dataset divalidasi saat dimuat: kolom wajib, tanggal, skor bulat non-negatif, "
    "laga duplikat, konsistensi nama tim, tepat 36 tim UCL, dan ketersediaan laga domestik untuk tiap tim.\n\n"
    "Seed dan parameter yang sama menghasilkan tabel yang identik. Tanggal data terakhir ditampilkan di Dashboard dan halaman Tabel."
)
