import streamlit as st
import folium
from streamlit_folium import st_folium

# --- CONFIG & STYLING ---
st.set_page_config(page_title="dd: Fire-Rated Spec Tool", layout="wide")

# Custom CSS for that "CarbonCats/dexdogs" dark-mode aesthetic
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stMetric { background-color: #161b22; padding: 15px; border-radius: 10px; border: 1px solid #30363d; }
    </style>
    """, unsafe_allow_html=True)

# --- ENGINE LOGIC ---
def calculate_vor(fuel, slope):
    return round((fuel * slope) / 100, 2)

# Zone Data: Fuel Density %, Slope Degrees, Carbon footprint (kgCO2e/m2)
zone_stats = {
    "Malibu / Santa Monica Mtns": {"fuel": 95, "slope": 40, "base_carbon": 210},
    "Hollywood Hills": {"fuel": 75, "slope": 30, "base_carbon": 180},
    "Pasadena Foothills": {"fuel": 60, "slope": 22, "base_carbon": 150},
    "Downtown LA": {"fuel": 10, "slope": 2, "base_carbon": 90}
}

# --- UI LAYOUT ---
st.title("🔥 dd (Dexdogs) Resilience Engine")
st.subheader("Residential New Construction: LA Wildfire Risk & Carbon Optimization")

col1, col2 = st.columns([2, 1])

with col1:
    # Interactive Map
    m = folium.Map(location=[34.0522, -118.2437], zoom_start=10, tiles="CartoDB dark_matter")
    
    # Adding Risk Zones
    folium.Circle([34.07, -118.70], radius=5000, color='#ff4b4b', fill=True, popup="Malibu / Santa Monica Mtns").add_to(m)
    folium.Circle([34.12, -118.32], radius=3000, color='#ff4b4b', fill=True, popup="Hollywood Hills").add_to(m)
    folium.Circle([34.14, -118.14], radius=3000, color='#ffa421', fill=True, popup="Pasadena Foothills").add_to(m)
    folium.Circle([34.04, -118.24], radius=2000, color='#28a745', fill=True, popup="Downtown LA").add_to(m)

    map_data = st_folium(m, width="100%", height=500)

with col2:
    st.write("### Spec Analysis")
    selected = map_data.get("last_object_clicked_popup")
    
    if selected:
        stats = zone_stats[selected]
        vor_score = calculate_vor(stats['fuel'], stats['slope'])
        
        # Risk Metric
        st.metric("VOR (Value of Risk)", f"{vor_score}")
        
        # Dynamic Material Selection
        if vor_score > 0.8:
            material = "Ultra-High Performance Concrete + Intumescent Coating"
            carbon_mod = 1.4 # Higher carbon for heavy fire-proofing
        elif vor_score > 0.4:
            material = "Fiber Cement Siding + 1/8\" Ember Mesh"
            carbon_mod = 1.1
        else:
            material = "Standard WUI Code Compliance"
            carbon_mod = 1.0

        st.warning(f"**Recommended Material:**\n{material}")
        
        # Carbon Toggle
        st.divider()
        show_carbon = st.toggle("Show Carbon Impact", value=True)
        
        if show_carbon:
            total_carbon = round(stats['base_carbon'] * carbon_mod, 1)
            st.metric("Embodied Carbon", f"{total_carbon} kgCO2e/m2", delta=f"{round((carbon_mod-1)*100)}% risk premium")
            st.info("💡 dd insight: Switch to Bio-based Intumescent coating to reduce carbon by 15% while maintaining VOR.")
            
        st.caption(f"Spatial Inputs: Fuel {stats['fuel']}% | Slope {stats['slope']}°")
    else:
        st.info("👈 Click a residential risk zone on the map to generate the specification.")

st.sidebar.image("https://via.placeholder.com/150?text=dd+Engine", width=100)
st.sidebar.write("**Startup:** dexdogs (dd)")
st.sidebar.write("**Target:** Residential Builders")
st.sidebar.write("**Location:** Boston / LA")
