import streamlit as st
import pandas as pd
import pydeck as pdk

# --- CONFIG ---
st.set_page_config(page_title="dd: 3D Resilience Engine", layout="wide")

# --- DATASET (Including Altadena) ---
# VOR = (Fuel * Slope) / 100. Height in map = VOR * 1000
data = pd.DataFrame({
    "zone": ["Malibu", "Hollywood Hills", "Altadena", "Pasadena", "Downtown LA"],
    "lat": [34.0259, 34.1235, 34.1867, 34.1478, 34.0407],
    "lon": [-118.7798, -118.3217, -118.1312, -118.1445, -118.2468],
    "fuel": [95, 75, 88, 60, 10],
    "slope": [40, 35, 42, 22, 2],
})

data["vor"] = (data["fuel"] * data["slope"]) / 100
data["height"] = data["vor"] * 500  # Visual extrusion height

# --- VOR INTERPRETATION LOGIC ---
def interpret_vor(val):
    if val > 30:
        return "CRITICAL: Flash-over high probability. Requires Non-Combustible Type I/II materials."
    elif val > 15:
        return "ELEVATED: Ember-storm zone. Requires WUI-compliant ignition-resistant cladding."
    else:
        return "NOMINAL: Low fuel load. Standard IBC residential framing acceptable."

# --- UI ---
st.title("🔥 dd (Dexdogs) 3D VOR Analytics")
st.subheader("Spatial Risk Extrusion: LA & Altadena Residential Zones")

col1, col2 = st.columns([2, 1])

with col1:
    # 3D Map Layer
    layer = pdk.Layer(
        "ColumnLayer",
        data,
        get_position=["lon", "lat"],
        get_elevation="height",
        elevation_scale=10,
        radius=800,
        get_fill_color=["vor * 5", "255 - (vor * 5)", 50, 140],
        pickable=True,
        auto_highlight=True,
    )

    # Initial View State (3D Tilt)
    view_state = pdk.ViewState(
        latitude=34.10, longitude=-118.40, zoom=9.5, pitch=45, bearing=0
    )

    r = pdk.Deck(
        layers=[layer],
        initial_view_state=view_state,
        map_style="mapbox://styles/mapbox/dark-v10",
        tooltip={"text": "{zone}\nVOR: {vor}\nFuel: {fuel}%"}
    )
    st.pydeck_chart(r)

with col2:
    st.write("### VOR Intelligence")
    selection = st.selectbox("Select Zone for Deep Dive", data["zone"])
    row = data[data["zone"] == selection].iloc[0]
    
    # Analytics Display
    st.metric("VOR Score", row["vor"])
    
    with st.expander("📝 What does this VOR number mean?"):
        st.write(f"**VOR {row['vor']} Index:**")
        st.info(interpret_vor(row["vor"]))
        st.caption("VOR (Value of Risk) is a dd-proprietary metric calculating the intersection of fuel density and topography gradient. It determines the thermal stress a building envelope must withstand.")

    # Carbon & Materials
    st.divider()
    if row["vor"] > 25:
        st.error("**Material Spec:** Mineral Wool Insulation + 3-coat Stucco")
        st.metric("Embodied Carbon Premium", "+22%", delta_color="inverse")
    else:
        st.success("**Material Spec:** Standard Timber + Fire-treated Sheathing")
        st.metric("Embodied Carbon Premium", "+4%", delta_color="inverse")

st.sidebar.markdown("""
**How to use:**
1. **Rotate:** Right-click + Drag
2. **Tilt:** Ctrl + Drag
3. **Analyze:** Columns height = VOR Score
""")
