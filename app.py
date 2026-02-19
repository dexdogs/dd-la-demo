import streamlit as st
import pandas as pd
import pydeck as pdk

# --- CONFIG ---
st.set_page_config(page_title="dd: 3D Resilience Engine", layout="wide")

# --- DATASET ---
# Adjusted height multiplier to keep towers short
data = pd.DataFrame({
    "zone": ["Malibu", "Hollywood Hills", "Altadena", "Pasadena", "Downtown LA"],
    "lat": [34.0259, 34.1235, 34.1867, 34.1478, 34.0407],
    "lon": [-118.7798, -118.3217, -118.1312, -118.1445, -118.2468],
    "fuel": [95, 75, 88, 60, 10],
    "slope": [40, 35, 42, 22, 2],
})

data["vor"] = (data["fuel"] * data["slope"]) / 100
# Lowered height factor from 500 to 150 to keep them short
data["height"] = data["vor"] * 150 

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
        elevation_scale=1, # Kept at 1 for true-to-data height
        radius=1200,       # Slightly wider for better visibility
        get_fill_color=["vor * 5", "205 - (vor * 3)", 150, 200],
        pickable=True,
        auto_highlight=True,
    )

    view_state = pdk.ViewState(
        latitude=34.10, longitude=-118.40, zoom=9, pitch=40, bearing=0
    )

    # Switched to 'light' or 'dark' (non-mapbox styles) to fix the white background issue
    r = pdk.Deck(
        layers=[layer],
        initial_view_state=view_state,
        map_style=None, # Uses the default simple base map
        tooltip={"text": "{zone}\nVOR: {vor}"}
    )
    st.pydeck_chart(r)

with col2:
    st.write("### VOR Intelligence")
    selection = st.selectbox("Select Zone", data["zone"])
    row = data[data["zone"] == selection].iloc[0]
    
    st.metric("VOR Score", row["vor"])
    
    with st.expander("📝 What is VOR?"):
        st.write(f"**VOR (Value of Risk)** is a measure of potential fire intensity at a specific building site. At a score of **{row['vor']}**, the {selection} zone faces thermal stress levels that exceed standard residential wood-frame capacity.")
        st.info(interpret_vor(row["vor"]))

    st.divider()
    if row["vor"] > 25:
        st.error("**Spec:** Mineral Wool + 3-coat Stucco")
        st.caption("Resilience Rating: High | Carbon Premium: +22%")
    else:
        st.success("**Spec:** Fire-treated Sheathing")
        st.caption("Resilience Rating: Standard | Carbon Premium: +4%")

st.sidebar.info("Map Fix: Background is now active. Towers scaled down for clarity.")
