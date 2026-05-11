# =========================================================
# DSS INVESTASI SAHAM BLUE CHIP
# METODE FUZZY TSUKAMOTO
# =========================================================

import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# =========================================================
# KONFIGURASI HALAMAN
# =========================================================

st.set_page_config(
    page_title="DSS Investasi Saham Blue Chip",
    page_icon="📈",
    layout="wide"
)

# =========================================================
# JUDUL
# =========================================================

st.title("📈 DSS Pemilihan Saham Blue Chip")
st.markdown("""
### Sistem Pendukung Keputusan Menggunakan Metode Fuzzy Tsukamoto
Aplikasi ini membantu menentukan saham blue chip terbaik berdasarkan beberapa kriteria investasi.
""")

st.markdown("---")

# =========================================================
# DATA SAHAM
# =========================================================

data = {
    "Saham": ["BBCA", "BBRI", "TLKM", "UNVR"],
    "Return": [85, 80, 70, 60],
    "Volatilitas": [20, 30, 25, 15],
    "Pertumbuhan_Laba": [90, 85, 70, 60],
    "Utang": [25, 35, 40, 20],
    "Dividen": [70, 75, 80, 85]
}

df = pd.DataFrame(data)

# =========================================================
# FUNGSI FUZZY
# =========================================================

def fuzzy_rendah(x, a, b):

    if x <= a:
        return 1

    elif a < x < b:
        return (b - x) / (b - a)

    else:
        return 0


def fuzzy_tinggi(x, a, b):

    if x <= a:
        return 0

    elif a < x < b:
        return (x - a) / (b - a)

    else:
        return 1

# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.header("⚙️ Pengaturan Bobot")

w_return = st.sidebar.slider(
    "Bobot Return",
    1, 5, 5
)

w_volatilitas = st.sidebar.slider(
    "Bobot Volatilitas",
    1, 5, 4
)

w_laba = st.sidebar.slider(
    "Bobot Pertumbuhan Laba",
    1, 5, 5
)

w_utang = st.sidebar.slider(
    "Bobot Utang",
    1, 5, 3
)

w_dividen = st.sidebar.slider(
    "Bobot Dividen",
    1, 5, 4
)

# =========================================================
# PERHITUNGAN FUZZY
# =========================================================

hasil = []

for i in range(len(df)):

    saham = df.loc[i, "Saham"]

    ret = df.loc[i, "Return"]
    vol = df.loc[i, "Volatilitas"]
    laba = df.loc[i, "Pertumbuhan_Laba"]
    utang = df.loc[i, "Utang"]
    div = df.loc[i, "Dividen"]

    # =====================================================
    # FUZZIFIKASI
    # =====================================================

    return_tinggi = fuzzy_tinggi(ret, 50, 100)

    volatilitas_rendah = fuzzy_rendah(vol, 10, 40)

    laba_tinggi = fuzzy_tinggi(laba, 50, 100)

    utang_rendah = fuzzy_rendah(utang, 10, 50)

    dividen_tinggi = fuzzy_tinggi(div, 50, 100)

    # =====================================================
    # FIRE STRENGTH
    # =====================================================

    alpha = min(
        return_tinggi,
        volatilitas_rendah,
        laba_tinggi,
        utang_rendah,
        dividen_tinggi
    )

    # =====================================================
    # SKOR
    # =====================================================

    total_bobot = (
        w_return +
        w_volatilitas +
        w_laba +
        w_utang +
        w_dividen
    )

    skor = (
        (
            ret * w_return +
            (100 - vol) * w_volatilitas +
            laba * w_laba +
            (100 - utang) * w_utang +
            div * w_dividen
        )
        / total_bobot
    )

    # =====================================================
    # NILAI AKHIR TSUKAMOTO
    # =====================================================

    z = alpha * skor

    hasil.append({
        "Saham": saham,
        "Alpha": round(alpha, 3),
        "Skor": round(skor, 3),
        "Nilai Akhir": round(z, 3)
    })

# =========================================================
# DATAFRAME HASIL
# =========================================================

hasil_df = pd.DataFrame(hasil)

hasil_df = hasil_df.sort_values(
    by="Nilai Akhir",
    ascending=False
)

# =========================================================
# HASIL PERHITUNGAN
# =========================================================

st.subheader("📋 Hasil Perhitungan")

st.dataframe(
    hasil_df,
    use_container_width=True
)

# =========================================================
# REKOMENDASI
# =========================================================

terbaik = hasil_df.iloc[0]

st.success(
    f"✅ Rekomendasi saham terbaik adalah "
    f"{terbaik['Saham']} "
    f"dengan nilai akhir "
    f"{terbaik['Nilai Akhir']}"
)

# =========================================================
# VISUALISASI
# =========================================================

st.subheader("📊 Grafik Ranking Saham")

fig, ax = plt.subplots(figsize=(8, 5))

ax.bar(
    hasil_df["Saham"],
    hasil_df["Nilai Akhir"]
)

ax.set_xlabel("Saham")
ax.set_ylabel("Nilai Akhir")
ax.set_title("Ranking Saham Blue Chip")

st.pyplot(fig)

# =========================================================
# DATA AWAL
# =========================================================

st.subheader("📁 Data Awal Saham")

st.dataframe(
    df,
    use_container_width=True
)

# =========================================================
# LANGKAH PERHITUNGAN
# =========================================================

st.subheader("🧮 Langkah Perhitungan Fuzzy Tsukamoto")

for i in range(len(df)):

    saham = df.loc[i, "Saham"]

    ret = df.loc[i, "Return"]
    vol = df.loc[i, "Volatilitas"]
    laba = df.loc[i, "Pertumbuhan_Laba"]
    utang = df.loc[i, "Utang"]
    div = df.loc[i, "Dividen"]

    # =====================================================
    # FUZZIFIKASI
    # =====================================================

    return_tinggi = fuzzy_tinggi(ret, 50, 100)

    volatilitas_rendah = fuzzy_rendah(vol, 10, 40)

    laba_tinggi = fuzzy_tinggi(laba, 50, 100)

    utang_rendah = fuzzy_rendah(utang, 10, 50)

    dividen_tinggi = fuzzy_tinggi(div, 50, 100)

    # =====================================================
    # FIRE STRENGTH
    # =====================================================

    alpha = min(
        return_tinggi,
        volatilitas_rendah,
        laba_tinggi,
        utang_rendah,
        dividen_tinggi
    )

    # =====================================================
    # SKOR
    # =====================================================

    total_bobot = (
        w_return +
        w_volatilitas +
        w_laba +
        w_utang +
        w_dividen
    )

    skor = (
        (
            ret * w_return +
            (100 - vol) * w_volatilitas +
            laba * w_laba +
            (100 - utang) * w_utang +
            div * w_dividen
        )
        / total_bobot
    )

    z = alpha * skor

    # =====================================================
    # DETAIL LANGKAH
    # =====================================================

    with st.expander(f"📌 Detail Perhitungan {saham}"):

        # =================================================
        # DATA AWAL
        # =================================================

        st.markdown("## 1️⃣ Data Awal")

        st.write(f"Return = {ret}")
        st.write(f"Volatilitas = {vol}")
        st.write(f"Pertumbuhan Laba = {laba}")
        st.write(f"Utang = {utang}")
        st.write(f"Dividen = {div}")

        st.markdown("---")

        # =================================================
        # FUZZIFIKASI
        # =================================================

        st.markdown("## 2️⃣ Fuzzifikasi")

        st.write("### Return Tinggi")

        st.write(
            f"μ Return Tinggi = "
            f"({ret} - 50) / (100 - 50)"
        )

        st.write(f"= {return_tinggi:.3f}")

        st.write("")

        st.write("### Volatilitas Rendah")

        st.write(
            f"μ Volatilitas Rendah = "
            f"(40 - {vol}) / (40 - 10)"
        )

        st.write(f"= {volatilitas_rendah:.3f}")

        st.write("")

        st.write("### Pertumbuhan Laba Tinggi")

        st.write(
            f"μ Pertumbuhan Laba Tinggi = "
            f"({laba} - 50) / (100 - 50)"
        )

        st.write(f"= {laba_tinggi:.3f}")

        st.write("")

        st.write("### Utang Rendah")

        st.write(
            f"μ Utang Rendah = "
            f"(50 - {utang}) / (50 - 10)"
        )

        st.write(f"= {utang_rendah:.3f}")

        st.write("")

        st.write("### Dividen Tinggi")

        st.write(
            f"μ Dividen Tinggi = "
            f"({div} - 50) / (100 - 50)"
        )

        st.write(f"= {dividen_tinggi:.3f}")

        st.markdown("---")

        # =================================================
        # FIRE STRENGTH
        # =================================================

        st.markdown("## 3️⃣ Fire Strength (α-predikat)")

        st.write(
            "α = min("
            f"{return_tinggi:.3f}, "
            f"{volatilitas_rendah:.3f}, "
            f"{laba_tinggi:.3f}, "
            f"{utang_rendah:.3f}, "
            f"{dividen_tinggi:.3f})"
        )

        st.write(f"α = {alpha:.3f}")

        st.markdown("---")

        # =================================================
        # SKOR
        # =================================================

        st.markdown("## 4️⃣ Perhitungan Skor")

        st.write("### Rumus")

        st.write(
            f"(({ret} × {w_return}) + "
            f"((100-{vol}) × {w_volatilitas}) + "
            f"({laba} × {w_laba}) + "
            f"((100-{utang}) × {w_utang}) + "
            f"({div} × {w_dividen})) "
            f"/ {total_bobot}"
        )

        st.write(f"Skor = {skor:.3f}")

        st.markdown("---")

        # =================================================
        # NILAI AKHIR
        # =================================================

        st.markdown("## 5️⃣ Nilai Akhir Tsukamoto")

        st.write("### Rumus")

        st.write("Z = α × skor")

        st.write(
            f"Z = {alpha:.3f} × {skor:.3f}"
        )

        st.write(f"Z = {z:.3f}")

        st.success(
            f"✅ Nilai akhir saham {saham} = {z:.3f}"
        )

# =========================================================
# FOOTER
# =========================================================

st.markdown("---")

st.caption(
    "DSS Investasi Saham Blue Chip "
    "Menggunakan Metode Fuzzy Tsukamoto"
)