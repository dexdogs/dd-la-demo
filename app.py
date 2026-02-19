import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
import altair as alt

st.set_page_config(page_title="dd | Spatial Risk Engine", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    .stApp { background-color: #000000; }
    .stApp, .stApp p, .stApp h1, .stApp h2, .stApp h3, .stApp span, .stApp label {
        color: #FFFFFF !important; font-family: 'Helvetica Neue', sans-serif;
    }
    div[data-testid="metric-container"], div[data-baseweb="select"] > div {
        background-color: #121212 !important; border: 1px solid #333 !important; 
    }
    div[data-testid="metric-container"] { padding: 5%; border-radius: 8px; }
    </style>
    """, unsafe_allow_html=True)

@st.cache_data
def load_data():
    zones = pd.DataFrame({
        "zone": ["Malibu", "Hollywood Hills", "Altadena", "Pasadena", "Downtown LA"],
        "city_county": ["(Malibu City)", "(Los Angeles)", "(LA County)", "(Pasadena City)", "(Los Angeles)"],
        "lat": [34.0259, 34.1235, 34.1867, 34.1478, 34.0407],
        "lon": [-118.7798, -118.3217, -118.1312, -118.1445, -118.2468],
        "fuel": [95, 75, 88, 60, 10],
        "slope": [40, 35, 42, 22, 2],
    })
    zones["vor"] = ((zones["fuel"] * zones["slope"]) / 100).round(1)
    zones["height"] = zones["vor"] * 250 
    zones["regional_risk"] = "Site Specific"
    
    # Pre-calculated grid to preserve text data (replaces auto-aggregation)
    lats, lons = np.meshgrid(np.linspace(33.8, 34.3, 45), np.linspace(-118.6, -118.1, 45))
    bg = pd.DataFrame({'lat': lats.flatten(), 'lon': lons.flatten()})
    
    bg = bg[~((bg['lat'] < 34.04) & (bg['lon'] < -118.52))] 
    bg = bg[~((bg['lat'] < 33.95) & (bg['lon'] < -118.45))] 
    bg = bg[~((bg['lat'] < 33.78) & (bg['lon'] < -118.40))] 
    
    bg['regional_risk'] = np.random.uniform(10, 100, len(bg)).round(1)
    bg['height'] = bg['regional_risk'] * 5 
    bg['zone'] = "Ambient Grid"
    bg['city_county'] = "(LA County Area)"
    bg['vor'] = "Regional Average"
    return zones, bg

zones_df, bg_df = load_data()

st.title("🔥 dd: Climate-to-Spec Analytics")
st.markdown("Quantifying environmental exposure to optimize low-carbon residential construction in Los Angeles.")
st.divider()

col_map, col_analytics = st.columns([2.5, 1.5], gap="large")

with col_analytics:
    st.subheader("Layer Controls & Legend")
    show_heatmap = st.toggle("Show Regional Risk Hexagons", value=True)
    show_towers = st.toggle("Show VOR Site Towers", value=True)
    
    st.divider()
    st.subheader("Site Intelligence")
    selected_zone = st.selectbox("Select Residential Zone", zones_df["zone"])
    site_data = zones_df[zones_df["zone"] == selected_zone].iloc[0]
    
    m1, m2 = st.columns(2)
    m1.metric("VOR Score", site_data['vor'])
    m2.metric("Gradient", f"{site_data['slope']}°")
    
    chart = alt.Chart(pd.DataFrame({
        "Factor": ["Fuel Density", "Slope Gradient"], 
        "Impact Value": [site_data['fuel'], site_data['slope']]
    })).mark_bar(color='#FF4B4B', opacity=0.8).encode(
        x=alt.X('Impact Value:Q', title=None, axis=alt.Axis(grid=False, labels=False, ticks=False)),
        y=alt.Y('Factor:N', sort='-x', title=None, axis=alt.Axis(labelColor='white'))
    ).properties(height=120).configure_view(strokeOpacity=0).configure(background='#000000')
    st.altair_chart(chart, use_container_width=True)

    if site_data['vor'] > 30:
        st.error("**Spec:** Holcim ECOPact LC3 + Rockwool Comfortbatt.")
        st.markdown("[🔗 Holcim EPD](https://www.holcim.us/ecopact) | [🔗 Rockwool EPD](https://www.rockwool.com/north-america/about-us/sustainability/)")
    elif site_data['vor'] > 15:
        st.warning("**Spec:** James Hardie Fiber Cement (Limestone-based).")
        st.markdown("[🔗 James Hardie EPD](https://www.jameshardie.com/about-us/sustainability)")
    else:
        st.success("**Spec:** FSC-Certified Mass Timber & Glulam.")
        st.markdown("[🔗 WoodWorks Timber EPD](https://www.woodworks.org/resources/environmental-product-declarations/)")

with col_map:
    layers = []
    
    if show_heatmap:
        layers.append(pdk.Layer(
            "ColumnLayer", # 6-sided column simulates a hexagon but keeps dataframe intact
            bg_df,
            get_position=["lon", "lat"],
            get_elevation="height",
            elevation_scale=1,
            radius=600,
            disk_resolution=6, 
            get_fill_color=["regional_risk * 2", "50", "150", 100], 
            pickable=True,
            auto_highlight=True,
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
        "html": "<b>{zone} {city_county}</b><br/>Site VOR: {vor}<br/>Aggregated Regional Risk: {regional_risk}",
        "style": {"backgroundColor": "#121212", "color": "#FFFFFF", "fontFamily": "Helvetica", "border": "1px solid #333"}
    }

    r = pdk.Deck(
        layers=layers,
        initial_view_state=pdk.ViewState(latitude=34.10, longitude=-118.35, zoom=9, pitch=50, bearing=-10),
        map_style="dark",
        tooltip=tooltip
    )
    st.pydeck_chart(r, use_container_width=True)
