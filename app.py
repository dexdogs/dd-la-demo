import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
import altair as alt

st.set_page_config(page_title="dd | Spatial Risk Engine", layout="wide")
st.markdown("""<style>div[data-testid="metric-container"] {background-color: #1E1E1E; border: 1px solid #333; padding: 5%; border-radius: 8px;} h1, h2, h3, p {color: #E0E0E0;}</style>""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    zones = pd.DataFrame({
        "zone": ["Malibu", "Hollywood Hills", "Altadena", "Pasadena", "Downtown LA"],
        "lat": [34.0259, 34.1235, 34.1867, 34.1478, 34.0407],
        "lon": [-118.7798, -118.3217, -118.1312, -118.1445, -118.2468],
        "fuel": [95, 75, 88, 60, 10],
        "slope": [40, 35, 42, 22, 2],
    })
    zones["vor"] = (zones["fuel"] * zones["slope"]) / 100
    zones["radius"] = zones["vor"] * 60 + 800 # Scale circle size by risk
    
    np.random.seed(42)
    bg = pd.DataFrame({'lat': np.random.normal(34.15, 0.15, 2000), 'lon': np.random.normal(-118.40, 0.30, 2000), 'risk': np.random.uniform(10, 100, 2000)})
    return zones, bg

zones_df, bg_df = load_data()

col_map, col_analytics = st.columns([2.5, 1.5], gap="large")

with col_map:
    # Smooth background risk gradient
    heatmap = pdk.Layer(
        "HeatmapLayer", bg_df, get_position=["lon", "lat"], get_weight="risk", radius_pixels=50
    )
    # Sharp, stroked circles for dd target sites
    scatter = pdk.Layer(
        "ScatterplotLayer", zones_df, get_position=["lon", "lat"], get_radius="radius",
        get_fill_color=[255, 75, 75, 200], get_line_color=[255, 255, 255, 255], 
        stroked=True, line_width_min_pixels=3, pickable=True
    )
    
    # Pitch set to 0 for a clean top-down 2D view
    r = pdk.Deck(
        layers=[heatmap, scatter], 
        initial_view_state=pdk.ViewState(latitude=34.10, longitude=-118.35, zoom=9, pitch=0), 
        map_style="dark", 
        tooltip={"text": "{zone}\nVOR: {vor}"}
    )
    st.pydeck_chart(r, use_container_width=True)

with col_analytics:
    st.subheader("dd Site Intelligence")
    sel = st.selectbox("Zone", zones_df["zone"])
    site = zones_df[zones_df["zone"] == sel].iloc[0]
    
    c1, c2 = st.columns(2)
    c1.metric("VOR Score", f"{site['vor']:.1f}")
    c2.metric("Gradient", f"{site['slope']}°")
    
    st.altair_chart(alt.Chart(pd.DataFrame({"Factor": ["Fuel", "Slope"], "Val": [site['fuel'], site['slope']]})).mark_bar(color='#FF4B4B').encode(x=alt.X('Val:Q', title="Impact"), y=alt.Y('Factor:N', sort='-x', title="")).properties(height=120), use_container_width=True)
    
    if site['vor'] > 30: 
        st.error("Spec: LC3 Cement + Mineral Wool\n\nHigh risk requires non-combustible assembly.")
    elif site['vor'] > 15: 
        st.warning("Spec: Fiber Cement Siding\n\nModerate risk requires ignition-resistant assembly.")
    else: 
        st.success("Spec: FSC Timber\n\nLow risk. Standard timber framing acceptable.")
