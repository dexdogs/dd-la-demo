import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
import altair as alt

# --- 1. CONFIG & STYLING ---
st.set_page_config(page_title="dd | Spatial Risk Engine", layout="wide", initial_sidebar_state="expanded")

# Strict Black Background & White Text
st.markdown("""
    <style>
    .stApp {
        background-color: #000000;
    }
    .stApp, .stApp p, .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6, .stApp span, .stApp label {
        color: #FFFFFF !important;
        font-family: 'Helvetica Neue', sans-serif;
    }
    div[data-testid="metric-container"] {
        background-color: #121212 !important; 
        border: 1px solid #333 !important; 
        padding: 5%; 
        border-radius: 8px;
    }
    div[data-baseweb="select"] > div {
        background-color: #121212 !important;
    }
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
    st.subheader("Layer Controls & Legend")
    
    show_heatmap = st.toggle("Show Regional Risk Hexagons", value=True)
    st.caption("**Hexagons:** Represents the macro-level environmental exposure (e.g., CAL FIRE hazard zones). The glowing honeycomb grid shows the baseline ambient threat across the region.")
    
    show_towers = st.toggle("Show VOR Site Towers", value=True)
    st.caption("**Towers:** Represents specific dd (dexdogs) project sites. The height is the VOR (Value of Risk) score, proving exactly how much thermal stress that specific building envelope must withstand.")
    
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
        x=alt.X('Impact Value:Q', title=None, axis=alt.Axis(grid=False, labels=False, ticks=False)),
        y=alt.Y('Factor:N', sort='-x', title=None, axis=alt.Axis(labelColor='white'))
    ).properties(height=120).configure_view(strokeOpacity=0).configure(background='#000000')
    
    st.altair_chart(chart, use_container_width=True)

    if site_data['vor'] > 30:
        st.error("**Spec:** LC3 Cement + Mineral Wool Cavity Insulation.\n\n*Impact: -45% embodied carbon vs standard non-combustible assembly.*")
    elif site_data['vor'] > 15:
        st.warning("**Spec:** Limestone-based Fiber Cement Siding.\n\n*Impact: Ignition-resistant with moderate carbon footprint.*")
    else:
        st.success("**Spec:** FSC-Certified Timber Framing.\n\n*Impact: Baseline standard. Focus on operational carbon.*")

with col_map:
    layers = []
    
    if show_heatmap:
        layers.append(pdk.Layer(
            "HexagonLayer",
            bg_df,
            get_position=["lon", "lat"],
            elevation_scale=10,
            pickable=False,
            extruded=True,
            coverage=0.8,
            get_fill_color=["risk * 2", "50", "150", 100], 
        ))

    if show_towers:
        layers.append(pdk.Layer(
            "ColumnLayer",
            zones_df,
            get_position=["lon", "lat"],
            get_elevation="height",
            elevation_scale=1,
            radius=1200,
            get_fill_color=[255, 75, 75, 220],
            pickable=True,
            auto_highlight=True,
        ))

    tooltip = {
        "html": "<b>{zone}</b><br/>VOR: {vor}<br/>Fuel: {fuel}% | Slope: {slope}°",
        "style": {"backgroundColor": "#121212", "color": "#FFFFFF", "fontFamily": "Helvetica", "border": "1px solid #333"}
    }

    r = pdk.Deck(
        layers=layers,
        initial_view_state=pdk.ViewState(latitude=34.10, longitude=-118.35, zoom=9, pitch=50, bearing=-10),
        map_style="dark",
        tooltip=tooltip
    )
    st.pydeck_chart(r, use_container_width=True)
