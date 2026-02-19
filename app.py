import streamlit as st
import pandas as pd
import pydeck as pdk

# --- CONFIG ---
st.set_page_config(page_title="dd: 3D Resilience Engine", layout="wide")

# --- DATASET ---
data = pd.DataFrame({
    "zone": ["Malibu", "Hollywood Hills", "Altadena", "Pasadena", "Downtown LA"],
    "lat": [34.0259, 34.1235, 34.1867, 34.1478, 34.0407],
    "lon": [-118.7798, -118.3217, -118.1312, -118.1445, -118.2468],
    "fuel": [95, 75, 88, 60, 10],
    "slope": [40, 35, 42, 22, 2],
})

data["vor"] = (data["fuel"] * data["slope"]) / 100
data["height"] = data["vor"] * 100 # Low, subtle towers

# --- UI ---
st.title("🔥 dd (Dexdogs) 3D VOR Analytics")
st.caption("Stabilized Engine: Hexagon Risk Overlay + Low-Carbon Spec Selection")

col1, col2 = st.columns([2, 1])

with col1:
    # 1. HEXAGON OVERLAY (Replaces Heatmap for better stability and technical look)
    # This layer represents the 'Wildfire Risk Dataset'
    risk_overlay = pdk.Layer(
        "HexagonLayer",
        data,
        get_position=["lon", "lat"],
        radius=2500,
        elevation_scale=0, # Keep it flat to ground the map
        upper_percentile=100,
        pickable=True,
        extruded=False,
        get_fill_color=[255, 60, 0, 80], # Transparent fire-orange hexes
    )

    # 2. VOR COLUMN LAYER (Your Specific Analytics)
    column_layer = pdk.Layer(
        "ColumnLayer",
        data,
        get_position=["lon", "lat"],
        get_elevation="height",
        elevation_scale=1,
        radius=1200,
        get_fill_color=["vor * 8", 100, 255, 200], # Blue-to-Red shift
        pickable=True,
        auto_highlight=True,
    )

    view_state = pdk.ViewState(
        latitude=34.10, longitude=-118.40, zoom=9, pitch=45, bearing=0
    )

    # CartoDB Dark Matter style is more stable in Pydeck
    r = pdk.Deck(
        layers=[risk_overlay, column_layer],
        initial_view_state=view_state,
        map_style="light", # Options: 'dark', 'light', 'road', 'satellite'
        tooltip={"text": "{zone}\nVOR Score: {vor}"}
    )
    # Force a dark theme via a wrapper
    st.pydeck_chart(r, use_container_width=True)

with col2:
    st.write("### 🏗️ Low-Carbon Spec Selection")
    selection = st.selectbox("Deep Dive Zone", data["zone"])
    row = data[data["zone"] == selection].iloc[0]
    
    st.metric("VOR Score", row["vor"])
    
    st.divider()
    
    # REGIONAL LOW-CARBON SPECS
    if row["vor"] > 30:
        st.error("🚨 HIGH RISK / LOW CARBON SPEC")
        st.markdown(f"""
        **Zone:** {selection} (Steep Slope / High Fuel)
        
        **Recommended Spec:** * **Envelope:** Carbon-Sequestering Mass Timber + Intumescent Bio-Retardant.
        * **Exterior:** Ultra-Low Carbon LC3 Cement Stucco.
        * **Impact:** 45% reduction in embodied carbon vs. standard fire-concrete.
        """)
    elif row["vor"] > 15:
        st.warning("⚠️ MODERATE RISK / LOW CARBON SPEC")
        st.markdown(f"""
        **Zone:** {selection} (Foothill Residential)
        
        **Recommended Spec:** * **Envelope:** 100% Recycled Mineral Wool Insulation.
        * **Exterior:** Fiber Cement Siding (Limestone-based).
        * **Impact:** High fire resistance with negative-carbon insulation value.
        """)
    else:
        st.success("✅ LOW RISK / BASELINE SPEC")
        st.markdown(f"""
        **Zone:** {selection} (Urban Low-Slope)
        
        **Recommended Spec:** * **Envelope:** FSC-Certified Advanced Timber Framing.
        * **Exterior:** Standard Wood Siding with Bio-Shield coating.
        * **Impact:** Lowest cost and carbon footprint while meeting IBC standards.
        """)

st.sidebar.markdown("""
**Demo Note:** If the map is still white, it is a browser cache issue. Try **Incognito Mode**.
The hex tiles represent regional fire hazard zones, while the columns show site-specific VOR.
""")
