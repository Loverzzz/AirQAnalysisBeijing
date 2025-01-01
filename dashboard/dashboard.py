import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Konfigurasi halaman
st.set_page_config(
    page_title="Dashboard Analisis Kualitas Udara",
    page_icon="🌍",
    layout="wide"
)

# Fungsi memuat data
@st.cache_data
def load_data():
    # Membaca file CSV
    df = pd.read_csv('dashboard/dashboard.py')
    
    # Tambahkan kolom waktu dan musim
    df['datetime'] = pd.to_datetime(df[['year', 'month', 'day', 'hour']])
    df['month'] = df['datetime'].dt.month
    df['month_name'] = df['datetime'].dt.strftime('%B')  # Nama bulan (Januari, Februari, ...)
    
    # Tentukan musim berdasarkan bulan
    def get_season(month):
        if month in [12, 1, 2]:
            return 'Winter'
        elif month in [3, 4, 5]:
            return 'Spring'
        elif month in [6, 7, 8]:
            return 'Summer'
        elif month in [9, 10, 11]:
            return 'Fall'

    # Tambahkan kolom 'season'
    df['season'] = df['month'].apply(get_season)
    
    # Penanganan missing values dengan interpolasi
    numeric_columns = ['PM2.5', 'PM10', 'SO2', 'NO2', 'CO', 'O3', 'TEMP', 'PRES', 'DEWP', 'RAIN', 'WSPM']
    for column in numeric_columns:
        df[column] = df[column].interpolate(method='linear').fillna(method='ffill').fillna(method='bfill')
    
    return df

# Memuat data
try:
    df = load_data()
except Exception as e:
    st.error(f"Error memuat data: {str(e)}")
    st.stop()

# Sidebar
st.sidebar.title("Pengaturan Filter")

# Tampilkan rentang waktu 
min_date, max_date = df['datetime'].min().strftime('%Y-%m-%d'), df['datetime'].max().strftime('%Y-%m-%d')
st.sidebar.write(f"Rentang Tanggal: {min_date} hingga {max_date}")

# Filter Stasiun
stations = ['Semua Stasiun'] + sorted(df['station'].unique())  
selected_station = st.sidebar.selectbox('Pilih Stasiun', stations)

# Filter Data
filtered_df = df.copy()
if selected_station != 'Semua Stasiun':
    filtered_df = filtered_df[filtered_df['station'] == selected_station]

# Halaman Utama
st.title("Dashboard Analisis Kualitas Udara di Beijing")

# Statistik Utama 
col1, col2, col3, col4 = st.columns(4)
col1.metric("Rata-rata PM2.5", f"{filtered_df['PM2.5'].mean():.2f} μg/m³")
col2.metric("Rata-rata PM10", f"{filtered_df['PM10'].mean():.2f} μg/m³")
col3.metric("Rata-rata Suhu", f"{filtered_df['TEMP'].mean():.2f} °C")
col4.metric("Rata-rata Curah Hujan", f"{filtered_df['RAIN'].mean():.2f} mm")

# **Pertanyaan 1: Pola Kualitas Udara**
st.subheader("Pola Harian dan Musiman PM2.5")
# Pola Harian
fig_hourly = px.line(
    filtered_df.groupby('hour')['PM2.5'].mean().reset_index(),
    x='hour',
    y='PM2.5',
    title='Rata-rata PM2.5 per Jam',
    labels={'hour': 'Jam', 'PM2.5': 'PM2.5 (µg/m³)'}
)
st.plotly_chart(fig_hourly, use_container_width=True)

# Pola Musiman/Bulanan PM2.5
monthly_avg = filtered_df.groupby(['month', 'season'])['PM2.5'].mean().reset_index()

fig_monthly = px.bar(
    monthly_avg,
    x='month',
    y='PM2.5',
    color='season',  # Warna berdasarkan musim
    title='Rata-rata PM2.5 per Bulan (dengan Keterangan Musim)',
    labels={'month': 'Bulan (1-12)', 'PM2.5': 'PM2.5 (µg/m³)', 'season': 'Musim'},
    color_discrete_sequence=px.colors.qualitative.Set2,
)

# Anotasi keterangan musim di bawah sumbu x
fig_monthly.update_layout(
    xaxis=dict(
        tickmode='array',
        tickvals=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
        ticktext=[
            "Jan (Winter)", "Feb (Winter)", "Mar (Spring)", "Apr (Spring)",
            "May (Spring)", "Jun (Summer)", "Jul (Summer)", "Aug (Summer)",
            "Sep (Fall)", "Oct (Fall)", "Nov (Fall)", "Dec (Winter)"
        ]
    )
)
st.plotly_chart(fig_monthly, use_container_width=True)

# **Pertanyaan 2: Pengaruh Cuaca**
# Hubungan PM2.5 dengan Kecepatan Angin
fig_scatter_wspm = px.scatter(
    filtered_df,
    x='WSPM',
    y='PM2.5',
    title=f'Hubungan Kecepatan Angin dengan PM2.5 - {selected_station}',
    labels={'WSPM': 'Kecepatan Angin (m/s)', 'PM2.5': 'PM2.5 (µg/m³)'},
    opacity=0.5
)
st.plotly_chart(fig_scatter_wspm, use_container_width=True)

# Hubungan PM2.5 dengan Curah Hujan
fig_scatter_rain = px.scatter(
    filtered_df,
    x='RAIN',
    y='PM2.5',
    title='Hubungan Curah Hujan dengan PM2.5',
    labels={'RAIN': 'Curah Hujan (mm)', 'PM2.5': 'PM2.5 (µg/m³)'}
)
st.plotly_chart(fig_scatter_rain, use_container_width=True)

# **Pertanyaan 3: Variasi Antar Stasiun**
st.subheader("Rata-rata PM2.5 Antar Stasiun")
if selected_station == 'Semua Stasiun':
    station_avg = df.groupby('station')['PM2.5'].mean().reset_index()
else:
    station_avg = filtered_df.groupby('station')['PM2.5'].mean().reset_index()

fig_station = px.bar(
    station_avg,
    x='station',
    y='PM2.5',
    title='Rata-rata PM2.5 Antar Stasiun',
    labels={'station': 'Stasiun', 'PM2.5': 'PM2.5 (µg/m³)'},
    color='station' if selected_station == 'Semua Stasiun' else None
)
st.plotly_chart(fig_station, use_container_width=True)

# **Pertanyaan 4: Korelasi Antar Polutan**
st.subheader("Korelasi Antar Polutan")
corr_matrix = filtered_df[['PM2.5', 'PM10', 'SO2', 'NO2', 'CO', 'O3']].corr()
fig_corr = px.imshow(
    corr_matrix,
    title='Korelasi Antar Polutan',
    labels=dict(color='Korelasi'),
    color_continuous_scale='RdBu'
)
st.plotly_chart(fig_corr, use_container_width=True)

# **Pertanyaan 5: Pengaruh Hujan**
st.subheader("Distribusi PM2.5 Berdasarkan Curah Hujan")
filtered_df['RAIN_CATEGORY'] = pd.cut(
    filtered_df['RAIN'], 
    bins=[0, 10, 20, 50, 100], 
    labels=['0-10 mm', '10-20 mm', '20-50 mm', '50-100 mm']
)
fig_rain_box = px.box(
    filtered_df,
    x='RAIN_CATEGORY',
    y='PM2.5',
    title='Distribusi PM2.5 Berdasarkan Curah Hujan',
    labels={'RAIN_CATEGORY': 'Curah Hujan (mm)', 'PM2.5': 'PM2.5 (µg/m³)'}
)
st.plotly_chart(fig_rain_box, use_container_width=True)

# Menampilkan Data Mentah
st.subheader("Data Mentah")
st.dataframe(filtered_df)
