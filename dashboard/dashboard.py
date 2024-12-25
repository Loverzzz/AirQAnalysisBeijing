import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Set page config
st.set_page_config(
    page_title="Air Quality Analysis Dashboard",
    page_icon="🌍",
    layout="wide"
)

# Load and process data
@st.cache_data
def load_data():
    # Baca CSV file tanpa menggunakan index
    df = pd.read_csv('main_data.csv')
    
    # Convert to datetime
    df['datetime'] = pd.to_datetime(df[['year', 'month', 'day', 'hour']])
    
    # Add season column
    df['month'] = df['datetime'].dt.month
    df['season'] = pd.cut(df['month'],
                         bins=[0, 3, 6, 9, 12],
                         labels=['Winter', 'Spring', 'Summer', 'Fall'],
                         include_lowest=True)
    return df

# Load data
try:
    df = load_data()
except Exception as e:
    st.error(f"Error loading data: {str(e)}")
    st.stop()

# Sidebar
st.sidebar.title("Air Quality Analysis")

# Date filter
min_date = df['datetime'].min()
max_date = df['datetime'].max()
start_date = st.sidebar.date_input('Start Date', min_date)
end_date = st.sidebar.date_input('End Date', max_date)

# Station filter
stations = sorted(df['station'].unique())
selected_station = st.sidebar.selectbox('Select Station', stations)

# Filter data
mask = ((df['datetime'].dt.date >= start_date) & (df['datetime'].dt.date <= end_date) & (df['station'] == selected_station))
filtered_df = df.loc[mask].copy()  # Use copy to avoid SettingWithCopyWarning

# Main page
st.title("Beijing Air Quality Analysis")

# Metrics
col1, col2, col3, col4 = st.columns(4)
with col1:
    avg_pm25 = filtered_df['PM2.5'].mean()
    st.metric("Average PM2.5", f"{avg_pm25:.2f} μg/m³")
with col2:
    avg_pm10 = filtered_df['PM10'].mean()
    st.metric("Average PM10", f"{avg_pm10:.2f} μg/m³")
with col3:
    avg_temp = filtered_df['TEMP'].mean()
    st.metric("Average Temperature", f"{avg_temp:.1f} °C")
with col4:
    avg_humid = filtered_df['DEWP'].mean()
    st.metric("Average Dew Point", f"{avg_humid:.1f} °C")

# Time series plot
st.subheader("Pollutant Levels Over Time")
pollutants = ['PM2.5', 'PM10', 'SO2', 'NO2', 'CO', 'O3']
selected_pollutant = st.selectbox('Select Pollutant', pollutants)

fig_time = px.line(filtered_df, 
                   x='datetime', 
                   y=selected_pollutant,
                   title=f'{selected_pollutant} Levels at {selected_station}')
st.plotly_chart(fig_time, use_container_width=True)

# Seasonal analysis
st.subheader("Seasonal Analysis")
seasonal_avg = filtered_df.groupby('season')[pollutants].mean().reset_index()
fig_season = px.bar(seasonal_avg,
                    x='season',
                    y=pollutants,
                    title='Average Pollutant Levels by Season',
                    barmode='group')
st.plotly_chart(fig_season, use_container_width=True)

# Comparison across stations
st.subheader("Comparison of Average Pollutant Levels Across Stations")

# Load data rata-rata per stasiun
station_avg = pd.read_csv('station_average.csv')

# Pilih polutan untuk dibandingkan
selected_pollutant_station = st.selectbox("Select Pollutant for Station Comparison", pollutants)

# Visualisasi perbandingan rata-rata antar stasiun
fig_station = px.bar(
    station_avg,
    x='station',
    y=selected_pollutant_station,
    title=f'Average {selected_pollutant_station} Levels Across Stations',
    labels={'station': 'Station', selected_pollutant_station: f'{selected_pollutant_station} Concentration'},
    color='station'
)
st.plotly_chart(fig_station, use_container_width=True)


# Wind direction analysis if 'wd' column exists
if 'wd' in df.columns and 'WSPM' in df.columns:
    st.subheader("Wind Direction Analysis")
    wind_data = filtered_df.groupby('wd')['WSPM'].mean().reset_index()
    fig_wind = go.Figure(go.Barpolar(
        r=wind_data['WSPM'],
        theta=wind_data['wd'],
        name='Wind Speed (m/s)',
        marker_color=wind_data['WSPM'],
        marker_colorscale='Viridis'
    ))
    fig_wind.update_layout(title='Wind Rose Diagram')
    st.plotly_chart(fig_wind, use_container_width=True)

# Correlation heatmap
st.subheader("Correlation Analysis")
corr_matrix = filtered_df[pollutants].corr()
fig_corr = px.imshow(corr_matrix,
                     labels=dict(color="Correlation"),
                     color_continuous_scale="RdBu")
st.plotly_chart(fig_corr, use_container_width=True)

# Display data table without index
st.subheader("Raw Data")
# Reset index and don't show it in the dataframe
display_df = filtered_df.reset_index(drop=True)
st.dataframe(display_df)