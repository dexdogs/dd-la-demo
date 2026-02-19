import streamlit as st
import pandas as pd
import pydeck as pdk

# --- CONFIG ---
st.set_page_config(page_title="dd: 3D Resilience Engine", layout="wide")

# --- DATASET ---
# VOR = (Fuel * Slope) / 100. 
data = pd.DataFrame({
    "zone": ["Malibu", "Hollywood Hills", "Altadena", "Pasadena", "Downtown LA"],
    "lat": [34.0259, 34.1235, 34.1867, 34.1478, 34.0407],
    "lon": [-118.7798, -118.3217, -118.1312, -118.1445, -118.2468],
    "fuel": [95, 75, 88, 60, 10],
    "slope": [40, 35, 42, 22, 2],
})

data["vor"] = (data["fuel"] * data["slope"]) / 100
data["height"] = data["vor"] * 120  # Subtle, short towers

# --- UI ---
st.title("🔥 dd (Dexdogs) 3D VOR Analytics")
st.caption("Overlay: CAL FIRE Hazard Severity Zones (Simulated) + dd Spatial Risk")

col1, col2 = st.columns([2, 1])

with col1:
    # 1. HEATMAP LAYER (Simulating Wildfire Risk Data Set)
    heatmap_layer = pdk.Layer(
        "HeatmapLayer",
        data,
        get_position=["lon", "lat"],
        get_weight="fuel",
        radius_pixels=100,
        opacity=0.4,
    )

    # 2. VOR COLUMN LAYER (Your Analytics)
    column_layer = pdk.Layer(
        "ColumnLayer",
        data,
        get_position=["lon", "lat"],
        get_elevation="height",
        elevation_scale=1,
        radius=1000,
        get_fill_color=["vor * 6", "150 - (vor * 2)", 200, 200],
        pickable=True,
        auto_highlight=True,
    )

    view_state = pdk.ViewState(
        latitude=34.10, longitude=-118.40, zoom=9, pitch=45, bearing=0
    )

    # Using CartoDB Dark Matter for the map background
    r = pdk.Deck(
        layers=[heatmap_layer, column_layer],
        initial_view_state=view_state,
        map_style="mapbox://styles/mapbox/dark-v11", # High-contrast dark
        tooltip={"text": "{zone}\nVOR Score: {vor}\nFuel: {fuel}% | Slope: {slope}°"}
    )
    st.pydeck_chart(r)

with col2:
    st.write("### 📊 Advanced Site Analytics")
    selection = st.selectbox("Deep Dive Zone", data["zone"])
    row = data[data["zone"] == selection].iloc[0]
    
    # Grid of Metrics
    m1, m2 = st.columns(2)
    m1.metric("VOR Score", row["vor"])
    m2.metric("Fuel Load", f"{row['fuel']}%")
    
    m3, m4 = st.columns(2)
    m3.metric("Slope Gradient", f"{row['slope']}°")
    m4.metric("Risk Level", "Critical" if row["vor"] > 30 else "Moderate")

    st.divider()
    
    # Material Logic
    st.write("#### Prescription Specs")
    if row["vor"] > 30:
        st.error(f"**Zone:** {selection}\n\n**Material:** UHPC + Ember-Resistant Multi-pane Windows.")
    else:
        st.success(f"**Zone:** {selection}\n\n**Material:** Standard Fire-Treated Wood Frame.")

    with st.expander("🔍 VOR Definition"):
        st.write("""
        **Value of Risk (VOR)** is the dd-proprietary intersection of topography and combustible fuel. 
        It converts 'scary' climate data into a specification tool for residential builders.
        """)

st.sidebar.markdown("""
### Map Settings
- **Theme:** Dark Matter
- **Overlay:** Fire Severity Heatmap
- **Data Source:** dd Risk Engine
""")
