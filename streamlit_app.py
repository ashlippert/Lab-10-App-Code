import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import folium
from streamlit_folium import folium_static

# Load datasets
station_file = "station.csv"
result_file = "narrowresult.csv"

# Read CSV files and handle potential missing data
df_stations = pd.read_csv(station_file)
df_results = pd.read_csv(result_file)

# Ensure the 'ActivityStartDate' is in datetime format
df_results["ActivityStartDate"] = pd.to_datetime(df_results["ActivityStartDate"], errors='coerce')

# Streamlit app layout
st.title("USGS Water Quality Data Explorer")

# ---- 1️⃣ Mapping Station Locations ----
st.header("📍 Water Quality Monitoring Stations")

# Filter unique stations with location data
if "MonitoringLocationIdentifier" in df_stations.columns:
    unique_stations = df_stations.drop_duplicates(subset=["MonitoringLocationIdentifier"]).dropna(subset=["LatitudeMeasure", "LongitudeMeasure"])
    if not unique_stations.empty:
        map_center = [unique_stations["LatitudeMeasure"].mean(), unique_stations["LongitudeMeasure"].mean()]
        
        # Create Folium map
        m = folium.Map(location=map_center, zoom_start=6)
        
        for _, row in unique_stations.iterrows():
            folium.Marker(
                location=[row["LatitudeMeasure"], row["LongitudeMeasure"]],
                popup=row["MonitoringLocationIdentifier"],
            ).add_to(m)

        folium_static(m)
    else:
        st.warning("No valid station locations found.")
else:
    st.warning("Station location data missing.")

# ---- 2️⃣ Water Quality Data Analysis ----
st.header("📊 Water Quality Trends")

# Dropdown for characteristic selection
characteristics = df_results["CharacteristicName"].dropna().unique().tolist()
char1 = st.selectbox("Select first water quality characteristic:", characteristics)
char2 = st.selectbox("Select second characteristic (optional):", ["None"] + characteristics)

# Plot function
def plot_characteristics(char1, char2=None):
    plt.figure(figsize=(12, 6))

    # Ensure that 'ActivityStartDate' is in datetime format
    df_results['ActivityStartDate'] = pd.to_datetime(df_results['ActivityStartDate'], errors='coerce')

    # Convert 'ResultMeasureValue' to numeric, ignoring errors
    df_results['ResultMeasureValue'] = pd.to_numeric(df_results['ResultMeasureValue'], errors='coerce')

    for char in [char1, char2] if char2 != "None" else [char1]:
        filtered_df = df_results[df_results["CharacteristicName"] == char].sort_values(by="ActivityStartDate")

        for site_id, site_data in filtered_df.groupby("MonitoringLocationIdentifier"):
            # Ensure that both x (date) and y (value) are correctly formatted
            plt.plot(site_data["ActivityStartDate"], site_data["ResultMeasureValue"], label=f"{str(site_id)} - {char}")
    
    plt.xlabel("Date")
    plt.ylabel("Measured Value")
    plt.title(f"Water Quality Trends: {char1} {f'vs {char2}' if char2 != 'None' else ''}")
    plt.legend(title="Site & Characteristic", bbox_to_anchor=(1.05, 1), loc="upper left")
    plt.xticks(rotation=45)
    plt.tight_layout()
    st.pyplot(plt)


# Generate plot button
if st.button("Plot Data"):
    plot_characteristics(char1, char2)

