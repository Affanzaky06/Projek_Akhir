# =========================
# IMPORT LIBRARY
# =========================

# streamlit untuk membuat web app
import streamlit as st

# numpy untuk array/rentang angka
import numpy as np

# skfuzzy untuk fuzzy logic
import skfuzzy as fuzz

# control digunakan untuk rule fuzzy
from skfuzzy import control as ctrl


# =========================
# JUDUL APLIKASI
# =========================

st.title("Sistem Rekomendasi Saham dengan Fuzzy Logic")

st.write("""
Aplikasi ini menggunakan metode fuzzy logic untuk menentukan
tingkat kelayakan saham berdasarkan beberapa kriteria:
- Return
- Volatilitas
- Pertumbuhan laba
- Utang
- Dividen
""")


# =========================
# PILIH SAHAM
# =========================

# dropdown pilihan saham
saham = st.selectbox(
    "Pilih Saham",
    ["BBCA", "BBRI", "TLKM", "UNVR"]
)


# =========================
# MEMBUAT VARIABEL FUZZY
# =========================

# Input fuzzy

# Return saham (0 - 100)
return_saham = ctrl.Antecedent(
    np.arange(0, 101, 1),
    'return_saham'
)

# Volatilitas (0 - 100)
volatilitas = ctrl.Antecedent(
    np.arange(0, 101, 1),
    'volatilitas'
)

# Pertumbuhan laba (0 - 100)
pertumbuhan = ctrl.Antecedent(
    np.arange(0, 101, 1),
    'pertumbuhan'
)

# Utang (0 - 100)
utang = ctrl.Antecedent(
    np.arange(0, 101, 1),
    'utang'
)

# Dividen (0 - 100)
dividen = ctrl.Antecedent(
    np.arange(0, 101, 1),
    'dividen'
)


# Output fuzzy

# Kelayakan investasi
kelayakan = ctrl.Consequent(
    np.arange(0, 101, 1),
    'kelayakan'
)


# =========================
# FUNGSI KEANGGOTAAN INPUT
# =========================

# ---- RETURN ----

return_saham['rendah'] = fuzz.trimf(
    return_saham.universe,
    [0, 0, 50]
)

return_saham['sedang'] = fuzz.trimf(
    return_saham.universe,
    [25, 50, 75]
)

return_saham['tinggi'] = fuzz.trimf(
    return_saham.universe,
    [50, 100, 100]
)


# ---- VOLATILITAS ----

volatilitas['rendah'] = fuzz.trimf(
    volatilitas.universe,
    [0, 0, 50]
)

volatilitas['sedang'] = fuzz.trimf(
    volatilitas.universe,
    [25, 50, 75]
)

volatilitas['tinggi'] = fuzz.trimf(
    volatilitas.universe,
    [50, 100, 100]
)


# ---- PERTUMBUHAN LABA ----

pertumbuhan['rendah'] = fuzz.trimf(
    pertumbuhan.universe,
    [0, 0, 50]
)

pertumbuhan['sedang'] = fuzz.trimf(
    pertumbuhan.universe,
    [25, 50, 75]
)

pertumbuhan['tinggi'] = fuzz.trimf(
    pertumbuhan.universe,
    [50, 100, 100]
)


# ---- UTANG ----

utang['rendah'] = fuzz.trimf(
    utang.universe,
    [0, 0, 50]
)

utang['sedang'] = fuzz.trimf(
    utang.universe,
    [25, 50, 75]
)

utang['tinggi'] = fuzz.trimf(
    utang.universe,
    [50, 100, 100]
)


# ---- DIVIDEN ----

dividen['rendah'] = fuzz.trimf(
    dividen.universe,
    [0, 0, 50]
)

dividen['sedang'] = fuzz.trimf(
    dividen.universe,
    [25, 50, 75]
)

dividen['tinggi'] = fuzz.trimf(
    dividen.universe,
    [50, 100, 100]
)


# =========================
# FUNGSI KEANGGOTAAN OUTPUT
# =========================

kelayakan['buruk'] = fuzz.trimf(
    kelayakan.universe,
    [0, 0, 50]
)

kelayakan['cukup'] = fuzz.trimf(
    kelayakan.universe,
    [25, 50, 75]
)

kelayakan['baik'] = fuzz.trimf(
    kelayakan.universe,
    [50, 100, 100]
)


# =========================
# RULE BASE
# =========================

rules = [

    # Jika return tinggi DAN pertumbuhan tinggi
    # DAN utang rendah
    # maka kelayakan baik
    ctrl.Rule(
        return_saham['tinggi']
        & pertumbuhan['tinggi']
        & utang['rendah'],
        kelayakan['baik']
    ),

    # Jika return sedang DAN dividen sedang
    # maka kelayakan cukup
    ctrl.Rule(
        return_saham['sedang']
        & dividen['sedang'],
        kelayakan['cukup']
    ),

    # Jika volatilitas tinggi ATAU utang tinggi
    # maka kelayakan buruk
    ctrl.Rule(
        volatilitas['tinggi']
        | utang['tinggi'],
        kelayakan['buruk']
    ),

    # Jika dividen tinggi DAN volatilitas rendah
    # maka kelayakan baik
    ctrl.Rule(
        dividen['tinggi']
        & volatilitas['rendah'],
        kelayakan['baik']
    ),

    # Jika pertumbuhan rendah
    # maka kelayakan buruk
    ctrl.Rule(
        pertumbuhan['rendah'],
        kelayakan['buruk']
    )
]


# =========================
# MEMBUAT SISTEM FUZZY
# =========================

sistem_ctrl = ctrl.ControlSystem(rules)

simulasi = ctrl.ControlSystemSimulation(sistem_ctrl)


# =========================
# INPUT USER DENGAN SLIDER
# =========================

st.subheader("Masukkan Nilai Kriteria")

nilai_return = st.slider(
    "Return",
    0,
    100,
    70
)

nilai_volatilitas = st.slider(
    "Volatilitas",
    0,
    100,
    40
)

nilai_pertumbuhan = st.slider(
    "Pertumbuhan Laba",
    0,
    100,
    75
)

nilai_utang = st.slider(
    "Utang",
    0,
    100,
    30
)

nilai_dividen = st.slider(
    "Dividen",
    0,
    100,
    65
)


# =========================
# PROSES FUZZY
# =========================

# memasukkan input ke sistem
simulasi.input['return_saham'] = nilai_return
simulasi.input['volatilitas'] = nilai_volatilitas
simulasi.input['pertumbuhan'] = nilai_pertumbuhan
simulasi.input['utang'] = nilai_utang
simulasi.input['dividen'] = nilai_dividen


# menghitung fuzzy
simulasi.compute()


# =========================
# HASIL OUTPUT
# =========================

hasil = simulasi.output['kelayakan']

st.subheader("Hasil Analisis")

st.write(f"Saham yang dipilih: **{saham}**")

st.write(f"Nilai kelayakan investasi: **{hasil:.2f}**")


# =========================
# INTERPRETASI HASIL
# =========================

if hasil < 40:
    st.error("Rekomendasi: Kurang Layak Investasi")

elif hasil < 70:
    st.warning("Rekomendasi: Cukup Layak Investasi")

else:
    st.success("Rekomendasi: Layak Investasi")