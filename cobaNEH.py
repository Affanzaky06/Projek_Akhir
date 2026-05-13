import streamlit as st
import pandas as pd
import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl
import matplotlib.pyplot as plt

# ==========================================
# KONFIGURASI HALAMAN & NAVIGASI
# ==========================================
st.set_page_config(page_title="SPK Saham Fuzzy", layout="wide")

# Navigasi Sidebar
st.sidebar.title("Navigasi SPK")
menu = st.sidebar.radio("Pilih Halaman:", ["Profil Kelompok", "Halaman Data", "Hitung SPK"])

# Load Dataset
@st.cache_data
def load_data():
    # Menggunakan file dataset yang sudah diproses menjadi skala 0-100
    return pd.read_csv('dataset_saham_final.csv')

df_saham = load_data()

# ==========================================
# HALAMAN 1: PROFIL KELOMPOK
# ==========================================
if menu == "Profil Kelompok":
    st.title("Profil Kelompok Proyek Akhir")
    st.write("Sistem Pendukung Keputusan Pemilihan Saham Menggunakan Logika Fuzzy")
    st.markdown("""
    **Anggota Kelompok:**
    1. Abyaz Affanzaky Shanahan (NIM: ......)
    2. [Nama Anggota 2] (NIM: ......)
    3. [Nama Anggota 3] (Opsional jika ganjil)
    """)

# ==========================================
# HALAMAN 2: HALAMAN DATA
# ==========================================
elif menu == "Halaman Data":
    st.title("Dataset Fundamental Saham (2023)")
    st.write(f"Menampilkan dataset bersih dengan total **{len(df_saham)} baris data alternatif** dan **5 kriteria evaluasi**.")
    st.info("Nilai pada tabel di bawah sudah dikonversi ke dalam skala Persentil (0 - 100) agar kompatibel dengan sistem komputasi Fuzzy Logic.")
    
    # Menampilkan dataset dalam tabel interaktif
    st.dataframe(df_saham, use_container_width=True)

# ==========================================
# HALAMAN 3: HITUNG SPK (FUZZY)
# ==========================================
elif menu == "Hitung SPK":
    st.title("Perhitungan Kelayakan Investasi Saham")
    
    st.markdown("### Pengaturan Analisis")
    col1, col2 = st.columns(2)
    
    with col1:
        # WIDGET 1: Memilih alternatif saham
        pilihan_saham = st.multiselect(
            "Pilih Alternatif Saham yang ingin dievaluasi (Pilih beberapa):", 
            options=df_saham['Kode Saham'].tolist(),
            default=["AALI", "ABMM", "ACES", "TLKM"] # Sesuaikan defaultnya jika tidak ada
        )
    
    with col2:
        # WIDGET 2 & 3: Filter dan Urutan Tabel
        filter_skor = st.slider("Filter Skor Minimal Kelayakan:", 0, 100, 40)
        urutan = st.selectbox("Urutkan Hasil Berdasarkan:", ["Tertinggi ke Terendah", "Terendah ke Tertinggi"])

    # Tombol Eksekusi
    if st.button("Proses Perhitungan SPK", type="primary"):
        # Jika saham yang dipilih user ada di dataset
        df_evaluasi = df_saham[df_saham['Kode Saham'].isin(pilihan_saham)]
        
        if len(df_evaluasi) == 0:
            st.warning("Silakan pilih minimal 1 saham yang valid untuk dievaluasi.")
        else:
            with st.spinner('Membangun sistem fuzzy dan melakukan komputasi...'):
                
                # ---------------- 1. FUZZY SETUP ----------------
                return_saham = ctrl.Antecedent(np.arange(0, 101, 1), 'return')
                utang = ctrl.Antecedent(np.arange(0, 101, 1), 'utang')
                likuiditas = ctrl.Antecedent(np.arange(0, 101, 1), 'likuiditas')
                net_margin = ctrl.Antecedent(np.arange(0, 101, 1), 'net_margin')
                gross_margin = ctrl.Antecedent(np.arange(0, 101, 1), 'gross_margin')
                
                kelayakan = ctrl.Consequent(np.arange(0, 101, 1), 'kelayakan')

                # Membership Functions (Fungsi Keanggotaan)
                for var in [return_saham, utang, likuiditas, net_margin, gross_margin, kelayakan]:
                    var['rendah'] = fuzz.trimf(var.universe, [0, 0, 50])
                    var['sedang'] = fuzz.trimf(var.universe, [25, 50, 75])
                    var['tinggi'] = fuzz.trimf(var.universe, [50, 100, 100])

                kelayakan['buruk'] = fuzz.trimf(kelayakan.universe, [0, 0, 50])
                kelayakan['cukup'] = fuzz.trimf(kelayakan.universe, [25, 50, 75])
                kelayakan['baik'] = fuzz.trimf(kelayakan.universe, [50, 100, 100])

                # ---------------- 2. FUZZY RULE BASE ----------------
                rules = [
                    # Jika Return Tinggi, Net Margin Tinggi, dan Utang Rendah -> Baik
                    ctrl.Rule(return_saham['tinggi'] & net_margin['tinggi'] & utang['rendah'], kelayakan['baik']),
                    # Jika Likuiditas Tinggi dan Gross Margin Tinggi -> Baik
                    ctrl.Rule(likuiditas['tinggi'] & gross_margin['tinggi'], kelayakan['baik']),
                    # Jika Utang Sangat Tinggi -> Buruk
                    ctrl.Rule(utang['tinggi'], kelayakan['buruk']),
                    # Jika Net Margin Rendah -> Buruk
                    ctrl.Rule(net_margin['rendah'], kelayakan['buruk']),
                    # Jika Return Sedang dan Gross Margin Sedang -> Cukup
                    ctrl.Rule(return_saham['sedang'] & gross_margin['sedang'], kelayakan['cukup'])
                ]

                sistem_ctrl = ctrl.ControlSystem(rules)
                simulasi = ctrl.ControlSystemSimulation(sistem_ctrl)
                
                # ---------------- 3. KOMPUTASI ----------------
                hasil_akhir = []
                
                for index, row in df_evaluasi.iterrows():
                    simulasi.input['return'] = row['Return']
                    simulasi.input['utang'] = row['Utang']
                    simulasi.input['likuiditas'] = row['Likuiditas']
                    simulasi.input['net_margin'] = row['Net Margin']
                    simulasi.input['gross_margin'] = row['Gross Margin']

            
            # Syarat 5b: Menampilkan proses visualisasi kurva SPK Fuzzy
            st.markdown("---")
            st.subheader("📈 Proses SPK: Kurva Himpunan Fuzzy (Membership Functions)")
            st.write("Visualisasi Fuzzifikasi untuk seluruh variabel yang digunakan dalam sistem.")
            
            # Daftar kriteria yang akan digambar
            kriteria_list = [
                {'nama': 'Return', 'warna_rendah': 'r', 'warna_tinggi': 'g'},
                {'nama': 'Utang (DER)', 'warna_rendah': 'g', 'warna_tinggi': 'r'}, # Utang rendah itu baik (hijau)
                {'nama': 'Likuiditas', 'warna_rendah': 'r', 'warna_tinggi': 'g'},
                {'nama': 'Net Margin', 'warna_rendah': 'r', 'warna_tinggi': 'g'},
                {'nama': 'Gross Margin', 'warna_rendah': 'r', 'warna_tinggi': 'g'},
                {'nama': 'Kelayakan (OUTPUT)', 'warna_rendah': 'r', 'warna_tinggi': 'g'}
            ]
            
            x_val = np.arange(0, 101, 1)
            
            # Membuat grid layout 2 kolom untuk menampilkan grafik agar rapi
            col_grafik1, col_grafik2 = st.columns(2)
            
            for i, kriteria in enumerate(kriteria_list):
                fig, ax = plt.subplots(figsize=(6, 3))
                
                # Menggambar kurva (Rendah, Sedang, Tinggi)
                ax.plot(x_val, fuzz.trimf(x_val, [0, 0, 50]), kriteria['warna_rendah'], linewidth=1.5, label='Rendah/Buruk')
                ax.plot(x_val, fuzz.trimf(x_val, [25, 50, 75]), 'y', linewidth=1.5, label='Sedang/Cukup')
                ax.plot(x_val, fuzz.trimf(x_val, [50, 100, 100]), kriteria['warna_tinggi'], linewidth=1.5, label='Tinggi/Baik')
                
                ax.set_title(f"Fungsi Keanggotaan: {kriteria['nama']}")
                ax.set_ylabel('Derajat Keanggotaan')
                ax.set_xlabel('Skala (0-100)')
                ax.legend(fontsize='small')
                ax.grid(True, alpha=0.3)
                
                # Menempatkan grafik bergantian di kolom kiri dan kanan
                if i % 2 == 0:
                    with col_grafik1:
                        st.pyplot(fig)
                else:
                    with col_grafik2:
                        st.pyplot(fig)