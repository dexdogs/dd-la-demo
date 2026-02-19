import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
import altair as alt

# --- 1. CONFIG & STYLING ---
st.set_page_config(page_title="dd | Spatial Risk Engine", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    div[data-testid="metric-container"] {
        background-color: #1E1E1E; border: 1px solid #333; padding: 5%; border-radius: 8px;
    }
    h1, h2, h3, p { color: #E0E0E0; font-family: 'Helvetica Neue', sans-serif; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. DATA GENERATION ---
@st.cache_data
def load_data():
    zones = pd.DataFrame({
        "zone": ["Malibu", "Hollywood Hills", "Altadena", "Pasadena", "Downtown LA"],
        "lat": [34.0259, 34.1235, 34.1867, 34.1478, 34.0407],
        "lon": [-118.7798, -118.3217, -118.1312, -118.1445, -118.2468],
        "fuel": [95, 75, 88, 60, 10],
        "slope": [40, 35, 42, 22, 2],
    })
    # Rounding VOR for clean tooltip display
    zones["vor"] = ((zones["fuel"] * zones["slope"]) / 100).round(1)
    zones["height"] = zones["vor"] * 250 
    
    np.random.seed(42)
    bg = pd.DataFrame({
        'lat': np.random.normal(34.15, 0.15, 2000), 
        'lon': np.random.normal(-118.40, 0.30, 2000), 
        'risk': np.random.uniform(10, 100, 2000)
    })
    return zones, bg

zones_df, bg_df = load_data()

# --- 3. UI DASHBOARD ---
st.title("🔥 dd: Climate-to-Spec Analytics")
st.markdown("Quantifying environmental exposure to optimize low-carbon residential construction in Los Angeles.")
st.divider()

col_map, col_analytics = st.columns([2.5, 1.5], gap="large")

with col_analytics:
    st.subheader("Layer Controls")
    # Toggles to control visual clutter
    show_towers = st.toggle("Show VOR Site Towers", value=True)
    show_heatmap = st.toggle("Show Regional Risk Hexagons", value=True)
    
    st.divider()
    
    st.subheader("Site Intelligence")
    selected_zone = st.selectbox("Select Residential Zone", zones_df["zone"])
    site_data = zones_df[zones_df["zone"] == selected_zone].iloc[0]
    
    m1, m2 = st.columns(2)
    m1.metric("VOR Score", site_data['vor'])
    m2.metric("Gradient", f"{site_data['slope']}°")
    
    # Analytics Chart
    chart = alt.Chart(pd.DataFrame({
        "Factor": ["Fuel Density", "Slope Gradient"], 
        "Impact Value": [site_data['fuel'], site_data['slope']]
    })).mark_bar(color='#FF4B4B', opacity=0.8).encode(
        x=alt.X('Impact Value:Q', title=None),
        y=alt.Y('Factor:N', sort='-x', title=None)
    ).properties(height=120).configure_view(strokeOpacity=0)
    
    st.altair_chart(chart, use_container_width=True)

    if site_data['vor'] > 30:
        st.error("**Spec:** LC3 Cement + Mineral Wool Cavity Insulation.\n\n*Impact: -45% embodied carbon vs standard non-combustible assembly.*")
    elif site_data['vor'] > 15:
        st.warning("**Spec:** Limestone-based Fiber Cement Siding.\n\n*Impact: Ignition-resistant with moderate carbon footprint.*")
    else:
        st.success("**Spec:** FSC-Certified Timber Framing.\n\n*Impact: Baseline standard. Focus on operational carbon.*")

with col_map:
    layers = []
    
    # Layer 1: Background Risk (Toggleable)
    if show_heatmap:
        layers.append(pdk.Layer(
            "HexagonLayer",
            bg_df,
            get_position=["lon", "lat"],
            elevation_scale=10,
            pickable=False,
            extruded=True,
            coverage=0.8,
            get_fill_color=["risk * 2", "50", "150", 100], # 100 alpha for transparency
        ))

    # Layer 2: The dd Towers (Toggleable)
    if show_towers:
        layers.append(pdk.Layer(
            "ColumnLayer",
            zones_df,
            get_position=["lon", "lat"],
            get_elevation="height",
            elevation_scale=1,
            radius=1200,
            get_fill_color=[255, 75, 75, 220], # 220 alpha so they stand out but aren't entirely solid
            pickable=True,
            auto_highlight=True,
        ))

    # Clean Tooltip passing exact dataframe columns
    tooltip = {
        "html": "<b>{zone}</b><br/>VOR: {vor}<br/>Fuel: {fuel}% | Slope: {slope}°",
        "style": {"backgroundColor": "#1E1E1E", "color": "white", "fontFamily": "Helvetica"}
    }

    r = pdk.Deck(
        layers=layers,
        initial_view_state=pdk.ViewState(latitude=34.10, longitude=-118.35, zoom=9, pitch=50, bearing=-10),
        map_style="dark",
        tooltip=tooltip
    )
    st.pydeck_chart(r, use_container_width=True)
