import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
import altair as alt

# --- 1. CONFIG & STYLING ---
st.set_page_config(page_title="dd | Spatial Risk Engine", layout="wide", initial_sidebar_state="expanded")

# Inject custom CSS for a sleek, dark analytics aesthetic
st.markdown("""
    <style>
    /* Darken the background and style the metric cards */
    div[data-testid="metric-container"] {
        background-color: #1E1E1E;
        border: 1px solid #333;
        padding: 5% 10% 5% 10%;
        border-radius: 8px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
    }
    h1, h2, h3 { color: #E0E0E0; font-family: 'Helvetica Neue', sans-serif; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. DATA GENERATION ---
@st.cache_data
def load_data():
    # A. Target Zones (Your actual spec targets)
    zones = pd.DataFrame({
        "zone": ["Malibu", "Hollywood Hills", "Altadena", "Pasadena", "Downtown LA"],
        "lat": [34.0259, 34.1235, 34.1867, 34.1478, 34.0407],
        "lon": [-118.7798, -118.3217, -118.1312, -118.1445, -118.2468],
        "fuel": [95, 75, 88, 60, 10],
        "slope": [40, 35, 42, 22, 2],
    })
    zones["vor"] = (zones["fuel"] * zones["slope"]) / 100
    zones["height"] = zones["vor"] * 200 
    
    # B. Synthetic Background Risk Data (Creates the "Big Data" look)
    np.random.seed(42)
    num_points = 2000
    bg_lats = np.random.normal(34.15, 0.15, num_points)
    bg_lons = np.random.normal(-118.40, 0.30, num_points)
    bg_risk = np.random.uniform(10, 100, num_points)
    
    background = pd.DataFrame({'lat': bg_lats, 'lon': bg_lons, 'risk': bg_risk})
    return zones, background

zones_df, bg_df = load_data()

# --- 3. UI HEADER ---
st.title("🔥 dd: Climate-to-Spec Analytics")
st.markdown("Quantifying environmental exposure to optimize low-carbon residential construction in Los Angeles.")
st.divider()

# --- 4. MAIN DASHBOARD LAYOUT ---
col_map, col_analytics = st.columns([2.5, 1.5], gap="large")

with col_map:
    st.subheader("Spatial Risk Topography")
    
    # Layer 1: The glowing honeycomb background (Simulates massive CAL FIRE dataset)
    hex_layer = pdk.Layer(
        "HexagonLayer",
        bg_df,
        get_position=["lon", "lat"],
        auto_highlight=True,
        elevation_scale=15,
        pickable=True,
        elevation_range=[0, 1000],
        extruded=True,
        coverage=0.8,
        get_fill_color=["risk * 2.5", "50", "150", 140],
    )

    # Layer 2: The specific dd target sites
    column_layer = pdk.Layer(
        "ColumnLayer",
        zones_df,
        get_position=["lon", "lat"],
        get_elevation="height",
        elevation_scale=1,
        radius=1500,
        get_fill_color=[255, 75, 75, 255],
        pickable=True,
        auto_highlight=True,
    )

    # Map configuration
    view_state = pdk.ViewState(
        latitude=34.10, longitude=-118.35, zoom=9, pitch=55, bearing=-15
    )

    r = pdk.Deck(
        layers=[hex_layer, column_layer],
        initial_view_state=view_state,
        map_style="dark", # Native dark style for reliability
        tooltip={
            "html": "<b>{zone}</b><br/>VOR: {vor}<br/>Fuel Density: {fuel}%",
            "style": {"backgroundColor": "#1E1E1E", "color": "white", "font-family": "Helvetica"}
        }
    )
    st.pydeck_chart(r, use_container_width=True)
    st.caption("Map controls: Left-click to pan | Right-click to rotate/tilt | Scroll to zoom")

with col_analytics:
    st.subheader("Site Intelligence")
    selected_zone = st.selectbox("Select Residential Zone", zones_df["zone"])
    site_data = zones_df[zones_df["zone"] == selected_zone].iloc[0]
    
    # Key Metrics Grid
    m1, m2 = st.columns(2)
    m1.metric("VOR Score", f"{site_data['vor']:.1f}", "Value of Risk")
    m2.metric("Gradient", f"{site_data['slope']}°", "Topography")
    
    m3, m4 = st.columns(2)
    m3.metric("Fuel Density", f"{site_data['fuel']}%", "Vegetation")
    carbon_delta = "+45%" if site_data['vor'] > 30 else ("+15%" if site_data['vor'] > 10 else "Baseline")
    m4.metric("Embodied Carbon", carbon_delta, "Spec Premium", delta_color="inverse")
    
    st.divider()
    
    # Analytics Chart: Fuel vs Slope contribution to VOR
    st.write("**Risk Factor Breakdown**")
    chart_data = pd.DataFrame({
        "Factor": ["Fuel Density", "Slope Gradient"],
        "Impact Value": [site_data['fuel'], site_data['slope']]
    })
    
    chart = alt.Chart(chart_data).mark_bar(color='#FF4B4B').encode(
        x=alt.X('Impact Value:Q', title=None),
        y=alt.Y('Factor:N', sort='-x', title=None),
        tooltip=['Factor', 'Impact Value']
    ).properties(height=150).configure_view(strokeOpacity=0)
    
    st.altair_chart(chart, use_container_width=True)

    # The dd "So What?" - Material Spec Output
    st.write("**dd Prescriptive Spec**")
    if site_data['vor'] > 30:
        st.error("Class A Non-Combustible Assembly Required. Recommend LC3 Cement exterior with mineral wool cavity insulation to mitigate the +45% carbon premium.")
    elif site_data['vor'] > 15:
        st.warning("Ignition-Resistant Assembly Required. Recommend Fiber Cement siding (Limestone-based) and multi-pane tempered glazing.")
    else:
        st.success("Standard Assembly. FSC-Certified advanced timber framing acceptable. Focus on standard operational carbon reduction.")
