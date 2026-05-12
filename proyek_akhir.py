# Import dependencies
import streamlit as st
import pandas as pd
import numpy as np

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Tsukamoto Blue Chip", layout="wide")
st.title("Sistem Rekomendasi Saham Blue Chip")
st.subheader("Mesin Inferensi: Fuzzy Tsukamoto")
st.write("Sistem ini menilai kelayakan investasi saham berdasarkan Valuasi (PER) dan Dividend Yield menggunakan logika Fuzzy Tsukamoto.")

# --- 2. PERSIAPAN DATA ---
data = {
    'Kode Saham': ['BBCA', 'BBRI', 'TLKM', 'UNVR'],
    'Nama Perusahaan': ['Bank Central Asia', 'Bank Rakyat Indonesia', 'Telkom Indonesia', 'Unilever Indonesia'],
    'Harga (Rp)': [9800, 6200, 3100, 2800],
    'PER (x)': [25.5, 14.2, 12.8, 28.4], # Makin kecil makin murah
    'Dividend Yield (%)': [2.1, 4.5, 5.2, 3.8] # Makin besar makin bagus
}
df = pd.DataFrame(data)

# --- 3. FUNGSI LOGIKA FUZZY TSUKAMOTO ---

# A. Fuzzifikasi PER (Batas: 10 sampai 30)
def fuzzy_per(per):
    # Himpunan MURAH (Turun)
    if per <= 10: mu_murah = 1.0
    elif per >= 30: mu_murah = 0.0
    else: mu_murah = (30 - per) / (30 - 10)
    
    # Himpunan MAHAL (Naik)
    if per <= 10: mu_mahal = 0.0
    elif per >= 30: mu_mahal = 1.0
    else: mu_mahal = (per - 10) / (30 - 10)
    
    return mu_murah, mu_mahal

# B. Fuzzifikasi Dividend Yield (Batas: 2% sampai 6%)
def fuzzy_yield(dy):
    # Himpunan RENDAH (Turun)
    if dy <= 2: mu_rendah = 1.0
    elif dy >= 6: mu_rendah = 0.0
    else: mu_rendah = (6 - dy) / (6 - 2)
    
    # Himpunan TINGGI (Naik)
    if dy <= 2: mu_tinggi = 0.0
    elif dy >= 6: mu_tinggi = 1.0
    else: mu_tinggi = (dy - 2) / (6 - 2)
    
    return mu_rendah, mu_tinggi

# C. Inferensi & Defuzzifikasi TSUKAMOTO
def hitung_skor_tsukamoto(per, dy):
    mu_murah, mu_mahal = fuzzy_per(per)
    mu_rendah, mu_tinggi = fuzzy_yield(dy)
    
    # Rule Base & Penentuan Nilai Z (Batas Skor: 0 sampai 100)
    # Rumus z TINGGI (Naik)  -> z = alpha * 100
    # Rumus z RENDAH (Turun) -> z = 100 - (alpha * 100)
    
    # [R1] IF PER Murah AND Yield Tinggi THEN Skor TINGGI
    a1 = min(mu_murah, mu_tinggi)
    z1 = a1 * 100
    
    # [R2] IF PER Murah AND Yield Rendah THEN Skor TINGGI (Karena valuasi masih murah)
    a2 = min(mu_murah, mu_rendah)
    z2 = a2 * 100
    
    # [R3] IF PER Mahal AND Yield Tinggi THEN Skor RENDAH (Waspada dividend trap / overvalued)
    a3 = min(mu_mahal, mu_tinggi)
    z3 = 100 - (a3 * 100)
    
    # [R4] IF PER Mahal AND Yield Rendah THEN Skor RENDAH (Sangat tidak layak)
    a4 = min(mu_mahal, mu_rendah)
    z4 = 100 - (a4 * 100)
    
    # Defuzzifikasi Tsukamoto: (a1*z1 + a2*z2 + a3*z3 + a4*z4) / (a1 + a2 + a3 + a4)
    total_alpha = a1 + a2 + a3 + a4
    
    # Cegah pembagian dengan nol
    if total_alpha == 0:
        return 0
        
    skor_akhir = ((a1*z1) + (a2*z2) + (a3*z3) + (a4*z4)) / total_alpha
    return skor_akhir

# --- 4. PROSES HITUNG SKOR ---
skor_list = []
for index, row in df.iterrows():
    skor = hitung_skor_tsukamoto(row['PER (x)'], row['Dividend Yield (%)'])
    skor_list.append(skor)

df['Skor Tsukamoto'] = skor_list
# Mengurutkan rekomendasi
df_rekomendasi = df.sort_values(by='Skor Tsukamoto', ascending=False).reset_index(drop=True)

# --- 5. TAMPILAN ANTARMUKA ---
st.write("---")
st.markdown("### 🏆 Papan Peringkat Saham Terbaik")

# Tabel dengan gradien warna
st.dataframe(df_rekomendasi.style.format({
    'Harga (Rp)': 'Rp {:,.0f}',
    'Dividend Yield (%)': '{:.2f}%',
    'Skor Tsukamoto': '{:.2f}'
}).background_gradient(subset=['Skor Tsukamoto'], cmap='Blues'))

# Penjelasan Rule Base di bawah tabel untuk edukasi/tugas
with st.expander("Lihat Logika Rule Base Tsukamoto yang Digunakan"):
    st.write("""
    1. **IF** PER Murah **AND** Yield Tinggi **THEN** Skor TINGGI
    2. **IF** PER Murah **AND** Yield Rendah **THEN** Skor TINGGI
    3. **IF** PER Mahal **AND** Yield Tinggi **THEN** Skor RENDAH
    4. **IF** PER Mahal **AND** Yield Rendah **THEN** Skor RENDAH
    """)

# Sidebar Kalkulator Tsukamoto
# st.sidebar.header("🧮 Uji Tsukamoto Manual")
# st.sidebar.write("Geser slider untuk melihat perubahan output Z.")
# test_per = st.sidebar.slider("PER (Valuasi)", 5.0, 40.0, 15.0)
# test_dy = st.sidebar.slider("Dividend Yield (%)", 0.0, 10.0, 4.0)
# skor_manual = hitung_skor_tsukamoto(test_per, test_dy)
# st.sidebar.success(f"**Skor Akhir (Z):** {skor_manual:.2f} / 100")