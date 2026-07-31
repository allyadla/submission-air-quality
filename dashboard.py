import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import folium
from streamlit_folium import st_folium

# ---------- Load Data ----------
main_df = pd.read_csv('main_data.csv.gz')
main_df['datetime'] = pd.to_datetime(main_df['datetime'])

st.title('Dashboard Analisis Kualitas Udara Beijing')
st.write('Dataset: Air Quality Dataset (12 stasiun, 2013-2017)')

# ---------- Sidebar Filter ----------
st.sidebar.header('Filter')
daftar_stasiun = ['Semua Stasiun'] + sorted(main_df['station'].unique().tolist())
pilihan_stasiun = st.sidebar.selectbox('Pilih Stasiun', daftar_stasiun)

daftar_tahun = ['Semua Tahun'] + sorted(main_df['year'].unique().tolist())
pilihan_tahun = st.sidebar.selectbox('Pilih Tahun', daftar_tahun)

daftar_bulan = ['Semua Bulan'] + list(range(1, 13))
pilihan_bulan = st.sidebar.selectbox('Pilih Bulan', daftar_bulan)

df_filtered = main_df.copy()
if pilihan_stasiun != 'Semua Stasiun':
    df_filtered = df_filtered[df_filtered['station'] == pilihan_stasiun]
if pilihan_tahun != 'Semua Tahun':
    df_filtered = df_filtered[df_filtered['year'] == pilihan_tahun]
if pilihan_bulan != 'Semua Bulan':
    df_filtered = df_filtered[df_filtered['month'] == pilihan_bulan]

# ---------- KPI Cards ----------
col1, col2, col3, col4 = st.columns(4)
col1.metric('Rata-rata PM2.5', f"{df_filtered['PM2.5'].mean():.2f}")
col2.metric('Jam Tidak Sehat', f"{(df_filtered['kategori_kualitas_udara'] == 'Tidak Sehat').sum():,}")
col3.metric('Jam Baik', f"{(df_filtered['kategori_kualitas_udara'] == 'Baik').sum():,}")
col4.metric('Kategori Dominan', df_filtered['kategori_kualitas_udara'].mode()[0])

st.divider()

# ---------- Baris 1: Line chart tren + Distribusi kategori per stasiun ----------
row1_col1, row1_col2 = st.columns(2)

with row1_col1:
    st.subheader('Tren Rata-rata PM2.5 Bulanan per Stasiun')
    df_filtered_copy = df_filtered.copy()
    df_filtered_copy['bulan_tahun'] = df_filtered_copy['datetime'].dt.to_period('M')
    tren_per_stasiun = df_filtered_copy.groupby(['bulan_tahun', 'station'])['PM2.5'].mean().unstack()

    fig1, ax1 = plt.subplots(figsize=(6, 4))
    for stasiun in tren_per_stasiun.columns:
        ax1.plot(tren_per_stasiun.index.astype(str), tren_per_stasiun[stasiun], label=stasiun, linewidth=1)
    ax1.set_xlabel('Bulan')
    ax1.set_ylabel('Rata-rata PM2.5')
    ax1.tick_params(axis='x', rotation=90)
    ax1.legend(fontsize=6, loc='upper right', ncol=2)
    st.pyplot(fig1)

with row1_col2:
    st.subheader('Distribusi Kategori Kualitas Udara per Stasiun')
    distribusi_stasiun = pd.crosstab(df_filtered['station'], df_filtered['kategori_kualitas_udara'])
    for kol in ['Baik', 'Sedang', 'Tidak Sehat']:
        if kol not in distribusi_stasiun.columns:
            distribusi_stasiun[kol] = 0
    distribusi_stasiun = distribusi_stasiun[['Baik', 'Sedang', 'Tidak Sehat']]
    fig2, ax2 = plt.subplots(figsize=(6, 4))
    distribusi_stasiun.plot(kind='barh', stacked=True, ax=ax2, color=['#43A047', '#FDD835', '#D72638'])
    ax2.set_xlabel('Jumlah Data')
    ax2.set_ylabel('')
    st.pyplot(fig2)

st.divider()

# ---------- Baris 2: Rata-rata PM2.5 per stasiun + Pie chart kategori ----------
row2_col1, row2_col2 = st.columns(2)

avg_pm25_station = main_df.groupby('station')['PM2.5'].mean().sort_values(ascending=False)

with row2_col1:
    st.subheader('Rata-rata PM2.5 per Stasiun')
    fig3, ax3 = plt.subplots(figsize=(6, 4))
    colors = ['#D3D3D3'] * len(avg_pm25_station)
    colors[0] = '#D72638'
    colors[-1] = '#1E88E5'
    sns.barplot(x=avg_pm25_station.values, y=avg_pm25_station.index, palette=colors, ax=ax3)
    ax3.set_xlabel('Rata-rata PM2.5')
    ax3.set_ylabel('')
    st.pyplot(fig3)

with row2_col2:
    st.subheader('Proporsi Kategori Kualitas Udara')
    distribusi_kategori = df_filtered['kategori_kualitas_udara'].value_counts()
    fig4, ax4 = plt.subplots(figsize=(6, 4))
    ax4.pie(distribusi_kategori.values, labels=distribusi_kategori.index, autopct='%1.1f%%',
            colors=['#43A047', '#FDD835', '#D72638'])
    st.pyplot(fig4)

st.divider()

# ---------- Peta Geospasial (full width) ----------
st.subheader('Peta Sebaran Rata-rata PM2.5 per Stasiun')

station_coords = {
    'Aotizhongxin':   (39.982, 116.397), 'Changping':      (40.220, 116.231),
    'Dingling':       (40.292, 116.220), 'Dongsi':         (39.929, 116.417),
    'Guanyuan':       (39.929, 116.339), 'Gucheng':        (39.914, 116.184),
    'Huairou':        (40.328, 116.628), 'Nongzhanguan':   (39.933, 116.461),
    'Shunyi':         (40.127, 116.655), 'Tiantan':        (39.886, 116.407),
    'Wanliu':         (39.987, 116.287), 'Wanshouxigong':  (39.878, 116.352),
}

peta_pm25 = folium.Map(location=[39.95, 116.40], zoom_start=9, tiles='CartoDB positron')
for stasiun, rata2 in avg_pm25_station.items():
    lat, lon = station_coords[stasiun]
    warna = 'red' if rata2 == avg_pm25_station.max() else ('blue' if rata2 == avg_pm25_station.min() else 'orange')
    folium.CircleMarker(
        location=[lat, lon], radius=8 + (rata2 / avg_pm25_station.max()) * 12,
        popup=f'{stasiun}: {rata2:.1f} µg/m³', tooltip=stasiun,
        color=warna, fill=True, fill_color=warna, fill_opacity=0.7
    ).add_to(peta_pm25)

st_folium(peta_pm25, width=1300, height=450)

st.divider()

# ---------- Pengelompokan Stasiun ----------
st.subheader('Pengelompokan Stasiun Berdasarkan Tingkat Polusi')
batas_tinggi = avg_pm25_station.quantile(0.66)
batas_rendah = avg_pm25_station.quantile(0.33)

def kelompok_stasiun(nilai):
    if nilai >= batas_tinggi:
        return 'Polusi Tinggi'
    elif nilai >= batas_rendah:
        return 'Polusi Sedang'
    return 'Polusi Rendah'

ringkasan_kelompok = pd.DataFrame({
    'rata_rata_pm25': avg_pm25_station,
    'kelompok': avg_pm25_station.apply(kelompok_stasiun)
}).sort_values('rata_rata_pm25', ascending=False)
st.dataframe(ringkasan_kelompok)

# ---------- Dataset mentah, disembunyikan di expander ----------
with st.expander('Lihat Dataset Mentah'):
    st.dataframe(df_filtered)