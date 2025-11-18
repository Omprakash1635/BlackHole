import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# =====================================================
# PAGE CONFIG
# =====================================================
st.set_page_config(
    page_title="Black Hole Accretion Dashboard",
    page_icon="🌀",
    layout="wide"
)

# =====================================================
# DARK THEME CSS
# =====================================================
st.markdown("""
    <style>
        .stApp { background-color: #0b1220; color: #E0E6ED; }
        .metric { background-color:#111827; padding:12px; border-radius:12px; }
        .block-container { padding-top: 1.5rem; }
    </style>
""", unsafe_allow_html=True)

NEON = "#00ccff"

# =====================================================
# LOAD DATA
# =====================================================
@st.cache_data
def load_data():
    df = pd.read_excel("BlackHole_Accretion_75.xlsx")
    df.columns = df.columns.str.strip()
    return df

df = load_data()

# =====================================================
# NUMERIC CLEANING
# =====================================================
num_cols = [col for col in df.columns if df[col].dtype != 'O']
for col in num_cols:
    df[col] = pd.to_numeric(df[col], errors="coerce")

# =====================================================
# ADD CATEGORIES
# =====================================================
def classify_mass(m):
    if pd.isna(m): return "Unknown"
    if m < df["BlackHole_Mass_SolarMass"].quantile(0.33): return "Low Mass"
    if m < df["BlackHole_Mass_SolarMass"].quantile(0.66): return "Medium Mass"
    return "High Mass"

def classify_spin(s):
    if pd.isna(s): return "Unknown"
    if s < 0.3: return "Low Spin"
    if s < 0.7: return "Medium Spin"
    return "High Spin"

def classify_edd(e):
    if pd.isna(e): return "Unknown"
    if e < 0.1: return "Sub-Eddington"
    if e <= 1.0: return "Near-Eddington"
    return "Super-Eddington"

df["Mass_Class"] = df["BlackHole_Mass_SolarMass"].apply(classify_mass)
df["Spin_Class"] = df["Spin_Factor"].apply(classify_spin)
df["Eddington_Class"] = df["Eddington_Ratio"].apply(classify_edd)

# =====================================================
# SIDEBAR FILTERS
# =====================================================
st.sidebar.header("🔭 Filters")

mass_f = st.sidebar.multiselect(
    "Mass Class", sorted(df["Mass_Class"].unique()), sorted(df["Mass_Class"].unique())
)
spin_f = st.sidebar.multiselect(
    "Spin Class", sorted(df["Spin_Class"].unique()), sorted(df["Spin_Class"].unique())
)
edd_f = st.sidebar.multiselect(
    "Eddington Regime", sorted(df["Eddington_Class"].unique()), sorted(df["Eddington_Class"].unique())
)

filtered = df[
    df["Mass_Class"].isin(mass_f) &
    df["Spin_Class"].isin(spin_f) &
    df["Eddington_Class"].isin(edd_f)
]

# =====================================================
# TITLE
# =====================================================
st.markdown(
    f"<h2 style='color:{NEON}; text-align:center;'>Black Hole Accretion Analytics Dashboard</h2>",
    unsafe_allow_html=True
)
st.markdown(
    "<p style='color:#9ca3af;text-align:center;'>Interactive astrophysics dashboard for accretion disk simulations.</p>",
    unsafe_allow_html=True
)

# =====================================================
# KPI CARDS
# =====================================================
col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Objects", len(filtered))
col2.metric("Avg Mass (M☉)", f"{filtered['BlackHole_Mass_SolarMass'].mean():.2f}")
col3.metric("Avg Spin", f"{filtered['Spin_Factor'].mean():.3f}")
col4.metric("Avg X-ray Luminosity", f"{filtered['Xray_Luminosity_erg_s'].mean():.2e}")

st.markdown("---")

# =====================================================
# ROW 1 – DONUT / BAR / HISTOGRAM
# =====================================================
r1c1, r1c2, r1c3 = st.columns(3)

with r1c1:
    fig = px.pie(
        filtered,
        names="Mass_Class",
        hole=0.55,
        color_discrete_sequence=[NEON, "#3b82f6", "#06b6d4"]
    )
    fig.update_layout(title="Mass Class Distribution", template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)

with r1c2:
    spin_count = filtered["Spin_Class"].value_counts().reset_index()
    spin_count.columns = ["Spin_Class", "count"]
    fig = px.bar(
        spin_count, x="Spin_Class", y="count",
        color="count", color_continuous_scale="Blues"
    )
    fig.update_layout(title="Spin Class Distribution", template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)

with r1c3:
    fig = px.histogram(
        filtered,
        x="Eddington_Ratio", nbins=15,
        color_discrete_sequence=[NEON]
    )
    fig.update_layout(title="Eddington Ratio Distribution", template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)

# =====================================================
# ROW 2 – SCATTER / LINE
# =====================================================
r2c1, r2c2 = st.columns(2)

with r2c1:
    fig = px.scatter(
        filtered,
        x="BlackHole_Mass_SolarMass",
        y="Xray_Luminosity_erg_s",
        color="Eddington_Class",
        hover_data=["BlackHole_ID"],
        template="plotly_dark"
    )
    fig.update_layout(title="Mass vs X-ray Luminosity")
    st.plotly_chart(fig, use_container_width=True)

with r2c2:
    fig = px.line(
        filtered.sort_values("BlackHole_Mass_SolarMass"),
        x="BlackHole_Mass_SolarMass",
        y="Disk_Temperature_Inner_K",
        color_discrete_sequence=[NEON],
        template="plotly_dark"
    )
    fig.update_layout(title="Inner Disk Temperature vs Mass")
    st.plotly_chart(fig, use_container_width=True)

# =====================================================
# ROW 3 – RADAR / GAUGE
# =====================================================
r3c1, r3c2 = st.columns(2)

with r3c1:
    radar_cols = [
        "Magnetic_Flux_Gauss", "Gravitational_Redshift",
        "Radiation_Pressure", "Relativistic_Beaming_Factor",
        "Hardness_Ratio", "Eddington_Ratio"
    ]
    radar_vals = [filtered[c].mean() if c in filtered else 0 for c in radar_cols]

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=radar_vals,
        theta=radar_cols,
        fill="toself",
        line_color=NEON
    ))

    fig.update_layout(
        template="plotly_dark",
        title="Accretion Physics Radar",
        polar=dict(bgcolor="#111827"),
        paper_bgcolor="#0b1220"
    )

    st.plotly_chart(fig, use_container_width=True)

with r3c2:
    jet_mean = filtered["Jet_Energy_erg"].mean()
    jet_90 = df["Jet_Energy_erg"].quantile(0.9)
    score = min(100, (jet_mean / jet_90) * 100) if jet_90 else 0

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        title={"text": "Jet Power Index", "font": {"color": "white"}},
        gauge={
            "axis": {"range": [0, 100]},
            "bar": {"color": NEON},
            "bgcolor": "#111827",
            "borderwidth": 2,
        }
    ))

    fig.update_layout(template="plotly_dark", paper_bgcolor="#0b1220")
    st.plotly_chart(fig, use_container_width=True)

# =====================================================
# RAW DATA TABLE
# =====================================================
with st.expander("Show Filtered Dataset"):
    st.dataframe(filtered)
