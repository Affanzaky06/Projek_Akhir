# =========================
# IMPORT LIBRARY
# =========================
import streamlit as st
import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl
import pandas as pd # Tambahkan pandas untuk membuat tabel

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
# MEMBUAT VARIABEL FUZZY
# =========================

# Input fuzzy
return_saham = ctrl.Antecedent(np.arange(0, 101, 1), 'return_saham')
volatilitas = ctrl.Antecedent(np.arange(0, 101, 1), 'volatilitas')
pertumbuhan = ctrl.Antecedent(np.arange(0, 101, 1), 'pertumbuhan')
utang = ctrl.Antecedent(np.arange(0, 101, 1), 'utang')
dividen = ctrl.Antecedent(np.arange(0, 101, 1), 'dividen')

# Output fuzzy
kelayakan = ctrl.Consequent(np.arange(0, 101, 1), 'kelayakan')

# =========================
# FUNGSI KEANGGOTAAN INPUT & OUTPUT
# =========================

for var in [return_saham, volatilitas, pertumbuhan, utang, dividen]:
    var['rendah'] = fuzz.trimf(var.universe, [0, 0, 50])
    var['sedang'] = fuzz.trimf(var.universe, [25, 50, 75])
    var['tinggi'] = fuzz.trimf(var.universe, [50, 100, 100])

kelayakan['buruk'] = fuzz.trimf(kelayakan.universe, [0, 0, 50])
kelayakan['cukup'] = fuzz.trimf(kelayakan.universe, [25, 50, 75])
kelayakan['baik'] = fuzz.trimf(kelayakan.universe, [50, 100, 100])

# =========================
# RULE BASE & SISTEM FUZZY
# =========================

rules = [
    ctrl.Rule(return_saham['tinggi'] & pertumbuhan['tinggi'] & utang['rendah'], kelayakan['baik']),
    ctrl.Rule(return_saham['sedang'] & dividen['sedang'], kelayakan['cukup']),
    ctrl.Rule(volatilitas['tinggi'] | utang['tinggi'], kelayakan['buruk']),
    ctrl.Rule(dividen['tinggi'] & volatilitas['rendah'], kelayakan['baik']),
    ctrl.Rule(pertumbuhan['rendah'], kelayakan['buruk'])
]

sistem_ctrl = ctrl.ControlSystem(rules)
simulasi = ctrl.ControlSystemSimulation(sistem_ctrl)

# =========================
# PILIH SAHAM & INPUT USER (TABS)
# =========================
st.subheader("Masukkan Nilai Kriteria per Saham")

# 5 Saham Alternatif
saham_list = ["BBCA", "BBRI", "TLKM", "UNVR", "BMRI"]

# Membuat UI Tabs untuk masing-masing saham agar rapi
tabs = st.tabs(saham_list)

# Dictionary untuk menyimpan input user
data_input = {}

for i, saham in enumerate(saham_list):
    with tabs[i]:
        st.write(f"**Atur kriteria untuk {saham}**")
        
        # Menggunakan kolom agar slider bersebelahan
        col1, col2 = st.columns(2)
        
        with col1:
            ret = st.slider(f"Return", 0, 100, 70, key=f"ret_{saham}")
            vol = st.slider(f"Volatilitas", 0, 100, 40, key=f"vol_{saham}")
            pert = st.slider(f"Pertumbuhan Laba", 0, 100, 75, key=f"pert_{saham}")
        
        with col2:
            utg = st.slider(f"Utang", 0, 100, 30, key=f"utg_{saham}")
            div = st.slider(f"Dividen", 0, 100, 65, key=f"div_{saham}")
            
        # Simpan nilai input ke dalam dictionary
        data_input[saham] = {
            'return': ret,
            'volatilitas': vol,
            'pertumbuhan': pert,
            'utang': utg,
            'dividen': div
        }

# =========================
# PROSES FUZZY & HASIL OUTPUT
# =========================
st.markdown("---")
st.subheader("Tabel Hasil Analisis & Rekomendasi")

hasil_akhir = []

# Looping untuk memproses masing-masing saham ke dalam sistem fuzzy
for saham in saham_list:
    simulasi.input['return_saham'] = data_input[saham]['return']
    simulasi.input['volatilitas'] = data_input[saham]['volatilitas']
    simulasi.input['pertumbuhan'] = data_input[saham]['pertumbuhan']
    simulasi.input['utang'] = data_input[saham]['utang']
    simulasi.input['dividen'] = data_input[saham]['dividen']
    
    try:
        simulasi.compute()
        skor = simulasi.output['kelayakan']
    except:
        # Fallback jika input tidak memicu rule apapun
        skor = 0.0 

    # Interpretasi Hasil
    if skor < 40:
        rekomendasi = "Kurang Layak Investasi 🔴"
    elif skor < 70:
        rekomendasi = "Cukup Layak Investasi 🟡"
    else:
        rekomendasi = "Layak Investasi 🟢"
        
    hasil_akhir.append({
        "Saham": saham,
        "Skor Kelayakan": round(skor, 2),
        "Status Rekomendasi": rekomendasi
    })

# Konversi hasil ke DataFrame
df_hasil = pd.DataFrame(hasil_akhir)

# Opsional: Urutkan dari skor tertinggi ke terendah
df_hasil = df_hasil.sort_values(by="Skor Kelayakan", ascending=False).reset_index(drop=True)

# Tampilkan tabel di Streamlit
st.dataframe(
    df_hasil, 
    use_container_width=True,
    hide_index=True
)

st.markdown("---")
st.subheader("Grafik Perbandingan Kelayakan Saham")

# 2. Menampilkan Grafik Bar Chart
# Menggunakan kolom "Saham" sebagai sumbu X dan "Skor Kelayakan" sebagai sumbu Y
st.line_chart(data=df_hasil, x="Saham", y="Skor Kelayakan")