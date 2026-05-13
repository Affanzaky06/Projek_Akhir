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
    df = pd.read_csv('dataset_saham_final.csv')
    
    # 1. Membersihkan nama kolom (menghilangkan spasi gaib)
    df.columns = df.columns.str.strip()
    
    # 2. Menjaga-jaga jika nama kolom masih pakai nama rasio lama
    df = df.rename(columns={
        'symbol': 'Kode Saham',
        'ROE': 'Return',
        'DER': 'Utang',
        'Current Ratio': 'Likuiditas',
        'NPM': 'Net Margin',
        'GPM': 'Gross Margin'
    })
    return df

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
                    ctrl.Rule(return_saham['tinggi'] & net_margin['tinggi'] & utang['rendah'], kelayakan['baik']),
                    ctrl.Rule(likuiditas['tinggi'] & gross_margin['tinggi'], kelayakan['baik']),
                    ctrl.Rule(utang['tinggi'], kelayakan['buruk']),
                    ctrl.Rule(net_margin['rendah'], kelayakan['buruk']),
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

                    try:
                        simulasi.compute()
                        skor = simulasi.output['kelayakan']
                    except:
                        skor = 0.0 

                    if skor < 40:
                        status = "Kurang Layak 🔴"
                    elif skor < 70:
                        status = "Cukup Layak 🟡"
                    else:
                        status = "Layak Investasi 🟢"
                        
                    hasil_akhir.append({    
                        "Kode Saham": row['Kode Saham'],
                        "Skor Kelayakan": round(skor, 2),
                        "Rekomendasi": status
                    })

                df_hasil = pd.DataFrame(hasil_akhir)
                
                df_hasil = df_hasil[df_hasil['Skor Kelayakan'] >= filter_skor]
                is_ascending = True if urutan == "Terendah ke Tertinggi" else False
                df_hasil = df_hasil.sort_values(by="Skor Kelayakan", ascending=is_ascending).reset_index(drop=True)

            # ---------------- 4. TAMPILAN OUTPUT ----------------
            st.markdown("---")
            st.subheader("🏆 Tabel Hasil Perangkingan Kelayakan")
            
            if len(df_hasil) > 0:
                df_hasil.index = np.arange(1, len(df_hasil) + 1) 
                st.dataframe(df_hasil, use_container_width=True)
                
                st.subheader("📊 Grafik Hasil Akhir Saham Terpilih")
                st.write("Perbandingan skor kelayakan investasi dari saham-saham yang dievaluasi:")
                st.line_chart(data=df_hasil, x="Kode Saham", y="Skor Kelayakan", color="#4CAF50")
            else:
                st.info("Tidak ada saham yang memenuhi batas filter skor minimal.")
            
            st.markdown("---")
            st.subheader("📈 Proses SPK: Kurva Defuzzifikasi (Output)")
            st.write("Sesuai ketentuan proyek akhir, berikut adalah representasi fungsi keanggotaan untuk hasil akhir (Kelayakan Investasi) pada proses defuzzifikasi sistem SPK.")
            
            fig, ax = plt.subplots(figsize=(8, 3))
            x_val = np.arange(0, 101, 1)
            
            ax.plot(x_val, fuzz.trimf(x_val, [0, 0, 50]), 'r', linewidth=1.5, label='Buruk')
            ax.plot(x_val, fuzz.trimf(x_val, [25, 50, 75]), 'y', linewidth=1.5, label='Cukup')
            ax.plot(x_val, fuzz.trimf(x_val, [50, 100, 100]), 'g', linewidth=1.5, label='Baik')
            
            ax.set_title('Fungsi Keanggotaan Output: Kelayakan')
            ax.set_ylabel('Derajat Keanggotaan')
            ax.set_xlabel('Skor Kelayakan (0-100)')
            ax.legend(fontsize='small')
            ax.grid(True, alpha=0.3)
            
            st.pyplot(fig)